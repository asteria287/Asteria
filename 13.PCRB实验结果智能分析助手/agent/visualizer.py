"""
PCRB 可视化 — 箱体图/排名图/对比图
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配色
COLORS = {
    "baseline": "#607D8B",
    "best": "#43A047",
    "others": ["#1E88E5", "#FB8C00", "#8E24AA", "#00ACC1", "#E53935",
               "#FDD835", "#6D4C41", "#546E7A", "#D81B60", "#7CB342"],
    "benefit": "#43A047",
    "drawback": "#E53935",
    "neutral": "#90A4AE",
}


class PCRBVisualizer:
    """PCRB 实验数据可视化器"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_boxplot_top_params(self, group_data: Dict[str, pd.DataFrame],
                                param_cols: List[str],
                                baseline_name: str,
                                best_group: Optional[str] = None,
                                top_n: int = 10,
                                anova_results: Optional[Dict] = None,
                                filename: str = "pcrb_boxplot_top_params.png") -> Path:
        """
        绘制 Top N 参数的箱体图 (每组一个子图, 按 ANOVA F 值排序)
        """
        # 按 ANOVA 显著性排序
        if anova_results:
            sorted_params = sorted(
                [p for p in param_cols if p in anova_results],
                key=lambda p: anova_results[p].get("f_statistic", 0) or 0,
                reverse=True
            )
        else:
            sorted_params = param_cols[:]

        params = sorted_params[:top_n]
        n_params = len(params)
        if n_params == 0:
            return None

        # Grid layout
        n_cols = min(3, n_params)
        n_rows = (n_params + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows))
        if n_params == 1:
            axes = [axes]
        else:
            axes = axes.flatten()

        groups = list(group_data.keys())
        group_colors = self._get_group_colors(groups, baseline_name, best_group)

        for idx, param in enumerate(params):
            ax = axes[idx]
            plot_data = []
            labels = []

            for g in groups:
                if param in group_data[g].columns:
                    vals = group_data[g][param].dropna().values
                    if len(vals) > 0:
                        plot_data.append(vals)
                        labels.append(str(g))

            if plot_data:
                bp = ax.boxplot(plot_data, patch_artist=True,
                                widths=0.6, showfliers=True, showmeans=True,
                                meanprops=dict(marker='D', markerfacecolor='red', markersize=6))
                ax.set_xticklabels(labels, rotation=30, fontsize=8)

                for patch, lbl in zip(bp['boxes'], labels):
                    color = group_colors.get(lbl, COLORS["others"][0])
                    patch.set_facecolor(color)
                    patch.set_alpha(0.6)

                # 标注 ANOVA
                if anova_results and param in anova_results:
                    ar = anova_results[param]
                    sig_text = f"ANOVA F={ar['f_statistic']:.2f}, p={ar['p_value']:.4f}"
                    color = '#E53935' if ar.get('significant') else '#666666'
                    ax.set_title(f"{param}\n{sig_text}", fontsize=10, fontweight='bold', color=color)
                else:
                    ax.set_title(param, fontsize=11, fontweight='bold')

                ax.grid(True, alpha=0.3, axis='y')
            else:
                ax.set_title(f"{param} (无数据)", fontsize=10)
                ax.axis('off')

        # 隐藏多余的 subplots
        for idx in range(n_params, len(axes)):
            axes[idx].set_visible(False)

        title = f"PCRB Top {n_params} 参数箱体图"
        if best_group:
            title += f" | 最优组: {best_group}"
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.01)
        fig.tight_layout()

        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return output_path

    def plot_ranking_chart(self, ranking: List[Dict],
                           filename: str = "pcrb_ranking.png") -> Path:
        """绘制实验组排名条形图"""
        if not ranking:
            return None

        groups = [r["group"] for r in ranking]
        scores = [r["score"] for r in ranking]
        stability = [r["stability_score"] for r in ranking]
        improvement = [r["improvement_score"] for r in ranking]

        fig, ax = plt.subplots(figsize=(10, max(4, len(groups) * 0.6)))

        y_pos = range(len(groups))
        colors = [COLORS["best"] if i == 0 else COLORS["others"][i % len(COLORS["others"])]
                  for i in range(len(groups))]

        bars = ax.barh(y_pos, scores, color=colors, alpha=0.8, edgecolor='white')

        # Score labels
        for i, (bar, s) in enumerate(zip(bars, scores)):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                    f'{s:.3f}', va='center', fontsize=11, fontweight='bold')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(groups, fontsize=11)
        ax.invert_yaxis()
        ax.set_xlabel('综合评分', fontsize=11)
        ax.set_title('PCRB 实验组综合排名 (最优→最差)', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # Annotate rank
        for i in range(len(groups)):
            ax.annotate(f'#{i + 1}', xy=(-0.08, i), xycoords=('axes fraction', 'data'),
                        fontsize=10, fontweight='bold', color='#666',
                        ha='right', va='center')

        fig.tight_layout()
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return output_path

    def plot_delta_heatmap(self, comparison: Dict,
                           top_n: int = 15,
                           filename: str = "pcrb_delta_heatmap.png") -> Path:
        """绘制 delta% 热力图 (组 × 参数)"""
        group_results = comparison.get("group_results", {})
        if not group_results:
            return None

        # 收集所有参数, 按最大|delta_pct|排序
        all_params = set()
        for gr in group_results.values():
            all_params.update(gr["params"].keys())

        param_deltas = {}
        for param in all_params:
            max_delta = max(
                abs(gr["params"].get(param, {}).get("delta_pct", 0))
                for gr in group_results.values()
                if param in gr.get("params", {})
            )
            param_deltas[param] = max_delta

        top_params = sorted(param_deltas, key=param_deltas.get, reverse=True)[:top_n]
        groups = list(group_results.keys())

        # Build matrix
        data = np.zeros((len(top_params), len(groups)))
        annot = np.empty((len(top_params), len(groups)), dtype=object)

        for i, param in enumerate(top_params):
            for j, group in enumerate(groups):
                p = group_results[group]["params"].get(param, {})
                d = p.get("delta_pct", 0)
                data[i, j] = d
                sig = " *" if p.get("significant") else ""
                annot[i, j] = f"{d:+.1f}%{sig}"

        fig, ax = plt.subplots(figsize=(max(8, len(groups) * 1.5),
                                        max(6, len(top_params) * 0.4)))

        cmap = plt.cm.RdBu_r
        im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=-np.max(np.abs(data)) * 1.1,
                       vmax=np.max(np.abs(data)) * 1.1)

        # Annotations
        for i in range(len(top_params)):
            for j in range(len(groups)):
                val = data[i, j]
                color = 'white' if abs(val) > np.max(np.abs(data)) * 0.5 else 'black'
                ax.text(j, i, annot[i, j], ha='center', va='center',
                        fontsize=8, color=color, fontweight='bold' if ' *' in annot[i, j] else 'normal')

        ax.set_xticks(range(len(groups)))
        ax.set_xticklabels(groups, rotation=45, ha='right', fontsize=9)
        ax.set_yticks(range(len(top_params)))
        ax.set_yticklabels(top_params, fontsize=9)
        ax.set_title(f'PCRB Delta% 热力图 (vs {comparison.get("baseline", "Baseline")})',
                     fontsize=13, fontweight='bold')
        fig.colorbar(im, ax=ax, label='Delta %', shrink=0.8)

        fig.tight_layout()
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return output_path

    def _get_group_colors(self, groups: List[str], baseline: str,
                          best_group: Optional[str]) -> Dict[str, str]:
        """为每组分配颜色"""
        colors = {}
        for i, g in enumerate(groups):
            if g == baseline:
                colors[g] = COLORS["baseline"]
            elif best_group and g == best_group:
                colors[g] = COLORS["best"]
            else:
                colors[g] = COLORS["others"][(i - 1) % len(COLORS["others"])]
        return colors
