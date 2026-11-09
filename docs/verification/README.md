# Spiritual Vibez — repair and reference UI verification

Updated November 9, 2026. GitHub Actions provides hosted results for each revision.

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
| Mobile PNG resolution | Pass: all 89 static local references resolve across every JS/TS/JSX/TSX source, including nested components and unused requires. All 24 panels remain mapped. |
| Asset-validator regressions | Six pass, including newly introduced missing requires, case mismatches, empty PNGs, WebP imports, absent panel mappings and nonzero CLI exits. |
| Web assets and typography | Eight checks pass: rendered PNGs/CSS backgrounds exist, no WebP URLs, local licensed fonts and canonical spread mappings. Home uses recreated panels with live text and new illustrations. All four new web/native illustration packs and all 24 panel definitions match; filters and labels are live UI elements. |
| TypeScript | Pass, including the native interaction tests. |
| Native interactions and API routes | 29 pass: navigation, card proportions, distinct study counts, quiz attempts, spread filters and live catalog layouts, journal persistence and native tool methods/paths, city selection, local birth-time submission, real card images and automatic daily sky plus the direct store link. |
| Metro Android and iOS | Both production bundles and asset exports pass locally. |
| Native Android | The first PR revision passed arm64 assembleDebug in hosted CI. The latest revision repeats that job and retains the debug APK for seven days. Consult the latest PR check before relying on its result. |
| Backend | The existing 28-check script and all 52 HTTP/pytest checks pass locally. Ritual keyword search now also has regression coverage. |
| Connected web flows | 15 backend-backed tools pass, plus cycle estimates, learning modules, quiz, a full spread, synthesis, saved readings, journal notes, moods and transits. No API failures or JavaScript errors were observed. |
| Browser layouts | Home, Spreads, Learn Tarot and Journal pass at 1448px and 390px with every displayed image loaded and no horizontal overflow. |
| Native iOS build / simulator | The cloud macOS/Xcode job built the Release app, launched it on iPhone 16 / iOS 18.5 and captured the native Home screen. Check the latest CI result for the current revision. |
| Device visuals and behavior | Still require Android/iOS device or simulator checks, including fonts, safe areas, touch targets, keyboard behavior and connectivity. The native Home screenshot was inspected; full device/interaction equivalence is not certified. |

Run `python frontend/tests/browser_flows.py --screenshots work/browser-evidence`
after installing `frontend/tests/requirements.txt`. It starts FastAPI against a
temporary database, uses installed Chrome/Chromium, exercises the connected flows,
and captures evidence. CI runs it too.

## Clear glass and platform separation

The home headline is **Your journey starts here**. Clear liquid glass appears
behind the illustrations, spread rows, reading surfaces and footer tabs. Reflected
edges and mild web refraction replace the opaque pastel fills; no frosted blur
is applied. Native uses transparent reflective surfaces without browser-specific
refraction. See [implementation and journal storage](../CLEAR_GLASS.md).

Journal checks include a browser reload and a native screen reopen. Entries,
readings and moods remain local to that browser/device, with no cloud sync.

The `web/desktop/` and `web/phone/` folders contain website captures. Native evidence
belongs in `mobile/` and the iOS simulator CI artifact. A phone-width Web preview
is not a native Mobile screenshot.

## Illustrated UI placement

[All 24 panels and their destinations](../UI_ARTWORK_PLACEMENT.md) now use 16 freshly
generated illustrations, live labels, gradients, borders, arrows and progress.
The four 1254 × 1254 RGBA source packs are copied unchanged between Web and Mobile;
each icon has a 627 × 627 source region and displays at 130 logical pixels or less.
The old blurry PNG crops and their web copies were removed. The existing larger
character/scenic/favorite illustrations and the 78 tarot cards remain in use.

Eight web asset checks validate source resolution, file identity, matching panel
definitions, all 24 live titles, actions and the absence of old panel image URLs.
Twenty-nine native checks include readable labels, navigation, filters, progress
and the unchanged chart/calendar flows. Eight new desktop/phone screenshots below
show the rebuilt panels. A [3× density phone capture](web/phone/panels-3x.png)
shows the new artwork and live typography at 1170-pixel viewport resolution.

## New astrology and tarot checks

The current repair adds all 78 uploaded card images to both native bundles and the web server. With the owner’s approval, the app now uses 648 × 1080 PNG display copies: 95.7 MiB versus 231.7 MiB for the untouched originals. All card borders and labels are preserved. Connected browser checks cover the city-based birth form, SVG wheel, detailed printable report, Tropical/Sidereal changes, ten daily planet positions, date selection and different Virgo/Pisces reflections. The latest backend CI run retains chart/sky/tarot evidence. Review the [chart wheel](web/desktop/birth-chart.png), [phone-width chart](web/phone/birth-chart.png), [daily sky](web/desktop/daily-sky.png), [tarot reading](web/desktop/tarot-reading.png) and [24-page sample report](web/desktop/birth-chart-report.pdf).

