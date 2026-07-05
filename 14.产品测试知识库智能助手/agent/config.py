"""
产品测试知识库 — 配置
"""
import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class TestKBConfig:
    # Paths
    BASE_DIR = BASE_DIR
    KB_DIR = BASE_DIR / "knowledge_base"
    WORKSPACE_DIR = BASE_DIR / "workspace"

    KB_FILES = [
        "cp_fundamentals.md",
        "ft_fundamentals.md",
        "slt_fundamentals.md",
        "test_terminology.md",
        "test_trends_2025.md",
        "test_compare_cp_ft_slt.md",
        "test_equipment_guide.md",
    ]

    # API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
    ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "")
    MODEL = os.getenv("AI_MODEL", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))
    MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "8192"))
    TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
    TOP_K = int(os.getenv("TOP_K_RESULTS", "8"))

    # Domain keywords
    TEST_PHASES = {
        "CP": ["晶圆测试", "chip probe", "wafer sort", "wafer test", "探针", "probe",
                "prober", "探针卡", "probe card", "CP测试", "CP", "EDS", "KGD", "PCM", "WAT"],
        "FT": ["封装测试", "final test", "package test", "成品测试", "FT测试", "FT",
                "handler", "分选机", "socket", "测试座", "load board", "STDF",
                "speed binning", "BIST", "DUT", "UPH"],
        "SLT": ["系统级测试", "system level test", "SLT测试", "SLT", "burn-in", "老化",
                "DPPM", "PVT", "corner lot", "SI/PI", "firmware", "FW", "HTOL"],
    }

    TERM_CATEGORIES = {
        "测试类型": ["DC测试", "AC测试", "O/S测试", "开短路", "functional test",
                    "功能测试", "parametric test", "BIST", "IDD测试"],
        "测试设备": ["ATE", "Prober", "Handler", "探针台", "分选机", "V93000",
                    "UltraFLEX", "J750", "TEL", "Advantest", "Teradyne", "Cohu"],
        "测试参数": ["IDD", "Ioff", "VOH", "VOL", "tSETUP", "tHOLD", "Fmax",
                    "yield", "contact resistance", "UPH", "DPPM"],
        "数据格式": ["STDF", "wafer map", "bin", "BIN"],
    }

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
    def detect_phase(cls, query: str) -> List[str]:
        """检测问题涉及的测试阶段"""
        phases = []
        ql = query.lower()
        for phase, keywords in cls.TEST_PHASES.items():
            if any(kw.lower() in ql for kw in keywords):
                phases.append(phase)
        return phases or ["CP", "FT", "SLT"]

    @classmethod
    def ensure_dirs(cls):
        cls.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        cls.KB_DIR.mkdir(parents=True, exist_ok=True)


TestKBConfig.ensure_dirs()
