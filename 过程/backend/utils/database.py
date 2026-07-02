"""
数据库初始化和工具函数
"""
from config import DATABASE_URI
from backend.extensions import db


def init_db(app):
    """初始化数据库连接"""
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return db


def create_tables(app):
    """创建所有表"""
    with app.app_context():
        db.create_all()


def check_tables_exist():
    """检查数据库表是否已存在"""
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return len(tables) > 0
