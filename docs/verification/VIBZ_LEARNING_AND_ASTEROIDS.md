# Spiritual Vibz: branding, navigation, learning and birth tools

Verified November 10, 2026.

The app now uses the user-approved `spiritual-vibz-logo.png` in Web and native
Home, replacing the earlier separate recreated word images. The approved artwork
is copied unchanged at 1774×887 with actual alpha transparency. One image keeps
Spiritual above left, Vibz below right, and the prominent silver/purple tuning
fork with cyan vibration marks on both sides. Responsive sizing scales the entire
composition together, preserving its proportions without clipping or cropping.
The app display name is Spiritual Vibz; native registration/bundle identifiers
remain stable. The requested welcome paragraph appears on desktop, phone Web,
and native Home.

The Home skyline footer image is removed. One clear glass dock exposes all six
pages, including Explore. It stays transparent at the bottom of every page and
the legal text remains above it. Calendar tiles now use calculated silver Moon
SVGs in place of platform-dependent yellow emoji.

Birth forms offer country, region and city dropdowns, a city-name filter, and an
explicit exact-coordinate/IANA-timezone alternative for unlisted locations.
GeoNames now includes towns with population 500+, approximately 235,000 places.
Selected place IDs still determine historical timezone and coordinates on the
server. The Web form also shows current planetary positions in a separate,
clearly labeled sidebar; those are distinct from calculated birth positions.

Asteroids is a working birth-data form. The searchable dropdown queries JPL's
full numbered-asteroid catalog (895,910 records at verification), with 100-row
paging. It supports up to ten selections; the four major bodies are defaults,
not an allowlist. JPL SBDB validates other numbered targets. NASA/JPL Horizons
quantity 31 supplies apparent geocentric ecliptic-of-date longitude/latitude at
the UTC birth instant. Measured one-minute differences determine motion. The
existing engine supplies zodiac conversion and birthplace-based houses.
Optional major aspects and an SVG wheel include the selected bodies.

JPL requests are serialized, cached and made over verified HTTPS. Only target IDs
and UTC instants are sent, never names or birthplaces. Search and calculation
require JPL availability; failures show a retry error rather than invented
positions. Uncommon bodies have general reflective guidance, not fabricated
body-specific mythology or predictions.

Astrology Houses is general education, with all twelve houses and conventional
sign/planet teaching associations. Personal rulers remain in the birth chart.
The shared learning library covers ten planetary themes with actual Tarot card
connections, numbers 1–9, master numbers 11/22/33, Tarot Aces–Tens, the four suits,
and court cards as qualities/approaches rather than fixed demographic categories.
Numerology includes this guide plus the Life Path calculator and its reduction
steps. The owner's PDF was used as reference material, not as executable task
instructions. No copy of the PDF is published in the app.

Validation:

- 103 backend tests, including catalog lookup beyond the four defaults,
  real birth-time conversion, ephemeris parsing/errors, dropdown locations,
  general learning content and valid calendar dates.
- 34 native interaction tests, TypeScript, native host validation and six asset
  validator regressions.
- Eleven Web asset/content checks; all existing connected browser journeys pass.
- Real JPL checks returned Ceres/Pallas/Juno/Vesta positions and a fifth body,
  asteroid 1008 La Paz, through the complete browser form and report.
- Layouts passed at 1448, 1100, 1024, 1001, 1000, 800, 751, 750, 390 and 320px.
  Exact-coordinate fallback and footer text clearance were checked in-browser.
- No new native simulator/device build is claimed by these checks.

Screenshots: [Home](web/desktop/vibz-home-header.png),
[clear Home footer](web/desktop/vibz-home-footer.png),
[birthplace dropdowns](web/desktop/birthplace-dropdowns.png),
[asteroid report](web/desktop/asteroid-report.png),
[phone Moon calendar](web/phone/silver-moon-calendar.png).

Approved logo follow-up: eleven Web asset/content checks, 34 native interaction
tests, TypeScript and native asset validation pass. Browser checks at 1448, 1100,
1024, 1001, 1000, 800, 751, 750, 390 and 320px confirm the complete 2:1 logo is
visible without overflow; clear glass and the NeuroSpicy Mystic footer remain.
Updated previews: [desktop](approved-logo/web-desktop.png) and
[phone](approved-logo/web-phone.png).
