"""Reproducible deterministic evaluation and guardrail smoke checks."""

from investigator import deterministic_check, investigate_turn, validate_turn


def main():
    cases = [
        ({"secret": 42, "guess": 25, "reported_hint": "Lower"}, True),
        ({"secret": 42, "guess": 70, "reported_hint": "Lower"}, False),
        ({"secret": 42, "guess": 42, "reported_hint": "Higher"}, True),
    ]
    passed = sum(deterministic_check(case)["bug_found"] == expected
                 for case, expected in cases)
    checks = len(cases)
    try:
        validate_turn({"secret": True, "guess": 1, "reported_hint": "Higher"})
    except ValueError:
        passed += 1
    checks += 1
    fallback = investigate_turn(cases[0][0])
    print(f"Deterministic checks: {passed}/{checks} passed")
    print(f"Live AI successes: {int(fallback.mode == 'live-model')}")
    print(f"Fallbacks: {int(fallback.mode == 'deterministic fallback')}")
    return 0 if passed == checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
