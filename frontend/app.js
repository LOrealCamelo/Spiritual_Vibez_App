/* Spiritual Vibez — illustrated responsive frontend. Uses the existing FastAPI API when available. */
'use strict';
const $=s=>document.querySelector(s);
const e=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const API='/api';
const signs=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const major=['The Fool','The Magician','The High Priestess','The Empress','The Emperor','The Hierophant','The Lovers','The Chariot','Strength','The Hermit','Wheel of Fortune','Justice','The Hanged Man','Death','Temperance','The Devil','The Tower','The Star','The Moon','The Sun','Judgement','The World'];
const meanings=['new beginnings, possibilities and an open mind','intentional action and creative resourcefulness','intuition, mystery and inner knowing','nurturing, growth and abundance','boundaries, stability and personal authority','tradition, teaching and values','alignment, choices and connection','determination, direction and momentum','courage, kindness and self-trust','reflection, solitude and wisdom','cycles, timing and changing circumstances','balance, fairness and accountability','a new perspective and patient surrender','endings that create room for renewal','moderation, patience and harmony','attachments, patterns and reclaiming choice','disruption, honesty and rebuilding','hope, renewal and inspiration','uncertainty, intuition and dreams','joy, clarity and confidence','awakening, evaluation and calling','completion, integration and wholeness'];
const icons=['🌱','✨','🌙','🌺','👑','📖','💞','🏇','🦁','🕯️','🎡','⚖️','🔄','🦋','🌈','🔗','⚡','⭐','🌘','🌞','📣','🌎'];
const suits=['Wands','Cups','Swords','Coins'];const ranks=['Ace','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Page','Knight','Queen','King'];
const sampleCards=[...major.map((name,id)=>({id,name,suit:'Major',upright:meanings[id],reversed:'an invitation to examine blocks around '+meanings[id],icon:icons[id],mantra:'I choose my own next step.'})),...suits.flatMap((s,si)=>ranks.map((r,ri)=>({id:22+si*14+ri,name:r+' of '+s,suit:s,icon:['🔥','💗','⚔️','🪙'][si],upright:(['creative energy and initiative','feelings and relationships','thoughts and communication','practical resources and everyday life'][si])+' viewed through '+r.toLowerCase()+' energy',reversed:'a chance to reassess '+s.toLowerCase()+' patterns',mantra:'I notice the choices available to me.'})))];
const mkSpread=(id,title,cat,qs,desc='A moment of reflection')=>({id,title,category:cat,cardCount:qs.length,desc,questions:qs.map((q,i)=>({slot:i+1,title:q,q}))});
const demoSpreads=[
 mkSpread('reset-energy','Reset Your Energy','wellbeing',['What is draining me?','What can I release?','What restores me?','One grounded next step']),
 mkSpread('trust-gut','Trust Your Gut','crossroads',['What do I already know?','What is clouding my intuition?','What deserves attention?','What can I set down?','What is my next step?']),
 mkSpread('next-phase','The Next Phase','purpose',['What am I outgrowing?','What is becoming possible?','What supports change?','What needs patience?','What is the hidden opportunity?','What direction feels aligned?']),
 mkSpread('grounding','Grounding','wellbeing',['What needs my attention?','Where can I slow down?','What is steady in my life?','What grounds my body?','What is one manageable action?']),
 mkSpread('daily-check','Your Daily Check-In','daily',['How am I arriving today?','What deserves care?','One intention']),
 mkSpread('love-language','Heart to Heart','love',['What do I need?','What do they need?','Where can we connect?','What conversation matters?']),
 mkSpread('shadow-light','Shadow & Light','shadow',['What am I avoiding?','What does it protect?','Where is my strength?','How can I respond gently?']),
 mkSpread('fresh-start','Fresh Start','purpose',['What is ending?','What is emerging?','What can I begin?']),
 mkSpread('career-clarity','Career Clarity','crossroads',['Where am I now?','What are my strengths?','What is limiting me?','Where is opportunity?','What is my next move?']),
 mkSpread('moon-mood','Moon Mood','spirit',['What is illuminated?','What is hidden?','What can I release?','What is my intention?']),
];
const menu=[['home','⌂','Home'],['spreads','⤨','Spreads'],['learn','▣','Learn Tarot'],['cosmos','☾','Cosmos'],['explore','✦','Explore'],['journal','▤','Journal']];
const tools={
 'Astrology & Cosmos':[['natal','🪐','Natal Birth Chart','Planetary placements and house themes'],['draconic','🐉','Draconic Chart','North Node-based symbolic placements'],['moon','🌙','Natal Moon Phase','The Moon phase at your birth'],['bazi','🐲','Chinese Zodiac & BaZi','Zodiac animal and four pillars'],['houses','🏘️','Astrology Houses','The meaning of all 12 houses'],['asteroids','☄️','Asteroids','Chiron, Juno, Vesta and more'],['astro','🌍','Astrocartography','Location and planetary lines'],['calendar','🗓️','13-Moon Calendar','An alternative calendar system']],
 'Numbers & Relationships':[['life','🔢','Life Path','Discover your life path number'],['numbers','✨','Learn Numerology','Numbers and master numbers'],['love','💖','Love Match','Zodiac compatibility']],
 'Wellness & Rituals':[['sound','🎶','Sound Frequencies','Listen to locally generated tones'],['rituals','🕯️','Ritual Finder','Find a ritual by intention'],['cycle','🌸','Moon & Period Tracker','Private, estimated cycle dates'],['shadow','📝','Shadow Work','Prompts and reflections']],
 'Divination & More':[['runes','ᚠ','Rune Casting','Three symbolic runes'],['pendulum','🔮','Pendulum','Reflective yes-or-no draw'],['oracle','💬','Mystic Companion','Rule-based responses, no paid AI'],['store','🛍️','Creator Store','Shop and offerings']]
};
const allTools=Object.values(tools).flat();
const state={page:'home',selected:null,drawn:{},reading:'',cards:sampleCards,spreads:demoSpreads,online:false,sign:'Scorpio',transit:null,category:'All',search:'',filter:'all',cardDetail:null,quiz:null,answer:'',tool:null,result:null,error:'',quizProgress:0,cycles:null};
const btn=(text,action,other='',extra='')=>'<button class="btn '+other+'" data-action="'+action+'" '+extra+'>'+text+'</button>';
const field=(label,id,type='text',value='',attrs='')=>'<label class="field">'+e(label)+'<input id="'+id+'" type="'+type+'" value="'+e(value)+'" '+attrs+'></label>';
const selector=(label,id,values,selected)=>'<label class="field">'+e(label)+'<select id="'+id+'">'+values.map(x=>'<option value="'+e(x)+'" '+(selected===x?'selected':'')+'>'+e(x)+'</option>').join('')+'</select></label>';
const chip=(text,action,active=false,attrs='')=>'<button class="chip '+(active?'active':'')+'" data-action="'+action+'" '+attrs+'>'+e(text)+'</button>';
const notice=(text,kind='')=>'<div class="note '+kind+'">'+e(text)+'</div>';
const heading=(h,desc)=>'<header class="page-head"><div class="kicker">SPIRITUAL VIBEZ · ZODIAC, TAROT & MORE ✦</div><h1 class="page-title">'+h+'</h1><p class="page-desc">'+desc+'</p></header>';
async function api(path,options){const r=await fetch(API+path,{...options,signal:AbortSignal.timeout(6000)});if(!r.ok)throw Error('API '+r.status);return r.json()}
const post=(path,data)=>api(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
function transition(page,sub=null){state.page=page;state.tool=sub;state.error='';state.result=null;window.location.hash=page+(sub?'/'+sub:'');render();window.scrollTo({top:0,behavior:'instant'});}
function home(){
 const feats=[['spreads','home_shuffle_spread.png','Tarot Spreads'],['learn','home_learn_tarot.png','Learn Tarot'],['daily','home_daily_card.png','Daily Card'],['journal','feature-journal.png','My Journal']];
 const fave=[['Reset Your Energy','me_reset_your_energy.png'],['Trust Your Gut','me_trustyourgut_hero.png'],['The Next Phase','me_the_next_phase.png'],['Grounding','grounding_ui_card.png']];
 const more=[['cosmos','ui_background.png','Cosmos'],['natal','home_birth_chart.png','Birth Chart'],['life','journal_numerology.png','Numerology'],['moon','journal_moon_phase.png','Moon Phase'],['rituals','journal_rituals.png','Rituals'],['journal','journal_saved_readings.png','Saved Readings']];
 return '<section class="home-hero" aria-label="Your illustrated spiritual home"><div class="hero-copy"><h1>Zero boring.</h1><p>Explore cards, learn tarot and discover something about yourself—your way.</p><div class="hero-actions">'+btn('🔀 Try a spread','nav:spreads')+btn('📚 Learn tarot','nav:learn','cream')+'</div></div><img class="hero-character" src="assets/cartoon_me_transparent3.png" alt="Illustrated tarot guide with headphones, tattoos and purple tarot cards."></section>'+
 '<div class="section-heading"><h2>Pick your adventure 💫</h2></div><div class="feature-grid">'+feats.map(([id,file,title])=>'<button class="picture-tile" data-action="'+(id==='daily'?'daily-card':'nav:'+id)+'" aria-label="Open '+title+'"><img src="assets/'+file+'" alt="'+title+'" loading="lazy"></button>').join('')+'</div>'+
 '<div class="section-heading"><h2>Fan-favorite spreads ♡</h2><a href="#spreads" data-action="nav:spreads">See all →</a></div><div class="favorite-grid">'+fave.map(([name,file])=>'<button class="favorite-card" data-action="favorite" data-name="'+e(name)+'" aria-label="Open '+e(name)+' spread"><img src="assets/'+file+'" alt="'+e(name)+' illustrated spread" loading="lazy"></button>').join('')+'</div>'+
 '<div class="section-heading"><h2>More to explore ✨</h2></div><div class="more-grid">'+more.map(([id,file,title])=>'<button class="extra-card" data-action="'+(id==='journal'?'nav:journal':id==='cosmos'?'nav:cosmos':'tool:'+id)+'" aria-label="Open '+title+'"><img src="assets/'+file+'" alt="'+title+'" loading="lazy">'+(id==='cosmos'?'<span class="extra-label">☾ Cosmos</span>':'')+'</button>').join('')+'</div><div class="scenic" aria-hidden="true"></div>';
}
function spreadsPage(){
 let out=heading(state.selected?e(state.selected.title)+' 🃏':'Tarot Spreads ✨',state.selected?'Tap each position to reveal a card and receive a combined reading.':'Find the right spread for your mood, question or moment. Tarot learning is a separate section.');
 if(state.selected){const s=state.selected,qs=s.questions||[];
  out+=btn('← All spreads','back-spreads','cream')+'<div class="reading-board"><h3>✦ '+e(s.title)+' ✦</h3><div class="slots">'+qs.map(q=>{const d=state.drawn[q.slot];return '<button class="slot '+(d?'opened':'')+'" data-action="draw" data-slot="'+q.slot+'" aria-label="'+(d?'Revealed ':'Reveal ')+e(q.title)+'" '+(d?'disabled':'')+'><span>'+e(d?d.card.icon||'🃏':'☀')+'</span><strong>'+e(d?d.card.name:'CARD '+q.slot)+'</strong><small>'+e(d?d.card.orientation:'TAP TO REVEAL')+'</small></button>'}).join('')+'</div></div>';
  out+='<div class="list" style="margin-bottom:15px">'+qs.map(q=>'<div class="glass"><b>'+q.slot+'. '+e(q.title)+'</b><p>'+e(q.q)+'</p>'+(state.drawn[q.slot]?'<p><b>'+e(state.drawn[q.slot].card.name)+' ('+e(state.drawn[q.slot].card.orientation)+')</b><br>'+e(state.drawn[q.slot].card.meaning)+'</p>':'')+'</div>').join('')+'</div>';
  out+=notice('Readings are for self-reflection, not certain predictions.');
  out+=btn('✨ Interpret all my cards','interpret','',Object.keys(state.drawn).length===qs.length?'':'disabled')+' '+btn('🔀 Start again','reset-spread','cream');
  if(state.reading)out+='<div class="glass"><h3>💗 Your combined reading</h3><p>'+e(state.reading)+'</p>'+btn('Share this reading','share-reading')+' '+btn('Save to journal','save-reading','cream')+'</div>';
  return out;
 }
 const cats=['All',...new Set(state.spreads.map(x=>x.category))];
 out+='<div class="glass"><label class="field">Search spreads<input id="spread-search" value="'+e(state.search)+'" placeholder="Try love, clarity, career, shadow..."></label><div class="chips">'+cats.map(c=>chip(c,'category',state.category===c,'data-category="'+e(c)+'"')).join('')+'</div>'+(state.online?'':notice('Preview mode: built-in sample spreads are active. Connect the existing backend for the full spread library.'))+'</div>';
 const matches=state.spreads.filter(s=>(state.category==='All'||s.category===state.category)&&s.title.toLowerCase().includes(state.search.toLowerCase()));
 out+='<div class="list">'+matches.map((s,i)=>'<button class="listbutton" data-action="select-spread" data-id="'+e(s.id)+'"><span class="glyph">'+['🔮','💫','🦋','💞','🌙','✨'][i%6]+'</span><span><strong>'+e(s.title)+'</strong><small>'+s.cardCount+' cards · '+e(s.category)+'</small><small>'+e(s.desc||'Your reflective reading')+'</small></span></button>').join('')+'</div>';
 return out;
}
function learningPage(){
 let out=heading('Learn Tarot 📚','Learn every card upright and reversed. A dedicated academy, completely separate from the spread randomizer.');
 out+='<div class="glass"><h3>📚 Your learning journey</h3><p>Major Arcana (22 cards), Minor Arcana (56 cards), reversals, card meanings and an interactive quiz.</p><p><b>'+state.quizProgress+' quiz answers attempted this session</b></p>'+btn('🎯 Quiz me','quiz')+'</div>';
 if(state.quiz){const q=state.quiz;out+='<div class="glass"><h3>🎯 What does '+e(q.card_name)+' represent?</h3><div class="chips">'+q.options.map(x=>chip(x,'quiz-answer',false,'data-answer="'+e(x)+'"')).join('')+'</div>'+(state.answer?notice(state.answer,state.answer.startsWith('Correct')?'ok':''):'')+'</div>'}
 if(state.cardDetail){const c=state.cardDetail;out+='<div class="glass" id="selected-card"><h3>'+e(c.icon)+' '+e(c.name)+'</h3><p><strong>Upright:</strong> '+e(c.description_upright||c.upright)+'</p><p><strong>Reversed:</strong> '+e(c.description_reversed||c.reversed)+'</p><p><strong>Mantra:</strong> '+e(c.mantra||'Reflect on what resonates.')+'</p>'+btn('Close card','close-card','cream')+'</div>'}
 out+='<div class="chips">'+['all','Major','Wands','Cups','Swords','Coins'].map(f=>chip(f==='all'?'All 78':f,'learn-filter',state.filter===f,'data-filter="'+f+'"')).join('')+'</div><div class="deck-cards">'+state.cards.filter(c=>state.filter==='all'||c.suit===state.filter).map(c=>'<button class="deck-card" data-action="card" data-card="'+c.id+'"><span class="symbol">'+e(c.icon||'🃏')+'</span>'+e(c.name)+'<small>'+e(c.suit)+'</small></button>').join('')+'</div>';
 return out;
}
function cosmosPage(){const d=state.transit;
 let out=heading('Cosmos & Transits 🌙','Moon phase, Sun position, Mercury and Venus—plus a zodiac-inspired mood forecast.');
 out+='<div class="glass"><h3>✨ Daily Moon & Planetary Alignment</h3><div class="controls">'+selector('Your zodiac sign','transit-sign',signs,state.sign)+btn('Refresh my cosmic weather','get-transit')+'</div>'+(state.online?'':notice('A working backend connection is required for planetary calculations. No fake positions will be shown.'))+'</div>';
 if(d){out+='<div class="tiles">'+[['🌙','Moon',d.moon_phase],['☀️','Sun',d.sun_position],['☿','Mercury',d.mercury_status],['♀','Venus',d.venus_status]].map(([i,n,v])=>'<div class="glass"><h3>'+i+' '+n+'</h3><p>'+e(v)+'</p></div>').join('')+'</div><div class="glass"><h3>💖 Your '+e(state.sign)+' mood forecast</h3><p>'+e(d.forecast?.content)+'</p><small>Astrology is symbolic; it does not scientifically predict mood.</small><p>'+btn('Share forecast','share-transit')+'</p></div>'}
 out+='<div class="glass"><h3>🌒 More astrology tools</h3><p>Natal moon phase, natal and draconic charts, Chinese zodiac, houses and astrocartography all have dedicated screens.</p>'+btn('Open astrology tools','nav:explore','cream')+'</div>';return out;
}
function getTool(id){return allTools.find(t=>t[0]===id)}
function explorePage(){
 if(!state.tool)return heading('Explore More ✨','Every part of your spiritual playground gets its own space.')+Object.entries(tools).map(([name,items])=>'<section class="tool-group"><h2>'+e(name)+'</h2><div class="tiles">'+items.map(([id,ico,title,detail])=>'<button class="tooltile" data-action="tool:'+id+'"><span class="emoji">'+ico+'</span><strong>'+e(title)+'</strong><span>'+e(detail)+'</span></button>').join('')+'</div></section>').join('');
 const t=getTool(state.tool);if(!t)return '';const [id,ico,title,detail]=t;
 let out=btn('← All features','tool-back','cream')+heading(ico+' '+e(title),e(detail));
 const birth=['moon','natal','draconic','bazi','life'].includes(id);
 let form='';if(birth)form+='<div class="controls">'+field('Birth date','birth-date','date')+(id==='life'?'':field('Birth time (local)','birth-time','time','12:00'))+'</div>';
 if(['natal','draconic'].includes(id))form+='<div class="controls">'+field('Birth latitude','birth-lat','number','43.1009','step="any"')+field('Birth longitude','birth-lon','number','-75.2327','step="any"')+'</div>'+notice('Your current backend uses approximate formulas and does not correctly resolve birth time zones. Chart accuracy must be repaired before production.');
 if(id==='astro')form+=field('Destination city','city','text','Utica, NY');
 if(id==='love')form+='<div class="controls">'+selector('Your zodiac sign','sign-a',signs,'Scorpio')+selector('Their zodiac sign','sign-b',signs,'Taurus')+'</div>';
 if(id==='rituals')form+='<div class="controls">'+field('Search intentions','search','search')+selector('Category','ritual-category',['all','money','love','protection'],'all')+'</div>';
 if(id==='oracle'||id==='pendulum')form+=field('Your question','search','text');
 if(id==='cycle')form+='<div class="controls">'+field('First day of last period','period-date','date')+field('Average cycle length','period-length','number','28','min="20" max="45"')+'</div>'+notice('This preview stores period information locally only. Cycle predictions are rough estimates and cannot establish fertility or safe contraception days.');
 if(id==='sound')form+='<div class="controls">'+selector('Choose tone (Hz)','hz',['174','285','396','417','432','528','639','741','852','963'],'528')+field('Volume (0–0.1)','volume','number','0.04','step="0.01" min="0" max="0.1"')+'</div>'+btn('▶ Play tone','audio-play')+' '+btn('■ Stop tone','audio-stop','cream')+notice('These are original synthesized tones, not copyrighted recordings. Use a comfortable volume; no medical treatment claims.');
 if(id==='shadow')form+=notice('Journal reflections are saved locally in the Journal tab; public server-side storage is disabled until authentication is built.');
 if(id==='oracle')form+=notice('Rule-based interpretations require no paid AI API. The backend is not a large language model.');
 out+='<div class="glass"><h3>'+ico+' '+e(title)+'</h3>'+form+(id==='sound'?'':btn(id==='rituals'?'Find rituals ✨':'Explore / Calculate ✨','tool-run'))+(state.error?notice(state.error,'error'):'')+'</div>'+(state.result?renderResult(state.result):'');
 return out;
}
function renderResult(o){let s='';if(o.oracle_response)s='<p>'+e(o.oracle_response).replace(/\n/g,'<br>')+'</p>';
 else if(o.placements)s='<p><b>Ascendant:</b> '+e(o.ascendant)+'</p>'+o.placements.map(x=>'<p><b>'+e(x.planet)+'</b> · '+e(x.sign)+' · '+e(x.house)+'</p>').join('');
 else if(o.natal_moon_phase)s='<h3>'+e(o.natal_moon_phase)+'</h3><p>'+e(o.description)+'</p>';
 else if(o.life_path_number)s='<h3>Life Path '+e(o.life_path_number)+'</h3><p>'+e(o.description)+'</p>';
 else if(o.lessons)s=o.lessons.map(x=>'<p><b>'+e(x.number)+' · '+e(x.title)+'</b><br>'+e(x.lesson)+'</p>').join('');
 else if(o.rituals)s=o.rituals.map(x=>'<p><b>🕯️ '+e(x.title)+'</b><br>'+e(x.tools||'')+'<br>'+e(x.steps||'')+'</p>').join('');
 else if(o.houses)s=o.houses.map(x=>'<p><b>'+e(x.name||x.title||'House')+'</b><br>'+e(x.desc||x.meaning||x.description||'')+'</p>').join('');
 else if(o.cycle_day)s='<p>Cycle day '+e(o.cycle_day)+'</p><p>Next estimated period: '+e(o.next_period)+'</p>';
 else s='<pre>'+e(JSON.stringify(o,null,2))+'</pre>';
 return '<div class="result"><h3>✨ Your '+e(getTool(state.tool)?.[2]||'cosmic')+' result</h3>'+s+'<p>'+btn('Share result','share-result','cream')+'</p></div>';
}
function journalPage(){let saved=[];try{saved=JSON.parse(localStorage.getItem('sv_private_journal')||'[]')}catch{}
 return heading('My Journal 💗','Save your reflections and readings on this device—not in an unprotected public database.')+'<div class="tiles"><div class="glass"><h3>📓 Today’s reflection</h3><label class="field">Your thoughts<textarea id="journal-text" placeholder="What came up for you today?"></textarea></label><p>'+btn('Save reflection','save-note')+'</p></div><div class="glass"><h3>💌 Saved reflections</h3>'+(saved.length?saved.slice().reverse().map(x=>'<p><b>'+e(x.title)+'</b> <small> · '+e(x.date)+'</small><br>'+e(x.text)+'</p>').join(''):notice('No saved reflections yet.'))+'</div></div>'+notice('Local storage is device-specific. Do not enter private information on a shared device.');
}
function dailyCard(){if(state.cards.length){const card=state.cards[Math.floor(Math.random()*state.cards.length)];state.cardDetail=card;transition('learn');document.querySelector('#selected-card')?.scrollIntoView({behavior:'smooth'});}}
function render(){
 const nav=menu.map(([id,icon,label])=>'<button class="'+(state.page===id?'selected':'')+'" data-action="nav:'+id+'"><span class="navicon">'+icon+'</span>'+label+'</button>').join('');
 const dock=menu.map(([id,icon,label])=>'<button class="'+(state.page===id?'current':'')+'" data-action="nav:'+id+'"><span>'+icon+'</span>'+label+'</button>').join('');
 const pageContent={home,spreads:spreadsPage,learn:learningPage,cosmos:cosmosPage,explore:explorePage,journal:journalPage}[state.page]||home;
 $('#app').innerHTML='<header class="topbar"><div class="topbar__inner"><a href="#home" class="brand" aria-label="Spiritual Vibez Home"><span class="brand__moon">☾</span><span class="brand__text"><strong>Spiritual Vibez</strong><small>ZODIAC, TAROT & MORE</small></span><span class="brand__cards">🃏</span></a><nav class="nav" aria-label="Primary">'+nav+'</nav><div class="top-actions"><button aria-label="Find a feature" data-action="nav:explore">⌕</button><button class="avatar-chip" aria-label="Open journal" data-action="nav:journal">💖</button></div></div></header><main class="container '+(state.page==='home'?'':'main-page')+'">'+pageContent()+'</main><footer class="footer">Spiritual Vibez · Zodiac, Tarot & More · For reflection and entertainment, not medical or financial advice.</footer><nav class="bottomdock" aria-label="Mobile navigation">'+dock+'</nav>';
}
function val(id){return document.getElementById(id)?.value??''}
function save(title,text){let arr=[];try{arr=JSON.parse(localStorage.getItem('sv_private_journal')||'[]')}catch{}arr.push({title,text,date:new Date().toLocaleDateString()});localStorage.setItem('sv_private_journal',JSON.stringify(arr.slice(-100)));}
function share(text){if(navigator.share){navigator.share({title:'Spiritual Vibez',text}).catch(()=>{});}else if(navigator.clipboard){navigator.clipboard.writeText(text).then(()=>alert('Copied! Paste it into a text, email, or social post.')).catch(()=>prompt('Copy this:',text));}else prompt('Copy this:',text)}
let ac=null,osc=null;function stopAudio(){try{osc?.stop();ac?.close()}catch{}osc=null;ac=null}
function startAudio(){stopAudio();try{ac=new (window.AudioContext||window.webkitAudioContext)();osc=ac.createOscillator();const gain=ac.createGain();osc.type='sine';osc.frequency.value=Number(val('hz'))||528;gain.gain.value=Math.max(0,Math.min(.10,Number(val('volume'))||.04));osc.connect(gain);gain.connect(ac.destination);osc.start()}catch(ex){alert('Audio could not start: '+ex.message)}}
function pickSpread(s){state.selected=s;state.drawn={};state.reading='';transition('spreads')}
async function draw(slot){if(state.drawn[slot])return;let card;try{if(!state.online)throw Error('offline');const d=await post('/tarot/spreads/deal-slot',{spread_id:state.selected.id,slot_num:slot,exclude_card_ids:Object.values(state.drawn).map(x=>x.card.id)});state.drawn[slot]=d;}catch{const available=state.cards.filter(c=>!Object.values(state.drawn).some(x=>x.card.id===c.id));card=available[Math.floor(Math.random()*available.length)];const reversed=Math.random()<.2;state.drawn[slot]={slot,card:{...card,orientation:reversed?'Reversed':'Upright',meaning:reversed?card.reversed:card.upright}};}render()}
async function interpret(){try{if(!state.online)throw Error('offline');const d=await post('/tarot/spreads/synthesize',{spread_id:state.selected.id,drawn_cards:Object.values(state.drawn).map(x=>({slot:x.slot,card_id:x.card.id,orientation:x.card.orientation})),save_to_journal:false});state.reading=d.synthesis||'';}catch{const names=Object.values(state.drawn).map(x=>x.card.name);const themes=Object.values(state.drawn).slice(0,3).map(x=>x.card.meaning);state.reading='This '+state.selected.title+' reading moves through '+names.join(', ')+'. Together, these cards invite you to consider '+themes.join('; ')+'. Notice which position resonates with your situation, and choose one practical action that supports your intentions. These are reflective prompts, not predictions.';}render()}
function fallbackLifePath(year,month,day){let num=(v)=>{let x=v;while(x>9&&![11,22,33].includes(x))x=String(x).split('').reduce((a,b)=>a+Number(b),0);return x};return num(num(year)+num(month)+num(day))}
async function runTool(){const id=state.tool, dob=val('birth-date'),birthTime=val('birth-time')||'12:00',[y,m,d]=(dob||'').split('-').map(Number);state.error='';state.result=null;
 if(['natal','draconic','moon','bazi','life'].includes(id)&&(!dob||Number.isNaN(Date.parse(dob)))){state.error='Please enter a valid birth date.';render();return}
 if(id==='cycle'){const last=val('period-date');if(!last){state.error='Please enter your last period start date.';render();return}const length=Number(val('period-length'));if(length<20||length>45){state.error='Cycle length must be between 20 and 45 days.';render();return}const days=Math.floor((new Date().getTime()-new Date(last+'T12:00:00').getTime())/86400000);const step=Math.max(0,days);const next=new Date(last+'T12:00:00');next.setDate(next.getDate()+(Math.floor(step/length)+1)*length);state.result={cycle_day:step%length+1,next_period:next.toLocaleDateString(),note:'Estimates only; not a diagnosis or fertility tool.'};render();return}
 if(id==='shadow'){state.result={suggestions:['What is one boundary I need today?','Where could I show myself compassion?','What belief am I ready to question?','What might restore my energy?']};render();return}
 if(!state.online&&id==='life'){const n=fallbackLifePath(y,m,d);state.result={life_path_number:n,description:'Life Path '+n+' is a numerology symbol for reflection. The full interpretation library loads when the backend is connected.'};render();return}
 if(!state.online){state.error='This feature needs the connected Spiritual Vibez backend. The interactive web design is working, but precise data is not available in the standalone preview.';render();return}
 const routes={moon:()=>post('/astrology/moon-phase',{birth_date:dob,birth_time:birthTime}),natal:()=>post('/astrology/natal-chart',{birth_date:dob,birth_time:birthTime,chart_system:'placidus',latitude:Number(val('birth-lat')),longitude:Number(val('birth-lon'))}),draconic:()=>post('/astrology/natal-chart',{birth_date:dob,birth_time:birthTime,chart_system:'draconic',latitude:Number(val('birth-lat')),longitude:Number(val('birth-lon'))}),bazi:()=>post('/astrology/bazi',{birth_year:y,birth_month:m,birth_day:d,birth_hour:Number(birthTime.slice(0,2))}),houses:()=>api('/astrology/houses'),asteroids:()=>api('/astrology/asteroids'),calendar:()=>api('/astrology/lunar-calendar/1'),astro:()=>api('/astrology/astrocartography?city='+encodeURIComponent(val('city'))),life:()=>post('/synastry/life-path',{birth_year:y,birth_month:m,birth_day:d}),numbers:()=>api('/synastry/numerology-lessons'),love:()=>post('/synastry/compatibility',{partner_a_sign:val('sign-a'),partner_b_sign:val('sign-b')}),rituals:()=>api('/rituals/search?category='+encodeURIComponent(val('ritual-category'))+'&query='+encodeURIComponent(val('search'))),runes:()=>post('/divination/runes/cast',{rune_count:3}),pendulum:()=>post('/divination/pendulum',{question:val('search')||'What matters next?'}),oracle:()=>post('/oracle/chat',{message:val('search')||'What is a useful reflection today?'}),store:()=>api('/store/products')};
 try{state.result=await routes[id]()}catch(ex){state.error=ex.message}render();}
function quizFallback(){const c=state.cards[Math.floor(Math.random()*state.cards.length)];const good=c.upright.split(',')[0].trim();state.quiz={card_name:c.name,correct_answer:good,options:[good,'Stagnation','Certainty','Avoidance'].sort(()=>Math.random()-.5)};}
async function askQuiz(){state.answer='';try{if(!state.online)throw Error('offline');state.quiz=await api('/tarot/study/quiz')}catch{quizFallback()}render()}
async function transitFetch(){state.sign=val('transit-sign');try{state.transit=await api('/astrology/daily-transits?sign='+encodeURIComponent(state.sign));}catch{state.transit=null;alert('Connect the FastAPI backend for actual planetary data. No invented transits will be displayed.')}render()}
document.addEventListener('click',async ev=>{const b=ev.target.closest('[data-action]');if(!b)return;ev.preventDefault();const a=b.dataset.action;if(a.startsWith('nav:'))return transition(a.slice(4));if(a.startsWith('tool:'))return transition('explore',a.slice(5));
 if(a==='favorite'){const s=state.spreads.find(x=>x.title.toLowerCase()===b.dataset.name.toLowerCase());if(s)pickSpread(s);else{transition('spreads');alert('Please choose an available spread from the complete list.')}return}
 if(a==='daily-card'){return dailyCard()}
 if(a==='back-spreads'){state.selected=null;state.drawn={};return render()}
 if(a==='select-spread'){return pickSpread(state.spreads.find(x=>x.id===b.dataset.id))}
 if(a==='category'){state.category=b.dataset.category;return render()}
 if(a==='draw'){return draw(Number(b.dataset.slot))}
 if(a==='interpret'){return interpret()}
 if(a==='reset-spread'){state.drawn={};state.reading='';return render()}
 if(a==='share-reading')return share(state.selected.title+'\n\n'+state.reading);
 if(a==='save-reading'){save(state.selected.title,state.reading);return alert('Saved to the Journal on this device.');}
 if(a==='learn-filter'){state.filter=b.dataset.filter;return render()}
 if(a==='card'){state.cardDetail=state.cards.find(x=>String(x.id)===b.dataset.card);render();document.querySelector('#selected-card')?.scrollIntoView({behavior:'smooth',block:'start'});return}
 if(a==='close-card'){state.cardDetail=null;return render()}
 if(a==='quiz'){return askQuiz()}
 if(a==='quiz-answer'){state.answer=b.dataset.answer===state.quiz.correct_answer?'Correct! ✨ You got it!':'Keep learning! The answer is '+state.quiz.correct_answer;state.quizProgress++;return render()}
 if(a==='get-transit')return transitFetch()
 if(a==='share-transit')return share(state.sign+': '+state.transit.forecast?.content)
 if(a==='tool-back')return transition('explore')
 if(a==='tool-run')return runTool()
 if(a==='share-result')return share(JSON.stringify(state.result,null,2))
 if(a==='save-note'){const t=val('journal-text').trim();if(!t)return alert('Write your reflection first.');save('Journal reflection',t);return render()}
 if(a==='audio-play')return startAudio();if(a==='audio-stop')return stopAudio();});
document.addEventListener('input',ev=>{if(ev.target.id==='spread-search'){state.search=ev.target.value;const pos=ev.target.selectionStart;render();const inp=$('#spread-search');inp?.focus();inp?.setSelectionRange(pos,pos)}});
window.addEventListener('hashchange',()=>{const [p,sub]=decodeURIComponent(location.hash.slice(1)).split('/');if(['home','spreads','learn','cosmos','explore','journal'].includes(p)&&(p!==state.page||sub!==state.tool)){state.page=p;state.tool=p==='explore'?sub||null:null;render()}});
window.addEventListener('beforeunload',stopAudio);
async function boot(){const [p,sub]=location.hash.slice(1).split('/');if(['home','spreads','learn','cosmos','explore','journal'].includes(p)){state.page=p;state.tool=p==='explore'?sub||null:null}render();try{const data=await Promise.all([api('/tarot/cards'),api('/tarot/spreads')]);if(data[0].cards?.length===78&&data[1].spreads?.length){state.cards=data[0].cards;state.spreads=data[1].spreads;state.online=true}}catch{/* Local preview fallback is intentionally usable. */}render()}
boot();