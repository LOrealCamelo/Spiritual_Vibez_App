const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');

function appContext() {
  const app = {innerHTML:''};
  const location = {hash:''};
  const context = vm.createContext({
    document:{querySelector:()=>app, addEventListener:()=>{}},
    window:{location, addEventListener:()=>{}, scrollTo:()=>{}},
    location, AbortSignal, fetch:async()=>{throw Error('Offline asset test')},
    localStorage:{getItem:()=>null},
  });
  vm.runInContext(fs.readFileSync(path.join(root,'artwork.js'),'utf8'), context);
  vm.runInContext(fs.readFileSync(path.join(root,'learning.js'),'utf8'), context);
  vm.runInContext(fs.readFileSync(path.join(root,'app.js'),'utf8'), context);
  return {context,app};
}

test('rendered images and CSS backgrounds resolve to real PNG uploads', () => {
  const {context} = appContext();
  const html = ['home()','spreadsPage()','learningPage()','journalPage()','explorePage()'].map(code=>vm.runInContext(code,context)).join('');
  const css = fs.readFileSync(path.join(root,'styles.css'),'utf8')+fs.readFileSync(path.join(root,'liquid-glass.css'),'utf8');
  const refs = [
    ...[...html.matchAll(/src="(assets\/[^"]+)"/g)].map(m=>m[1]),
    ...[...css.matchAll(/url\(["']?(assets\/[^)'"\s]+\.png)["']?\)/g)].map(m=>m[1]),
  ];
  assert.ok(refs.length >= 16,'Expected all home images and CSS backgrounds to be checked');
  for(const ref of refs){
    assert.match(ref,/\.png$/i,ref);
    const file=path.join(root,ref);
    assert.ok(fs.existsSync(file),`Missing uploaded image: ${ref}`);
    assert.equal(fs.readFileSync(file).subarray(0,8).toString('hex'),'89504e470d0a1a0a',`Not an actual PNG: ${ref}`);
  }
  for(const file of ['app.js','artwork.js','styles.css','index.html']){
    assert.doesNotMatch(fs.readFileSync(path.join(root,file),'utf8'),/\.webp\b/i,`Legacy image URL in ${file}`);
  }
});

test('Home uses one extended room scene and accessible HTML actions', () => {
  const {context} = appContext();
  const html=vm.runInContext('home()',context);
  assert.match(html,/home-room-scene/);
  assert.doesNotMatch(html,/hero-character|home-greeting|phone-welcome|me_hero2/);
  assert.match(html,/<h1>Your journey starts here<\/h1>/);
  for(const action of ['nav:spreads','daily-card','nav:journal','nav:cosmos','tool:natal','tool:rituals']){
    assert.ok(html.includes(`data-action="${action}"`),`Missing interactive action: ${action}`);
  }
});

test('display fonts are local licensed assets, so the reference typography works offline',()=>{
  const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
  for(const family of ['Pacifico','KaushanScript','DMSans','GreatVibes']){
    const font=family==='DMSans'?'DMSans-Variable.ttf':family+'-Regular.ttf';
    assert.ok(fs.statSync(path.join(root,'assets/fonts',font)).size>1000);
    assert.ok(fs.existsSync(path.join(root,'assets/fonts',family+'-OFL.txt')));
    assert.ok(css.includes(font));
  }
});

test('illustrated spread names retain the real backend IDs and card counts',()=>{
  const {context}=appContext();
  const catalog=JSON.parse(fs.readFileSync(path.join(root,'../backend/data/master_data.json'),'utf8')).masterSpreadsData;
  context.catalog=catalog;
  const normalized=vm.runInContext('normalizeSpreads(catalog)',context);
  for(const [name,id,count] of [['Trust Your Gut','trust-your-gut',5],['At a Crossroads','at-a-crossroads',10],['The Next Phase','stepping-into-new-timeline',6],['Grounding','mindfulness-calm',5]]){
    const spread=normalized.find(x=>x.title===name);
    assert.equal(spread?.id,id);assert.equal(spread?.cardCount,count);
  }
});

test('store has one external website link and no product catalog',()=>{
  const {context}=appContext();
  const html=vm.runInContext('state.tool="store";explorePage()',context);
  assert.equal((html.match(/href="https:\/\/neurospicymystic.com\/"/g)||[]).length,1);
  assert.ok(html.includes('Visit my store'));
  assert.ok(!html.includes('data-action="tool-run"'));
});


test('all 24 panels use fresh artwork and live text, with identical web/native definitions',()=>{
 const {context}=appContext();context.catalog=JSON.parse(fs.readFileSync(path.join(root,'../backend/data/master_data.json'),'utf8')).masterSpreadsData;
 vm.runInContext('state.spreads=normalizeSpreads(catalog)',context);
 const html=['home()','spreadsPage()','learningPage()','journalPage()'].map(code=>vm.runInContext(code,context)).join('');
 const panels=JSON.parse(fs.readFileSync(path.join(root,'../mobile/src/data/uiPanels.json'),'utf8'));
 assert.equal(Object.keys(panels).length,24);
 assert.equal(vm.runInContext('JSON.stringify(CARD_PANELS)',context),JSON.stringify(panels));
 for(const [key,p] of Object.entries(panels)){
  if(key.startsWith('home_'))continue;
  assert.ok(html.includes('data-panel="'+key+'"'),'Missing panel: '+key);
  assert.ok(html.includes(p.title.replace(/&/g,'&amp;').replace(/'/g,'&#39;')),'Missing live title: '+p.title);
  assert.ok(!html.includes('assets/'+key+'.png'),'Old cropped image remains: '+key);
 }
 for(const pack of ['cosmic','study','journal','ritual']){
  const name='illustrations/'+pack+'.png';const bytes=fs.readFileSync(path.join(root,'assets',name));
  assert.deepEqual(bytes,fs.readFileSync(path.join(root,'../mobile/assets',name)));
  assert.ok(bytes.readUInt32BE(16)>=1200&&bytes.readUInt32BE(20)>=1200,'Insufficient source resolution');
 }
 for(const vibe of ['All','Love','Career','Growth'])assert.ok(html.includes('aria-label="Filter by '+vibe+'"'));
 assert.doesNotMatch(vm.runInContext('state.tool=null;explorePage()',context),/Draconic/);
});

test('vibe filters include actual career and relationship spreads',()=>{
 const {context}=appContext();context.catalog=JSON.parse(fs.readFileSync(path.join(root,'../backend/data/master_data.json'),'utf8')).masterSpreadsData;
 const career=vm.runInContext('catalog.filter(s=>matchesVibe(s,"Career")).map(s=>s.id)',context);
 assert.ok(career.includes('career-shift'));assert.ok(career.includes('financial-healing'));
 assert.equal(vm.runInContext('matchesVibe({title:"A relationship reflection",category:"love"},"Love")',context),true);
 assert.equal(vm.runInContext('matchesVibe({title:"Grounding",category:"wellbeing"},"Career")',context),false);
});


test('clear glass uses refraction and reflective edges without frosted blur',()=>{
 const css=fs.readFileSync(path.join(root,'liquid-glass.css'),'utf8');
 const artwork=fs.readFileSync(path.join(root,'artwork.js'),'utf8');
 assert.doesNotMatch(css,/blur\s*\(/i);
 assert.ok(css.includes('.slot.opened')&&css.includes('.listbutton')&&css.includes('.bottomdock'));
 assert.ok(css.includes('inset')&&css.includes('ffffff05'));
 assert.ok(artwork.includes('feDisplacementMap'));assert.ok(!artwork.includes('feGaussianBlur'));
 assert.ok(fs.readFileSync(path.join(root,'index.html'),'utf8').includes('liquid-glass.css'));
});

test('every feature and spread uses the shared original illustrations instead of emoji tiles',()=>{
 const {context}=appContext();
 const bindings=JSON.parse(fs.readFileSync(path.join(root,'../mobile/src/data/illustrationBindings.json'),'utf8'));
 assert.equal(vm.runInContext('JSON.stringify(ILLUSTRATION_BINDINGS)',context),JSON.stringify(bindings));
 const ids=Array.from(vm.runInContext('allTools.map(t=>t[0])',context));
 assert.equal(ids.length,18);
 assert.deepEqual(Object.keys(bindings.tools).sort(),ids.sort());
 for(const art of [...Object.values(bindings.tools),...Object.values(bindings.spreads)]){
  assert.ok(['cosmic','study','journal','ritual'].includes(art.pack));
  assert.ok(Number.isInteger(art.cell)&&art.cell>=0&&art.cell<=3);
 }
 const html=vm.runInContext('state.tool=null;explorePage()',context);
 assert.equal((html.match(/class="panel-illustration"/g)||[]).length,18);
 assert.doesNotMatch(html,/class="emoji"|class="tooltile"/);
 for(const id of ids)assert.ok(html.includes('data-action="tool:'+id+'"'));
 assert.doesNotMatch(vm.runInContext('spreadsPage()',context),/class="glyph"/);
});

test('the app name uses the intact approved transparent logo and the full welcome copy',()=>{
 const {context}=appContext();const html=vm.runInContext('home()',context);
 assert.ok(html.includes('aria-label="Spiritual Vibz"'));
 assert.ok(html.includes('Daily spiritual tools, lunar guidance, and soul-aligned insights'));
 assert.ok(html.includes('stay connected to your highest self.'));
 assert.doesNotMatch(html,/class="scenic"/);
 const name='assets/spiritual-vibz-logo-compact.png';const bytes=fs.readFileSync(path.join(root,name));
 assert.equal(bytes[25],6,'Expected RGBA logo with alpha');
 assert.equal(bytes.readUInt32BE(16),1984);
 assert.equal(bytes.readUInt32BE(20),793);
 assert.deepEqual(bytes,fs.readFileSync(path.join(root,'../mobile',name)));
 for(const asset of ['home-tarot-moon.png','home-feature-icons.png','daily-vibz-bright-sunshine.png','daily-vibz-crystal-pink.png','rainbow-sun-face.png','purple-yellow-sun-face.png','ace-cups-crystal-ball.png','ace-cups-deck.png','galaxy-crystal-ball.png','home-mystic-room-arabic.png','home-light-portal.png','neurospicy-mystic-logo.png']){
  const shared=fs.readFileSync(path.join(root,'assets',asset));
  assert.deepEqual(shared,fs.readFileSync(path.join(root,'../mobile/assets',asset)),`Web/native Home artwork differs: ${asset}`);
  if(['daily-vibz-bright-sunshine.png','daily-vibz-crystal-pink.png','rainbow-sun-face.png','purple-yellow-sun-face.png','ace-cups-crystal-ball.png','ace-cups-deck.png','galaxy-crystal-ball.png'].includes(asset))assert.equal(shared[25],6,`Expected transparent RGBA: ${asset}`);
 }
 assert.equal((html.match(/assets\/spiritual-vibz-logo-compact\.png/g)||[]).length,1);
 assert.doesNotMatch(html,/brand-spiritual\.png|brand-vibz\.png/);
});

test('the full learning reference is shared and linked from Tarot, houses and numerology',()=>{
 const {context}=appContext();const native=JSON.parse(fs.readFileSync(path.join(root,'../mobile/src/data/learningLibrary.json'),'utf8'));
 assert.equal(vm.runInContext('JSON.stringify(LEARNING_LIBRARY)',context),JSON.stringify(native));
 assert.deepEqual(native,JSON.parse(fs.readFileSync(path.join(root,'../backend/data/learning_library.json'),'utf8')));
 assert.equal(native.houses.length,12);assert.equal(native.planets.length,10);assert.equal(native.numbers.length,12);
 const html=vm.runInContext('state.tool="numbers";explorePage()',context);
 for(const text of ['Master numbers: 11, 22, 33','The numbers of Tarot','Court cards','Life Path calculator'])assert.ok(html.includes(text));
 const houses=vm.runInContext('state.tool="houses";explorePage()',context);
 assert.ok(houses.includes('general house meanings'));assert.ok(!houses.includes('data-action="tool-run"'));
});


test('reference homepage has exactly six live cards and shared native routes',()=>{
 const {context}=appContext();const html=vm.runInContext('home()',context);
 const design=JSON.parse(fs.readFileSync(path.join(root,'../mobile/src/data/homeDesign.json'),'utf8'));
 assert.equal(vm.runInContext('JSON.stringify(HOME_DESIGN)',context),JSON.stringify(design));
 assert.equal((html.match(/data-home-feature=/g)||[]).length,6);
 for(const feature of design.features){assert.ok(html.includes('aria-label="'+feature.label+'"'));assert.ok(html.includes('data-action="'+feature.action+'"'));}
 assert.doesNotMatch(html.split('<section class="home-light-portal"')[0],/Pick your adventure|Fan-favorite|More to explore|Track your|home-wall-tagline/);
 assert.match(html,/home-light-portal/);
 for(const file of ['home-tarot-moon.png','home-feature-icons.png']){
  const bytes=fs.readFileSync(path.join(root,'assets',file));assert.equal(bytes[25],6);
  assert.deepEqual(bytes,fs.readFileSync(path.join(root,'../mobile/assets',file)));
 }
 const font=fs.readFileSync(path.join(root,'assets/fonts/GreatVibes-Regular.ttf'));
 for(const file of ['android/app/src/main/assets/fonts/GreatVibes-Regular.ttf','ios/SpiritualVibez/Fonts/GreatVibes-Regular.ttf'])assert.deepEqual(font,fs.readFileSync(path.join(root,'../mobile',file)));
});
