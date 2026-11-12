"""Mobile portal restoration and fixed-dock scroll clearance regressions."""
import json


def exercise_portal(page, screenshots):
 client=page.context.new_cdp_session(page)
 for width,height in [(320,740),(375,667),(390,844),(430,932)]:
  page.set_viewport_size({'width':width,'height':height});page.evaluate('transition("home")');page.evaluate('document.fonts.ready')
  page.locator('img').evaluate_all('(imgs)=>imgs.forEach(n=>n.loading="eager")');page.wait_for_function('Array.from(document.images).every(n=>n.complete&&n.naturalWidth>0)')
  portal=page.locator('.home-light-portal');assert portal.is_visible(),width
  assert 'home-light-portal.png' in portal.evaluate('(n)=>getComputedStyle(n,"::before").backgroundImage')
  assert page.locator('.home-feature').count()==6
  assert portal.locator('.picture-tile').count()==4 and portal.locator('.favorite-card').count()==4 and portal.locator('.extra-card').count()==4
  room=page.locator('.mystic-room-continuation').bounding_box();first=portal.locator('.home-quick-actions').bounding_box()
  assert first['y']>=room['y']+room['height'],(width,room,first)
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
  grid=page.locator('.home-feature-grid');grid.evaluate('(n)=>n.scrollIntoView({block:"end",behavior:"instant"})')
  dock=page.locator('.bottomdock').bounding_box();cards=grid.bounding_box()
  assert cards['y']+cards['height']<=dock['y']-8,(width,cards,dock)
  assert cards['y']>=page.locator('.topbar').bounding_box()['height'],(width,cards)
  for card in page.locator('.home-feature').all():
   card.scroll_into_view_if_needed();box=card.bounding_box();nav=page.locator('.bottomdock').bounding_box()
   assert box['y']+box['height']<=nav['y']-4,(width,box,nav)
   assert card.evaluate('(n)=>n.contains(document.elementFromPoint(n.getBoundingClientRect().x+n.clientWidth/2,n.getBoundingClientRect().y+n.clientHeight/2))')
  page.screenshot(path=str(screenshots/f'mobile-six-cards-clear-{width}.png'))
  for card in portal.locator('.picture-tile,.favorite-card,.extra-card').all():
   card.scroll_into_view_if_needed();box=card.bounding_box();nav=page.locator('.bottomdock').bounding_box()
   assert box['y']+box['height']<=nav['y']-4,(width,card.get_attribute('aria-label'),box,nav)
  page.evaluate('window.scrollTo({top:document.documentElement.scrollHeight,behavior:"instant"})')
  last=portal.locator('[data-action="nav:explore"]').bounding_box();nav=page.locator('.bottomdock').bounding_box()
  assert last['y']+last['height']<=nav['y']-8,(width,last,nav)
  assert page.evaluate('getComputedStyle(document.documentElement).backgroundColor')=='rgb(238, 229, 247)'
  page.locator('.home-light-portal .feature-grid').evaluate('(n)=>n.scrollIntoView({block:"start",behavior:"instant"})');page.screenshot(path=str(screenshots/f'mobile-restored-portal-{width}.png'))
 # Exercise the original portal destinations through the real delegated handlers.
 targets=[('Open Daily Card','learn',None),('Open Shuffle a Spread','spreads',None),('Open Learn Tarot','learn',None),('Open Birth Chart','explore','natal'),('Open Moon Phase','cosmos',None),('Open Numerology','explore','numbers'),('Open Saved Readings','journal',None),('Open Rituals','explore','rituals')]
 for label,route,tool in targets:
  page.evaluate('state.selected=null;transition("home")');page.locator('.home-light-portal').get_by_role('button',name=label,exact=True).click()
  assert page.evaluate('state.page')==route,label
  if tool:assert page.evaluate('state.tool')==tool,label
 for name in ['Reset Your Energy','Trust Your Gut','The Next Phase','Grounding']:
  page.evaluate('state.selected=null;transition("home")');page.locator('.home-light-portal').get_by_role('button',name='Open '+name+' spread',exact=True).click()
  assert page.evaluate('state.selected.title')==name
 # Simulate the iPhone bottom safe area in Chromium when this CDP API is available.
 client.send('Emulation.setSafeAreaInsetsOverride',{'insets':{'top':0,'left':0,'right':0,'bottom':34}})
 page.set_viewport_size({'width':390,'height':844});page.evaluate('state.selected=null;transition("home")')
 assert page.locator('.bottomdock').evaluate('(n)=>parseFloat(getComputedStyle(n).bottom)')>=44
 page.locator('.home-feature-grid').evaluate('(n)=>n.scrollIntoView({block:"end",behavior:"instant"})')
 grid=page.locator('.home-feature-grid').bounding_box();dock=page.locator('.bottomdock').bounding_box();assert grid['y']+grid['height']<dock['y']-8
 page.screenshot(path=str(screenshots/'mobile-iphone-safe-area.png'))
 client.send('Emulation.setSafeAreaInsetsOverride',{'insets':{'top':0,'left':0,'right':0,'bottom':0}})
 for width in [1024,1448]:
  page.set_viewport_size({'width':width,'height':1086});page.evaluate('transition("home")');assert not page.locator('.home-light-portal').is_visible();assert page.locator('.home-feature').count()==6
 page.evaluate('state.selected=null;state.cardDetail=null;state.learningModule=null;transition("home")')
 print(json.dumps({'restored_portal':'original image and 12 original web cards below the table','widths':[320,375,390,430],'dock':'fixed, keyboard/scroll clearance and 34px iPhone safe area','desktop':'portal hidden; current design retained'}))
