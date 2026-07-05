---
name: sop-qa
description: SOP智能问答系统。基于机台维保SOP知识库进行智能问答，根据用户query检索相关SOP章节并生成结构化回答(含安全标注/标准值/工具清单/来源追溯)。支持交互式问答、快速查询、SOP概览、离线检索。触发条件：SOP问答、维保问题、PM步骤查询、机台操作步骤、SOP内容检索、设备维护SOP查询。
---

# SOP智能问答 — 机台维保SOP智能问答Skill

## 核心能力

基于半导体设备维保 SOP 知识库，智能回答用户的 SOP 相关问题。支持多策略混合检索 + LLM 深度分析 + 来源追溯。

## 能力矩阵

| 能力 | 说明 | 示例 |
|------|------|------|
| 🔍 智能检索 | 精确术语+语义概念+密度匹配+层级提权 | "如何清洁上电极?" |
| 📋 步骤还原 | 按 SOP 原有顺序还原操作步骤 | "PM 前安全准备有哪些?" |
| ⚠️ 安全标注 | 自动识别并优先展示安全关键项 | EMO/PPE/LOTO/通风 |
| 📏 标准值提取 | 精确引用 SOP 中的数值标准 | "<40°C, <5ppm, >10MΩ" |
| 🔧 工具清单 | 自动汇总所需工具和物料 | "扭矩扳手, 氦检漏仪..." |
| 📝 来源追溯 | 每条引用标注文件名+章节号 | "[SOP-001] > §2.1.2" |
| 💡 专家补充 | SOP 未覆盖时补充维护知识 | 标注 "基于专家知识" |

## 问答流程

```
┌─────────────┐
│  用户 Query  │  "如何更换Focus Ring?"
└──────┬──────┘
       │ SOPRetriever.search()
       ▼
┌─────────────┐
│ 多策略检索   │  精确术语 → 概念语义 → 密度匹配 → 层级提权
│ SOP 知识库   │  safety/ tools/ procedure/ standards/ equipment
└──────┬──────┘
       │ build_context()
       ▼
┌─────────────┐
│ Prompt 构建  │  System: 设备维护专家 + SOP上下文注入
│ QA/Quick/   │  User: 结构化输出模板
│ Overview     │
└──────┬──────┘
       │
       ├──→ LLM模式: Claude API 流式输出 + 结构化回答
       └──→ 离线模式: 返回检索到的 SOP 原文
            │
            ▼
┌─────────────────────────────────┐
│  结构化回答                      │
│  ⚠️ 安全注意事项 (优先展示)       │
│  → SOP 步骤 (按章节顺序)         │
│  → 关键数值与标准 (表格)         │
│  → 所需工具与物料                │
│  → 常见问题与注意事项            │
│  → 知识来源追溯                  │
│  → 补充建议 (专家知识)            │
└─────────────────────────────────┘
```

## 项目路径

```
C:\Users\28144\Desktop\长鑫培训预演\12.机台维保SOP的智能问答\
```

## 使用

```bash
cd "C:\Users\28144\Desktop\长鑫培训预演\12.机台维保SOP的智能问答"

# 导入 SOP 文档到知识库 (支持 .md/.txt/.pdf/.docx)
python main.py --import samples/sample_sop_etch_chamber_pm.md

# 交互式问答
python main.py

# 标准问答
python main.py -q "PM前安全准备步骤有哪些?"

# 快速简洁模式
python main.py -q "O-ring更换注意事项?" --quick

# SOP 概览
python main.py --overview

# 离线模式 (无需 API Key)
python main.py -q "腔体清洁步骤?" --offline

# 生成 Workspace 笔记
python main.py -q "ESC检查标准值?" --note

# 批量问答
python main.py --batch samples/sample_queries.txt

# 列出安全项/工具
python main.py --safety
python main.py --tools
```

## 项目文件结构

```
12.机台维保SOP的智能问答/
├── SKILL.md                         ← 本文件 (Skill Registry)
├── README.md                        ← 用户文档
├── main.py                          ← 主入口 (CLI + 交互模式)
├── requirements.txt                 ← Python依赖
├── .env.example                     ← API Key 模板
├── agent/
│   ├── __init__.py
│   ├── config.py                    ← 配置 (路径/API/关键词/同义词)
│   ├── sop_retriever.py             ← SOP 知识库检索器 (多策略混合)
│   ├── qa_engine.py                 ← Q&A 引擎 (LLM + 离线 + 笔记)
│   └── doc_parser.py               ← 文档解析器 (md/txt/pdf/docx)
├── prompts/
│   ├── __init__.py
│   └── sop_prompts.py              ← Prompt 模板 (QA/Quick/Overview/Compare)
├── knowledge_base/                  ← SOP 文档存放目录
├── samples/
│   └── sample_queries.txt           ← 示例问题集
└── workspace/                       ← 问答笔记输出
```

## VSCode

```
/sop-qa PM前需要做哪些安全准备?
```
