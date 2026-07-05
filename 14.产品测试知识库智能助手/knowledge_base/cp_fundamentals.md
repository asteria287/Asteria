# CP 晶圆测试 (Chip Probe / Wafer Sort)

> 测试阶段: 晶圆级 | 环境: 常温/高温/低温 | 载体: Prober + Probe Card

---

## 1. CP 测试概述

CP (Chip Probe) 是在晶圆切割封装之前，通过探针卡 (Probe Card) 对晶圆上每个 die 进行电性测试的工序。也称为 Wafer Sort 或 Wafer Test。

**核心目的**:
- 筛选出功能完好的 die (Known Good Die, KGD)
- 减少封装成本 (避免封装坏 die)
- 提供工艺反馈数据 (良率、失效模式分布)

**测试环境**: 晶圆放置于 Prober 的 chuck 上，探针卡针尖接触 die 的 bonding pad，通过 ATE (Automatic Test Equipment) 发送测试信号。

---

## 2. CP 测试流程

### 2.1 测试准备
1. 晶圆加载 (Wafer Loading): 将晶圆放置在 Prober chuck 上
2. 晶圆对准 (Wafer Alignment): 光学对准晶圆 notch/flat
3. 探针卡安装 (Probe Card Mounting): 安装对应产品的探针卡
4. 针尖校准 (Needle Alignment): 确保针尖与 pad 精确对准
5. 温度设定: 根据测试规格设定 chuck 温度 (25°C / 85°C / -40°C)
6. 测试程式加载: 加载对应产品的 Test Program (通常为 .tpl/.test 格式)

### 2.2 测试执行
1. Contact Test (接触测试): 验证探针与 pad 的接触电阻
2. DC Test (直流测试): 测量漏电流、电源电流、I/O 特性
3. Functional Test (功能测试): 运行关键功能 pattern 验证逻辑
4. Parametric Test (参数测试): 测量 Vt, Idsat, 频率等关键参数
5. Binning: 根据测试结果对 die 进行分类 (Good / Repair / Scrap)

### 2.3 测试收尾
1. Ink Marking (墨点标记): 在坏 die 上打墨点 (部分工厂已弃用)
2. Wafer Map 生成: 记录每个 die 的测试结果 (bin 分布)
3. 数据上传: 将 wafer map 上传至 MES/YMS 系统
4. 探针卡清洁与维护

---

## 3. CP 核心参数

| 参数 | 说明 | 典型规格 |
|------|------|----------|
| Contact Resistance | 探针与pad接触电阻 | < 2Ω |
| Probe Force | 探针压力 | 2-5g/pin |
| Chuck Temperature | 载台温度 | 25°C ± 0.5°C |
| Test Time/Die | 单die测试时间 | 0.5-5s (取决于产品复杂度) |
| Overdrive | 过驱动距离 | 50-75μm |
| Needle Lifetime | 探针寿命 | 500K-1M touchdown |

---

## 4. CP 主要机台

| 机台型号 | 厂商 | 特点 |
|----------|------|------|
| TEL P-12 | Tokyo Electron | 高精度 Prober |
| TSK UF3000 | Accretech | 300mm 全自动 |
| EG4090 | Electroglas | 成熟平台 |
| V93000 | Advantest | ATE, 高频支持 |
| UltraFLEX | Teradyne | ATE, 大规模SoC测试 |

---

## 5. CP 常见问题

| 问题 | 现象 | 根因 | 处理 |
|------|------|------|------|
| 接触不良 | 高接触电阻 | 针尖氧化/磨损/偏位 | 清洁或更换探针卡 |
| Pad Damage | pad 表面损伤 | 探针压力过大 | 调整 overdrive |
| 温度偏差 | chuck 温度不均 | 热偶故障/chuck 污染 | 校准热偶/清洁 chuck |
| Wafer Map 偏移 | die 位置错位 | 对准误差 | 重新做 wafer alignment |

---

## 6. 术语

| 术语 | 全称 | 说明 |
|------|------|------|
| KGD | Known Good Die | CP 后确认完好的 die |
| BIN | Bin Classification | 测试结果分类 |
| PCM | Process Control Monitor | 工艺控制监控结构 |
| O/S | Open/Short Test | 开短路测试 |
| EDS | Electrical Die Sort | 电气 die 分类 |
