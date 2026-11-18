const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

function setup(){
 const documentEvents={},windowEvents={};
 const context=vm.createContext({
  document:{visibilityState:'visible',addEventListener:(name,callback)=>{documentEvents[name]=callback}},
  window:{addEventListener:(name,callback)=>{windowEvents[name]=callback}},
 });
 vm.runInContext(fs.readFileSync(require.resolve('../cosmic.js'),'utf8'),context);
 return {context,documentEvents,windowEvents};
}
test('focus and visibility during deferred app loading do not access missing state',()=>{
 const {windowEvents,documentEvents}=setup();
 assert.doesNotThrow(()=>windowEvents.focus());
 assert.doesNotThrow(()=>documentEvents.visibilitychange());
});
test('focus and visibility still refresh Cosmos once application state exists',()=>{
 const {context,windowEvents,documentEvents}=setup();
 vm.runInContext("let calls=0;const state={page:'cosmos',transit:null};fetchDailySky=()=>calls++;",context);
 windowEvents.focus();documentEvents.visibilitychange();
 assert.equal(vm.runInContext('calls',context),2);
});
