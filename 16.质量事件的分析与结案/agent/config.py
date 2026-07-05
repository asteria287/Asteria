"""
QRA 质量事件分析 — 配置
"""
import os, re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


class QRAConfig:
    BASE_DIR = BASE_DIR
    KB_DIR = BASE_DIR / "knowledge_base"
    WORKSPACE_DIR = BASE_DIR / "workspace"

    API_KEY = os.getenv("ANTHROPIC_AUTH_TOKEN", "") or os.getenv("ANTHROPIC_API_KEY", "")
    BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "") or None
    MODEL = os.getenv("AI_MODEL", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))
    MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "4096"))
    TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))

    # 3 workshop cases
    CASES = {
        "case1": "CP测试良率突降 — Probe Card针尖异常",
        "case2": "FT Handler卡料导致批次良率波动",
        "case3": "新产品SLT Burn-in失效 — 固件时序问题",
    }

    # 案例相似度关键词权重
    SIMILARITY_KW = {
        "cp": ["CP测试", "Probe Card", "探针卡", "晶圆", "针尖", "接触电阻", "wafer"],
        "ft": ["FT测试", "Handler", "Socket", "分选机", "重测率", "Jam", "机械"],
        "slt": ["SLT", "Burn-in", "老化", "FW", "固件", "时序", "DDR", "DPPM"],
        "general": ["良率", "yield", "失效", "fail", "批次", "lot", "SPC", "偏移"],
    }

    @classmethod
    def is_available(cls):
        return bool(cls.API_KEY and (cls.API_KEY.startswith("sk-ant-") or cls.API_KEY.startswith("sk-")))

    @classmethod
    def ensure_dirs(cls):
        for d in [cls.WORKSPACE_DIR, cls.KB_DIR]:
            d.mkdir(parents=True, exist_ok=True)


QRAConfig.ensure_dirs()
