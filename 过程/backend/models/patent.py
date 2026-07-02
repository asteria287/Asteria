"""
专利和论文模型
"""
from datetime import datetime, date
from backend.extensions import db


class Patent(db.Model):
    """专利记录"""
    __tablename__ = "patents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    technology_id = db.Column(
        db.Integer, db.ForeignKey("technologies.id"), nullable=True
    )
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=True
    )
    patent_number = db.Column(db.String(50), comment="专利号")
    title = db.Column(db.String(500), nullable=False, comment="专利标题")
    abstract = db.Column(db.Text, comment="专利摘要")
    filing_date = db.Column(db.Date, comment="申请日期")
    publication_date = db.Column(db.Date, comment="公开日期")
    assignee = db.Column(db.String(200), comment="专利权人")
    inventors = db.Column(db.JSON, comment="发明人列表")
    ipc_classification = db.Column(db.String(100), comment="IPC分类号")
    jurisdiction = db.Column(db.String(10), comment="管辖区域: US/CN/KR/EP/WO/JP")
    citation_count = db.Column(db.Integer, default=0, comment="引用次数")
    patent_type = db.Column(
        db.String(30),
        default="Invention",
        comment="专利类型: Invention/Utility/Design"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "technology_id": self.technology_id,
            "company_id": self.company_id,
            "patent_number": self.patent_number,
            "title": self.title,
            "abstract": self.abstract,
            "filing_date": (
                self.filing_date.isoformat() if self.filing_date else None
            ),
            "publication_date": (
                self.publication_date.isoformat() if self.publication_date else None
            ),
            "assignee": self.assignee,
            "inventors": self.inventors,
            "ipc_classification": self.ipc_classification,
            "jurisdiction": self.jurisdiction,
            "citation_count": self.citation_count,
            "patent_type": self.patent_type,
        }


class ResearchPaper(db.Model):
    """研究论文"""
    __tablename__ = "research_papers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    technology_id = db.Column(
        db.Integer, db.ForeignKey("technologies.id"), nullable=True
    )
    title = db.Column(db.String(500), nullable=False, comment="论文标题")
    authors = db.Column(db.JSON, comment="作者列表")
    affiliations = db.Column(db.JSON, comment="所属机构列表")
    journal_or_conference = db.Column(
        db.String(200), comment="期刊/会议名称"
    )
    publication_date = db.Column(db.Date, comment="发表日期")
    doi = db.Column(db.String(200), comment="DOI")
    abstract = db.Column(db.Text, comment="摘要")
    citation_count = db.Column(db.Integer, default=0, comment="引用次数")
    key_findings = db.Column(db.Text, comment="关键发现")
    paper_type = db.Column(
        db.String(30),
        default="Conference",
        comment="类型: Journal/Conference/Review/WhitePaper"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "technology_id": self.technology_id,
            "title": self.title,
            "authors": self.authors,
            "affiliations": self.affiliations,
            "journal_or_conference": self.journal_or_conference,
            "publication_date": (
                self.publication_date.isoformat() if self.publication_date else None
            ),
            "doi": self.doi,
            "abstract": self.abstract,
            "citation_count": self.citation_count,
            "key_findings": self.key_findings,
            "paper_type": self.paper_type,
        }
