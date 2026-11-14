/* SpiritualVibz · Illustrated Ritual Library page
 * Original, modern reflection activities. Historical essays remain in research.
 */
(function(root){
 'use strict';
 const escape=(value)=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
 const assetRoot='assets/';
 const COLLECTION_TOPICS=[
  ['Rose-petal reflection baths','Writing a self-worth letter','Gentle gratitude rituals'],
  ['Moon phases and symbolism','Setting practical intentions','An evening reflection'],
  ['Recognizing repeated patterns','Self-compassion and boundaries','Release and reflection'],
  ['Seasonal stories and sources','Imbolc and Brigid: historical context','Modern nature appreciation'],
  ['Historical spirit imagery','Changing meanings across cultures','Distinguishing sources from theories'],
  ['Enheduanna and early records','Priestesses, healers and scholars','Women who preserved traditions']
 ];
 function cards(features){
  return features.map((f,i)=>{
   const x=i%3===0?'0%':i%3===1?'50%':'100%',y=i<3?'0%':'100%';
   const topics=(COLLECTION_TOPICS[i]||[]).map(t=>'<li>'+escape(t)+'</li>').join('');
   return '<details class="sv-ritual-card" data-collection="'+i+'">'+
    '<summary aria-label="Explore '+escape(f.title)+' collection">'+
     '<span class="sv-ritual-card-art" role="img" aria-label="Illustration for '+escape(f.title)+'" style="--sv-art-x:'+x+';--sv-art-y:'+y+'"></span>'+
     '<span class="sv-ritual-card-label"><span><strong>'+escape(f.title)+'</strong><small>'+escape(f.subtitle)+'</small></span><span class="sv-ritual-card-action" aria-hidden="true">Explore ＋</span></span>'+
    '</summary>'+
    '<div class="sv-ritual-card-inside"><span class="sv-ritual-label">✦ A practice you can try</span><h4>'+escape(f.practice)+'</h4><p>'+escape(f.body)+'</p><p class="sv-ritual-label">Explore these themes:</p><ul>'+topics+'</ul>'+
    (i===2?'<p>Want to explore a repeating pattern? <button type="button" class="sv-ritual-text-button" data-action="tool:shadow">Open the guided Shadow Work Journey</button></p>':'')+
    '<p class="sv-ritual-context">This is a modern reflection. Historical and living religious practices will be explained with their cultural context and sources.</p></div>'+
    '</details>';
  }).join('');
 }
 function bookmarks(){try{const v=JSON.parse(root.localStorage.getItem('sv_ritual_page_bookmarks')||'[]');return Array.isArray(v)?v:[]}catch{return []}}
 const countryFirst=(name)=>name.normalize('NFD').replace(/[\u0300-\u036f]/g,'')[0].toUpperCase();
 function directory(letter){
  const countries=Array.isArray(root.SV_RITUAL_COUNTRIES)?root.SV_RITUAL_COUNTRIES:[];
  const letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  const available=new Set(countries.map(countryFirst));
  const tabs=letters.map(v=>'<button type="button" data-action="ritual-letter" data-letter="'+v+'" aria-label="Browse countries beginning with '+v+'" aria-pressed="'+(letter===v?'true':'false')+'" class="sv-ritual-letter'+(letter===v?' is-current':'')+'" '+(!available.has(v)?'disabled':'')+'>'+v+'</button>').join('');
  const items=countries.filter(n=>countryFirst(n)===letter).map(n=>'<li class="sv-ritual-country"><span>'+escape(n)+'</span><small>Historical chapter being researched</small></li>').join('');
  return '<section class="sv-ritual-world" id="sv-ritual-world"><div class="sv-ritual-section-heading"><div><span class="sv-ritual-eyebrow">03 · Explore the globe</span><h2>Rituals Around the World — A–Z</h2></div><p>Browse 249 countries and territories. Future entries will distinguish documented traditions, women’s contributions, living religious customs and modern adaptations.</p></div>'+
   '<nav class="sv-ritual-letters" aria-label="Alphabetical country directory">'+tabs+'</nav>'+
   '<h3>'+escape(letter)+' · '+(items?String(countries.filter(n=>countryFirst(n)===letter).length)+' places':'No entries yet')+'</h3><ul class="sv-ritual-countries">'+items+'</ul>'+
   '<p class="sv-ritual-world-note">The directory is open for browsing; individual historical articles are not yet published. Indigenous nations, territories and diaspora traditions will receive their own researched entries rather than being folded into unrelated national histories.</p></section>';
 }
 function render({features=[],book=[],position=0,letter='A'}={}){
  const current=Math.max(0,Math.min(book.length-1,Number(position)||0)),chapter=book[current]||{title:'Reading preview',text:'The library is growing.'};
  const isSaved=bookmarks().includes(current),hasPrev=current>0,hasNext=current<book.length-1;
  return '<div class="sv-ritual-library" id="sv-ritual-library">'+
   '<header class="sv-ritual-hero" aria-label="Welcome to the Worldwide Ritual Library"><div class="sv-ritual-hero-shade"><span class="sv-ritual-eyebrow">✦ SpiritualVibz · Ancient wisdom & modern rituals ✦</span><h1>Discover the Ritual Library</h1><p>A beautiful home for meaningful practices, global spiritual histories and the women whose stories deserve to be remembered.</p><span class="sv-ritual-hero-prompt">Choose a collection below to begin</span></div></header>'+
   '<section class="sv-ritual-featured" id="sv-ritual-collections"><div class="sv-ritual-section-heading"><div><span class="sv-ritual-eyebrow">01 · Start exploring</span><h2>Featured Illustrated Collections</h2></div><p>Six doors into reflection, historical stories and spiritual traditions. Tap an illustration to see what is inside.</p></div><div class="sv-ritual-card-grid">'+cards(features)+'</div></section>'+
   '<section class="sv-ritual-bookshelf" id="sv-ritual-bookshelf"><div class="sv-ritual-section-heading"><div><span class="sv-ritual-eyebrow">02 · Pages worth lingering over</span><h2>Ancient Wisdom & Digital Bookshelf</h2></div><p>Step into a candlelit reading room. Explore the starter e-book today, and discover the manuscript and historical volumes being prepared.</p></div>'+
    '<div class="sv-ritual-bookshelf-stage"><div class="sv-ritual-bookshelf-art"><img src="'+assetRoot+'ritual-enchanted-bookshelf.webp" alt="Warm enchanted library with antique books, candles and a reading table" loading="lazy"><span>✦ Your mystical reading room</span></div>'+
    '<div class="sv-ritual-book-list"><div class="sv-ritual-book-option is-readable"><span class="sv-ritual-book-icon">📖</span><div><span class="sv-ritual-label">Available to read · 3-page introduction</span><h3>Rituals for Reflection</h3><p>A welcoming short guide to personal intention and mindful ritual.</p><button type="button" class="sv-ritual-book-open" data-action="ritual-reader-scroll">Open the sample book</button></div></div>'+
    '<div class="sv-ritual-book-option"><span class="sv-ritual-book-icon">📜</span><div><span class="sv-ritual-label">Special section planned</span><h3>The Voynich Manuscript</h3><p>A page-by-page illustrated reader, historical notes and community theories.</p></div></div>'+
    '<div class="sv-ritual-book-option"><span class="sv-ritual-book-icon">🌘</span><div><span class="sv-ritual-label">Volume being researched</span><h3>Demonology: Beyond Good & Evil</h3><p>Historical perspectives on protective figures, spirit lore and changing meanings.</p></div></div>'+
    '<div class="sv-ritual-book-option"><span class="sv-ritual-book-icon">👑</span><div><span class="sv-ritual-label">Stories in development</span><h3>Women in Spiritual History</h3><p>Documented lives and legacies across centuries and cultures.</p></div></div></div></div>'+
    '<div class="sv-ritual-reader" id="ritual-reader" aria-label="Rituals for Reflection e-book sample"><div class="sv-ritual-reader-top"><span class="sv-ritual-reader-bookmark">📖 Rituals for Reflection</span><span>Page '+(current+1)+' of '+book.length+'</span></div><div class="sv-ritual-progress"><span style="width:'+((current+1)/Math.max(1,book.length)*100)+'%"></span></div><div class="sv-ritual-reader-paper"><span class="sv-ritual-label">✦ A gentle place to start</span><h3>'+escape(chapter.title)+'</h3><p>'+escape(chapter.text)+'</p></div>'+
    '<div class="sv-ritual-reader-controls"><button type="button" data-action="ritual-book-prev" '+(hasPrev?'':'disabled')+'>← Previous page</button><button type="button" data-action="ritual-bookmark" aria-pressed="'+(isSaved?'true':'false')+'">'+(isSaved?'★ Page bookmarked':'☆ Bookmark page')+'</button><button type="button" data-action="ritual-page-journal">Save page to Journal</button><button type="button" data-action="ritual-book-next" '+(hasNext?'':'disabled')+'>Next page →</button></div><p class="sv-ritual-reader-note">Your bookmarks and Journal entries are kept in this browser. This is a short, original preview—not a completed historical volume.</p></div></section>'+
    directory(letter)+
    '<p class="sv-ritual-footer-note">✦ The featured reflections are contemporary personal practices. Historical books and worldwide research will be clearly sourced before publication. No community chat is active here yet.</p>'+
   '</div>';
 }
 root.SpiritualRitualLibrary={render,bookmarks};
})(window);