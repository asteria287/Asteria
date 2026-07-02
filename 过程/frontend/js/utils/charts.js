/**
 * ECharts图表配置工厂函数
 * 每个函数接收数据，返回完整的ECharts option对象
 */
const Charts = {
    /**
     * 通用暗色主题基础配置
     */
    baseOption() {
        return {
            backgroundColor: "transparent",
            textStyle: { color: "#a0b4cc" },
            tooltip: {
                backgroundColor: "rgba(17, 24, 39, 0.95)",
                borderColor: "#2a3a52",
                textStyle: { color: "#e8edf5", fontSize: 13 },
            },
        };
    },

    /**
     * 技术雷达图
     * @param {Array} indicators - [{name, max}] 雷达轴
     * @param {Array} series - [{name, value: []] 数据系列
     */
    createRadarOption(indicators, series) {
        const base = this.baseOption();
        return {
            ...base,
            radar: {
                indicator: indicators,
                center: ["50%", "55%"],
                radius: "65%",
                axisName: { color: "#a0b4cc", fontSize: 12 },
                splitArea: {
                    areaStyle: {
                        color: ["rgba(59, 130, 246, 0.05)", "rgba(59, 130, 246, 0.1)"],
                    },
                },
                splitLine: { lineStyle: { color: "#2a3a52" } },
                axisLine: { lineStyle: { color: "#2a3a52" } },
            },
            series: [
                {
                    type: "radar",
                    data: series.map((s) => ({
                        name: s.name,
                        value: s.value,
                        areaStyle: { opacity: 0.15 },
                        lineStyle: { width: 2 },
                        symbol: "circle",
                        symbolSize: 4,
                    })),
                    emphasis: {
                        lineStyle: { width: 3 },
                    },
                },
            ],
            legend: {
                bottom: 10,
                textStyle: { color: "#a0b4cc" },
            },
        };
    },

    /**
     * 力导向图 - 技术全景
     * @param {Array} nodes - [{id, name, category, symbolSize}]
     * @param {Array} edges - [{source, target, relation_type}]
     * @param {Object} categories - [{name}] 用于图例
     */
    createForceGraphOption(nodes, edges, categories) {
        const base = this.baseOption();
        return {
            ...base,
            legend: {
                data: categories.map((c) => c.name),
                bottom: 10,
                textStyle: { color: "#a0b4cc" },
            },
            series: [
                {
                    type: "graph",
                    layout: "force",
                    roam: true,
                    draggable: true,
                    categories: categories,
                    data: nodes.map((n) => ({
                        ...n,
                        label: {
                            show: true,
                            position: "right",
                            fontSize: 12,
                            color: "#e8edf5",
                        },
                    })),
                    links: edges.map((e) => ({
                        source: e.source,
                        target: e.target,
                        lineStyle: {
                            color: CONSTANTS.RELATION_TYPES[e.relation_type]?.color || "#374867",
                            width: e.strength || 1,
                            curveness: 0.2,
                            opacity: 0.6,
                        },
                    })),
                    force: {
                        repulsion: 500,
                        gravity: 0.1,
                        edgeLength: [150, 300],
                        layoutAnimation: true,
                    },
                    emphasis: {
                        focus: "adjacency",
                        lineStyle: { width: 3 },
                    },
                },
            ],
        };
    },

    /**
     * 热力图 - 公司×技术矩阵
     * @param {Array} xLabels - 技术名称 (列)
     * @param {Array} yLabels - 公司名称 (行)
     * @param {Array} data - [[xIdx, yIdx, value]]
     */
    createHeatmapOption(xLabels, yLabels, data) {
        const base = this.baseOption();
        return {
            ...base,
            xAxis: {
                type: "category",
                data: xLabels,
                axisLabel: { color: "#a0b4cc", rotate: 45, fontSize: 11 },
                axisLine: { lineStyle: { color: "#2a3a52" } },
            },
            yAxis: {
                type: "category",
                data: yLabels,
                axisLabel: { color: "#a0b4cc", fontSize: 12 },
                axisLine: { lineStyle: { color: "#2a3a52" } },
            },
            visualMap: {
                min: 0,
                max: 4,
                categories: ["无", "探索", "跟随", "活跃", "领先"],
                inRange: { color: ["#374867", "#94a3b8", "#f59e0b", "#3b82f6", "#10b981"] },
                bottom: 10,
                textStyle: { color: "#a0b4cc" },
            },
            series: [
                {
                    type: "heatmap",
                    data: data,
                    label: { show: false },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: "rgba(0,0,0,0.5)",
                        },
                    },
                },
            ],
        };
    },

    /**
     * 甘特图时间线 - 路线图
     * @param {Array} data - [{name, milestones: [{year, milestone, status, company}]}]
     */
    createTimelineOption(data, yearRange) {
        const base = this.baseOption();
        const [yearStart, yearEnd] = yearRange;

        // 构建系列数据
        const categories = data.map((d) => d.name).reverse();
        const seriesData = [];

        data.forEach((item, rowIdx) => {
            (item.milestones || []).forEach((m) => {
                seriesData.push({
                    name: item.name,
                    value: [rowIdx, m.year, m.year + 0.8, m.milestone],
                    itemStyle: {
                        color: CONSTANTS.STATUS[m.status]?.color || "#3b82f6",
                        borderColor: m.is_ai_generated ? "#f59e0b" : undefined,
                        borderWidth: m.is_ai_generated ? 2 : 0,
                        borderType: m.is_ai_generated ? "dashed" : "solid",
                    },
                    milestone: m,
                });
            });
        });

        return {
            ...base,
            tooltip: {
                ...base.tooltip,
                formatter(params) {
                    const m = params.data?.milestone;
                    if (!m) return "";
                    const confStr = m.confidence
                        ? `<br/>AI置信度: ${(m.confidence * 100).toFixed(0)}%`
                        : "";
                    return `
                        <strong>${m.milestone}</strong><br/>
                        年份: ${m.year}${m.quarter ? " " + m.quarter : ""}<br/>
                        状态: ${format.statusLabel(m.status)}<br/>
                        公司: ${m.company || "行业整体"}${confStr}
                    `;
                },
            },
            grid: { left: 200, right: 40, top: 20, bottom: 40 },
            xAxis: {
                type: "value",
                min: yearStart,
                max: yearEnd,
                interval: 1,
                axisLabel: { color: "#a0b4cc" },
                axisLine: { lineStyle: { color: "#2a3a52" } },
                splitLine: { lineStyle: { color: "#1e2d42" } },
            },
            yAxis: {
                type: "category",
                data: categories,
                axisLabel: { color: "#e8edf5", fontSize: 12 },
                axisLine: { lineStyle: { color: "#2a3a52" } },
            },
            series: [
                {
                    type: "custom",
                    renderItem(params, api) {
                        const yIdx = api.value(0);
                        const start = api.coord([api.value(1), yIdx]);
                        const end = api.coord([api.value(2), yIdx]);
                        const height = api.size([0, 1])[1] * 0.6;
                        return {
                            type: "rect",
                            shape: {
                                x: start[0],
                                y: start[1] - height / 2,
                                width: Math.max(end[0] - start[0], 4),
                                height: height,
                                r: 4,
                            },
                            style: api.style(),
                        };
                    },
                    encode: { x: [1, 2], y: 0 },
                    data: seriesData,
                },
            ],
        };
    },

    /**
     * 趋势折线图 - 专利/论文
     * @param {Array} xData - 年份
     * @param {Array} series - [{name, data: []}]
     */
    createTrendLineOption(xData, series) {
        const base = this.baseOption();
        return {
            ...base,
            xAxis: {
                type: "category",
                data: xData,
                axisLabel: { color: "#a0b4cc" },
                axisLine: { lineStyle: { color: "#2a3a52" } },
            },
            yAxis: {
                type: "value",
                axisLabel: { color: "#a0b4cc" },
                splitLine: { lineStyle: { color: "#1e2d42" } },
            },
            series: series.map((s, i) => ({
                name: s.name,
                type: "line",
                data: s.data,
                smooth: true,
                symbol: "circle",
                symbolSize: 6,
                lineStyle: { width: 2 },
                areaStyle: { opacity: 0.1 },
                color: CONSTANTS.CHART_COLORS[i % CONSTANTS.CHART_COLORS.length],
            })),
            legend: {
                bottom: 10,
                textStyle: { color: "#a0b4cc" },
            },
        };
    },

    /**
     * 柱状图 - Top N排名
     */
    createBarOption(labels, values, horizontal = false) {
        const base = this.baseOption();
        const color = CONSTANTS.CHART_COLORS[0];
        return {
            ...base,
            [horizontal ? "yAxis" : "xAxis"]: {
                type: "category",
                data: labels,
                axisLabel: { color: "#a0b4cc" },
                axisLine: { lineStyle: { color: "#2a3a52" } },
            },
            [horizontal ? "xAxis" : "yAxis"]: {
                type: "value",
                axisLabel: { color: "#a0b4cc" },
                splitLine: { lineStyle: { color: "#1e2d42" } },
            },
            series: [
                {
                    type: "bar",
                    data: values,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, horizontal ? 1 : 0, 0, [
                            { offset: 0, color: CONSTANTS.CHART_COLORS[0] },
                            { offset: 1, color: CONSTANTS.CHART_COLORS[1] },
                        ]),
                        borderRadius: 4,
                    },
                },
            ],
        };
    },

    /**
     * 矩形树图 - 市场份额
     */
    createTreemapOption(data) {
        const base = this.baseOption();
        return {
            ...base,
            series: [
                {
                    type: "treemap",
                    data: data,
                    width: "100%",
                    height: "100%",
                    roam: false,
                    label: {
                        show: true,
                        formatter: "{b}\n{c}",
                        fontSize: 12,
                        color: "#fff",
                    },
                    itemStyle: {
                        borderColor: "#0a0e17",
                        borderWidth: 2,
                    },
                    levels: [
                        { itemStyle: { gapWidth: 2 } },
                        { colorSaturation: [0.3, 0.6] },
                    ],
                },
            ],
        };
    },

    /**
     * 气泡图 - 技术共现
     */
    createBubbleOption(data) {
        const base = this.baseOption();
        return {
            ...base,
            xAxis: {
                type: "value",
                axisLabel: { color: "#a0b4cc" },
                splitLine: { lineStyle: { color: "#1e2d42" } },
            },
            yAxis: {
                type: "value",
                axisLabel: { color: "#a0b4cc" },
                splitLine: { lineStyle: { color: "#1e2d42" } },
            },
            series: [
                {
                    type: "scatter",
                    data: data,
                    symbolSize: (val) => Math.sqrt(val[2]) * 3,
                    itemStyle: { opacity: 0.7 },
                    emphasis: {
                        scale: 1.5,
                    },
                },
            ],
        };
    },

    /**
     * 饼图
     */
    createPieOption(data, nameField = "name", valueField = "value") {
        const base = this.baseOption();
        return {
            ...base,
            series: [
                {
                    type: "pie",
                    radius: ["40%", "70%"],
                    center: ["50%", "50%"],
                    data: data.map((d) => ({
                        name: d[nameField],
                        value: d[valueField],
                    })),
                    label: { color: "#a0b4cc" },
                    emphasis: {
                        scaleSize: 10,
                        label: { fontSize: 16, fontWeight: "bold" },
                    },
                },
            ],
        };
    },
};

window.Charts = Charts;
