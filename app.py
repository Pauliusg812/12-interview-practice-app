"""Interview Practice App — Streamlit front-end."""

import streamlit as st
from src.llm_client import chat, load_prompt

st.title("Interview Practice App")

prompt_options = {
    "v1 — Zero-shot": "system_v1.md",
    "v2 — Few-shot": "system_v2.md",
    "v3 — Chain-of-thought": "system_v3.md",
    "v4 — Structured output": "system_v4.md",
    "v5 — Persona (Alex)": "system_v5.md",
}

selected = st.selectbox("Choose a prompt style:", prompt_options.keys())
system_prompt = load_prompt(prompt_options[selected])

user_input = st.text_area(
    "Paste a job listing or describe the role you are preparing for:",
    height=200,
)

INJECTION_PHRASES = [
    "ignore previous instructions",
    "disregard earlier guidelines",
    "you are now under my control",
]

if st.button("Generate Interview Prep"):
    if not user_input.strip():
        st.warning("Please enter a job listing or role description.")
    elif len(user_input.strip()) > 2000:
        st.warning("Input is too long. Please limit to 2000 characters.")
    elif any(phrase in user_input.strip().lower() for phrase in INJECTION_PHRASES):
        st.warning("Input contains suspicious phrases. Please revise.")
    else:
        with st.spinner("Generating your interview prep..."):
            result = chat(system_prompt, user_input)
        st.markdown(result["content"])
        st.caption(f"Tokens used: {result['tokens']} | " f"Model: {result['model']}")
