"""Birth-based angular planetary lines, from apparent geocentric equatorial positions.

MC/IC are the upper/lower meridians; ASC/DSC solve geometric altitude=0.
No refraction, terrain, parans or relocated-house claims are included.
"""
import json
import math
from html import escape
from pathlib import Path
from functools import lru_cache
import astronomy as ae
from .birth_locations import resolve_birth, city_records, catalog
from .sky_engine import PLANETS, GLYPHS, astro_time, signed

COLORS = ['#ffce54','#d4e6ff','#67e3d1','#ff83cb','#ff876c','#bca0ff','#dfc39b','#7cddff','#8fafff','#e8a5ed']
THEMES = {
 'Sun':'Visibility, confidence and self-expression', 'Moon':'Emotional needs, belonging and familiar rhythms',
 'Mercury':'Communication, learning and networking', 'Venus':'Connection, affection, beauty and harmony',
 'Mars':'Drive and initiative; conflict and pressure may also be themes', 'Jupiter':'Growth, opportunity and exploration',
 'Saturn':'Responsibility, patient effort and boundaries', 'Uranus':'Independence, reinvention and change',
 'Neptune':'Imagination and spirituality; clarity and boundaries matter', 'Pluto':'Intensity, power and deep transformation'}
ANGLES = {'ASC':'Rising: identity and how you meet the world', 'DSC':'Setting: relationships and partnerships',
          'MC':'Upper culmination: public life, vocation and visibility', 'IC':'Lower culmination: home, roots and private life'}
FOCUS = {'home':[('Moon','IC'),('Venus','IC'),('Jupiter','IC'),('Sun','IC')],
         'relationships':[('Venus','DSC'),('Jupiter','DSC'),('Moon','DSC'),('Sun','ASC')],
         'career':[('Sun','MC'),('Jupiter','MC'),('Mercury','MC'),('Saturn','MC')],
         'retreat':[('Moon','IC'),('Neptune','IC'),('Venus','IC')],
         'reinvention':[('Uranus','ASC'),('Sun','ASC'),('Pluto','ASC')],
         'growth':[('Jupiter','ASC'),('Sun','ASC'),('Mercury','ASC'),('Venus','ASC')]}
R = 6371.0088


def angular_points(ra, dec, sidereal):
    meridian = signed(ra*15-sidereal*15)
    result = {'MC': [[-89.9,meridian],[89.9,meridian]],
              'IC': [[-89.9,signed(meridian+180)],[89.9,signed(meridian+180)]], 'ASC':[], 'DSC':[]}
    # Parameterize each complete horizon semicircle, including its polar
    # tangent endpoints. Latitude-only sampling would truncate those bends.
    lam, delta = math.radians(meridian), math.radians(dec)
    north=[-math.sin(delta)*math.cos(lam),-math.sin(delta)*math.sin(lam),math.cos(delta)]
    east=[-math.sin(lam),math.cos(lam),0]
    for angle,sign in [('ASC',-1),('DSC',1)]:
        for step in range(181):
            theta=math.radians(step)
            x,y,z=[north[i]*math.cos(theta)+sign*east[i]*math.sin(theta) for i in range(3)]
            lat=math.degrees(math.asin(max(-1,min(1,z))))
            lon=signed(meridian+sign*90) if math.hypot(x,y)<1e-12 else math.degrees(math.atan2(y,x))
            result[angle].append([lat,lon])
    return meridian, result


def distance_to_line(lat, lon, planet, angle):
    h = math.radians(signed(lon-planet['mc_longitude']))
    phi, dec = math.radians(lat), math.radians(planet['declination'])
    if angle in ('MC','IC'):
        delta = math.radians(signed(lon-planet['mc_longitude']-(180 if angle=='IC' else 0)))
        # Distance to the correct half-meridian, not its opposite (MC vs IC).
        return R*(math.pi/2-abs(phi) if math.cos(delta)<0 else math.asin(min(1,abs(math.cos(phi)*math.sin(delta)))))
    # Project onto the horizon great circle, then check which semicircle that
    # closest point lies on. For the opposite branch the closest point is an
    # endpoint, not a falsely nearby line on the other side of the planet.
    dot = math.sin(phi)*math.sin(dec)+math.cos(phi)*math.cos(dec)*math.cos(h)
    x=math.cos(phi)*math.cos(h)-dot*math.cos(dec)
    y=math.cos(phi)*math.sin(h)
    z=math.sin(phi)-dot*math.sin(dec)
    norm=math.sqrt(x*x+y*y+z*z)
    if norm<1e-12: return R*math.pi/2
    if (angle=='ASC' and y<=0) or (angle=='DSC' and y>=0):
        return R*abs(math.asin(max(-1,min(1,dot))))
    endpoint_dot=-math.cos(phi)*math.cos(h)*math.sin(dec)+math.sin(phi)*math.cos(dec)
    return R*math.acos(min(1,abs(endpoint_dot)))


