"""
良率数据生成器 — 时间序列 + 关联因子 (含受控异常注入)
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_yield_data(output_path: str = None, n_days: int = 120) -> pd.DataFrame:
    np.random.seed(42)
    dates = [datetime(2026, 1, 1) + timedelta(days=i) for i in range(n_days)]

    testers = ["ATE_V93000_01", "ATE_V93000_02", "ATE_UltraFLEX_01", "ATE_J750_01"]
    programs = ["TP_DRAM_A_v3.2", "TP_NAND_B_v2.1", "TP_SoC_C_v1.8", "TP_DRAM_A_v3.1"]
    products = ["DDR5_16Gb", "NAND_512Gb", "SoC_A1", "DDR5_8Gb"]

    base_cp = 94.5
    rows = []

    for i, date in enumerate(dates):
        lot = f"LOT_{i+1:04d}"
        # 异常期间强制分配到特定程式和机台
        if 30 <= i <= 45:
            tester, program, product = "ATE_V93000_01", "TP_DRAM_A_v3.2", "DDR5_16Gb"
        elif 70 <= i <= 90:
            tester, program, product = "ATE_UltraFLEX_01", "TP_NAND_B_v2.1", "NAND_512Gb"
        else:
            idx = i % 4
            tester, program, product = testers[idx], programs[idx], products[idx]

        cp_yield = base_cp + np.random.normal(0, 0.6)
        anomaly_type = "normal"

        # 异常注入
        if 30 <= i <= 45:
            cp_yield -= np.random.uniform(4, 7)
            anomaly_type = "sudden_drop"
        elif 70 <= i <= 90:
            cp_yield -= (i - 68) * 0.4
            anomaly_type = "trending_decline"
        elif i in [55, 105]:
            cp_yield -= np.random.uniform(5, 8)
            anomaly_type = "spike"

        cp_yield = max(70, min(99, cp_yield))
        ft_yield = cp_yield + np.random.uniform(1.5, 4.0)
        ft_yield = max(80, min(99.5, ft_yield))

        total_fail = 100 - cp_yield
        bins = {
            "Bin1_Leakage": np.random.uniform(0.15, 0.30) * total_fail,
            "Bin2_Short": np.random.uniform(0.10, 0.20) * total_fail,
            "Bin3_Open": np.random.uniform(0.05, 0.15) * total_fail,
            "Bin4_VtFail": np.random.uniform(0.10, 0.25) * total_fail,
            "Bin5_FuncFail": np.random.uniform(0.15, 0.30) * total_fail,
            "Bin6_IDDQ": np.random.uniform(0.05, 0.10) * total_fail,
            "Bin7_Speed": np.random.uniform(0.05, 0.10) * total_fail,
            "Bin8_Other": np.random.uniform(0.02, 0.05) * total_fail,
        }
        if anomaly_type != "normal":
            bins["Bin1_Leakage"] *= 2.5
            bins["Bin4_VtFail"] *= 3.0

        rows.append({
            "Date": date.strftime("%Y-%m-%d"), "Lot": lot,
            "Tester": tester, "Program": program, "Product": product,
            "CP_Yield": round(cp_yield, 2), "FT_Yield": round(ft_yield, 2),
            "Anomaly_Type": anomaly_type,
            **{k: round(v, 2) for k, v in bins.items()},
        })

    df = pd.DataFrame(rows)
    if output_path:
        df.to_csv(output_path, index=False, encoding="utf-8")
    return df
