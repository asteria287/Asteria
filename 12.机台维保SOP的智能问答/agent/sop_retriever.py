"""
SOP 知识库检索器
多策略混合检索: 精确术语、中文语义概念、关键字密度、章节结构匹配
"""
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from .config import SOPQConfig


class SOPRetriever:
    """SOP 知识库检索器 — 多策略混合检索"""

    def __init__(self):
        self.kb_dir = SOPQConfig.KB_DIR
        self.documents: Dict[str, str] = {}           # filename → raw content
        self.sections: Dict[str, List[Dict]] = {}     # filename → [{heading, level, content, section_num}]
        self.keyword_index: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self._section_index: Dict[str, set] = defaultdict(set)  # concept → {(file, idx, heading)}

        self._load()
        self._parse_sections()
        self._build_index()

    def _load(self):
        """加载知识库中所有 SOP 文档"""
        SOPQConfig.discover_kb()
        for fname in SOPQConfig.KB_FILES:
            fp = self.kb_dir / fname
            if fp.exists():
                try:
                    self.documents[fname] = fp.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    # fallback encoding for some Windows docs
                    self.documents[fname] = fp.read_text(encoding="gbk")

    def _parse_sections(self):
        """解析 SOP 文档章节结构, 提取层级 + 编号"""
        heading_re = re.compile(r'^(#{1,4})[\s]*(\d+(?:\.\d+)*)?[\s]*(.+)?$', re.MULTILINE)

        for fname, content in self.documents.items():
            self.sections[fname] = []
            lines = content.split('\n')
            cur_h = "前言"
            cur_lv = 0
            cur_num = ""
            cur_buf = []

            for line in lines:
                m = heading_re.match(line)
                if m:
                    # flush previous section
                    if cur_buf:
                        self.sections[fname].append({
                            "heading": cur_h,
                            "level": cur_lv,
                            "section_num": cur_num,
                            "content": '\n'.join(cur_buf).strip(),
                        })
                    cur_h = (m.group(3) or m.group(2) or line).strip()
                    cur_lv = len(m.group(1))
                    cur_num = m.group(2) or ""
                    cur_buf = []
                else:
                    cur_buf.append(line)

            # flush last section
            if cur_buf:
                self.sections[fname].append({
                    "heading": cur_h,
                    "level": cur_lv,
                    "section_num": cur_num,
                    "content": '\n'.join(cur_buf).strip(),
                })

    def _build_index(self):
        """构建多层次倒排索引"""
        for fname, secs in self.sections.items():
            for idx, sec in enumerate(secs):
                combined = (sec["heading"] + " " + sec["content"]).lower()

                # 1. 安全项索引 (特殊权重)
                safety_pattern = re.compile(
                    r'(EMO|PPE|lockout|tagout|LOTO|上锁|挂牌|警示|警告|危险|有害气体|'
                    r'防酸手套|护目镜|防静电鞋|安全帽|禁止操作|通风|hazard|danger|'
                    r'emergency|泄漏检测|helmet|goggle|glove)',
                    re.IGNORECASE
                )
                for m in safety_pattern.finditer(combined):
                    self.keyword_index[f"SAFETY:{m.group(0).upper()}"].append((fname, idx))
                    self._section_index["安全"].add((fname, idx, sec["heading"]))

                # 2. 工具/设备索引
                tool_pattern = re.compile(
                    r'(扭矩扳手|torque\s*wrench|氦检漏仪|helium\s*leak\s*detector|'
                    r'真空吸尘器|vacuum\s*cleaner|Scotch[\s-]*Brite|无尘布|lint[\s-]*free\s*cloth|'
                    r'IPA|isopropyl|DI\s*Water|去离子水|N2|氮气|塞尺|feeler\s*gauge|'
                    r'热像仪|thermal\s*camera|网络分析仪|network\s*analyzer|'
                    r'O[\s-]*ring\s*pick|真空脂|Krytox|扭矩|torque|扳手|wrench)',
                    re.IGNORECASE
                )
                for m in tool_pattern.finditer(combined):
                    key = m.group(0).upper().replace(' ', '_')
                    self.keyword_index[f"TOOL:{key}"].append((fname, idx))
                    self._section_index["工具"].add((fname, idx, sec["heading"]))

                # 3. 数值/标准索引
                spec_pattern = re.compile(
                    r'(\d+(?:\.\d+)?\s*(?:°C|ppm|Torr|mTorr|MΩ|mm|μm|nm|sccm|'
                    r'mbar|L/s|VSWR|hours?|min|分钟|小时)\b)',
                    re.IGNORECASE
                )
                for m in spec_pattern.finditer(combined):
                    self.keyword_index["SPEC:NUMERIC"].append((fname, idx))

                # 4. 中文 SOP 概念 (长词优先)
                cn_pattern = re.compile(
                    r'(安全准备|腔体清洁|消耗件更换|部件检查|恢复与验证|记录与签核|'
                    r'上电极|静电卡盘|聚焦环|边缘环|密封圈|涡轮分子泵|干泵|'
                    r'工艺气体|RF系统|真空系统|匹配网络|终点检测|'
                    r'基础真空|漏率测试|Seasoning|Monitor Wafer|'
                    r'维护类型|预计工时|所需人员|文件编号|版本|生效日期|'
                    r'周保养|月保养|季保养|年度保养|PM|preventive maintenance)',
                    re.IGNORECASE
                )
                for m in cn_pattern.finditer(combined):
                    concept = m.group(0)
                    self.keyword_index[f"CONCEPT:{concept}"].append((fname, idx))

                # 5. 按概念词索引
                for concept, synonyms in SOPQConfig.CONCEPT_SYNONYMS.items():
                    for syn in synonyms:
                        if syn.lower() in combined:
                            self._section_index[concept].add((fname, idx, sec["heading"]))
                            break

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        多策略混合检索

        策略顺序:
          1. 精确术语匹配 (安全/工具/概念)
          2. 中文语义概念映射
          3. 关键字密度匹配
          4. 章节层级提权
        """
        if top_k is None:
            top_k = SOPQConfig.TOP_K
        results = []
        seen = set()
        ql = query.lower()

        # ── Strategy 1: 精确术语命中 ──
        all_keywords = []
        for kw_list in SOPQConfig.SOP_KEYWORDS.values():
            all_keywords.extend(kw_list)
        # dedup + longest first
        all_keywords = sorted(set(all_keywords), key=len, reverse=True)

        for kw in all_keywords:
            if kw.lower() in ql:
                # search in keyword_index
                for idx_key, entries in self.keyword_index.items():
                    if kw.upper() in idx_key:
                        for fname, sec_idx in entries:
                            k = (fname, sec_idx)
                            if k not in seen:
                                seen.add(k)
                                sec = self.sections[fname][sec_idx]
                                results.append({
                                    "filename": fname,
                                    "heading": sec["heading"],
                                    "level": sec["level"],
                                    "section_num": sec.get("section_num", ""),
                                    "content": sec["content"],
                                    "score": 0.95,
                                    "match_type": f"exact:{kw}",
                                })

        # ── Strategy 2: 概念语义匹配 ──
        for concept, synonyms in SOPQConfig.CONCEPT_SYNONYMS.items():
            if any(s.lower() in ql for s in synonyms):
                for fname, secs in self.sections.items():
                    for idx, sec in enumerate(secs):
                        k = (fname, idx)
                        if k in seen:
                            continue
                        combined = (sec["heading"] + " " + sec["content"]).lower()
                        hits = sum(1 for s in synonyms if s.lower() in combined)
                        if hits >= 2:
                            seen.add(k)
                            results.append({
                                "filename": fname,
                                "heading": sec["heading"],
                                "level": sec["level"],
                                "section_num": sec.get("section_num", ""),
                                "content": sec["content"],
                                "score": 0.65 + 0.05 * min(hits, 6),
                                "match_type": f"concept:{concept}",
                            })

        # ── Strategy 3: 关键词密度匹配 ──
        query_words = set(re.findall(r'[a-zA-Z]{3,}|[一-鿿]{2,}', ql))
        if len(results) < 3:
            for fname, secs in self.sections.items():
                for idx, sec in enumerate(secs):
                    k = (fname, idx)
                    if k in seen:
                        continue
                    combined = (sec["heading"] + " " + sec["content"]).lower()
                    hits = sum(1 for w in query_words if w in combined)
                    if hits >= 3:
                        seen.add(k)
                        results.append({
                            "filename": fname,
                            "heading": sec["heading"],
                            "level": sec["level"],
                            "section_num": sec.get("section_num", ""),
                            "content": sec["content"],
                            "score": 0.35 + 0.05 * min(hits, 10),
                            "match_type": "keyword_density",
                        })

        # ── Strategy 4: 章节层级提权 ──
        # Higher-level sections (closer to chapter headings) get a boost
        for r in results:
            lv = r.get("level", 3)
            r["score"] += (4 - lv) * 0.02  # level 1: +0.06, level 2: +0.04, level 3: +0.02

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def search_section(self, section_num: str) -> Optional[Dict]:
        """精确查找某个章节号 (如 '2.1', '3.1.2')"""
        for fname, secs in self.sections.items():
            for sec in secs:
                if sec.get("section_num", "") == section_num:
                    return {
                        "filename": fname,
                        **sec,
                        "score": 1.0,
                        "match_type": "section_lookup",
                    }
        return None

    def build_context(self, query: str, top_k: int = None) -> str:
        """构建检索上下文 (注入 LLM prompt 的)"""
        results = self.search(query, top_k)
        if not results:
            return ""

        parts = ["# SOP 知识库检索上下文\n"]

        by_file = defaultdict(list)
        for r in results:
            by_file[r["filename"]].append(r)

        for fname, entries in by_file.items():
            parts.append(f"## 来源: {fname}\n")
            for e in entries[:5]:
                sn = f" ({e.get('section_num', '')})" if e.get('section_num') else ""
                parts.append(
                    f"### {e['heading']}{sn} "
                    f"(相关度: {e['score']:.0%}, 匹配: {e.get('match_type', 'unknown')})\n"
                )
                # truncate long sections
                content = e["content"]
                if len(content) > 1000:
                    content = content[:1000] + "\n... (内容截断)"
                parts.append(content)
                parts.append("\n---\n")

        return "\n".join(parts)

    def build_structured_result(self, query: str, top_k: int = None) -> List[Dict]:
        """返回结构化检索结果 (用于前端展示)"""
        results = self.search(query, top_k)
        return [
            {
                "rank": i + 1,
                "source": r["filename"],
                "section": r.get("section_num", ""),
                "heading": r["heading"],
                "content": r["content"][:500],
                "score": round(r["score"], 3),
                "match_type": r["match_type"],
            }
            for i, r in enumerate(results)
        ]

    def get_stats(self) -> Dict:
        return {
            "documents": len(self.documents),
            "sections": sum(len(s) for s in self.sections.values()),
            "keywords": len(self.keyword_index),
            "concepts": len(self._section_index),
            "files": list(self.documents.keys()),
        }

    def list_safety_items(self) -> List[Dict]:
        """列出所有安全相关条目"""
        items = []
        seen = set()
        for fname, idx, heading in self._section_index.get("安全", set()):
            key = (fname, idx)
            if key in seen:
                continue
            seen.add(key)
            sec = self.sections[fname][idx]
            items.append({
                "source": fname,
                "section": sec.get("section_num", ""),
                "heading": heading,
                "content": sec["content"][:300],
            })
        return items

    def list_tools(self) -> List[str]:
        """列出所有识别到的工具"""
        tools = set()
        for idx_key in self.keyword_index:
            if idx_key.startswith("TOOL:"):
                tools.add(idx_key[5:].replace('_', ' '))
        return sorted(tools)
