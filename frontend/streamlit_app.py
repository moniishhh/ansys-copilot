"""Streamlit MVP chat UI for ANSYS Copilot."""

import requests
import streamlit as st

# Backend API base URL
API_BASE = "http://localhost:8000"

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
user_input = st.chat_input(f"Ask me anything about ANSYS…")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the appropriate backend endpoint
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                if mode == "General Q&A":
                    resp = requests.post(
                        f"{API_BASE}/chat",
                        json={"message": user_input, "conversation_history": []},
                        timeout=60,
                    )
                    resp.raise_for_status()
                    answer = resp.json()["response"]
                    sources = resp.json().get("sources", [])
                    st.markdown(answer)
                    if sources:
                        with st.expander("📚 Sources"):
                            for src in sources:
                                st.write(f"- {src}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                elif mode in ("Generate APDL Script", "Generate PyMAPDL Script"):
                    script_type = "apdl" if mode == "Generate APDL Script" else "pymapdl"
                    resp = requests.post(
                        f"{API_BASE}/generate-script",
                        json={
                            "description": user_input,
                            "script_type": script_type,
                            "analysis_type": analysis_type,
                        },
                        timeout=90,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    lang = data["language"]
                    code = data["code"]
                    explanation = data.get("explanation", "")

                    if explanation:
                        st.markdown(explanation)
                    st.code(code, language=lang)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": code, "is_code": True, "language": lang}
                    )
                    if explanation:
                        st.session_state.messages.append({"role": "assistant", "content": explanation})

                elif mode == "Troubleshoot":
                    resp = requests.post(
                        f"{API_BASE}/troubleshoot",
                        json={
                            "problem": user_input,
                            "analysis_type": analysis_type,
                            "error_message": error_message,
                            "current_settings": current_settings,
                        },
                        timeout=90,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    diagnosis = data["diagnosis"]
                    solutions = data["solutions"]
                    recommended = data.get("recommended_settings", "")

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

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.")
            except requests.exceptions.HTTPError as exc:
                st.error(f"❌ Backend error: {exc.response.text}")
            except Exception as exc:
                st.error(f"❌ Unexpected error: {exc}")
