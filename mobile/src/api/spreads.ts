/** Display names from the illustrated collection, retaining authoritative API IDs and layouts. */
export const SPREAD_LABELS:Record<string,string>={
  'reset-energy':'Reset Your Energy',
  'trust-your-gut':'Trust Your Gut',
  'at-a-crossroads':'At a Crossroads',
  'stepping-into-new-timeline':'The Next Phase',
  'mindfulness-calm':'Grounding',
};
export function normalizeSpreads<T extends {id:string;title:string}>(spreads:T[]){
  return spreads.map(spread=>({...spread,originalTitle:spread.title,title:SPREAD_LABELS[spread.id]||spread.title}));
}
