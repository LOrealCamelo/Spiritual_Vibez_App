/* Cloudflare Worker API. Phase 1: birth-location dropdowns (not natal calculations).
 * All geographic lookups are local Workers static assets: no Render cold starts.
 */
const headers={'content-type':'application/json; charset=utf-8','cache-control':'no-store'};
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers});
const normalize=v=>String(v||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('en').trim();
async function geo(request,env,path){
  const response=await env.ASSETS.fetch(new Request(new URL(path,request.url)));
  if(!response.ok)throw Error('Missing geographic file '+path+' (HTTP '+response.status+'). Run npm run build:geo.');
  return response.json();
}
async function locationRoute(request,env,path,params){
  if(path==='/api/astrology/locations/countries'){
    return json({countries:await geo(request,env,'/geo/countries.json')});
  }
  if(path==='/api/astrology/locations/timezones'){
    return json({timezones:Intl.supportedValuesOf('timeZone')});
  }
  if(!['/api/astrology/locations/regions','/api/astrology/locations/cities'].includes(path))return null;
  const country=String(params.get('country')||'').trim().toUpperCase();
  if(!/^[A-Z]{2}$/.test(country))return json({detail:'Choose a country first.'},422);
  const countries=await geo(request,env,'/geo/countries.json');
  if(!countries.some(c=>c.code===country))return json({detail:'Choose a country from the list.'},422);
  const regions=await geo(request,env,'/geo/regions.json');
  if(path.endsWith('/regions'))return json({regions:regions[country]||[]});
  const state=String(params.get('state')||'').trim();
  if(state&&!(regions[country]||[]).some(s=>s.code===state))return json({detail:'Choose a state or province from the list.'},422);
  const query=normalize(params.get('query'));
  const cityRecords=await geo(request,env,'/geo/cities/'+country+'.json');
  const matches=cityRecords.filter(c=>(!state||c.state_code===state)&&(!query||normalize(c.city).includes(query)));
  return json({places:matches.slice(0,300),total:matches.length,limited:matches.length>300,
    note:'Offline city directory; timezones estimated from coordinates. Confirm cities near timezone borders.'});
}
export default {
  async fetch(request,env){
    const url=new URL(request.url);
    if(!url.pathname.startsWith('/api/'))return env.ASSETS.fetch(request);
    if(url.pathname==='/api/health')return json({status:'partial',host:'Cloudflare Workers',locations:'available',natal_chart:'not_migrated'});
    if(!['GET','POST'].includes(request.method))return json({detail:'Method not allowed'},405);
    try{
      if(request.method==='GET'&&url.pathname.startsWith('/api/astrology/locations/')){
        const response=await locationRoute(request,env,url.pathname,url.searchParams);
        if(response)return response;
      }
      return json({detail:'This feature still depends on the Python backend and has not yet been migrated to Cloudflare.',
        code:'CLOUDFLARE_API_NOT_MIGRATED'},501);
    }catch(error){
      return json({detail:'Cloudflare geographic data is not ready. Ensure npm run build:geo completed.',error:error.message},503);
    }
  }
};