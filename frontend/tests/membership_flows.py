"""Customer and owner flows against an isolated, enforced membership backend."""
import os
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
import browser_flows


def exercise(base, screenshots):
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(executable_path=os.getenv('BROWSER_EXECUTABLE','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  owner=browser.new_page(viewport={'width':1440,'height':1000})
  errors=[];owner.on('pageerror',lambda error:errors.append(str(error)))
  owner.goto(base,wait_until='networkidle')
  owner.get_by_role('button',name='Account',exact=True).click()
  def login(page,email):
   form=page.locator('[data-member-form="login"]');form.locator('[name="email"]').fill(email);form.locator('[name="password"]').fill('cloud garden test password 88');form.get_by_role('button',name='Log in',exact=True).click();page.wait_for_selector('[data-member-action="logout"]')
  login(owner,'owner@example.test')
  assert owner.get_by_role('heading',name='Owner dashboard').count()==1
  customer=browser.new_context(viewport={'width':390,'height':844}).new_page()
  customer.on('pageerror',lambda error:errors.append(str(error)))
  customer.goto(base+'/#register',wait_until='networkidle')
  assert customer.locator('[data-member-form="register"]').count()==1
  form=customer.locator('[data-member-form="register"]');form.locator('[name="email"]').fill('buyer@example.test');form.locator('[name="password"]').fill('cloud garden test password 88');form.get_by_role('button',name='Create account').click()
  customer.wait_for_selector('[data-member-form="login"]');login(customer,'buyer@example.test')
  assert not customer.evaluate('Membership.user.active')
  form=customer.locator('[data-member-form="payment"]');form.locator('[name="reference"]').fill('TEST-CASH-REF');form.get_by_role('button',name='Submit payment for verification').click()
  customer.wait_for_function('document.body.innerText.includes("Access begins only after")')
  assert not customer.evaluate('Membership.user.active')
  owner.locator('[data-member-action="admin"]').click();owner.wait_for_selector('[data-member-action^="approve:"]')
  owner.on('dialog',lambda dialog:dialog.accept('TEST-VERIFIED-RECEIPT'))
  owner.locator('[data-member-action^="approve:"]').click();owner.wait_for_function('document.body.innerText.includes("Request reviewed")')
  customer.locator('[data-member-action="refresh"]').click();customer.wait_for_function('Membership.user.active===true')
  customer.locator('[data-member-action="close"]').click() if customer.locator('[data-member-action="close"]').count() else None
  for width in [320,375,390,430,1440]:
   customer.set_viewport_size({'width':width,'height':900});customer.evaluate('transition("home")');assert customer.locator('.home-feature').count()==6
   assert not customer.evaluate('document.documentElement.scrollWidth>innerWidth'),width
  customer.set_viewport_size({'width':390,'height':844});customer.evaluate('transition("explore","metadata")');assert customer.locator('#metadata-name').is_visible()
  customer.get_by_role('button',name='Account',exact=True).click()
  customer.evaluate('Membership.storage.setItem("sv_private_journal", JSON.stringify([{title:"Private buyer note",text:"Keep this safe"}]))')
  form=owner.locator('[data-member-form="gift"]');form.locator('[name="kind"]').select_option('lifetime');form.get_by_role('button',name='Generate new gift code').click();owner.wait_for_selector('.membership-secret');code=owner.locator('.membership-secret').inner_text()
  form=customer.locator('[data-member-form="redeem"]');form.locator('[name="code"]').fill(code);form.get_by_role('button',name='Redeem gift').click();customer.wait_for_function('Membership.user.lifetime===1')
  customer.locator('[data-member-action="logout"]').click();customer.wait_for_function('typeof Membership!=="undefined" && Membership.user===null');customer.wait_for_load_state('networkidle')
  assert customer.evaluate('sessionStorage.getItem("sv_session")') is None
  customer.get_by_role('button',name='Account',exact=True).click();login(customer,'buyer@example.test')
  assert 'Keep this safe' in customer.evaluate('Membership.storage.getItem("sv_private_journal")')
  screenshots.mkdir(parents=True,exist_ok=True)
  for width in [320,390,1440]:
   customer.set_viewport_size({'width':width,'height':900});customer.screenshot(path=str(screenshots/f'account-{width}.png'),full_page=True)
  assert not errors,errors
  browser.close()
  print('PASS: signup/login, owner-only approval, no self-unlock, gift redemption, private saves, logout, and responsive paid tools.')


if __name__=='__main__':
 with tempfile.TemporaryDirectory(prefix='sv-membership-browser-') as temporary:
  os.environ.update(MEMBERSHIP_REQUIRED='true',MEMBERSHIP_DB_PATH=str(Path(temporary)/'members.db'),MEMBERSHIP_USER_DATA_DIR=str(Path(temporary)/'users'),MEMBERSHIP_PUBLIC_URL='https://example.test',MEMBERSHIP_SUPPORT_EMAIL='owner@example.test')
  from backend.services import memberships as m
  with m.database() as db:db.execute('INSERT INTO members(email,password,admin,created) VALUES(?,?,1,?)',('owner@example.test',m.password_hash('cloud garden test password 88'),m.now()))
  browser_flows.exercise=exercise
  browser_flows.main()
