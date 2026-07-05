# 产品良率分析智能助手

PTE部门 — 良率异常检测 + 根因定位

## 快速开始
```bash
pip install -r requirements.txt
python main.py --sample
python main.py --sample --report  # AI报告
```

## 能力
1. 异常检测: 3σ + CUSUM + 移动平均 + 趋势分析
2. 根因定位: 测试程式/机台/产品/Bin → Top 5因子
3. 可视化: 时间序列 + Pareto + 热力图
