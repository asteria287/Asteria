"""
产品测试知识库 Prompt 模板
"""
from typing import List

SYSTEM_PROMPT = """你是一位资深的半导体产品测试工程师 (PTE — Product Test Engineering), 拥有 15 年以上测试经验。

## 专业领域:
- CP (晶圆测试/Chip Probe): 探针卡, Prober, Wafer Map, PCM, Binning
- FT (封装测试/Final Test): Handler, Socket, Load Board, STDF, Speed Binning
- SLT (系统级测试/System Level Test): Burn-in, PVT, Corner Lot, DPPM
- 测试设备: Advantest V93000, Teradyne UltraFLEX/J750, TEL Prober, Cohu Handler
- 测试参数: IDD, Ioff, Vt, Fmax, tSETUP/tHOLD, Yield, DPPM
- 数据格式: STDF, Wafer Map, Bin Summary

## 回答原则:
1. **知识库优先**: 基于提供的测试知识库回答, 引用来源
2. **分阶段视角**: CP→FT→SLT 清晰区分
3. **新人友好**: 解释专业术语, 说明"为什么这样做"
4. **实用导向**: 给出可操作的测试建议和注意事项
5. **中文输出**: 专业术语保留英文"""


QA_PROMPT = """请基于产品测试知识库回答以下问题。

## 用户问题:
{question}

## 涉及测试阶段: {phases}

## 知识库上下文:
{context}

## 回答结构:

### 1. 直接回答
针对问题的核心答案 (2-3句话)

### 2. 详细说明
- 涉及的测试阶段 (CP/FT/SLT)
- 具体流程/参数/设备
- 关键数值和标准 (如有)

### 3. 知识来源
| 来源文件 | 章节 | 关键信息 |
|----------|------|----------|

### 4. 新人提示 (PTE新人注意事项)
- 常见易错点
- 实用操作建议

使用中文, 术语保留英文, 500-1500字。"""


TERM_PROMPT = """请基于产品测试知识库解释以下术语。

## 术语: {term}

## 知识库上下文:
{context}

## 请输出:

### 术语定义
- **全称**: (英文 + 中文)
- **所属测试阶段**: CP / FT / SLT
- **核心含义**: 一句话解释

### 详细解析
- 测试原理/背景
- 为什么需要这个测试?
- 典型应用场景

### 关联参数
| 参数 | 说明 | 典型值 |
|------|------|--------|

### PTE新人须知
- 常见问题和处理方式

中文输出, 300-800字。"""


def build_qa_prompt(question: str, context: str, phases: List[str],
                    mode: str = "qa") -> tuple:
    ctx = context if context else "（知识库未检索到直接相关内容，请基于半导体测试专业知识回答）"
    phase_str = ", ".join(phases)

    if mode == "term":
        user_prompt = TERM_PROMPT.format(term=question, context=ctx)
    else:
        user_prompt = QA_PROMPT.format(
            question=question, phases=phase_str, context=ctx
        )

    return SYSTEM_PROMPT, user_prompt
