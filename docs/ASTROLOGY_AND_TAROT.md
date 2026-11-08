# Birth charts, daily sky and the uploaded tarot deck

The web and bare React Native iOS/Android apps use the same FastAPI calculations.
The source application includes the code changes and all 78 card PNGs; screenshot
and log artifacts are verification evidence rather than the runnable application.

## Try the changes

Download the [updated branch ZIP](https://github.com/LOrealCamelo/Spiritual_Vibez_App/archive/refs/heads/fix/mobile-assets-metro-ci.zip),
extract it and double-click `START_WEB_WINDOWS.cmd`. The first launch installs
the Python packages, then opens the web app and backend together.

- Open Birth Chart from Home or Explore. Enter a name, birth date, local hour and
  minutes, country, state/province and city. Find the city and select its result.
- Choose Tropical or Sidereal (Lahiri), and Placidus, Whole Sign or Equal houses.
  Calculate to see the wheel, ten planet placements, twelve house descriptions,
  major aspects, element counts and a detailed symbolic report. The browser can
  print the report or save it as a PDF.
- Open Cosmos. It loads the current sky automatically in the device's timezone,
  refreshes every minute and when returning to the app, and accepts other dates.
  Other dates use local noon, which is shown explicitly. Change your zodiac sign
  to see different whole-sign solar-house reflections for the same sky snapshot.
- Open any spread and reveal a position. Its actual card PNG appears, rotated if
  reversed. The same deck appears in lessons, daily cards and quizzes. Native apps
  bundle every image and the full core card catalog for use without a connection.

## Calculation methods and limits

Astronomy Engine 2.1.19 (MIT license) supplies geocentric apparent ecliptic
longitudes for Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune
and Pluto. Retrograde motion comes from the change in computed longitude.
Lunar illumination uses Sun–Moon–Earth geometry. New/quarter/full phases are
instants; the display uses those names within ±1° of the corresponding elongation
and otherwise shows waxing/waning crescent or gibbous. It also shows the next
principal phase's calculated time. This convention is visible in both apps.

The historical IANA timezone from the selected city converts local birth time
to UTC, including daylight saving. Nonexistent clock times are rejected; repeated
times require choosing the first or second occurrence. Missing birth locations
are rejected rather than silently substituting Utica. Existing coordinate-based
API integrations must explicitly supply coordinates **and** a timezone.

GeoNames city data (through geonamescache 3.0.2) covers towns with population
of at least 1,000. State/province names come from the bundled GeoNames admin1
directory. Data is [GeoNames, CC BY 4.0](https://www.geonames.org/). No name or
birth details are sent to an external geocoding service. For an absent small
settlement, a nearby listed town can be selected; this can slightly change houses.

Placidus cusps solve the semi-diurnal/nocturnal arc equations using apparent
sidereal time and true obliquity. Polar locations at or above 66° absolute
latitude require an explicit choice of Equal or Whole Sign houses. The Sidereal
option uses mean Lahiri ayanamsa with IAU 2006 general precession, accurate to
within 0.01° over the supported 1900–2100 dates. This can differ by a few arcminutes
from a site using true Lahiri or a different ephemeris or house convention.

Regression fixtures independently computed with Swiss Ephemeris 2.10.03/Moshier
show planetary longitude differences below 0.005° at 2026-11-08 00:00 UTC and
Placidus cusp differences below 0.0001° for the three tested locations in both
hemispheres. Swiss Ephemeris is a development comparison only and is not a runtime
dependency. These comparisons are numerical checks, not a claim of scientific
validity for astrology interpretations. Personal feelings cannot be calculated
from planetary positions. Daily reflections use solar houses rather than a
person's complete natal chart. Birth-time accuracy affects houses and Ascendant.

The existing draconic option subtracts the **mean** ascending lunar node; it is
labelled draconic rather than sidereal. The existing progressed option uses the
secondary day-for-year convention. The repaired natal report does not invent
asteroid positions. Separate educational asteroid, BaZi, astrocartography and
13-moon calendar tools retain their earlier behavior; they are outside the
numerical validation described here.

## Deck provenance and packaging

The owner supplied the [78-PNG Drive folder](https://drive.google.com/drive/folders/1MLC_nQ5YPfuGH0wOwq76xSW0T4ciCwWJ).
The original PNGs are copied to `mobile/assets/tarot/` with stable, case-sensitive
names. `backend/data/tarot_images.json` maps canonical IDs 0–77 to those files and
records their original names. Numeric minor-card filenames from Drive map to the
written ranks in the catalog; Pentacles images also match the catalog's Coins suit.
The original files total about 232 MiB. They have not been cropped, regenerated
or resized. The complete source ZIP is consequently larger than the earlier UI
repair ZIP.

The backend mounts this same directory at `/assets/tarot/`; the browser requests
those PNGs, and Metro uses 78 explicit static requires for both native platforms.
Catalog, card detail, quiz, single draw, full draw and synthesis responses include
the corresponding `image_url`. Web cards load lazily. A card back appears until
the user reveals a position; a revealed card displays the supplied artwork.

## Verification

Run `python -m pytest -q backend/tests`, `node --test frontend/tests/assets.test.cjs`,
and `python frontend/tests/browser_flows.py --screenshots work/browser-evidence`.
In `mobile`, run `npm run check:assets`, `npm run check:native`, `npm run test:assets`,
`npm run typecheck` and `npm test -- --runInBand`.

The browser journey verifies city selection, UTC conversion, SVG/report output,
Sidereal changes, full tarot reveals and lessons, automatic sky loading and
different Virgo/Pisces reflections. It captures a printable report, chart wheel,
daily sky and tarot reading, alongside desktop and phone-width reference screens.
The extracted-source workflow also checks the deck and new browser script.

The PR's native workflow repeats both Metro bundles, Android compilation and a
cloud macOS/Xcode Release build and iPhone simulator launch. Consult its result
for the current commit. A simulator launch is not a physical-device test or a
full visual/interaction test of every native screen. TestFlight and App Store
distribution need paid Apple membership and signing setup; browser hosting does
not run the native iOS binary. Flutter and FlutterFlow are not required.
