# Birth charts, daily sky and the uploaded tarot deck

The web and bare React Native iOS/Android apps use the same FastAPI calculations.
The source application includes the code changes and all 78 card PNGs; screenshot
and log artifacts are verification evidence rather than the runnable application.

## Try the changes

Download the [current app ZIP](https://github.com/LOrealCamelo/Spiritual_Vibez_App/archive/refs/heads/main.zip),
extract it and double-click `START_WEB_WINDOWS.cmd`. The first launch installs
the Python packages, then opens the web app and backend together.

- Open Birth Chart from Home or Explore. Enter a name, birth date, local hour
  (12 AM through 11 AM, then 12 PM through 11 PM) and minutes (00–59), country,
  state/province and city from the dropdowns. Filter the city list by name when needed. The hour must be
  selected explicitly; 12 AM means midnight and 12 PM means noon.
- Choose Tropical or Sidereal (Lahiri), and Placidus, Whole Sign or Equal houses.
  Calculate to see the wheel, ten planet placements, twelve house descriptions,
  major aspects, element counts and a detailed symbolic report. The positions
  sidebar includes planet and zodiac symbols, degrees, house numbers, retrograde
  markers and a Tropical/Sidereal dropdown. It sits below the wheel on phones.
  Choose Modern (10 planets) or Traditional (7 planets) house rulers to see each
  ruler’s actual sign/house, the planets occupying each house and ASC/MC/DC/IC
  interpretations with applying/separating aspects. The browser can
  print the report or save it as a PDF.
- Open Cosmos. It loads the current sky automatically in the device's timezone,
  refreshes every minute and when returning to the app, and accepts other dates.
  Other dates use local noon, which is shown explicitly. Change your zodiac sign
  to see different whole-sign solar-house reflections for the same sky snapshot.
- Inside the existing Moon Phases/Cosmos section, browse any month/year from
  1900–2100 using the month picker or previous/next month/year controls. A daily
  list shows weekday, date, a calculated phase illustration, exact principal-phase
  times, Moon sign changes and traditional body associations for each sign interval.
  The Moon card and the natal Moon page both open this section; no new navigation
  category is needed.
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

Both apps submit the selected 12-hour clock time and an explicit `birth_period`
(`AM` or `PM`). Python normalizes it to a 24-hour local time before constructing
the birth datetime: `hour % 12 + (12 if period == 'PM' else 0)`. Existing API
clients can omit `birth_period` and continue submitting a 24-hour `birth_time`.
Responses retain normalized 24-hour `birth_time` and also include
`birth_time_12h`, the offset-bearing `birth_local_time`, and `birth_utc`.

The historical IANA timezone from the selected city converts local birth time
to UTC, including daylight saving. Nonexistent clock times are rejected; repeated
times require choosing the first or second occurrence. Missing birth locations
are rejected rather than silently substituting Utica. Existing coordinate-based
API integrations must explicitly supply coordinates **and** a timezone.

That UTC instant drives the planetary ephemeris; the same instant and the city's
latitude/longitude drive local sidereal time, the Ascendant, Midheaven, and house
cusps. Changing AM to PM therefore recalculates both the sky and houses. Regression
tests cover all 24 hour choices, noon/midnight, historical DST gaps and repeated
hours, different birthplaces, and AM/PM chart comparisons with independent
Swiss Ephemeris 2.10.03 / Moshier reference values (Moon within 0.02°, angles and
all 12 Placidus cusps within 0.001°). Swiss Ephemeris is a development reference,
not an application dependency.

GeoNames city data (through geonamescache 3.0.2) covers towns with population
of at least 500. State/province names come from the bundled GeoNames admin1
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

The Draconic chart has been removed at the owner’s request, including its menus,
calculation branch and API option. Old web links return to the tool catalog, and
API requests for this removed chart return 422. Secondary progressions retain the
existing day-for-year convention. The repaired natal report does not invent
asteroid positions. Separate educational asteroid, BaZi, astrocartography and
13-moon calendar tools retain their earlier behavior; they are outside the
numerical validation described here.

## Reference layout and lunar calendar

The owner supplied these Astro-Seek references:

- [Natal birth chart](https://horoscopes.astro-seek.com/calculate-birth-chart-horoscope-online/)
- [November 2026 lunar calendar](https://mooncalendar.astro-seek.com/moon-phases-calendar-november-2026)

Automated requests return HTTP 403, so no direct calculator-to-calculator match is
claimed. The supplied screenshots guide the report/table structure. Independent
Swiss Ephemeris comparisons remain development fixtures only. All four November
2026 phase times differ by less than 40 seconds in the current comparison. The
first four Moon ingresses agree within one minute with the screenshot’s Leo
04:18, Virgo 08:28, Libra 14:38 and Scorpio 22:40 UTC entries. Different ephemerides
and minute-display conventions can produce small differences.

Moon ingress searches bracket each 30° zodiac boundary and bisect to under one
second; this solver resolution does not imply sub-second astronomical accuracy.
Tropical and mean-Lahiri Sidereal use their respective sign boundaries. Daily
illumination and phase illustrations use local noon, with a north-up convention
(waxing on the right); principal phase labels refer to actual events during that
civil date. All intervals and events use the selected timezone, including daylight
saving and 23/25-hour dates. Historically skipped civil dates are marked unavailable.
Responses cache up to 64 month/timezone/zodiac combinations.

Body correspondences are explicitly presented as traditional astrology lore,
not established physiological effects. The Surgery column directs users to their
surgical team. Moon placements do not establish surgical safety; the app does not
provide a lunar yes/no medical recommendation.

House rulership is a symbolic convention. Modern rulers use Pluto for Scorpio,
Uranus for Aquarius and Neptune for Pisces; traditional rulers use Mars, Saturn
and Jupiter respectively. Major planetary aspect orbs are 8° conjunction, 4°
sextile, 6° square/trine and 8° opposition; angle aspects use 8°. Applying/separating
is derived from angular-error motion, with horizon/meridian motion included for
chart angles. It is not inferred from sign order. Interpretations are original
text based on those computed placements, rather than copied Astro-Seek prose.

## Deck provenance and packaging

The owner supplied the [78-PNG Drive folder](https://drive.google.com/drive/folders/1MLC_nQ5YPfuGH0wOwq76xSW0T4ciCwWJ).
The app bundles 648 × 1080 PNG display copies in `mobile/assets/tarot/`, using
stable, case-sensitive filenames. The original 1086 × 1810 files in Drive and
our separate source directory remain unchanged. The full card frame, borders,
labels and artwork are preserved. Lanczos downsampling retains full RGB color;
there is no cropping or palette reduction.

The deck decreased from **231.7 MiB to 95.7 MiB (58.7% smaller)**. Web, iOS and
Android all use these same display copies. `backend/data/tarot_images.json` maps
canonical IDs 0–77 to the app assets and records each original filename,
source/display dimensions, byte sizes and SHA-256 hashes. Numeric minor-card
filenames from Drive map to written ranks; Pentacles images also match the
catalog's Coins suit.

To regenerate the display copies from a separate folder containing the originals,
install Pillow in a development environment and run:

```sh
python mobile/scripts/prepare-tarot-images.py --source-dir /path/to/originals
```

The script reads originals without modifying them and updates the app's display
copies and provenance manifest. Pillow is not required to run the application.
The earlier full-resolution app assets also remain available in Git history at
commit `464e60e`.

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
