"""
种子数据服务 - 首次运行时自动填充数据库
"""
import json
from datetime import datetime, date
from config import SeedConfig
from backend.extensions import db
from backend.models.technology import Technology, TechnologyRelation
from backend.models.company import Company, CompanyTechnologyPortfolio
from backend.models.roadmap import RoadmapMilestone
from backend.models.patent import Patent, ResearchPaper


def seed_if_empty(app) -> bool:
    """检查并填充种子数据，仅在Technology表为空时执行"""
    if not SeedConfig.AUTO_SEED:
        return False

    with app.app_context():
        if Technology.query.count() > 0:
            return False

        print("  检测到空数据库，开始导入种子数据...")
        _seed_technologies()
        _seed_companies()
        _seed_relations()
        _seed_roadmap()
        _seed_patents()
        _seed_papers()
        _seed_portfolios()
        db.session.commit()
        print("  种子数据导入完成")
        return True


def _seed_technologies():
    """导入技术数据"""
    if not SeedConfig.TECH_FILE.exists():
        return
    with open(SeedConfig.TECH_FILE, "r", encoding="utf-8") as f:
        techs = json.load(f)
    for t in techs:
        tech = Technology(
            name=t["name"], name_en=t.get("name_en", ""),
            category=t["category"], subcategory=t.get("subcategory", ""),
            maturity_level=t.get("maturity_level", 1),
            description=t.get("description", ""),
            key_parameters=t.get("key_parameters"),
            advantages=t.get("advantages", ""),
            challenges=t.get("challenges", ""),
            first_announced=t.get("first_announced", ""),
            expected_mass_production=t.get("expected_mass_production", ""),
        )
        db.session.add(tech)
    db.session.flush()
    print(f"  导入 {len(techs)} 条技术数据")


def _seed_companies():
    """导入公司数据"""
    if not SeedConfig.COMPANIES_FILE.exists():
        return
    with open(SeedConfig.COMPANIES_FILE, "r", encoding="utf-8") as f:
        companies = json.load(f)
    for c in companies:
        company = Company(
            name=c["name"], name_en=c.get("name_en", ""),
            country=c.get("country", ""), company_type=c.get("company_type", ""),
            focus_areas=c.get("focus_areas", []),
            revenue_2024_billion_usd=c.get("revenue_2024_billion_usd"),
            rd_spending_percent=c.get("rd_spending_percent"),
            employee_count=c.get("employee_count"),
            founded_year=c.get("founded_year"),
            description=c.get("description", ""), website=c.get("website", ""),
        )
        db.session.add(company)
    db.session.flush()
    print(f"  导入 {len(companies)} 条公司数据")


def _seed_relations():
    """导入技术关联"""
    if not SeedConfig.RELATIONS_FILE.exists():
        return
    with open(SeedConfig.RELATIONS_FILE, "r", encoding="utf-8") as f:
        relations = json.load(f)
    for r in relations:
        rel = TechnologyRelation(
            source_tech_id=r["source_tech_id"],
            target_tech_id=r["target_tech_id"],
            relation_type=r["relation_type"],
            description=r.get("description", ""),
            strength=r.get("strength", 1),
        )
        db.session.add(rel)
    print(f"  导入 {len(relations)} 条技术关系")


def _seed_roadmap():
    """导入路线图数据"""
    if not SeedConfig.ROADMAP_FILE.exists():
        return
    with open(SeedConfig.ROADMAP_FILE, "r", encoding="utf-8") as f:
        milestones = json.load(f)
    for m in milestones:
        milestone = RoadmapMilestone(
            company_id=m.get("company_id"),
            technology_id=m["technology_id"],
            year=m["year"],
            quarter=m.get("quarter"),
            milestone=m["milestone"],
            description=m.get("description", ""),
            status=m.get("status", "Planned"),
            source_url=m.get("source_url"),
            is_ai_generated=m.get("is_ai_generated", False),
            confidence=m.get("confidence"),
            impact_level=m.get("impact_level", "Medium"),
        )
        db.session.add(milestone)
    print(f"  导入 {len(milestones)} 条路线图里程碑")


def _seed_patents():
    """导入专利数据"""
    if not SeedConfig.PATENT_FILE.exists():
        return
    with open(SeedConfig.PATENT_FILE, "r", encoding="utf-8") as f:
        patents = json.load(f)
    for p in patents:
        patent = Patent(
            technology_id=p.get("technology_id"),
            company_id=p.get("company_id"),
            patent_number=p.get("patent_number"),
            title=p["title"],
            abstract=p.get("abstract", ""),
            filing_date=date.fromisoformat(p["filing_date"]) if p.get("filing_date") else None,
            publication_date=date.fromisoformat(p["publication_date"]) if p.get("publication_date") else None,
            assignee=p.get("assignee"),
            inventors=p.get("inventors"),
            ipc_classification=p.get("ipc_classification"),
            jurisdiction=p.get("jurisdiction"),
            citation_count=p.get("citation_count", 0),
            patent_type=p.get("patent_type", "Invention"),
        )
        db.session.add(patent)
    print(f"  导入 {len(patents)} 条专利数据")


