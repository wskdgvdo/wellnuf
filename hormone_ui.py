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
    "AMH偏低": "卵巢储备功能下降；建议进一步检测FSH、E2及窦卵泡数，并补充抗氧化营养素（辅酶Q10、维生素D）、规律作息，必要时咨询生殖内分泌科。",
    "AMH偏高": "AMH偏高可能提示PCOS风险；建议评估胰岛素敏感性及卵巢B超形态，饮食低GI、规律运动。",
    "月经周期偏低": "周期<24天，提示排卵期不足；建议基础体温+LH试纸监测排卵，并评估黄体功能。",
    "月经周期偏高": "周期>35天，提示无排卵或功能性闭经；建议检测FSH、LH、E2，考虑促排卵治疗。",
    "经期长度偏低": "经期<3天，可能内膜发育不足；建议评估E2水平及超声下内膜厚度，可考虑排卵后雌激素支持。",
    "经期长度偏高": "经期>7天，需排查内膜病变或凝血异常；建议行B超及凝血功能检测。",
    "经期血量偏低": "经血<5mL，可能黄体功能不全或内膜过薄；建议检测排卵后P4及内膜厚度，必要时黄体支持。",
    "经期血量偏高": "经血>80mL，需评估子宫肌瘤或息肉及凝血四项，严重者行宫腔镜评估。"
}

# 性激素参考范围
REFERENCE = {
    "卵泡早期": {"FSH": (3, 10), "LH": (2, 12), "E2": (20, 50), "P": (0, 3),  "PRL": (5, 25), "T": (20, 60)},
    "排卵期":   {"FSH": (3, 10), "LH": (10, 20), "E2": (150, 400), "P": (0, 3),  "PRL": (5, 25), "T": (20, 60)},
    "黄体期":   {"FSH": (2, 8),  "LH": (1, 12), "E2": (100, 250), "P": (10, 20),  "PRL": (5, 25), "T": (20, 60)}
}
# 激素AI管理建议（性激素六项）
AI_SUGGESTIONS = {
    "FSH偏高":  "卵巢储备下降；建议检测AMH、窦卵泡数，补充辅酶Q10，规律作息，必要时就诊生殖科。",
    "FSH偏低":  "下丘脑-垂体功能抑制；排查甲状腺、体重过低、过度运动，并优化营养。",
    "LH偏高":   "疑似PCOS；建议评估胰岛素抵抗、卵巢B超，控制体重、低GI饮食、规律运动。",
    "LH/FSH高": "典型PCOS表现；建议胰岛素曲线及卵巢B超评估，必要时内分泌科干预。",
    "E2偏低":   "卵泡发育不佳；可补充优质蛋白、健康脂肪，DHEA或辅酶Q10（遵医嘱）。",
    "E2偏高":   "卵巢高反应；监测卵泡，谨慎用药，遵医嘱调整方案。",
    "E2早期偏高": "雌二醇水平偏高；可能存在卵泡提前发育或功能性卵泡囊肿，需结合B超影像报告判断。",
    "P偏高":    "排卵期P4偏高；可能黄体残留，建议下周期复查。",
    "P偏低":    "黄体功能不全；可补充黄体酮或维B6、锌，改善内膜容受性。",
    "PRL偏高":  "高泌乳素血症；避免压力/咖啡因，必要时垂体MRI。",
    "T偏高":    "高雄激素；控制糖分，抗阻训练，肌醇类补充剂（遵医嘱）。"
}

@st.cache_data
def get_phase(cycle_day: int) -> str:
    if cycle_day <= 5:
        return "卵泡早期"
    elif cycle_day <= 14:
        return "排卵期"
    else:
        return "黄体期"

@st.cache_data
def evaluate_basic(age, amh, cycle, period_len, blood_vol):
    data, suggestions = [], []
    metrics = {"年龄": age, "AMH": amh, "月经周期": cycle, "经期长度": period_len, "经期血量": blood_vol}
    for name, value in metrics.items():
        low, high = BASIC_REF[name]
        key = None
        if name == "年龄":
            status, color = "正常", "green"
        else:
            if value < low:
                status, color, key = "偏低", "yellow", f"{name}偏低"
            elif value > high:
                status, color, key = "偏高", "red", f"{name}偏高"
            else:
                status, color = "正常", "green"
        data.append({"项目": name, "数值": round(value,1), "状态": status, "颜色": color})
        if key and key in BASIC_SUGGESTIONS:
            suggestions.append(BASIC_SUGGESTIONS[key])
    return pd.DataFrame(data), suggestions

@st.cache_data
def evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day):
    phase = get_phase(cycle_day)
    ref = REFERENCE[phase]
    data, suggestions = [], set()
    for name, value in {"FSH":fsh, "LH":lh, "E2":e2, "P":p, "PRL":prl, "T":t}.items():
        low, high = ref[name]
        # 特殊：月经第2-5天 E2 判断
        if name == "E2" and 2 <= cycle_day <= 5:
            if value > 50:
                status, color = "偏高", "red"
                suggestions.add(AI_SUGGESTIONS["E2早期偏高"])
            else:
                status, color = "正常", "green"
        else:
            if value < low:
                status, color = "偏低", "yellow"
            elif value > high:
                status, color = "偏高", "red"
            else:
                status, color = "正常", "green"
            key = f"{name}{status}"
            if key in AI_SUGGESTIONS:
                suggestions.add(AI_SUGGESTIONS[key])
        data.append({"激素":name, "数值":round(value,1), "状态":status, "颜色":color, "参考低":low, "参考高":high})
    # LH/FSH 比值判断
    if fsh > 0 and lh / fsh > 2:
        suggestions.add(AI_SUGGESTIONS["LH/FSH高"])
    return phase, pd.DataFrame(data), list(suggestions)


def plot_hormones(df, phase):
    fig = go.Figure()
    for idx, row in df.iterrows():
        fig.add_trace(go.Bar(x=[row['激素']], y=[row['数值']], marker_color=row['颜色'], name=row['状态']))
        fig.add_shape(type='rect', x0=idx-0.4, x1=idx+0.4, y0=row['参考低'], y1=row['参考高'], fillcolor='LightBlue', opacity=0.2, layer='below', line_width=0)
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
        month_day = st.number_input("月经天数 (第几天)", min_value=1, max_value=30, value=7)

    with st.expander("二、性激素六项输入", expanded=True):
        fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
        lh = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
        e2 = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=1.0, value=100.0)
        p = st.number_input("孕酮 P (ng/mL)", min_value=0.0, step=0.1, value=1.0)
        prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1, value=15.0)
        t = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1, value=25.0)

    if st.button("开始评估"):
        basic_df, basic_sugg = evaluate_basic(age, amh, cycle, period_len, blood_vol)
        st.subheader("📋 基础信息评估结果")
        recs = basic_df.to_dict('records')
        cols = st.columns(len(recs))
        for i, r in enumerate(recs):
            c = cols[i]
            c.markdown(f"**{r['项目']}**")
            c.markdown(f"<div style='color:{r['颜色']}; font-size:18px'>{r['数值']:.1f} ({r['状态']})</div>", unsafe_allow_html=True)
        if basic_sugg:
            st.subheader("💡 基础信息建议")
            for s in basic_sugg:
                st.write(f"- {s}")

        phase, hormone_df, hormone_sugg = evaluate_hormones(fsh, lh, e2, p, prl, t, month_day)
        st.subheader(f"📌 周期阶段：{phase}")
        h_recs = hormone_df.to_dict('records')
        cols_h = st.columns(len(h_recs))
        for i, r in enumerate(h_recs):
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
