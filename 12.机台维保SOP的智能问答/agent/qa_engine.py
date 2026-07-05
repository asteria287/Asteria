"""
SOP 智能问答引擎 — 检索 + LLM 分析 + 笔记生成
"""
import json
import time
from pathlib import Path
from datetime import date
from typing import Dict, Optional, Callable, List
from .config import SOPQConfig
from .sop_retriever import SOPRetriever
from prompts.sop_prompts import build_prompt


class SOPQAEngine:
    """SOP 智能问答引擎"""

    def __init__(self):
        self.retriever = SOPRetriever()
        self.config = SOPQConfig

    @property
    def is_available(self) -> bool:
        return self.config.is_available()

    def query(self, question: str, mode: str = "qa",
              stream_callback: Optional[Callable] = None,
              save_note: bool = True) -> Dict:
        """
        主入口: 用户 Query → SOP 知识库检索 → LLM 分析 → 结构化回答

        Args:
            question: 用户的 SOP 相关问题
            mode: "qa" (标准) | "quick" (快速) | "overview" (概览) | "compare" (对比)
            stream_callback: 流式输出回调
            save_note: 是否保存到 workspace

        Returns:
            {
                "question": str,
                "answer": str,
                "context": str,
                "kb_stats": dict,
                "retrieved_sections": list,
                "note_path": str (if save_note),
                "tokens_used": dict,
                "elapsed": float,
            }
        """
        start = time.time()

        # Step 1: 检索 SOP 知识库
        context = self.retriever.build_context(question)
        kb_stats = self.retriever.get_stats()
        retrieved = self.retriever.build_structured_result(question)

        # Step 2: 构建 Prompt
        system_prompt, user_prompt = build_prompt(question, context, mode)

        # Step 3: 调用 LLM 或离线模式
        answer = ""
        tokens = {"input": 0, "output": 0}

        if self.is_available:
            try:
                import anthropic
                kwargs = {"api_key": self.config.get_api_key(), "timeout": 300.0}
                base_url = self.config.get_base_url()
                if base_url:
                    kwargs["base_url"] = base_url
                client = anthropic.Anthropic(**kwargs)

                if stream_callback:
                    with client.messages.stream(
                        model=self.config.MODEL,
                        max_tokens=self.config.MAX_TOKENS,
                        temperature=self.config.TEMPERATURE,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    ) as stream:
                        for text in stream.text_stream:
                            answer += text
                            stream_callback(text)
                else:
                    resp = client.messages.create(
                        model=self.config.MODEL,
                        max_tokens=self.config.MAX_TOKENS,
                        temperature=self.config.TEMPERATURE,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                    answer = ""
                    for block in resp.content:
                        if hasattr(block, 'text'):
                            answer += block.text
                    tokens["input"] = resp.usage.input_tokens
                    tokens["output"] = resp.usage.output_tokens

            except Exception as e:
                answer = (
                    f"[LLM 调用失败: {str(e)}]\n\n"
                    f"## SOP 知识库检索结果 (离线模式)\n\n{context}"
                )
        else:
            # 离线模式
            answer = self._offline_answer(question, context)

        elapsed = time.time() - start

        result = {
            "question": question,
            "answer": answer,
            "context": context,
            "kb_stats": kb_stats,
            "retrieved_sections": retrieved,
            "tokens_used": tokens,
            "elapsed": round(elapsed, 2),
            "note_path": None,
        }

        # Step 4: 保存 workspace 笔记
        if save_note and answer:
            note_path = self._save_note(question, answer, context, retrieved)
            result["note_path"] = str(note_path)

        return result

    def _offline_answer(self, question: str, context: str) -> str:
        """离线模式: 返回结构化 SOP 检索结果"""
        lines = [
            "# SOP 智能问答 (离线模式)",
            "",
            "> ⚠️ ANTHROPIC_API_KEY 未配置, 以下为 SOP 知识库检索结果。",
            "> 配置 API Key 后可获得 AI 智能分析和完整 SOP 回答。",
            "",
            f"## 您的问题: {question}",
            "",
        ]

        if context:
            lines.append(context)
        else:
            lines.append("（未检索到相关 SOP 内容，请检查知识库中是否已导入相关 SOP 文档）")

        lines.extend([
            "",
            "---",
            "*离线模式: 上述为知识库匹配结果。配置 .env 中的 ANTHROPIC_API_KEY 启用 AI 问答。*",
        ])
        return "\n".join(lines)

    def _save_note(self, question: str, answer: str, context: str,
                   retrieved: List[Dict]) -> Path:
        """保存 workspace 笔记"""
        today = date.today().isoformat()

        # 从 question 提取简短标题
        title = question[:50].replace("?", "").replace("？", "").replace("/", "-").strip()
        if len(title) > 50:
            title = title[:47] + "..."

        safe_title = "".join(c if c.isalnum() or c in '-_' else '_' for c in title)
        filename = f"SOP_问答_{safe_title}_{today}.md"
        filepath = SOPQConfig.WORKSPACE_DIR / filename

        # 生成来源追溯表
        source_rows = []
        for r in (retrieved or [])[:10]:
            source_rows.append(
                f"| {r['rank']} | {r['source']} | {r.get('section', '')} {r['heading']} "
                f"| {r['score']:.0%} |"
            )

        note_content = f"""# SOP 智能问答笔记

> **创建日期**: {today}
> **分析引擎**: SOP 智能问答 (Claude + SOP 知识库)
> **知识库**: {len(self.retriever.documents)} 文档, {sum(len(s) for s in self.retriever.sections.values())} 章节

---

## 用户问题

{question}

---

{answer}

---

## 检索来源追溯

| # | 来源文件 | 章节 | 相关度 |
|---|----------|------|--------|
{chr(10).join(source_rows) if source_rows else '（无检索结果）'}

---

## SOP 知识库检索原始上下文

<details>
<summary>展开查看完整检索上下文</summary>

{context[:3000] if context else '（无上下文）'}

</details>

---

*本笔记由 SOP 智能问答自动生成。所有 SOP 引用可追溯至原始文档。*
"""
        filepath.write_text(note_content, encoding="utf-8")
        return filepath

    def get_safety_checks(self, topic: str = "") -> List[Dict]:
        """快速获取指定主题的安全检查项"""
        all_safety = self.retriever.list_safety_items()
        if topic:
            return [
                s for s in all_safety
                if topic.lower() in s["heading"].lower() or topic.lower() in s["content"].lower()
            ]
        return all_safety

    def get_tools_for_operation(self, operation: str = "") -> List[str]:
        """获取指定操作所需的工具"""
        context = self.retriever.build_context(operation) if operation else ""
        tools = self.retriever.list_tools()
        return tools