def _seed_papers():
    """导入论文数据"""
    if not SeedConfig.PAPER_FILE.exists():
        return
    with open(SeedConfig.PAPER_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)
    for p in papers:
        paper = ResearchPaper(
            technology_id=p.get("technology_id"),
            title=p["title"],
            authors=p.get("authors", []),
            affiliations=p.get("affiliations", []),
            journal_or_conference=p.get("journal_or_conference"),
            publication_date=date.fromisoformat(p["publication_date"]) if p.get("publication_date") else None,
            doi=p.get("doi"),
            abstract=p.get("abstract", ""),
            citation_count=p.get("citation_count", 0),
            key_findings=p.get("key_findings"),
            paper_type=p.get("paper_type", "Conference"),
        )
        db.session.add(paper)
    print(f"  导入 {len(papers)} 条论文数据")


def _seed_portfolios():
    """自动生成公司技术组合关联"""
    portfolios = [
        {"company_id": 1, "technology_id": 1, "investment_level": "Leading", "key_products": ["HBM3E 12-Hi Shinebolt"], "notes": "全球最大HBM供应商"},
        {"company_id": 1, "technology_id": 2, "investment_level": "Active", "key_products": ["HBM4 16-Hi (开发中)"], "notes": "HBM4样品2025年交付"},
        {"company_id": 1, "technology_id": 3, "investment_level": "Active", "key_products": ["3D DRAM VCT方案"], "notes": "VCT技术路线领先"},
        {"company_id": 1, "technology_id": 4, "investment_level": "Leading", "key_products": ["HBM-PIM Gen2 Amber"], "notes": "PIM技术先驱"},
        {"company_id": 1, "technology_id": 7, "investment_level": "Leading", "key_products": ["3nm GAA MBCFET"], "notes": "首家量产GAA"},
        {"company_id": 2, "technology_id": 1, "investment_level": "Leading", "key_products": ["HBM3E 12-Hi"], "notes": "Nvidia H200/B100主供"},
        {"company_id": 2, "technology_id": 2, "investment_level": "Leading", "key_products": ["HBM4 12-Hi (2025Q3)"], "notes": "HBM4量产进度最快"},
        {"company_id": 2, "technology_id": 3, "investment_level": "Active", "key_products": ["3D DRAM COB方案"], "notes": "电容下置方案研发"},
        {"company_id": 2, "technology_id": 4, "investment_level": "Active", "key_products": ["AiM加速器"], "notes": "GDDR6 PIM方案"},
        {"company_id": 3, "technology_id": 1, "investment_level": "Active", "key_products": ["HBM3E Gen2"], "notes": "HBM3E新进入者"},
        {"company_id": 3, "technology_id": 2, "investment_level": "Following", "key_products": ["HBM4 (2026目标)"], "notes": "加速HBM4追赶"},
        {"company_id": 3, "technology_id": 3, "investment_level": "Active", "key_products": ["3D DRAM研究"], "notes": "IEDM研究成果发表"},
        {"company_id": 4, "technology_id": 7, "investment_level": "Active", "key_products": ["N2 Nanosheet GAA"], "notes": "2025年N2量产"},
        {"company_id": 4, "technology_id": 9, "investment_level": "Leading", "key_products": ["CoWoS-S/R/L"], "notes": "垄断AI芯片封装"},
        {"company_id": 4, "technology_id": 11, "investment_level": "Leading", "key_products": ["SoIC 3D IC"], "notes": "混合键合3D封装"},
        {"company_id": 5, "technology_id": 7, "investment_level": "Active", "key_products": ["Intel 20A/18A RibbonFET"], "notes": "GAA+背面供电"},
        {"company_id": 5, "technology_id": 10, "investment_level": "Leading", "key_products": ["EMIB 2.5代", "Foveros"], "notes": "先进封装差异化"},
        {"company_id": 5, "technology_id": 14, "investment_level": "Leading", "key_products": ["全球首台High-NA EUV"], "notes": "High-NA EUV先行者"},
        {"company_id": 5, "technology_id": 18, "investment_level": "Active", "key_products": ["Loihi 2"], "notes": "神经形态芯片领先"},
        {"company_id": 5, "technology_id": 19, "investment_level": "Leading", "key_products": ["PowerVia背面供电"], "notes": "首个BSPDN量产"},
        {"company_id": 9, "technology_id": 14, "investment_level": "Leading", "key_products": ["EXE:5000 High-NA EUV"], "notes": "全球唯一EUV供应商"},
        {"company_id": 8, "technology_id": 13, "investment_level": "Leading", "key_products": ["CXL 3.0 Retimer"], "notes": "CXL互连芯片领导者"},
        {"company_id": 12, "technology_id": 3, "investment_level": "Following", "key_products": ["3D DRAM专利布局"], "notes": "自主3D DRAM研发"},
        {"company_id": 13, "technology_id": 3, "investment_level": "Exploring", "key_products": [], "notes": "Xtacking架构3D NAND为主"},
        {"company_id": 6, "technology_id": 9, "investment_level": "Following", "key_products": ["B100/B200 (TSMC代工)"], "notes": "CoWoS最大客户"},
        {"company_id": 7, "technology_id": 12, "investment_level": "Leading", "key_products": ["MI300X Chiplet"], "notes": "Chiplet架构先驱"},
    ]
    for pf in portfolios:
        p = CompanyTechnologyPortfolio(
            company_id=pf["company_id"], technology_id=pf["technology_id"],
            investment_level=pf["investment_level"],
            key_products=pf.get("key_products", []),
            notes=pf.get("notes", ""),
        )
        db.session.add(p)
    print(f"  导入 {len(portfolios)} 条公司技术组合")
