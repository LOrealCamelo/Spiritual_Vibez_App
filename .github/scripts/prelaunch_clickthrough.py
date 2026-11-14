"""Read-only prelaunch clickthrough with synthetic test data and fresh browser profile.

Netlify may be owner-private: in that case test the same frontend files served by
the Render FastAPI origin, clearly disclosing that this is NOT Netlify E2E proof.
No production deployment, purchases, or real personal information.
"""
import json
import shutil
import traceback
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from playwright.sync_api import sync_playwright

ROOT=Path("prelaunch-audit")
ROOT.mkdir(exist_ok=True)
RENDER="https://spiritual-vibez-app.onrender.com"
NETLIFY="https://spiritualvibz.netlify.app"
CUSTOM="https://app.neurospicymystic.com"
RESULTS=[]
JS_ERRORS=[]
HTTP_ERRORS=[]

def save(section,name,ok,detail=""):
    row={"section":section,"test":name,"passed":bool(ok),"detail":str(detail)[:500]}
    RESULTS.append(row)
    print(("PASS" if ok else "FAIL")+f" | {section} | {name} | {detail}",flush=True)

def probe(url):
    try:
        with urlopen(Request(url,headers={"User-Agent":"SpiritualVibezPrelaunchAudit/1.0"}),timeout=50) as response:
            return response.status,response.read(20000),response.headers.get("Content-Type","")
    except HTTPError as exc:
        return exc.code,exc.read(200),""
    except Exception as exc:
        return None,str(exc).encode(),""

def test(section,name,func):
    try:
        value=func()
        save(section,name,True,value or "OK")
    except Exception as exc:
        save(section,name,False,f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc(limit=2),flush=True)

def navigate(page,tab):
    page.locator('.topbar [data-action="nav:'+tab+'"]').first.click(timeout=14000)
    page.wait_for_function("(name)=>state.page===name",arg=tab,timeout=15000)
    assert page.locator("main").count()==1 and page.locator("main").is_visible()
    assert len(page.locator("main").inner_text().strip())>12
    return tab+" visible"

def visit_tool(page,tool):
    page.evaluate('transition("explore")')
    locator=page.locator('[data-action="tool:'+tool+'"]').first
    locator.click(timeout=12000)
    page.wait_for_function("(name)=>state.tool===name",arg=tool,timeout=15000)
    assert len(page.locator("main").inner_text().strip())>12
    return tool+" opens"

def calculate(page,tool,fields,timeout=45000):
    visit_tool(page,tool)
    if tool == "rituals":
        # The Ritual Finder form is intentionally collapsed beneath its library;
        # expand the native details element before exercising the search.
        page.locator(".ritual-search-original summary").click()
    for selector,value in fields:
        if selector.startswith("select:"):
            page.locator(selector[7:]).select_option(value)
        else:
            page.locator(selector).fill(value)
    page.locator('[data-action="tool-run"]').last.click(timeout=12000)
    page.wait_for_function('state.result!==null||state.error!==""',timeout=timeout)
    err=page.evaluate('state.error')
    assert not err,"App error: "+str(err)
    assert page.evaluate('state.result!==null')
    return tool+" result generated"

def manifest_check(page):
    response=page.evaluate("""async () => {
      try {let r=await fetch('/assets/icons/spiritual-vibz.webmanifest');
        let text=await r.text();return {status:r.status,type:r.headers.get('content-type'),text:text.slice(0,200)};}
      catch(e){return {error:String(e)}}}""")
    assert response.get("status")==200,response
    assert "json" in (response.get("type") or ""),response
    return "HTTP 200, manifest JSON available"


