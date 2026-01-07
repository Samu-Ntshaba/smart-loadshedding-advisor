import streamlit as st

from ui_footer import render_footer


st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

st.title("About")

st.markdown(
    """
### About the project
I built StageWatch AI Advisor to make load-shedding planning clearer and less stressful.
The goal is to turn schedule data into simple, actionable insights that help households
and teams plan their day with fewer surprises.

### About the builder
I’m Simukelo Ntshaba, an AI engineer who cares about practical systems that respect
real-world constraints. My approach blends AI engineering, careful data handling, and
system thinking—so the experience stays reliable, transparent, and easy to understand.
""".strip()
)

render_footer()
