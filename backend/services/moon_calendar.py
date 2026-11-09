"""Monthly lunar snapshots plus exact principal-phase events, in local time."""
import calendar
import math
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import astronomy as ae
from .sky_engine import astro_time, compute_planetary_positions, longitude_at, zodiac_offset, signed, SIGNS, SIGN_GLYPHS


# Historical astrological correspondences, not medical effects or risk estimates.
BODY_ASSOCIATIONS = dict(zip(SIGNS, [
    'Head, face, brain, eyes', 'Neck, throat, vocal cords, thyroid',
    'Shoulders, arms, hands, lungs', 'Chest, breasts, stomach',
    'Heart, aorta, blood pressure, blood circulation',
    'Pancreas, small intestine, digestive tract',
    'Kidneys, ureters, urinary bladder, veins, skin',
    'Genitals, anus, urethra, prostate', 'Liver, hips, thighs, sacrum',
    'Bones, joints, knees, teeth, skin', 'Calves, ankles, veins',
    'Feet, toes, lymphatic system']))
HEALTH_NOTE = ('Body associations are traditional astrology lore, not established medical effects. '
               'Moon phases and signs cannot determine whether surgery is safe. '
               'Follow your surgical team’s advice; do not delay needed care based on this calendar.')



def moon_disc_svg(angle):
    """Geometric illuminated disc; waxing right, waning left, north-up convention."""
    mirror=1 if angle<180 else -1
    cosine=math.cos(math.radians(angle))
    ys=[-1+2*i/48 for i in range(49)]
    outer=[(mirror*math.sqrt(max(0,1-y*y)),y) for y in ys]
    inner=[(mirror*cosine*math.sqrt(max(0,1-y*y)),y) for y in reversed(ys)]
    points=' '.join(f'{24+21*x:.3f},{24+21*y:.3f}' for x,y in outer+inner)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
            '<circle cx="24" cy="24" r="22" fill="#171129" stroke="#d2b9e4"/>'
            f'<polygon points="{points}" fill="#ffedc5"/>'
            '<circle cx="24" cy="24" r="21" fill="none" stroke="#bda7d3" stroke-width=".4"/></svg>')

def moon_longitude(dt, zodiac):
    t=astro_time(dt)
    return (longitude_at('Moon',t)-zodiac_offset(t,zodiac))%360


def sign_interval(sign, start, end, zone):
    return dict(sign=SIGNS[sign],glyph=SIGN_GLYPHS[sign],
                from_utc=start.isoformat(),until_utc=end.isoformat(),
                from_local=start.astimezone(zone).isoformat(),until_local=end.astimezone(zone).isoformat(),
                traditional_body_associations=BODY_ASSOCIATIONS[SIGNS[sign]])


