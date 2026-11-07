/** Illustrated Spiritual Vibez cards - each image is a separate local PNG asset.
 *  Native accessibility and navigation remain in React Native; no Expo/WebView.
 */
import React from 'react';
import {Image,View,TouchableOpacity,useWindowDimensions,StyleProp,ViewStyle} from 'react-native';

export const UI_CARD_IMAGES = {
  'home_birth_chart': require('../../assets/ui_cards/home_birth_chart.png'),
  'home_daily_card': require('../../assets/ui_cards/home_daily_card.png'),
  'home_learn_tarot': require('../../assets/ui_cards/home_learn_tarot.png'),
  'home_shuffle_spread': require('../../assets/ui_cards/home_shuffle_spread.png'),
  'journal_header': require('../../assets/ui_cards/journal_header.png'),
  'journal_mood_checkin': require('../../assets/ui_cards/journal_mood_checkin.png'),
  'journal_moon_phase': require('../../assets/ui_cards/journal_moon_phase.png'),
  'journal_numerology': require('../../assets/ui_cards/journal_numerology.png'),
  'journal_rituals': require('../../assets/ui_cards/journal_rituals.png'),
  'journal_saved_readings': require('../../assets/ui_cards/journal_saved_readings.png'),
  'journal_today': require('../../assets/ui_cards/journal_today.png'),
  'learn_card_meanings': require('../../assets/ui_cards/learn_card_meanings.png'),
  'learn_header': require('../../assets/ui_cards/learn_header.png'),
  'learn_major_arcana': require('../../assets/ui_cards/learn_major_arcana.png'),
  'learn_minor_arcana': require('../../assets/ui_cards/learn_minor_arcana.png'),
  'learn_progress': require('../../assets/ui_cards/learn_progress.png'),
  'learn_quiz_me': require('../../assets/ui_cards/learn_quiz_me.png'),
  'learn_reversed_cards': require('../../assets/ui_cards/learn_reversed_cards.png'),
  'spreads_crossroads': require('../../assets/ui_cards/spreads_crossroads.png'),
  'spreads_filters': require('../../assets/ui_cards/spreads_filters.png'),
  'spreads_header': require('../../assets/ui_cards/spreads_header.png'),
  'spreads_next_phase': require('../../assets/ui_cards/spreads_next_phase.png'),
  'spreads_randomize': require('../../assets/ui_cards/spreads_randomize.png'),
  'spreads_trust_gut': require('../../assets/ui_cards/spreads_trust_gut.png'),
} as const;

export type CardArtName = keyof typeof UI_CARD_IMAGES;
type Props={asset:CardArtName;width?:number;label?:string;onPress?:()=>void;style?:StyleProp<ViewStyle>;children?:React.ReactNode};
export function IllustratedCard({asset,width,label,onPress,style,children}:Props){
  const {width:screenWidth}=useWindowDimensions();
  const w=width??Math.min(screenWidth-24,580);
  const source=UI_CARD_IMAGES[asset];
  const size=Image.resolveAssetSource(source);
  const h=w*size.height/size.width;
  const content=<><Image source={source} resizeMode="contain" style={{width:w,height:h}} accessible={!onPress&&!children} accessibilityLabel={label||asset} />{children}</>;
  if(onPress)return <TouchableOpacity accessibilityRole="button" accessibilityLabel={label||asset} onPress={onPress} style={[{width:w,height:h,marginBottom:10},style]}>{content}</TouchableOpacity>;
  return <View style={[{width:w,height:h,marginBottom:10},style]}>{content}</View>;
}
