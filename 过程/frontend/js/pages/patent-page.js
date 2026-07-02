/**
 * 专利与论文分析
 */
const PatentPage = {
    template: `
        <div class="animate-fade-in">
            <div class="flex items-center justify-between" style="margin-bottom:16px;">
                <h2 style="font-size:var(--font-size-xl);">专利与论文趋势分析</h2>
                <div class="flex gap-sm">
                    <button class="btn" :class="{ 'btn-primary': activeTab === 'patents' }"
                            @click="activeTab = 'patents'">专利分析</button>
                    <button class="btn" :class="{ 'btn-primary': activeTab === 'papers' }"
                            @click="activeTab = 'papers'">论文分析</button>
                </div>
            </div>

            <!-- 趋势图 -->
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">{{ activeTab === 'patents' ? '专利申请趋势' : '论文发表趋势' }}</span>
                    </div>
                    <div class="card-body">
                        <chart-container
                            v-if="trendOption"
                            :option="trendOption">
                        </chart-container>
                        <loading-spinner v-else text="加载趋势数据..."></loading-spinner>
                    </div>
                </div>

                <!-- Top排名 -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">{{ activeTab === 'patents' ? 'Top 专利权人' : 'Top 研究机构' }}</span>
                    </div>
                    <div class="card-body">
                        <chart-container
                            v-if="barOption"
                            :option="barOption">
                        </chart-container>
                        <loading-spinner v-else text="加载排名数据..."></loading-spinner>
                    </div>
                </div>
            </div>

            <!-- 地理分布 -->
            <div class="card" style="margin-top:16px;">
                <div class="card-header">
                    <span class="card-title">地理分布概览</span>
                </div>
                <div class="card-body">
                    <div class="flex gap-md" style="flex-wrap:wrap;">
                        <div v-for="region in regions" :key="region.name" class="card" style="flex:1;min-width:180px;padding:16px;text-align:center;">
                            <div style="font-size:32px;margin-bottom:8px;">{{ region.flag }}</div>
                            <div style="font-weight:600;">{{ region.name }}</div>
                            <div class="metric-value" style="font-size:20px;">{{ format.number(region.count) }}</div>
                            <div class="text-muted text-sm">{{ activeTab === 'patents' ? '件专利' : '篇论文' }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            activeTab: "patents",
        };
    },

    computed: {
        trendOption() {
            // 占位数据 - Phase 4实现真实数据
            const years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"];
            const series = [
                { name: "3D DRAM", data: [45, 52, 68, 85, 110, 135, 158] },
                { name: "HBM", data: [30, 38, 55, 72, 95, 120, 145] },
                { name: "PIM", data: [15, 22, 35, 48, 62, 78, 95] },
                { name: "CXL", data: [5, 12, 25, 42, 58, 75, 90] },
            ];
            return Charts.createTrendLineOption(years, series);
        },

        barOption() {
            const labels = ["Samsung", "SK Hynix", "Micron", "TSMC", "Intel", "Kioxia", "CXMT", "YMTC"];
            const values = [2850, 2100, 1850, 3200, 2900, 1500, 450, 380];
            return Charts.createBarOption(labels, values, true);
        },

        regions() {
            return [
                { name: "韩国", flag: "🇰🇷", count: 12500 },
                { name: "美国", flag: "🇺🇸", count: 15800 },
                { name: "中国大陆", flag: "🇨🇳", count: 9800 },
                { name: "中国台湾", flag: "🇹🇼", count: 7200 },
                { name: "日本", flag: "🇯🇵", count: 5600 },
                { name: "欧洲", flag: "🇪🇺", count: 4200 },
            ];
        },
    },

    setup() {
        return { format };
    },
};
