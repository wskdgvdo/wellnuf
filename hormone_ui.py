import streamlit as st

def evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day):
    result = []

    if cycle_day <= 5:
        phase = "卵泡早期"
    elif 6 <= cycle_day <= 14:
        phase = "排卵期"
    else:
        phase = "黄体期"
    result.append(f"周期阶段: {phase}")

    if fsh > 10 and phase == "卵泡早期":
        result.append("FSH偏高 → 卵巢储备下降，建议AMH、窦卵泡监测")
    elif fsh < 2 and phase == "卵泡早期":
        result.append("FSH偏低 → 可能下丘脑-垂体抑制，建议复查")

    if lh > 12 or (lh/fsh > 2 and fsh < 10 and phase == "卵泡早期"):
        result.append("LH偏高或LH/FSH>2 → 考虑PCOS，建议胰岛素评估")

    if phase == "卵泡早期" and e2 < 50:
        result.append("E2偏低 → 卵泡发育不良，建议卵泡监测")
    elif phase == "卵泡早期" and e2 > 300:
        result.append("E2偏高 → 多卵泡，高反应，需监测")

    if phase == "卵泡早期" and p > 3:
        result.append("孕酮卵泡期偏高 → 可能黄体残留")
    elif phase == "黄体期" and 10 <= p <= 20:
        result.append("孕酮黄体期正常")
    elif phase == "黄体期" and p < 10:
        result.append("孕酮黄体期偏低 → 黄体功能不足，考虑支持")

    if prl > 25:
        result.append("泌乳素偏高 → 需排查压力、药物或垂体MRI")
    elif prl < 5:
        result.append("泌乳素偏低（少见） → 无症状可观察")

    if t > 60:
        result.append("睾酮偏高 → 高雄激素，建议DHEAS检查")
    elif t < 20:
        result.append("睾酮偏低 → 可能卵巢储备差")

    if len(result) == 1:
        result.append("六项激素均正常 → 维持健康生活方式")

    return "\n".join(result)


st.set_page_config(page_title="女性激素六项评估工具", page_icon="💡", layout="centered")
st.title("女性激素六项评估工具")

fsh = st.number_input("FSH (mIU/mL)", min_value=0.0, step=0.1)
lh = st.number_input("LH (mIU/mL)", min_value=0.0, step=0.1)
e2 = st.number_input("雌二醇 E2 (pg/mL)", min_value=0.0, step=1.0)
p = st.number_input("孕酮 P (ng/mL)", min_value=0.0, step=0.1)
prl = st.number_input("泌乳素 PRL (ng/mL)", min_value=0.0, step=0.1)
t = st.number_input("睾酮 T (ng/dL)", min_value=0.0, step=0.1)
cycle_day = st.number_input("月经天数", min_value=1, max_value=30, step=1)

if st.button("评估"):
    st.subheader("评估结果")
    st.write(evaluate_hormones(fsh, lh, e2, p, prl, t, cycle_day))
