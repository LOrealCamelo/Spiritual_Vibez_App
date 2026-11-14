"""Exercise result attachments and journal persistence in a real browser."""
import json


def exercise_sharing(page, screenshots):
 # The calling flow has just calculated a real natal chart.
 page.evaluate('''() => {
  window.sharedResults=[];
  Object.defineProperty(navigator,'canShare',{configurable:true,value:({files})=>!!files?.length});
  Object.defineProperty(navigator,'share',{configurable:true,value:async data=>{
   const f=data.files?.[0];window.sharedResults.push({title:data.title,text:data.text,type:f?.type,size:f?.size,signature:f?Array.from(new Uint8Array(await f.arrayBuffer()).slice(0,8)):null});
  }});
 }''')
 page.get_by_role('button',name='Share full Natal Birth Chart',exact=True).first.click()
 page.wait_for_selector('.share-preview img')
 assert page.locator('.share-preview textarea').input_value().find('Get your own here:')>=0
 assert 'wheel_svg' not in page.locator('.share-preview textarea').input_value()
 page.get_by_role('button',name='Share full reading',exact=True).click()
 page.wait_for_function('sharedResults.length===1')
 chart=page.evaluate('sharedResults[0]')
 assert chart['type']=='image/png' and chart['size']>15000,chart
 assert chart['signature']==[137,80,78,71,13,10,26,10]
 assert 'Sample Mystic' in chart['text'] and '#explore/natal' in chart['text']
 assert 'Planets' in chart['text'] or 'Placements' in chart['text']
 assert '<svg' not in chart['text'] and 'wheel_svg' not in chart['text']
 page.locator('.share-preview summary').click()
 with page.expect_download() as download:
  page.get_by_role('link',name='Download full image',exact=True).click()
 download.value.save_as(screenshots/'birth-chart-share.png')
 page.locator('.share-preview').screenshot(path=str(screenshots/'birth-chart-share-preview.png'))
 page.get_by_role('button',name='Close',exact=True).click()

 page.evaluate('transition("explore","bazi")')
 page.locator('#birth-date').fill('1977-06-15');page.locator('#birth-time').fill('12:00')
 page.locator('[data-action="tool-run"]').click();page.wait_for_selector('.result')
 expected=page.evaluate('ContentFormat.readable(state.result)')
 assert 'Fire Snake' in expected and 'Day master' in expected
 page.locator('.complete-reading-share [data-action="content-journal"]').click()
 saved=page.evaluate('JSON.parse(localStorage.getItem("sv_private_journal")).at(-1)')
 assert 'Fire Snake' in saved['text'] and 'day_master' not in saved['text']
 # The full result remains available after a reload and navigation to the journal.
 page.reload(wait_until='networkidle');page.evaluate('transition("journal");state.journalView="saved";render()')
 assert 'Fire Snake' in page.locator('main').inner_text()
 page.evaluate('transition("explore","bazi")');page.locator('#birth-date').fill('1977-06-15');page.locator('[data-action="tool-run"]').click();page.wait_for_selector('.result')
 page.locator('.complete-reading-share [data-action="content-share"]').click();page.wait_for_selector('.share-preview img')
 caption=page.locator('.share-preview textarea').input_value()
 assert 'Fire Snake' in caption and 'Year pillar' in caption and 'Day master' in caption
 assert 'Get your own here: https://app.neurospicymystic.com/#explore/bazi' in caption
 assert 'birth_year' not in caption and 'year_pillar' not in caption and '{' not in caption
 # Without file sharing, offer a PNG download and readable text copy.
 page.evaluate('''() => {window.copiedReading='';Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.copiedReading=text}}})}''')
 page.locator('.share-preview summary').click()
 page.get_by_role('button',name='Copy full reading and link',exact=True).click()
 assert page.evaluate('copiedReading')==caption
 page.locator('.share-preview').screenshot(path=str(screenshots/'bazi-share-preview.png'))
 page.get_by_role('button',name='Close',exact=True).click()
 page.evaluate('Object.defineProperty(navigator,"canShare",{configurable:true,value:()=>false})')
 page.locator('.complete-reading-share [data-action="content-share"]').click();page.wait_for_selector('.share-preview img')
 assert page.get_by_role('button',name='Share full reading',exact=True).count()==1
 page.locator('.share-preview summary').click()
 with page.expect_download() as download:page.get_by_role('link',name='Download full image',exact=True).click()
 assert download.value.suggested_filename.endswith('.png')
 page.get_by_role('button',name='Close',exact=True).click()

 # Storage failure must not claim that a reading was saved.
 notices=[];page.once('dialog',lambda d:notices.append(d.message))
 before=page.evaluate('localStorage.getItem("sv_private_journal")')
 page.evaluate('() => {window.originalSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key==="sv_private_journal")throw new Error("Storage full");return window.originalSetItem.call(this,key,value)}}')
 try:
  page.locator('.complete-reading-share [data-action="content-journal"]').click()
  assert notices and 'Could not add' in notices[0],notices
  assert page.evaluate('localStorage.getItem("sv_private_journal")')==before
 finally:page.evaluate('() => {Storage.prototype.setItem=window.originalSetItem}')
 # Dismissing the phone share sheet is a normal cancellation.
 page.evaluate('Object.defineProperty(navigator,"canShare",{configurable:true,value:()=>true});Object.defineProperty(navigator,"share",{configurable:true,value:async()=>{window.shareCancelled=true;throw new DOMException("Cancelled","AbortError")}})')
 page.locator('.complete-reading-share [data-action="content-share"]').click();page.wait_for_selector('.share-preview img')
 page.get_by_role('button',name='Share full reading',exact=True).click();page.wait_for_function('window.shareCancelled')
 assert 'Sharing did not finish' not in page.locator('.share-preview').inner_text()
 page.get_by_role('button',name='Close',exact=True).click()

 # One share/save pair only when there is a complete, shareable reading.
 page.evaluate('''() => {
  transition('spreads');
  const spread=state.spreads.find(x=>x.questions?.length>=4);
  state.selected=spread;
  state.drawn=Object.fromEntries(spread.questions.map((q,i)=>[q.slot,{
   slot:q.slot,card:{...state.cards[i],orientation:'Upright',meaning:state.cards[i].upright}
  }]));
  state.reading='All four cards invite an intentional next step.';
  render();
 }''')
 assert page.locator('.complete-reading-share [data-action="content-share"]').count()==1
 assert page.locator('.complete-reading-share [data-action="content-journal"]').count()==1
 assert page.locator('.slot [data-action="content-share"]').count()==0
 reading=page.evaluate('''() => {
  const item=[...contentItems.values()][0];
  return {text:item.text,images:item.images.length,questions:state.selected.questions.length};
 }''')
 assert reading['images']==reading['questions'],reading
 assert all(word in reading['text'] for word in ['Question:','Drawn card:','Card meaning:','Overall interpretation']),reading
 page.locator('.complete-reading-share [data-action="content-share"]').click()
 page.wait_for_selector('.share-preview img')
 assert 'All four cards invite an intentional next step.' in page.locator('.share-preview textarea').input_value()
 page.get_by_role('button',name='Close',exact=True).click()

 for route in ['home','spreads','learn','cosmos','explore','journal']:
  page.evaluate('(route)=>transition(route)',route)
  if route=='learn':page.evaluate('state.learningModule="all";render()')
  assert page.locator('main .content-card').count()==0,route
  assert page.locator('main [data-action="content-share"]').count()<=1,route
  if route=='home':assert page.locator('.home-feature').count()==6
  assert page.locator('main button button').count()==0,route
  if route=='learn':assert page.locator('.deck-card').count()==78
  if route=='explore':assert page.locator('.explore-card').count()==18
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),route
 print(json.dumps({'sharing':'PNG attachment, readable caption, canonical invitation, download/copy fallback','journal':'full BaZi reading survives reload','card_actions':'one complete-reading action pair, no fragmented card controls'}))
