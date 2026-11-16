/* Remove attribution tags without changing application state or hash routes. */
(function(root){
 'use strict';
 const tracking=/^(utm_.+|fbclid|gclid|dclid|msclkid|ttclid|twclid|igshid|mc_cid|mc_eid|_ga|_gl)$/i;
 function cleanAddress(location,history){
  const url=new URL(location.href);let changed=false;
  function removeTags(params){
   let removed=false;
   for(const key of [...params.keys()])if(tracking.test(key)){params.delete(key);removed=true;}
   return removed;
  }
  changed=removeTags(url.searchParams);
  // Some link generators append tracking after the hash route. Retain any
  // legitimate fragment query and clean only recognized application hashes.
  const at=url.hash.indexOf('?');
  if(at>=0 && /^#(?:home|spreads|learn|cosmos|explore|journal)(?:\/[^?]*)?$/.test(url.hash.slice(0,at))){
   const params=new URLSearchParams(url.hash.slice(at+1));
   if(removeTags(params)){url.hash=url.hash.slice(0,at)+(params.size?'?'+params:'');changed=true;}
  }
  if(changed)history.replaceState(history.state,'',url.pathname+url.search+url.hash);
  return changed;
 }
 root.SpiritualUrlHygiene={cleanAddress};
 if(root.location&&root.history){
  try{cleanAddress(root.location,root.history);}catch{/* Restricted embedded browsers may deny history access. */}
 }
})(globalThis);
