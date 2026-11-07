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
  for tool in ['natal','draconic','moon','bazi','houses','asteroids','astro','calendar','life','numbers','love','rituals','shadow','runes','pendulum','oracle','store']:
   page.evaluate('(tool)=>transition("explore",tool)',tool)
   if page.locator('#birth-date').count():page.locator('#birth-date').fill('1996-11-05')
   if page.locator('#search').count():page.locator('#search').fill('clarity')
   page.locator('[data-action="tool-run"]').click()
   page.wait_for_function('state.result!==null||state.error!==""')
   error=page.evaluate('state.error');assert not error,(tool,error)
   requests.append(tool)
  # Cycle is intentionally local and sound is synthesized locally.
  page.evaluate('transition("explore","cycle")');page.locator('#period-date').fill('2026-10-22');page.locator('[data-action="tool-run"]').click();assert page.locator('.result').count()==1
  page.evaluate('transition("learn")');page.get_by_role('button',name='Major Arcana',exact=True).click();page.locator('[data-action="card"]').first.click();assert page.locator('#selected-card').count()==1
  page.locator('[data-action="learn-back"]').click();page.get_by_role('button',name='Quiz Me',exact=True).click();page.wait_for_selector('[data-action="quiz-answer"]');correct=page.evaluate('state.quiz.correct_answer');page.get_by_role('button',name=correct,exact=True).click();assert page.locator('.ok').count()==1
  page.evaluate('transition("spreads")');page.get_by_role('button',name='Randomize a Spread',exact=True).click()
  for index in range(page.locator('.slot').count()):
   page.locator('.slot').nth(index).click();page.wait_for_function('(n)=>Object.keys(state.drawn).length>=n',arg=index+1)
  page.locator('[data-action="interpret"]').click();page.wait_for_function('Boolean(state.reading)');page.locator('[data-action="save-reading"]').click()
  page.evaluate('transition("journal")');page.get_by_role('button',name="Today's Journal",exact=True).click();page.locator('#journal-text').fill('Connected flow verification');page.locator('[data-action="save-note"]').click();assert 'Connected flow verification' in page.locator('main').inner_text()
  page.get_by_role('button',name='Mood Check-In',exact=True).click();page.get_by_role('button',name='Log mood 😊').click();assert 'Latest check-in' in page.locator('main').inner_text()
  page.evaluate('transition("cosmos")');page.locator('[data-action="get-transit"]').click();page.wait_for_function('state.transit!==null')
  assert not failures,failures
  assert not errors,errors
  print(json.dumps({'passedTools':requests,'extraFlows':['cycle','learn module','quiz','complete spread','synthesis','save reading','journal note','mood','transits'],'apiErrors':failures,'jsErrors':errors}))
  for width,height,label in [(1448,1086,'desktop'),(390,844,'mobile')]:
   page.set_viewport_size({'width':width,'height':height})
   for name in ['home','spreads','learn','journal']:
    page.evaluate('(name)=>{state.selected=null;state.learningModule=null;transition(name)}',name)
    page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');page.evaluate('document.fonts.ready')
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(label,name)
    page.screenshot(path=str(screenshots/f'web-{label}-{name}.png'),full_page=True)
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
