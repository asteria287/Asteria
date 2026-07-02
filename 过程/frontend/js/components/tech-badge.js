/**
 * 技术类别徽章
 */
const TechBadge = {
    props: {
        category: String,
        label: String,
    },
    template: `
        <span :class="['badge', 'badge-' + (category || '').toLowerCase()]">
            {{ label || format.categoryLabel(category) }}
        </span>
    `,
    setup() {
        return { format };
    },
};
