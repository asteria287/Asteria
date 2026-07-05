"""
PCRB 实验结果分析 — 配置
"""
import os
import re
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class PCRBConfig:
    # Paths
    BASE_DIR = BASE_DIR
    SAMPLES_DIR = BASE_DIR / "samples"
    WORKSPACE_DIR = BASE_DIR / "workspace"

    # API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "")
    ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
    MODEL = os.getenv("AI_MODEL", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))
    MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "8192"))
    TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))

    # Analysis parameters
    DEFAULT_BASELINE = "Baseline"
    SIGMA_THRESHOLD = 2.0
    TOP_N_PARAMS = 10
    ALPHA = 0.05

    # ══════════════════════════════════════════════════
    # 参数组 (Category) 定义 — 按半导体工艺参数类别
    # ══════════════════════════════════════════════════
    PARAM_CATEGORIES: Dict[str, Dict] = {
        "Vt_阈值电压": {
            "keywords": ["Vt", "Vth", "threshold", "阈值"],
            "desc_cn": "阈值电压参数 — 决定晶体管开关特性, Vt偏移影响电路时序和功耗",
        },
        "Id_驱动电流": {
            "keywords": ["Idsat", "Idlin", "Ion", "drive", "驱动", "饱和电流"],
            "desc_cn": "驱动电流参数 — 决定晶体管速度, Idsat直接影响电路性能",
        },
        "Ioff_漏电流": {
            "keywords": ["Ioff", "Ileak", "leakage", "off-state", "漏电", "关态电流",
                         "Gate_Leakage", "栅极漏电", "Ig", "gate current"],
            "desc_cn": "漏电流参数 — 影响待机功耗, Ioff过高导致静态功耗增加",
        },
        "SS_亚阈值": {
            "keywords": ["SS", "subthreshold", "swing", "亚阈值", "DIBL", "drain induced",
                         "barrier lowering", "短沟道"],
            "desc_cn": "亚阈值特性参数 — 决定开关转换陡峭度, SS/DIBL反映短沟道效应控制能力",
        },
        "可靠性": {
            "keywords": ["Vbd", "breakdown", "击穿", "HCI", "NBTI", "TDDB", "reliability",
                         "Rs_Contact", "contact resistance", "接触电阻"],
            "desc_cn": "可靠性与接触参数 — 击穿电压/接触电阻反映工艺可靠性和欧姆接触质量",
        },
        "寄生参数": {
            "keywords": ["Cgd", "Cgs", "Cds", "Overlap", "overlap", "寄生电容",
                         "Miller", "miller", "capacitance", "cap"],
            "desc_cn": "寄生电容参数 — 影响开关速度和动态功耗, Cgd的Miller效应对放大器影响显著",
        },
        "良率": {
            "keywords": ["Yield", "yield", "良率", "pass", "fail", "bin"],
            "desc_cn": "良率参数 — 综合反映工艺窗口和缺陷水平",
        },
        "性能_FOM": {
            "keywords": ["Fmax", "fmax", "Ft", "Noise", "noise", "频率", "噪声",
                         "Gm", "transconductance", "跨导", "gain", "增益"],
            "desc_cn": "性能指标参数 — Fmax/Noise等综合反映高频和噪声性能",
        },
    }

    @classmethod
    def classify_param(cls, param_name: str) -> str:
        """根据参数名自动归类到参数组"""
        pn = param_name.lower()
        for cat_name, cat_info in cls.PARAM_CATEGORIES.items():
            for kw in cat_info["keywords"]:
                if kw.lower() in pn:
                    return cat_name
        return "其他参数"

    @classmethod
    def classify_params(cls, param_names: List[str]) -> Dict[str, List[str]]:
        """批量归类参数 → {category: [param1, param2, ...]}"""
        result: Dict[str, List[str]] = {}
        for p in param_names:
            cat = cls.classify_param(p)
            if cat not in result:
                result[cat] = []
            result[cat].append(p)
        return result

    @classmethod
    def get_category_desc(cls, cat_name: str) -> str:
        """获取参数组的描述"""
        return cls.PARAM_CATEGORIES.get(cat_name, {}).get("desc_cn", "未分类参数")

    @classmethod
    def get_api_key(cls):
        return cls.ANTHROPIC_AUTH_TOKEN or cls.ANTHROPIC_API_KEY

    @classmethod
    def get_base_url(cls):
        return cls.ANTHROPIC_BASE_URL or None

    @classmethod
    def is_available(cls):
        key = cls.get_api_key()
        return bool(key and (key.startswith("sk-ant-") or key.startswith("sk-")))

    @classmethod
    def ensure_dirs(cls):
        cls.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        cls.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


PCRBConfig.ensure_dirs()
