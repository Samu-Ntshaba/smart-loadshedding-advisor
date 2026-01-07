import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

<<<<<<< HEAD
API_BASE_URL = (
    st.secrets.get("API_BASE_URL", None) if hasattr(st, "secrets") else None
) or os.getenv("API_BASE_URL", "http://localhost:8000")
=======

# -----------------------------
# Config
# -----------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
>>>>>>> bd8892e (qqzqqz)


def api_url(path: str) -> str:
    """Safely join base URL + path (avoids double slashes)."""
    return f"{API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"


<<<<<<< HEAD
def api_url(path: str) -> str:
    return f"{API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"


def api_get(path: str, **kwargs) -> dict:
    response = requests.get(api_url(path), timeout=20, **kwargs)
=======
def api_get(path: str, params: dict | None = None) -> dict:
    response = requests.get(api_url(path), params=params, timeout=20)
>>>>>>> bd8892e (qqzqqz)
    response.raise_for_status()
    return response.json()


<<<<<<< HEAD
def api_post(path: str, json: dict | None = None, **kwargs) -> dict:
    response = requests.post(api_url(path), json=json, timeout=20, **kwargs)
=======
def api_post(path: str, payload: dict) -> dict:
    response = requests.post(api_url(path), json=payload, timeout=30)
>>>>>>> bd8892e (qqzqqz)
    response.raise_for_status()
    return response.json()


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Smart Loadshedding Advisor",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------
# UI: CSS + Icons (Font Awesome)
# -----------------------------
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

    <style>
      .sla-shell { max-width: 1200px; margin: 0 auto; }
      .sla-hero {
        background: linear-gradient(135deg, #0b1f3a 0%, #102b52 55%, #16406b 100%);
        color: #ffffff;
        padding: 26px 28px;
        border-radius: 18px;
        margin-bottom: 18px;
        box-shadow: 0 14px 28px rgba(15, 30, 60, 0.35);
      }
      .sla-hero h1 { font-size: 32px; margin: 0 0 6px 0; letter-spacing: 0.2px; }
      .sla-hero p { margin: 0; opacity: 0.9; font-size: 15px; }

      .sla-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.18);
        font-size: 12px;
        margin-top: 10px;
      }
      .sla-pill i { opacity: 0.95; }

      .sla-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid #e6ecf5;
        box-shadow: 0 10px 20px rgba(17, 24, 39, 0.08);
      }

      .sla-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
      }
      .sla-title i { color: #0b1f3a; }
      .sla-muted { color: rgba(15, 30, 60, 0.72); font-size: 13px; }

      .sla-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
      }
      @media (max-width: 900px) {
        .sla-grid { grid-template-columns: 1fr; }
      }

      .sla-metric {
        background: #f7faff;
        border: 1px solid #e6ecf5;
        border-radius: 14px;
        padding: 14px;
      }
      .sla-metric .label { font-size: 12px; color: rgba(15, 30, 60, 0.70); margin-bottom: 6px; }
      .sla-metric .value { font-size: 20px; font-weight: 700; color: #0b1f3a; }
      .sla-metric .sub { font-size: 12px; color: rgba(15, 30, 60, 0.70); margin-top: 4px; }

      .sla-footer {
        margin-top: 30px;
        padding: 18px 0 8px 0;
        border-top: 1px solid #e6ecf5;
        text-align: center;
      }
      .sla-footer .name { font-weight: 700; color: #0b1f3a; margin-bottom: 8px; }
      .sla-links a {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px; height: 40px;
        border-radius: 999px;
        border: 1px solid #e6ecf5;
        margin: 0 6px;
        color: #0b1f3a;
        text-decoration: none;
        background: #fff;
        box-shadow: 0 8px 16px rgba(17, 24, 39, 0.06);
      }
      .sla-links a:hover { background: #f7faff; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="sla-shell">
      <div class="sla-hero">
        <h1>Smart Loadshedding Advisor</h1>
        <p>AI-powered Eskom schedule insights for South Africa — plan smarter, stay powered.</p>
        <div class="sla-pill">
          <i class="fa-solid fa-link"></i>
          <span>API: <b>{API_BASE_URL}</b></span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# State
# -----------------------------
if "area_results" not in st.session_state:
    st.session_state.area_results = []
if "insights" not in st.session_state:
    st.session_state.insights = None
if "analytics" not in st.session_state:
    st.session_state.analytics = None


def safe_get(d: dict, key: str, default: Any = None) -> Any:
    return d.get(key, default) if isinstance(d, dict) else default


# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sla-title">
          <i class="fa-solid fa-magnifying-glass"></i>
          <h3 style="margin:0;">Find your area</h3>
        </div>
        <div class="sla-muted">Powered by EskomSePush • Electricity advisory</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    query = st.text_input(
        "Search area", placeholder="e.g. Fourways, Soweto, Durban", key="search_query"
    )

    colA, colB = st.columns(2)
    with colA:
        do_search = st.button("Search", use_container_width=True)
    with colB:
        clear = st.button("Clear", use_container_width=True)

    if clear:
        st.session_state.area_results = []
        st.session_state.insights = None
        st.session_state.analytics = None
        st.rerun()

    if do_search:
        if not query.strip():
            st.warning("Enter an area name to search.")
        else:
            with st.spinner("Searching areas..."):
                try:
                    response = api_get("/eskom/areas-search", params={"text": query})
                    data = (
                        response.get("data", {}) if isinstance(response, dict) else {}
                    )
                    results = data.get("areas", data.get("results", []))
                    st.session_state.area_results = results or []
                    st.success(f"Found {len(st.session_state.area_results)} areas.")
                except requests.HTTPError as exc:
                    st.error(f"Area search failed (HTTP): {exc}")
                except requests.RequestException as exc:
                    st.error(f"Area search failed: {exc}")

    area_options = st.session_state.area_results or []
    area_labels = [
        f"{area.get('name')} ({area.get('region')})"
        if area.get("region")
        else area.get("name")
        for area in area_options
        if isinstance(area, dict)
    ]

    st.write("")
    if area_labels:
        selected_index = st.selectbox(
            "Select area",
            options=list(range(len(area_labels))),
            format_func=lambda idx: area_labels[idx],
        )
        can_advise = True
    else:
        st.selectbox("Select area", options=["No results yet"], disabled=True)
        selected_index = 0
        can_advise = False

    st.write("")
    get_advice = st.button(
        "Get Advice", use_container_width=True, type="primary", disabled=not can_advise
    )

    if get_advice and can_advise:
        selected_area = area_options[selected_index]
        payload = {
            "area_id": selected_area.get("id"),
            "area_name": selected_area.get("name"),
            "query": query,
        }
        with st.spinner("Fetching insights & analytics..."):
            try:
                st.session_state.insights = api_post(
                    "/advisor/insights", json=payload
                )
                st.session_state.analytics = api_get(
                    "/advisor/analytics", params={"area_id": selected_area.get("id")}
                )
                st.success("Done.")
            except requests.HTTPError as exc:
                st.error(f"Advisor request failed (HTTP): {exc}")
            except requests.RequestException as exc:
                st.error(f"Advisor request failed: {exc}")


insights = st.session_state.insights
analytics = st.session_state.analytics

# -----------------------------
# Main layout
# -----------------------------
shell_left, shell_right = st.columns([2, 1], gap="large")

with shell_left:
    st.markdown(
        """
        <div class="sla-title">
          <i class="fa-solid fa-bolt"></i>
          <h3 style="margin:0;">Today's Outlook</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if insights:
        stage = safe_get(insights, "stage", 0)
        summary = safe_get(insights, "summary", {}) or {}
        cache = safe_get(insights, "cache", {}) or {}

        next_outage = summary.get("next_outage")
        next_outage_text = "None"
        next_outage_sub = "No outages today"
        if isinstance(next_outage, dict) and next_outage.get("start"):
            next_outage_text = "Scheduled"
            next_outage_sub = str(next_outage.get("start"))

        total_minutes = summary.get("total_outage_minutes_today", 0)

        st.markdown(
            f"""
            <div class="sla-card">
              <div class="sla-grid">
                <div class="sla-metric">
                  <div class="label">Current Eskom Stage</div>
                  <div class="value">Stage {stage}</div>
                  <div class="sub">Live status / cached when limited</div>
                </div>
                <div class="sla-metric">
                  <div class="label">Next Outage</div>
                  <div class="value">{next_outage_text}</div>
                  <div class="sub">{next_outage_sub}</div>
                </div>
                <div class="sla-metric">
                  <div class="label">Total Outage Minutes Today</div>
                  <div class="value">{total_minutes}</div>
                  <div class="sub">Calculated from schedule events</div>
                </div>
              </div>
              <div style="margin-top:12px; font-size:12px; color: rgba(15, 30, 60, 0.70);">
                <i class="fa-solid fa-database"></i>
                Status source: <b>{cache.get("status", "live")}</b> &nbsp; • &nbsp;
                Area source: <b>{cache.get("area", "live")}</b>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info(
            "Search for an area in the sidebar, then click **Get Advice** to see your schedule."
        )

    st.write("")
    st.markdown(
        """
        <div class="sla-title">
          <i class="fa-solid fa-calendar-days"></i>
          <h3 style="margin:0;">Upcoming outages</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if insights:
        events = safe_get(insights, "events", []) or []
        if events:
            rows = []
            for event in events:
                if not isinstance(event, dict):
                    continue
                rows.append(
                    {
                        "Start": event.get("start"),
                        "End": event.get("end"),
                        "Note": event.get("note", ""),
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No upcoming outages reported for this area.")
    else:
        st.caption("Upcoming outages will appear after fetching insights.")

    st.write("")
    st.markdown(
        """
        <div class="sla-title">
          <i class="fa-solid fa-wand-magic-sparkles"></i>
          <h3 style="margin:0;">AI Advice</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if insights:
        advice = (
            safe_get(insights, "ai_advice", "No advice available.")
            or "No advice available."
        )
        advice_html = str(advice).replace("\n", "<br/>")
        st.markdown(
            f"<div class='sla-card'>{advice_html}</div>", unsafe_allow_html=True
        )
    else:
        st.caption("AI advice will appear after fetching insights.")

with shell_right:
    st.markdown(
        """
        <div class="sla-title">
          <i class="fa-solid fa-chart-line"></i>
          <h3 style="margin:0;">Analytics</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if analytics:
        outage_data = safe_get(analytics, "outage_minutes_per_day", []) or []
        stage_data = safe_get(analytics, "stage_distribution", []) or []

        st.markdown("<div class='sla-card'>", unsafe_allow_html=True)

        st.caption("Outage minutes per day (cached history)")
        if outage_data:
            outage_df = pd.DataFrame(outage_data)
            if (
                not outage_df.empty
                and "date" in outage_df.columns
                and "minutes" in outage_df.columns
            ):
                outage_df = outage_df.sort_values("date")
                st.bar_chart(outage_df, x="date", y="minutes", height=240)
            else:
                st.info("Outage history format is unexpected.")
        else:
            st.info("Collecting outage history — come back tomorrow.")

        st.write("")
        st.caption("Stage distribution (cached history)")
        if stage_data:
            stage_df = pd.DataFrame(stage_data)
            if (
                not stage_df.empty
                and "stage" in stage_df.columns
                and "count" in stage_df.columns
            ):
                st.bar_chart(stage_df, x="stage", y="count", height=240)
            else:
                st.info("Stage distribution format is unexpected.")
        else:
            st.info("Collecting stage history — come back tomorrow.")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.caption("Analytics will appear after fetching insights.")

# -----------------------------
# Footer (replace placeholders with your real links)
# -----------------------------
# Update these to your real profiles if you want:
WEBSITE_URL = "#"
LINKEDIN_URL = "#"
GITHUB_URL = "#"

st.markdown(
    f"""
    <div class="sla-shell">
      <div class="sla-footer">
        <div class="name">Created by Simukelo Ntshaba</div>
        <div class="sla-links">
          <a href="{WEBSITE_URL}" target="_blank" title="Website"><i class="fa-solid fa-globe"></i></a>
          <a href="{LINKEDIN_URL}" target="_blank" title="LinkedIn"><i class="fa-brands fa-linkedin-in"></i></a>
          <a href="{GITHUB_URL}" target="_blank" title="GitHub"><i class="fa-brands fa-github"></i></a>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
