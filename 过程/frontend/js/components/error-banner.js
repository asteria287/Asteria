/**
 * 错误提示组件
 */
const ErrorBanner = {
    props: {
        message: String,
        closable: { type: Boolean, default: true },
    },
    emits: ["close"],
    template: `
        <div class="error-banner animate-fade-in" style="margin-bottom:16px;">
            <span>⚠️</span>
            <span style="flex:1;">{{ message }}</span>
            <button v-if="closable" class="btn btn-sm" @click="$emit('close')" style="color:#fca5a5;">✕</button>
        </div>
    `,
};
