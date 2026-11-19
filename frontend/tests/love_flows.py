"""Questionnaire, actual GeoNames dropdowns, responsive Love UI and public account routes."""
import json
import os
from playwright.sync_api import sync_playwright
import browser_flows


def exercise(base, screenshots):
 screenshots.mkdir(parents=True,exist_ok=True)
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(executable_path=os.getenv('BROWSER_EXECUTABLE','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1440,'height':1000})
  errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
  page.goto(base+'/#explore/love',wait_until='networkidle')
  try:page.wait_for_selector('#love-country option[value="US"]',state='attached',timeout=10000)
  except Exception:
   print('Love page errors:',errors,flush=True)
   print('Love status:',page.locator('#love-status').all_text_contents(),flush=True)
   print('Page diagnostic:', page.evaluate('({url:location.href,page:typeof state!=="undefined"?state.page:null,tool:typeof state!=="undefined"?state.tool:null,module:typeof window.SpiritualLoveExperience,scripts:[...document.scripts].map(x=>x.src),text:document.body.innerText.slice(0,500)})'),flush=True)
   raise
  assert page.locator('#sign-a').is_visible() and page.locator('#sign-b').is_visible()
  assert page.locator('.love-experience').count() == 1
  assert page.locator('#love-couple-form').count() == 0  # No duplicate legacy questionnaire.
  for select in page.locator('.love-question select').all():select.select_option('0')
  page.locator('[data-love=analyze]').click()
  assert '6 shared preferences across 6 questions' in page.locator('#love-analysis').inner_text()
  assert 'do not measure whether' in page.locator('#love-analysis').inner_text()
  page.locator('[data-love=save]').click()
  assert 'Our connection reflections' in page.evaluate('localStorage.getItem("sv_private_journal")')
  page.locator('#love-country').select_option('US')
  page.wait_for_selector('#love-region option[value="NY"]',state='attached')
  page.locator('#love-region').select_option('NY')
  page.locator('#love-city-query').fill('Utica')
  page.wait_for_selector('#love-city option[value="5142056"]',state='attached')
  page.locator('#love-city').select_option('5142056')
  page.locator('#love-category').select_option('Restaurants')
  def listing(route):
   assert 'place_id=5142056' in route.request.url
   route.fulfill(content_type='application/json',body=json.dumps({'place':'Utica, New York, United States','category':'Restaurants','checked_at':'2026-11-17T12:00:00Z','notices':['Test provider fixture; mapped places are not live events.'],'events':[],'places':[{'name':'Test café','url':'https://www.openstreetmap.org/node/123','hours':''}],'search_links':[{'label':'Search more local ideas','url':'https://www.google.com/search?q=Utica'}]}))
  page.route('**/api/love/activities?*',listing)
  page.locator('[data-love=places]').click()
  page.wait_for_selector('#love-results a')
  assert page.locator('#love-results').get_by_text('Test café').is_visible()
  for width in [320,375,390,430,1280,1440,1920]:
   page.set_viewport_size({'width':width,'height':900})
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
   page.locator('#love-results').scroll_into_view_if_needed()
   assert page.locator('#love-results').is_visible()
   page.screenshot(path=str(screenshots/f'love-{width}.png'),full_page=True)
  for route in ['sales','register','login','checkout']:
   page.goto(base+'/#'+route,wait_until='networkidle')
   assert page.locator('body').get_attribute('data-page')==route
   assert page.locator('.membership-panel').count()==1
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),route
  assert not errors,errors
  browser.close()
  print('PASS: zodiac preserved; questionnaire scoring/journal; real country/region/city selection; provider rendering; 7 viewport widths; sales/register/login/checkout routes; no JS errors.')


if __name__=='__main__':
 browser_flows.exercise=exercise
 browser_flows.main()
