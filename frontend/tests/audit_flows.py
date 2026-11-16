"""Prelaunch regressions: clean addresses, complete Metadata and Web Audio."""
import json


def exercise_audit(page, base):
 documents = []
 page.on('request', lambda r: documents.append(r.url) if r.is_navigation_request() else None)
 page.goto(base + '/?utm_source=chatgpt.com&fbclid=tracking&keep=1#explore/natal?utm_medium=chat&section=houses', wait_until='networkidle')
 page.wait_for_function('state.online && state.tool==="natal"')
 assert page.evaluate('location.search') == '?keep=1'
 assert page.evaluate('location.hash') == '#explore/natal?section=houses'
 assert len(documents) == 1, documents  # replaceState must not load another document.
 assert page.locator('#birth-date').is_visible()

 page.evaluate('transition("explore","metadata")')
 page.locator('#metadata-name').fill("O'ralle Rivenunti")
 page.locator('#metadata-date').fill('1986-09-09')
 page.locator('#metadata-year').fill('2026')
 page.get_by_role('button', name='Calculate Your Metadata', exact=True).click()
 page.wait_for_selector('.metadata-report')
 assert page.evaluate('state.result.core.expression.steps') == [78, 15, 6]
 assert page.evaluate('state.result.core.personality.steps') == [40, 4]
 assert page.evaluate('state.result.challenges') == [0, 3, 3, 3]
 assert page.locator('.metadata-reading').count() >= 10
 page.locator('.complete-reading-share [data-action="content-share"]').click()
 page.wait_for_selector('.share-preview img')
 caption = page.locator('.share-preview textarea').input_value()
 assert '78 → 15 → 6' in caption and '#explore/metadata' in caption
 assert 'report_svg' not in caption and '<svg' not in caption
 assert page.locator('.share-preview img').evaluate('(n)=>n.complete&&n.naturalWidth>0')
 page.get_by_role('button', name='Close', exact=True).click()
 page.locator('.complete-reading-share [data-action="content-journal"]').click()
 saved = page.evaluate('JSON.parse(localStorage.getItem("sv_private_journal")).at(-1)')
 assert '78 → 15 → 6' in saved['text']
 for width in [320, 375, 390, 430, 1440]:
  page.set_viewport_size({'width': width, 'height': 900})
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), ('metadata', width)

 page.evaluate('transition("explore","sound")')
 page.locator('[data-action="audio-play"]').click()
 page.wait_for_function('ac?.state==="running" && osc!==null')
 assert page.evaluate('osc.frequency.value') > 0
 page.locator('[data-action="audio-stop"]').click()
 assert page.evaluate('ac===null && osc===null')
 page.locator('[data-action="audio-play"]').click()
 page.wait_for_function('ac?.state==="running"')
 page.evaluate('transition("home")')
 assert page.evaluate('ac===null && osc===null')
 print(json.dumps({'url_cleanup': 'one document, legitimate query and natal hash preserved',
                   'metadata': 'arithmetic, full reading, PNG preview, clean invite and journal',
                   'audio': 'real Web Audio Play, Stop and navigation cleanup'}))
