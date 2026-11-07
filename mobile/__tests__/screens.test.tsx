import React from 'react';
import TestRenderer,{act,ReactTestRenderer} from 'react-test-renderer';
import {Image,Text,TextInput,TouchableOpacity} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import App,{HomeScreen,SpreadsScreen,LearnScreen,JournalScreen} from '../App';
import {IllustratedCard,UI_CARD_IMAGES} from '../src/components/IllustratedCard';
import {LearningCard} from '../src/components/LearningCard';

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
    ['Numerology','Explore',{tool:'life'}],['Moon Phase','Explore',{tool:'moon'}],
    ['Saved Readings','Journal',undefined],['Cosmos','Cosmos',undefined],
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
