import React from 'react';
import {StyleSheet,Text,View,useWindowDimensions} from 'react-native';
import {CardArtName,IllustratedCard} from './IllustratedCard';

type LearningArt = Extract<CardArtName, 'learn_progress'|'learn_major_arcana'|'learn_minor_arcana'|'learn_card_meanings'|'learn_reversed_cards'>;
type Props = {asset:LearningArt;label:string;completed:number;total:number;onPress:()=>void};

/** Opaque native overlays hide the sample numbers and bars painted into the PNGs. */
export function LearningCard({asset,label,completed,total,onPress}:Props){
  const {width}=useWindowDimensions();
  const scale=Math.min(width-24,580)/600;
  const percent=total?Math.min(100,Math.round(completed/total*100)):0;
  const journey=asset==='learn_progress';
  const layouts={learn_major_arcana:[34,4,65,13,45],learn_minor_arcana:[35,6,65,16,41],learn_card_meanings:[38,3,63,16,52],learn_reversed_cards:[41,4,64,13,45]};
  const [left,right,top,bottom,track]=journey?[0,0,0,0,0]:layouts[asset];
  const status=journey?`${percent}% complete`:`${completed} / ${total} cards`;
  return <IllustratedCard asset={asset} label={`${label}: ${status}`} onPress={onPress}>
    {journey?<>
      <View pointerEvents="none" style={styles.journeyLabel}><Text style={[styles.count,{fontSize:22*scale}]}>{status}</Text></View>
      <View pointerEvents="none" style={styles.journeyTrack}><View style={[styles.fill,{width:`${percent}%`}]} /></View>
    </>:<View pointerEvents="none" style={[styles.moduleOverlay,{left:`${left}%`,right:`${right}%`,top:`${top}%`,bottom:`${bottom}%`}]}>
      <View style={[styles.moduleTrack,{width:`${track}%`}]}><View style={[styles.fill,{width:`${percent}%`}]} /></View>
      <Text style={[styles.count,{fontSize:22*scale,flex:1,textAlign:'right'}]}>{status}</Text>
    </View>}
  </IllustratedCard>;
}

const styles=StyleSheet.create({
  count:{color:'#3A156B',fontWeight:'800'},
  journeyLabel:{position:'absolute',left:'70%',right:'3%',top:'17%',height:'32%',backgroundColor:'#FCE9F1',justifyContent:'center',alignItems:'flex-end'},
  journeyTrack:{position:'absolute',left:'17%',right:'3%',top:'52%',height:'25%',borderRadius:24,backgroundColor:'#E3CBD7',borderWidth:2,borderColor:'#FFF2FC',overflow:'hidden'},
  fill:{height:'100%',backgroundColor:'#F71C9F',borderRadius:24},
  moduleOverlay:{position:'absolute',backgroundColor:'#FCE9F1',flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:6,borderRadius:7},
  moduleTrack:{height:'52%',borderRadius:24,backgroundColor:'#E3CBD7',overflow:'hidden'},
});
