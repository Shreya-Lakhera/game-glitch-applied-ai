# Game Glitch Investigator AI model card

## Configuration and intended use

The optional provider is OpenAI Chat Completions. Set `OPENAI_API_KEY` and
optionally `OPENAI_MODEL` (default `gpt-4o-mini`) in the process environment.
The model explains a deterministic comparison for a recorded game turn. It is
not intended to find arbitrary source-code defects, edit files, or expose a
secret during normal play.

## Safety and limitations

Input and output guardrails reject missing fields, booleans, out-of-range
numbers, invalid hints, incorrect verdicts, long explanations, and unknown
source IDs. A malformed response receives one repair attempt; otherwise the
result is labeled deterministic fallback. The model can still produce unclear
language, and retrieval supports context selection rather than proving factual
support. No live-model result was available in this environment because no
credential was configured.

## Evaluation and comparison

`python evaluate.py` checks deterministic verdicts and a boolean guardrail
case. Baseline and specialized prompts are represented in
`investigator.py`; a live comparison remains pending until a configured model
is run on the same cases. No scores are fabricated. Retrieval uses local
project-authored Markdown sections and has no external-source claim.

## Collaboration reflection

The accepted implementation direction was to keep Python authoritative for
the verdict and use the model only for explanation, because this makes
incorrect model verdicts rejectable. A proposed broad rewrite was revised
into small standard-library modules so the original Streamlit game and its
tests remain stable. Review these development notes before submission.

## Future improvements

Add a provider abstraction for additional APIs, record anonymized evaluation
artifacts, and add an explicit manual rubric for explanation support.
