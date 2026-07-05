# 半导体测试术语词典

---

## DC 测试 (Direct Current Test)
- **全称**: Direct Current Test / 直流测试
- **测试阶段**: CP (晶圆测试), FT (封装测试)
- **定义**: 对芯片直流电性参数的测量，包括电源电流、漏电流、I/O 电平等
- **关联参数**: IDD (电源电流), Ioff (关态漏电), VOH/VOL (输出电平), IIH/IIL (输入漏电)
- **应用场景**: 所有芯片测试的基础环节，通常在 Functional Test 之前执行
- **常见设备**: ATE 的 DC 测量单元 (PPMU/VI)

---

## AC 测试 (Alternating Current Test)
- **全称**: AC Parametric Test / 交流参数测试
- **测试阶段**: FT (封装测试)
- **定义**: 对芯片时序参数的测量，包括 setup/hold time, propagation delay, clock frequency
- **关联参数**: tSETUP, tHOLD, tPD, Fmax, tCO, tSKEW
- **应用场景**: 高速数字芯片 (CPU/GPU/FPGA/DDR) 的时序验证
- **常见设备**: ATE 的高速数字通道 (HSD)

---

## BIST (Built-In Self Test)
- **全称**: Built-In Self Test
- **测试阶段**: CP, FT, SLT 均可用
- **定义**: 芯片内建的自我测试电路，可在不依赖外部 ATE 的情况下执行测试
- **关联参数**: Repair Rate, BIST Coverage, Test Time
- **应用场景**: Memory BIST (DRAM/SRAM 测试), Logic BIST (随机逻辑测试)
- **常见设备**: 芯片内部集成，ATE 仅需发送 BIST 启动指令

---

## RDBI (Resistance Detection By Imbalance)
- **全称**: Resistance Detection By Imbalance
- **测试阶段**: CP (晶圆测试)
- **定义**: 一种通过检测不平衡电阻来定位晶圆上缺陷的技术，通常用于检测微小漏电路径
- **关联参数**: Leakage Current, Resistance Threshold, Guard Band
- **应用场景**: 先进工艺节点的晶圆级缺陷筛查，特别是 BEOL 金属桥接/断路的检测
- **常见设备**: 高灵敏度 DC 测量单元

---

## O/S 测试 (Open/Short Test)
- **全称**: Open/Short Test / 开短路测试
- **测试阶段**: CP (晶圆测试), FT (封装测试)
- **定义**: 检测芯片引脚或 pad 的开路和短路状态的测试，是所有测试流程的第一步
- **关联参数**: Contact Resistance, Diode Drop Voltage, Pin Count
- **应用场景**: 每颗芯片测试的起始步骤，快速筛选出引脚连接异常的芯片
- **常见设备**: ATE 的基础 DC 通道

---

## STDF (Standard Test Data Format)
- **全称**: Standard Test Data Format
- **测试阶段**: CP, FT
- **定义**: 半导体行业标准测试数据格式 (IEEE 1450.5)，用于存储和交换测试结果
- **关联参数**: Bin Info, Test Result, Wafer Map, Yield Summary
- **应用场景**: 测试数据上传至 YMS/MES，良率分析，SPC 监控
- **常见设备**: 所有 ATE 均支持 STDF 输出

---

## PCM (Process Control Monitor)
- **全称**: Process Control Monitor
- **测试阶段**: CP (晶圆测试)
- **定义**: 放置在晶圆 scribe line 中的测试结构，用于监控工艺健康状态
- **关联参数**: Vt, Idsat, Rs, Cgate, Junction Leakage
- **应用场景**: 工艺窗口监控，SPC chart，异常批次预警
- **常见设备**: 专用 PCM Tester 或 ATE

---

## Handler (分选机)
- **全称**: IC Handler / 自动分选机
- **测试阶段**: FT (封装测试)
- **定义**: 自动将封装芯片从 tray 送入测试 socket，测试完成后按 bin 分类的机械系统
- **关联参数**: UPH (Units Per Hour), Jam Rate, Soak Time
- **应用场景**: FT 量产测试
- **常见设备**: Cohu Delta Matrix, Hon M4871, TESEC

---

## Prober (探针台)
- **全称**: Wafer Prober
- **测试阶段**: CP (晶圆测试)
- **定义**: 自动将晶圆上每个 die 移动到探针卡下方进行测试的精密机械系统
- **关联参数**: Accuracy (μm), Throughput (wph), Chuck Temperature Uniformity
- **应用场景**: CP 量产测试
- **常见设备**: TEL P-12, TSK UF3000, Electroglas EG4090

---

## IDD Test (电源电流测试)
- **全称**: IDD Current Test / 电源电流测试
- **测试阶段**: CP, FT
- **定义**: 测量芯片在不同工作模式下的电源电流，包括静态 (IDDQ) 和动态 (IDDA)
- **关联参数**: IDD_Static, IDD_Dynamic, IDD_Sleep, IDDQ, IDDA
- **应用场景**: 功耗验证，漏电筛选
- **常见设备**: ATE 的精密电源测量单元

---

## Burn-in (老化测试)
- **全称**: Burn-in Test / 老化测试
- **测试阶段**: FT 后 (可靠性验证)，部分整合入 SLT
- **定义**: 在高温高压条件下长时间运行芯片，加速早期失效 (Infant Mortality) 的暴露
- **关联参数**: Temperature, Voltage, Duration, Failure Rate
- **应用场景**: 高可靠性产品 (汽车/航空/医疗)
- **常见设备**: Burn-in Oven, Burn-in Board
