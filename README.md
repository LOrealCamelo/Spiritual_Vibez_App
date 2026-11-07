# Spiritual Vibez — Zodiac, Tarot & More

Production-ready Git repository containing the complete **FastAPI Backend**, **SQLite Persistence Layer**, **Astronomical/Ephemeris Calculation Engine**, **Interactive Web Application**, and **Bare React Native CLI Mobile Client (no Expo)** for **AuraMystic** by **NeuroSpicy Mystic** ([neurospicymystic.com](https://www.neurospicymystic.com)).

## Repository Structure

```text
auramystic-repo/
├── backend/
│   ├── main.py                      # FastAPI server entry point, CORS, health check & static hosting
│   ├── database.py                  # SQLite schema & persistence (journals, readings, cycles, streaks, cart)
│   ├── models.py                    # Pydantic v2 request/response validation schemas
│   ├── requirements.txt             # Python dependencies
│   ├── data/
│   │   └── master_data.json         # Complete 78 Tarot cards, 48 spreads, rituals, frequencies, houses & asteroids
│   ├── services/
│   │   └── ephemeris_engine.py      # Real Julian Day, lunar phase, Placidus/Draconic, 13-Moon, BaZi & Astrocartography engine
│   ├── routers/
│   │   ├── astrology.py             # /api/astrology/* (Transits, Moon Phase, Natal/Placidus/Draconic, 13-Moon, BaZi, Relocation)
│   │   ├── synastry.py              # /api/synastry/* (Life Path, Master Numbers 11/22/33, Love Compatibility & 4 Sub-scores)
│   │   ├── tarot.py                 # /api/tarot/* (78-Card Encyclopedia, Study Quiz, Peek, 48 Spreads, Reset Your Energy)
│   │   ├── rituals.py               # /api/rituals/* (8 Solfeggio Frequencies, Ritual Finder, Eugen Jonas Lunar Fertility)
│   │   ├── wellness.py              # /api/wellness/* (Lunar Menstrual Cycle Tracker & Private Shadow Work Journal CRUD)
│   │   ├── divination.py            # /api/divination/* (Amethyst Crystal Pendulum Dowsing & Elder Futhark 3-Rune Casting)
│   │   ├── oracle_ai.py             # /api/oracle/* (The AuraMystic AI Oracle Synthesis Engine & Chat History)
│   │   └── store.py                 # /api/store/* (NeuroSpicy Mystic Storefront Catalog & Shopping Bag)
│   └── tests/
│       └── test_all_endpoints.py    # Automated verification test suite covering all 8 routers
├── frontend/
│   └── index.html                   # Self-contained interactive web app with all 9 clickable tabs + Store
├── mobile/
│   ├── App.tsx                      # Bare React Native CLI 6-tab mobile navigation client
│   ├── package.json                 # React Native CLI dependencies
│   └── src/api/spiritualVibezClient.ts  # TypeScript API client wired to the FastAPI backend
├── Dockerfile                       # Production container build
├── docker-compose.yml               # Local Docker Compose orchestration with persistent SQLite volume
├── render.yaml                      # 1-Click Render deployment blueprint
├── .env.example                     # Environment variable template
└── .gitignore                       # Git ignore rules
```

## Quick Start (Local Development)

### 1. Run the FastAPI Backend & Web App

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

- **Web App UI**: Open `http://localhost:8000/`
- **Interactive Swagger API Docs**: Open `http://localhost:8000/docs`
- **Health Check**: Open `http://localhost:8000/api/health`

### 2. Run Automated Backend Tests

```bash
python3 backend/tests/test_all_endpoints.py
```

### 3. Deploy to Render (1-Click Blueprint)

1. Push this repository to GitHub (`git init && git add . && git commit -m "Initial commit"`).
2. In Render, click **New +** -> **Blueprint** and connect this repository (`render.yaml` is pre-configured).
# Spiritual_Vibez_App

For the bare Android/iOS client, installation and build checks, see [mobile/README.md](mobile/README.md).
