#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
产品良率分析智能助手
====================
PTE部门 — 良率异常检测 + 根因定位 + 自动报告

核心能力:
  1. 良率异常检测: 3σ + CUSUM + 移动平均 + 趋势分析 → 异常类型/等级
  2. 根因定位: 测试程式/机台/批次/产品/失效Bin → Top 5相关因子
  3. 可视化 + 报告生成

使用:
  python main.py --sample                              # 示例数据
  python main.py -f yield_data.csv                      # 分析数据
  python main.py -f yield_data.csv --report             # AI报告
"""

import argparse, sys, os, json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from agent.config import YieldConfig
from agent.data_generator import generate_yield_data
from agent.anomaly_detector import YieldAnomalyDetector
from agent.rootcause_engine import RootCauseEngine
from agent.visualizer import YieldVisualizer
from dotenv import load_dotenv

load_dotenv()


def print_banner():
    print(r"""
+======================================================================+
|  产品良率分析智能助手 — PTE Yield Analysis                             |
|  Anomaly Detection + Root Cause Localization                          |
+======================================================================+
""")


def stream_print(text: str):
    print(text, end="", flush=True)


def run_analysis(filepath: str, args):
    import pandas as pd

    # 1. Load
    print(f"\n[LOAD] {filepath}")
    df = pd.read_csv(filepath)
    print(f"[LOAD] {len(df)} rows, {len(df.columns)} cols")
    print(f"[LOAD] Columns: {list(df.columns)[:8]}...")

    # 2. Anomaly Detection
    print(f"\n[DETECT] 良率异常检测...")
    detector = YieldAnomalyDetector(df["CP_Yield"].values, df["Date"].tolist())
    detection = detector.full_detection()
    s = detection["summary"]
    print(f"[DETECT] {s['anomaly_count']}/{s['total_points']} 异常点 ({s['anomaly_rate']}%)")
    print(f"[DETECT] 3σ: {s['sigma_anomalies']} | MA: {s['moving_avg_anomalies']} | CUSUM: {s['cusum_anomalies']}")
    print(f"[DETECT] 趋势下降: {s['has_trending_decline']} | 综合等级: {s['overall_severity']}")

    # List anomalies
    for a in detection["anomalies"][:8]:
        print(f"  [{a['date']}] Yield={a['yield']:.1f}% Z={a.get('z_score','?')} "
              f"Type={a.get('type','?')} Sev={a.get('severity','?')} Method={a.get('method','?')}")

    # 3. Root Cause
    print(f"\n[ROOTCAUSE] 根因定位...")
    anomaly_idx = [a["index"] for a in detection["anomalies"]]
    engine = RootCauseEngine(df, anomaly_idx)
    rootcause = engine.full_analysis()
    top = rootcause["top_factors"]
    print(f"[ROOTCAUSE] Top {len(top)} 相关因子:")
    for i, f in enumerate(top):
        sig = "✅显著" if f.get("significant") else ""
        print(f"  #{i+1} [{f['dimension']}] {f['factor']}: "
              f"异常率={f.get('anomaly_rate',0):.0f}% p={f.get('p_value',1):.4f} {sig}")

    # 4. Visualize
    print(f"\n[VIZ] 生成图表...")
    viz = YieldVisualizer(YieldConfig.OUTPUT_DIR)
    ts_path = viz.plot_yield_timeseries(
        df["Date"].tolist(), df["CP_Yield"].values,
        detection["anomalies"], detection["summary"]["trend_info"],
    )
    print(f"[VIZ] 时间序列: {ts_path}")

    pareto_path = viz.plot_bin_pareto(rootcause["bin_analysis"])
    if pareto_path:
        print(f"[VIZ] Bin Pareto: {pareto_path}")

    factor_data = {k: rootcause[k] for k in ["program_analysis", "tester_analysis", "product_analysis"]}
    heat_path = viz.plot_factor_heatmap(factor_data)
    if heat_path:
        print(f"[VIZ] 因子热力图: {heat_path}")

    # 5. Report
    if args.report:
        print(f"\n[REPORT] 生成AI报告...")
        from prompts.yield_prompts import build_prompt
        system_prompt, user_prompt = build_prompt(detection, rootcause, YieldConfig.TOP_N_FACTORS)

        if YieldConfig.is_available():
            try:
                import anthropic
                kwargs = {"api_key": YieldConfig.API_KEY, "timeout": 300.0}
                if YieldConfig.BASE_URL:
                    kwargs["base_url"] = YieldConfig.BASE_URL
                client = anthropic.Anthropic(**kwargs)

                if args.no_stream:
                    resp = client.messages.create(
                        model=YieldConfig.MODEL, max_tokens=YieldConfig.MAX_TOKENS,
                        temperature=YieldConfig.TEMPERATURE,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                    answer = ""
                    for block in resp.content:
                        if hasattr(block, 'text'):
                            answer += block.text
                    print(answer)
                else:
                    with client.messages.stream(
                        model=YieldConfig.MODEL, max_tokens=YieldConfig.MAX_TOKENS,
                        temperature=YieldConfig.TEMPERATURE,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    ) as stream:
                        for text in stream.text_stream:
                            print(text, end="", flush=True)
                print()
            except Exception as e:
                print(f"[REPORT] LLM失败: {e}\n离线报告已生成")
        else:
            print("[REPORT] 离线模式 — 统计结果如上")

    return detection, rootcause


def main():
    parser = argparse.ArgumentParser(description="产品良率分析智能助手")
    parser.add_argument("-f", "--file", type=str, help="良率数据CSV")
    parser.add_argument("--sample", action="store_true", help="使用示例数据")
    parser.add_argument("--report", action="store_true", help="生成AI报告")
    parser.add_argument("--no-stream", action="store_true")
    args = parser.parse_args()
    print_banner()

    if args.sample:
        sample_path = YieldConfig.SAMPLES_DIR / "sample_yield_data.csv"
        generate_yield_data(str(sample_path))
        args.file = str(sample_path)
        print(f"[SAMPLE] 生成示例数据: {sample_path}")

    if not args.file:
        print("[ERROR] 请指定 -f 或 --sample")
        sys.exit(1)

    run_analysis(args.file, args)
    print("\n[DONE] 良率分析完成。")


if __name__ == "__main__":
    main()
