import React from 'react';
import {View,Text,TouchableOpacity,useWindowDimensions} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
/** Live text and controls stay sharp; no screenshot supplies this filter. */
export function VibeFilter({value,onChange}:{value:string,onChange:(value:string)=>void}){
 const {width}=useWindowDimensions();const w=Math.min(width-24,580);
 return <LinearGradient colors={['#ffe5ef','#f7d5f5']} style={{width:w,padding:14,borderRadius:24,borderWidth:2,borderColor:'#fff',marginBottom:18}}><Text style={{color:'#361147',fontWeight:'900',fontSize:21,marginBottom:12}}>Filter by Vibe</Text><View style={{flexDirection:'row',gap:6}}>{['All','Love','Career','Growth'].map((label,i)=><TouchableOpacity key={label} accessibilityRole="button" accessibilityLabel={'Filter by '+label} accessibilityState={{selected:value===label}} onPress={()=>onChange(label)} style={{flex:1,justifyContent:'center',alignItems:'center',paddingVertical:11,paddingHorizontal:3,borderRadius:24,borderWidth:2,borderColor:'#fff',backgroundColor:value===label?'#ed138d':'#fff8fd'}}><Text style={{color:value===label?'#fff':'#401251',fontSize:w<400?12:16,fontWeight:'800'}}>{label} {['✦','♡','💼','🌱'][i]}</Text></TouchableOpacity>)}</View></LinearGradient>;
}
