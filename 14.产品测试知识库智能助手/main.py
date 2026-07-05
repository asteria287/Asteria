#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
产品测试知识库智能助手
======================
PTE 部门新人学习工具 — CP/FT/SLT 三大测试环节知识库 + AI 问答 + 术语解析

能力1: 知识问答 — 针对测试概念/流程/设备/参数的结构化回答
能力2: 术语解析 — 术语定义 + 测试阶段 + 关联参数 + 应用场景

使用:
  python main.py                                     # 交互模式
  python main.py -q "CP测试流程是什么?"                # 知识问答
  python main.py -t "RDBI"                            # 术语解析
  python main.py -q "FT和SLT的区别?" --report          # AI深度回答
"""

import argparse, sys, os
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent.config import TestKBConfig
from agent.qa_engine import TestQAEngine
from agent.terminology_engine import TerminologyEngine
from dotenv import load_dotenv

load_dotenv()

SAMPLE_QUERIES = [
    "CP测试的核心流程是什么?",
    "FT测试中Handler的作用是什么?",
    "什么是SLT系统级测试?为什么需要SLT?",
    "CP和FT的主要区别是什么?",
    "STDF数据格式是什么?",
]


def print_banner():
    print(r"""
+======================================================================+
|  产品测试知识库智能助手 — PTE 部门新人学习工具                          |
|  Product Test Knowledge Base Assistant (CP/FT/SLT)                    |
+======================================================================+
""")


def stream_print(text: str):
    print(text, end="", flush=True)


def main():
    parser = argparse.ArgumentParser(description="产品测试知识库智能助手")
    parser.add_argument("-q", "--query", type=str, help="测试相关问题")
    parser.add_argument("-t", "--term", type=str, help="术语解析 (如 RDBI, DC测试)")
    parser.add_argument("--report", action="store_true", help="AI深度回答 (需API Key)")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--stats", action="store_true", help="知识库统计")
    parser.add_argument("--samples", action="store_true", help="示例问题")

    args = parser.parse_args()
    print_banner()

    kb_config = TestKBConfig
    stats = {"documents": 4, "sections": 0, "keywords": 0, "terms": 0}

    try:
        from agent.retriever import TestKBRetriever
        r = TestKBRetriever()
        stats = r.get_stats()
    except Exception:
        pass

    print(f"[KB] 知识库: {stats['documents']} 文档, {stats['sections']} 章节, "
          f"{stats['keywords']} 关键词, {stats['terms']} 术语")
    if kb_config.is_available():
        print(f"[AI] LLM: {kb_config.MODEL} (已连接)")
    else:
        print(f"[AI] LLM: 未配置, 离线模式可用")
    print()

    # ── 统计 ──
    if args.stats:
        return

    # ── 术语解析 (能力2) ──
    if args.term:
        engine = TerminologyEngine()
        result = engine.lookup(args.term)
        print(engine.format_lookup_result(result))
        return

    # ── 知识问答 (能力1) ──
    engine = TestQAEngine()

    if args.query:
        print(f"[Q] {args.query}\n{'─' * 60}")
        mode = "qa"
        if args.report:
            mode = "qa"
            sc = None if args.no_stream else stream_print
            result = engine.ask(args.query, mode=mode, stream_callback=sc)
            if args.no_stream:
                print(result["answer"])
        else:
            result = engine.ask(args.query, mode=mode, stream_callback=None)
            print(result["answer"])

        print(f"\n{'─' * 60}")
        print(f"[TIME] {result['elapsed']:.1f}s | [PHASE] {', '.join(result.get('phases', []))}")
        if result.get("note_path"):
            print(f"[NOTE] {result['note_path']}")
    elif args.samples:
        print("[SAMPLES] 示例问题:\n")
        for i, q in enumerate(SAMPLE_QUERIES, 1):
            print(f"{'─' * 60}\n[{i}/{len(SAMPLE_QUERIES)}] {q}\n{'─' * 60}")
            result = engine.ask(q, mode="qa", stream_callback=None)
            print(result["answer"][:800])
            print()
    else:
        # 交互模式
        print("[INTERACTIVE] 产品测试知识问答 — 交互模式")
        print("  输入问题  → 知识问答 (能力1)")
        print("  :t <术语> → 术语解析 (能力2)")
        print("  :samples  → 示例问题")
        print("  :stats    → 知识库统计")
        print("  :q        → 退出\n")

        while True:
            try:
                q = input("Test> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not q:
                continue
            if q == ":q":
                break
            if q == ":stats":
                s = TestKBRetriever().get_stats()
                print(f"  文档: {s['documents']}, 章节: {s['sections']}, "
                      f"关键词: {s['keywords']}, 术语: {s['terms']}")
                continue
            if q == ":samples":
                for i, sq in enumerate(SAMPLE_QUERIES, 1):
                    print(f"  {i}. {sq}")
                continue
            if q.startswith(":t "):
                term = q[3:].strip()
                te = TerminologyEngine()
                print(te.format_lookup_result(te.lookup(term)))
                continue

            result = engine.ask(q, mode="qa", stream_callback=None)
            print(result["answer"][:1200])
            print()

    print("\n[DONE] 产品测试知识库助手。")


if __name__ == "__main__":
    main()
