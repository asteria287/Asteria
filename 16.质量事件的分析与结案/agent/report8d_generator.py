"""
8D报告生成器 — 基于案例数据填充8D模板
"""
from pathlib import Path
from datetime import date
from typing import Dict
from .config import QRAConfig


class Report8DGenerator:
    """8D报告生成器"""

    def __init__(self):
        self.template_path = QRAConfig.KB_DIR / "8d_template.md"
        self.template = ""
        if self.template_path.exists():
            self.template = self.template_path.read_text(encoding="utf-8")

    def generate_8d(self, case_data: Dict, output_dir: Path = None) -> str:
        """
        基于案例数据填充8D报告

        Args:
            case_data: {case_id, title, 5w1h, 8d_sections, rootcause_analysis}
            output_dir: 输出目录
        """
        title = case_data.get("title", "未标题")
        today = date.today().isoformat()

        # Parse existing 8D sections from case
        eight_d = case_data.get("8d_sections", {})
        five_w = case_data.get("5w1h", {})
        team = case_data.get("team", {})
        rootcause = case_data.get("rootcause_analysis", {})

        report = f"""# 8D 报告: {title}

> **8D编号**: 8D-{today.replace('-', '')}-{case_data.get('case_id', 'XXX')}
> **结案日期**: {today}
> **状态**: Closed ✅

---

## D1 — 团队组建

| 角色 | 姓名 | 部门 |
|------|------|------|
| 组长 | {team.get('lead', '')} | |
| 技术专家 | {team.get('tech', '')} | |
| QRA代表 | {team.get('qra', '')} | QRA |
| 其他 | {team.get('others', '')} | |

---

## D2 — 问题描述 (5W+1H)

| 维度 | 描述 |
|------|------|
| **Who** | {five_w.get('who', '')} |
| **What** | {five_w.get('what', '')} |
| **When** | {five_w.get('when', '')} |
| **Where** | {five_w.get('where', '')} |
| **Why** | {five_w.get('why', '')} |
| **How** | {five_w.get('how', '')} |

### IS / IS NOT

{case_data.get('is_isnot', '')}

---

## D3 — 遏制措施

{eight_d.get('d3', '')}

---

## D4 — 根因分析

### 5-Why

```
{rootcause.get('five_why', '')}
```

### 鱼骨图分析

{rootcause.get('ishikawa', '')}

**根因结论**: {rootcause.get('conclusion', '')}

---

## D5 — 纠正措施

{eight_d.get('d5', '')}

---

## D6 — 验证

{eight_d.get('d6', '')}

---

## D7 — 预防措施

{eight_d.get('d7', '')}

### Lessons Learned
{rootcause.get('lessons', '')}

---

## D8 — 结案与分享

| 项目 | 状态 |
|------|:---:|
| 所有措施已完成并验证 | ✅ |
| 8D报告已完成 | ✅ |
| 案例归档至QRA案例库 | ✅ |
| 团队分享完成 | ✅ |
| 横向展开检查 | ✅ |

**签核**: 组长: _____ | QRA主管: _____ | 日期: {today}

---

*本8D报告由QRA质量事件分析助手自动生成。基于8D标准模板+案例库数据。*
"""

        if output_dir:
            safe = case_data.get("case_id", "case")
            path = output_dir / f"8D报告_{safe}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(report, encoding="utf-8")
            return str(path)
        return report

    def generate_workspace_record(self, case_id: str, case_data: Dict,
                                  recommendations: list) -> str:
        """生成 Workspace 过程记录"""
        today = date.today().isoformat()
        title = case_data.get("title", case_id)

        rec_text = "\n".join(
            f"  #{i+1} [{r['case_id']}] {r['title']} (相似度: {r['score']:.1f})"
            for i, r in enumerate(recommendations)
        ) if recommendations else "  (无推荐)"

        return f"""# QRA 案件登记 — {title}

> **登记日期**: {today} | **案件编号**: {case_id}
> **当前阶段**: 8D完成 ✅

---

## 5W+1H 案件登记

{case_data.get('5w1h_formatted', '')}

---

## 相似案例推荐 (AI)

{rec_text}

---

## 8D 报告摘要

{case_data.get('8d_summary', '')}

---

*过程记录由QRA质量事件分析助手自动生成。*
"""
