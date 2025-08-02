import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 基础信息参考范围
BASIC_REF = {
    "年龄": (0, 100),  # 年龄仅展示
    "AMH": (1.0, 4.0),
    "月经周期": (24, 35),
    "经期长度": (3, 7),
    "经期血量": (5, 80)
}
# 基础信息建议映射（更详尽AI风格建议）
BASIC_SUGGESTIONS = {
    "AMH偏低": "卵巢储备功能下降；建议进一步检测FSH、E2及窦卵泡数，并在生活中补充抗氧化营养素（辅酶Q10、维生素D），规律作息，必要时咨询生殖内分泌科。",
    "AMH偏高": "AMH偏高可能提示PCOS风险；建议评估LH/FSH比值与胰岛素敏感性，并进行盆腔超声检查卵巢形态，饮食低GI、规律运动。",
    "月经周期偏低": "周期<24天，提示月经频发或黄体期不足；建议排卵监测（基础体温+LH试纸）并评估黄体功能。",
    "月经周期偏高": "周期>35天，提示月经稀发或无排卵；建议检测FSH、LH、E2及基础体温记录，必要时行促排卵治疗或评估功能性闭经。",
    "经期长度偏低": "经期<3天，可能子宫内膜发育不足；建议评估E2水平及超声下内膜厚度，可在排卵后适度雌激素支持。",
    "经期长度偏高": "经期>7天，警惕子宫内膜增生、肌瘤或凝血异常；建议行B超及凝血功能检查，并结合激素水平评估。",
    "经期血量偏低": "经血<5mL，可能黄体功能不全或内膜过薄；建议检测排卵后P4水平并评估子宫内膜厚度，必要时黄体支持。",
    "经期血量偏高": "经血>80mL，需排查子宫肌瘤、内膜息肉或凝血障碍；建议子宫B超及凝血四项检测，严重者行宫腔镜评估。"
}

# 性激素参考范围
REFERENCE = {
    "卵泡早期": {"FSH": (3, 10), "LH": (2, 12), "E2": (50, 300), "P": (0, 3),  "PRL": (5, 25), "T": (20, 60)},
    "排卵期":   {"FSH": (3, 10), "LH": (10,20), "E2": (150,400), "P": (0, 3),  "PRL": (5, 25), "T": (20, 60)},
    "黄体期":   {"FSH": (2, 8),  "LH": (1, 12), "E2": (100,250), "P": (10,20),  "PRL": (5, 25), "T": (20, 60)}
}
# AI管理建议映射（性激素六项）
AI_SUGGESTIONS = {
    "FSH偏高":  "卵巢储备下降 → 建议检查AMH、窦卵泡数，FSH偏高意味着卵巢储备下降；研究发现提高AMH的方法有很多，比如改善基础营养、优化卵巢微环境、减少氧化应激和慢性炎症、增加卵巢血供、改善线粒体功能，减少环境毒素和内分泌干扰物；必要时进行激素平衡管理，维持卵巢功能。",
    "FSH偏低":  "下丘脑-垂体功能抑制 → 可能存在垂体功能低下；建议排查甲状腺功能、体重过低或过度运动，并进行合理营养与适度运动。",
    "LH偏高":   "可能PCOS → 建议结合其它性激素、B超等影像学检查；多囊卵巢综合征与胰岛素抵抗、遗传和生活方式有关，控制体重、低GI饮食、规律运动。",
    "LH/FSH高": "LH/FSH>2 → 典型PCOS表现；建议加做胰岛素曲线及B超卵巢评估，必要时内分泌科干预。",
    "E2偏低":   "卵泡发育不佳 → E2偏低可能与颗粒细胞数量或芳香化酶活性不足有关；建议补充优质蛋白、健康脂肪，可考虑DHEA或辅酶Q10（遵医嘱），并加强锻炼改善血供和降低慢性炎症。",
    "E2偏高":   "多卵泡或卵巢高反应 → 定期监测卵泡发育，警惕功能性卵泡囊肿；避免自行用药，遵医嘱调整促排方案。",
    "P偏高":    "卵泡期孕酮偏高 → 可能黄体残留；会抑制卵泡发育和内膜增殖，建议下周期复查P4水平。",
    "P偏低":    "黄体期孕酮不足 → 黄体功能不全；影响子宫内膜容受性和胚胎着床，建议改善基础营养、增强代谢功能，必要时行黄体酮支持。",
    "PRL偏高":  "高泌乳素血症 → 避免压力和咖啡因；必要时行垂体MRI排查泌乳素瘤。",
    "T偏高":    "高雄激素 → 建议控制糖分摄入、加强抗阻训练；高雄激素可导致卵泡闭锁，可在医生指导下使用肌醇类补充剂。"
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
    data = []
    suggestions = []
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
        data.append({"项目": name, "数值": round(value, 1), "状态": status, "颜色": color})
        if key and key in BASIC_SUGGESTIONS:
            suggestions.append(BASIC_SUGGESTIONS[key])
    return pd.DataFrame(data), suggestions

@st.cache_data
def evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day):
    phase = get_phase(cycle_day)
    ref = REFERENCE[phase]
    data = []
    suggestions = set()
    hormones = {"FSH": fsh, "LH": lh, "E2": e2, "P": p, "PRL": prl, "T": t}
    for name, value in hormones.items():
        low, high = ref[name]
        if value < low:
            status, color = "偏低", "yellow"
        elif value > high:
            status, color = "偏高", "red"
        else:
            status, color = "正常", "green"
        data.append({"激素": name, "数值": round(value,1), "状态": status, "颜色": color, "参考低": low, "参考高": high})
        key = f"{name}{status}"
        if key in AI_SUGGESTIONS:
            suggestions.add(AI_SUGGESTIONS[key])
    if fsh > 0 and lh / fsh > 2:
        suggestions.add(AI_SUGGESTIONS["LH/FSH高"])
    return phase, pd.DataFrame(data), list(suggestions)


