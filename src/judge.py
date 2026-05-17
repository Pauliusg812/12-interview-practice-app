"""LLM-as-judge: a second LLM scores the app's output."""

from src.llm_client import load_prompt, chat


def judge(job_listing, app_output, model="openrouter/free"):
    """Score app output against the judge rubric. Returns a dict."""
    judge_prompt = load_prompt("judge_v1.md")
    judge_prompt = judge_prompt.replace("{job_description}", job_listing)
    judge_prompt = judge_prompt.replace("{assistant_response}", app_output)
    result = chat(judge_prompt, "Evaluate the response above.", model=model)
    return result
