"""
良率分析 Prompt 模板
"""
SYSTEM_PROMPT = """你是半导体良率分析专家 (PTE Yield Engineer), 专精于:
- CP/FT 良率时间序列异常检测 (3σ, CUSUM, 移动平均, 趋势分析)
- 根因定位: 测试程式/机台/批次/失效Bin 多维度关联
- 统计方法: 卡方检验, ANOVA, 相关性分析
- 半导体失效模式: Leakage, Short, Open, Vt Fail, Func Fail, IDDQ, Speed

回答原则: 数据驱动, 统计严谨, 工艺视角解读, 可操作建议, 中文输出术语英文"""


REPORT_PROMPT = """请基于以下良率分析数据生成根因分析报告。

## 异常检测摘要
{detection_summary}

## Top {top_n} 相关因子
{top_factors}

## 失效Bin分析
{bin_summary}

## 因子维度详情
{factor_details}

## 报告结构:

### 1. 良率异常概述
- 异常类型 (突降/趋势下降/尖峰) 和等级 (Critical/High/Medium)
- 时间范围和影响批次数量
- 良率统计 (均值/标准差/最低点)

### 2. 根因定位 — Top {top_n} 相关因子
对每个因子:
- 因子名称和维度 (测试程式/测试机台/产品/失效Bin)
- 关联强度 (异常率, p-value, 显著性)
- 工艺解读 — 为什么这个因子可能导致良率异常
- 排查建议

### 3. 失效Bin Pareto分析
- 异常期间主要贡献的失效Bin
- 每个Bin的工艺含义和可能根因
- 建议的FA方向

### 4. 综合结论与建议
- 最可能的根因假设 (1-2个)
- 验证计划 (Next Steps)
- 短期遏制措施

中文输出, 800-1500字, 数据引用精确。"""


def build_prompt(detection, rootcause, top_n=5) -> tuple:
    summary = detection.get("summary", {})
    det_text = f"""
- 总数据点: {summary.get('total_points', '?')}
- 异常点数: {summary.get('anomaly_count', '?')} ({summary.get('anomaly_rate', '?')}%)
- 3σ异常: {summary.get('sigma_anomalies', '?')} | CUSUM: {summary.get('cusum_anomalies', '?')}
- 趋势下降: {summary.get('has_trending_decline', '?')}
- 综合等级: {summary.get('overall_severity', '?')}
"""

    top = rootcause.get("top_factors", [])
    tf_text = "\n".join(
        f"  #{i+1} [{f['dimension']}] {f['factor']}: "
        f"异常率={f.get('anomaly_rate',0):.0f}%, "
        f"p={f.get('p_value',1):.4f}, "
        f"显著={f.get('significant',False)}"
        for i, f in enumerate(top)
    ) if top else "(无)"

    bin_data = rootcause.get("bin_analysis", {}).get("results", [])
    bin_text = "\n".join(
        f"  {b['bin']}: Δ={b['delta_pct']:+.0f}% (异常期{b['anomaly_avg']:.1f} vs 正常{b['normal_avg']:.1f})"
        for b in bin_data[:5]
    ) if bin_data else "(无)"

    factor_text = ""
    for key in ["program_analysis", "tester_analysis", "product_analysis"]:
        data = rootcause.get(key, {})
        factor_text += f"\n### {data.get('dimension', key)}\n"
        for r in data.get("results", [])[:3]:
            factor_text += (f"  {r['value']}: 异常率={r['anomaly_rate']:.0f}%, "
                            f"均值={r['avg_yield']:.1f}%, p={r['p_value']:.4f}\n")

    user_prompt = REPORT_PROMPT.format(
        detection_summary=det_text, top_n=top_n,
        top_factors=tf_text, bin_summary=bin_text, factor_details=factor_text,
    )
    return SYSTEM_PROMPT, user_prompt
