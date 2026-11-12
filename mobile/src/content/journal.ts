import AsyncStorage from '@react-native-async-storage/async-storage';
const subscribers=new Set<()=>void>();
let writes:Promise<unknown>=Promise.resolve();
export function subscribeJournal(callback:()=>void){subscribers.add(callback);return()=>{subscribers.delete(callback)};}
export function addJournalContent(title:string,text:string){
 const next=writes.catch(()=>{}).then(async()=>{
  const raw=await AsyncStorage.getItem('sv_readings');let entries=[];
  try{const parsed=JSON.parse(raw||'[]');if(Array.isArray(parsed))entries=parsed}catch{}
  const entry={title,text,date:new Date().toLocaleDateString()};
  await AsyncStorage.setItem('sv_readings',JSON.stringify([entry,...entries].slice(0,100)));
  subscribers.forEach(callback=>callback());return entry;
 });
 writes=next;return next;
}