def nearby_lines(planets, lat, lon, radius=500):
    found=[]
    for planet in planets:
        for angle in ANGLES:
            km=distance_to_line(lat,lon,planet,angle)
            if km<=radius:
                found.append(dict(planet=planet['planet'],angle=angle,distance_km=round(km),
                                  distance_miles=round(km/1.609344),interpretation=THEMES[planet['planet']]+'. '+ANGLES[angle]+'.'))
    return sorted(found,key=lambda x:x['distance_km'])


def crossings(planets):
    result=[]
    def normals(p):
        lon=math.radians(p['mc_longitude']);dec=math.radians(p['declination'])
        return {'meridian':[-math.sin(lon),math.cos(lon),0],
                'horizon':[math.cos(dec)*math.cos(lon),math.cos(dec)*math.sin(lon),math.sin(dec)]}
    def angle(p,kind,lon):
        h=math.radians(signed(lon-p['mc_longitude']))
        return ('MC' if math.cos(h)>=0 else 'IC') if kind=='meridian' else ('ASC' if math.sin(h)<=0 else 'DSC')
    for i,a in enumerate(planets):
        for b in planets[i+1:]:
            for ka,na in normals(a).items():
                for kb,nb in normals(b).items():
                    cross=[na[1]*nb[2]-na[2]*nb[1],na[2]*nb[0]-na[0]*nb[2],na[0]*nb[1]-na[1]*nb[0]]
                    norm=math.sqrt(sum(v*v for v in cross))
                    if norm<1e-10:continue
                    for sign in [-1,1]:
                        x,y,z=[v*sign/norm for v in cross]
                        lat=math.degrees(math.asin(max(-1,min(1,z))));lon=math.degrees(math.atan2(y,x))
                        if abs(lat)>80:continue
                        aa,ab=angle(a,ka,lon),angle(b,kb,lon)
                        combo=f'{a["planet"]} {aa} + {b["planet"]} {ab}'
                        reading=THEMES[a['planet']]+'. '+ANGLES[aa]+'. '+THEMES[b['planet']]+'. '+ANGLES[ab]+'.'
                        if {a['planet'],b['planet']}=={'Sun','Jupiter'}:reading+=' Astrology often associates this pairing with optimism, visibility and opportunity.'
                        if {a['planet'],b['planet']}=={'Mars','Saturn'}:reading+=' Drive meets discipline: this can symbolize productive effort alongside tension and limits.'
                        result.append(dict(latitude=lat,longitude=lon,planet_a=a['planet'],angle_a=aa,
                                           planet_b=b['planet'],angle_b=ab,title=combo,interpretation=reading))
    return result


@lru_cache(maxsize=1)
def candidate_cities():
    countries = catalog().get_countries()
    return [(c,countries[c['countrycode']]['name']) for c in city_records().values()
            if c.get('population',0)>=100000 and abs(c['latitude'])<=75]


def suggestions(planets, focus):
    lookup = {p['planet']:p for p in planets}; ranked=[]
    for city,country in candidate_cities():
        options=[]
        for name,angle in FOCUS[focus]:
            distance=distance_to_line(city['latitude'],city['longitude'],lookup[name],angle)
            if distance is not None: options.append((distance,name,angle))
        if not options: continue
        km,name,angle=min(options)
        ranked.append((km,city,country,name,angle))
    ranked.sort(key=lambda x:(x[0],-x[1]['population'],x[1]['name']))
    found=[]; counts={}
    for km,c,country,name,angle in ranked:
        if counts.get(country,0)>=2: continue
        if any(abs(c['latitude']-r['latitude'])<2 and abs(signed(c['longitude']-r['longitude']))<2 for r in found):continue
        counts[country]=counts.get(country,0)+1
        found.append(dict(city=c['name'],country=country,latitude=c['latitude'],longitude=c['longitude'],
                          planet=name,angle=angle,distance_km=round(km),distance_miles=round(km/1.609344),
                          interpretation=THEMES[name]+'. '+ANGLES[angle]+'.'))
        if len(found)==8:break
    return found


def project(lat,lon): return ((lon+180)*1200/360,(90-lat)*600/180)


@lru_cache(maxsize=1)
def land_paths():
    data=json.loads(Path(__file__).parents[1].joinpath('data/world_land_110m.geojson').read_text())
    parts=[]
    for feature in data['features']:
        geometry=feature['geometry']; polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
        for polygon in polygons:
            d=''
            for ring in polygon:
                coords=[project(lat,lon) for lon,lat in ring]
                d+='M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in coords)+'Z'
            parts.append(f'<path d="{d}"/>')
    return ''.join(parts)


