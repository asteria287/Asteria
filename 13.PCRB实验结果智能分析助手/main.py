#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PCRB 实验结果智能分析助手
==========================
背景: OP部门 YI/PI/DI 新人, 掌握 PCRB 实验数据分析。

核心逻辑:
  1. 最优组 = 参数0与Baseline最相近的组
  2. 按参数组(Category)找出相对Baseline最异常的参数
  3. 绘制异常程度Top N箱体图 + LLM按类别总结
  4. 生成综合报告 → WorkSpace 笔记

使用:
  python main.py --sample                              # 示例数据
  python main.py -f data.csv                           # 基础分析
  python main.py -f data.csv --report                  # 含AI报告
"""

import argparse, json, sys, os
from pathlib import Path
from typing import Dict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from agent.config import PCRBConfig
from agent.data_loader import PCRBDataLoader
from agent.experiment_analyzer import ExperimentAnalyzer
from agent.visualizer import PCRBVisualizer
from agent.report_generator import ReportGenerator
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def print_banner():
    print(r"""
+======================================================================+
|  PCRB 实验结果智能分析助手 — OP 部门实验数据分析                         |
+======================================================================+
""")


def stream_print(text: str):
    print(text, end="", flush=True)


def generate_sample_csv(output_path: Path) -> str:
    """生成 PCRB 实验 Demo CSV (5组 × 16参数 × 8样本)"""
    np.random.seed(42)
    n = 8
    groups = ["Baseline", "Split_A", "Split_B", "Split_C", "Split_D"]
    params = [
        "Vt_SAT_NMOS", "Vt_SAT_PMOS", "Idsat_NMOS", "Idsat_PMOS",
        "Ioff_NMOS", "Ioff_PMOS", "Vbd", "Rs_Contact",
        "Cgd_Overlap", "Gate_Leakage", "DIBL", "SS_NMOS",
        "SS_PMOS", "Yield_Pct", "Fmax_GHz", "Noise_dBm",
    ]

    base_means = {
        "Vt_SAT_NMOS": 0.350, "Vt_SAT_PMOS": -0.380, "Idsat_NMOS": 650.0,
        "Idsat_PMOS": -320.0, "Ioff_NMOS": 1.5e-9, "Ioff_PMOS": 1.2e-9,
        "Vbd": 5.2, "Rs_Contact": 12.5, "Cgd_Overlap": 0.250,
        "Gate_Leakage": 2.0e-11, "DIBL": 45.0, "SS_NMOS": 72.0,
        "SS_PMOS": 74.0, "Yield_Pct": 92.5, "Fmax_GHz": 28.0,
        "Noise_dBm": -145.0,
    }
    base_stds = {k: abs(v * 0.03) + 0.001 for k, v in base_means.items()}

    # Split_A: 参数0(Vt_SAT_NMOS) 非常接近Baseline → should be best
    # Split_B: moderate deviation
    # Split_C: 参数0偏移最大
    # Split_D: 参数0偏移第二大
    offsets = {
        "Split_A": {"Vt_SAT_NMOS": -0.001, "Idsat_NMOS": 15.0, "SS_NMOS": -1.5, "Fmax_GHz": 0.8, "Yield_Pct": 1.0},
        "Split_B": {"Vt_SAT_NMOS": -0.015, "Idsat_NMOS": 25.0, "Ioff_NMOS": 1.0e-9, "DIBL": 5.0, "Vbd": -0.3},
        "Split_C": {"Vt_SAT_NMOS": -0.035, "Idsat_NMOS": 35.0, "Ioff_NMOS": -0.5e-9, "SS_NMOS": -3.0, "Fmax_GHz": 2.5},
        "Split_D": {"Vt_SAT_NMOS": -0.025, "Ioff_NMOS": 2.0e-9, "Gate_Leakage": 3.0e-11, "DIBL": 10.0, "Rs_Contact": 3.0, "Vbd": -0.8},
    }

    rows = []
    for group in groups:
        for i in range(n):
            row = {"Group": group}
            for p in params:
                val = np.random.normal(base_means[p], base_stds[p])
                if group in offsets and p in offsets[group]:
                    val += offsets[group][p]
                row[p] = round(val, 8) if abs(val) < 1e-3 else round(val, 6)
            rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return str(output_path)


def run_analysis(filepath: str, args) -> Dict:
    """完整 PCRB 分析"""
    # 1. Load
    print(f"\n[LOAD] {filepath}")
    df = PCRBDataLoader.load(filepath)
    info = PCRBDataLoader.validate(df)
    print(f"[LOAD] {info['rows']}行 × {info['cols']}列, "
          f"GroupCol={info['group_col']}, Groups={len(info['groups'])}")
    for issue in info.get("issues", []):
        print(f"  ⚠️ {issue}")

    group_col = info["group_col"]
    param_cols = info["param_cols"]
    baseline = args.baseline or PCRBDataLoader.detect_baseline(df, group_col, info["groups"])
    param0 = param_cols[0]
    param_categories = PCRBConfig.classify_params(param_cols)

    print(f"[CONFIG] Baseline={baseline}, 参数0={param0}")
    print(f"[CONFIG] 参数组: {len(param_categories)} 类 → {dict((k, len(v)) for k, v in param_categories.items())}")

    # 2. Prepare
    group_data = PCRBDataLoader.prepare_analysis_data(df, group_col, param_cols)

    # 3. Analyze
    print(f"\n[ANALYZE] 统计分析 (最优组=参数0与Baseline最相近)...")
    analyzer = ExperimentAnalyzer(group_data, baseline, param_cols, param_categories)
    result = analyzer.full_analysis()
    summary = result["summary"]

    # Best group display
    selection = result["selection"]
    print(f"\n{'=' * 60}")
    print(f"最优组: {summary['best_group']} (参数0={param0}, |Δ%|={summary['best_delta_pct']:.2f}%)")
    print(f"{'=' * 60}")
    print(f"\n参数0对比排名:")
    for r in selection["ranking"]:
        marker = " ← 最优" if r["rank"] == 1 else ""
        print(f"  #{r['rank']} {r['group']}: mean={r['param0_mean']:.4f}, "
              f"BL={r['baseline_mean']:.4f}, |Δ%|={r['delta_pct_abs']:.2f}%{marker}")

    # Category-based abnormal params
    comparison = result["comparison"]
    if comparison:
        print(f"\n--- 按参数组类别 — 最异常参数 (最优组 vs Baseline) ---")
        for cat_name, cat_result in comparison["categories"].items():
            ma = cat_result.get("most_abnormal")
            if ma:
                print(f"  [{cat_name}] 🔥 {ma['param']}: "
                      f"Z={ma['z_score']:.1f}, Δ={ma['delta_pct']:+.1f}%, "
                      f"d={ma['effect_size']:.2f}, p={ma['p_value']:.4f}")

        print(f"\n--- Top 10 异常参数 (跨类别, |Z|降序) ---")
        for i, a in enumerate(comparison["overall_most_abnormal"][:10]):
            print(f"  {i + 1}. [{a['category']}] {a['param']}: "
                  f"Z={a['z_score']:.1f}, Δ={a['delta_pct']:+.1f}%, "
                  f"d={a['effect_size']:.2f}, {'✅显著' if a['significant'] else '➖'}")

    # 4. Visualize
    print(f"\n[VIZ] 生成图表...")
    viz = PCRBVisualizer(OUTPUT_DIR)

    box_path = viz.plot_boxplot_top_params(
        group_data, param_cols, baseline,
        best_group=summary["best_group"],
        anova_results=result["anova"],
        top_n=PCRBConfig.TOP_N_PARAMS,
    )
    if box_path:
        print(f"[VIZ] 箱体图: {box_path}")

    rank_path = viz.plot_ranking_chart(
        [{"group": r["group"], "score": 1.0 / (1.0 + r["delta_pct_abs"]),
          "stability_score": 0, "improvement_score": 0, "abnormal_count": 0}
         for r in selection["ranking"]],
        filename="pcrb_param0_ranking.png"
    )
    if rank_path:
        print(f"[VIZ] 参数0排名图: {rank_path}")

    # 5. AI Report
    if args.report:
        print(f"\n[REPORT] 生成 AI 分析报告...")
        reporter = ReportGenerator()
        report_res = reporter.generate_report(
            result,
            stream_callback=stream_print if not args.no_stream else None,
            save_note=not args.no_save,
        )
        if args.no_stream:
            print(report_res["answer"])
        if report_res.get("note_path"):
            print(f"\n[NOTE] Workspace报告: {report_res['note_path']}")
        print(f"[REPORT] 耗时: {report_res['elapsed']:.1f}s")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="PCRB 实验结果智能分析助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --sample                  # 使用示例数据
  python main.py -f data.csv               # 基础分析
  python main.py -f data.csv --report      # 含AI报告
        """,
    )
    parser.add_argument("-f", "--file", type=str, help="PCRB实验数据 (.csv/.xlsx)")
    parser.add_argument("--sample", action="store_true", help="使用示例数据")
    parser.add_argument("--baseline", type=str, help="指定Baseline组名")
    parser.add_argument("--report", action="store_true", help="生成AI报告 (需API Key)")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    parser.add_argument("--stats", action="store_true", help="仅显示数据统计")

    args = parser.parse_args()
    print_banner()

    if args.sample:
        sample_path = PCRBConfig.SAMPLES_DIR / "sample_pcrb_data.csv"
        if not sample_path.exists():
            print(f"[SAMPLE] 生成Demo CSV...")
            generate_sample_csv(sample_path)
        args.file = str(sample_path)

    if not args.file:
        print("[ERROR] 请指定数据文件 (-f) 或 --sample")
        sys.exit(1)

    if args.stats:
        df = PCRBDataLoader.load(args.file)
        info = PCRBDataLoader.validate(df)
        print(json.dumps(info, ensure_ascii=False, indent=2))
        # Show categories
        cats = PCRBConfig.classify_params(info["param_cols"])
        print("\n[CATEGORIES] 参数组分类:")
        for cat, params in cats.items():
            print(f"  {cat}: {params}")
        return

    run_analysis(args.file, args)
    print("\n[DONE] PCRB 实验分析完成。")


if __name__ == "__main__":
    main()
