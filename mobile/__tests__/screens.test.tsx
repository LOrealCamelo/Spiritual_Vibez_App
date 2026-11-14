import React from 'react';
import TestRenderer,{act,ReactTestRenderer} from 'react-test-renderer';
import {Image,Text,TextInput,TouchableOpacity,Linking,Alert,ScrollView,StyleSheet,View} from 'react-native';
import * as SafeArea from 'react-native-safe-area-context';
import {ReferenceHome} from '../src/components/ReferenceHome';
import AsyncStorage from '@react-native-async-storage/async-storage';
import App,{HomeScreen,SpreadsScreen,LearnScreen,JournalScreen,ExploreScreen,CosmosScreen} from '../App';
import {IllustratedCard,IllustratedToolCard,PanelIllustration,SpreadIllustration,UI_PANELS} from '../src/components/IllustratedCard';
import {LearningCard} from '../src/components/LearningCard';
import {NativeChartReport,NativeMoonCalendar} from '../src/components/CosmicTools';
import {EquinoxCalendar} from '../src/components/EquinoxCalendar';
import {AstrocartographyReport} from '../src/components/AstrocartographyReport';
import {matchesVibe} from '../src/api/spreads';
import {SvgXml} from 'react-native-svg';

let tree:ReactTestRenderer;
beforeEach(()=>{
  jest.spyOn(Image,'resolveAssetSource').mockReturnValue({width:600,height:250,uri:'test.png',scale:1});
  globalThis.fetch=jest.fn().mockRejectedValue(new Error('Offline in test'));
  jest.clearAllMocks();
});
afterEach(async()=>{
  if(tree)await act(async()=>tree.unmount());
  jest.restoreAllMocks();
});
async function render(element:React.ReactElement){await act(async()=>{tree=TestRenderer.create(element)});return tree;}
async function press(label:string){
  const button=tree.root.findAllByType(TouchableOpacity).find(x=>x.props.accessibilityLabel===label);
  expect(button).toBeDefined();
  await act(async()=>button!.props.onPress());
}
const text=()=>tree.root.findAllByType(Text).map(x=>x.props.children).flat(Infinity).join(' ');

test('Home clean PNG cards navigate independently to learning, spreads, cosmos, tools and journal',async()=>{
  const navigate=jest.fn();
  await render(<HomeScreen navigation={{navigate}}/>);
  for(const [label,route,params] of [
    ['Explore','Explore',undefined],['Daily Readings','Learn',{daily:true}],['Moon Cycles','Cosmos',undefined],
    ['Manifest','Explore',{tool:'rituals'}],['Natal Reading','Explore',{tool:'natal'}],['Tarot','Spreads',undefined],['Journal','Journal',undefined],
  ] as const){
    await press(label);
    expect(navigate.mock.calls.at(-1)?.[0]).toBe(route);
    if(params)expect(navigate.mock.calls.at(-1)?.[1]).toEqual(params);
  }
});

test('all 24 panels use fresh illustration sources and readable live labels',async()=>{
  expect(Object.keys(UI_PANELS)).toHaveLength(24);
  const onPress=jest.fn();
  await render(<IllustratedCard asset="home_daily_card" width={300} label="Daily card" onPress={onPress}/>);
  expect(text()).toContain('Daily Card');expect(text()).toContain('Get today’s insight');
  const image=tree.root.findByType(Image);expect(image.props.style.width).toBe(image.props.style.height);
  expect(image.props.style.width).toBeGreaterThan(0);expect(image.props.accessible).toBe(false);
  await press('Daily card');
  expect(onPress).toHaveBeenCalledTimes(1);
});

test('all 18 Explore features use clear illustrated cards and open their own tools',async()=>{
 await render(<ExploreScreen route={{params:{}}} navigation={{goBack:jest.fn()}}/>);
 const cards=tree.root.findAllByType(IllustratedToolCard);
 expect(cards).toHaveLength(18);expect(tree.root.findAllByType(PanelIllustration)).toHaveLength(18);
 const labels=cards.map(c=>c.props.title);
 for(const label of labels){
  await press(label);
  expect(text()).toContain(label);
  await press('Back to all features');
  expect(tree.root.findAllByType(IllustratedToolCard)).toHaveLength(18);
 }
});

