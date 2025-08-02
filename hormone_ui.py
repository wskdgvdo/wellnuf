import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 基础信息参考范围
BASIC_REF = {
    "年龄": (0, 100),
    "AMH": (1.0, 4.0),
    "月经周期": (24, 35),
    "经期长度": (3, 7),
    "经期血量": (5, 80)
}
# 基础信息建议映射
BASIC_SUGGESTIONS = {
    "AMH偏低": "卵巢储备功能下降；建议进一步检测FSH、E2及窦卵泡数，并补充抗氧化营养素、规律作息，必要时咨询生殖科。",
    "AMH偏高": "AMH偏高可能提示PCOS风险；建议评估胰岛素敏感性及卵巢B超形态，低GI饮食、规律运动。",
    "月经周期偏低": "周期<24天，建议排卵监测并评估黄体功能。",
    "月经周期偏高": "周期>35天，建议检测FSH、LH、E2，评估促排卵。",
    "经期长度偏低": "经期<3天，可能内膜发育不足；评估E2及内膜厚度，可考虑雌激素支持。",
    "经期长度偏高": "经期>7天，建议行B超及凝血功能检测。",
    "经期血量偏低": "经血<5mL，可能黄体功能不全或内膜过薄；建议排卵后P4评估并黄体支持。",
    "经期血量偏高": "经血>80mL，建议评估子宫肌瘤、息肉，及凝血功能。"
}

# 性激素参考范围
REFERENCE = {
    "卵泡早期": {"FSH": (3, 10), "LH": (2, 12), "E2": (20, 50), "P4": (0.1, 0.5), "PRL": (5, 25), "T": (20, 60)},
    "排卵期":   {"FSH": (3, 10), "LH": (10, 20), "E2": (150, 400), "P4": (0, 3),  "PRL": (5, 25), "T": (20, 60)},
    "黄体期":   {"FSH": (2, 8),  "LH": (1, 12), "E2": (100, 250), "P4": (10, 20), "PRL": (5, 25), "T": (20, 60)}
}

# 激素管理建议映射
AI_SUGGESTIONS = {
    "FSH偏高": "卵巢储备下降；建议检测AMH、窦卵泡数，辅酶Q10，规律作息。",
    "FSH偏低": "下丘脑-垂体功能抑制；排查甲状腺、体重过低、过度运动。",
    "LH偏高": "疑似PCOS；评估胰岛素抵抗、卵巢B超。",
    "LH/FSH高": "典型PCOS；做胰岛素曲线及卵巢B超。",
    "E2偏低": "卵泡发育不佳；优质蛋白、健康脂肪，DHEA/Q10。",
    "E2偏高": "卵巢高反应；监测卵泡，遵医嘱调整。",
    "E2早期偏高": "雌二醇偏高；提示卵泡提前发育或囊肿，需B超判断。",
    "P4卵泡期偏低": "P4<0.8(1-14天)→未排卵或未黄素化。",
    "P4卵泡非排卵期偏高": "P4>0.8(1-10天)→孕激素过量或肾上腺增生。",
    "P4早卵泡偏高": "P4>0.5(4-5天)→黄体萎缩不良，复查HCG。",
    "P4排卵前偏高": "P4>2(12-14天)→卵泡过早黄素化，受孕率下降。",
    "P4排卵后偏高": "P4>3(>15天)→90%可能排卵，LUFS约10%。",
    "P4黄体中期功能不全": "P4 3-10(19-23天)→黄体功能不全。",
    "P4黄体功能良好": "P4 15-30(19-23天)→黄体功能良好。",
    "P4中期高提示妊娠": "P4>30(19-23天)→可能怀孕，查HCG。",
    "P4末期妊娠可能": "P4>10且E2>150(24-28天)→提示妊娠，查HCG。",
    "PRL偏高": "高泌乳素；避免压力/咖啡因，MRI排查。",
    "T偏高": "高雄激素；控糖、抗阻训练。"
}

@st.cache_data
def get_phase(day: int) -> str:
    if day <= 5:
        return "卵泡早期"
    if day <= 14:
        return "排卵期"
    return "黄体期"

@st.cache_data
def evaluate_basic(age, amh, cycle, period_len, blood_vol):
    df_list = []
    suggestions = []
    metrics = {"年龄": age, "AMH": amh, "月经周期": cycle, "经期长度": period_len, "经期血量": blood_vol}
    for name, value in metrics.items():
        low, high = BASIC_REF[name]
        status, color = "正常", "green"
        key = None
        if name != "年龄":
            if value < low:
                status, color, key = "偏低", "yellow", f"{name}偏低"
            elif value > high:
                status, color, key = "偏高", "red", f"{name}偏高"
        df_list.append({"项目": name, "数值": round(value, 1), "状态": status, "颜色": color})
        if key and key in BASIC_SUGGESTIONS:
            suggestions.append(BASIC_SUGGESTIONS[key])
    return pd.DataFrame(df_list), suggestions

