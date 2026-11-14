/* Build offline country/region/city static assets for Cloudflare Workers.
 * MIT licensed dataset and CC0 timezone lookup; no external runtime geocoding.
 */
import {mkdirSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
import {Countries} from 'countries-states-cities-service/countries';
import {States} from 'countries-states-cities-service/states';
import {Cities} from 'countries-states-cities-service/cities';
import tzlookup from 'tz-lookup';
const base=resolve(dirname(fileURLToPath(import.meta.url)),'..','geo');
mkdirSync(resolve(base,'cities'),{recursive:true});
const save=(name,data)=>writeFileSync(resolve(base,name),JSON.stringify(data));
const countries=Countries.getCountries().map(c=>({code:c.iso2,name:c.name}))
  .filter(c=>/^[A-Z]{2}$/.test(c.code)).sort((a,b)=>a.name.localeCompare(b.name));
const names=Object.fromEntries(countries.map(c=>[c.code,c.name]));
const states=States.getStates();
const regions=Object.fromEntries(countries.map(c=>[c.code,[]]));
const stateNames=new Map();
for(const state of states){
  const code=state.country_code;
  if(!regions[code])continue;
  regions[code].push({code:state.state_code,name:state.name});
  stateNames.set(code+'|'+state.state_code,state.name);
}
for(const r of Object.values(regions))r.sort((a,b)=>a.name.localeCompare(b.name));
const cityBuckets=Object.fromEntries(countries.map(c=>[c.code,[]]));
for(const city of Cities.getCities()){
  const code=city.country_code, bucket=cityBuckets[code];
  if(!bucket)continue;
  const latitude=Number(city.latitude),longitude=Number(city.longitude);
  if(!Number.isFinite(latitude)||!Number.isFinite(longitude)||Math.abs(latitude)>90||Math.abs(longitude)>180)continue;
  let timezone='';
  try{timezone=tzlookup(latitude,longitude)}catch{}
  const state=stateNames.get(code+'|'+city.state_code)||city.state_code||'';
  bucket.push({place_id:'csc:'+city.id,city:city.name,state,state_code:city.state_code||'',
    country:names[code],country_code:code,latitude,longitude,timezone,
    label:[city.name,state,names[code]].filter(Boolean).join(', ')});
}
save('countries.json',countries);
save('regions.json',regions);
for(const [code,cities] of Object.entries(cityBuckets)){
  cities.sort((a,b)=>a.city.localeCompare(b.city)||a.state.localeCompare(b.state));
  save('cities/'+code+'.json',cities);
}
console.log('Built',countries.length,'countries,',states.length,'regions,',
  Object.values(cityBuckets).reduce((n,x)=>n+x.length,0),'cities.');