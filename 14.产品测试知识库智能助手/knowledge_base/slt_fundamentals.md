# SLT 系统级测试 (System Level Test)

> 测试阶段: 系统应用级 | 环境: 模拟真实应用场景 | 载体: SLT Board + 系统外设

---

## 1. SLT 测试概述

SLT (System Level Test) 是在模拟最终用户实际使用场景下，对芯片进行的系统级功能验证。SLT 介于 FT 和终端应用之间，能发现 CP/FT 无法覆盖的系统级缺陷。

**核心目的**:
- 发现系统级缺陷 (电气互操作、时序、功耗场景)
- 验证芯片在真实工作负载下的表现
- 筛选 CP/FT 无法检测的 marginal fail
- 验证 Firmware/Driver 兼容性

**SLT 的必要性**: CP/FT 仅覆盖电性参数和功能 pattern，SLT 覆盖真实 Workload。据行业数据，SLT 可额外筛出 0.1-0.5% 的缺陷率 (DPPM 级改善)。

---

## 2. SLT 测试流程

### 2.1 测试准备
1. SLT Board 设计: 设计模拟终端应用场景的 PCB
2. 外设连接: 连接 DDR、Flash、PMIC、Display 等系统组件
3. Firmware 烧录: 烧录测试 FW 到芯片或外部 Flash
4. 操作系统加载 (如适用): 加载 Linux/RTOS 等
5. 测试脚本部署: 部署自动化测试脚本
6. 温控环境设定: 设置 chamber 温度曲线

### 2.2 测试执行
1. Boot Test: 验证芯片启动流程
2. DDR Stress Test: 内存读写压力测试
3. Interface Test: PCIe/USB/Ethernet 等高速接口
4. Power Scenario Test: 各种功耗模式切换
5. Thermal Throttling Test: 温度保护机制验证
6. Long-Run Stability: 长时间 (24-72hr) 老化测试
7. Corner Lot Test: 工艺角芯片验证

### 2.3 测试收尾
1. 日志收集: 收集系统 log、温度曲线、功耗曲线
2. 失效分析: 对 fail chip 进行 FA
3. 数据上传: 上传到质量管理系统
4. SLT 报告生成: DPPM、失效模式统计

---

## 3. SLT 核心参数

| 参数 | 说明 | 典型规格 |
|------|------|----------|
| SLT DPPM | SLT 额外筛出的缺陷率 | 500-2000 DPPM |
| Test Coverage | SLT 测试覆盖率 | 取决于应用场景 |
| Test Time/Chip | 单芯片 SLT 时长 | 5min-24hr |
| Temp Profile | 温度曲线范围 | 0°C-125°C |
| Power Cycles | 电源开关循环数 | 100-1000 cycles |
| Data Retention | 数据保持测试时长 | 24-168 hr |

---

## 4. SLT 主要机台/平台

| 平台 | 厂商 | 特点 |
|------|------|------|
| SLT Platform | Advantest | 集成 SLT 解决方案 |
| Neptune | Teradyne | 大规模并行 SLT |
| Custom SLT Board | 自研 | 按产品定制 PCB |
| Thermal Stream | Temptronic | 快速温变系统 |
| Bench System | 多厂商 | 实验室手动测试 |

---

## 5. SLT 常见问题

| 问题 | 现象 | 根因 | 处理 |
|------|------|------|------|
| Boot Fail | 芯片不启动 | FW/晶振/Power Sequence | 检查 FW 版本/硬件连接 |
| DDR Fail | 内存错误 | 时序 margin/信号完整性 | 调整 DDR PHY 参数 |
| Thermal Shutdown | 过温保护触发 | 散热不足 | 改进散热/检查温控 |
| Interface CRC Error | 高速接口误码 | SI/PI 问题 | 检查 PCB layout |
| Marginal Fail | 间歇性 fail | PVT variation | Corner lot 验证 |

---

## 6. SLT 术语

| 术语 | 全称 | 说明 |
|------|------|------|
| DPPM | Defect Parts Per Million | 百万分之缺陷数 |
| PVT | Process/Voltage/Temperature | 工艺/电压/温度变化 |
| SI/PI | Signal/Power Integrity | 信号/电源完整性 |
| FW | Firmware | 固件 |
| Corner Lot | 工艺角批 | 工艺偏差极限的晶圆批 |
| Burn-in | 老化测试 | 高温高压加速老化 |
