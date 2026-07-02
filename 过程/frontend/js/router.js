/**
 * 哈希路由 - 基于Vue 3响应式的SPA路由
 */
const ROUTES = {
    "/dashboard": {
        component: "dashboard-page",
        label: "首页总览",
        icon: "📊",
    },
    "/landscape": {
        component: "landscape-page",
        label: "技术全景",
        icon: "🔬",
    },
    "/competitive": {
        component: "competitive-page",
        label: "竞争格局",
        icon: "🏢",
    },
    "/roadmap": {
        component: "roadmap-page",
        label: "技术路线图",
        icon: "🗺️",
    },
    "/patents": {
        component: "patent-page",
        label: "专利与论文",
        icon: "📄",
    },
    "/ai-assistant": {
        component: "ai-assistant-page",
        label: "AI智能分析",
        icon: "🤖",
    },
};

const DEFAULT_ROUTE = "/dashboard";

// 创建全局路由状态
const routerState = Vue.reactive({
    currentRoute: DEFAULT_ROUTE,
    currentComponent: ROUTES[DEFAULT_ROUTE].component,
    currentLabel: ROUTES[DEFAULT_ROUTE].label,
    params: {},
});

function getRouteFromHash() {
    const hash = window.location.hash.slice(1) || DEFAULT_ROUTE;
    // 检查路由是否存在
    const baseRoute = hash.split("?")[0];
    if (!ROUTES[baseRoute]) {
        return DEFAULT_ROUTE;
    }
    return hash;
}

function parseParams(hash) {
    const [route, queryString] = hash.split("?");
    const params = {};
    if (queryString) {
        queryString.split("&").forEach((pair) => {
            const [key, value] = pair.split("=");
            if (key) params[decodeURIComponent(key)] = decodeURIComponent(value || "");
        });
    }
    return { route, params };
}

function navigate(route, params = {}) {
    const queryParts = Object.entries(params)
        .filter(([, v]) => v !== null && v !== undefined)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
    const hash = queryParts.length > 0 ? `${route}?${queryParts.join("&")}` : route;
    window.location.hash = hash;
}

function updateRoute() {
    const hash = getRouteFromHash();
    const { route, params } = parseParams(hash);
    const routeConfig = ROUTES[route];

    if (routeConfig) {
        routerState.currentRoute = route;
        routerState.currentComponent = routeConfig.component;
        routerState.currentLabel = routeConfig.label;
        routerState.params = params;
    }
}

// 监听hash变化
window.addEventListener("hashchange", updateRoute);
window.addEventListener("load", updateRoute);

// 暴露到全局
window.router = { navigate, ROUTES, state: routerState };
