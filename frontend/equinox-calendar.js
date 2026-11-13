/* Custom 13 x 28-day equinox calendar; the shared backend owns all date math. */
function civilToday(){const d=new Date();return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-')}
const equinoxUI={date:civilToday(),timezone:Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC',busy:false,request:0};
function equinoxForm(){return '<p>Thirteen months of 28 days, beginning on the March spring equinox.</p><div class="controls">'+field('Gregorian date','calendar-date','date',equinoxUI.date,'min="1601-01-01" max="2400-12-31"')+'</div><p>'+e(equinoxUI.timezone)+'</p>'+btn(equinoxUI.busy?'Loading…':'Show calendar','tool-run','',equinoxUI.busy?'disabled':'')+' '+btn('Today','equinox-today','cream');}
async function loadEquinoxCalendar(view={}){
 const request=++equinoxUI.request;const date=view.today?civilToday():(val('calendar-date')||equinoxUI.date);
 equinoxUI.date=date;equinoxUI.busy=true;state.error='';state.result=null;render();
 const params=new URLSearchParams({date,timezone:equinoxUI.timezone});
 if(view.year!=null)params.set('year',view.year);if(view.month!=null)params.set('month',view.month);
 try{const data=await api('/astrology/calendar-13-month?'+params);if(request===equinoxUI.request&&state.tool==='calendar')state.result=data}
 catch(ex){if(request===equinoxUI.request&&state.tool==='calendar')state.error=ex.message}
 finally{if(request===equinoxUI.request){equinoxUI.busy=false;if(state.tool==='calendar')render()}}
}
function equinoxResult(o){
 const nav=(v,label)=>v?btn(label,'equinox-month','cream','data-year="'+v.year+'" data-month="'+v.month+'"'):'';
 return '<section class="result equinox-calendar"><h2>'+e(o.converted_date.label)+'</h2><p>'+e(o.selected_date)+' · '+e(o.timezone)+'</p><p>Equinox year '+o.year+': '+e(o.year_start)+' to '+e(o.next_year_start)+' ('+o.year_days+' days)</p><h3>'+e(o.month_name)+' · '+e(o.months[o.month_number-1].start_date)+' – '+e(o.months[o.month_number-1].end_date)+'</h3><div class="controls">'+nav(o.previous,'← Previous month')+nav(o.next,'Next month →')+'</div><nav class="equinox-months" aria-label="All thirteen months">'+o.months.map(m=>'<button class="chip" data-action="equinox-month" data-year="'+o.year+'" data-month="'+m.number+'" aria-pressed="'+(m.number===o.month_number)+'">Month '+m.number+'</button>').join('')+'</nav><p>Four weeks · seven days in every week</p><div class="equinox-grid" role="group" aria-label="28 days in '+e(o.month_name)+'">'+o.days.map(d=>'<button data-action="equinox-date" data-date="'+d.gregorian_date+'" aria-label="Month '+o.month_number+', Day '+d.day+' · '+d.gregorian_date+'" aria-pressed="'+d.is_selected+'" class="equinox-day'+(d.is_today?' is-today':'')+'"><strong>'+d.day+'</strong><small>'+e(d.gregorian_date.slice(5))+'</small>'+(d.is_today?'<small>Today</small>':'')+'</button>').join('')+'</div><h3>Days outside the months and weeks</h3>'+o.extra_days.map(d=>'<p><button class="chip" data-action="equinox-date" data-date="'+d.gregorian_date+'" aria-pressed="'+d.is_selected+'">'+e(d.label)+' · '+e(d.gregorian_date)+'</button></p>').join('')+'<p>'+e(o.note)+'</p></section>';
}
document.addEventListener('click',ev=>{const b=ev.target.closest('[data-action]');if(!b||state.tool!=='calendar')return;const a=b.dataset.action;
 if(a==='equinox-today'){ev.preventDefault();loadEquinoxCalendar({today:true})}
 if(a==='equinox-month'){ev.preventDefault();loadEquinoxCalendar({year:Number(b.dataset.year),month:Number(b.dataset.month)})}
 if(a==='equinox-date'){ev.preventDefault();equinoxUI.date=b.dataset.date;const input=document.getElementById('calendar-date');if(input)input.value=equinoxUI.date;loadEquinoxCalendar()}
});
