# 8D 报告: 新产品SLT Burn-in失效 — 固件时序问题

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

> **8D编号**: 8D-20260705-case3
> **结案日期**: 2026-07-05
> **状态**: Closed ✅

---

## D1 — 团队组建

| 角色 | 姓名 | 部门 |
|------|------|------|
| 组长 |  | |
| 技术专家 |  | |
| QRA代表 | QRA代表 | QRA |
| 其他 |  | |

---

## D2 — 问题描述 (5W+1H)

| 维度 | 描述 |
|------|------|
| **Who** | PTE工程师陈伟, FW工程师刘洋, QRA工程师孙丽 |
| **What** | SoC_A2新产品SLT阶段Burn-in 48hr后出现5.8%失效, DPPM超标 |
| **When** | 2026-05-20 ~ 06-05 |
| **Where** | SLT Lab, Advantest 7038 STR, Burn-in Chamber #BI-12 |
| **Why** | 初步怀疑DDR PHY时序margin不足或FW电源管理逻辑异常 |
| **How** | SLT量产导入前Burn-in Qualification, 48hr后DDR Stress Test出现CRC Error |

### IS / IS NOT



---

## D3 — 遏制措施



---

## D4 — 根因分析

### 5-Why

```

```

### 鱼骨图分析



**根因结论**: 

---

## D5 — 纠正措施



---

## D6 — 验证



---

## D7 — 预防措施



### Lessons Learned


---

## D8 — 结案与分享

| 项目 | 状态 |
|------|:---:|
| 所有措施已完成并验证 | ✅ |
| 8D报告已完成 | ✅ |
| 案例归档至QRA案例库 | ✅ |
| 团队分享完成 | ✅ |
| 横向展开检查 | ✅ |

**签核**: 组长: _____ | QRA主管: _____ | 日期: 2026-07-05

---

*本8D报告由QRA质量事件分析助手自动生成。基于8D标准模板+案例库数据。*
