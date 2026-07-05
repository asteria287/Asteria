"""
LLM-based Knowledge Base Enricher
Uses DeepSeek to structure web search results into KB documents
"""
import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import anthropic
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
KB_DIR = BASE / "knowledge_base"

client = anthropic.Anthropic(
    api_key="sk-f4ef05ea048440dfa9860f89b60d23e4",
    base_url="https://api.deepseek.com/anthropic",
    timeout=300.0,
)

TASKS = [
    {
        "filename": "test_trends_2025.md",
        "title": "半导体测试技术趋势 (2024-2025)",
        "prompt": """你是半导体测试专家。请基于搜索到的行业信息，为PTE新人生成技术趋势知识库章节（中文Markdown，1000-1500字）。

内容要点：
1. 市场背景：2024全球测试设备75-95亿$，2031预计156亿$，CAGR 6.8%
2. AI自适应测试：合肥工大研究减42%测试项，逃逸/良率损失降90%+
3. 先进封装驱动：Chiplet/3D IC/CoWoS推动CP+FT需求暴增，TSV检测、垂直探针阵列
4. 探针技术演进：定位±2μm，针径30μm，112Gbps PAM4，32并行，三温车规-55~175°C
5. 硅光子测试：ficonTEC 300mm双面电光晶圆测试（2025年3月），AI/CPO目标
6. Advantest V93000 EXA Scale：密度8x，功耗-80%，5nm以下
7. SLT平台：AEM AMPS PiXL>2000W，Advantest 7038液冷1.4kW/site，48异步站点
8. 国产替代：华峰测控（模拟60-70%市占）、长川科技（SoC测试机AI芯片验证）、精智达

对每项趋势给出"PTE新人须知"（1-2句实用建议）。表格展示关键数据。"""
    },
    {
        "filename": "test_compare_cp_ft_slt.md",
        "title": "CP/FT/SLT 三大测试环节对比",
        "prompt": """你是半导体测试专家。为PTE新人写CP/FT/SLT对比知识库章节（中文Markdown，800-1000字）。

基于以下信息：
- CP：晶圆裸片测试，秒级，筛制造缺陷80%，Prober+探针卡+ATE，Wafer Map输出KGD
- FT：封装芯片测试，秒-分钟级，成本占比35%，Handler+Socket+Load Board+ATE，STDF输出
- SLT：系统级测试，小时级，成本极高，选择性采用，捕捉系统级交互故障（AI/HPC/车规常用）
- 协作逻辑：CP筛80%坏片→FT确保硬件达标→SLT补足系统级

输出：
1. 对比表格（对象/目的/设备/时间/成本/是否可省略）
2. 典型测试内容每环节展开
3. PTE新人须知：何时建议CP/FT/SLT、成本权衡
4. 行业数据：SLT可额外筛500-2000 DPPM"""
    },
    {
        "filename": "test_equipment_guide.md",
        "title": "测试设备与平台速查",
        "prompt": """你是半导体测试专家。为PTE新人写测试设备速查知识库（中文Markdown，800-1000字）。

基于以下信息：
CP设备：TEL P-12/TSK UF3000(Prober)，V93000/UltraFLEX(ATE)，ficonTEC(硅光子)
FT设备：UltraFLEX/J750(Teradyne)，V93000(Advantest)，Cohu Delta Matrix/Hon M4871(Handler)
SLT设备：AEM AMPS(PiXL>2000W/>320站点)，Advantest 7038(液冷1.4kW/48站点)，Intel Foundry生态
国产设备：华峰测控(模拟测试机60-70%市占)，长川科技(SoC测试机+三温分选机)，精智达(DRAM测试)

输出：
1. 按CP/FT/SLT分类的设备表格（型号/厂商/关键规格/适用芯片类型）
2. 设备选型考虑因素（测试覆盖率、成本、UPH、并行度）
3. PTE新人须知：常见设备缩写、如何快速上手"""
    },
]

def run():
    for task in TASKS:
        print(f"[ENRICH] {task['filename']} ...")
        try:
            resp = client.messages.create(
                model="deepseek-v4-pro[1m]",
                max_tokens=2500,
                temperature=0.3,
                messages=[{"role": "user", "content": task["prompt"]}],
            )
            answer = ""
            for block in resp.content:
                if hasattr(block, "text"):
                    answer += block.text

            if answer:
                output = f"# {task['title']}\n\n> 由 DeepSeek v4 Pro 基于联网搜索结果结构化生成\n\n{answer}"
                (KB_DIR / task["filename"]).write_text(output, encoding="utf-8")
                print(f"  OK: {len(answer)} chars saved")
            else:
                print(f"  WARN: empty response")
            time.sleep(2)  # Rate limit
        except Exception as e:
            print(f"  ERR: {e}")

    print("[ENRICH] Done. Files:")
    for f in KB_DIR.glob("*.md"):
        print(f"  {f.name} ({f.stat().st_size} bytes)")

if __name__ == "__main__":
    run()
