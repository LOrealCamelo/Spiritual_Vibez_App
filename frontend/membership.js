/* Optional, server-enforced membership UI shared by desktop and mobile web/PWA.
   Session tokens stay in this tab's sessionStorage; passwords never persist. */
'use strict';
const Membership=(()=>{
 let config={required:false},user=null,token='',ready=false,mode='login',message='',busy=false,adminPayments=[],adminGifts=[],adminMembers=[],oneTime='',lastPage='';
 const raw=window.localStorage;
 const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const apiBase=()=>((location.hostname.endsWith('.netlify.app')||location.hostname==='app.neurospicymystic.com')?'https://spiritual-vibez-app.onrender.com/api':'/api');
 const storage={getItem(key){return raw.getItem(config.required?(user?'sv_member_'+user.id+':'+key:'sv_logged_out:'+key):key)},setItem(key,value){if(config.required&&!user)throw Error('Log in to save private entries.');raw.setItem(config.required?'sv_member_'+user.id+':'+key:key,value)}};
 function headers(){return token?{Authorization:'Bearer '+token}:{}}
 async function request(path,body){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),60000);
  try{
   const response=await fetch(apiBase()+'/account'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',...headers()},...(body===undefined?{}:{body:JSON.stringify(body)}),signal:controller.signal});
   const data=await response.json();
   if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:'Please check your entries and try again.');
   return data;
  }finally{clearTimeout(timer)}
 }
 async function initialize(){
  try{config=await request('/config');try{token=sessionStorage.getItem('sv_session')||''}catch{}
   if(token){try{user=await request('/me')}catch{token='';try{sessionStorage.removeItem('sv_session')}catch{}}}
  }catch{config={required:true,unavailable:true};message='Account services are temporarily unavailable. Please try again.'}
  ready=true;
 }
 const blocked=()=>!ready||config.unavailable||(config.required&&!user?.active);
 const field=(name,label,type='text',extra='')=>'<label>'+label+'<input name="'+name+'" type="'+type+'" '+extra+' required></label>';
 const button=(label,action)=>'<button type="button" data-member-action="'+action+'" '+(busy?'disabled':'')+'>'+label+'</button>';
 function screen(){
  let html='<section class="membership-panel" aria-labelledby="account-heading"><h1 id="account-heading">Your Spiritual Vibz account</h1>';
  if(config.accounts_configured===false)return html+'<p>Account setup is not active yet. Please contact the owner before sending payment.</p></section>';
  if(config.unavailable)return html+'<p role="alert">'+esc(message)+'</p>'+button('Retry','retry')+'</section>';
  if(message)html+='<p role="status">'+esc(message)+'</p>';
  if(!user){
   html+='<div class="membership-options">'+button('Log in','mode:login')+button('Sign up','mode:register')+button('Forgot password','mode:forgot')+button('Reset password','mode:reset')+'</div>';
   html+='<form id="membership-form" data-member-form="'+mode+'">';
   if(mode==='reset')html+=field('token','Private reset code','text','autocomplete="off" minlength="20" maxlength="200"');
   else html+=field('email','Email','email','autocomplete="email" maxlength="254"');
   if(mode!=='forgot')html+=field('password',mode==='register'?'Choose a password (at least 12 characters)':'Password','password','autocomplete="'+(mode==='login'?'current-password':'new-password')+'" minlength="12" maxlength="256"');
   html+='<button '+(busy?'disabled':'')+'>'+({login:'Log in',register:'Create account',forgot:'Request recovery',reset:'Set new password'}[mode])+'</button></form>';
   if(mode==='forgot'&&!config.password_reset_email)html+='<p>Email recovery is not configured yet. Contact support for verified recovery.</p>';
  }else{
   html+='<p>Signed in as '+esc(user.email)+'</p><p>Membership: <strong>'+(user.admin?'Administrator':user.lifetime?'Lifetime access':user.active?'Active until '+new Date(user.expires*1000).toLocaleDateString():'Not active')+'</strong></p>'+button('Log out','logout');
   if(config.owner_ready&&!user.lifetime&&!user.admin&&config.paypal_enabled)html+='<h2>$5.99 USD monthly</h2><p>PayPal automatically renews monthly until you cancel. Cancel anytime in PayPal Automatic Payments to prevent future charges. Your first payment is due at checkout. Access starts after payment verification and lasts through your paid period.</p>'+button('Start subscription with PayPal','paypal')+'<p><a href="https://www.paypal.com/myaccount/autopay/" target="_blank" rel="noopener noreferrer">Manage or cancel in PayPal</a></p><p>Returning from PayPal does not activate access. Wait for payment verification, then refresh your membership status.</p>';;
   if(config.owner_ready&&!user.lifetime&&!user.admin)html+='<h2>$5.99 USD per month</h2><p>Cash App / Venmo alternative: manual renewal, with no automatic charges. Pay only once per renewal, using either service. Copy your transaction reference afterward.</p><div class="membership-options"><a href="'+esc(config.cashapp)+'" target="_blank" rel="noopener noreferrer">Pay Cash App · $lvcenterprise</a><a href="'+esc(config.venmo)+'" target="_blank" rel="noopener noreferrer">Pay Venmo · @lvcenterprise</a></div><p>Confirm the recipient before paying. Access starts only when the owner verifies receipt and approves your request.</p><form data-member-form="payment"><label>Payment service<select name="provider"><option value="cashapp">Cash App</option><option value="venmo">Venmo</option></select></label>'+field('reference','Transaction reference (not a screenshot)','text','minlength="4" maxlength="150"')+'<button '+(busy?'disabled':'')+'>Submit payment for verification</button></form>';
   if(!config.paypal_enabled&&user.active&&!user.admin&&!user.lifetime&&user.expires*1000-Date.now()<7*86400000)html+='<p role="status">Your membership expires within seven days. Renew manually if you want to continue; there will be no automatic charge.</p>';
   if(config.paypal_enabled)html+='<p><a href="https://www.paypal.com/myaccount/autopay/" target="_blank" rel="noopener noreferrer">Manage or cancel existing PayPal billing</a></p>';
   html+='<h2>Redeem your gift</h2><p>Each code works once. Gifts grant one month or lifetime access and never start automatic billing. If you already subscribe with PayPal, cancel that billing in PayPal separately to stop future charges.</p><form data-member-form="redeem">'+field('code','Gift code','text','autocomplete="off" minlength="8" maxlength="200"')+'<button '+(busy?'disabled':'')+'>Redeem gift</button></form>'+button('Refresh membership and payment status','refresh')+button('Download my data','export');
   if(raw.getItem('sv_private_journal')||raw.getItem('sv_moods')||raw.getItem('sv_ritual_page_bookmarks'))html+='<details><summary>Existing entries on this device</summary><p>Old browser entries remain untouched. Import them only if they belong to you. Import copies them into this account on this browser; it does not upload them or delete originals.</p>'+button('Copy my old entries into this account','import')+'</details>';
   html+='<p>New browser saves are separate for each account on this device. They do not synchronize to other devices.</p>';
   if(user.admin)html+=adminScreen();
  }
  if(config.support_email)html+='<p>Support: <a href="mailto:'+esc(config.support_email)+'">'+esc(config.support_email)+'</a></p>';
  return html+'</section>';
 }
 function adminScreen(){
  return '<section class="membership-admin"><h2>Owner dashboard</h2>'+button('Refresh owner dashboard','admin')+'<h3>Payment verification</h3><p>Open your payment app and independently verify the completed $5.99 USD receipt, recipient, customer and transaction reference. Never approve based only on this form, an email or a screenshot.</p>'+adminPayments.map(p=>'<article><p>#'+p.id+' · '+esc(p.email)+' · '+esc(p.provider)+' · '+esc(p.reference)+' · '+esc(p.status)+'</p>'+(p.status==='pending'?button('Approve verified $5.99 receipt','approve:'+p.id)+button('Reject request','reject:'+p.id):'')+'</article>').join('')+
   '<h3>Create a unique single-use gift</h3><form data-member-form="gift"><label>Access granted<select name="kind"><option value="month">One calendar month</option><option value="lifetime">Lifetime</option></select></label><label>Code must be redeemed within (days)<input name="valid_days" type="number" min="1" max="365" value="30" required></label><button '+(busy?'disabled':'')+'>Generate new gift code</button></form>'+(oneTime?'<p>Copy and deliver privately now. This secret is shown only in this session:</p><output class="membership-secret">'+esc(oneTime)+'</output>':'')+
   '<h3>Gift status</h3>'+adminGifts.map(g=>'<article>'+esc(g.kind)+' · '+(g.redeemed_by?'Used':g.revoked?'Revoked':g.expires*1000<Date.now()?'Expired':'Unused')+(g.redeemed_by||g.revoked?'':button('Revoke unused code','revoke:'+g.hash))+'</article>').join('')+
   '<h3>Account recovery and access</h3><p>Issue a recovery code only after privately verifying the account owner. Suspending access or granting a gift does not cancel existing PayPal billing; manage that separately in PayPal.</p>'+adminMembers.map(u=>'<article>'+esc(u.email)+' · '+(u.active?'Active':'Inactive')+button('Issue private recovery code','recover:'+u.id)+(u.admin?'':button(u.disabled?'Restore account access':'Suspend account access',(u.disabled?'restore:':'suspend:')+u.id))+'</article>').join('')+'</section>';
 }
 function cleanPrivateState(){
  if(typeof stopAudio==='function')stopAudio();
  if(typeof LovePage!=='undefined')LovePage.clear();
  if(typeof state!=='undefined'){Object.assign(state,{page:'home',tool:null,result:null,transit:null,reading:'',drawn:{},selected:null,cardDetail:null,quiz:null,answer:'',shadowAnswers:{},shadowMessage:'',cycles:null});}
  document.querySelector('.share-preview')?.remove();
  if(typeof contentItems!=='undefined')contentItems.clear();
 }
 function show(){document.querySelector('#membership-overlay')?.remove();const existing=document.querySelector('main .membership-panel');if(existing){existing.outerHTML=screen();document.querySelector('main .membership-panel input,main .membership-panel button')?.focus();return;}const overlay=document.createElement('div');overlay.id='membership-overlay';overlay.className='membership-overlay';overlay.innerHTML='<div class="membership-dialog" role="dialog" aria-modal="true" aria-label="Account and membership">'+button('Close','close')+screen()+'</div>';document.body.append(overlay);overlay.querySelector('button')?.focus();}
 async function refresh(){user=await request('/me');}
 function accessDenied(status){if(status===403&&user)user.active=false;if(status===401){token='';user=null;try{sessionStorage.removeItem('sv_session')}catch{}cleanPrivateState();location.reload();}show();}
 async function loadAdmin(){[adminPayments,adminGifts,adminMembers]=await Promise.all([request('/admin/payments'),request('/admin/gifts'),request('/admin/members')]);}
 async function action(task){if(busy)return;busy=true;message='';document.querySelectorAll('.membership-panel').forEach(panel=>{panel.setAttribute('aria-busy','true');panel.querySelectorAll('button').forEach(control=>control.disabled=true)});try{await task()}catch(error){message=error.message}finally{busy=false;if(typeof render==='function')render();show()}}
 document.addEventListener('keydown',event=>{
  const overlay=document.querySelector('#membership-overlay');if(!overlay)return;
  if(event.key==='Escape'){overlay.remove();document.querySelector('[data-member-action="open"]')?.focus();}
  if(event.key==='Tab'){
   const controls=[...overlay.querySelectorAll('button:not([disabled]),input,select,a[href]')];
   const first=controls[0],last=controls[controls.length-1];
   if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}
   else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}
  }
 });
 document.addEventListener('submit',event=>{
  const form=event.target.closest('[data-member-form]');if(!form)return;event.preventDefault();
  const values=Object.fromEntries(new FormData(form)),kind=form.dataset.memberForm;
  action(async()=>{
   if(kind==='login'){const result=await request('/login',values);token=result.token;user=result.user;try{sessionStorage.setItem('sv_session',token)}catch{}cleanPrivateState();message='You are signed in.';if(user.admin)await loadAdmin();if(typeof boot==='function')await boot();}
   if(kind==='register'){message=(await request('/register',values)).message;mode='login';}
   if(kind==='forgot'){message=(await request('/forgot-password',values)).message;}
   if(kind==='reset'){message=(await request('/reset-password',values)).message;mode='login';}
   if(kind==='payment'){message=(await request('/payments',values)).message;}
   if(kind==='redeem'){message=(await request('/redeem',values)).message;await refresh();if(typeof boot==='function')await boot();}
   if(kind==='gift'){const result=await request('/admin/gifts',{...values,valid_days:Number(values.valid_days)});oneTime=result.code;await loadAdmin();message=result.message;}
  });
 });
 document.addEventListener('click',event=>{
  const control=event.target.closest('[data-member-action]');if(!control)return;
  const [name,value]=control.dataset.memberAction.split(':');
  if(name==='open'){message='';show();return}
  if(name==='close'){document.querySelector('#membership-overlay')?.remove();return}
  if(name==='mode'){mode=value;message='';show();return}
  action(async()=>{
   if(name==='paypal'){
    if(!confirm('Subscribe for $5.99 USD now and every month until cancelled in PayPal?'))return;
    const checkout=await request('/paypal/checkout',{});
    if(checkout.action!=='https://www.paypal.com/cgi-bin/webscr')throw Error('Unexpected checkout address.');
    const form=document.createElement('form');form.method='POST';form.action=checkout.action;
    for(const [name,value] of Object.entries(checkout.fields)){const input=document.createElement('input');input.type='hidden';input.name=name;input.value=value;form.append(input)}
    document.body.append(form);form.submit();return;
   }
   if(name==='retry'){await initialize();if(!blocked()&&typeof boot==='function')await boot();}
   if(name==='logout'){try{await request('/logout',{})}finally{token='';user=null;adminPayments=[];adminGifts=[];adminMembers=[];oneTime='';try{sessionStorage.removeItem('sv_session')}catch{}cleanPrivateState();location.reload();message='Signed out. Your saved entries remain on this device.';}}
   if(name==='refresh'){await refresh();const payments=await request('/payments');message=payments.length?payments.map(p=>'Request #'+p.id+': '+p.status+(p.note?' · '+p.note:'')).join('; '):'No payment requests yet.';}
   if(name==='export'){const server=await request('/export');const local={};for(const key of ['sv_private_journal','sv_moods','sv_ritual_page_bookmarks'])local[key]=JSON.parse(storage.getItem(key)||'[]');const url=URL.createObjectURL(new Blob([JSON.stringify({server,local},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='spiritual-vibz-my-data.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);message='Your data download is ready.';}
   if(name==='admin'){await loadAdmin();}
   if(name==='approve'||name==='reject'){const note=prompt(name==='approve'?'Confirm the actual $5.99 receipt in your payment app, then enter its verified reference for the audit record:':'Reason for rejection:');if(!note||note.trim().length<3)throw Error('A verification note or rejection reason is required.');await request('/admin/payments/'+value+'/review',{approve:name==='approve',note,verified_reference:name==='approve'?note:''});await loadAdmin();message='Request reviewed.';}
   if(name==='revoke'){await request('/admin/gifts/'+value+'/revoke',{});await loadAdmin();message='Unused gift code revoked.';}
   if(name==='suspend'||name==='restore'){const reason=prompt('Reason for this access change:');if(!reason||reason.trim().length<3)return;await request('/admin/members/'+value+'/access',{disabled:name==='suspend',reason});await loadAdmin();message='Account access updated; saved data was preserved.';}
   if(name==='recover'){if(!confirm('Have you privately verified this account owner?'))return;oneTime=(await request('/admin/members/'+value+'/reset',{})).code;message='Deliver this recovery code privately. It expires in 30 minutes.';}
   if(name==='import'){
    if(!confirm('Copy old entries from this device into this account? Only continue if they belong to you.'))return;
    const marker='sv_imported_'+user.id;
    if(raw.getItem(marker))throw Error('Old entries were already copied for this account. Originals remain unchanged.');
    for(const key of ['sv_private_journal','sv_moods','sv_ritual_page_bookmarks']){
     let existing=JSON.parse(storage.getItem(key)||'[]'),old=JSON.parse(raw.getItem(key)||'[]');
     if(!Array.isArray(existing)||!Array.isArray(old))throw Error('An old data file could not be read. Originals were preserved.');
     storage.setItem(key,JSON.stringify([...existing,...old]));
    }
    raw.setItem(marker,'1');message='Entries copied locally. Originals were preserved.';
   }
  });
 });
 function page(route){
  if(route==='sales')return '<section class="membership-panel membership-sales"><img class="membership-sales-logo" src="assets/optimized/spiritual-vibz-logo-compact.webp" alt="Spiritual Vibz" width="600" height="240"><h1>Explore your Spiritual Vibz</h1><p>Tarot, lunar guidance, birth charts, rituals and a space for your reflections.</p><ul class="membership-benefits"><li>Daily readings and Tarot</li><li>Moon cycles and lunar guidance</li><li>Birth charts and Your Metadata</li><li>Rituals and reflective practices</li><li>Love Match and shared activity ideas</li><li>Your personal Journal</li></ul><h2>$5.99 USD per month</h2><p>Your first payment is due at checkout. PayPal subscriptions renew automatically until cancelled. Cancel anytime through PayPal. Cash App and Venmo are optional manual payments, without automatic renewal.</p><div class="membership-options"><a href="#register">Create your account</a><a href="#login">Log in</a><a href="#checkout">Membership and checkout</a></div><p>No App Store download needed. Use the app in your browser or add it to your Home Screen.</p></section>';
  if(route!==lastPage){if(route==='register'||route==='login')mode=route;lastPage=route}
  return screen();
 }
 return {page,initialize,headers,blocked,screen,show,storage,accessDenied,get user(){return user},get required(){return config.required}};
})();
