"""
PCRB 实验数据加载器
支持 CSV / Excel (.xlsx) 格式
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class PCRBDataLoader:
    """PCRB 实验数据加载 + 验证 + 预处理"""

    SUPPORTED_EXTS = {'.csv', '.xlsx', '.xls'}

    @staticmethod
    def load(filepath: str) -> pd.DataFrame:
        """加载 PCRB 实验数据"""
        fp = Path(filepath)
        if not fp.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")

        ext = fp.suffix.lower()
        if ext == '.csv':
            df = pd.read_csv(fp)
        elif ext in ('.xlsx', '.xls'):
            df = pd.read_excel(fp)
        else:
            raise ValueError(f"不支持的格式: {ext} (支持: .csv/.xlsx/.xls)")

        return df

    @staticmethod
    def validate(df: pd.DataFrame) -> Dict:
        """
        验证数据结构, 返回元信息

        Returns:
            {
                "valid": bool,
                "rows": int, "cols": int,
                "group_col": str,           # 检测到的分组列名
                "groups": [str],             # 所有分组名
                "param_cols": [str],         # 数值参数列
                "numeric_cols": [str],       # 所有数值列
                "issues": [str],             # 数据问题
            }
        """
        info = {
            "valid": True,
            "rows": len(df),
            "cols": len(df.columns),
            "group_col": None,
            "groups": [],
            "param_cols": [],
            "numeric_cols": [],
            "issues": [],
        }

        # 检测分组列 (名称含 group/split/lot/recipe/condition/experiment/wfr/wafer/baseline)
        group_pattern = re.compile(
            r'(group|split|lot|recipe|condition|experiment|分组|组别|实验组|'
            r'wfr|wafer|baseline|id|name|label|target)',
            re.IGNORECASE
        )
        for col in df.columns:
            if group_pattern.search(str(col)):
                info["group_col"] = str(col)
                break

        if info["group_col"] is None:
            # 第一列如果是字符串类型, 当作分组列
            for col in df.columns:
                if df[col].dtype == 'object' and df[col].nunique() <= 20:
                    info["group_col"] = str(col)
                    info["issues"].append(f"自动将 '{col}' 识别为分组列, 请确认")
                    break

        if info["group_col"] is None:
            info["valid"] = False
            info["issues"].append("未找到分组列, 数据需包含分组/实验组列")
            return info

        # 分组信息
        info["groups"] = df[info["group_col"]].dropna().unique().tolist()

        # 数值列
        for col in df.columns:
            if col == info["group_col"]:
                continue
            if pd.api.types.is_numeric_dtype(df[col]):
                info["numeric_cols"].append(str(col))

        # 参数列 = 非分组数值列
        info["param_cols"] = info["numeric_cols"][:]

        if len(info["param_cols"]) == 0:
            info["valid"] = False
            info["issues"].append("未找到数值参数列")

        # 检查缺失值
        for col in info["param_cols"]:
            missing = df[col].isna().sum()
            if missing > 0:
                info["issues"].append(f"列 '{col}' 有 {missing} 个缺失值")

        # 检查每组样本量
        gc = info["group_col"]
        for g in info["groups"]:
            n = len(df[df[gc] == g])
            if n < 3:
                info["issues"].append(f"组 '{g}' 样本量仅 {n}, 统计结果可能不可靠")

        return info

    @staticmethod
    def detect_baseline(df: pd.DataFrame, group_col: str, groups: List[str]) -> str:
        """自动检测 baseline 组"""
        # 1. 名称匹配
        baseline_pattern = re.compile(
            r'(baseline|basal|基准|control|ctrl|ref|reference|std|standard|'
            r'POR|default|normal|current|baseline_split)',
            re.IGNORECASE
        )
        for g in groups:
            if baseline_pattern.search(str(g)):
                return str(g)

        # 2. 第一个组
        return str(groups[0])

    @staticmethod
    def prepare_analysis_data(df: pd.DataFrame, group_col: str,
                              param_cols: List[str]) -> Dict[str, pd.DataFrame]:
        """按分组拆分数据, 返回 {group_name: DataFrame[param_cols]}"""
        result = {}
        for g in df[group_col].unique():
            mask = df[group_col] == g
            result[str(g)] = df.loc[mask, param_cols].copy()
        return result
