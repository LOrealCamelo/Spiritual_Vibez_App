# Love page additions

The existing zodiac comparison remains first. A two-partner, ten-question
preferences questionnaire adds a transparent similarity score and conversation
prompts, plus an explicit Add to Journal action. Answers stay in memory unless
saved and are cleared on account sign-out. This does not predict relationship
success or replace real-world consent, communication or safety.

Country/region/city dropdowns reuse the existing GeoNames catalog. City search
narrows its bounded city list. No geolocation permissions are requested.
Fourteen categories cover the requested broad activity types. OpenStreetMap
Overpass supplies named nearby mapped venues, cached for 15 minutes, with source
attribution and links. They are not presented as live events or verified hours.

For scheduled events configure server-only `TICKETMASTER_API_KEY`. Results use a
50 km radius, current UTC lower date bound and provider listing links. Coverage is
limited to Ticketmaster's participating providers. Without the key the interface
explicitly says event listings are not connected. External Google/Eventbrite
search links are separately labeled; they are not invented results. Not every
activity, rental or small business is available from these sources.

The requested cherry blossom background has not been supplied in this turn.
No new background or artwork has been selected, generated or applied. Once the
exact image is supplied, scope it to `body[data-tool="love"]` and use proportional
cover/contain choices with mobile/desktop checks. Other backgrounds must remain
unchanged.

Automated coverage: mocked upstream provider contracts, unavailable-provider
states, URL filtering, invalid locations/categories, real GeoNames dropdown
interaction, two-partner scoring/journal, and 320/375/390/430/1280/1440/1920 layouts.
The real event service still requires a configured key and a live smoke test.