def fill_birthplace(page):
    page.locator("#birth-name").fill("Sample Mystic")
    page.locator("#birth-date").fill("1996-11-05")
    page.locator("#birth-hour").select_option("02 PM")
    page.locator("#birth-minute").select_option("30")
    page.wait_for_selector('#birth-country option[value="US"]',state="attached",timeout=25000)
    page.locator("#birth-country").select_option("US")
    page.wait_for_selector('#birth-region option[value="NY"]',state="attached",timeout=25000)
    page.locator("#birth-region").select_option("NY")
    page.wait_for_function('birthLocations.key.includes("US|NY|")&&!birthLocations.loading',timeout=25000)
    page.locator("#birth-city").fill("Utica")
    page.locator('[data-action="birth-search"]').click()
    page.wait_for_selector('#birth-city-select option[value="5142056"]',state="attached",timeout=25000)
    page.locator("#birth-city-select").select_option("5142056")
    assert "America/New_York" in page.locator("#birth-place-results").inner_text()

def run_birth(page,tool,timeout=90000):
    visit_tool(page,tool)
    fill_birthplace(page)
    page.locator('[data-action="tool-run"]').click()
    page.wait_for_function('state.result!==null||state.error!==""',timeout=timeout)
    err=page.evaluate("state.error")
    assert not err,"Birth calculation error: "+str(err)
    assert page.evaluate("state.result!==null")
    return page.evaluate("state.result")

def test_deep_calculations(page):
    page.set_viewport_size({"width":1448,"height":900})
    def natal():
        result=run_birth(page,"natal")
        assert len(result["placements"])==10,"Expected 10 planets"
        assert len(result["houses"])==12,"Expected 12 houses"
        assert result["birth_utc"]=="1996-11-05T19:30:00+00:00",result["birth_utc"]
        assert page.locator(".chart-wheel svg").count()==1
        assert len(result["angles"])==4
        return "10 planets, 12 houses, 4 angles, correct NY timezone, chart wheel"
    test("advanced astrology","complete natal chart",natal)
    def change_time():
        result=run_birth(page,"natal")
        pm=result["ascendant"]
        page.locator("#birth-hour").select_option("02 AM")
        page.locator('[data-action="tool-run"]').click()
        page.wait_for_function('state.result?.birth_utc==="1996-11-05T07:30:00+00:00"',timeout=90000)
        am=page.evaluate("state.result")
        assert pm!=am["ascendant"],"Ascendant must differ between 2 AM and 2 PM"
        return f"2 PM ascendant {pm}, 2 AM ascendant {am['ascendant']}"
    test("advanced astrology","birth-time sensitivity",change_time)
    def sidereal():
        result=run_birth(page,"natal")
        original=result["placements"][0]["longitude"]
        page.locator("#report-zodiac").select_option("sidereal")
        page.wait_for_function('state.result?.zodiac==="sidereal"',timeout=90000)
        change=page.evaluate("state.result")
        assert abs(original-change["placements"][0]["longitude"])>1,"Zodiac did not shift"
        return "Switch to sidereal changes chart placements"
    test("advanced astrology","tropical and sidereal",sidereal)
    def natal_moon():
        result=run_birth(page,"moon")
        assert result.get("natal_moon_phase"),list(result)
        return "Natal moon phase "+str(result.get("natal_moon_phase"))
    test("advanced astrology","natal moon phase",natal_moon)
    def asteroids():
        visit_tool(page,"asteroids")
        fill_birthplace(page)
        page.wait_for_function('asteroidUI.loaded&&!asteroidUI.loading',timeout=55000)
        total=page.evaluate("asteroidUI.total")
        assert total>10000,total
        page.locator("#asteroid-query").fill("1008")
        page.locator('[data-action="asteroid-search"]').click()
        page.wait_for_selector('#asteroid-add option[value="1008"]',state="attached",timeout=35000)
        page.locator("#asteroid-add").select_option("1008")
        page.locator('[data-action="tool-run"]').click()
        page.wait_for_function('state.result!==null||state.error!==""',timeout=90000)
        err=page.evaluate("state.error")
        assert not err,err
        count=len(page.evaluate("state.result.asteroids"))
        assert count==5,f"Expected 5 selected asteroids, got {count}"
        assert "NASA/JPL Horizons" in page.locator(".asteroid-report").inner_text()
        return f"Loaded {total} catalog records, computed {count} asteroid positions"
    test("advanced astrology","asteroid catalog and positions",asteroids)
    def astrocarto():
        result=run_birth(page,"astro",timeout=110000)
        lines=page.locator(".astro-line").count()
        crossing=page.locator(".astro-crossing").count()
        assert lines==40,lines
        assert crossing>100,crossing
        assert len(result["places"])==8
        page.locator('[data-action="astro-layer"][data-planet="Sun"]').click()
        page.locator('[data-action="astro-angle"][data-angle="IC"]').click()
        assert "Sun" in page.locator("#astro-active-line").inner_text()
        page.locator('[data-action="astro-angle"][data-angle="All"]').click()
        page.locator('[data-action="astro-layer"][data-planet="All"]').click()
        return f"{lines} planetary lines, {crossing} crossings, 8 places, working filters"
    test("advanced astrology","astrocartography map",astrocarto)
    def moon_calendar():
        navigate(page,"cosmos")
        page.wait_for_function('state.transit!==null&&!skyUI.loading',timeout=90000)
        page.wait_for_function('moonUI.data!==null&&!moonUI.loading',timeout=90000)
        page.locator("#moon-month").fill("2026-11")
        page.locator("#moon-month").dispatch_event("change")
        page.wait_for_function("moonUI.data?.year===2026&&moonUI.data?.month===11&&!moonUI.loading",timeout=90000)
        days=page.locator(".moon-calendar-grid [data-action='moon-day']").count()
        assert days==30,days
        planets=page.evaluate("state.transit.planets.length")
        assert planets==10,planets
        return f"Moon calendar for November 2026 displays 30 days and {planets} planetary transits"
    test("advanced astrology","moon calendar and daily transits",moon_calendar)

