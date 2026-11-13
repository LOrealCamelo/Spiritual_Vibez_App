const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Tools=require('../astro-map-tools');
const report=require('../../mobile/__tests__/fixtures/astrocartography.json');

test('map location inspector finds every nearby line and matches backend city distances',()=>{
 for(const city of report.places){
  const actual=Tools.inspect(report,city.latitude,city.longitude).nearby_lines;
  assert.deepEqual(actual.map(p=>[p.planet,p.angle,p.distance_km]),city.nearby_lines.map(p=>[p.planet,p.angle,p.distance_km]));
 }
});
test('every crossing inspection combines both actual line geometries',()=>{
 for(const point of report.crossings){
  const actual=Tools.select(report,(point.longitude+180)/360,(90-point.latitude)/180);
  assert.ok(actual.crossing);
  for(const [name,angle] of [[point.planet_a,point.angle_a],[point.planet_b,point.angle_b]]){
   const p=actual.nearby_lines.find(p=>p.planet===name&&p.angle===angle);
   assert.ok(p&&p.distance_km===0,point.title);
  }
 }
});
test('web and native use identical map inspection math and the complete reading guide',()=>{
 assert.deepEqual(fs.readFileSync(path.join(__dirname,'../astro-map-tools.js')),fs.readFileSync(path.join(__dirname,'../../mobile/src/content/astro-map-tools.js')));
 assert.equal(Tools.guide.passes.length,3);assert.equal(Tools.guide.comparison.length,3);
 assert.match(Tools.guide.method,/Astronomy Engine/);
 assert.doesNotMatch(JSON.stringify(Tools.guide),/DE431|Swiss Ephemeris|Decision Report|WorldMap Charts|ReadHoroscopes/);
});
