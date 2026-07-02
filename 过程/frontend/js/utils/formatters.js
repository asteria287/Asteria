/**
 * 格式化工具函数
 */
const format = {
    number(n) {
        if (n === null || n === undefined) return "-";
        if (n >= 1e9) return (n / 1e9).toFixed(1) + "B";
        if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
        if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
        return n.toLocaleString();
    },

    currency(billions) {
        if (billions === null || billions === undefined) return "-";
        return `$${billions.toFixed(1)}B`;
    },

    percent(value) {
        if (value === null || value === undefined) return "-";
        return `${value.toFixed(1)}%`;
    },

    year(value) {
        if (!value) return "-";
        return String(value);
    },

    date(dateStr) {
        if (!dateStr) return "-";
        const d = new Date(dateStr);
        return d.toLocaleDateString("zh-CN", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
        });
    },

    truncated(str, maxLen = 100) {
        if (!str) return "";
        if (str.length <= maxLen) return str;
        return str.slice(0, maxLen) + "...";
    },

    maturityLevel(level) {
        const labels = {
            1: "基础研究",
            2: "应用研究",
            3: "概念验证",
            4: "实验室验证",
            5: "原型验证",
            6: "工程样机",
            7: "小批量产",
            8: "规模量产",
            9: "成熟商用",
        };
        return labels[level] || `TRL ${level}`;
    },

    investmentLabel(level) {
        return CONSTANTS.INVESTMENT_LEVELS[level]?.label || level;
    },

    categoryLabel(cat) {
        return CONSTANTS.CATEGORIES[cat]?.label || cat;
    },

    statusLabel(status) {
        return CONSTANTS.STATUS[status]?.label || status;
    },
};

window.format = format;
