"""
路线图API路由
"""
from flask import Blueprint, request, jsonify
from backend.services.roadmap_service import RoadmapService

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/api/roadmap")
service = RoadmapService()


def _ok(data, meta=None):
    return jsonify({"success": True, "data": data, "error": None, "meta": meta})


@roadmap_bp.route("/timeline", methods=["GET"])
def get_timeline():
    """获取时间线"""
    filters = {}
    for key in ["tech_id", "company_id", "year_start", "year_end", "status"]:
        if request.args.get(key):
            filters[key] = request.args[key]
    data = service.get_timeline(filters)
    return _ok(data, {"total": len(data)})


@roadmap_bp.route("/technology/<int:tech_id>", methods=["GET"])
def get_by_technology(tech_id):
    """按技术获取路线图"""
    data = service.get_by_technology(tech_id)
    return _ok(data)


@roadmap_bp.route("/gap-analysis", methods=["GET"])
def get_gap_analysis():
    """获取缺口分析"""
    data = service.get_gap_analysis()
    return _ok(data, {"total": len(data)})


@roadmap_bp.route("/stats", methods=["GET"])
def get_stats():
    """获取统计数据"""
    data = service.get_stats()
    return _ok(data)
