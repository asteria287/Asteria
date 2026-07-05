# FT 封装测试 (Final Test / Package Test)

> 测试阶段: 封装后 | 环境: 常温/高温/低温 | 载体: Handler + Test Socket

---

## 1. FT 测试概述

FT (Final Test) 是在芯片封装完成后，对成品芯片进行的电性测试。也称为 Package Test 或 Back-end Test。

**核心目的**:
- 验证封装后的芯片功能完整性
- 筛选封装过程中损坏的芯片 (Assembly Yield Loss)
- 验证芯片符合规格书 (Datasheet) 参数
- 进行 Speed Binning (按速度等级分类)

**测试环境**: 芯片通过 Handler 自动送入测试插座 (Test Socket)，ATE 通过 Load Board + DUT Board 连接芯片引脚。

---

## 2. FT 测试流程

### 2.1 测试准备
1. 封装芯片上料 (Device Loading): 将 tray 中的芯片放入 Handler
2. Handler 配置: 设定温度 chamber, soak time, handler speed
3. Socket 安装: 安装对应封装的 Test Socket
4. Load Board 连接: 连接 ATE 与 DUT Board
5. 测试程式加载: 加载 FT Test Program
6. 温控确认: 确保芯片达到测试温度 (soak time 通常 3-5min)

### 2.2 测试执行
1. Continuity Test (连续性测试): 验证引脚连通性
2. IDD Test (电源电流): 测量静态/动态功耗
3. DC Test: I/O 电平、输入漏电、输出驱动
4. AC Test: 时序参数 (setup/hold, propagation delay)
5. Functional Test: 全功能 pattern 向量
6. BIST (Built-In Self Test): 内建自测试 (Memory BIST, Logic BIST)
7. Speed Binning: 按 Fmax 分级 (e.g., 2.0GHz / 2.4GHz / 2.8GHz)

### 2.3 测试收尾
1. Bin Sorting: 按测试结果分 bin (Good/Speed/Fail)
2. Marking: 激光 marking 芯片表面信息
3. T&R (Tape & Reel): 编带包装
4. 数据上传: 上传 STDF 数据至 YMS

---

## 3. FT 核心参数

| 参数 | 说明 | 典型规格 |
|------|------|----------|
| Test Yield | 测试良率 | > 97% (含 assembly loss) |
| Retest Rate | 重测率 | < 2% |
| Correlation | FT vs CP 良率相关性 | > 99% |
| Soak Time | 温控稳定时间 | 3-5 min |
| Handler UPH | 单位小时产出 | 5K-15K units |
| Socket Lifetime | 测试座寿命 | 100K-500K insertions |

---

## 4. FT 主要机台

| 机台型号 | 厂商 | 特点 |
|----------|------|------|
| V93000 | Advantest | 高速数字/mixed-signal |
| UltraFLEX | Teradyne | SoC 测试平台 |
| J750 | Teradyne | 低成本数字测试 |
| ETS-800 | Teradyne | 模拟/功率测试 |
| M4871 | Hon Precision | Handler |
| Delta Matrix | Cohu | Pick-and-place handler |

---

## 5. FT 常见问题

| 问题 | 现象 | 根因 | 处理 |
|------|------|------|------|
| Socket 接触不良 | Open/Short fail | Socket 磨损/氧化 | 更换 Socket |
| 温度偏差 | 参数漂移 | Soak time 不足 | 延长 soak / 校准 |
| Handler Jam | 机台停机 | 芯片卡料 | 清理轨道 |
| FT Yield Drop | 良率突然下降 | Assembly 工艺波动 | 通知封装厂 |
| Retest Gap | 重测后 pass | 接触问题 | 检查 socket/clean |

---

## 6. FT 术语

| 术语 | 全称 | 说明 |
|------|------|------|
| STDF | Standard Test Data Format | 测试数据标准格式 |
| BIST | Built-In Self Test | 内建自测试 |
| DUT | Device Under Test | 被测器件 |
| Load Board | 负载板 | ATE 与 socket 之间的接口板 |
| UPH | Units Per Hour | 单位小时产出 |
| OCAP | Out of Control Action Plan | 失控行动计划 |
