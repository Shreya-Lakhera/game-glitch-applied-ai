import random

import streamlit as st

from investigator import investigate_turn
from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


def reset_game(difficulty):
    low, high = get_range_for_difficulty(difficulty)
    st.session_state.game_difficulty = difficulty
    st.session_state.status = "playing"
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.history = []
    st.session_state[f"guess_input_{difficulty}"] = ""


def record_high_score(difficulty):
    """Keep the best winning score per difficulty for this session."""
    best = st.session_state.high_scores.get(difficulty)
    score = st.session_state.score
    if best is None or score > best:
        st.session_state.high_scores[difficulty] = score


def render_high_scores(difficulty):
    """Show session records without mixing scores across difficulties."""
    st.sidebar.header("🏆 Session high scores")
    best = st.session_state.high_scores.get(difficulty)
    st.sidebar.metric(
        f"Best winning score · {difficulty}",
        "—" if best is None else best,
    )
    st.sidebar.table([
        {
            "Difficulty": level,
            "Best score": str(st.session_state.high_scores[level])
            if level in st.session_state.high_scores else "No wins yet",
        }
        for level in ("Easy", "Normal", "Hard")
    ])
    st.sidebar.caption(
        "Winning rounds only. Records survive New Game and difficulty "
        "changes during this session. A new session starts fresh."
    )


def render_hint(outcome):
    """Show a direction using both text and a distinct color."""
    if outcome == "Too High":
        st.warning("📉 Too high — Go LOWER!")
    elif outcome == "Too Low":
        st.info("📈 Too low — Go HIGHER!")
    else:
        st.success("🎯 Correct guess!")


def render_round_summary(attempt_limit, show_hint):
    """Display round metrics and valid guesses without revealing the secret."""
    st.subheader("Your round")
    attempts = st.session_state.attempts
    used, remaining, score = st.columns(3)
    used.metric("Guesses used", attempts)
    remaining.metric("Attempts left", max(0, attempt_limit - attempts))
    score.metric("Score", st.session_state.score)
    st.progress(min(1.0, attempts / attempt_limit))

    guesses = [
        guess for guess in st.session_state.history
        if isinstance(guess, int)
    ]
    if not guesses:
        st.caption("Your guesses will appear here. Make your first guess!")
        return

    rows = []
    for number, guess in enumerate(guesses, 1):
        row = {"Attempt": number, "Guess": guess}
        if show_hint:
            outcome = check_guess(guess, st.session_state.secret)
            row["Result"] = {
                "Win": "🎯 Correct",
                "Too High": "📉 Too high — try lower",
                "Too Low": "📈 Too low — try higher",
            }[outcome]
        rows.append(row)
    st.table(rows)


def render_game(difficulty, attempt_limit, low, high):
    st.subheader("Make a guess")
    attempts_banner = st.empty()
    attempts_banner.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )

    raw_guess = st.text_input(
        "Enter your guess:",
        key=f"guess_input_{difficulty}",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.button(
            "Submit Guess 🚀",
            disabled=st.session_state.status != "playing",
        )
    with col2:
        st.button("New Game 🔁", on_click=reset_game, args=(difficulty,))
    with col3:
        show_hint = st.checkbox("Show hint", value=True)

    if submit and st.session_state.status == "playing":
        ok, guess_int, err = parse_guess(raw_guess)
        if not ok:
            st.session_state.history.append(raw_guess)
            st.error(err)
        elif not low <= guess_int <= high:
            st.error(f"Enter a number between {low} and {high}.")
        else:
            st.session_state.attempts += 1
            st.session_state.history.append(guess_int)
            outcome = check_guess(guess_int, st.session_state.secret)
            if show_hint:
                render_hint(outcome)
            st.session_state.score = update_score(
                current_score=st.session_state.score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )
            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                record_high_score(difficulty)
            elif st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"

    if st.session_state.status == "won":
        st.success(
            f"🏆 You won! The secret was {st.session_state.secret}. "
            f"Final score: {st.session_state.score}"
        )
    elif st.session_state.status == "lost":
        st.error(
            f"Out of attempts! The secret was {st.session_state.secret}. "
            f"Score: {st.session_state.score}"
        )
    if st.session_state.status != "playing":
        st.caption("Click New Game to start another round.")

    attempts_banner.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {max(0, attempt_limit - st.session_state.attempts)}"
    )
    st.divider()
    render_round_summary(attempt_limit, show_hint)
    render_high_scores(difficulty)


def render_investigator():
    st.header("AI Investigator")
    st.caption(
        "Investigate a completed turn or a labeled demonstration. "
        "Python verifies the hint; AI only explains it."
    )
    cases = {
        "Demo: 42, 25, Lower (incorrect)": {
            "secret": 42, "guess": 25, "reported_hint": "Lower"
        },
        "Demo: 42, 70, Lower (correct)": {
            "secret": 42, "guess": 70, "reported_hint": "Lower"
        },
        "Demo: 42, 42, Higher (missed win)": {
            "secret": 42, "guess": 42, "reported_hint": "Higher"
        },
    }
    if st.session_state.status != "playing":
        for number, guess in enumerate(st.session_state.history, 1):
            if isinstance(guess, int):
                outcome = check_guess(guess, st.session_state.secret)
                reported = {
                    "Win": "Correct",
                    "Too High": "Lower",
                    "Too Low": "Higher",
                }[outcome]
                cases[f"Completed game turn {number}"] = {
                    "secret": st.session_state.secret,
                    "guess": guess,
                    "reported_hint": reported,
                }

    case_name = st.selectbox("Investigation case", list(cases))
    if st.button("Investigate case"):
        result = investigate_turn(cases[case_name])
        st.info(f"Response mode: {result.mode}")
        st.write(f"Expected hint: **{result.expected_hint}**")
        st.write(f"Bug found: **{result.bug_found}**")
        st.write(result.explanation)
        if result.source_ids:
            with st.expander("Retrieved debugging notes"):
                st.write(", ".join(result.source_ids))


def render_about():
    st.header("Evaluation / About")
    st.write(
        "The investigator validates a turn, computes the expected hint in "
        "Python, retrieves debugging notes, and optionally asks a real model "
        "for a structured explanation."
    )
    st.write(
        "Malformed model output receives exactly one repair attempt. "
        "If credentials are absent or validation still fails, the result is "
        "labeled deterministic fallback."
    )
    st.code(
        "python -m pytest -q\n"
        "python evaluate.py\n"
        "python demo.py --cases examples/cases.json",
        language="powershell",
    )
    st.caption(
        "Live AI requires OPENAI_API_KEY. Fallback output is never labeled "
        "as live AI."
    )


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")
st.title("🎮 Game Glitch Investigator AI")
st.caption("Play the game, investigate hints, and review the evaluation.")

st.sidebar.header("Settings")
difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)
attempt_limit = {"Easy": 6, "Normal": 8, "Hard": 5}[difficulty]
low, high = get_range_for_difficulty(difficulty)
st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if (
    "secret" not in st.session_state
    or st.session_state.get("game_difficulty") != difficulty
    or not low <= st.session_state.secret <= high
):
    reset_game(difficulty)
for key, default in (
    ("attempts", 0),
    ("score", 0),
    ("status", "playing"),
    ("history", []),
    ("high_scores", {}),
):
    if key not in st.session_state:
        st.session_state[key] = default

play_tab, investigator_tab, about_tab = st.tabs(
    ["Play Game", "AI Investigator", "Evaluation / About"]
)
with play_tab:
    render_game(difficulty, attempt_limit, low, high)
with investigator_tab:
    render_investigator()
with about_tab:
    render_about()