test('the complete spread list uses original illustrations on glass surfaces',async()=>{
 await render(<SpreadsScreen route={{params:{}}}/>);
 expect(tree.root.findAllByType(SpreadIllustration).length).toBeGreaterThan(0);
 for(const art of tree.root.findAllByType(SpreadIllustration))expect(art.findByType(PanelIllustration)).toBeDefined();
});

test('asteroid dropdown searches the complete catalog and adds a non-major body',async()=>{
 const defaults=[{id:1,name:'Ceres'},{id:2,name:'Pallas'},{id:3,name:'Juno'},{id:4,name:'Vesta'}];
 globalThis.fetch=jest.fn().mockImplementation(async(url:string)=>({ok:true,json:async()=>url.includes('/locations/countries')?{countries:[{code:'US',name:'United States'}]}:url.includes('/locations/regions')?{regions:[]}:url.includes('/locations/cities')?{places:[]}:url.includes('query=1008')?{asteroids:[{id:1008,name:'La Paz'}],total:1,defaults}:{asteroids:defaults,total:895910,defaults,has_more:true}}));
 await render(<ExploreScreen route={{params:{tool:'asteroids'}}} navigation={{goBack:jest.fn()}}/>);
 await act(async()=>tree.root.findAllByType(TextInput).find(x=>x.props.accessibilityLabel==='Find an asteroid by name or number')!.props.onChangeText('1008'));
 await press('Search asteroids');await press('Add an asteroid');await press('Select La Paz (1008)');
 expect(text().replace(/\s+/g,' ')).toContain('5 / 10 selected');
 await press('Remove La Paz');expect(text().replace(/\s+/g,' ')).toContain('4 / 10 selected');
});

test('houses and numerology teach general meanings and include Tarot connections',async()=>{
 await render(<ExploreScreen route={{params:{tool:'houses'}}} navigation={{goBack:jest.fn()}}/>);
 expect(text()).toContain('These are general house meanings');expect(text()).toContain('Planets & Tarot connections');
 expect(tree.root.findAllByType(TextInput)).toHaveLength(0);
 await act(async()=>tree.unmount());
 await render(<ExploreScreen route={{params:{tool:'numbers'}}} navigation={{goBack:jest.fn()}}/>);
 for(const label of ['The Master Builder','The Master Teacher','The numbers of Tarot','Court cards'])expect(text()).toContain(label);
 expect(tree.root.findAllByType(TextInput).some(x=>x.props.placeholder==='1996-11-05')).toBe(true);
});

test('learning module progress comes from distinct studied cards and a quiz can only be answered once',async()=>{
  await render(<LearnScreen route={{params:{}}}/>);
  expect(tree.root.findAllByType(LearningCard)[0].props.completed).toBe(0);
  await press('Major Arcana: 0 / 22 cards');
  await press('The Fool');
  await press('The Fool');
  expect(tree.root.findAllByType(LearningCard)[0].props.completed).toBe(1);
  const back=tree.root.findAllByType(TouchableOpacity).find(x=>x.findAllByType(Text).some(t=>t.props.children==='← Learning modules'))!;
  await act(async()=>back.props.onPress());
  expect(tree.root.findAllByType(LearningCard).find(x=>x.props.asset==='learn_major_arcana')!.props.completed).toBe(1);
  await press('Quiz Me');
  const choices=tree.root.findAllByType(TouchableOpacity).filter(x=>x.props.accessibilityRole==='button' && ['Restlessness','Confusion','Isolation'].includes(x.props.accessibilityLabel));
  const option=choices[0];
  await act(async()=>option.props.onPress());
  expect(choices.every(x=>x.props.disabled)).toBe(true);
  const completed=tree.root.findAllByType(LearningCard)[0].props.completed;
  await act(async()=>option.props.onPress());
  expect(tree.root.findAllByType(LearningCard)[0].props.completed).toBe(completed);
});

test('spread artwork opens an interactive reading and filters affect the illustrated collection',async()=>{
  await render(<SpreadsScreen route={{params:{}}}/>);
  await press('Filter by Love');
  expect(tree.root.findAllByType(IllustratedCard).some(x=>x.props.asset==='spreads_trust_gut')).toBe(false);
  await press('Filter by All');
  await press('Trust Your Gut');
  expect(text()).toContain('TAP TO REVEAL');
  expect(text()).toContain('CARD 5');
});

