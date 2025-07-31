import streamlit as st
import plotly.graph_objects as go

# ========== 页面设置 ==========
st.set_page_config(page_title="性激素六项评估工具", layout="wide")
st.title("🩺 性激素六项评估工具")

st.markdown("输入基础信息（仅作参考）和六项性激素指标，系统将根据激素水平进行科学评估，并给出医疗与生活方式建议。")

# ========== 基础信息（仅参考，不参与评估输出） ==========
st.markdown("### 📌 基础信息（参考）")
col1, col2, col3 = st.columns(3)
age = col1.number_input("年龄 (岁)", min_value=15, max_value=55, value=30)
cycle_day = col2.number_input("当前月经第几天", min_value=1, max_value=30, value=3)
amh = col3.number_input("AMH (ng/mL)", min_value=0.0, max_value=10.0, value=2.0)

# ========== 六项性激素 ==========
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

# ========== 评估函数（仅针对六项性激素） ==========
def evaluate_hormones(fsh, lh, e2, p4, prl, t, cycle_day):
    evaluation = []
    medical_advice = []
    lifestyle_advice = []

    # FSH
    if fsh > refs["FSH"][1]:
        evaluation.append("⚠️ FSH 偏高：提示卵巢功能减退")
        medical_advice.append("建议行基础内分泌检查，并结合窦卵泡数评估卵巢储备")
    elif fsh < refs["FSH"][0]:
        evaluation.append("⚠️ FSH 偏低：可能提示下丘脑-垂体功能抑制")
        medical_advice.append("建议结合LH及E2水平综合判断")

    # LH
    if lh > refs["LH"][1]:
        evaluation.append("⚠️ LH 偏高：可能为多囊卵巢综合征")
        lifestyle_advice.append("建议低GI饮食、规律运动以改善胰岛素抵抗")
    if fsh > 0 and lh / fsh > 2:
        evaluation.append("⚠️ LH/FSH > 2：多囊卵巢综合征高风险")

    # 雌二醇 (E2)
    if e2 < refs["E2"][0] and cycle_day <= 3:
        evaluation.append("⚠️ 雌二醇偏低（早卵泡期）：卵泡募集不足")
        medical_advice.append("建议复查E2及B超监测卵泡")
    elif e2 > refs["E2"][1] and cycle_day <= 3:
        evaluation.append("⚠️ 雌二醇偏高（早卵泡期）：可能有卵泡早发育")
    elif e2 < refs["E2"][0] and cycle_day > 14:
        evaluation.append("⚠️ 雌二醇偏低（黄体期）：可能影响子宫内膜发育")

    # 孕酮 (P4)
    if p4 < refs["P4"][1] and cycle_day >= 15:
        evaluation.append("⚠️ 孕酮偏低（黄体期）：黄体功能不足")
        medical_advice.append("建议黄体期补充孕酮支持")

    # 泌乳素 (PRL)
    if prl > refs["PRL"][1]:
        evaluation.append("⚠️ 泌乳素偏高：可能为高泌乳素血症")
        medical_advice.append("建议复查PRL并考虑垂体MRI")

    # 睾酮 (T)
    if t > refs["T"][1]:
        evaluation.append("⚠️ 睾酮偏高：高雄激素状态")
        lifestyle_advice.append("建议低糖饮食，增加有氧及力量训练")

    if not evaluation:
        evaluation = ["✅ 六项性激素均在正常范围，内分泌状态良好"]
        lifestyle_advice = ["保持健康作息，规律运动，均衡饮食"]

    return evaluation, medical_advice, lifestyle_advice

# ========== 生成报告 ==========
if st.button("生成评估报告"):
    evaluation, medical_advice, lifestyle_advice = evaluate_hormones(fsh, lh, e2, p4, prl, t, cycle_day)

    st.markdown("### 📊 激素评估结果")
    for item in evaluation:
        st.write(item)

    # 雷达图
    st.markdown("### 📈 激素雷达图")
    labels = ["FSH", "LH", "E2", "P4", "PRL", "T"]
    values = [fsh, lh, e2, p4, prl, t]
    max_vals = [refs[k][1] for k in labels]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill='toself', name='当前指标'))
    fig.add_trace(go.Scatterpolar(r=max_vals, theta=labels, fill='toself', name='参考上限', line=dict(dash='dash')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(max_vals)*1.2])), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # 医疗建议
    st.markdown("### 🏥 医疗建议")
    if medical_advice:
        for advice in medical_advice:
            st.write(f"- {advice}")
    else:
        st.write("- 暂无特殊医疗建议，建议定期复查。")

    # 生活方式建议
    st.markdown("### 🥗 生活方式建议")
    if lifestyle_advice:
        for advice in lifestyle_advice:
            st.write(f"- {advice}")
    else:
        st.write("- 保持规律作息，均衡饮食，适度运动")
