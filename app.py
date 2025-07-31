import streamlit as st
import openai
import os
import plotly.graph_objects as go
import os
import streamlit as st
import openai

# ========== API Key 检查器 ==========
# 兼容 环境变量 / secrets.toml
openai_api_key = (
    os.getenv("OPENAI_API_KEY")
    or st.secrets.get("OPENAI_API_KEY")
    or st.secrets.get("general", {}).get("OPENAI_API_KEY")
)

st.subheader("🔑 API Key 检查器")

if not openai_api_key:
    st.error("""
    ❌ 未检测到 OpenAI API Key。
    解决方法：
    1. 本地环境变量设置：
       - macOS / Linux: export OPENAI_API_KEY="sk-xxxx"
       - Windows PowerShell: setx OPENAI_API_KEY "sk-xxxx"
    2. 或者在 .streamlit/secrets.toml 中配置：
       [general]
       OPENAI_API_KEY = "sk-xxxx"
    """)
    st.stop()

openai.api_key = openai_api_key

# 显示 Key 前 5 位进行确认
st.success(f"✅ 已检测到 API Key: {openai_api_key[:5]}***")

# 验证 Key 是否有效
with st.spinner("正在验证 API Key..."):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "测试API Key是否可用，仅回答：OK"}],
            max_tokens=5,
        )
        st.success(f"API Key 验证成功，模型回复：{response.choices[0].message.content}")
    except Exception as e:
        st.error(f"❌ API Key 验证失败：{e}")
        st.stop()

# ========== API Key ==========
openai_api_key = (
    os.getenv("OPENAI_API_KEY")
    or st.secrets.get("OPENAI_API_KEY")
    or st.secrets.get("general", {}).get("OPENAI_API_KEY")
)

if not openai_api_key:
    st.error("❌ 未检测到 OpenAI API Key，请在环境变量或 .streamlit/secrets.toml 中配置。")
    st.stop()
st.write(os.getenv("OPENAI_API_KEY"))
openai.api_key = openai_api_key

# ========== 页面设置 ==========
st.set_page_config(page_title="性激素六项评估工具", layout="wide")
st.title("🩺 性激素评估工具（基于年龄、月经天数、AMH）")

st.markdown("请先填写 **年龄、月经天数、AMH**，然后填写六项性激素，工具会基于这些变量提供科学评估和 AI 建议。")

# ========== 固定变量 ==========
st.markdown("### 📌 基础信息")
col1, col2, col3 = st.columns(3)
age = col1.number_input("年龄 (岁)", min_value=15, max_value=55, value=30)
menstrual_days = col2.number_input("月经天数 (天)", min_value=1, max_value=10, value=5)
amh = col3.number_input("AMH (ng/mL)", min_value=0.0, max_value=10.0, value=2.0)

# ========== 动态变量 ==========
st.markdown("### 🧪 六项性激素")
col1, col2 = st.columns(2)
with col1:
    fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1)
    lh  = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1)
    e2  = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=0.1)
with col2:
    p4  = st.number_input("孕酮 P4 (ng/mL)", min_value=0.0, step=0.1)
    prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1)
    t   = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1)

# ========== 参考区间 ==========
refs = {
    "FSH": (2.5, 10.2),
    "LH":  (1.9, 12.5),
    "E2":  (25.8, 60.7),
    "P4":  (0.0, 1.5),
    "PRL": (3.0, 25.0),
    "T":   (15.0, 70.0),
}

# ========== 规则评估 ==========
def evaluate_hormones(age, menstrual_days, amh, fsh, lh, e2, p4, prl, t):
    report = []

    # 年龄与AMH
    if age > 35 and amh < 1.0:
        report.append("⚠️ 年龄>35 且 AMH<1.0：卵巢储备显著下降，建议尽快助孕。")
    elif amh < 1.0:
        report.append("⚠️ AMH 偏低：卵巢储备减少，需早期干预。")
    elif amh > 4.0:
        report.append("⚠️ AMH 偏高：提示可能存在多囊卵巢综合征风险。")

    # 月经天数
    if menstrual_days < 3:
        report.append("⚠️ 月经天数过短：可能提示雌激素偏低或内膜发育不良。")
    elif menstrual_days > 7:
        report.append("⚠️ 月经天数过长：需警惕子宫内膜病变或内分泌异常。")

    # 六项激素
    if fsh > 0:
        if fsh > refs["FSH"][1]:
            report.append("⚠️ FSH 偏高：卵巢功能减退可能。")
    if lh > 0 and fsh > 0 and lh/fsh > 2:
        report.append("⚠️ LH/FSH>2：多囊卵巢综合征风险。")
    if e2 > 0:
        if e2 < refs["E2"][0]:
            report.append("⚠️ 雌二醇偏低：卵泡发育不良可能。")
    if p4 > 0 and p4 < refs["P4"][1]:
        report.append("⚠️ 孕酮偏低：黄体功能不足可能影响着床。")
    if prl > refs["PRL"][1]:
        report.append("⚠️ 泌乳素偏高：需排查垂体高泌乳素血症。")
    if t > refs["T"][1]:
        report.append("⚠️ 睾酮偏高：提示高雄激素状态，常见于PCOS。")

    if not report:
        report = ["✅ 指标基本正常，建议继续保持健康生活方式。"]
    return report

# ========== 生成评估报告 ==========
if st.button("生成评估报告"):
    st.markdown("### 📊 评估结果")
    report = evaluate_hormones(age, menstrual_days, amh, fsh, lh, e2, p4, prl, t)
    for line in report:
        st.write(line)

    # ========= 雷达图 =========
    st.markdown("### 📈 激素雷达图")
    labels = ["FSH", "LH", "E2", "P4", "PRL", "T"]
    values = [fsh, lh, e2, p4, prl, t]
    max_vals = [refs[k][1] for k in labels]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill='toself', name='当前指标'))
    fig.add_trace(go.Scatterpolar(r=max_vals, theta=labels, fill='toself', name='参考上限', line=dict(dash='dash')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(max_vals)*1.2])), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # ========= AI 建议 =========
    st.markdown("### 🤖 AI 医疗与生活方式建议")
    prompt = (
        f"患者信息：年龄 {age} 岁，月经天数 {menstrual_days} 天，AMH {amh} ng/mL。\n"
        f"激素指标：FSH={fsh}, LH={lh}, E2={e2}, P4={p4}, PRL={prl}, T={t}\n"
        "请结合基础信息与激素指标，提供：\n"
        "1. 医学评估（2-3句）；\n"
        "2. 医疗建议（如是否需进一步检查或治疗方案）；\n"
        "3. 生活方式建议（饮食、运动、作息）。"
    )
    with st.spinner("AI 正在生成建议..."):
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        st.write(response.choices[0].message.content)
