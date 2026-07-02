"""
AI分析API路由
"""
import json
from flask import Blueprint, request, jsonify, Response
from backend.services.ai_service import get_analyzer
from backend.utils.sse import sse_event

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


def _ok(data, meta=None):
    return jsonify({"success": True, "data": data, "error": None, "meta": meta})


@ai_bp.route("/analyze", methods=["POST"])
def analyze_technology():
    """深度技术分析"""
    data = request.get_json() or {}
    tech_name = data.get("technology_name", "")
    aspects = data.get("aspects", ["技术现状", "关键挑战", "竞争格局", "发展趋势"])

    if not tech_name:
        return _ok({"error": "请提供 technology_name"}), 400

    analyzer = get_analyzer()
    result = analyzer.analyze_technology(tech_name, aspects)
    return _ok(result)


@ai_bp.route("/qa", methods=["POST"])
def qa():
    """流式Q&A"""
    data = request.get_json() or {}
    question = data.get("question", "")
    session_id = data.get("session_id", "default")
    context_tech_ids = data.get("context_tech_ids", [])

    if not question:
        return _ok({"error": "请提供 question"}), 400

    analyzer = get_analyzer()

    if not analyzer.is_available:
        # 降级模式 - 返回提示信息
        return _ok({
            "response": "AI分析服务未配置。请在项目根目录的.env文件中设置 ANTHROPIC_API_KEY=sk-ant-... 来启用AI分析功能。\n\n当前系统支持的技术分析能力:\n- 技术路线图查询\n- 竞争格局分析\n- 专利趋势分析\n- 技术参数对比\n\n请配置API Key后重试。",
            "mode": "offline"
        })

    def generate():
        try:
            for chunk in analyzer.qa_stream(question, session_id, context_tech_ids):
                yield sse_event("delta", {"content": chunk})
            yield sse_event("done", {"status": "completed", "session_id": session_id})
        except Exception as e:
            yield sse_event("error", {"message": str(e)})

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@ai_bp.route("/qa-simple", methods=["POST"])
def qa_simple():
    """非流式Q&A(降级模式)"""
    data = request.get_json() or {}
    question = data.get("question", "")
    session_id = data.get("session_id", "default")
    context_tech_ids = data.get("context_tech_ids", [])

    if not question:
        return _ok({"error": "请提供 question"}), 400

    analyzer = get_analyzer()
    result_text = ""
    for chunk in analyzer.qa_stream(question, session_id, context_tech_ids):
        result_text += chunk

    return _ok({"response": result_text, "session_id": session_id})


@ai_bp.route("/roadmap-predict", methods=["POST"])
def roadmap_predict():
    """路线图预测"""
    data = request.get_json() or {}
    tech_id = data.get("technology_id")
    horizon_years = data.get("horizon_years", 10)

    if not tech_id:
        return _ok({"error": "请提供 technology_id"}), 400

    analyzer = get_analyzer()
    result = analyzer.predict_roadmap(int(tech_id), int(horizon_years))
    return _ok(result)


@ai_bp.route("/competitive-summary", methods=["POST"])
def competitive_summary():
    """竞争格局总结"""
    data = request.get_json() or {}
    tech_id = data.get("technology_id")

    if not tech_id:
        return _ok({"error": "请提供 technology_id"}), 400

    analyzer = get_analyzer()
    result = analyzer.competitive_summary(int(tech_id))
    return _ok(result)


@ai_bp.route("/chat-history/<session_id>", methods=["GET"])
def chat_history(session_id):
    """获取聊天历史"""
    analyzer = get_analyzer()
    data = analyzer.get_chat_history(session_id)
    return _ok(data, {"total": len(data)})