test('journal actions save a reflection that survives a screen reopen and open saved readings',async()=>{
  await render(<JournalScreen navigation={{navigate:jest.fn()}}/>);
  await press("Open today's journal");
  await act(async()=>tree.root.findByType(TextInput).props.onChangeText('A calmer day.'));
  const save=tree.root.findAllByType(TouchableOpacity).find(x=>x.findAllByType(Text).some(t=>t.props.children==='Save reflection ✎'))!;
  await act(async()=>save.props.onPress());
  expect(AsyncStorage.setItem).toHaveBeenCalledWith('sv_journal',expect.stringContaining('A calmer day.'));
  await press('Saved Readings');
  expect(text()).toContain('No saved readings yet.');
  await act(async()=>tree.unmount());
  await render(<JournalScreen navigation={{navigate:jest.fn()}}/>);
  expect(text()).toContain('A calmer day.');
});

test('real tab navigator exposes six destinations and opens the independent learning and spreads screens',async()=>{
  await render(<App/>);
  const output=JSON.stringify(tree.toJSON());
  for(const label of ['Home','Spreads','Learn','Cosmos','Explore','Journal'])expect(output).toContain(label);
  for(const [label,asset] of [['Learn Tarot','learn_header'],['Spreads','spreads_header']] as const){
    let button=tree.root.findAllByType(Text).filter(x=>x.props.children===label).at(-1)!;
    while(!button.props.onPress && button.parent)button=button.parent;
    expect(button.props.onPress).toBeInstanceOf(Function);
    await act(async()=>button.props.onPress({preventDefault:()=>{}}));
    expect(tree.root.findAllByType(IllustratedCard).some(x=>x.props.asset===asset)).toBe(true);
  }
});

test('connected spread artwork uses canonical API IDs and the full backend layout',async()=>{
  const catalog=require('../../backend/data/master_data.json').masterSpreadsData;
  globalThis.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>({spreads:catalog})});
  await render(<SpreadsScreen route={{params:{}}}/>);
  await press('At a Crossroads');
  expect(text()).toContain('CARD 10');
});

test.each([
  ['bazi','/astrology/bazi','POST'],


  ['life','/synastry/life-path','POST'],['numbers','/synastry/life-path','POST'],
  ['love','/synastry/compatibility','POST'],['sound','/rituals/frequencies','GET'],
  ['rituals','/rituals/search','GET'],['pendulum','/divination/pendulum','POST'],
  ['oracle','/oracle/chat','POST'],
])('native %s action calls the correct backend method and path',async(tool,path,method)=>{
  globalThis.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>({connected:true})});
  await render(<ExploreScreen route={{params:{tool}}} navigation={{goBack:jest.fn()}}/>);
  const date=tree.root.findAllByType(TextInput).find(x=>x.props.placeholder==='1996-11-05');
  if(date)await act(async()=>date.props.onChangeText('1996-11-05'));
  const run=tree.root.findAllByType(TouchableOpacity).find(x=>x.findAllByType(Text).some(t=>t.props.children==='✨ Explore this feature'))!;
  await act(async()=>run.props.onPress());
  const [url,options]=(globalThis.fetch as jest.Mock).mock.calls.at(-1)!;
  expect(String(url).replace(/^https?:\/\/[^/]+/,'').split('?')[0]).toBe('/api'+path);
  expect(options?.method||'GET').toBe(method);
  if(date)expect(JSON.parse(options.body)).toMatchObject(['life','numbers','bazi'].includes(tool)?{birth_year:1996,birth_month:11,birth_day:5}:{birth_date:'1996-11-05',birth_time:'12:00'});
  expect(text()).toContain('true');
});

test('store shows one website link without loading a product catalog',async()=>{
  const open=jest.spyOn(Linking,'openURL').mockResolvedValue(true);
  await render(<ExploreScreen route={{params:{tool:'store'}}} navigation={{goBack:jest.fn()}}/>);
  const button=tree.root.findAllByType(TouchableOpacity).find(x=>x.findAllByType(Text).some(t=>t.props.children==='Visit my store ↗'))!;
  await act(async()=>button.props.onPress());
  expect(open).toHaveBeenCalledWith('https://neurospicymystic.com/');
  expect(globalThis.fetch).not.toHaveBeenCalled();
});


