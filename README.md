## Investigator repair update

The investigator now loads the repository `.env` file (existing environment variables take precedence), displays actionable missing-key/API errors, preserves the last investigation across UI reruns, allows edited demonstration cases, shows retrieved note text and observable workflow steps, and exports investigation JSON. Completed-game investigations use saved turns and the correct difficulty. Injected test clients are labeled mocked-model.

Windows setup, from this repository:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Only create .env if it does not already exist:
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
# Set OPENAI_API_KEY locally, save, then restart:
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Verification of this repair: `python -m pytest -q` — **26 passed**. These include Streamlit AppTest interaction checks, missing credentials, malformed responses, bounded repair, and HTTP authentication failure. Live API generation and visual browser inspection were not verified in this repair environment. The original project documentation below may describe additional work; this repair does not certify every rubric claim.

---

# Game Glitch Investigator AI

This project preserves the Module 1 Streamlit number-guessing game and adds
an applied AI investigator for recorded turns. The original starter repository
is [ai110-module1show-gameglitchinvestigator-starter](https://github.com/Shreya-Lakhera/ai110-module1show-gameglitchinvestigator-starter).

## Run it

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

For optional live explanations, copy `.env.example` to `.env` and set
`OPENAI_API_KEY` and optionally `OPENAI_MODEL`. The app remains usable without
credentials and labels its deterministic fallback clearly.

```powershell
python demo.py --cases examples/cases.json
python -m pytest -q
python evaluate.py
python tools/check_style.py
```

## What was added

`investigator.py` validates turns, computes the expected hint in Python,
retrieves small project-authored Markdown sections, optionally asks a real
language model for a JSON explanation, validates that response, allows exactly
one repair, and falls back explicitly when needed. `app.py` uses the same
pipeline as `demo.py`; the game secret is not displayed during normal play.

Example deterministic outputs:

```text
{"secret": 42, "guess": 25, "reported_hint": "Lower"}
=> expected_hint: Higher, bug_found: true

{"secret": 42, "guess": 70, "reported_hint": "Lower"}
=> expected_hint: Lower, bug_found: false

{"secret": 42, "guess": 42, "reported_hint": "Higher"}
=> expected_hint: Correct, bug_found: true
```

| Guardrail input | Result |
|---|---|
| Missing `reported_hint` | rejected |
| Boolean `secret` or `guess` | rejected |
| Number outside selected range | rejected |
| Unknown source ID from model | rejected |
| Invalid model JSON after one repair | deterministic fallback |

## Evidence and limitations

The existing Streamlit tests and local style checker are the reproducible
baseline. `evaluate.py` reports deterministic and fallback results without
pretending fallback is live AI. Live model comparison, live API output, and
visual browser inspection are pending because this environment has no API
credential or browser validation session. See [model_card.md](model_card.md),
[architecture](diagrams/architecture.mmd), [workflow evidence](ai_interactions.md),
[presentation outline](presentation_outline.md), and
[rubric checklist](rubric_checklist.md).