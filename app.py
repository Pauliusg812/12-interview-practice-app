"""Interview Practice App — Streamlit front-end."""

import streamlit as st
from src.llm_client import chat, load_prompt

st.title("Interview Practice App")

system_prompt = load_prompt("system_v1.md")

user_input = st.text_area(
    "Paste a job listing or describe the role you are preparing for:",
    height=200,
)

if st.button("Generate Interview Prep"):
    if not user_input.strip():
        st.warning("Please enter a job listing or role description.")
    else:
        with st.spinner("Generating your interview prep..."):
            result = chat(system_prompt, user_input)
        st.markdown(result["content"])
        st.caption(f"Tokens used: {result['tokens']} | " f"Model: {result['model']}")
