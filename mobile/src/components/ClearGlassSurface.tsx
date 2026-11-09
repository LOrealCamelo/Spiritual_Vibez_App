/** Clear glass keeps the scene visible; no blur view or frosted fill is used. */
import React from 'react';
import {StyleSheet,View,StyleProp,ViewStyle} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
type Props={children?:React.ReactNode;style?:StyleProp<ViewStyle>;radius?:number;pointerEvents?:'none'|'auto'|'box-none'|'box-only'};
export function ClearGlassSurface({children,style,radius=24,pointerEvents}:Props){
 return <View pointerEvents={pointerEvents} style={[styles.surface,{borderRadius:radius},style]}><LinearGradient pointerEvents="none" colors={['rgba(255,255,255,0.10)','rgba(255,255,255,0.015)','rgba(255,255,255,0.005)','rgba(255,255,255,0.07)']} locations={[0,.3,.7,1]} start={{x:0,y:0}} end={{x:1,y:1}} style={[StyleSheet.absoluteFillObject,{borderRadius:radius}]}/><View pointerEvents="none" style={[StyleSheet.absoluteFillObject,{borderRadius:radius,borderTopWidth:1,borderLeftWidth:1,borderBottomWidth:1,borderRightWidth:1,borderTopColor:'rgba(255,255,255,0.8)',borderLeftColor:'rgba(255,255,255,0.5)',borderBottomColor:'rgba(255,255,255,0.25)',borderRightColor:'rgba(255,255,255,0.35)'}]}/>{children}</View>;
}
const styles=StyleSheet.create({surface:{backgroundColor:'rgba(255,255,255,0.025)',borderWidth:1,borderColor:'rgba(255,255,255,0.45)',shadowColor:'#18072d',shadowOffset:{width:0,height:6},shadowOpacity:.2,shadowRadius:12,elevation:3}});
