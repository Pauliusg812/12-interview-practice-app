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

  ## Post-review improvements

These items were raised in the Sprint 1 project review (score: 96).
The sprint is complete; these are recorded as forward-looking
lessons to apply in later sprints, not changes to this submission.

- **Schema-enforced JSON output.** Replace prompt-based JSON
  instructions with API-level schema enforcement (Pydantic models
  passed to the request). The API then guarantees a parseable
  response, which removes the truncation/parse-failure path
  entirely and shrinks the JSON prompts to a one-line instruction.
  To apply in Sprint 2.

- **Timeout and retry on API calls.** The OpenRouter call has no
  timeout and no retry, so a transient network failure or a 429
  rate-limit response would crash the UI. The robust approach is
  an explicit timeout plus retry with backoff (e.g. the `tenacity`
  library). AI providers are unstable in production, so this is
  standard practice for any real deployment.

- **Token cost display.** Token usage is already tracked in
  `result["tokens"]` but not converted to a monetary cost.
  OpenRouter exposes per-model pricing via its models endpoint,
  so the app could show the estimated cost per call. This would
  also complete Sprint 1 medium task #4.

- **Direct vs transitive dependencies.** `requirements.txt`
  currently pins 50+ packages, including `pandas`, `numpy`, and
  `pyarrow`, which are pulled in by Streamlit and never imported
  directly. The lesson is to separate direct dependencies (what
  the project actually imports) from transitive ones (what those
  dependencies need), e.g. by moving to a `pyproject.toml` with a
  lockfile so the distinction is explicit.

- **Structured logging.** The app uses no `print` statements
  (good) but also has no logging. Adding a logging setup would
  make API calls, JSON parsing failures, and judge invocations
  traceable when something goes wrong — important for debugging
  anything beyond a local demo.

- **Stronger prompt-injection defense.** The current guard matches
  only three hardcoded English phrases, so paraphrases, non-English
  variants, and encoded payloads bypass it. This was already noted
  as a known limitation. The better approach treats all user input
  as untrusted and layers defenses: input filtering, system-prompt
  hardening, and output validation, rather than relying on phrase
  matching alone.