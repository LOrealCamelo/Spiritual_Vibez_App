# Supplied illustrated UI panels

The 24 interface panels have been recreated because the supplied small PNGs were
soft and had rough edges. They now combine **16 newly generated illustrations**
with live text, gradients, borders, arrows, progress and accessible controls.

The four source PNG packs in `mobile/assets/illustrations/` and
`frontend/assets/illustrations/` match byte-for-byte. Each is 1254 × 1254 with real
transparency, containing four isolated icons (627 × 627 per region). The renderer
selects the appropriate icon without creating an enlarged screenshot crop. Source
files remain unmodified. Text, counters and outlines scale independently.

Panel definitions are in `mobile/src/data/uiPanels.json` and
`frontend/artwork.js`; checks ensure they match. The old 24 `ui_cards/` images,
their web copies and the unused cropped Journal alias were removed. The original
images remain available in Git history if needed.

| Recreated panel | Placement and action |
| --- | --- |
| Daily Card | Home → a real tarot card and its study details |
| Shuffle a Spread | Home → Spreads |
| Learn Tarot | Home → the learning academy |
| Birth Chart | Home → city-based birth chart form |
| Spreads header | Spreads heading |
| Randomize a Spread | Spreads → choose an available layout |
| Filter by Vibe | Spreads → independent All, Love, Career and Growth buttons |
| Trust Your Gut | Spreads → canonical `trust-your-gut` layout |
| At a Crossroads | Spreads → canonical `at-a-crossroads` layout |
| Next Phase | Spreads → canonical `stepping-into-new-timeline` layout |
| Learn Tarot header | Learning heading |
| Your Learning Journey | Learning → current progress and card catalog |
| Major Arcana | Learning → the 22 major cards |
| Minor Arcana | Learning → the 56 minor cards |
| Card Meanings | Learning → all 78 card meanings |
| Reversed Cards | Learning → reversed images and meanings |
| Quiz Me | Learning → a multiple-choice card study question |
| My Journal header | Journal heading |
| Today's Journal | Journal → write and save a reflection on the device |
| Saved Readings | Journal → saved reflections and readings |
| Mood Check-In | Journal → record a mood on the device |
| Moon Phase | Journal and Home → current daily Moon/planetary sky and monthly lunar calendar |
| Numerology | Journal and Home → Life Path calculator |
| Rituals | Journal and Home → ritual search |

The full Hey Mystic illustration is the phone Home greeting. Desktop web Home
composes the supplied skyline and transparent yellow-shirt character; both apps
use the supplied skyline footer. Native screens also use a faint skyline backdrop.
The larger supplied Trust Your Gut, Next Phase, Reset Your Energy and Grounding
illustrations appear in the Home favorites collection.

Progress bars and counts are real UI elements and reflect distinct cards studied
this session. Counts on the three featured spread panels come from the real
backend layout: 5, 10 and 6 cards respectively. No opaque patches hide baked-in
sample text. Filters are normal labeled buttons with selected states, and the
web’s advanced search expands below them. Career includes career and financial
spreads from the existing library.

The 78 tarot deck images remain the cards revealed in readings, daily draws,
study details and quizzes. Their display-copy optimization is documented in
[Astronomy and Tarot](ASTROLOGY_AND_TAROT.md).

Verification covers all 24 definitions, live labels, source file identity, PNG resolution,
native navigation, live learning progress, illustrated filter behavior, full
connected browser flows and desktop/phone screenshots. The cloud native build
workflow verifies the current revision separately; inspect its check status for
the platform compilation and simulator result.
