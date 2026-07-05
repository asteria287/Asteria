"""
PCRB 报告生成器 — LLM 分析 + Workspace 笔记
"""
import time
from pathlib import Path
from datetime import date
from typing import Dict, Optional, Callable, List
from .config import PCRBConfig
from prompts.pcrb_prompts import build_report_prompt


class ReportGenerator:
    """PCRB 分析报告生成器"""

    def __init__(self):
        self.config = PCRBConfig

    @property
    def is_available(self) -> bool:
        return self.config.is_available()

    def generate_report(self,
                        analysis_result: Dict,
                        stream_callback: Optional[Callable] = None,
                        save_note: bool = True) -> Dict:
        """生成完整 PCRB 分析报告"""
        start = time.time()

        system_prompt, user_prompt = build_report_prompt(analysis_result)

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
                    for block in resp.content:
                        if hasattr(block, 'text'):
                            answer += block.text
                    tokens["input"] = resp.usage.input_tokens
                    tokens["output"] = resp.usage.output_tokens

            except Exception as e:
                answer = (f"[LLM 调用失败: {str(e)}]\n\n"
                          f"## PCRB 统计分析结果 (离线模式)\n\n"
                          f"请配置 ANTHROPIC_API_KEY 以生成 AI 分析报告。")
        else:
            answer = self._offline_report(analysis_result)

        elapsed = time.time() - start

        result = {
            "answer": answer,
            "tokens_used": tokens,
            "elapsed": round(elapsed, 2),
            "note_path": None,
        }

        if save_note:
            note_path = self._save_note(analysis_result, answer)
            result["note_path"] = str(note_path)

        return result

    def _offline_report(self, analysis_result: Dict) -> str:
        """离线模式报告"""
        summary = analysis_result.get("summary", {})
        selection = analysis_result.get("selection", {})
        comparison = analysis_result.get("comparison", {})

        lines = [
            "# PCRB 实验分析报告 (离线模式)",
            "",
            "> ⚠️ ANTHROPIC_API_KEY 未配置, 以下为统计计算结果。",
            "> 配置 API Key 后可获得 AI 按参数组类别的深度解读。",
            "",
            f"## 实验概况",
            f"- 总组数: {summary.get('total_groups', '?')}",
            f"- Baseline: {summary.get('baseline', '?')}",
            f"- 参数0: {summary.get('param0', '?')} (最优组判定依据)",
            f"- 总参数数: {summary.get('total_params', '?')}",
            f"- 参数组类别数: {summary.get('total_categories', '?')}",
            "",
            f"## 最优组: **{summary.get('best_group', '?')}**",
            f"- 判定: 参数0与Baseline最相近 (|Δ%|={summary.get('best_delta_pct', '?'):.2f}%)",
            "",
            "## 参数0对比排名",
            "| 排名 | 组名 | 参数0均值 | Baseline均值 | |Δ%| |",
            "|------|------|-----------|-------------|------|",
        ]
        for r in (selection.get("ranking") or []):
            lines.append(
                f"| {r['rank']} | {r['group']} | {r['param0_mean']:.4f} | "
                f"{r['baseline_mean']:.4f} | {r['delta_pct_abs']:.2f}% |"
            )

        if comparison:
            lines.append("")
            lines.append("## 按参数组类别 — 异常参数")
            for cat_name, cat_result in comparison.get("categories", {}).items():
                lines.append(f"\n### {cat_name}")
                lines.append(f"> {cat_result.get('desc', '')}")
                ma = cat_result.get("most_abnormal")
                if ma:
                    lines.append(
                        f"🔥 最异常: **{ma['param']}** "
                        f"(Z={ma['z_score']:.1f}, Δ={ma['delta_pct']:+.1f}%, d={ma['effect_size']:.2f})"
                    )
                for p_name, p in cat_result.get("params", {}).items():
                    sig = "✅" if p["significant"] else "➖"
                    lines.append(
                        f"  {sig} {p_name}: Δ={p['delta_pct']:+.1f}%, "
                        f"Z={p['z_score']:.1f}, p={p['p_value']:.4f}"
                    )

        lines.extend([
            "",
            "---",
            "*离线模式: 上述为统计计算结果。配置 ANTHROPIC_API_KEY 启用 AI 类别解读。*",
        ])
        return "\n".join(lines)

    def _save_note(self, analysis_result: Dict, answer: str) -> Path:
        """保存 workspace 笔记"""
        today = date.today().isoformat()
        summary = analysis_result.get("summary", {})
        best = summary.get("best_group", "unknown")
        filename = f"PCRB实验分析报告_{best}_{today}.md"
        filepath = PCRBConfig.WORKSPACE_DIR / filename

        note = f"""# PCRB 实验分析报告

> **分析日期**: {today}
> **分析引擎**: PCRB 实验分析助手 (统计分析 + Claude AI)
> **最优组**: {best} (参数0与Baseline最相近原则)

---

{answer}

---

*本报告由 PCRB 实验分析助手生成。最优组基于参数0与Baseline最相近原则选出。*
"""
        filepath.write_text(note, encoding="utf-8")
        return filepath
