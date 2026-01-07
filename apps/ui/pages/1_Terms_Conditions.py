import streamlit as st

from ui_footer import render_footer


st.set_page_config(page_title="Terms & Conditions", page_icon="📄", layout="wide")

st.title("Terms & Conditions")

st.markdown(
    """
**What this system does**
StageWatch AI Advisor summarizes public load-shedding schedules and provides advisory
insights to help you plan. It is an informational tool only.

**Advisory-only disclaimer**
All guidance is best-effort and provided “as is.” There are no guarantees of accuracy,
availability, or completeness.

**Not affiliated / not endorsed**
This project is independent and not affiliated with, sponsored by, or endorsed by any
utility, municipality, or official agency.

**Privacy note**
No accounts are required. The app does not store personal data or user profiles.

**Limitation of liability**
By using this app, you agree that the builder is not liable for decisions, losses, or
damages that may result from relying on the information provided.
""".strip()
)

render_footer()