def clicks(page,origin):
    page.on("pageerror",lambda exc: JS_ERRORS.append(str(exc)[:450]))
    page.on("response",lambda r: HTTP_ERRORS.append((r.status,r.url)) if r.status>=400 and "/api/" in r.url else None)
    for tab in ["home","spreads","learn","cosmos","explore","journal"]:
        test("navigation",tab,lambda tab=tab:navigate(page,tab))
    for tool in ["natal","moon","bazi","houses","asteroids","astro","calendar",
                 "life","numbers","love","sound","rituals","cycle","shadow",
                 "runes","pendulum","oracle","store"]:
        test("tool opens",tool,lambda tool=tool:visit_tool(page,tool))

    test("calculation","numerology life path",lambda:calculate(page,"life",[("#birth-date","1996-11-05")]))
    test("calculation","BaZi",lambda:calculate(page,"bazi",[("#birth-date","1977-06-15")]))
    test("calculation","love compatibility",lambda:calculate(page,"love",[
        ("select:#sign-a","Scorpio"),("select:#sign-b","Taurus")]))
    test("calculation","ritual search",lambda:calculate(page,"rituals",[("#search","abundance")]))
    test("calculation","pendulum",lambda:calculate(page,"pendulum",[("#search","Should I pause?")]))
    test("calculation","oracle",lambda:calculate(page,"oracle",[("#search","What helps me reflect?")]))
    test("calculation","cycle tracker",lambda:calculate(page,"cycle",[("#period-date","2026-10-22")]))
    test("calculation","13-month calendar",lambda:calculate(page,"calendar",[("#calendar-date","2026-11-12")]))

    def tarot():
        navigate(page,"spreads")
        page.locator('[data-action="random-spread"]').first.click()
        page.wait_for_function("state.selected!==null",timeout=20000)
        count=page.locator(".slot").count()
        assert count>=1,"No card slots"
        page.locator(".slot").first.click()
        page.wait_for_function("Object.keys(state.drawn).length>=1",timeout=25000)
        assert page.locator(".slot.opened").count()>=1
        return "Opened spread and revealed first card"
    test("interaction","tarot draw",tarot)

    def learning():
        navigate(page,"learn")
        page.locator('[data-action="learn-module"]').first.click()
        assert page.locator('[data-action="card"]').count()>0,"No study cards"
        page.locator('[data-action="card"]').first.click()
        assert page.locator("#selected-card").count()==1
        return "Opened learning deck and card detail"
    test("interaction","learn tarot",learning)

    def journal():
        navigate(page,"journal")
        page.locator('[data-action="journal-entry"]').first.click()
        page.locator("#journal-text").fill("Synthetic automated prelaunch note")
        page.locator('[data-action="save-note"]').click()
        assert "Synthetic automated prelaunch note" in page.locator("main").inner_text()
        return "Saved test journal entry in temporary browser storage"
    test("interaction","private journal",journal)

    def runes():
        visit_tool(page,"runes")
        page.locator('[data-action="rune-cast"]').first.click()
        page.wait_for_selector(".rune-result-head",timeout=20000)
        return "Rune cast showed result"
    test("interaction","rune casting",runes)

    def quiz():
        navigate(page,"learn")
        # The previous Learn Tarot test left a card detail open. Return to the
        # module overview before selecting the quiz.
        if page.locator('[data-action="learn-back"]').count():
            page.locator('[data-action="learn-back"]').first.click()
        page.locator('[data-action="quiz"]').first.click()
        page.wait_for_selector('[data-action="quiz-answer"]',timeout=25000)
        page.locator('[data-action="quiz-answer"]').first.click()
        assert page.evaluate('Boolean(state.answer)')
        return "Tarot quiz question and answer evaluated"
    test("interaction","tarot knowledge quiz",quiz)

    def shadow():
        visit_tool(page,"shadow")
        page.locator('[data-action="shadow-theme"]').first.click()
        assert page.locator("#shadow-guide").count()>=1
        page.locator('[data-action="shadow-next"]').first.click()
        return "Opened guided shadow-work exercise and advanced a step"
    test("interaction","shadow work journey",shadow)

    def store():
        visit_tool(page,"store")
        href=page.get_by_role("link",name="Visit my store ↗").get_attribute("href")
        assert href=="https://neurospicymystic.com/",href
        return "External store link points to existing storefront"
    test("interaction","store link",store)

    def mobile():
        page.set_viewport_size({"width":390,"height":844})
        for tab in ["home","spreads","learn","cosmos","explore","journal"]:
            page.locator('.bottomdock [data-action="nav:'+tab+'"]').click()
            page.wait_for_function("(name)=>state.page===name",arg=tab)
            assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),"overflow on "+tab
        page.screenshot(path=str(ROOT/"mobile-journal.png"),full_page=True,animations="disabled")
        return "all 6 mobile tabs open, no horizontal overflow"
    test("mobile","390px mobile navigation and overflow",mobile)
    test_deep_calculations(page)
    save("browser","JavaScript page errors",not JS_ERRORS,json.dumps(JS_ERRORS[:10]))
    save("browser","HTTP API responses without errors",not HTTP_ERRORS,json.dumps(HTTP_ERRORS[:10]))


