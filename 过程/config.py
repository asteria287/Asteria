"""
集中配置文件
加载环境变量，定义所有可调参数
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
SEED_DIR = DATA_DIR / "seed"
CACHE_DIR = DATA_DIR / "cache"

# 数据库
DATABASE_PATH = DATA_DIR / "tech_roadmap.db"
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

# 确保数据目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class AppConfig:
    """Flask应用配置"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JSON_AS_ASCII = False  # 支持中文JSON输出
    JSONIFY_PRETTYPRINT_REGULAR = True


class AIConfig:
    """AI服务配置"""
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-20250514")
    MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "4096"))
    TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
    CACHE_TTL_ANALYSIS = int(os.getenv("CACHE_TTL_ANALYSIS", "604800"))  # 7天
    CACHE_TTL_QA = int(os.getenv("CACHE_TTL_QA", "3600"))  # 1小时


class SeedConfig:
    """种子数据配置"""
    AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() == "true"
    # 种子数据文件列表
    TECH_FILE = SEED_DIR / "technologies.json"
    COMPANIES_FILE = SEED_DIR / "companies.json"
    ROADMAP_FILE = SEED_DIR / "roadmap_entries.json"
    PATENT_FILE = SEED_DIR / "patent_samples.json"
    PAPER_FILE = SEED_DIR / "paper_samples.json"
    RELATIONS_FILE = SEED_DIR / "tech_relations.json"


class ServerConfig:
    """服务器配置"""
    HOST = os.getenv("SERVER_HOST", "127.0.0.1")
    PORT = int(os.getenv("SERVER_PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
