import streamlit as st
import plotly.express as px
import pandas as pd

# ========== 页面设置 ==========
st.set_page_config(page_title="性激素六项评估工具", layout="wide")
st.title("🩺 性激素六项评估工具（详细版）")

st.markdown("输入基础信息和六项性激素指标，系统将针对每个指标给出科学评估（高/低/正常）、医学意义及建议。")

# ========== 基础信息（仅参考，不参与评估输出） ==========
st.markdown("### 📌 基础信息（仅参考）")
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

# 参考区间
refs = {
    "FSH": (5, 8),
    "LH":  (5, 8),
    "E2":  (25, 50),
    "P4":  (0.1, 1),
    "PRL": (3.0, 25.0),
    "T":   (15.50),
}

# ========== 评估函数 ==========
def evaluate_single_hormone(name, value, ref_low, ref_high):
    if value == 0:
        return {
            "状态": "未输入",
            "意义": "未提供数据",
            "医疗建议": "请填写此项指标以便评估",
            "生活方式建议": "无"
        }
    if value < ref_low:
        return {
            "状态": "偏低",
            "意义": f"{name} 偏低，可能提示功能不足或下丘脑-垂体轴抑制",
            "医疗建议": f"建议复查{name}，必要时行内分泌检查",
            "生活方式建议": "保证睡眠，营养均衡，减少压力"
        }
    elif value > ref_high:
        return {
            "状态": "偏高",
            "意义": f"{name} 偏高，可能提示功能异常或相关疾病风险",
            "医疗建议": f"建议复查{name}，必要时行影像学检查及内分泌就诊",
            "生活方式建议": "控制体重，均衡饮食，避免过度压力"
        }
    else:
        return {
            "状态": "正常",
            "意义": f"{name} 在正常范围，功能稳定",
            "医疗建议": "维持健康生活方式，定期复查",
            "生活方式建议": "保持规律作息与适度运动"
        }

# ========== 生成报告 ==========
if st.button("生成评估报告"):
   hormones = {
    "FSH": (fsh, refs["FSH"][0], refs["FSH"][1]),
    "LH": (lh, refs["LH"][0], refs["LH"][1]),
    "E2": (e2, refs["E2"][0], refs["E2"][1]),
    "P4": (p4, refs["P4"][0], refs["P4"][1]),
    "PRL": (prl, refs["PRL"][0], refs["PRL"][1]),
    "T": (t, refs["T"][0], refs["T"][1]),

    results = {}
    chart_data = []

    for name, (val, low, high) in hormones.items():
        result = evaluate_single_hormone(name, val, low, high)
        results[name] = result
        chart_data.append({"激素": name, "数值": val, "参考下限": low, "参考上限": high})

    # 输出详细评估
    st.markdown("### 📊 评估结果（逐项分析）")
    for hormone, res in results.items():
        st.markdown(f"#### {hormone}")
        st.write(f"- 状态：**{res['状态']}**")
        st.write(f"- 意义：{res['意义']}")
        st.write(f"- 医疗建议：{res['医疗建议']}")
        st.write(f"- 生活方式建议：{res['生活方式建议']}")
        st.markdown("---")

    # 绘制柱状图
    st.markdown("### 📈 激素水平对比图")
    df = pd.DataFrame(chart_data)

    fig = px.bar(
        df,
        x="激素",
        y="数值",
        color="激素",
        text="数值",
        title="性激素六项水平与参考区间对比"
    )

    # 添加参考区间
    for _, row in df.iterrows():
        fig.add_shape(type="line", x0=row["激素"], x1=row["激素"], y0=row["参考下限"], y1=row["参考上限"],
                      line=dict(color="green", dash="dot"))

    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(yaxis=dict(title="数值"), xaxis=dict(title="激素"))
    st.plotly_chart(fig, use_container_width=True)
