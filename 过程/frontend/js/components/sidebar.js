/**
 * 侧边栏导航组件
 */
const SidebarComponent = {
    template: `
        <aside :class="['sidebar', { collapsed: store.ui.sidebarCollapsed }]">
            <div class="sidebar-header">
                <div class="logo-icon">🔬</div>
                <span class="logo-text">技术路线图</span>
            </div>
            <nav class="sidebar-nav">
                <div
                    v-for="(route, path) in router.ROUTES"
                    :key="path"
                    :class="['nav-item', { active: router.state.currentRoute === path }]"
                    @click="router.navigate(path)"
                    :title="route.label"
                >
                    <span class="nav-icon">{{ route.icon }}</span>
                    <span class="nav-label">{{ route.label }}</span>
                </div>
            </nav>
            <div class="sidebar-footer" style="padding:12px;border-top:1px solid var(--color-border);">
                <div v-if="!store.ui.sidebarCollapsed" class="text-muted" style="font-size:11px;">
                    v1.0 · 半导体技术路线图
                </div>
            </div>
        </aside>
    `,
    setup() {
        return { store, router: window.router };
    },
};
