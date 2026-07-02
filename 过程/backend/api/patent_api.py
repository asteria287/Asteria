"""
专利与论文API路由
"""
from flask import Blueprint, request, jsonify
from backend.services.patent_service import PatentService

patent_bp = Blueprint("patent", __name__, url_prefix="/api/patents")
service = PatentService()


def _ok(data, meta=None):
    return jsonify({"success": True, "data": data, "error": None, "meta": meta})


@patent_bp.route("/trends", methods=["GET"])
def get_trends():
    """获取专利趋势"""
    group_by = request.args.get("group_by", "technology")
    data = service.get_filing_trends(group_by)
    return _ok(data)


@patent_bp.route("/top-assignees", methods=["GET"])
def get_top_assignees():
    """获取Top专利权人"""
    limit = request.args.get("limit", 15, type=int)
    data = service.get_top_assignees(limit)
    return _ok(data)


@patent_bp.route("/geographic", methods=["GET"])
def get_geographic():
    """获取地理分布"""
    data = service.get_geographic_distribution()
    return _ok(data)


@patent_bp.route("/search", methods=["GET"])
def search_patents():
    """搜索专利"""
    query = request.args.get("q", "")
    tech_id = request.args.get("tech_id", type=int)
    data = service.search_patents(query, tech_id)
    return _ok(data, {"total": len(data)})


# 论文相关路由(复用PatentService)
patent_paper_bp = Blueprint("papers", __name__, url_prefix="/api/papers")


@patent_paper_bp.route("/trends", methods=["GET"])
def get_paper_trends():
    """获取论文趋势"""
    group_by = request.args.get("group_by", "technology")
    data = service.get_paper_trends(group_by)
    return _ok(data)


# 注意: papers blueprint需要在__init__.py中注册
# 这里暂时将论文路由合并到patent_bp
@patent_bp.route("/../papers/trends", methods=["GET"])
def papers_trends_redirect():
    group_by = request.args.get("group_by", "technology")
    data = service.get_paper_trends(group_by)
    return _ok(data)
