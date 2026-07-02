"""
技术模型
"""
from datetime import datetime
from backend.extensions import db


class Technology(db.Model):
    """半导体技术"""
    __tablename__ = "technologies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, comment="技术名称")
    name_en = db.Column(db.String(200), comment="英文名称")
    category = db.Column(db.String(50), nullable=False, comment="技术类别")
    subcategory = db.Column(db.String(100), comment="技术子类别")
    maturity_level = db.Column(db.Integer, default=1, comment="技术成熟度 1-9")
    description = db.Column(db.Text, comment="技术描述")
    key_parameters = db.Column(db.JSON, comment="关键参数")
    advantages = db.Column(db.Text, comment="技术优势")
    challenges = db.Column(db.Text, comment="技术挑战")
    first_announced = db.Column(db.String(10), comment="首次发布年份")
    expected_mass_production = db.Column(db.String(10), comment="预计量产年份")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    relations_from = db.relationship(
        "TechnologyRelation",
        foreign_keys="TechnologyRelation.source_tech_id",
        backref="source_tech",
        lazy="dynamic"
    )
    relations_to = db.relationship(
        "TechnologyRelation",
        foreign_keys="TechnologyRelation.target_tech_id",
        backref="target_tech",
        lazy="dynamic"
    )
    portfolios = db.relationship(
        "CompanyTechnologyPortfolio",
        backref="technology",
        lazy="dynamic"
    )
    milestones = db.relationship(
        "RoadmapMilestone",
        backref="technology",
        lazy="dynamic"
    )
    patents = db.relationship(
        "Patent",
        backref="technology",
        lazy="dynamic"
    )
    papers = db.relationship(
        "ResearchPaper",
        backref="technology",
        lazy="dynamic"
    )

    def to_dict(self, include_relations=False):
        """转换为字典"""
        result = {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "category": self.category,
            "subcategory": self.subcategory,
            "maturity_level": self.maturity_level,
            "description": self.description,
            "key_parameters": self.key_parameters,
            "advantages": self.advantages,
            "challenges": self.challenges,
            "first_announced": self.first_announced,
            "expected_mass_production": self.expected_mass_production,
        }
        if include_relations:
            result["related_count"] = (
                self.relations_from.count() + self.relations_to.count()
            )
        return result


class TechnologyRelation(db.Model):
    """技术关联关系"""
    __tablename__ = "technology_relations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_tech_id = db.Column(
        db.Integer, db.ForeignKey("technologies.id"), nullable=False
    )
    target_tech_id = db.Column(
        db.Integer, db.ForeignKey("technologies.id"), nullable=False
    )
    relation_type = db.Column(
        db.String(30),
        nullable=False,
        comment="关系类型: enables/depends_on/competes_with/related_to"
    )
    description = db.Column(db.Text, comment="关系描述")
    strength = db.Column(db.Integer, default=1, comment="关系强度 1-5")

    def to_dict(self):
        return {
            "id": self.id,
            "source_tech_id": self.source_tech_id,
            "target_tech_id": self.target_tech_id,
            "relation_type": self.relation_type,
            "description": self.description,
            "strength": self.strength,
        }
