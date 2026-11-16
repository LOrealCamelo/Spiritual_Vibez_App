"""Real Firefox/WebKit checks; no publishing, remote app calls or persistent data."""
import json
import os
from playwright.sync_api import sync_playwright
import browser_flows
from audit_flows import exercise_audit


def exercise(base, screenshots):
 screenshots.mkdir(parents=True, exist_ok=True)
 with sync_playwright() as playwright:
  for engine in os.environ.get('AUDIT_BROWSERS', 'firefox,webkit').split(','):
   browser = getattr(playwright, engine).launch(headless=True, timeout=60000)
   page = browser.new_page()
   errors = []
   page.on('pageerror', lambda error: errors.append(str(error)))
   page.goto(base, wait_until='networkidle')
   page.wait_for_function('state.online')
   ids = page.evaluate('allTools.map(t=>t[0])')
   assert len(ids) == 19 and len(set(ids)) == 19
   for width in [320, 375, 390, 430, 1440]:
    page.set_viewport_size({'width': width, 'height': 900})
    page.evaluate('transition("home")')
    page.evaluate('document.fonts.ready')
    assert page.locator('.home-feature').count() == 6
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), (engine, width)
    assert page.locator('.home-light-portal').is_visible() == (width < 960)
    nav = '.bottomdock' if width < 960 else '.topbar .nav'
    for route in ['spreads', 'learn', 'cosmos', 'explore', 'journal', 'home']:
     page.locator(nav+' [data-action="nav:'+route+'"]').click()
     assert page.evaluate('state.page') == route
   page.set_viewport_size({'width': 390, 'height': 844})
   for tool in ids:
    page.evaluate('transition("explore")')
    page.locator('.explore-card[data-action="tool:'+tool+'"]').click()
    assert page.evaluate('state.tool') == tool
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), (engine, tool)
   exercise_audit(page, base)
   assert not errors, (engine, errors)
   page.screenshot(path=str(screenshots/(engine+'-mobile.png')), full_page=True)
   print(json.dumps({'engine': engine, 'version': browser.version,
                     'tabs': 6, 'tools': len(ids), 'widths': [320,375,390,430,1440],
                     'errors': errors}))
   browser.close()


if __name__ == '__main__':
 browser_flows.exercise = exercise
 browser_flows.main()
