/** Daily astronomical data and city-based charts on both native platforms. */
import React,{useEffect,useRef,useState} from 'react';
import {AppState,ActivityIndicator,Share,StyleSheet,Text,TextInput,TouchableOpacity,View,useWindowDimensions} from 'react-native';
import {SvgXml} from 'react-native-svg';
import {API_BASE_URL} from '../api/spiritualVibezClient';

const SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const query=(params:Record<string,string>)=>Object.entries(params).map(([k,v])=>encodeURIComponent(k)+'='+encodeURIComponent(v)).join('&');
async function request(path:string,payload?:any){
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),20000);
 try{const r=await fetch(API_BASE_URL+path,{signal:controller.signal,...(payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}:{})});
  const result=await r.json();if(!r.ok)throw Error(typeof result.detail==='string'?result.detail:'Unable to calculate ('+r.status+').');return result;
 }finally{clearTimeout(timeout)}
}
function Button({label,onPress,disabled=false}:{label:string,onPress:()=>void,disabled?:boolean}){return <TouchableOpacity accessibilityRole="button" accessibilityLabel={label} onPress={onPress} disabled={disabled} style={[s.button,disabled?{opacity:.5}:null]}><Text style={s.buttonText}>{label}</Text></TouchableOpacity>}
function Input({label,value,onChange,numeric=false,placeholder=''}:{label:string,value:string,onChange:(v:string)=>void,numeric?:boolean,placeholder?:string}){return <View style={{marginBottom:12}}><Text style={s.label}>{label}</Text><TextInput accessibilityLabel={label} style={s.input} value={value} onChangeText={onChange} placeholder={placeholder} placeholderTextColor="#85728e" keyboardType={numeric?'number-pad':'default'}/></View>}
function Choices({values,value,onChange}:{values:[string,string][],value:string,onChange:(v:string)=>void}){return <View style={s.choices}>{values.map(([key,label])=><TouchableOpacity key={key} accessibilityRole="button" accessibilityLabel={label} accessibilityState={{selected:key===value}} onPress={()=>onChange(key)} style={[s.choice,key===value?{backgroundColor:'#e51a9a'}:null]}><Text style={{color:key===value?'white':'#3a156b',fontWeight:'700'}}>{label}</Text></TouchableOpacity>)}</View>}

export function NativeBirthChart({tool='natal'}:{tool?:string}){
 const [name,setName]=useState(''),[date,setDate]=useState(''),[hour,setHour]=useState('12'),[minute,setMinute]=useState('00');
 const [city,setCity]=useState(''),[country,setCountry]=useState('US'),[region,setRegion]=useState(''),[places,setPlaces]=useState<any[]>([]),[place,setPlace]=useState<any>(null);
 const [zodiac,setZodiac]=useState('tropical'),[houses,setHouses]=useState('placidus'),[fold,setFold]=useState('');
 const [busy,setBusy]=useState(false),[error,setError]=useState(''),[result,setResult]=useState<any>(null);
 const cityVersion=useRef(0);
 const updatePlace=(setter:(v:string)=>void)=>(v:string)=>{setter(v);cityVersion.current++;setPlace(null);setPlaces([]);setResult(null)};
 const search=async()=>{const version=cityVersion.current;setBusy(true);setError('');setPlace(null);try{
  const r=await request('/astrology/locations/search?'+query({city,country,state:region}));if(version!==cityVersion.current)return;setPlaces(r.places);
  if(!r.places.length)setError('No matching city found. Check country and state, or try a nearby town. The directory covers towns with at least 1,000 people.');
 }catch(ex:any){setError(ex.message)}finally{setBusy(false)}};
 const calculate=async()=>{
  setError('');setResult(null);if(!place){setError('Find and select your birth city first.');return}
  if(!date||!/^(?:[01]?\d|2[0-3])$/.test(hour)||!/^\d{1,2}$/.test(minute)||Number(minute)>59){setError('Enter a birth date, an hour from 0 to 23, and minutes from 0 to 59.');return}
  setBusy(true);try{setResult(await request('/astrology/'+(tool==='moon'?'moon-phase':'natal-chart'),{name,birth_date:date,birth_time:hour.padStart(2,'0')+':'+minute.padStart(2,'0'),place_id:place.place_id,zodiac,house_system:houses,chart_system:tool==='draconic'?'draconic':'natal',time_fold:fold===''?null:Number(fold)}))}catch(ex:any){setError(ex.message)}finally{setBusy(false)}
 };
 return <>
  <View style={s.panel}><Text style={s.title}>Your birth details</Text>
  <Input label="Name (optional)" value={name} onChange={setName}/><Input label="Birth date YYYY-MM-DD" placeholder="1996-11-05" value={date} onChange={v=>{setDate(v);setFold('')}}/>
  <View style={s.row}><View style={s.flex}><Input label="Hour (0–23)" value={hour} onChange={v=>{setHour(v);setFold('')}} numeric/></View><View style={s.flex}><Input label="Minutes (0–59)" value={minute} onChange={v=>{setMinute(v);setFold('')}} numeric/></View></View>
  <Input label="Country name or code" placeholder="United States or US" value={country} onChange={updatePlace(setCountry)}/><Input label="State / province" placeholder="New York or NY" value={region} onChange={updatePlace(setRegion)}/><Input label="City of birth" value={city} onChange={updatePlace(setCity)}/>
  <Button label="Find my birth city" onPress={search} disabled={busy}/>
  {places.map(p=><TouchableOpacity key={p.place_id} accessibilityRole="button" accessibilityLabel={'Select '+p.label} style={s.place} onPress={()=>{setPlace(p);setPlaces([]);setResult(null);setFold('')}}><Text style={s.label}>{p.label}</Text><Text style={s.body}>{p.timezone}</Text></TouchableOpacity>)}
  {place?<Text style={s.body}>✓ {place.label} · {place.timezone}</Text>:null}
  <Text style={s.label}>Zodiac</Text><Choices values={[["tropical","Tropical"],["sidereal","Sidereal (Lahiri)"]]} value={zodiac} onChange={setZodiac}/>
  {tool!=='moon'?<><Text style={s.label}>House system</Text><Choices values={[["placidus","Placidus"],["whole_sign","Whole Sign"],["equal","Equal"]]} value={houses} onChange={setHouses}/></>:null}
  <Text style={s.body}>Birth time uses your city’s historical timezone. Sidereal uses Lahiri.</Text>
  {error.includes('occurred twice')?<><Text style={s.label}>This clock time occurred twice</Text><Choices values={[["0","First occurrence"],["1","Second occurrence"]]} value={fold} onChange={setFold}/></>:null}
  {error?<Text accessibilityRole="alert" style={s.error}>{error}</Text>:null}
  <Button label={busy?'Working…':tool==='moon'?'Find my natal Moon':'Create my birth chart'} onPress={calculate} disabled={busy}/></View>
  {result?.wheel_svg?<NativeChartReport result={result}/>:result?<View style={s.panel}><Text style={s.title}>{result.emoji} {result.natal_moon_phase}</Text><Text style={s.body}>{result.moon_position} · {result.illumination_percentage}% illuminated</Text><Text style={s.body}>{result.description}</Text><Text style={s.body}>{result.birth_local_time} · {result.location.label}</Text></View>:null}
 </>;
}

