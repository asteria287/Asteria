---
name: test-kb
description: 产品测试知识库智能助手。基于CP/FT/SLT三大测试环节知识库进行智能问答和术语解析，支持交互式问答、术语定义+阶段+关联参数+场景输出。基于联网搜索(论文/专利/行业信息)+LLM结构化分解构建知识体系。触发条件：半导体测试、CP测试、FT测试、SLT测试、晶圆测试、封装测试、系统级测试、测试术语、探针卡、Handler、ATE、STDF、RDBI、BIST、Burn-in等。
---

# 产品测试知识库智能助手

## 核心能力

| 能力 | 说明 | 示例 |
|------|------|------|
| 🔍 能力1: 知识问答 | CP/FT/SLT 测试概念/流程/设备/参数问答 | "CP测试流程是什么?" |
| 📖 能力2: 术语解析 | 术语定义+测试阶段+关联参数+应用场景 | ":t RDBI" → 结构化解析 |

## 知识构建方式 (3步实现)

```
Step 1: 联网搜索 → 3次搜索 (CP/ATE趋势 + FT/SLT/Burn-in + 中文全流程)
Step 2: DeepSeek v4 Pro 结构化分解 → 7份知识库文档
  • cp_fundamentals.md         — CP 晶圆测试 (流程/参数/设备/术语)
  • ft_fundamentals.md         — FT 封装测试 (流程/参数/设备/术语)
  • slt_fundamentals.md        — SLT 系统级测试 (流程/参数/设备/术语)
  • test_terminology.md        — 术语词典 (12术语精确索引)
  • test_trends_2025.md        — 🆕 技术趋势 (AI自适应/Chiplet/硅光子/国产替代)
  • test_compare_cp_ft_slt.md  — 🆕 CP/FT/SLT 三大环节对比
  • test_equipment_guide.md    — 🆕 测试设备速查 (ATE/Prober/Handler/SLT)
Step 3: Skill注册 + 调用验证
```

## 项目路径

```
C:\Users\28144\Desktop\长鑫培训预演\14.产品测试知识库智能助手\
```

## 使用

```bash
cd "C:\Users\28144\Desktop\长鑫培训预演\14.产品测试知识库智能助手"

python main.py -q "CP测试流程是什么?"        # 能力1: 知识问答
python main.py -t "RDBI"                     # 能力2: 术语解析
python main.py -q "FT和SLT的区别?" --report   # AI深度回答
python main.py                                # 交互模式
```

## VSCode

```
/test-kb CP测试的核心流程是什么?
```
