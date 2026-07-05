#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SOP 智能问答系统 — 基于机台维保 SOP 知识库的智能问答
=====================================================

使用方式:
    # 交互式问答
    python main.py

    # 单个问题
    python main.py -q "如何清洁腔体上电极?"

    # 快速问答 (简洁模式)
    python main.py -q "PM前安全准备有哪些?" --quick

    # SOP 概览
    python main.py --overview

    # 生成 Workspace 笔记
    python main.py -q "ESC检查的标准值是多少?" --note

    # 离线模式 (无需 API Key)
    python main.py -q "O-ring更换步骤?" --offline

    # 导入 SOP 文档到知识库
    python main.py --import my_sop.md

    # 批量问题 (从文件读取)
    python main.py --batch samples/sample_queries.txt
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent.config import SOPQConfig
from agent.qa_engine import SOPQAEngine
from agent.doc_parser import SOPDocumentParser
from dotenv import load_dotenv

load_dotenv()

SAMPLE_QUERIES = [
    "进行PM保养前需要做哪些安全准备?",
    "上电极(Shower Head)的清洁步骤是什么?",
    "Focus Ring更换时需要注意什么标准值?",
    "ESC静电卡盘检查包含哪些测试项目?",
    "腔体恢复后需要做哪些验证测试?",
    "PM完成后需要填写哪些记录?",
    "O-ring更换的详细步骤和注意事项?",
    "真空漏率测试的标准是什么?",
]


def print_banner():
    print(r"""
+======================================================================+
|   SOP 智能问答系统 — 机台维保 SOP 知识库 + AI 问答                      |
|   SOP Intelligent Q&A System for Equipment Maintenance                |
+======================================================================+
""")


def stream_print(text: str):
    print(text, end="", flush=True)


def run_query(engine: SOPQAEngine, question: str, args):
    """执行单次问答"""
    print(f"\n[Q] {question}\n")
    print(f"{'─' * 60}")

    mode = "quick" if args.quick else "qa"

    if args.offline:
        original = SOPQConfig.ANTHROPIC_API_KEY
        SOPQConfig.ANTHROPIC_API_KEY = ""
        result = engine.query(question, mode=mode, save_note=args.note or args.save)
        SOPQConfig.ANTHROPIC_API_KEY = original
    else:
        sc = None if args.no_stream else stream_print
        result = engine.query(question, mode=mode,
                              stream_callback=sc,
                              save_note=args.note or args.save)

    if args.no_stream or args.offline:
        print(result["answer"])

    print(f"\n{'─' * 60}")
    print(f"[TIME] {result['elapsed']:.1f}s", end="")
    tokens = result.get("tokens_used", {})
    if tokens.get("input", 0) > 0:
        print(f" | [TOKEN] {tokens['input']}入/{tokens['output']}出", end="")
    if result.get("note_path"):
        print(f"\n[NOTE] 笔记已保存: {result['note_path']}", end="")
    print()


def import_sop(filepath: str) -> bool:
    """导入 SOP 文档到知识库"""
    fp = Path(filepath)
    if not fp.exists():
        print(f"[ERR] 文件不存在: {filepath}")
        return False

    ext = fp.suffix.lower()
    if ext not in SOPDocumentParser.SUPPORTED_EXT:
        print(f"[ERR] 不支持的格式: {ext}")
        return False

    try:
        doc = SOPDocumentParser.parse(filepath)
    except Exception as e:
        print(f"[ERR] 解析失败: {e}")
        return False

    # Copy to knowledge_base
    dest = SOPQConfig.KB_DIR / fp.name
    if ext == '.md' or ext == '.txt':
        dest.write_text(doc["raw_text"], encoding="utf-8")
    else:
        # For PDF/DOCX, save parsed markdown
        md_name = fp.stem + '.md'
        dest = SOPQConfig.KB_DIR / md_name
        md_content = _build_markdown_from_parsed(doc)
        dest.write_text(md_content, encoding="utf-8")

    print(f"[IMPORT] ✅ 已导入: {fp.name}")
    print(f"[IMPORT] → {dest}")
    print(f"[IMPORT] 元数据: {json.dumps(doc['metadata'], ensure_ascii=False, indent=2)}")
    print(f"[IMPORT] 章节数: {len(doc['sections'])}")
    print(f"[IMPORT] 安全项: {len(doc['safety_items'])}")
    print(f"[IMPORT] 工具: {len(doc['tool_list'])}")
    print(f"[IMPORT] 标准值: {len(doc['standard_values'])}")

    # Reload retriever
    print(f"[IMPORT] 知识库已更新, 重启后生效或重新初始化引擎。")
    return True


