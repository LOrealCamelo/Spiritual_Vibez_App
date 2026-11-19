const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');

function setup({suspended=false,delayed=false}={}){
 const nodes=[],contexts=[];let resume;
 class Audio{
  constructor(){this.state=suspended?'suspended':'running';contexts.push(this);}
  resume(){this.resumed=true;return delayed?new Promise(r=>{resume=r}):Promise.resolve();}
  createGain(){const gain={gain:{value:1},connect(){}};this.gain=gain;return gain;}
  createOscillator(){const osc={frequency:{value:0},connect(){},start(){this.started=true},stop(){this.stopped=true}};nodes.push(osc);return osc;}
  close(){this.state='closed';return Promise.resolve();}
 }
 const app={innerHTML:''};
 const window={webkitAudioContext:Audio,addEventListener(){},scrollTo(){}};
 const context=vm.createContext({window,location:{hash:'',hostname:'localhost'},
  document:{querySelector:()=>app,addEventListener(){},getElementById:id=>({value:id==='volume'?'0':'432'})},
  AbortController,AbortSignal,setTimeout,clearTimeout,
  localStorage:{getItem:()=>null},fetch:async()=>{throw Error('offline')},alert:message=>{throw Error(message)}});
 for(const file of ['artwork.js','learning.js','app.js'])vm.runInContext(fs.readFileSync(require.resolve('../'+file),'utf8'),context);
 return {context,nodes,contexts,release:()=>resume?.()};
}
test('Safari AudioContext fallback resumes, honors mute and stops resources',async()=>{
 const {context,nodes,contexts}=setup({suspended:true});
 await vm.runInContext('startAudio()',context);
 assert.equal(contexts[0].resumed,true);assert.equal(contexts[0].gain.gain.value,0);
 assert.equal(nodes[0].frequency.value,432);assert.equal(nodes[0].started,true);
 vm.runInContext('stopAudio();stopAudio()',context);
 assert.equal(nodes[0].stopped,true);assert.equal(contexts[0].state,'closed');
});
test('Stop during asynchronous audio resume cannot start a hidden oscillator',async()=>{
 const {context,nodes,contexts,release}=setup({suspended:true,delayed:true});
 const started=vm.runInContext('startAudio()',context);
 vm.runInContext('stopAudio()',context);release();await started;
 assert.equal(nodes.length,0);assert.equal(contexts[0].state,'closed');
});
