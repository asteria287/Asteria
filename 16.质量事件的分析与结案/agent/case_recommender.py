"""
相似案例推荐引擎 — 基于关键词匹配 + 语义相似度
"""
import re
from pathlib import Path
from typing import Dict, List
from .config import QRAConfig


class CaseRecommender:
    """质量事件案例推荐器"""

    def __init__(self):
        self.case_lib_path = QRAConfig.KB_DIR / "case_library.md"
        self.cases = self._load_cases()

    def _load_cases(self) -> Dict:
        """加载案例库 → {case_id: {title, 5w1h, 8d, keywords}}"""
        if not self.case_lib_path.exists():
            return {}

        text = self.case_lib_path.read_text(encoding="utf-8")
        cases = {}
        current_id = None
        current_data = {"title": "", "keywords": [], "content": ""}

        for line in text.split('\n'):
            if line.startswith('## 案例'):
                if current_id:
                    cases[current_id] = current_data
                # Extract case ID
                m = re.match(r'## 案例(\d+):\s*(.+)', line)
                if m:
                    current_id = f"case{m.group(1)}"
                    current_data = {"title": m.group(2), "keywords": [], "content": line + "\n"}
                else:
                    current_id = None
                    current_data = {"title": "", "keywords": [], "content": ""}
            elif current_id:
                current_data["content"] += line + "\n"
                if line.startswith('### 关键词') or line.startswith('**关键词**'):
                    kw_match = re.findall(r'[\w\-]+', line)
                    current_data["keywords"] = [k for k in kw_match if len(k) > 2 and not k.startswith('###')]

        if current_id:
            cases[current_id] = current_data

        return cases

    def recommend(self, query: str, top_k: int = 3) -> List[Dict]:
        """根据问题描述推荐相似案例"""
        if not self.cases:
            return []

        ql = query.lower()
        scores = {}
        for cid, case in self.cases.items():
            score = 0
            content_lower = case["content"].lower()

            # Keyword matching
            for kw in case.get("keywords", []):
                if kw.lower() in ql:
                    score += 2.0
                if kw.lower() in content_lower:
                    score += 0.1  # small bonus for each keyword in case

            # Semantic dimension matching
            dims = {
                "cp": ["cp", "探针", "probe", "晶圆", "wafer", "针尖", "接触电阻"],
                "ft": ["ft", "handler", "socket", "分选", "重测", "jam", "机械"],
                "slt": ["slt", "burn-in", "老化", "fw", "固件", "时序", "ddr", "dppm"],
            }
            for dim, kws in dims.items():
                if any(kw.lower() in ql for kw in kws) and any(kw.lower() in content_lower for kw in kws):
                    score += 1.5

            # Content density
            query_words = set(re.findall(r'[a-zA-Z]{3,}|[一-鿿]{2,}', ql))
            hits = sum(1 for w in query_words if w in content_lower)
            score += hits * 0.3

            scores[cid] = round(score, 1)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for cid, score in ranked[:top_k]:
            case = self.cases[cid]
            # Extract 5W1H summary
            summary = ""
            m = re.search(r'### 8D 摘要.*?(?=### 关键词|\Z)', case["content"], re.DOTALL)
            if m:
                summary = m.group(0)[:500]

            result.append({
                "case_id": cid, "title": case["title"],
                "score": score, "keywords": case.get("keywords", [])[:8],
                "summary": summary.strip(),
            })
        return result

    def get_case_detail(self, case_id: str) -> Dict:
        """获取案例完整详情(5W1H + 8D)"""
        case = self.cases.get(case_id, {})
        return {"case_id": case_id, "title": case.get("title", ""), "content": case.get("content", "")}
