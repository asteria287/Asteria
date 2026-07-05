#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QRA 质量事件分析与结案 — 8D报告 + 案例推荐 + Workspace过程记录
================================================================
背景: QRA新人, 学习质量事件分析手法(5W1H/5-Why/鱼骨图/8D)
功能:
  1. 5W+1H 案件登记 → Workspace
  2. 相似案例推荐 (案例库检索)
  3. 8D报告生成 + 评审
  4. 案例归档 + 分享

3个案例分组练习 (Case1: CP探针 / Case2: FT Handler / Case3: SLT FW)

使用:
  python main.py --list-cases                  # 列出3个案例
  python main.py --case case1                  # 完成案例1全流程
  python main.py --case case2 --recommend      # 案例2 + 推荐相似案例
  python main.py --workshop                    # 3组工作坊模式
"""

import argparse, sys, os, re
from pathlib import Path
from datetime import date

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent.config import QRAConfig
from agent.case_recommender import CaseRecommender
from agent.report8d_generator import Report8DGenerator


def print_banner():
    print(r"""
+======================================================================+
|  QRA 质量事件分析与结案 — 8D Report System                            |
|  Case Analysis + Root Cause + 8D Report + Knowledge Sharing          |
+======================================================================+
""")


def parse_case_from_lib(case_id: str) -> dict:
    """从 case_library.md 解析案例数据"""
    lib = QRAConfig.KB_DIR / "case_library.md"
    if not lib.exists():
        return {}

    text = lib.read_text(encoding="utf-8")
    # Find case section
    pattern = rf'## 案例{case_id[-1]}:(.+?)(?=## 案例|\Z)'
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return {}

    content = m.group(0)
    title = m.group(1).strip()

    def extract_field(field):
        fm = re.search(rf'\|\s*\*\*{field}\*\*\s*\|\s*(.+?)\s*\|', content)
        if fm:
            return fm.group(1).strip().lstrip("|").strip()
        return ""

    fivew = {
        "who": extract_field("Who"), "what": extract_field("What"),
        "when": extract_field("When"), "where": extract_field("Where"),
        "why": extract_field("Why"), "how": extract_field("How"),
    }

    # Extract 8D sections (table format: | D1 团队 | xxx |)
    d_sections = {}
    for d in ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]:
        dm = re.search(rf'\|\s*{d}\s+[^|]*\|\s*(.+?)\s*\|', content)
        if dm:
            d_sections[d.lower()] = dm.group(1).strip()

    return {
        "case_id": case_id, "title": title,
        "5w1h": fivew,
        "5w1h_formatted": "\n".join(f"| **{k.capitalize()}** | {v} |" for k, v in fivew.items()),
        "8d_sections": d_sections,
        "8d_summary": "\n".join(f"**{d.upper()}**: {v[:200]}" for d, v in d_sections.items()),
        "team": {"lead": extract_field("团队").split(",")[0] if extract_field("团队") else "",
                 "tech": "", "qra": "QRA代表", "others": ""},
        "rootcause_analysis": {"five_why": d_sections.get("d4", ""),
                               "ishikawa": "", "conclusion": d_sections.get("d4", "")[:200],
                               "lessons": ""},
        "is_isnot": "",
    }


def run_case(case_id: str, do_recommend: bool = True):
    """运行单个案例的完整8D流程"""
    case_data = parse_case_from_lib(case_id)
    if not case_data:
        print(f"[ERROR] 案例 {case_id} 未找到")
        return

    title = case_data["title"]
    print(f"\n{'=' * 60}")
    print(f"案件: {case_id} — {title}")
    print(f"{'=' * 60}")

    # Step 1: 5W+1H 登记
    print(f"\n[STEP 1] 5W+1H 案件登记")
    fw = case_data["5w1h"]
    print(f"  Who: {fw['who']}")
    print(f"  What: {fw['what']}")
    print(f"  When: {fw['when']}")
    print(f"  Where: {fw['where']}")
    print(f"  Why: {fw['why']}")
    print(f"  How: {fw['how']}")
    print(f"  ✅ 5W+1H已登记至Workspace")

    # Step 2: 案例推荐
    recommendations = []
    if do_recommend:
        print(f"\n[STEP 2] AI相似案例推荐")
        rec = CaseRecommender()
        query = f"{fw['what']} {fw['where']} {fw['why']}"
        recommendations = rec.recommend(query)
        for i, r in enumerate(recommendations):
            marker = " ← 当前" if r["case_id"] == case_id else ""
            print(f"  #{i+1} [{r['case_id']}] {r['title']} (相似度: {r['score']:.1f}){marker}")
            print(f"     关键词: {', '.join(r['keywords'][:5])}")

    # Step 3: 8D报告生成
    print(f"\n[STEP 3] 8D报告生成")
    gen = Report8DGenerator()

    # Workspace process record
    ws_dir = QRAConfig.WORKSPACE_DIR / case_id
    ws_dir.mkdir(parents=True, exist_ok=True)

    short_title = title.split("—")[0].strip()[:20]
    ws_record = gen.generate_workspace_record(case_id, case_data, recommendations)
    ws_path = ws_dir / f"案件登记_{case_id}.md"
    ws_path.write_text(ws_record, encoding="utf-8")
    print(f"  ✅ Workspace记录: {ws_path}")

    # 8D report
    case_data["_title_short"] = short_title
    report8d_path = gen.generate_8d(case_data, ws_dir)
    if report8d_path:
        print(f"  ✅ 8D报告: {report8d_path}")

    # Print 8D summary
    print(f"\n  8D各阶段状态:")
    for d in ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"]:
        status = "✅" if d in case_data.get("8d_sections", {}) else "⏳"
        d_name = d.upper()
        print(f"    {status} {d_name}")

    # Step 4: 评审 + 分享
    print(f"\n[STEP 4] 8D评审与分享")
    print(f"  ✅ 8D报告已完成, 待组长和QRA主管签核")
    print(f"  ✅ 案例已归档至QRA案例库")
    print(f"  📋 请将本案例分享给其他两组, 收集反馈建议")

    return case_data


def run_workshop():
    """3组工作坊模式 — 完整流程"""
    print(f"\n{'=' * 60}")
    print(f"QRA 质量事件分析工作坊 — 3组分组练习")
    print(f"{'=' * 60}")
    print(f"""
  分组安排:
    第1组 → Case 1: CP测试良率突降 — Probe Card针尖异常
    第2组 → Case 2: FT Handler卡料导致批次良率波动
    第3组 → Case 3: 新产品SLT Burn-in失效 — 固件时序问题

  流程:
    1. 各组完成5W+1H案件登记
    2. AI相似案例推荐
    3. 完成8D报告(D1-D8)
    4. 组内评审
    5. 跨组分享 → 收集其他两组建议
    6. 最终定稿归档
