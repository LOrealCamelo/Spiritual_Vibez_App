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
  vm.runInContext(fs.readFileSync(path.join(root,'app.js'),'utf8'), context);
  return {context,app};
}

test('rendered images and CSS backgrounds resolve to real PNG uploads', () => {
  const {context} = appContext();
  const html = ['home()','spreadsPage()','learningPage()','journalPage()'].map(code=>vm.runInContext(code,context)).join('');
  const css = fs.readFileSync(path.join(root,'styles.css'),'utf8');
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
  for(const file of ['app.js','styles.css','index.html']){
    assert.doesNotMatch(fs.readFileSync(path.join(root,file),'utf8'),/\.webp\b/i,`Legacy image URL in ${file}`);
  }
});

test('hero has separate character/background layers and accessible HTML actions', () => {
  const {context} = appContext();
  const html=vm.runInContext('home()',context);
  assert.match(html,/assets\/cartoon_me_transparent3.png/);
  assert.match(html,/<h1>Zero boring\.<\/h1>/);
  for(const action of ['nav:spreads','nav:learn','daily-card','nav:journal','nav:cosmos','tool:natal','tool:life','tool:moon','tool:rituals']){
    assert.ok(html.includes(`data-action="${action}"`),`Missing interactive action: ${action}`);
  }
});

test('display fonts are local licensed assets, so the reference typography works offline',()=>{
  const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
  for(const family of ['Pacifico','KaushanScript','DMSans']){
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
