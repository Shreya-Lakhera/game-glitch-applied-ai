# 5–7 minute presentation outline

1. **Problem and original game (1 minute):** Show the number-guessing loop,
   ranges, attempts, score, and session-state reset behavior.
2. **Investigator flow (1 minute):** Show a recorded/demo turn entering
   validation, deterministic comparison, retrieval, model explanation, and
   output validation.
3. **Live demonstration (2 minutes):** Run `python demo.py --cases
   examples/cases.json` and show incorrect hint, correct hint, and missed win.
4. **Guardrails (1 minute):** Demonstrate invalid types and the explicit
   deterministic fallback when credentials are absent.
5. **Evidence and limits (1–2 minutes):** Run tests/evaluation, distinguish
   fallback from live AI, and explain pending live comparison.
