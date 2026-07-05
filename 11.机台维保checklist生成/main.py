#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SOP → Checklist 智能转换 Skill
===============================
读取SOP → LLM关键信息提炼 → 格式改写 → Checklist → workspace笔记
"""
import sys, os, json
from pathlib import Path
from datetime import date, datetime
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR / "workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

# ================================================================
# 1. SOP PARSER
# ================================================================

def parse_sop(file_path: str) -> dict:
    """Parse SOP document into structured text"""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in ('.md', '.markdown'):
        content = path.read_text(encoding='utf-8')
    elif suffix in ('.txt', '.log'):
        content = path.read_text(encoding='utf-8', errors='replace')
    elif suffix == '.pdf':
        try:
            import pdfplumber
            import logging
            logging.getLogger("pdfplumber").setLevel(logging.ERROR)
            text_parts = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: text_parts.append(t)
            content = '\n'.join(text_parts)
        except ImportError:
            content = f"[PDF需要pdfplumber库] {path.read_bytes()[:100]}"
    elif suffix == '.docx':
        try:
            from docx import Document
            doc = Document(str(path))
            content = '\n'.join(p.text for p in doc.paragraphs)
        except ImportError:
            content = f"[DOCX需要python-docx库] {path.read_bytes()[:100]}"
    else:
        content = path.read_text(encoding='utf-8', errors='replace')

    # Extract metadata
    meta = {}
    for line in content.split('\n')[:15]:
        m = re.match(r'^[>#*\s]*(SOP编号|文件编号|版本|设备|维护类型|预计工时|所需人员|生效日期)\s*[:：]\s*(.+)', line)
        if m:
            meta[m.group(1)] = m.group(2).strip()

    return {"file": file_path, "content": content, "meta": meta}

# ================================================================
# 2. CHECKLIST GENERATOR (LLM + Rule-based)
# ================================================================

SYSTEM_PROMPT = """你是半导体设备维护SOP专家。将SOP文档转换为可执行的Checklist。

## 提取规则:
1. 每个步骤必须包含: 序号、操作内容、检查标准/目标值、完成标记 [ ]
2. 保留原SOP的层级结构 (章→节→步骤)
3. 关键数值必须保留 (温度/压力/时间/尺寸阈值)
4. 安全步骤必须标注 ⚠️
5. 测量/验证步骤必须标注目标值
6. 签核步骤必须保留审批节点

## Checklist格式:
```markdown
## [步骤名称]
- [ ] [操作内容] | 标准: [目标值/检查标准] | 工具: [所需工具] ⚠️
```

## 原则:
- 顺序必须与SOP一致，不得遗漏
- 数值精度保留原SOP精度
- 安全关键步骤用 ⚠️ 标注
- 输出为 Markdown checklist 格式"""


def generate_checklist(sop_data: dict, use_llm: bool = True) -> str:
    """Generate checklist from SOP data"""
    content = sop_data["content"]
    meta = sop_data["meta"]

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    has_api = api_key.startswith("sk-ant-")

    if use_llm and has_api:
        return _llm_checklist(sop_data, api_key)
    else:
        return _rule_checklist(content, meta)


def _llm_checklist(sop_data: dict, api_key: str) -> str:
    """Use Claude to generate checklist"""
    try:
        import anthropic, os
        kwargs = {"api_key": api_key, "timeout": 300.0}
        base_url = os.getenv("ANTHROPIC_BASE_URL", "")
        if base_url:
            kwargs["base_url"] = base_url
        client = anthropic.Anthropic(**kwargs)
        meta_str = json.dumps(sop_data["meta"], ensure_ascii=False, indent=2)
        prompt = f"""请将以下SOP转换为Checklist格式。

## SOP元数据:
{meta_str}

## SOP正文:
{sop_data["content"][:8000]}

## 要求: 按章节输出Markdown Checklist，每项格式为 "- [ ] [操作] | 标准: [目标] | 工具: [工具]" """

        resp = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096, temperature=0.2,
            system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}])
        result = ""
        for block in resp.content:
            if hasattr(block, 'text'):
                result += block.text
        return result.strip()
    except Exception as e:
        return _rule_checklist(sop_data["content"], sop_data["meta"]) + f"\n\n> LLM生成失败({e}), 已使用规则引擎回退"


