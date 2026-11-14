/* Interactive rune cloth — no external physics or audio dependencies. */
(function(root){
'use strict';
const DATA=root.SpiritualRuneLibrary;
if(!DATA)return;
let layout='three',reversals=false,sound=true,motion=false,intention='',result=null,pieces=[],frame=0,generation=0,shaking=false,audioCtx=null,lastClack=0,motionCount=0,motionLast=0,shakeTimer=null;
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const reduced=()=>!!root.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
function selectMarkup(){
 return Object.entries(DATA.LAYOUTS).map(([id,o])=>'<button type="button" data-action="rune-layout" data-layout="'+id+'" class="rune-mode'+(layout===id?' selected':'')+'" aria-pressed="'+(layout===id?'true':'false')+'">'+escape(o.title)+'<small>'+o.count+' runes</small></button>').join('');
}
function markup(){
 const count=DATA.LAYOUTS[layout].count;
 return '<section class="rune-sanctuary" aria-label="Rune Casting Sanctuary">'+
 '<header class="rune-heading"><div class="rune-kicker">✦ SpiritualVibz · A contemporary reflective practice</div><h2>Cast the Runes</h2><p>Gather a handful of carved rune bones, give them a gentle shake, and release them onto the cloth. Each cast invites a question—not a fixed prediction.</p></header>'+
 '<h3>Choose your reading</h3><div class="rune-modes">'+selectMarkup()+'</div>'+
 '<label class="rune-question" for="rune-intention">Your question or intention <span>(optional)</span><input id="rune-intention" maxlength="250" placeholder="What would be helpful to understand today?" value="'+escape(intention)+'"></label>'+
 '<div class="rune-settings"><label><input type="checkbox" id="rune-reversals" '+(reversals?'checked':'')+'> Include modern reversed meanings</label><label><input type="checkbox" id="rune-sound" '+(sound?'checked':'')+'> Soft bone-clack sounds</label></div>'+
 '<p class="rune-help">For a tactile cast, press and hold the pouch, wiggle or shake gently, then release. You can also tap <strong>Cast '+count+' Runes</strong> instead. The scatter uses '+count+' unique runes. Face-down pieces are not read.</p>'+
 '<div class="rune-cloth" id="rune-cloth" aria-label="Circular casting cloth where rune bones settle">'+
 '<div class="rune-cloth-ring"></div><div class="rune-cloth-center">✦</div><div class="rune-stones" id="rune-stones"></div>'+
 '<div class="rune-hand" id="rune-hand" role="button" tabindex="0" aria-label="Hold to rattle rune bones, then release to cast"><span class="rune-hand-mark" aria-hidden="true">✦ ᚠ ᚹ ✦</span><span class="rune-hand-label">Hold to gather & rattle</span></div>'+
 '</div><p id="rune-status" class="rune-status" aria-live="polite">Your rune bones are ready.</p>'+
 '<div class="rune-cast-controls"><button type="button" class="rune-cast-button" data-action="rune-cast">✦ Cast '+count+' Runes</button><button type="button" class="rune-secondary" data-action="rune-motion" id="rune-motion-btn">'+(motion?'Disable':'Enable')+' phone shake (optional)</button></div>'+
 '<p class="rune-minor">Sound and device motion are optional. Use the button for a silent, keyboard-accessible cast. If device sensors are unavailable, touch or tap still works.</p>'+
 '<div id="rune-results" class="rune-results" aria-live="polite"></div>'+
 '<details class="rune-history"><summary>About the history of these runes</summary><p>The 24 Elder Futhark symbols were used for writing in the early centuries CE, before the Viking-Age 16-rune Younger Futhark. Their old names are partly reconstructed. Drawing runes for readings, using reversed meanings, five-rune layouts and reading scattered bone positions are contemporary adaptations—not proven ancient Viking ceremonies. A blank “Odin rune” is not part of the historical 24-letter alphabet.</p><p>The meanings here are original, modern reflective prompts. No cast guarantees a future outcome.</p><p>Read more: <a target="_blank" rel="noopener noreferrer" href="https://nors.ku.dk/english/research/runes/">University of Copenhagen · Runology</a> and <a target="_blank" rel="noopener noreferrer" href="https://www.vikingeskibsmuseet.dk/en/professions/education/viking-age-people/runes">Viking Ship Museum · Runes</a>.</p></details>'+
 '</section>';
}
function clack(intensity=.25){
 if(!sound||intensity<.1)return;
 const now=performance.now();if(now-lastClack<90)return;lastClack=now;
 try{
  const Audio=root.AudioContext||root.webkitAudioContext;if(!Audio)return;
  if(!audioCtx)audioCtx=new Audio();
  if(audioCtx.state==='suspended')audioCtx.resume().catch(()=>{});
  const osc=audioCtx.createOscillator(),gain=audioCtx.createGain(),t=audioCtx.currentTime;
  osc.type='triangle';osc.frequency.setValueAtTime(750+Math.random()*480,t);
  osc.frequency.exponentialRampToValueAtTime(160,t+.065);
  const vol=Math.max(.001,Math.min(.036,intensity*.035));
  gain.gain.setValueAtTime(vol,t);gain.gain.exponentialRampToValueAtTime(.0001,t+.075);
  osc.connect(gain);gain.connect(audioCtx.destination);osc.start(t);osc.stop(t+.079);
 }catch{}
}
function vibrate(duration=10){try{root.navigator?.vibrate?.(duration)}catch{}}
function setStatus(s){const e=document.getElementById('rune-status');if(e)e.textContent=s;}
function updateView(){
 const stage=document.getElementById('rune-cloth');if(!stage)return;
 stage.classList.toggle('rattling',shaking);
}
function rattle(){
 if(!document.getElementById('rune-cloth'))return;
 shaking=true;updateView();setStatus('The rune bones are rattling in your hand…');clack(.45);vibrate(8);
}
function stopRattle(){shaking=false;updateView();}
function motionHandler(ev){
 if(!motion)return;
 const a=ev.acceleration||ev.accelerationIncludingGravity;if(!a)return;
 const intensity=Math.hypot(a.x||0,a.y||0,a.z||0);
 if(intensity<16)return;
 const now=performance.now();if(now-motionLast<130)return;motionLast=now;
 rattle();motionCount++;clearTimeout(shakeTimer);
 shakeTimer=setTimeout(()=>{if(motion&&shaking&&motionCount>=2)castRunes();motionCount=0;stopRattle()},600);
}
async function toggleMotion(){
 if(motion){motion=false;root.removeEventListener('devicemotion',motionHandler);clearTimeout(shakeTimer);stopRattle();setStatus('Phone shake is off. Touch casting is always available.');return;}
 try{
  if(typeof root.DeviceMotionEvent==='undefined'){setStatus('Motion sensors are unavailable here. Hold or tap to cast instead.');return}
  if(typeof root.DeviceMotionEvent.requestPermission==='function'){
   const permission=await root.DeviceMotionEvent.requestPermission();
   if(permission!=='granted'){setStatus('Motion permission was not granted. Touch casting is ready.');return}
  }
  motion=true;root.addEventListener('devicemotion',motionHandler);
  setStatus('Shake is enabled. Gently move your phone, or use the touch controls.');
 }catch{setStatus('Motion is unavailable on this device. Touch casting still works.')}
 const btn=document.getElementById('rune-motion-btn');if(btn)btn.textContent=(motion?'Disable':'Enable')+' phone shake (optional)';
}
function spawn(){
 const rootEl=document.getElementById('rune-cloth'),wrap=document.getElementById('rune-stones');if(!rootEl||!wrap)return false;
 const width=rootEl.clientWidth,height=rootEl.clientHeight;
 const cx=width/2,cy=height/2;wrap.textContent='';
 pieces.forEach((piece,i)=>{
  const el=document.createElement('button');el.type='button';el.className='rune-bone '+(piece.faceUp?'face-up':'face-down');
  el.setAttribute('aria-label',piece.faceUp?'Explore '+piece.rune.name:'A face-down rune, not read');el.setAttribute('data-rune-index',String(i));
  el.innerHTML='<span class="rune-bone-glyph" aria-hidden="true">'+(piece.faceUp?escape(piece.rune.symbol):'✦')+'</span>';
  piece.el=el;piece.x=cx+(Math.random()-.5)*36;piece.y=height+25+(Math.random()-.5)*12;
  const angle=(Math.random()-.5)*.8,speed=.8+Math.random()*.45;
  piece.vx=(Math.random()-.5)*11*speed+Math.sin(angle)*6;
  piece.vy=(-10.8-Math.random()*4.0)*speed;piece.a=Math.random()*Math.PI*2;piece.va=(Math.random()-.5)*.35;
  wrap.append(el);
 });
 return true;
}
function place(piece){
 if(!piece.el)return;
 piece.el.style.transform='translate3d('+piece.x.toFixed(1)+'px,'+piece.y.toFixed(1)+'px,0) translate(-50%,-50%) rotate('+piece.a.toFixed(3)+'rad)';
}
function applyPhysics(gen,start){
 if(gen!==generation||!document.getElementById('rune-stones'))return;
 const parent=document.getElementById('rune-cloth'),w=parent.clientWidth,h=parent.clientHeight;
 let moving=0;const radius=27,margin=34;
 for(const p of pieces){
  p.x+=p.vx;p.y+=p.vy;p.a+=p.va;
  if(p.x<margin||p.x>w-margin){p.x=Math.max(margin,Math.min(w-margin,p.x));p.vx*=-.27;clack(Math.abs(p.vx)/7)}
  if(p.y<margin||p.y>h-margin){p.y=Math.max(margin,Math.min(h-margin,p.y));p.vy*=-.26;clack(Math.abs(p.vy)/7)}
  p.vx*=.958;p.vy*=.958;p.va*=.939;
 }
 for(let i=0;i<pieces.length;i++)for(let j=i+1;j<pieces.length;j++){
  const a=pieces[i],b=pieces[j],dx=b.x-a.x,dy=b.y-a.y,dist=Math.hypot(dx,dy)||1;
  if(dist<radius*2){const nx=dx/dist,ny=dy/dist,overlap=(radius*2-dist)*.5;
   a.x-=nx*overlap;a.y-=ny*overlap;b.x+=nx*overlap;b.y+=ny*overlap;
   const rvx=a.vx-b.vx,rvy=a.vy-b.vy,impact=Math.abs(rvx*nx+rvy*ny);
   if(impact>.3){a.vx-=nx*impact*.16;a.vy-=ny*impact*.16;b.vx+=nx*impact*.16;b.vy+=ny*impact*.16;clack(Math.min(1,impact/9))}
  }
 }
 for(const p of pieces){place(p);if(Math.hypot(p.vx,p.vy)>.1||Math.abs(p.va)>.015)moving++}
 if((moving===0&&performance.now()-start>650)||performance.now()-start>2900){finish(gen);return}
 frame=root.requestAnimationFrame(()=>applyPhysics(gen,start));
}
function spatial(){
 const cloth=document.getElementById('rune-cloth');const w=cloth?.clientWidth||360,h=cloth?.clientHeight||380,cx=w/2,cy=h/2;
 const face=pieces.filter(p=>p.faceUp);
 face.forEach(p=>{
  const distance=Math.hypot((p.x-cx)/(w*.5),(p.y-cy)/(h*.5));
  p.zone=distance<.38?'near the center':distance>.84?'toward the outer edge':'between center and edge';
  p.neighbors=face.filter(n=>n!==p&&Math.hypot(n.x-p.x,n.y-p.y)<95).map(n=>n.rune.name);
 });
}
function finish(gen){
 if(gen!==generation)return;root.cancelAnimationFrame(frame);
 const cloth=document.getElementById('rune-cloth');if(cloth)cloth.classList.remove('casting');
 spatial();result={layout,intention,cast:pieces.map(p=>({rune:p.rune,faceUp:p.faceUp,zone:p.zone,neighbors:p.neighbors||[]}))};
 setStatus('The bones have settled. Tap any face-up rune to explore its meaning.');
 renderResult();
}
function castRunes(){
 const cloth=document.getElementById('rune-cloth');if(!cloth)return;
 stopRattle();generation++;root.cancelAnimationFrame(frame);result=null;
 const field=document.getElementById('rune-intention');if(field)intention=field.value.trim().slice(0,250);
 const selected=DATA.cast(layout,reversals);
 pieces=selected.map(r=>({rune:r,faceUp:layout==='handful'?Math.random()>.3:true}));
 if(pieces.every(p=>!p.faceUp))pieces[0].faceUp=true;
 const results=document.getElementById('rune-results');if(results)results.innerHTML='';
 document.querySelector('.complete-reading-share')?.remove();
 if(!spawn())return;
 setStatus('The bones are tumbling across the cloth…');
 cloth.classList.add('casting');clack(.55);vibrate(12);
 const id=generation,start=performance.now();
 if(reduced()){
  const w=cloth.clientWidth,h=cloth.clientHeight;
  pieces.forEach((p,i)=>{p.x=w*(.23+.54*((i%3)/2))+Math.random()*9;p.y=h*(.2+.63*(Math.floor(i/3)/2.5));p.a=(Math.random()-.5)*.8;p.vx=p.vy=p.va=0;place(p)});
  finish(id);
 }else frame=root.requestAnimationFrame(()=>applyPhysics(id,start));
}
function summaryLines(){
 if(!result)return '';
 const layoutInfo=DATA.LAYOUTS[result.layout];
 const lines=[layoutInfo.title,result.intention?'Question: '+result.intention:'Question: Open reflection'];
 result.cast.forEach((p,i)=>{
  if(!p.faceUp){lines.push('Bone '+(i+1)+': face-down (not interpreted)');return;}
  const r=p.rune;
  lines.push('Rune '+(i+1)+' · '+r.positionName+': '+r.symbol+' '+r.name+' ('+r.orientation+')'
   +'\nHistorical name association: '+r.historic
   +'\nModern themes: '+r.reading.keywords.join(', ')
   +'\nReflection: '+r.reading.meaning
   +(result.layout==='handful'?'\nCloth position: '+p.zone+(p.neighbors.length?'; near '+p.neighbors.join(', '):''):''));
 });
 lines.push('Closing reflection: Which theme feels useful today, and what one small, practical action can you take?');
 lines.push('This is a modern interpretation for reflection, not a prediction or a reconstruction of ancient ritual.');
 return lines.join('\n\n');
}
function renderResult(){
 const target=document.getElementById('rune-results');if(!target||!result)return;
 const layoutInfo=DATA.LAYOUTS[result.layout];
 const parts=result.cast.map((p,i)=>{
  if(!p.faceUp)return '<article class="rune-interpretation"><h4>Bone '+(i+1)+' · Face down</h4><p>This piece stays hidden and is not interpreted in this modern scatter style.</p></article>';
  const r=p.rune,meaning=r.reading;
  return '<article class="rune-interpretation" id="rune-reading-'+i+'"><div class="rune-interpretation-glyph">'+escape(r.symbol)+'</div><div><h4>'+escape(r.name)+' · '+escape(r.positionName)+'</h4><p class="rune-meta">'+escape(r.orientation==='reversed'?'Modern reversed reading':'Upright reading')+' · Historical name association: '+escape(r.historic)+'</p><p><strong>'+escape(meaning.keywords.join(' · '))+'</strong></p><p>'+escape(meaning.meaning)+'</p>'+(result.layout==='handful'?'<p class="rune-meta">On the cloth: '+escape(p.zone)+(p.neighbors.length?'; near '+escape(p.neighbors.join(', ')):'')+'</p>':'')+'</div></article>';
 }).join('');
 target.innerHTML='<div class="rune-result-head"><h3>✦ Your '+escape(layoutInfo.title)+' Reading</h3><p>'+escape(result.intention||'A moment of open reflection')+'</p></div>'+parts+
 '<div class="rune-conclusion"><strong>Your next step</strong><p>What theme resonates? What is one manageable action you can take? You decide what, if anything, this reading means for you.</p></div>';
 if(typeof root.installContentActions==='function')root.installContentActions();
}
function snapshot(){
 if(!result||!root.ContentFormat)return null;
 return root.ContentFormat.snapshot({title:'Rune Casting · '+DATA.LAYOUTS[result.layout].title,text:summaryLines(),route:'explore/runes'});
}
function showRune(index){
 if(!result)return;
 const item=result.cast[index];if(!item||!item.faceUp){setStatus('That piece landed face down, so it is not interpreted.');return;}
 document.getElementById('rune-reading-'+index)?.scrollIntoView({behavior:reduced()?'instant':'smooth',block:'nearest'});
}
function action(a,button){
 if(a==='rune-layout'){
  if(!DATA.LAYOUTS[button.dataset.layout])return;
  layout=button.dataset.layout;result=null;generation++;root.cancelAnimationFrame(frame);root.render();return;
 }
 if(a==='rune-cast'){castRunes();return;}
 if(a==='rune-motion'){toggleMotion();return;}
}
function sync(){
 const cloth=document.getElementById('rune-cloth');
 if(!cloth){generation++;root.cancelAnimationFrame(frame);if(motion){motion=false;root.removeEventListener('devicemotion',motionHandler)}return;}
 const inp=document.getElementById('rune-intention');
 inp?.addEventListener('input',()=>{intention=inp.value.slice(0,250)});
 const rev=document.getElementById('rune-reversals');
 rev?.addEventListener('change',()=>{reversals=rev.checked});
 const snd=document.getElementById('rune-sound');
 snd?.addEventListener('change',()=>{sound=snd.checked});
 const pad=document.getElementById('rune-hand');
 if(pad){
  let held=false;
  pad.addEventListener('pointerdown',e=>{held=true;pad.setPointerCapture?.(e.pointerId);rattle()});
  pad.addEventListener('pointermove',e=>{if(held&&Math.random()<.28)clack(.24)});
  pad.addEventListener('pointerup',()=>{if(held){held=false;castRunes()}});
  pad.addEventListener('pointercancel',()=>{held=false;stopRattle()});
  pad.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();castRunes()}});
 }
 document.getElementById('rune-stones')?.addEventListener('click',e=>{
  const t=e.target.closest?.('[data-rune-index]');if(t)showRune(Number(t.dataset.runeIndex));
 });
 if(result)renderResult();
}
root.RuneCasting={markup,action,sync,snapshot,summaryLines,getState:()=>({layout,reversals,sound,motion,intention,result,deckCount:DATA.RUNES.length})};
})(window);
