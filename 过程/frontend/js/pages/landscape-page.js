/**
 * 技术全景 - 力导向图 + 详情面板
 */
const LandscapePage = {
    template: `
        <div class="animate-fade-in" style="height:calc(100vh - 120px);">
            <!-- 工具栏 -->
            <div class="flex items-center gap-md" style="margin-bottom:16px;">
                <div class="search-bar" style="width:300px;">
                    <span class="search-icon">🔍</span>
                    <input v-model="searchQuery" placeholder="搜索技术..." @input="filterData">
                </div>
                <select class="form-select" v-model="filterCategory" @change="filterData">
                    <option value="">全部类别</option>
                    <option v-for="(cat, key) in CONSTANTS.CATEGORIES" :key="key" :value="key">
                        {{ cat.label }}
                    </option>
                </select>
                <span class="text-muted text-sm">
                    显示 {{ filteredNodes.length }} / {{ allNodes.length }} 节点
                </span>
            </div>

            <!-- 力导向图 -->
            <div style="height:100%;position:relative;">
                <chart-container
                    v-if="graphOption"
                    :option="graphOption"
                    :large="true"
                    @chart-click="onNodeClick">
                </chart-container>
                <loading-spinner v-else text="构建技术图谱..."></loading-spinner>
            </div>

            <!-- 详情面板 -->
            <div v-if="store.ui.detailPanelVisible && selectedTech" class="detail-panel">
                <div class="detail-panel-header">
                    <div>
                        <div class="text-lg" style="font-weight:600;">{{ selectedTech.name }}</div>
                        <tech-badge :category="selectedTech.category"></tech-badge>
                    </div>
                    <button class="detail-panel-close" @click="store.closeDetailPanel()">✕</button>
                </div>
                <div class="detail-panel-body">
                    <div class="metric-grid" style="grid-template-columns:1fr 1fr;">
                        <div class="metric-card" style="padding:12px;">
                            <span class="metric-label">技术成熟度</span>
                            <div class="metric-value" style="font-size:24px;">TRL {{ selectedTech.maturity_level }}</div>
                            <span class="text-muted text-sm">{{ format.maturityLevel(selectedTech.maturity_level) }}</span>
                        </div>
                        <div class="metric-card" style="padding:12px;">
                            <span class="metric-label">预计量产</span>
                            <div class="metric-value" style="font-size:24px;">{{ selectedTech.expected_mass_production || '待定' }}</div>
                        </div>
                    </div>
                    <div style="margin-top:16px;">
                        <h4 style="color:var(--color-text-muted);margin-bottom:8px;">技术描述</h4>
                        <p style="line-height:1.8;">{{ selectedTech.description || '暂无详细描述' }}</p>
                    </div>
                    <div v-if="selectedTech.advantages" style="margin-top:16px;">
                        <h4 style="color:var(--color-success);margin-bottom:8px;">优势</h4>
                        <p>{{ selectedTech.advantages }}</p>
                    </div>
                    <div v-if="selectedTech.challenges" style="margin-top:16px;">
                        <h4 style="color:var(--color-warning);margin-bottom:8px;">挑战</h4>
                        <p>{{ selectedTech.challenges }}</p>
                    </div>
                    <div style="margin-top:16px;">
                        <button class="btn btn-primary" @click="router.navigate('/ai-assistant', {tech: selectedTech.id})">
                            🤖 AI深度分析
                        </button>
                        <button class="btn" style="margin-left:8px;" @click="router.navigate('/roadmap', {tech: selectedTech.id})">
                            🗺️ 查看路线图
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            searchQuery: "",
            filterCategory: "",
            selectedTech: null,
        };
    },

    computed: {
        allNodes() {
            return store.technologies.map((t) => ({
                id: t.id,
                name: t.name,
                category: t.category,
                symbolSize: Math.max(20, (t.maturity_level || 1) * 5),
                itemStyle: {
                    color: CONSTANTS.CATEGORIES[t.category]?.color || "#3b82f6",
                },
                tech: t,
            }));
        },

        allEdges() {
            const edges = [];
            store.technologies.forEach((t) => {
                if (t.related_techs) {
                    t.related_techs.forEach((rel) => {
                        edges.push({
                            source: t.id,
                            target: rel.id,
                            relation_type: rel.relation_type || "related_to",
                            strength: rel.strength || 1,
                        });
                    });
                }
            });
            return edges;
        },

        filteredNodes() {
            let nodes = this.allNodes;
            if (this.searchQuery) {
                const q = this.searchQuery.toLowerCase();
                nodes = nodes.filter((n) => n.name.toLowerCase().includes(q));
            }
            if (this.filterCategory) {
                nodes = nodes.filter((n) => n.category === this.filterCategory);
            }
            return nodes;
        },

        filteredEdges() {
            const nodeIds = new Set(this.filteredNodes.map((n) => n.id));
            return this.allEdges.filter(
                (e) => nodeIds.has(e.source) && nodeIds.has(e.target)
            );
        },

        graphOption() {
            if (this.filteredNodes.length === 0) return null;
            const categories = Object.entries(CONSTANTS.CATEGORIES).map(([key, val]) => ({
                name: val.label,
                itemStyle: { color: val.color },
            }));
            return Charts.createForceGraphOption(
                this.filteredNodes,
                this.filteredEdges,
                categories
            );
        },
    },

    methods: {
        filterData() {
            // computed自动处理
        },
        onNodeClick(params) {
            if (params.data?.tech) {
                this.selectedTech = params.data.tech;
                store.openDetailPanel(params.data.tech);
            }
        },
    },

    setup() {
        return { store, router: window.router, CONSTANTS, format };
    },
};
