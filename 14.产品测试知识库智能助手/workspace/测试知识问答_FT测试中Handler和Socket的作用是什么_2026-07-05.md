# 产品测试知识问答

> **日期**: 2026-07-05 | **引擎**: 产品测试知识库 + DeepSeek v4 Pro AI

## Query
FT测试中Handler和Socket的作用是什么?

---
### 1. 直接回答
在FT（封装测试）中，**Handler** 是自动分选机，负责将封装好的芯片从料盘中取出，精准送入测试插座，并在测试完成后按结果分类放回不同料盘；**Socket** 是安装在Load Board上的精密测试插座，提供芯片引脚与测试系统之间的临时电气连接，确保信号质量且不损伤芯片。

### 2. 详细说明

**Handler（分选机）** — FT产线的自动化执行核心：

1. **上料（Loading）**：从JEDEC标准料盘取出待测芯片，通过机械臂pick & place输送
2. **温度浸泡（Soak）**：芯片进入温度腔室，保持在高温/低温，Soak Time 3~5分钟确保热平衡
3. **精准对接（Plunger & Guide）**：精准机械定位，将芯片引脚与Socket接触件对齐，施加适当压力
4. **测试执行（Test）**：ATE通过Load Board + Socket向芯片供电、激励并采集响应
5. **分选下料（Binning）**：读取ATE bin码，将芯片分别放入良品/次品/速度等级不同料盘

Handler关键指标：**UPH（5K-15K）**、卡料率（Jam Rate）、温度控制精度。

**Socket（测试插座）** — 芯片与测试系统间的关键电气机械界面：

- **电气连接**：Socket内弹簧探针（pogo pin）与芯片每个引脚形成稳定低接触电阻（<50mΩ），保持受控阻抗传输高速信号
- **机械保护**：数千到数十万次插拔不损伤芯片引脚，自身不快速磨损
- **适配封装**：按封装形式（QFN/BGA/QFP/LGA）定制，探针排列与引脚一一对应
- **寿命管理**：寿命通常100K~500K次插入，达预警值后需更换

典型测试拓扑：ATE → Load Board → DUT Board → Socket → IC under test

### 3. 知识来源
| 来源文件 | 章节 | 关键信息 |
|----------|------|----------|
| ft_fundamentals.md | 1. FT测试概述 | Handler自动送入Socket，ATE通过Load Board连接 |
| ft_fundamentals.md | 2.1 测试准备 | Handler配置：温度chamber/soak time/speed；Socket安装 |
| test_terminology.md | Handler（分选机） | 定义+UPH/Jam Rate/Soak Time |
| ft_fundamentals.md | 3. FT核心参数 | Socket Lifetime 100K-500K；Soak Time 3-5min |

### 4. 新人提示
- **Socket选型与维护**：不同封装Socket绝不可混用，寿命达80%时安排更换
- **Handler Soak Time验证**：切勿为提升UPH盲目缩短soak time
- **卡料与清洁**：卡料时先暂停记录位置，每天吹除dust和socket碎屑
- **Golden Unit校验**：FT上线前用已知好/坏标准芯片跑完整流程确认链路正常

---
*由产品测试知识库智能助手生成。DeepSeek v4 Pro 分析。*
