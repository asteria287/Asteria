"""
技术数据服务层
"""
from backend.extensions import db
from backend.models.technology import Technology, TechnologyRelation
from backend.models.company import Company


class TechnologyService:
    """技术服务"""

    def get_all(self, filters=None):
        """获取所有技术，支持筛选"""
        query = Technology.query
        if filters:
            if filters.get("category"):
                query = query.filter(Technology.category == filters["category"])
            if filters.get("maturity_min"):
                query = query.filter(Technology.maturity_level >= int(filters["maturity_min"]))
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.filter(
                    db.or_(
                        Technology.name.like(search),
                        Technology.name_en.like(search),
                        Technology.description.like(search),
                    )
                )
        techs = query.order_by(Technology.category, Technology.maturity_level.desc()).all()
        return [t.to_dict() for t in techs]

    def get_by_id(self, tech_id):
        """获取单个技术详情"""
        tech = Technology.query.get(tech_id)
        if not tech:
            return None
        result = tech.to_dict()
        # 包含关联关系
        relations = []
        for r in tech.relations_from:
            target = Technology.query.get(r.target_tech_id)
            relations.append({
                "id": r.target_tech_id,
                "name": target.name if target else "",
                "relation_type": r.relation_type,
                "description": r.description,
                "strength": r.strength,
                "direction": "out",
            })
        for r in tech.relations_to:
            source = Technology.query.get(r.source_tech_id)
            relations.append({
                "id": r.source_tech_id,
                "name": source.name if source else "",
                "relation_type": r.relation_type,
                "description": r.description,
                "strength": r.strength,
                "direction": "in",
            })
        result["related_techs"] = relations
        return result

    def get_landscape(self, center_tech_id=None):
        """获取技术全景图谱数据(节点+边)"""
        techs = Technology.query.all()
        nodes = [{
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "maturity_level": t.maturity_level,
            "symbolSize": max(20, (t.maturity_level or 1) * 5),
        } for t in techs]

        relations = TechnologyRelation.query.all()
        edges = [{
            "source": r.source_tech_id,
            "target": r.target_tech_id,
            "relation_type": r.relation_type,
            "description": r.description,
            "strength": r.strength,
        } for r in relations]

        return {"nodes": nodes, "edges": edges}

    def get_overview(self):
        """获取技术概览统计"""
        techs = Technology.query.all()
        categories = {}
        for t in techs:
            if t.category not in categories:
                categories[t.category] = {"count": 0, "avg_maturity": 0, "techs": []}
            categories[t.category]["count"] += 1
            categories[t.category]["techs"].append(t.name)

        for cat in categories:
            cat_techs = [t for t in techs if t.category == cat]
            categories[cat]["avg_maturity"] = round(
                sum(t.maturity_level for t in cat_techs) / len(cat_techs), 1
            )

        # 热门技术(成熟度最高的前5)
        hot_techs = sorted(techs, key=lambda t: t.maturity_level, reverse=True)[:5]

        return {
            "total": len(techs),
            "categories": categories,
            "hot_technologies": [t.to_dict() for t in hot_techs],
            "maturity_distribution": self._maturity_distribution(techs),
        }

    def get_radar_data(self):
        """获取雷达图数据"""
        techs = Technology.query.all()
        categories = list(set(t.category for t in techs))
        indicators = [{"name": cat, "max": 10} for cat in categories]

        # 整体成熟度
        avg_values = []
        for cat in categories:
            cat_techs = [t for t in techs if t.category == cat]
            avg = sum(t.maturity_level for t in cat_techs) / max(len(cat_techs), 1)
            avg_values.append(round(avg, 1))

        return {
            "indicators": indicators,
            "series": [
                {"name": "平均技术成熟度", "value": avg_values}
            ],
        }

    def _maturity_distribution(self, techs):
        """计算成熟度分布"""
        dist = {i: 0 for i in range(1, 10)}
        for t in techs:
            if t.maturity_level:
                dist[t.maturity_level] = dist.get(t.maturity_level, 0) + 1
        return dist
