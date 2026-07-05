# PCRB 实验结果智能分析助手

OP 部门 (YI/PI/DI) 新人 PCRB 实验数据分析工具。

## 快速开始

```bash
pip install -r requirements.txt
python main.py --sample    # 内置示例数据, 直接看效果
```

## 功能

1. **最优实验组选择** — 4维度评分自动推荐最佳分组
2. **Baseline 异常参数分析** — 统计检验 + 效应大小
3. **箱体图/排名图/热力图** — 可视化辅助判断
4. **AI 工艺解读报告** — LLM 生成 Benefit/Drawback + Next Steps

## 输入格式

CSV 或 Excel, 需包含:
- 分组列 (如 Group/Split/Lot/实验组)
- 数值参数列 (如 Idsat/Vt/Yield/...)

```csv
Group,Vt_SAT_NMOS,Idsat_NMOS,Ioff_NMOS,Yield_Pct
Baseline,0.352,655.3,1.52e-9,92.1
Split_A,0.331,680.1,1.21e-9,93.6
...
```

## 使用

```bash
python main.py -f my_pcrb.csv                    # 基础分析
python main.py -f my_pcrb.csv --report           # 含AI报告
python main.py -f my_pcrb.csv --maximize "Idsat,Yield" --minimize "Ioff" --report
```
