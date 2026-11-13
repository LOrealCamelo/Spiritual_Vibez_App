/* Shared map inspection math and reading guide for web and native. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.AstroMapTools=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 const rad=v=>v*Math.PI/180,clamp=v=>Math.max(-1,Math.min(1,v)),signed=v=>(v+180)%360<0?(v+180)%360+180:(v+180)%360-180;
 const angles={ASC:'Identity and self-expression',DSC:'Relationships and partnerships',MC:'Career and public life',IC:'Home and roots'};
 function distance(lat,lon,p,angle){
  const phi=rad(lat),dec=rad(p.declination),h=rad(signed(lon-p.mc_longitude)),R=6371.0088;
  if(angle==='MC'||angle==='IC'){const delta=rad(signed(lon-p.mc_longitude-(angle==='IC'?180:0)));return R*(Math.cos(delta)<0?Math.PI/2-Math.abs(phi):Math.asin(Math.min(1,Math.abs(Math.cos(phi)*Math.sin(delta)))))}
  const dot=Math.sin(phi)*Math.sin(dec)+Math.cos(phi)*Math.cos(dec)*Math.cos(h),x=Math.cos(phi)*Math.cos(h)-dot*Math.cos(dec),y=Math.cos(phi)*Math.sin(h),z=Math.sin(phi)-dot*Math.sin(dec);
  if(Math.hypot(x,y,z)<1e-12)return R*Math.PI/2;
  if((angle==='ASC'&&y<=0)||(angle==='DSC'&&y>=0))return R*Math.abs(Math.asin(clamp(dot)));
  return R*Math.acos(Math.min(1,Math.abs(-Math.cos(phi)*Math.cos(h)*Math.sin(dec)+Math.sin(phi)*Math.cos(dec))));
 }
 function inspect(report,lat,lon){
  const lines=[];
  for(const p of report.planets)for(const angle of Object.keys(angles)){const km=distance(lat,lon,p,angle);if(km<=500)lines.push({planet:p.planet,angle,distance_km:Math.round(km),distance_miles:Math.round(km/1.609344),interpretation:p.interpretation+'. '+angles[angle]+'.'})}
  lines.sort((a,b)=>a.distance_km-b.distance_km);
  return {latitude:Number(lat.toFixed(3)),longitude:Number(lon.toFixed(3)),nearby_lines:lines};
 }
 function select(report,x,y,tolerance=.009){
  const lat=90-y*180,lon=x*360-180;
  const crossing=(report.crossings||[]).map(c=>({point:c,delta:Math.hypot((c.longitude-lon)/360,(c.latitude-lat)/180)})).sort((a,b)=>a.delta-b.delta)[0];
  if(crossing&&crossing.delta<tolerance)return {...inspect(report,crossing.point.latitude,crossing.point.longitude),crossing:crossing.point};
  return inspect(report,lat,lon);
 }
 const guide={
  title:'How to read your astrocartography map: three passes',
  passes:[
   {title:'Find the lines near places you care about',text:'Zoom into where you live, grew up, or are considering a move. Astrological traditions often consider lines within roughly 300 miles (500 km), with closer lines interpreted as more prominent. Select a suggested city or tap anywhere on the map to see every angular line within 500 km.'},
   {title:'Name the planet and the angle',text:'The planet describes the theme: Venus for relationships and pleasure, Saturn for discipline and structure, Jupiter for growth. The angle describes the area of life: MC for career, IC for home, ASC for identity, DSC for partnerships. Venus DSC and Venus MC describe different expressions of the same planetary theme.'},
   {title:'Check for crossings',text:'A crossing combines two planetary themes at one location. In astrology, Sun–Jupiter is often associated with optimism and opportunity; Mars–Saturn can suggest productive effort alongside tension. Select a marked crossing to read both planets and angles together. These interpretations are symbolic, not predictions.'}
  ],
  comparisonTitle:'Birth chart, astrocartography map and relocation chart',
  comparisonIntro:'These are views of the same birth moment. “Astrocartography chart” and “astrocartography map” name the same world-map view.',
  comparison:[
   {name:'Birth chart',shows:'Planets, signs and houses at your birthplace',use:'Personality and life themes'},
   {name:'Astrocartography chart / map',shows:'Where each planet was rising, setting, culminating or anti-culminating on Earth',use:'Comparing many places at once'},
   {name:'Relocation chart',shows:'Your natal planets recast with houses and angles for one chosen city',use:'A deeper look at one place; a different calculation from this map'}
  ],
  livingTitle:'Using your map to explore where to live',
  living:[
   {title:'Shortlist by goal',text:'For career, explore Sun, Jupiter or Saturn on the MC. For relationships, Venus or Moon on the DSC. For rest and reflection, Moon or Neptune on the IC. For reinvention, Uranus on the ASC. Choose your focus before generating the map to change the city shortlist.'},
   {title:'Read the whole neighbourhood',text:'Inspect every line near a candidate city, not just its nearest line. A Jupiter line and a Pluto line may both be relevant. Compare several cities using their complete nearby-line lists.'},
   {title:'Weigh demanding lines honestly',text:'Saturn, Pluto and Mars are not automatically “bad” places. Their traditional themes include sustained effort, transformation and drive, alongside pressure or intensity. Consider the chapter of life you want.'},
   {title:'Then use real life',text:'Your map is one lens alongside cost of living, visas, work, language and the people you love. Treat it as a reflection and shortlist tool, not a verdict.'}
  ],
  stepsTitle:'How to use this calculator',
  steps:['Enter your birth date, exact recorded time, city, state/province and country. Historical timezone and daylight-saving rules convert it to UTC.','Choose your focus and generate your map. All ten planets and four angles are included.','Use planet and angle controls to explore lines. Zoom, select cities, inspect locations and choose crossings for combined readings.'],
  methodTitle:'How your map is calculated',
  method:'Spiritual Vibz uses apparent geocentric positions from Astronomy Engine, together with Greenwich apparent sidereal time, to solve the locations of ASC, DSC, MC and IC at your birth moment. The map uses geometric horizons, without atmospheric refraction, terrain or parans. This is not a relocated house chart. Different software may use different ephemerides and horizon conventions.'
 };
 return {distance,inspect,select,guide};
});