export function NativeChartReport({result:o}:{result:any}){
 const {width}=useWindowDimensions();const size=Math.min(width-64,680);
 const reportText=()=>[o.name,o.title,o.birth_local_time,o.location.label,o.zodiac_label,o.house_system+' houses',...o.placements.flatMap((p:any)=>[p.planet+' in '+p.sign+', house '+p.house,...p.paragraphs]),...o.houses.map((h:any)=>h.description),...o.aspects.map((a:any)=>a.planet_a+' '+a.aspect+' '+a.planet_b+': '+a.description),o.report_note].join('\n\n');
 return <View style={s.panel}><Text style={s.title}>{o.name?o.name+'’s ':''}{o.title}</Text><Text style={s.body}>{o.location.label} · {o.birth_local_time}</Text><Text style={s.body}>{o.zodiac_label} · {o.house_system.replace(/_/g,' ')} houses</Text>
 <View accessible accessibilityLabel="Birth chart wheel showing zodiac signs, twelve houses and planetary positions" style={{alignItems:'center'}}><SvgXml xml={o.wheel_svg} width={size} height={size}/></View>
 <Text style={s.label}>Ascendant: {o.ascendant}</Text><Text style={s.label}>Midheaven: {o.midheaven}</Text>
 <Text style={s.title}>Your planets: signs & houses</Text>{o.placements.map((p:any)=><View key={p.planet} style={s.section}><Text style={s.heading}>{p.planet} in {p.sign} · House {p.house}</Text><Text style={s.label}>{p.formatted} · {p.motion}</Text>{p.paragraphs.map((t:string,i:number)=><Text key={i} selectable style={s.body}>{t}</Text>)}</View>)}
 <Text style={s.title}>Your twelve houses</Text>{o.houses.map((h:any)=><View key={h.number} style={s.section}><Text style={s.heading}>House {h.number} · {h.title}</Text><Text style={s.label}>{h.formatted}</Text><Text selectable style={s.body}>{h.description}</Text></View>)}
 <Text style={s.title}>Major planetary aspects</Text>{o.aspects.map((a:any,i:number)=><View key={i} style={s.section}><Text style={s.heading}>{a.planet_a} {a.aspect} {a.planet_b}</Text><Text style={s.label}>Orb {a.orb.toFixed(2)}°</Text><Text selectable style={s.body}>{a.description}</Text></View>)}
 <Text style={s.title}>Element & modality balance</Text><Text style={s.body}>{Object.entries(o.elements).map(([k,v])=>k+': '+v).join(' · ')}</Text><Text style={s.body}>{Object.entries(o.modalities).map(([k,v])=>k+': '+v).join(' · ')}</Text><Text style={s.body}>{o.report_note}</Text><Button label="Share birth chart report" onPress={()=>Share.share({message:reportText()})}/></View>;
}

