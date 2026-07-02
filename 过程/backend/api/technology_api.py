"""
技术API路由
"""
from flask import Blueprint, request, jsonify
from backend.services.technology_service import TechnologyService

technology_bp = Blueprint("technology", __name__, url_prefix="/api/technologies")
service = TechnologyService()


def _ok(data, meta=None):
    return jsonify({"success": True, "data": data, "error": None, "meta": meta})


@technology_bp.route("/", methods=["GET"])
def list_technologies():
    """获取技术列表"""
    filters = {}
    if request.args.get("category"):
        filters["category"] = request.args["category"]
    if request.args.get("maturity_min"):
        filters["maturity_min"] = request.args["maturity_min"]
    if request.args.get("search"):
        filters["search"] = request.args["search"]
    data = service.get_all(filters)
    return _ok(data, {"total": len(data)})


@technology_bp.route("/<int:tech_id>", methods=["GET"])
def get_technology(tech_id):
    """获取技术详情"""
    data = service.get_by_id(tech_id)
    if not data:
        return _ok(None), 404
    return _ok(data)


@technology_bp.route("/<int:tech_id>/landscape", methods=["GET"])
def get_landscape(tech_id):
    """获取技术全景图"""
    data = service.get_landscape(center_tech_id=tech_id)
    return _ok(data)


@technology_bp.route("/overview", methods=["GET"])
def get_overview():
    """获取概览统计"""
    data = service.get_overview()
    return _ok(data)


@technology_bp.route("/radar", methods=["GET"])
def get_radar():
    """获取雷达图数据"""
    data = service.get_radar_data()
    return _ok(data)
