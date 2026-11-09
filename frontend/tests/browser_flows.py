"""Connected browser checks for every tool route, illustrated actions and desktop/phone layouts.

Run after installing frontend/tests/requirements.txt. Uses an installed Chrome or
Chromium; starts FastAPI with a temporary database unless --base-url is supplied.
"""
import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright


def exercise(base_url, screenshots):
 browser_path=os.environ.get('BROWSER_EXECUTABLE') or shutil.which('google-chrome') or shutil.which('chromium')
 if not browser_path:raise RuntimeError('Install Chrome/Chromium or set BROWSER_EXECUTABLE')
 screenshots.mkdir(parents=True,exist_ok=True)
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=browser_path,headless=True,args=['--no-sandbox'])
  page=b.new_page(viewport={'width':1448,'height':1086})
  failures=[];requests=[];errors=[]
  page.on('response',lambda r: failures.append((r.url,r.status)) if '/api/' in r.url and r.status>=400 else None)
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base_url,wait_until='networkidle')
  page.on('dialog',lambda d:d.accept())
  page.wait_for_function('state.online===true')
  for title,spread_id in [('Reset Your Energy','reset-energy'),('Trust Your Gut','trust-your-gut'),('The Next Phase','stepping-into-new-timeline'),('Grounding','mindfulness-calm')]:
   page.evaluate('transition("home")')
   page.get_by_role('button',name='Open '+title+' spread',exact=True).click()
   assert page.evaluate('state.selected.id')==spread_id,(title,spread_id)
   page.get_by_role('button',name='← All spreads',exact=True).click()
  page.evaluate('transition("spreads")');page.get_by_role('button',name='Filter by Career',exact=True).click()
  assert page.locator('[data-action="vibe"][data-vibe="Career"]').get_attribute('aria-pressed')=='true'
  assert page.locator('[data-action="select-spread"][data-id="career-shift"]').count()==1
  page.get_by_role('button',name='Filter by All',exact=True).click()
  page.locator('.spread-search summary').click();page.locator('#spread-search').fill('career');page.locator('#spread-search').press('Backspace')
  assert page.locator('.spread-search').get_attribute('open') is not None
  assert page.locator('#spread-search').input_value()=='caree'
  page.locator('#spread-search').fill('');page.locator('.spread-search summary').click()
  for tool in ['natal','moon','bazi','houses','asteroids','astro','calendar','life','numbers','love','rituals','shadow','runes','pendulum','oracle']:
   page.evaluate('(tool)=>transition("explore",tool)',tool)
   if page.locator('#birth-date').count():page.locator('#birth-date').fill('1996-11-05')
   if tool in ['natal','moon']:
    page.locator('#birth-name').fill('Sample Mystic');page.locator('#birth-hour').fill('14');page.locator('#birth-minute').fill('30')
    page.locator('#birth-country').fill('US');page.locator('#birth-region').fill('NY');page.locator('#birth-city').fill('Utica')
    page.locator('[data-action="birth-search"]').click();page.wait_for_selector('[data-action="birth-place"]');page.locator('[data-action="birth-place"]').first.click()
    assert page.locator('#birth-lat').count()==0 and page.locator('#birth-lon').count()==0
   if page.locator('#search').count():page.locator('#search').fill('clarity')
   page.locator('[data-action="tool-run"]').click()
   page.wait_for_function('state.result!==null||state.error!==""')
   error=page.evaluate('state.error');assert not error,(tool,error)
   if tool in ['natal']:
    assert page.locator('.chart-wheel svg').count()==1
    assert page.evaluate('state.result.placements.length')==10 and page.evaluate('state.result.houses.length')==12
    assert page.evaluate('state.result.birth_utc')=='1996-11-05T19:30:00+00:00'
    assert page.evaluate('state.result.houses.every(h=>h.ruler_placement&&Array.isArray(h.occupants))')
    assert page.evaluate('state.result.angles.length')==4
    assert page.locator('.birth-sidebar table').count()==3
    assert '☉' in page.locator('.birth-sidebar').inner_text() and '♏' in page.locator('.birth-sidebar').inner_text()
    assert page.locator('#report-zodiac').input_value()=='tropical'
    if tool=='natal':
     page.locator('.birth-report').scroll_into_view_if_needed();page.screenshot(path=str(screenshots/'web-birth-report-sidebar.png'))
     page.locator('.chart-wheel').screenshot(path=str(screenshots/'web-desktop-birth-chart.png'))
     page.pdf(path=str(screenshots/'birth-chart-report.pdf'),format='A4',print_background=True,margin={'top':'12mm','bottom':'12mm','left':'12mm','right':'12mm'})
     page.get_by_role('link',name='Houses',exact=True).click();assert page.locator('#chart-houses').is_visible()
     page.locator('#birth-rulership').select_option('traditional');page.locator('[data-action="tool-run"]').click();page.wait_for_function('state.result?.rulership==="traditional"')
     assert page.evaluate('state.result.houses[0].ruling_planet')=='Jupiter'
     before=page.evaluate('state.result.placements[0].longitude')
     page.locator('#report-zodiac').select_option('sidereal');page.wait_for_function('state.result?.zodiac==="sidereal"')
     assert before!=page.evaluate('state.result.placements[0].longitude')
   requests.append(tool)
  page.evaluate('transition("explore","store")')
  assert page.get_by_role('link',name='Visit my store ↗',exact=True).get_attribute('href')=='https://neurospicymystic.com/'
  assert page.locator('[data-action="tool-run"]').count()==0
  # Cycle is intentionally local and sound is synthesized locally.
  page.evaluate('transition("explore","cycle")');page.locator('#period-date').fill('2026-10-22');page.locator('[data-action="tool-run"]').click();assert page.locator('.result').count()==1
  page.evaluate('transition("learn")');page.get_by_role('button',name='Major Arcana',exact=True).click();page.locator('[data-action="card"]').first.click();assert page.locator('#selected-card').count()==1;assert page.locator('#selected-card img.tarot-image').count()==1
  page.locator('[data-action="learn-back"]').click();page.get_by_role('button',name='Quiz Me',exact=True).click();page.wait_for_selector('[data-action="quiz-answer"]');correct=page.evaluate('state.quiz.correct_answer');page.get_by_role('button',name=correct,exact=True).click();assert page.locator('.ok').count()==1
  page.evaluate('transition("spreads")');page.get_by_role('button',name='Randomize a Spread',exact=True).click()
  for index in range(page.locator('.slot').count()):
   page.locator('.slot').nth(index).click();page.wait_for_function('(n)=>Object.keys(state.drawn).length>=n',arg=index+1)
  assert page.locator('.slot.opened img.tarot-image').count()==page.locator('.slot').count()
  page.locator('img.tarot-image').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")');page.wait_for_function('Array.from(document.querySelectorAll(".slot img")).every(i=>i.complete&&i.naturalWidth>0)')
  page.screenshot(path=str(screenshots/'web-tarot-reading.png'))
  page.locator('[data-action="interpret"]').click();page.wait_for_function('Boolean(state.reading)');page.locator('[data-action="save-reading"]').click()
  page.evaluate('transition("journal")');page.get_by_role('button',name="Today's Journal",exact=True).click();page.locator('#journal-text').fill('Connected flow verification');page.locator('[data-action="save-note"]').click();assert 'Connected flow verification' in page.locator('main').inner_text()
  page.get_by_role('button',name='Mood Check-In',exact=True).click();page.get_by_role('button',name='Log mood 😊').click();assert 'Latest check-in' in page.locator('main').inner_text()
  page.evaluate('transition("cosmos")');page.wait_for_function('state.transit!==null&&!skyUI.loading')
  assert page.evaluate('state.transit.planets.length')==10
  page.wait_for_function('moonUI.data!==null&&!moonUI.loading')
  page.locator('#moon-month').fill('2026-11');page.locator('#moon-month').dispatch_event('change');page.wait_for_function('moonUI.data?.month===11&&!moonUI.loading')
  assert page.locator('.moon-calendar-grid [data-action="moon-day"]').count()==30
  page.get_by_role('button',name='2026-11-09 New Moon',exact=True).click();page.wait_for_function('state.transit?.date==="2026-11-09"&&!skyUI.loading')
  assert page.locator('.lunar-daily-table tbody tr').count()==30
  assert page.locator('.lunar-daily-table svg').count()==30
  assert 'not established medical effects' in page.locator('.lunar-health-note').inner_text()
  assert 'At start of day' in page.locator('.lunar-daily-table').inner_text()
  page.locator('#moon-calendar').screenshot(path=str(screenshots/'web-moon-calendar.png'))
  page.set_viewport_size({'width':390,'height':844});page.locator('#moon-calendar').scroll_into_view_if_needed()
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  page.screenshot(path=str(screenshots/'web-mobile-moon-calendar.png'))
  page.set_viewport_size({'width':1448,'height':1086})
  page.get_by_role('button',name='Next year →',exact=True).click();page.wait_for_function('moonUI.data?.year===2027&&!moonUI.loading')
  page.get_by_role('button',name='← Previous year',exact=True).click();page.wait_for_function('moonUI.data?.year===2026&&!moonUI.loading')
  page.get_by_role('button',name='Next month →',exact=True).click();page.wait_for_function('moonUI.data?.month===12&&!moonUI.loading');assert page.locator('.moon-calendar-grid [data-action="moon-day"]').count()==31
  page.get_by_role('button',name='← Previous month',exact=True).click();page.wait_for_function('moonUI.data?.month===11&&!moonUI.loading')
  page.locator('#sky-date').fill('2026-11-08');page.locator('#transit-sign').select_option('Virgo');page.wait_for_function('state.transit?.date==="2026-11-08"&&state.transit?.selected_sign==="Virgo"&&!skyUI.loading')
  assert page.evaluate('state.transit.moon.waxing') is False
  assert page.evaluate('state.transit.moon.phase_name')=='Waning Crescent'
  virgo=page.evaluate('state.transit.forecast.content');page.locator('#transit-sign').select_option('Pisces');page.wait_for_function('state.transit?.selected_sign==="Pisces"&&!skyUI.loading');assert virgo!=page.evaluate('state.transit.forecast.content')
  page.screenshot(path=str(screenshots/'web-daily-sky.png'))
  assert not failures,failures
  assert not errors,errors
  print(json.dumps({'passedTools':requests,'extraFlows':['cycle','learn module','quiz','complete spread','synthesis','save reading','journal note','mood','transits'],'apiErrors':failures,'jsErrors':errors}))
  for width,height,label in [(1448,1086,'desktop'),(390,844,'mobile')]:
   page.set_viewport_size({'width':width,'height':height})
   for name in ['home','spreads','learn','journal']:
    page.evaluate('(name)=>{state.selected=null;state.learningModule=null;transition(name)}',name)
    page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');page.evaluate('document.fonts.ready')
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(label,name)
    assert page.locator('.fresh-panel').count()>0,(label,name)
    assert page.locator('.panel-illustration img').evaluate_all('(imgs)=>imgs.every(i=>i.naturalWidth>=1200&&i.naturalWidth>=6*i.parentElement.clientWidth)'),(label,name,'illustration density')
    assert page.locator('.panel-copy').evaluate_all('(nodes)=>nodes.every(n=>n.getBoundingClientRect().right<=n.closest(".fresh-panel").getBoundingClientRect().right+1)'),(label,name,'clipped copy')
    page.screenshot(path=str(screenshots/f'web-{label}-{name}.png'),full_page=True)
  retina=b.new_context(viewport={'width':390,'height':844},device_scale_factor=3)
  retina_page=retina.new_page();retina_page.goto(base_url,wait_until='networkidle');retina_page.evaluate('document.fonts.ready')
  retina_page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
  retina_page.locator('.feature-grid').screenshot(path=str(screenshots/'web-mobile-panels-3x.png'))
  retina.close()
  page.set_viewport_size({'width':390,'height':844});page.evaluate('transition("explore","natal")');page.locator('[data-action="tool-run"]').click();page.wait_for_selector('.chart-wheel svg')
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  page.locator('.chart-wheel').scroll_into_view_if_needed();page.screenshot(path=str(screenshots/'web-mobile-birth-chart.png'))
  b.close()


def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--base-url')
 parser.add_argument('--screenshots',type=Path,default=Path('work/browser-evidence'))
 args=parser.parse_args()
 if args.base_url:
  exercise(args.base_url,args.screenshots)
  return
 root=Path(__file__).resolve().parents[2]
 with tempfile.TemporaryDirectory(prefix='sv-browser-') as temporary:
  with socket.socket() as sock:
   sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
  base=f'http://127.0.0.1:{port}'
  env={**os.environ,'AURAMYSTIC_DB_PATH':str(Path(temporary)/'browser.db')}
  with open(Path(temporary)/'server.log','w+') as log:
   server=subprocess.Popen([sys.executable,'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',str(port),'--log-level','warning'],cwd=root,env=env,stdout=log,stderr=log)
   try:
    for _ in range(100):
     try:
      with urllib.request.urlopen(base+'/api/health',timeout=1):break
     except OSError:time.sleep(.1)
    else:
     log.seek(0);raise RuntimeError(log.read())
    exercise(base,args.screenshots)
   finally:
    server.terminate();server.wait(timeout=10)

if __name__=='__main__':main()
