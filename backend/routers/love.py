"""Date ideas from provider data; no invented venues or events."""
import asyncio
import os
import time
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse
import httpx
from fastapi import APIRouter, HTTPException, Query
from ..services.birth_locations import city_records, place_record

router = APIRouter(prefix='/api/love', tags=['Love and shared activities'])
CATEGORIES = {
 'food': ('Restaurants, cafés, tea houses and ale houses', 'amenity', 'restaurant|cafe|pub|bar|food_court', 'food festival'),
 'creative': ('Paint & sip, pottery, woodworking and glassblowing', 'craft', 'pottery|carpenter|glassblower', 'art workshop'),
 'adventure': ('Escape rooms, axe throwing and amusement parks', 'leisure', 'escape_game|amusement_arcade', 'family'),
 'culture': ('Museums, castles, reading clubs and movies', 'tourism', 'museum|gallery|attraction|castle', 'film'),
 'nature': ('Trails, state parks, waterfalls and nature', 'leisure', 'park|nature_reserve', 'outdoor'),
 'water': ('Boat rides and snorkeling', 'leisure', 'marina|water_park', 'boat'),
 'sport': ('Skating, boxing, baseball, basketball, hockey and football', 'leisure', 'sports_centre|stadium|ice_rink', 'sports'),
 'shows': ('Comedy, festivals, carnivals and outdoor movies', 'amenity', 'theatre|cinema|arts_centre', 'comedy'),
 'markets': ('Farmers markets, food trucks and food festivals', 'amenity', 'marketplace', 'food festival'),
 'seasonal': ('Orchards, pumpkin patches and strawberry picking', 'shop', 'farm', 'harvest'),
 'wine': ('Wineries and vineyards', 'craft', 'winery', 'wine'),
 'getaway': ('Skiing, lodges, cabins and vacation rentals', 'tourism', 'chalet|alpine_hut|guest_house|camp_site', 'ski'),
 'community': ('Volunteering and animal sanctuaries', 'amenity', 'animal_shelter|community_centre', 'volunteer'),
 'classes': ('Cooking classes and shared learning', 'amenity', 'cooking_school|arts_centre', 'class'),
}
EXTRA_TAGS = {
 'nature': [('natural','waterfall'), ('boundary','national_park'), ('route','hiking')],
 'adventure': [('tourism','theme_park'), ('sport','axe_throwing')],
 'water': [('sport','scuba_diving|sailing|canoe')],
 'sport': [('sport','roller_skating|boxing|baseball|basketball|ice_hockey|soccer|american_football')],
 'culture': [('historic','castle'), ('club','book')],
 'wine': [('landuse','vineyard')],
 'seasonal': [('landuse','orchard'), ('shop','pick_your_own')],
 'getaway': [('sport','skiing')],
}
_cache = {}
_lock = asyncio.Lock()


def safe_url(value, suffix=None):
    try:
        parsed = urlparse(value)
        if parsed.scheme == 'https' and parsed.hostname and (not suffix or parsed.hostname == suffix or parsed.hostname.endswith('.'+suffix)):
            return value
    except ValueError:
        pass
    return ''


@router.get('/categories')
def categories():
    return [{'id': key, 'label': value[0]} for key, value in CATEGORIES.items()]


@router.get('/activities')
async def activities(place_id: str = Query(max_length=30), category: str = 'food'):
    city = city_records().get(place_id)
    if city is None:
        # GeoNames cache versions may use integer keys.
        city = next((c for c in city_records().values() if str(c['geonameid']) == place_id), None)
    if city is None or category not in CATEGORIES:
        raise HTTPException(422, 'Choose a listed city and activity category.')
    key = (place_id, category)
    if key in _cache and _cache[key][0] > time.time()-900:
        return _cache[key][1]
    place = place_record(city)
    label, tag, values, keyword = CATEGORIES[category]
    result = {'place':place['label'], 'category':label, 'events':[], 'places':[], 'notices':[],
        'checked_at':datetime.now(timezone.utc).isoformat(),
        'search_links':[
          {'label':'Search more local ideas', 'url':'https://www.google.com/search?'+urlencode({'q':label+' near '+place['label']})},
          {'label':'Search local events and classes', 'url':'https://www.eventbrite.com/d/online/all-events/?'+urlencode({'q':keyword+' '+place['label']})},
        ]}
    # Serialize and cache public Overpass calls to respect shared infrastructure.
    async with _lock:
        if key in _cache and _cache[key][0] > time.time()-900:
            return _cache[key][1]
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            selectors=[(tag,values), *EXTRA_TAGS.get(category,[])]
            clauses=''.join(f'nwr(around:15000,{city["latitude"]},{city["longitude"]})["{k}"~"^({v})$"]["name"];' for k,v in selectors)
            query=f'[out:json][timeout:10];({clauses});out center 20;'
            try:
                response=await client.post('https://overpass-api.de/api/interpreter',data={'data':query},headers={'User-Agent':'SpiritualVibz/1.0 (local activity discovery)'})
                response.raise_for_status()
                for item in response.json().get('elements',[])[:20]:
                    tags=item.get('tags',{});oid=item.get('id');kind=item.get('type')
                    if kind not in ('node','way','relation') or not isinstance(oid,int):continue
                    result['places'].append({'name':str(tags.get('name',''))[:300],
                       'url':f'https://www.openstreetmap.org/{kind}/{oid}',
                       'hours':str(tags.get('opening_hours',''))[:200]})
                result['notices'].append('Places: © OpenStreetMap contributors (ODbL). These are mapped venues, not confirmed events or live opening times. Confirm details before visiting.')
            except (httpx.HTTPError,ValueError,TypeError,AttributeError):
                result['notices'].append('Mapped places are temporarily unavailable. The search links below remain available.')
            token=os.getenv('TICKETMASTER_API_KEY')
            if token:
                try:
                    response=await client.get('https://app.ticketmaster.com/discovery/v2/events.json',params={
                        'apikey':token,'latlong':f'{city["latitude"]},{city["longitude"]}',
                        'radius':'50','unit':'km','countryCode':city['countrycode'], 'keyword':keyword,
                        'startDateTime':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'sort':'date,asc','size':'20'})
                    response.raise_for_status()
                    for item in response.json().get('_embedded',{}).get('events',[]):
                        url=safe_url(item.get('url',''),'ticketmaster.com')
                        if not url:continue
                        start=item.get('dates',{}).get('start',{})
                        result['events'].append({'name':str(item.get('name',''))[:300], 'url':url,
                            'date':start.get('localDate',''), 'time':start.get('localTime',''),
                            'status':item.get('dates',{}).get('status',{}).get('code',''),
                            'venue':item.get('_embedded',{}).get('venues',[{}])[0].get('name','')})
                    result['notices'].append('Scheduled events supplied by Ticketmaster; coverage is limited to participating providers. Check the listing for availability and changes.')
                except (httpx.HTTPError,ValueError,TypeError,AttributeError,IndexError):
                    result['notices'].append('Scheduled event listings are temporarily unavailable.')
            else:
                result['notices'].append('Scheduled live events are not connected yet. Search links are external searches, not verified listings.')
    if len(_cache)>=200:_cache.pop(next(iter(_cache)))
    _cache[key]=(time.time(),result)
    return result
