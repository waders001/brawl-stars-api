from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from .database import db
from .config import settings
from .routers import brawlers

# Get absolute path to frontend directory (adjusts to your project structure)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

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

# Serve static files (CSS, JS)
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

# Include routers
app.include_router(brawlers.router)

# API endpoints (keep these at /api or separate)
@app.get("/api")
async def api_root():
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

# Serve frontend HTML pages (now your site works!)
@app.get("/")
async def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/brawlers.html")
async def serve_brawlers():
    return FileResponse(os.path.join(FRONTEND_DIR, "brawlers.html"))

@app.get("/player.html")
async def serve_player():
    return FileResponse(os.path.join(FRONTEND_DIR, "player.html"))

@app.get("/rankings.html")
async def serve_rankings():
    return FileResponse(os.path.join(FRONTEND_DIR, "rankings.html"))