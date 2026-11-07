import React from 'react';
import {StyleSheet,Text,View,useWindowDimensions} from 'react-native';
import {CardArtName,IllustratedCard} from './IllustratedCard';

type LearningArt = Extract<CardArtName, 'learn_progress'|'learn_major_arcana'|'learn_minor_arcana'|'learn_card_meanings'|'learn_reversed_cards'>;
type Props = {asset:LearningArt;label:string;completed:number;total:number;onPress:()=>void};

/** Opaque native overlays hide the sample numbers and bars painted into the PNGs. */
export function LearningCard({asset,label,completed,total,onPress}:Props){
  const {width}=useWindowDimensions();
  const scale=Math.min(width-32,580)/600;
  const percent=total?Math.min(100,Math.round(completed/total*100)):0;
  const journey=asset==='learn_progress';
  const left=asset==='learn_minor_arcana'?'39%':asset==='learn_reversed_cards'?'34%':'33%';
  const status=journey?`${percent}% complete`:`${completed} / ${total} cards`;
  return <IllustratedCard asset={asset} label={`${label}: ${status}`} onPress={onPress}>
    {journey?<>
      <View pointerEvents="none" style={styles.journeyLabel}><Text style={[styles.count,{fontSize:22*scale}]}>{status}</Text></View>
      <View pointerEvents="none" style={styles.journeyTrack}><View style={[styles.fill,{width:`${percent}%`}]} /></View>
    </>:<View pointerEvents="none" style={[styles.moduleOverlay,{left}]}>
      <View style={styles.moduleTrack}><View style={[styles.fill,{width:`${percent}%`}]} /></View>
      <Text style={[styles.count,{fontSize:22*scale}]}>{status}</Text>
    </View>}
  </IllustratedCard>;
}

const styles=StyleSheet.create({
  count:{color:'#3A156B',fontWeight:'800'},
  journeyLabel:{position:'absolute',left:'68%',right:'3%',top:'17%',height:'32%',backgroundColor:'#FCE9F1',justifyContent:'center',alignItems:'flex-end'},
  journeyTrack:{position:'absolute',left:'17%',right:'3%',top:'52%',height:'25%',borderRadius:24,backgroundColor:'#E3CBD7',borderWidth:2,borderColor:'#FFF2FC',overflow:'hidden'},
  fill:{height:'100%',backgroundColor:'#F71C9F',borderRadius:24},
  moduleOverlay:{position:'absolute',right:'3%',top:'66%',bottom:'7%',backgroundColor:'#FCE9F1',flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:6},
  moduleTrack:{height:'52%',flex:1,borderRadius:24,backgroundColor:'#E3CBD7',overflow:'hidden'},
});