def check_http_security_seo():
    """Non-invasive live HTML/header and indexability checks; informational only."""
    targets=[("custom",CUSTOM),("temporary Netlify",NETLIFY),("Render",RENDER)]
    for name,base in targets:
        for path in ["/","/robots.txt","/sitemap.xml","/assets/icons/spiritual-vibz.webmanifest"]:
            url=base+path
            try:
                with urlopen(Request(url,headers={"User-Agent":"SpiritualVibezPrelaunchAudit/1.0"}),timeout=40) as response:
                    status=response.status
                    data=response.read(120000).decode("utf-8",errors="replace")
                    headers=response.headers
            except HTTPError as exc:
                status=exc.code
                data=exc.read(1000).decode("utf-8",errors="replace")
                headers=exc.headers
            except Exception as exc:
                print("AUDIT ERROR",name,path,str(exc)[:160],flush=True)
                continue
            if path=="/":
                values={key:headers.get(key) for key in ["Server","Content-Type","Content-Security-Policy","Strict-Transport-Security","X-Content-Type-Options","X-Frame-Options","Referrer-Policy","Permissions-Policy","X-Robots-Tag","CF-Ray","X-Nf-Request-Id"] if headers.get(key) is not None}
                info={"http":status,"headers":values,"title":("<title" in data.lower()),"description":('name="description"' in data.lower()),"canonical":('rel="canonical"' in data.lower()),"og":('property="og:' in data.lower()),"html_app_empty":('<div id="app"></div>' in data)}
            elif path=="/robots.txt":
                info={"http":status,"content_type":headers.get("Content-Type"),"robots_format":("User-agent:" in data or "user-agent:" in data),"body_start":data[:90]}
            elif path=="/sitemap.xml":
                info={"http":status,"content_type":headers.get("Content-Type"),"sitemap_format":("<urlset" in data or "<sitemapindex" in data),"body_start":data[:90]}
            else:
                info={"http":status,"content_type":headers.get("Content-Type"),"valid_manifest":data.strip().startswith("{")}
            print("AUDIT "+json.dumps({"site":name,"path":path,**info}),flush=True)
    try:
        request=Request(RENDER+"/api/health",method="OPTIONS",headers={
            "Origin":"https://example-unrelated-site.invalid",
            "Access-Control-Request-Method":"GET"})
        with urlopen(request,timeout=30) as response:
            print("AUDIT CORS "+json.dumps({"http":response.status,
                "allow_origin":response.headers.get("Access-Control-Allow-Origin"),
                "allow_credentials":response.headers.get("Access-Control-Allow-Credentials")}),flush=True)
    except Exception as exc:
        print("AUDIT CORS ERROR "+str(exc)[:200],flush=True)