test.each([['natal','AM'],['natal','PM'],['moon','AM'],['moon','PM'],['asteroids','PM']])('native %s submits an explicit %s birth time and selected city',async(tool,period)=>{
 const place={place_id:'5142056',label:'Utica, New York, United States',timezone:'America/New_York'};
 globalThis.fetch=jest.fn().mockImplementation(async(url:string)=>({ok:true,json:async()=>url.includes('/locations/countries')?{countries:[{code:'US',name:'United States'}]}:url.includes('/locations/regions')?{regions:[{code:'NY',name:'New York'}]}:url.includes('/locations/cities')?{places:[place]}:url.endsWith('/astrology/asteroids')?{asteroids:[{id:1,name:'Ceres'},{id:2,name:'Pallas'},{id:3,name:'Juno'},{id:4,name:'Vesta'}]}:{emoji:'🌘',natal_moon_phase:'Waning Crescent',illumination_percentage:21,description:'Birth Moon',moon_position:'Virgo 2°',birth_local_time:'1996-11-05T14:30:00-05:00',location:place}}));
 await render(<ExploreScreen route={{params:{tool}}} navigation={{goBack:jest.fn()}}/>);
 const fill=async(label:string,value:string)=>act(async()=>tree.root.findAllByType(TextInput).find(x=>x.props.accessibilityLabel===label)!.props.onChangeText(value));
 await fill('Name (optional)','Mystic');await fill('Birth date YYYY-MM-DD','1996-11-05');await press('Hour (AM/PM)');await press('Select 2 '+period);await press('Minutes');await press('Select 30');await press('State / province');await press('Select New York');await fill('Filter city list','Utica');
 expect(text()).not.toContain('Birth latitude');expect(text()).not.toContain('Birth longitude');
 await press('Search cities');expect((globalThis.fetch as jest.Mock).mock.calls.some(([url])=>String(url).includes('query=Utica'))).toBe(true);await press('City of birth');await press('Select '+place.label);
 await press('Sidereal (Lahiri)');if(tool==='natal')await press('Traditional (7 planets)');await press(tool==='moon'?'Find my natal Moon':tool==='asteroids'?'Calculate asteroids':'Create my birth chart');
 const [url,options]=(globalThis.fetch as jest.Mock).mock.calls.at(-1)!;
 expect(url).toContain('/astrology/'+(tool==='moon'?'moon-phase':tool==='asteroids'?'asteroids/natal-chart':'natal-chart'));
 expect(JSON.parse(options.body)).toMatchObject({name:'Mystic',birth_date:'1996-11-05',birth_time:'02:30',birth_period:period,place_id:'5142056',zodiac:'sidereal',rulership:tool==='natal'?'traditional':'modern',chart_system:'natal'});
 expect(text()).toContain('Waning Crescent');
});

test('actual tarot PNGs appear in a reveal, a lesson and a study quiz',async()=>{
 await render(<SpreadsScreen route={{params:{}}}/>);await press('Trust Your Gut');
 const slot=tree.root.findAllByType(TouchableOpacity).find(x=>x.findAllByType(Text).some(t=>String(t.props.children).includes('CARD ')&&t.props.children.includes(1)))!;
 await act(async()=>slot.props.onPress());
 expect(tree.root.findAllByType(Image).some(x=>x.props.accessibilityLabel&&x.props.style?.width===96)).toBe(true);
 await act(async()=>tree.unmount());await render(<LearnScreen route={{params:{}}}/>);await press('Major Arcana: 0 / 22 cards');await press('The Fool');
 expect(tree.root.findAllByType(Image).some(x=>x.props.accessibilityLabel==='The Fool'&&x.props.style?.width===200)).toBe(true);
 const back=tree.root.findAllByType(TouchableOpacity).find(x=>x.findAllByType(Text).some(t=>t.props.children==='← Learning modules'))!;
 await act(async()=>back.props.onPress());await press('Quiz Me');expect(tree.root.findAllByType(Image).some(x=>x.props.style?.width===180)).toBe(true);
});

