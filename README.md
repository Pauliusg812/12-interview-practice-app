# Interview Practice App

An AI-powered interview preparation tool built with Streamlit and
OpenRouter. The user pastes a job listing or describes a role, and
the app generates tailored interview questions with coaching tips
and example answers. Questions cover technical, behavioural, and
role-specific areas.

## Setup

1. Clone the repo
2. Create a virtual environment: `python3 -m venv .venv`
3. Activate it: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your OpenRouter API key
6. Run: `streamlit run app.py`

## Prompt techniques

The app has a dropdown to choose between 5 system prompt styles:

- **v1 — Zero-shot:** No examples given. General-purpose, short
  but informative output from instructions alone.
- **v2 — Few-shot:** Includes worked examples so the model
  follows a specific format. More thorough output.
- **v3 — Chain-of-thought:** The model analyses the role context
  step by step before generating questions.
- **v4 — Structured output:** Output follows a strict template
  with fixed sections and a prep checklist. Concise, no filler.
- **v5 — Persona (Alex):** The model role-plays a veteran
  engineering manager — practical, direct, neither bureaucratic
  nor overly friendly.

## Temperature setting

The user can adjust the **temperature** parameter (0.0–1.0) with a
slider. Default is **0.7**.

Temperature controls randomness in the model's word choice. At 0.0
the output is deterministic and repetitive — the same input gives
nearly identical questions every time. At 1.0 the output is more
varied and creative but risks drifting off-topic or producing
irrelevant questions.

0.7 was chosen as a deliberate middle ground: interview questions
benefit from variety so the user doesn't see the same set on every
run, but the questions must stay grounded in the job listing.

## Security guard

The app validates user input before sending it to the API:

- **Empty input check:** blocks requests with no text.
- **Length cap:** rejects input over 2000 characters to prevent
  oversized prompts and runaway token costs.
- **Prompt injection detection:** scans input for known
  injection phrases (e.g. "ignore previous instructions") and
  rejects the request if found.

## Limitations

- **Free model reliability:** the development model
  (`openrouter/free`) sometimes returns an empty "None"
  response, requiring a retry.
- **Variable output quality:** `openrouter/free` routes to a
  different model on each call, so response quality and length
  are inconsistent between runs.
- **Single-shot, not conversational:** the app generates one
  response per request. It does not keep conversation history
  or support follow-up questions.