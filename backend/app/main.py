from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import db
from .config import settings
from .routers import brawlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(brawlers.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Brawl Stars API",
        "version": settings.api_version,
        "endpoints": {
            "brawlers": "/brawlers",
            "brawler_by_id": "/brawlers/{brawler_id}",
            "brawler_by_name": "/brawlers/name/{name}",
            "brawlers_by_class": "/brawlers/class/{class_name}",
            "brawlers_by_rarity": "/brawlers/rarity/{rarity}",
            "legendary_stats": "/brawlers/stats/legendary",
            "search": "/brawlers/search/?q={query}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}