test('daily sky loads on entry, switches sign and requests the selected date',async()=>{
 const planets=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto'].map(planet=>({planet,glyph:'',formatted:'Scorpio 2°',motion:'Direct'}));
 globalThis.fetch=jest.fn().mockImplementation(async(url:string)=>({ok:true,json:async()=>url.includes('/moon-calendar')?require('./fixtures/moonCalendar.json'):({date:'2026-11-08',as_of:'2026-11-08T12:00:00',selected_sign:url.includes('sign=Pisces')?'Pisces':'Scorpio',moon_phase:'Waning Crescent in Scorpio',moon:{waxing:false,next_phase:'New Moon',next_phase_at:'2026-11-09T07:02:00Z'},planets,forecast:{details:[],method:'Solar houses',note:'Symbolic'}})}));
 await render(<CosmosScreen navigation={{goBack:jest.fn()}}/>);expect(text()).toContain('Waning Crescent');expect(text()).toContain('Neptune');
 await press('Pisces');expect(text().replace(/\s+/g,' ')).toContain('Your Pisces daily reflection');
 await act(async()=>tree.root.findAllByType(TextInput).find(x=>x.props.accessibilityLabel==='Date YYYY-MM-DD (blank = today)')!.props.onChangeText('2026-11-07'));await press('Refresh my cosmic weather');
 expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)![0])).toContain('date=2026-11-07');
});


test('native SVG parser renders a real backend chart and its complete report',async()=>{
 const report=require('./fixtures/natalChart.json');
 await render(<NativeChartReport result={report}/>);
 expect(tree.root.findByType(SvgXml).props.xml).toContain('viewBox="0 0 760 760"');
 const output=text().replace(/\s+/g,' ');
 for(const p of report.placements)expect(output).toContain(p.planet+' in '+p.sign);
 expect(output).toContain('House 12');expect(output).toContain('Major planetary aspects');expect(output).toMatch(/Ruler of house\s+1\s*:\s*Neptune/);expect(output).toContain('ASC aspects');
});


test('live Career filter finds the API career spreads and keeps a readable selected label',async()=>{
 const catalog=require('../../backend/data/master_data.json').masterSpreadsData;
 expect(catalog.filter((s:any)=>matchesVibe(s,'Career')).map((s:any)=>s.id)).toEqual(expect.arrayContaining(['career-shift','financial-healing']));
 globalThis.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>({spreads:catalog})});
 await render(<SpreadsScreen route={{params:{}}}/>);await press('Filter by Career');
 expect(text()).toContain('Career Shift');
 const selected=tree.root.findAllByType(TouchableOpacity).find(x=>x.props.accessibilityLabel==='Filter by Career')!;
 expect(selected.props.accessibilityState.selected).toBe(true);
 expect(selected.findAllByType(Text)).toHaveLength(1);
 expect(selected.findByType(Text).props.children).toContain('Career');
});


test('monthly Moon calendar stays in the Moon section and supports day and month selection',async()=>{
 const calendar=require('./fixtures/moonCalendar.json');const onSelect=jest.fn();
 globalThis.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>calendar});
 await render(<NativeMoonCalendar timezone="UTC" zodiac="tropical" currentDate="2026-11-08" selectedDate="" onSelect={onSelect}/>);
 expect(text()).toContain('Monthly Moon Phases');expect(text()).toContain('November 2026');
 expect(text()).toContain('Day-by-day lunar calendar');expect(text()).toContain('Heart, aorta');expect(text()).toContain('Ask your surgical team');
 expect(tree.root.findAllByType(SvgXml)).toHaveLength(60);
 await press('Next year →');expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)![0])).toContain('year=2027');
 await press('← Previous year');
 await press('2026-11-09 New Moon');expect(onSelect).toHaveBeenCalledWith('2026-11-09');
 await press('Next month →');expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)![0])).toContain('month=12');
 await press('← Previous month');expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)![0])).toContain('month=11');
});

test('navigation cards stay uncluttered and rune casting shares the complete result only',async()=>{
 const {ContentActions}=require('../src/components/ContentActions');
 await render(<ExploreScreen route={{params:{}}} navigation={{goBack:jest.fn()}}/>);
 expect(tree.root.findAllByType(IllustratedToolCard)).toHaveLength(18);
 for(const card of tree.root.findAllByType(IllustratedToolCard)){
  expect(card.findAllByType(ContentActions)).toHaveLength(0);
 }
 await act(async()=>tree.unmount());
 await render(<ExploreScreen route={{params:{tool:'runes'}}} navigation={{goBack:jest.fn()}}/>);
 expect(text()).toContain('Cast the Runes');
 expect(tree.root.findAllByType(ContentActions)).toHaveLength(0);
 const cast=tree.root.findAllByType(TouchableOpacity).find(x=>
  x.findAllByType(Text).some(t=>JSON.stringify(t.props.children).includes('Cast ')&&JSON.stringify(t.props.children).includes(' Runes'))
 );
 expect(cast).toBeDefined();
 await act(async()=>cast!.props.onPress());
 const shared=tree.root.findAllByType(ContentActions);
 expect(shared).toHaveLength(1);
 expect(shared[0].props.text).toContain('Question:');
 expect(shared[0].props.text).toContain('Interpretation:');
 expect(shared[0].props.text).toContain('Closing reflection:');
});

