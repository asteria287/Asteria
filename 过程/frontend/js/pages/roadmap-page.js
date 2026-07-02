/**
 * 技术路线图 - 甘特图时间线 + 筛选器
 */
const RoadmapPage = {
    template: `
        <div class="animate-fade-in">
            <!-- 工具栏 -->
            <div class="flex items-center justify-between" style="margin-bottom:16px;">
                <h2 style="font-size:var(--font-size-xl);">技术路线图</h2>
                <div class="flex gap-sm">
                    <select class="form-select" v-model="filterTechId">
                        <option value="">全部技术</option>
                        <option v-for="t in store.technologies" :key="t.id" :value="t.id">{{ t.name }}</option>
                    </select>
                    <select class="form-select" v-model="filterCompanyId">
                        <option value="">全部公司</option>
                        <option v-for="c in store.companies" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                    <button class="btn btn-primary" @click="router.navigate('/ai-assistant')">
                        🤖 AI预测路线图
                    </button>
                </div>
            </div>

            <!-- 时间线统计 -->
            <div class="flex gap-md" style="margin-bottom:16px;">
                <div class="badge badge-success">✅ 已完成: {{ statusCounts.Achieved || 0 }}</div>
                <div class="badge badge-primary">🔄 进行中: {{ statusCounts['In Progress'] || 0 }}</div>
                <div class="badge badge-warning">📋 计划中: {{ statusCounts.Planned || 0 }}</div>
                <div class="badge" style="background:rgba(148,163,184,0.2);">🔮 预测: {{ statusCounts.Speculative || 0 }}</div>
            </div>

            <!-- 甘特图 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">{{ yearStart }} - {{ yearEnd }} 里程碑时间线</span>
                    <span class="text-muted text-sm">共 {{ totalMilestones }} 个里程碑</span>
                </div>
                <div class="card-body">
                    <chart-container
                        v-if="timelineOption"
                        :option="timelineOption"
                        :large="true">
                    </chart-container>
                    <div v-else style="text-align:center;padding:60px;color:var(--color-text-muted);">
                        <div style="font-size:48px;margin-bottom:16px;">🗺️</div>
                        <p>路线图数据加载中...</p>
                        <p class="text-sm">种子数据导入后将显示完整时间线</p>
                    </div>
                </div>
            </div>

            <!-- 近期里程碑列表 -->
            <div class="card" style="margin-top:16px;">
                <div class="card-header">
                    <span class="card-title">近期里程碑 (2024-2026)</span>
                </div>
                <div class="card-body">
                    <div class="timeline-list">
                        <div v-for="m in recentMilestones" :key="m.id" :class="['timeline-item', m.status.toLowerCase().replace(' ', '-')]">
                            <div>
                                <div style="font-weight:600;">{{ m.milestone }}</div>
                                <div class="text-muted text-sm">
                                    {{ m.year }}{{ m.quarter ? ' ' + m.quarter : '' }}
                                    <span v-if="m.company_name"> · {{ m.company_name }}</span>
                                    <span v-if="m.technology_name"> · {{ m.technology_name }}</span>
                                </div>
                            </div>
                            <span :class="['badge', 'badge-' + (m.status === 'Achieved' ? 'success' : m.status === 'In Progress' ? 'info' : 'warning')]">
                                {{ format.statusLabel(m.status) }}
                            </span>
                        </div>
                        <div v-if="recentMilestones.length === 0" class="text-muted text-sm" style="padding:16px;text-align:center;">
                            数据加载中...
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            filterTechId: "",
            filterCompanyId: "",
            yearStart: 2020,
            yearEnd: 2035,
        };
    },

    computed: {
        filteredMilestones() {
            let items = store.roadmapMilestones || [];
            if (this.filterTechId) {
                items = items.filter((m) => m.technology_id == this.filterTechId);
            }
            if (this.filterCompanyId) {
                items = items.filter((m) => m.company_id == this.filterCompanyId);
            }
            return items.filter(
                (m) => m.year >= this.yearStart && m.year <= this.yearEnd
            );
        },

        totalMilestones() {
            return this.filteredMilestones.length;
        },

        statusCounts() {
            const counts = {};
            this.filteredMilestones.forEach((m) => {
                counts[m.status] = (counts[m.status] || 0) + 1;
            });
            return counts;
        },

        recentMilestones() {
            return (store.roadmapMilestones || [])
                .filter((m) => m.year >= 2024 && m.year <= 2026)
                .sort((a, b) => a.year - b.year || (a.quarter || "").localeCompare(b.quarter || ""))
                .slice(0, 15);
        },

        timelineOption() {
            if (this.filteredMilestones.length === 0) return null;
            // 按技术分组
            const groups = {};
            this.filteredMilestones.forEach((m) => {
                const key = m.technology_name || `技术${m.technology_id}`;
                if (!groups[key]) groups[key] = [];
                groups[key].push(m);
            });
            const data = Object.entries(groups).map(([name, milestones]) => ({
                name,
                milestones,
            }));
            return Charts.createTimelineOption(data, [this.yearStart, this.yearEnd]);
        },
    },

    setup() {
        return { store, router: window.router, format };
    },
};
