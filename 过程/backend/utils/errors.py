"""
自定义异常类和错误处理
"""
from flask import jsonify


class APIError(Exception):
    """API基础异常"""
    def __init__(self, message, status_code=400, error_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class NotFoundError(APIError):
    """资源未找到"""
    def __init__(self, message="资源未找到"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ValidationError(APIError):
    """参数验证错误"""
    def __init__(self, message="参数验证失败"):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")


class AIServiceError(APIError):
    """AI服务异常"""
    def __init__(self, message="AI服务异常"):
        super().__init__(message, status_code=500, error_code="AI_SERVICE_ERROR")


def register_error_handlers(app):
    """注册全局错误处理"""
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": error.error_code,
                "message": error.message
            }
        })
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "NOT_FOUND",
                "message": "请求的资源不存在"
            }
        }), 404

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误"
            }
        }), 500
