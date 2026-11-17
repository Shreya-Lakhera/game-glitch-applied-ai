import pytest

from investigator import investigate_turn, validate_turn


def test_validation_normalizes_hints_and_rejects_booleans():
    assert validate_turn(
        {"secret": 42, "guess": 70, "reported_hint": " lower "}
    )["reported_hint"] == "Lower"
    with pytest.raises(ValueError, match="not booleans"):
        validate_turn({"secret": True, "guess": 1, "reported_hint": "Higher"})


def test_model_response_is_repaired_once():
    responses = [
        {"bug_found": True, "expected_hint": "Higher",
         "explanation": "wrong verdict", "source_ids": []},
        {"bug_found": False, "expected_hint": "Lower",
         "explanation": "The guess is above the secret, so Lower is correct.",
         "source_ids": ["game-rules:Number comparison rules"]},
    ]

    def model_call(prompt):
        return responses.pop(0)

    result = investigate_turn(
        {"secret": 42, "guess": 70, "reported_hint": "Lower"},
        model_call=model_call,
    )
    assert result.mode == "live-model"
    assert len(responses) == 0


def test_failed_model_repair_is_explicit_fallback():
    calls = []

    def model_call(prompt):
        calls.append(prompt)
        return "{}"

    result = investigate_turn(
        {"secret": 42, "guess": 25, "reported_hint": "Lower"},
        model_call=model_call,
    )
    assert result.mode == "deterministic fallback"
    assert result.bug_found is True
    assert len(calls) == 2
    assert "AI explanation unavailable." in result.explanation
