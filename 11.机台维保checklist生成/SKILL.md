---
name: sop2checklist
description: SOP→Checklist智能转换。读取设备维保SOP文档(支持.md/.txt/.pdf/.docx)，提炼关键信息(步骤/标准值/工具/安全项)，转换为可执行Checklist格式(含签核栏)，输出workspace笔记。触发条件：SOP转换、生成checklist、维保清单、SOP提取、操作步骤清单、机台PM checklist。
---

# SOP2Checklist — 设备维保SOP智能转换Skill

## 核心能力

将半导体设备维保 SOP 文档自动转换为结构化的 **可执行 Checklist**，提取关键信息并标注安全项、标准值、工具需求。

## 支持的文档格式

| 格式 | 解析引擎 | 说明 |
|------|----------|------|
| `.md` / `.markdown` | 直接读取 | 保留Markdown层级结构 |
| `.txt` | 直接读取 | 按行解析编号步骤 |
| `.pdf` | pdfplumber | 按页提取文本 + 表格 |
| `.docx` | python-docx | 段落级提取 |

## 转换流程

```
┌─────────────┐
│  SOP 文档    │  (.md/.txt/.pdf/.docx)
└──────┬──────┘
       │ parse_sop()
       ▼
┌─────────────┐
│ 元数据提取   │  编号/版本/设备/维护类型/工时/人员
│ 层级解析     │  章→节→步骤 (保留原结构)
└──────┬──────┘
       │
       ├──→ LLM模式 (--llm): Claude API 智能提炼
       │    System: 半导体设备维护SOP专家
       │    Prompt: meta JSON + SOP正文
       │
       └──→ 规则引擎 (默认): 正则提取步骤/标准值/工具/安全项
            │
            ▼
┌─────────────────────────────────┐
│  Checklist 输出                  │
│  - [ ] 操作步骤 | 标准: <值>    │
│  ⚠️ 安全关键步骤自动标记          │
│  工具: 自动识别所需工具           │
│  签核栏: 执行/复核/审核           │
│  完成统计: 总步骤/安全项/标准项   │
└─────────────────────────────────┘
```

## Checklist 特征

| 特征 | 说明 | 示例 |
|------|------|------|
| 可勾选 `- [ ]` | 每步骤可逐项确认 | `- [ ] 确认机台状态为 IDLE` |
| 标准值 | 自动提取阈值/目标 | `标准: <40°C; < 5ppm` |
| 工具标注 | 自动识别工具名称 | `工具: 扭矩扳手, 氦检漏仪` |
| 安全标记 ⚠️ | EMO/PPE/泄漏/通风 | `⚠️` 标注关键安全步骤 |
| 签核栏 | 三级审批 | 执行工程师 / 复核技术员 / 主管审核 |
| 完成统计 | 自动汇总 | 总58步, 安全6项, 标准10项, 工具16项 |

## 项目路径

```
C:\Users\28144\Desktop\长鑫培训预演\11.机台维保checklist生成\
```

## 使用

```bash
cd "C:\Users\28144\Desktop\长鑫培训预演\11.机台维保checklist生成"

# 默认规则引擎 (无需API, 即时转换)
python main.py -f samples/sample_sop_etch_chamber_pm.md

# LLM模式 (需配置 ANTHROPIC_API_KEY)
python main.py -f samples/sample_sop_etch_chamber_pm.md --llm

# 指定输出路径
python main.py -f my_sop.pdf -o workspace/my_checklist.md
```

## 项目文件结构

```
11.机台维保checklist生成/
├── SKILL.md                         ← 本文件
├── main.py                          ← SOP解析 + Checklist生成引擎
├── samples/
│   └── sample_sop_etch_chamber_pm.md ← 示例SOP (Etch Chamber PM)
├── workspace/
│   ├── Checklist_*.md               ← 生成的Checklist
│   └── SOP2Checklist_完整报告.md     ← workspace报告
└── requirements.txt
```

## VSCode

```
/sop2checklist 将这份SOP转成checklist
```
