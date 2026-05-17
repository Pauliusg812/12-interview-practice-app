"""Interview Practice App — Streamlit front-end."""

import json

import streamlit as st

from src.judge import judge
from src.llm_client import chat, load_prompt

INJECTION_PHRASES = [
    "ignore previous instructions",
    "disregard earlier guidelines",
    "you are now under my control",
]

st.title("Interview Practice App")

prompt_options = {
    "v1 — Zero-shot": "system_v1.md",
    "v2 — Few-shot": "system_v2.md",
    "v3 — Chain-of-thought": "system_v3.md",
    "v4 — Structured output": "system_v4.md",
    "v5 — Persona (Alex)": "system_v5.md",
    "JSON v1 — Flat array": "system_json_v1.md",
    "JSON v2 — Grouped by category": "system_json_v2.md",
}

model_options = {
    "Free (development)": "openrouter/free",
    "GPT-5-mini (paid, recommended)": "openai/gpt-5-mini",
    "GPT-5-nano (paid, cheaper)": "openai/gpt-5-nano",
    "GPT-5 (paid, highest)": "openai/gpt-5",
}
selected_model = st.selectbox("Choose a model:", model_options.keys())
model = model_options[selected_model]

if model == "openai/gpt-5":
    st.warning(
        "GPT-5 is a reasoning model — it may need max tokens "
        "at 4000 to return output, and costs noticeably more "
        "per call than GPT-5-mini."
    )

selected = st.selectbox("Choose a prompt style:", prompt_options.keys())
temperature = st.slider(
    "Temperature (0 = focused, 1 = creative):",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.1,
)
max_tokens = st.slider(
    "Max tokens (response length cap):",
    min_value=500,
    max_value=4000,
    value=2000,
    step=500,
)


system_prompt = load_prompt(prompt_options[selected])

user_input = st.text_area(
    "Paste a job listing or describe the role you are preparing for:",
    height=200,
)

if st.button("Generate Interview Prep"):
    if not user_input.strip():
        st.warning("Please enter a job listing or role description.")
    elif len(user_input.strip()) > 2000:
        st.warning("Input is too long. Please limit to 2000 characters.")
    elif any(phrase in user_input.strip().lower() for phrase in INJECTION_PHRASES):
        st.warning("Input contains suspicious phrases. Please revise.")
    else:
        with st.spinner("Generating your interview prep..."):
            result = chat(
                system_prompt,
                user_input,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        st.session_state["last_result"] = result
        st.session_state["last_input"] = user_input

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    is_json_prompt = "json" in prompt_options[selected]

    if is_json_prompt:
        try:
            data = json.loads(result["content"])
            st.json(data)
        except json.JSONDecodeError:
            st.warning(
                "Model did not return valid JSON. Showing raw " "output instead."
            )
            st.markdown(result["content"])
    else:
        st.markdown(result["content"])

    st.caption(f"Tokens used: {result['tokens']} | " f"Model: {result['model']}")

    selected_judge_model = st.selectbox("Choose a judge model:", model_options.keys())
    judge_model = model_options[selected_judge_model]

    if st.button("Judge this output"):
        with st.spinner("Judging..."):
            verdict = judge(
                st.session_state["last_input"],
                result["content"],
                model=judge_model,
            )
        st.subheader("Judge verdict")
        st.markdown(verdict["content"])
