---
name: qra-8d
description: QRA质量事件分析与8D结案。支持5W+1H案件登记、AI相似案例推荐、5-Why/鱼骨图根因分析、8D报告(D1-D8)自动生成、Workspace过程记录、案例归档与组织内分享。3个半导体质量案例分组练习。触发条件：质量事件、8D报告、根因分析、5Why、QRA、质量异常、案例推荐、案件登记。
---

# QRA 质量事件分析与8D结案

## 交付物

| 交付物 | 说明 |
|--------|------|
| 1. 相似案例推荐 | AI基于案例库检索相似历史案件 |
| 2. 数据分析+根因+Workspace记录 | 5W1H→5-Why→鱼骨图→Workspace全流程 |
| 3. 8D报告+Skill沉淀 | D1-D8自动填充+案例归档分享 |

## 3个练习案例

| 案例 | 内容 | 测试阶段 |
|------|------|----------|
| case1 | CP测试良率突降 — Probe Card针尖异常 | CP |
| case2 | FT Handler卡料导致批次良率波动 | FT |
| case3 | 新产品SLT Burn-in失效 — 固件时序问题 | SLT |

## 使用

```bash
cd "C:\Users\28144\Desktop\长鑫培训预演\16.质量事件的分析与结案"
python main.py --workshop              # 3组工作坊模式(全流程)
python main.py --case case1            # 单独案例
python main.py --recommend-text "CP良率突然下降"  # 案例推荐
```

## VSCode
```
/qra-8d 启动质量事件分析工作坊
```
