"""Reference-home visual layout, live navigation and local-data preservation."""
import json


def exercise_homepage(page, screenshots):
 expected={'daily':('learn',None),'moon':('cosmos',None),'manifest':('explore','rituals'),'natal':('explore','natal'),'tarot':('spreads',None),'journal':('journal',None)}
 # Existing reflections must survive homepage rendering and feature navigation.
 preserved={'sv_private_journal':json.dumps([{'title':'Existing saved reading','text':'Keep this reflection intact.','date':'2026-01-01'}]),'sv_moods':json.dumps([{'mood':'calm','date':'2026-01-01'}])}
 original=page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(preserved))
 page.evaluate('(entries)=>Object.entries(entries).forEach(([key,value])=>localStorage.setItem(key,value))',preserved)
 for feature,(route,tool) in expected.items():
  page.evaluate('transition("home")')
  page.locator('[data-home-feature="'+feature+'"]').click()
  assert page.evaluate('state.page')==route,feature
  if tool:assert page.evaluate('state.tool')==tool,feature
  if feature=='daily':assert page.locator('#selected-card .tarot-image').count()==1
  if feature=='manifest':
   page.locator('#search').fill('abundance');page.locator('[data-action="tool-run"]').click();page.wait_for_selector('.result')
   assert 'Abundance' in page.locator('.result').inner_text()
  if feature=='natal':assert page.locator('#birth-date').count()==1
  page.locator('.bottomdock [data-action="nav:home"]').click()
  assert page.locator('.home-feature').count()==6
 for route in ['spreads','learn','cosmos','explore','journal','home']:
  page.locator('.bottomdock [data-action="nav:'+route+'"]').click();assert page.evaluate('state.page')==route
 assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(preserved))==preserved
 for width,height,label in [(1448,1086,'desktop'),(390,844,'iphone'),(412,915,'android'),(320,740,'small-phone'),(768,1024,'tablet'),(2560,1440,'large-desktop')]:
  page.set_viewport_size({'width':width,'height':height});page.evaluate('transition("home")')
  page.evaluate('document.fonts.ready')
  page.locator('img').evaluate_all('(imgs)=>imgs.forEach(n=>n.loading="eager")')
  page.wait_for_function('Array.from(document.images).every(n=>n.complete&&n.naturalWidth>0)')
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),label
  assert page.get_by_role('heading',name='Your journey starts here',exact=True).count()==1
  assert page.locator('.home-feature').count()==6
  assert page.locator('.bottomdock button').count()==6
  assert page.locator('.header-tagline,.home-wall-tagline,.favorite-grid,.more-grid').count()==0
  logo=page.locator('.brand-wordmark img').bounding_box();assert abs(logo['width']/logo['height']-1984/793)<.01
  title=page.locator('.mystic-copy h1').bounding_box();assert title['x']>=0 and title['x']+title['width']<=width+1,label
  assert page.locator('.home-feature').evaluate_all('nodes=>nodes.every(n=>n.clientHeight>=44&&n.getBoundingClientRect().left>=0&&n.getBoundingClientRect().right<=innerWidth)'),label
  assert page.locator('.home-feature-label').evaluate_all('nodes=>nodes.every(n=>n.scrollWidth<=n.clientWidth+1)'),(label,page.locator('.home-feature-label').evaluate_all('nodes=>nodes.map(n=>({text:n.innerText,width:n.clientWidth,scroll:n.scrollWidth}))'))
  boxes=page.locator('.home-feature').evaluate_all('nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})')
  for i,a in enumerate(boxes):
   for b in boxes[i+1:]:assert not (a['x']<b['x']+b['w']-1 and b['x']<a['x']+a['w']-1 and a['y']<b['y']+b['h']-1 and b['y']<a['y']+a['h']-1),(label,a,b)
  page.evaluate('window.scrollTo({top:0,behavior:"instant"})');page.screenshot(path=str(screenshots/('home-reference-'+label+'.png')))
 page.evaluate('(entries)=>{Object.entries(entries).forEach(([key,value])=>value===null?localStorage.removeItem(key):localStorage.setItem(key,value));state.cardDetail=null;state.learningModule=null;render()}',original)
 print(json.dumps({'reference_home':'six live cards, six bottom destinations, unchanged local journal and moods','sizes':['desktop','iPhone','Android','small phone','tablet','large desktop']}))
