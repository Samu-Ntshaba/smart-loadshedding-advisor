from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.db.models import AreaLookup, CachedRequest


class CacheService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_cached_request(self, key: str, now: datetime) -> CachedRequest | None:
        statement = select(CachedRequest).where(
            CachedRequest.cache_key == key,
            CachedRequest.expires_at > now,
        )
        return self.session.execute(statement).scalars().first()

    def set_cached_request(
        self,
        key: str,
        data: dict,
        fetched_at: datetime,
        expires_at: datetime,
    ) -> CachedRequest:
        statement = select(CachedRequest).where(CachedRequest.cache_key == key)
        existing = self.session.execute(statement).scalars().first()
        if existing:
            existing.data_json = data
            existing.fetched_at = fetched_at
            existing.expires_at = expires_at
            cached = existing
        else:
            cached = CachedRequest(
                cache_key=key,
                data_json=data,
                fetched_at=fetched_at,
                expires_at=expires_at,
            )
            self.session.add(cached)
        self.session.commit()
        self.session.refresh(cached)
        return cached

    def get_area_lookup(self, query_text: str, now: datetime) -> AreaLookup | None:
        statement = select(AreaLookup).where(
            AreaLookup.query_text == query_text,
            AreaLookup.expires_at > now,
        )
        return self.session.execute(statement).scalars().first()

    def set_area_lookup(
        self,
        query_text: str,
        results: dict,
        fetched_at: datetime,
        expires_at: datetime,
    ) -> AreaLookup:
        statement = select(AreaLookup).where(AreaLookup.query_text == query_text)
        existing = self.session.execute(statement).scalars().first()
        if existing:
            existing.results_json = results
            existing.fetched_at = fetched_at
            existing.expires_at = expires_at
            lookup = existing
        else:
            lookup = AreaLookup(
                query_text=query_text,
                results_json=results,
                fetched_at=fetched_at,
                expires_at=expires_at,
            )
            self.session.add(lookup)
        self.session.commit()
        self.session.refresh(lookup)
        return lookup

    def list_cached_requests(self, prefix: str, since: datetime) -> list[CachedRequest]:
        statement = (
            select(CachedRequest)
            .where(
                CachedRequest.cache_key.like(f"{prefix}%"),
                CachedRequest.fetched_at >= since,
            )
            .order_by(CachedRequest.fetched_at.desc())
        )
        return list(self.session.execute(statement).scalars().all())
