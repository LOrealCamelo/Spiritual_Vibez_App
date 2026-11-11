# Spiritual Vibz: branding, navigation, learning and birth tools

Core features verified November 10, 2026; light-portal update verified November 11.

The app now uses the user-approved `spiritual-vibz-logo-compact.png` in Web and native
Home, replacing the earlier separate recreated word images. The approved artwork
is copied unchanged at 1984×793 with actual alpha transparency. One image keeps
the two words close together in the clarified compact arrangement, and the silver/purple tuning
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
1024, 1001, 1000, 800, 751, 750, 390 and 320px confirm the complete original-aspect logo is
visible without overflow; clear glass and the NeuroSpicy Mystic footer remain.
Updated previews: [desktop](approved-logo/web-desktop.png) and
[phone](approved-logo/web-phone.png).

Homepage room redesign: Home now uses one extended reading-room illustration
based on the supplied white-top portrait. The speech bubble is removed and the
covered torso, forearm and table are restored in the artwork. The guide sits at
the central reading table; there is no separate avatar on the right. The room is
extended to both sides rather than stretching the original square portrait. The
unchanged approved logo sits toward the upper left without a card, with welcome
text and working reading/learning actions beneath the scene. A soft transition
into the matching room-colored page avoids a rectangular picture edge. Phone Web
uses the same scene with proportional cropping and no duplicate portrait.

Other Web tabs retain the starry background and all clear-glass cards and footer
navigation remain. This room redesign does not change the native Home artwork.
Twelve browser widths from 320 to 1920px pass, with intact logo proportions, no
horizontal overflow, functional hero actions, no duplicate avatar or logo,
and no JavaScript errors. Eleven Web asset/content checks pass. Current previews:
[desktop](reading-room/web-desktop.png) and [phone](reading-room/web-phone.png).

Light-portal follow-up: the area below the desk now transitions into a light
pearl/lavender/blush portal illustration. It is anchored below the room and
scrolls with the page, fading into a matching pale background. The room and
approved logo assets are unchanged. Home labels, arrows, welcome copy and footer
use dark-plum ink for contrast; clear-glass fills remain transparent and unfrosted.
Other pages retain their existing backgrounds and colors. Eleven Web checks and
twelve browser widths pass, including glass-opacity checks and hero navigation.
Current previews: [room transition](light-portal/web-desktop.png),
[desktop cards](light-portal/cards-desktop.png), and
[phone cards](light-portal/cards-phone.png).

Personal-tattoo follow-up: Web Home now uses `home-mystic-room-tattoos.png`,
adapting the owner's tattoo references into the existing illustrated scene.
Visible motifs include lotus petals, sacred geometric mandalas, the colored
wrist mandala and bead chains, Egyptian wings, and a triple-moon neck design.
The original reference photographs are not published in the repository.
The owner clarified that the Spiritual Vibz name logo should be larger; its
unchanged transparent artwork now scales up at both desktop and phone widths.
The room artwork has a pale lower-edge mist, no border or shadow, and a lighter
transition beneath it into the existing portal. Twelve browser widths, clear
glass checks, hero actions and eleven Web content/asset checks pass.
The downloadable `frontend/assets/homepage-redesign-preview.png` is refreshed.
Current previews: [desktop](personal-tattoos/web-desktop.png) and
[phone](personal-tattoos/web-phone.png).

Tattoo-placement corrections use `home-mystic-room-personalized.png`: the
shoulder lotus is smaller beside the Virgo glyph/constellation/arrow design;
necklaces are removed; the upper chest has the referenced dreamcatcher/feather
and Eye of Horus. The approved logo, triple-moon neck motif, remaining room,
light lower-edge blend and clear-glass cards are retained. Eleven Web checks
and twelve responsive browser widths pass. The separate downloadable
`frontend/assets/home-portrait-with-logo.png` contains only the top room artwork,
guide, desk and approved logo, excluding navigation, feature cards and the lower
portal section. It is exported from the rendered hero at 1824×912 pixels.

Shoulder/ankh refinement uses `home-mystic-room-final.png`: the shoulder is
reduced to natural proportions, Virgo moves to the outer upper arm and the
small lotus moves inward/right. The larger turquoise Eye of Horus is joined
with its black ankh as one chest design. A smaller, higher dreamcatcher/feather
visually hangs beneath the neck moon. The top-only PNG retains the exact
approved logo. Eleven Web checks and twelve browser widths pass; the existing
portal and clear-glass surfaces remain intact.

Reference-geometry refinement uses `home-mystic-room-geometry.png`: the elbow
medallion has a dense triangular sacred-geometry center, the space above it is
filled with the other geometric motif, the Virgo components align vertically,
and the turquoise eye is reduced to fit the black ankh. The shoulder is narrowed
using the original illustrated reference. The owner accepted this tattoo version
and requested the logo be added. The final top-only composition includes the
unchanged approved Spiritual Vibz logo and is also saved with the explicit name
`frontend/assets/home-top-with-spiritual-vibz-logo.png`. Eleven Web checks and
twelve responsive widths pass; no changes were made to the approved logo art.
