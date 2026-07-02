/**
 * 加载动画组件
 */
const LoadingSpinner = {
    props: {
        text: { type: String, default: "加载中..." },
    },
    template: `
        <div class="loading-spinner">
            <div style="text-align:center;">
                <div class="spinner" style="margin:0 auto 12px;"></div>
                <div class="text-muted text-sm">{{ text }}</div>
            </div>
        </div>
    `,
};
