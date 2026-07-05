# QRA 案件登记 — 新产品SLT Burn-in失效 — 固件时序问题

### 5W+1H

| 维度 | 描述 |
|------|------|
| **Who** | PTE工程师陈伟, FW工程师刘洋, QRA工程师孙丽 |
| **What** | SoC_A2新产品SLT阶段Burn-in 48hr后出现5.8%失效, DPPM超标 |
| **When** | 2026-05-20 ~ 06-05 |
| **Where** | SLT Lab, Advantest 7038 STR, Burn-in Chamber #BI-12 |
| **Why** | 初步怀疑DDR PHY时序margin不足或FW电源管理逻辑异常 |
| **How** | SLT量产导入前Burn-in Qualification, 48hr后DDR Stress Test出现CRC Error |

### 8D 摘要

| D | 内容 |
|---|------|
| D1 团队 | 陈伟(PTE), 刘洋(FW), 孙丽(QRA), 周杰(Design) |
| D2 问题描述 | SoC_A2 Burn-in 48hr后5.8%失效(目标<2%), 失效模式: DDR CRC Error(80%), Boot Fail(20%), 温度85°C时恶化 |
| D3 遏制 | 暂停SoC_A2 SLT量产导入, 已出货Lot全数召回重测SLT, FW版本回退至v1.2 |
| D4 根因 | 5-Why分析: (1)Why DDR CRC Error? → DDR PHY training失败 (2)Why training失败? → FW v1.3修改了DDR初始化时序 (3)Why修改时序? → 为了优化功耗 (4)Why未发现? → SLT corner test未覆盖85°C+DDR stress组合 (5)Why FW变更未通知PTE? → 变更管理流程缺失 → **根因: FW时序变更+SLT覆盖不足+变更管理漏洞** |
| D5 纠正 | FW修复: 恢复DDR初始化时序+增加温度补偿; SLT增加85°C+DDR stress test case; 建立FW变更→PTE通知流程 |
| D6 验证 | FW v1.4 Burn-in 72hr通过, 0% CRC Error; SLT覆盖率从82%→94%; 连续10批DPPM<1000 |
| D7 预防 | FW变更管理流程: 所有时序参数变更需PTE+QRA会签; SLT test case定期review(季度); 建立Cross-functional change review board |
| D8 结案 | 2026-06-08签核, 案例归档, 全公司All-Hands分享, 更新NPI流程 |

### 关键词
SLT Burn-in, FW时序, DDR CRC Error, 变更管理, DPPM, 5-Why, Cross-functional

---

> **登记日期**: 2026-07-05 | **案件编号**: case3
> **当前阶段**: 8D完成 ✅

---

## 5W+1H 案件登记

| **Who** | PTE工程师陈伟, FW工程师刘洋, QRA工程师孙丽 |
| **What** | SoC_A2新产品SLT阶段Burn-in 48hr后出现5.8%失效, DPPM超标 |
| **When** | 2026-05-20 ~ 06-05 |
| **Where** | SLT Lab, Advantest 7038 STR, Burn-in Chamber #BI-12 |
| **Why** | 初步怀疑DDR PHY时序margin不足或FW电源管理逻辑异常 |
| **How** | SLT量产导入前Burn-in Qualification, 48hr后DDR Stress Test出现CRC Error |

---

## 相似案例推荐 (AI)

  #1 [case3] 新产品SLT Burn-in失效 — 固件时序问题 (相似度: 7.6)
  #2 [case1] CP测试良率突降 — Probe Card针尖异常 (相似度: 2.5)
  #3 [case2] FT Handler卡料导致批次良率波动 (相似度: 0.7)

---

## 8D 报告摘要



---

*过程记录由QRA质量事件分析助手自动生成。*
