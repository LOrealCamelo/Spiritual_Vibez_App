# Explicit AM/PM birth time

Verified November 10, 2026 (UTC).

The Web and native birth forms now offer 24 labeled hour choices, all AM hours
followed by all PM hours, plus minutes 00–59. An hour must be selected explicitly.
The Natal Birth Chart heading is larger in both layouts, and the Web Explore
tile has a larger label. The clear glass surfaces remain unchanged.

Python accepts `birth_time: "02:30", birth_period: "PM"`, normalizes it to
`14:30`, then resolves the selected city's historical IANA timezone to UTC.
The UTC instant and city coordinates drive the actual ephemeris and house
calculation. Existing 24-hour API requests remain supported.

For the test birth in Utica on November 5, 1996:

| Local birth time | UTC | Ascendant longitude |
| --- | --- | --- |
| 2:30 AM | 07:30 UTC | approximately 173.858° |
| 2:30 PM | 19:30 UTC | approximately 346.475° |

Checks passed locally:

- 91 backend tests, including all 24 hour conversions, noon and midnight,
  AM/PM chart differences, backward compatibility, historical DST gaps and
  repeated hours, and different birthplaces.
- Independent Swiss Ephemeris 2.10.03 / Moshier comparisons for both AM and PM:
  Moon longitude within 0.02°, Ascendant/Midheaven and all Placidus cusps within
  0.001°. The reference library is not shipped as an application dependency.
- 31 native interaction tests and TypeScript checking. Native tests select the
  hour/minute menus and confirm explicit AM/PM request payloads for both natal
  chart and natal Moon. This is not a new native simulator or device build.
- Eight Web asset checks and JavaScript syntax checks.
- Connected browser flows: all 15 backend-backed tools and the existing
  journal/tarot/sky journeys. The birth flow switches AM/PM and checks actual
  planet and house changes, midnight/noon UTC conversion, and report labels.

Screenshots: [desktop form](web/desktop/birth-time-form.png) and
[phone website form](web/phone/birth-time-form.png).
