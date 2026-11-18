"""
AuraMystic — Uplifting Spiritual Sanctuary & Solar Astrology Portal
Production FastAPI Backend Server (NeuroSpicy Mystic)
"""
import os
import sqlite3
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

from .routers import accounts
from .services import memberships
from .database import ACCOUNT_ID
from .postgres import DatabaseUnavailable
import psycopg
app.include_router(accounts.router)
from .routers import love
app.include_router(love.router)

@app.exception_handler(DatabaseUnavailable)
@app.exception_handler(psycopg.Error)
async def postgres_unavailable(request, exc):
    import logging
    logging.getLogger(__name__).error('PostgreSQL request failed: %s', type(exc).__name__)
    return JSONResponse({'detail':'Account storage is temporarily unavailable.'}, status_code=503,
                        headers={'Cache-Control':'no-store'})



@app.middleware("http")
async def membership_access(request, call_next):
    path = request.url.path
    if not memberships.enabled() or request.method == 'OPTIONS' or not path.startswith('/api/') or path.startswith('/api/account/') or path == '/api/health':
        return await call_next(request)
    try:
        token = request.headers.get('authorization', '').removeprefix('Bearer ')
        member = memberships.session_user(token)
    except (RuntimeError, OSError, sqlite3.Error):
        return JSONResponse({'detail': 'Membership storage is unavailable.'}, status_code=503, headers={'Cache-Control':'no-store'})
    if not member:
        return JSONResponse({'detail': 'Please log in.'}, status_code=401, headers={'Cache-Control':'no-store'})
    if not member['active']:
        return JSONResponse({'detail': 'An active membership is required.'}, status_code=403, headers={'Cache-Control':'no-store'})
    context = ACCOUNT_ID.set(member['id'])
    try:
        return await call_next(request)
    finally:
        ACCOUNT_ID.reset(context)


@app.middleware("http")
async def public_response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get('/url-hygiene.js', include_in_schema=False)
def serve_url_hygiene():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'url-hygiene.js'), media_type='text/javascript')


@app.get('/robots.txt', include_in_schema=False)
def serve_robots():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'robots.txt'), media_type='text/plain')


@app.get('/sitemap.xml', include_in_schema=False)
def serve_sitemap():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'sitemap.xml'), media_type='application/xml')


@app.on_event("startup")
def on_startup():
    if memberships.enabled():
        storage_keys=[] if os.getenv('DATABASE_URL') else ['MEMBERSHIP_DB_PATH','MEMBERSHIP_USER_DATA_DIR']
        for key in storage_keys+['MEMBERSHIP_PUBLIC_URL','MEMBERSHIP_SUPPORT_EMAIL']:
            if not os.getenv(key):
                raise RuntimeError(key + ' is required before enabling membership protection.')
        if not os.environ['MEMBERSHIP_PUBLIC_URL'].startswith('https://') and os.getenv('RENDER'):
            raise RuntimeError('Production membership URLs require HTTPS.')
        for key in storage_keys:
            value = os.environ[key]
            if not os.path.isabs(value) or (os.getenv('RENDER') and value.startswith('/tmp/')):
                raise RuntimeError('Membership storage must use configured durable absolute paths.')
        with memberships.database():
            pass
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


@app.get("/ritual-world-data.js", include_in_schema=False)
def serve_ritual_world_data():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "ritual-world-data.js"), media_type="text/javascript")


@app.get("/ritual-library.js", include_in_schema=False)
def serve_ritual_library_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "ritual-library.js"), media_type="text/javascript")


@app.get("/ritual-library.css", include_in_schema=False)
def serve_ritual_library_styles():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "ritual-library.css"), media_type="text/css")


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

@app.get('/metadata.js', include_in_schema=False)
def serve_metadata_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'metadata.js'), media_type='text/javascript')


# The same 78 PNGs serve browsers and are bundled by Metro for iOS/Android.
# Keep this specific mount before the general /assets mount.
app.mount('/assets/tarot', StaticFiles(directory=os.path.join(os.path.dirname(__file__), '..', 'mobile', 'assets', 'tarot')), name='tarot-deck')

# Serve the approved Spiritual Vibez illustrated artwork as real image assets.
app.mount("/assets", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend", "assets")), name="spiritual-vibez-artwork")

@app.get('/membership.js', include_in_schema=False)
def serve_membership_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'membership.js'), media_type='text/javascript')

@app.get('/membership.css', include_in_schema=False)
def serve_membership_styles():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'membership.css'), media_type='text/css')


@app.get('/love.js', include_in_schema=False)
def serve_love_script():
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'love.js'), media_type='text/javascript')
