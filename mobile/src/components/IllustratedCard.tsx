/** Original art, live labels and scalable decoration shared by all 24 panels. */
import React,{createContext,useContext} from 'react';
import {Image,View,Text,TouchableOpacity,useWindowDimensions,StyleSheet,StyleProp,ViewStyle} from 'react-native';
import {ClearGlassSurface} from './ClearGlassSurface';
import catalog from '../data/uiPanels.json';
import illustrationBindings from '../data/illustrationBindings.json';
export const UI_PANELS=catalog;
export const HomePaletteContext=createContext(false);
export type CardArtName=keyof typeof catalog;
export const ILLUSTRATION_PACKS={
 cosmic:require('../../assets/illustrations/cosmic.png'),
 study:require('../../assets/illustrations/study.png'),
 journal:require('../../assets/illustrations/journal.png'),
 ritual:require('../../assets/illustrations/ritual.png'),
};
export function PanelIllustration({pack,cell,size=110}:{pack:keyof typeof ILLUSTRATION_PACKS,cell:number,size?:number}){
 return <View pointerEvents="none" accessible={false} style={{width:size,height:size,overflow:'hidden',flexShrink:0}}><Image source={ILLUSTRATION_PACKS[pack]} accessible={false} resizeMode="stretch" style={{position:'absolute',width:size*2,height:size*2,left:-(cell%2)*size,top:-Math.floor(cell/2)*size}}/></View>;
}
export function SpreadIllustration({category,size=68}:{category:string,size?:number}){
 const art=illustrationBindings.spreads[category as keyof typeof illustrationBindings.spreads]||illustrationBindings.spreads.default;
 return <PanelIllustration pack={art.pack as keyof typeof ILLUSTRATION_PACKS} cell={art.cell} size={size}/>;
}
export function IllustratedToolCard({tool,title,width,onPress}:{tool:string,title:string,width:number,onPress:()=>void}){
 const art=illustrationBindings.tools[tool as keyof typeof illustrationBindings.tools];
 if(!art)throw Error('Missing tool illustration: '+tool);
 return <TouchableOpacity accessibilityRole="button" accessibilityLabel={title} onPress={onPress} style={{width,marginBottom:16}}><ClearGlassSurface radius={25} style={{minHeight:260,padding:14,paddingBottom:42,gap:14,alignItems:'center'}}><PanelIllustration pack={art.pack as keyof typeof ILLUSTRATION_PACKS} cell={art.cell} size={104}/><Text style={{alignSelf:'stretch',color:'#fff9fe',fontSize:tool==='natal'?24:23,lineHeight:28,fontWeight:'800'}}>{title}</Text><View accessible={false} style={[st.arrow,{position:'absolute',right:12,bottom:12}]}><Text style={{color:'#fff9fe',fontSize:28,lineHeight:29}}>›</Text></View></ClearGlassSurface></TouchableOpacity>;
}
type Props={asset:CardArtName;width?:number;label?:string;onPress?:()=>void;style?:StyleProp<ViewStyle>;children?:React.ReactNode;progress?:{completed:number,total:number};meta?:string};
export function IllustratedCard({asset,width,label,onPress,style,children,progress,meta}:Props){
 const {width:screenWidth}=useWindowDimensions();const w=width??Math.min(screenWidth-24,580);
 const light=useContext(HomePaletteContext);
 const p=catalog[asset],theme={ink:light?'#35174d':'#fff9fe',accent:light?'#603282':'#fff'};const compact=w<260,header=p.kind==='header',random=p.kind==='randomize';
 const percent=progress?Math.max(0,Math.min(100,Math.round(progress.completed/Math.max(progress.total,1)*100))):0;
 const size=compact?104:random?72:header?112:106;
 const content=<ClearGlassSurface radius={25} style={[st.surface,{flexDirection:compact?'column':header?'row-reverse':'row',minHeight:compact?250:random?112:156,padding:compact?14:16,gap:compact?12:14}]}>
  <Text accessible={false} style={st.sparkle}>✦</Text>
  <PanelIllustration pack={p.pack as keyof typeof ILLUSTRATION_PACKS} cell={p.cell} size={size}/>
  <View style={{flex:compact?undefined:1,alignSelf:compact?'stretch':undefined,gap:8,paddingBottom:compact&&onPress?24:0}}>
   <Text style={{color:theme.ink,fontWeight:header||random?'400':'900',fontFamily:header||random?'KaushanScript-Regular':undefined,fontSize:compact?23:header?37:random?27:26,letterSpacing:header?0:-.5,lineHeight:compact?26:header?45:31}}>{p.title}</Text>
   <Text style={{color:theme.ink,fontSize:compact?13:15,lineHeight:compact?19:22,fontWeight:'500'}}>{p.description}</Text>
   {meta?<Text style={{color:theme.ink,fontSize:13,fontWeight:'800',lineHeight:19}}>{meta}</Text>:null}
   {progress?<View accessibilityRole="progressbar" accessibilityLabel={p.title+' progress'} accessibilityValue={{min:0,max:progress.total,now:progress.completed}} style={{gap:7,marginTop:4}}><View style={st.track}><View style={[st.fill,{width:`${percent}%`}]}/></View><Text style={{color:theme.ink,fontSize:13,fontWeight:'800'}}>{p.kind==='progress'?percent+'% complete · ':''}{progress.completed} / {progress.total} cards</Text></View>:null}
   {children}
  </View>
  {onPress&&!header?<View accessible={false} style={[st.arrow,compact?{position:'absolute',right:12,bottom:12}:null]}><Text style={{fontSize:32,color:theme.accent,fontWeight:'800',lineHeight:30}}>›</Text></View>:null}
 </ClearGlassSurface>;
 const outer=[st.outer,{width:w},style];
 return onPress?<TouchableOpacity accessibilityRole="button" accessibilityLabel={label||p.title} onPress={onPress} style={outer}>{content}</TouchableOpacity>:<View accessibilityLabel={label||p.title} style={outer}>{content}</View>;
}
const st=StyleSheet.create({outer:{marginBottom:16,borderRadius:27,borderWidth:0,borderColor:'transparent',shadowColor:'#32104b',shadowOffset:{width:0,height:6},shadowOpacity:.25,shadowRadius:8,elevation:5},surface:{alignItems:'center',borderRadius:25,borderWidth:1,borderColor:'#ffffff80',overflow:'hidden'},sparkle:{position:'absolute',top:7,right:'12%',color:'#ffe67c',fontSize:23,opacity:.8},arrow:{width:30,height:30,borderRadius:16,borderWidth:2,borderColor:'#fff',backgroundColor:'rgba(255,255,255,.05)',alignItems:'center',justifyContent:'center',flexShrink:0},track:{height:13,borderRadius:12,borderWidth:2,borderColor:'#fff9',backgroundColor:'#c19eb74a',overflow:'hidden'},fill:{height:'100%',backgroundColor:'#ec138c',borderRadius:10}});
