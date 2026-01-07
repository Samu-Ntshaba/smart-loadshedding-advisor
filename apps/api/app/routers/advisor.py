from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from apps.api.app.core.config import settings
from apps.api.app.db.deps import get_db
from apps.api.app.services.cache_service import CacheService
from apps.api.app.services.eskom_client import EskomAPIError, EskomClient

router = APIRouter(prefix="/advisor", tags=["advisor"])
JOHANNESBURG_TZ = ZoneInfo("Africa/Johannesburg")


class InsightsRequest(BaseModel):
    area_id: str = Field(..., description="Selected area identifier")
    area_name: str = Field(..., description="Selected area name")
    query: str = Field(..., description="User search query")
    notes: str | None = Field(None, description="Optional user context")


def _extract_stage(status_payload: dict) -> int:
    return int(status_payload.get("status", {}).get("eskom", {}).get("stage") or 0)


def _parse_iso(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str)


def _summarize_events(events: list[dict[str, Any]], now: datetime) -> dict:
    sorted_events = sorted(events, key=lambda event: event.get("start") or "")
    parsed_events: list[tuple[datetime, datetime]] = []
    for event in sorted_events:
        if not event.get("start") or not event.get("end"):
            continue
        try:
            start = _parse_iso(event["start"])
            end = _parse_iso(event["end"])
        except ValueError:
            continue
        parsed_events.append((start, end))

    next_outage = None
    for start, end in parsed_events:
        if start <= now <= end or start >= now:
            next_outage = {"start": start.isoformat(), "end": end.isoformat()}
            break

    day_start = datetime.combine(now.date(), time.min, tzinfo=JOHANNESBURG_TZ)
    day_end = datetime.combine(now.date(), time.max, tzinfo=JOHANNESBURG_TZ)
    total_minutes = 0
    for start, end in parsed_events:
        overlap_start = max(start, day_start)
        overlap_end = min(end, day_end)
        if overlap_start < overlap_end:
            total_minutes += int((overlap_end - overlap_start).total_seconds() / 60)

    return {
        "next_outage": next_outage,
        "total_outage_minutes_today": total_minutes,
    }


def _generate_ai_advice(
    area_name: str,
    stage: int,
    events: list[dict[str, Any]],
    notes: str | None,
) -> str:
    if not settings.openai_key:
        return "AI advice is unavailable because the OpenAI key is not configured."
    client = OpenAI(api_key=settings.openai_key)
    event_lines = "\n".join(
        f"- {event.get('start')} to {event.get('end')}" for event in events
    )
    notes_line = f"User notes: {notes}" if notes else "User notes: none"
    prompt = (
        "You are a South Africa energy advisor. Provide short, practical advice based only "
        "on the supplied schedule times. Do not invent new times.\n\n"
        f"Area: {area_name}\n"
        f"Stage: {stage}\n"
        f"Outage windows:\n{event_lines or '- none'}\n"
        f"{notes_line}\n\n"
        "Output format:\n"
        "Today at a glance: 2-3 short lines.\n"
        "Action plan: bullet list (max 8 bullets).\n"
        "Optional: battery/generator tips: 1-2 bullets.\n"
        "Include the disclaimer sentence exactly: Times may change if Eskom updates the schedule."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=350,
            messages=[
                {"role": "system", "content": "You are a concise, practical energy advisor."},
                {"role": "user", "content": prompt},
            ],
        )
    except Exception:
        return "AI advice is temporarily unavailable. Please try again later."
    return response.choices[0].message.content.strip()


@router.post("/insights")
def advisor_insights(payload: InsightsRequest, db: Session = Depends(get_db)) -> dict:
    now = datetime.now(JOHANNESBURG_TZ)
    cache_service = CacheService(db)

    status_key = f"status:current:{now:%Y-%m-%d}:{now:%H}"
    status_cache = cache_service.get_cached_request(status_key, now)
    status_source = "cache"
    if status_cache:
        status_data = status_cache.data_json
    else:
        try:
            status_data = EskomClient().get_status_current()
        except EskomAPIError as exc:
            raise HTTPException(status_code=503, detail=exc.message) from exc
        status_source = "live"
        cache_service.set_cached_request(
            status_key,
            status_data,
            now,
            now + timedelta(minutes=30),
        )

    area_key = f"area:{payload.area_id}:{now.date().isoformat()}"
    area_cache = cache_service.get_cached_request(area_key, now)
    area_source = "cache"
    if area_cache:
        area_data = area_cache.data_json
    else:
        try:
            area_data = EskomClient().get_area(payload.area_id)
        except EskomAPIError as exc:
            raise HTTPException(status_code=503, detail=exc.message) from exc
        area_source = "live"
        end_of_day = datetime.combine(now.date(), time(23, 59, 59), tzinfo=JOHANNESBURG_TZ)
        cache_service.set_cached_request(area_key, area_data, now, end_of_day)

    events = area_data.get("events", [])
    summary = _summarize_events(events, now)
    stage = _extract_stage(status_data)
    ai_advice = _generate_ai_advice(payload.area_name, stage, events, payload.notes)

    return {
        "stage": stage,
        "events": events,
        "summary": summary,
        "ai_advice": ai_advice,
        "cache": {"status": status_source, "area": area_source},
    }


@router.get("/analytics")
def advisor_analytics(area_id: str, db: Session = Depends(get_db)) -> dict:
    now = datetime.now(JOHANNESBURG_TZ)
    cache_service = CacheService(db)
    since = now - timedelta(days=7)

    area_cached = cache_service.list_cached_requests(f"area:{area_id}:", since)
    outage_minutes_per_day: list[dict[str, Any]] = []
    for entry in area_cached:
        date_key = entry.cache_key.split(":")[-1]
        events = entry.data_json.get("events", [])
        total_minutes = 0
        for event in events:
            try:
                start = _parse_iso(event["start"])
                end = _parse_iso(event["end"])
            except (KeyError, ValueError):
                continue
            total_minutes += int((end - start).total_seconds() / 60)
        outage_minutes_per_day.append({"date": date_key, "minutes": total_minutes})

    status_cached = cache_service.list_cached_requests("status:current:", since)
    stage_counts: dict[str, int] = {}
    for entry in status_cached:
        stage = _extract_stage(entry.data_json)
        stage_counts[str(stage)] = stage_counts.get(str(stage), 0) + 1

    stage_distribution = [
        {"stage": stage, "count": count} for stage, count in sorted(stage_counts.items())
    ]

    return {
        "outage_minutes_per_day": outage_minutes_per_day,
        "stage_distribution": stage_distribution,
    }
