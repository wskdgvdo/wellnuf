import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 参考范围定义
REFERENCE = {
    "卵泡早期": {"FSH": (3, 10), "LH": (2, 12), "E2": (50, 300), "P": (0, 3), "PRL": (5, 25), "T": (20, 60)},
    "排卵期": {"FSH": (3, 10), "LH": (10, 20), "E2": (150, 400), "P": (0, 3), "PRL": (5, 25), "T": (20, 60)},
    "黄体期": {"FSH": (2, 8), "LH": (1, 12), "E2": (100, 250), "P": (10, 20), "PRL": (5, 25), "T": (20, 60)}
}

# AI管理建议映射
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

@st.cache_data
# 根据月经天数获取周期阶段
def get_phase(cycle_day: int) -> str:
    if cycle_day <= 5:
        return "卵泡早期"
    elif cycle_day <= 14:
        return "排卵期"
    else:
        return "黄体期"

@st.cache_data
# 评估激素水平并生成建议
def evaluate_hormones(fsh: float, lh: float, e2: float, p: float, prl: float, t: float, cycle_day: int):
    phase = get_phase(cycle_day)
    ref = REFERENCE[phase]
    data = []
    suggestions = set()

    # 激素字典
    hormones = {"FSH": fsh, "LH": lh, "E2": e2, "P": p, "PRL": prl, "T": t}

    # 逐项检测
    for name, value in hormones.items():
        low, high = ref[name]
        if value < low:
            status = "偏低"
            color = "yellow"
        elif value > high:
            status = "偏高"
            color = "red"
        else:
            status = "正常"
            color = "green"

        data.append({
            "激素": name,
            "数值": value,
            "状态": status,
            "颜色": color,
            "参考低": low,
            "参考高": high
        })

        # 建议映射
        key = f"{name}{status}"
        if key in AI_SUGGESTIONS:
            suggestions.add(AI_SUGGESTIONS[key])

    # 额外LH/FSH比值判断
    if fsh > 0 and (lh / fsh) > 2:
        suggestions.add(AI_SUGGESTIONS.get("LH/FSH高", ""))

    df = pd.DataFrame(data)
    return phase, df, list(suggestions)

# 绘制激素水平对比图
def plot_hormones(df: pd.DataFrame, phase: str):
    fig = go.Figure()
    for idx, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row["激素"]],
            y=[row["数值"]],
            marker_color=row["颜色"],
            name=row["状态"]
        ))
        # 添加参考范围背景带
        fig.add_shape(
            type="rect",
            x0=idx - 0.4,
            x1=idx + 0.4,
            y0=row["参考低"],
            y1=row["参考高"],
            fillcolor="LightBlue",
            opacity=0.2,
            layer="below",
            line_width=0
        )

    fig.update_layout(
        title=f"{phase} 激素水平对比",
        xaxis_title="激素",
        yaxis_title="数值",
        barmode="group",
        legend_title="状态"
    )
    return fig

# 主程序
def main():
    st.set_page_config(page_title="女性激素六项评估", layout="wide")
    st.title("💡 女性激素六项评估工具 + AI管理建议")

    # 侧边栏输入
    with st.sidebar:
        st.header("输入参数")
        fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
        lh = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1, value=5.0)
        e2 = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=1.0, value=100.0)
        p = st.number_input("孕酮 P (ng/mL)", min_value=0.0, step=0.1, value=1.0)
        prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1, value=15.0)
        t = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1, value=25.0)
        cycle_day = st.slider("月经天数", 1, 30, 7)

        if st.button("开始评估"):
            phase, df, suggestions = evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day)

            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader(f"📌 周期阶段：{phase}")
                # 显示结果表格并高亮颜色列
                styled_df = df.style.applymap(
                    lambda c: f"color: {c}" if c in ["red", "yellow", "green"] else "",
                    subset=["颜色"]
                )
                st.dataframe(styled_df)

                st.subheader("💡 AI管理建议")
                if suggestions:
                    for s in suggestions:
                        st.write(f"- {s}")
                else:
                    st.success("激素水平均正常 → 维持健康生活方式")

            with col2:
                fig = plot_hormones(df, phase)
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
