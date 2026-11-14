/** SpiritualVibz Rune Sanctuary — modern reflective rune casting.
 * Shared 24-rune library with web; no external native packages required.
 * Animated toss and gentle haptic feedback, with accessible touch fallback.
 */
import React,{useEffect,useRef,useState} from 'react';
import {Animated,Easing,Linking,Text,TextInput,TouchableOpacity,View,Vibration,useWindowDimensions} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import {ContentActions} from './ContentActions';

const RuneLibrary=require('../content/rune-library');
type CastRune={id:number;name:string;symbol:string;historic:string;reversible:boolean;position:number;positionName:string;orientation:'upright'|'reversed';reading:{keywords:string[];meaning:string}};
type Piece={rune:CastRune;x:number;y:number;angle:number;faceUp:boolean;zone:string;neighbors:string[]};
const clothHeight=410;
const reduceMotion=false;
function Bone({piece,index,castVersion,onTap,highlight}:{piece:Piece;index:number;castVersion:number;onTap:(index:number)=>void;highlight:boolean}){
 const move=useRef(new Animated.Value(0)).current;
 useEffect(()=>{
  move.setValue(0);
  const animation=Animated.timing(move,{toValue:1,duration:800+index*65,easing:Easing.out(Easing.cubic),useNativeDriver:true});
  animation.start();
  return()=>animation.stop();
 },[castVersion,index,move]);
 const startX=piece.x, startY=clothHeight+16;
 const translateX=move.interpolate({inputRange:[0,1],outputRange:[0,startX]});
 const translateY=move.interpolate({inputRange:[0,1],outputRange:[startY,piece.y]});
 const rotation=move.interpolate({inputRange:[0,1],outputRange:[(index%2?270:-270)+'deg',piece.angle+'deg']});
 return <Animated.View style={{position:'absolute',left:0,top:0,transform:[{translateX},{translateY},{rotate:rotation}],zIndex:highlight?8:3}}>
  <TouchableOpacity accessibilityRole="button"
   accessibilityLabel={piece.faceUp?'View '+piece.rune.name:'Face-down rune; not interpreted'}
   onPress={()=>onTap(index)} style={{width:54,height:75,borderRadius:20,borderTopLeftRadius:28,borderBottomRightRadius:26,backgroundColor:piece.faceUp?'#F0DAB9':'#C4AB91',borderColor:highlight?'#9E4D89':'#9C7D64',borderWidth:highlight?3:2,alignItems:'center',justifyContent:'center',shadowColor:'#130D1D',shadowOpacity:.65,shadowRadius:8,elevation:6}}>
   <Text style={{fontSize:piece.faceUp?35:25,color:piece.faceUp?'#4C3042':'#E9D6C0',transform:[{rotate:piece.rune.orientation==='reversed'?'180deg':'0deg'}]}}>{piece.faceUp?piece.rune.symbol:'✦'}</Text>
  </TouchableOpacity>
 </Animated.View>;
}
export function RuneCastingExperience(){
 const {width:screenWidth}=useWindowDimensions();
 const clothWidth=Math.min(540,screenWidth-58);
 const [layout,setLayout]=useState<'daily'|'three'|'cross'|'handful'>('three');
 const [reversals,setReversals]=useState(false);
 const [intention,setIntention]=useState('');
 const [pieces,setPieces]=useState<Piece[]>([]);
 const [castVersion,setCastVersion]=useState(0);
 const [rattling,setRattling]=useState(false);
 const [highlight,setHighlight]=useState<number|null>(null);
 const [message,setMessage]=useState('Your runes are ready.');
 const isGathered=useRef(false);
 const animateRattle=useRef(new Animated.Value(0)).current;
 const layoutInfo=RuneLibrary.LAYOUTS[layout];
 useEffect(()=>{
  let loop:Animated.CompositeAnimation|undefined;
  if(rattling){
   loop=Animated.loop(Animated.sequence([
    Animated.timing(animateRattle,{toValue:1,duration:85,useNativeDriver:true}),
    Animated.timing(animateRattle,{toValue:-1,duration:85,useNativeDriver:true})
   ]));loop.start();
  }else{animateRattle.stopAnimation();animateRattle.setValue(0)}
  return()=>loop?.stop();
 },[animateRattle,rattling]);
 const throwRunes=()=>{
  setRattling(false);isGathered.current=false;
  const picked:CastRune[]=RuneLibrary.cast(layout,reversals);
  const count=picked.length;
  const xs=clothWidth-62,ys=clothHeight-85;
  const cols=count<=3?count:count===5?3:4,rows=Math.ceil(count/cols);
  const next:Piece[]=picked.map((r,i)=>{
   const col=i%cols,row=Math.floor(i/cols);
   const gridX=cols===1?xs*.48:(col+.5)/cols*xs;
   const gridY=(row+.65)/Math.max(1,rows)*ys;
   const x=Math.max(8,Math.min(xs,gridX+(Math.random()-.5)*38));
   const y=Math.max(30,Math.min(ys,gridY+(Math.random()-.5)*40));
   return {rune:r,x,y,angle:Math.floor((Math.random()-.5)*75),faceUp:layout!=='handful'||Math.random()>.3,zone:'',neighbors:[]};
  });
  if(next.every(p=>!p.faceUp))next[0].faceUp=true;
  for(const p of next){
   const cx=xs/2,cy=ys/2,distance=Math.hypot((p.x-cx)/xs,(p.y-cy)/ys);
   p.zone=distance<.24?'near the center':distance>.42?'toward the outer edge':'between center and edge';
   p.neighbors=next.filter(other=>other!==p&&other.faceUp&&Math.hypot(other.x-p.x,other.y-p.y)<105).map(other=>other.rune.name);
  }
  setPieces(next);setCastVersion(c=>c+1);setHighlight(null);
  setMessage('Your runes have landed. Tap a rune to explore its meaning.');
  Vibration.vibrate(12);
 };
 const beginHold=()=>{isGathered.current=true;setRattling(true);setMessage('Gently rattle the rune bones in your hand…');Vibration.vibrate(8)};
 const release=()=>{if(isGathered.current)throwRunes()};
 const switchLayout=(key:'daily'|'three'|'cross'|'handful')=>{setLayout(key);setPieces([]);setHighlight(null);setMessage('Choose a question and cast when ready.')};
 const summary=pieces.length?[
  layoutInfo.title,
  intention.trim()?'Question: '+intention.trim():'Question: Open reflection',
  ...pieces.map((p,i)=>p.faceUp
   ?'Rune '+(i+1)+' — '+p.rune.positionName+': '+p.rune.symbol+' '+p.rune.name+' ('+p.rune.orientation+')'+
    '\nHistorical name association: '+p.rune.historic+
    '\nModern themes: '+p.rune.reading.keywords.join(', ')+
    '\nInterpretation: '+p.rune.reading.meaning+
    (layout==='handful'?'\nCloth position: '+p.zone+(p.neighbors.length?'; near '+p.neighbors.join(', '):''):'')
   :'Bone '+(i+1)+' — face down (not interpreted)'),
  'Closing reflection: What theme seems useful? What is one practical next step?',
  'This is a modern reflective interpretation, not a prediction or an ancient ceremony.'
 ].join('\n\n'):'';
 return <View style={{marginBottom:28}}>
  <LinearGradient colors={['#2A203D','#5A3B58','#302438']} start={{x:0,y:0}} end={{x:1,y:1}} style={{borderRadius:24,borderWidth:1,borderColor:'#D7B493',padding:16}}>
   <Text style={{color:'#F9D4B5',fontSize:12,letterSpacing:1.6,fontWeight:'800',textAlign:'center'}}>✦ MODERN RUNE REFLECTION ✦</Text>
   <Text style={{color:'#FFF3E8',fontSize:30,fontWeight:'800',textAlign:'center',marginTop:10}}>Cast the Runes</Text>
   <Text style={{color:'#F0DBE4',fontSize:14,lineHeight:22,marginVertical:14,textAlign:'center'}}>Choose a layout, gather the rune bones, and release them onto the cloth. Use the symbols as prompts for your own thinking—not fixed predictions.</Text>
   <Text style={{color:'#FFE8CE',fontWeight:'800',fontSize:18,marginBottom:8}}>Choose your cast</Text>
   <View style={{flexDirection:'row',flexWrap:'wrap',gap:8,marginBottom:16}}>
    {(Object.keys(RuneLibrary.LAYOUTS) as Array<'daily'|'three'|'cross'|'handful'>).map(key=><TouchableOpacity key={key} accessibilityRole="button" accessibilityState={{selected:layout===key}} onPress={()=>switchLayout(key)} style={{flexGrow:1,minWidth:'44%',padding:12,backgroundColor:layout===key?'#976F8A':'#513950',borderRadius:13,borderWidth:1,borderColor:layout===key?'#FFDCA8':'#B69BB1'}}>
     <Text style={{fontWeight:'800',textAlign:'center',color:'#FFF8EB',fontSize:13}}>{RuneLibrary.LAYOUTS[key].title}</Text><Text style={{textAlign:'center',fontSize:11,color:'#EBD3E0',marginTop:5}}>{RuneLibrary.LAYOUTS[key].count} runes</Text>
    </TouchableOpacity>)}
   </View>
   <Text style={{color:'#FBE5DA',fontSize:14,fontWeight:'800',marginBottom:7}}>Your question (optional)</Text>
   <TextInput maxLength={250} value={intention} onChangeText={setIntention} placeholder="What would help me reflect today?" placeholderTextColor="#83748C" style={{color:'#342A3E',backgroundColor:'#FFF9F4',minHeight:48,padding:12,borderRadius:12,marginBottom:12}}/>
   <TouchableOpacity accessibilityRole="checkbox" accessibilityState={{checked:reversals}} onPress={()=>setReversals(p=>!p)} style={{padding:8,flexDirection:'row',alignItems:'center',gap:11,marginBottom:12}}>
    <Text style={{color:'#FFE8D2',fontSize:18}}>{reversals?'☑':'□'}</Text><Text style={{color:'#FFF3EE',fontSize:13}}>Include modern reversed meanings</Text>
   </TouchableOpacity>
   <View style={{height:clothHeight,width:clothWidth,maxWidth:'100%',alignSelf:'center',marginVertical:8,overflow:'hidden',borderWidth:9,borderColor:'#A98B7A',borderRadius:110,backgroundColor:'#5E5172',shadowColor:'#0E0A16',shadowOpacity:.5,shadowRadius:18,elevation:7}}>
    <View pointerEvents="none" style={{position:'absolute',width:clothWidth*.6,height:clothHeight*.6,top:clothHeight*.2,left:clothWidth*.2,borderRadius:999,borderWidth:1,borderColor:'#E9C1A255'}}/>
    <Text accessible={false} style={{position:'absolute',top:clothHeight*.35,alignSelf:'center',fontSize:90,color:'#F5D7BB55'}}>✦</Text>
    {pieces.map((p,i)=><Bone key={castVersion+'-'+p.rune.id} piece={p} index={i} castVersion={castVersion} onTap={n=>{setHighlight(n);Vibration.vibrate(7)}} highlight={highlight===i}/>)}
    <Animated.View style={{position:'absolute',bottom:14,alignSelf:'center',transform:[{rotate:animateRattle.interpolate({inputRange:[-1,0,1],outputRange:['-5deg','0deg','5deg']})}]}}>
     <TouchableOpacity accessibilityRole="button" accessibilityLabel="Hold and rattle the rune bones, release to cast" onPressIn={beginHold} onPressOut={release} style={{borderColor:'#F4D1A6',borderWidth:1,borderRadius:40,backgroundColor:'#422D42EF',padding:12,minWidth:162,alignItems:'center',opacity:pieces.length?.65:1}}>
      <Text style={{color:'#FFE1BC',fontSize:19}}>✦ ᚠ ᚹ ✦</Text><Text style={{color:'#FFF1E4',fontWeight:'800',fontSize:12}}>{rattling?'Rattling…':'Hold · Rattle · Release'}</Text>
     </TouchableOpacity>
    </Animated.View>
   </View>
   <Text accessibilityRole="text" style={{color:'#F8E0C7',fontSize:13,lineHeight:19,textAlign:'center',marginVertical:10}}>{message}</Text>
   <TouchableOpacity accessibilityRole="button" onPress={throwRunes} style={{minHeight:51,backgroundColor:'#F1C4D9',borderRadius:24,alignItems:'center',justifyContent:'center',marginTop:7}}>
    <Text style={{color:'#442C48',fontSize:16,fontWeight:'800'}}>✦ Cast {layoutInfo.count} Runes</Text>
   </TouchableOpacity>
   <Text style={{color:'#EAD8E1',fontSize:12,lineHeight:18,marginTop:12}}>Touch casting works without motion sensors. Light vibration is used when available; native bone-clack audio and device-shake controls require an additional tested build.</Text>
  </LinearGradient>
  {pieces.length?<View style={{marginTop:16}}>
   <Text style={{color:'#FFF2E3',fontSize:23,fontWeight:'800',marginBottom:12}}>✦ Your {layoutInfo.title} Reading</Text>
   {pieces.map((p,i)=>!p.faceUp?<View key={'down'+i} style={{backgroundColor:'#F7EAE5',borderRadius:15,padding:15,marginBottom:10}}><Text style={{color:'#4D3349',fontWeight:'800'}}>Bone {i+1} · Face down</Text><Text style={{color:'#60475C'}}>This piece stays hidden and is not interpreted.</Text></View>:<View key={p.rune.id} style={{borderRadius:16,borderColor:highlight===i?'#E8BB80':'#F3DFDC',borderWidth:highlight===i?3:1,backgroundColor:'#F8ECE7',padding:17,marginBottom:11,flexDirection:'row',gap:12}}>
    <Text style={{color:'#5B3555',fontSize:39,transform:[{rotate:p.rune.orientation==='reversed'?'180deg':'0deg'}]}}>{p.rune.symbol}</Text><View style={{flex:1}}><Text style={{color:'#482D48',fontWeight:'800',fontSize:16}}>{p.rune.name} · {p.rune.positionName}</Text><Text style={{color:'#765D73',fontSize:12,marginTop:5}}>{p.rune.orientation} · {p.rune.historic}</Text><Text style={{color:'#5C3B56',fontWeight:'800',fontSize:13,marginTop:8}}>{p.rune.reading.keywords.join(' · ')}</Text><Text style={{color:'#453242',fontSize:14,lineHeight:21,marginTop:7}}>{p.rune.reading.meaning}</Text>{layout==='handful'?<Text style={{color:'#765D73',fontSize:12,marginTop:7}}>On the cloth: {p.zone}{p.neighbors.length?'; near '+p.neighbors.join(', '):''}</Text>:null}</View>
   </View>)}
   <View style={{backgroundColor:'#664D66',borderRadius:16,padding:16,marginVertical:10}}><Text style={{fontWeight:'800',fontSize:17,color:'#FFF3E8'}}>Your next step</Text><Text style={{color:'#F9E9F1',fontSize:14,lineHeight:21,marginTop:8}}>What theme feels helpful? What is one practical step you can choose?</Text></View>
   <ContentActions title={'Rune Casting · '+layoutInfo.title} text={summary} route="explore/runes"/>
  </View>:null}
  <View style={{backgroundColor:'#F8ECE9',padding:16,borderRadius:17,marginTop:18}}>
   <Text style={{fontSize:18,fontWeight:'800',color:'#4E3150'}}>📜 Where do the runes come from?</Text>
   <Text style={{fontSize:13,lineHeight:21,marginTop:8,color:'#553D53'}}>The Elder Futhark was a 24-letter writing system used in early northern Europe. The divination spreads and reversed readings offered here are modern adaptations, not a documented Viking-Age casting ritual. There is no historical 25th blank letter. This is for reflection, not certainty.</Text>
   <TouchableOpacity accessibilityRole="link" onPress={()=>Linking.openURL('https://nors.ku.dk/english/research/runes/').catch(()=>{})}><Text style={{color:'#744779',textDecorationLine:'underline',fontSize:13,marginTop:11}}>Read about runology · University of Copenhagen</Text></TouchableOpacity>
  </View>
 </View>;
}
