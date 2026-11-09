"""Original house/angle interpretations built from measured natal positions.

Report structure follows the owner's Astro-Seek reference screenshot. No remote
report text is fetched or copied. Rulership is an explicit astrological convention.
"""
from .chart_interpretations import SIGNS, SIGN_STYLE, PLANET_THEMES, HOUSE_THEMES, ASPECT_TEXT

MODERN_RULERS = dict(zip(SIGNS, ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Pluto','Jupiter','Saturn','Uranus','Neptune']))
TRADITIONAL_RULERS = {**MODERN_RULERS, 'Scorpio':'Mars','Aquarius':'Saturn','Pisces':'Jupiter'}
ASPECTS = [('Conjunction',0,8),('Sextile',60,4),('Square',90,6),('Trine',120,6),('Opposition',180,8)]


def orb_text(orb):
    degrees, minutes = divmod(round(orb*60),60)
    return f'{degrees}°{minutes:02d}′'


def aspect_between(a,b,angle_orb=None):
    delta = (b['longitude']-a['longitude']+180)%360-180
    separation = abs(delta)
    relative_speed = b['speed_deg_per_day']-a['speed_deg_per_day']
    separation_rate = relative_speed if delta >= 0 else -relative_speed
    for label, target, default_orb in ASPECTS:
        limit = angle_orb if angle_orb is not None else default_orb
        error = separation-target
        if abs(error) <= limit:
            if abs(error)<.001:
                motion='Exact'
            elif abs(separation_rate)<1e-8:
                motion='Stationary'
            else:
                motion='Applying' if error*separation_rate<0 else 'Separating'
            return dict(planet_a=a['planet'],planet_b=b['planet'],aspect=label,angle=target,
                        separation=round(separation,3),orb=round(abs(error),3),
                        orb_formatted=orb_text(abs(error)),motion=motion,
                        description=ASPECT_TEXT[label])
    return None


def enrich_houses(houses,placements,rulership):
    rulers=MODERN_RULERS if rulership=='modern' else TRADITIONAL_RULERS
    by_name={p['planet']:p for p in placements}
    for h in houses:
        ruler=by_name[rulers[h['sign']]]
        number=h['number']
        h['ruling_planet']=ruler['planet']
        h['ruler_placement']={key:ruler[key] for key in ['planet','sign','formatted','house','retrograde']}
        h['occupants']=[p['planet'] for p in placements if p['house']==number]
        h['ruler_paragraphs']=[
            f"In {rulership} rulership, {h['sign']} is ruled by {ruler['planet']}. The ruler of house {number} is therefore {ruler['planet']}, located at {ruler['formatted']} in house {ruler['house']}.",
            f"{ruler['planet']} in {ruler['sign']} brings themes of {PLANET_THEMES[ruler['planet']][0]} into the discussion. Its symbolic approach emphasizes {SIGN_STYLE[SIGNS.index(ruler['sign'])]}.",
            f"The ruler of house {number} in house {ruler['house']} connects {HOUSE_THEMES[number-1][1]} with {HOUSE_THEMES[ruler['house']-1][1]}. Consider how choices in one area support or complicate the other; this is a reflection prompt rather than a prediction.",
        ]


def angle_report(name,code,position,speed,placements,rulership):
    rulers=MODERN_RULERS if rulership=='modern' else TRADITIONAL_RULERS
    ruler=next(p for p in placements if p['planet']==rulers[position['sign']])
    themes={
        'ASC':('Self & first impressions','The Ascendant is the ecliptic point rising on the eastern horizon at birth. In astrology it describes an approach to new situations and the way you begin presenting yourself to others.'),
        'MC':('Vocation & public life','The Midheaven is the upper intersection of the meridian with the ecliptic. Astrologers connect it with public responsibilities, vocation and the contribution you want to be recognized for.'),
        'DC':('Partnerships & agreements','The Descendant is opposite the Ascendant. Its symbolism concerns one-to-one relationships, the qualities you notice in others and the agreements you make together.'),
        'IC':('Home & foundations','The Imum Coeli is opposite the Midheaven. Its symbolism concerns privacy, home, roots and the foundations that support life outside the public eye.'),
    }
    topic,intro=themes[code]
    aspects=[]
    point={**position,'planet':name,'speed_deg_per_day':speed}
    for p in placements:
        aspect=aspect_between(point,p,angle_orb=8)
        if aspect:aspects.append(aspect)
    aspects.sort(key=lambda a:a['orb'])
    return dict(name=name,code=code,topic=topic,**position,
                ruling_planet=ruler['planet'],
                ruler_placement={key:ruler[key] for key in ['planet','sign','formatted','house','retrograde']},
                paragraphs=[intro,
                    f"{name} in {position['sign']} emphasizes {SIGN_STYLE[SIGNS.index(position['sign'])]}. Read this together with the ruler's placement and the rest of the chart.",
                    f"Its {rulership} ruler, {ruler['planet']}, is in {ruler['sign']} and house {ruler['house']}. This links {topic.lower()} with {HOUSE_THEMES[ruler['house']-1][1]}."] ,
                aspects=aspects)
