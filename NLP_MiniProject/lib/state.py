import streamlit as st

def get_state():
    if "sdata" not in st.session_state:
        st.session_state.sdata = {
            "current_question": "",
            "current_level": 0,
            "attempts": [],
            "confidence_history": [],
            "retrieved_chunk": "",
            "topic": "",
            "all_attempts": []
        }
    return st.session_state.sdata

def reset_state(question="", chunk="", topic=""):
    s = get_state()
    s["current_question"] = question
    s["current_level"] = 0
    s["attempts"] = []
    s["confidence_history"] = []
    s["retrieved_chunk"] = chunk
    s["topic"] = topic

def log_attempt(text, sim_score, level, confidence):
    s = get_state()
    item = {
        "question": s["current_question"],
        "text": text,
        "similarity_score": sim_score,
        "level": level,
        "confidence": confidence
    }
    s["attempts"].append(item)
    s["all_attempts"].append(item)
    s["confidence_history"].append(confidence)
    return item
