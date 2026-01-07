import streamlit as st


GLOBAL_STYLE = """
<style>
  /* Visual-only hide of Streamlit default UI */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }

  .sla-app-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    background: #ffffff;
    border-top: 1px solid #e6ecf5;
    padding: 12px 16px;
    box-shadow: 0 -10px 20px rgba(17, 24, 39, 0.08);
  }

  .sla-app-footer .stButton > button {
    background: transparent;
    border: none;
    padding: 0;
    color: #0b1f3a;
    font-weight: 600;
    font-size: 14px;
  }

  .sla-app-footer .stButton > button:hover {
    color: #16406b;
    background: transparent;
  }

  .sla-footer-spacer {
    height: 70px;
  }

  .sla-footer-links {
    display: flex;
    gap: 24px;
    align-items: center;
    justify-content: center;
  }
</style>
"""


def render_footer() -> None:
    st.markdown(GLOBAL_STYLE, unsafe_allow_html=True)
    st.markdown('<div class="sla-app-footer">', unsafe_allow_html=True)
    st.markdown('<div class="sla-footer-links">', unsafe_allow_html=True)

    if st.button("Terms & Conditions", key="footer_terms"):
        st.switch_page("apps/ui/pages/1_Terms_Conditions.py")

    if st.button("About", key="footer_about"):
        st.switch_page("apps/ui/pages/2_About.py")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="sla-footer-spacer"></div>', unsafe_allow_html=True)