""")

    for case_id in ["case1", "case2", "case3"]:
        print(f"\n{'─' * 60}")
        print(f">>> 正在处理 {case_id} ...")
        run_case(case_id, do_recommend=True)

    print(f"\n{'=' * 60}")
    print(f"工作坊完成! 3个案例已全部处理。")
    print(f"工作目录: {QRAConfig.WORKSPACE_DIR}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="QRA质量事件分析助手")
    parser.add_argument("--case", type=str, choices=["case1", "case2", "case3"],
                        help="指定案例 (case1/case2/case3)")
    parser.add_argument("--workshop", action="store_true", help="3组工作坊模式")
    parser.add_argument("--list-cases", action="store_true", help="列出案例库")
    parser.add_argument("--recommend", action="store_true", help="启用案例推荐")
    parser.add_argument("--recommend-text", type=str, help="自定义问题描述推荐案例")
    args = parser.parse_args()
    print_banner()

    if args.list_cases:
        print("案例库:")
        for cid, ctitle in QRAConfig.CASES.items():
            print(f"  [{cid}] {ctitle}")
        return

    if args.recommend_text:
        rec = CaseRecommender()
        results = rec.recommend(args.recommend_text)
        print(f"\n推荐结果 (查询: {args.recommend_text}):")
        for i, r in enumerate(results):
            print(f"  #{i+1} [{r['case_id']}] {r['title']} (相似度: {r['score']:.1f})")
        return

    if args.case:
        run_case(args.case, do_recommend=args.recommend)
        return

    # Default: workshop mode
    run_workshop()


if __name__ == "__main__":
    main()
