import React from 'react';
import {Image,Text,TouchableOpacity,View,useWindowDimensions} from 'react-native';
import {UI_CARD_IMAGES} from './IllustratedCard';

/** Transparent touch targets preserve the supplied icons and lettering. */
export function PaintedVibeFilter({value,onChange}:{value:string,onChange:(s:string)=>void}){
 const {width}=useWindowDimensions();const w=Math.min(width-24,580);
 const image=Image.resolveAssetSource(UI_CARD_IMAGES.spreads_filters);const h=w*image.height/image.width;
 const bounds=[[2,21],[24,22],[47,24],[73,25]];
 return <View style={{width:w,height:h,marginBottom:13}}>
  <Image source={UI_CARD_IMAGES.spreads_filters} style={{width:w,height:h}} resizeMode="contain" accessibilityLabel="Filter by Vibe"/>
  {['All','Love','Career','Growth'].map((label,i)=><TouchableOpacity key={label} accessibilityRole="button" accessibilityLabel={'Filter by '+label} accessibilityState={{selected:value===label}} onPress={()=>onChange(label)} style={{position:'absolute',left:w*bounds[i][0]/100,width:w*bounds[i][1]/100,top:h*.4,height:h*.43,borderRadius:h*.22,borderWidth:value===label&&i!==0?2:0,borderColor:'#f7199f',backgroundColor:value===label&&i!==0?'#f7199f18':'transparent'}}>
   {i===0&&value!=='All'?<View pointerEvents="none" style={{flex:1,borderRadius:h*.22,backgroundColor:'#fff1f9',borderWidth:2,borderColor:'#fff',justifyContent:'center',alignItems:'center'}}><Text style={{fontSize:w*.045,fontWeight:'800',color:'#5e1d79'}}>All</Text></View>:null}
  </TouchableOpacity>)}
 </View>;
}
