/** Spiritual Vibez • Bare React Native CLI app. No Expo. */
import React,{useEffect,useMemo,useState} from 'react';
import {Image,ImageBackground,ScrollView,Text,View,TouchableOpacity,TextInput,ActivityIndicator,Share,Alert,useWindowDimensions,StyleSheet,StatusBar,Platform} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import {SafeAreaView} from 'react-native-safe-area-context';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {Home,Shuffle,BookOpen,Moon,Star,BookText,ChevronRight,ArrowLeft,ArrowRight,Search,Heart} from 'lucide-react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {API_BASE_URL} from './src/api/spiritualVibezClient';
import {IllustratedCard,UI_CARD_IMAGES} from './src/components/IllustratedCard';

const BACKEND = API_BASE_URL;
const ARTWORK: Record<string, any> = {
  'feature-spreads.png': require('./assets/feature-spreads.png'),
  'feature-learn.png': require('./assets/feature-learn.png'),
  'feature-daily.png': require('./assets/feature-daily.png'),
  'feature-journal.png': require('./assets/feature-journal.png'),
  'hero.png': require('./assets/hero.png'),
  'hero-portrait.png': require('./assets/hero-portrait.png'),
  'scenic-footer.png': require('./assets/scenic-footer.png'),
  'spread-reset.png': require('./assets/spread-reset.png'),
  'spread-gut.png': require('./assets/spread-gut.png'),
  'spread-next.png': require('./assets/spread-next.png'),
  'spread-ground.png': require('./assets/spread-ground.png'),
  'more-cosmos.png': require('./assets/more-cosmos.png'),
  'more-birth.png': require('./assets/more-birth.png'),
  'more-numerology.png': require('./assets/more-numerology.png'),
  'more-moon.png': require('./assets/more-moon.png'),
  'more-ritual.png': require('./assets/more-ritual.png'),
  'more-readings.png': require('./assets/more-readings.png'),
  'hero-mystic-cutout.png': require('./assets/hero-mystic-cutout.png'),
  'hero-skyline-background.png': require('./assets/hero-skyline-background.png'),
  'spread-reset-energy-illustrated.png': require('./assets/spread-reset-energy-illustrated.png'),
  'spread-trust-your-gut-illustrated.png': require('./assets/spread-trust-your-gut-illustrated.png'),
  'spread-next-phase-illustrated.png': require('./assets/spread-next-phase-illustrated.png'),
  'spread-grounding-illustrated.png': require('./assets/spread-grounding-illustrated.png'),
  'footer-skyline-background.png': require('./assets/footer-skyline-background.png'),
  'spread-trust-your-gut-three-card.png': require('./assets/spread-trust-your-gut-three-card.png'),
  'home-hey-mystic-illustrated.png': require('./assets/home-hey-mystic-illustrated.png'),
  'avatar-sunglasses-transparent.png': require('./assets/avatar-sunglasses-transparent.png'),
  'avatar-tarot-headphones-transparent.png': require('./assets/avatar-tarot-headphones-transparent.png'),
};
const image=(name:string)=>ARTWORK[name];
const C={purple:'#6522B4',plum:'#3A156B',pink:'#F71C9F',lilac:'#BE6DEC',peach:'#FFD0AE',cream:'#FFF1FC',aqua:'#84EAE6',ink:'#291345',white:'#FFFFFF'};
const SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const BOTTOM=['Home','Spreads','Learn','Cosmos','Explore','Journal'];
const Tab=createBottomTabNavigator();
const featureImages=[['home_daily_card','Daily'],['home_shuffle_spread','Spreads'],['home_learn_tarot','Learn'],['home_birth_chart','Birth']];
const favourite=[['Trust Your Gut','spreads_trust_gut'],['At a Crossroads','spreads_crossroads'],['The Next Phase','spreads_next_phase'],['Reset Your Energy','spread-reset-energy-illustrated.png'],['Grounding','spread-grounding-illustrated.png']];
const extra=[['Cosmos','more-cosmos.png'],['Birth Chart','more-birth.png'],['Numerology','more-numerology.png'],['Moon Phase','more-moon.png'],['Rituals','more-ritual.png'],['Saved Readings','more-readings.png']];
const exampleSpreads=[
 {id:'reset-energy',title:'Reset Your Energy',category:'wellbeing',cardCount:4,questions:['What drains me?','What can I release?','What can restore me?','One small step forward'].map((q,i)=>({slot:i+1,title:'Position '+(i+1),q}))},
 {id:'trust-gut',title:'Trust Your Gut',category:'crossroads',cardCount:5,questions:['What do I know?','What causes doubt?','What deserves care?','What can I let go?','My next step'].map((q,i)=>({slot:i+1,title:'Position '+(i+1),q}))},
 {id:'crossroads',title:'At a Crossroads',category:'decisions',cardCount:5,questions:['The choice before me','What pulls me one way','What pulls me another','What matters most','My next decision'].map((q,i)=>({slot:i+1,title:'Position '+(i+1),q}))},
 {id:'next-phase',title:'The Next Phase',category:'purpose',cardCount:6,questions:['An ending','A new opportunity','A resource','What I can release','My direction','The first action'].map((q,i)=>({slot:i+1,title:'Position '+(i+1),q}))},
 {id:'grounding',title:'Grounding',category:'wellbeing',cardCount:5,questions:['Body','Mind','Emotion','Support','Next action'].map((q,i)=>({slot:i+1,title:'Position '+(i+1),q}))}
];
const introCards=[{id:0,name:'The Fool',suit:'Major',icon:'🌱',upright:'Beginnings, curiosity, freedom',reversed:'Recklessness or hesitation'},{id:1,name:'The Magician',suit:'Major',icon:'✨',upright:'Resources, confidence, action',reversed:'Scattered energy or doubt'},{id:2,name:'The High Priestess',suit:'Major',icon:'🌙',upright:'Intuition and inner knowing',reversed:'Blocked intuition or secrecy'},{id:17,name:'The Star',suit:'Major',icon:'⭐',upright:'Hope, renewal, inspiration',reversed:'Rebuilding faith in yourself'},{id:19,name:'The Sun',suit:'Major',icon:'☀️',upright:'Joy, clarity and warmth',reversed:'Clouded optimism or rest'}];
const extendedCards=[...introCards,...['The Empress','The Emperor','The Hierophant','The Lovers','The Chariot','Strength','The Hermit','Wheel of Fortune','Justice','The Hanged Man','Death','Temperance','The Devil','The Tower','The Moon','Judgement','The World'].map((name,i)=>({id:40+i,name,suit:'Major',icon:'✨',upright:'Themes of awareness, choices and personal growth',reversed:'Reconsider this theme from another perspective'}))];
const exploreGroups=[
 {title:'Astrology & Charts',items:[['moon','🌒','Natal Moon Phase'],['natal','🪐','Natal Birth Chart'],['draconic','🐉','Draconic Chart'],['bazi','🐲','Chinese Zodiac & BaZi'],['houses','🏡','Astrology Houses'],['asteroids','☄️','Asteroids'],['astro','🌍','Astrocartography'],['calendar','🗓️','13-Moon Calendar']]},
 {title:'Numbers & Love',items:[['life','🔢','Life Path'],['numbers','✨','Numerology Academy'],['love','💖','Love Match']]},
 {title:'Wellness & Rituals',items:[['sound','🎵','Sound Frequencies'],['rituals','🕯️','Ritual Finder'],['cycle','🌸','Moon & Period Tracker'],['shadow','📓','Shadow Work']]},
 {title:'Divination & More',items:[['runes','ᚠ','Rune Casting'],['pendulum','🔮','Pendulum'],['oracle','💬','Mystic Companion'],['store','🛍️','Creator Store']]}
];

