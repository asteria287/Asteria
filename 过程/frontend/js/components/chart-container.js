/**
 * ECharts容器组件 - 自动处理初始化和resize
 */
const ChartContainer = {
    props: {
        option: Object,
        large: Boolean,
        notMerge: Boolean,
    },
    template: `
        <div :class="['chart-container', { large: large }]" ref="chartDom"></div>
    `,
    data() {
        return { chart: null, resizeObserver: null };
    },
    mounted() {
        this.initChart();
        this.resizeObserver = new ResizeObserver(() => {
            this.chart?.resize();
        });
        this.resizeObserver.observe(this.$refs.chartDom);
    },
    beforeUnmount() {
        this.resizeObserver?.disconnect();
        this.chart?.dispose();
    },
    methods: {
        initChart() {
            if (!this.$refs.chartDom || !this.option) return;
            this.chart = echarts.init(this.$refs.chartDom);
            this.chart.setOption(this.option, this.notMerge);
            this.chart.on("click", (params) => {
                this.$emit("chartClick", params);
            });
        },
        setOption(option, notMerge) {
            if (this.chart && option) {
                this.chart.setOption(option, notMerge);
            }
        },
    },
    watch: {
        option: {
            handler(newOpt) {
                this.setOption(newOpt, this.notMerge);
            },
            deep: true,
        },
    },
};
