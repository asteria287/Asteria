/**
 * AI智能分析助手 - 流式对话界面
 */
const AIAssistantPage = {
    template: `
        <div class="animate-fade-in">
            <div class="grid-2" style="gap:24px;">
                <!-- 对话区域 -->
                <div class="card" style="display:flex;flex-direction:column;">
                    <div class="card-header">
                        <span class="card-title">🤖 AI技术分析助手</span>
                        <span v-if="currentSession" class="badge badge-info">会话: {{ currentSession }}</span>
                    </div>

                    <!-- 消息列表 -->
                    <div class="chat-messages" ref="chatMessages" style="min-height:400px;max-height:500px;">
                        <div v-if="messages.length === 0" style="text-align:center;padding:40px;color:var(--color-text-muted);">
                            <div style="font-size:48px;margin-bottom:16px;">🤖</div>
                            <h3>半导体技术路线图智能分析助手</h3>
                            <p style="margin-top:8px;">我可以帮你分析:</p>
                            <ul style="text-align:left;display:inline-block;margin-top:8px;">
                                <li>前沿技术深度分析 (3D DRAM, PIM, HBM, CXL...)</li>
                                <li>技术发展趋势预测</li>
                                <li>竞争格局对比</li>
                                <li>专利和论文趋势解读</li>
                            </ul>
                        </div>
                        <div v-for="(msg, idx) in messages" :key="idx"
                             :class="['chat-message', msg.role]">
                            <div v-if="msg.role === 'assistant'" v-html="renderMarkdown(msg.content)"></div>
                            <div v-else>{{ msg.content }}</div>
                            <div v-if="msg.streaming" class="text-muted" style="font-size:11px;margin-top:4px;">
                                <span class="spinner" style="width:12px;height:12px;display:inline-block;margin-right:4px;"></span>
                                分析中...
                            </div>
                        </div>
                    </div>

                    <!-- 输入区域 -->
                    <div class="chat-input-area">
                        <input
                            v-model="userInput"
                            placeholder="输入技术分析问题，例如: 3D DRAM的技术挑战有哪些？"
                            @keydown.enter="sendMessage"
                            :disabled="isStreaming"
                        >
                        <button class="btn btn-primary" @click="sendMessage" :disabled="isStreaming || !userInput.trim()">
                            发送
                        </button>
                    </div>
                </div>

                <!-- 快速分析面板 -->
                <div>
                    <h3 style="margin-bottom:16px;">快速分析</h3>
                    <div style="display:flex;flex-direction:column;gap:12px;">
                        <div v-for="template in quickTemplates" :key="template.title"
                             class="card" style="cursor:pointer;padding:16px;"
                             @click="runTemplate(template)">
                            <div style="font-weight:600;margin-bottom:4px;">{{ template.title }}</div>
                            <div class="text-muted text-sm">{{ template.desc }}</div>
                            <div class="flex gap-sm" style="margin-top:8px;">
                                <span v-for="tag in template.tags" :key="tag" class="badge badge-info">{{ tag }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- 关联技术上下文 -->
                    <div class="card" style="margin-top:16px;padding:16px;">
                        <h4 style="margin-bottom:8px;">技术上下文</h4>
                        <p class="text-muted text-sm">选择相关技术以增强分析精度:</p>
                        <div class="flex gap-sm" style="margin-top:8px;flex-wrap:wrap;">
                            <span v-for="t in store.technologies.slice(0, 8)" :key="t.id"
                                  :class="['badge', contextTechIds.includes(t.id) ? 'badge-success' : 'badge-info']"
                                  style="cursor:pointer;"
                                  @click="toggleContextTech(t.id)">
                                {{ t.name }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            messages: [],
            userInput: "",
            isStreaming: false,
            currentSession: null,
            contextTechIds: [],
            quickTemplates: [
                {
                    title: "HBM技术深度分析",
                    desc: "分析HBM4的技术现状、关键挑战和发展前景",
                    tags: ["HBM", "存储器"],
                    prompt: "请对HBM (High Bandwidth Memory) 技术进行深度分析，包括: 1) HBM4最新技术规格和路线图; 2) 关键挑战(散热、堆叠层数、成本); 3) 主要竞争者对比(Samsung/SK Hynix/Micron); 4) 未来3-5年发展趋势",
                },
                {
                    title: "3D DRAM可行性评估",
                    desc: "评估3D DRAM技术的商业化前景和时间线",
                    tags: ["3D DRAM", "存储器"],
                    prompt: "请对3D DRAM技术进行全面评估: 1) 当前技术状态(各家方案对比); 2) 关键工艺挑战(刻蚀、沉积、 bonding); 3) 与HBM的技术路线竞争关系; 4) 预期量产时间线和市场规模预测",
                },
                {
                    title: "PIM技术竞争格局",
                    desc: "Processing in Memory技术路线对比分析",
                    tags: ["PIM", "存内计算"],
                    prompt: "请分析PIM (Processing in Memory) 技术的竞争格局: 1) 主要技术路线(Functional PIM vs Near-memory Computing); 2) 各家公司方案对比(Samsung HBM-PIM, SK Hynix AiM, 学术界); 3) 关键应用场景(AI加速、图计算); 4) 产业生态建设进展",
                },
                {
                    title: "先进封装技术对比",
                    desc: "CoWoS/HBM/EMIB/混合键合技术对比",
                    tags: ["先进封装", "Chiplet"],
                    prompt: "请对比分析主流先进封装技术: 1) TSMC CoWoS/InFO/SoIC; 2) Intel EMIB/Foveros; 3) Samsung I-Cube/X-Cube; 4) 混合键合(Hybrid Bonding)技术进展; 5) 与Chiplet生态的关系",
                },
                {
                    title: "CXL生态系统分析",
                    desc: "Compute Express Link技术生态和标准化进展",
                    tags: ["CXL", "互连"],
                    prompt: "请分析CXL (Compute Express Link) 技术生态: 1) CXL 1.1/2.0/3.0规范演进; 2) 主要参与者(Astera Labs, Marvell, Samsung, SK Hynix, Intel); 3) CXL内存池化和共享方案; 4) 与UCIe/PCIe的竞合关系; 5) 数据中心应用前景",
                },
            ],
        };
    },

    methods: {
        async sendMessage() {
            const text = this.userInput.trim();
            if (!text || this.isStreaming) return;

            this.messages.push({ role: "user", content: text });
            this.userInput = "";

            // 添加AI回复占位
            const aiMsg = { role: "assistant", content: "", streaming: true };
            this.messages.push(aiMsg);

            this.isStreaming = true;
            this.scrollToBottom();

            try {
                // 尝试SSE流式调用
                const response = await api.aiQA(
                    text,
                    this.currentSession,
                    this.contextTechIds
                );

                if (response && response.body) {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value);
                        const lines = chunk.split("\n");
                        for (const line of lines) {
                            if (line.startsWith("data: ")) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    if (data.content) {
                                        aiMsg.content += data.content;
                                    }
                                    if (data.session_id) {
                                        this.currentSession = data.session_id;
                                    }
                                } catch (e) {
                                    // 纯文本delta
                                    aiMsg.content += line.slice(6);
                                }
                            }
                        }
                    }
                }
            } catch (e) {
                // 降级为非流式响应
                aiMsg.content = `关于 "${text}" 的分析:\n\nAI分析服务需要配置Anthropic API Key。请在项目根目录创建 .env 文件并设置 ANTHROPIC_API_KEY。\n\n当前系统支持以下分析模式:\n- 技术深度分析\n- 路线图预测\n- 竞争格局总结\n- 技术趋势问答`;
            }

            aiMsg.streaming = false;
            this.isStreaming = false;
            this.scrollToBottom();
        },

        runTemplate(template) {
            this.userInput = template.prompt;
            this.sendMessage();
        },

        toggleContextTech(id) {
            const idx = this.contextTechIds.indexOf(id);
            if (idx >= 0) {
                this.contextTechIds.splice(idx, 1);
            } else {
                this.contextTechIds.push(id);
            }
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const el = this.$refs.chatMessages;
                if (el) {
                    el.scrollTop = el.scrollHeight;
                }
            });
        },

        renderMarkdown(text) {
            if (!text) return "";
            // 简易Markdown渲染
            return text
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                .replace(/\*(.*?)\*/g, "<em>$1</em>")
                .replace(/`(.*?)`/g, "<code>$1</code>")
                .replace(/\n/g, "<br>")
                .replace(/^- (.*)/gm, "<li>$1</li>");
        },
    },

    mounted() {
        this.currentSession = "session_" + Date.now();
        // 从URL参数获取技术上下文
        if (router.state.params.tech) {
            this.contextTechIds.push(parseInt(router.state.params.tech));
        }
    },

    setup() {
        return { store, router: window.router, api };
    },
};
