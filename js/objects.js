// js/objects.js — objets flottants de la vitrine : ils dérivent avec le champ de
// vagues (field.flowAt) et peuvent être déplacés à la souris / au doigt.
// Chaque objet est un <a> : un raccourci vers une page du site ou un lien externe.
// Pour ajouter un raccourci : une ligne dans ITEMS + ses libellés fr/en dans js/i18n.js (T.*.obj).
const Objects=(()=>{

  // ---- icônes inline (évite un fichier par icône) ; stroke=currentColor -> coloré par le CSS ----
  const svgDoc=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 12h6M9 16h6"/></svg>`;
  const svgConf=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M12 16v3M8.5 21l3.5-2 3.5 2"/></svg>`;
  const svgMembers=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="9" cy="8" r="3.2"/><path d="M3.5 20c.6-3.4 2.8-5 5.5-5s4.9 1.6 5.5 5"/><circle cx="17" cy="9" r="2.4"/><path d="M16 15.2c2.4.2 4 1.7 4.5 4.3"/></svg>`;
  const svgGitlab=`<svg viewBox="0 0 24 24"><path fill="#E24329" d="M12 21.4 8.7 10H3.6L12 21.4z"/><path fill="#FC6D26" d="M12 21.4 8.7 10h6.6L12 21.4z"/><path fill="#FCA326" d="M3.6 10 2.5 13.4c-.1.3 0 .7.3.9l9.2 6.7L3.6 10z"/><path fill="#E24329" d="M3.6 10h5.1L6.1 3.6c-.1-.4-.6-.4-.7 0L3.6 10z"/><path fill="#FC6D26" d="M12 21.4l3.3-11.4h5.1L12 21.4z"/><path fill="#FCA326" d="M20.4 10l1.1 3.4c.1.3 0 .7-.3.9L12 21.4 20.4 10z"/><path fill="#FCA326" d="M20.4 10h-5.1l2.6-6.4c.1-.4.6-.4.7 0l1.8 6.4z"/></svg>`;

  // ---- configuration des raccourcis ----
  // href : page du site (relatif) ou URL externe ; external:true => nouvel onglet + "↗"
  // bare:true => bulle "logo seul" (pas de texte), pour les institutions ; le label sert alors
  //              uniquement d'aria-label (défini dans js/i18n.js, T.*.obj, clé = id)
  // fx, fy : position de départ, en fraction de la largeur / hauteur de l'écran
  const ITEMS=[
    { id:'journal',    href:'articles/index.html?type=journal',      icon:svgDoc,                              fx:.22, fy:.42 },
    { id:'conference', href:'articles/index.html?type=conference',   icon:svgConf,                             fx:.78, fy:.42 },
    { id:'members',    href:'members/index.html',                     icon:svgMembers,                          fx:.15, fy:.68 },
    { id:'tops',       href:'app/index.html',                icon:'<img src="assets/tops.png" alt="">', fx:.38, fy:.85 },
    { id:'anr',        href:'https://anr.fr/Projet-ANR-23-CE22-0008',  icon:'<img src="assets/logo_anr.png" alt="">', external:true, bare:true, fx:.64, fy:.85 },
    { id:'gitlab',     href:'https://src.koda.cnrs.fr/3nbf9z2m/tops',  icon:svgGitlab, external:true,            fx:.85, fy:.68 },
    { id:'cnrs',       href:'https://www.cnrs.fr',                     icon:'<img src="assets/logo_cnrs.png" alt="">',  external:true, bare:true, fx:.14, fy:.12 },
    { id:'iusti',      href:'https://iusti.cnrs.fr',                   icon:'<img src="assets/logo_iusti.png" alt="">', external:true, bare:true, fx:.86, fy:.12 },
    { id:'lr',         href:'https://www.univ-larochelle.fr',          icon:'<img src="assets/logo_lr.png" alt="">',    external:true, bare:true, fx:.07, fy:.45 },
    { id:'lasie',      href:'https://lasie.univ-larochelle.fr/',       icon:'<img src="assets/logo_lasie.png" alt="">', external:true, bare:true, fx:.93, fy:.45 },
  ];

  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));

  function make(sea, field){
    const objs=ITEMS.map(it=>{
      const el=document.createElement('a');
      el.className='obj'+(it.bare?' bare':''); el.id='obj-'+it.id;
      el.href=it.href;
      if(it.external){ el.target='_blank'; el.rel='noopener'; }
      el.innerHTML=`<span class="ico">${it.icon}</span>`+
        (it.bare?'':'<span class="lbl"></span>')+
        (it.external?'<span class="go" aria-hidden="true">↗</span>':'');
      el.draggable=false;
      sea.appendChild(el);
      return {it, el, x:0, y:0, vx:0, vy:0, r:0, s:1, w:0, h:0, hgt:0,
              fx:it.fx, fy:it.fy,
              dragging:false, moved:false, suppressClick:false,
              grabX:0, grabY:0, tx:0, ty:0, px:0, py:0, pt:0, sx:0, sy:0, svx:0, svy:0};
    });

    // ---- libellés fr/en (appelé au chargement et à chaque changement de langue) ----
    function applyLang(lang){
      const dict=(I18N.T[lang]||I18N.T.fr).obj;
      objs.forEach(o=>{
        const d=dict[o.it.id]||{};
        const label=d.label||o.it.id, sub=d.sub||'';
        const lbl=o.el.querySelector('.lbl');
        if(lbl) lbl.innerHTML=label+(sub?`<small>${sub}</small>`:'');   // absent si bare (logo seul)
        o.el.setAttribute('aria-label',label+(sub?' — '+sub:''));
        o.el.title=sub||label;
      });
    }

    let ftRect=null;   // zone du crédit en bas : les objets n'y entrent pas (le haut est libre)
    function layout(){
      const W=innerWidth, H=innerHeight;
      const ft=document.querySelector('.foot');
      if(ft){ const r=ft.getBoundingClientRect(); ftRect={l:r.left,t:r.top,r:r.right,b:r.bottom}; }
      objs.forEach(o=>{
        o.w=o.el.offsetWidth; o.h=o.el.offsetHeight;
        if(!o.placed){ o.x=o.fx*W; o.y=o.fy*H; o.placed=true; }
        o.x=clamp(o.x, o.w/2+6, W-o.w/2-6);
        o.y=clamp(o.y, o.h/2+6, H-o.h/2-6);
      });
    }
    layout();

    // ---- drag (souris + tactile via Pointer Events) ----
    objs.forEach(o=>{
      const el=o.el;
      el.addEventListener('dragstart',e=>e.preventDefault());
      el.addEventListener('pointerdown',e=>{
        if(e.button!==undefined&&e.button!==0) return;
        try{ el.setPointerCapture(e.pointerId); }catch(_){}
        o.dragging=true; o.moved=false;
        o.sx=e.clientX; o.sy=e.clientY;
        o.grabX=o.x-e.clientX; o.grabY=o.y-e.clientY;
        o.px=e.clientX; o.py=e.clientY; o.pt=performance.now();
        o.svx=0; o.svy=0; o.tx=o.x; o.ty=o.y;
        el.classList.add('dragging');
        document.getElementById('hint')?.classList.add('off');
      });
      el.addEventListener('pointermove',e=>{
        if(!o.dragging) return;
        if(Math.hypot(e.clientX-o.sx,e.clientY-o.sy)>6) o.moved=true;
        const now=performance.now(), dtm=Math.max(1,now-o.pt)/1000;
        const ivx=(e.clientX-o.px)/dtm, ivy=(e.clientY-o.py)/dtm;
        o.svx=o.svx*.7+ivx*.3; o.svy=o.svy*.7+ivy*.3;
        o.px=e.clientX; o.py=e.clientY; o.pt=now;
        o.tx=e.clientX+o.grabX; o.ty=e.clientY+o.grabY;
      });
      const end=e=>{
        if(!o.dragging) return;
        o.dragging=false; el.classList.remove('dragging');
        o.vx=clamp(o.svx,-1200,1200); o.vy=clamp(o.svy,-1200,1200);   // élan au relâcher, borné
        if(o.moved) o.suppressClick=true;          // ne pas naviguer après un drag
      };
      el.addEventListener('pointerup',end);
      el.addEventListener('pointercancel',end);
      el.addEventListener('click',e=>{
        if(o.suppressClick){ e.preventDefault(); e.stopPropagation(); o.suppressClick=false; }
      },true);
    });

    // ---- physique : flotteur sur le champ de vagues ----
    // - dérive le long des iso-lignes (tangente au champ), d'autant plus vite que la
    //   pente |grad| est forte (vagues raides = courant fort)
    // - flotte verticalement sur la hauteur du champ h (comme sur l'eau)
    function step(dt,t,drift){
      const W=innerWidth, H=innerHeight;
      objs.forEach(o=>{
        const fl=field?field.flowAt(o.x,o.y,t):{vx:0,vy:0,amp:0,h:0};
        o.hgt=fl.h;
        if(o.dragging){
          const k=Math.min(1,dt*22);
          o.vx=(o.tx-o.x)*22; o.vy=(o.ty-o.y)*22;
          o.x+=(o.tx-o.x)*k; o.y+=(o.ty-o.y)*k;
        }else{
          const speed=(12+42*Math.min(1,fl.amp/3))*drift;   // px/s, piloté par la pente
          const k=Math.min(1,dt*1.1);
          o.vx+=((fl.vx*speed)-o.vx)*k;
          o.vy+=((fl.vy*speed)-o.vy)*k;
          o.x+=o.vx*dt; o.y+=o.vy*dt;
        }
        // bords : rebond doux
        const mX=o.w/2+6, mY=o.h/2+6;
        if(o.x<mX){o.x=mX;o.vx=Math.abs(o.vx)*.6;} else if(o.x>W-mX){o.x=W-mX;o.vx=-Math.abs(o.vx)*.6;}
        if(o.y<mY){o.y=mY;o.vy=Math.abs(o.vy)*.6;} else if(o.y>H-mY){o.y=H-mY;o.vy=-Math.abs(o.vy)*.6;}
        // zone du crédit (en bas) : on pousse doucement vers le haut
        if(ftRect){
          const pad=o.h/2+10;
          if(o.x>ftRect.l-pad&&o.x<ftRect.r+pad&&o.y>ftRect.t-pad&&o.y<ftRect.b+pad){
            o.y=ftRect.t-pad; o.vy=-Math.abs(o.vy)*.5-30;
          }
        }
        // léger tilt dans la direction du mouvement
        const tilt=o.dragging?0:clamp(o.vx*.012,-.12,.12);
        o.r+=(tilt-o.r)*Math.min(1,dt*4);
        o.s+=((o.dragging?1.05:1)-o.s)*Math.min(1,dt*10);
      });
      // répulsion douce entre objets (ils ne se chevauchent pas)
      for(let i=0;i<objs.length;i++) for(let j=i+1;j<objs.length;j++){
        const a=objs[i], b=objs[j];
        const dx=b.x-a.x, dy=b.y-a.y, d=Math.hypot(dx,dy)||.01;
        const min=(a.w+b.w)/2*.72+26;
        if(d<min){
          const push=(min-d)/d*.5, px=dx*push, py=dy*push;
          a.x-=px; a.y-=py; b.x+=px; b.y+=py;
          a.vx-=px*8; a.vy-=py*8; b.vx+=px*8; b.vy+=py*8;
        }
      }
    }

    function render(){
      const now=performance.now()/1000;
      objs.forEach(o=>{
        const bob=o.hgt*14;                       // flotte sur la hauteur du champ
        const wob=o.hgt*.05+Math.sin(now*.8+o.fx*9)*.015;
        o.el.style.transform=`translate3d(${o.x-o.w/2}px,${o.y-o.h/2+bob}px,0) rotate(${o.r+wob}rad) scale(${o.s})`;
      });
    }

    return {step, render, layout, applyLang};
  }

  return {make, ITEMS};
})();
