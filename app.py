import streamlit as st
import plotly.graph_objects as go

# ========== 页面设置 ==========
st.set_page_config(page_title="性激素六项评估工具", layout="wide")
st.title("🩺 性激素评估工具（规则版）")

st.markdown("输入基础信息和六项性激素指标，系统将根据医学参考范围进行评估，并给出医疗与生活方式建议。")

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
    evaluation = []
    medical_advice = []
    lifestyle_advice = []

    # 年龄与 AMH
    if age > 35 and amh < 1.0:
        evaluation.append("⚠️ 年龄>35 且 AMH<1.0：卵巢储备显著下降")
        medical_advice.append("建议尽快进行生育力评估或辅助生殖咨询")
        lifestyle_advice.append("保持规律作息，避免熬夜，补充抗氧化营养素（如辅酶Q10）")
    elif amh < 1.0:
        evaluation.append("⚠️ AMH 偏低：卵巢储备减少")
        medical_advice.append("建议做基础窦卵泡数（AFC）超声检查")
        lifestyle_advice.append("高蛋白、低炎症饮食有助于卵巢功能")
    elif amh > 4.0:
        evaluation.append("⚠️ AMH 偏高：可能存在多囊卵巢综合征风险")
        medical_advice.append("建议行B超及代谢检查，必要时考虑内分泌科评估")
        lifestyle_advice.append("控制体重，进行规律有氧运动")

    # 月经天数
    if menstrual_days < 3:
        evaluation.append("⚠️ 月经天数过短：可能提示雌激素偏低或内膜发育不良")
        medical_advice.append("建议检查雌二醇和子宫内膜厚度")
        lifestyle_advice.append("可增加健康脂肪摄入，如深海鱼、橄榄油")
    elif menstrual_days > 7:
        evaluation.append("⚠️ 月经天数过长：需警惕子宫内膜病变")
        medical_advice.append("建议做盆腔超声，必要时行宫腔镜检查")

    # 六项激素
    if fsh > refs["FSH"][1]:
        evaluation.append("⚠️ FSH 偏高：卵巢功能减退")
        medical_advice.append("建议进行基础内分泌全面检查")
    if lh > 0 and fsh > 0 and lh/fsh > 2:
        evaluation.append("⚠️ LH/FSH > 2：多囊卵巢综合征风险")
        lifestyle_advice.append("建议低GI饮食和规律运动")
    if e2 < refs["E2"][0]:
        evaluation.append("⚠️ 雌二醇偏低：卵泡发育不良")
        medical_advice.append("建议在卵泡期复查E2和B超监测卵泡")
    if p4 < refs["P4"][1]:
        evaluation.append("⚠️ 孕酮偏低：黄体功能不足")
        medical_advice.append("建议黄体期复查孕酮，必要时补充黄体支持")
    if prl > refs["PRL"][1]:
        evaluation.append("⚠️ 泌乳素偏高：可能为高泌乳素血症")
        medical_advice.append("建议行垂体MRI及内分泌科就诊")
    if t > refs["T"][1]:
        evaluation.append("⚠️ 睾酮偏高：高雄激素状态")
        lifestyle_advice.append("减少高糖饮食，增加阻力训练")

    if not evaluation:
        evaluation = ["✅ 指标基本正常，卵巢功能及激素状态良好"]
        lifestyle_advice = ["保持健康作息，均衡饮食，定期复查"]

    return evaluation, medical_advice, lifestyle_advice

# ========== 生成报告 ==========
if st.button("生成评估报告"):
    evaluation, medical_advice, lifestyle_advice = evaluate_hormones(age, menstrual_days, amh, fsh, lh, e2, p4, prl, t)

    st.markdown("### 📊 评估结果")
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
