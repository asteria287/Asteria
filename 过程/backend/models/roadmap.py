"""
路线图模型
"""
from datetime import datetime
from backend.extensions import db


class RoadmapMilestone(db.Model):
    """技术路线图里程碑"""
    __tablename__ = "roadmap_milestones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=True
    )
    technology_id = db.Column(
        db.Integer, db.ForeignKey("technologies.id"), nullable=False
    )
    year = db.Column(db.Integer, nullable=False, comment="年份")
    quarter = db.Column(db.String(5), comment="季度 Q1-Q4")
    milestone = db.Column(db.String(200), nullable=False, comment="里程碑名称")
    description = db.Column(db.Text, comment="详细描述")
    status = db.Column(
        db.String(30),
        default="Planned",
        comment="状态: Achieved/In Progress/Planned/Speculative"
    )
    source_url = db.Column(db.String(500), comment="信息来源URL")
    is_ai_generated = db.Column(db.Boolean, default=False, comment="是否AI生成")
    confidence = db.Column(db.Float, comment="AI预测置信度 0-1")
    impact_level = db.Column(
        db.String(20),
        default="Medium",
        comment="影响程度: Critical/High/Medium/Low"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "technology_id": self.technology_id,
            "year": self.year,
            "quarter": self.quarter,
            "milestone": self.milestone,
            "description": self.description,
            "status": self.status,
            "source_url": self.source_url,
            "is_ai_generated": self.is_ai_generated,
            "confidence": self.confidence,
            "impact_level": self.impact_level,
        }
