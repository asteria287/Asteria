"""
良率异常检测引擎
算法: 3σ/Z-score + 移动平均 + CUSUM + 趋势检测
"""
import numpy as np
from typing import Dict, List, Tuple
from .config import YieldConfig


class YieldAnomalyDetector:
    """良率时间序列异常检测器"""

    def __init__(self, yields: np.ndarray, dates: List[str] = None):
        self.yields = np.array(yields, dtype=float)
        self.dates = dates or [str(i) for i in range(len(yields))]
        self.n = len(yields)
        self.cfg = YieldConfig

    # ═══════════════════════════════════════════════
    # 1. 3σ / Z-Score 检测 (点异常)
    # ═══════════════════════════════════════════════
    def detect_sigma(self) -> List[Dict]:
        mean = np.mean(self.yields)
        std = np.std(self.yields, ddof=1)
        anomalies = []
        for i, y in enumerate(self.yields):
            z = abs(y - mean) / std if std > 0 else 0
            if z > self.cfg.SIGMA_THRESHOLD:
                anomalies.append({
                    "index": i, "date": self.dates[i], "yield": round(y, 2),
                    "z_score": round(z, 1), "mean": round(mean, 2),
                    "type": "spike_low" if y < mean else "spike_high",
                    "severity": "critical" if z > 5 else ("high" if z > 4 else "medium"),
                    "method": "3sigma",
                })
        return anomalies

    # ═══════════════════════════════════════════════
    # 2. 移动平均 + 残差检测 (趋势偏移)
    # ═══════════════════════════════════════════════
    def detect_moving_avg(self) -> List[Dict]:
        w = self.cfg.MA_WINDOW
        if self.n < w:
            return []
        ma = np.convolve(self.yields, np.ones(w)/w, mode='valid')
        residuals = self.yields[w-1:] - ma
        std_r = np.std(residuals, ddof=1) if np.std(residuals, ddof=1) > 0 else 1

        anomalies = []
        for i, r in enumerate(residuals):
            z = abs(r) / std_r
            if z > 2.5:
                idx = i + w - 1
                anomalies.append({
                    "index": idx, "date": self.dates[idx], "yield": round(self.yields[idx], 2),
                    "ma": round(ma[i], 2), "residual": round(r, 2),
                    "z_score": round(z, 1),
                    "type": "deviation_from_ma",
                    "severity": "high" if z > 4 else "medium",
                    "method": "moving_avg",
                })
        return anomalies

    # ═══════════════════════════════════════════════
    # 3. CUSUM 累积和检测 (持续性偏移)
    # ═══════════════════════════════════════════════
    def detect_cusum(self) -> List[Dict]:
        target = np.mean(self.yields)
        cusum_pos, cusum_neg = 0, 0
        anomalies = []
        for i, y in enumerate(self.yields):
            cusum_pos = max(0, cusum_pos + (y - target) - 0.5)
            cusum_neg = max(0, cusum_neg + (target - y) - 0.5)
            if cusum_neg > self.cfg.CUSUM_THRESHOLD:
                anomalies.append({
                    "index": i, "date": self.dates[i], "yield": round(y, 2),
                    "cusum_neg": round(cusum_neg, 1), "target": round(target, 2),
                    "type": "sustained_decline",
                    "severity": "critical" if cusum_neg > 10 else "high",
                    "method": "cusum",
                })
        return anomalies

    # ═══════════════════════════════════════════════
    # 4. 趋势检测 (线性回归斜率)
    # ═══════════════════════════════════════════════
    def detect_trend(self) -> Dict:
        w = min(self.cfg.TREND_WINDOW, self.n)
        recent = self.yields[-w:]
        x = np.arange(w)
        slope = np.polyfit(x, recent, 1)[0]
        total_drop = slope * w
        return {
            "slope_per_day": round(slope, 3),
            "total_drop": round(total_drop, 2),
            "window_days": w,
            "has_negative_trend": slope < -0.05,
            "trend_severity": ("critical" if total_drop < -5
                               else "high" if total_drop < -3
                               else "medium" if total_drop < -1.5
                               else "none"),
            "method": "trend_analysis",
        }

    # ═══════════════════════════════════════════════
    # 5. 综合异常报告
    # ═══════════════════════════════════════════════
    def full_detection(self) -> Dict:
        sigma = self.detect_sigma()
        ma_anoms = self.detect_moving_avg()
        cusum = self.detect_cusum()
        trend = self.detect_trend()

        # 合并去重 (保留最早检测)
        all_anoms = {}
        for a in sigma + ma_anoms + cusum:
            key = a["index"]
            if key not in all_anoms or a.get("severity", "") == "critical":
                all_anoms[key] = a

        anomalies = sorted(all_anoms.values(), key=lambda x: x["index"])

        # 异常分类
        sudden_drops = [a for a in sigma if a["type"] == "spike_low"]
        sustained = cusum
        trending = trend["has_negative_trend"]

        summary = {
            "total_points": self.n,
            "anomaly_count": len(anomalies),
            "anomaly_rate": round(len(anomalies) / self.n * 100, 1),
            "sigma_anomalies": len(sigma),
            "moving_avg_anomalies": len(ma_anoms),
            "cusum_anomalies": len(cusum),
            "has_trending_decline": trending,
            "trend_info": trend,
            "sudden_drop_count": len(sudden_drops),
            "sustained_decline_count": len(sustained),
            "overall_severity": (
                "critical" if any(a["severity"] == "critical" for a in anomalies)
                else "high" if len(anomalies) > 5
                else "medium" if len(anomalies) > 0
                else "normal"
            ),
        }

        return {
            "anomalies": anomalies,
            "summary": summary,
            "yield_stats": {
                "mean": round(np.mean(self.yields), 2),
                "std": round(np.std(self.yields, ddof=1), 2),
                "min": round(np.min(self.yields), 2),
                "max": round(np.max(self.yields), 2),
                "recent_avg": round(np.mean(self.yields[-10:]), 2),
            },
        }
