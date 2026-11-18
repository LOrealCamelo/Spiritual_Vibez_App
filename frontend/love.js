/* Love Match additions, shared by desktop and mobile. Answers stay in memory unless journalled. */
'use strict';
const LovePage=(()=>{
 const questions=[
 ['communication','I prefer to discuss concerns as soon as they come up.'],
 ['space','I need regular quiet time on my own.'],
 ['affection','Frequent affection is important to me.'],
 ['planning','I enjoy planning our time together in advance.'],
 ['adventure','I like trying new experiences together.'],
 ['money','I prefer saving for the future over spontaneous spending.'],
 ['social','I enjoy spending much of my free time with friends and groups.'],
 ['support','When stressed, I want listening before advice.'],
 ['growth','Shared learning and personal growth are priorities for me.'],
 ['ritual','Shared spiritual or reflective practices matter to me.']
 ];
 const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let answers={},result='',locations=null,searchVersion=0;
 function markup(){return '<section class="love-couple"><h2>Discover your connection</h2><p>Each partner answers independently, then compare your preferences. This is a conversation tool, not a prediction or clinical assessment. Different answers can be valuable, too.</p><form id="love-couple-form"><div class="love-partners">'+['a','b'].map((p,i)=>'<fieldset><legend>Partner '+(i+1)+'</legend>'+questions.map(([id,q])=>'<label>'+esc(q)+'<select name="'+p+'-'+id+'" required><option value="">Choose an answer</option>'+[1,2,3,4,5].map(n=>'<option value="'+n+'" '+(answers[p+'-'+id]===String(n)?'selected':'')+'>'+n+' — '+['Strongly disagree','Disagree','Neutral','Agree','Strongly agree'][n-1]+'</option>').join('')+'</select></label>').join('')+'</fieldset>').join('')+'</div><button class="btn">Compare our answers</button></form><div id="love-couple-result" aria-live="polite">'+result+'</div></section>'+finder();}
 function finder(){return '<section class="love-finder"><h2>Find something to enjoy together</h2><p>Choose a location for mapped places, available event listings and more ideas. No location permission is needed.</p><form id="love-activity-form"><div class="controls"><label>Country<select id="love-country" required><option value="">Choose a country</option></select></label><label>State / region<select id="love-region"><option value="">Choose a country first</option></select></label><label>Find city<input id="love-city-query" type="search" maxlength="100" placeholder="Type to narrow the city list"></label><label>City<select id="love-city" required><option value="">Choose a region first</option></select></label></div><label>Activity<select id="love-category" required><option value="">Loading activities…</option></select></label><button class="btn">Find local ideas</button></form><div id="love-activities" aria-live="polite"></div></section>';}
 async function api(path){const response=await fetch((typeof API!=='undefined'?API:'/api')+path,{headers:typeof Membership!=='undefined'?Membership.headers():{}});if(!response.ok){if(typeof Membership!=='undefined'&&[401,403].includes(response.status))Membership.accessDenied(response.status);throw Error('This service is unavailable. Please try again.')}return response.json()}
 function options(id,items,placeholder){const target=document.getElementById(id);if(!target)return;target.innerHTML='<option value="">'+esc(placeholder)+'</option>'+items.map(item=>'<option value="'+esc(item.code??item.place_id??item.id)+'">'+esc(item.name??item.label)+'</option>').join('');}
 async function load(){const marker=++searchVersion;try{const [data,categories]=await Promise.all([locations?Promise.resolve(locations):api('/astrology/locations/countries'),api('/love/categories')]);if(marker!==searchVersion||!document.getElementById('love-country'))return;locations=data;options('love-country',data.countries,'Choose a country');options('love-category',categories,'Choose an activity');}catch(error){const output=document.getElementById('love-activities');if(output)output.textContent=error.message}}
 document.addEventListener('change',async event=>{
  const id=event.target.id;if(!['love-country','love-region'].includes(id))return;
  const marker=++searchVersion,country=document.getElementById('love-country').value,region=document.getElementById('love-region').value;
  options('love-city',[],'Loading cities…');if(id==='love-country')options('love-region',[],'Loading regions…');
  try{
   if(!country){options('love-region',[],'Choose a country first');options('love-city',[],'Choose a country first');return}
   if(id==='love-country'){const data=await api('/astrology/locations/regions?country='+encodeURIComponent(country));if(marker!==searchVersion)return;options('love-region',data.regions,'All regions');}
   const data=await api('/astrology/locations/cities?country='+encodeURIComponent(country)+'&state='+encodeURIComponent(id==='love-country'?'':region));if(marker!==searchVersion)return;options('love-city',data.places,'Choose a city');
  }catch(error){const output=document.getElementById('love-activities');if(output)output.textContent=error.message}
 });
 let cityTimer;
 document.addEventListener('input',event=>{if(event.target.id!=='love-city-query')return;clearTimeout(cityTimer);cityTimer=setTimeout(async()=>{const marker=++searchVersion,country=document.getElementById('love-country')?.value,region=document.getElementById('love-region')?.value,query=event.target.value;if(!country)return;try{const data=await api('/astrology/locations/cities?'+new URLSearchParams({country,state:region||'',query}));if(marker===searchVersion)options('love-city',data.places,data.limited?'Choose a city (type more to narrow)':'Choose a city')}catch(error){const output=document.getElementById('love-activities');if(output)output.textContent=error.message}},350)});
 document.addEventListener('submit',async event=>{
  if(event.target.id==='love-couple-form'){
   event.preventDefault();answers=Object.fromEntries(new FormData(event.target));let distance=0;const shared=[],discuss=[];
   for(const [id,q] of questions){const delta=Math.abs(Number(answers['a-'+id])-Number(answers['b-'+id]));distance+=delta;(delta<=1?shared:discuss).push(q)}
   result='<h3>Your answer alignment: '+Math.round((1-distance/(questions.length*4))*100)+'%</h3><p>This percentage measures similarity across these answers only. It does not measure love, safety, or long-term compatibility.</p><h4>Shared preferences</h4><ul>'+shared.map(q=>'<li>'+esc(q)+'</li>').join('')+'</ul><h4>Explore your differences</h4><ul>'+discuss.map(q=>'<li>'+esc(q)+' Ask each other: what would a balanced approach look like for us?</li>').join('')+'</ul><p>Take turns sharing what matters most. Respect each other’s boundaries and revisit your answers as your needs change.</p><button type="button" class="btn" id="love-save-couple">Add to Journal</button>';
   document.getElementById('love-couple-result').innerHTML=result;
  }
  if(event.target.id==='love-activity-form'){
   event.preventDefault();const output=document.getElementById('love-activities'),button=event.target.querySelector('button');button.disabled=true;output.textContent='Looking for ideas…';
   try{const data=await api('/love/activities?place_id='+encodeURIComponent(document.getElementById('love-city').value)+'&category='+encodeURIComponent(document.getElementById('love-category').value));if(!output.isConnected)return;
    output.innerHTML='<h3>'+esc(data.category)+' near '+esc(data.place)+'</h3>'+data.notices.map(n=>'<p>'+esc(n)+'</p>').join('')+'<h4>Scheduled events</h4>'+(data.events.length?'<ul>'+data.events.map(x=>'<li><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer">'+esc(x.name)+'</a> · '+esc(x.date)+' '+esc(x.time)+' · '+esc(x.venue)+' · '+esc(x.status)+'</li>').join('')+'</ul>':'<p>No scheduled listings were returned.</p>')+'<h4>Mapped places</h4>'+(data.places.length?'<ul>'+data.places.map(x=>'<li><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer">'+esc(x.name)+'</a>'+(x.hours?' · Listed hours: '+esc(x.hours):'')+'</li>').join('')+'</ul>':'<p>No mapped places were returned for this category.</p>')+'<h4>Broaden your search</h4>'+data.search_links.map(x=>'<p><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer">'+esc(x.label)+'</a></p>').join('')+'<p>Checked '+esc(new Date(data.checked_at).toLocaleString())+'. Confirm costs, accessibility, bookings and opening times with the organizer.</p>';
   }catch(error){output.textContent=error.message}finally{button.disabled=false}
  }
 });
 document.addEventListener('click',event=>{if(event.target.id==='love-save-couple'&&result){const div=document.createElement('div');div.innerHTML=result;div.querySelector('button')?.remove();save('Our connection reflections',div.textContent);event.target.textContent='Added to Journal';event.target.disabled=true}});
 return {markup,load,clear(){answers={};result='';searchVersion++}};
})();
