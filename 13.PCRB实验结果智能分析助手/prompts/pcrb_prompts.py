"""
PCRB 实验分析 Prompt 模板 — 按参数组类别分析
"""
from datetime import date as dt_date


SYSTEM_PROMPT = """你是一位资深的半导体工艺工程师, 专精于 OP 部门的 PCRB (Process Condition Review Board) 实验数据分析。

## 你的专业领域:
- PCRB 实验设计与评审
- 半导体工艺参数分析: Vt/Id/Ioff/SS/DIBL/Vbd/寄生电容/良率/噪声
- 参数组(Category)解读: 每个工艺参数属于特定类别, 需按类别维度进行分析
- 统计方法: Z-score, t-test, ANOVA, Cohen's d Effect Size
- 工艺优化建议: 基于数据分析给出可操作的下一步实验方向

## 回答原则:
1. **按参数组(Category)组织分析**: 先说明该参数组的工艺意义, 再列出组内各参数变化
2. **数据驱动**: 严格基于提供的统计结果, 不编造数据
3. **工艺视角**: 从半导体工艺物理角度解释参数偏移
4. **异常优先**: 先分析显著异常的参数, 再概述正常参数
5. **中文输出**: 专业术语保留英文, 工艺概念用中文解释"""


REPORT_PROMPT = """请基于以下 PCRB 实验分析结果, 按参数组类别生成实验分析报告。

## 实验概况
- 总组数: {total_groups} (含Baseline: {baseline})
- 参数0: {param0} (用于最优组判定)
- 总参数数: {total_params}, 分为 {total_categories} 个参数组
- ANOVA 显著参数: {anova_sig_count}

## 最优组选择: {best_group}
- 判定依据: **参数0 ({param0}) 与Baseline最相近**
- 最优组 {param0}: mean={best_param0_mean}, Baseline mean={baseline_param0_mean}
- |Delta%|: {best_delta_pct}% (所有组中最小)

## 各实验组参数0对比
{ranking_text}

## 最优组按参数组的详细对比结果
{category_detail}

## 请按以下结构输出分析报告:

### 1. 最优组选择说明
- 判定标准: 参数0 ({param0}) 与Baseline平均值的|Delta%|最小
- 各实验组参数0对比排名
- 最优组 {best_group} vs Baseline 的 {param0} 对比

### 2. 按参数组类别分析 ({best_group} vs Baseline)

对每个参数组类别, 输出:

#### [类别名] — {{参数组工艺意义简述}}
- 📊 该类别共 N 个参数
- 📈 显著偏高参数: (列出参数名, delta%, Z-score, effect size, 工艺解读)
- 📉 显著偏低参数: (同上)
- 🔥 **最异常参数**: (该类别中Z-score最大的参数, 详细分析其工艺含义和可能根因)
- ➖ 无显著变化参数: (简述)

### 3. 跨类别Top异常参数排名
| 排名 | 参数 | 类别 | |Z-score| | |Delta%| | 方向 | 显著性 |
|------|------|------|---------|----------|------|--------|
(列出Top 10)

### 4. 箱体图关键发现
- Top异常参数的分布特征
- 组间离散度对比
- 离群值/异常样本提示

### 5. Benefit & Drawback 分析
- ✅ **Benefit**: 最优组相对Baseline改善的参数及工艺价值
- ⚠️ **Drawback**: 恶化的参数及潜在风险
- 🔬 **需关注**: 统计学显著但工艺含义待确认的变化

### 6. 综合总结描述
- 一段话总结本次PCRB实验的核心发现
- 最优组 {best_group} 的综合评价
- 工艺建议和下一步方向

## 输出要求:
- 按参数组类别逐类分析, 每类先定义工艺意义再分析数据
- 使用表格展示关键数据
- 中文输出, 专业术语保留英文
- 总字数: 1000-2500 字"""


def build_report_prompt(analysis_result: dict) -> tuple:
    """构建报告生成 Prompt"""
    summary = analysis_result.get("summary", {})
    selection = analysis_result.get("selection", {})
    comparison = analysis_result.get("comparison", {})

    # 排名文本
    ranking_lines = []
    for r in (selection.get("ranking") or []):
        ranking_lines.append(
            f"  #{r['rank']} {r['group']}: {r['param0_name']}={r['param0_mean']:.4f}, "
            f"Baseline={r['baseline_mean']:.4f}, |Δ%|={r['delta_pct_abs']:.2f}%"
        )
    ranking_text = '\n'.join(ranking_lines) if ranking_lines else "(无)"

    # 参数组详细结果
    cat_lines = []
    categories = comparison.get("categories", {})
    for cat_name, cat_result in categories.items():
        cat_lines.append(f"\n### 参数组: {cat_name}")
        cat_lines.append(f"描述: {cat_result.get('desc', '')}")

        # Most abnormal
        ma = cat_result.get("most_abnormal")
        if ma:
            cat_lines.append(
                f"🔥 最异常参数: {ma['param']} | "
                f"Z={ma['z_score']:.1f}, Δ={ma['delta_pct']:+.1f}%, "
                f"d={ma['effect_size']:.2f}, p={ma['p_value']:.4f}"
            )

        # All params
        for p_name, p in cat_result.get("params", {}).items():
            sig = "✅显著" if p["significant"] else "➖"
            cat_lines.append(
                f"  {sig} {p_name}: mean={p['mean']:.4f} (BL={p['baseline_mean']:.4f}), "
                f"Δ={p['delta_pct']:+.1f}%, Z={p['z_score']:.1f}, "
                f"d={p['effect_size']:.2f}, p={p['p_value']:.4f}"
            )

    category_detail = '\n'.join(cat_lines) if cat_lines else "(无)"

    best_param0_mean = "?"
    baseline_param0_mean = "?"
    if selection.get("ranking"):
        r0 = selection["ranking"][0]
        best_param0_mean = f"{r0['param0_mean']:.4f}"
        baseline_param0_mean = f"{r0['baseline_mean']:.4f}"

    user_prompt = REPORT_PROMPT.format(
        total_groups=summary.get("total_groups", "?"),
        baseline=summary.get("baseline", "?"),
        param0=summary.get("param0", "?"),
        total_params=summary.get("total_params", "?"),
        total_categories=summary.get("total_categories", "?"),
        anova_sig_count=summary.get("anova_significant_params", 0),
        best_group=summary.get("best_group", "?"),
        best_param0_mean=best_param0_mean,
        baseline_param0_mean=baseline_param0_mean,
        best_delta_pct=f"{summary.get('best_delta_pct', 0):.2f}",
        ranking_text=ranking_text,
        category_detail=category_detail,
    )

    return SYSTEM_PROMPT, user_prompt
