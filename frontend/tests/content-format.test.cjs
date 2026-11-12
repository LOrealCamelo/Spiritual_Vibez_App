const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Format=require('../content-format');
const reading={birth_year:1977,polarity:'Yin Feminine',animal_sign:'Fire Snake 🐍',pillars:{year_pillar:{title:'Fire Snake (Ding Si)',domain:'Ancestral Lineage & Outer Persona'},day_master:{title:'Yin Earth Snake (Ji Si)',domain:'Core Soul Identity & Spouse Palace'}},wheel_svg:'<svg>PRIVATE XML</svg>',session_id:'private-token'};
test('BaZi results share human-readable complete text with a clean app invitation',()=>{
 const item=Format.snapshot({title:'Chinese Zodiac & BaZi',value:reading,route:'explore/bazi'});
 const message=Format.message(item);
 for(const text of ['Birth year: 1977','Zodiac animal: Fire Snake','Year pillar','Day master','Core Soul Identity','Get your own here: https://spiritual-vibez-app.onrender.com/#explore/bazi'])assert.ok(message.includes(text),text);
 assert.doesNotMatch(message,/[{}]|birth_year|year_pillar|PRIVATE XML|private-token/);
 assert.equal(new URL(item.url).search,'');assert.ok(!item.url.includes('1977'));
});
test('image summaries stay bounded while accompanying text preserves the full reading',()=>{
 const text=Array.from({length:150},(_,i)=>'Interpretation '+i+': a thoughtful paragraph about this placement.').join('\n');
 const item=Format.snapshot({title:'Birth chart',text,route:'explore/natal'});
 assert.ok(Format.summary(item).length<2300);assert.ok(Format.message(item).includes('Interpretation 149'));
 assert.equal(item.text,text);
});
test('the browser and native app use exactly the same result formatter',()=>{
 assert.deepEqual(fs.readFileSync(path.join(__dirname,'../content-format.js')),fs.readFileSync(path.join(__dirname,'../../mobile/src/content/content-format.js')));
});
