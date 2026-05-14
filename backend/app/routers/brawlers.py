from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database import db
from ..models import Brawler, BrawlerListResponse, BrawlerStatsResponse

router = APIRouter(prefix="/brawlers", tags=["brawlers"])

@router.get("/", response_model=BrawlerListResponse)
async def get_all_brawlers(
    limit: int = Query(50, ge=1, le=100, description="Number of brawlers to return"),
    offset: int = Query(0, ge=0, description="Number of brawlers to skip"),
    class_filter: Optional[str] = Query(None, description="Filter by class"),
    rarity_filter: Optional[str] = Query(None, description="Filter by rarity")
):
    """Get all brawlers with optional filters"""
    
    # Build the query
    conditions = []
    params = []
    
    if class_filter:
        conditions.append("class = $" + str(len(params) + 1))
        params.append(class_filter)
    
    if rarity_filter:
        conditions.append("rarity = $" + str(len(params) + 1))
        params.append(rarity_filter)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM brawlers WHERE {where_clause}"
    total = await db.fetch_one(count_query, *params)
    total_count = total[0] if total else 0
    
    # Get brawlers
    query = f"SELECT * FROM brawlers WHERE {where_clause} ORDER BY name LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])
    
    rows = await db.fetch_all(query, *params)
    brawlers = [dict(row) for row in rows]
    
    return BrawlerListResponse(total=total_count, brawlers=brawlers)

@router.get("/{brawler_id}", response_model=Brawler)
async def get_brawler_by_id(brawler_id: int):
    """Get a specific brawler by ID"""
    
    row = await db.fetch_one("SELECT * FROM brawlers WHERE brawler_id = $1", brawler_id)
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Brawler with ID {brawler_id} not found")
    
    return dict(row)

@router.get("/name/{name}", response_model=Brawler)
async def get_brawler_by_name(name: str):
    """Get a specific brawler by name (case-insensitive)"""
    
    row = await db.fetch_one(
        "SELECT * FROM brawlers WHERE LOWER(name) = LOWER($1)", 
        name
    )
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Brawler with name '{name}' not found")
    
    return dict(row)

@router.get("/class/{class_name}", response_model=BrawlerListResponse)
async def get_brawlers_by_class(
    class_name: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all brawlers of a specific class"""
    
    total = await db.fetch_one(
        "SELECT COUNT(*) FROM brawlers WHERE LOWER(class) = LOWER($1)",
        class_name
    )
    total_count = total[0] if total else 0
    
    rows = await db.fetch_all(
        "SELECT * FROM brawlers WHERE LOWER(class) = LOWER($1) ORDER BY name LIMIT $2 OFFSET $3",
        class_name, limit, offset
    )
    
    brawlers = [dict(row) for row in rows]
    return BrawlerListResponse(total=total_count, brawlers=brawlers)

@router.get("/rarity/{rarity}", response_model=BrawlerListResponse)
async def get_brawlers_by_rarity(
    rarity: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all brawlers of a specific rarity"""
    
    total = await db.fetch_one(
        "SELECT COUNT(*) FROM brawlers WHERE LOWER(rarity) = LOWER($1)",
        rarity
    )
    total_count = total[0] if total else 0
    
    rows = await db.fetch_all(
        "SELECT * FROM brawlers WHERE LOWER(rarity) = LOWER($1) ORDER BY name LIMIT $2 OFFSET $3",
        rarity, limit, offset
    )
    
    brawlers = [dict(row) for row in rows]
    return BrawlerListResponse(total=total_count, brawlers=brawlers)

@router.get("/stats/legendary", response_model=list[BrawlerStatsResponse])
async def get_legendary_brawlers_stats():
    """Get all legendary brawlers with simplified stats"""
    
    rows = await db.fetch_all("""
        SELECT 
            name, 
            class, 
            base_health as health, 
            base_attack_damage as damage, 
            movement_speed as speed, 
            attack_range as range, 
            rarity
        FROM brawlers 
        WHERE rarity = 'Legendary'
        ORDER BY base_health DESC
    """)
    
    return [dict(row) for row in rows]

@router.get("/search/")
async def search_brawlers(
    q: str = "",
    limit: int = 20
):
    """Search brawlers by name (case-insensitive partial match)"""
    
    # If no search term, return empty
    if not q or len(q.strip()) < 1:
        return {"total": 0, "brawlers": []}
    
    # Clean the search term
    search_term = q.strip()
    
    # Use ILIKE for case-insensitive search
    rows = await db.fetch_all(
        "SELECT * FROM brawlers WHERE name ILIKE $1 ORDER BY name LIMIT $2",
        f"%{search_term}%", limit
    )
    
    brawlers = [dict(row) for row in rows]
    return {"total": len(brawlers), "brawlers": brawlers}