def _rule_checklist(content: str, meta: dict) -> str:
    """Rule-based checklist extraction"""
    lines = content.split('\n')
    checklist_lines = []
    current_section = ""
    step_counter = 0
    safety_count = 0
    section_steps = {}  # section_name → count

    # Metadata header
    checklist_lines.append("# SOP → Checklist 转换结果\n")
    checklist_lines.append("## 基本信息\n")
    checklist_lines.append("| 属性 | 值 |")
    checklist_lines.append("|------|-----|")
    for k, v in meta.items():
        checklist_lines.append(f"| {k} | {v} |")
    checklist_lines.append(f"| 转换日期 | {date.today().isoformat()} |")
    checklist_lines.append(f"| 转换引擎 | SOP2Checklist Skill v1.0 (规则引擎) |\n")
    checklist_lines.append("---\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Section headers
        h1 = re.match(r'^#\s+(.+)', stripped)
        h2 = re.match(r'^##\s+(.+)', stripped)
        h3 = re.match(r'^###\s+(.+)', stripped)

        if h1:
            current_section = h1.group(1)
            section_steps[current_section] = 0
            checklist_lines.append(f"## {current_section}\n")
        elif h2:
            current_section = h2.group(1)
            section_steps[current_section] = 0
            checklist_lines.append(f"### {current_section}\n")
        elif h3:
            current_section = h3.group(1)
            section_steps[current_section] = 0
            checklist_lines.append(f"#### {current_section}\n")
        elif re.match(r'^\d+\.\d+', stripped) or re.match(r'^\d+\.\s', stripped):
            # Numbered step
            step_text = re.sub(r'^\d+\.\d*\.?\s*', '', stripped)
            step_text = re.sub(r'^\d+\.\s*', '', step_text)

            # Skip pure sub-headers (no actionable verb)
            if re.match(r'^[一-鿿]+[：:]\s*$', step_text) and len(step_text) < 20:
                checklist_lines.append(f"**{step_text.rstrip('：:')}**")
                continue

            # Extract target values
            targets = re.findall(r'[<＞≥≤]\s*[\d.]+(?:×\d+)?\s*(?:°C|ppm|mm|Torr|min|mTorr|MΩ|mbar)?', step_text)
            target_str = f" | 标准: {'; '.join(targets)}" if targets else ""

            # Detect safety keywords
            is_safety = any(kw in step_text for kw in ['EMO', 'PPE', '安全', '警示', '通风', '泄漏', '有害', '检漏'])
            safety_mark = " ⚠️" if is_safety else ""
            if is_safety:
                safety_count += 1

            # Detect tools
            tools = re.findall(r'(扭矩扳手|吊具|无尘布|IPA|专用清洁剂|真空吸尘器|Scotch-Brite|塞尺|O-ring pick|真空脂|热像仪|氦检漏仪|网络分析仪|N2|DI Water)', step_text)

            step_counter += 1
            if current_section and current_section in section_steps:
                section_steps[current_section] += 1

            tool_str = f" | 工具: {', '.join(tools)}" if tools else ""
            checklist_lines.append(f"- [ ] {step_text[:120]}{target_str}{tool_str}{safety_mark}")

    if step_counter == 0:
        for line in lines:
            stripped = line.strip()
            m = re.match(r'^(\d+[\.\d]*)\s+(.+)', stripped)
            if m:
                step_text = m.group(2)
                is_safety = any(kw in step_text for kw in ['EMO', 'PPE', '安全', '警示', '通风', '泄漏', '有害'])
                safety_mark = " ⚠️" if is_safety else ""
                checklist_lines.append(f"- [ ] {step_text[:120]}{safety_mark}")

    if not any(l.startswith('- [ ]') for l in checklist_lines):
        checklist_lines.append("\n> ⚠️ 未能从SOP中自动提取步骤，请检查SOP格式或使用LLM模式")
        return '\n'.join(checklist_lines)

    # === APPEND: Summary + Sign-off ===
    summary = []
    summary.append("\n---\n")
    summary.append("## 完成统计\n")
    summary.append(f"- 总步骤: **{step_counter}** 项\n")
    summary.append(f"- 安全关键步骤 (⚠️): **{safety_count}** 项\n")
    summary.append(f"- 检查项含标准值: **{sum(1 for l in checklist_lines if '标准:' in l)}** 项\n")
    summary.append(f"- 检查项含工具: **{sum(1 for l in checklist_lines if '工具:' in l)}** 项\n")
    summary.append("")
    summary.append("## 各章节步骤分布\n")
    summary.append("| 章节 | 步骤数 |")
    summary.append("|------|--------|")
    for sec, count in section_steps.items():
        if count > 0:
            summary.append(f"| {sec} | {count} |")
    summary.append("")

    summary.append("## 签核栏\n")
    summary.append("| 角色 | 姓名 | 签字 | 日期 | 备注 |")
    summary.append("|------|------|------|------|------|")
    for role in ["执行工程师", "复核技术员", "主管审核"]:
        summary.append(f"| {role} | ________ | ________ | ____/____/____ | |")
    summary.append("")

    return '\n'.join(checklist_lines + summary)


# ================================================================
# 3. MAIN
# ================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="SOP → Checklist 转换器")
    parser.add_argument("-f", "--file", help="SOP文件路径", type=str,
                        default="samples/sample_sop_etch_chamber_pm.md")
    parser.add_argument("--llm", help="使用LLM模式 (需API Key)", action="store_true")
    parser.add_argument("-o", "--output", help="输出路径", type=str)
    args = parser.parse_args()

    print("=" * 50)
    print("  SOP → Checklist 智能转换 Skill")
    print("=" * 50)

    # Parse SOP
    print(f"\n[1/2] 解析SOP: {args.file}")
    sop_data = parse_sop(args.file)
    print(f"  元数据: {sop_data['meta']}")
    print(f"  正文字数: {len(sop_data['content'])}")

    # Generate checklist
    mode = "LLM" if args.llm else "规则引擎"
    print(f"\n[2/2] 生成Checklist (模式: {mode})...")
    checklist = generate_checklist(sop_data, use_llm=args.llm)

    # Save
    stem = Path(args.file).stem
    out = args.output or str(WORKSPACE_DIR / f"Checklist_{stem}_{date.today().isoformat()}.md")
    Path(out).write_text(checklist, encoding='utf-8')

    step_count = len(re.findall(r'^- \[ \]', checklist, re.MULTILINE))
    print(f"  提取步骤: {step_count}")
    print(f"  输出: {out}")
    print(f"\n[DONE] Checklist生成完成!")

if __name__ == "__main__":
    main()
