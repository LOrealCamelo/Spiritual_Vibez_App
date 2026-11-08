/* Birth charts and daily sky: shared API data, accessible browser controls. */
'use strict';
const zodiacLabels={tropical:'Tropical',sidereal:'Sidereal (Lahiri)'};
const houseLabels={placidus:'Placidus',whole_sign:'Whole Sign',equal:'Equal'};
const birthFormState={name:'',date:'',hour:'12',minute:'00',city:'',country:'US',region:'',place:null,places:[],zodiac:'tropical',houses:'placidus',fold:'',busy:false};
const skyUI={date:'',timezone:Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC',zodiac:'tropical',loading:false,error:'',request:0,lastFetch:0};
function birthInput(label,key,type='text',attrs=''){
 const id=key==='date'?'birth-date':'birth-'+key;
 return '<label class="field">'+e(label)+'<input id="'+id+'" data-birth-key="'+key+'" type="'+type+'" value="'+e(birthFormState[key])+'" '+attrs+'></label>';
}
function birthForm(){const b=birthFormState;
 return '<div class="glass birth-form"><h3>Your birth details</h3>'+birthInput('Name (optional)','name','text','autocomplete="name" maxlength="80"')+
 '<div class="controls">'+birthInput('Date of birth','date','date','min="1900-01-01" max="2100-12-31"')+birthInput('Hour (24-hour clock)','hour','number','min="0" max="23"')+birthInput('Minutes','minute','number','min="0" max="59"')+'</div>'+
 '<div class="controls">'+birthInput('Country name or code','country','text','placeholder="United States or US"')+birthInput('State / province','region','text','placeholder="New York or NY"')+birthInput('City of birth','city','text','placeholder="Enter your birth city"')+'</div>'+
 btn('Find my birth city','birth-search','cream',b.busy?'disabled':'')+'<div id="birth-place-results" aria-live="polite">'+birthPlaceResults()+'</div>'+
 '<div class="controls">'+selector('Zodiac','birth-zodiac',['tropical','sidereal'],b.zodiac,zodiacLabels)+(state.tool==='moon'?'':selector('House system','birth-houses',['placidus','whole_sign','equal'],b.houses,houseLabels))+'</div><p class="muted">Sidereal uses Lahiri. Your birth time is converted using the selected city’s historical timezone.</p>'+
 (state.error.includes('occurred twice')?'<label class="field">Repeated clock time<select id="birth-fold"><option value="">Choose an occurrence</option><option value="0" '+(b.fold==='0'?'selected':'')+'>First occurrence (before clocks moved back)</option><option value="1" '+(b.fold==='1'?'selected':'')+'>Second occurrence (after clocks moved back)</option></select></label>':'')+
 btn(b.busy?'Calculating…':state.tool==='moon'?'Find my natal Moon':'Create my birth chart','tool-run','',b.busy?'disabled':'')+
 (state.error?notice(state.error,'error'):'')+'</div>';
}
function birthPlaceResults(){const b=birthFormState;return (b.place?'<p class="selected-place">✓ '+e(b.place.label)+' · '+e(b.place.timezone)+'</p>':'')+
 b.places.map(p=>'<button class="place-choice" data-action="birth-place" data-place-id="'+e(p.place_id)+'">'+e(p.label)+'<small>'+e(p.timezone)+'</small></button>').join('');}
async function searchBirthCity(){const b=birthFormState;b.busy=true;b.place=null;b.places=[];state.error='';render();try{
 const r=await api('/astrology/locations/search?'+new URLSearchParams({city:b.city,country:b.country,state:b.region}));b.places=r.places;
 if(!b.places.length)state.error='No matching city found. Check the country and state, or try a nearby listed town. The city directory covers towns with at least 1,000 people.';
 }catch(ex){state.error=ex.message}b.busy=false;render();}
async function calculateBirth(){const b=birthFormState;state.error='';state.result=null;
 if(!b.place){state.error='Find and select your birth city first.';render();return}
 if(!b.date||!/^(?:[01]?\d|2[0-3])$/.test(b.hour)||!/^\d{1,2}$/.test(b.minute)||Number(b.minute)>59){state.error='Enter a valid birth date, hour (0–23) and minutes (0–59).';render();return}
 b.busy=true;render();try{state.result=await post('/astrology/'+(state.tool==='moon'?'moon-phase':'natal-chart'),{
 name:b.name,birth_date:b.date,birth_time:b.hour.padStart(2,'0')+':'+b.minute.padStart(2,'0'),place_id:b.place.place_id,
 zodiac:b.zodiac,house_system:b.houses,chart_system:state.tool==='draconic'?'draconic':'natal',time_fold:b.fold===''?null:Number(b.fold)
 });}catch(ex){state.error=ex.message}b.busy=false;render();document.querySelector('.birth-report')?.scrollIntoView({behavior:'smooth',block:'start'});}
function birthReport(o){return '<article class="result birth-report"><h2>'+e(o.name?o.name+'’s '+o.title:o.title)+'</h2><p>'+e(o.location?.label)+' · '+e(o.birth_local_time)+'<br>'+e(o.zodiac_label)+' · '+e(houseLabels[o.house_system]||o.house_system)+' houses</p>'+
 '<div class="chart-wheel" role="img" aria-label="Birth chart wheel showing the twelve zodiac signs, houses and planet positions">'+o.wheel_svg+'</div><p><b>Ascendant:</b> '+e(o.ascendant)+' · <b>Midheaven:</b> '+e(o.midheaven)+'</p>'+
 '<p>'+e(o.report_note)+'</p><h2>Your planets: signs & houses</h2><div class="planet-summary">'+o.placements.map(p=>'<div><b>'+e(p.planet)+'</b><span>'+e(p.formatted)+' · House '+p.house+(p.retrograde?' · Retrograde':'')+'</span></div>').join('')+'</div>'+
 o.placements.map(p=>'<section class="report-section"><h3>'+e(p.planet)+' in '+e(p.sign)+' · House '+p.house+'</h3>'+p.paragraphs.map(t=>'<p>'+e(t)+'</p>').join('')+'</section>').join('')+
 '<h2>Your twelve houses</h2>'+o.houses.map(h=>'<section class="report-section"><h3>House '+h.number+' · '+e(h.title)+' · '+e(h.formatted)+'</h3><p>'+e(h.description)+'</p></section>').join('')+
 '<h2>Major planetary aspects</h2>'+(o.aspects.length?o.aspects.map(a=>'<section class="report-section"><h3>'+e(a.planet_a)+' '+e(a.aspect)+' '+e(a.planet_b)+' · Orb '+a.orb.toFixed(2)+'°</h3><p>'+e(a.description)+'</p></section>').join(''):'<p>No major aspects fall within the selected orbs.</p>')+
 '<h2>Element & modality balance</h2><p>'+e(Object.entries(o.elements).map(([k,v])=>k+': '+v).join(' · '))+'</p><p>'+e(Object.entries(o.modalities).map(([k,v])=>k+': '+v).join(' · '))+'</p><p>These counts include all ten planets equally. Slow planets describe shared generational themes.</p>'+btn('Print / save report as PDF','print-chart','cream')+'</article>';}
function dailySkyPage(){const d=state.transit;
 let out=heading('Cosmos & Transits 🌙','Your daily Moon phase, planetary positions and zodiac reflections.');
 out+='<div class="glass"><h3>Daily Moon & Planetary Alignment</h3><div class="controls">'+field('Date (blank = today)','sky-date','date',skyUI.date)+selector('Zodiac','sky-zodiac',['tropical','sidereal'],skyUI.zodiac,zodiacLabels)+selector('Your zodiac sign','transit-sign',signs,state.sign)+'</div><p>Timezone: '+e(skyUI.timezone)+'. Today updates automatically; other dates show local noon.</p>'+btn(skyUI.loading?'Loading…':'Refresh my cosmic weather','get-transit','',skyUI.loading?'disabled':'')+(skyUI.error?notice(skyUI.error,'error'):'')+'</div>';
 if(d){out+='<div class="glass moon-detail"><h2>'+e(d.moon_emoji)+' '+e(d.moon_phase)+'</h2><p>'+d.illumination_percent+'% illuminated · '+(d.moon.waxing?'Waxing':'Waning')+'</p><p><b>Sky for '+e(d.date)+'</b> · '+e(new Date(d.as_of).toLocaleString(undefined,{timeZone:d.timezone,dateStyle:'long',timeStyle:'short'}))+'<br>'+e(d.zodiac_label)+'</p><p>Next '+e(d.moon.next_phase)+': '+e(new Date(d.moon.next_phase_at).toLocaleString())+'</p><small>'+e(d.moon.phase_convention)+'</small></div>'+
 '<div class="tiles">'+d.planets.map(p=>'<div class="glass"><h3>'+e(p.glyph)+' '+e(p.planet)+'</h3><p>'+e(p.formatted)+'</p><b class="'+(p.retrograde?'retrograde':'')+'">'+e(p.motion)+'</b></div>').join('')+'</div>'+
 '<div class="glass"><h2>Your '+e(d.selected_sign)+' daily reflection</h2>'+d.forecast.details.map(f=>'<h3>'+e(f.planet)+' · '+e(f.title)+'</h3><p>'+e(f.text)+'</p>').join('')+'<p class="muted">'+e(d.forecast.method)+'</p><small>'+e(d.forecast.note)+'</small></div>';
 }return out+'<div class="glass">'+btn('Create my birth chart','tool:natal')+' '+btn('Explore astrology tools','nav:explore','cream')+'</div>';}
async function fetchDailySky(){const request=++skyUI.request;skyUI.loading=true;skyUI.error='';if(state.page==='cosmos')render();
 try{const data=await api('/astrology/daily-transits?'+new URLSearchParams({sign:state.sign,timezone:skyUI.timezone,zodiac:skyUI.zodiac,...(skyUI.date?{date:skyUI.date}:{})}));if(request!==skyUI.request)return;state.transit=data;skyUI.lastFetch=Date.now();}
 catch(ex){if(request!==skyUI.request)return;state.transit=null;skyUI.error='Unable to load the sky: '+ex.message;}
 skyUI.loading=false;if(state.page==='cosmos')render();}
function refreshSkyIfNeeded(force=false){if(state.page==='cosmos'&&!skyUI.loading&&(force||!state.transit||Date.now()-skyUI.lastFetch>60000))fetchDailySky();}
document.addEventListener('input',ev=>{const key=ev.target.dataset?.birthKey;if(key){birthFormState[key]=ev.target.value;if(['date','hour','minute'].includes(key))birthFormState.fold='';if(['city','country','region'].includes(key)){birthFormState.place=null;birthFormState.places=[];birthFormState.fold='';const results=document.querySelector('#birth-place-results');if(results)results.innerHTML='';}}});
document.addEventListener('change',ev=>{const id=ev.target.id;if(id==='birth-zodiac')birthFormState.zodiac=ev.target.value;if(id==='birth-houses')birthFormState.houses=ev.target.value;if(id==='birth-fold')birthFormState.fold=ev.target.value;
 if(['sky-date','sky-zodiac','transit-sign'].includes(id)){skyUI.date=document.querySelector('#sky-date')?.value||'';skyUI.zodiac=document.querySelector('#sky-zodiac')?.value||'tropical';state.sign=document.querySelector('#transit-sign')?.value||state.sign;fetchDailySky();}});
document.addEventListener('click',ev=>{const b=ev.target.closest('[data-action]');if(!b)return;const a=b.dataset.action;
 if(a==='birth-search'){ev.preventDefault();searchBirthCity()}
 if(a==='birth-place'){ev.preventDefault();birthFormState.place=birthFormState.places.find(p=>p.place_id===b.dataset.placeId);birthFormState.places=[];birthFormState.fold='';render()}
 if(a==='print-chart')window.print();});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refreshSkyIfNeeded(true)});
window.addEventListener('focus',()=>refreshSkyIfNeeded(true));
window.addEventListener('hashchange',()=>{if(typeof state!=='undefined'&&location.hash==='#cosmos')setTimeout(()=>refreshSkyIfNeeded(true),0)});
if(typeof setInterval!=='undefined')setInterval(()=>{if(typeof state!=='undefined')refreshSkyIfNeeded()},60000);
