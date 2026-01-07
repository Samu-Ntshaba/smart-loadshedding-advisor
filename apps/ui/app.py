import os

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Smart Loadshedding Advisor", layout="wide")
st.markdown(
    """
    <style>
    .sla-hero {
        background: linear-gradient(135deg, #0b1f3a 0%, #102b52 55%, #16406b 100%);
        color: #ffffff;
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 18px;
        box-shadow: 0 12px 24px rgba(15, 30, 60, 0.35);
    }
    .sla-hero h1 {
        font-size: 32px;
        margin: 0 0 6px 0;
    }
    .sla-hero p {
        margin: 0;
        opacity: 0.85;
    }
    .sla-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #e6ecf5;
        box-shadow: 0 8px 16px rgba(17, 24, 39, 0.08);
    }
    .sla-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        background: #eef4ff;
        color: #1e3a8a;
        margin-left: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="sla-hero">
        <h1>Smart Loadshedding Advisor</h1>
        <p>AI-powered Eskom schedule insights for South Africa — plan smarter, stay powered.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str, params: dict | None = None) -> dict:
    response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict) -> dict:
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


if "area_results" not in st.session_state:
    st.session_state.area_results = []
if "insights" not in st.session_state:
    st.session_state.insights = None
if "analytics" not in st.session_state:
    st.session_state.analytics = None

with st.sidebar:
    st.header("Find your area")
    st.caption("Powered by EskomSePush • Electricity advisory")
    query = st.text_input("Search area", placeholder="e.g. Fourways", key="search_query")
    if st.button("Search Eskom areas", use_container_width=True):
        if not query.strip():
            st.warning("Enter an area name to search.")
        else:
            try:
                response = api_get("/eskom/areas-search", params={"text": query})
                data = response.get("data", {})
                st.session_state.area_results = data.get("areas", data.get("results", []))
                st.success(f"Found {len(st.session_state.area_results)} areas.")
            except requests.RequestException as exc:
                st.error(f"Area search failed: {exc}")

    area_options = st.session_state.area_results
    area_labels = [
        f"{area.get('name')} ({area.get('region')})"
        if area.get("region")
        else area.get("name")
        for area in area_options
    ]
    if area_labels:
        selected_index = st.selectbox(
            "Select area",
            options=list(range(len(area_labels))),
            format_func=lambda idx: area_labels[idx],
        )
    else:
        st.selectbox("Select area", options=["No results yet"], disabled=True)
        selected_index = 0
    notes = st.text_area("Notes (optional)", placeholder="WFH 9-5, medical equipment, etc.")

    if st.button("Get Advice", use_container_width=True, type="primary"):
        if not area_options:
            st.warning("Search for an area first.")
        else:
            selected_area = area_options[selected_index]
            payload = {
                "area_id": selected_area.get("id"),
                "area_name": selected_area.get("name"),
                "query": query,
                "notes": notes or None,
            }
            try:
                st.session_state.insights = api_post("/advisor/insights", payload)
                st.session_state.analytics = api_get(
                    "/advisor/analytics", params={"area_id": selected_area.get("id")}
                )
            except requests.RequestException as exc:
                st.error(f"Advisor request failed: {exc}")


insights = st.session_state.insights
analytics = st.session_state.analytics

left, right = st.columns([2, 1])

with left:
    st.subheader("Today's Outlook")
    if insights:
        stage = insights.get("stage", 0)
        summary = insights.get("summary", {})
        cache = insights.get("cache", {})
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Eskom Stage", f"Stage {stage}")
        next_outage = summary.get("next_outage")
        col2.metric(
            "Next Outage",
            "Scheduled" if next_outage else "None",
            next_outage.get("start") if next_outage else "No outages today",
        )
        col3.metric(
            "Total Outage Minutes Today",
            summary.get("total_outage_minutes_today", 0),
        )
        st.markdown(
            f"Status source: <span class='sla-badge'>{cache.get('status', 'live')}</span> "
            f"Area source: <span class='sla-badge'>{cache.get('area', 'live')}</span>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Search for an area and click Get Advice to view your schedule.")

    st.subheader("Upcoming outages")
    if insights:
        events = insights.get("events", [])
        if events:
            st.dataframe(
                [
                    {
                        "Start": event.get("start"),
                        "End": event.get("end"),
                        "Note": event.get("note", ""),
                    }
                    for event in events
                ],
                use_container_width=True,
            )
        else:
            st.info("No upcoming outages reported for this area.")

    st.subheader("AI Advice")
    if insights:
        advice = insights.get("ai_advice", "No advice available.")
        advice_html = advice.replace("\n", "<br/>")
        st.markdown(
            f"<div class='sla-card'>{advice_html}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("AI advice will appear after fetching insights.")

with right:
    st.subheader("Analytics")
    if analytics:
        outage_data = analytics.get("outage_minutes_per_day", [])
        stage_data = analytics.get("stage_distribution", [])

        if outage_data:
            outage_df = pd.DataFrame(outage_data).sort_values("date")
            st.caption("Outage minutes per day (cached history)")
            st.bar_chart(outage_df, x="date", y="minutes", height=240)
        else:
            st.info("Collecting outage history — come back tomorrow.")

        if stage_data:
            stage_df = pd.DataFrame(stage_data)
            st.caption("Stage distribution (cached history)")
            st.bar_chart(stage_df, x="stage", y="count", height=240)
        else:
            st.info("Collecting stage history — come back tomorrow.")
    else:
        st.caption("Analytics appear after fetching insights.")