export function NativeDailySky(){
 const [sign,setSign]=useState('Scorpio'),[date,setDate]=useState(''),[selectedDate,setSelectedDate]=useState(''),[zodiac,setZodiac]=useState('tropical');
 const [data,setData]=useState<any>(null),[error,setError]=useState(''),[loading,setLoading]=useState(false),[revision,setRevision]=useState(0);
 const timezone=Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC';
 useEffect(()=>{let active=true;setLoading(true);setError('');
  request('/astrology/daily-transits?'+query({sign,timezone,zodiac,...(selectedDate?{date:selectedDate}:{})})).then(r=>{if(active)setData(r)}).catch(ex=>{if(active){setData(null);setError('Unable to load the daily sky: '+ex.message)}}).finally(()=>{if(active)setLoading(false)});
  return()=>{active=false};
 },[sign,selectedDate,zodiac,revision,timezone]);
 useEffect(()=>{const interval=setInterval(()=>setRevision(v=>v+1),60000);const sub=AppState.addEventListener('change',state=>{if(state==='active')setRevision(v=>v+1)});return()=>{clearInterval(interval);sub.remove()}},[]);
 return <><View style={s.panel}><Text style={s.title}>Daily Moon & Planetary Alignment</Text><Input label="Date YYYY-MM-DD (blank = today)" value={date} onChange={setDate}/><Text style={s.body}>Timezone: {timezone}. Today updates automatically; other dates show local noon.</Text><Choices values={[["tropical","Tropical"],["sidereal","Sidereal (Lahiri)"]]} value={zodiac} onChange={setZodiac}/><Text style={s.label}>Your zodiac sign</Text><Choices values={SIGNS.map(x=>[x,x])} value={sign} onChange={setSign}/><Button label="Refresh my cosmic weather" onPress={()=>{setSelectedDate(date);setRevision(v=>v+1)}}/>{loading?<ActivityIndicator accessibilityLabel="Loading daily sky" color="#e51a9a"/>:null}{error?<Text accessibilityRole="alert" style={s.error}>{error}</Text>:null}</View>
 {data?<><View style={s.panel}><Text style={s.title}>{data.moon_emoji} {data.moon_phase}</Text><Text style={s.body}>{data.illumination_percent}% illuminated · {data.moon.waxing?'Waxing':'Waning'}</Text><Text style={s.label}>Sky for {data.date}</Text><Text style={s.body}>{data.as_of} · {data.zodiac_label}</Text><Text style={s.body}>Next {data.moon.next_phase}: {new Date(data.moon.next_phase_at).toLocaleString()}</Text><Text style={s.body}>{data.moon.phase_convention}</Text></View>
 <View style={s.row}>{data.planets.map((p:any)=><View key={p.planet} style={[s.panel,{width:'48%'}]}><Text style={s.heading}>{p.glyph} {p.planet}</Text><Text style={s.body}>{p.formatted}</Text><Text style={[s.label,p.retrograde?{color:'#ba167b'}:null]}>{p.motion}</Text></View>)}</View>
 <View style={s.panel}><Text style={s.title}>Your {data.selected_sign} daily reflection</Text>{data.forecast.details.map((d:any)=><View key={d.planet} style={s.section}><Text style={s.heading}>{d.planet} · {d.title}</Text><Text style={s.body}>{d.text}</Text></View>)}<Text style={s.body}>{data.forecast.method}</Text><Text style={s.body}>{data.forecast.note}</Text><Button label="Share daily reflection" onPress={()=>Share.share({message:data.forecast.content})}/></View></>:null}</>;
}
const s=StyleSheet.create({panel:{backgroundColor:'#fff0fa',borderColor:'#f7c1e3',borderWidth:2,borderRadius:22,padding:16,marginBottom:14},title:{fontSize:23,fontWeight:'800',color:'#3a156b',marginVertical:12},heading:{fontSize:18,fontWeight:'800',color:'#3a156b',marginBottom:8},label:{fontSize:14,fontWeight:'700',color:'#543066',marginBottom:7},body:{fontSize:15,color:'#3f2c4b',lineHeight:23,marginBottom:12},input:{backgroundColor:'#fff',borderWidth:1,borderColor:'#cfadd4',borderRadius:12,padding:13,color:'#3a156b'},button:{backgroundColor:'#e51a9a',padding:15,borderRadius:24,marginVertical:8,alignItems:'center'},buttonText:{color:'#fff',fontWeight:'800',fontSize:16},choices:{flexDirection:'row',flexWrap:'wrap',gap:7,marginBottom:14},choice:{backgroundColor:'#fff',borderWidth:1,borderColor:'#e9b4dc',borderRadius:19,paddingVertical:9,paddingHorizontal:13},place:{padding:13,borderBottomWidth:1,borderColor:'#e4b7d5'},error:{color:'#a2144a',lineHeight:22,marginVertical:12},row:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',gap:10},flex:{flex:1},section:{paddingVertical:15,borderBottomWidth:1,borderColor:'#e9cee5'}});
