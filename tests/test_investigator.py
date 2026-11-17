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
    assert result.mode == "mocked-model"
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

@pytest.mark.parametrize("hint", [None, 5, True, []])
def test_nontext_hint_is_rejected(hint):
    with pytest.raises(ValueError, match="must be text"):
        validate_turn({"secret": 42, "guess": 25, "reported_hint": hint})


def test_missing_key_reports_setup_and_correct_comparison(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = investigate_turn({"secret": 42, "guess": 25, "reported_hint": "Lower"})
    assert "Missing OPENAI_API_KEY" in result.diagnostic
    assert "below the secret 42" in result.explanation
    assert result.sources
    assert result.events[-1]["result"] == "Skipped: missing API key"


def test_equal_guess_fallback_is_grammatical(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = investigate_turn({"secret": 42, "guess": 42, "reported_hint": "Higher"})
    assert "equal to the secret" in result.explanation


def test_auth_error_is_actionable_without_retry_or_secret_leak():
    from urllib.error import HTTPError
    calls = []
    def fail(prompt):
        calls.append(prompt)
        raise HTTPError("https://example.com", 401, "SECRET_VALUE", {}, None)
    result = investigate_turn({"secret": 42, "guess": 25, "reported_hint": "Lower"}, model_call=fail)
    assert len(calls) == 1
    assert "authentication failed" in result.diagnostic
    assert "SECRET_VALUE" not in str(result.as_dict())
