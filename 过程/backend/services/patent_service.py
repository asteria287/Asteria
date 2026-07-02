"""
专利和论文服务层
"""
from backend.extensions import db
from backend.models.patent import Patent, ResearchPaper
from backend.models.technology import Technology
from backend.models.company import Company
from sqlalchemy import func


class PatentService:
    """专利分析服务"""

    def get_filing_trends(self, group_by="technology"):
        """获取专利申请趋势"""
        patents = Patent.query.all()
        if not patents:
            return {"years": [], "series": []}

        # 按年份和技术分组
        year_tech_counts = {}
        all_years = set()
        all_techs = set()

        for p in patents:
            if p.filing_date:
                year = p.filing_date.year
                all_years.add(year)
                tech = Technology.query.get(p.technology_id) if p.technology_id else None
                tech_name = tech.name if tech else "其他"
                all_techs.add(tech_name)
                key = (year, tech_name)
                year_tech_counts[key] = year_tech_counts.get(key, 0) + 1

        years = sorted(all_years)
        tech_names = sorted(all_techs)

        series = []
        for tech_name in tech_names:
            data = [year_tech_counts.get((y, tech_name), 0) for y in years]
            series.append({"name": tech_name, "data": data})

        return {"years": [str(y) for y in years], "series": series}

    def get_top_assignees(self, limit=15):
        """获取Top专利权人"""
        results = db.session.query(
            Patent.assignee,
            func.count(Patent.id).label("count")
        ).group_by(Patent.assignee).order_by(func.count(Patent.id).desc()).limit(limit).all()

        return [{"assignee": r[0] or "Unknown", "count": r[1]} for r in results]

    def get_geographic_distribution(self):
        """获取地理分布"""
        results = db.session.query(
            Patent.jurisdiction,
            func.count(Patent.id).label("count")
        ).group_by(Patent.jurisdiction).order_by(func.count(Patent.id).desc()).all()

        return [{"jurisdiction": r[0] or "Unknown", "count": r[1]} for r in results]

    def search_patents(self, query=None, tech_id=None):
        """搜索专利"""
        q = Patent.query
        if query:
            search = f"%{query}%"
            q = q.filter(
                db.or_(
                    Patent.title.like(search),
                    Patent.abstract.like(search),
                )
            )
        if tech_id:
            q = q.filter(Patent.technology_id == int(tech_id))

        patents = q.order_by(Patent.citation_count.desc()).limit(50).all()
        return [p.to_dict() for p in patents]

    def get_paper_trends(self, group_by="technology"):
        """获取论文发表趋势"""
        papers = ResearchPaper.query.all()
        if not papers:
            return {"years": [], "series": []}

        year_tech_counts = {}
        all_years = set()
        all_techs = set()

        for p in papers:
            if p.publication_date:
                year = p.publication_date.year
                all_years.add(year)
                tech = Technology.query.get(p.technology_id) if p.technology_id else None
                tech_name = tech.name if tech else "其他"
                all_techs.add(tech_name)
                key = (year, tech_name)
                year_tech_counts[key] = year_tech_counts.get(key, 0) + 1

        years = sorted(all_years)
        tech_names = sorted(all_techs)

        series = []
        for tech_name in tech_names:
            data = [year_tech_counts.get((y, tech_name), 0) for y in years]
            series.append({"name": tech_name, "data": data})

        return {"years": [str(y) for y in years], "series": series}
