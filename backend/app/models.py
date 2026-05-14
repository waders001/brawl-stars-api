from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Brawler(BaseModel):
    brawler_id: int
    name: str
    class_name: Optional[str] = Field(None, alias="class")  # Handle 'class' keyword
    rarity: Optional[str] = None
    base_health: Optional[int] = None
    base_attack_damage: Optional[int] = None
    attack_range: Optional[float] = None
    movement_speed: Optional[int] = None
    trait: Optional[str] = None
    last_verified: Optional[date] = None
    data_source: Optional[str] = None
    
    class Config:
        populate_by_name = True

class BrawlerListResponse(BaseModel):
    total: int
    brawlers: list[Brawler]

class BrawlerStatsResponse(BaseModel):
    name: str
    class_name: str = Field(..., alias="class")
    health: int
    damage: int
    speed: int
    range: float
    rarity: str