The existing Moon Phases section now includes a monthly grid and daily list with
1900–2100 browsing, phase illustrations, exact phase times and Moon sign ingresses.
Checks cover local dates, leap years, skipped dates, a 25-hour DST day, screenshot
ingress fixtures and independent phase-time fixtures. Body associations are labeled
astrology lore, and surgery safety is referred to the surgical team. The Draconic
chart was removed from both apps and the API.

The natal report adds modern/traditional house rulers, ruler locations, house
occupants, four chart angles and applying/separating aspects. Its sidebar shows
planet/zodiac symbols, degrees, houses and a Zodiac dropdown; it reflows below the
wheel on phones. See the [birth report sidebar](web/desktop/birth-report-sidebar.png) and
[monthly lunar calendar with daily details](web/desktop/moon-calendar.png) and its
[phone layout](web/phone/moon-calendar.png).

## Screenshots

These are browser captures of the web app, including phone-width views. They are
not native simulator screenshots.

| Screen | Desktop | Phone width |
| --- | --- | --- |
| Home | [View](web/desktop/home.png) | [View](web/phone/home.png) |
| Spreads | [View](web/desktop/spreads.png) | [View](web/phone/spreads.png) |
| Learn Tarot | [View](web/desktop/learn.png) | [View](web/phone/learn.png) |
| Journal | [View](web/desktop/journal.png) | [View](web/phone/journal.png) |

## Working paths and backend repairs

The illustrated names map to real backend IDs without replacing the backend's
questions or counts: Trust Your Gut → `trust-your-gut`; At a Crossroads →
`at-a-crossroads` (10 cards); The Next Phase → `stepping-into-new-timeline`;
Grounding → `mindfulness-calm`. This fixes missing/nonfunctional featured buttons
when the live catalog loads.

Ritual search formerly read a nonexistent `tools` field although the source data
stores materials under `items`. It now normalizes that field and safely searches
optional fields. Browser testing found this failure after the older suite passed.

The owner wants products and checkout on https://neurospicymystic.com/ only.
Both apps expose one **Visit my store** link and no product listings, prices or
per-product buttons. The link works without calling the backend catalog endpoint.

Birth-chart and daily-sky calculations now use Astronomy Engine, historical city timezones and real Placidus houses; see [methods and numerical checks](../ASTROLOGY_AND_TAROT.md). Other legacy astrology tools are outside that numerical validation. No paid AI, payment
provider, authentication system or external deployment was added.

## Artwork and native host audit

Every retained PNG decodes. The three character layers have genuine alpha channels
with fully transparent and fully opaque pixels:

| Layer | Dimensions | Fully transparent pixels |
| --- | --- | --- |
| hero-mystic-cutout / cartoon_me_transparent3 | 1122 × 1402 | 528,963 |
| avatar-sunglasses / cartoon_me_transparent2 | 1254 × 1254 | 491,815 |
| avatar-tarot-headphones / cartoon_me_transparent1 | 1254 × 1254 | 610,615 |

Learning counters/bars and spread counts are real UI elements with no baked-in
sample values to cover. No deleted crop was restored. Licensed Pacifico and Kaushan Script
fonts are linked into both native hosts; the web also bundles DM Sans. License
notices accompany the fonts.

The nested native trees were identical copies. The CLI points at `mobile/android`
and `mobile/ios`; only the duplicate nested copies were removed. Scaffolding now
copies directory contents and no longer regenerates old mobile images.

Official checkout v7, setup-node v7, setup-java v6, setup-python v7 and
upload-artifact v7 were checked for Node 24 support. CI uses Ubuntu 24.04,
Node 24 and the committed npm lockfile. RN screens is pinned to 4.25.2 for RN 0.83.

## Store and iOS follow-up

The owner confirmed that products and checkout belong on neurospicymystic.com.
Both apps now expose a single **Visit my store** link. They do not fetch or display
the legacy backend product catalog, prices or per-product buttons.

A new macOS/Xcode CI job attempts a real Release simulator build and launches it
on an iPhone with a backend running on the same runner. It retains an actual native
Home screenshot and logs. This extends the earlier Metro-only iOS checks; consult
the newest CI result for whether the native build and launch passed.

The web app can be tested without a mobile SDK: from the updated repository root,
install backend/requirements.txt, run `python -m uvicorn backend.main:app --port 8000`,
and open http://localhost:8000 on the same computer. Render can host this Python
service and its web frontend using render.yaml. It cannot host an iOS simulator.
