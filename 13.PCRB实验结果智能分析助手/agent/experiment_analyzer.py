"""
PCRB 实验统计分析引擎
核心逻辑:
  1. 最优组 = 参数0与Baseline最相近的组 (|delta_pct|最小)
  2. 按参数组(Category)找出相对Baseline最异常的参数
  3. Z-score + t-test + ANOVA + Cohen's d
"""
from typing import Dict, List, Optional
import numpy as np
from scipy import stats
from .config import PCRBConfig


class ExperimentAnalyzer:
    """PCRB 实验结果统计分析器"""

    def __init__(self, group_data: Dict[str, 'pd.DataFrame'],
                 baseline_name: str,
                 param_cols: List[str],
                 param_categories: Optional[Dict[str, List[str]]] = None):
        """
        Args:
            group_data: {group_name: DataFrame[param_cols]}
            baseline_name: baseline 组名
            param_cols: 数值参数列名列表
            param_categories: {category: [param_names]} 参数分组
        """
        self.group_data = group_data
        self.baseline_name = baseline_name
        self.param_cols = param_cols
        self.param_categories = param_categories or PCRBConfig.classify_params(param_cols)
        self.groups = list(group_data.keys())
        self.config = PCRBConfig

        # 参数0 = 第一列数值参数
        self.param0 = param_cols[0] if param_cols else None

    # ═══════════════════════════════════════════════════════════
    # 1. 最优组选择: 参数0与Baseline最相近
    # ═══════════════════════════════════════════════════════════

    def select_best_group(self) -> Dict:
        """
        基于参数0与Baseline最相近选择最优组

        逻辑: 计算每组参数0的均值与Baseline参数0均值的delta_pct绝对值,
               |delta_pct|最小的组即为最优组。

        Returns:
            {
                "best_group": str,
                "param0_name": str,
                "ranking": [{group, param0_mean, baseline_mean, delta_pct, rank}],
            }
        """
        if self.baseline_name not in self.group_data:
            raise ValueError(f"Baseline '{self.baseline_name}' 不在数据中")
        if not self.param0:
            return {"best_group": None, "param0_name": None, "ranking": []}

        baseline_df = self.group_data[self.baseline_name]
        if self.param0 not in baseline_df.columns:
            return {"best_group": None, "param0_name": self.param0, "ranking": []}

        b_vals = baseline_df[self.param0].dropna().values
        b_mean = np.mean(b_vals) if len(b_vals) > 0 else 0.0

        ranking = []
        for group, df in self.group_data.items():
            if group == self.baseline_name:
                continue
            if self.param0 not in df.columns:
                continue

            g_vals = df[self.param0].dropna().values
            if len(g_vals) == 0:
                continue

            g_mean = np.mean(g_vals)
            delta = g_mean - b_mean
            delta_pct = abs(delta / b_mean * 100) if b_mean != 0 else float('inf')

            ranking.append({
                "group": str(group),
                "param0_name": self.param0,
                "param0_mean": round(g_mean, 6),
                "baseline_mean": round(b_mean, 6),
                "delta": round(delta, 6),
                "delta_pct_abs": round(delta_pct, 4),
                "delta_pct": round(delta / b_mean * 100 if b_mean != 0 else 0, 2),
            })

        # Sort by |delta_pct| ascending (closest = best)
        ranking.sort(key=lambda x: x["delta_pct_abs"])
        for i, r in enumerate(ranking):
            r["rank"] = i + 1

        best = ranking[0]["group"] if ranking else None
        return {
            "best_group": best,
            "param0_name": self.param0,
            "baseline_mean": round(b_mean, 6),
            "ranking": ranking,
        }

    # ═══════════════════════════════════════════════════════════
    # 2. Baseline 对比分析 (按参数组分类)
    # ═══════════════════════════════════════════════════════════

    def compare_to_baseline_by_category(self, target_group: str) -> Dict:
        """
        对比指定组 vs Baseline, 按参数组(Category)组织结果

        Returns:
            {
                "target_group": str,
                "baseline": str,
                "categories": {
                    category_name: {
                        "desc": str,
                        "params": {param: {statistical results}},
                        "most_abnormal": {param: {...}},   # 该类别中最异常的参数
                        "z_max": float,
                    }
                },
                "overall_most_abnormal": [{param, z_score, category, ...}]  # 跨类别排名
            }
        """
        if self.baseline_name not in self.group_data:
            raise ValueError(f"Baseline '{self.baseline_name}' 不在数据中")
        if target_group not in self.group_data:
            raise ValueError(f"目标组 '{target_group}' 不在数据中")

        baseline_df = self.group_data[self.baseline_name]
        target_df = self.group_data[target_group]

        categories = {}
        all_abnormal = []

        for cat_name, cat_params in self.param_categories.items():
            cat_desc = PCRBConfig.get_category_desc(cat_name)
            cat_result = {
                "desc": cat_desc,
                "params": {},
                "most_abnormal": None,
                "z_max": 0.0,
            }

            for param in cat_params:
                if param not in target_df.columns or param not in baseline_df.columns:
                    continue

                g_vals = target_df[param].dropna().values
                b_vals = baseline_df[param].dropna().values
                if len(g_vals) < 2 or len(b_vals) < 2:
                    continue

                g_mean, g_std = np.mean(g_vals), np.std(g_vals, ddof=1)
                b_mean, b_std = np.mean(b_vals), np.std(b_vals, ddof=1)

                delta = g_mean - b_mean
                delta_pct = (delta / b_mean * 100) if b_mean != 0 else 0.0

                # Z-score
                z_score = abs(delta) / b_std if b_std > 0 else 0.0

                # t-test
                try:
                    t_stat, p_value = stats.ttest_ind(g_vals, b_vals, equal_var=False)
                except Exception:
                    p_value = 1.0

                # Cohen's d
                pooled_std = np.sqrt((np.var(g_vals, ddof=1) + np.var(b_vals, ddof=1)) / 2)
                effect_size = abs(delta) / pooled_std if pooled_std > 0 else 0.0

                direction = "higher" if delta > 0 else "lower"
                significant = p_value < self.config.ALPHA

                param_result = {
                    "mean": round(g_mean, 6),
                    "std": round(g_std, 6),
                    "baseline_mean": round(b_mean, 6),
                    "baseline_std": round(b_std, 6),
                    "delta_mean": round(delta, 6),
                    "delta_pct": round(delta_pct, 2),
                    "z_score": round(z_score, 2),
                    "p_value": round(p_value, 4),
                    "significant": significant,
                    "direction": direction,
                    "effect_size": round(effect_size, 3),
                    "effect_magnitude": self._magnitude(effect_size),
                }

                cat_result["params"][param] = param_result

                # Track most abnormal in this category
                if z_score > cat_result["z_max"]:
                    cat_result["z_max"] = z_score
                    cat_result["most_abnormal"] = {
                        "param": param,
                        **param_result,
                    }

                # Track overall abnormal
                if significant or z_score > self.config.SIGMA_THRESHOLD:
                    all_abnormal.append({
                        "category": cat_name,
                        "param": param,
                        "z_score": z_score,
                        "delta_pct": delta_pct,
                        "direction": direction,
                        "p_value": p_value,
                        "significant": significant,
                        "effect_size": effect_size,
                        "effect_magnitude": param_result["effect_magnitude"],
                    })

            categories[cat_name] = cat_result

        # Sort overall abnormal by Z-score descending
        all_abnormal.sort(key=lambda x: x["z_score"], reverse=True)

        return {
            "target_group": target_group,
            "baseline": self.baseline_name,
            "categories": categories,
            "overall_most_abnormal": all_abnormal,
        }

    def _magnitude(self, effect_size: float) -> str:
        if effect_size < 0.2:
            return "negligible"
        elif effect_size < 0.5:
            return "small"
        elif effect_size < 0.8:
            return "medium"
        else:
            return "large"

    # ═══════════════════════════════════════════════════════════
    # 3. ANOVA 多组检验
    # ═══════════════════════════════════════════════════════════

    def anova_test(self) -> Dict:
        results = {}
        for param in self.param_cols:
            group_arrays, valid_groups = [], []
            for g in self.groups:
                if param in self.group_data[g].columns:
                    vals = self.group_data[g][param].dropna().values
                    if len(vals) >= 2:
                        group_arrays.append(vals)
                        valid_groups.append(g)
            if len(group_arrays) < 2:
                continue
            try:
                f_stat, p_value = stats.f_oneway(*group_arrays)
                results[param] = {
                    "f_statistic": round(f_stat, 4),
                    "p_value": round(p_value, 6),
                    "significant": p_value < self.config.ALPHA,
                    "category": PCRBConfig.classify_param(param),
                }
            except Exception:
                results[param] = {
                    "f_statistic": None, "p_value": None,
                    "significant": False,
                    "category": PCRBConfig.classify_param(param),
                }
        return results

    # ═══════════════════════════════════════════════════════════
    # 4. 一站式分析
    # ═══════════════════════════════════════════════════════════

    def full_analysis(self) -> Dict:
        """完整分析流程"""
        # 1. 最优组选择 (参数0最近)
        selection = self.select_best_group()
        best = selection.get("best_group")

        # 2. 最优组 vs Baseline (按参数组)
        comparison = None
        if best:
            comparison = self.compare_to_baseline_by_category(best)

        # 3. ANOVA
        anova = self.anova_test()

        return {
            "selection": selection,
            "comparison": comparison,
            "anova": anova,
            "summary": {
                "total_groups": len(self.groups),
                "total_params": len(self.param_cols),
                "total_categories": len(self.param_categories),
                "param0": self.param0,
                "baseline": self.baseline_name,
                "best_group": best,
                "best_delta_pct": selection["ranking"][0]["delta_pct_abs"] if selection.get("ranking") else None,
                "anova_significant_params": sum(1 for r in anova.values() if r.get("significant")),
                "abnormal_count": len(comparison["overall_most_abnormal"]) if comparison else 0,
            },
        }
