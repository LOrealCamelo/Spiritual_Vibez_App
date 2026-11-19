import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
const packageInfo=JSON.parse(readFileSync('package.json','utf8'));
if(!packageInfo.private)throw Error('This application package must stay private.');
const {default:neonConfig}=await import('../neon.ts');
if(neonConfig.auth || neonConfig.functions || neonConfig.buckets || neonConfig.aiGateway || neonConfig.preview?.realtime)throw Error('Only the requested Postgres service may be enabled.');
console.log('Neon config loaded: Postgres only.');
const scripts=['frontend/love.js','frontend/membership.js','frontend/app.js','scripts/start.mjs'];
for(const script of scripts){const result=spawnSync(process.execPath,['--check',script],{stdio:'inherit'});if(result.status)process.exit(result.status);}
const built=spawnSync(process.execPath,['frontend/scripts/build-netlify.mjs'],{stdio:'inherit'});
if(built.status)process.exit(built.status);
console.log('Build passed: browser syntax and existing static application build.');
console.log('FastAPI remains the application server; no hosted deployment was triggered.');
