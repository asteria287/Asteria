---
name: yield-analyzer
description: 产品良率分析智能助手。对良率时间序列进行异常检测(3σ/CUSUM/移动平均/趋势分析)自动识别突降、趋势下降、尖峰等异常类型和等级，并通过测试程式/测试机台/批次/产品/失效Bin多维度关联分析定位Top 5根因因子，输出可视化图表和根因分析报告。触发条件：良率异常、yield drop、良率分析、根因定位、CP良率、FT良率、批次异常、yield anomaly、root cause。
---

# 产品良率分析智能助手

## 核心能力

| 模块 | 说明 | 方法 |
|------|------|------|
| 🔍 异常检测 | 自动识别异常点(突降/趋势/尖峰) + 等级 | 3σ + CUSUM + 移动平均 + 趋势分析 |
| 🎯 根因定位 | 多维度关联 → Top 5 因子 | 测试程式/机台/产品/Bin 卡方检验 + 贡献度 |
| 📊 可视化 | 时间序列+异常标注+Pareto+热力图 | matplotlib |

## 实现步骤
1. 联网搜索良率分析论文/专利 → 确定异常检测算法 (3σ, CUSUM, GNN)
2. 实现时间序列异常检测 + 根因关联分析
3. 生成分析报告
4. 发布为skill

## 使用
```bash
cd "C:\Users\28144\Desktop\长鑫培训预演\15.产品良率分析智能助手"
python main.py --sample                    # 示例数据
python main.py -f yield.csv --report       # AI报告
```

## VSCode
```
/yield-analyzer 分析良率异常
```
