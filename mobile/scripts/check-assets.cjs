#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');

const excluded = new Set(['node_modules', '.git', '.gradle', 'build', 'Pods', 'dist', 'coverage']);
function sourceFiles(root) {
  return fs.readdirSync(root, {withFileTypes: true}).flatMap(entry => {
    if (excluded.has(entry.name)) return [];
    const file = path.join(root, entry.name);
    if (entry.isDirectory()) return sourceFiles(file);
    return entry.isFile() && /\.(?:[cm]?[jt]s|[jt]sx)$/.test(entry.name) ? [file] : [];
  });
}

// Parse syntax rather than matching a short allowlist or text inside comments.
function pngReferences(file, text) {
  const source = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true);
  const refs = [];
  function visit(node) {
    let value;
    if (ts.isCallExpression(node) && node.arguments.length === 1 &&
        ((ts.isIdentifier(node.expression) && node.expression.text === 'require') ||
         node.expression.kind === ts.SyntaxKind.ImportKeyword)) value = node.arguments[0];
    if (ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) value = node.moduleSpecifier;
    if (value && (ts.isStringLiteral(value) || ts.isNoSubstitutionTemplateLiteral(value)) &&
        /^\.{1,2}\//.test(value.text) && /\.(?:png|webp)$/i.test(value.text)) {
      refs.push({request: value.text, line: source.getLineAndCharacterOfPosition(value.getStart(source)).line + 1});
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  return refs;
}

function exactFile(root, file) {
  const relative = path.relative(root, file);
  if (relative.startsWith('..') || path.isAbsolute(relative)) return false;
  let current = root;
  for (const segment of relative.split(path.sep)) {
    if (!fs.existsSync(current) || !fs.statSync(current).isDirectory() || !fs.readdirSync(current).includes(segment)) return false;
    current = path.join(current, segment);
  }
  return fs.statSync(current).isFile();
}

function checkLocalPngs(root, {checkPanels = true} = {}) {
  root = path.resolve(root);
  const errors = [], references = [];
  const files = sourceFiles(root);
  for (const file of files) {
    for (const ref of pngReferences(file, fs.readFileSync(file, 'utf8'))) {
      const resolved = path.resolve(path.dirname(file), ref.request);
      const location = `${path.relative(root, file)}:${ref.line} (${ref.request})`;
      references.push({file, resolved, ...ref});
      if (/\.webp$/i.test(ref.request)) errors.push(`Use a PNG upload instead of WebP: ${location}`);
      if (!exactFile(root, resolved)) errors.push(`Missing PNG or filename case mismatch: ${location}`);
      else {
        const bytes = fs.readFileSync(resolved);
        if (bytes.length < 24 || !bytes.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10])) ||
            bytes.toString('ascii',12,16) !== 'IHDR' || !bytes.readUInt32BE(16) || !bytes.readUInt32BE(20)) {
          errors.push(`Invalid PNG header: ${location}`);
        }
      }
    }
  }
  if (!references.length) errors.push('No local PNG references found; check the scan root.');
  if (checkPanels) {
    const catalogFile=path.join(root,'src/data/uiPanels.json');
    if(!fs.existsSync(catalogFile)) errors.push('Missing UI panel catalog.');
    else {
      const panels=JSON.parse(fs.readFileSync(catalogFile,'utf8'));
      if(Object.keys(panels).length!==24) errors.push('Expected 24 live UI panel definitions.');
      const mapped=new Set(references.map(ref=>ref.resolved));
      for(const [name,panel] of Object.entries(panels)){
        const asset=path.join(root,'assets/illustrations',panel.pack+'.png');
        if(!mapped.has(asset))errors.push('UI illustration missing from static map: '+name);
        if(!Number.isInteger(panel.cell)||panel.cell<0||panel.cell>3||!panel.title)errors.push('Invalid UI panel definition: '+name);
      }
    }
  }
  return {files: files.length, references, errors};
}

if (require.main === module) {
  const result = checkLocalPngs(process.argv[2] || path.join(__dirname, '..'));
  for (const error of result.errors) console.error(error);
  console.log(`Checked ${result.references.length} PNG references across ${result.files} source files.`);
  process.exitCode = result.errors.length ? 1 : 0;
}
module.exports = {pngReferences, checkLocalPngs};
