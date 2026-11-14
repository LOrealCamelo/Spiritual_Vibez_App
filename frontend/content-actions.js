/* Shareable PNG previews and local journal actions for every card and feature. */
'use strict';
const contentItems=new Map();let contentSequence=0,sharePreview=null;
function contentActionMarkup(item){
 const key=String(++contentSequence);contentItems.set(key,item);
 return '<div class="content-actions" data-content-actions><button type="button" data-action="content-share" data-content="'+key+'" aria-label="Share full '+e(item.title)+'">Share full reading</button><button type="button" data-action="content-journal" data-content="'+key+'" aria-label="Save full '+e(item.title)+' to journal">Save full reading to Journal</button></div>';
}
function visibleContentText(node){
 const copy=node.cloneNode(true);
 const originals=[...node.querySelectorAll('input,select,textarea')];
 copy.querySelectorAll('input,select,textarea').forEach((field,i)=>{const source=originals[i],text=source.tagName==='SELECT'?source.selectedOptions?.[0]?.textContent:source.value;field.replaceWith(document.createTextNode(text||''));});
 copy.querySelectorAll('[data-content-actions],button,nav,svg,script,style,.share-preview').forEach(n=>n.remove());
 copy.querySelectorAll('p,div,section,article,h1,h2,h3,h4,li,tr,br').forEach(n=>n.append(document.createTextNode('\n')));
 return copy.textContent.replace(/[ \t]+/g,' ').replace(/\n[ \t]+/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
}
function currentContent(){
 const route=state.page+(state.page==='explore'&&state.tool?'/'+state.tool:'');
 const title=state.page==='explore'&&state.tool?getTool(state.tool)?.[2]:state.page==='spreads'&&state.selected?state.selected.title:state.page==='learn'&&state.cardDetail?state.cardDetail.name:{home:'Spiritual Vibz',spreads:'Tarot spreads',learn:'Learn Tarot',cosmos:'Moon cycles & daily reflection',journal:'My Journal'}[state.page];
 const result=state.page==='explore'?state.result:state.page==='learn'?state.cardDetail:null;
 return ContentFormat.snapshot({title,route,text:result?undefined:visibleContentText(document.querySelector('main.container')),value:result,imageUrl:state.page==='learn'?document.querySelector('#selected-card img')?.src:undefined,imageSvg:result?.wheel_svg||result?.map_svg||result?.moon_image_svg||(state.page==='cosmos'?state.transit?.moon?.image_svg:undefined)});
}
function cardContent(node){
 const a=node.dataset.action,id=node.dataset.id;
 if(a==='card'){const c=state.cards.find(x=>String(x.id)===node.dataset.card);if(c)return ContentFormat.snapshot({title:c.name,value:c,route:'learn',imageUrl:node.querySelector('img')?.src});}
 if(a==='draw'){const q=state.selected.questions.find(x=>x.slot===Number(node.dataset.slot)),d=state.drawn[Number(node.dataset.slot)];return ContentFormat.snapshot({title:d?d.card.name:state.selected.title+' — '+q.title,text:[q.q,d?.card.orientation,d?.card.meaning].filter(Boolean).join('\n\n'),route:'spreads',imageUrl:node.querySelector('img')?.src});}
 const spread=a==='select-spread'?state.spreads.find(x=>x.id===id):a==='favorite'?state.spreads.find(x=>x.title===node.dataset.name):null;
 if(spread)return ContentFormat.snapshot({title:spread.title,value:{description:spread.desc||'A reflective tarot spread',questions:spread.questions.map(x=>x.q)},route:'spreads'});
 const tool=a?.startsWith('tool:')?getTool(a.slice(5)):null;
 const panel=CARD_PANELS[node.dataset.panel];
 return ContentFormat.snapshot({title:tool?.[2]||panel?.title||node.getAttribute('aria-label')||node.innerText.trim(),text:tool?.[3]||panel?.description||node.innerText.trim(),route:tool?'explore/'+tool[0]:a?.startsWith('nav:')?a.slice(4):state.page,imageUrl:node.classList.contains('favorite-card')?node.querySelector('img')?.src:undefined});
}

function fullSpreadSnapshot(){
 if(state.page!=='spreads'||!state.selected||!state.reading)return null;
 const spread=state.selected,questions=spread.questions||[],images=[];
 const paragraphs=[spread.title,spread.desc?'About this spread: '+spread.desc:'A reflective tarot spread'];
 for(const q of questions){
  const slot=state.drawn[q.slot],card=slot?.card;
  paragraphs.push('Position '+q.slot+': '+(q.title||'Card '+q.slot)+'\nQuestion: '+(q.q||'')+'\nDrawn card: '+(card?.name||'Not yet revealed')+(card?.orientation?' ('+card.orientation+')':'')+'\nCard meaning: '+(card?.meaning||card?.upright||'Not yet interpreted'));
  const src=document.querySelector('main .slot[data-slot="'+q.slot+'"] img')?.src;
  if(card&&src)images.push({src,label:q.slot+'. '+card.name});
 }
 paragraphs.push('Overall interpretation\n'+state.reading);
 const item=ContentFormat.snapshot({title:spread.title+' — Complete Tarot Spread',text:paragraphs.filter(Boolean).join('\n\n'),route:'spreads'});
 return {...item,images};
}
function wholeReadingSnapshot(){
 if(state.page==='spreads')return fullSpreadSnapshot();
 if(state.page==='learn'){
  if(state.learningModule==='quiz'&&state.quiz&&state.answer){
   const q=state.quiz;
   return ContentFormat.snapshot({title:'Tarot Learning — '+q.card_name,text:'Card: '+q.card_name+'\nQuestion: '+(q.prompt||'What does this card represent?')+'\nYour result: '+state.answer+'\nCorrect answer: '+q.correct_answer,route:'learn',imageUrl:document.querySelector('main .glass img')?.src});
  }
  if(state.cardDetail)return currentContent();
  return null;
 }
 if(state.page==='explore'){
  if(!state.tool)return null;
  if(state.tool==='runes')return RuneCasting.snapshot();
  // Private Shadow Work writing is only shared deliberately from the Journal.
  if(state.tool==='shadow')return null;
  if(state.result)return currentContent();
  if(['houses','numbers','rituals'].includes(state.tool))return currentContent();
  return null;
 }
 if(state.page==='cosmos'){
  if(!state.transit)return null;
  return currentContent();
 }
 return null;
}
function installContentActions(){
 if(!document.body)return;
 contentItems.clear();
 document.querySelectorAll('main .complete-reading-share').forEach(n=>n.remove());
 const item=wholeReadingSnapshot();
 if(!item)return;
 const main=document.querySelector('main.container');if(!main)return;
 const section=document.createElement('section');
 section.className='complete-reading-share';
 section.setAttribute('aria-label','Your complete reading actions');
 section.innerHTML='<div class="complete-reading-label">✦ Your complete reading</div><p>Share or privately save the full result, with all its details together.</p>'+contentActionMarkup(item);
 main.append(section);
}
function resolveContent(item){return item.getSnapshot?item.getSnapshot():item;}
async function addContentToJournal(item){
 const snapshot=resolveContent(item);
 try{save(snapshot.title,snapshot.text);alert('Added to the Journal on this device.');}
 catch{alert('Could not add this to your journal. Please check the available storage on this device.');}
}
function loadExportImage(source){return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=source;});}
function wrapExportText(ctx,text,width){
 const lines=[];for(const paragraph of String(text).split('\n')){let line='';for(const word of paragraph.split(/\s+/)){if(!word)continue;const next=line?line+' '+word:word;if(ctx.measureText(next).width>width&&line){lines.push(line);line=word;}else line=next;}lines.push(line);}return lines;
}
async function makeContentImage(item){
 const canvas=document.createElement('canvas');canvas.width=1080;const ctx=canvas.getContext('2d');
 const fullGallery=Array.isArray(item.images)&&item.images.length>0;
 const exportText=fullGallery?item.text:ContentFormat.summary(item,2100);
 ctx.font='600 42px Arial';const titleLines=wrapExportText(ctx,item.title,936);
 ctx.font='28px Arial';const lines=wrapExportText(ctx,exportText,936);
 let picture=null,svgUrl=null;const gallery=[];
 try{if(item.imageSvg){svgUrl=URL.createObjectURL(new Blob([item.imageSvg],{type:'image/svg+xml'}));picture=await loadExportImage(svgUrl);}else if(item.imageUrl)picture=await loadExportImage(item.imageUrl);}catch{/* Export text remains available. */}
 if(fullGallery){
  for(const entry of item.images.slice(0,24)){try{gallery.push({picture:await loadExportImage(entry.src),label:entry.label||''})}catch{/* Keep the full textual reading. */}}
 }
 let logo=null;try{logo=await loadExportImage('assets/spiritual-vibz-logo-compact.png');}catch{}
 const pictureHeight=picture?Math.min(660,936*picture.height/picture.width):0;
 const cols=gallery.length<=2?gallery.length:3,tileW=cols?Math.floor((936-20*(cols-1))/cols):0;
 const tileH=gallery.length?Math.floor(tileW*1.55)+43:0;
 const galleryHeight=gallery.length?Math.ceil(gallery.length/cols)*tileH+35:0;
 canvas.height=240+titleLines.length*54+(picture?pictureHeight+36:0)+galleryHeight+lines.length*39+196;
 const bg=ctx.createLinearGradient(0,0,1080,canvas.height);bg.addColorStop(0,'#f4ecff');bg.addColorStop(1,'#f7e9f2');ctx.fillStyle=bg;ctx.fillRect(0,0,1080,canvas.height);
 if(logo)ctx.drawImage(logo,72,40,320,320*793/1984);
 ctx.fillStyle='#35174d';ctx.font='600 42px Arial';let y=218;
 for(const line of titleLines){ctx.fillText(line,72,y);y+=54;}
 if(picture){y+=14;const w=pictureHeight*picture.width/picture.height;ctx.drawImage(picture,(1080-w)/2,y,w,pictureHeight);y+=pictureHeight+36;}
 if(gallery.length){
  y+=14;
  gallery.forEach(({picture:pic,label},i)=>{
   const col=i%cols,row=Math.floor(i/cols),x=72+col*(tileW+20),top=y+row*tileH;
   const maxImageH=tileH-49,scale=Math.min(tileW/pic.width,maxImageH/pic.height);
   const w=pic.width*scale,h=pic.height*scale;
   ctx.drawImage(pic,x+(tileW-w)/2,top,w,h);
   ctx.fillStyle='#35174d';ctx.font='bold 19px Arial';
   const shortLabel=label.length>30?label.slice(0,27)+'…':label;
   ctx.fillText(shortLabel,x,top+maxImageH+27);
  });
  y+=galleryHeight;
 }
 ctx.fillStyle='#35174d';ctx.font='28px Arial';
 for(const line of lines){ctx.fillText(line,72,y);y+=39;}
 ctx.fillStyle='#b31380';ctx.fillRect(72,y+24,936,2);ctx.font='bold 30px Arial';ctx.fillText('Explore SpiritualVibz',72,y+85);ctx.fillStyle='#35174d';ctx.font='24px Arial';ctx.fillText(item.url,72,y+129);
 if(svgUrl)URL.revokeObjectURL(svgUrl);
 return new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error('Could not create the result image.')),'image/png'));
}
function closeContentPreview(){if(!sharePreview)return;sharePreview.dialog.close?.();sharePreview.dialog.remove();if(sharePreview.url)URL.revokeObjectURL(sharePreview.url);sharePreview=null;}
async function previewContentShare(item){
 closeContentPreview();const snapshot=resolveContent(item),dialog=document.createElement('dialog');dialog.className='share-preview';dialog.setAttribute('aria-label','Share '+snapshot.title);
 dialog.innerHTML='<h2 tabindex="-1" autofocus>'+e(snapshot.title)+'</h2><p class="share-privacy-note">This shares the complete result, including any birth details or personal reflections it contains. Please review before sending.</p><p role="status">Preparing your result image…</p><div class="share-preview-art"></div><label>Reading text and link<textarea readonly rows="3">'+e(ContentFormat.message(snapshot))+'</textarea></label><div class="share-preview-actions"><button class="btn" data-action="content-send" disabled>Share full reading</button><details><summary>More sharing options</summary><a class="btn" data-export-download download>Download full image</a><button class="btn" data-action="content-copy">Copy full reading and link</button></details><button class="btn" data-action="content-close">Close</button></div>';
 document.body.append(dialog);sharePreview={dialog,item:snapshot,file:null,url:null};dialog.showModal?dialog.showModal():dialog.setAttribute('open','');
 dialog.addEventListener('close',()=>{if(sharePreview?.dialog===dialog)closeContentPreview();});
 try{const blob=await makeContentImage(snapshot);if(sharePreview?.dialog!==dialog)return;
  const filename=(snapshot.title.replace(/[^a-z0-9]+/gi,'-').replace(/^-|-$/g,'')||'Spiritual-Vibz')+'.png';const file=new File([blob],filename,{type:'image/png'}),url=URL.createObjectURL(blob);
  Object.assign(sharePreview,{file,url});dialog.querySelector('.share-preview-art').innerHTML='<img alt="Result image preview" src="'+url+'">';const link=dialog.querySelector('[data-export-download]');link.href=url;link.download=filename;
  const files=!!navigator.canShare?.({files:[file]});const send=dialog.querySelector('[data-action="content-send"]');send.disabled=!navigator.share;send.textContent='Share full reading';
  dialog.querySelector('h2').focus({preventScroll:true});dialog.scrollTop=0;
  dialog.querySelector('[role="status"]').textContent=files?'Share the result image, reading text and app link.':'Download the image, then share or copy the reading text and app link below.';
 }catch{const send=dialog.querySelector('[data-action="content-send"]');send.disabled=!navigator.share;send.textContent='Share full reading';dialog.querySelector('[role="status"]').textContent='The image could not be prepared. You can still share or copy the complete reading and link.';}
}
async function sendContentPreview(){
 const p=sharePreview;if(!p)return;const data={title:p.item.title,text:ContentFormat.message(p.item)};if(p.file&&navigator.canShare?.({files:[p.file]}))data.files=[p.file];
 try{await navigator.share(data);}catch(error){if(error.name!=='AbortError')p.dialog.querySelector('[role="status"]').textContent='Sharing did not finish. You can download the image and copy the text and link.';}
}
async function copyContentPreviewText(){
 const p=sharePreview;if(!p)return;const text=ContentFormat.message(p.item);
 try{await navigator.clipboard.writeText(text);p.dialog.querySelector('[role="status"]').textContent='Copied the reading and app link.';}catch{prompt('Copy the reading and link:',text);}
}