def main():
    for name,origin in [("Netlify",NETLIFY),("custom",CUSTOM),("Render",RENDER)]:
        for suffix in ["/","/assets/icons/spiritual-vibz.webmanifest","/assets/tarot/00-the-fool.png"]:
            status,body,ctype=probe(origin+suffix)
            save("public access",name+" "+suffix,status==200,f"HTTP {status}, {ctype}")
    executable=shutil.which("google-chrome") or shutil.which("chromium")
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path=executable if executable else None,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1448,"height":900})
        candidates=[("custom domain",CUSTOM),("Render",RENDER),("Netlify",NETLIFY)]
        origin=None
        for name,url in candidates:
            try:
                response=page.goto(url,wait_until="domcontentloaded",timeout=50000)
                print("BROWSER ORIGIN",name,"HTTP",response.status if response else None,
                      "URL",page.url,"TITLE",page.title(),"#app",page.locator("#app").count(),
                      "BODY",page.locator("body").inner_text()[:180],flush=True)
                page.screenshot(path=str(ROOT/("origin-"+name.replace(" ","-")+".png")),full_page=False)
                if response and response.status==200 and page.locator("#app").count()==1:
                    page.wait_for_function("typeof state!=='undefined'&&state.page==='home'",timeout=40000)
                    origin=(name,url)
                    break
            except Exception as exc:
                print("Origin "+name+" browser unavailable: "+str(exc)[:200],flush=True)
        if origin is None:
            save("browser","Open app",False,"Neither Netlify nor Render served an accessible app")
        else:
            save("browser","Test origin selected",True,origin[0]+": "+origin[1])
            test("browser","manifest fetch from selected origin",lambda:manifest_check(page))
            try: page.wait_for_function("state.online===true",timeout=55000)
            except Exception: pass
            save("browser","Connected tarot catalog",page.evaluate("state.online===true"),
                 "state.online="+str(page.evaluate("state.online")))
            clicks(page,origin[0])
        browser.close()
    check_http_security_seo()
    (ROOT/"results.json").write_text(json.dumps({"results":RESULTS,"jsErrors":JS_ERRORS,"httpErrors":HTTP_ERRORS},indent=2))
    print("SUMMARY "+json.dumps({"passed":sum(r["passed"] for r in RESULTS),
      "failed":sum(not r["passed"] for r in RESULTS),
      "total":len(RESULTS)}),flush=True)
    # The audit is informational. Report failures in the logs, not as a workflow
    # execution error, so evidence is retained for review.
    return 0

if __name__=="__main__":
    raise SystemExit(main())
