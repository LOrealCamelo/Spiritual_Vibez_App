const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const frontend=path.resolve(__dirname,'..');
function setup(){
 const window={localStorage:{getItem:()=>null},SV_RITUAL_COUNTRIES:[]};
 const context=vm.createContext({window});
 vm.runInContext(fs.readFileSync(path.join(frontend,'ritual-world-data.js'),'utf8'),context);
 vm.runInContext(fs.readFileSync(path.join(frontend,'ritual-library.js'),'utf8'),context);
 return window;
}
const features=['Love & Self-Love','Moon & Manifestation','Dark & Shadow Work','Celtic & Irish Traditions','Demonology & Spirit Lore','Women in Spiritual History'].map(title=>({title,subtitle:'Explore this theme',practice:'Original reflection',body:'A gentle modern practice.'}));
const book=[{title:'Start Here',text:'Your first page.'},{title:'Continue',text:'Your next page.'},{title:'Reflect',text:'Your closing page.'}];
test('all three ritual artwork files are real, non-empty binary assets',()=>{
 for(const filename of ['ritual-featured-six.webp','ritual-garden-circle.webp','ritual-enchanted-bookshelf.webp']){
  const file=path.join(frontend,'assets',filename);
  assert.ok(fs.existsSync(file),filename);
  assert.ok(fs.statSync(file).size>1000,filename);
 }
});
test('six unique illustrated collections render in the approved order',()=>{
 const window=setup();
 const html=window.SpiritualRitualLibrary.render({features,book,position:0,letter:'A'});
 assert.equal((html.match(/class="sv-ritual-card"/g)||[]).length,6);
 for(const feature of features)assert.ok(html.includes(feature.title));
 for(const artPosition of ['--sv-art-x:0%;--sv-art-y:0%','--sv-art-x:50%;--sv-art-y:0%','--sv-art-x:100%;--sv-art-y:0%','--sv-art-x:0%;--sv-art-y:100%','--sv-art-x:50%;--sv-art-y:100%','--sv-art-x:100%;--sv-art-y:100%'])assert.ok(html.includes(artPosition));
 assert.ok(html.includes('ritual-garden-circle.webp')===false,'hero background belongs in CSS');
 assert.ok(html.includes('ritual-enchanted-bookshelf.webp'));
});
test('book page navigation controls and private save action render',()=>{
 const html=setup().SpiritualRitualLibrary.render({features,book,position:1,letter:'A'});
 for(const action of ['ritual-book-prev','ritual-book-next','ritual-bookmark','ritual-page-journal'])assert.ok(html.includes('data-action="'+action+'"'));
 assert.ok(html.includes('Page 2 of 3'));
 assert.ok(html.includes('Continue'));
});
test('country browse includes territories but does not pretend articles are finished',()=>{
 const window=setup();
 assert.equal(window.SV_RITUAL_COUNTRIES.length,249);
 assert.equal(window.SV_RITUAL_COUNTRIES[0],'Afghanistan');
 assert.equal(window.SV_RITUAL_COUNTRIES.at(-1),'Zimbabwe');
 const html=window.SpiritualRitualLibrary.render({features,book,letter:'Z'});
 assert.ok(html.includes('Zimbabwe'));
 assert.ok(!html.includes('Afghanistan</span>'));
 assert.ok(html.includes('Historical chapter being researched'));
 assert.ok(html.includes('Indigenous nations'));
});
