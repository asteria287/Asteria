"""
SOP 智能问答 — 配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class SOPQConfig:
    # Paths
    BASE_DIR = BASE_DIR
    KB_DIR = BASE_DIR / "knowledge_base"
    WORKSPACE_DIR = BASE_DIR / "workspace"
    SAMPLES_DIR = BASE_DIR / "samples"

    # KB files (auto-discover, or use explicit list)
    KB_FILES = []  # populated at runtime via discover_kb()

    # API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
    ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "")
    MODEL = os.getenv("AI_MODEL", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))
    MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "8192"))
    TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
    TOP_K = int(os.getenv("TOP_K_RESULTS", "8"))

    # SOP domain keywords for index building
    SOP_KEYWORDS = {
        "safety": [
            "安全", "PPE", "EMO", "ventilation", "通风", "有害气体", "danger",
            "警告", "警示", "lockout", "tagout", "LOTO", "上锁", "挂牌",
            "防酸手套", "护目镜", "防静电", "安全帽", "禁止操作",
        ],
        "tools": [
            "工具", "torque wrench", "扭矩扳手", "氦检漏仪", "helium leak detector",
            "真空吸尘器", "vacuum cleaner", "Scotch-Brite", "无尘布", "IPA",
            "DI Water", "N2", "塞尺", "feeler gauge", "热像仪", "thermal camera",
            "网络分析仪", "network analyzer", "O-ring pick",
        ],
        "procedure": [
            "步骤", "拆卸", "安装", "清洁", "更换", "检查", "测量", "测试",
            "验证", "确认", "记录", "签核", "关闭", "启动", "恢复",
            "disassemble", "assemble", "clean", "replace", "inspect", "measure",
            "test", "verify", "confirm", "record", "sign off",
        ],
        "standards": [
            "标准", "阈值", "目标", "范围", "规格", "specification",
            "<", ">", "±", "ppm", "Torr", "mTorr", "°C", "MΩ", "mm",
            "mbar", "L/s", "VSWR", "RF hours", "base vacuum",
        ],
        "equipment": [
            "腔体", "chamber", "上电极", "shower head", "ESC", "静电卡盘",
            "Focus Ring", "Edge Ring", "O-ring", "Gate Valve", "TMP",
            "涡轮分子泵", "Dry Pump", "干泵", "RF", "匹配网络", "Matching",
            "MFC", "气体管路", "gas line",
        ],
        "quality": [
            "漏率", "leak rate", "颗粒", "particle", "均匀性", "uniformity",
            "Etch Rate", "CD", "NU%", "洁净度", "cleanliness",
        ],
    }

    # Concept synonyms for semantic matching
    CONCEPT_SYNONYMS = {
        "清洁": ["清洁", "clean", "清洗", "擦拭", "清除", "wipe", "scrub"],
        "安全": ["安全", "safety", "PPE", "危险", "警告", "EMO", "lockout", "LOTO"],
        "更换": ["更换", "replace", "swap", "install", "安装", "拆卸", "remove"],
        "检查": ["检查", "inspect", "check", "examine", "验证", "verify", "确认"],
        "泄漏": ["泄漏", "leak", "漏率", "氦检", "helium", "密封", "seal"],
        "真空": ["真空", "vacuum", "TMP", "泵", "pump", "base vacuum", "抽真空"],
        "温度": ["温度", "temperature", "°C", "热像", "thermal", "冷却", "cooling"],
        "RF": ["RF", "射频", "VSWR", "匹配", "Matching", "功率", "power"],
        "ESC": ["ESC", "静电卡盘", "chuck", "He背冷", "helium backside"],
        "电极": ["电极", "electrode", "Shower Head", "上电极", "showerhead"],
        "O-ring": ["O-ring", "O型圈", "密封圈", "seal ring", "真空脂", "Krytox"],
        "验证": ["验证", "verify", "monitor", "测试", "test", "qualify", "seasoning"],
        "腔体": ["腔体", "chamber", "腔壁", "内壁", "chamber wall", "Y2O3"],
        "气体": ["气体", "gas", "CF4", "CHF3", "O2", "Ar", "MFC", "管路", "气瓶"],
    }

    @classmethod
    def discover_kb(cls):
        """Auto-discover SOP documents in knowledge_base/"""
        if not cls.KB_DIR.exists():
            return []
        supported = {'.md', '.txt'}
        files = sorted([
            f.name for f in cls.KB_DIR.iterdir()
            if f.suffix.lower() in supported and not f.name.startswith('.')
        ])
        cls.KB_FILES = files
        return files

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
        cls.KB_DIR.mkdir(parents=True, exist_ok=True)
        cls.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


# Ensure dirs on import
SOPQConfig.ensure_dirs()
