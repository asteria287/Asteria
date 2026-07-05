"""
产品测试术语解析引擎 — 能力2: 术语定义 + 阶段 + 关联参数 + 场景
"""
from typing import Dict
from .config import TestKBConfig
from .retriever import TestKBRetriever


class TerminologyEngine:
    """术语解析引擎"""

    def __init__(self):
        self.retriever = TestKBRetriever()

    def _normalize(self, s: str) -> str:
        """标准化术语: 去空格, 小写"""
        return s.replace(" ", "").replace("-", "").replace("/", "").lower()

    def lookup(self, term: str) -> Dict:
        """
        术语查询 → 结构化解析

        Returns:
            {
                "term": str,
                "found": bool,
                "definition": str,
                "full_name": str,
                "test_phase": str,
                "related_params": [str],
                "scenarios": [str],
                "source": str,
                "see_also": [str],
            }
        """
        result = {
            "term": term,
            "found": False,
            "definition": "",
            "full_name": "",
            "test_phase": "",
            "related_params": [],
            "scenarios": [],
            "source": "",
            "see_also": [],
        }

        # 1. 精确匹配 (标准化空格)
        t_norm = self._normalize(term)
        term_info = self.retriever.search_term(term)

        # Also try normalized key lookup
        if not term_info.get("found"):
            for key, val in self.retriever._term_index.items():
                if self._normalize(key) == t_norm:
                    term_info = {"found": True, **val}
                    break

        if term_info.get("found"):
            result["found"] = True
            result["term"] = term_info.get("term", term)
            result["full_name"] = term_info.get("full_name", "")
            result["test_phase"] = term_info.get("phase", "")
            result["source"] = "test_terminology.md"

            # Parse related params and scenarios from content
            content = term_info.get("full_content", "")
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith("- **关联参数**:") or line.startswith("- **关联参数**:"):
                    params_str = line.split(":", 1)[-1].strip()
                    result["related_params"] = [p.strip() for p in params_str.split(",") if p.strip()]
                if line.startswith("- **应用场景**:") or line.startswith("- **应用场景**:"):
                    scenes_str = line.split(":", 1)[-1].strip()
                    result["scenarios"] = [s.strip() for s in scenes_str.split(",") if s.strip()]
                if line.startswith("- **定义**:") or line.startswith("- **定义**:"):
                    result["definition"] = line.split(":", 1)[-1].strip()
                if line.startswith("- **常见设备**:") or line.startswith("- **常见设备**:"):
                    result["see_also"].append(line.split(":", 1)[-1].strip())

        # 2. 知识库模糊检索 (补充)
        context = self.retriever.build_context(term, top_k=3)
        if context and not result["definition"]:
            result["found"] = True
            result["definition"] = f"从知识库检索: {context[:500]}"
            result["source"] = "知识库检索"

        # 3. 推断测试阶段
        if not result["test_phase"]:
            phases = TestKBConfig.detect_phase(term)
            result["test_phase"] = ", ".join(phases)

        return result

    def format_lookup_result(self, result: Dict) -> str:
        """格式化术语查询结果为可读文本"""
        if not result["found"]:
            return f"## 术语: {result['term']}\n\n> ⚠️ 未在知识库中找到该术语。请检查拼写或尝试其他关键词。"

        lines = [
            f"## 术语解析: {result['term']}",
            "",
        ]

        if result.get("full_name"):
            lines.append(f"**全称**: {result['full_name']}")
            lines.append("")

        if result.get("test_phase"):
            lines.append(f"**测试阶段**: {result['test_phase']}")
            lines.append("")

        if result.get("definition"):
            lines.append(f"**定义**: {result['definition']}")
            lines.append("")

        if result.get("related_params"):
            lines.append("**关联参数**:")
            for p in result["related_params"]:
                lines.append(f"  - {p}")
            lines.append("")

        if result.get("scenarios"):
            lines.append("**常见应用场景**:")
            for s in result["scenarios"]:
                lines.append(f"  - {s}")
            lines.append("")

        if result.get("see_also"):
            lines.append("**相关设备/参考**:")
            for s in result["see_also"]:
                lines.append(f"  - {s}")
            lines.append("")

        if result.get("source"):
            lines.append(f"\n> 来源: {result['source']}")

        return "\n".join(lines)
