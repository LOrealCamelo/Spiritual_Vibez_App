const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {pngReferences, checkLocalPngs} = require('./check-assets.cjs');

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'sv-assets-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  fs.mkdirSync(path.join(root, 'src/components'), {recursive: true});
  fs.mkdirSync(path.join(root, 'assets'));
  fs.copyFileSync(path.join(__dirname, '../assets/ui_cards/home_daily_card.png'), path.join(root, 'assets/good.png'));
  return root;
}
const check = root => checkLocalPngs(root, {checkPanels: false});

test('parses multiline, double/single quoted, template literal requires and PNG imports; ignores comments/strings', () => {
  const source = [
    `require(\n './one.png'\n); require("../../two.png");`,
    'require(`./three.png`);',
    `import icon from './four.png'; export {default} from './five.png'; import('../six.png');`,
    `// require('./comment.png')`,
    `/* require('./block.png') */`,
    `const text = "require('./string.png')"; require('package.png'); require('./module');`,
  ].join('\n');
  assert.deepEqual(pngReferences('Example.tsx', source).map(x => x.request),
    ['./one.png','../../two.png','./three.png','./four.png','./five.png','../six.png']);
});

test('resolves references relative to every nested component, including unused aliases', t => {
  const root = fixture(t);
  fs.writeFileSync(path.join(root, 'App.tsx'), `const good=require('./assets/good.png');`);
  fs.writeFileSync(path.join(root, 'src/components/Hidden.tsx'), `const unused = require(\n '../../assets/missing.png'\n);`);
  const result = check(root);
  assert.equal(result.references.length, 2);
  assert.match(result.errors.join('\n'), /Hidden.tsx:2.*missing.png/);
  fs.renameSync(path.join(root, 'assets/good.png'), path.join(root, 'assets/missing.png'));
  assert.match(check(root).errors.join('\n'), /App.tsx:1.*good.png/);
});

test('accepts valid PNGs, rejects case mismatches and empty images', t => {
  const root = fixture(t);
  const component = path.join(root, 'src/components/Panel.tsx');
  fs.writeFileSync(component, `const art=require('../../assets/good.png');`);
  assert.deepEqual(check(root).errors, []);
  fs.writeFileSync(component, `const art=require('../../assets/Good.png');`);
  assert.match(check(root).errors[0], /case mismatch/);
  fs.writeFileSync(component, `const art=require('../../assets/good.png');`);
  fs.writeFileSync(path.join(root, 'assets/good.png'), '');
  assert.match(check(root).errors[0], /Invalid PNG/);
});

test('ignores installed dependencies but fails an empty source scan', t => {
  const root = fixture(t);
  fs.mkdirSync(path.join(root, 'node_modules'));
  fs.writeFileSync(path.join(root, 'node_modules/Dependency.tsx'), `require('./missing.png')`);
  assert.match(check(root).errors[0], /No local PNG references/);
});

test('rejects static WebP imports so Android and iOS continue to use PNG artwork', t => {
  const root = fixture(t);
  fs.writeFileSync(path.join(root, 'App.tsx'), `require('./assets/legacy.webp')`);
  assert.match(check(root).errors.join('\n'), /Use a PNG upload instead of WebP/);
});

test('requires all 24 panels to be mapped and exits nonzero for a newly broken component', t => {
  const root = fixture(t);
  fs.cpSync(path.join(__dirname, '../assets/ui_cards'), path.join(root, 'assets/ui_cards'), {recursive:true});
  fs.copyFileSync(path.join(__dirname, '../src/components/IllustratedCard.tsx'), path.join(root, 'src/components/IllustratedCard.tsx'));
  assert.deepEqual(checkLocalPngs(root).errors, []);
  fs.writeFileSync(path.join(root, 'src/components/NewScreen.tsx'), `const unused = require('../../assets/missing.png')`);
  const cli = spawnSync(process.execPath, [path.join(__dirname,'check-assets.cjs'), root], {encoding:'utf8'});
  assert.equal(cli.status, 1);
  assert.match(cli.stderr, /NewScreen.tsx:1/);
  fs.writeFileSync(path.join(root, 'src/components/IllustratedCard.tsx'), `require('../../assets/good.png')`);
  assert.match(checkLocalPngs(root).errors.join('\n'), /UI panel missing from IllustratedCard map/);
});
