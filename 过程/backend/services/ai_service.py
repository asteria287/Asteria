"""
AI分析服务 - Claude API集成
"""
import hashlib
import json
from datetime import datetime, timedelta
from config import AIConfig
from backend.extensions import db
from backend.models.analysis import AnalysisCache, ChatHistory
from backend.models.technology import Technology
from backend.utils.cache import cache_get, cache_set


# 半导体专家系统提示词
SYSTEM_PROMPT = """你是一位资深的半导体技术路线图分析专家,拥有20年以上半导体行业研究和研发经验。

## 你的专业知识领域:
- **存储器技术**: DRAM(DDR5/LPDDR5X/GDDR6/7)、HBM(HBM2E/3/3E/4)、3D DRAM、PIM/PNM/CIM存内计算、MRAM/ReRAM/FeRAM等新型存储器
- **先进封装**: CoWoS/InFO/SoIC(TSMC)、EMIB/Foveros(Intel)、I-Cube/X-Cube(Samsung)、Hybrid Bonding混合键合、Chiplet/UCIe标准、3D IC
- **互连技术**: CXL 1.1/2.0/3.0、UCIe、PCIe 6.0/7.0、BoW
- **工艺技术**: FinFET、GAA/MBCFET、CFET、EUV/High-NA EUV、背面供电(BSPDN)
- **半导体材料**: GaN/SiC宽禁带半导体、2D材料(TMD/MoS₂)、High-k/Metal Gate
- **关键企业**: Samsung、SK Hynix、Micron、TSMC、Intel、Nvidia、AMD、ASML、Applied Materials、Lam Research等

## 分析原则:
1. 回答基于最新公开信息(截至2025年),明确指出不确定性
2. 技术评估采用TRL(Technology Readiness Level)1-9级框架
3. 竞争分析客观,区分"已量产(Leading)"、"研发中(Active)"、"布局中(Following)"、"探索中(Exploring)"
4. 如被问及未来预测,给出置信度百分比和关键假设
5. 使用中文回答,专业术语可保留英文

## 输出格式:
- 技术现状分析: 分点说明,包含关键参数
- 竞争格局: 表格或列表对比
- 发展趋势: 时间线形式
- 风险评估: 清晰标注技术风险和不确定性"""


