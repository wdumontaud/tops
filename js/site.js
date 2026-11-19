/* TOPS site: language (FR / EN), the film (one screen, steps played as one scrolls), download by code. */
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
      s1t: 'Ouvrir TOPS',
      s1p: 'TOPS s’ouvre comme une application de bureau. On choisit la co-simulation Domus : le bâtiment et sa paroi calculés ensemble, ici dans une rue de La Rochelle.',
      s2t: 'Paramétrer la scène',
      s2p: 'Rangées de bâtiments, largeur de la rue, étages : le plan suit chaque changement. Le bouton à côté de Run écrit le fichier IDF et la vue 3D montre la nouvelle scène.',
      s3t: 'Se promener dans la vue 3D', soon: 'Bientôt.', steps: 'Étapes'
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
      s1t: 'Opening TOPS',
      s1p: 'TOPS opens as a desktop application. We pick the Domus co-simulation: the building and its wall computed together, here in a street of La Rochelle.',
      s2t: 'Setting up the scene',
      s2p: 'Rows of buildings, street width, floors: the plan follows every change. The button beside Run writes the IDF file and the 3D view shows the new scene.',
      s3t: 'Walking through the 3D view', soon: 'Coming soon.', steps: 'Steps'
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
    if (window.__filmLang) window.__filmLang();
  };
  document.querySelectorAll('.lang button').forEach(function (b) { b.onclick = function () { setLang(b.dataset.lang); }; });
  setLang(lang);

  // ---------- top bar line once scrolled ----------
  // hidden while going down past the landing (the application fills the screen), back when going up
  var top = document.querySelector('.top'), lastY = window.scrollY;
  var onScroll = function () {
    var y = window.scrollY, hero = document.querySelector('.hero').offsetHeight;
    top.classList.toggle('scrolled', y > 8);
    if (Math.abs(y - lastY) > 4) { top.classList.toggle('away', y > lastY && y > hero * .6); lastY = y; }
  };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // ---------- the film ----------
  // One screen held in place (sticky); under it one step per screen of scrolling. Step k is played when it is
  // reached; it starts on the picture where step k-1 ended (one take, cut in steps: tools/film/take.py), so the
  // swap between the two <video> is not seen. Going back up shows the end of the step reached.
  var film = document.getElementById('film');
  if (film) (function () {
    var screen = film.querySelector('.screen'), V = [].slice.call(screen.querySelectorAll('.v'));
    var steps = [].slice.call(film.querySelectorAll('.step')), N = steps.length;
    var cap = screen.querySelector('.cap'), dots = screen.querySelector('.dots');
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var front = V[0], cur = -1, want = null, capTimer = null;
    steps.forEach(function (s, k) {
      var d = document.createElement('a'); d.href = '#film'; d.dataset.k = k;
      d.onclick = function (e) { e.preventDefault(); go(k); };
      dots.appendChild(d);
    });
    var other = function () { return front === V[0] ? V[1] : V[0]; };
    var srcOf = function (k) { return steps[k].dataset.clip + '.mp4'; };
    var load = function (v, k) {
      if (v.dataset.k !== String(k)) { v.dataset.k = k; v.src = srcOf(k); v.load(); }
    };
    var ready = function (v, fn) {
      if (v.readyState >= 2) fn(); else v.addEventListener('loadeddata', function h() { v.removeEventListener('loadeddata', h); fn(); });
    };
    var swap = function (v) {
      if (v !== front) { v.classList.add('on'); front.classList.remove('on'); front.pause(); front = v; }
    };
    // the card of the step: shown when it starts, gone after a while (the application is the film); stays on a
    // still picture (going back up)
    var caption = function (k, still) {
      var t = T[lang], st = steps[k];
      cap.classList.remove('in');
      clearTimeout(capTimer);
      capTimer = setTimeout(function () {
        cap.querySelector('.num').textContent = ('0' + (k + 1)).slice(-2);
        cap.querySelector('h2').textContent = t[st.dataset.t];
        cap.querySelector('.txt').textContent = t[st.dataset.p];
        cap.classList.add('in');
        if (!still) capTimer = setTimeout(function () { cap.classList.remove('in'); }, 7000);
      }, cur < 0 ? 0 : 250);
      dots.querySelectorAll('a').forEach(function (d, i) { d.classList.toggle('on', i === k); d.title = t[steps[i].dataset.t]; });
      dots.setAttribute('aria-label', t.steps);
      // « Continuer : <what comes next> »
      var after = k + 1 < N ? t[steps[k + 1].dataset.t] : (document.querySelector('.soon h2') || {}).textContent;
      screen.querySelector('.next span').textContent = t.next + (after ? ' : ' + after : '');
    };
    window.__filmLang = function () { if (cur >= 0) caption(cur, screen.classList.contains('ended')); };
    // show step k: played from its start, or (going back, reduced motion) its last picture
    var show = function (k, atEnd) {
      want = k;
      screen.classList.remove('ended', 'more');
      caption(k, atEnd);
      var v = front.dataset.k === String(k) ? front : other();
      load(v, k);
      ready(v, function () {
        if (want !== k) return;
        if (atEnd) {
          v.pause();
          v.addEventListener('seeked', function h() { v.removeEventListener('seeked', h); if (want === k) { swap(v); ended(k); } });
          v.currentTime = Math.max(0, v.duration - 0.04);
        } else {
          v.currentTime = 0;
          var p = v.play();
          var on = function () { if (want === k) swap(v); };
          if (p && p.then) p.then(on, function () { on(); ended(k); }); else on();
          if (k + 1 < N) setTimeout(function () { if (want === k) load(other(), k + 1); }, 400);   // the next one, ready
        }
      });
    };
    var ended = function (k) { screen.classList.add('ended', 'more'); };
    V.forEach(function (v) { v.addEventListener('ended', function () { if (v === front && want === +v.dataset.k) ended(want); }); });
    // the step reached by scrolling (half a screen into it); -1: the film is not on screen yet
    var stepAt = function () {
      var r = film.getBoundingClientRect(), h = window.innerHeight;
      if (r.top > h * .35 || r.bottom < h * .5) return -1;
      return Math.max(0, Math.min(N - 1, Math.floor(-r.top / h + .5)));
    };
    // step k (k = N: what follows the film)
    var go = function (k) {
      var y = k < N ? film.offsetTop + k * window.innerHeight : film.offsetTop + film.offsetHeight - 52;
      window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    };
    var onFilmScroll = function () {
      var k = stepAt();
      if (k === cur) return;
      if (k < 0) { front.pause(); cur = -1; return; }
      var back = k < cur;
      cur = k;
      show(k, back || reduce);
    };
    window.addEventListener('scroll', onFilmScroll, { passive: true });
    window.addEventListener('resize', onFilmScroll);
    screen.querySelector('.replay').onclick = function () { show(cur, false); };
    screen.querySelector('.next').onclick = function (e) { e.preventDefault(); go(cur + 1); };
    onFilmScroll();
  })();


  // ---------- download by code (the service behind is not open yet) ----------
  var form = document.getElementById('dlForm'), note = document.getElementById('dlNote');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var code = form.code.value.trim();
    note.classList.add('warn');
    note.textContent = code ? T[lang].dlSoon : T[lang].dlEmpty;
  });
})();
