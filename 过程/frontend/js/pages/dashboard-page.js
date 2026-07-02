/**
 * 首页总览 - Dashboard
 */
const DashboardPage = {
    template: `
        <div class="animate-fade-in">
            <!-- KPI指标卡 -->
            <div class="metric-grid">
                <metric-card
                    label="追踪技术"
                    :value="store.technologies.length"
                    :change="{ direction: 'up', text: '覆盖6大类别' }"
                    icon="🔬">
                </metric-card>
                <metric-card
                    label="监控公司"
                    :value="store.companies.length"
                    :change="{ direction: 'up', text: '全球主要玩家' }"
                    icon="🏢">
                </metric-card>
                <metric-card
                    label="路线图里程碑"
                    :value="milestoneCount"
                    :change="{ direction: 'up', text: yearRange + ' 年度覆盖' }"
                    icon="🎯">
                </metric-card>
                <metric-card
                    label="AI分析模块"
                    :value="'就绪'"
                    icon="🤖">
                </metric-card>
            </div>

            <!-- 内容区域 -->
            <div class="grid-2">
                <!-- 技术分布雷达图 -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">技术领域覆盖</span>
                        <button class="btn btn-sm" @click="router.navigate('/landscape')">查看全景 →</button>
                    </div>
                    <div class="card-body">
                        <chart-container
                            v-if="radarOption"
                            :option="radarOption"
                            :large="false">
                        </chart-container>
                        <loading-spinner v-else text="加载图表数据..."></loading-spinner>
                    </div>
                </div>

                <!-- 近期动态 -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">快速导航</span>
                    </div>
                    <div class="card-body">
                        <div style="display:flex;flex-direction:column;gap:12px;">
                            <div v-for="section in quickActions" :key="section.label"
                                 class="card" style="cursor:pointer;padding:12px;"
                                 @click="router.navigate(section.route)">
                                <div class="flex items-center gap-sm">
                                    <span style="font-size:24px;">{{ section.icon }}</span>
                                    <div>
                                        <div style="font-weight:600;">{{ section.label }}</div>
                                        <div class="text-muted text-sm">{{ section.desc }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 技术类别分布 -->
            <div class="card" style="margin-top:16px;">
                <div class="card-header">
                    <span class="card-title">技术类别分布</span>
                </div>
                <div class="card-body">
                    <div class="flex gap-md" style="flex-wrap:wrap;">
                        <div v-for="cat in categories" :key="cat.name" class="card" style="flex:1;min-width:180px;padding:16px;">
                            <div class="flex items-center gap-sm">
                                <span style="font-size:24px;">{{ cat.icon }}</span>
                                <div>
                                    <div style="font-weight:600;">{{ cat.label }}</div>
                                    <div class="text-muted text-sm">{{ cat.count }} 项技术</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            quickActions: [
                { icon: "🔬", label: "技术全景分析", desc: "可视化技术关系图谱", route: "/landscape" },
                { icon: "🏢", label: "竞争格局对比", desc: "公司技术组合矩阵", route: "/competitive" },
                { icon: "🗺️", label: "技术路线图", desc: "时间线里程碑查看", route: "/roadmap" },
                { icon: "🤖", label: "AI智能分析", desc: "深度技术问答", route: "/ai-assistant" },
            ],
        };
    },

    computed: {
        categories() {
            const cats = {};
            store.technologies.forEach((t) => {
                if (!cats[t.category]) {
                    cats[t.category] = {
                        name: t.category,
                        label: format.categoryLabel(t.category),
                        icon: CONSTANTS.CATEGORIES[t.category]?.icon || "📌",
                        count: 0,
                    };
                }
                cats[t.category].count++;
            });
            return Object.values(cats).sort((a, b) => b.count - a.count);
        },

        radarOption() {
            const cats = [...new Set(store.technologies.map((t) => t.category))];
            if (cats.length === 0) return null;

            const indicators = cats.map((c) => ({
                name: format.categoryLabel(c),
                max: 10,
            }));

            const values = cats.map((c) => {
                const techs = store.technologies.filter((t) => t.category === c);
                return Math.min(
                    Math.round((techs.reduce((s, t) => s + (t.maturity_level || 1), 0) / Math.max(techs.length, 1))),
                    10
                );
            });

            return Charts.createRadarOption(indicators, [
                { name: "技术成熟度", value: values },
            ]);
        },

        milestoneCount() {
            return store.roadmapMilestones.length || "~100+";
        },

        yearRange() {
            return "2020-2035";
        },
    },

    setup() {
        return { store, router: window.router, format };
    },
};
