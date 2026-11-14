const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const lib=require('../rune-library.js');
const ROOT=path.join(__dirname,'../..');
test('web and native share the exact Elder Futhark rune library',()=>{
 assert.equal(fs.readFileSync(path.join(ROOT,'frontend/rune-library.js'),'utf8'),
              fs.readFileSync(path.join(ROOT,'mobile/src/content/rune-library.js'),'utf8'));
});
test('24 unique Elder Futhark signs, no historically invented blank rune',()=>{
 assert.equal(lib.RUNES.length,24);
 assert.equal(new Set(lib.RUNES.map(r=>r.name)).size,24);
 assert.equal(new Set(lib.RUNES.map(r=>r.symbol)).size,24);
 assert.equal(lib.RUNES.filter(r=>!r.reversible).length,9);
 assert.equal(lib.RUNES.filter(r=>r.reversed===null).length,9);
 assert.ok(!lib.RUNES.some(r=>/blank|odin rune/i.test(r.name)));
 for(const rune of lib.RUNES){
  assert.ok(rune.upright.meaning&&rune.historic);
  assert.equal(rune.reversible,!!rune.reversed);
 }
});
test('randomized draws do not repeat symbols and honor their spread sizes',()=>{
 for(const [key,spread] of Object.entries(lib.LAYOUTS)){
  for(let iteration=0;iteration<150;iteration++){
   const cast=lib.cast(key,true);
   assert.equal(cast.length,spread.count);
   assert.equal(new Set(cast.map(r=>r.name)).size,spread.count);
   for(const rune of cast){
    assert.ok(['upright','reversed'].includes(rune.orientation));
    assert.ok(rune.reversible||rune.orientation==='upright');
    assert.ok(rune.reading.meaning);
   }
  }
 }
});
test('reversal can be disabled for any modern rune cast',()=>{
 for(let iteration=0;iteration<100;iteration++){
  assert.ok(lib.cast('handful',false).every(r=>r.orientation==='upright'));
 }
});
