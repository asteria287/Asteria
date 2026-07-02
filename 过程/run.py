"""
研发技术路线图智能分析助手 - 启动入口
一键启动: python run.py
"""
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import ServerConfig
from backend import create_app, init_database
from backend.services.seed_service import seed_if_empty


def main():
    """主启动函数"""
    print("=" * 60)
    print("  研发技术路线图智能分析助手")
    print("  Semiconductor Technology Roadmap Analyzer")
    print("=" * 60)
    print()

    # 创建应用
    print("[1/3] 初始化应用...")
    app = create_app()

    # 初始化数据库
    print("[2/3] 初始化数据库...")
    tables_exist = init_database(app)
    if tables_exist:
        print("  数据库已就绪")
    else:
        print("  数据库表已创建")

    # 检查并填充种子数据
    print("[3/3] 检查种子数据...")
    try:
        seeded = seed_if_empty(app)
        if seeded:
            print("  种子数据已导入")
        else:
            print("  数据已存在，跳过种子导入")
    except Exception as e:
        print(f"  种子数据导入提示: {e}")
        print("  应用将以空数据库启动")

    print()
    print(f"  启动服务器: http://{ServerConfig.HOST}:{ServerConfig.PORT}")
    print(f"  按 Ctrl+C 停止服务")
    print("=" * 60)

    # 启动服务器
    from waitress import serve
    serve(
        app,
        host=ServerConfig.HOST,
        port=ServerConfig.PORT,
        threads=4,
    )


if __name__ == "__main__":
    main()
