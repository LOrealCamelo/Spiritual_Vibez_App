/**
 * Make a self-contained Netlify static site without changing the Render backend.
 * Only public browser assets are published; Worker config, source tests, and
 * documentation are kept out of the deploy directory.
 */
import {mkdir, readdir, cp, copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../../', import.meta.url));
const frontend = path.join(root, 'frontend');
const output = path.join(root, 'dist', 'netlify');
await mkdir(output, {recursive:true});

let pages = 0;
for (const entry of await readdir(frontend, {withFileTypes:true})) {
  if (!entry.isFile() || entry.name === 'cloudflare-api.js' ||
      !(entry.name === 'robots.txt' || entry.name === 'sitemap.xml' || /\.(html|js|css|svg)$/i.test(entry.name))) continue;
  await copyFile(path.join(frontend,entry.name),path.join(output,entry.name));
  pages++;
}
await cp(path.join(frontend, 'assets'), path.join(output, 'assets'), {recursive:true});

// The original deck is in mobile/assets/tarot, outside the static frontend.
// Publish the actual 78 PNGs so the browser does not need to ask Render for
// every card image (and avoids a second platform's image proxy/rate limits).
const tarotSource = path.join(root,'mobile','assets','tarot');
const cards = (await readdir(tarotSource)).filter(x=>x.endsWith('.png'));
if (cards.length !== 78) {
  throw Error('Expected exactly 78 tarot card PNGs, found '+cards.length);
}
const tarotDest = path.join(output,'assets','tarot');
await mkdir(tarotDest, {recursive:true});
for (const filename of cards) {
  await copyFile(path.join(tarotSource,filename),path.join(tarotDest,filename));
}
console.log('Netlify static site ready: '+pages+' top-level browser files and '+cards.length+' original tarot cards.');
