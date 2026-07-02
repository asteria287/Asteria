/**
 * 竞争格局 - 公司对比矩阵 + 雷达图 + 市场份额
 */
const CompetitivePage = {
    template: `
        <div class="animate-fade-in">
            <div class="flex items-center justify-between" style="margin-bottom:16px;">
                <h2 style="font-size:var(--font-size-xl);">竞争格局分析</h2>
                <div class="flex gap-sm">
                    <select class="form-select" v-model="selectedSegment">
                        <option value="all">全部领域</option>
                        <option value="Memory">存储器</option>
                        <option value="Logic">逻辑芯片</option>
                        <option value="Packaging">先进封装</option>
                        <option value="Interconnect">互连技术</option>
                    </select>
                </div>
            </div>

            <!-- 公司列表 -->
            <div class="grid-3" style="margin-bottom:16px;">
                <div v-for="company in filteredCompanies" :key="company.id"
                     class="card" style="cursor:pointer;padding:16px;"
                     :style="{ borderColor: selectedCompanyId === company.id ? 'var(--color-accent)' : '' }"
                     @click="selectCompany(company)">
                    <div class="flex items-center justify-between">
                        <div>
                            <div style="font-weight:600;font-size:var(--font-size-lg);">{{ company.name }}</div>
                            <div class="text-muted text-sm">{{ company.name_en }}</div>
                        </div>
                        <span class="badge badge-info">{{ company.country }}</span>
                    </div>
                    <div class="flex gap-sm" style="margin-top:8px;flex-wrap:wrap;">
                        <span class="badge badge-primary">{{ CONSTANTS.COMPANY_TYPES[company.company_type] || company.company_type }}</span>
                        <span v-if="company.revenue_2024_billion_usd" class="badge badge-success">
                            营收 {{ format.currency(company.revenue_2024_billion_usd) }}
                        </span>
                    </div>
                    <div class="text-muted text-sm" style="margin-top:8px;">
                        {{ format.truncated(company.description, 80) }}
                    </div>
                </div>
            </div>

            <!-- 公司详情 -->
            <div v-if="selectedCompany" class="card" style="margin-bottom:16px;">
                <div class="card-header">
                    <span class="card-title">{{ selectedCompany.name }} - 技术组合</span>
                    <button class="btn btn-sm" @click="selectedCompany = null">关闭</button>
                </div>
                <div class="card-body">
                    <div class="grid-2">
                        <div>
                            <h4 style="color:var(--color-text-muted);margin-bottom:8px;">重点领域</h4>
                            <div class="flex gap-sm" style="flex-wrap:wrap;">
                                <span v-for="area in (selectedCompany.focus_areas || [])" :key="area"
                                      class="badge badge-primary">{{ area }}</span>
                            </div>
                            <div style="margin-top:16px;">
                                <p><strong>研发投入占比:</strong> {{ selectedCompany.rd_spending_percent }}%</p>
                                <p><strong>员工规模:</strong> {{ format.number(selectedCompany.employee_count) }}</p>
                                <p><strong>成立年份:</strong> {{ selectedCompany.founded_year }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 市场份额树图 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">市场份额概览</span>
                </div>
                <div class="card-body">
                    <chart-container
                        v-if="treemapOption"
                        :option="treemapOption">
                    </chart-container>
                    <loading-spinner v-else text="加载市场数据..."></loading-spinner>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            selectedSegment: "all",
            selectedCompanyId: null,
        };
    },

    computed: {
        filteredCompanies() {
            if (this.selectedSegment === "all") return store.companies;
            return store.companies.filter((c) =>
                (c.focus_areas || []).includes(this.selectedSegment)
            );
        },

        selectedCompany() {
            return store.companies.find((c) => c.id === this.selectedCompanyId) || null;
        },

        treemapOption() {
            const data = this.filteredCompanies.map((c) => ({
                name: c.name,
                value: c.revenue_2024_billion_usd || 1,
            }));
            if (data.length === 0) return null;
            return Charts.createTreemapOption(data);
        },
    },

    methods: {
        selectCompany(company) {
            this.selectedCompanyId = company.id;
        },
    },

    setup() {
        return { store, CONSTANTS, format };
    },
};
