import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 参考范围
REFERENCE = {
    "卵泡早期": {"FSH": (3, 10), "LH": (2, 12), "E2": (50, 300), "P": (0, 3), "PRL": (5, 25), "T": (20, 60)},
    "排卵期": {"FSH": (3, 10), "LH": (10, 20), "E2": (150, 400), "P": (0, 3), "PRL": (5, 25), "T": (20, 60)},
    "黄体期": {"FSH": (2, 8), "LH": (1, 12), "E2": (100, 250), "P": (10, 20), "PRL": (5, 25), "T": (20, 60)}
}

# AI管理建议
AI_SUGGESTIONS = {
    "FSH高": "卵巢储备下降 → 建议检查AMH、窦卵泡数，补充辅酶Q10，保持规律作息，必要时就诊生殖科",
    "FSH低": "下丘脑-垂体功能抑制 → 需排查甲状腺、体重过低、过度运动，建议合理营养",
    "LH高": "考虑PCOS → 控制体重、低GI饮食、规律运动，可评估胰岛素抵抗",
    "LH/FSH高": "LH/FSH>2 → 典型PCOS表现，建议加做胰岛素曲线",
    "E2低": "卵泡发育差 → 补充优质蛋白、健康脂肪，可考虑DHEA或辅酶Q10（遵医嘱）",
    "E2高": "多卵泡或卵巢高反应 → 需监测卵泡，避免自行用药",
    "P高": "卵泡期孕酮高 → 可能黄体残留，建议下周期复查",
    "P低": "黄体期孕酮低 → 黄体功能不足，可补充维生素B6、锌，必要时黄体支持",
    "PRL高": "高泌乳素血症 → 避免压力、咖啡因，必要时检查垂体MRI",
    "T高": "高雄激素 → 控制糖分，增加阻力训练，可加用肌醇类补充剂（遵医嘱）"
}

def get_phase(cycle_day):
    if cycle_day <= 5:
        return "卵泡早期"
    elif 6 <= cycle_day <= 14:
        return "排卵期"
    else:
        return "黄体期"

def evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day):
    phase = get_phase(cycle_day)
    ref = REFERENCE[phase]
    results = []
    suggestions = []

    def check_value(name, value):
        low, high = ref[name]
        if value < low:
            return "偏低", "yellow"
        elif value > high:
            return "偏高", "red"
        else:
            return "正常", "green"

    hormones = {"FSH": fsh, "LH": lh, "E2": e2, "P": p, "PRL": prl, "T": t}

    for name, value in hormones.items():
        status, color = check_value(name, value)
        results.append((name, value, status, color))

        # 生成AI建议
        if name == "FSH" and status == "偏高":
            suggestions.append(AI_SUGGESTIONS["FSH高"])
        elif name == "FSH" and status == "偏低":
            suggestions.append(AI_SUGGESTIONS["FSH低"])
        if name == "LH" and status == "偏高":
            suggestions.append(AI_SUGGESTIONS["LH高"])
            if fsh < 10 and lh / (fsh if fsh > 0 else 1) > 2:
                suggestions.append(AI_SUGGESTIONS["LH/FSH高"])
        if name == "E2" and status == "偏低":
            suggestions.append(AI_SUGGESTIONS["E2低"])
        elif name == "E2" and status == "偏高":
            suggestions.append(AI_SUGGESTIONS["E2高"])
        if name == "P" and phase == "卵泡早期" and status == "偏高":
            suggestions.append(AI_SUGGESTIONS["P高"])
        elif name == "P" and phase == "黄体期" and status == "偏低":
            suggestions.append(AI_SUGGESTIONS["P低"])
        if name == "PRL" and status == "偏高":
            suggestions.append(AI_SUGGESTIONS["PRL高"])
        if name == "T" and status == "偏高":
            suggestions.append(AI_SUGGESTIONS["T高"])

    return phase, results, list(set(suggestions))

def plot_hormones(results, phase):
    df = pd.DataFrame(results, columns=["激素", "数值", "状态", "颜色"])
    fig = go.Figure()
    for _, row in df.iterrows():
        low, high = REFERENCE[phase][row["激素"]]
        fig.add_trace(go.Bar(
            x=[row["激素"]], y=[row["数值"]],
            marker_color=row["颜色"], name=row["状态"]
        ))
        fig.add_shape(type="line", x0=row["激素"], x1=row["激素"], y0=low, y1=high, line=dict(color="blue", width=3))
    fig.update_layout(title=f"{phase} 激素水平对比", yaxis_title="数值", barmode="group")
    return fig

# UI
st.set_page_config(page_title="女性激素六项AI评估工具", layout="wide")
st.title("💡 女性激素六项评估工具 + AI管理建议")

col1, col2 = st.columns(2)

with col1:
    fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1)
    lh = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1)
    e2 = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=1.0)
    p = st.number_input("孕酮 P (ng/mL)", min_value=0.0, step=0.1)
    prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1)
    t = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1)
    cycle_day = st.number_input("月经天数", min_value=1, max_value=30, step=1)

if st.button("🔍 开始评估"):
    phase, results, suggestions = evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day)
    with col2:
        st.subheader(f"📌 周期阶段：{phase}")
        for r in results:
            name, value, status, color = r
            st.markdown(f"<span style='color:{color};font-weight:bold'>{name}: {value} → {status}</span>", unsafe_allow_html=True)

        st.plotly_chart(plot_hormones(results, phase))

        st.subheader("💡 AI管理建议")
        if suggestions:
            for s in suggestions:
                st.write(f"- {s}")
        else:
            st.success("激素水平均正常 → 维持健康生活方式")
