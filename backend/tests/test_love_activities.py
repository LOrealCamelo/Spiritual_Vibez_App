"""Real provider response shapes; no invented live listings or leaked provider keys."""
import httpx
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.routers import love


class Provider:
    def __init__(self,*args,**kwargs):pass
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass
    async def post(self,url,**kwargs):
        assert url=='https://overpass-api.de/api/interpreter'
        assert '["amenity"~"^(restaurant|cafe|pub|bar|food_court)$"]' in kwargs['data']['data']
        return httpx.Response(200,request=httpx.Request('POST',url),json={'elements':[
          {'type':'node','id':123,'tags':{'name':'Provider café','opening_hours':'Mo-Fr 10:00-18:00'}},
          {'type':'unknown','id':1,'tags':{'name':'Skip invalid object'}}]})
    async def get(self,url,params):
        assert params['apikey']=='test-private-key'
        assert params['startDateTime'].endswith('Z') and params['radius']=='50'
        return httpx.Response(200,request=httpx.Request('GET',url),json={'_embedded':{'events':[
          {'name':'Provider event','url':'https://www.ticketmaster.com/event/123','dates':{'start':{'localDate':'2026-12-01'},'status':{'code':'onsale'}},'_embedded':{'venues':[{'name':'Test venue'}]}},
          {'name':'Unsafe URL','url':'javascript:alert(1)'}]}})


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('MEMBERSHIP_REQUIRED','false')
    monkeypatch.delenv('TICKETMASTER_API_KEY',raising=False)
    monkeypatch.setattr(love.httpx,'AsyncClient',Provider)
    love._cache.clear()
    with TestClient(app) as client:yield client
    love._cache.clear()


def test_places_are_distinct_from_scheduled_events_and_search_links(client):
    response=client.get('/api/love/activities?place_id=5128581&category=food')
    assert response.status_code==200
    data=response.json()
    assert data['places'][0]['name']=='Provider café'
    assert data['places'][0]['url']=='https://www.openstreetmap.org/node/123'
    assert data['events']==[]
    assert any('not connected' in n for n in data['notices'])
    assert data['search_links'] and data['checked_at']


def test_provider_events_are_filtered_and_key_stays_private(client,monkeypatch):
    monkeypatch.setenv('TICKETMASTER_API_KEY','test-private-key')
    response=client.get('/api/love/activities?place_id=5128581&category=food')
    assert response.status_code==200
    assert [e['name'] for e in response.json()['events']]==['Provider event']
    assert 'test-private-key' not in response.text


def test_category_and_location_are_validated(client):
    assert len(client.get('/api/love/categories').json())==14
    assert client.get('/api/love/activities?place_id=5128581&category=evil').status_code==422
    assert client.get('/api/love/activities?place_id=invalid').status_code==422


def test_upstream_failure_returns_honest_unavailable_state(client,monkeypatch):
    async def failed(*args,**kwargs):raise httpx.ConnectError('provider unavailable')
    monkeypatch.setattr(Provider,'post',failed)
    data=client.get('/api/love/activities?place_id=5128581').json()
    assert data['places']==[] and data['events']==[]
    assert any('temporarily unavailable' in n for n in data['notices'])