async function get(path:string){const r=await fetch(BACKEND+path);if(!r.ok)throw Error('Backend unavailable ('+r.status+')');return r.json()}
async function post(path:string,payload:any){const r=await fetch(BACKEND+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});if(!r.ok)throw Error('Backend unavailable ('+r.status+')');return r.json()}
const crop=(route:string)=>route;
function Header({label='Spiritual Vibez',subtitle='ZODIAC, TAROT & MORE'}:{label?:string,subtitle?:string}){
 return <View style={st.header}><Text style={st.brand}>☾ {label} ✦</Text><Text style={st.tagline}>{subtitle}</Text></View>;
}
function Screen({children}:{children:React.ReactNode}){return <SafeAreaView edges={['top']} style={st.safe}><StatusBar barStyle="light-content" backgroundColor="#4F168F"/><ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={st.page}>{children}</ScrollView></SafeAreaView>}
function Title({eyebrow,title,sub}:{eyebrow:string,title:string,sub?:string}){return <View style={{marginBottom:16}}><Text style={st.kicker}>{eyebrow.toUpperCase()} ✦</Text><Text style={st.title}>{title}</Text>{sub?<Text style={st.subtitle}>{sub}</Text>:null}</View>}
function Action({text,onPress,secondary=false,disabled=false}:{text:string,onPress:()=>void,secondary?:boolean,disabled?:boolean}){return <TouchableOpacity accessibilityRole="button" onPress={onPress} disabled={disabled} style={[st.action,secondary?st.actionSecondary:null,disabled?{opacity:.5}:null]}><Text style={[st.actionLabel,secondary?{color:C.plum}:null]}>{text}</Text><ArrowRight size={16} color={secondary?C.plum:'#fff'}/></TouchableOpacity>}
function Info({children,warning=false}:{children:React.ReactNode,warning?:boolean}){return <View style={[st.info,warning?{backgroundColor:'#FFF0D3'}:null]}><Text style={st.infoText}>{children}</Text></View>}
function Panel({children}:{children:React.ReactNode}){return <View style={st.panel}>{children}</View>}
function Input({title,value,onChange,placeholder='',keyboardType='default'}:{title:string,value:string,onChange:(s:string)=>void,placeholder?:string,keyboardType?:any}){return <View style={{marginBottom:13}}><Text style={st.formLabel}>{title}</Text><TextInput style={st.input} value={value} onChangeText={onChange} placeholder={placeholder} placeholderTextColor="#9682A1" keyboardType={keyboardType}/></View>}
function OptionRow({choices,value,onSelect}:{choices:string[],value:string,onSelect:(v:string)=>void}){return <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,paddingVertical:8}}>{choices.map(x=><TouchableOpacity key={x} onPress={()=>onSelect(x)} style={[st.chip,x===value?st.chipActive:null]}><Text style={[st.chipText,x===value?{color:'#fff'}:null]}>{x}</Text></TouchableOpacity>)}</ScrollView>}
function ArtTile({name,label,width,onPress}:{name:string,label:string,width:number,onPress:()=>void}){return <IllustratedCard asset={name as keyof typeof UI_CARD_IMAGES} width={width} label={label} onPress={onPress}/>}
function ArtSpread({name,label,width,onPress}:{name:string,label:string,width:number,onPress:()=>void}){return name.startsWith("spreads_")?<IllustratedCard asset={name as keyof typeof UI_CARD_IMAGES} width={width} label={label} onPress={onPress}/>:<TouchableOpacity accessibilityRole="button" accessibilityLabel={label} onPress={onPress} style={{width,marginBottom:11}}><Image style={{width,height:width*.79,borderRadius:19}} source={image(name)} resizeMode="stretch" /></TouchableOpacity>}

/** The painted filter artwork stays interactive: each visible chip has its own touch target. */
function PaintedVibeFilter({value,onChange}:{value:string,onChange:(s:string)=>void}){
 const {width}=useWindowDimensions();const w=Math.min(width-32,580);
 const a=Image.resolveAssetSource(UI_CARD_IMAGES.spreads_filters);const h=w*a.height/a.width;
 return <View style={{width:w,height:h,marginBottom:13}}>
   <Image source={UI_CARD_IMAGES.spreads_filters} style={{width:w,height:h}} resizeMode="stretch"/>
   <View style={{position:'absolute',left:w*.015,right:w*.015,bottom:h*.08,height:h*.42,flexDirection:'row'}}>
    {['All','Love','Career','Growth'].map((x)=><TouchableOpacity key={x} accessibilityRole="button" accessibilityLabel={'Filter by '+x} onPress={()=>onChange(x)} style={{flex:1,borderRadius:22,borderWidth:value===x?2:0,borderColor:'#F526A3'}} />)}
   </View>
 </View>;
}

