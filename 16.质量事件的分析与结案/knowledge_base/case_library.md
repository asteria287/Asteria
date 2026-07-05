# 半导体质量事件案例库

> QRA 部门 — 用于案例推荐、8D学习和新人培训

---

## 案例1: CP测试良率突降 — Probe Card针尖异常

### 5W+1H

| 维度 | 描述 |
|------|------|
| **Who** | PTE工程师张三, QRA工程师李四 |
| **What** | DDR5产品CP良率从94.5%突然降至86.2% (下降8.3%) |
| **When** | 2026-03-15 14:00 ~ 03-18 10:00 |
| **Where** | CP Test Floor, ATE_V93000_03, TEL P-12 Prober, Probe Card PC-DDR5-088 |
| **Why** | 初步怀疑探针卡磨损/污染导致接触电阻异常 |
| **How** | 日常良率监控SPC报警触发, Wafer Map显示区域性Edge Ring失效 |

### 8D 摘要

| D | 内容 |
|---|------|
| D1 团队 | 张三(PTE), 李四(QRA), 王五(EE) |
| D2 问题描述 | DDR5 CP良率突降8.3%, Lot LOT_0315~LOT_0318共4批受影响, 失效Bin: Bin5_FuncFail占比从12%升至35% |
| D3 遏制 | 立即停用PC-DDR5-088探针卡, 切换至备用卡PC-DDR5-089, 隔离受影响Lot |
| D4 根因 | 探针卡#088针尖氧化+聚合物污染, 接触电阻从1.5Ω升至8.2Ω, 高速信号SI退化导致FuncFail |
| D5 纠正 | 更换探针卡#088, 执行深度清洁+针尖研磨, 恢复接触电阻<2Ω |
| D6 验证 | 使用Golden Wafer验证, CP良率恢复至94.3%, 连续3批稳定; 探针卡寿命监控从1M→500K TD |
| D7 预防 | 更新探针卡PM频率: 每500K TD强制清洁; SPC增加Contact Resistance趋势监控 |
| D8 结案 | 2026-03-20签核, 案例归档至QRA案例库, 分享至PTE全员 |

### 关键词
CP良率突降, Probe Card, 接触电阻, 针尖氧化, Edge Ring失效, Bin5_FuncFail

---

## 案例2: FT Handler卡料导致批次良率波动

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

## 案例3: 新产品SLT Burn-in失效 — 固件时序问题

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

## 案例相似度矩阵

| | 案例1(CP探针) | 案例2(FT Handler) | 案例3(SLT FW) |
|---|---|---|---|
| **案例1** | 1.0 | 0.6 (接触类) | 0.2 |
| **案例2** | 0.6 | 1.0 | 0.3 |
| **案例3** | 0.2 | 0.3 | 1.0 |
