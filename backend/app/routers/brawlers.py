import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from ..config import settings

router = APIRouter(prefix="/brawlers", tags=["brawlers"])

BRAWL_STARS_API_URL = "https://api.brawlstars.com/v1"
API_KEY = settings.brawl_stars_api_key

# Helper to fetch all brawlers from API (with caching optional)
async def fetch_all_brawlers() -> List[Dict[str, Any]]:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BRAWL_STARS_API_URL}/brawlers", headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch brawlers from Brawl Stars API")
        data = resp.json()
        return data.get("items", [])

# Transform raw API brawler to frontend expected format
def transform_brawler(brawler: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": brawler.get("id"),
        "name": brawler.get("name"),
        "class": brawler.get("class", {}).get("name") if brawler.get("class") else None,
        "rarity": brawler.get("rarity", {}).get("name") if brawler.get("rarity") else None,
        "base_health": brawler.get("health"),
        "base_attack_damage": brawler.get("attack", {}).get("damage") if brawler.get("attack") else None,
        "attack_range": brawler.get("attack", {}).get("range") if brawler.get("attack") else None,
        "movement_speed": brawler.get("speed"),
    }

@router.get("/")
async def get_all_brawlers(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    class_filter: Optional[str] = Query(None, alias="class_filter"),
    rarity_filter: Optional[str] = Query(None, alias="rarity_filter")
):
    """Get all brawlers with optional filters (pagination)."""
    try:
        brawlers = await fetch_all_brawlers()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Brawl Stars API unavailable")

    # Apply filters
    if class_filter:
        brawlers = [b for b in brawlers if b.get("class", {}).get("name") == class_filter]
    if rarity_filter:
        brawlers = [b for b in brawlers if b.get("rarity", {}).get("name") == rarity_filter]

    total = len(brawlers)
    paginated = brawlers[offset:offset + limit]
    transformed = [transform_brawler(b) for b in paginated]

    return {
        "total": total,
        "brawlers": transformed,
        "limit": limit,
        "offset": offset
    }

@router.get("/search/")
async def search_brawlers(
    q: str = "",
    limit: int = Query(20, ge=1, le=100)
):
    """Search brawlers by name (case-insensitive partial match)."""
    if not q or len(q.strip()) < 1:
        return {"total": 0, "brawlers": []}

    try:
        brawlers = await fetch_all_brawlers()
    except Exception:
        raise HTTPException(status_code=503, detail="Brawl Stars API unavailable")

    search_term = q.strip().lower()
    matched = [b for b in brawlers if search_term in b.get("name", "").lower()]
    matched = matched[:limit]
    transformed = [transform_brawler(b) for b in matched]

    return {"total": len(matched), "brawlers": transformed}

# The following endpoints are kept for compatibility, but they now
# fetch from the API and filter in memory (since no database).
@router.get("/{brawler_id}")
async def get_brawler_by_id(brawler_id: int):
    try:
        brawlers = await fetch_all_brawlers()
    except Exception:
        raise HTTPException(status_code=503, detail="Brawl Stars API unavailable")

    for b in brawlers:
        if b.get("id") == brawler_id:
            return transform_brawler(b)
    raise HTTPException(status_code=404, detail=f"Brawler with ID {brawler_id} not found")

@router.get("/name/{name}")
async def get_brawler_by_name(name: str):
    try:
        brawlers = await fetch_all_brawlers()
    except Exception:
        raise HTTPException(status_code=503, detail="Brawl Stars API unavailable")

    for b in brawlers:
        if b.get("name", "").lower() == name.lower():
            return transform_brawler(b)
    raise HTTPException(status_code=404, detail=f"Brawler with name '{name}' not found")

@router.get("/class/{class_name}")
async def get_brawlers_by_class(
    class_name: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    try:
        brawlers = await fetch_all_brawlers()
    except Exception:
        raise HTTPException(status_code=503, detail="Brawl Stars API unavailable")

    filtered = [b for b in brawlers if b.get("class", {}).get("name", "").lower() == class_name.lower()]
    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    transformed = [transform_brawler(b) for b in paginated]
    return {"total": total, "brawlers": transformed}

@router.get("/rarity/{rarity}")
async def get_brawlers_by_rarity(
    rarity: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    try:
        brawlers = await fetch_all_brawlers()
    except Exception:
        raise HTTPException(status_code=503, detail="Brawl Stars API unavailable")

    filtered = [b for b in brawlers if b.get("rarity", {}).get("name", "").lower() == rarity.lower()]
    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    transformed = [transform_brawler(b) for b in paginated]
    return {"total": total, "brawlers": transformed}

@router.get("/stats/legendary")
async def get_legendary_brawlers_stats():
    try:
        brawlers = await fetch_all_brawlers()
    except Exception:
        raise HTTPException(status_code=503, detail="Brawl Stars API unavailable")

    legendary = [b for b in brawlers if b.get("rarity", {}).get("name") == "Legendary"]
    result = []
    for b in legendary:
        result.append({
            "name": b.get("name"),
            "class": b.get("class", {}).get("name"),
            "health": b.get("health"),
            "damage": b.get("attack", {}).get("damage") if b.get("attack") else None,
            "speed": b.get("speed"),
            "range": b.get("attack", {}).get("range") if b.get("attack") else None,
            "rarity": "Legendary"
        })
    return result