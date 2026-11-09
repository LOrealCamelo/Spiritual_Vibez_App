import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.natal_report import aspect_between

client=TestClient(app)
BIRTH={'birth_date':'1996-11-05','birth_time':'14:30','place_id':'5142056'}


def test_house_rulers_locations_occupants_and_four_angles():
    modern=client.post('/api/astrology/natal-chart',json=BIRTH).json()
    traditional=client.post('/api/astrology/natal-chart',json={**BIRTH,'rulership':'traditional'}).json()
    assert modern['houses'][0]['ruling_planet']=='Neptune'
    assert modern['houses'][0]['ruler_placement']['house']==11
    assert modern['houses'][0]['ruler_placement']['sign']=='Capricorn'
    assert traditional['houses'][0]['ruling_planet']=='Jupiter'
    assert traditional['houses'][0]['ruler_placement']['house']==10
    assert [p['longitude'] for p in modern['placements']]==[p['longitude'] for p in traditional['placements']]
    occupants=[p for h in modern['houses'] for p in h['occupants']]
    assert sorted(occupants)==sorted(p['planet'] for p in modern['placements'])
    assert all(len(h['ruler_paragraphs'])==3 for h in modern['houses'])
    assert {a['code'] for a in modern['angles']}=={'ASC','MC','DC','IC'}
    assert modern['angles'][0]['ruling_planet']=='Neptune'
    assert all('orb_formatted' in a and a['motion'] in ('Applying','Separating','Exact','Stationary') for a in modern['aspects'])
    assert client.post('/api/astrology/natal-chart',json={**BIRTH,'rulership':'unknown'}).status_code==422


@pytest.mark.parametrize('a,b,expected',[
    ({'planet':'ASC','longitude':2.533333,'speed_deg_per_day':360},{'planet':'Moon','longitude':127.566667,'speed_deg_per_day':13},'Applying'),
    ({'planet':'MC','longitude':271.5,'speed_deg_per_day':360},{'planet':'Mercury','longitude':158.45,'speed_deg_per_day':-1},'Applying'),
    ({'planet':'Sun','longitude':10,'speed_deg_per_day':1},{'planet':'Moon','longitude':132,'speed_deg_per_day':13},'Separating'),
    ({'planet':'Sun','longitude':359,'speed_deg_per_day':1},{'planet':'Moon','longitude':1,'speed_deg_per_day':13},'Separating'),
])
def test_aspect_direction_uses_motion_and_handles_longitude_wrap(a,b,expected):
    aspect=aspect_between(a,b,angle_orb=8)
    assert aspect and aspect['motion']==expected
    assert '°' in aspect['orb_formatted']


def test_symbolic_display_positions_follow_rounding_carry():
    from backend.services.sky_engine import sign_position
    before=sign_position(29.9999)
    assert before['sign']=='Aries' and before['display_sign']=='Taurus'
    assert before['display_sign_glyph']=='♉' and before['degree_formatted']=='0°00′'
    chart=client.post('/api/astrology/natal-chart',json=BIRTH).json()
    assert all(p['glyph'] and p['sign_glyph'] and p['degree_formatted'] for p in chart['placements'])
