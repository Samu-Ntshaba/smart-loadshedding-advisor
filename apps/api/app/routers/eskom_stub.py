from fastapi import APIRouter, Query

router = APIRouter(prefix="/eskom", tags=["eskom"])


@router.get("/status")
def eskom_status() -> dict:
    return {
        "mock": True,
        "status": "not_connected",
        "detail": "EskomSePush integration will be added in Phase 2.",
    }


@router.get("/areas-search")
def eskom_area_search(text: str = Query(..., description="Search text")) -> dict:
    return {
        "mock": True,
        "query": text,
        "results": [
            {"id": "area-1", "name": "Mock Area 1"},
            {"id": "area-2", "name": "Mock Area 2"},
        ],
    }


@router.get("/area")
def eskom_area(id: str = Query(..., description="Area identifier")) -> dict:
    return {
        "mock": True,
        "area": {
            "id": id,
            "name": "Mock Area",
            "events": [],
        },
    }
