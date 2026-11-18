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
  page.wait_for_selector('#love-country option[value="US"]',state='attached')
  assert page.locator('#sign-a').is_visible() and page.locator('#sign-b').is_visible()
  for select in page.locator('#love-couple-form select').all():select.select_option('4')
  page.locator('#love-couple-form button').click()
  assert '100%' in page.locator('#love-couple-result').inner_text()
  assert 'does not measure love' in page.locator('#love-couple-result').inner_text()
  page.locator('#love-save-couple').click()
  assert 'Our connection reflections' in page.evaluate('localStorage.getItem("sv_private_journal")')
  page.locator('#love-country').select_option('US')
  page.wait_for_selector('#love-region option[value="NY"]',state='attached')
  page.locator('#love-region').select_option('NY')
  page.locator('#love-city-query').fill('Utica')
  page.wait_for_selector('#love-city option[value="5142056"]',state='attached')
  page.locator('#love-city').select_option('5142056')
  page.locator('#love-category').select_option('food')
  def listing(route):
   assert 'place_id=5142056' in route.request.url
   route.fulfill(content_type='application/json',body=json.dumps({'place':'Utica, New York, United States','category':'Restaurants','checked_at':'2026-11-17T12:00:00Z','notices':['Test provider fixture; mapped places are not live events.'],'events':[],'places':[{'name':'Test café','url':'https://www.openstreetmap.org/node/123','hours':''}],'search_links':[{'label':'Search more local ideas','url':'https://www.google.com/search?q=Utica'}]}))
  page.route('**/api/love/activities?*',listing)
  page.locator('#love-activity-form button').click()
  page.wait_for_selector('#love-activities a')
  assert page.locator('#love-activities').get_by_text('Test café').is_visible()
  for width in [320,375,390,430,1280,1440,1920]:
   page.set_viewport_size({'width':width,'height':900})
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
   page.locator('#love-activities').scroll_into_view_if_needed()
   assert page.locator('#love-activities').is_visible()
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
