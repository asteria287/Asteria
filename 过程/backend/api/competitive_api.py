"""
竞争格局API路由
"""
from flask import Blueprint, request, jsonify
from backend.services.competitive_service import CompetitiveService

competitive_bp = Blueprint("competitive", __name__, url_prefix="/api/competitive")
service = CompetitiveService()


def _ok(data, meta=None):
    return jsonify({"success": True, "data": data, "error": None, "meta": meta})


@competitive_bp.route("/companies", methods=["GET"])
def list_companies():
    """获取公司列表"""
    data = service.get_all_companies()
    return _ok(data, {"total": len(data)})


@competitive_bp.route("/companies/<int:company_id>", methods=["GET"])
def get_company(company_id):
    """获取公司详情"""
    data = service.get_company_by_id(company_id)
    if not data:
        return _ok(None), 404
    return _ok(data)


@competitive_bp.route("/comparison", methods=["GET"])
def get_comparison():
    """获取公司对比矩阵"""
    tech_ids = request.args.getlist("tech_ids", type=int)
    data = service.get_comparison_matrix(tech_ids if tech_ids else None)
    return _ok(data)


@competitive_bp.route("/market-share", methods=["GET"])
def get_market_share():
    """获取市场份额数据"""
    data = service.get_market_share()
    return _ok(data)


@competitive_bp.route("/heatmap", methods=["GET"])
def get_heatmap():
    """获取热力图数据"""
    data = service.get_heatmap_data()
    return _ok(data)
