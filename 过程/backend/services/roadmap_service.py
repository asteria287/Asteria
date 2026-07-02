"""
路线图服务层
"""
from backend.extensions import db
from backend.models.roadmap import RoadmapMilestone
from backend.models.technology import Technology
from backend.models.company import Company


class RoadmapService:
    """路线图服务"""

    def get_timeline(self, filters=None):
        """获取时间线，支持筛选"""
        query = RoadmapMilestone.query

        if filters:
            if filters.get("tech_id"):
                query = query.filter(RoadmapMilestone.technology_id == int(filters["tech_id"]))
            if filters.get("company_id"):
                query = query.filter(RoadmapMilestone.company_id == int(filters["company_id"]))
            if filters.get("year_start"):
                query = query.filter(RoadmapMilestone.year >= int(filters["year_start"]))
            if filters.get("year_end"):
                query = query.filter(RoadmapMilestone.year <= int(filters["year_end"]))
            if filters.get("status"):
                query = query.filter(RoadmapMilestone.status == filters["status"])

        milestones = query.order_by(RoadmapMilestone.year, RoadmapMilestone.quarter).all()
        result = []
        for m in milestones:
            item = m.to_dict()
            if m.technology_id:
                tech = Technology.query.get(m.technology_id)
                item["technology_name"] = tech.name if tech else ""
            if m.company_id:
                company = Company.query.get(m.company_id)
                item["company_name"] = company.name if company else ""
            result.append(item)
        return result

    def get_by_technology(self, tech_id):
        """按技术分组获取路线图"""
        milestones = RoadmapMilestone.query.filter_by(technology_id=tech_id)\
            .order_by(RoadmapMilestone.year, RoadmapMilestone.quarter).all()
        companies = {}
        for m in milestones:
            company_name = "行业整体"
            if m.company_id:
                company = Company.query.get(m.company_id)
                company_name = company.name if company else f"Company {m.company_id}"
            if company_name not in companies:
                companies[company_name] = []
            item = m.to_dict()
            item["company_name"] = company_name
            companies[company_name].append(item)

        tech = Technology.query.get(tech_id)
        return {
            "technology": tech.to_dict() if tech else None,
            "companies": companies,
        }

    def get_stats(self):
        """获取路线图统计数据"""
        milestones = RoadmapMilestone.query.all()
        status_counts = {}
        year_distribution = {}
        for m in milestones:
            status_counts[m.status] = status_counts.get(m.status, 0) + 1
            year_distribution[str(m.year)] = year_distribution.get(str(m.year), 0) + 1

        return {
            "total": len(milestones),
            "status_counts": status_counts,
            "year_distribution": year_distribution,
            "ai_generated_count": sum(1 for m in milestones if m.is_ai_generated),
        }

    def get_gap_analysis(self):
        """缺口分析 - 找出没有足够里程碑的技术"""
        techs = Technology.query.all()
        gaps = []
        for tech in techs:
            count = RoadmapMilestone.query.filter_by(technology_id=tech.id).count()
            if count < 3:
                gaps.append({
                    "technology_id": tech.id,
                    "technology_name": tech.name,
                    "category": tech.category,
                    "milestone_count": count,
                    "maturity_level": tech.maturity_level,
                })
        return gaps
