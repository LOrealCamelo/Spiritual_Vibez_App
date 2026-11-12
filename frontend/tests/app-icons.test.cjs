const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
function png(file,size,alpha=false){const bytes=fs.readFileSync(file);assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a',file);assert.equal(bytes.readUInt32BE(16),size,file);assert.equal(bytes.readUInt32BE(20),size,file);assert.equal(bytes[25],alpha?6:2,file);return bytes;}
test('Apple touch icons, browser favicons and Android PWA icons are public PNG assets',()=>{
 const dir=path.join(root,'frontend/assets/icons'),html=fs.readFileSync(path.join(root,'frontend/index.html'),'utf8');
 for(const size of [16,32,48,120,152,167,180,192,512])png(path.join(dir,`avatar-${size}.png`),size);
 png(path.join(dir,'avatar-maskable-512.png'),512);
 for(const size of [120,152,167,180])assert.ok(html.includes(`sizes="${size}x${size}" href="assets/icons/avatar-${size}.png"`));
 assert.match(html,/rel="manifest" href="assets\/icons\/spiritual-vibz.webmanifest"/);
 assert.match(html,/name="apple-mobile-web-app-title" content="Spiritual Vibz"/);
 assert.match(html,/sizes="32x32" href="assets\/icons\/avatar-32.png"/);
 const ico=fs.readFileSync(path.join(dir,'favicon.ico'));assert.equal(ico.readUInt16LE(2),1);assert.ok(ico.readUInt16LE(4)>=3);
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'spiritual-vibz.webmanifest'),'utf8'));
 assert.equal(manifest.name,'Spiritual Vibz');assert.equal(manifest.start_url,'/#home');assert.equal(manifest.scope,'/');assert.equal(manifest.id,'/');
 for(const size of ['192x192','512x512'])assert.ok(manifest.icons.some(i=>i.sizes===size&&i.purpose==='any'));
 assert.ok(manifest.icons.some(i=>i.purpose==='maskable'&&i.sizes==='512x512'));
 for(const icon of manifest.icons){assert.equal(icon.type,'image/png');assert.ok(fs.existsSync(path.join(root,'frontend',icon.src)));}
});
test('iPhone, iPad and App Store icon slots resolve to opaque PNGs with exact pixel sizes',()=>{
 const dir=path.join(root,'mobile/ios/SpiritualVibez/Images.xcassets/AppIcon.appiconset');const catalog=JSON.parse(fs.readFileSync(path.join(dir,'Contents.json'),'utf8'));
 for(const image of catalog.images){assert.ok(image.filename);png(path.join(dir,image.filename),Math.round(Number(image.size.split('x')[0])*parseFloat(image.scale)));}
 for(const idiom of ['iphone','ipad','ios-marketing'])assert.ok(catalog.images.some(i=>i.idiom===idiom));
 const project=fs.readFileSync(path.join(root,'mobile/ios/SpiritualVibez.xcodeproj/project.pbxproj'),'utf8');assert.match(project,/ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon/);
});
test('legacy and adaptive Android launchers retain the full avatar at every density',()=>{
 const res=path.join(root,'mobile/android/app/src/main/res');
 for(const [density,scale] of [['mdpi',1],['hdpi',1.5],['xhdpi',2],['xxhdpi',3],['xxxhdpi',4]]){
  const dir=path.join(res,'mipmap-'+density);png(path.join(dir,'ic_launcher.png'),48*scale);png(path.join(dir,'ic_launcher_round.png'),48*scale);png(path.join(dir,'ic_launcher_foreground.png'),108*scale,true);
 }
 for(const icon of ['ic_launcher','ic_launcher_round']){const xml=fs.readFileSync(path.join(res,'mipmap-anydpi-v26',icon+'.xml'),'utf8');assert.match(xml,/@color\/launcher_background/);assert.match(xml,/@mipmap\/ic_launcher_foreground/);}
 const manifest=fs.readFileSync(path.join(root,'mobile/android/app/src/main/AndroidManifest.xml'),'utf8');assert.match(manifest,/@mipmap\/ic_launcher/);
});
