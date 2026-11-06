import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, ActivityIndicator, Share, StyleSheet, SafeAreaView, useWindowDimensions } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Home, Layers3, BookOpen, MoonStar, Grid2X2, Sparkles, ArrowRight, Heart, RefreshCw, Share2, ChevronLeft, Search, Sun, Star, Volume2 } from 'lucide-react-native';

const API = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';
const P = { pink: '#FF45A6', magenta: '#ED2E94', purple: '#6D3CEB', plum: '#342169', aqua: '#4DE3D2', peach: '#FFC68D', cream: '#FFF4E9', ink: '#39244F', white: '#FFFFFF' };
const zodiac = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const Tab = createBottomTabNavigator();

type Spread = { id: string; title: string; category: string; desc?: string; cardCount: number; questions: {slot:number;title:string;q:string}[] };
type Deal = {slot:number;card:{id:number;name:string;icon:string;orientation:string;meaning:string};question:string;contextual_interpretation:string};

async function api(path:string, opts?:RequestInit) {
  const response = await fetch(API + path, opts);
  if (!response.ok) throw new Error('The Spiritual Vibez server could not complete that request.');
  return response.json();
}
const post = (path:string, body:unknown) => api(path, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
const gradients = [
  ['#FF80B8','#F050A0','#7336DB'],
  ['#49E1D9','#5CAFF1','#7955EB'],
  ['#FFCD86','#FF7799','#EF43AB'],
  ['#B889FF','#EC5DBD','#FF9E87'],
] as const;

function Label({children,style}:any){return <Text style={[styles.label,style]}>{children}</Text>}
function Heading({children,style}:any){return <Text style={[styles.heading,style]}>{children}</Text>}
function Body({children,style}:any){return <Text style={[styles.body,style]}>{children}</Text>}
function Pill({text,onPress,active=false}: {text:string;onPress:()=>void;active?:boolean}) {
  return <TouchableOpacity accessibilityRole="button" onPress={onPress} style={[styles.pill,active&&styles.pillActive]}><Text style={[styles.pillText,active&&{color:'#fff'}]}>{text}</Text></TouchableOpacity>;
}
function Button({text,onPress,light=false,disabled=false}: {text:string;onPress:()=>void;light?:boolean;disabled?:boolean}) {
  return <TouchableOpacity accessibilityRole="button" disabled={disabled} onPress={onPress} style={[styles.button,light&&styles.buttonLight,disabled&&{opacity:.5}]}><Text style={[styles.buttonText,light&&{color:P.plum}]}>{text}</Text><ArrowRight size={17} color={light?P.plum:'#fff'}/></TouchableOpacity>;
}
function FeatureTile({emoji,title,caption,onPress,index=0}: {emoji:string;title:string;caption:string;onPress:()=>void;index?:number}) {
  return <TouchableOpacity accessibilityRole="button" onPress={onPress} style={styles.tile}>
    <LinearGradient colors={gradients[index%4]} start={{x:0,y:0}} end={{x:1,y:1}} style={styles.tileGradient}>
      <Text style={{fontSize:31}}>{emoji}</Text>
      <Text style={styles.tileTitle}>{title}</Text>
      <Text style={styles.tileCaption}>{caption}</Text>
      <View style={styles.tileArrow}><ArrowRight size={15} color={P.plum}/></View>
    </LinearGradient>
  </TouchableOpacity>;
}
function Top({eyebrow,title,subtitle}: {eyebrow?:string;title:string;subtitle?:string}) {
  return <View style={{marginBottom:16}}>
    {eyebrow&&<Label>{eyebrow.toUpperCase()} ✦</Label>}
    <Heading>{title}</Heading>
    {subtitle&&<Body>{subtitle}</Body>}
  </View>
}
function Page({children}: {children:React.ReactNode}) {
  return <SafeAreaView style={{flex:1,backgroundColor:'#FFF2EC'}}>
    <StatusBar style="dark"/>
    <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={styles.page}>{children}</ScrollView>
  </SafeAreaView>
}
function ErrorNote({message}: {message:string}) {return <View style={styles.note}><Text style={styles.noteText}>{message}</Text></View>}
function AppHeader() {
  return <LinearGradient colors={['#FF72B9','#A46AEE','#6339C8']} style={styles.header}>
    <Text style={styles.headerName}>✨ Spiritual Vibez</Text>
    <Text style={styles.headerSubtitle}>ZODIAC • TAROT • & MORE</Text>
    <View style={styles.headerDoodles}><Text style={{fontSize:23}}>🌙  ✦  ☀️</Text></View>
  </LinearGradient>;
}
function HomeScreen({navigation}:any) {
  return <Page>
    <AppHeader/>
    <LinearGradient colors={['#6A36C9','#E54EAD','#FFAC7E']} style={styles.hero}>
      <View style={{flex:1,zIndex:2}}>
        <Text style={styles.heroEyebrow}>HEY, MYSTIC! 👋</Text>
        <Text style={styles.heroTitle}>Zero boring.{'\n'}All the vibez.</Text>
        <Text style={styles.heroCopy}>Your cosmic playground for tarot, astrology & self-discovery.</Text>
        <Button text="Try a spread ✨" onPress={()=>navigation.navigate('Spreads')}/>
      </View>
      <View style={styles.avatarScene}><Text style={styles.avatarFace}>👩🏽‍🎤</Text><Text style={styles.avatarCards}>🃏 ✨</Text></View>
      <Text style={styles.heroStar}>✦</Text>
    </LinearGradient>
    <Top title="Pick your adventure 💫" subtitle="Everything has its own space—jump into your vibe."/>
    <View style={styles.grid}>
      <FeatureTile emoji="🃏" title="Tarot Spreads" caption="Shuffle, reveal, reflect" onPress={()=>navigation.navigate('Spreads')} index={0}/>
      <FeatureTile emoji="📚" title="Learn Tarot" caption="Cards, quizzes & progress" onPress={()=>navigation.navigate('Learn')} index={2}/>
      <FeatureTile emoji="🌙" title="Daily Cosmos" caption="Your planetary weather" onPress={()=>navigation.navigate('Cosmos')} index={1}/>
      <FeatureTile emoji="✨" title="Explore More" caption="Charts, love, rituals & more" onPress={()=>navigation.navigate('Explore')} index={3}/>
    </View>
    <View style={styles.tip}><Text style={styles.tipTitle}>💖 Your space, your pace.</Text><Body>Spiritual Vibez is for curiosity and reflection—not fixed predictions. Explore whatever feels right today.</Body></View>
  </Page>
}
function SpreadsScreen(){
  const [spreads,setSpreads]=useState<Spread[]>([]);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState('');
  const [category,setCategory]=useState('All');
  const [query,setQuery]=useState('');
  const [selected,setSelected]=useState<Spread|null>(null);
  const [dealt,setDealt]=useState<Record<number,Deal>>({});
  const [busy,setBusy]=useState(false);
  const [synthesis,setSynthesis]=useState('');
  useEffect(()=>{api('/tarot/spreads').then(r=>setSpreads(r.spreads||[])).catch(()=>setError('Unable to connect to your backend. Start the FastAPI server and configure EXPO_PUBLIC_API_URL to load the 48 spreads.')).finally(()=>setLoading(false))},[]);
  const cats=['All',...Array.from(new Set(spreads.map(s=>s.category)))];
  const shown=spreads.filter(s=>(category==='All'||s.category===category)&&(!query||s.title.toLowerCase().includes(query.toLowerCase())));
  const begin=(s:Spread)=>{setSelected(s);setDealt({});setSynthesis('')};
  const draw=async(slot:number)=>{
    if(!selected||busy||dealt[slot])return;
    setBusy(true);setError('');
    try {
      const r=await post('/tarot/spreads/deal-slot',{spread_id:selected.id,slot_num:slot,exclude_card_ids:Object.values(dealt).map(d=>d.card.id)});
      setDealt(prev=>({...prev,[slot]:r}));
    } catch(e:any){setError(e.message)} finally{setBusy(false)}
  };
  const finish=async()=>{
    if(!selected)return;setBusy(true);setError('');
    try {
      const r=await post('/tarot/spreads/synthesize',{spread_id:selected.id,drawn_cards:Object.values(dealt).map(d=>({slot:d.slot,card_id:d.card.id,orientation:d.card.orientation})),save_to_journal:false});
      setSynthesis(r.synthesis||'');
    }catch(e:any){setError(e.message)}finally{setBusy(false)}
  };
  const share=()=>Share.share({message: selected?.title+'\n\n'+synthesis});
  return <Page>
    <Top eyebrow="The card studio" title={selected?selected.title:'Spreads ✨'} subtitle={selected?'Tap each numbered position to reveal its card.':'Find a layout for any question, mood, or moment.'}/>
    {selected ? <>
      <Pill text="← Browse all spreads" onPress={()=>setSelected(null)}/>
      <LinearGradient colors={['#6C39D4','#DB52AD','#FFA16B']} style={styles.readingBoard}>
        <Text style={styles.boardHeading}>✦ YOUR TAROT SPREAD ✦</Text>
        <View style={styles.cardGrid}>
          {selected.questions.map((q,i)=>{
            const d=dealt[q.slot];
            return <TouchableOpacity accessibilityRole="button" accessibilityLabel={'Draw card '+q.slot} key={q.slot} disabled={!!d||busy} onPress={()=>draw(q.slot)} style={styles.cardSlot}>
              <Text style={styles.slotSymbol}>{d?(d.card.icon||'✧'):'✦'}</Text>
              <Text style={styles.slotNumber}>{d?d.card.name:'CARD '+q.slot}</Text>
              <Text style={styles.slotHint}>{d?d.card.orientation:'TAP TO REVEAL'}</Text>
            </TouchableOpacity>;
          })}
        </View>
        <Text style={{color:'white',textAlign:'center',fontSize:12,marginTop:10}}>Cards are drawn without repeats.</Text>
      </LinearGradient>
      {selected.questions.map(q=><View key={q.slot} style={styles.detailRow}>
        <View style={styles.numberBubble}><Text style={{fontWeight:'900',color:'#fff'}}>{q.slot}</Text></View>
        <View style={{flex:1}}><Text style={styles.detailTitle}>{q.title}</Text><Body>{q.q}</Body>
          {dealt[q.slot]&&<Text style={styles.revealText}>{dealt[q.slot].card.name} ({dealt[q.slot].card.orientation}): {dealt[q.slot].card.meaning}</Text>}
        </View>
      </View>)}
      {error?<ErrorNote message={error}/>:null}
      <Button text={busy?'Working…':'Interpret my reading ✨'} disabled={busy||Object.keys(dealt).length!==selected.questions.length} onPress={finish}/>
      {synthesis?<View style={styles.result}><Text style={styles.resultTitle}>💫 Your combined reading</Text><Body>{synthesis}</Body><Button light text="Share this reading" onPress={share}/></View>:null}
      <Button light text="Start over" onPress={()=>begin(selected)}/>
    </> : <>
      <TextInput accessibilityLabel="Search tarot spreads" style={styles.search} placeholder="🔎 Search spreads..." placeholderTextColor="#85749A" value={query} onChangeText={setQuery}/>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,marginBottom:16}}>{cats.map(c=><Pill key={c} text={c} active={category===c} onPress={()=>setCategory(c)}/>)}</ScrollView>
      {loading?<ActivityIndicator color={P.pink}/>:null}
      {error?<ErrorNote message={error}/>:null}
      {shown.map((s,i)=><TouchableOpacity key={s.id} onPress={()=>begin(s)} accessibilityRole="button" style={styles.spreadRow}>
        <LinearGradient colors={gradients[i%4]} style={styles.spreadThumb}><Text style={{fontSize:36}}>{['🔮','🦋','🌆','💓','🌙','✨'][i%6]}</Text></LinearGradient>
        <View style={{flex:1}}><Text style={styles.spreadName}>{s.title}</Text><Text style={styles.small}>{s.cardCount} cards · {s.category}</Text><Text style={styles.small} numberOfLines={2}>{s.desc||'Discover a new perspective'}</Text></View>
        <ArrowRight color={P.magenta} size={22}/>
      </TouchableOpacity>)}
    </>}
  </Page>
}
function LearnScreen(){
  const [cards,setCards]=useState<any[]>([]);const [search,setSearch]=useState('');const [card,setCard]=useState<any>(null);const [quiz,setQuiz]=useState<any>(null);const [feedback,setFeedback]=useState('');
  const [error,setError]=useState('');
  useEffect(()=>{api('/tarot/cards').then(r=>setCards(r.cards||[])).catch(()=>setError('Connect to the backend to load the complete 78-card academy.'))},[]);
  const nextQuiz=async()=>{setFeedback('');try{setQuiz(await api('/tarot/study/quiz'))}catch(e:any){setError(e.message)}};
  return <Page>
    <Top eyebrow="Your tarot academy" title="Learn Tarot 📚" subtitle="Separate from spreads. Learn all 78 cards and quiz yourself."/>
    <LinearGradient colors={['#E987FF','#A87CF5','#66DCD8']} style={styles.learnBanner}><Text style={{fontSize:40}}>📚 🌞 🃏</Text><Text style={styles.learnBannerTitle}>Become a tarot pro, your way.</Text><Text style={styles.learnBannerSmall}>Major Arcana · Minor Arcana · Upright & reversed</Text></LinearGradient>
    <Button text="Quiz me ✨" onPress={nextQuiz}/>
    {quiz&&<View style={styles.result}><Text style={styles.resultTitle}>What does {quiz.card_name} represent?</Text>{(quiz.options||[]).map((option:string)=><Pill key={option} text={option} onPress={()=>setFeedback(option===quiz.correct_answer?'✨ You got it! '+quiz.correct_answer:'Keep learning! The answer is '+quiz.correct_answer)}/>)}{feedback?<Body>{feedback}</Body>:null}</View>}
    <TextInput style={styles.search} placeholder="🔎 Search card meanings..." placeholderTextColor="#85749A" value={search} onChangeText={setSearch}/>
    {error?<ErrorNote message={error}/>:null}
    {card&&<View style={styles.result}><Pill text="← Close card" onPress={()=>setCard(null)}/><Text style={styles.resultTitle}>{card.name}</Text><Body>Upright: {card.upright}</Body><Body>Reversed: {card.reversed}</Body><Body>Element: {card.element||'—'}</Body></View>}
    <Text style={styles.sectionTitle}>Explore the deck</Text>
    <View style={styles.grid}>{cards.filter(c=>c.name.toLowerCase().includes(search.toLowerCase())).map((c,i)=><TouchableOpacity key={c.id} style={styles.learningCard} onPress={()=>setCard(c)}><Text style={{fontSize:27}}>{c.icon||'🃏'}</Text><Text style={styles.learningName}>{c.name}</Text><Text style={styles.small}>{c.suit}</Text></TouchableOpacity>)}</View>
  </Page>
}
function CosmosScreen(){
  const [sign,setSign]=useState('Scorpio');const [data,setData]=useState<any>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);
  useEffect(()=>{setBusy(true);api('/astrology/daily-transits?sign='+sign).then(setData).catch(()=>setError('Unable to load live transits. Check your backend connection.')).finally(()=>setBusy(false))},[sign]);
  return <Page>
    <Top eyebrow="Your cosmic weather" title="Cosmos & Transits 🌙" subtitle="Sun, Moon, Mercury and Venus—plus your zodiac mood forecast."/>
    <LinearGradient colors={['#6F49DA','#B457E5','#FF7AAE']} style={styles.cosmosCard}>
      <Text style={{fontSize:50}}>🌙 ✨</Text>
      <Text style={styles.cosmosTitle}>{data?.moon_phase||'Your daily cosmic check-in'}</Text>
      <Text style={{color:'#fff'}}>Moon illumination: {data?.illumination_percent??'—'}%</Text>
    </LinearGradient>
    <Text style={styles.sectionTitle}>Choose your zodiac sign</Text>
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:7,marginBottom:16}}>{zodiac.map(z=><Pill key={z} text={z} active={sign===z} onPress={()=>{setError('');setSign(z)}}/>)}</ScrollView>
    {busy?<ActivityIndicator color={P.pink}/>:null}
    {error?<ErrorNote message={error}/>:null}
    {data&&<><View style={styles.grid}>
      {[['☀️','Sun',data.sun_position],['☿','Mercury',data.mercury_status],['♀','Venus',data.venus_status],['🌘','Moon',data.moon_phase]].map(([emoji,title,value])=><View key={title} style={styles.planetCard}><Text style={{fontSize:27}}>{emoji}</Text><Text style={styles.detailTitle}>{title}</Text><Body>{value}</Body></View>)}
    </View><View style={styles.result}><Text style={styles.resultTitle}>💖 Your {sign} vibe</Text><Body>{data.forecast?.content}</Body><Text style={styles.small}>For reflection and entertainment, not a measured mood prediction.</Text><Button light text="Share my cosmic forecast" onPress={()=>Share.share({message:sign+' cosmic forecast: '+data.forecast?.content})}/></View></>}
  </Page>
}
const tools = [
  {id:'moon',emoji:'🌒',title:'Natal Moon Phase',description:'Discover the moon phase at birth',group:'Astrology'},
  {id:'natal',emoji:'🪐',title:'Natal Birth Chart',description:'Explore your planetary placements',group:'Astrology'},
  {id:'draconic',emoji:'🐉',title:'Draconic Chart',description:'Explore your symbolic soul chart',group:'Astrology'},
  {id:'bazi',emoji:'🐲',title:'Chinese Zodiac & BaZi',description:'Four pillars and the Chinese zodiac',group:'Astrology'},
  {id:'houses',emoji:'🏘️',title:'Zodiac Houses',description:'Learn all twelve astrological houses',group:'Astrology'},
  {id:'lunar',emoji:'🗓️',title:'13-Moon Calendar',description:'Explore the alternative lunar calendar',group:'Astrology'},
  {id:'astro',emoji:'🌍',title:'Astrocartography',description:'Explore relocation themes',group:'Astrology'},
  {id:'life',emoji:'🔢',title:'Life Path Numerology',description:'Calculate your number',group:'Numbers & Love'},
  {id:'numbers',emoji:'✨',title:'Numerology Lessons',description:'The meaning of the numbers',group:'Numbers & Love'},
  {id:'love',emoji:'💞',title:'Love Match',description:'Compare zodiac signs',group:'Numbers & Love'},
  {id:'sound',emoji:'🎵',title:'Sound Frequencies',description:'Solfeggio sounds and information',group:'Wellness & Rituals'},
  {id:'rituals',emoji:'🕯️',title:'Ritual Finder',description:'Browse ceremonial practices',group:'Wellness & Rituals'},
  {id:'cycle',emoji:'🌸',title:'Moon & Period Tracker',description:'Track cycles privately',group:'Wellness & Rituals'},
  {id:'shadow',emoji:'📓',title:'Shadow Work Journal',description:'Reflect in your own space',group:'Wellness & Rituals'},
  {id:'divination',emoji:'🔮',title:'Divination Hub',description:'Pendulum and runes',group:'Other Vibez'},
  {id:'oracle',emoji:'💬',title:'Mystic Companion',description:'Explore the rule-based guide',group:'Other Vibez'},
  {id:'store',emoji:'🛍️',title:'Creator Store',description:'Discover creator offerings',group:'Other Vibez'},
];
function ExploreScreen(){
  const [chosen,setChosen]=useState<string|null>(null);
  const [date,setDate]=useState('1996-11-05');const [time,setTime]=useState('14:30');const [sign,setSign]=useState('Scorpio');const [sign2,setSign2]=useState('Taurus');
  const [lastPeriod,setLastPeriod]=useState('2026-10-23');const [cycleLength,setCycleLength]=useState('28');
  const [city,setCity]=useState('New York City');const [query,setQuery]=useState('');const [response,setResponse]=useState<any>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);
  const tool=tools.find(t=>t.id===chosen);
  const load=async()=> {
    if(!chosen)return;setBusy(true);setError('');setResponse(null);
    const [year,month,day]=date.split('-').map(Number);
    const params:Record<string,()=>Promise<any>>={
      moon:()=>post('/astrology/moon-phase',{birth_date:date,birth_time:time}),
      natal:()=>post('/astrology/natal-chart',{birth_date:date,birth_time:time,chart_system:'placidus'}),
      draconic:()=>post('/astrology/natal-chart',{birth_date:date,birth_time:time,chart_system:'draconic'}),
      bazi:()=>post('/astrology/bazi',{birth_year:year,birth_month:month,birth_day:day,birth_hour:Number(time.slice(0,2))}),
      houses:()=>api('/astrology/houses'),lunar:()=>api('/astrology/lunar-calendar/1'),
      astro:()=>api('/astrology/astrocartography?city='+encodeURIComponent(city)),
      life:()=>post('/synastry/life-path',{birth_year:year,birth_month:month,birth_day:day}),
      numbers:()=>api('/synastry/numerology-lessons'),love:()=>post('/synastry/compatibility',{partner_a_sign:sign,partner_b_sign:sign2}),
      sound:()=>api('/rituals/frequencies'),rituals:()=>api('/rituals/search?query='+encodeURIComponent(query)),
      cycle:()=>post('/wellness/menstrual-cycle',{last_period_date:lastPeriod,cycle_length:Number(cycleLength)}),
      shadow:()=>api('/wellness/shadow-prompts'),divination:()=>api('/divination/runes'),
      oracle:()=>post('/oracle/chat',{message:query||'What does the Moon mean?',zodiac_sign:sign}),
      store:()=>api('/store/products'),
    };
    try{setResponse(await params[chosen]())}catch(e:any){setError(e.message)}finally{setBusy(false)}
  };
  const Input=({value,onChange,placeholder}:any)=><TextInput accessibilityLabel={placeholder} style={styles.search} value={value} onChangeText={onChange} placeholder={placeholder} placeholderTextColor="#8A7DA0"/>;
  return <Page>
    {!tool?<>
      <Top eyebrow="The cosmic playground" title="Explore More ✨" subtitle="Every feature in its own space. Tap a tool to open it."/>
      {Array.from(new Set(tools.map(t=>t.group))).map(group=><View key={group}><Text style={styles.sectionTitle}>{group}</Text><View style={styles.grid}>{tools.filter(t=>t.group===group).map((t,i)=><FeatureTile key={t.id} emoji={t.emoji} title={t.title} caption={t.description} index={i} onPress={()=>{setChosen(t.id);setError('');setResponse(null)}}/>)}</View></View>)}
    </>:<>
      <Pill text="← All features" onPress={()=>{setChosen(null);setResponse(null)}}/>
      <View style={{height:14}}/>
      <Top eyebrow={tool.group} title={tool.emoji+' '+tool.title} subtitle={tool.description}/>
      {['moon','natal','draconic','bazi','life'].includes(chosen)&&<><Label>Birth date (YYYY-MM-DD)</Label><Input value={date} onChange={setDate} placeholder="1996-11-05"/><Label>Birth time (HH:MM)</Label><Input value={time} onChange={setTime} placeholder="14:30"/></>}
      {chosen==='cycle'&&<><Label>Last period start (YYYY-MM-DD)</Label><Input value={lastPeriod} onChange={setLastPeriod} placeholder="2026-10-23"/><Label>Average cycle length (days)</Label><Input value={cycleLength} onChange={setCycleLength} placeholder="28"/><ErrorNote message="Cycle projections are estimates and not a reliable way to predict fertility or avoid pregnancy."/></>}
      {chosen==='astro'&&<Input value={city} onChange={setCity} placeholder="Focus city"/>}
      {['rituals','oracle'].includes(chosen)&&<Input value={query} onChange={setQuery} placeholder={chosen==='oracle'?'Ask about a tarot card, zodiac sign, or ritual':'Search rituals'}/>}
      {chosen==='love'&&<><Label>Your zodiac sign</Label><ScrollView horizontal contentContainerStyle={{gap:6,marginBottom:12}}>{zodiac.map(z=><Pill key={z} text={z} active={z===sign} onPress={()=>setSign(z)}/>)}</ScrollView><Label>Their zodiac sign</Label><ScrollView horizontal contentContainerStyle={{gap:6,marginBottom:12}}>{zodiac.map(z=><Pill key={z} text={z} active={z===sign2} onPress={()=>setSign2(z)}/>)}</ScrollView></>}
      {chosen==='sound'&&<ErrorNote message="Frequency descriptions are available here. Audio playback will be added with device-safe volume controls; wellness claims are not medical treatments."/>}
      {['natal','draconic','bazi','astro'].includes(chosen)&&<ErrorNote message="The current backend calculations are preliminary and must be validated before being presented as precise astrological charts."/>}
      {chosen==='shadow'&&<ErrorNote message="Private journal writing is disabled in this preview until user authentication and private storage are implemented."/>}
      <Button text={busy?'Loading…':chosen==='rituals'?'Find rituals ✨':chosen==='oracle'?'Ask my companion ✨':'Explore this feature ✨'} onPress={load} disabled={busy}/>
      {error?<ErrorNote message={error}/>:null}
      {response&&<View style={styles.result}><Text style={styles.resultTitle}>Your {tool.title} result</Text>
        <Text selectable style={styles.jsonText}>{JSON.stringify(response,null,2)}</Text>
        <Button light text="Share results" onPress={()=>Share.share({message:tool.title+'\n'+JSON.stringify(response,null,2)})}/>
      </View>}
    </>}
  </Page>
}
const icons=[Home,Layers3,BookOpen,MoonStar,Grid2X2];
export default function App(){
  return <NavigationContainer><Tab.Navigator screenOptions={({route})=>({
    headerShown:false,
    tabBarStyle:{backgroundColor:'#FFF6F2',borderTopColor:'#F9CADE',borderTopWidth:1,height:72,paddingTop:8,paddingBottom:8},
    tabBarActiveTintColor:P.magenta,tabBarInactiveTintColor:'#917C9B',
    tabBarLabelStyle:{fontSize:11,fontWeight:'800'},
    tabBarIcon:({color,size})=>{const Icon=icons[['Home','Spreads','Learn','Cosmos','Explore'].indexOf(route.name)];return <Icon size={size} color={color} strokeWidth={2.5}/>},
  })}>
    <Tab.Screen name="Home" component={HomeScreen}/>
    <Tab.Screen name="Spreads" component={SpreadsScreen}/>
    <Tab.Screen name="Learn" component={LearnScreen}/>
    <Tab.Screen name="Cosmos" component={CosmosScreen}/>
    <Tab.Screen name="Explore" component={ExploreScreen}/>
  </Tab.Navigator></NavigationContainer>;
}
const styles=StyleSheet.create({
  page:{paddingHorizontal:18,paddingTop:10,paddingBottom:46,maxWidth:900,width:'100%',alignSelf:'center'},
  header:{borderRadius:23,padding:19,marginBottom:18,overflow:'hidden'},
  headerName:{color:'#fff',fontSize:30,fontWeight:'900',letterSpacing:-1},
  headerSubtitle:{color:'#FFE7F3',fontSize:10,letterSpacing:3,fontWeight:'900',marginTop:5},
  headerDoodles:{position:'absolute',right:13,top:24},
  hero:{minHeight:250,borderRadius:27,marginBottom:24,padding:21,overflow:'hidden',flexDirection:'row'},
  heroEyebrow:{color:'#FFE89A',fontSize:12,fontWeight:'900',letterSpacing:2},
  heroTitle:{color:'#fff',fontSize:31,fontWeight:'900',lineHeight:36,marginTop:13,textShadowColor:'#65237D',textShadowRadius:8},
  heroCopy:{color:'#fff',fontSize:13,lineHeight:19,marginVertical:13,maxWidth:230},
  avatarScene:{width:114,justifyContent:'center',alignItems:'center'},
  avatarFace:{fontSize:74},avatarCards:{fontSize:24,marginTop:-4},heroStar:{position:'absolute',top:14,right:18,color:'#FFE69E',fontSize:32},
  label:{fontSize:11,color:P.magenta,letterSpacing:1.8,fontWeight:'900',marginBottom:6},
  heading:{fontSize:27,fontWeight:'900',color:P.ink,letterSpacing:-.5,marginBottom:6},
  body:{fontSize:13.5,lineHeight:20,color:'#755F82'},
  sectionTitle:{fontSize:19,fontWeight:'900',color:P.ink,marginBottom:12,marginTop:16},
  grid:{flexDirection:'row',flexWrap:'wrap',gap:12,marginBottom:16},
  tile:{width:'48%',flexGrow:1,minWidth:138,borderRadius:21,overflow:'hidden',shadowColor:'#B361B1',shadowRadius:7,shadowOpacity:.15,elevation:3},
  tileGradient:{minHeight:158,padding:15,justifyContent:'center'},
  tileTitle:{color:'#fff',fontSize:17,fontWeight:'900',marginTop:6},
  tileCaption:{color:'#FFF6FE',fontSize:11.5,marginTop:3,marginRight:24},
  tileArrow:{width:24,height:24,borderRadius:12,backgroundColor:'#FFF0F8',alignItems:'center',justifyContent:'center',position:'absolute',right:12,bottom:12},
  tip:{padding:18,backgroundColor:'#FFE4F1',borderRadius:20,marginTop:5},tipTitle:{color:P.ink,fontSize:17,fontWeight:'900',marginBottom:7},
  button:{marginVertical:10,borderRadius:27,paddingVertical:13,paddingHorizontal:19,backgroundColor:P.magenta,alignItems:'center',justifyContent:'center',flexDirection:'row',gap:9,alignSelf:'flex-start'},
  buttonLight:{backgroundColor:'#FFE5F5'},buttonText:{color:'#fff',fontSize:14,fontWeight:'900'},
  pill:{paddingHorizontal:14,paddingVertical:9,borderRadius:23,backgroundColor:'#FFE7F2',alignSelf:'flex-start',marginBottom:7},
  pillActive:{backgroundColor:P.magenta},pillText:{color:P.plum,fontSize:12,fontWeight:'800'},
  search:{borderRadius:17,backgroundColor:'#fff',paddingHorizontal:16,paddingVertical:12,fontSize:14,color:P.ink,borderWidth:1,borderColor:'#FAD1E5',marginVertical:9},
  note:{backgroundColor:'#FFF0D9',borderRadius:15,padding:13,marginVertical:8},noteText:{fontSize:12,color:'#674466',lineHeight:18},
  spreadRow:{flexDirection:'row',alignItems:'center',gap:12,backgroundColor:'#fff',padding:9,borderRadius:20,marginBottom:12,shadowColor:'#B86DB0',shadowRadius:6,shadowOpacity:.1,elevation:2},
  spreadThumb:{height:92,width:94,borderRadius:15,alignItems:'center',justifyContent:'center'},
  spreadName:{color:P.ink,fontWeight:'900',fontSize:16,marginBottom:4},
  small:{color:'#846E8D',fontSize:11.5,lineHeight:17},
  readingBoard:{padding:16,borderRadius:24,marginVertical:14},boardHeading:{color:'#fff',textAlign:'center',fontWeight:'900',marginBottom:14,letterSpacing:2},
  cardGrid:{flexDirection:'row',flexWrap:'wrap',gap:11,justifyContent:'center'},
  cardSlot:{width:94,height:143,backgroundColor:'#FFF4EB',borderWidth:3,borderColor:'#FFDEF7',borderRadius:13,alignItems:'center',justifyContent:'center',padding:5},
  slotSymbol:{fontSize:31,color:P.purple},slotNumber:{fontSize:11,textAlign:'center',fontWeight:'900',color:P.plum,marginTop:5},
  slotHint:{fontSize:9,color:P.magenta,textAlign:'center',marginTop:5},
  detailRow:{flexDirection:'row',gap:12,backgroundColor:'#fff',padding:15,borderRadius:17,marginBottom:10},
  numberBubble:{height:30,width:30,borderRadius:15,backgroundColor:P.magenta,alignItems:'center',justifyContent:'center'},
  detailTitle:{color:P.ink,fontSize:14,fontWeight:'900',marginBottom:4},
  revealText:{color:P.purple,fontSize:12,lineHeight:18,marginTop:8},
  result:{padding:17,backgroundColor:'#FFF',borderWidth:1,borderColor:'#FFD5EA',borderRadius:22,marginVertical:13,gap:9},
  resultTitle:{fontSize:20,color:P.plum,fontWeight:'900'},
  learnBanner:{borderRadius:25,padding:20,marginBottom:14,minHeight:156},
  learnBannerTitle:{color:'#fff',fontSize:23,fontWeight:'900',marginVertical:10},learnBannerSmall:{color:'#fff',fontSize:12},
  learningCard:{width:'47%',flexGrow:1,backgroundColor:'#fff',borderRadius:17,padding:15,marginBottom:1},
  learningName:{fontSize:14,fontWeight:'900',color:P.ink,marginTop:7,marginBottom:3},
  cosmosCard:{borderRadius:26,padding:22,alignItems:'center',gap:10,marginBottom:18},
  cosmosTitle:{color:'#fff',fontSize:23,textAlign:'center',fontWeight:'900'},
  planetCard:{width:'47%',flexGrow:1,padding:17,backgroundColor:'#fff',borderRadius:19,minHeight:125},
  jsonText:{color:P.ink,fontSize:12,lineHeight:19},
});
