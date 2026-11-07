# Spiritual Vibez — repair and reference UI verification

Updated November 7, 2026. The PR check runs provide hosted results for the latest commit.

The supplied reference images guide the purple/pink skyline, transparent character,
handwritten typography, illustrated modules, glowing cards and navigation. The brand
remains **Spiritual Vibez — Zodiac, Tarot & More**. Native Home uses the standalone
Hey Mystic illustration. Its four primary tabs are Home, Spreads, Learn and Journal;
Cosmos and Explore remain independent destinations opened through Home/Journal cards.
The web navigation has Home, Spreads, Learn Tarot, Cosmos and Journal; Explore opens
from the search icon and feature tiles.

## Checks and limits

| Check | Result |
| --- | --- |
| Mobile PNG resolution | Pass: all 28 static local references resolve across every JS/TS/JSX/TSX source, including nested components and unused requires. All 24 panels remain mapped. |
| Asset-validator regressions | Six pass, including newly introduced missing requires, case mismatches, empty PNGs, WebP imports, absent panel mappings and nonzero CLI exits. |
| Web assets and typography | Four checks pass: rendered PNGs/CSS backgrounds exist, no WebP URLs, local licensed fonts and canonical spread mappings. Decorative web feature icons use inline SVG with live text. |
| TypeScript | Pass, including the native interaction tests. |
| Native interactions and API routes | 25 pass: navigation, card proportions, distinct study counts, quiz attempts, spread filters and live catalog layouts, journal persistence and all 18 network-backed native tool methods/paths. |
| Metro Android and iOS | Both production bundles and asset exports pass locally. |
| Native Android | The first PR revision passed arm64 assembleDebug in hosted CI. The latest revision repeats that job and retains the debug APK for seven days. Consult the latest PR check before relying on its result. |
| Backend | The existing 28-check script and all 15 HTTP/pytest checks pass locally. Ritual keyword search now also has regression coverage. |
| Connected web flows | 17 backend-backed tools pass, plus cycle estimates, learning modules, quiz, a full spread, synthesis, saved readings, journal notes, moods and transits. No API failures or JavaScript errors were observed. |
| Browser layouts | Home, Spreads, Learn Tarot and Journal pass at 1448px and 390px with every displayed image loaded and no horizontal overflow. |
| Native iOS build / simulator | Unavailable on this Linux workspace. iOS Metro validation and resource checks do not replace Xcode compilation. |
| Device visuals and behavior | Still require Android/iOS device or simulator checks, including fonts, safe areas, touch targets, keyboard behavior and connectivity. Exact native visual equivalence is not verified. |

Run `python frontend/tests/browser_flows.py --screenshots work/browser-evidence`
after installing `frontend/tests/requirements.txt`. It starts FastAPI against a
temporary database, uses installed Chrome/Chromium, exercises the connected flows,
and captures evidence. CI runs it too.

## Screenshots

These are browser captures of the web app, including phone-width views. They are
not native simulator screenshots.

| Screen | Desktop | Phone width |
| --- | --- | --- |
| Home | [View](web-desktop-home.png) | [View](web-mobile-home.png) |
| Spreads | [View](web-desktop-spreads.png) | [View](web-mobile-spreads.png) |
| Learn Tarot | [View](web-desktop-learn.png) | [View](web-mobile-learn.png) |
| Journal | [View](web-desktop-journal.png) | [View](web-mobile-journal.png) |

## Working paths and backend repairs

The illustrated names map to real backend IDs without replacing the backend's
questions or counts: Trust Your Gut → `trust-your-gut`; At a Crossroads →
`at-a-crossroads` (10 cards); The Next Phase → `stepping-into-new-timeline`;
Grounding → `mindfulness-calm`. This fixes missing/nonfunctional featured buttons
when the live catalog loads.

Ritual search formerly read a nonexistent `tools` field although the source data
stores materials under `items`. It now normalizes that field and safely searches
optional fields. Browser testing found this failure after the older suite passed.

All four product deep links in the original catalog returned HTTP 404. The creator
homepage, https://neurospicymystic.com/, returned HTTP 200. Product buttons now say
"Visit creator store" and use that working homepage until real product URLs are
supplied. This does not establish that any checkout or purchase completes.

Existing astrology calculations remain approximate; timezone and scientific
accuracy have not been certified by this UI/route repair. No paid AI, payment
provider, authentication system or external deployment was added.

## Artwork and native host audit

Every retained PNG decodes. The three character layers have genuine alpha channels
with fully transparent and fully opaque pixels:

| Layer | Dimensions | Fully transparent pixels |
| --- | --- | --- |
| hero-mystic-cutout / cartoon_me_transparent3 | 1122 × 1402 | 528,963 |
| avatar-sunglasses / cartoon_me_transparent2 | 1254 × 1254 | 491,815 |
| avatar-tarot-headphones / cartoon_me_transparent1 | 1254 × 1254 | 610,615 |

Native learning counters/bars and spread counts cover sample values painted into
the artwork. No deleted crop was restored. Licensed Pacifico and Kaushan Script
fonts are linked into both native hosts; the web also bundles DM Sans. License
notices accompany the fonts.

The nested native trees were identical copies. The CLI points at `mobile/android`
and `mobile/ios`; only the duplicate nested copies were removed. Scaffolding now
copies directory contents and no longer regenerates old mobile images.

Official checkout v7, setup-node v7, setup-java v6, setup-python v7 and
upload-artifact v7 were checked for Node 24 support. CI uses Ubuntu 24.04,
Node 24 and the committed npm lockfile. RN screens is pinned to 4.25.2 for RN 0.83.
