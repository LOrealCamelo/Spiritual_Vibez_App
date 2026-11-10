"""Birth-time asteroid charts from NASA/JPL Horizons apparent geocentric positions.

Only target IDs and UTC instants are sent to Horizons, never names or birthplaces.
Queries are serialized in accordance with JPL's single-request fair-use policy.
"""
import csv
import json
import re
from datetime import timedelta, datetime
from functools import lru_cache
from threading import Lock
from urllib.parse import urlencode
from urllib.request import urlopen
from .birth_locations import resolve_birth, birth_time_24h
from .sky_engine import natal_chart, astro_time, zodiac_offset, sign_position, signed, house_for
from .natal_report import aspect_between
from .chart_wheel import wheel_svg

ASTEROIDS = [
    dict(id=1, name='Ceres', glyph='⚳', group='Major asteroids', theme='Nurturing, care, nourishment and the balance between giving and receiving.'),
    dict(id=2, name='Pallas', glyph='⚴', group='Major asteroids', theme='Creative intelligence, pattern recognition, strategy and practical wisdom.'),
    dict(id=3, name='Juno', glyph='⚵', group='Major asteroids', theme='Commitment, agreements, fairness and the relationships you choose to sustain.'),
    dict(id=4, name='Vesta', glyph='⚶', group='Major asteroids', theme='Dedication, focus, personal boundaries and the work you hold sacred.'),
    dict(id=16, name='Psyche', glyph='Ψ', group='Love & connection', theme='Sensitivity, trust, inner life and the experience of being understood.'),
    dict(id=433, name='Eros', glyph='♡', group='Love & connection', theme='Desire, attraction, creative passion and what brings you alive.'),
    dict(id=1181, name='Lilith (asteroid)', glyph='L', group='Love & connection', theme='Autonomy, refusal and the parts of yourself you reclaim. This is asteroid 1181, not Black Moon Lilith.'),
    dict(id=2101, name='Adonis', glyph='A', group='Love & connection', theme='Beauty, admiration, idealization and how you relate to being desired.'),
    dict(id=1221, name='Amor', glyph='♥', group='Love & connection', theme='Affection, devotion, generosity and the way you express love.'),
    dict(id=1388, name='Aphrodite', glyph='a', group='Love & connection', theme='Pleasure, creativity, beauty and your relationship with attraction.'),
    dict(id=2060, name='Chiron', glyph='⚷', group='Centaurs', theme='Vulnerability, learning through experience and offering care without abandoning yourself.'),
]
_HORIZONS_LOCK = Lock()
_CATALOG_RECORDS = {}


class EphemerisUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=128)
def search_asteroids(query='', offset=0):
    """Page/search the complete JPL catalog of numbered asteroids, not just majors."""
    query = query.strip()
    if len(query) > 80 or offset < 0 or offset > 2000000:
        raise ValueError('Use an asteroid name or number of at most 80 characters.')
    params = {'fields': 'pdes,name', 'sb-kind': 'a', 'sb-ns': 'n',
              'limit': '100', 'limit-from': str(offset), 'sort': 'spkid'}
    if query:
        constraint = 'pdes|EQ|' + query if query.isdigit() else 'name|RE|' + re.escape(query)
        params['sb-cdata'] = json.dumps({'AND': [constraint]})
    try:
        with _HORIZONS_LOCK:
            with urlopen('https://ssd-api.jpl.nasa.gov/sbdb_query.api?' + urlencode(params), timeout=20) as response:
                result = json.load(response)
        if 'error' in result or 'count' not in result:
            raise EphemerisUnavailable('JPL asteroid catalog search is unavailable. Please retry.')
        known = {a['id']: a for a in ASTEROIDS}
        records = []
        for number, name in result.get('data', []):
            if not str(number).isdigit():
                continue
            body_id = int(number)
            record = known.get(body_id, dict(id=body_id, name=name or 'Asteroid ' + number,
                          glyph='◇', group='Numbered asteroids',
                          theme='Consider this named body as an additional symbolic lens. Interpret its measured sign, house and aspects alongside your question and the main chart; its name alone does not establish a personal prediction.'))
            records.append(record)
            _CATALOG_RECORDS[body_id] = record
        while len(_CATALOG_RECORDS) > 4096:
            _CATALOG_RECORDS.pop(next(iter(_CATALOG_RECORDS)), None)
        total = int(result['count'])
        return {'asteroids': records, 'defaults': ASTEROIDS[:4], 'total': total, 'offset': offset, 'has_more': offset + 100 < total,
                'source': 'NASA/JPL Small-Body Database — numbered asteroids',
                'note': 'Search the full numbered-asteroid catalog by name or number. Select up to ten; Ceres, Pallas, Juno and Vesta are defaults only.'}
    except (OSError, ValueError) as exc:
        raise EphemerisUnavailable('JPL asteroid catalog search is unavailable. Please retry.') from exc


