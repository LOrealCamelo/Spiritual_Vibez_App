# Supplied illustrated UI panels

The owner's 24 individual PNG panels are used directly in both applications.
The web copies in `frontend/assets/` match the native originals in
`mobile/assets/ui_cards/` byte-for-byte. Native sources use static Metro requires;
web controls use the same filenames. The artwork keeps its original aspect ratio.

| Supplied artwork | Placement and action |
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

Progress bars and counts cover the sample values printed in the learning artwork
and reflect distinct cards studied this session. Counts on the three narrow spread
panels reflect the real backend layout: 5, 10 and 6 cards respectively. Their
Intuition/Clarity, Decision/Direction and Growth/What's Next captions remain visible.
The supplied artwork is not rewritten to change the sample numbers.

The Filter by Vibe buttons use transparent touch targets so the original heart,
briefcase, sprout and lettering remain visible. Selecting a vibe updates the
available layouts. Career includes the career and financial spreads from the
existing library. The web's advanced search expands below the illustrated filter.

The 78 tarot deck images remain the cards revealed in readings, daily draws,
study details and quizzes. Their display-copy optimization is documented in
[Astronomy and Tarot](ASTROLOGY_AND_TAROT.md).

Verification covers all 24 panel placements and file identity, exact PNG paths,
native navigation, live learning progress, illustrated filter behavior, full
connected browser flows and desktop/phone screenshots. The cloud native build
workflow verifies the current revision separately; inspect its check status for
the platform compilation and simulator result.
