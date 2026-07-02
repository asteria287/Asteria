/**
 * API请求封装
 */
const API_BASE = "/api";

async function apiRequest(path, options = {}) {
    const url = `${API_BASE}${path}`;
    const config = {
        headers: {
            "Content-Type": "application/json",
        },
        ...options,
    };

    try {
        store.setLoading(true);
        store.clearError();

        const response = await fetch(url, config);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const message = errorData.error?.message || `HTTP ${response.status}`;
            throw new Error(message);
        }

        // SSE流式响应不解析JSON
        if (options.stream) {
            store.setLoading(false);
            return response;
        }

        const data = await response.json();
        store.setLoading(false);
        return data;
    } catch (error) {
        store.setLoading(false);
        if (error.name !== "AbortError") {
            store.setError(error.message);
        }
        throw error;
    }
}

const api = {
    // 技术
    getTechnologies(params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/technologies/${query ? `?${query}` : ""}`);
    },
    getTechnology(id) {
        return apiRequest(`/technologies/${id}`);
    },
    getTechnologyLandscape(id) {
        return apiRequest(`/technologies/${id}/landscape`);
    },
    getTechnologyOverview() {
        return apiRequest("/technologies/overview");
    },
    getTechnologyRadar() {
        return apiRequest("/technologies/radar");
    },

    // 竞争格局
    getCompanies(params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/competitive/companies${query ? `?${query}` : ""}`);
    },
    getCompany(id) {
        return apiRequest(`/competitive/companies/${id}`);
    },
    getComparison(techIds) {
        const query = techIds.map((id) => `tech_ids=${id}`).join("&");
        return apiRequest(`/competitive/comparison?${query}`);
    },
    getMarketShare() {
        return apiRequest("/competitive/market-share");
    },
    getHeatmap() {
        return apiRequest("/competitive/heatmap");
    },

    // 路线图
    getTimeline(params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/roadmap/timeline${query ? `?${query}` : ""}`);
    },
    getRoadmapByTech(techId) {
        return apiRequest(`/roadmap/technology/${techId}`);
    },
    getGapAnalysis() {
        return apiRequest("/roadmap/gap-analysis");
    },
    getRoadmapStats() {
        return apiRequest("/roadmap/stats");
    },

    // 专利与论文
    getPatentTrends(params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/patents/trends${query ? `?${query}` : ""}`);
    },
    getTopAssignees() {
        return apiRequest("/patents/top-assignees");
    },
    getGeographicDistribution() {
        return apiRequest("/patents/geographic");
    },
    searchPatents(query) {
        return apiRequest(`/patents/search?q=${encodeURIComponent(query)}`);
    },
    getPaperTrends(params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/papers/trends${query ? `?${query}` : ""}`);
    },

    // AI分析
    analyzeTechnology(technologyName, aspects) {
        return apiRequest("/ai/analyze", {
            method: "POST",
            body: JSON.stringify({ technology_name: technologyName, aspects }),
        });
    },
    aiQA(question, sessionId, contextTechIds) {
        return apiRequest("/ai/qa", {
            method: "POST",
            body: JSON.stringify({
                question,
                session_id: sessionId,
                context_tech_ids: contextTechIds || [],
            }),
            stream: true,
        });
    },
    predictRoadmap(technologyId, horizonYears) {
        return apiRequest("/ai/roadmap-predict", {
            method: "POST",
            body: JSON.stringify({ technology_id: technologyId, horizon_years: horizonYears }),
        });
    },
    competitiveSummary(technologyId) {
        return apiRequest("/ai/competitive-summary", {
            method: "POST",
            body: JSON.stringify({ technology_id: technologyId }),
        });
    },
    getChatHistory(sessionId) {
        return apiRequest(`/ai/chat-history/${sessionId}`);
    },
};

window.api = api;