def asteroid_record(body_id):
    known = next((a for a in ASTEROIDS if a['id'] == body_id), None)
    if known:
        return known
    if not 1 <= body_id <= 10000000:
        raise ValueError('Choose a valid numbered asteroid from the catalog.')
    if body_id in _CATALOG_RECORDS:
        return _CATALOG_RECORDS[body_id]
    matches = search_asteroids(str(body_id))['asteroids']
    if not matches:
        raise ValueError(f'Asteroid {body_id} is not in the numbered catalog. Choose a listed result.')
    return matches[0]


def parse_horizons(result):
    if '$$SOE' not in result or '$$EOE' not in result:
        raise EphemerisUnavailable('NASA/JPL did not return ephemeris positions. Please try again.')
    rows = list(csv.reader(result.split('$$SOE', 1)[1].split('$$EOE', 1)[0].strip().splitlines()))
    try:
        values = [(float(row[3]), float(row[4])) for row in rows]
        if len(values) != 3 or any(not 0 <= lon < 360 or not -90 <= lat <= 90 for lon, lat in values):
            raise ValueError('Invalid ephemeris')
        return values[1][0], values[1][1], signed(values[2][0] - values[0][0]) * 720
    except (IndexError, ValueError) as exc:
        raise EphemerisUnavailable('NASA/JPL returned incomplete ephemeris data. Please retry.') from exc


@lru_cache(maxsize=512)
def horizons_position(body_id, utc_iso):
    dt = datetime.fromisoformat(utc_iso)
    params = {'format': 'json', 'COMMAND': f"'{body_id};'", 'EPHEM_TYPE': "'OBSERVER'",
              'CENTER': "'500@399'", 'START_TIME': (dt-timedelta(minutes=1)).strftime("'%Y-%m-%d %H:%M:%S'"),
              'STOP_TIME': (dt+timedelta(minutes=1)).strftime("'%Y-%m-%d %H:%M:%S'"),
              'STEP_SIZE': "'1 m'", 'QUANTITIES': "'31'", 'CSV_FORMAT': "'YES'"}
    try:
        with _HORIZONS_LOCK:
            with urlopen('https://ssd.jpl.nasa.gov/api/horizons.api?' + urlencode(params), timeout=20) as response:
                data = json.load(response)
        return parse_horizons(data.get('result', ''))
    except (OSError, ValueError) as exc:
        raise EphemerisUnavailable('NASA/JPL ephemeris is unavailable. Please retry; no positions were estimated.') from exc


def asteroid_chart(data):
    if len(set(data.asteroid_ids)) != len(data.asteroid_ids):
        raise ValueError('Select 1–10 different asteroids from the list.')
    selected = [asteroid_record(body_id) for body_id in data.asteroid_ids]
    dt, location, local = resolve_birth(data)
    chart = natal_chart(dt, location['latitude'], location['longitude'], name=data.name,
                        zodiac=data.zodiac, house_system=data.house_system, chart_system='natal', rulership=data.rulership)
    offset = zodiac_offset(astro_time(dt), data.zodiac)
    bodies = []
    for index, asteroid in enumerate(selected):
        lon, lat, speed = horizons_position(asteroid['id'], dt.isoformat())
        position = sign_position(lon-offset)
        house = house_for(position['longitude'], [h['longitude'] for h in chart['houses']])
        bodies.append(dict(**asteroid, **position, planet=asteroid['name'], latitude=lat, house=house,
                           speed_deg_per_day=speed, retrograde=speed < 0, motion='Retrograde' if speed < 0 else 'Direct',
                           paragraphs=[asteroid['theme'], f"{asteroid['name']} in {position['sign']} brings this symbolic theme into the expression of that sign.",
                                       f"House {house} — {chart['houses'][house-1]['title']} — is the life area to consider when reflecting on this placement."]))
        if bodies[-1]['glyph'] == '◇':
            bodies[-1]['glyph'] = f'A{index+1}'
    aspects = []
    if data.aspect_mode == 'major':
        for i, body in enumerate(bodies):
            for other in chart['placements'] + bodies[i+1:]:
                aspect = aspect_between(body, other)
                if aspect:
                    aspects.append(aspect)
    chart.update(title='Asteroids in your natal chart', birth_date=data.birth_date, birth_time=birth_time_24h(data),
                 birth_time_12h=datetime.fromisoformat(local).strftime('%I:%M %p'), birth_local_time=local,
                 birth_utc=dt.isoformat(), location=location, asteroids=bodies, asteroid_aspects=sorted(aspects, key=lambda a:a['orb']),
                 aspect_mode=data.aspect_mode, ephemeris_source='NASA/JPL Horizons; apparent geocentric IAU76/80 ecliptic-of-date',
                 ephemeris_url='https://ssd.jpl.nasa.gov/horizons/',
                 ephemeris_note='Positions are computed for your UTC birth instant. Houses use your birthplace coordinates. Before 1962 Horizons uses UT1; UTC/UT1 differences are below one second in modern dates. Symbolic interpretations are reflective, not predictions.')
    wheel = {**chart, 'placements': chart['placements'] + bodies,
             'aspects': chart['aspects'] + aspects}
    chart['wheel_svg'] = wheel_svg(wheel)
    return chart
