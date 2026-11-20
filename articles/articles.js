// articles/articles.js — page articles : liste classique sur le fond animé (même shader que l'accueil),
// filtres par type, FR/EN (même clé localStorage 'webpage.lang' que l'accueil).
(()=>{

  // ---- mini i18n local (mêmes conventions que ../js/i18n.js) ----
  const T={
    fr:{ title:'Articles de revue', back:'Accueil', empty:'Aucun article pour l’instant.',
         fAll:'Tous', fJournal:'Revues', fConf:'Conférences', fPre:'Preprints',
         abstract:'Résumé', chip:{journal:'Revue', conference:'Conférence', preprint:'Preprint'},
         status:{published:'Publié', 'in-press':'Sous presse', preprint:'Preprint', submitted:'Soumis'} },
    en:{ title:'Journal articles', back:'Home', empty:'No article yet.',
         fAll:'All', fJournal:'Journals', fConf:'Conferences', fPre:'Preprints',
         abstract:'Abstract', chip:{journal:'Journal', conference:'Conference', preprint:'Preprint'},
         status:{published:'Published', 'in-press':'In press', preprint:'Preprint', submitted:'Submitted'} }
  };
  const store={get:k=>{try{return localStorage.getItem(k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}};
  let lang=store.get('webpage.lang')||((navigator.language||'fr').slice(0,2)==='fr'?'fr':'en');
  function setLang(l){
    lang=T[l]?l:'fr';
    document.documentElement.lang=lang;
    const t=T[lang];
    document.querySelectorAll('[data-i18n]').forEach(e=>{const k=e.dataset.i18n; if(t[k]!=null) e.textContent=t[k];});
    document.querySelectorAll('.lang button').forEach(b=>b.classList.toggle('on',b.dataset.lang===lang));
    store.set('webpage.lang',lang);
    render();
  }
  document.querySelectorAll('.lang button').forEach(b=>{b.onclick=()=>setLang(b.dataset.lang)});

  // ---- rendu de la liste ----
  const list=document.getElementById('list'), empty=document.getElementById('empty');
  const TYPES=new Set(['all','journal','conference','preprint']);
  let filter='all';
  // "Revues" (journal) inclut aussi les preprints : un preprint est un article de revue non encore publié
  const matches=a=>filter==='all'||a.type===filter||(filter==='journal'&&a.type==='preprint');
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  function chip(type,status){
    const t=T[lang];
    return `<span class="chip ${type}">${esc(t.chip[type]||type)}</span>`+
           (t.status[status]&&status!==type?`<span class="chip">${esc(t.status[status])}</span>`:'');
  }
  function render(){
    const t=T[lang];
    const arts=[...ARTICLES].sort((a,b)=>b.year-a.year);
    list.innerHTML=arts.map(a=>{
      const links=[];
      if(a.doi) links.push(`<a href="https://doi.org/${esc(a.doi)}" target="_blank" rel="noopener">DOI ↗</a>`);
      if(a.hal) links.push(`<a href="${esc(a.hal)}" target="_blank" rel="noopener">HAL ↗</a>`);
      (a.links||[]).forEach(l=>links.push(`<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} ↗</a>`));
      return `<li class="art${matches(a)?'':' hide'}" data-type="${a.type}">
        <div class="yr">${a.year}</div>
        <div>
          <h2>${a.doi?`<a href="https://doi.org/${esc(a.doi)}" target="_blank" rel="noopener">${esc(a.title)}</a>`:esc(a.title)}</h2>
          <p class="authors">${esc(a.authors)}</p>
          ${a.venue?`<p class="venue"><i>${esc(a.venue)}</i></p>`:''}
          <div class="chips">${chip(a.type,a.status||a.type)}</div>
          ${links.length?`<p class="links">${links.join('')}</p>`:''}
          ${a.abstract?`<details class="abs"><summary>${esc(t.abstract)}</summary><p>${esc(a.abstract)}</p></details>`:''}
        </div>
      </li>`;
    }).join('');
    empty.hidden=arts.some(matches);
  }
  function setFilter(f){
    filter=TYPES.has(f)?f:'all';
    document.querySelectorAll('.filters button').forEach(x=>x.classList.toggle('on',x.dataset.filter===filter));
    try{ history.replaceState(null,'',filter==='all'?location.pathname:'?type='+filter); }catch(_){}
    render();
  }
  document.querySelectorAll('.filters button').forEach(b=>{
    b.onclick=()=>setFilter(b.dataset.filter);
  });
  setLang(lang);
  // filtre initial via l'URL (?type=journal|conference|preprint|all), ex. lien depuis l'accueil
  setFilter(new URLSearchParams(location.search).get('type')||'all');

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
