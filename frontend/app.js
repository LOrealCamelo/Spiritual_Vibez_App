'use strict';
const $=(s)=>document.querySelector(s);
const esc=(v)=>String(v??'').replace(/[&<>"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const signs=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const groups={
  'Astrology & Charts':[['moon','🌒','Natal Moon Phase'],['natal','🪐','Natal Birth Chart'],['draconic','🐉','Draconic Chart'],['bazi','🐲','Chinese Zodiac & BaZi'],['houses','🏡','Twelve Zodiac Houses'],['asteroids','☄️','Asteroids'],['calendar','🗓️','13-Moon Calendar'],['astro','🌍','Astrocartography']],
  'Numbers & Love':[['life','🔢','Life Path Calculator'],['numbers','✨','Numerology Academy'],['love','💞','Love Match']],
  'Sound, Rituals & Wellness':[['sound','🎵','Frequency Studio'],['rituals','🕯️','Ritual Finder'],['cycle','🌸','Moon & Cycle Tracker'],['shadow','📓','Shadow Work']],
  'Divination & More':[['runes','ᚠ','Rune Casting'],['pendulum','🔮','Pendulum Dowsing'],['oracle','💬','Mystic Companion'],['store','🛍️','Creator Store']]
};
const tools=Object.values(groups).flat();
const pill=(name,action,active=false,attr='')=>'<button class="pill '+(active?'active':'')+'" data-action="'+action+'" '+attr+'>'+esc(name)+'</button>';
const btn=(name,action,alt=false,disabled=false)=>'<button class="btn '+(alt?'alt':'')+'" data-action="'+action+'" '+(disabled?'disabled':'')+'>'+name+'</button>';
const field=(label,id,type='text',value='')=>'<label class="field">'+esc(label)+'<input id="'+id+'" type="'+type+'" value="'+esc(value)+'"></label>';
const chooser=(label,id,options,selected)=>'<label class="field">'+esc(label)+'<select id="'+id+'">'+options.map(x=>'<option '+(x===selected?'selected':'')+'>'+esc(x)+'</option>').join('')+'</select></label>';
const note=(txt,kind='')=>'<div class="notice '+kind+'">'+esc(txt)+'</div>';
const heading=(title,sub)=>'<div class="eyebrow">SPIRITUAL VIBEZ ✦</div><h1 class="page-title">'+title+'</h1><p class="page-sub">'+sub+'</p>';
let page='home',tool=null,spreads=[],cards=[],chosen=null,dealt={},interpretation='',cat='All',query='',filter='all',cardDetails=null,quiz=null,answer='',transit=null,sign='Scorpio',result=null,err='',audio=null,osc=null;
async function request(path,opts){const r=await fetch('/api'+path,opts);if(!r.ok)throw Error('Backend HTTP '+r.status+'. Please verify the API is running.');return r.json()}
const post=(p,obj)=>request(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)});
function screen(p){page=p;tool=null;result=null;err='';location.hash=p;paint();window.scrollTo(0,0)}
function openTool(id){page='explore';tool=id;result=null;err='';location.hash='explore/'+id;paint();window.scrollTo(0,0)}
function home(){
 let out='<section class="hero"><div class="stars"></div><div class="skyline"></div><span class="moon">☾</span><div class="hero-copy"><div class="eyebrow">TAROT, ASTRO & DAILY VIBES ✨</div><h1>Zero boring.</h1><p>Explore cards, learn tarot, and discover something about yourself—your way.</p><div class="hero-buttons">'+btn('🔀 Try a spread','nav:spreads')+btn('📚 Learn tarot','nav:learn',true)+'</div></div><div class="hero-art"><img src="/guide.svg" style="height:100%;width:100%;object-fit:contain;object-position:bottom" alt="Illustrated tarot guide with headphones, tattoos and colorful tarot cards"></div></section>';
 const quick=[['spreads','🃏','Tarot Spreads','Shuffle & reveal'],['learn','📚','Learn Tarot','78 cards + quizzes'],['cosmos','☀️','Daily Cosmos','Planetary forecast'],['explore','💖','Explore More','All your cosmic tools']];
 out+='<div class="section-head"><h2>Pick your adventure 💫</h2></div><div class="feature-grid">'+quick.map(([id,e,n,d])=>'<button class="feature" data-action="nav:'+id+'"><span class="emoji">'+e+'</span><span><b>'+n+'</b><small>'+d+'</small></span><span class="arrow">❯</span></button>').join('')+'</div>';
 const fav=[['Reset Your Energy','⚡','Self-care'],['Trust Your Gut','💗','Clarity & Choices'],['The Next Phase','🛤️','Growth & Change'],['Grounding','🪷','Self-care']];
 out+='<div class="section-head"><h2>Fan-favorite spreads ♡</h2><a href="#spreads">See all →</a></div><div class="spread-grid">'+fav.map(([n,e,k])=>'<button class="spread-preview" data-action="favorite" data-name="'+esc(n)+'"><div class="spread-art">'+e+'</div><div class="spread-info"><small>'+k+'</small><b>'+n+'</b><span>Tap to explore ✨ →</span></div></button>').join('')+'</div>';
 return out+'<div class="home-callout"><h2>🌈 A whole cosmic world—not just tarot.</h2><p>Daily transits, birth charts, draconic charts, Chinese astrology, numerology, love matching, sound, rituals, divination and wellness in their own sections.</p>'+btn('Explore everything','nav:explore',true)+'</div>';
}
function spreadPage(){
 let h=heading(chosen?esc(chosen.title)+' 🔮':'Tarot Spreads ✨','A dedicated spread studio. Each card position has its own meaning.');
 if(chosen){
 const qs=chosen.questions||[];
 h+=btn('← Browse spreads','back-spreads',true)+'<div class="reading-board"><h3>✦ '+esc(chosen.title)+' ✦</h3><div class="card-row">'+qs.map(q=>{const d=dealt[q.slot];return '<button class="flip-card '+(d?'revealed':'')+'" data-action="draw" data-slot="'+q.slot+'" '+(d?'disabled':'')+'><span class="symbol">'+(d?esc(d.card.icon||'✦'):'☀')+'</span><b>'+esc(d?d.card.name:'CARD '+q.slot)+'</b><small>'+esc(d?d.card.orientation:'TAP TO REVEAL')+'</small></button>'}).join('')+'</div></div><div class="reading-positions">'+qs.map(q=>'<div class="position"><strong>POSITION '+q.slot+' · '+esc(q.title)+'</strong><p>'+esc(q.q)+'</p>'+(dealt[q.slot]?'<p>🃏 '+esc(dealt[q.slot].card.name)+' ('+esc(dealt[q.slot].card.orientation)+'): '+esc(dealt[q.slot].card.meaning)+'</p>':'')+'</div>').join('')+'</div>';
 h+=note('Interpretations are reflective—not predictions or professional advice.');
 h+=btn('✨ Interpret my reading','interpret',false,Object.keys(dealt).length!==qs.length)+' '+btn('🔀 Start again','reset',true);
 if(interpretation)h+='<div class="result"><h3>💗 Your combined reading</h3><p>'+esc(interpretation)+'</p>'+btn('Share reading','share-reading',true)+' '+btn('Save to journal','save-reading',true)+'</div>';
 return h;
 }
 const cats=['All',...new Set(spreads.map(s=>s.category))];
 h+='<div class="panel"><label class="field">Find a spread<input id="spread-search" placeholder="Search all spreads" value="'+esc(query)+'"></label><div class="pillbar">'+cats.map(c=>pill(c,'cat',cat===c,'data-cat="'+esc(c)+'"')).join('')+'</div></div>';
 const filtered=spreads.filter(s=>(cat==='All'||s.category===cat)&&s.title.toLowerCase().includes(query.toLowerCase()));
 h+='<div class="panels">'+filtered.map((s,i)=>'<button class="list-item" data-action="choose" data-id="'+esc(s.id)+'"><span class="icon">'+['🔮','🌙','💗','🌈','🦋','🪷'][i%6]+'</span><span><b>'+esc(s.title)+'</b><small>'+s.cardCount+' cards · '+esc(s.category)+'</small><small>'+esc(s.desc||'Reveal your insights')+'</small></span><span>❯</span></button>').join('')+'</div>';
 return h+(spreads.length?'':note('Connect to the running backend to load the 48-spread library.','error'));
}
function learnPage(){
 let h=heading('Learn Tarot 📚','This academy is completely separate from your tarot spread randomizer.');
 h+='<div class="panel gradient"><h3>🎓 Learn all 78 cards</h3><p>Study card meanings, elements, upright and reversed themes. Take a quick knowledge quiz.</p>'+btn('✨ Quiz Me','quiz')+'</div>';
 if(quiz)h+='<div class="panel"><h3>🎯 What does '+esc(quiz.card_name)+' mean?</h3><div class="pillbar">'+quiz.options.map(o=>pill(o,'answer',false,'data-answer="'+esc(o)+'"')).join('')+'</div>'+(answer?note(answer,answer.startsWith('Correct')?'success':''):'')+'</div>';
 if(cardDetails)h+='<div class="panel"><h3>'+esc(cardDetails.name)+'</h3><p><b>Upright:</b> '+esc(cardDetails.description_upright||cardDetails.upright)+'</p><p><b>Reversed:</b> '+esc(cardDetails.description_reversed||cardDetails.reversed)+'</p><p><b>Mantra:</b> '+esc(cardDetails.mantra)+'</p>'+btn('Close card','close-card',true)+'</div>';
 h+='<div class="pillbar">'+['all','Major','Wands','Cups','Swords','Coins'].map(f=>pill(f==='all'?'All 78':f,'filter',f===filter,'data-filter="'+f+'"')).join('')+'</div><div class="lesson-grid">'+cards.filter(c=>filter==='all'||c.suit===filter).map(c=>'<button class="lesson" data-action="card" data-id="'+c.id+'"><span class="sym">'+esc(c.icon||'🃏')+'</span><strong>'+esc(c.name)+'</strong><small>'+esc(c.suit)+'</small></button>').join('')+'</div>';
 return h+(cards.length?'':note('Connect to the backend to display the complete tarot encyclopedia.','error'));
}
function cosmosPage(){
 let h=heading('Cosmos & Transits 🌙','Moon phase, Sun position, Mercury and Venus, with a symbolic mood forecast.');
 h+='<div class="panel gradient"><h3>☀️ Daily planetary alignment</h3><div class="controls">'+chooser('Choose your zodiac sign','transit-sign',signs,sign)+btn('Refresh forecast','refresh')+'</div>';
 if(transit)h+='<div class="panels">'+[['🌙 Moon',transit.moon_phase],['☀️ Sun',transit.sun_position],['☿ Mercury',transit.mercury_status],['♀ Venus',transit.venus_status]].map(([a,b])=>'<div class="panel"><h3>'+esc(a)+'</h3><p>'+esc(b)+'</p></div>').join('')+'</div><div class="result"><h3>💖 Your '+esc(sign)+' forecast</h3><p>'+esc(transit.forecast?.content)+'</p>'+btn('Share forecast','share-transit')+'</div>';
 else h+=note('Select your sign and tap Refresh to fetch data from the backend.');
 return h+'</div><div class="panel"><h3>🌒 Birth charts & moon phase</h3><p>Your separate calculators are under Explore More.</p>'+btn('View astrology tools','nav:explore',true)+'</div>';
}
function toolPage(){
 if(!tool)return heading('Explore More ✨','All the features you requested, grouped into their own tappable sections.')+Object.entries(groups).map(([group,entries])=>'<div class="section-head"><h2>'+esc(group)+'</h2></div><div class="tool-grid">'+entries.map(([id,e,t])=>'<button class="tool-card" data-action="open-tool" data-tool="'+id+'"><span class="icon">'+e+'</span><b>'+esc(t)+'</b><small>Tap to explore →</small></button>').join('')+'</div>').join('');
 const t=tools.find(x=>x[0]===tool)||[tool,'✨',tool],id=tool;
 let h=btn('← Explore all','back-tools',true)+heading(t[1]+' '+esc(t[2]),'Your own dedicated '+esc(t[2])+' screen.');
 let form='';
 if(['moon','natal','draconic','bazi','life'].includes(id))form+='<div class="controls">'+field('Birth date','birth-date','date')+(['moon','natal','draconic','bazi'].includes(id)?field('Birth time','birth-time','time','12:00'):'')+'</div>';
 if(['natal','draconic'].includes(id))form+=note('CHART LIMITATION: Current backend coordinates and astronomical formulas are approximations. Accurate birth charts require verified time zones and a precision ephemeris.');
 if(id==='love')form+='<div class="controls">'+chooser('Your sign','sign-a',signs,'Scorpio')+chooser('Their sign','sign-b',signs,'Taurus')+'</div>';
 if(id==='cycle')form+='<div class="controls">'+field('Last period','period-date','date')+field('Average cycle length','cycle-length','number','28')+'</div>'+note('Cycle predictions are estimates, not fertility or contraception guidance. Do not enter personal tracking data on the public backend until accounts and privacy are implemented.');
 if(id==='rituals')form+='<div class="controls">'+field('Search by intention','search','search')+chooser('Category','ritual-category',['all','money','love','protection'],'all')+'</div>';
 if(id==='astro')form+=field('Focus city','city','text','Utica, NY');
 if(['oracle','pendulum'].includes(id))form+=field('Your question','search','text');
 if(id==='sound')form+='<div class="controls">'+chooser('Frequency (Hz)','hz',['396','417','432','528','639','741','852','963'],'528')+field('Volume (0.00–0.10)','volume','number','0.04')+'</div>'+btn('▶ Play tone','play')+' '+btn('■ Stop tone','stop',true)+note('Generated original pure sine wave, not a medical treatment. Start at low volume.');
 if(id==='shadow')form+=note('Personal journal saving should remain local until private accounts and secure storage are added.');
 if(id==='oracle')form+=note('Uses free, deterministic question matching; no paid AI API is required.');
 h+='<div class="panel"><div class="controls">'+form+'</div>'+(id==='sound'?'':btn(id==='rituals'?'Find rituals':'✨ Calculate / Explore','run-tool'))+(err?note(err,'error'):'')+'</div>';
 if(result)h+=renderResult(result);
 return h;
}
function renderResult(o){
 let inner='';
 if(o.oracle_response)inner='<p>'+esc(o.oracle_response).replace(/\n/g,'<br>')+'</p>';
 else if(o.placements)inner='<p><b>Ascendant:</b> '+esc(o.ascendant)+'</p>'+o.placements.map(x=>'<div class="line"><b>'+esc(x.planet)+':</b> '+esc(x.sign)+' · '+esc(x.house)+'</div>').join('');
 else if(o.cards)inner=o.cards.map(c=>'<p>'+esc(c.name)+'</p>').join('');
 else if(o.lessons)inner=o.lessons.map(x=>'<div class="line"><b>'+esc(x.number)+' · '+esc(x.title)+'</b><p>'+esc(x.lesson)+'</p></div>').join('');
 else if(o.rituals)inner=o.rituals.map(x=>'<div class="line"><b>'+esc(x.title)+'</b><p>'+esc(x.tools)+'</p><p>'+esc(x.steps)+'</p></div>').join('');
 else if(o.houses)inner=o.houses.map(x=>'<div class="line"><b>'+esc(x.name||x.title||x.house)+'</b><p>'+esc(x.meaning||x.desc||x.description)+'</p></div>').join('');
 else if(o.life_path_number)inner='<h3>Life Path '+esc(o.life_path_number)+'</h3><p>'+esc(o.description)+'</p>';
 else if(o.natal_moon_phase)inner='<h3>'+esc(o.natal_moon_phase)+'</h3><p>'+esc(o.description)+'</p>';
 else inner='<pre>'+esc(JSON.stringify(o,null,2))+'</pre>';
 return '<div class="result"><h3>✨ Your result</h3>'+inner+btn('Share result','share-result',true)+'</div>';
}
function journal(){
 let x=[];try{x=JSON.parse(localStorage.getItem('spiritual-vibez-journal')||'[]')}catch{}
 return heading('My Journal 💗','Save your own reflections locally in this browser.')+'<div class="panels"><div class="panel"><h3>📝 Write a reflection</h3><label class="field">Your thoughts<textarea id="journal-text" placeholder="What did you notice today?"></textarea></label>'+btn('Save reflection','save-note')+'</div><div class="panel"><h3>💌 Saved notes</h3>'+(x.length?x.slice().reverse().map(i=>'<p><b>'+esc(i.title)+'</b> · '+esc(i.date)+'<br>'+esc(i.text)+'</p>').join(''):note('Nothing saved yet.'))+'</div></div>'+note('Journal contents stay on this browser only. Avoid shared devices for sensitive entries.');
}
function layout(content){
 const n=[['home','🏠','Home'],['spreads','🔀','Spreads'],['learn','📖','Learn Tarot'],['cosmos','🌙','Cosmos'],['explore','✨','Explore'],['journal','📝','Journal']];
 const items=n.map(([id,e,t])=>'<button class="'+(id===page?'active':'')+'" data-action="nav:'+id+'"><span>'+e+'</span> '+t+'</button>').join('');
 return '<header class="topbar"><div class="nav-inner"><a class="logo" href="#home"><strong>🌙 Spiritual Vibez ✦</strong><span>ZODIAC, TAROT & MORE</span></a><nav class="topnav" aria-label="Main navigation">'+items+'</nav><div class="nav-heart">💖</div></div></header><main class="shell">'+content+'</main><footer class="footer">Spiritual Vibez • Zodiac, Tarot & More ✨ For personal reflection and entertainment.</footer><nav class="bottom-nav" aria-label="Quick navigation">'+items+'</nav>';
}
function paint(){const h={home,spreads:spreadPage,learn:learnPage,cosmos:cosmosPage,explore:toolPage,journal};$('#app').innerHTML=layout((h[page]||home)());}
const val=(id)=>document.getElementById(id)?.value||'';
const save=(title,text)=>{let x=[];try{x=JSON.parse(localStorage.getItem('spiritual-vibez-journal')||'[]')}catch{}x.push({title,text,date:new Date().toLocaleDateString()});localStorage.setItem('spiritual-vibez-journal',JSON.stringify(x.slice(-70)))};
const share=(text)=>{if(navigator.share)navigator.share({title:'Spiritual Vibez',text}).catch(()=>{});else if(navigator.clipboard)navigator.clipboard.writeText(text).then(()=>alert('Copied. You can paste it into a text, email or social post.'));else prompt('Copy to share:',text)};
async function doTool(){
 const id=tool,dob=val('birth-date'),[y,m,d]=dob.split('-').map(Number),bt=val('birth-time')||'12:00';
 if(['moon','natal','draconic','bazi','life'].includes(id)&&(!dob||isNaN(Date.parse(dob)))){err='Enter a valid birth date.';paint();return}
 const routes={
 moon:()=>post('/astrology/moon-phase',{birth_date:dob,birth_time:bt}),
 natal:()=>post('/astrology/natal-chart',{birth_date:dob,birth_time:bt,chart_system:'placidus'}),
 draconic:()=>post('/astrology/natal-chart',{birth_date:dob,birth_time:bt,chart_system:'draconic'}),
 bazi:()=>post('/astrology/bazi',{birth_year:y,birth_month:m,birth_day:d,birth_hour:Number(bt.slice(0,2))}),
 houses:()=>request('/astrology/houses'),asteroids:()=>request('/astrology/asteroids'),
 calendar:()=>request('/astrology/lunar-calendar/1'),astro:()=>request('/astrology/astrocartography?city='+encodeURIComponent(val('city'))),
 life:()=>post('/synastry/life-path',{birth_year:y,birth_month:m,birth_day:d}),
 numbers:()=>request('/synastry/numerology-lessons'),
 love:()=>post('/synastry/compatibility',{partner_a_sign:val('sign-a'),partner_b_sign:val('sign-b')}),
 rituals:()=>request('/rituals/search?category='+encodeURIComponent(val('ritual-category'))+'&query='+encodeURIComponent(val('search'))),
 cycle:()=>post('/wellness/menstrual-cycle',{last_period_date:val('period-date'),cycle_length:Number(val('cycle-length'))}),
 shadow:()=>request('/wellness/shadow-prompts'),
 runes:()=>post('/divination/runes/cast',{rune_count:3}),
 pendulum:()=>post('/divination/pendulum',{question:val('search')||'What is my next step?'}),
 oracle:()=>post('/oracle/chat',{message:val('search')||'Tell me about the Moon'}),
 store:()=>request('/store/products')
 };
 err='';result=null;try{result=await routes[id]()}catch(e){err=e.message}paint();
}
function stop(){try{osc?.stop();audio?.close()}catch{}osc=null;audio=null}
function play(){stop();try{audio=new (window.AudioContext||window.webkitAudioContext)();osc=audio.createOscillator();const gain=audio.createGain();osc.type='sine';osc.frequency.value=Number(val('hz')||528);gain.gain.value=Math.max(0,Math.min(.10,Number(val('volume')||.04)));osc.connect(gain);gain.connect(audio.destination);osc.start()}catch(e){alert(e.message)}}
document.addEventListener('click',async(e)=>{
 const b=e.target.closest('[data-action]');if(!b)return;e.preventDefault();const action=b.dataset.action;
 if(action.startsWith('nav:'))return screen(action.slice(4));
 if(action==='open-tool')return openTool(b.dataset.tool);
 if(action==='back-tools')return screen('explore');
 if(action==='favorite'){chosen=spreads.find(s=>s.title.toLowerCase()===b.dataset.name.toLowerCase())||null;dealt={};interpretation='';screen('spreads');if(!chosen)alert('Choose an available spread in the list.');return}
 if(action==='cat'){cat=b.dataset.cat;paint();return}
 if(action==='choose'){chosen=spreads.find(s=>s.id===b.dataset.id);dealt={};interpretation='';paint();window.scrollTo(0,0);return}
 if(action==='back-spreads'){chosen=null;paint();return}
 if(action==='reset'){dealt={};interpretation='';paint();return}
 if(action==='draw'){if(dealt[b.dataset.slot])return;try{const r=await post('/tarot/spreads/deal-slot',{spread_id:chosen.id,slot_num:Number(b.dataset.slot),exclude_card_ids:Object.values(dealt).map(x=>x.card.id)});dealt[b.dataset.slot]=r;paint()}catch(e){alert(e.message)}return}
 if(action==='interpret'){try{const r=await post('/tarot/spreads/synthesize',{spread_id:chosen.id,drawn_cards:Object.values(dealt).map(x=>({slot:x.slot,card_id:x.card.id,orientation:x.card.orientation})),save_to_journal:false});interpretation=r.synthesis;paint()}catch(e){alert(e.message)}return}
 if(action==='share-reading')return share(chosen.title+'\n\n'+interpretation);
 if(action==='save-reading'){save(chosen.title,interpretation);alert('Saved locally to your journal.');return}
 if(action==='filter'){filter=b.dataset.filter;paint();return}
 if(action==='card'){cardDetails=cards.find(x=>String(x.id)===b.dataset.id);paint();window.scrollTo(0,0);return}
 if(action==='close-card'){cardDetails=null;paint();return}
 if(action==='quiz'){try{quiz=await request('/tarot/study/quiz');answer='';paint()}catch(e){alert(e.message)}return}
 if(action==='answer'){answer=b.dataset.answer===quiz.correct_answer?'Correct! ✨':'Keep learning—the answer is '+quiz.correct_answer;paint();return}
 if(action==='refresh'){sign=val('transit-sign');try{transit=await request('/astrology/daily-transits?sign='+sign);paint()}catch(e){alert(e.message)}return}
 if(action==='share-transit')return share(sign+' forecast: '+transit.forecast?.content);
 if(action==='run-tool')return doTool();
 if(action==='share-result')return share(JSON.stringify(result,null,2));
 if(action==='save-note'){const t=val('journal-text').trim();if(t){save('Journal reflection',t);paint()}else alert('Write something first.');return}
 if(action==='play')return play();
 if(action==='stop')return stop();
});
document.addEventListener('input',e=>{if(e.target.id==='spread-search'){query=e.target.value;const pos=e.target.selectionStart;paint();$('#spread-search')?.focus();$('#spread-search')?.setSelectionRange(pos,pos)}});
window.addEventListener('hashchange',()=>{const parts=location.hash.slice(1).split('/');if(parts[0]&&parts[0]!==page){page=parts[0];tool=parts[0]==='explore'?(parts[1]||null):null;paint()}});
window.addEventListener('beforeunload',stop);
async function start(){const parts=location.hash.slice(1).split('/');page=['home','spreads','learn','cosmos','explore','journal'].includes(parts[0])?parts[0]:'home';tool=parts[1]||null;paint();const all=await Promise.allSettled([request('/tarot/spreads'),request('/tarot/cards')]);if(all[0].status==='fulfilled')spreads=all[0].value.spreads||[];if(all[1].status==='fulfilled')cards=all[1].value.cards||[];paint()}
start();
