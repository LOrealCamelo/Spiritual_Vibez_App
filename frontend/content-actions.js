/* Shareable PNG previews and local journal actions for every card and feature. */
'use strict';
const contentItems=new Map();let contentSequence=0,sharePreview=null;
function contentActionMarkup(item){
 const key=String(++contentSequence);contentItems.set(key,item);
 return '<div class="content-actions" data-content-actions><button type="button" data-action="content-share" data-content="'+key+'" aria-label="Share '+e(item.title)+'">Share</button><button type="button" data-action="content-journal" data-content="'+key+'" aria-label="Add '+e(item.title)+' to journal">Add to journal</button></div>';
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
function installContentActions(){
 if(!document.body||!document.querySelectorAll)return;
 contentItems.clear();
 document.querySelectorAll('main button.picture-tile,main button.favorite-card,main button.extra-card,main button.art-button,main button.listbutton,main button.explore-card,main button.tooltile,main button.deck-card,main button.slot').forEach(node=>{
  const item=cardContent(node),wrap=document.createElement('article');wrap.className='content-card';
  node.replaceWith(wrap);wrap.append(node);wrap.insertAdjacentHTML('beforeend',contentActionMarkup(item));
 });
 const context=currentContent();
 document.querySelectorAll('main .result,main .birth-report,main .moon-detail,main #selected-card,main .reference-grid>section,main .reading-board,main .report-section,main .tiles>.glass,main .glass:not(.spread-search)').forEach(node=>{
  if(node.querySelector(':scope>[data-content-actions]'))return;
  const title=node.querySelector('h2,h3,h4,strong,b')?.textContent?.trim()||context.title;
  const base=context,item={...base,title,getSnapshot:()=>({...base,title,text:node.matches(".result,.birth-report")&&state.result?ContentFormat.readable(state.result):visibleContentText(node)})};
  node.insertAdjacentHTML('beforeend',contentActionMarkup(item));
 });
 if(state.page!=='home'){
  const anchor=document.querySelector('main .tool-heading,main .natal-tool-heading,main .page-head,main .art-header');
  const row=contentActionMarkup({...currentContent(),getSnapshot:currentContent});
  if(anchor)anchor.insertAdjacentHTML('afterend',row);else document.querySelector('main').insertAdjacentHTML('beforeend',row);
 }
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
 ctx.font='600 42px Arial';const titleLines=wrapExportText(ctx,item.title,936);
 ctx.font='28px Arial';const lines=wrapExportText(ctx,ContentFormat.summary(item,2100),936);
 let picture=null,svgUrl=null;
 try{if(item.imageSvg){svgUrl=URL.createObjectURL(new Blob([item.imageSvg],{type:'image/svg+xml'}));picture=await loadExportImage(svgUrl);}else if(item.imageUrl)picture=await loadExportImage(item.imageUrl);}catch{/* The complete result still appears as readable text. */}
 let logo=null;try{logo=await loadExportImage('assets/spiritual-vibz-logo-compact.png');}catch{}
 const pictureHeight=picture?Math.min(660,936*picture.height/picture.width):0;
 canvas.height=240+titleLines.length*54+(picture?pictureHeight+36:0)+lines.length*39+196;
 const bg=ctx.createLinearGradient(0,0,1080,canvas.height);bg.addColorStop(0,'#f4ecff');bg.addColorStop(1,'#f7e9f2');ctx.fillStyle=bg;ctx.fillRect(0,0,1080,canvas.height);
 if(logo)ctx.drawImage(logo,72,40,320,320*793/1984);
 ctx.fillStyle='#35174d';ctx.font='600 42px Arial';let y=218;
 for(const line of titleLines){ctx.fillText(line,72,y);y+=54;}
 if(picture){y+=14;const w=pictureHeight*picture.width/picture.height;ctx.drawImage(picture,(1080-w)/2,y,w,pictureHeight);y+=pictureHeight+36;}
 ctx.font='28px Arial';for(const line of lines){ctx.fillText(line,72,y);y+=39;}
 ctx.fillStyle='#b31380';ctx.fillRect(72,y+24,936,2);ctx.font='bold 30px Arial';ctx.fillText('Get your own here',72,y+85);ctx.fillStyle='#35174d';ctx.font='24px Arial';ctx.fillText(item.url,72,y+129);
 if(svgUrl)URL.revokeObjectURL(svgUrl);
 return new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error('Could not create the result image.')),'image/png'));
}
function closeContentPreview(){if(!sharePreview)return;sharePreview.dialog.close?.();sharePreview.dialog.remove();if(sharePreview.url)URL.revokeObjectURL(sharePreview.url);sharePreview=null;}
async function previewContentShare(item){
 closeContentPreview();const snapshot=resolveContent(item),dialog=document.createElement('dialog');dialog.className='share-preview';dialog.setAttribute('aria-label','Share '+snapshot.title);
 dialog.innerHTML='<h2 tabindex="-1" autofocus>'+e(snapshot.title)+'</h2><p role="status">Preparing your result image…</p><div class="share-preview-art"></div><label>Reading text and link<textarea readonly rows="3">'+e(ContentFormat.message(snapshot))+'</textarea></label><div class="share-preview-actions"><button class="btn" data-action="content-send" disabled>Share image &amp; text</button><a class="btn" data-export-download download>Download image</a><button class="btn" data-action="content-copy">Copy text and link</button><button class="btn" data-action="content-close">Close</button></div>';
 document.body.append(dialog);sharePreview={dialog,item:snapshot,file:null,url:null};dialog.showModal?dialog.showModal():dialog.setAttribute('open','');
 dialog.addEventListener('close',()=>{if(sharePreview?.dialog===dialog)closeContentPreview();});
 try{const blob=await makeContentImage(snapshot);if(sharePreview?.dialog!==dialog)return;
  const filename=(snapshot.title.replace(/[^a-z0-9]+/gi,'-').replace(/^-|-$/g,'')||'Spiritual-Vibz')+'.png';const file=new File([blob],filename,{type:'image/png'}),url=URL.createObjectURL(blob);
  Object.assign(sharePreview,{file,url});dialog.querySelector('.share-preview-art').innerHTML='<img alt="Result image preview" src="'+url+'">';const link=dialog.querySelector('[data-export-download]');link.href=url;link.download=filename;
  const files=!!navigator.canShare?.({files:[file]});const send=dialog.querySelector('[data-action="content-send"]');send.disabled=!navigator.share;send.textContent=files?'Share image & text':'Share text and link';
  dialog.querySelector('h2').focus({preventScroll:true});dialog.scrollTop=0;
  dialog.querySelector('[role="status"]').textContent=files?'Share the result image, reading text and app link.':'Download the image, then share or copy the reading text and app link below.';
 }catch{dialog.querySelector('[role="status"]').textContent='The image could not be prepared. You can still copy the complete reading and link.';}
}
async function sendContentPreview(){
 const p=sharePreview;if(!p?.file)return;const data={title:p.item.title,text:ContentFormat.message(p.item)};if(navigator.canShare?.({files:[p.file]}))data.files=[p.file];
 try{await navigator.share(data);}catch(error){if(error.name!=='AbortError')p.dialog.querySelector('[role="status"]').textContent='Sharing did not finish. You can download the image and copy the text and link.';}
}
async function copyContentPreviewText(){
 const p=sharePreview;if(!p)return;const text=ContentFormat.message(p.item);
 try{await navigator.clipboard.writeText(text);p.dialog.querySelector('[role="status"]').textContent='Copied the reading and app link.';}catch{prompt('Copy the reading and link:',text);}
}
