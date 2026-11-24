// members/data.js — les membres affichés sur la page members/ (dans cet ordre).
// Champs : id (= photos/<id>.jpg ; sans fichier, la carte montre les initiales), name, role {fr,en},
// labs [clés de LABS], bio {fr,en}, links [{label, url}] (label : chaîne, ou {fr,en}).
// Sources (2026-11-24) : pages de profil LaSIE / IUSTI ; photos découpées dans
// meeting/PUCPR_seminar2/assets/02-who/who_I_am_noplane.jpg.
const LABS={
  lasie:{name:'LaSIE', full:{fr:'UMR 7356 CNRS — La Rochelle Université', en:'UMR 7356 CNRS — La Rochelle University'},
         url:'https://lasie.univ-larochelle.fr/'},
  iusti:{name:'IUSTI', full:{fr:'UMR 7343 CNRS — Aix-Marseille Université', en:'UMR 7343 CNRS — Aix-Marseille University'},
         url:'https://iusti.cnrs.fr'}
};

// HAL : CV HAL de l'idHal ; Berger et Kadoch (pas de CV HAL configuré) : recherche HAL par idHal. ORCID : vérifiés sur la notice
// HAL hal-05679840 (idHal + ORCID de chaque auteur) et sur pub.orcid.org (nom du titulaire).
const hal=id=>'https://cv.hal.science/'+id, orcid=id=>'https://orcid.org/'+id;

const MEMBERS=[
  {
    id:'berger', name:'Julien Berger',
    role:{fr:'Directeur de thèse', en:'Thesis supervisor'},
    labs:['lasie'],
    bio:{
      fr:'Chercheur CNRS au LaSIE, équipe Bâtiments et ville durables. Ses travaux portent sur la modélisation des transferts de chaleur et de masse dans les matériaux poreux du bâtiment, les modèles numériques rapides et précis, leur confrontation à l’expérience et l’estimation de paramètres à partir de mesures in situ.',
      en:'CNRS researcher at LaSIE, Sustainable Buildings and Cities team. His work deals with heat and mass transfer modelling in porous building materials, fast and accurate numerical models, their comparison with experiments, and parameter estimation from in-situ measurements.'
    },
    links:[
      {label:{fr:'Page LaSIE', en:'LaSIE page'}, url:'https://lasie.univ-larochelle.fr/berger-julien'},
      {label:'HAL', url:'https://hal.science/search/index?q=authIdHal_s:julien-berger'},
      {label:'ORCID', url:orcid('0000-0001-8890-1273')}
    ]
  },
  {
    id:'kadoch', name:'Benjamin Kadoch',
    role:{fr:'Co-directeur de thèse', en:'Thesis co-supervisor'},
    labs:['iusti'],
    bio:{
      fr:'Enseignant-chercheur à l’IUSTI, Aix-Marseille Université. Il co-encadre la thèse depuis Marseille, et co-signe les travaux sur la diffusion dans les domaines composites à interface non régulière et l’optimisation de forme des parois.',
      en:'Lecturer-researcher at IUSTI, Aix-Marseille University. He co-supervises the thesis from Marseille and co-authors the work on diffusion in composite domains with non-regular interfaces and on wall shape optimisation.'
    },
    links:[
      {label:{fr:'Page IUSTI', en:'IUSTI page'}, url:'https://iusti.cnrs.fr/members/kadoch-benjamin'},
      {label:'HAL', url:'https://hal.science/search/index?q=authIdHal_s:benjamin-kadoch'},
      {label:'ORCID', url:orcid('0000-0001-9346-1399')}
    ]
  },
  {
    id:'dumontaud', name:'William Dumontaud',
    role:{fr:'Doctorant', en:'PhD student'},
    labs:['lasie','iusti'],
    bio:{
      fr:'Doctorant CNRS au LaSIE depuis novembre 2024, financé par le projet ANR JCJC TOPS. Il optimise la forme et la répartition de l’isolant dans les parois de bâtiment, avec des modèles numériques efficaces des transferts de chaleur instationnaires.',
      en:'CNRS PhD student at LaSIE since November 2024, funded by the ANR JCJC TOPS project. He optimises the shape and layout of insulation in building walls with efficient numerical models of transient heat transfer.'
    },
    links:[
      {label:{fr:'Page LaSIE', en:'LaSIE page'}, url:'https://lasie.univ-larochelle.fr/dumontaud-william'},
      {label:'HAL', url:hal('william-dumontaud')},
      {label:'ORCID', url:orcid('0009-0004-4638-8415')}
    ]
  }
];
