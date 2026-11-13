/* Interactive angular-line map; all positions come from the person's birth data. */
const astroUI={planet:'All',angle:'All',zoom:1,highlight:[],cities:[],searchRequest:0};
function astroGuide(){const g=AstroMapTools.guide;return '<section class="astro-guide"><h2>'+e(g.title)+'</h2><ol>'+g.passes.map(p=>'<li><h3>'+e(p.title)+'</h3><p>'+e(p.text)+'</p></li>').join('')+'</ol><h2>'+e(g.comparisonTitle)+'</h2><p>'+e(g.comparisonIntro)+'</p><table><thead><tr><th>View</th><th>What it shows</th><th>Best for</th></tr></thead><tbody>'+g.comparison.map(c=>'<tr><th>'+e(c.name)+'</th><td>'+e(c.shows)+'</td><td>'+e(c.use)+'</td></tr>').join('')+'</tbody></table><h2>'+e(g.livingTitle)+'</h2>'+g.living.map(p=>'<h3>'+e(p.title)+'</h3><p>'+e(p.text)+'</p>').join('')+'<h2>'+e(g.stepsTitle)+'</h2><ol>'+g.steps.map(s=>'<li>'+e(s)+'</li>').join('')+'</ol><h2>'+e(g.methodTitle)+'</h2><p>'+e(g.method)+'</p>'+btn('Explore your birth chart','tool:natal','cream')+'</section>';}
function inspectAstroLocation(info){
 state.result.inspected_location=info;
 const panel=document.getElementById('astro-inspection');if(!panel)return;
 const title=info.crossing?'Crossing: '+info.crossing.title:info.label||'Selected map location';
 panel.innerHTML='<h3>'+e(title)+'</h3><p>'+info.latitude+'°, '+info.longitude+'°</p>'+(info.crossing?'<p>'+e(info.crossing.interpretation)+'</p>':'')+'<h4>Every line within 500 km</h4>'+(info.nearby_lines.length?'<ul>'+info.nearby_lines.map(p=>'<li><b>'+e(p.planet+' '+p.angle)+'</b> · '+p.distance_miles+' miles ('+p.distance_km+' km)<br>'+e(p.interpretation)+'</li>').join('')+'</ul>':'<p>No angular planetary lines within 500 km of this point.</p>')+contentActionMarkup({title,text:ContentFormat.readable(info),route:'explore/astro',imageSvg:state.result.map_svg});
 const svg=document.querySelector('.astro-map svg');let pin=svg.querySelector('.astro-pin');if(!pin){pin=document.createElementNS('http://www.w3.org/2000/svg','circle');pin.setAttribute('class','astro-pin');pin.setAttribute('r','8');pin.setAttribute('fill','none');pin.setAttribute('stroke','#fff');pin.setAttribute('stroke-width','3');svg.append(pin)}pin.setAttribute('cx',(info.longitude+180)*1200/360);pin.setAttribute('cy',(90-info.latitude)*600/180);
}
function astroReport(o){
 astroUI.planet='All';astroUI.angle='All';astroUI.zoom=1;astroUI.highlight=[];
 return '<article class="result birth-report astro-report"><h2>'+e(o.name?o.name+'’s Astrocartography Map':o.title)+'</h2><p>'+e(o.location.label)+' · '+e(birthLocalLabel(o))+'</p><p>Focus: '+e(o.focus)+'. White dot: birthplace. Numbered dots match the places below.</p><div class="astro-map-controls"><div class="controls" role="group" aria-label="Planetary map layers">'+['All',...o.planets.map(p=>p.planet)].map(p=>btn(p,'astro-layer','cream','data-planet="'+p+'" aria-pressed="'+(p==='All')+'"')).join('')+'</div><div class="controls" role="group" aria-label="Angle layers">'+['All','ASC','DSC','MC','IC'].map(a=>btn(a==='All'?'All angles':a,'astro-angle','cream','data-angle="'+a+'" aria-pressed="'+(a==='All')+'"')).join('')+'</div>'+btn('Zoom in','astro-zoom','cream','data-step="1"')+' '+btn('Zoom out','astro-zoom','cream','data-step="-1"')+'</div><div class="astro-map" tabindex="0" aria-label="Scrollable world map"><div class="astro-map-canvas">'+o.map_svg+'</div></div><p id="astro-active-line" aria-live="polite">Select a planet or tap a map line to explore its meaning.</p><div class="astro-city-search"><label class="field">Find a city to explore<input id="astro-city-query" type="search" placeholder="City name, then choose the matching region and country"></label>'+btn('Find places','astro-search','cream')+'<div id="astro-city-results" aria-live="polite"></div></div><section id="astro-inspection" class="glass" aria-live="polite"><h3>Explore a location or crossing</h3><p>Select a city below, tap a marked crossing, or choose any point on the map.</p></section><div class="reference-grid">'+Object.entries(o.angle_meanings).map(([a,t])=>'<section><h3>'+e(a)+'</h3><p>'+e(t)+'</p></section>').join('')+'</div><h2>Places to explore for '+e(o.focus)+'</h2><ol class="astro-places">'+o.places.map((p,i)=>'<li><h3>'+btn(e(p.city+', '+p.country),'astro-place','cream','data-place-index="'+i+'"')+'</h3><p>'+e(p.planet+' '+p.angle)+' · approximately '+p.distance_miles+' miles ('+p.distance_km+' km) from this line.</p><p>'+e(p.interpretation)+'</p></li>').join('')+'</ol><p>'+e(o.proximity_note)+'</p><p>'+e(o.note)+'</p><details><summary>Calculation method and map sources</summary><p>'+e(o.method)+'</p><p>'+e(o.map_credit)+'</p><a class="link" href="'+e(o.map_source)+'" target="_blank" rel="noopener noreferrer">Natural Earth map source</a></details>'+astroGuide()+'</article>';
}
function updateAstroMap(){const o=state.result;if(o?.report_type!=='astrocartography')return;
 document.querySelectorAll('.astro-map g[data-planet]').forEach(g=>{g.style.opacity=(astroUI.highlight.length?astroUI.highlight.includes(g.dataset.planet):astroUI.planet==='All'||g.dataset.planet===astroUI.planet)?'1':'.12'});
 document.querySelectorAll('.astro-line').forEach(p=>{p.style.opacity=astroUI.angle==='All'||p.dataset.angle===astroUI.angle?'.9':'.08';p.style.strokeWidth=astroUI.planet===p.dataset.planet?'3':'1.6'});
 document.querySelectorAll('[data-action="astro-layer"]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.planet===astroUI.planet)));
 document.querySelectorAll('[data-action="astro-angle"]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.angle===astroUI.angle)));
 const planet=o.planets.find(p=>p.planet===astroUI.planet);const active=document.getElementById('astro-active-line');
 if(active)active.textContent=(planet?planet.planet+': '+planet.interpretation:'All planets')+(astroUI.angle!=='All'?' · '+o.angle_meanings[astroUI.angle]:' · All four angles');
 const canvas=document.querySelector('.astro-map-canvas');if(canvas)canvas.style.width=(astroUI.zoom*100)+'%';
}
document.addEventListener('click',async ev=>{
 if(state.tool!=='astro'||state.result?.report_type!=='astrocartography')return;
 const b=ev.target.closest('[data-action]'),a=b?.dataset.action,o=state.result;
 if(a==='astro-search'){
  const query=document.getElementById('astro-city-query').value.trim(),ticket=++astroUI.searchRequest,panel=document.getElementById('astro-city-results');
  if(query.length<2){panel.textContent='Enter at least two letters of a city name.';return}panel.textContent='Searching…';
  try{const data=await api('/astrology/astrocartography/places?'+new URLSearchParams({query}));if(state.result!==o||ticket!==astroUI.searchRequest)return;astroUI.cities=data.places;panel.innerHTML=data.places.length?data.places.map((p,i)=>btn(e(p.label),'astro-city','cream','data-city-index="'+i+'"')).join(' '):'<p>No matching city. Try another spelling or select its position on the map.</p>'}
  catch(ex){if(state.result===o&&ticket===astroUI.searchRequest)panel.textContent=ex.message}return;
 }
 if(a==='astro-city'){const p=astroUI.cities[Number(b.dataset.cityIndex)];inspectAstroLocation({...AstroMapTools.inspect(o,p.latitude,p.longitude),label:p.label});return}
 if(a==='astro-layer'){astroUI.planet=b.dataset.planet;astroUI.highlight=[]}
 else if(a==='astro-angle'){astroUI.angle=b.dataset.angle;astroUI.highlight=[]}
 else if(a==='astro-line'){astroUI.planet=b.dataset.planet;astroUI.angle=b.dataset.angle;astroUI.highlight=[]}
 else if(a==='astro-zoom')astroUI.zoom=Math.max(1,Math.min(4,astroUI.zoom+Number(b.dataset.step)*.5));
 else if(a==='astro-place'){const p=o.places[Number(b.dataset.placeIndex)];inspectAstroLocation({...AstroMapTools.inspect(o,p.latitude,p.longitude),label:p.city+', '+p.country})}
 else if(a==='astro-crossing'){const p=o.crossings[Number(b.dataset.crossingIndex)];astroUI.planet='All';astroUI.angle='All';astroUI.highlight=[p.planet_a,p.planet_b];inspectAstroLocation({...AstroMapTools.inspect(o,p.latitude,p.longitude),crossing:p})}
 const svg=ev.target.closest('.astro-map svg');
 if(svg&&a!=='astro-crossing'){const r=svg.getBoundingClientRect();const info=AstroMapTools.select(o,(ev.clientX-r.x)/r.width,(ev.clientY-r.y)/r.height,.009/astroUI.zoom);if(info.crossing)astroUI.highlight=[info.crossing.planet_a,info.crossing.planet_b];inspectAstroLocation(info)}
 if(a?.startsWith('astro-')||svg){ev.preventDefault();updateAstroMap()}
});
document.addEventListener('keydown',ev=>{
 if((ev.key!=='Enter'&&ev.key!==' ')||!ev.target.matches?.('.astro-line,.astro-crossing'))return;
 ev.preventDefault();let point={};
 if(ev.target.matches('.astro-line')){const p=state.result.planets.find(p=>p.planet===ev.target.dataset.planet);const pts=p.lines[ev.target.dataset.angle],coord=pts[Math.floor(pts.length/2)],r=ev.target.closest('svg').getBoundingClientRect();point={clientX:r.x+(coord[1]+180)*r.width/360,clientY:r.y+(90-coord[0])*r.height/180}}
 ev.target.dispatchEvent(new MouseEvent('click',{bubbles:true,...point}));
});
