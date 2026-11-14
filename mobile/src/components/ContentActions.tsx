import React,{createContext,useContext,useRef,useState} from 'react';
import {ActivityIndicator,Alert,Image,ImageSourcePropType,Modal,ScrollView,StyleSheet,Text,TouchableOpacity,View,useWindowDimensions} from 'react-native';
import NativeShare from 'react-native-share';
import {captureRef} from 'react-native-view-shot';
import {SvgXml} from 'react-native-svg';
import {HomePaletteContext} from './HomePalette';
import {addJournalContent} from '../content/journal';
const Format=require('../content/content-format');
export const ContentLocationContext=createContext('home');
export type ContentProps={title:string;text?:string;value?:any;route?:string;imageSvg?:string;imageSource?:ImageSourcePropType;imageSources?:ImageSourcePropType[]};
export function collectContentText(children:React.ReactNode):string{
 const parts:string[]=[];
 function visit(node:any){
  if(node==null||typeof node==='boolean')return;
  if(typeof node==='string'||typeof node==='number'){parts.push(String(node));return;}
  if(Array.isArray(node)){node.forEach(visit);return;}
  const p=node.props||{},name=node.type?.name||node.type?.displayName;
  if(p.onPress||p.accessibilityRole==='button'||['Action','Button','ContentActions'].includes(name))return;
  if(p.value!=null&&typeof p.value==='object'){parts.push(Format.readable(p.value));return;}
  visit(p.children);
 }
 visit(children);return parts.join('\n').replace(/\n{3,}/g,'\n\n').trim();
}
export function ContentActions(props:ContentProps){
 const location=useContext(ContentLocationContext),light=useContext(HomePaletteContext),{width,height}=useWindowDimensions();
 const [preview,setPreview]=useState<any>(null),[busy,setBusy]=useState(false),[saved,setSaved]=useState(false),[ready,setReady]=useState(false);
 const exportSize=useRef({width:1,height:1});
 const assetsReady=useRef({layout:false,logo:false,art:false});const galleryLoaded=useRef(0);
 const markReady=(part: "layout"|"logo"|"art")=>{assetsReady.current[part]=true;setReady(Object.values(assetsReady.current).every(Boolean))};
 const openPreview=()=>{const item=snapshot();galleryLoaded.current=0;assetsReady.current={layout:false,logo:false,art:!item.imageSvg&&!item.imageSource&&!item.imageSources?.length};setReady(false);setPreview(item)};
 const capture=useRef<ScrollView>(null);const cardWidth=Math.min(width-80,440);
 const snapshot=()=>({...Format.snapshot({...props,route:props.route||location}),imageSources:props.imageSources});
 const add=async()=>{try{const item=snapshot();await addJournalContent(item.title,item.text);setSaved(true)}catch{Alert.alert('Could not add to journal','Please try again after checking the available storage on this device.')}};
 const send=async()=>{
  if(!preview||!ready)return;setBusy(true);
  try{const uri=await captureRef(capture.current!,{format:'png',result:'tmpfile',snapshotContentContainer:true,width:1080,height:Math.ceil(exportSize.current.height*1080/exportSize.current.width)});
   await NativeShare.open({title:preview.title,message:Format.message(preview),url:uri.startsWith('file://')?uri:'file://'+uri,type:'image/png',failOnCancel:false});
  }catch{Alert.alert('Sharing did not finish','Your reading is still available. Please try sharing again.')}finally{setBusy(false)}
 };
 return <><View style={styles.row}>
  <TouchableOpacity accessibilityRole="button" accessibilityLabel={'Share complete '+props.title} onPress={openPreview} style={[styles.action,light?styles.lightBorder:null]}><Text style={[styles.actionText,light?styles.lightInk:null]}>Share full reading</Text></TouchableOpacity>
  <TouchableOpacity accessibilityRole="button" accessibilityLabel={'Save complete '+props.title+' to journal'} onPress={add} style={[styles.action,light?styles.lightBorder:null]}><Text style={[styles.actionText,light?styles.lightInk:null]}>Save full reading to Journal</Text></TouchableOpacity>
 </View>{saved?<Text accessibilityRole="alert" style={[styles.confirmation,light?styles.lightInk:null]}>Added to your journal.</Text>:null}
 {preview?<Modal transparent animationType="slide" onRequestClose={()=>setPreview(null)}><View style={styles.overlay}><View accessibilityViewIsModal style={[styles.sheet,{maxHeight:height*.9}]}>
  <Text accessibilityRole="header" style={styles.heading}>Share {preview.title}</Text>
  <ScrollView ref={capture} onContentSizeChange={(width,height)=>{exportSize.current={width,height}}} removeClippedSubviews={false} style={{maxHeight:height*.65}} contentContainerStyle={{alignItems:'center'}}>
   <View collapsable={false} style={[styles.exportCard,{width:cardWidth}]} onLayout={()=>markReady("layout")}>
    <Image source={require('../../assets/spiritual-vibz-logo-compact.png')} resizeMode="contain" onLoadEnd={()=>markReady('logo')} style={{width:200,height:80,marginBottom:20}}/>
    <Text style={styles.heading}>{preview.title}</Text>
    {preview.imageSvg?<SvgXml xml={preview.imageSvg} width={cardWidth-40} height={cardWidth-40} onLayout={()=>markReady("art")}/>:preview.imageSources?.length?<View style={{flexDirection:'row',flexWrap:'wrap',justifyContent:'center',gap:8}}>
     {preview.imageSources.map((source:ImageSourcePropType,i:number)=><Image key={i} source={source} resizeMode="contain" onLoadEnd={()=>{galleryLoaded.current++;if(galleryLoaded.current>=preview.imageSources.length)markReady('art')}} style={{width:Math.min(130,(cardWidth-64)/3),height:210}}/>)}
    </View>:preview.imageSource?<Image source={preview.imageSource} resizeMode="contain" onLoadEnd={()=>markReady("art")} style={{width:cardWidth-40,height:280}}/>:null}
    <Text style={styles.exportBody}>{preview.imageSources?.length||preview.route==='explore/runes'?preview.text:Format.summary(preview)}</Text><View style={styles.rule}/><Text style={styles.cta}>Get your own here</Text><Text style={styles.url}>{preview.url}</Text>
   </View>
  </ScrollView>
  <Text style={styles.note}>One share includes all card or chart artwork and the complete text. Review birth details and personal reflections before sending.</Text><View style={styles.row}>
   <TouchableOpacity accessibilityRole="button" accessibilityLabel="Share full reading" disabled={busy||!ready} onPress={send} style={styles.previewAction}>{busy?<ActivityIndicator color="#35174d"/>:<Text style={styles.lightInk}>Share full reading</Text>}</TouchableOpacity>
   <TouchableOpacity accessibilityRole="button" accessibilityLabel="Close share preview" disabled={busy} onPress={()=>setPreview(null)} style={styles.previewAction}><Text style={styles.lightInk}>Close</Text></TouchableOpacity>
  </View>
 </View></View></Modal>:null}</>;
}
const styles=StyleSheet.create({row:{flexDirection:'row',flexWrap:'wrap',gap:6,marginTop:8,marginBottom:12},action:{flex:1,minHeight:44,minWidth:60,padding:8,borderWidth:1,borderColor:'#ffffff80',borderRadius:18,backgroundColor:'#ffffff08',alignItems:'center',justifyContent:'center'},actionText:{fontSize:12,fontWeight:'700',color:'#fff9fe',textAlign:'center'},lightInk:{color:'#35174d'},lightBorder:{borderColor:'#754a9880'},confirmation:{fontSize:12,color:'#fff9fe',marginBottom:8},overlay:{flex:1,backgroundColor:'#1c1027a6',alignItems:'center',justifyContent:'center',padding:16},sheet:{width:'100%',maxWidth:480,borderRadius:22,backgroundColor:'#f4ecff',padding:12},heading:{fontSize:23,fontWeight:'800',color:'#35174d',marginBottom:16},exportCard:{padding:20,backgroundColor:'#f4ecff'},exportBody:{fontSize:16,lineHeight:24,color:'#35174d',marginTop:16},rule:{height:1,backgroundColor:'#b31380',marginTop:24,marginBottom:16},cta:{fontSize:18,fontWeight:'800',color:'#b31380'},url:{fontSize:13,color:'#35174d',marginTop:8},note:{fontSize:12,color:'#35174d',marginTop:12},previewAction:{flex:1,minHeight:46,borderWidth:1,borderColor:'#754a9880',borderRadius:18,padding:12,alignItems:'center',justifyContent:'center'}});
