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

## Model selection

The user can choose between a free model (for development and
testing) and three paid GPT-5 models (`gpt-5-mini`, `gpt-5-nano`,
`gpt-5`) for final use. An adjustable `max_tokens` slider controls
the response length cap.

The slider is exposed deliberately: reasoning models such as GPT-5
spend tokens on internal reasoning before producing visible output.
If `max_tokens` is too low, the entire budget can be consumed by
reasoning and the model returns nothing. A warning is shown when
GPT-5 is selected, noting it may need a higher token cap and costs
more per call.

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

## JSON output

Two prompts produce structured JSON instead of prose:

- **JSON v1** returns a flat array of question objects, each
  tagged with a type.
- **JSON v2** returns an object grouped by category
  (technical, behavioural, role_specific).

Structured output matters because it gives a predictable schema
the app can parse with `json.loads()` and render with
`st.json()`, rather than displaying raw text.

Models do not always return valid JSON (e.g. truncated output
when the response exceeds the token cap). The app handles this
defensively: if parsing fails, it catches the error, warns the
user, and falls back to showing the raw model output instead of
crashing.

## Security guard

The app validates user input before sending it to the API:

- **Empty input check:** blocks requests with no text.
- **Length cap:** rejects input over 2000 characters to prevent
  oversized prompts and runaway token costs.
- **Prompt injection detection:** scans input for known
  injection phrases (e.g. "ignore previous instructions") and
  rejects the request if found.

## LLM-as-judge (hard optional)

A second LLM scores the app's output against a rubric, returning
a score and one-sentence justification on four dimensions:

- **Role specificity** — is the prep tailored to the listing?
- **Seniority alignment** — does it match the role's level?
- **Comprehensiveness** — does it cover the key areas?
- **Contextual accuracy** — does it avoid inventing details
  not in the listing?

It also outputs an overall score and a FLAGS line listing any
hallucinations found.

The judge model is selectable separately from the generation
model. Generating with one model and judging with another
reduces self-bias (a model tends to favour its own outputs —
covered in Sprint 1 Part 4). The rubric lives in
`prompts/judge_v1.md`, kept separate from code so it can be
versioned and revised independently.

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
- **JSON output can fail:** longer JSON responses may exceed
  the token cap and truncate, producing invalid JSON. The app
  falls back to raw output in that case.
- **Judge format depends on model strength:** weaker models
  follow the judge's output format inconsistently (duplicated
  lines, collapsed output). A capable model (e.g.
  `gpt-5-mini`) produces reliable, parseable verdicts.