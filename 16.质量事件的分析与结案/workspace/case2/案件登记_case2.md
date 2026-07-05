# QRA 案件登记 — FT Handler卡料导致批次良率波动

### 5W+1H

| 维度 | 描述 |
|------|------|
| **Who** | PTE工程师李明, QRA工程师王芳 |
| **What** | NAND产品FT良率在2天内出现间歇性下降(正常97.2%→94.5%~96.8%波动) |
| **When** | 2026-04-10 ~ 04-12 |
| **Where** | FT Test Floor, Cohu Delta Matrix Handler #DM-06, Socket S-NAND-042 |
| **Why** | 初步怀疑Handler机械精度下降或Socket接触不良 |
| **How** | 良率日报发现Lot间良率波动>2%, Retest Rate从1.2%升至8.5% |

### 8D 摘要

| D | 内容 |
|---|------|
| D1 团队 | 李明(PTE), 王芳(QRA), 赵六(ME) |
| D2 问题描述 | NAND FT良率间歇波动2.7%, 重测率从1.2%升至8.5%, Handler #DM-06 Jam Rate从0.3%升至2.1% |
| D3 遏制 | 停用Handler #DM-06, 切换至#DM-07, 受影响Lot全部重测 |
| D4 根因 | Handler #DM-06 Pick&Place机械臂Y轴导轨磨损→定位精度从±25μm退化至±80μm→芯片放入Socket位置偏移→接触电阻波动→间歇性Fail |
| D5 纠正 | 更换Y轴导轨+滚珠丝杆, 重新校准定位精度至±20μm, 更换Socket S-NAND-042 (寿命已达480K) |
| D6 验证 | Golden Unit验证通过, 连续5批良率97.0~97.5%, Retest Rate恢复至1.0%, Jam Rate<0.2% |
| D7 预防 | Handler PM增加每月精度校验; Socket寿命预警从500K降至350K; 建立Handler-Socket配对追溯 |
| D8 结案 | 2026-04-15签核, 案例归档, ME团队分享 |

### 关键词
FT良率波动, Handler卡料, Socket寿命, 定位精度退化, Retest Rate, Jam Rate

---

> **登记日期**: 2026-07-05 | **案件编号**: case2
> **当前阶段**: 8D完成 ✅

---

## 5W+1H 案件登记

| **Who** | PTE工程师李明, QRA工程师王芳 |
| **What** | NAND产品FT良率在2天内出现间歇性下降(正常97.2%→94.5%~96.8%波动) |
| **When** | 2026-04-10 ~ 04-12 |
| **Where** | FT Test Floor, Cohu Delta Matrix Handler #DM-06, Socket S-NAND-042 |
| **Why** | 初步怀疑Handler机械精度下降或Socket接触不良 |
| **How** | 良率日报发现Lot间良率波动>2%, Retest Rate从1.2%升至8.5% |

---

## 相似案例推荐 (AI)

  #1 [case2] FT Handler卡料导致批次良率波动 (相似度: 6.4)
  #2 [case3] 新产品SLT Burn-in失效 — 固件时序问题 (相似度: 2.5)
  #3 [case1] CP测试良率突降 — Probe Card针尖异常 (相似度: 1.3)

---

## 8D 报告摘要



---

*过程记录由QRA质量事件分析助手自动生成。*
