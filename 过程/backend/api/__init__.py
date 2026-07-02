"""
API蓝图注册
"""
from backend.api.technology_api import technology_bp
from backend.api.competitive_api import competitive_bp
from backend.api.roadmap_api import roadmap_bp
from backend.api.patent_api import patent_bp
from backend.api.ai_api import ai_bp


def register_blueprints(app):
    """注册所有API蓝图"""
    app.register_blueprint(technology_bp)
    app.register_blueprint(competitive_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(patent_bp)
    app.register_blueprint(ai_bp)
