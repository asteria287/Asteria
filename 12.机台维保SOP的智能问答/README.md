# SOP 智能问答系统

半导体设备维保 SOP 知识库 + AI 智能问答。作为 EM 部门新人，通过自然语言提问即可获得准确的 SOP 步骤答案。

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env  # 配置 ANTHROPIC_API_KEY (可选, 离线也可用)

# 1. 导入 SOP 文档
python main.py --import samples/sample_sop_etch_chamber_pm.md

# 2. 开始问答
python main.py
```

## 能力

1. **智能问答**: 自然语言提问 → SOP 步骤级精确回答
2. **安全标注**: 自动识别安全关键步骤, ⚠️ 优先展示
3. **数值引用**: 精确还原 SOP 中的标准值/阈值
4. **工具清单**: 自动汇总操作所需工具和物料
5. **来源追溯**: 每条回答标注 [文件名] > 章节号
6. **离线可用**: 无需 API Key 也可获得 SOP 检索结果
7. **多格式导入**: 支持 .md / .txt / .pdf / .docx

## 使用场景

作为 EM 部门新人, 你可以这样使用:

```bash
# 想了解 PM 前要做什么?
python main.py -q "PM保养前需要做哪些安全准备?"

# 操作中途忘记了清洁步骤?
python main.py -q "上电极Shower Head怎么清洁?" --quick

# 不确定某个标准值?
python main.py -q "ESC静电卡盘检查的标准值是多少?"

# 想知道需要哪些工具?
python main.py -q "更换O-ring需要准备什么工具?"

# PM 完成后要做哪些验证?
python main.py -q "腔体恢复后需要做什么验证测试?"

# 快速浏览整个 SOP 结构
python main.py --overview
```

## 支持的问题类型

| 类型 | 示例 |
|------|------|
| 步骤询问 | "XX 操作的步骤是什么?" |
| 安全确认 | "XX 前有哪些安全注意事项?" |
| 数值标准 | "XX 的标准值/阈值是多少?" |
| 工具需求 | "XX 需要哪些工具和物料?" |
| 检查项目 | "XX 检查包含哪些测试?" |
| 异常处理 | "XX 不通过/不合格怎么办?" |
| 记录签核 | "PM 完成后需要填写什么?" |

## 添加更多 SOP

将你的 SOP 文档放入 `knowledge_base/` 目录或使用 `--import`:

```bash
python main.py --import "CVD_PM_SOP.pdf"
python main.py --import "PVD_Weekly_PM.docx"
python main.py --import "my_custom_sop.md"
```
