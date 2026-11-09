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

export function matchesVibe(spread:{title:string;originalTitle?:string;category?:string},vibe:string){
  if(vibe==='All')return true;
  const text=[spread.title,spread.originalTitle,spread.category].join(' ').toLowerCase();
  const terms:Record<string,RegExp>={
    Love:/love|relationship|partner|romance|heart|dating|soulmate|breakup/,
    Career:/career|work|job|business|money|financ|abundance|wealth|profession/,
    Growth:/growth|change|purpose|shadow|healing|wellbeing|crossroads|timeline|self|spirit|transform|mindfulness/,
  };
  return !!terms[vibe]?.test(text);
}
