"""
Flask应用工厂
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import AppConfig, BASE_DIR
from backend.extensions import db
from backend.utils.database import init_db, create_tables, check_tables_exist
from backend.utils.errors import register_error_handlers


def create_app(config=None):
    """创建并配置Flask应用"""
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "frontend"),
        static_url_path="/static",
        template_folder=str(BASE_DIR / "frontend"),
    )

    # 加载配置
    app.config.from_object(AppConfig)
    if config:
        app.config.update(config)

    # 启用CORS
    CORS(app)

    # 初始化数据库
    init_db(app)

    # 注册错误处理
    register_error_handlers(app)

    # 注册API蓝图
    from backend.api import register_blueprints
    register_blueprints(app)

    # SPA路由 - 服务前端页面
    @app.route("/")
    def serve_index():
        """服务SPA主页"""
        return send_from_directory(
            str(BASE_DIR / "frontend"), "index.html"
        )

    @app.route("/<path:path>")
    def serve_static(path):
        """服务静态文件"""
        # 对于SPA路由（非静态文件请求），返回index.html
        static_dir = BASE_DIR / "frontend"
        target = static_dir / path
        if target.exists() and target.is_file():
            return send_from_directory(str(static_dir), path)
        # SPA fallback
        return send_from_directory(str(static_dir), "index.html")

    # 健康检查
    @app.route("/api/health")
    def health_check():
        return {"status": "ok", "service": "Tech Roadmap Analyzer"}

    return app


def init_database(app):
    """初始化数据库 - 创建表"""
    with app.app_context():
        create_tables(app)
        return check_tables_exist()
