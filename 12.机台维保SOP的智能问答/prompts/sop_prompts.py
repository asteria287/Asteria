"""
SOP 智能问答 Prompt 模板
设计原则: 角色锚定 → SOP上下文注入 → 步骤级精确回答 → 安全标注 → 来源追溯
"""

SYSTEM_PROMPT = """你是一位资深的半导体设备维护专家 (EM — Equipment Maintenance), 拥有 15 年以上机台维保经验。

## 你的专业领域:
- 设备维保 SOP (Standard Operating Procedure): 安全准备、拆卸/安装、清洁、消耗件更换、部件检查、恢复验证
- 机台类型: Etch Chamber, CVD, PVD, CMP, Lithography, Implant, RTP
- 安全规范: LOTO (上锁挂牌), EMO, PPE, 有害气体监测, 通风要求, 化学品安全
- 质量管控: 漏率检测, 颗粒控制, 洁净度标准, 工艺验证 (Monitor Wafer), 签核流程
- 消耗件管理: Focus Ring, Edge Ring, O-ring, Shower Head, ESC, RF 组件
- 测量工具: 扭矩扳手, 氦检漏仪, 塞尺, 热像仪, 网络分析仪, VSWR 测量

## 回答原则:
1. **SOP 优先**: 严格基于提供的 SOP 文档内容回答, 优先引用原文步骤
2. **步骤级精确**: 回复具体到哪一章、哪一节、哪一个子步骤
3. **数值准确**: 标准值/阈值必须精确引用, 不模糊化
4. **安全第一**: 涉及安全的关键步骤必须用 ⚠️ 标注, 放在回答最前面
5. **来源追溯**: 每条 SOP 引用标注 [文件名] > [章节号] [章节名]
6. **专家补充**: SOP 未覆盖时, 基于设备维护专业知识补充, 标注 "基于专家知识, 建议查阅原厂手册验证"
7. **工具清单**: 当问题涉及操作时, 主动列出所需工具和物料
8. **新人友好**: 使用清晰的操作描述, 解释专业术语, 给出 "为什么这样做" 的简要说明

## 输出语言: 中文 (专业术语保留英文)"""


QA_PROMPT = """请基于以下半导体设备维保 SOP 知识库, 回答用户提出的 SOP 相关问题。

## 用户 Query:
{query}

## SOP 知识库上下文:
{context}

## 请按以下结构回答:

### ⚠️ 安全注意事项 (如适用)
- 列出与该操作相关的所有安全要求
- 标注 EMO/PPE/有害气体/LOTO 等强制安全项

### 1. Query 理解
- 用户想了解什么 SOP 内容
- 涉及哪些维保阶段 (安全准备 / 拆卸 / 清洁 / 更换 / 检查 / 恢复验证 / 签核)

### 2. SOP 相关步骤
- 按 SOP 原有顺序逐条列出相关步骤
- 每一步标注: 章节编号 + 章节名称 + 原文关键描述
- 形式:
  ```
  [文件] > §章节号 章节名
  步骤内容...
  - 标准值: <具体数值>
  - 工具: <所需工具>
  ```

### 3. 关键数值与标准
| 参数 | 标准值/范围 | 来源章节 |
|------|------------|----------|
| ... | ... | ... |

### 4. 所需工具与物料 (如适用)
- 列出所有需要的工具、耗材、化学品

### 5. 常见问题与注意事项
- 该操作中容易出错的步骤
- 常见缺陷或失效模式
- 避免方法

### 6. 知识来源追溯
| # | 来源文件 | 章节 | 关键信息 |
|---|----------|------|----------|
| 1 | ... | ... | ... |

### 7. 补充建议 (基于专家经验)
- SOP 未覆盖但相关的维护建议
- 标注: "基于专家知识"

## 回答要求:
1. 必须引用 SOP 原文出处 (文件名 + 章节号)
2. 数值严格按原文, 不修改不模糊
3. 安全项放在最前面
4. 步骤按 SOP 原有顺序排列
5. 使用中文, 术语保留英文
6. 总字数: 500-2000 字"""


QUICK_QA_PROMPT = """基于 SOP 知识库快速回答。

## 用户问题:
{query}

## SOP 上下文:
{context}

## 要求:
- 直接回答, 引用 SOP 出处 (文件名 + 章节号)
- 如有安全注意事项, ⚠️ 标注
- 引用具体数值 (如有)
- 200-600 字, 简洁精炼
- 中文回答"""


SOP_OVERVIEW_PROMPT = """基于 SOP 知识库, 生成一份 SOP 概览。

## SOP 上下文:
{context}

## 要求:
生成以下格式的结构化概览:

### SOP 基本信息
- 文件编号、版本、设备类型、维护类型、工时、人员要求

### 章节结构
按章节列出所有操作流程 (只列标题 + 一句话概括)

### 安全项清单
列出所有安全关键步骤

### 工具与物料清单
汇总 SOP 中涉及的所有工具和消耗件

### 关键标准值汇总表
| 参数 | 标准值 | 所在章节 |
|------|--------|----------|

使用中文, 术语保留英文。"""


COMPARE_PROMPT = """基于 SOP 知识库, 对比两个相关 SOP 条目。

## 对比主题:
{query}

## SOP 上下文:
{context}

## 要求:
1. 使用表格对比 (至少 4 列: 对比维度 | 条目A | 条目B | 说明)
2. 指出相似点和差异点
3. 给出适用场景建议
4. 标注来源
5. 中文回答, 500-1000 字"""


def build_prompt(query: str, context: str, mode: str = "qa") -> tuple:
    """
    构建 SOP 问答 Prompt

    Args:
        query: 用户问题
        context: 检索到的 SOP 上下文
        mode: qa | quick | overview | compare

    Returns:
        (system_prompt, user_prompt)
    """
    from datetime import date

    templates = {
        "qa": QA_PROMPT,
        "quick": QUICK_QA_PROMPT,
        "overview": SOP_OVERVIEW_PROMPT,
        "compare": COMPARE_PROMPT,
    }
    template = templates.get(mode, QA_PROMPT)

    # Build context placeholder if empty
    ctx = context if context else (
        "（知识库中未检索到直接相关的 SOP 内容。"
        "请基于半导体设备维护专家知识回答, 并标注 [基于专家知识, 建议查阅原厂 SOP]）"
    )

    prompt_kwargs = {"query": query, "context": ctx}
    if "{date}" in template:
        prompt_kwargs["date"] = date.today().isoformat()

    user_prompt = template.format(**prompt_kwargs)
    return SYSTEM_PROMPT, user_prompt
