"""Geocentric apparent ephemerides using the MIT-licensed Astronomy Engine.

Coordinates are true ecliptic/equinox of date, including light time and aberration.
Houses use local apparent sidereal time and true obliquity. Placidus cusps solve
the semi-diurnal/nocturnal arc equations, rather than substituting equal houses.
"""
from datetime import datetime, timezone, timedelta
from functools import lru_cache
import math
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import astronomy as ae
from .chart_interpretations import SIGNS, HOUSE_THEMES, planet_report, house_report, transit_forecast
from .natal_report import aspect_between, enrich_houses, angle_report

PLANETS = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
ELEMENTS = ['Fire','Earth','Air','Water']
MODES = ['Cardinal','Fixed','Mutable']
SIGN_GLYPHS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
GLYPHS = ['☉','☽','☿','♀','♂','♃','♄','♅','♆','♇']
RULERS = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars / Pluto','Jupiter','Saturn','Saturn / Uranus','Jupiter / Neptune']


def signed(angle):
    return (angle + 180) % 360 - 180


def astro_time(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return ae.Time(dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'))


def sign_position(longitude):
    lon = longitude % 360
    index = int(lon // 30)
    # Round the displayed position as one integer, allowing carry into the next sign.
    total_minutes = round(lon * 60) % (360 * 60)
    display_index, remainder = divmod(total_minutes, 30 * 60)
    degree, minute = divmod(remainder, 60)
    return dict(longitude=round(lon, 6), sign=SIGNS[index], degree=int(lon % 30),
                minute=int((lon % 1) * 60), sign_glyph=SIGN_GLYPHS[index],
                display_sign=SIGNS[display_index], display_sign_glyph=SIGN_GLYPHS[display_index],
                degree_formatted=f'{degree}°{minute:02d}′', formatted=f"{SIGNS[display_index]} {degree}°{minute:02d}′",
                element=ELEMENTS[index % 4], modality=MODES[index % 3], ruler=RULERS[index])


def lahiri_ayanamsa(t):
    # Mean Lahiri at J2000 plus accumulated general precession (IAU 2006,
    # arcseconds). Adequate to <0.01 degree over the supported 1900–2100 span.
    centuries = t.tt / 36525
    precession = 5028.796195 * centuries + 1.1054348 * centuries**2 + 0.00007964 * centuries**3
    return 23.857092 + precession / 3600


def zodiac_offset(t, zodiac):
    if zodiac == 'tropical':
        return 0.0
    if zodiac == 'sidereal':
        # The small nutation term is below the stated 0.01° accuracy of this
        # mean Lahiri model. Do not imply arcsecond agreement with other models.
        return lahiri_ayanamsa(t)
    raise ValueError('Choose tropical or sidereal zodiac.')


def longitude_at(body, t):
    return ae.Ecliptic(ae.GeoVector(getattr(ae.Body, body), t, True)).elon


@lru_cache(maxsize=256)
def positions_at(iso, zodiac='tropical'):
    t = ae.Time(iso)
    offset = zodiac_offset(t, zodiac)
    positions = {}
    for index, body in enumerate(PLANETS):
        lon = longitude_at(body, t)
        speed = signed(longitude_at(body, t.AddDays(.25)) - longitude_at(body, t.AddDays(-.25))) / .5
        positions[body] = dict(**sign_position(lon - offset), planet=body, glyph=GLYPHS[index],
                               retrograde=speed < 0, motion='Retrograde' if speed < 0 else 'Direct',
                               speed_deg_per_day=round(speed, 6))
    # Mean lunar ascending node (Meeus, Astronomical Algorithms, ch. 47).
    c = t.tt / 36525
    node = 125.0445479 - 1934.1362891*c + .0020754*c*c + c**3/467441 - c**4/60616000
    positions['NorthNode'] = dict(**sign_position(node - offset), model='Mean lunar ascending node')
    angle = ae.MoonPhase(t)
    illumination = ae.Illumination(ae.Body.Moon, t).phase_fraction * 100
    # Principal phases are instants. A narrow ±1° event window avoids calling
    # an entire 45° span "New Moon". The exact angle and illumination are shown.
    if min(angle, 360-angle) <= 1:
        name, emoji = 'New Moon', '🌑'
    elif abs(angle - 90) <= 1:
        name, emoji = 'First Quarter', '🌓'
    elif abs(angle - 180) <= 1:
        name, emoji = 'Full Moon', '🌕'
    elif abs(angle - 270) <= 1:
        name, emoji = 'Last Quarter', '🌗'
    elif angle < 90:
        name, emoji = 'Waxing Crescent', '🌒'
    elif angle < 180:
        name, emoji = 'Waxing Gibbous', '🌔'
    elif angle < 270:
        name, emoji = 'Waning Gibbous', '🌖'
    else:
        name, emoji = 'Waning Crescent', '🌘'
    next_phase = ae.SearchMoonQuarter(t)
    phase = dict(phase_name=name, emoji=emoji, phase_angle_deg=round(angle, 3),
                 illumination_percent=round(illumination, 2), waxing=angle < 180,
                 moon_sign=positions['Moon']['sign'], moon_formatted=positions['Moon']['formatted'],
                 phase_convention='Principal phase names within ±1° of their exact elongation; otherwise crescent or gibbous.',
                 next_phase=['New Moon','First Quarter','Full Moon','Last Quarter'][next_phase.quarter],
                 next_phase_at=str(next_phase.time), archetype=f'{name} reflection',
                 description=f'The Moon was {name.lower()}, with {illumination:.2f}% of its visible disc illuminated. This describes Sun–Moon geometry, not a fixed personality.',
                 gifts=['Reflect on your own rhythms', 'Notice what supports you'])
    return {**positions, 'LunarPhase': phase}


def compute_planetary_positions(dt, zodiac='tropical'):
    # Callers may enrich their own result without mutating a cached snapshot.
    import copy
    return copy.deepcopy(positions_at(str(astro_time(dt)), zodiac))


def daily_transits(sign='Scorpio', date_str=None, timezone_name='UTC', zodiac='tropical', now=None):
    sign = sign.capitalize()
    if sign not in SIGNS:
        raise ValueError('Choose one of the twelve zodiac signs.')
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError('Choose a valid IANA timezone.') from exc
    current = (now or datetime.now(timezone.utc)).astimezone(zone)
    if date_str:
        try:
            requested = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError as exc:
            raise ValueError('Date must be a valid YYYY-MM-DD date.') from exc
        if not 1900 <= requested.year <= 2100:
            raise ValueError('Choose a date between 1900 and 2100.')
        dt = current if requested == current.date() else datetime.combine(requested, datetime.min.time(), zone).replace(hour=12)
    else:
        dt = current
    pos = compute_planetary_positions(dt, zodiac)
    phase = pos['LunarPhase']
    forecast = transit_forecast(sign, pos)
    return dict(date=dt.date().isoformat(), timezone=timezone_name, as_of=dt.isoformat(),
                calculated_at_utc=dt.astimezone(timezone.utc).isoformat(), zodiac=zodiac,
                zodiac_label='Tropical' if zodiac == 'tropical' else 'Sidereal (Lahiri)',
                selected_sign=sign, moon_phase=f"{phase['phase_name']} in {pos['Moon']['sign']}",
                moon_emoji=phase['emoji'], illumination_percent=phase['illumination_percent'], moon=phase,
                planets=[pos[p] for p in PLANETS], sun_position=pos['Sun']['formatted'],
                sun_element_badge=pos['Sun']['element'], mercury_status=f"{pos['Mercury']['formatted']} ({pos['Mercury']['motion']})",
                venus_status=f"{pos['Venus']['formatted']} ({pos['Venus']['motion']})", mars_status=pos['Mars']['formatted'],
                forecast=forecast, calculation_method='Astronomy Engine 2.1.19; apparent geocentric ecliptic of date',
                date_note='Current time for today; local noon for other dates.')


def house_cusps(dt, latitude, longitude, system='placidus'):
    t = astro_time(dt)
    theta = ae.SiderealTime(t) * 15 + longitude
    eps = math.acos(ae.Rotation_EQD_ECT(t).rot[1][1])
    th, phi = math.radians(theta), math.radians(latitude)
    asc = (math.degrees(math.atan2(-math.cos(th), math.sin(th)*math.cos(eps) + math.tan(phi)*math.sin(eps))) + 180) % 360
    mc = math.degrees(math.atan2(math.sin(th), math.cos(th)*math.cos(eps))) % 360
    if system == 'equal':
        return [(asc + i*30) % 360 for i in range(12)], asc, mc
    if system == 'whole_sign':
        return [(int(asc//30)*30 + i*30) % 360 for i in range(12)], asc, mc
    if system != 'placidus':
        raise ValueError('Choose Placidus, Equal or Whole Sign houses.')
    if abs(latitude) >= 66:
        raise ValueError('Placidus houses are not reliable at this polar latitude. Choose Whole Sign or Equal houses.')

    def equation(lon, fraction, lower):
        lam = math.radians(lon)
        ra = math.degrees(math.atan2(math.sin(lam)*math.cos(eps), math.cos(lam)))
        dec = math.asin(math.sin(eps)*math.sin(lam))
        arc = math.degrees(math.acos(max(-1, min(1, -math.tan(phi)*math.tan(dec)))))
        target = theta + (arc + fraction*(180-arc) if lower else fraction*arc)
        return signed(ra-target)

    def root(start, end, fraction, lower=False):
        end = start + (end-start) % 360
        lo, hi = start, end
        for _ in range(65):
            mid = (lo+hi)/2
            if equation(mid, fraction, lower) < 0:
                lo = mid
            else:
                hi = mid
        return ((lo+hi)/2) % 360

    c11, c12 = root(mc, asc, 1/3), root(mc, asc, 2/3)
    c2, c3 = root(asc, (mc+180)%360, 1/3, True), root(asc, (mc+180)%360, 2/3, True)
    cusps = [asc,c2,c3,(mc+180)%360,(c11+180)%360,(c12+180)%360,(asc+180)%360,(c2+180)%360,(c3+180)%360,mc,c11,c12]
    return cusps, asc, mc


def house_for(longitude, cusps):
    for i, start in enumerate(cusps):
        if (longitude-start) % 360 < (cusps[(i+1)%12]-start) % 360:
            return i+1
    return 1


def natal_chart(dt, latitude, longitude, name='', zodiac='tropical', house_system='placidus', chart_system='natal', rulership='modern'):
    if rulership not in ('modern','traditional'):
        raise ValueError('Choose modern or traditional house rulership.')
    if chart_system not in ('natal','placidus','tropical','progressed'):
        raise ValueError('Unknown chart system.')
    calculation_dt = dt
    if chart_system == 'progressed':
        age = max(0, (datetime.now(timezone.utc) - dt).total_seconds()/86400/365.2425)
        calculation_dt = dt + timedelta(days=age)
    pos = compute_planetary_positions(calculation_dt, zodiac)
    cusps, asc, mc = house_cusps(calculation_dt, latitude, longitude, house_system)
    offset = zodiac_offset(astro_time(calculation_dt), zodiac)
    cusps = [(c-offset)%360 for c in cusps]
    # Whole-sign cusps must start at the chosen zodiac's sign boundary.
    if house_system == 'whole_sign':
        cusps = [(int(((asc-offset)%360)//30)*30 + i*30)%360 for i in range(12)]
    asc, mc = (asc-offset)%360, (mc-offset)%360
    placements = []
    for p in PLANETS:
        row = {**pos[p], 'house': house_for(pos[p]['longitude'], cusps)}
        row['paragraphs'] = planet_report(p, row, row['house'])
        placements.append(row)
    houses = [dict(number=i+1, title=HOUSE_THEMES[i][0], **sign_position(c),
                   description=house_report(i+1, sign_position(c)['sign'])) for i,c in enumerate(cusps)]
    enrich_houses(houses,placements,rulership)
    aspects = []
    for i, a in enumerate(placements):
        for b in placements[i+1:]:
            aspect=aspect_between(a,b)
            if aspect:aspects.append(aspect)
    aspects.sort(key=lambda a:a['orb'])
    # Natal angle motion includes Earth's rotation, as well as planetary motion.
    # Derive it from two real sky instants; do not guess from zodiac order.
    before=house_cusps(calculation_dt-timedelta(minutes=1),latitude,longitude,'equal')
    after=house_cusps(calculation_dt+timedelta(minutes=1),latitude,longitude,'equal')
    asc_speed=signed(after[1]-before[1])*720
    mc_speed=signed(after[2]-before[2])*720
    angles=[angle_report(n,c,sign_position(lon),speed,placements,rulership) for n,c,lon,speed in
            [('Ascendant','ASC',asc,asc_speed),('Midheaven','MC',mc,mc_speed),
             ('Descendant','DC',(asc+180)%360,asc_speed),('Imum Coeli','IC',(mc+180)%360,mc_speed)]]
    result = dict(name=name, title=('Secondary progressed' if chart_system == 'progressed' else 'Natal')+' birth chart',
                  zodiac=zodiac, zodiac_label='Tropical' if zodiac == 'tropical' else 'Sidereal (Lahiri)',
                  ayanamsa_degrees=round(lahiri_ayanamsa(astro_time(calculation_dt)),6) if zodiac == 'sidereal' else 0,
                  house_system=house_system, system=chart_system, rulership=rulership,
                  ascendant=sign_position(asc)['formatted'], midheaven=sign_position(mc)['formatted'],
                  ascendant_longitude=asc, midheaven_longitude=mc,
                  placements=placements, houses=houses, aspects=aspects, angles=angles,
                  aspect_settings={'Conjunction':8,'Sextile':4,'Square':6,'Trine':6,'Opposition':8,'angles':8},
                  aspect_motion_note='Applying means the angular error is decreasing at the calculation instant; separating means it is increasing. Angle aspects include the motion of the local horizon/meridian.',
                  reference_url='https://horoscopes.astro-seek.com/calculate-birth-chart-horoscope-online/',
                  elements={e:sum(p['element']==e for p in placements) for e in ELEMENTS},
                  modalities={m:sum(p['modality']==m for p in placements) for m in MODES},
                  calculation_time_utc=calculation_dt.isoformat(),
                  calculation_method='Astronomy Engine 2.1.19; geocentric apparent positions; Placidus semi-arc / Equal / Whole Sign houses.',
                  report_note='Astrology is a symbolic tradition, not a scientific personality assessment or prediction. House positions depend on an accurate birth time. Sidereal uses a mean Lahiri model accurate to within 0.01° over 1900–2100.',
                  asteroids=[])
    from .chart_wheel import wheel_svg
    result['wheel_svg'] = wheel_svg(result)
    return result
