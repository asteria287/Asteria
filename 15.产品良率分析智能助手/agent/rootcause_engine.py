"""
异常根因定位引擎
分析维度: 测试程式 / 测试机台 / 批次 / 产品 / 失效Bin → Top 5相关因子
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from scipy import stats
from .config import YieldConfig


class RootCauseEngine:
    """良率异常根因定位器"""

    def __init__(self, df: pd.DataFrame, anomaly_indices: List[int]):
        self.df = df.copy()
        self.anomaly_indices = anomaly_indices
        self.df["is_anomaly"] = self.df.index.isin(anomaly_indices)
        self.cfg = YieldConfig
        self._add_bin_features()

    def _add_bin_features(self):
        """聚合 Bin 特征"""
        bin_cols = [c for c in self.df.columns if c.startswith("Bin")]
        if bin_cols:
            self.df["Total_Bin_Fail"] = self.df[bin_cols].sum(axis=1)
            for c in bin_cols:
                self.df[f"{c}_Pct"] = self.df[c] / self.df["Total_Bin_Fail"] * 100

    # ═══════════════════════════════════════
    # 1. 测试程式关联分析
    # ═══════════════════════════════════════
    def analyze_program(self) -> Dict:
        return self._factor_analysis("Program", "测试程式")

    # ═══════════════════════════════════════
    # 2. 测试机台关联分析
    # ═══════════════════════════════════════
    def analyze_tester(self) -> Dict:
        return self._factor_analysis("Tester", "测试机台")

    # ═══════════════════════════════════════
    # 3. 产品类型关联分析
    # ═══════════════════════════════════════
    def analyze_product(self) -> Dict:
        return self._factor_analysis("Product", "产品类型")

    def _factor_analysis(self, col: str, label: str) -> Dict:
        """通用因子分析 — 卡方检验 + 异常率"""
        results = []
        for val in self.df[col].unique():
            subset = self.df[self.df[col] == val]
            n_total = len(subset)
            n_anom = subset["is_anomaly"].sum()
            anom_rate = n_anom / n_total * 100 if n_total > 0 else 0
            avg_yield = subset["CP_Yield"].mean()

            # 卡方检验
            contingency = pd.crosstab(self.df[col] == val, self.df["is_anomaly"])
            chi2, p_value = 0, 1.0
            if contingency.shape == (2, 2):
                try:
                    chi2, p_value, _, _ = stats.chi2_contingency(contingency)
                except Exception:
                    pass

            results.append({
                "value": str(val), "total_lots": n_total,
                "anomaly_count": n_anom, "anomaly_rate": round(anom_rate, 1),
                "avg_yield": round(avg_yield, 2),
                "chi2": round(chi2, 2), "p_value": round(p_value, 4),
                "significant": p_value < 0.05,
            })

        results.sort(key=lambda x: x["anomaly_rate"], reverse=True)
        return {"dimension": label, "factor_column": col, "results": results}

    # ═══════════════════════════════════════
    # 4. 失效Bin Pareto分析
    # ═══════════════════════════════════════
    def analyze_bins(self) -> Dict:
        bin_cols = [c for c in self.df.columns if c.startswith("Bin") and not c.endswith("_Pct")]
        normal = self.df[~self.df["is_anomaly"]]
        anom = self.df[self.df["is_anomaly"]]

        results = []
        for c in bin_cols:
            n_avg = normal[c].mean() if len(normal) > 0 else 0
            a_avg = anom[c].mean() if len(anom) > 0 else 0
            delta = a_avg - n_avg
            delta_pct = (delta / n_avg * 100) if n_avg > 0 else 0
            results.append({
                "bin": c, "normal_avg": round(n_avg, 2),
                "anomaly_avg": round(a_avg, 2),
                "delta": round(delta, 2), "delta_pct": round(delta_pct, 1),
            })

        results.sort(key=lambda x: abs(x["delta"]), reverse=True)
        return {"dimension": "失效Bin", "results": results}

    # ═══════════════════════════════════════
    # 5. Top 5 根因因子
    # ═══════════════════════════════════════
    def top_factors(self) -> List[Dict]:
        """综合所有维度 → Top 5 相关因子"""
        all_factors = []

        for analyzer in [self.analyze_program, self.analyze_tester, self.analyze_product]:
            result = analyzer()
            for r in result["results"]:
                if r.get("significant") or r["anomaly_rate"] > 20:
                    all_factors.append({
                        "dimension": result["dimension"],
                        "factor": r["value"],
                        "anomaly_rate": r["anomaly_rate"],
                        "avg_yield": r["avg_yield"],
                        "chi2": r.get("chi2", 0),
                        "p_value": r.get("p_value", 1),
                        "significant": r.get("significant", False),
                        "score": r["anomaly_rate"] * (1 + (0.5 if r.get("significant") else 0)),
                    })

        # Bin贡献
        bin_result = self.analyze_bins()
        for r in bin_result["results"][:5]:
            if abs(r["delta_pct"]) > 10:
                all_factors.append({
                    "dimension": "失效Bin",
                    "factor": r["bin"],
                    "anomaly_rate": 0,
                    "avg_yield": 0,
                    "chi2": 0,
                    "p_value": 1,
                    "significant": abs(r["delta_pct"]) > 30,
                    "score": abs(r["delta_pct"]) / 10,
                    "delta_pct": r["delta_pct"],
                })

        all_factors.sort(key=lambda x: x["score"], reverse=True)
        return all_factors[:self.cfg.TOP_N_FACTORS]

    # ═══════════════════════════════════════
    # 6. 综合根因报告
    # ═══════════════════════════════════════
    def full_analysis(self) -> Dict:
        return {
            "program_analysis": self.analyze_program(),
            "tester_analysis": self.analyze_tester(),
            "product_analysis": self.analyze_product(),
            "bin_analysis": self.analyze_bins(),
            "top_factors": self.top_factors(),
            "summary": {
                "total_lots": len(self.df),
                "anomaly_lots": int(self.df["is_anomaly"].sum()),
                "anomaly_rate": round(self.df["is_anomaly"].mean() * 100, 1),
            },
        }
