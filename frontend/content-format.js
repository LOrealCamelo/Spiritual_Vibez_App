/* Shared readable exports. Never publish a person's chart data in an invite URL. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.ContentFormat=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const APP_URL='https://app.neurospicymystic.com/';
 const hidden=new Set(['id','session_id','user_id','brand','wheel_svg','image_svg','moon_image_svg','moon_image_url','image_url','raw','raw_response']);
 const labels={bazi:'BaZi',birth_year:'Birth year',animal_sign:'Zodiac animal',stem_branch_title:'Year sign',year_pillar:'Year pillar',month_pillar:'Month pillar',day_master:'Day master',hour_pillar:'Hour pillar',domain:'Represents',natal_moon_phase:'Natal Moon phase',description_upright:'Upright meaning',description_reversed:'Reversed meaning',birth_utc:'Birth time (UTC)',birth_local_time:'Local birth time'};
 function label(key){return labels[key]||String(key).replace(/[_-]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase());}
 function clean(value){return String(value??'').replace(/<svg[\s\S]*?<\/svg>/gi,'').replace(/<[^>]*>/g,'').replace(/[ \t]+/g,' ').trim();}
 function readable(value,depth=0){
  if(value==null||depth>15)return '';
  if(value?.report_type==='astrocartography')return readable({title:value.title,name:value.name,birth_local_time:value.birth_local_time,birthplace:value.location?.label,focus:value.focus,planetary_themes:value.planets.map(p=>p.planet+': '+p.interpretation),angle_meanings:value.angle_meanings,places:value.places,inspected_location:value.inspected_location,proximity_note:value.proximity_note,note:value.note,method:value.method,map_credit:value.map_credit},depth+1);
  if(Array.isArray(value))return value.map(x=>readable(x,depth+1)).filter(Boolean).join('\n\n');
  if(typeof value==='object')return Object.entries(value).filter(([k,v])=>!hidden.has(k)&&!/_svg$/.test(k)&&v!=null).map(([key,v])=>{
   const body=readable(v,depth+1);if(!body)return '';
   return (typeof v==='object'?label(key)+'\n':label(key)+': ')+body;
  }).filter(Boolean).join('\n\n');
  return typeof value==='boolean'?(value?'Yes':'No'):clean(value);
 }
 function invite(route='home'){return APP_URL+'#'+String(route).replace(/[^a-zA-Z0-9/_-]/g,'');}
 function chartSummary(value){
  if(!value?.wheel_svg)return '';
  return [value.name,value.title,value.location?.label,value.birth_local_time,value.zodiac_label,value.ascendant?'Ascendant: '+value.ascendant:null,value.midheaven?'Midheaven: '+value.midheaven:null,...(value.placements||[]).map(p=>p.planet+' in '+p.sign+' · House '+p.house),...(value.asteroids||[]).map(p=>p.name+' · '+p.formatted+' · House '+p.house),'The complete interpretation is included in the accompanying text.'].filter(Boolean).join('\n');
 }
 function snapshot({title,text,value,route='home',imageSvg,imageSource,imageUrl}){
  const body=clean(text||'')||readable(value)||'Explore this feature in Spiritual Vibz.';
  return {title:clean(title)||'Spiritual Vibz',text:body,route,url:invite(route),imageSvg,imageSource,imageUrl,imageText:chartSummary(value)};
 }
 function message(item){return item.title+'\n\n'+item.text+'\n\nGet your own here: '+item.url;}
 function summary(item,max=2100){const text=item.imageText||item.text;if(text.length<=max)return text;const cut=text.slice(0,max).replace(/\s+\S*$/,'');return cut+'…\n\nThe full reading is included in the accompanying text.';}
 return {APP_URL,label,readable,clean,invite,snapshot,message,summary};
});
