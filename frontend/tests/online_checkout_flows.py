"""Real account UI and callback endpoints; provider SDKs/APIs are fixtures, no charges."""
import copy
import hashlib
import hmac
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
from datetime import datetime,timezone
from urllib.parse import parse_qs,urlencode

import httpx
import uvicorn
from playwright.sync_api import sync_playwright


def main():
 with tempfile.TemporaryDirectory(prefix='sv-online-browser-') as temp:
  os.environ.update(MEMBERSHIP_REQUIRED='true',MEMBERSHIP_DB_PATH=temp+'/members.db',MEMBERSHIP_USER_DATA_DIR=temp+'/users',
   AURAMYSTIC_DB_PATH=temp+'/legacy.db',MEMBERSHIP_PUBLIC_URL='https://example.test',MEMBERSHIP_SUPPORT_EMAIL='owner@example.test',
   STRIPE_CHECKOUT_ENABLED='true',STRIPE_SECRET_KEY='sk_live_fixture',STRIPE_WEBHOOK_SECRET='whsec_fixture',
   STRIPE_MONTH_PRICE_ID='price_month',STRIPE_YEAR_PRICE_ID='price_year',STRIPE_LIFETIME_PRICE_ID='price_lifetime',
   PAYPAL_API_ENABLED='true',PAYPAL_CLIENT_SECRET='private-fixture',PAYPAL_WEBHOOK_ID='WH-fixture',
   PAYPAL_SUBSCRIPTIONS_ENABLED='true',PAYPAL_LIFETIME_ENABLED='true',PAYPAL_IPN_URL='https://example.test/api/account/paypal/ipn')
  from backend.main import app
  from backend.services import memberships as m,online_payments as o,paypal_memberships as old
  from backend.tests.test_online_payments import price
  password='cloud garden test password 88'
  with m.database() as db:db.execute('INSERT INTO members(email,password,admin,created) VALUES(?,?,1,?)',('owner@example.test',m.password_hash(password),m.now()))
  objects={}
  async def stripe_request(method,path,data=None,params=None):
   if path.startswith('prices/'):return price(path.removeprefix('prices/price_'))
   return copy.deepcopy(objects[path])
  async def paypal_request(method,path,data=None):
   if path=='/v1/notifications/verify-webhook-signature':return {'verification_status':'SUCCESS'}
   if path.startswith('/v1/billing/plans/'):
    plan=next(k for k,v in o.PAYPAL_PLANS.items() if path.endswith(v))
    return {'status':'ACTIVE','billing_cycles':[{'tenure_type':'REGULAR','total_cycles':0,'frequency':{'interval_unit':'MONTH' if plan=='month' else 'YEAR','interval_count':1},'pricing_scheme':{'fixed_price':{'value':str(m.PLANS[plan]['price_cents']/100),'currency_code':'USD'}}}]}
   return copy.deepcopy(objects[path])
  async def verify_ipn(raw):return True
  o.stripe_request=stripe_request;o.paypal_request=paypal_request;old.verify=verify_ipn
  with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
  base=f'http://127.0.0.1:{port}'
  server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=port,log_level='warning'))
  thread=threading.Thread(target=server.run,daemon=True);thread.start()
  try:
   for _ in range(100):
    if server.started:break
    time.sleep(.1)
   else:raise RuntimeError('Local test server failed to start')
   with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.getenv('BROWSER_EXECUTABLE','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    errors=[]
    def customer(email,width):
     page=browser.new_context(viewport={'width':width,'height':900}).new_page()
     page.on('pageerror',lambda e:errors.append(str(e)))
     page.goto(base+'/#register',wait_until='networkidle')
     form=page.locator('[data-member-form=register]');form.locator('[name=email]').fill(email);form.locator('[name=password]').fill(password);form.locator('button').click()
     page.wait_for_selector('[data-member-form=login]')
     form=page.locator('[data-member-form=login]');form.locator('[name=email]').fill(email);form.locator('[name=password]').fill(password);form.locator('button').click();page.wait_for_selector('[data-member-action=logout]')
     return page
    visitor=browser.new_page(viewport={'width':390,'height':844})
    visitor.goto(base+'/#home',wait_until='networkidle')
    assert visitor.locator('.membership-invitation').is_visible()
    assert visitor.locator('.membership-invitation a[href="#register"]').inner_text()=='Sign up and subscribe'
    assert visitor.locator('.home-feature').count()==6
    visitor.locator('.membership-invitation a[href="#register"]').click()
    visitor.wait_for_selector('[data-member-form=register]')
    assert visitor.get_by_role('heading',name='Sign up and subscribe',exact=True).is_visible()
    visitor.close()
    page=customer('stripe-buyer@example.test',390)
    assert page.locator('[data-member-action=stripe]').count()==0
    assert 'No free trials' not in page.locator('body').inner_text()
    assert page.get_by_role('button',name='$5.99 monthly',exact=True).count()==1
    assert page.get_by_role('button',name='$45 yearly',exact=True).count()==1
    assert page.get_by_role('button',name='Buy lifetime access',exact=True).count()==1
    assert page.locator('[data-member-action="paypal-api:month"]').is_enabled()
    assert page.locator('[data-member-action="paypal-api:year"]').is_enabled()
    assert 'No ongoing commitment' in page.locator('[data-plan-summary]').inner_text()
    assert 'No automatic renewal' in page.locator('[data-plan-summary]').inner_text()
    assert '$5.99' in page.locator('[data-plan-summary]').inner_text()
    assert page.get_by_role('link',name='Pay Cash App · $lvcenterprise').count()==1
    assert page.get_by_role('link',name='Pay Venmo · @lvcenterprise').count()==1
    switches=['STRIPE_CHECKOUT_ENABLED','PAYPAL_API_ENABLED','PAYPAL_SUBSCRIPTIONS_ENABLED']
    for switch in switches:os.environ[switch]='false'
    page.reload(wait_until='networkidle')
    assert page.locator('[data-member-action=stripe]').count()==0
    assert page.locator('[data-member-action="paypal-api:month"]').is_disabled()
    assert page.locator('[data-member-form=payment]').count()==1
    for switch in switches:os.environ[switch]='true'
    page.reload(wait_until='networkidle')
    # Preserve existing Stripe payment verification without advertising new Stripe checkout.
    context=page.evaluate("""async()=>{const response=await fetch('/api/account/stripe/context',{method:'POST',headers:{'Content-Type':'application/json',...Membership.headers()},body:'{}'});if(!response.ok)throw Error('Fixture checkout context failed');return response.json()}""")
    token=context['client_reference_id']
    assert context['table_id']==o.STRIPE_TABLE and context['publishable_key']==o.STRIPE_PUBLIC
    assert token and not page.evaluate('Membership.user.active')
    for width in [320,375,390,430,1280,1440,1920]:
     page.set_viewport_size({'width':width,'height':900});assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
     page.locator('[data-member-action=export]').scroll_into_view_if_needed()
     assert page.locator('[data-member-action=export]').evaluate('''node=>{const b=node.getBoundingClientRect(),dock=document.querySelector('.bottomdock');return b.bottom<=(getComputedStyle(dock).display==='none'?innerHeight:dock.getBoundingClientRect().top)}'''),width
    objects['checkout/sessions/cs_browser']={'id':'cs_browser','livemode':True,'client_reference_id':token,'mode':'payment','payment_status':'paid','created':m.now(),
      'currency':'usd','amount_subtotal':6000,'amount_total':6000,'payment_intent':'pi_browser','line_items':{'data':[{'quantity':1,'price':price('lifetime')}]}}
    event={'id':'evt_browser','object':'event','type':'checkout.session.completed','livemode':True,'data':{'object':{'id':'cs_browser'}}}
    raw=json.dumps(event).encode();timestamp=m.now();signature=hmac.new(b'whsec_fixture',str(timestamp).encode()+b'.'+raw,hashlib.sha256).hexdigest()
    r=httpx.post(base+'/api/account/stripe/webhook',content=raw,headers={'stripe-signature':f't={timestamp},v1={signature}'});assert r.status_code==200,r.text
    page.locator('[data-member-action=refresh]').click();page.wait_for_function('Membership.user.lifetime===1 && Membership.user.active===true')
    print('PASS: Stripe checkout is absent from customer UI; existing signed fulfillment remains valid; 7 viewport widths.',flush=True)
    page=customer('paypal-year-buyer@example.test',1440)
    def created(data):
     objects['/v1/billing/subscriptions/I-BROWSER']={'id':'I-BROWSER','custom_id':data['custom_id'],'plan_id':data['plan_id'],'create_time':datetime.now(timezone.utc).isoformat(),'status':'ACTIVE'}
     return 'I-BROWSER'
    page.expose_function('recordPaypalFixture',created)
    sdk="window.spiritualPayPal={Buttons:opts=>({render:target=>{const b=document.createElement('button');b.textContent='Fixture PayPal approve';b.onclick=async()=>{const id=await opts.createSubscription({}, {subscription:{create:window.recordPaypalFixture}});await opts.onApprove({subscriptionID:id})};target.append(b)}})}"
    page.route('https://www.paypal.com/sdk/js?*',lambda r:r.fulfill(content_type='text/javascript',body=sdk))
    page.locator('[data-member-action="paypal-api:year"]').click()
    page.wait_for_selector('#membership-paypal-button')
    assert page.evaluate("document.activeElement.id==='membership-paypal-button'")
    page.get_by_role('button',name='Fixture PayPal approve').click()
    page.wait_for_function('document.body.innerText.includes("PayPal approval received")')
    assert objects['/v1/billing/subscriptions/I-BROWSER']['plan_id']==o.PAYPAL_PLANS['year']
    assert not page.evaluate('Membership.user.active')
    event={'event_type':'PAYMENT.SALE.COMPLETED','resource':{'id':'BROWSER123','billing_agreement_id':'I-BROWSER','state':'completed','create_time':datetime.now(timezone.utc).isoformat(),'amount':{'total':'45.00','currency':'USD'}}}
    r=httpx.post(base+'/api/account/paypal/webhook',json=event,headers={'paypal-auth-algo':'SHA256withRSA','paypal-cert-url':'https://api.paypal.com/v1/notifications/certs/fixture','paypal-transmission-id':'fixture','paypal-transmission-sig':'fixture','paypal-transmission-time':datetime.now(timezone.utc).isoformat()});assert r.status_code==200,r.text
    page.locator('[data-member-action=refresh]').click();page.wait_for_function('Membership.user.active===true')
    assert page.get_by_role('link',name='Manage or cancel existing PayPal billing').count()==1
    print('PASS: yearly SDK uses confirmed plan ID and opaque account binding; browser approval alone stays unpaid; verified sale activates yearly access.',flush=True)
    page=customer('paypal-lifetime-buyer@example.test',390);page.on('dialog',lambda d:d.accept())
    posted={}
    def form(route):
     posted.update({key:value[0] for key,value in parse_qs(route.request.post_data).items()})
     route.fulfill(content_type='text/html',body='<h1>Fixture PayPal checkout</h1>')
    page.route('https://www.paypal.com/cgi-bin/webscr',form)
    page.locator('[data-member-action=paypal-lifetime]').click();page.wait_for_url('https://www.paypal.com/cgi-bin/webscr')
    assert posted['hosted_button_id']==o.LIFETIME_BUTTON and posted['custom']
    event={'receiver_id':old.MERCHANT,'receiver_email':old.EMAIL,'txn_type':'web_accept','txn_id':'LIFEBROWSER','custom':posted['custom'],'payment_status':'Completed','mc_currency':'USD','mc_gross':'60.00','payment_date':datetime.now(timezone.utc).isoformat()}
    r=httpx.post(base+'/api/account/paypal/ipn',content=urlencode(event),headers={'content-type':'application/x-www-form-urlencoded'});assert r.status_code==200,r.text
    page.goto(base+'/#account',wait_until='networkidle');page.wait_for_function('Membership.user.lifetime===1 && Membership.user.active===true')
    assert not errors,errors
    print('PASS: lifetime Buy Now uses supplied button and account reference; verified $60 IPN grants access. No live provider payment was made.',flush=True)
    browser.close()
  finally:
   server.should_exit=True;thread.join(timeout=10)


if __name__=='__main__':main()
