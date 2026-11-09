import React from 'react';
import TestRenderer,{act,ReactTestRenderer} from 'react-test-renderer';
import {Image,Text,TextInput,TouchableOpacity,Linking} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import App,{HomeScreen,SpreadsScreen,LearnScreen,JournalScreen,ExploreScreen,CosmosScreen} from '../App';
import {IllustratedCard,UI_CARD_IMAGES} from '../src/components/IllustratedCard';
import {LearningCard} from '../src/components/LearningCard';
import {NativeChartReport,NativeMoonCalendar} from '../src/components/CosmicTools';
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
    ['Learn','Learn',undefined],['Spreads','Spreads',undefined],['Daily','Learn',{daily:true}],
    ['Numerology','Explore',{tool:'life'}],['Moon Phase','Cosmos',undefined],
    ['Saved Readings','Journal',undefined],['Birth','Explore',{tool:'natal'}],
  ] as const){
    await press(label);
    expect(navigate.mock.calls.at(-1)?.[0]).toBe(route);
    if(params)expect(navigate.mock.calls.at(-1)?.[1]).toEqual(params);
  }
});

test('all 24 panels have concrete local sources and preserve their intrinsic aspect ratio',async()=>{
  expect(Object.keys(UI_CARD_IMAGES)).toHaveLength(24);
  const onPress=jest.fn();
  await render(<IllustratedCard asset="home_daily_card" width={300} label="Daily card" onPress={onPress}/>);
  expect(tree.root.findByType(Image).props.style).toEqual({width:300,height:125});
  await press('Daily card');
  expect(onPress).toHaveBeenCalledTimes(1);
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

test('journal PNG actions save a reflection and open saved readings',async()=>{
  await render(<JournalScreen navigation={{navigate:jest.fn()}}/>);
  await press("Open today's journal");
  await act(async()=>tree.root.findByType(TextInput).props.onChangeText('A calmer day.'));
  const save=tree.root.findAllByType(TouchableOpacity).find(x=>x.findAllByType(Text).some(t=>t.props.children==='Save reflection ✎'))!;
  await act(async()=>save.props.onPress());
  expect(AsyncStorage.setItem).toHaveBeenCalledWith('sv_journal',expect.stringContaining('A calmer day.'));
  await press('Saved Readings');
  expect(text()).toContain('No saved readings yet.');
});

test('real tab navigator exposes six destinations and opens the independent learning and spreads screens',async()=>{
  await render(<App/>);
  const output=JSON.stringify(tree.toJSON());
  for(const label of ['Home','Spreads','Learn','Cosmos','Explore','Journal'])expect(output).toContain(label);
  for(const [label,asset] of [['Learn','learn_header'],['Spreads','spreads_header']] as const){
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
  ['houses','/astrology/houses','GET'],['asteroids','/astrology/asteroids','GET'],
  ['astro','/astrology/astrocartography','GET'],['calendar','/astrology/lunar-calendar/1','GET'],
  ['life','/synastry/life-path','POST'],['numbers','/synastry/numerology-lessons','GET'],
  ['love','/synastry/compatibility','POST'],['sound','/rituals/frequencies','GET'],
  ['rituals','/rituals/search','GET'],['shadow','/wellness/shadow-prompts','GET'],
  ['runes','/divination/runes/cast','POST'],['pendulum','/divination/pendulum','POST'],
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
  if(date)expect(JSON.parse(options.body)).toMatchObject(tool==='life'||tool==='bazi'?{birth_year:1996,birth_month:11,birth_day:5}:{birth_date:'1996-11-05',birth_time:'12:00'});
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


test.each(['natal','moon'])('native %s resolves a city and submits local birth time without coordinate fields',async(tool)=>{
 const place={place_id:'5142056',label:'Utica, New York, United States',timezone:'America/New_York'};
 globalThis.fetch=jest.fn().mockImplementation(async(url:string)=>({ok:true,json:async()=>url.includes('/locations/search')?{places:[place]}:{emoji:'🌘',natal_moon_phase:'Waning Crescent',illumination_percentage:21,description:'Birth Moon',moon_position:'Virgo 2°',birth_local_time:'1996-11-05T14:30:00-05:00',location:place}}));
 await render(<ExploreScreen route={{params:{tool}}} navigation={{goBack:jest.fn()}}/>);
 const fill=async(label:string,value:string)=>act(async()=>tree.root.findAllByType(TextInput).find(x=>x.props.accessibilityLabel===label)!.props.onChangeText(value));
 await fill('Name (optional)','Mystic');await fill('Birth date YYYY-MM-DD','1996-11-05');await fill('Hour (0–23)','14');await fill('Minutes (0–59)','30');await fill('State / province','NY');await fill('City of birth','Utica');
 expect(text()).not.toContain('Birth latitude');expect(text()).not.toContain('Birth longitude');
 await press('Find my birth city');expect(String((globalThis.fetch as jest.Mock).mock.calls[0][0])).toContain('city=Utica');await press('Select '+place.label);
 await press('Sidereal (Lahiri)');if(tool==='natal')await press('Traditional (7 planets)');await press(tool==='moon'?'Find my natal Moon':'Create my birth chart');
 const [url,options]=(globalThis.fetch as jest.Mock).mock.calls.at(-1)!;
 expect(url).toContain('/astrology/'+(tool==='moon'?'moon-phase':'natal-chart'));
 expect(JSON.parse(options.body)).toMatchObject({name:'Mystic',birth_date:'1996-11-05',birth_time:'14:30',place_id:'5142056',zodiac:'sidereal',rulership:tool==='natal'?'traditional':'modern',chart_system:'natal'});
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


test('painted Career filter finds the API career spreads without covering its icons',async()=>{
 const catalog=require('../../backend/data/master_data.json').masterSpreadsData;
 expect(catalog.filter((s:any)=>matchesVibe(s,'Career')).map((s:any)=>s.id)).toEqual(expect.arrayContaining(['career-shift','financial-healing']));
 globalThis.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>({spreads:catalog})});
 await render(<SpreadsScreen route={{params:{}}}/>);await press('Filter by Career');
 expect(text()).toContain('Career Shift');
 const selected=tree.root.findAllByType(TouchableOpacity).find(x=>x.props.accessibilityLabel==='Filter by Career')!;
 expect(selected.props.accessibilityState.selected).toBe(true);
 expect(selected.findAllByType(Text)).toHaveLength(0);
});


test('monthly Moon calendar stays in the Moon section and supports day and month selection',async()=>{
 const calendar=require('./fixtures/moonCalendar.json');const onSelect=jest.fn();
 globalThis.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>calendar});
 await render(<NativeMoonCalendar timezone="UTC" zodiac="tropical" currentDate="2026-11-08" selectedDate="" onSelect={onSelect}/>);
 expect(text()).toContain('Monthly Moon Phases');expect(text()).toContain('November 2026');
 expect(text()).toContain('Day-by-day lunar calendar');expect(text()).toContain('Heart, aorta');expect(text()).toContain('Ask your surgical team');
 expect(tree.root.findAllByType(SvgXml)).toHaveLength(30);
 await press('Next year →');expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)![0])).toContain('year=2027');
 await press('← Previous year');
 await press('2026-11-09 New Moon');expect(onSelect).toHaveBeenCalledWith('2026-11-09');
 await press('Next month →');expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)![0])).toContain('month=12');
 await press('← Previous month');expect(String((globalThis.fetch as jest.Mock).mock.calls.at(-1)![0])).toContain('month=11');
});
