const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(require.resolve('../url-hygiene.js'),'utf8');
function run(href){
 const calls=[],state={saved:'preserved'};
 const history={state,replaceState:(...args)=>calls.push(args)};
 vm.runInNewContext(source,{URL,URLSearchParams,location:{href},history});
 return {calls,state};
}
test('tracking is removed in place while legitimate params and natal hash survive',()=>{
 const {calls,state}=run('https://app.neurospicymystic.com/?utm_source=chatgpt.com&code=abc&state=xyz&date=2026-11-16&UTM_MEDIUM=chat&fbclid=a&gclid=b#explore/natal');
 assert.equal(calls.length,1);assert.equal(calls[0][0],state);
 assert.equal(calls[0][2],'/?code=abc&state=xyz&date=2026-11-16#explore/natal');
});
test('clean URLs, hash queries and authentication parameters are untouched',()=>{
 for(const href of ['https://example.com/#explore/natal','https://example.com/?code=secret&state=x&ref=friend#explore/natal?tab=houses'])assert.equal(run(href).calls.length,0);
});
test('duplicates and all explicitly recognized tracking keys are removed',()=>{
 const keys=['utm_source','utm_medium','utm_campaign','utm_term','utm_content','fbclid','gclid','dclid','msclkid','ttclid','twclid','igshid','mc_cid','mc_eid','_ga','_gl'];
 const {calls}=run('https://example.com/path?keep=1&'+keys.map(k=>k+'=tag').join('&')+'&utm_source=again#journal');
 assert.equal(calls[0][2],'/path?keep=1#journal');
});
test('tracking appended after an application hash does not swallow the tool route',()=>{
 const {calls}=run('https://example.com/?utm_source=chatgpt.com#explore/natal?utm_medium=chat&section=houses');
 assert.equal(calls.length,1);
 assert.equal(calls[0][2],'/#explore/natal?section=houses');
 assert.equal(run('https://example.com/#explore/natal?utm_source=chatgpt.com').calls[0][2],'/#explore/natal');
 assert.equal(run('https://example.com/#article?utm_source=untouched').calls.length,0);
 const legacyCalls=[];
 class LegacyParams extends URLSearchParams{get size(){return undefined;}}
 vm.runInNewContext(source,{URL,URLSearchParams:LegacyParams,
  location:{href:'https://example.com/#explore/natal?utm_source=chat&section=houses'},
  history:{replaceState:(...args)=>legacyCalls.push(args)}});
 assert.equal(legacyCalls[0][2],'/#explore/natal?section=houses');
});
test('history failures do not prevent app startup',()=>{
 assert.doesNotThrow(()=>vm.runInNewContext(source,{URL,location:{href:'https://example.com/?utm_source=tag'},history:{replaceState(){throw Error('restricted');}}}));
});
