"""
Public Streamlit demo for AI Operations Copilot.

Forced DEMO_MODE — rule-based tool orchestration only.
No Amazon Bedrock / Anthropic calls, so AWS credits are never spent.

Deploy on Streamlit Community Cloud with NO AWS secrets.
For the real Claude agent, run locally with AWS credentials (see README).
"""

import os

# Must be set before importing the agent so DEMO_MODE is read correctly.
os.environ["DEMO_MODE"] = "1"

import streamlit as st

from agent.copilot import ask_copilot, get_agent_mode

EXAMPLES = [
    "How is pump P-104?",
    "Risk for compressor C-7?",
    "Show me recent anomalies",
    "What is the current vibration on P-104?",
    "Has there been any corrosion reported on tanks?",
]

st.set_page_config(
    page_title="AI Operations Copilot — Public Demo",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg, #0a0e17 0%, #0f172a 55%, #0a0e17 100%); }
      [data-testid="stSidebar"] { background: #111827; border-right: 1px solid rgba(148,163,184,0.15); }
      h1 { letter-spacing: -0.02em; }
      .demo-banner {
        padding: 0.85rem 1rem;
        border-radius: 10px;
        border: 1px solid rgba(96,165,250,0.35);
        background: rgba(37,99,235,0.12);
        color: #e2e8f0;
        margin-bottom: 1rem;
        font-size: 0.92rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("🔧 Ops Copilot")
    st.caption("Industrial asset monitoring agent")
    st.markdown("---")
    st.markdown("**Mode**")
    st.info(get_agent_mode())
    st.markdown("**Known assets**")
    st.code("P-104  C-7  P-22  T-12", language=None)
    st.markdown("**Tools used**")
    st.markdown(
        """
        - Sensor anomaly check (IsolationForest)
        - Failure risk (Random Forest / AI4I 2020)
        - Maintenance log search (TF-IDF)
        """
    )
    st.markdown("---")
    st.caption(
        "Public demo uses keyword-based tool selection. "
        "The full portfolio version uses Claude on Amazon Bedrock for real tool-calling."
    )
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("AI Operations Copilot")
st.markdown(
    '<div class="demo-banner">'
    "<strong>Public demo</strong> — rule-based tools only (no live Claude / Bedrock). "
    "Safe to share: your AWS credits are not used."
    "</div>",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

cols = st.columns(len(EXAMPLES[:4]))
for i, example in enumerate(EXAMPLES[:4]):
    if cols[i].button(example, key=f"ex_{i}", use_container_width=True):
        st.session_state.pending = example

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about plant assets...")
if "pending" in st.session_state:
    prompt = st.session_state.pop("pending")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking tools..."):
            answer = ask_copilot(prompt)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

st.caption(
    "Assistive only — confirm maintenance decisions with a qualified engineer. "
    "Sensor readings are simulated for portfolio demonstration."
)
