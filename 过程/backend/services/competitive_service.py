"""
竞争格局服务层
"""
from backend.extensions import db
from backend.models.company import Company, CompanyTechnologyPortfolio
from backend.models.technology import Technology


class CompetitiveService:
    """竞争分析服务"""

    def get_all_companies(self):
        """获取所有公司"""
        companies = Company.query.order_by(Company.revenue_2024_billion_usd.desc()).all()
        return [c.to_dict(include_stats=True) for c in companies]

    def get_company_by_id(self, company_id):
        """获取公司详情(含技术组合)"""
        company = Company.query.get(company_id)
        if not company:
            return None
        result = company.to_dict(include_stats=True)

        # 技术组合
        portfolios = CompanyTechnologyPortfolio.query.filter_by(company_id=company_id).all()
        portfolio_list = []
        for pf in portfolios:
            tech = Technology.query.get(pf.technology_id)
            item = pf.to_dict()
            item["technology_name"] = tech.name if tech else ""
            item["technology_category"] = tech.category if tech else ""
            portfolio_list.append(item)
        result["portfolio"] = portfolio_list
        return result

    def get_comparison_matrix(self, tech_ids=None):
        """获取公司×技术对比矩阵"""
        companies = Company.query.order_by(Company.name).all()
        technologies = Technology.query
        if tech_ids:
            technologies = technologies.filter(Technology.id.in_(tech_ids))
        technologies = technologies.order_by(Technology.category, Technology.name).all()

        portfolios = CompanyTechnologyPortfolio.query.all()
        pf_map = {}
        for pf in portfolios:
            pf_map[(pf.company_id, pf.technology_id)] = pf.investment_level

        rows = []
        for company in companies:
            row = {
                "company_id": company.id,
                "company_name": company.name,
                "country": company.country,
                "investments": {},
            }
            for tech in technologies:
                level = pf_map.get((company.id, tech.id), "None")
                row["investments"][str(tech.id)] = {
                    "technology_name": tech.name,
                    "category": tech.category,
                    "level": level,
                }
            rows.append(row)

        return {
            "companies": [c.to_dict() for c in companies],
            "technologies": [t.to_dict() for t in technologies],
            "matrix": rows,
        }

    def get_heatmap_data(self):
        """获取热力图数据(公司×技术投资水平)"""
        companies = Company.query.order_by(Company.name).all()
        technologies = Technology.query.order_by(Technology.category, Technology.name).all()
        portfolios = CompanyTechnologyPortfolio.query.all()

        level_map = {"None": 0, "Exploring": 1, "Following": 2, "Active": 3, "Leading": 4}
        pf_map = {}
        for pf in portfolios:
            pf_map[(pf.company_id, pf.technology_id)] = level_map.get(pf.investment_level, 0)

        data = []
        for ci, company in enumerate(companies):
            for ti, tech in enumerate(technologies):
                val = pf_map.get((company.id, tech.id), 0)
                if val > 0:
                    data.append([ti, ci, val])

        return {
            "x_labels": [t.name for t in technologies],
            "y_labels": [c.name for c in companies],
            "data": data,
        }

    def get_market_share(self):
        """获取市场份额数据"""
        segments = [
            {
                "name": "DRAM (2024 Q4)",
                "children": [
                    {"name": "Samsung", "value": 41.2},
                    {"name": "SK Hynix", "value": 34.5},
                    {"name": "Micron", "value": 21.8},
                    {"name": "Others", "value": 2.5},
                ],
            },
            {
                "name": "NAND Flash (2024 Q4)",
                "children": [
                    {"name": "Samsung", "value": 34.0},
                    {"name": "Kioxia+WD", "value": 28.5},
                    {"name": "SK Hynix", "value": 22.3},
                    {"name": "Micron", "value": 10.2},
                    {"name": "YMTC", "value": 5.0},
                ],
            },
            {
                "name": "Foundry (2024 Q4)",
                "children": [
                    {"name": "TSMC", "value": 62.3},
                    {"name": "Samsung", "value": 12.8},
                    {"name": "Intel", "value": 7.5},
                    {"name": "UMC", "value": 5.2},
                    {"name": "SMIC", "value": 5.8},
                    {"name": "Others", "value": 6.4},
                ],
            },
            {
                "name": "HBM (2024)",
                "children": [
                    {"name": "SK Hynix", "value": 53.0},
                    {"name": "Samsung", "value": 35.0},
                    {"name": "Micron", "value": 12.0},
                ],
            },
        ]
        return {"segments": segments}
