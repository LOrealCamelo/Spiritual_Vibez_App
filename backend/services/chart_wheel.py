"""One self-contained vector chart shared by browsers and react-native-svg."""
import math
from html import escape

SIGN_GLYPHS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']


def wheel_svg(chart):
    asc = chart['ascendant_longitude']

    def point(lon, r):
        a = math.radians(180 + asc - lon)
        return (380+r*math.cos(a), 380+r*math.sin(a))

    def line(a, b, color, width=1):
        return f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="{width}"/>'

    def text(lon, r, label, size=14, color='#3a156b', y_offset=0):
        x,y = point(lon,r)
        return f'<text x="{x:.2f}" y="{y+size*.34+y_offset:.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{size}" fill="{color}">{escape(str(label))}</text>'

    pieces = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 760">',
              '<title>Birth chart: zodiac signs, twelve houses, planets and major aspects</title>',
              '<circle cx="380" cy="380" r="357" fill="#fff8fc" stroke="#ee75b9" stroke-width="3"/>']
    for index, sign in enumerate(SIGNS):
        start,end = index*30, (index+1)*30
        a,b,c,d = point(start,340),point(end,340),point(end,285),point(start,285)
        path = f'M {a[0]} {a[1]} A 340 340 0 0 0 {b[0]} {b[1]} L {c[0]} {c[1]} A 285 285 0 0 1 {d[0]} {d[1]} Z'
        pieces.append(f'<path d="{path}" fill="{["#ffe5c6","#f1e4ff","#dcf7f4","#ffe0f1"][index%4]}" stroke="#b99ac9" stroke-width="1"/>')
        pieces.append(text(start+15,313,SIGN_GLYPHS[index]+'\ufe0e',23,y_offset=-8))
        pieces.append(text(start+15,313,sign,10,y_offset=13))
    for degree in range(360):
        pieces.append(line(point(degree,285),point(degree,280 if degree%5 else 275),'#9e7aae'))
    for r in (180,250,273,285,340):
        pieces.append(f'<circle cx="380" cy="380" r="{r}" fill="none" stroke="#c5a8d1" stroke-width="1"/>')
    cusps = [h['longitude'] for h in chart['houses']]
    for i,lon in enumerate(cusps):
        pieces.append(line(point(lon,180),point(lon,285),'#82639c',2 if i%3==0 else 1))
        midpoint = lon+((cusps[(i+1)%12]-lon)%360)/2
        pieces.append(text(midpoint,261,i+1,13))
    positions = {p['planet']:p['longitude'] for p in chart['placements']}
    for aspect in chart['aspects']:
        color = '#d45c90' if aspect['aspect'] in ('Square','Opposition') else '#55a2bd' if aspect['aspect'] in ('Trine','Sextile') else '#a17bc4'
        pieces.append(line(point(positions[aspect['planet_a']],175),point(positions[aspect['planet_b']],175),color,1))
    # Preserve actual longitude markers and move only their labels to avoid collisions.
    ordered = sorted(chart['placements'],key=lambda p:p['longitude'])
    labels = [p['longitude'] for p in ordered]
    for _ in range(40):
        for i in range(len(labels)):
            j=(i+1)%len(labels)
            gap=(labels[j]-labels[i])%360
            if gap<14:
                labels[i]=(labels[i]-(14-gap)/2)%360
                labels[j]=(labels[j]+(14-gap)/2)%360
    for p,label in zip(ordered,labels):
        lon=p['longitude']
        pieces.append(line(point(lon,247),point(label,230),'#77489b'))
        x,y=point(lon,247)
        pieces.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="#e62494"/>')
        pieces.append(text(label,218,p['glyph']+(' R' if p['retrograde'] else ''),20,y_offset=-6))
        pieces.append(text(label,218,p['degree_formatted'],11,y_offset=13))
    pieces.append(text(asc,355,'ASC',12,'#cf168c'))
    pieces.append(text(chart['midheaven_longitude'],355,'MC',12,'#cf168c'))
    pieces.append('<circle cx="380" cy="380" r="5" fill="#c699da"/></svg>')
    return ''.join(pieces)
