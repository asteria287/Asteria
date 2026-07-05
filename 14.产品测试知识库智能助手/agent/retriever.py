"""
产品测试知识库检索器 — 多策略混合检索
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from .config import TestKBConfig


class TestKBRetriever:
    """产品测试知识库检索器"""

    def __init__(self):
        self.kb_dir = TestKBConfig.KB_DIR
        self.documents: Dict[str, str] = {}
        self.sections: Dict[str, List[Dict]] = {}
        self.keyword_index: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self._term_index: Dict[str, Dict] = {}  # 术语精确索引

        self._load()
        self._parse_sections()
        self._build_index()
        self._build_term_index()

    def _load(self):
        for fname in TestKBConfig.KB_FILES:
            fp = self.kb_dir / fname
            if fp.exists():
                try:
                    self.documents[fname] = fp.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    self.documents[fname] = fp.read_text(encoding="gbk")

    def _parse_sections(self):
        heading_re = re.compile(r'^(#{1,4})\s+(.+)$', re.MULTILINE)
        for fname, content in self.documents.items():
            self.sections[fname] = []
            lines = content.split('\n')
            cur_h, cur_buf = "前言", []
            for line in lines:
                m = heading_re.match(line)
                if m:
                    if cur_buf:
                        self.sections[fname].append({
                            "heading": cur_h, "level": len(m.group(1)),
                            "content": '\n'.join(cur_buf).strip(),
                        })
                    cur_h = m.group(2).strip()
                    cur_buf = []
                else:
                    cur_buf.append(line)
            if cur_buf:
                self.sections[fname].append({
                    "heading": cur_h, "level": 1,
                    "content": '\n'.join(cur_buf).strip(),
                })

    def _build_index(self):
        for fname, secs in self.sections.items():
            for idx, sec in enumerate(secs):
                combined = (sec["heading"] + " " + sec["content"]).lower()

                # Test-specific keywords
                all_kw = []
                for phase, kws in TestKBConfig.TEST_PHASES.items():
                    all_kw.extend(kws)
                for cat, kws in TestKBConfig.TERM_CATEGORIES.items():
                    all_kw.extend(kws)
                all_kw = sorted(set(all_kw), key=len, reverse=True)

                for kw in all_kw:
                    if kw.lower() in combined:
                        self.keyword_index[kw.upper()].append((fname, idx))

                # Chinese concept indexing
                cn_terms = set(re.findall(
                    r'(晶圆测试|封装测试|系统级测试|探针卡|探针台|分选机|测试座|'
                    r'负载板|老化测试|良率|漏电流|接触电阻|时序参数|'
                    r'开短路|功能测试|直流测试|交流测试|BIST|内建自测试|'
                    r'测试程式|测试程序|工艺角|相关性|重测率|吞吐率)',
                    combined
                ))
                for t in cn_terms:
                    self.keyword_index[t].append((fname, idx))

    def _build_term_index(self):
        """构建术语精确索引 (从 test_terminology.md 解析)"""
        if "test_terminology.md" not in self.sections:
            return

        for sec in self.sections["test_terminology.md"]:
            content = sec["content"]
            heading = sec["heading"]
            if not heading or heading == "前言":
                continue

            # Parse term definition block
            term_name = heading.strip()
            # Store both with-space and without-space keys
            key = term_name.lower()
            key_nospace = key.replace(" ", "").replace("-", "").replace("/", "")
            entry = {"term": term_name, "full_content": content}
            self._term_index[key] = entry
            if key_nospace != key:
                self._term_index[key_nospace] = entry

            # Also index by acronyms in content
            for line in content.split('\n'):
                m = re.match(r'-\s*\*\*全称\*\*:\s*(.+)', line)
                if m:
                    self._term_index[term_name.lower()]["full_name"] = m.group(1).strip()
                m = re.match(r'-\s*\*\*测试阶段\*\*:\s*(.+)', line)
                if m:
                    self._term_index[term_name.lower()]["phase"] = m.group(1).strip()

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        if top_k is None:
            top_k = TestKBConfig.TOP_K
        results = []
        seen = set()
        ql = query.lower()

        # Strategy 1: Exact keyword match
        all_kw = []
        for kws in list(TestKBConfig.TEST_PHASES.values()) + list(TestKBConfig.TERM_CATEGORIES.values()):
            all_kw.extend(kws)
        all_kw = sorted(set(all_kw), key=len, reverse=True)

        for kw in all_kw:
            if kw.lower() in ql:
                for fname, idx in self.keyword_index.get(kw.upper(), []):
                    k = (fname, idx)
                    if k not in seen:
                        seen.add(k)
                        sec = self.sections[fname][idx]
                        results.append({
                            "filename": fname, "heading": sec["heading"],
                            "content": sec["content"][:1200],
                            "score": 0.95, "match_type": f"exact:{kw}",
                        })

        # Strategy 2: Chinese concept semantic
        phases = TestKBConfig.detect_phase(query)
        for fname, secs in self.sections.items():
            phase_match = any(
                p.lower() in fname.lower() or
                any(kw.lower() in fname.lower() for kw in TestKBConfig.TEST_PHASES.get(p, []))
                for p in phases
            )
            for idx, sec in enumerate(secs):
                k = (fname, idx)
                if k in seen:
                    continue
                combined = (sec["heading"] + " " + sec["content"]).lower()
                if phase_match:
                    query_words = set(re.findall(r'[a-zA-Z]{3,}|[一-鿿]{2,}', ql))
                    hits = sum(1 for w in query_words if w in combined)
                    if hits >= 2:
                        seen.add(k)
                        results.append({
                            "filename": fname, "heading": sec["heading"],
                            "content": sec["content"][:1200],
                            "score": 0.65 + 0.05 * min(hits, 6),
                            "match_type": f"semantic:{','.join(phases)}",
                        })

        # Strategy 3: Keyword density fallback
        if len(results) < 3:
            for fname, secs in self.sections.items():
                for idx, sec in enumerate(secs):
                    k = (fname, idx)
                    if k in seen:
                        continue
                    combined = (sec["heading"] + " " + sec["content"]).lower()
                    query_words = set(re.findall(r'[a-zA-Z]{3,}|[一-鿿]{2,}', ql))
                    hits = sum(1 for w in query_words if w in combined)
                    if hits >= 3:
                        seen.add(k)
                        results.append({
                            "filename": fname, "heading": sec["heading"],
                            "content": sec["content"][:1200],
                            "score": 0.35 + 0.05 * min(hits, 10),
                            "match_type": "density",
                        })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def search_term(self, term: str) -> Dict:
        """精确术语查询 — 支持带/不带空格"""
        term_lower = term.lower().strip()
        term_nospace = term_lower.replace(" ", "").replace("-", "").replace("/", "")

        # Try exact match first
        if term_lower in self._term_index:
            return {"found": True, **self._term_index[term_lower]}
        if term_nospace in self._term_index:
            return {"found": True, **self._term_index[term_nospace]}

        # Fuzzy: substring match on normalized keys
        for key, val in self._term_index.items():
            kn = key.replace(" ", "").replace("-", "").replace("/", "")
            if term_nospace in kn or kn in term_nospace:
                return {"found": True, "fuzzy_match": key, **val}

        return {"found": False, "term": term}

    def build_context(self, query: str, top_k: int = None) -> str:
        results = self.search(query, top_k)
        if not results:
            return ""
        parts = ["# 产品测试知识库检索上下文\n"]
        by_file = defaultdict(list)
        for r in results:
            by_file[r["filename"]].append(r)
        for fname, entries in by_file.items():
            parts.append(f"## {fname}\n")
            for e in entries[:4]:
                parts.append(f"### {e['heading']} (相关度: {e['score']:.0%})\n")
                parts.append(e["content"][:800])
                parts.append("\n---\n")
        return "\n".join(parts)

    def get_stats(self) -> Dict:
        return {
            "documents": len(self.documents),
            "sections": sum(len(s) for s in self.sections.values()),
            "keywords": len(self.keyword_index),
            "terms": len(self._term_index),
            "files": list(self.documents.keys()),
        }