def _build_markdown_from_parsed(doc: Dict) -> str:
    """将解析结果转回 Markdown (用于 PDF/DOCX → KB)"""
    lines = []
    meta = doc.get("metadata", {})
    if meta:
        lines.append(f"> 文件编号: {meta.get('doc_id', 'N/A')}")
        lines.append(f"> 版本: {meta.get('version', 'N/A')}")
        lines.append(f"> 设备: {meta.get('equipment', 'N/A')}")
        lines.append(f"> 维护类型: {meta.get('maintenance_type', 'N/A')}")
        lines.append(f"> 预计工时: {meta.get('estimated_time', 'N/A')}")
        lines.append(f"> 所需人员: {meta.get('personnel', 'N/A')}")
        lines.append("")

    for sec in doc.get("sections", []):
        prefix = "#" * max(1, min(sec.get("level", 2), 4))
        num = sec.get("number", "")
        heading = f"{num} {sec['heading']}" if num else sec["heading"]
        lines.append(f"{prefix} {heading}")
        if sec.get("is_safety"):
            lines.append(f"⚠️ **安全关键步骤**")
        if sec.get("content"):
            lines.append(sec["content"])
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="SOP 智能问答系统 — 机台维保 SOP 知识库 + AI 问答",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                                                    # 交互模式
  python main.py -q "PM前安全准备步骤?"                               # 标准问答
  python main.py -q "如何更换O-ring?" --quick                        # 快速问答
  python main.py --overview                                          # SOP 概览
  python main.py -q "ESC检查标准值?" --note                           # 生成笔记
  python main.py -q "腔体清洁步骤?" --offline                          # 离线检索
  python main.py --import my_sop.pdf                                 # 导入 SOP
  python main.py --batch samples/sample_queries.txt                  # 批量问答
        """,
    )
    # Query modes
    parser.add_argument("-q", "--query", help="SOP 相关问题", type=str)
    parser.add_argument("--quick", help="快速简洁模式", action="store_true")
    parser.add_argument("--overview", help="SOP 文档概览", action="store_true")
    parser.add_argument("--compare", help="对比两个 SOP 条目 (用 vs 分隔)", type=str)
    # Batch
    parser.add_argument("--batch", help="批量问题文件 (每行一个问题)", type=str)
    # Output
    parser.add_argument("--note", help="保存为 Workspace 笔记", action="store_true")
    parser.add_argument("--save", help="保存结果到 workspace", action="store_true")
    parser.add_argument("--no-stream", help="禁用流式输出", action="store_true")
    # Modes
    parser.add_argument("--offline", help="离线模式 (无需 API Key)", action="store_true")
    # Import
    parser.add_argument("--import", dest="import_file", help="导入 SOP 文档到知识库", type=str)
    # Info
    parser.add_argument("--stats", help="知识库统计", action="store_true")
    parser.add_argument("--safety", help="列出所有安全项", action="store_true")
    parser.add_argument("--tools", help="列出所有工具清单", action="store_true")
    parser.add_argument("--samples", help="运行示例问题", action="store_true")

    args = parser.parse_args()

    print_banner()

    # ── 导入 SOP ──
    if args.import_file:
        import_sop(args.import_file)
        return

    # ── 初始化 ──
    engine = SOPQAEngine()
    stats = engine.retriever.get_stats()

    print(f"[KB] SOP 知识库: {stats['documents']} 文档, {stats['sections']} 章节")
    print(f"[KB] 索引: {stats['keywords']} 关键词, {stats['concepts']} 概念")
    if stats['files']:
        print(f"[KB] 文件: {', '.join(stats['files'])}")
    else:
        print(f"[KB] ⚠️ 知识库为空, 请先用 --import 导入 SOP 文档")
    if engine.is_available:
        print(f"[AI] LLM: {SOPQConfig.MODEL} (已连接)")
    else:
        print(f"[AI] LLM: 未配置 API Key, 离线模式可用")
    print()

    # ── 统计 ──
    if args.stats:
        return

    # ── 安全列表 ──
    if args.safety:
        items = engine.get_safety_checks()
        print(f"[SAFETY] 共 {len(items)} 项安全相关条目:\n")
        for i, item in enumerate(items, 1):
            print(f"  {i}. [{item['source']}] {item['section']} {item['heading']}")
            print(f"     {item['content'][:120]}...")
        return

    # ── 工具列表 ──
    if args.tools:
        tools = engine.retriever.list_tools()
        print(f"[TOOLS] 共 {len(tools)} 种工具/物料:\n")
        for t in tools:
            print(f"  - {t}")
        return

    # ── SOP 概览 ──
    if args.overview:
        context = engine.retriever.build_context("安全准备 腔体清洁 消耗件更换 部件检查 恢复验证 记录签核")
        if engine.is_available and not args.offline:
            print("[OVERVIEW] 正在生成 SOP 概览...\n")
            result = engine.query(
                "请生成这份SOP的完整概览",
                mode="overview",
                stream_callback=stream_print if not args.no_stream else None,
                save_note=True,
            )
            if args.no_stream:
                print(result["answer"])
            print(f"\n{'─' * 60}")
            print(f"[NOTE] 笔记已保存: {result.get('note_path', 'N/A')}")
        else:
            print("[OVERVIEW] 离线模式 — 显示 SOP 知识库内容:\n")
            print(context)
        return

    # ── 对比 ──
    if args.compare:
        print(f"[COMPARE] 对比: {args.compare}")
        result = engine.query(
            args.compare, mode="compare",
            stream_callback=stream_print if not args.no_stream else None,
            save_note=True,
        )
        if args.no_stream:
            print(result["answer"])
        print()
        return

    # ── 执行查询 ──
    if args.query:
        run_query(engine, args.query, args)
    elif args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"[ERR] 文件不存在: {args.batch}")
            sys.exit(1)
        queries = [l.strip() for l in batch_path.read_text(encoding="utf-8").split('\n') if l.strip()]
        print(f"[BATCH] {len(queries)} 个问题\n")
        for i, q in enumerate(queries, 1):
            print(f"\n{'=' * 60}")
            print(f"[{i}/{len(queries)}]")
            run_query(engine, q, args)
    elif args.samples:
        print(f"[SAMPLES] 运行 {len(SAMPLE_QUERIES)} 个示例问题\n")
        for i, q in enumerate(SAMPLE_QUERIES[:4], 1):
            print(f"\n{'=' * 60}")
            print(f"[{i}/{4}]")
            args.offline = True
            args.save = True
            run_query(engine, q, args)
    else:
        # ── 交互模式 ──
        print("[INTERACTIVE] SOP 智能问答 — 交互模式")
        print("  输入 SOP 相关问题, 或输入以下命令:")
        print("  :samples  — 运行示例问题")
        print("  :safety   — 列出安全项")
        print("  :tools    — 列出工具清单")
        print("  :overview — SOP 概览")
        print("  :stats    — 知识库统计")
        print("  :q        — 退出")
        print()

        while True:
            try:
                q = input("SOP> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not q:
                continue
            if q == ":q":
                break
            if q == ":stats":
                s = engine.retriever.get_stats()
                print(f"  文档: {s['documents']}, 章节: {s['sections']}, "
                      f"关键词: {s['keywords']}, 概念: {s['concepts']}")
                print(f"  文件: {', '.join(s['files']) if s['files'] else '（空）'}")
                continue
            if q == ":safety":
                items = engine.get_safety_checks()
                print(f"  安全项: {len(items)} 条")
                for item in items[:10]:
                    print(f"  - [{item['source']}] {item['section']} {item['heading']}")
                continue
            if q == ":tools":
                tools = engine.retriever.list_tools()
                print(f"  工具/物料: {len(tools)} 种")
                for t in tools:
                    print(f"  - {t}")
                continue
            if q == ":overview":
                print("  [生成 SOP 概览...]")
                ctx = engine.retriever.build_context("安全准备 腔体清洁 消耗件更换 部件检查 恢复与验证")
                print(ctx[:2000])
                continue
            if q == ":samples":
                print(f"  示例问题:")
                for i, sq in enumerate(SAMPLE_QUERIES, 1):
                    print(f"  {i}. {sq}")
                print()
                continue

            # Default: offline mode in interactive
            args.offline = True
            args.note = True
            args.save = True
            args.quick = False
            run_query(engine, q, args)

    print("\n[DONE] SOP 智能问答完成。")


if __name__ == "__main__":
    main()
