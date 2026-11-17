# Streamlit notes

## Session state behavior
Streamlit reruns the script after interaction. Values stored in st.session_state persist for that user's session, so the secret, attempts, score, and history must be initialized and reset deliberately.
