import React from 'react';
import {CardArtName,IllustratedCard} from './IllustratedCard';
type LearningArt=Extract<CardArtName,'learn_progress'|'learn_major_arcana'|'learn_minor_arcana'|'learn_card_meanings'|'learn_reversed_cards'>;
type Props={asset:LearningArt;label:string;completed:number;total:number;onPress:()=>void};
/** Progress is a real native control; no numbers or bars are painted into an image. */
export function LearningCard({asset,label,completed,total,onPress}:Props){
 const percent=total?Math.min(100,Math.round(completed/total*100)):0;
 return <IllustratedCard asset={asset} label={`${label}: ${asset==='learn_progress'?percent+'% complete':completed+' / '+total+' cards'}`} onPress={onPress} progress={{completed,total}}/>;
}
