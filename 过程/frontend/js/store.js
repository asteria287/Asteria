/**
 * 全局状态管理 - 基于Vue 3 reactive
 */
const store = Vue.reactive({
    // 数据
    technologies: [],
    companies: [],
    roadmapMilestones: [],

    // 当前选中
    selectedTechId: null,
    selectedCompanyId: null,

    // 筛选器
    filters: {
        category: null,
        yearRange: [2020, 2035],
        companyIds: [],
        techIds: [],
        status: null,
    },

    // UI状态
    ui: {
        sidebarCollapsed: false,
        loading: false,
        currentError: null,
        detailPanelVisible: false,
        detailPanelData: null,
    },

    // 计算
    get selectedTech() {
        return this.technologies.find((t) => t.id === this.selectedTechId) || null;
    },
    get selectedCompany() {
        return this.companies.find((c) => c.id === this.selectedCompanyId) || null;
    },
    get techCategories() {
        const cats = new Set(this.technologies.map((t) => t.category));
        return [...cats].sort();
    },

    // 方法
    setLoading(loading) {
        this.ui.loading = loading;
    },
    setError(error) {
        this.ui.currentError = error;
    },
    clearError() {
        this.ui.currentError = null;
    },
    selectTech(id) {
        this.selectedTechId = id;
    },
    selectCompany(id) {
        this.selectedCompanyId = id;
    },
    toggleSidebar() {
        this.ui.sidebarCollapsed = !this.ui.sidebarCollapsed;
    },
    openDetailPanel(data) {
        this.ui.detailPanelData = data;
        this.ui.detailPanelVisible = true;
    },
    closeDetailPanel() {
        this.ui.detailPanelVisible = false;
        this.ui.detailPanelData = null;
    },
    setFilter(key, value) {
        this.filters[key] = value;
    },
    resetFilters() {
        this.filters = {
            category: null,
            yearRange: [2020, 2035],
            companyIds: [],
            techIds: [],
            status: null,
        };
    },
});

window.store = store;
