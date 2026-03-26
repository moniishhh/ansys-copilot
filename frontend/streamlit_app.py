"""Streamlit MVP chat UI for ANSYS Copilot, directly calling backend services."""

import os
import sys
from pathlib import Path

# Fix sys.path for Streamlit Cloud to find the `backend` package
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
    
import streamlit as st

from backend.services.code_generator import CodeGenerator
from backend.services.rag_engine import RAGEngine
from backend.services.troubleshooter import Troubleshooter


# ── Lazy initialization of ML models and backend services ─────────────────────
@st.cache_resource
def get_rag_engine():
    engine = RAGEngine()
    engine.initialize()
    return engine


@st.cache_resource
def get_code_generator():
    return CodeGenerator()


@st.cache_resource
def get_troubleshooter():
    return Troubleshooter()


# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ANSYS Copilot",
    page_icon="🤖",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 ANSYS Copilot")
    st.markdown("AI-powered assistant for ANSYS simulation workflows")
    st.divider()

    mode = st.selectbox(
        "Mode",
        options=[
            "General Q&A",
            "Generate APDL Script",
            "Generate PyMAPDL Script",
            "Troubleshoot",
        ],
    )

    if mode in ("Generate APDL Script", "Generate PyMAPDL Script"):
        analysis_type = st.text_input("Analysis type (optional)", placeholder="e.g. static structural")
    else:
        analysis_type = ""

    if mode == "Troubleshoot":
        error_message = st.text_area("Error message (optional)", height=80)
        current_settings = st.text_area("Current settings (optional)", height=80)
    else:
        error_message = ""
        current_settings = ""

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Main content ──────────────────────────────────────────────────────────────
st.title("🤖 ANSYS Copilot")
st.caption(f"Mode: **{mode}**")

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("is_code"):
            st.code(msg["content"], language=msg.get("language", "text"))
            if st.button("📋 Copy", key=f"copy_{id(msg)}"):
                st.write("(Use Ctrl+C to copy the code above)")
        else:
            st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask me anything about ANSYS…")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the appropriate backend endpoint directly
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                if mode == "General Q&A":
                    rag = get_rag_engine()
                    result = rag.query(user_input)
                    answer = result["answer"]
                    sources = result.get("sources", [])
                    st.markdown(answer)
                    if sources:
                        with st.expander("📚 Sources"):
                            for src in sources:
                                st.write(f"- {src}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                elif mode in ("Generate APDL Script", "Generate PyMAPDL Script"):
                    generator = get_code_generator()
                    if mode == "Generate APDL Script":
                        result = generator.generate_apdl(user_input, analysis_type)
                    else:
                        result = generator.generate_pymapdl(user_input, analysis_type)

                    lang = result["language"]
                    code = result["code"]
                    explanation = result.get("explanation", "")

                    if explanation:
                        st.markdown(explanation)
                    st.code(code, language=lang)
                    
                    st.session_state.messages.append(
                        {"role": "assistant", "content": code, "is_code": True, "language": lang}
                    )
                    if explanation:
                        st.session_state.messages.append({"role": "assistant", "content": explanation})

                elif mode == "Troubleshoot":
                    troubleshooter = get_troubleshooter()
                    context = {
                        "analysis_type": analysis_type,
                        "error_message": error_message,
                        "current_settings": current_settings,
                    }
                    result = troubleshooter.diagnose(user_input, context)
                    
                    diagnosis = result["diagnosis"]
                    solutions = result["solutions"]
                    recommended = result.get("recommended_settings", "")

                    st.markdown(f"**🔍 Diagnosis**\n\n{diagnosis}")
                    st.markdown("**✅ Solutions**")
                    for sol in solutions:
                        st.markdown(f"- {sol}")
                    if recommended:
                        st.markdown("**⚙️ Recommended Settings**")
                        st.code(recommended, language="text")

                    full_text = f"**Diagnosis:** {diagnosis}\n\n**Solutions:**\n" + "\n".join(
                        f"- {s}" for s in solutions
                    )
                    st.session_state.messages.append({"role": "assistant", "content": full_text})

            except Exception as exc:
                st.error(f"❌ Unexpected error within backend models: {exc}")
