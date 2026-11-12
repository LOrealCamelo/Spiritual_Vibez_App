#!/usr/bin/env node
// Package the approved avatar into standard web/iOS/Android icon sizes.
// Only proportional resizing, opaque backgrounds and platform safe-area padding.
const fs=require('node:fs');
const path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
const web=path.join(root,'frontend/assets/icons');
const source=path.join(web,'avatar-master.png');
const background='#30084d';
function run(args){const result=spawnSync('magick',args,{stdio:'inherit'});if(result.status!==0)throw Error('ImageMagick icon packaging failed');}
function square(file,size,padded=false){fs.mkdirSync(path.dirname(file),{recursive:true});const inner=padded?Math.round(size*.88):size;run([source,'-resize',`${inner}x${inner}`,'-background',background,'-alpha','remove','-alpha','off','-gravity','center','-extent',`${size}x${size}`,'-strip','PNG24:'+file]);}
for(const size of [16,32,48,120,152,167,180,192,512])square(path.join(web,`avatar-${size}.png`),size);
square(path.join(web,'avatar-maskable-512.png'),512,true);
run([source,'-background',background,'-alpha','remove','-alpha','off','-define','icon:auto-resize=64,48,32,16',path.join(web,'favicon.ico')]);
const ios=path.join(root,'mobile/ios/SpiritualVibez/Images.xcassets/AppIcon.appiconset');
const entries=[];const generatedIosSizes=new Set();
for(const [idiom,specs] of [['iphone',[[20,[2,3]],[29,[2,3]],[40,[2,3]],[60,[2,3]]]],['ipad',[[20,[1,2]],[29,[1,2]],[40,[1,2]],[76,[1,2]],[83.5,[2]]]],['ios-marketing',[[1024,[1]]]]]){
 for(const [size,scales] of specs)for(const scale of scales){const px=Math.round(size*scale),filename=`avatar-${px}.png`;if(!generatedIosSizes.has(px)){square(path.join(ios,filename),px);generatedIosSizes.add(px)}entries.push({idiom,size:`${size}x${size}`,scale:`${scale}x`,filename});}
}
fs.writeFileSync(path.join(ios,'Contents.json'),JSON.stringify({images:entries,info:{author:'xcode',version:1}},null,2)+'\n');
const res=path.join(root,'mobile/android/app/src/main/res');
for(const [density,scale] of [['mdpi',1],['hdpi',1.5],['xhdpi',2],['xxhdpi',3],['xxxhdpi',4]]){
 const dir=path.join(res,'mipmap-'+density);fs.mkdirSync(dir,{recursive:true});
 square(path.join(dir,'ic_launcher.png'),48*scale);square(path.join(dir,'ic_launcher_round.png'),48*scale);
 const canvas=108*scale,inner=74*scale;
 run([source,'-resize',`${inner}x${inner}`,'-gravity','center','-background','none','-extent',`${canvas}x${canvas}`,'-strip','PNG32:'+path.join(dir,'ic_launcher_foreground.png')]);
}
const adaptive=path.join(res,'mipmap-anydpi-v26');fs.mkdirSync(adaptive,{recursive:true});
for(const name of ['ic_launcher','ic_launcher_round'])fs.writeFileSync(path.join(adaptive,name+'.xml'),'<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/launcher_background" />\n    <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n</adaptive-icon>\n');
fs.writeFileSync(path.join(res,'values/launcher_colors.xml'),'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="launcher_background">'+background+'</color>\n</resources>\n');
console.log('Packaged opaque web/iOS icons and legacy/adaptive Android icons from the full avatar.');
