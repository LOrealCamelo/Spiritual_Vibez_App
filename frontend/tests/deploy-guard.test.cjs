const {test}=require('node:test');
const assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const path=require('node:path');
const script=path.join(__dirname,'../scripts/skip-review-deploy.mjs');
test('Netlify cancels this review branch before building, including PRs targeting main',()=>{
 for(const values of [{BRANCH:'release/neon-memberships-review'},{BRANCH:'main',HEAD:'release/neon-memberships-review'},{BRANCH:'feature/manual-memberships'},{BRANCH:'feature/neon-postgres-memberships'},{BRANCH:'review/prelaunch-audit'},{BRANCH:'main',HEAD:'review/prelaunch-audit'}]){
  assert.equal(spawnSync(process.execPath,[script],{env:{...process.env,BRANCH:'',HEAD:'',COMMIT_REF:'',...values}}).status,0);
 }
});
test('the review guard does not disable the normal production build policy',()=>{
 assert.equal(spawnSync(process.execPath,[script],{env:{...process.env,BRANCH:'main',HEAD:'main',COMMIT_REF:'test-sha'}}).status,1);
});
