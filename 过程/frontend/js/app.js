/**
 * Vue应用入口
 * 注册全局组件、创建Vue实例
 */
import "./utils/constants.js";
import "./utils/formatters.js";
import "./utils/charts.js";
import "./router.js";
import "./store.js";
import "./api.js";

// 导入组件
import "./components/app-shell.js";
import "./components/sidebar.js";
import "./components/metric-card.js";
import "./components/chart-container.js";
import "./components/loading-spinner.js";
import "./components/error-banner.js";
import "./components/tech-badge.js";

// 导入页面
import "./pages/dashboard-page.js";
import "./pages/landscape-page.js";
import "./pages/competitive-page.js";
import "./pages/roadmap-page.js";
import "./pages/patent-page.js";
import "./pages/ai-assistant-page.js";

// 创建Vue应用
const app = Vue.createApp({});

// 注册全局组件
app.component("app-shell", AppShell);
app.component("sidebar-component", SidebarComponent);
app.component("metric-card", MetricCard);
app.component("chart-container", ChartContainer);
app.component("loading-spinner", LoadingSpinner);
app.component("error-banner", ErrorBanner);
app.component("tech-badge", TechBadge);

app.component("dashboard-page", DashboardPage);
app.component("landscape-page", LandscapePage);
app.component("competitive-page", CompetitivePage);
app.component("roadmap-page", RoadmapPage);
app.component("patent-page", PatentPage);
app.component("ai-assistant-page", AIAssistantPage);

// 挂载
app.mount("#app");

// 初始化加载数据
(async function initData() {
    try {
        // 加载技术数据
        const techResp = await api.getTechnologies();
        if (techResp?.success) {
            store.technologies = techResp.data || [];
        }

        // 加载公司数据
        const compResp = await api.getCompanies();
        if (compResp?.success) {
            store.companies = compResp.data || [];
        }
    } catch (e) {
        console.warn("初始数据加载失败，将在API就绪后重试:", e.message);
    }
})();
