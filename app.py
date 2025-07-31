import streamlit as st
import openai
import os

# ============ 配置 ============
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="性激素六项评估工具", layout="centered")
st.title("🩺 性激素六项评估 + AI 建议")

st.markdown("输入六项性激素及相关指标，工具会生成科学评估，并用 AI 给出个性化建议。")

# ============ 输入区域 ============
col1, col2 = st.columns(2)
with col1:
    fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1)
    lh  = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1)
    e2  = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=0.1)
    p4  = st.number_input("孕酮 P4 (ng/mL)", min_value=0.0, step=0.1)
with col2:
    prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1)
    t   = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1)
    age = st.number_input("年龄 (岁)", min_value=0, step=1)
    amh = st.number_input("AMH (ng/mL)", min_value=0.0, step=0.1)

# ============ 阈值参考 ============
refs = {
    "FSH": (2.5, 10.2),
    "LH":  (1.9, 12.5),
    "E2":  (25.8, 60.7),
    "P4":  (0.0, 1.5),
    "PRL": (3.0, 25.0),
    "T":   (15.0, 70.0),
    "AMH": (1.0, 4.0),
}

def evaluate_hormones(fsh, lh, e2, p4, prl, t, age, amh):
    report = []
    if fsh > 0:
        low, high = refs["FSH"]
        if fsh < low:
            report.append("⚠️ FSH 偏低：可能存在垂体功能减退或低促性腺激素血症。")
        elif fsh > high:
            report.append("⚠️ FSH 偏高：提示卵巢储备下降或卵巢早衰。")
    if lh > 0 and fsh > 0 and lh/fsh > 2:
        report.append("⚠️ LH/FSH > 2：需排查多囊卵巢综合征 (PCOS)。")
    if e2 > 0:
        low, high = refs["E2"]
        if e2 < low:
            report.append("⚠️ E2 偏低：提示卵泡发育不足。")
        elif e2 > high * 5:
            report.append("⚠️ E2 明显偏高：警惕卵巢功能亢进或 OHSS 风险。")
    if p4 > 0 and p4 < refs["P4"][1]:
        report.append("⚠️ P4 偏低：提示黄体功能不足。")
    if prl > refs["PRL"][1]:
        report.append("⚠️ PRL 偏高：需排查高泌乳素血症或垂体腺瘤。")
    if t > refs["T"][1]:
        report.append("⚠️ T 偏高：提示高雄激素状态，可能与 PCOS 或肾上腺有关。")
    if age > 35 and amh > 0 and amh < refs["AMH"][0]:
        report.append("⚠️ 年龄 > 35 且 AMH < 1.0：卵巢储备显著下降，建议助孕评估。")
    if not report:
        report = ["✅ 指标均在参考范围内，未发现显著异常。"]
    return report

# ============ 生成报告 ============
if st.button("生成报告"):
    # 阈值评估
    st.subheader("初步评估结果")
    report = evaluate_hormones(fsh, lh, e2, p4, prl, t, age, amh)
    for line in report:
        st.write(line)

    # AI 建议
    st.subheader("AI 个性化建议")
    prompt = (
        "你是一位生殖内分泌医生。基于以下指标：\n"
        f"FSH={fsh}, LH={lh}, E2={e2}, P4={p4}, PRL={prl}, T={t}, 年龄={age}, AMH={amh}\n"
        "请给出：\n"
        "1. 综合评估（2-3句）；\n"
        "2. 4-5 条个性化治疗或生活方式建议。"
    )

    with st.spinner("AI 正在生成建议..."):
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        st.write(response.choices[0].message.content)
