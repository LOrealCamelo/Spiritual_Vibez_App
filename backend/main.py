"""
AuraMystic — Uplifting Spiritual Sanctuary & Solar Astrology Portal
Production FastAPI Backend Server (NeuroSpicy Mystic)
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from .database import init_db
from .routers import astrology, synastry, tarot, rituals, wellness, divination, oracle_ai, store

app = FastAPI(
    title="AuraMystic API — NeuroSpicy Mystic",
    description=(
        "Production Full-Stack Backend powering AuraMystic: Daily Ephemeris & Transits, "
        "Natal Moon Phase, Numerology & Love Synastry, 78-Card Tarot Studio & 48 Spreads, "
        "Solfeggio Frequencies & Rituals, Lunar Menstrual Cycle & Shadow Work Journal, "
        "Placidus/Draconic/BaZi/Astrocartography Charts, Divination Hub, AI Mystic Oracle, "
        "and the Official NeuroSpicy Mystic Storefront (neurospicymystic.com)."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# Mount all 8 production routers
app.include_router(astrology.router, prefix="/api/astrology", tags=["1. Cosmos, Transits & Multi-System Charts"])
app.include_router(synastry.router, prefix="/api/synastry", tags=["2. Numerology & Relationship Synastry"])
app.include_router(tarot.router, prefix="/api/tarot", tags=["3. Tarot Study Academy & 48 Spreads Studio"])
app.include_router(rituals.router, prefix="/api/rituals", tags=["4. Solfeggio Frequencies, Rituals & Fertility"])
app.include_router(wellness.router, prefix="/api/wellness", tags=["5. Lunar Menstrual Cycle & Shadow Work Vault"])
app.include_router(divination.router, prefix="/api/divination", tags=["6. Divination Hub: Pendulum & Elder Futhark Runes"])
app.include_router(oracle_ai.router, prefix="/api/oracle", tags=["7. The AuraMystic AI Oracle Companion"])
app.include_router(store.router, prefix="/api/store", tags=["8. NeuroSpicy Mystic Sanctuary Storefront"])

@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "app": "AuraMystic — NeuroSpicy Mystic Sanctuary API",
        "version": "2.0.0",
        "store_url": "https://www.neurospicymystic.com",
        "docs_url": "/docs",
        "modules": [
            "/api/astrology",
            "/api/synastry",
            "/api/tarot",
            "/api/rituals",
            "/api/wellness",
            "/api/divination",
            "/api/oracle",
            "/api/store"
        ]
    }

@app.get("/", include_in_schema=False)
def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return JSONResponse(content=health_check())