def moon_ingresses(start,end,zone,zodiac):
    # Scan in six-hour steps, then bisect each 30-degree boundary to <1 second.
    # Geocentric Moon motion is direct, crossing at most one boundary per step.
    events=[]
    left=start.astimezone(timezone.utc)
    stop=end.astimezone(timezone.utc)
    while left<stop:
        right=min(left+timedelta(hours=6),stop)
        sign=int(moon_longitude(left,zodiac)//30)
        if int(moon_longitude(right,zodiac)//30)!=sign:
            target=((sign+1)*30)%360
            lo,hi=left,right
            while (hi-lo).total_seconds()>.5:
                mid=lo+(hi-lo)/2
                if signed(moon_longitude(mid,zodiac)-target)<0:lo=mid
                else:hi=mid
            at=hi
            local=at.astimezone(zone)
            events.append(dict(sign=SIGNS[(sign+1)%12],glyph=SIGN_GLYPHS[(sign+1)%12],
                               at_utc=at.isoformat(),at_local=local.isoformat(),date=local.date().isoformat()))
        left=right
    return events

PHASES=['New Moon','First Quarter','Full Moon','Last Quarter']
EMOJI=['🌑','🌓','🌕','🌗']


def monthly_moon_calendar(year=None,month=None,timezone_name='UTC',zodiac='tropical'):
    try:
        zone=ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError('Choose a valid IANA timezone.') from exc
    today=datetime.now(timezone.utc).astimezone(zone)
    year=today.year if year is None else year
    month=today.month if month is None else month
    if not 1900<=year<=2100 or not 1<=month<=12:
        raise ValueError('Choose a month from 1 to 12 and a year from 1900 to 2100.')
    if zodiac not in ('tropical','sidereal'):
        raise ValueError('Choose tropical or sidereal zodiac.')
    return _calendar(year,month,timezone_name,zodiac)


@lru_cache(maxsize=64)
def _calendar(year,month,timezone_name,zodiac):
    zone=ZoneInfo(timezone_name)
    first_weekday,number_of_days=calendar.monthrange(year,month)
    start=datetime(year,month,1,tzinfo=zone)
    end=datetime(year+int(month==12),1 if month==12 else month+1,1,tzinfo=zone)
    phase=ae.SearchMoonQuarter(astro_time(start))
    events=[]
    while True:
        utc=datetime.fromisoformat(str(phase.time).replace('Z','+00:00'))
        if utc>=end:
            break
        if utc>=start:
            local=utc.astimezone(zone)
            events.append(dict(phase=PHASES[phase.quarter],emoji=EMOJI[phase.quarter],
                               at_utc=utc.isoformat(),at_local=local.isoformat(),date=local.date().isoformat()))
        phase=ae.NextMoonQuarter(phase)
    ingresses=moon_ingresses(start,end,zone,zodiac)
    days=[]
    for number in range(1,number_of_days+1):
        noon=datetime(year,month,number,12,tzinfo=zone)
        local=noon.astimezone(timezone.utc).astimezone(zone)
        date=noon.date().isoformat()
        if local.date()!=noon.date():
            days.append(dict(day=number,date=date,available=False,
                             note='This civil date was skipped by a historical timezone change.',events=[]))
            continue
        day_start=datetime(year,month,number,tzinfo=zone).astimezone(timezone.utc)
        day_end=(datetime(year,month,number,tzinfo=zone)+timedelta(days=1)).astimezone(timezone.utc)
        changes=[e for e in ingresses if day_start<=datetime.fromisoformat(e['at_utc'])<day_end]
        intervals=[]
        cursor=day_start
        sign=int(moon_longitude(cursor,zodiac)//30)
        for event in changes:
            at=datetime.fromisoformat(event['at_utc'])
            intervals.append(sign_interval(sign,cursor,at,zone))
            cursor=at;sign=SIGNS.index(event['sign'])
        intervals.append(sign_interval(sign,cursor,day_end,zone))
        pos=compute_planetary_positions(noon,zodiac)
        moon=pos['LunarPhase']
        days.append(dict(day=number,date=date,weekday=noon.strftime('%A'),available=True,
                         phase=moon['phase_name'],emoji=moon['emoji'],waxing=moon['waxing'],
                         illumination_percent=moon['illumination_percent'],
                         moon_sign=pos['Moon']['sign'],moon_position=pos['Moon']['formatted'],
                         sign_intervals=intervals,ingresses=changes,
                         surgery_guidance='Ask your surgical team; Moon placement does not establish safety.',
                         phase_angle_deg=moon['phase_angle_deg'],moon_image_svg=moon_disc_svg(moon['phase_angle_deg']),snapshot_at=noon.isoformat(),
                         events=[e for e in events if e['date']==date]))
    return dict(year=year,month=month,title=f'{calendar.month_name[month]} {year}',
                timezone=timezone_name,zodiac=zodiac,first_weekday=first_weekday,
                weekdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],days=days,events=events,ingresses=ingresses,health_note=HEALTH_NOTE,
                note='Daily illumination and Moon sign are calculated at local noon. Sign intervals use calculated ingress times, in the selected timezone. Principal phase markers show exact events, which can occur at another time on the same date.',
                reference_url='https://mooncalendar.astro-seek.com/moon-phases-calendar-november-2026')
