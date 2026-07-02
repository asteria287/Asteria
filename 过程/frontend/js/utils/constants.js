/**
 * 常量和配置
 */
const CONSTANTS = {
    // 技术类别
    CATEGORIES: {
        Memory: { label: "存储器", color: "#3b82f6", icon: "💾" },
        Logic: { label: "逻辑芯片", color: "#8b5cf6", icon: "🧠" },
        Packaging: { label: "先进封装", color: "#10b981", icon: "📦" },
        Interconnect: { label: "互连技术", color: "#f59e0b", icon: "🔗" },
        Lithography: { label: "光刻技术", color: "#ef4444", icon: "🔬" },
        Materials: { label: "半导体材料", color: "#ec4899", icon: "🧪" },
    },

    // 投资水平
    INVESTMENT_LEVELS: {
        Leading: { label: "领先", color: "#10b981", level: 4 },
        Active: { label: "活跃", color: "#3b82f6", level: 3 },
        Following: { label: "跟随", color: "#f59e0b", level: 2 },
        Exploring: { label: "探索", color: "#94a3b8", level: 1 },
        None: { label: "无", color: "#374867", level: 0 },
    },

    // 里程碑状态
    STATUS: {
        Achieved: { label: "已完成", color: "#10b981" },
        "In Progress": { label: "进行中", color: "#3b82f6" },
        Planned: { label: "计划中", color: "#f59e0b" },
        Speculative: { label: "预测", color: "#94a3b8" },
    },

    // 关系类型
    RELATION_TYPES: {
        enables: { label: "使能", color: "#10b981" },
        depends_on: { label: "依赖", color: "#f59e0b" },
        competes_with: { label: "竞争", color: "#ef4444" },
        related_to: { label: "相关", color: "#3b82f6" },
    },

    // 公司类型
    COMPANY_TYPES: {
        IDM: "整合器件制造商",
        Foundry: "晶圆代工",
        Fabless: "无晶圆设计",
        OSAT: "封测外包",
        Equipment: "设备供应商",
    },

    // ECharts通用主题
    CHART_COLORS: [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444",
        "#8b5cf6", "#ec4899", "#22d3ee", "#f97316",
        "#84cc16", "#06b6d4", "#a855f7", "#14b8a6",
    ],

    // 年份范围
    YEAR_RANGE: {
        min: 2015,
        max: 2035,
        default: [2020, 2035],
    },
};

window.CONSTANTS = CONSTANTS;