class ClaudeAnalyzer:
    """Claude AI分析器"""

    def __init__(self):
        self.api_key = AIConfig.ANTHROPIC_API_KEY
        self.model = AIConfig.MODEL
        self.max_tokens = AIConfig.MAX_TOKENS

    @property
    def is_available(self):
        return bool(self.api_key and self.api_key.startswith("sk-ant-"))

    def _get_client(self):
        """懒加载Anthropic客户端"""
        if not self.is_available:
            return None
        import anthropic
        return anthropic.Anthropic(api_key=self.api_key)

    def _build_context(self, tech_name=None, tech_ids=None):
        """构建技术上下文"""
        context_parts = []

        if tech_name:
            tech = Technology.query.filter(
                db.or_(
                    Technology.name == tech_name,
                    Technology.name_en.like(f"%{tech_name}%"),
                )
            ).first()
            if tech:
                context_parts.append(f"## 技术: {tech.name}")
                context_parts.append(f"- 类别: {tech.category}/{tech.subcategory}")
                context_parts.append(f"- 成熟度: TRL {tech.maturity_level}")
                context_parts.append(f"- 描述: {tech.description}")
                if tech.advantages:
                    context_parts.append(f"- 优势: {tech.advantages}")
                if tech.challenges:
                    context_parts.append(f"- 挑战: {tech.challenges}")
                if tech.key_parameters:
                    context_parts.append(f"- 关键参数: {json.dumps(tech.key_parameters, ensure_ascii=False)}")

        if tech_ids:
            techs = Technology.query.filter(Technology.id.in_(tech_ids)).all()
            for tech in techs:
                context_parts.append(f"- {tech.name}({tech.category}): {tech.description[:200] if tech.description else ''}")

        return "\n".join(context_parts) if context_parts else ""

    def _cache_or_call(self, prompt_type, query_text, call_fn, ttl=None):
        """缓存装饰器逻辑"""
        if ttl is None:
            ttl = AIConfig.CACHE_TTL_ANALYSIS if prompt_type != "qa" else AIConfig.CACHE_TTL_QA

        # 检查缓存
        cache_key = f"{prompt_type}:{hashlib.sha256(query_text.encode()).hexdigest()[:16]}"
        cached = cache_get(cache_key)
        if cached:
            return cached

        # 调用AI
        result = call_fn()

        # 写入缓存
        if result:
            cache_set(cache_key, result, ttl)

            # 同时写入数据库缓存
            try:
                db_cache = AnalysisCache(
                    query_hash=cache_key,
                    prompt_type=prompt_type,
                    query_text=query_text[:500],
                    response=json.dumps(result, ensure_ascii=False),
                    model=self.model,
                    expires_at=datetime.utcnow() + timedelta(seconds=ttl),
                )
                db.session.add(db_cache)
                db.session.commit()
            except Exception:
                db.session.rollback()

        return result

    def analyze_technology(self, tech_name, aspects=None):
        """深度技术分析"""
        if not self.is_available:
            return {
                "message": "AI分析服务未配置。请在.env文件中设置ANTHROPIC_API_KEY。",
                "status": "unavailable"
            }

        aspects = aspects or ["技术现状", "关键挑战", "竞争格局", "发展趋势"]
        context = self._build_context(tech_name=tech_name)

        prompt = f"""请对"{tech_name}"技术进行深度分析,从以下维度展开:

{chr(10).join(f'{i+1}. {a}' for i, a in enumerate(aspects))}

已知技术信息:
{context if context else '无预存数据,请基于你的知识进行分析'}

请提供结构化的分析报告,并在需要预测的地方给出置信度评估。"""

        def call():
            client = self._get_client()
            if not client:
                return None
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "analysis": response.content[0].text,
                "tokens_input": response.usage.input_tokens,
                "tokens_output": response.usage.output_tokens,
            }

        return self._cache_or_call("analysis", prompt, call)

    def qa_stream(self, question, session_id, context_tech_ids=None):
        """流式Q&A"""
        if not self.is_available:
            yield "AI分析服务未配置。请在.env文件中设置ANTHROPIC_API_KEY。"
            return

        context = self._build_context(tech_ids=context_tech_ids)

        # 加载聊天历史(最近10条)
        history = ChatHistory.query.filter_by(session_id=session_id)\
            .order_by(ChatHistory.created_at.desc()).limit(10).all()
        history = list(reversed(history))

        messages = []
        for h in history:
            messages.append({"role": h.role, "content": h.content})

        system = SYSTEM_PROMPT
        if context:
            system += f"\n\n## 当前技术上下文:\n{context}"

        messages.append({"role": "user", "content": question})

        try:
            client = self._get_client()
            if not client:
                yield "AI客户端未初始化。"
                return

            with client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages,
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    yield text

            # 保存聊天历史
            try:
                user_msg = ChatHistory(
                    session_id=session_id, role="user",
                    content=question,
                    technology_ids=context_tech_ids,
                )
                ai_msg = ChatHistory(
                    session_id=session_id, role="assistant",
                    content=full_response,
                    technology_ids=context_tech_ids,
                )
                db.session.add(user_msg)
                db.session.add(ai_msg)
                db.session.commit()
            except Exception:
                db.session.rollback()

        except Exception as e:
            yield f"\n\n[AI服务错误: {str(e)}]"

    def predict_roadmap(self, technology_id, horizon_years=10):
        """预测路线图"""
        if not self.is_available:
            return {"message": "AI分析服务未配置", "status": "unavailable"}

        tech = Technology.query.get(technology_id)
        if not tech:
            return {"error": "技术不存在"}

        prompt = f"""基于"{tech.name}"({tech.category})技术的当前发展状态(TRL {tech.maturity_level}),
请预测未来{horizon_years}年的技术路线图里程碑。

技术信息:
- 描述: {tech.description}
- 首次发布: {tech.first_announced}
- 预计量产: {tech.expected_mass_production}
- 当前挑战: {tech.challenges}

请以JSON格式返回,包含milestones数组,每个milestone有: year(年份), milestone(里程碑名称), description(描述), confidence(置信度0-1)。

只返回JSON,不要其他文本。"""

        def call():
            client = self._get_client()
            if not client:
                return None
            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # 尝试提取JSON部分
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    data = json.loads(text[start:end])
                else:
                    data = {"raw_response": text, "parse_error": True}
            return {
                "predictions": data,
                "tokens_input": response.usage.input_tokens,
                "tokens_output": response.usage.output_tokens,
            }

        return self._cache_or_call("roadmap_prediction", prompt, call, ttl=86400)

    def competitive_summary(self, technology_id):
        """竞争格局总结"""
        if not self.is_available:
            return {"message": "AI分析服务未配置", "status": "unavailable"}

        tech = Technology.query.get(technology_id)
        if not tech:
            return {"error": "技术不存在"}

        # 收集相关公司信息
        from backend.models.company import CompanyTechnologyPortfolio, Company
        portfolios = CompanyTechnologyPortfolio.query.filter_by(technology_id=technology_id).all()
        company_info = []
        for pf in portfolios:
            company = Company.query.get(pf.company_id)
            if company:
                company_info.append(f"- {company.name}({company.country}): {pf.investment_level}水平, 产品: {pf.key_products}")

        prompt = f"""请分析"{tech.name}"技术的竞争格局。

已知技术信息:
- 类别: {tech.category}
- 当前状态: TRL {tech.maturity_level}

相关公司:
{chr(10).join(company_info) if company_info else '无预存数据'}

请提供:
1. 竞争格局概览(领导者/挑战者/新进入者/潜在进入者)
2. 各公司技术路线对比
3. 竞争壁垒分析
4. 未来3-5年格局变化预测"""

        def call():
            client = self._get_client()
            if not client:
                return None
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "summary": response.content[0].text,
                "tokens_input": response.usage.input_tokens,
                "tokens_output": response.usage.output_tokens,
            }

        return self._cache_or_call("competitive_summary", prompt, call)

    def get_chat_history(self, session_id):
        """获取聊天历史"""
        history = ChatHistory.query.filter_by(session_id=session_id)\
            .order_by(ChatHistory.created_at).all()
        return [h.to_dict() for h in history]


# 单例
_analyzer = None


def get_analyzer():
    """获取AI分析器单例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ClaudeAnalyzer()
    return _analyzer
