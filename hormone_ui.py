import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 基础信息参考范围
BASIC_REF = {
    "年龄": (0, 100),  # 年龄仅展示
    "AMH": (1.0, 4.0),
    "月经周期长度": (24, 35),
    "经期长度": (3, 7),
    "经期血量": (5, 80)
}
# 基础信息建议
BASIC_SUGGESTIONS = {
    "AMH偏低": "卵巢储备下降 → 建议评估生育规划并咨询生殖科",
    "AMH偏高": "AMH偏高，需结合临床评估PCOS风险",
    "月经周期长度偏短": "周期<24天，提示月经频发，建议排卵监测",
    "月经周期长度偏长": "周期>35天，提示月经稀发，需评估卵巢储备与内分泌",
    "经期长度偏短": "经期<3天，子宫内膜发育可能不足",
    "经期长度偏长": "经期>7天，警惕子宫内膜增生或凝血异常",
    "经期血量偏少": "经血<5mL，考虑子宫内膜薄或排卵障碍",
    "经期血量偏多": "经血>80mL，需评估子宫肌瘤、内膜病变及贫血风险"
}

# 激素参考范围
REFERENCE = {
    "卵泡早期": {"FSH": (3, 10), "LH": (2, 12), "E2": (50, 300), "P": (0, 3), "PRL": (5, 25), "T": (20, 60)},
    "排卵期": {"FSH": (3, 10), "LH": (10, 20), "E2": (150, 400), "P": (0, 3), "PRL": (5, 25), "T": (20, 60)},
    "黄体期": {"FSH": (2, 8), "LH": (1, 12), "E2": (100, 250), "P": (10, 20), "PRL": (5, 25), "T": (20, 60)}
}
# AI管理建议
AI_SUGGESTIONS = {
    "FSH偏高": "卵巢储备下降 → 建议检查AMH、窦卵泡数，补充辅酶Q10，保持规律作息，必要时就诊生殖科",
    "FSH偏低": "下丘脑-垂体功能抑制 → 需排查甲状腺、体重过低、过度运动，建议合理营养",
    "LH偏高": "考虑PCOS → 控制体重、低GI饮食、规律运动，可评估胰岛素抵抗",
    "LH/FSH高": "LH/FSH>2 → 典型PCOS表现，建议加做胰岛素曲线",
    "E2偏低": "卵泡发育差 → 补充优质蛋白、健康脂肪，可考虑DHEA或辅酶Q10（遵医嘱）",
    "E2偏高": "多卵泡或卵巢高反应 → 需监测卵泡，避免自行用药",
    "P偏高": "卵泡期孕酮高 → 可能黄体残留，建议下周期复查",
    "P偏低": "黄体期孕酮低 → 黄体功能不足，可补充维生素B6、锌，必要时黄体支持",
    "PRL偏高": "高泌乳素血症 → 避免压力、咖啡因，必要时检查垂体MRI",
    "T偏高": "高雄激素 → 控制糖分，增加阻力训练，可加用肌醇类补充剂（遵医嘱）"
}

# 获取周期阶段
@st.cache_data
def get_phase(cycle_day: int) -> str:
    if cycle_day <= 5:
        return "卵泡早期"
    elif cycle_day <= 14:
        return "排卵期"
    else:
        return "黄体期"

# 评估基础信息
@st.cache_data
def evaluate_basic(age, amh, cycle_len, period_len, blood_vol):
    data = []
    suggestions = []
    metrics = {
        "年龄": age,
        "AMH": amh,
        "月经周期长度": cycle_len,
        "经期长度": period_len,
        "经期血量": blood_vol
    }
    for name, value in metrics.items():
        low, high = BASIC_REF[name]
        key = None  # 初始化 key，避免未定义
        if name == "年龄":
            status, color = "正常", "green"
        else:
            if value < low:
                status, color = "偏低", "yellow"
                key = f"{name}偏低"
            elif value > high:
                status, color = "偏高", "red"
                key = f"{name}偏高"
            else:
                status, color = "正常", "green"
        data.append({"项目": name, "数值": value, "状态": status, "颜色": color})
        if key and key in BASIC_SUGGESTIONS:
            suggestions.append(BASIC_SUGGESTIONS[key])
    return pd.DataFrame(data), suggestions(data), suggestions

# 评估激素
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
        data.append({"激素": name, "数值": value, "状态": status, "颜色": color,
                     "参考低": low, "参考高": high})
        key = f"{name}{status}"
        if key in AI_SUGGESTIONS:
            suggestions.add(AI_SUGGESTIONS[key])
    # LH/FSH 比值
    if fsh > 0 and lh / fsh > 2:
        suggestions.add(AI_SUGGESTIONS.get("LH/FSH高", ""))
    return phase, pd.DataFrame(data), list(suggestions)

# 绘图
def plot_hormones(df, phase):
    fig = go.Figure()
    for idx, row in df.iterrows():
        fig.add_trace(go.Bar(x=[row["激素"]], y=[row["数值"]], marker_color=row["颜色"], name=row["状态"]))
        fig.add_shape(type="rect", x0=idx-0.4, x1=idx+0.4, y0=row["参考低"], y1=row["参考高"],
                      fillcolor="LightBlue", opacity=0.2, layer="below", line_width=0)
    fig.update_layout(title=f"{phase} 激素水平对比", xaxis_title="激素", yaxis_title="数值", legend_title="状态")
    return fig

# 主程序：上下布局
st.set_page_config(page_title="女性激素六项评估", layout="wide")
st.title("💡 女性激素六项评估工具 + AI管理建议")

# 基础信息输入
st.header("一、基础信息输入")
age = st.number_input("年龄 (岁)", min_value=0, max_value=120, value=30)
amh = st.number_input("AMH (ng/mL)", min_value=0.0, step=0.1, value=2.0)
cycle_len = st.number_input("月经周期长度 (天)", min_value=1, max_value=365, value=28)
period_len = st.number_input("经期长度 (天)", min_value=1, max_value=30, value=5)
blood_vol = st.number_input("经期月经量 (mL)", min_value=0.0, step=1.0, value=30.0)

# 性激素输入
st.header("二、性激素六项输入")
fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
lh = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
e2 = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=1.0, value=100.0)
p = st.number_input("孕酮 P (ng/mL)", min_value=0.0, step=0.1, value=1.0)
prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1, value=15.0)
t = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1, value=25.0)
cycle_day = st.slider("月经天数", 1, 30, 7)

# 执行评估
if st.button("开始评估"):
    # 基础信息评估
    basic_df, basic_sugg = evaluate_basic(age, amh, cycle_len, period_len, blood_vol)
    st.subheader("📋 基础信息评估结果")
    st.dataframe(basic_df.style.applymap(lambda c: f"color: {c}" if c in ['red','yellow'] else '', subset=['颜色']))
    if basic_sugg:
        st.subheader("💡 基础信息建议")
        for s in basic_sugg:
            st.write(f"- {s}")
    # 激素评估
    phase, hormone_df, hormone_sugg = evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day)
    st.subheader(f"📌 周期阶段：{phase}")
    st.dataframe(hormone_df.style.applymap(lambda c: f"color: {c}" if c in ['red','yellow'] else '', subset=['颜色']))
    st.plotly_chart(plot_hormones(hormone_df, phase), use_container_width=True)
    st.subheader("💡 激素管理建议")
    if hormone_sugg:
        for s in hormone_sugg:
            st.write(f"- {s}")
    else:
        st.success("激素水平均正常 → 维持健康生活方式")
