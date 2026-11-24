// members/members.js — page membres : cartes sur le fond animé (même shader que l'accueil),
// FR/EN (même clé localStorage 'webpage.lang' que les autres pages). Données : data.js.
(()=>{

  const T={
    fr:{ title:'Membres', back:'Accueil',
         intro:'Le projet est mené au <b>LaSIE</b> (La Rochelle) et à l’<b>IUSTI</b> (Marseille), avec le soutien de l’ANR (<a href="https://anr.fr/Projet-ANR-23-CE22-0008" target="_blank" rel="noopener">ANR-23-CE22-0008 ↗</a>).' },
    en:{ title:'Members', back:'Home',
         intro:'The project is carried out at <b>LaSIE</b> (La Rochelle) and <b>IUSTI</b> (Marseille), with the support of the ANR (<a href="https://anr.fr/Projet-ANR-23-CE22-0008" target="_blank" rel="noopener">ANR-23-CE22-0008 ↗</a>).' }
  };
  const store={get:k=>{try{return localStorage.getItem(k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}};
  let lang=store.get('webpage.lang')||((navigator.language||'fr').slice(0,2)==='fr'?'fr':'en');
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const tr=v=>v==null?'':(typeof v==='string'?v:(v[lang]||v.fr));   // chaîne ou {fr,en}

  function setLang(l){
    lang=T[l]?l:'fr';
    document.documentElement.lang=lang;
    const t=T[lang];
    document.querySelectorAll('[data-i18n]').forEach(e=>{const k=e.dataset.i18n; if(t[k]!=null) e.textContent=t[k];});
    document.querySelectorAll('[data-i18n-html]').forEach(e=>{const k=e.dataset.i18nHtml; if(t[k]!=null) e.innerHTML=t[k];});  // textes de T seulement
    document.querySelectorAll('.lang button').forEach(b=>b.classList.toggle('on',b.dataset.lang===lang));
    store.set('webpage.lang',lang);
    render();
  }
  document.querySelectorAll('.lang button').forEach(b=>{b.onclick=()=>setLang(b.dataset.lang)});

  // ---- cartes ----
  const grid=document.getElementById('grid');
  const initials=n=>n.split(/\s+/).map(w=>w[0]).join('').slice(0,2).toUpperCase();
  function render(){
    grid.innerHTML=MEMBERS.map(m=>{
      const labs=(m.labs||[]).map(k=>{const L=LABS[k]; return L?
        `<a class="lab" href="${esc(L.url)}" target="_blank" rel="noopener" title="${esc(tr(L.full))}">${esc(L.name)}</a>`:'';}).join('');
      const links=(m.links||[]).map(l=>l.internal?
        `<a href="${esc(l.url)}">${esc(tr(l.label))} →</a>`:
        `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(tr(l.label))} ↗</a>`).join('');
      return `<li class="card">
        <div class="ph" data-ini="${esc(initials(m.name))}"><img src="photos/${esc(m.id)}.jpg" alt="${esc(m.name)}" loading="lazy" onerror="this.remove()"></div>
        <h2>${esc(m.name)}</h2>
        <p class="role">${esc(tr(m.role))}</p>
        ${labs?`<div class="labs">${labs}</div>`:''}
        ${m.bio?`<p class="bio">${esc(tr(m.bio))}</p>`:''}
        ${links?`<p class="links">${links}</p>`:''}
      </li>`;
    }).join('');
  }
  setLang(lang);

  // ---- fond animé (même shader que l'accueil, via ../js/field.js) ----
  const field=FIELD(document.getElementById('field'));
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  addEventListener('resize',()=>{ if(field) field.resize(); });
  if(field&&reduced) field.draw(20);
  function loop(ms){
    if(field&&!reduced) field.draw(ms/1000+20);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