@st.cache_data
def evaluate_hormones(fsh, lh, e2, p4, prl, t, day):
    phase = get_phase(day)
    ref = REFERENCE[phase]
    data = []
    suggestions = set()
    hormones = {"FSH": fsh, "LH": lh, "E2": e2, "P4": p4, "PRL": prl, "T": t}
    for name, value in hormones.items():
        low, high = ref[name if name != "P4" else "P4"]
        status, color = "正常", "green"
        # E2早期逻辑
        if name == "E2" and 2 <= day <= 5 and value > 50:
            status, color = "偏高", "red"
            suggestions.add(AI_SUGGESTIONS["E2早期偏高"])
        # P4多阶段逻辑
        elif name == "P4":
            if 1 <= day <= 14 and value < 0.8:
                status, color = "偏低", "yellow"
                suggestions.add(AI_SUGGESTIONS["P4卵泡期偏低"])
            if 1 <= day <= 10 and value > 0.8:
                status, color = "偏高", "red"
                suggestions.add(AI_SUGGESTIONS["P4卵泡非排卵期偏高"])
            if 4 <= day <= 5 and value > 0.5:
                status, color = "偏高", "red"
                suggestions.add(AI_SUGGESTIONS["P4早卵泡偏高"])
            if 12 <= day <= 14 and value > 2:
                status, color = "偏高", "red"
                suggestions.add(AI_SUGGESTIONS["P4排卵前偏高"])
            if day > 15 and value > 3:
                status, color = "偏高", "red"
                suggestions.add(AI_SUGGESTIONS["P4排卵后偏高"])
            if 19 <= day <= 23:
                if 3 <= value <= 10:
                    suggestions.add(AI_SUGGESTIONS["P4黄体中期功能不全"])
                if 15 <= value <= 30:
                    suggestions.add(AI_SUGGESTIONS["P4黄体功能良好"])
                if value > 30:
                    status, color = "偏高", "red"
                    suggestions.add(AI_SUGGESTIONS["P4中期高提示妊娠"])
            if 24 <= day <= 28 and value > 10 and e2 > 150:
                status, color = "偏高", "red"
                suggestions.add(AI_SUGGESTIONS["P4末期妊娠可能"])
        else:
            if value < low:
                status, color = "偏低", "yellow"
            elif value > high:
                status, color = "偏高", "red"
            key = f"{name}{status}"
            if key in AI_SUGGESTIONS:
                suggestions.add(AI_SUGGESTIONS[key])
        data.append({"激素": name, "数值": round(value, 1), "状态": status, "颜色": color, "参考低": low, "参考高": high})
    # LH/FSH比值
    if fsh > 0 and lh / fsh > 2:
        suggestions.add(AI_SUGGESTIONS["LH/FSH高"])
    return phase, pd.DataFrame(data), list(suggestions)


def plot_hormones(df, phase):
    fig = go.Figure()
    for idx, row in df.iterrows():
        fig.add_trace(go.Bar(x=[row['激素']], y=[row['数值']], marker_color=row['颜色'], name=row['状态']))
        fig.add_shape(type='rect', x0=idx - 0.4, x1=idx + 0.4, y0=row['参考低'], y1=row['参考高'], fillcolor='LightBlue', opacity=0.2, layer='below', line_width=0)
    fig.update_layout(title=f"{phase} 激素水平对比", xaxis_title="激素", yaxis_title="数值", legend_title="状态")
    return fig


def main():
    st.set_page_config(page_title="女性激素六项评估", layout="wide")
    st.title("💡 女性激素六项评估工具 + AI管理建议")

    with st.expander("一、基础信息输入", expanded=True):
        age = st.number_input("年龄 (岁)", min_value=0, max_value=120, value=30)
        amh = st.number_input("AMH (ng/mL)", min_value=0.0, step=0.1, value=2.0)
        cycle = st.number_input("月经周期 (天)", min_value=1, max_value=365, value=28)
        period_len = st.number_input("经期长度 (天)", min_value=1, max_value=30, value=5)
        blood_vol = st.number_input("经期血量 (mL)", min_value=0.0, step=1.0, value=30.0)
        day = st.number_input("月经天数 (第几天)", min_value=1, max_value=30, value=7)

    with st.expander("二、性激素六项输入", expanded=True):
        fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
        lh = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
        e2 = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=1.0, value=100.0)
        p4 = st.number_input("孕酮 P (ng/mL)", min_value=0.0, step=0.1, value=1.0)
        prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1, value=15.0)
        t = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1, value=25.0)

    if st.button("开始评估"):
        basic_df, basic_sugg = evaluate_basic(age, amh, cycle, period_len, blood_vol)
        st.subheader("📋 基础信息评估结果")
        cols = st.columns(len(basic_df))
        for i, row in enumerate(basic_df.to_dict('records')):
            c = cols[i]
            c.markdown(f"**{row['项目']}**")
            c.markdown(f"<div style='color:{row['颜色']}; font-size:18px'>{row['数值']:.1f} ({row['状态']})</div>", unsafe_allow_html=True)
        if basic_sugg:
            st.subheader("💡 基础信息建议")
            for s in basic_sugg:
                st.write(f"- {s}")

        phase, hormone_df, hormone_sugg = evaluate_hormones(fsh, lh, e2, p4, prl, t, day)
        st.subheader(f"📌 周期阶段：{phase}")
        cols_h = st.columns(len(hormone_df))
        for i, r in enumerate(hormone_df.to_dict('records')):
            c = cols_h[i]
            ratio = min(max((r['数值'] - r['参考低']) / (r['参考高'] - r['参考低']), 0), 1)
            c.markdown(f"**{r['激素']}**")
            c.markdown(f"<div style='color:{r['颜色']}; font-size:18px'>{r['数值']:.1f} ({r['状态']})</div>", unsafe_allow_html=True)
            c.markdown(f"<div style='width:100%; background:#eee; border-radius:5px; height:10px'><div style='width:{ratio*100:.1f}%; background:{r['颜色']}; height:100%; border-radius:5px'></div></div>", unsafe_allow_html=True)
            c.markdown(f"参考范围: {r['参考低']} - {r['参考高']}")
        st.plotly_chart(plot_hormones(hormone_df, phase), use_container_width=True)

        if hormone_sugg:
            st.subheader("💡 激素管理建议")
            for s in hormone_sugg:
                st.write(f"- {s}")
        else:
            st.success("激素水平均正常 → 维持健康生活方式")

if __name__ == "__main__":
    main()
