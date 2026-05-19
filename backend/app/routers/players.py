import httpx
from fastapi import APIRouter, HTTPException
from ..config import settings

router = APIRouter(prefix="/players", tags=["players"])

BRAWL_STARS_API_URL = "https://api.brawlstars.com/v1"
API_KEY = settings.brawl_stars_api_key

@router.get("/{player_tag}")
async def get_player(player_tag: str):
    """
    Get player information by tag
    Example: #2PPU9VUR or 2PPU9VUR
    """
    # Remove # if present and encode properly
    clean_tag = player_tag.replace("#", "")
    encoded_tag = f"%23{clean_tag}"
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BRAWL_STARS_API_URL}/players/{encoded_tag}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Player not found")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="Invalid API key or access denied")
            elif response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later")
            else:
                raise HTTPException(status_code=response.status_code, detail="Error fetching player data")
                
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Brawl Stars API is unavailable")

@router.get("/{player_tag}/battlelog")
async def get_player_battlelog(player_tag: str, limit: int = 10):
    """
    Get recent battles for a player
    """
    clean_tag = player_tag.replace("#", "")
    encoded_tag = f"%23{clean_tag}"
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BRAWL_STARS_API_URL}/players/{encoded_tag}/battlelog",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    data["items"] = data["items"][:limit]
                return data
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Player not found")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="Invalid API key or access denied")
            else:
                raise HTTPException(status_code=response.status_code, detail="Error fetching battle log")
                
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Brawl Stars API is unavailable")