/* Birth charts and daily sky: shared API data, accessible browser controls. */
'use strict';
const zodiacLabels={tropical:'Tropical',sidereal:'Sidereal (Lahiri)'};
const houseLabels={placidus:'Placidus',whole_sign:'Whole Sign',equal:'Equal'};
const birthFormState={name:'',date:'',hour:'',minute:'00',city:'',country:'US',region:'',place:null,places:[],zodiac:'tropical',houses:'placidus',rulership:'modern',fold:'',busy:false};
const skyUI={date:'',timezone:Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC',zodiac:'tropical',loading:false,error:'',request:0,lastFetch:0};
function birthInput(label,key,type='text',attrs=''){
 const id=key==='date'?'birth-date':'birth-'+key;
 return '<label class="field">'+e(label)+'<input id="'+id+'" data-birth-key="'+key+'" type="'+type+'" value="'+e(birthFormState[key])+'" '+attrs+'></label>';
}
function birthForm(){const b=birthFormState;
 return '<div class="glass birth-form"><h3>Your birth details</h3>'+birthInput('Name (optional)','name','text','autocomplete="name" maxlength="80"')+
 '<div class="controls">'+birthInput('Date of birth','date','date','min="1900-01-01" max="2100-12-31"')+birthClockSelectors()+'</div>'+
 '<div class="controls">'+birthInput('Country name or code','country','text','placeholder="United States or US"')+birthInput('State / province','region','text','placeholder="New York or NY"')+birthInput('City of birth','city','text','placeholder="Enter your birth city"')+'</div>'+
 btn('Find my birth city','birth-search','cream',b.busy?'disabled':'')+'<div id="birth-place-results" aria-live="polite">'+birthPlaceResults()+'</div>'+
 '<div class="controls">'+selector('Zodiac','birth-zodiac',['tropical','sidereal'],b.zodiac,zodiacLabels)+(state.tool==='moon'?'':selector('House system','birth-houses',['placidus','whole_sign','equal'],b.houses,houseLabels)+selector('House rulers','birth-rulership',['modern','traditional'],b.rulership,{modern:'Modern (10 planets)',traditional:'Traditional (7 planets)'}))+'</div><p class="muted">Sidereal uses Lahiri. Your birth time is converted using the selected city’s historical timezone.</p>'+
 (state.error.includes('occurred twice')?'<label class="field">Repeated clock time<select id="birth-fold"><option value="">Choose an occurrence</option><option value="0" '+(b.fold==='0'?'selected':'')+'>First occurrence (before clocks moved back)</option><option value="1" '+(b.fold==='1'?'selected':'')+'>Second occurrence (after clocks moved back)</option></select></label>':'')+
 btn(b.busy?'Calculating…':state.tool==='moon'?'Find my natal Moon':'Create my birth chart','tool-run','',b.busy?'disabled':'')+
 (state.error?notice(state.error,'error'):'')+'</div>';
}
function birthClockSelectors(){const b=birthFormState;
 const hours=['AM','PM'].map(period=>'<optgroup label="'+period+'">'+Array.from({length:12},(_,i)=>{const hour=String(i||12).padStart(2,'0'),value=hour+' '+period;return '<option value="'+value+'" '+(b.hour===value?'selected':'')+'>'+Number(hour)+' '+period+(i===0?(period==='AM'?' (midnight)':' (noon)'):'')+'</option>'}).join('')+'</optgroup>').join('');
 return '<label class="field">Hour (AM/PM)<select id="birth-hour" data-birth-key="hour"><option value="" '+(!b.hour?'selected':'')+'>Choose your birth hour</option>'+hours+'</select></label><label class="field">Minutes<select id="birth-minute" data-birth-key="minute">'+Array.from({length:60},(_,i)=>{const value=String(i).padStart(2,'0');return '<option value="'+value+'" '+(b.minute===value?'selected':'')+'>'+value+'</option>'}).join('')+'</select></label><p class="birth-time-hint">Use the local time on your birth record. 12 AM is midnight; 12 PM is noon.</p>';
}
function birthPlaceResults(){const b=birthFormState;return (b.place?'<p class="selected-place">✓ '+e(b.place.label)+' · '+e(b.place.timezone)+'</p>':'')+
 b.places.map(p=>'<button class="place-choice" data-action="birth-place" data-place-id="'+e(p.place_id)+'">'+e(p.label)+'<small>'+e(p.timezone)+'</small></button>').join('');}
async function searchBirthCity(){const b=birthFormState;b.busy=true;b.place=null;b.places=[];state.error='';render();try{
 const r=await api('/astrology/locations/search?'+new URLSearchParams({city:b.city,country:b.country,state:b.region}));b.places=r.places;
 if(!b.places.length)state.error='No matching city found. Check the country and state, or try a nearby listed town. The city directory covers towns with at least 1,000 people.';
 }catch(ex){state.error=ex.message}b.busy=false;render();}
async function calculateBirth(){const b=birthFormState;state.error='';state.result=null;
 if(!b.place){state.error='Find and select your birth city first.';render();return}
 if(!b.date||!/^(?:0[1-9]|1[0-2]) (?:AM|PM)$/.test(b.hour)||!/^\d{2}$/.test(b.minute)||Number(b.minute)>59){state.error='Enter a valid birth date, choose an AM or PM birth hour, and minutes (00–59).';render();return}
 const [hour,period]=b.hour.split(' ');
 b.busy=true;render();try{state.result=await post('/astrology/'+(state.tool==='moon'?'moon-phase':'natal-chart'),{
 name:b.name,birth_date:b.date,birth_time:hour+':'+b.minute,birth_period:period,place_id:b.place.place_id,
 zodiac:b.zodiac,house_system:b.houses,rulership:b.rulership,chart_system:'natal',time_fold:b.fold===''?null:Number(b.fold)
 });}catch(ex){state.error=ex.message}b.busy=false;render();document.querySelector('.birth-report')?.scrollIntoView({behavior:'smooth',block:'start'});}
function birthLocalLabel(o){try{return new Date(o.birth_local_time).toLocaleString(undefined,{timeZone:o.location.timezone,year:'numeric',month:'long',day:'numeric',hour:'numeric',minute:'2-digit',hour12:true,timeZoneName:'short'})}catch{return o.birth_local_time}}
function aspectLine(a){return e(a.planet_a)+' '+e(a.aspect)+' '+e(a.planet_b)+' · '+e(a.orb_formatted||a.orb.toFixed(2)+'°')+(a.motion?' · '+e(a.motion):'')}
function symbolicPosition(p){return e(p.display_sign_glyph||p.sign_glyph||'')+' '+e(p.degree_formatted||p.formatted)+' <small>'+e(p.display_sign||p.sign)+'</small>'}
function chartPositionTables(o){return selector('Zodiac','report-zodiac',['tropical','sidereal'],o.zodiac,zodiacLabels)+'<nav class="report-jumps" aria-label="Birth report sections"><a href="#chart-wheel">Chart</a><a href="#chart-angles">Angles</a><a href="#chart-planets">Planets</a><a href="#chart-houses">Houses</a><a href="#chart-aspects">Aspects</a></nav><h3>Planet positions</h3><table><thead><tr><th>Planet</th><th>Position</th><th>House</th></tr></thead><tbody>'+o.placements.map(p=>'<tr><td>'+e(p.glyph||'')+' '+e(p.planet)+'</td><td>'+symbolicPosition(p)+(p.retrograde?' R':'')+'</td><td>'+p.house+'</td></tr>').join('')+'</tbody></table><h3>Angles</h3><table><tbody>'+(o.angles||[]).map(a=>'<tr><th>'+e(a.code)+'</th><td>'+symbolicPosition(a)+'</td></tr>').join('')+'</tbody></table><h3>House cusps</h3><table><tbody>'+o.houses.map(h=>'<tr><th>'+h.number+'</th><td>'+symbolicPosition(h)+'</td></tr>').join('')+'</tbody></table>'}
function birthReport(o){return '<article class="result birth-report"><h2>'+e(o.name?o.name+'’s '+o.title:o.title)+'</h2><p>'+e(o.location?.label)+' · '+e(birthLocalLabel(o))+'<br>'+e(o.zodiac_label)+' · '+e(houseLabels[o.house_system]||o.house_system)+' houses · '+e(o.rulership||'modern')+' rulership</p><div class="birth-chart-layout"><div class="birth-narrative">'+
 '<div class="chart-wheel" id="chart-wheel" role="img" aria-label="Birth chart wheel showing the twelve zodiac signs, houses and planet positions">'+o.wheel_svg+'</div><p><b>Ascendant:</b> '+e(o.ascendant)+' · <b>Midheaven:</b> '+e(o.midheaven)+'</p><p>'+e(o.report_note)+'</p>'+
 '<div class="report-mobile-summary planet-summary">'+o.placements.map(p=>'<div><b>'+e(p.glyph||'')+' '+e(p.planet)+'</b><span>'+symbolicPosition(p)+' · House '+p.house+(p.retrograde?' · Retrograde':'')+'</span></div>').join('')+'</div>'+
 '<h2 id="chart-angles">Ascendant, Midheaven & chart angles</h2>'+(o.angles||[]).map(a=>'<section class="report-section"><h3>'+e(a.name)+' ('+e(a.code)+') in '+e(a.sign)+'</h3><p><b>'+e(a.topic)+' · '+e(a.formatted)+'</b></p>'+a.paragraphs.map(t=>'<p>'+e(t)+'</p>').join('')+'<h4>'+e(a.code)+' aspects</h4>'+(a.aspects.length?a.aspects.map(x=>'<p>'+aspectLine(x)+'</p>').join(''):'<p>No major aspects within the selected orb.</p>')+'</section>').join('')+
 '<h2 id="chart-planets">Your planets: signs & houses</h2>'+o.placements.map(p=>'<section class="report-section"><h3>'+e(p.planet)+' in '+e(p.sign)+' · House '+p.house+'</h3><p>'+e(p.formatted)+' · '+e(p.motion)+'</p>'+p.paragraphs.map(t=>'<p>'+e(t)+'</p>').join('')+'</section>').join('')+
 '<h2 id="chart-houses">Your twelve houses</h2>'+o.houses.map(h=>'<section class="report-section"><h3>House '+h.number+' · '+e(h.title)+' · '+e(h.formatted)+'</h3><p>'+e(h.description)+'</p>'+(h.ruler_placement?'<h4>Ruler of house '+h.number+': '+e(h.ruling_planet)+'</h4>'+h.ruler_paragraphs.map(t=>'<p>'+e(t)+'</p>').join(''):'')+'<h4>Planets in house '+h.number+'</h4><p>'+e(h.occupants?.length?h.occupants.join(', '):'No planets in this house.')+'</p></section>').join('')+
 '<h2 id="chart-aspects">Major planetary aspects</h2>'+(o.aspects.length?o.aspects.map(a=>'<section class="report-section"><h3>'+aspectLine(a)+'</h3><p>'+e(a.description)+'</p></section>').join(''):'<p>No major aspects fall within the selected orbs.</p>')+
 '<p>'+e(o.aspect_motion_note||'')+'</p>'+(o.aspect_settings?'<p>Orb limits (degrees): '+e(Object.entries(o.aspect_settings).map(([k,v])=>k+': '+v).join(' · '))+'</p>':'')+
 '<h2>Element & modality balance</h2><p>'+e(Object.entries(o.elements).map(([k,v])=>k+': '+v).join(' · '))+'</p><p>'+e(Object.entries(o.modalities).map(([k,v])=>k+': '+v).join(' · '))+'</p><p>These counts include all ten planets equally. Slow planets describe shared generational themes.</p>'+btn('Print / save report as PDF','print-chart','cream')+'</div><aside class="birth-sidebar" aria-label="Birth chart positions">'+chartPositionTables(o)+'</aside></div></article>';}
const moonUI={month:'',pinned:false,data:null,key:'',loading:false,error:'',request:0,selectedDate:''};
function moonCalendar(){
 const c=moonUI.data;const selected=c?.days.find(d=>d.date===(moonUI.selectedDate||skyUI.date||state.transit?.date))||c?.days[0];
 let html='<section class="glass moon-calendar" id="moon-calendar"><h2>Monthly Moon Phases</h2><div class="moon-month-nav">'+btn('← Previous year','moon-prev-year','cream',moonUI.month.startsWith('1900')?'disabled':'')+btn('← Previous month','moon-prev','cream',moonUI.month==='1900-01'?'disabled':'')+field('Month','moon-month','month',moonUI.month,'min="1900-01" max="2100-12"')+btn('Next month →','moon-next','cream',moonUI.month==='2100-12'?'disabled':'')+btn('Next year →','moon-next-year','cream',moonUI.month.startsWith('2100')?'disabled':'')+'</div>';
 if(moonUI.loading)return html+'<p role="status">Loading Moon calendar…</p></section>';
 if(moonUI.error)return html+notice(moonUI.error,'error')+btn('Retry calendar','moon-retry')+'</section>';
 if(!c)return html+'<p>The monthly calendar loads with your daily sky.</p></section>';
 html+='<h3>'+e(c.title)+'</h3><p>'+e(c.timezone)+' · '+e(zodiacLabels[c.zodiac])+'</p><div class="moon-calendar-grid">'+c.weekdays.map(d=>'<div class="moon-weekday">'+d+'</div>').join('')+Array(c.first_weekday).fill('<div class="moon-calendar-blank" aria-hidden="true"></div>').join('')+c.days.map(d=>{
  const event=d.events[0];const label=event?.phase||d.phase||'Skipped date';const emoji=event?.emoji||d.emoji||'—';
  return '<button class="moon-calendar-day '+(event?'moon-event-day ':'')+(selected?.date===d.date?'moon-day-selected':'')+'" data-action="moon-day" data-date="'+d.date+'" aria-label="'+d.date+' '+e(label)+'" '+(!d.available?'disabled':'')+'><b>'+d.day+'</b><span class="moon-day-emoji">'+emoji+'</span><small>'+e(d.moon_sign?.slice(0,3)||'—')+'</small></button>';
 }).join('')+'</div>';
 if(selected)html+='<div class="moon-selected-day"><h3>'+e(selected.date)+' · '+e(selected.phase||'Skipped date')+'</h3>'+(selected.available?'<p>'+selected.illumination_percent+'% illuminated at local noon · '+e(selected.moon_position)+'</p>':'<p>'+e(selected.note)+'</p>')+selected.events.map(x=>'<p><b>'+e(x.emoji+' '+x.phase)+'</b> · '+e(new Date(x.at_local).toLocaleString(undefined,{timeZone:c.timezone,dateStyle:'long',timeStyle:'short'}))+'</p>').join('')+'</div>';
 return html+lunarDailyTable(c)+'<h3>This month’s principal phases</h3><ul class="moon-events">'+c.events.map(x=>'<li><b>'+e(x.emoji+' '+x.phase)+'</b><span>'+e(new Date(x.at_local).toLocaleString(undefined,{timeZone:c.timezone,dateStyle:'long',timeStyle:'short'}))+'</span></li>').join('')+'</ul><p class="muted">'+e(c.note)+'</p></section>';
}
function lunarDailyTable(c){
 const time=value=>new Date(value).toLocaleTimeString(undefined,{timeZone:c.timezone,hour:'2-digit',minute:'2-digit'});
 const date=d=>new Date(d.date+'T12:00:00Z').toLocaleDateString(undefined,{timeZone:'UTC',weekday:'long',month:'long',day:'numeric'});
 return '<h3>Day-by-day lunar calendar</h3><p class="muted">Sign changes and phase events use '+e(c.timezone)+'. Body correspondences below are traditional astrology lore.</p><div class="lunar-table-wrap"><table class="lunar-daily-table"><thead><tr><th>Date</th><th>Lunar phase</th><th>Moon sign & changes</th><th>Traditional body associations</th><th>Surgery</th></tr></thead><tbody>'+c.days.map(d=>'<tr class="'+(d.events.length?'lunar-principal-row':'')+'"><th><button data-action="moon-day" data-date="'+d.date+'" '+(!d.available?'disabled':'')+'>'+e(date(d))+'</button></th><td><span class="moon-day-emoji" role="img" aria-label="'+e(d.phase||'Skipped date')+'">'+(d.moon_image_svg||e(d.emoji||'—'))+'</span> '+e(d.events[0]?.phase||d.phase||'Skipped date')+(d.available?'<small>'+d.illumination_percent+'% at noon</small>':'')+d.events.map(x=>'<small>'+e(x.phase)+' at '+e(time(x.at_local))+'</small>').join('')+'</td><td>'+(d.sign_intervals||[]).map((x,i)=>'<div><b>'+e(x.glyph+' '+x.sign)+'</b><small>'+(i?'From '+e(time(x.from_local)):'At start of day')+'</small></div>').join('')+'</td><td>'+(d.sign_intervals||[]).map(x=>'<p><b>'+e(x.sign)+':</b> '+e(x.traditional_body_associations)+'</p>').join('')+'</td><td>Ask your surgical team</td></tr>').join('')+'</tbody></table></div><p class="lunar-health-note">'+e(c.health_note||'')+'</p>';
}
async function loadMoonCalendar(force=false){
 if(!moonUI.month)moonUI.month=state.transit?.date?.slice(0,7)||new Date().toISOString().slice(0,7);
 const key=[moonUI.month,skyUI.timezone,skyUI.zodiac].join('|');if(!force&&moonUI.key===key&&moonUI.data)return;
 const request=++moonUI.request;moonUI.loading=true;moonUI.error='';if(moonUI.key!==key)moonUI.data=null;if(state.page==='cosmos')render();
 try{const [year,month]=moonUI.month.split('-');const data=await api('/astrology/moon-calendar?'+new URLSearchParams({year,month,timezone:skyUI.timezone,zodiac:skyUI.zodiac}));if(request!==moonUI.request)return;moonUI.data=data;moonUI.key=key;}
 catch(ex){if(request!==moonUI.request)return;moonUI.data=null;moonUI.error='Unable to load Moon calendar: '+ex.message}
 moonUI.loading=false;if(state.page==='cosmos')render();
}
function changeMoonMonth(step){const [y,m]=moonUI.month.split('-').map(Number);const date=new Date(Date.UTC(y,m-1+step,1));const value=date.toISOString().slice(0,7);if(value<'1900-01'||value>'2100-12')return;moonUI.month=value;moonUI.pinned=true;moonUI.selectedDate='';loadMoonCalendar();}
function dailySkyPage(){const d=state.transit;
 let out=heading('Cosmos & Transits 🌙','Your daily Moon phase, planetary positions and zodiac reflections.');
 out+='<div class="glass"><h3>Daily Moon & Planetary Alignment</h3><div class="controls">'+field('Date (blank = today)','sky-date','date',skyUI.date)+selector('Zodiac','sky-zodiac',['tropical','sidereal'],skyUI.zodiac,zodiacLabels)+selector('Your zodiac sign','transit-sign',signs,state.sign)+'</div><p>Timezone: '+e(skyUI.timezone)+'. Today updates automatically; other dates show local noon.</p>'+btn(skyUI.loading?'Loading…':'Refresh my cosmic weather','get-transit','',skyUI.loading?'disabled':'')+(skyUI.error?notice(skyUI.error,'error'):'')+'</div>';
 if(d){out+='<div class="glass moon-detail"><h2>'+e(d.moon_emoji)+' '+e(d.moon_phase)+'</h2><p>'+d.illumination_percent+'% illuminated · '+(d.moon.waxing?'Waxing':'Waning')+'</p><p><b>Sky for '+e(d.date)+'</b> · '+e(new Date(d.as_of).toLocaleString(undefined,{timeZone:d.timezone,dateStyle:'long',timeStyle:'short'}))+'<br>'+e(d.zodiac_label)+'</p><p>Next '+e(d.moon.next_phase)+': '+e(new Date(d.moon.next_phase_at).toLocaleString())+'</p><small>'+e(d.moon.phase_convention)+'</small></div>'+
 moonCalendar()+'<div class="tiles">'+d.planets.map(p=>'<div class="glass"><h3>'+e(p.glyph)+' '+e(p.planet)+'</h3><p>'+e(p.formatted)+'</p><b class="'+(p.retrograde?'retrograde':'')+'">'+e(p.motion)+'</b></div>').join('')+'</div>'+
 '<div class="glass"><h2>Your '+e(d.selected_sign)+' daily reflection</h2>'+d.forecast.details.map(f=>'<h3>'+e(f.planet)+' · '+e(f.title)+'</h3><p>'+e(f.text)+'</p>').join('')+'<p class="muted">'+e(d.forecast.method)+'</p><small>'+e(d.forecast.note)+'</small></div>';
 }return out+'<div class="glass">'+btn('Create my birth chart','tool:natal')+' '+btn('Explore astrology tools','nav:explore','cream')+'</div>';}
async function fetchDailySky(){const request=++skyUI.request;skyUI.loading=true;skyUI.error='';if(state.page==='cosmos')render();
 try{const data=await api('/astrology/daily-transits?'+new URLSearchParams({sign:state.sign,timezone:skyUI.timezone,zodiac:skyUI.zodiac,...(skyUI.date?{date:skyUI.date}:{})}));if(request!==skyUI.request)return;state.transit=data;skyUI.lastFetch=Date.now();if(!moonUI.pinned)moonUI.month=data.date.slice(0,7);loadMoonCalendar();}
 catch(ex){if(request!==skyUI.request)return;state.transit=null;skyUI.error='Unable to load the sky: '+ex.message;}
 skyUI.loading=false;if(state.page==='cosmos')render();}
function refreshSkyIfNeeded(force=false){if(state.page==='cosmos'&&!skyUI.loading&&(force||!state.transit||Date.now()-skyUI.lastFetch>60000))fetchDailySky();}
function updateBirthField(ev){const key=ev.target.dataset?.birthKey;if(key){birthFormState[key]=ev.target.value;if(['date','hour','minute'].includes(key))birthFormState.fold='';if(['city','country','region'].includes(key)){birthFormState.place=null;birthFormState.places=[];birthFormState.fold='';const results=document.querySelector('#birth-place-results');if(results)results.innerHTML='';}}}
document.addEventListener('input',updateBirthField);
document.addEventListener('change',updateBirthField);
document.addEventListener('change',ev=>{const id=ev.target.id;if(id==='report-zodiac'){birthFormState.zodiac=ev.target.value;calculateBirth();}if(id==='birth-zodiac')birthFormState.zodiac=ev.target.value;if(id==='birth-houses')birthFormState.houses=ev.target.value;if(id==='birth-rulership')birthFormState.rulership=ev.target.value;if(id==='birth-fold')birthFormState.fold=ev.target.value;
 if(id==='moon-month'&&/^\d{4}-\d{2}$/.test(ev.target.value)){moonUI.month=ev.target.value;moonUI.pinned=true;moonUI.selectedDate='';loadMoonCalendar();}
 if(id==='sky-date')moonUI.pinned=false;
 if(['sky-date','sky-zodiac','transit-sign'].includes(id)){skyUI.date=document.querySelector('#sky-date')?.value||'';skyUI.zodiac=document.querySelector('#sky-zodiac')?.value||'tropical';state.sign=document.querySelector('#transit-sign')?.value||state.sign;fetchDailySky();}});
document.addEventListener('click',ev=>{const b=ev.target.closest('[data-action]');if(!b)return;const a=b.dataset.action;
 if(a==='birth-search'){ev.preventDefault();searchBirthCity()}
 if(a==='birth-place'){ev.preventDefault();birthFormState.place=birthFormState.places.find(p=>p.place_id===b.dataset.placeId);birthFormState.places=[];birthFormState.fold='';render()}
 if(a==='moon-prev-year'){ev.preventDefault();changeMoonMonth(-12)}
 if(a==='moon-next-year'){ev.preventDefault();changeMoonMonth(12)}
 if(a==='moon-prev'){ev.preventDefault();changeMoonMonth(-1)}
 if(a==='moon-next'){ev.preventDefault();changeMoonMonth(1)}
 if(a==='moon-retry'){ev.preventDefault();loadMoonCalendar(true)}
 if(a==='moon-day'){ev.preventDefault();skyUI.date=b.dataset.date;moonUI.selectedDate=b.dataset.date;moonUI.pinned=true;fetchDailySky();}
 if(a==='print-chart')window.print();});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refreshSkyIfNeeded(true)});
window.addEventListener('focus',()=>refreshSkyIfNeeded(true));
window.addEventListener('hashchange',()=>{if(typeof state!=='undefined'&&location.hash==='#cosmos')setTimeout(()=>refreshSkyIfNeeded(true),0)});
if(typeof setInterval!=='undefined')setInterval(()=>{if(typeof state!=='undefined')refreshSkyIfNeeded()},60000);