function HomeScreen({navigation}:any){const {width}=useWindowDimensions();const contentW=Math.min(width-32,580);const tileW=(contentW-12)/2;
 return <Screen><Header/><ImageBackground source={image('hero-skyline-background.png')} style={st.homeHero} imageStyle={{borderRadius:24}} resizeMode="cover">
   <LinearGradient colors={['rgba(64,14,123,0.92)','rgba(71,17,123,0.53)','rgba(61,17,118,0.10)']} style={st.heroTint} pointerEvents="none"/>
   <Image source={image('hero-mystic-cutout.png')} style={st.heroArt} resizeMode="contain"/>
   <View style={st.heroContent}>
     <Text style={st.heroTitle}>Zero boring.</Text>
     <Text style={st.heroSub}>Explore cards, learn tarot, and discover something about yourself—your way.</Text>
     <View style={st.heroActions}><Action text="Try a spread ✨" onPress={()=>navigation.navigate('Spreads')}/><Action text="Learn tarot" secondary onPress={()=>navigation.navigate('Learn')}/></View>
   </View>
  </ImageBackground>
 <Text style={st.section}>Pick your adventure 💫</Text><View style={st.twoCols}>{featureImages.map(([file,target])=><ArtTile key={file} name={file} label={target} width={tileW} onPress={()=>target==='Daily'?navigation.navigate('Learn',{daily:true}):target==='Birth'?navigation.navigate('Explore',{tool:'natal'}):navigation.navigate(target)}/>)}</View>
 <View style={st.sectionRow}><Text style={st.section}>Fan-favorite spreads ♡</Text><TouchableOpacity onPress={()=>navigation.navigate('Spreads')}><Text style={{color:'#fff',fontWeight:'900'}}>See all →</Text></TouchableOpacity></View>
 <View style={st.twoCols}>{favourite.map(([label,file])=><ArtSpread key={file} name={file} label={label} width={tileW} onPress={()=>navigation.navigate('Spreads',{favorite:label})}/>)}</View>
 <Text style={st.section}>More to explore ✨</Text><View style={st.moreGrid}>{extra.map(([label,file])=><TouchableOpacity key={file} accessibilityLabel={label} accessibilityRole="button" style={{width:(contentW-16)/3,marginBottom:8}} onPress={()=>label==='Saved Readings'?navigation.navigate('Journal'):label==='Cosmos'?navigation.navigate('Cosmos'):navigation.navigate('Explore',{tool:label==='Birth Chart'?'natal':label==='Numerology'?'life':label==='Moon Phase'?'moon':'rituals'})}><Image source={image(file)} style={{width:'100%',height:64,borderRadius:12}} resizeMode="stretch"/></TouchableOpacity>)}</View>
 <Image source={image('footer-skyline-background.png')} style={st.homeFooter} resizeMode="cover" accessibilityLabel="Illustrated skyline and crystals"/>
 </Screen>
}
function SpreadsScreen({route}:any){const [items,setItems]=useState<any[]>(exampleSpreads);const [selected,setSelected]=useState<any>(null);const [cards,setCards]=useState<Record<number,any>>({});const [reading,setReading]=useState('');const [error,setError]=useState('');const [busy,setBusy]=useState(false);const [search,setSearch]=useState('');const [vibe,setVibe]=useState('All');const [connected,setConnected]=useState(false);
 useEffect(()=>{get('/tarot/spreads').then(x=>{setItems(x.spreads||[]);setConnected(true)}).catch(()=>{})},[]);
 useEffect(()=>{const f=route.params?.favorite;if(f&&items.length){const found=items.find(x=>x.title?.toLowerCase()===f.toLowerCase());if(found){setSelected(found);setCards({});setReading('')}}},[route.params?.favorite,items]);
 const start=(s:any)=>{setSelected(s);setCards({});setReading('');setError('')};
 const randomize=()=>{if(items.length)start(items[Math.floor(Math.random()*items.length)])};
 const shown=items.filter(x=>x.title.toLowerCase().includes(search.toLowerCase())&&(vibe==='All'||(x.category+' '+x.title).toLowerCase().includes(vibe.toLowerCase())));
 const draw=async(slot:number)=>{if(!selected||busy||cards[slot])return;setBusy(true);setError('');try{const x=await post('/tarot/spreads/deal-slot',{spread_id:selected.id,slot_num:slot,exclude_card_ids:Object.values(cards).map((d:any)=>d.card.id)});setCards(old=>({...old,[slot]:x}))}catch{const existing=Object.values(cards).map((x:any)=>x.card.id);const pool=extendedCards.filter(x=>!existing.includes(x.id));const card=pool[Math.floor(Math.random()*pool.length)];setCards(old=>({...old,[slot]:{slot,card:{...card,orientation:'Upright',meaning:card.upright}}}))}finally{setBusy(false)}};
 const saveReading=async()=>{if(!selected||!reading)return;try{const current=await AsyncStorage.getItem('sv_readings');const old=current?JSON.parse(current):[];const next=[{date:new Date().toLocaleDateString(),title:selected.title,text:reading},...old].slice(0,100);await AsyncStorage.setItem('sv_readings',JSON.stringify(next));Alert.alert('Saved','Reading saved on this device.')}catch{Alert.alert('Save failed','Could not save this reading.')}};
 const interpret=async()=>{if(!selected)return;setBusy(true);try{const r=await post('/tarot/spreads/synthesize',{spread_id:selected.id,drawn_cards:Object.values(cards).map((v:any)=>({slot:v.slot,card_id:v.card.id,orientation:v.card.orientation})),save_to_journal:false});setReading(r.synthesis)}catch{setReading('Your '+selected.title+' cards invite a reflection on '+Object.values(cards).map((d:any)=>d.card.name).join(', ')+'. Consider each question in the spread, notice patterns, and choose one practical next step. This is a reflective prompt, not a prediction.')}finally{setBusy(false)}};
 return <Screen><IllustratedCard asset="spreads_header" label="Spreads screen header"/>{selected?<>
 <TouchableOpacity style={{marginBottom:15}} onPress={()=>setSelected(null)}><Text style={st.back}>← Browse all spreads</Text></TouchableOpacity><Title eyebrow="The spread studio" title={selected.title} sub="Tap each numbered position to reveal its card."/>
 <LinearGradient colors={['#5422AA','#B72EC3','#FC7CAC']} style={st.readingBoard}><Text style={st.readingLabel}>✦ YOUR READING ✦</Text><View style={st.slotWrap}>{(selected.questions||[]).map((q:any)=><TouchableOpacity key={q.slot} onPress={()=>draw(q.slot)} disabled={!!cards[q.slot]||busy} style={[st.slot,cards[q.slot]?st.slotOpen:null]}><Text style={st.slotIcon}>{cards[q.slot]?cards[q.slot].card.icon||'🃏':'☀️'}</Text><Text style={[st.slotText,cards[q.slot]?{color:C.plum}:null]}>{cards[q.slot]?cards[q.slot].card.name:'CARD '+q.slot}</Text><Text style={st.slotHint}>{cards[q.slot]?cards[q.slot].card.orientation:'TAP TO REVEAL'}</Text></TouchableOpacity>)}</View></LinearGradient>
 {(selected.questions||[]).map((q:any)=><Panel key={q.slot}><Text style={st.panelTitle}>{q.slot}. {q.title||'Position '+q.slot}</Text><Text style={st.body}>{q.q}</Text>{cards[q.slot]?<Text style={st.meaning}>{cards[q.slot].card.name}: {cards[q.slot].card.meaning}</Text>:null}</Panel>)}
 {error?<Info warning>{error}</Info>:null}<Action text={busy?'Working…':'Interpret my reading ✨'} onPress={interpret} disabled={busy||Object.keys(cards).length!==(selected.questions||[]).length}/>
 {reading?<Panel><Text style={st.panelTitle}>💖 Your overall reading</Text><Text style={st.body}>{reading}</Text><Action text="Share reading" onPress={()=>Share.share({message:selected.title+'\n\n'+reading})}/><Action text="Save reading" secondary onPress={saveReading}/></Panel>:null}<Action text="Shuffle again" secondary onPress={()=>start(selected)}/>
 </>:<>
 <IllustratedCard asset="spreads_randomize" label="Randomize a Spread" onPress={randomize}/>
 <PaintedVibeFilter value={vibe} onChange={setVibe}/>
 <Title eyebrow="Your illustrated spread collection" title="Pick your spread ✨" sub="Each layout opens a real interactive card reading."/>
 {([["Trust Your Gut","spreads_trust_gut"],["At a Crossroads","spreads_crossroads"],["The Next Phase","spreads_next_phase"]] as const).map(([title,art])=>{
  const match=items.find(x=>x.title.toLowerCase()===title.toLowerCase());
  return <IllustratedCard key={art} asset={art} label={title} onPress={match?()=>start(match):undefined}/>;
 })}
 <Input title="Find your vibe" value={search} onChange={setSearch} placeholder="Search tarot spreads"/>
 {!connected?<Info>Showing sample spread layouts. Connect your existing backend to load all 48.</Info>:null}
 {shown.map((s,i)=><TouchableOpacity key={s.id} style={st.spreadRow} onPress={()=>start(s)}><LinearGradient colors={['#FF8FD1','#AA6BF0']} style={st.spreadIcon}><Text style={{fontSize:31}}>{['🔮','💗','🦋','🌙'][i%4]}</Text></LinearGradient><View style={{flex:1}}><Text style={st.spreadTitle}>{s.title}</Text><Text style={st.muted}>{s.cardCount} cards · {s.category}</Text></View><ChevronRight size={21} color={C.pink}/></TouchableOpacity>)}
 </>}</Screen>
}
function LearnScreen({route}:any){const [all,setAll]=useState<any[]>(extendedCards);const [selected,setSelected]=useState<any>(null);const [mode,setMode]=useState('home');const [quiz,setQuiz]=useState<any>(null);const [answer,setAnswer]=useState('');const [search,setSearch]=useState('');const [progress,setProgress]=useState(0);const [online,setOnline]=useState(false);
 useEffect(()=>{get('/tarot/cards').then(x=>{setAll(x.cards||[]);setOnline(true)}).catch(()=>{})},[]);
 useEffect(()=>{if(route.params?.daily){setSelected(all[Math.floor(Math.random()*all.length)]);setMode('detail')}},[route.params?.daily]);
 const ask=async()=>{try{setQuiz(await get('/tarot/study/quiz'))}catch{const c=all[Math.floor(Math.random()*all.length)];const correct=c.upright.split(',')[0];setQuiz({card_name:c.name,prompt:'What idea does this card represent?',options:[correct,'Restlessness','Confusion','Isolation'],correct_answer:correct})}setMode('quiz');setAnswer('')};
 const choose=(opt:string)=>{setAnswer(opt===quiz.correct_answer?'Correct! ✨':'The answer is '+quiz.correct_answer);setProgress(x=>x+1)};
 return <Screen><IllustratedCard asset="learn_header" label="Learn Tarot academy header"/>
 <IllustratedCard asset="learn_progress" label="Your Learning Journey illustrated progress card"/><Text style={[st.muted,{color:"#FFF0FC",marginBottom:11}]}>Live progress: {progress} quiz answers this session (the percentage in the artwork is illustrative).</Text>
 {mode==='home'?<>{([['Major Arcana','learn_major_arcana'],['Minor Arcana','learn_minor_arcana'],['Card Meanings','learn_card_meanings'],['Reversed Cards','learn_reversed_cards'],['Quiz Me','learn_quiz_me']] as const).map(([name,asset])=><IllustratedCard key={name} asset={asset} label={name} onPress={()=>name==='Quiz Me'?ask():setMode(name)}/>)}</>:<>
 <TouchableOpacity onPress={()=>{setMode('home');setSelected(null)}}><Text style={st.back}>← Learning modules</Text></TouchableOpacity>
 {mode==='quiz'&&quiz?<Panel><Text style={st.panelTitle}>🎯 {quiz.card_name}</Text><Text style={st.body}>{quiz.prompt}</Text>{quiz.options.map((o:string)=><TouchableOpacity key={o} style={st.quizOption} onPress={()=>choose(o)}><Text style={{fontWeight:'900',color:C.plum}}>{o}</Text></TouchableOpacity>)}{answer?<Text style={st.meaning}>{answer}</Text>:null}<Action text="Next question" onPress={ask}/></Panel>:<>
 <Input title="Find a tarot card" value={search} onChange={setSearch} placeholder="Search the tarot deck"/>
 {!online?<Info>Showing a few sample cards. Your backend contains the full 78-card encyclopedia.</Info>:null}
 {selected?<Panel><Text style={st.panelTitle}>{selected.icon} {selected.name}</Text><Text style={st.body}>Upright: {selected.description_upright||selected.upright}</Text><Text style={st.body}>Reversed: {selected.description_reversed||selected.reversed}</Text><Action text="Back to cards" secondary onPress={()=>setSelected(null)}/></Panel>:null}
 {all.filter(c=>((mode==='Major Arcana'&&c.suit==='Major')||(mode==='Minor Arcana'&&c.suit!=='Major')||(!['Major Arcana','Minor Arcana'].includes(mode)))&&c.name.toLowerCase().includes(search.toLowerCase())).map(c=><TouchableOpacity key={c.id} style={st.lessonRow} onPress={()=>setSelected(c)}><Text style={{fontSize:28}}>{c.icon||'🃏'}</Text><View style={{flex:1}}><Text style={st.lessonTitle}>{c.name}</Text><Text style={st.muted}>{c.suit}</Text></View><ChevronRight color={C.pink}/></TouchableOpacity>)}
 </>}</>}
 </Screen>
}
function CosmosScreen(){const [sign,setSign]=useState('Scorpio');const [data,setData]=useState<any>(null);const [loading,setLoading]=useState(false);const [error,setError]=useState('');
 const reload=async(s=sign)=>{setLoading(true);setError('');try{setData(await get('/astrology/daily-transits?sign='+encodeURIComponent(s)))}catch{setData(null);setError('Connect your backend for current planetary positions. I will not display invented transits.')}finally{setLoading(false)}};
 useEffect(()=>{reload('Scorpio')},[]);
 return <Screen><Header label="Cosmos" subtitle="YOUR DAILY COSMIC CHECK-IN"/><Title eyebrow="Astrology & transits" title="Your Cosmic Weather 🌙" sub="See the current Sun, Moon, Mercury and Venus and your sign-based forecast."/>
 <LinearGradient colors={['#4B22B4','#9F42D5','#FF7EB6']} style={st.cosmosBanner}><Text style={{fontSize:53,textAlign:'center'}}>🌙 ✨</Text><Text style={st.cosmosBig}>{data?.moon_phase||'Your Moon & Planetary Weather'}</Text><Text style={{color:'white',textAlign:'center'}}>{data?.illumination_percent!=null?'Moon illumination '+data.illumination_percent+'%':'Refresh when connected'}</Text></LinearGradient>
 <Text style={st.section}>Choose your sign</Text><OptionRow choices={SIGNS} value={sign} onSelect={s=>{setSign(s);reload(s)}}/>
 {loading?<ActivityIndicator color={C.pink} size="large"/>:null}{error?<Info warning>{error}</Info>:null}
 {data?<><View style={st.twoCols}>{[['☀️','Sun',data.sun_position],['☿','Mercury',data.mercury_status],['♀','Venus',data.venus_status],['🌘','Moon',data.moon_phase]].map(([ico,name,text])=><View key={name} style={st.planet}><Text style={{fontSize:27}}>{ico}</Text><Text style={st.panelTitle}>{name}</Text><Text style={st.body}>{text}</Text></View>)}</View><Panel><Text style={st.panelTitle}>💖 Your {sign} Vibe</Text><Text style={st.body}>{data.forecast?.content}</Text><Info>Astrology is symbolic and does not scientifically predict your mood.</Info><Action text="Share my forecast" onPress={()=>Share.share({message:sign+' forecast: '+data.forecast?.content})}/></Panel></>:null}
 </Screen>
}
const toolMap=Object.fromEntries(exploreGroups.flatMap(g=>g.items.map((item:any)=>[item[0],item])));
function ExploreScreen({route}:any){const [tool,setTool]=useState<string|null>(null);const [date,setDate]=useState('');const [time,setTime]=useState('12:00');const [lat,setLat]=useState('43.1009');const [lon,setLon]=useState('-75.2327');const [city,setCity]=useState('Utica, NY');const [query,setQuery]=useState('');const [signA,setSignA]=useState('Scorpio');const [signB,setSignB]=useState('Taurus');const [period,setPeriod]=useState('');const [cycleLength,setCycleLength]=useState('28');const [result,setResult]=useState<any>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);
 useEffect(()=>{if(route.params?.tool)setTool(route.params.tool)},[route.params?.tool]);
 const go=(id:string)=>{setTool(id);setError('');setResult(null)};
 const run=async()=>{if(!tool)return;setBusy(true);setError('');setResult(null);const [yy,mm,dd]=date.split('-').map(Number);
  if(tool==='cycle'){if(!period){setError('Enter the start of your last period.');setBusy(false);return}const days=Math.floor((Date.now()-new Date(period+'T12:00:00').getTime())/86400000),length=Number(cycleLength),n=new Date(period+'T12:00:00');n.setDate(n.getDate()+(Math.floor(Math.max(0,days)/length)+1)*length);setResult({Estimated_cycle_day:Math.max(0,days)%length+1,Estimated_next_period:n.toDateString(),Note:'Not fertility or contraceptive advice.'});setBusy(false);return}
  const routes:Record<string,()=>Promise<any>>={moon:()=>post('/astrology/moon-phase',{birth_date:date,birth_time:time}),natal:()=>post('/astrology/natal-chart',{birth_date:date,birth_time:time,latitude:Number(lat),longitude:Number(lon),chart_system:'placidus'}),draconic:()=>post('/astrology/natal-chart',{birth_date:date,birth_time:time,latitude:Number(lat),longitude:Number(lon),chart_system:'draconic'}),bazi:()=>post('/astrology/bazi',{birth_year:yy,birth_month:mm,birth_day:dd,birth_hour:Number(time.slice(0,2))}),houses:()=>get('/astrology/houses'),asteroids:()=>get('/astrology/asteroids'),astro:()=>get('/astrology/astrocartography?city='+encodeURIComponent(city)),calendar:()=>get('/astrology/lunar-calendar/1'),life:()=>post('/synastry/life-path',{birth_year:yy,birth_month:mm,birth_day:dd}),numbers:()=>get('/synastry/numerology-lessons'),love:()=>post('/synastry/compatibility',{partner_a_sign:signA,partner_b_sign:signB}),sound:()=>get('/rituals/frequencies'),rituals:()=>get('/rituals/search?query='+encodeURIComponent(query)),shadow:()=>get('/wellness/shadow-prompts'),runes:()=>post('/divination/runes/cast',{rune_count:3}),pendulum:()=>post('/divination/pendulum',{question:query||'What matters most today?'}),oracle:()=>post('/oracle/chat',{message:query||'What should I reflect on?'}),store:()=>get('/store/products')};
  try{setResult(await routes[tool]())}catch{setError('This tool needs the connected backend. Your local app interface is ready, but no fabricated result will be shown.')}finally{setBusy(false)}
 };
 return <Screen><Header label="Explore" subtitle="YOUR COSMIC PLAYGROUND"/>{!tool?<><Title eyebrow="All your features" title="Explore More ✨" sub="Tap a feature to open its own screen."/>{exploreGroups.map(g=><View key={g.title}><Text style={st.section}>{g.title}</Text><View style={st.twoCols}>{g.items.map(([id,ico,title])=><TouchableOpacity key={id} style={st.toolTile} onPress={()=>go(id)}><Text style={{fontSize:33}}>{ico}</Text><Text style={st.toolName}>{title}</Text><ChevronRight color={C.pink} size={20}/></TouchableOpacity>)}</View></View>)}</>:<>
 <TouchableOpacity onPress={()=>go('')}><Text style={st.back}>← All features</Text></TouchableOpacity><Title eyebrow="Your personal tools" title={(toolMap[tool]?.[1]||'✨')+' '+(toolMap[tool]?.[2]||tool)} sub="Powered by Spiritual Vibez."/>
 {['natal','draconic','moon','bazi','life'].includes(tool)?<><Input title="Birth date YYYY-MM-DD" value={date} onChange={setDate} placeholder="1996-11-05"/>{tool!=='life'?<Input title="Birth time HH:MM" value={time} onChange={setTime}/>:null}</>:null}
 {['natal','draconic'].includes(tool)?<><Input title="Birth latitude" value={lat} onChange={setLat}/><Input title="Birth longitude" value={lon} onChange={setLon}/><Info warning>Astrology chart calculations in the current backend are approximate and do not convert birth time zones properly. Verify before release.</Info></>:null}
 {tool==='astro'?<Input title="Destination city" value={city} onChange={setCity}/>:null}
 {tool==='love'?<><Text style={st.formLabel}>Your sign</Text><OptionRow choices={SIGNS} value={signA} onSelect={setSignA}/><Text style={st.formLabel}>Their sign</Text><OptionRow choices={SIGNS} value={signB} onSelect={setSignB}/></>:null}
 {['rituals','pendulum','oracle'].includes(tool)?<Input title="Your intention or question" value={query} onChange={setQuery} placeholder="Type your question..."/>:null}
 {tool==='cycle'?<><Input title="Last period start YYYY-MM-DD" value={period} onChange={setPeriod}/><Input title="Average cycle length" value={cycleLength} onChange={setCycleLength} keyboardType="numeric"/><Info warning>Period estimates stay in this app session. Do not use this tracker to predict fertile days, and do not rely on it for contraception.</Info></>:null}
 {tool==='sound'?<Info>Frequency education is connected to your existing API. Native audio playback still needs licensed or original audio files wired to Expo AV.</Info>:null}
 <Action text={busy?'Working…':'✨ Explore this feature'} onPress={run} disabled={busy}/>{error?<Info warning>{error}</Info>:null}
 {result?<Panel><Text style={st.panelTitle}>Your {toolMap[tool]?.[2]} result</Text><Text selectable style={st.body}>{JSON.stringify(result,null,2)}</Text><Action text="Share result" onPress={()=>Share.share({message:JSON.stringify(result,null,2)})}/></Panel>:null}
 </>}</Screen>
}
function JournalScreen({navigation}:any){
 const {width}=useWindowDimensions();const colWidth=(Math.min(width-32,580)-12)/2;
 const [notes,setNotes]=useState<any[]>([]);const [readings,setReadings]=useState<any[]>([]);const [moods,setMoods]=useState<any[]>([]);
 const [draft,setDraft]=useState('');const [saved,setSaved]=useState('');const [view,setView]=useState('home');
 useEffect(()=>{AsyncStorage.multiGet(['sv_journal','sv_readings','sv_moods']).then(data=>{
   const parse=(value:string|null)=>{try{return value?JSON.parse(value):[]}catch{return []}};
   setNotes(parse(data[0][1]));setReadings(parse(data[1][1]));setMoods(parse(data[2][1]));
 }).catch(()=>{})},[]);
 const save=async()=>{const msg=draft.trim();if(!msg)return;const next=[{date:new Date().toLocaleDateString(),text:msg},...notes].slice(0,100);
  try{await AsyncStorage.setItem('sv_journal',JSON.stringify(next));setNotes(next);setDraft('');setSaved('Saved on this device.')}catch{setSaved('Could not save on this device.')};
 };
 const openSaved=async()=>{try{const value=await AsyncStorage.getItem('sv_readings');setReadings(value?JSON.parse(value):[])}catch{}setView('saved')};
 const saveMood=async(value:string)=>{const next=[{date:new Date().toLocaleDateString(),mood:value},...moods].slice(0,100);
  try{await AsyncStorage.setItem('sv_moods',JSON.stringify(next));setMoods(next);setSaved('Mood saved on this device.')}catch{setSaved('Could not save your mood.')};
 };
 return <Screen>
  <IllustratedCard asset="journal_header" label="My Journal screen header"/>
  <IllustratedCard asset="journal_today" label="Open today's journal" onPress={()=>setView('entry')}/>
  {view==='entry'?<Panel>
    <Text style={st.panelTitle}>Today's Journal ♡</Text>
    <TextInput multiline value={draft} onChangeText={setDraft} placeholder="What's on your mind today?" placeholderTextColor="#9781A0" style={[st.input,{minHeight:130,textAlignVertical:'top'}]}/>
    <Action text="Save reflection ✎" onPress={save}/>{saved?<Text style={st.meaning}>{saved}</Text>:null}
  </Panel>:null}
  <View style={st.twoCols}>
   <IllustratedCard asset="journal_saved_readings" width={colWidth} label="Saved Readings" onPress={openSaved}/>
   <IllustratedCard asset="journal_mood_checkin" width={colWidth} label="Mood Check-In" onPress={()=>setView('mood')}/>
   <IllustratedCard asset="journal_moon_phase" width={colWidth} label="Moon Phase" onPress={()=>navigation.navigate('Cosmos')}/>
   <IllustratedCard asset="journal_numerology" width={colWidth} label="Numerology" onPress={()=>navigation.navigate('Explore',{tool:'life'})}/>
  </View>
  <IllustratedCard asset="journal_rituals" label="Ritual Finder" onPress={()=>navigation.navigate('Explore',{tool:'rituals'})}/>
  {view==='saved'?<Panel>
   <Text style={st.panelTitle}>🃏 Saved readings</Text>
   {readings.length?readings.map((r:any,i:number)=><View key={i} style={{marginVertical:7}}><Text style={st.spreadTitle}>{r.title}</Text><Text style={st.muted}>{r.date}</Text><Text style={st.body}>{r.text}</Text></View>):<Text style={st.body}>No saved readings yet. Open a spread and save your first reading.</Text>}
  </Panel>:null}
  {view==='mood'?<Panel>
   <Text style={st.panelTitle}>💖 How are you feeling?</Text>
   <View style={{flexDirection:'row',justifyContent:'space-between',marginVertical:10}}>
    {['😊','🥰','😐','😔','😴'].map(m=><TouchableOpacity key={m} accessibilityRole="button" accessibilityLabel={'Log mood '+m} onPress={()=>saveMood(m)}><Text style={{fontSize:35}}>{m}</Text></TouchableOpacity>)}
   </View>
   {moods[0]?<Text style={st.body}>Most recent check-in: {moods[0].mood} · {moods[0].date}</Text>:null}
   {saved?<Text style={st.meaning}>{saved}</Text>:null}
  </Panel>:null}
  <Text style={st.section}>Your private reflections</Text>
  {notes.length?notes.slice(0,3).map((x:any,i:number)=><Panel key={i}><Text style={st.muted}>{x.date}</Text><Text style={st.body}>{x.text}</Text></Panel>):<Info>Tap Today's Journal to start writing.</Info>}
  <Info warning>Journal notes, saved readings and mood check-ins are stored locally on this device. Avoid storing sensitive information on shared devices.</Info>
 </Screen>;
}
const ICONS:Record<string,any>={Home,Spreads:Shuffle,Learn:BookOpen,Cosmos:Moon,Explore:Star,Journal:BookText};
export default function App(){return <NavigationContainer><Tab.Navigator id="main-tabs" screenOptions={({route}:any)=>({headerShown:false,tabBarActiveTintColor:C.pink,tabBarInactiveTintColor:'#9E829B',tabBarStyle:{height:76,paddingTop:8,paddingBottom:8,backgroundColor:'#FFF2FC',borderTopColor:'#FBC5EC'},tabBarLabelStyle:{fontSize:10,fontWeight:'900'},tabBarIcon:({color,size}:any)=>{const Icon=ICONS[route.name]||Star;return <Icon color={color} size={size} strokeWidth={2.4}/>}})}><Tab.Screen name="Home" component={HomeScreen}/><Tab.Screen name="Spreads" component={SpreadsScreen}/><Tab.Screen name="Learn" component={LearnScreen}/><Tab.Screen name="Cosmos" component={CosmosScreen}/><Tab.Screen name="Explore" component={ExploreScreen}/><Tab.Screen name="Journal" component={JournalScreen}/></Tab.Navigator></NavigationContainer>}
const st=StyleSheet.create({
 safe:{flex:1,backgroundColor:'#7427BD'},page:{paddingHorizontal:16,paddingBottom:28,maxWidth:600,width:'100%',alignSelf:'center'},header:{paddingTop:8,paddingBottom:13,alignItems:'center'},brand:{fontSize:29,fontWeight:'900',color:'#fff',textShadowColor:'#EF2A9B',textShadowRadius:10},tagline:{fontSize:10,letterSpacing:2,color:'#FFE5AA',fontWeight:'900'},
 homeHero:{borderRadius:24,minHeight:465,overflow:'hidden',padding:18,borderWidth:2,borderColor:'#FFD7EF'},heroTitle:{fontSize:41,color:'#fff',fontWeight:'900',fontStyle:'italic',textShadowColor:'#EE188C',textShadowRadius:12},heroSub:{fontSize:14,fontWeight:'800',color:'#fff',lineHeight:21,marginTop:10,maxWidth:285},heroActions:{flexDirection:'row',gap:7,marginTop:12,zIndex:3},heroArt:{position:'absolute',bottom:-5,right:-14,width:'78%',height:314},heroTint:{...StyleSheet.absoluteFillObject,borderRadius:24},heroContent:{zIndex:2,width:'100%',alignSelf:'flex-start'},homeFooter:{width:'100%',height:102,borderRadius:18,marginTop:20,overflow:'hidden'},avatarStrip:{height:138,backgroundColor:'#F8B0DA',borderRadius:22,borderWidth:2,borderColor:'#FFDFEF',overflow:'hidden',flexDirection:'row',alignItems:'center',marginBottom:15},stripAvatar:{width:141,height:137,alignSelf:'flex-end'},stripText:{flex:1,marginRight:8,justifyContent:'center'},stripHeading:{color:'#4B156A',fontSize:17,fontWeight:'900',marginBottom:6},stripCopy:{color:'#65316D',fontSize:12,lineHeight:17,fontWeight:'700'},spreadPromo:{width:'100%',height:188,borderRadius:18,marginBottom:14},journalIntro:{width:'100%',height:280,borderRadius:22,marginBottom:14},action:{backgroundColor:C.pink,borderWidth:2,borderColor:'#FFE3FA',borderRadius:28,paddingVertical:11,paddingHorizontal:13,flexDirection:'row',gap:8,alignItems:'center',justifyContent:'center',alignSelf:'flex-start',marginTop:10,marginBottom:8},actionSecondary:{backgroundColor:'#FFF3FD'},actionLabel:{color:'#fff',fontSize:13,fontWeight:'900'},
 section:{color:'#fff',fontSize:23,fontWeight:'900',marginTop:20,marginBottom:12,textShadowColor:'#EA37A6',textShadowRadius:8},sectionRow:{flexDirection:'row',justifyContent:'space-between',alignItems:'center'},twoCols:{flexDirection:'row',flexWrap:'wrap',gap:12,justifyContent:'space-between'},moreGrid:{flexDirection:'row',flexWrap:'wrap',gap:8,justifyContent:'space-between'},
 kicker:{fontSize:11,color:'#FFE8A2',fontWeight:'900',letterSpacing:1.7,marginBottom:6},title:{fontSize:31,fontWeight:'900',color:'#fff',marginBottom:6,textShadowColor:C.pink,textShadowRadius:8},subtitle:{color:'#FFE6FA',fontSize:14,lineHeight:21},panel:{backgroundColor:'#FFF5FC',borderRadius:20,borderWidth:2,borderColor:'#FFE1F7',padding:17,marginBottom:14},panelTitle:{fontSize:19,fontWeight:'900',color:C.ink,marginBottom:7},body:{fontSize:13.5,lineHeight:20,color:'#664879',marginBottom:7},muted:{color:'#8D698B',fontSize:11.5,lineHeight:16},meaning:{fontSize:13.5,color:'#7B249B',marginTop:9,fontWeight:'700',lineHeight:20},
 info:{backgroundColor:'#FFE5F5',padding:13,borderRadius:16,marginVertical:10},infoText:{fontSize:12.5,color:'#66346A',lineHeight:18},formLabel:{fontSize:12,color:'#FFE2B6',fontWeight:'900',marginBottom:5},input:{backgroundColor:'#FFF8FC',borderWidth:2,borderColor:'#FFCDF1',borderRadius:14,paddingHorizontal:12,paddingVertical:10,fontSize:14,color:C.ink,minHeight:47},
 chip:{paddingHorizontal:13,paddingVertical:9,borderRadius:27,backgroundColor:'#FFE7F8',borderWidth:1,borderColor:'#FFC9E9'},chipActive:{backgroundColor:C.pink,borderColor:'#fff'},chipText:{fontSize:12,color:C.plum,fontWeight:'900'},back:{color:'#FFE6FA',fontWeight:'900',marginVertical:12,fontSize:15},
 spreadRow:{flexDirection:'row',alignItems:'center',gap:12,backgroundColor:'#FFF5FC',padding:11,marginBottom:12,borderRadius:18},spreadIcon:{width:73,height:73,borderRadius:15,alignItems:'center',justifyContent:'center'},spreadTitle:{fontSize:17,color:C.ink,fontWeight:'900',marginBottom:4},
 readingBoard:{borderRadius:24,padding:17,borderWidth:2,borderColor:'#FFE4FA',marginBottom:14},readingLabel:{color:'#fff',fontSize:18,fontWeight:'900',textAlign:'center',marginBottom:15},slotWrap:{flexDirection:'row',flexWrap:'wrap',justifyContent:'center',gap:10},slot:{width:91,minHeight:139,borderRadius:14,backgroundColor:'#5925A5',borderWidth:3,borderColor:'#FFE7A8',padding:7,justifyContent:'center',alignItems:'center'},slotOpen:{backgroundColor:'#FFF0FB',borderColor:'#fff'},slotIcon:{fontSize:28,marginBottom:7},slotText:{fontSize:11,fontWeight:'900',color:'#fff',textAlign:'center'},slotHint:{fontSize:9,fontWeight:'700',color:'#F4C8E5',marginTop:6,textAlign:'center'},
 lessonRow:{flexDirection:'row',alignItems:'center',gap:13,backgroundColor:'#FFF2FC',borderRadius:18,borderWidth:2,borderColor:'#FFE1F8',padding:12,marginBottom:11},lessonTitle:{color:C.ink,fontSize:17,fontWeight:'900'},progressTrack:{height:11,borderRadius:7,backgroundColor:'#EBD6E4',overflow:'hidden',marginVertical:9},progressFill:{backgroundColor:C.pink,height:11,borderRadius:7},quizOption:{padding:12,backgroundColor:'#FDE1F1',borderRadius:12,marginVertical:5},
 cosmosBanner:{borderRadius:25,padding:20,minHeight:195,justifyContent:'center',marginBottom:14},cosmosBig:{color:'#fff',fontSize:22,fontWeight:'900',textAlign:'center',marginVertical:13},planet:{backgroundColor:'#FFF4FD',borderRadius:18,padding:14,marginBottom:12,flexBasis:'46%',flexGrow:1},
 toolTile:{backgroundColor:'#FFF1FA',borderWidth:2,borderColor:'#FFD5F0',borderRadius:20,padding:13,minHeight:120,width:'47%',justifyContent:'space-between',marginBottom:12},toolName:{fontSize:15,color:C.ink,fontWeight:'900'},journalHero:{borderRadius:23,padding:18,marginBottom:14},journalHeroTitle:{fontSize:25,color:C.plum,fontWeight:'900',marginVertical:6}
});