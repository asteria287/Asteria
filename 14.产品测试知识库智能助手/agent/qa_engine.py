"""
产品测试知识库 Q&A 引擎
"""
import time
from pathlib import Path
from datetime import date
from typing import Dict, Optional, Callable
from .config import TestKBConfig
from .retriever import TestKBRetriever
from prompts.test_prompts import build_qa_prompt


class TestQAEngine:
    """产品测试知识库 Q&A 引擎"""

    def __init__(self):
        self.retriever = TestKBRetriever()
        self.config = TestKBConfig

    @property
    def is_available(self) -> bool:
        return self.config.is_available()

    def ask(self, question: str, mode: str = "qa",
            stream_callback: Optional[Callable] = None,
            save_note: bool = True) -> Dict:
        """主问答入口"""
        start = time.time()

        # Detect test phase
        phases = TestKBConfig.detect_phase(question)

        # Retrieve
        context = self.retriever.build_context(question)
        kb_stats = self.retriever.get_stats()

        # Build prompt
        system_prompt, user_prompt = build_qa_prompt(question, context, phases, mode)

        # LLM or offline
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
                        model=self.config.MODEL, max_tokens=self.config.MAX_TOKENS,
                        temperature=self.config.TEMPERATURE,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    ) as stream:
                        for text in stream.text_stream:
                            answer += text
                            stream_callback(text)
                else:
                    resp = client.messages.create(
                        model=self.config.MODEL, max_tokens=self.config.MAX_TOKENS,
                        temperature=self.config.TEMPERATURE,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                    for block in resp.content:
                        if hasattr(block, 'text'):
                            answer += block.text
                    tokens = {"input": resp.usage.input_tokens, "output": resp.usage.output_tokens}
            except Exception as e:
                answer = f"[LLM 调用失败: {e}]\n\n## 知识库检索结果\n\n{context}"
        else:
            answer = self._offline_answer(question, context, phases)

        elapsed = time.time() - start

        result = {
            "question": question, "answer": answer, "context": context,
            "phases": phases, "kb_stats": kb_stats,
            "tokens_used": tokens, "elapsed": round(elapsed, 2),
            "note_path": None,
        }

        if save_note and answer:
            result["note_path"] = str(self._save_note(question, answer))

        return result

    def _offline_answer(self, question: str, context: str, phases: list) -> str:
        lines = [
            "# 产品测试知识问答 (离线模式)",
            f"\n> ⚠️ API Key 未配置, 以下为知识库检索结果。涉及阶段: {', '.join(phases)}",
            f"\n## Query: {question}\n",
            context if context else "未检索到相关内容",
            "\n---\n*配置 ANTHROPIC_API_KEY 启用 AI 深度解读.*",
        ]
        return "\n".join(lines)

    def _save_note(self, question: str, answer: str) -> Path:
        today = date.today().isoformat()
        title = question[:40].replace("?", "").replace("？", "").strip()
        safe = "".join(c if c.isalnum() or c in '-_' else '_' for c in title)
        filepath = TestKBConfig.WORKSPACE_DIR / f"测试知识问答_{safe}_{today}.md"
        note = f"""# 产品测试知识问答

> **日期**: {today} | **引擎**: 产品测试知识库 + AI

## Query
{question}

---
{answer}

---
*由产品测试知识库智能助手生成*
"""
        filepath.write_text(note, encoding="utf-8")
        return filepath
