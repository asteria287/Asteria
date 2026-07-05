---
name: pcrb-analyzer
description: PCRB实验结果智能分析助手。对PCRB实验数据(CSV/Excel)进行统计分析(Z-score/t-test/ANOVA/Effect Size)多维度评分选择最优实验分组，输出Benefit&Drawback分析、异常参数识别、箱体图+排名图+热力图可视化，并基于LLM生成工艺解读报告。触发条件：PCRB实验分析、实验分组选择、工艺split对比、DOE结果分析、最优条件推荐、实验组benefit drawback。
---

# PCRB 实验结果智能分析助手

## 核心能力

| 能力 | 说明 | 输出 |
|------|------|------|
| 🏆 最优组选择 | 稳定性+改善度+副作用+效应大小 4维评分 | 排名表 + 评分分解 |
| 📊 异常参数识别 | Z-score + t-test + Effect Size vs Baseline | 按类别异常参数清单 |
| 📈 箱体图可视化 | Top N 参数箱体图 (ANOVA排序) + 排名图 + Delta热力图 | PNG 图表 |
| 🤖 AI 报告生成 | LLM 工艺解读 + Benefit/Drawback + Next Steps | Workspace 笔记 |

## 分析流程

```
┌──────────┐   ┌───────────────┐   ┌──────────────────┐   ┌──────────┐
│ CSV/Excel│ → │ 统计分析引擎    │ → │ 可视化 (箱体图等)  │ → │ AI 报告   │
│ 实验数据  │   │ ANOVA+t-test   │   │ Top参数 + 热力图   │   │ LLM解读   │
└──────────┘   └───────┬───────┘   └──────────────────┘   └──────────┘
                       │
          ┌────────────▼────────────┐
          │ 1. 最优组选择 (4维评分)   │
          │ 2. 异常参数 (Z>2σ)       │
          │ 3. Benefit & Drawback   │
          └─────────────────────────┘
```

## 项目路径

```
C:\Users\28144\Desktop\长鑫培训预演\13.PCRB实验结果智能分析助手\
```

## 使用

```bash
cd "C:\Users\28144\Desktop\长鑫培训预演\13.PCRB实验结果智能分析助手"

# 使用示例数据测试
python main.py --sample

# 分析实验数据
python main.py -f pcrb_experiment_data.csv

# 指定优化方向 + AI报告
python main.py -f data.csv --maximize "Idsat,Yield" --minimize "Ioff,DIBL" --report

# 仅查看数据统计
python main.py -f data.csv --stats
```

## VSCode

```
/pcrb-analyzer 分析这份PCRB实验数据, 选择最优实验分组
```
