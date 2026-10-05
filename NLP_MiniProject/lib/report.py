import streamlit as st
from lib.state import get_state

def render_report():
    s = get_state()
    attempts = s.get("all_attempts", [])
    if not attempts:
        st.info("No attempts recorded yet.")
        return

    by_q = {}
    for a in attempts:
        q = a["question"]
        if q not in by_q:
            by_q[q] = []
        by_q[q].append(a)

    rows = []
    chart_data = []

    for q, q_att in by_q.items():
        n = len(q_att)
        best = max(a["similarity_score"] for a in q_att)
        avg_conf = sum(a["confidence"] for a in q_att) / n
        last_lvl = q_att[-1]["level"]

        if best >= 0.45 and n == 1:
            verdict = "✅ Understood immediately"
        elif best >= 0.45:
            verdict = f"✅ Got it after {n} attempts"
        elif last_lvl >= 3:
            verdict = f"📖 Needed full answer after {n} attempts"
        else:
            verdict = f"🔄 In progress (level {last_lvl})"

        rows.append({
            "Question": q[:50],
            "Attempts": n,
            "Best Score": round(best, 2),
            "Avg Confidence": round(avg_conf, 1),
            "Result": verdict
        })
        chart_data.append({"Question": q[:30], "Best Score": round(best, 2)})

    st.subheader("Evaluation Report")
    st.table(rows)

    if len(chart_data) > 1:
        st.bar_chart(chart_data, x="Question", y="Best Score")

    total = len(attempts)
    passed = sum(1 for a in attempts if a["similarity_score"] >= 0.60)
    st.caption(f"Session total: {total} attempts, {passed} passed ({100*passed//max(total,1)}%)")