test('BaZi shares a PNG plus readable results and invitation, and saves the same full reading',async()=>{
 const {ContentActions}=require('../src/components/ContentActions');
 const {captureRef}=require('react-native-view-shot');const NativeShare=require('react-native-share').default;
 const reading={birth_year:1977,animal_sign:'Fire Snake',pillars:{day_master:{title:'Yin Earth Snake',domain:'Core Soul Identity & Spouse Palace'}}};
 await render(<ContentActions title="Chinese Zodiac & BaZi" value={reading} route="explore/bazi"/>);
 await press('Share complete Chinese Zodiac & BaZi');
 const send=()=>tree.root.findAllByType(TouchableOpacity).find(x=>x.props.accessibilityLabel==='Share full reading')!;
 expect(send().props.disabled).toBe(true);
 await act(async()=>{tree.root.findAllByType(Image).forEach(n=>n.props.onLoadEnd?.());tree.root.findAll(n=>typeof n.props.onLayout==='function').forEach(n=>n.props.onLayout({nativeEvent:{layout:{width:342,height:1400}}}))});
 expect(send().props.disabled).toBe(false);await press('Share full reading');
 expect(captureRef).toHaveBeenCalledWith(expect.anything(),expect.objectContaining({format:'png',snapshotContentContainer:true}));
 const payload=NativeShare.open.mock.calls[0][0];expect(payload.type).toBe('image/png');expect(payload.url).toMatch(/^file:\/\/.+\.png$/);
 expect(payload.message).toContain('Zodiac animal: Fire Snake');expect(payload.message).toContain('Core Soul Identity');expect(payload.message).toContain('Get your own here: https://app.neurospicymystic.com/#explore/bazi');expect(payload.message).not.toMatch(/birth_year|day_master|[{}]/);
 await press('Close share preview');await press('Save complete Chinese Zodiac & BaZi to journal');
 const saved=JSON.parse((await AsyncStorage.getItem('sv_readings'))||'[]');expect(saved[0].title).toBe('Chinese Zodiac & BaZi');expect(saved[0].text).toContain('Core Soul Identity');
 await act(async()=>tree.unmount());await render(<JournalScreen navigation={{navigate:jest.fn()}}/>);await press('Saved Readings');expect(text()).toContain('Yin Earth Snake');
});


test('a failed journal write reports the error and never claims success',async()=>{
 const {ContentActions}=require('../src/components/ContentActions');
 const alert=jest.spyOn(Alert,'alert').mockImplementation(()=>{});
 (AsyncStorage.setItem as jest.Mock).mockRejectedValueOnce(new Error('Device storage full'));
 await render(<ContentActions title="My reflection" text="A meaningful reading" route="journal"/>);
 await press('Save complete My reflection to journal');
 expect(alert).toHaveBeenCalledWith('Could not add to journal',expect.any(String));
 expect(text()).not.toContain('Added to your journal.');
});


test('mobile Home restores the original portal cards alongside the six approved hero links',async()=>{
 const navigate=jest.fn();await render(<HomeScreen navigation={{navigate}}/>);
 const hero=tree.root.findByType(ReferenceHome);
 expect(hero.findAllByType(TouchableOpacity).map(n=>n.props.accessibilityLabel)).toEqual(['Daily Readings','Moon Cycles','Manifest','Natal Reading','Tarot','Journal']);
 for(const [label,screen,params] of [
  ['Daily','Learn',{daily:true}],['Spreads','Spreads',undefined],['Learn','Learn',undefined],['Birth','Explore',{tool:'natal'}],
  ['Moon Phase','Cosmos',undefined],['Numerology','Explore',{tool:'numbers'}],['Saved Readings','Journal',undefined],['Rituals','Explore',{tool:'rituals'}],
  ['Trust Your Gut','Spreads',{favorite:'Trust Your Gut'}],['At a Crossroads','Spreads',{favorite:'At a Crossroads'}],['The Next Phase','Spreads',{favorite:'The Next Phase'}],['Reset Your Energy','Spreads',{favorite:'Reset Your Energy'}],['Grounding','Spreads',{favorite:'Grounding'}],
 ] as const){await press(label);expect(navigate.mock.calls.at(-1)[0]).toBe(screen);if(params)expect(navigate.mock.calls.at(-1)[1]).toEqual(params);}
 expect(tree.root.findAllByType(Image).some(n=>n.props.source===require('../assets/home-light-portal.png'))).toBe(true);
});

