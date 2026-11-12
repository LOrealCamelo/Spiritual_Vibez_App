"""Reference-home visual layout, live navigation and local-data preservation."""
import json


def exercise_homepage(page, screenshots):
 expected={'daily':('learn',None),'moon':('cosmos',None),'manifest':('explore','rituals'),'natal':('explore','natal'),'tarot':('spreads',None),'journal':('journal',None)}
 # Existing reflections must survive homepage rendering and feature navigation.
 preserved={'sv_private_journal':json.dumps([{'title':'Existing saved reading','text':'Keep this reflection intact.','date':'2026-01-01'}]),'sv_moods':json.dumps([{'mood':'calm','date':'2026-01-01'}])}
 original=page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(preserved))
 page.evaluate('(entries)=>Object.entries(entries).forEach(([key,value])=>localStorage.setItem(key,value))',preserved)
 page.set_viewport_size({'width':390,'height':844})
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
 for width,height,label in [(320,740,'small-phone'),(375,667,'iphone-se'),(390,844,'iphone'),(430,932,'large-phone'),(412,915,'android'),(768,1024,'tablet-portrait'),(1024,768,'tablet-landscape'),(1280,900,'desktop-1280'),(1440,1080,'desktop-1440'),(1920,1080,'desktop-1920'),(959,900,'below-desktop-breakpoint'),(960,900,'desktop-breakpoint')]:
  page.set_viewport_size({'width':width,'height':height});page.evaluate('transition("home")')
  page.evaluate('document.fonts.ready')
  page.locator('img').evaluate_all('(imgs)=>imgs.forEach(n=>n.loading="eager")')
  page.wait_for_function('Array.from(document.images).every(n=>n.complete&&n.naturalWidth>0)')
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),label
  assert page.get_by_role('heading',name='Your journey starts here',exact=True).count()==1
  assert page.locator('.home-feature').count()==6
  assert page.locator('.bottomdock button').count()==6
  assert page.locator('.header-tagline,.home-wall-tagline,.mystic-home .favorite-grid,.mystic-home .more-grid').count()==0
  logo=page.locator('.brand-wordmark img').bounding_box();assert abs(logo['width']/logo['height']-1984/793)<.01
  title=page.locator('.mystic-copy h1').bounding_box();assert title['x']>=0 and title['x']+title['width']<=width+1,label
  assert page.locator('.home-feature').evaluate_all('nodes=>nodes.every(n=>n.clientHeight>=44&&n.getBoundingClientRect().left>=0&&n.getBoundingClientRect().right<=innerWidth)'),label
  assert page.locator('.home-feature-label').evaluate_all('nodes=>nodes.every(n=>n.scrollWidth<=n.clientWidth+1)'),(label,page.locator('.home-feature-label').evaluate_all('nodes=>nodes.map(n=>({text:n.innerText,width:n.clientWidth,scroll:n.scrollWidth}))'))
  desktop=width>=960
  assert page.locator('.topbar .nav').is_visible()==desktop,label
  assert page.locator('.bottomdock').is_visible()!=desktop,label
  assert page.locator('.mystic-tarot-art').is_visible()!=desktop,label
  assert page.locator('.home-light-portal').is_visible()!=desktop,label
  if desktop:
   room=page.locator('.mystic-room-continuation').bounding_box();features=page.locator('.mystic-features').bounding_box();copy=page.locator('.mystic-copy').bounding_box()
   assert abs(room['x'])<1 and abs(room['width']-width)<1,label
   assert abs(room['height']-width/2)<1,(label,room)
   assert abs(room['y']-page.locator('.topbar').bounding_box()['height'])<1,label
   assert abs(features['y']-room['y']-room['height'])<1,(label,room,features)
   assert copy['x']>=0 and copy['x']+copy['width']<=width*.35,label
   assert copy['y']+copy['height']<=room['y']+room['height']*.75,(label,copy,room)
   scene_style=page.locator('.mystic-room-continuation').evaluate('(n)=>{const s=getComputedStyle(n);return {size:s.backgroundSize,mask:s.maskImage}}')
   assert scene_style=={'size':'contain','mask':'none'},(label,scene_style)
   assert page.locator('.topbar .nav button').count()==6
   assert page.locator('.topbar .nav button').evaluate_all('nodes=>nodes.every(n=>n.getBoundingClientRect().right<=innerWidth&&n.getBoundingClientRect().left>=0)'),label
   # There is no empty fixed-height continuation or spacer below the cards.
   moon=page.locator('.mystic-features .home-flourish--moons').bounding_box()
   assert features['y']+features['height']-(moon['y']+moon['height'])<=40,label
  else:
   room=page.locator('.mystic-room-continuation').bounding_box();portal=page.locator('.home-light-portal').bounding_box()
   assert portal['y']>=room['y']+room['height'],label
  boxes=page.locator('.home-feature').evaluate_all('nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})')
  assert len({round(box['y']) for box in boxes})==(1 if width>=1200 else 2),(label,boxes)
  for i,a in enumerate(boxes):
   for b in boxes[i+1:]:assert not (a['x']<b['x']+b['w']-1 and b['x']<a['x']+a['w']-1 and a['y']<b['y']+b['h']-1 and b['y']<a['y']+a['h']-1),(label,a,b)
  for card in page.locator('.home-feature').all():
   card.evaluate('(n)=>n.scrollIntoView({block:"center",behavior:"instant"})')
   assert card.evaluate('(n)=>{const r=n.getBoundingClientRect();return n.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}'),(label,card.get_attribute('aria-label'))
  page.evaluate('window.scrollTo({top:0,behavior:"instant"})');page.mouse.move(0,0);page.screenshot(path=str(screenshots/('home-reference-'+label+'.png')),full_page=True)
 # The desktop top bar and mobile dock must both retain all real destinations.
 for width in [390,1440]:
  page.set_viewport_size({'width':width,'height':900});page.evaluate('state.cardDetail=null;state.learningModule=null;transition("home")')
  nav='.topbar .nav' if width>=960 else '.bottomdock'
  for feature,(route,tool) in expected.items():
   page.locator('[data-home-feature="'+feature+'"]').click();assert page.evaluate('state.page')==route,(width,feature)
   if tool:assert page.evaluate('state.tool')==tool,(width,feature)
   page.locator(nav+' [data-action="nav:home"]').click()
  for route in ['spreads','learn','cosmos','explore','journal','home']:
   page.locator(nav+' [data-action="nav:'+route+'"]').click();assert page.evaluate('state.page')==route,(width,route)
  assert page.evaluate('(keys)=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)]))',list(preserved))==preserved

 page.evaluate('(entries)=>{Object.entries(entries).forEach(([key,value])=>value===null?localStorage.removeItem(key):localStorage.setItem(key,value));state.cardDetail=null;state.learningModule=null;render()}',original)
 print(json.dumps({'reference_home':'full desktop room, six live cards, responsive navigation, unchanged local journal and moods','widths':[320,375,390,430,412,768,1024,1280,1440,1920,959,960]}))
