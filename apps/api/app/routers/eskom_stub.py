from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.app.db.deps import get_db
from apps.api.app.services.cache_service import CacheService
from apps.api.app.services.eskom_client import EskomAPIError, EskomClient

router = APIRouter(prefix="/eskom", tags=["eskom"])
JOHANNESBURG_TZ = ZoneInfo("Africa/Johannesburg")


def _handle_eskom_error(exc: EskomAPIError) -> HTTPException:
    status_code = 503 if exc.status_code in {429, 500, 502, 503, 504} else 502
    return HTTPException(status_code=status_code, detail=exc.message)


@router.get("/status")
def eskom_status(db: Session = Depends(get_db)) -> dict:
    now = datetime.now(JOHANNESBURG_TZ)
    cache_key = f"status:current:{now:%Y-%m-%d}:{now:%H}"
    cache = CacheService(db).get_cached_request(cache_key, now)
    if cache:
        return {
            "source": "cache",
            "data": cache.data_json,
            "fetched_at": cache.fetched_at,
            "expires_at": cache.expires_at,
        }
    try:
        data = EskomClient().get_status_current()
    except EskomAPIError as exc:
        raise _handle_eskom_error(exc) from exc
    fetched_at = now
    expires_at = now + timedelta(minutes=30)
    stored = CacheService(db).set_cached_request(cache_key, data, fetched_at, expires_at)
    return {
        "source": "live",
        "data": stored.data_json,
        "fetched_at": stored.fetched_at,
        "expires_at": stored.expires_at,
    }


@router.get("/areas-search")
def eskom_area_search(
    text: str = Query(..., description="Search text"),
    db: Session = Depends(get_db),
) -> dict:
    normalized = text.strip().lower()
    now = datetime.now(JOHANNESBURG_TZ)
    cache = CacheService(db).get_area_lookup(normalized, now)
    if cache:
        return {
            "source": "cache",
            "data": cache.results_json,
            "fetched_at": cache.fetched_at,
            "expires_at": cache.expires_at,
        }
    try:
        data = EskomClient().search_areas(normalized)
    except EskomAPIError as exc:
        raise _handle_eskom_error(exc) from exc
    fetched_at = now
    expires_at = now + timedelta(hours=24)
    stored = CacheService(db).set_area_lookup(normalized, data, fetched_at, expires_at)
    return {
        "source": "live",
        "data": stored.results_json,
        "fetched_at": stored.fetched_at,
        "expires_at": stored.expires_at,
    }


@router.get("/area")
def eskom_area(id: str = Query(..., description="Area identifier"), db: Session = Depends(get_db)) -> dict:
    now = datetime.now(JOHANNESBURG_TZ)
    date_key = now.date().isoformat()
    cache_key = f"area:{id}:{date_key}"
    cache = CacheService(db).get_cached_request(cache_key, now)
    if cache:
        return {
            "source": "cache",
            "data": cache.data_json,
            "fetched_at": cache.fetched_at,
            "expires_at": cache.expires_at,
        }
    try:
        data = EskomClient().get_area(id)
    except EskomAPIError as exc:
        raise _handle_eskom_error(exc) from exc
    fetched_at = now
    end_of_day = datetime.combine(now.date(), time(23, 59, 59), tzinfo=JOHANNESBURG_TZ)
    stored = CacheService(db).set_cached_request(cache_key, data, fetched_at, end_of_day)
    return {
        "source": "live",
        "data": stored.data_json,
        "fetched_at": stored.fetched_at,
        "expires_at": stored.expires_at,
    }