test('iPhone Home reserves the bottom safe area for both scrolling and the fixed dock',async()=>{
 jest.spyOn(require('react-native'),'useWindowDimensions').mockReturnValue({width:390,height:844,scale:3,fontScale:1});
 jest.spyOn(SafeArea,'useSafeAreaInsets').mockReturnValue({top:47,bottom:34,left:0,right:0});
 await render(<App/>);
 const scroll=tree.root.findAllByType(ScrollView).find(n=>n.props.contentContainerStyle)!;
 expect(StyleSheet.flatten(scroll.props.contentContainerStyle).paddingBottom).toBeGreaterThanOrEqual(138);
 expect(scroll.props.scrollIndicatorInsets.bottom).toBe(122);
 const dock=tree.root.findAllByType(View).find(n=>{const v=StyleSheet.flatten(n.props.style);return v?.position==='absolute'&&v?.height===88&&v?.bottom===34});
 expect(dock).toBeDefined();
});

test('desktop Home retains its existing composition and scroll spacing',async()=>{
 jest.spyOn(require('react-native'),'useWindowDimensions').mockReturnValue({width:1024,height:900,scale:1,fontScale:1});
 jest.spyOn(SafeArea,'useSafeAreaInsets').mockReturnValue({top:0,bottom:34,left:0,right:0});
 await render(<HomeScreen navigation={{navigate:jest.fn()}}/>);
 expect(tree.root.findAllByType(IllustratedCard)).toHaveLength(0);
 const scroll=tree.root.findAllByType(ScrollView).find(n=>n.props.contentContainerStyle)!;expect(StyleSheet.flatten(scroll.props.contentContainerStyle).paddingBottom).toBe(110);
 expect(tree.root.findByType(ReferenceHome).findAllByType(TouchableOpacity)).toHaveLength(6);
});

test('13-month calendar converts a chosen date, browses Month 13 and exposes Year Day',async()=>{
 const normal=require('./fixtures/equinoxCalendar.json'),last=require('./fixtures/equinoxMonth13.json'),extra=require('./fixtures/equinoxYearDay.json');
 const onResult=jest.fn();
 globalThis.fetch=jest.fn().mockImplementation(async(url:string)=>({ok:true,json:async()=>url.includes('2027-03-19')?extra:url.includes('month=13')?last:normal}));
 await render(<EquinoxCalendar onResult={onResult}/>);
 const input=()=>tree.root.findAllByType(TextInput).find(n=>n.props.accessibilityLabel==='Calendar Gregorian date')!;
 await act(async()=>input().props.onChangeText('2026-11-12'));await press('Show calendar');
 expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)[0])).toContain('/calendar-13-month?date=2026-11-12');
 expect(text()).toContain('Month 9, Day 14');
 expect(tree.root.findAllByType(TouchableOpacity).filter(n=>/^Month 9, Day /.test(n.props.accessibilityLabel))).toHaveLength(28);
 await press('Month 13');expect(onResult.mock.calls.at(-1)[0].month_number).toBe(13);
 await press('Year Day · 2027-03-19');expect(text()).toContain('Year Day · Equinox year 2026');
 expect(input().props.value).toBe('2027-03-19');
});

test('calendar shows backend validation errors instead of a fabricated conversion',async()=>{
 globalThis.fetch=jest.fn().mockResolvedValue({ok:false,json:async()=>({detail:'Enter a valid Gregorian date (YYYY-MM-DD).'})});
 await render(<EquinoxCalendar onResult={jest.fn()}/>);await press('Show calendar');
 expect(text()).toContain('Enter a valid Gregorian date');
 expect(tree.root.findAllByType(TouchableOpacity).filter(n=>/^Month \d+, Day /.test(n.props.accessibilityLabel))).toHaveLength(0);
});

