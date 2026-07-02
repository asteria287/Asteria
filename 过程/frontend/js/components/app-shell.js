/**
 * AppShell - 主布局组件
 * 包含侧边栏、头部和页面内容区域
 */
const AppShell = {
    template: `
        <div class="flex" style="width:100vw;height:100vh;">
            <sidebar-component></sidebar-component>
            <div class="main-content">
                <header class="header">
                    <button class="btn btn-sm" @click="store.toggleSidebar()" title="折叠侧边栏">
                        ☰
                    </button>
                    <div class="flex-1">
                        <div class="header-title">{{ router.state.currentLabel }}</div>
                        <div class="header-breadcrumb">
                            研发技术路线图 / {{ router.state.currentLabel }}
                        </div>
                    </div>
                    <div class="flex items-center gap-sm">
                        <span v-if="store.ui.loading" class="text-muted text-sm">加载中...</span>
                        <span class="badge badge-info">{{ store.technologies.length }} 技术</span>
                        <span class="badge badge-success">{{ store.companies.length }} 公司</span>
                    </div>
                </header>
                <main class="page-content">
                    <error-banner
                        v-if="store.ui.currentError"
                        :message="store.ui.currentError"
                        @close="store.clearError()">
                    </error-banner>
                    <component :is="router.state.currentComponent"></component>
                </main>
            </div>
            <!-- 详情面板 -->
            <div v-if="store.ui.detailPanelVisible" class="backdrop" @click="store.closeDetailPanel()"></div>
        </div>
    `,
    setup() {
        return { store, router: window.router };
    },
};