def plot_hormones(df: pd.DataFrame, phase: str):
    fig = go.Figure()
    for idx, row in df.iterrows():
        fig.add_trace(go.Bar(x=[row["激素"]], y=[row["数值"]], marker_color=row["颜色"], name=row["状态"]))
        fig.add_shape(type="rect", x0=idx-0.4, x1=idx+0.4, y0=row["参考低"], y1=row["参考高"], fillcolor="LightBlue", opacity=0.2, layer="below", line_width=0)
    fig.update_layout(title=f"{phase} 激素水平对比", xaxis_title="激素", yaxis_title="数值", legend_title="状态")
    return fig


def main():
    st.set_page_config(page_title="女性激素六项评估", layout="wide")
    st.title("💡 女性激素六项评估工具 + AI管理建议")

    # 基础信息输入
    st.header("一、基础信息输入")
    age = st.number_input("年龄 (岁)", min_value=0, max_value=120, value=30)
    amh = st.number_input("AMH (ng/mL)", min_value=0.0, step=0.1, value=2.0)
    cycle = st.number_input("月经周期 (天)", min_value=1, max_value=365, value=28)
    period_len = st.number_input("经期长度 (天)", min_value=1, max_value=30, value=5)
    blood_vol = st.number_input("经期血量 (mL)", min_value=0.0, step=1.0, value=30.0)
    month_day = st.number_input("月经天数 (第几天)", min_value=1, max_value=30, value=7)

    # 性激素输入
    st.header("二、性激素六项输入")
    fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
    lh = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
    e2 = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=1.0, value=100.0)
    p = st.number_input("孕酮 P (ng/mL)", min_value=0.0, step=0.1, value=1.0)
    prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1, value=15.0)
    t = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1, value=25.0)

    if st.button("开始评估"):
        # 基础评估
        basic_df, basic_sugg = evaluate_basic(age, amh, cycle, period_len, blood_vol)
        st.subheader("📋 基础信息评估结果")
        records = basic_df.to_dict('records')
        cols = st.columns(len(records))
        for idx, row in enumerate(records):
            c = cols[idx]
            c.markdown(f"**{row['项目']}**")
            c.markdown(f"<div style='color:{row['颜色']}; font-size:18px'>{row['数值']:.1f} ({row['状态']})</div>", unsafe_allow_html=True)
        if basic_sugg:
            st.subheader("💡 基础信息建议")
            for s in basic_sugg:
                st.write(f"- {s}")

                # 激素评估
        phase, hormone_df, hormone_sugg = evaluate_hormones(fsh, lh, e2, p, prl, t, month_day)
        st.subheader(f"📌 周期阶段：{phase}")
        h_records = hormone_df.to_dict('records')
        cols_h = st.columns(len(h_records))
        for idx, row in enumerate(h_records):
            ch = cols_h[idx]
            ch.markdown(f"**{row['激素']}**")
            # 进度条比例计算
            ratio = min(max((row['数值'] - row['参考低']) / (row['参考高'] - row['参考低']), 0), 1)
            # 值与状态
            ch.markdown(f"<div style='font-size:18px; margin-bottom:4px; color:{row['颜色']};'>{row['数值']:.1f} ({row['状态']})</div>", unsafe_allow_html=True)
            # 进度条展示
            ch.markdown(f"<div style='width:100%; background-color:#eee; border-radius:5px; height:10px;'><div style='width:{ratio*100:.1f}%; background-color:{row['颜色']}; height:100%; border-radius:5px;'></div></div>", unsafe_allow_html=True)
            ch.markdown(f"参考范围: {row['参考低']} - {row['参考高']}")
        # 直观柱状图
        st.plotly_chart(plot_hormones(hormone_df, phase), use_container_width=True)
        st.subheader("💡 激素管理建议")(plot_hormones(hormone_df, phase), use_container_width=True)
        st.subheader("💡 激素管理建议")
        if hormone_sugg:
            for s in hormone_sugg:
                st.write(f"- {s}")
        else:
            st.success("激素水平均正常 → 维持健康生活方式")

if __name__ == "__main__":
    main()
