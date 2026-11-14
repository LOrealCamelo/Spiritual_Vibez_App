import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../cloudflare-api.js';
const countries=[{code:'US',name:'United States'}];
const regions={US:[{code:'NY',name:'New York'}]};
const cities=[{place_id:'csc:1',city:'Utica',state:'New York',state_code:'NY',country:'United States',country_code:'US',latitude:43.1,longitude:-75.2,timezone:'America/New_York',label:'Utica, New York, United States'}];
const env={ASSETS:{fetch:async req=>{
  const path=new URL(req.url).pathname;
  const v=path==='/geo/countries.json'?countries:path==='/geo/regions.json'?regions:path==='/geo/cities/US.json'?cities:null;
  return v===null?new Response('Not Found',{status:404}):Response.json(v);
}}};
const call=path=>worker.fetch(new Request('https://app.test'+path),env);
test('countries load',async()=>{
  assert.deepEqual((await (await call('/api/astrology/locations/countries')).json()).countries,countries);
});
test('states load',async()=>{
  assert.deepEqual((await (await call('/api/astrology/locations/regions?country=US')).json()).regions,regions.US);
});
test('cities search and timezone',async()=>{
  const r=await call('/api/astrology/locations/cities?country=US&state=NY&query=uti');
  assert.equal(r.status,200);
  const data=await r.json();
  assert.equal(data.total,1);
  assert.equal(data.places[0].timezone,'America/New_York');
});
test('unknown country validated',async()=>{
  assert.equal((await call('/api/astrology/locations/regions?country=XX')).status,422);
});
test('no fake natal chart results',async()=>{
  const r=await worker.fetch(new Request('https://app.test/api/astrology/natal-chart',{method:'POST'}),env);
  assert.equal(r.status,501);
  assert.equal((await r.json()).code,'CLOUDFLARE_API_NOT_MIGRATED');
});
