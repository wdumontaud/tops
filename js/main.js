// js/main.js — bootstrap : fond animé (field) + objets flottants (objects), une boucle rAF.
const cv=document.getElementById('field');
const field=FIELD(cv);                       // null si WebGL2 indisponible : le fond bleu uni reste
const sea=document.getElementById('sea');
const objs=Objects.make(sea, field);
objs.applyLang(I18N.lang);                   // libellés des bulles dans la langue courante
document.addEventListener('lang',e=>objs.applyLang(e.detail));

const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

addEventListener('resize',()=>{ if(field) field.resize(); objs.layout(); if(reduced&&field) field.draw(20); });
try{ document.fonts.ready.then(()=>objs.layout()); }catch(e){}   // tailles des bulles revues après la police

if(field&&reduced) field.draw(20);           // une seule frame fixe si mouvement réduit

let last=performance.now();
function loop(ms){
  const dt=Math.min(.05,(ms-last)/1000); last=ms;
  if(field&&!reduced) field.draw(ms/1000+20);   // +20 : même décalage que la présentation
  objs.step(dt, reduced?20:ms/1000+20, reduced?0:1);
  objs.render();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// le hint disparaît au premier drag (voir objects.js) ou après 9 s
setTimeout(()=>document.getElementById('hint')?.classList.add('off'),9000);