test('native astrocartography collects exact birth details and requests a personal map',async()=>{
 const result=require('./fixtures/astrocartography.json');const place={place_id:'5142056',label:'Utica, New York, United States',timezone:'America/New_York'};
 globalThis.fetch=jest.fn().mockImplementation(async(url:string)=>({ok:true,json:async()=>url.includes('/locations/countries')?{countries:[{code:'US',name:'United States'}]}:url.includes('/locations/regions')?{regions:[{code:'NY',name:'New York'}]}:url.includes('/locations/cities')?{places:[place]}:result}));
 await render(<ExploreScreen route={{params:{tool:'astro'}}} navigation={{goBack:jest.fn()}}/>);
 expect(text()).not.toContain('Destination city');
 const fill=async(label:string,value:string)=>act(async()=>tree.root.findAllByType(TextInput).find(n=>n.props.accessibilityLabel===label)!.props.onChangeText(value));
 await fill('Birth date YYYY-MM-DD','1996-11-05');await press('Hour (AM/PM)');await press('Select 2 PM');await press('Minutes');await press('Select 30');await press('City of birth');await press('Select '+place.label);await press('Career & visibility');await press('Create my astrocartography map');
 const [url,options]=(globalThis.fetch as jest.Mock).mock.calls.at(-1)!;
 expect(url).toContain('/astrology/astrocartography');expect(options.method).toBe('POST');
 expect(JSON.parse(options.body)).toMatchObject({birth_date:'1996-11-05',birth_time:'02:30',birth_period:'PM',place_id:'5142056',focus:'career'});
 expect(tree.root.findAllByType(SvgXml).some(n=>n.props.xml.includes('astro-line'))).toBe(true);
 expect(text()).toContain('Places to explore for');
});

test('native world map planet and angle layers respond to selection and zoom',async()=>{
 await render(<AstrocartographyReport result={require('./fixtures/astrocartography.json')}/>);
 const map=()=>tree.root.findAllByType(SvgXml).find(n=>n.props.xml.includes('astro-line'))!;
 const width=map().props.width;await press('Sun');await press('IC');
 expect(map().props.xml).toContain('<g data-planet="Venus" opacity=".12"');
 expect(map().props.xml).toContain('opacity=".08"');
 expect(text()).toContain('Lower culmination: home');
 await press('Zoom in');expect(map().props.width).toBeGreaterThan(width);
});

test('native map tap reads a real crossing and includes the three-pass guide',async()=>{
 const result=require('./fixtures/astrocartography.json');
 await render(<AstrocartographyReport result={result}/>);
 const point=result.crossings.find((p:any)=>p.planet_a==='Sun'&&p.planet_b==='Jupiter');
 const map=tree.root.findAllByType(SvgXml).find(n=>n.props.xml.includes('astro-line'))!;
 const target=tree.root.findAllByType(TouchableOpacity).find(n=>n.props.accessibilityLabel==='Inspect map location')!;
 await act(async()=>target.props.onPress({nativeEvent:{locationX:(point.longitude+180)*map.props.width/360,locationY:(90-point.latitude)*map.props.height/180}}));
 expect(text()).toContain('Crossing: Sun');expect(text()).toContain('Every line within 500 km');
 expect(text()).toContain('How to read your astrocartography map: three passes');
 expect(text()).toContain('Relocation chart');expect(text()).toContain('Astronomy Engine');
 expect(tree.root.findAllByType(SvgXml).some(n=>n.props.xml.includes('r="8"'))).toBe(true);
});

test('native map city lookup inspects the chosen country and its full nearby-line list',async()=>{
 const place={place_id:'2988507',label:'Paris, Île-de-France, France',latitude:48.85341,longitude:2.3488};
 globalThis.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>({places:[place]})});
 await render(<AstrocartographyReport result={require('./fixtures/astrocartography.json')}/>);
 const input=tree.root.findAllByType(TextInput).find(n=>n.props.accessibilityLabel==='Map city search')!;
 await act(async()=>input.props.onChangeText('Paris'));await press('Find places');await press(place.label);
 expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)[0])).toContain('/astrocartography/places?query=Paris');
 expect(text()).toContain('Every line within 500 km');
 expect(text()).toContain('48.853');
});
