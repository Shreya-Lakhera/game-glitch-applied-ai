import random
import json
import os

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
    st.session_state.recorded_turns = []
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
            st.session_state.recorded_turns.append({
                "secret": st.session_state.secret, "guess": guess_int,
                "reported_hint": {"Win": "Correct", "Too High": "Lower", "Too Low": "Higher"}[outcome],
            })
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
    st.write("Reproduce a suspicious hint, compare it with the game rules, and get a sourced AI explanation.")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        st.warning("AI is not configured. Python checks still work; add OPENAI_API_KEY to .env and restart for AI explanations.")
    else:
        st.caption("API key detected. Connection is checked when you investigate; credentials are never displayed.")
    cases = {
        "Reversed hint": {"secret": 42, "guess": 25, "reported_hint": "Lower"},
        "Correct hint": {"secret": 42, "guess": 70, "reported_hint": "Lower"},
        "Missed win": {"secret": 42, "guess": 42, "reported_hint": "Higher"},
    }
    if st.session_state.status != "playing":
        for i, turn in enumerate(st.session_state.get("recorded_turns", []), 1):
            cases[f"Completed game turn {i}"] = turn
    case_name = st.selectbox("Investigation case", list(cases))
    original = cases[case_name]
    is_recorded = case_name.startswith("Completed")
    case_difficulty = st.session_state.game_difficulty if is_recorded else "Normal"
    case_low, case_high = get_range_for_difficulty(case_difficulty)
    st.caption("Demonstration cases are editable and use the Normal range (1–100). Completed turns preserve the recorded game data.")
    with st.form("investigate_form"):
        cols = st.columns(3)
        secret = cols[0].number_input("Secret", case_low, case_high, original["secret"], key=f"secret_{case_name}", disabled=is_recorded)
        guess = cols[1].number_input("Guess", case_low, case_high, original["guess"], key=f"guess_{case_name}", disabled=is_recorded)
        hints = ["Higher", "Lower", "Correct"]
        hint = cols[2].selectbox("Reported hint", hints, index=hints.index(original["reported_hint"]), key=f"hint_{case_name}", disabled=is_recorded)
        submitted = st.form_submit_button("Investigate case")
    if submitted:
        turn = {"secret": int(secret), "guess": int(guess), "reported_hint": hint}
        with st.spinner("Checking the turn, retrieving notes, and requesting an explanation…"):
            result = investigate_turn(turn, difficulty=case_difficulty)
        st.session_state.investigation_result = {"case": case_name, "input": turn, **result.as_dict()}
    report = st.session_state.get("investigation_result")
    if not report:
        st.caption("Select a case and click Investigate case to begin.")
        return
    st.divider()
    st.caption(f"Last investigation: {report['case']} — secret {report['input']['secret']}, guess {report['input']['guess']}")
    if report["bug_found"]:
        st.error(f"Incorrect hint: {report['input']['reported_hint']} → {report['expected_hint']}")
    else:
        st.success(f"Hint verified: {report['expected_hint']}")
    st.write(report["explanation"])
    st.caption(f"Response mode: {report['mode']}")
    if report["diagnostic"]:
        st.warning(report["diagnostic"])
    with st.expander("Retrieved debugging notes"):
        for source in report["sources"]:
            st.markdown(f"**{source['source_id']}**")
            st.write(source["text"])
        if not report["sources"]:
            st.write("No relevant notes found.")
    with st.expander("Investigation steps", expanded=True):
        st.dataframe(report["events"], hide_index=True, use_container_width=True)
    st.download_button("Download investigation log", json.dumps(report, indent=2), "investigation.json", "application/json")


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


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮", layout="wide")
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
