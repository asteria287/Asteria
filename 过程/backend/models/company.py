"""
公司模型
"""
from datetime import datetime
from backend.extensions import db


class Company(db.Model):
    """半导体公司"""
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, comment="公司名称")
    name_en = db.Column(db.String(200), comment="英文名称")
    country = db.Column(db.String(50), comment="所属国家/地区")
    company_type = db.Column(
        db.String(30),
        comment="公司类型: IDM/Foundry/Fabless/OSAT/Equipment"
    )
    focus_areas = db.Column(db.JSON, comment="主要领域列表")
    revenue_2024_billion_usd = db.Column(db.Float, comment="2024年营收(十亿美元)")
    rd_spending_percent = db.Column(db.Float, comment="研发投入占比(%)")
    employee_count = db.Column(db.Integer, comment="员工数量")
    founded_year = db.Column(db.Integer, comment="成立年份")
    logo_url = db.Column(db.String(500), comment="Logo URL")
    description = db.Column(db.Text, comment="公司简介")
    website = db.Column(db.String(300), comment="官网")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    portfolios = db.relationship(
        "CompanyTechnologyPortfolio",
        backref="company",
        lazy="dynamic"
    )
    milestones = db.relationship(
        "RoadmapMilestone",
        backref="company",
        lazy="dynamic"
    )
    patents = db.relationship(
        "Patent",
        backref="company",
        lazy="dynamic"
    )

    def to_dict(self, include_stats=False):
        result = {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "country": self.country,
            "company_type": self.company_type,
            "focus_areas": self.focus_areas,
            "revenue_2024_billion_usd": self.revenue_2024_billion_usd,
            "rd_spending_percent": self.rd_spending_percent,
            "employee_count": self.employee_count,
            "founded_year": self.founded_year,
            "description": self.description,
            "website": self.website,
        }
        if include_stats:
            result["portfolio_count"] = self.portfolios.count()
            result["milestone_count"] = self.milestones.count()
            result["patent_count"] = self.patents.count()
        return result


class CompanyTechnologyPortfolio(db.Model):
    """公司技术组合"""
    __tablename__ = "company_technology_portfolios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=False
    )
    technology_id = db.Column(
        db.Integer, db.ForeignKey("technologies.id"), nullable=False
    )
    investment_level = db.Column(
        db.String(20),
        default="Exploring",
        comment="投资水平: Leading/Active/Following/Exploring/None"
    )
    key_products = db.Column(db.JSON, comment="关键产品列表")
    announced_milestones = db.Column(db.JSON, comment="已公布的里程碑")
    competitive_position = db.Column(db.Text, comment="竞争地位描述")
    notes = db.Column(db.Text, comment="备注")

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "technology_id": self.technology_id,
            "investment_level": self.investment_level,
            "key_products": self.key_products,
            "announced_milestones": self.announced_milestones,
            "competitive_position": self.competitive_position,
            "notes": self.notes,
        }
