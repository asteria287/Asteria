"""
良率分析可视化 — 时间序列+异常标注 / Pareto / 热力图
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

COLORS = {"normal": "#43A047", "sudden_drop": "#E53935", "trending": "#FB8C00",
          "spike": "#8E24AA", "ma": "#1E88E5", "target": "#666666"}


class YieldVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_yield_timeseries(self, dates, yields, anomalies, trend_info,
                              filename="yield_timeseries.png") -> Path:
        """良率时间序列 + 异常标注 + 趋势线"""
        fig, ax = plt.subplots(figsize=(16, 6))
        x = range(len(yields))
        ax.plot(x, yields, '-o', color=COLORS["normal"], markersize=3, linewidth=1.2, label="CP Yield", alpha=0.8)

        # 移动平均线
        w = 5
        if len(yields) >= w:
            ma = np.convolve(yields, np.ones(w)/w, mode='valid')
            ax.plot(range(w-1, len(yields)), ma, '-', color=COLORS["ma"], linewidth=2, label=f"MA({w})", alpha=0.7)

        # 均值线
        mean_y = np.mean(yields)
        ax.axhline(mean_y, color=COLORS["target"], linestyle='--', linewidth=1, label=f"Mean ({mean_y:.1f}%)")

        # 标注异常点
        for a in anomalies:
            c = COLORS.get(a.get("type", "spike"), COLORS["spike"])
            ax.annotate(f'{a.get("severity", "")[:2]}', xy=(a["index"], a["yield"]),
                        fontsize=9, color=c, fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=c, lw=1.2))
            ax.scatter(a["index"], a["yield"], color=c, s=80, zorder=5, edgecolors='white')

        # 趋势标注
        if trend_info.get("has_negative_trend"):
            ax.text(0.98, 0.05, f'Trend: {trend_info["slope_per_day"]:.3f}/day | Drop: {trend_info["total_drop"]:.1f}%',
                    transform=ax.transAxes, ha='right', fontsize=10, color='red',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax.set_xlabel("Day", fontsize=11)
        ax.set_ylabel("CP Yield (%)", fontsize=11)
        ax.set_title("CP Yield Time Series — Anomaly Detection", fontsize=14, fontweight='bold')
        ax.legend(loc='lower left', fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        path = self.output_dir / filename
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return path

    def plot_bin_pareto(self, bin_analysis, filename="bin_pareto.png") -> Path:
        """失效Bin Pareto图"""
        results = bin_analysis.get("results", [])[:8]
        if not results:
            return None

        bins = [r["bin"].replace("Bin", "") for r in results]
        deltas = [abs(r["delta"]) for r in results]
        colors_bar = ['#E53935' if abs(r["delta_pct"]) > 30 else '#FB8C00' if abs(r["delta_pct"]) > 15 else '#1E88E5'
                      for r in results]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(bins, deltas, color=colors_bar, alpha=0.8, edgecolor='white')
        for bar, r in zip(bars, results):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{r["delta_pct"]:+.0f}%', ha='center', fontsize=9, fontweight='bold')

        ax.set_xlabel("Failure Bin", fontsize=11)
        ax.set_ylabel("Δ Failure Rate (anomaly - normal)", fontsize=11)
        ax.set_title("Failure Bin Contribution — Anomaly vs Normal", fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        fig.tight_layout()

        path = self.output_dir / filename
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return path

    def plot_factor_heatmap(self, factor_results, filename="factor_heatmap.png") -> Path:
        """因子关联热力图"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        for ax, (dim, data) in zip(axes, factor_results.items()):
            results = data.get("results", [])[:6]
            if not results:
                continue
            values = [r["anomaly_rate"] for r in results]
            labels = [r["value"][:15] for r in results]
            colors_h = ['#E53935' if v > 33 else '#FB8C00' if v > 15 else '#43A047' for v in values]
            ax.barh(range(len(labels)), values, color=colors_h, alpha=0.8)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_title(dim, fontsize=11, fontweight='bold')
            ax.set_xlabel("Anomaly Rate (%)")
            for i, v in enumerate(values):
                ax.text(v + 0.5, i, f'{v:.0f}%', va='center', fontsize=8)
        fig.suptitle("Factor Correlation Analysis — Anomaly Rate by Dimension", fontsize=13, fontweight='bold')
        fig.tight_layout()
        path = self.output_dir / filename
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return path
