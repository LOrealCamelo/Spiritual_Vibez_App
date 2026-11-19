// Execute shipped UMD scripts as classic browser scripts. The Cloudflare
// package is ESM, so require() would return an empty module namespace.
const fs=require('node:fs');
const vm=require('node:vm');
module.exports=function(file,globalName){
 const context=vm.createContext({});
 vm.runInContext(fs.readFileSync(require.resolve(file),'utf8'),context,{filename:file});
 const api=context[globalName];
 if(!api)throw new Error('Browser global missing: '+globalName);
 return api;
};
