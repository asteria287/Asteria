"""
产品良率分析 — 配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


class YieldConfig:
    BASE_DIR = BASE_DIR
    SAMPLES_DIR = BASE_DIR / "samples"
    OUTPUT_DIR = BASE_DIR / "output"
    WORKSPACE_DIR = BASE_DIR / "workspace"

    API_KEY = os.getenv("ANTHROPIC_AUTH_TOKEN", "") or os.getenv("ANTHROPIC_API_KEY", "")
    BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "") or None
    MODEL = os.getenv("AI_MODEL", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))
    MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "8192"))
    TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))

    SIGMA_THRESHOLD = 3.0
    CUSUM_THRESHOLD = 5.0
    MA_WINDOW = 5
    TREND_WINDOW = 10
    MIN_YIELD_DROP = 2.0
    TOP_N_FACTORS = 5

    @classmethod
    def is_available(cls):
        return bool(cls.API_KEY and (cls.API_KEY.startswith("sk-ant-") or cls.API_KEY.startswith("sk-")))

    @classmethod
    def ensure_dirs(cls):
        for d in [cls.WORKSPACE_DIR, cls.OUTPUT_DIR, cls.SAMPLES_DIR]:
            d.mkdir(parents=True, exist_ok=True)


YieldConfig.ensure_dirs()
