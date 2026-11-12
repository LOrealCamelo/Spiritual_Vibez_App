"""Verify installed-icon metadata, deployed resources and browser mask previews."""
import base64
import json
from pathlib import Path


def exercise_icons(page, screenshots):
 manifest=page.locator('link[rel="manifest"]').get_attribute('href')
 assert manifest=='assets/icons/spiritual-vibz.webmanifest'
 parsed=page.evaluate('async path=>{const r=await fetch(path);return {status:r.status,type:r.headers.get("content-type"),body:await r.json()}}',manifest)
 assert parsed['status']==200 and 'manifest+json' in parsed['type'],parsed
 assert parsed['body']['start_url']=='/#home' and parsed['body']['scope']=='/'
 cdp=page.context.new_cdp_session(page);data=cdp.send('Page.getAppManifest');assert not data.get('errors'),data
 root=Path(__file__).resolve().parents[2]
 for file in (root/'frontend/assets/icons').iterdir():
  resource=page.evaluate('''async path=>{const r=await fetch(path);const bytes=new Uint8Array(await r.arrayBuffer());return {status:r.status,type:r.headers.get('content-type'),signature:Array.from(bytes.slice(0,8)),length:bytes.length}}''','/assets/icons/'+file.name)
  assert resource['status']==200 and resource['length']>0,(file.name,resource)
  if file.suffix=='.png':assert resource['signature']==[137,80,78,71,13,10,26,10] and resource['type']=='image/png',(file.name,resource)
 for size in [180,167,152,120]:assert page.locator('link[rel="apple-touch-icon"][sizes="'+str(size)+'x'+str(size)+'"]').count()==1
 # A separate test page previews platform masks without changing the app UI.
 origin=page.evaluate('location.origin')
 foreground=base64.b64encode((root/'mobile/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_foreground.png').read_bytes()).decode()
 preview=page.context.browser.new_page(viewport={'width':750,'height':310})
 preview.set_content('''<html><body style="margin:0;padding:24px;background:#f1e5f8;color:#45115e;font:15px Arial"><div style="display:flex;gap:35px;justify-content:center">'''+
  '<figure style="margin:0;text-align:center"><img width="180" height="180" style="border-radius:23%" src="'+origin+'/assets/icons/avatar-180.png"><figcaption>iPhone / iPad</figcaption></figure>'+
  '<figure style="margin:0;text-align:center"><img width="180" height="180" style="clip-path:circle(40% at 50% 50%)" src="'+origin+'/assets/icons/avatar-maskable-512.png"><figcaption>Android maskable safe area</figcaption></figure>'+
  '<figure style="margin:0;text-align:center"><div style="width:180px;height:180px;background:#30084d;overflow:hidden;border-radius:50%;position:relative"><img style="position:absolute;width:270px;height:270px;left:-45px;top:-45px" src="data:image/png;base64,'+foreground+'"></div><figcaption>Native Android adaptive icon</figcaption></figure></div></body></html>')
 preview.wait_for_function('Array.from(document.images).every(n=>n.complete&&n.naturalWidth>0)');preview.screenshot(path=str(screenshots/'official-app-icon-masks.png'));preview.close()
 print(json.dumps({'official_icon':'public Apple touch icons, PWA manifest, favicon and every icon file load','manifest_errors':data.get('errors',[]),'mask_previews':'iPhone/iPad, Android safe area and native Android adaptive'}))
