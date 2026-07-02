"""
Server-Sent Events 辅助函数
"""
import json
from flask import Response, stream_with_context


def sse_event(event: str, data: dict | str) -> str:
    """
    格式化SSE事件

    Args:
        event: 事件类型 (delta, done, error)
        data: 事件数据

    Returns:
        SSE格式字符串
    """
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {data}\n\n"


def sse_stream(generator):
    """
    将生成器包装为SSE流式响应

    用法:
        @app.route('/api/ai/qa', methods=['POST'])
        def qa():
            def generate():
                for chunk in ai_service.qa_stream(...):
                    yield sse_event('delta', {'content': chunk})
                yield sse_event('done', {'status': 'completed'})
            return sse_stream(generate())
    """
    return Response(
        stream_with_context(generator()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