def line_path(points):
    path='';previous=None
    for lat,lon in points:
        x,y=project(lat,lon)
        path+=('M' if previous is None or abs(lon-previous)>180 else 'L')+f'{x:.2f},{y:.2f}'
        previous=lon
    return path


def map_svg(planets, places, location, intersections):
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" role="img" aria-label="Your birth-based astrocartography world map"><rect width="1200" height="600" fill="#160d32"/>'
    svg+='<g stroke="#ab9bc1" opacity=".25" stroke-width=".6">'
    for lon in range(-150,180,30):
        x,_=project(0,lon);svg+=f'<path d="M{x},0V600"/>'
    for lat in range(-60,90,30):
        _,y=project(lat,0);svg+=f'<path d="M0,{y}H1200"/>'
    svg+='</g><g fill="#c5b0d9" fill-opacity=".25" stroke="#c5b0d9" stroke-width=".6" fill-rule="evenodd">'+land_paths()+'</g>'
    for planet in planets:
        name=planet['planet'];svg+=f'<g data-planet="{name}" stroke="{planet["color"]}" fill="none">'
        for angle,points in planet['lines'].items():
            dash={'MC':'','IC':'8 5','ASC':'2 4','DSC':'10 3 2 3'}[angle]
            svg+=f'<path class="astro-line" data-action="astro-line" data-planet="{name}" data-angle="{angle}" tabindex="0" role="button" aria-label="{name} {angle} line" d="{line_path(points)}" stroke-width="1.6" stroke-dasharray="{dash}" opacity=".8"><title>{name} {angle}: {escape(THEMES[name])}</title></path>'
        svg+='</g>'
    for index,point in enumerate(intersections):
        x,y=project(point['latitude'],point['longitude'])
        svg+=f'<circle class="astro-crossing" data-action="astro-crossing" data-crossing-index="{index}" cx="{x:.2f}" cy="{y:.2f}" r="2.8" fill="#fff" opacity=".55" tabindex="0" role="button" aria-label="{point["title"]} crossing"><title>{point["title"]}</title></circle>'
    for index,place in enumerate(places,1):
        x,y=project(place['latitude'],place['longitude']);svg+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#ffcf69" stroke="#160d32"/><text x="{x+7:.2f}" y="{y-5:.2f}" fill="#fff" font-size="12">{index}</text>'
    x,y=project(location['latitude'],location['longitude'])
    svg+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#fff" stroke="#f785d9" stroke-width="2"><title>Birthplace: {escape(location["label"])}</title></circle></svg>'
    return svg


def astrocartography_report(data):
    utc,location,local=resolve_birth(data);t=astro_time(utc);sidereal=ae.SiderealTime(t)
    rotation=ae.Rotation_EQJ_EQD(t);planets=[]
    for i,name in enumerate(PLANETS):
        eq=ae.EquatorFromVector(ae.RotateVector(rotation,ae.GeoVector(getattr(ae.Body,name),t,True)))
        mc,lines=angular_points(eq.ra,eq.dec,sidereal)
        planets.append(dict(planet=name,glyph=GLYPHS[i],color=COLORS[i],right_ascension_hours=eq.ra,
                            declination=eq.dec,mc_longitude=mc,interpretation=THEMES[name],lines=lines))
    places=suggestions(planets,data.focus);intersections=crossings(planets)
    for place in places:place['nearby_lines']=nearby_lines(planets,place['latitude'],place['longitude'])
    return dict(report_type='astrocartography',title='Your Astrocartography Map',name=data.name,focus=data.focus,
                birth_utc=utc.isoformat(),birth_local_time=local,location=location,
                sidereal_time_hours=sidereal,planets=planets,angle_meanings=ANGLES,places=places,
                crossings=intersections,map_svg=map_svg(planets,places,location,intersections),
                method='Apparent geocentric equatorial positions (Astronomy Engine), Greenwich apparent sidereal time, geometric rising/setting and upper/lower meridians. No refraction, terrain, parans or relocated houses.',
                proximity_note='Astrocartography traditions often emphasize places within roughly 200–300 miles of a line. This is an interpretive convention, not a measured energy field.',
                note='These are symbolic astrological interpretations, not guarantees of the best place to live. Suggestions rank major cities by proximity to the lines associated with your chosen focus; practical factors such as work, housing and community still matter. Exact recorded birth time is important: a few minutes can shift the lines.',
                map_credit='Land: Natural Earth 1:110m (public domain). Cities: GeoNames (CC BY 4.0).',
                map_source='https://www.naturalearthdata.com/about/terms-of-use/')
