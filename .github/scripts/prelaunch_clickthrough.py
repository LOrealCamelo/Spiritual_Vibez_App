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

    def mobile():
        page.set_viewport_size({"width":390,"height":844})
        for tab in ["home","spreads","learn","cosmos","explore","journal"]:
            page.locator('.bottomdock [data-action="nav:'+tab+'"]').click()
            page.wait_for_function("(name)=>state.page===name",arg=tab)
            assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),"overflow on "+tab
        page.screenshot(path=str(ROOT/"mobile-journal.png"),full_page=True,animations="disabled")
        return "all 6 mobile tabs open, no horizontal overflow"
    test("mobile","390px mobile navigation and overflow",mobile)
    save("browser","JavaScript page errors",not JS_ERRORS,json.dumps(JS_ERRORS[:10]))
    save("browser","HTTP API responses without errors",not HTTP_ERRORS,json.dumps(HTTP_ERRORS[:10]))

def main():
    for name,origin in [("Netlify",NETLIFY),("custom",CUSTOM),("Render",RENDER)]:
        for suffix in ["/","/assets/icons/spiritual-vibz.webmanifest","/assets/tarot/00-the-fool.png"]:
            status,body,ctype=probe(origin+suffix)
            save("public access",name+" "+suffix,status==200,f"HTTP {status}, {ctype}")
    executable=shutil.which("google-chrome") or shutil.which("chromium")
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path=executable if executable else None,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1448,"height":900})
        candidates=[("Netlify",NETLIFY),("Render",RENDER)]
        origin=None
        for name,url in candidates:
            try:
                response=page.goto(url,wait_until="domcontentloaded",timeout=50000)
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
    (ROOT/"results.json").write_text(json.dumps({"results":RESULTS,"jsErrors":JS_ERRORS,"httpErrors":HTTP_ERRORS},indent=2))
    print("SUMMARY "+json.dumps({"passed":sum(r["passed"] for r in RESULTS),
      "failed":sum(not r["passed"] for r in RESULTS),
      "total":len(RESULTS)}),flush=True)
    # The audit is informational. Report failures in the logs, not as a workflow
    # execution error, so evidence is retained for review.
    return 0

if __name__=="__main__":
    raise SystemExit(main())
