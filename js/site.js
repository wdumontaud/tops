/* TOPS site: language (FR / EN), clips played when their chapter comes on screen, download by code. */
(function () {
  'use strict';

  // ---------- texts ----------
  var T = {
    fr: {
      tagline: 'Optimisation énergétique de la topologie et de la forme d’une paroi de bâtiment',
      lead: 'Une application qui couple la simulation thermique d’un bâtiment (Domus) à un modèle fin de sa paroi, puis cherche la forme de paroi qui consomme le moins.',
      dlTitle: 'Télécharger TOPS', dlLabel: 'Code d’accès', dlPh: 'Votre code', dlBtn: 'Télécharger',
      dlNote: 'Le code vous est donné personnellement. Vous serez prévenu des nouvelles versions.',
      dlEmpty: 'Entrez le code que vous avez reçu.',
      dlSoon: 'Le téléchargement par code sera ouvert prochainement.',
      heroAlt: 'La fenêtre de TOPS : paramètres de la co-simulation, coupe de la paroi et vue 3D',
      more: 'Découvrir l’application', next: 'Continuer', replay: 'Revoir',
      c1t: 'Ouvrir TOPS',
      c1p: 'TOPS s’ouvre comme une application de bureau. L’accueil présente les modèles : on choisit la co-simulation Domus, le bâtiment et sa paroi calculés ensemble.',
      c2t: 'Paramétrer la scène', soon: 'Bientôt.'
    },
    en: {
      tagline: 'Energy optimisation of the topology and the shape of a building wall',
      lead: 'An application that couples the thermal simulation of a building (Domus) with a fine model of its wall, then looks for the wall shape that uses the least energy.',
      dlTitle: 'Download TOPS', dlLabel: 'Access code', dlPh: 'Your code', dlBtn: 'Download',
      dlNote: 'The code is given to you personally. You will be told of new versions.',
      dlEmpty: 'Enter the code you received.',
      dlSoon: 'Download by code opens soon.',
      heroAlt: 'The TOPS window: co-simulation settings, wall section and 3D view',
      more: 'Discover the application', next: 'Continue', replay: 'Replay',
      c1t: 'Opening TOPS',
      c1p: 'TOPS opens as a desktop application. The home page lists the models: we pick the Domus co-simulation, where the building and its wall are computed together.',
      c2t: 'Setting up the scene', soon: 'Coming soon.'
    }
  };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private window */ } }
  };
  var lang = store.get('tops.lang') || ((navigator.language || 'fr').slice(0, 2) === 'fr' ? 'fr' : 'en');
  var setLang = function (l) {
    lang = T[l] ? l : 'fr';
    document.documentElement.lang = lang;
    var t = T[lang];
    document.querySelectorAll('[data-i18n]').forEach(function (e) { e.textContent = t[e.dataset.i18n]; });
    document.querySelectorAll('[data-i18n-ph]').forEach(function (e) { e.placeholder = t[e.dataset.i18nPh]; });
    document.querySelectorAll('[data-i18n-alt]').forEach(function (e) { e.alt = t[e.dataset.i18nAlt]; });
    document.querySelectorAll('[data-i18n-title]').forEach(function (e) { e.title = t[e.dataset.i18nTitle]; });
    document.querySelectorAll('.lang button').forEach(function (b) { b.classList.toggle('on', b.dataset.lang === lang); });
    store.set('tops.lang', lang);
  };
  document.querySelectorAll('.lang button').forEach(function (b) { b.onclick = function () { setLang(b.dataset.lang); }; });
  setLang(lang);

  // ---------- top bar line once scrolled ----------
  var top = document.querySelector('.top');
  var onScroll = function () { top.classList.toggle('scrolled', window.scrollY > 8); };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // ---------- clips: play from the start when the chapter comes on screen, invite to go on at the end ----------
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.chapter[data-clip]').forEach(function (ch) {
    var v = ch.querySelector('video'), loaded = false;
    var play = function () {
      if (!loaded) { v.src = ch.dataset.clip; loaded = true; }
      ch.classList.remove('ended');
      try { v.currentTime = 0; } catch (e) { /* not loaded yet */ }
      var p = v.play(); if (p && p.catch) p.catch(function () { ch.classList.add('ended'); });
    };
    v.addEventListener('ended', function () { ch.classList.add('ended'); });
    ch.querySelector('.replay').onclick = play;
    if (reduce) {                       // no autoplay: the last picture, and the replay button
      v.poster = ch.dataset.clip.replace(/\.mp4$/, '.jpg'); ch.classList.add('ended'); return;
    }
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) play();
        else { v.pause(); }
      });
    }, { threshold: 0.6 }).observe(v);
  });

  // ---------- download by code (the service behind is not open yet) ----------
  var form = document.getElementById('dlForm'), note = document.getElementById('dlNote');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var code = form.code.value.trim();
    note.classList.add('warn');
    note.textContent = code ? T[lang].dlSoon : T[lang].dlEmpty;
  });
})();
