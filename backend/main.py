"""
AuraMystic — Uplifting Spiritual Sanctuary & Solar Astrology Portal
Production FastAPI Backend Server (NeuroSpicy Mystic)
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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
        "Placidus/BaZi/Astrocartography Charts, Divination Hub, AI Mystic Oracle, "
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


@app.get("/styles.css", include_in_schema=False)
def serve_styles():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "styles.css"), media_type="text/css")

@app.get("/liquid-glass.css", include_in_schema=False)
def serve_liquid_glass_styles():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "liquid-glass.css"), media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def serve_app_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "app.js"), media_type="text/javascript")

@app.get("/guide.svg", include_in_schema=False)
def serve_guide_illustration():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "guide.svg"), media_type="image/svg+xml")


@app.get("/rune-library.js", include_in_schema=False)
def serve_rune_library():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "rune-library.js"), media_type="text/javascript")

@app.get("/rune-casting.js", include_in_schema=False)
def serve_rune_casting():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "rune-casting.js"), media_type="text/javascript")


@app.get('/artwork.js', include_in_schema=False)
def serve_artwork_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'artwork.js'), media_type='text/javascript')


@app.get('/cosmic.js', include_in_schema=False)
def serve_cosmic_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'cosmic.js'), media_type='text/javascript')


@app.get('/content-format.js', include_in_schema=False)
def content_format_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'content-format.js'), media_type='text/javascript')


@app.get('/content-actions.js', include_in_schema=False)
def content_actions_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'content-actions.js'), media_type='text/javascript')

@app.get('/learning.js', include_in_schema=False)
def serve_learning_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'learning.js'), media_type='text/javascript')

@app.get('/equinox-calendar.js', include_in_schema=False)
def serve_equinox_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'equinox-calendar.js'), media_type='text/javascript')

@app.get('/astro-map-tools.js', include_in_schema=False)
def serve_map_tools_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'astro-map-tools.js'), media_type='text/javascript')

@app.get('/astrocartography.js', include_in_schema=False)
def serve_astrocartography_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'astrocartography.js'), media_type='text/javascript')


# The same 78 PNGs serve browsers and are bundled by Metro for iOS/Android.
# Keep this specific mount before the general /assets mount.
app.mount('/assets/tarot', StaticFiles(directory=os.path.join(os.path.dirname(__file__), '..', 'mobile', 'assets', 'tarot')), name='tarot-deck')

# Serve the approved Spiritual Vibez illustrated artwork as real image assets.
app.mount("/assets", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend", "assets")), name="spiritual-vibez-artwork")
