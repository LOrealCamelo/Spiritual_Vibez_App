/* Remove attribution tags without changing application state or hash routes. */
(function(root){
 'use strict';
 const tracking=/^(utm_.+|fbclid|gclid|dclid|msclkid|ttclid|twclid|igshid|mc_cid|mc_eid|_ga|_gl)$/i;
 function cleanAddress(location,history){
  const url=new URL(location.href);let changed=false;
  for(const key of [...url.searchParams.keys()]){
   if(tracking.test(key)){url.searchParams.delete(key);changed=true;}
  }
  if(changed)history.replaceState(history.state,'',url.pathname+url.search+url.hash);
  return changed;
 }
 root.SpiritualUrlHygiene={cleanAddress};
 if(root.location&&root.history){
  try{cleanAddress(root.location,root.history);}catch{/* Restricted embedded browsers may deny history access. */}
 }
})(globalThis);
