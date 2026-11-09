"""The uploaded deck must resolve consistently in API, browser and native bundles."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app

ROOT=Path(__file__).parents[2]
client=TestClient(app)


def test_all_78_cards_have_real_pngs_and_native_static_requires():
    cards=client.get('/api/tarot/cards').json()['cards']
    requires=(ROOT/'mobile/src/data/tarotImages.ts').read_text()
    assert len(cards)==78 and len({c['image_url'] for c in cards})==78
    for card in cards:
        path=ROOT/'mobile/assets/tarot'/card['image_url'].split('/')[-1]
        assert path.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
        assert f"{card['id']}: require('../../assets/tarot/{path.name}')" in requires
    response=client.get(cards[0]['image_url'])
    assert response.status_code==200 and response.headers['content-type']=='image/png'
    assert response.content.startswith(b'\x89PNG\r\n\x1a\n')


def test_quiz_and_every_dealt_position_include_the_same_image():
    cards={c['id']:c['image_url'] for c in client.get('/api/tarot/cards').json()['cards']}
    quiz=client.get('/api/tarot/study/quiz?card_id=77').json()
    assert quiz['image_url']==cards[77]
    single=client.post('/api/tarot/spreads/deal-slot',json={'spread_id':'reset-energy','slot_num':1}).json()['card']
    assert single['image_url']==cards[single['id']]
    all_cards=client.post('/api/tarot/spreads/deal-all',json={'spread_id':'reset-energy'}).json()['positions']
    for card in all_cards:
        assert card['image_url']==cards[card['card_id']]
