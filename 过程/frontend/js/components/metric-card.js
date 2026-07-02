/**
 * KPI指标卡组件
 */
const MetricCard = {
    props: {
        label: String,
        value: [String, Number],
        change: Object, // { direction: 'up'|'down', text: String }
        icon: String,
    },
    template: `
        <div class="metric-card">
            <div class="flex items-center gap-sm">
                <span v-if="icon" style="font-size:20px;">{{ icon }}</span>
                <span class="metric-label">{{ label }}</span>
            </div>
            <div class="metric-value">{{ value }}</div>
            <div v-if="change" :class="['metric-change', change.direction]">
                <span>{{ change.direction === 'up' ? '↑' : '↓' }}</span>
                <span>{{ change.text }}</span>
            </div>
        </div>
    `,
};
