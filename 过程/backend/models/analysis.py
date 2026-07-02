"""
AI分析缓存和聊天历史模型
"""
from datetime import datetime
from backend.extensions import db


class AnalysisCache(db.Model):
    """AI分析结果缓存"""
    __tablename__ = "analysis_cache"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query_hash = db.Column(db.String(64), index=True, nullable=False, comment="查询SHA-256哈希")
    prompt_type = db.Column(
        db.String(50),
        nullable=False,
        comment="提示类型: analysis/qa/roadmap_prediction/competitive_summary"
    )
    query_text = db.Column(db.Text, comment="原始查询文本")
    response = db.Column(db.Text, comment="AI响应内容")
    model = db.Column(db.String(100), comment="使用的模型")
    tokens_input = db.Column(db.Integer, comment="输入Token数")
    tokens_output = db.Column(db.Integer, comment="输出Token数")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, comment="过期时间")


class ChatHistory(db.Model):
    """聊天历史"""
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(50), index=True, nullable=False, comment="会话ID")
    role = db.Column(
        db.String(20),
        nullable=False,
        comment="角色: user/assistant/system"
    )
    content = db.Column(db.Text, nullable=False, comment="消息内容")
    technology_ids = db.Column(db.JSON, comment="关联技术ID列表")
    tokens_used = db.Column(db.Integer, comment="消耗Token数")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "technology_ids": self.technology_ids,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
