import os
import time
import streamlit as st
from lib.ingestion import load_corpus
from lib.vectorstore import build_index, retrieve
from lib.evaluator import evaluate_attempt
from lib.socratic import generate_response
from lib.state import get_state, reset_state, log_attempt
from lib.report import render_report

st.set_page_config(page_title="Teach Don't Tell RAG", layout="wide")

s = get_state()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "gate_done" not in st.session_state:
    st.session_state.gate_done = True
if "pending" not in st.session_state:
    st.session_state.pending = None

with st.sidebar:
    st.header("Corpus & Setup")
    uploaded = st.file_uploader("Upload document", type=["txt", "md", "pdf"])
    if uploaded:
        os.makedirs("data/corpus", exist_ok=True)
        path = os.path.join("data/corpus", uploaded.name)
        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"Saved {uploaded.name}")

    if os.path.exists("data/corpus"):
        files = [f for f in os.listdir("data/corpus") if not f.startswith(".")]
        if files:
            st.caption(f"Corpus: {', '.join(files)}")

    if st.button("Build Index"):
        with st.spinner("Loading and indexing..."):
            chunks = load_corpus("data/corpus")
            if chunks:
                build_index(chunks)
                st.success(f"Indexed {len(chunks)} chunks")
            else:
                st.warning("No documents found in corpus")

    st.divider()
    timer_sec = st.number_input("Thinking gate (seconds)", min_value=0, max_value=120, value=10)

    st.divider()
    new_q = st.text_input("Enter topic or question")
    if st.button("Start Question") and new_q.strip():
        with st.spinner("Finding relevant content..."):
            chunks = retrieve(new_q.strip(), k=1)
        if not chunks:
            st.error("Build the index first!")
        else:
            chunk_text = chunks[0]["text"]
            reset_state(new_q.strip(), chunk_text, "")
            st.session_state.messages = []
            with st.spinner("Thinking of a guiding question..."):
                first_resp = generate_response(new_q.strip(), chunk_text, 0)
            st.session_state.messages.append({"role": "assistant", "content": first_resp})
            st.session_state.gate_done = False if timer_sec > 0 else True
            st.session_state.pending = None
            st.rerun()

    st.divider()
    if st.button("Reset Session"):
        reset_state()
        st.session_state.messages = []
        st.session_state.gate_done = True
        st.session_state.pending = None
        st.rerun()

st.title("Teach Don't Tell RAG")

if s["current_question"]:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Topic: {s['current_question']}")
    with col2:
        lvl = s["current_level"]
        labels = {0: "🟢 Open Question", 1: "🟡 Narrowing Down", 2: "🟠 Gentle Nudge", 3: "🔴 Full Answer"}
        st.metric("Escalation", labels.get(lvl, f"Level {lvl}"))

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.gate_done and s["current_question"] and timer_sec > 0:
    ph = st.empty()
    bar = st.progress(0)
    for rem in range(timer_sec, 0, -1):
        pct = int(((timer_sec - rem) / max(timer_sec, 1)) * 100)
        bar.progress(pct)
        ph.warning(f"⏳ **Thinking gate active** — {rem}s remaining. Read the hint above and think before answering...")
        time.sleep(1)
    bar.empty()
    ph.empty()
    st.session_state.gate_done = True
    st.rerun()

if st.session_state.pending:
    st.info(f"Your attempt: *{st.session_state.pending}*")
    with st.form("conf_form"):
        conf = st.slider("Rate your confidence (1-5)", min_value=1, max_value=5, value=3)
        if st.form_submit_button("Submit & Continue"):
            user_text = st.session_state.pending
            chunk_text = s["retrieved_chunk"]
            with st.spinner("Evaluating your answer..."):
                ev = evaluate_attempt(user_text, chunk_text, len(s["attempts"]) + 1)
            log_attempt(user_text, ev["score"], s["current_level"], conf)

            if ev["passed"]:
                s["current_level"] = 3
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ Great work! Your answer scored **{ev['score']:.2f}** — you clearly understand this concept."
                })
            else:
                s["current_level"] = ev["level"]
                with st.spinner("Preparing your hint..."):
                    resp = generate_response(s["current_question"], chunk_text, ev["level"], user_text)
                st.session_state.messages.append({"role": "assistant", "content": resp})

            st.session_state.pending = None
            st.rerun()
elif s["current_question"] and st.session_state.gate_done:
    user_input = st.chat_input("Enter your attempt...")
    if user_input and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.session_state.pending = user_input.strip()
        st.rerun()

with st.expander("Session Evaluation Report"):
    render_report()
