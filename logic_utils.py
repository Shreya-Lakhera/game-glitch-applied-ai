def get_range_for_difficulty(difficulty: str):
    """Return the inclusive number range for a difficulty."""
    ranges = {"Easy": (1, 20), "Normal": (1, 100), "Hard": (1, 50)}
    return ranges.get(difficulty, ranges["Normal"])


def parse_guess(raw: str):
    """Parse user-entered text into an integer and a user-facing error."""
    if raw is None or raw == "":
        return False, None, "Enter a guess."
    try:
        value = int(float(raw)) if "." in raw else int(raw)
    except (TypeError, ValueError):
        return False, None, "That is not a number."
    return True, value, None


def check_guess(guess, secret):
    """Compare a numeric guess with the secret and return its outcome.

    Args:
        guess (int): Player's numeric guess.
        secret (int): Target number for the current round.

    Returns:
        str: "Win" for equality, "Too High" when the guess exceeds the
        secret, or "Too Low" when the guess is below the secret.

    Raises:
        TypeError: If the values cannot be ordered against each other.

    Note:
        Inputs must already be numeric; this function does not parse text
        or validate the selected difficulty's range.
    """
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Apply the game's scoring rules to a submitted attempt."""
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * (attempt_number + 1))
    if outcome == "Too High":
        return (
            current_score + 5
            if attempt_number % 2 == 0
            else current_score - 5
        )
    if outcome == "Too Low":
        return current_score - 5
    return current_score
