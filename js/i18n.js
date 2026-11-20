// js/i18n.js — FR/EN, mêmes conventions que app/js/site.js et articles/articles.js (clé 'webpage.lang' commune) :
// dictionnaire T, attributs data-i18n / data-i18n-title, boutons .lang button[data-lang],
// choix gardé dans localStorage. Les libellés des objets flottants sont traduits
// via l'événement 'lang' (voir js/objects.js -> Objects.applyLang).
const I18N=(()=>{
  const T={
    fr:{
      home:'Accueil',
      tagline:'Optimisation de la forme et du domaine d’isolation au regard de l’efficacité énergétique des parois',
      hint:'Les objets dérivent avec le courant — glissez-les pour les déplacer',
      credit:'William Dumontaud — LaSIE, La Rochelle Université · IUSTI, Aix-Marseille Université',
      seaLabel:'Raccourcis',
      obj:{
        journal:{label:'Articles de revue', sub:'Revues à comité de lecture'},
        conference:{label:'Communications', sub:'Conférences internationales'},
        members:{label:'Membres', sub:'L’équipe'},
        tops:{label:'TOPS', sub:'L’application — démo'},
        anr:{label:'ANR', sub:'Projet ANR-23-CE22-0008'},
        gitlab:{label:'GitLab', sub:'Code — projet TOPS'},
        cnrs:{label:'CNRS', sub:''},
        iusti:{label:'IUSTI — Aix-Marseille Université', sub:''},
        lr:{label:'La Rochelle Université', sub:''},
        lasie:{label:'LaSIE — La Rochelle Université', sub:''},
      }
    },
    en:{
      home:'Home',
      tagline:'Shape and insulation domain optimisation regarding wall energy efficiency',
      hint:'The objects drift with the current — drag them around',
      credit:'William Dumontaud — LaSIE, La Rochelle Université · IUSTI, Aix-Marseille University',
      seaLabel:'Shortcuts',
      obj:{
        journal:{label:'Journal articles', sub:'Peer-reviewed journals'},
        conference:{label:'Conference papers', sub:'International conferences'},
        members:{label:'Members', sub:'The team'},
        tops:{label:'TOPS', sub:'The application — demo'},
        anr:{label:'ANR', sub:'ANR project ANR-23-CE22-0008'},
        gitlab:{label:'GitLab', sub:'Code — TOPS project'},
        cnrs:{label:'CNRS', sub:''},
        iusti:{label:'IUSTI — Aix-Marseille University', sub:''},
        lr:{label:'La Rochelle Université', sub:''},
        lasie:{label:'LaSIE — La Rochelle Université', sub:''},
      }
    }
  };
  const store={
    get:k=>{try{return localStorage.getItem(k)}catch(e){return null}},
    set:(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}}
  };
  let lang=store.get('webpage.lang')||((navigator.language||'fr').slice(0,2)==='fr'?'fr':'en');
  function setLang(l){
    lang=T[l]?l:'fr';
    document.documentElement.lang=lang;
    const t=T[lang];
    document.querySelectorAll('[data-i18n]').forEach(e=>{e.textContent=t[e.dataset.i18n]});
    document.querySelectorAll('[data-i18n-title]').forEach(e=>{e.title=t[e.dataset.i18nTitle]});
    document.querySelectorAll('.lang button').forEach(b=>b.classList.toggle('on',b.dataset.lang===lang));
    const sea=document.getElementById('sea'); if(sea) sea.setAttribute('aria-label',t.seaLabel);
    store.set('webpage.lang',lang);
    document.dispatchEvent(new CustomEvent('lang',{detail:lang}));
  }
  document.querySelectorAll('.lang button').forEach(b=>{b.onclick=()=>setLang(b.dataset.lang)});
  setLang(lang);
  return {setLang, T, get lang(){return lang}};
})();
