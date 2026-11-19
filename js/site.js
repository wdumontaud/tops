/* TOPS site: language (FR / EN), the film (one screen; scrolling moves the film forwards and backwards, still when
   one stops; Play scrolls by itself at the speed of the film), the 3D view of step 3, download by code. */
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
      more: 'Découvrir l’application', watch: 'Regarder comme une vidéo', play: 'Lecture', pause: 'Pause',
      scrollHint: 'Faites défiler pour avancer',
      s1t: 'Ouvrir TOPS',
      s1p: 'TOPS s’ouvre comme une application de bureau. On choisit la co-simulation Domus : le bâtiment et sa paroi calculés ensemble, ici dans une rue de La Rochelle.',
      s2t: 'Paramétrer la scène',
      s2p: 'Rangées de bâtiments, largeur de la rue, étages : le plan suit chaque changement. Le bouton à côté de Run écrit le fichier IDF et la vue 3D montre la nouvelle scène.',
      s3t: 'Se promener dans la vue 3D',
      s3p: 'La vraie vue 3D de TOPS, dans la page : le soleil tourne, les façades prennent leurs heures d’ensoleillement, puis les facteurs de forme de la façade étudiée, calculés comme dans le modèle de paroi. Elle suit le défilement ; prenez-la en main quand vous voulez.',
      liveHint: 'La vue est à vous : glissez pour tourner, Ctrl + molette pour zoomer',
      liveTouch: 'Touchez pour prendre la vue en main', liveResume: 'Reprendre la visite guidée',
      s4t: 'Choisir la météo',
      s4p: 'Une fenêtre pour les stations météo du monde entier (17 000). Pour La Rochelle : le climat actuel, ou des climats futurs (RCP 8.5) tirés des projections de Copernicus, sur la période de son choix. On garde ici le climat actuel.',
      s5t: 'Optimiser la forme de la paroi',
      s5p: 'En mode Optimisation, la paroi devient un dessin libre de deux matériaux (level-set). Un algorithme génétique cherche celui qui réduit le flux de chaleur à travers la face intérieure sur un an ; chaque essai est une co-simulation Domus. Run donne d’abord une estimation du temps ; le run complet (200 individus, 20 générations, 4 200 co-simulations) a tourné sur le cluster.',
      s6t: 'Les résultats de l’optimisation',
      s6p: 'Le meilleur dessin de chaque génération défile dans la coupe de la paroi. La convergence : de 700 kWh pour le mur plan à 180 kWh, soit −74 %. Puis le dessin optimal face à la référence, et les meilleurs au fil des générations. Un clic le charge dans le formulaire.',
      s7t: 'Simuler le cas optimal',
      s7p: 'Le dessin optimal, en mode Simulation : trois jours de juillet, avec les champs de température et de flux dans la paroi. Domus (le bâtiment et la rue) et le modèle de paroi tournent ensemble, pas à pas.',
      s8t: 'Les champs dans la paroi', soon: 'Bientôt.', steps: 'Étapes'
    },
    en: {
      tagline: 'Energy optimisation of the topology and the shape of a building wall',
      lead: 'An application that couples the thermal simulation of a building (Domus) with a fine model of its wall, then looks for the wall shape that uses the least energy.',
      dlTitle: 'Download TOPS', dlLabel: 'Access code', dlPh: 'Your code', dlBtn: 'Download',
      dlNote: 'The code is given to you personally. You will be told of new versions.',
      dlEmpty: 'Enter the code you received.',
      dlSoon: 'Download by code opens soon.',
      heroAlt: 'The TOPS window: co-simulation settings, wall section and 3D view',
      more: 'Discover the application', watch: 'Watch as a video', play: 'Play', pause: 'Pause',
      scrollHint: 'Scroll to move on',
      s1t: 'Opening TOPS',
      s1p: 'TOPS opens as a desktop application. We pick the Domus co-simulation: the building and its wall computed together, here in a street of La Rochelle.',
      s2t: 'Setting up the scene',
      s2p: 'Rows of buildings, street width, floors: the plan follows every change. The button beside Run writes the IDF file and the 3D view shows the new scene.',
      s3t: 'Walking through the 3D view',
      s3p: 'The real 3D view of TOPS, in the page: the sun goes round, the facades take their hours of sun, then the view factors of the studied facade, computed as in the wall model. It follows the scrolling; take it in hand whenever you like.',
      liveHint: 'The view is yours: drag to turn, Ctrl + wheel to zoom',
      liveTouch: 'Tap to take the view in hand', liveResume: 'Back to the guided tour',
      s4t: 'Choosing the weather',
      s4p: 'One window for the weather stations of the whole world (17,000). For La Rochelle: the present climate, or future climates (RCP 8.5) made from the Copernicus projections, over the period of your choice. Here the present climate is kept.',
      s5t: 'Optimising the shape of the wall',
      s5p: 'In Optimisation mode the wall becomes a free drawing of two materials (level-set). A genetic algorithm looks for the one that lowers the heat flux through the internal face over a year; each try is a Domus co-simulation. Run first gives an estimate of the time; the full run (200 individuals, 20 generations, 4,200 co-simulations) was done on the cluster.',
      s6t: 'The results of the optimisation',
      s6p: 'The best drawing of each generation plays in the section of the wall. The convergence: from 700 kWh for the plane wall to 180 kWh, −74 %. Then the optimal drawing against the reference, and the best ones generation after generation. One click loads it into the form.',
      s7t: 'Simulating the optimal case',
      s7p: 'The optimal drawing in Simulation mode: three days of July, with the fields of temperature and heat flux in the wall. Domus (the building and the street) and the wall model run together, step by step.',
      s8t: 'The fields in the wall', soon: 'Coming soon.', steps: 'Steps'
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
  // One screen held in place (sticky) while the page scrolls under it: the scrolling is the time of the film (PX
  // pixels per second). The steps are the clips of one take (tools/film/take.py: each starts on the last picture of
  // the one before) and, for step 3, the 3D viewer itself (viewer/index.html) laid over the 3D view of the picture,
  // moved by the scrolling until the visitor takes it in hand. media/film.json: durations, where the 3D view is.
  var film = document.getElementById('film');
  if (film) (function () {
    var screen = film.querySelector('.screen'), clipsBox = screen.querySelector('.clips'), stepsBox = film.querySelector('.steps');
    var steps = [].slice.call(film.querySelectorAll('.step')), N = steps.length;
    var cap = screen.querySelector('.cap');
    var ctl = screen.querySelector('.ctl'), playBtn = ctl.querySelector('.play'), track = ctl.querySelector('.track'), dots = track;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
    var CAP_S = 7;                 // seconds of film a card stays (from the start of its step)
    var TAU = reduce ? 0 : 0.11;   // smoothing of the scrolling (s): the wheel goes by notches
    var segs = [], total = 0, FR = [1440, 900], LIVE = null, ready = false;
    var PX = function () { return Math.max(70, window.innerHeight * 0.13); };

    // ---- the timeline, once film.json is read
    var build = function (cfg) {
      FR = cfg.frame || FR; LIVE = cfg.live || null;
      var t0 = 0;
      steps.forEach(function (st, k) {
        var id = st.dataset.id, s = {k: k, id: id, t0: t0, st: st};
        if (st.dataset.live) { s.kind = 'live'; s.dur = +st.dataset.dur; }
        else {
          s.kind = 'video'; s.dur = +(cfg.clips || {})[id] || 1;
          var v = document.createElement('video');
          v.className = 'v'; v.muted = true; v.playsInline = true; v.preload = 'none';
          v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
          v.poster = 'media/' + id + '_first.jpg'; v.dataset.src = 'media/' + id + '.mp4';
          clipsBox.appendChild(v); s.v = v;
        }
        t0 += s.dur; segs.push(s);
      });
      total = t0;
      // one dot per step on the track (where it starts)
      segs.forEach(function (s) {
        var d = document.createElement('a'); d.href = '#film'; d.style.top = (s.t0 / total * 100) + '%';
        d.onclick = function (e) { e.preventDefault(); e.stopPropagation(); stopAuto(); seekTo(s.t0 + .01, true); };
        dots.appendChild(d);
      });
      layout(); ready = true; window.__filmLang();
      requestAnimationFrame(loop);
    };
    var layout = function () {
      if (!segs.length) return;
      var px = PX();
      stepsBox.style.height = (total * px + window.innerHeight) + 'px';
      segs.forEach(function (s) { s.st.style.top = (s.t0 * px) + 'px'; s.st.style.height = (s.dur * px) + 'px'; });
    };
    var tOfScroll = function () { return Math.max(0, Math.min(total, (window.scrollY - film.offsetTop) / PX())); };
    var yOfT = function (t) { return film.offsetTop + t * PX(); };
    var seekTo = function (t, smooth) {
      window.scrollTo({top: yOfT(t), behavior: smooth && !reduce ? 'smooth' : 'instant'});
    };
    var segAt = function (t) {
      for (var i = segs.length - 1; i >= 0; i--) if (t >= segs[i].t0) return segs[i];
      return segs[0];
    };
    var onScreen = function () { var r = film.getBoundingClientRect(); return r.top < window.innerHeight * .5 && r.bottom > window.innerHeight * .5; };

    // ---- clips: loaded around the step shown; one shown at a time (the next starts on the last picture of the one before)
    var want = function (s) { if (s && s.v && !s.v.src) { s.v.preload = 'auto'; s.v.src = s.v.dataset.src; } };
    var shownV = null;
    var showVideo = function (s, local, follow) {      // follow: played (Play), not sought
      want(s); want(segs[s.k + 1]); want(segs[s.k - 1]);
      var v = s.v;
      if (shownV !== v) { if (shownV) { shownV.classList.remove('on'); shownV.pause(); } v.classList.add('on'); shownV = v; }
      if (follow) return;
      if (!v.paused) v.pause();
      var at = Math.max(0, Math.min(s.dur - 0.02, local));
      if (v.readyState >= 1 && !v.seeking && Math.abs(v.currentTime - at) > 0.017) {
        try { v.currentTime = at; } catch (e) { /* not seekable yet */ }
      }
    };

    // ---- the 3D view of step 3 (live): over the 3D view of the picture, then the whole screen, then back
    var live = screen.querySelector('.live'), frame = live.querySelector('iframe'), gate = live.querySelector('.gate');
    var tour = screen.querySelector('.tour'), resume = tour.querySelector('.resume');
    var W = null, free = false, lastU = null, blend = null, liveOn = false;
    var FADE = 0.8;              // seconds of film of the cross-fade picture <-> live view (each end)
    var EXP = 1.6;               // seconds of film to grow from the picture to the whole screen (and back at the end)
    var liveLoad = function (s) {
      if (frame.dataset.src) return;
      frame.dataset.src = s.st.dataset.live; frame.src = s.st.dataset.live;
      frame.addEventListener('load', function () {
        try {
          var w = frame.contentWindow;
          var take = function (e) { stopAuto(); if (e.type === 'wheel' && !e.ctrlKey) return; if (!free) setFree(true); };
          ['pointerdown', 'keydown', 'wheel'].forEach(function (k) { w.addEventListener(k, take, true); });
        } catch (e) { /* the page of the viewer is of the site: same origin */ }
      });
    };
    var api = function () { try { var w = frame.contentWindow; return w && w.__site && w.__site.ready ? w.__site : null; } catch (e) { return null; } };
    var setFree = function (on) {
      free = on; screen.classList.toggle('free', on);
      if (!on && W) { blend = {from: W.getPose(), t: performance.now()}; lastU = null; }
    };
    resume.onclick = function () { setFree(false); };
    gate.onclick = function () { stopAuto(); setFree(true); };
    var ease = function (x) { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };
    var lerp = function (a, b, f) { return a + (b - a) * f; };
    // the box of the picture of the film on the screen (object-fit: contain)
    var picBox = function () {
      var Ws = screen.clientWidth, Hs = screen.clientHeight, s = Math.min(Ws / FR[0], Hs / FR[1]);
      return {s: s, x: (Ws - FR[0] * s) / 2, y: (Hs - FR[1] * s) / 2};
    };
    var placeLive = function (p) {          // p: 0 = over the 3D view of the picture, 1 = the whole screen
      var b = picBox(), r = LIVE.rect, Ws = screen.clientWidth, Hs = screen.clientHeight;
      var x = lerp(b.x + r[0] * b.s, 0, p), y = lerp(b.y + r[1] * b.s, 0, p);
      var w = lerp(r[2] * b.s, Ws, p), h = lerp(r[3] * b.s, Hs, p), sc = lerp(Math.min(b.s, 1), 1, p);
      var key = [x, y, w, h, sc].map(function (v) { return v.toFixed(1); }).join();
      if (live.dataset.box === key) return;
      live.dataset.box = key;
      live.style.left = x + 'px'; live.style.top = y + 'px'; live.style.width = w + 'px'; live.style.height = h + 'px';
      frame.style.width = (w / sc) + 'px'; frame.style.height = (h / sc) + 'px'; frame.style.transform = 'scale(' + sc + ')';
      live.style.borderRadius = (6 * (1 - p)) + 'px';
      if (W) W.resize();                    // the viewer takes its new size at once (camera, canvas)
    };
    // the guided tour: camera, time and layer at u seconds of the step (a function of u only: both ways)
    var sph = function (P, daz, del, k) {    // the pose P turned round its target (degrees), its distance times k
      var p = P.pos, t = P.target, dx = p[0] - t[0], dy = p[1] - t[1], dz = p[2] - t[2];
      var d = Math.hypot(dx, dy, dz), az = Math.atan2(dx, dz) + daz * Math.PI / 180;
      var el = Math.asin(dy / d) + del * Math.PI / 180, r = d * k;
      return {pos: [t[0] + r * Math.cos(el) * Math.sin(az), t[1] + r * Math.sin(el), t[2] + r * Math.cos(el) * Math.cos(az)],
              target: t.slice(), fov: P.fov};
    };
    var KEYS = null;
    var keys = function () {
      if (KEYS) return KEYS;
      var P0 = LIVE.pose, D = segs.filter(function (s) { return s.kind === 'live'; })[0].dur;
      var fac = W.view('facade'), street = W.view('street');
      KEYS = {D: D, cam: [
        [0, P0], [EXP, P0],
        [7.5, sph(P0, -50, -6, .72)],
        [12.5, sph(P0, -105, -2, .62)],
        [15.5, fac], [21, sph(fac, 22, -4, .9)],
        [24.5, street], [28.5, street],
        [D - EXP - 1.2, P0], [D, P0]],
        // absolute hour (day 0 at 0): noon, the evening, the night (lit windows), the morning, the afternoon
        hour: [[0, 12], [EXP, 12], [9.5, 33], [13.5, 38], [28.5, 38], [D - EXP - 1.2, 36], [D, 36]],
        layer: [[10.2, 'sh'], [14.8, 'none'], [15.6, 'lw'], [23.2, 'none']],
        tool: [[24.5, 'street'], [28.6, null]]};
      return KEYS;
    };
    var track1 = function (K, u) {           // value of a list of [time, value] at u (smoothstep between keys)
      if (u <= K[0][0]) return {a: K[0][1], b: K[0][1], f: 0};
      for (var i = 1; i < K.length; i++) if (u <= K[i][0]) return {a: K[i - 1][1], b: K[i][1], f: ease((u - K[i - 1][0]) / (K[i][0] - K[i - 1][0]))};
      var l = K[K.length - 1][1]; return {a: l, b: l, f: 0};
    };
    var step1 = function (K, u, d) { var v = d; K.forEach(function (k) { if (u >= k[0]) v = k[1]; }); return v; };
    var mix = function (A, B, f) {
      return {pos: A.pos.map(function (v, i) { return lerp(v, B.pos[i], f); }), target: A.target.map(function (v, i) { return lerp(v, B.target[i], f); }),
              fov: lerp(A.fov, B.fov, f)};
    };
    var curLayer = null, curTool;
    var applyTour = function (u) {
      var K = keys(), c = track1(K.cam, u), pose = mix(c.a, c.b, c.f);
      if (blend) {                           // back from the visitor's camera to the tour, in 0.7 s
        var f = ease((performance.now() - blend.t) / 700);
        pose = mix(blend.from, pose, f); if (f >= 1) blend = null;
      }
      W.pose(pose);
      var h = track1(K.hour, u), ah = lerp(h.a, h.b, h.f);
      if (u >= K.D - EXP - 1.2 - 1e-6) ah = 12 + (ah - 36);      // the day of the picture again (same sun)
      W.time(Math.floor(ah / 24), ah - 24 * Math.floor(ah / 24));
      var ly = step1(K.layer, u, 'none');
      if (ly !== curLayer) { W.layer(ly); curLayer = ly; }
      var tl = step1(K.tool, u, null);
      if (tl !== curTool) { W.tool(tl); curTool = tl; }
    };
    var liveRender = function (s, u) {
      if (!W) W = api();
      if (!W || !LIVE) { liveHide(); return false; }
      // the picture under it: the last one of the step before (= the first of the next)
      var p = u < EXP ? ease(u / EXP) : u > s.dur - EXP ? ease((s.dur - u) / EXP) : 1;
      placeLive(p);
      // a cross-fade with the picture at both ends: the hub draws its 3D view a bit differently after Regenerate
      var o = Math.max(0, Math.min(1, u / FADE, (s.dur - u) / FADE)).toFixed(3);
      if (live.style.opacity !== o) live.style.opacity = o;
      if (!liveOn) { liveOn = true; screen.classList.add('live-on'); W.resize(); }
      var full = p > .98;
      if (full !== screen.classList.contains('touring')) { screen.classList.toggle('touring', full); W.hud(full); }
      // the end of the step: the tour takes the view back (the film goes on from its camera)
      if (free && u > s.dur - EXP - 1.4) setFree(false);
      if (!free && (lastU === null || Math.abs(u - lastU) > 1e-4 || blend)) { applyTour(u); lastU = u; }
      return true;
    };
    var liveHide = function () {
      if (!liveOn) return;
      liveOn = false; screen.classList.remove('live-on', 'touring'); if (W) W.hud(false);
      if (free) setFree(false);
      blend = null;
    };

    // ---- the cards, the dots, the track
    var curK = -1, capIn = false;
    var cards = function (s, local) {
      var t = T[lang];
      if (s.k !== curK) {
        curK = s.k;
        cap.classList.remove('in'); capIn = false;
        cap.querySelector('.num').textContent = ('0' + (s.k + 1)).slice(-2);
        cap.querySelector('h2').textContent = t[s.st.dataset.t];
        cap.querySelector('.txt').textContent = t[s.st.dataset.p];
        dots.querySelectorAll('a').forEach(function (d, i) { d.classList.toggle('on', i === s.k); });
      }
      var from = s.kind === 'live' ? EXP : 0.15, on = local >= from && local < from + CAP_S;
      if (on !== capIn) { capIn = on; cap.classList.toggle('in', on); }
    };
    window.__filmLang = function () {
      if (!ready) return;
      var t = T[lang];
      dots.setAttribute('aria-label', t.steps);
      dots.querySelectorAll('a').forEach(function (d, i) { d.title = t[steps[i].dataset.t]; });
      curK = -1; capIn = null;
      playBtn.title = auto ? t.pause : t.play;
    };

    // ---- play: scrolls by itself at the speed of the film (the clips play, the tour goes on); any hand stops it
    var auto = false, T0 = 0, shown = 0, last = null;
    var startAuto = function () {
      if (!ready) return;
      auto = true; screen.classList.add('auto'); playBtn.title = T[lang].pause;
      if (tOfScroll() >= total - .05) shown = 0;
      T0 = shown; seekTo(T0, false);
      if (free) setFree(false);
    };
    var stopAuto = function () {
      if (!auto) return;
      auto = false; screen.classList.remove('auto'); playBtn.title = T[lang].play;
      segs.forEach(function (s) { if (s.v && !s.v.paused) s.v.pause(); });
    };
    playBtn.onclick = function () { if (auto) stopAuto(); else startAuto(); };
    var watch = document.querySelector('.watch');
    if (watch) watch.onclick = function () { shown = 0; seekTo(0, false); setTimeout(startAuto, 50); };
    ['wheel', 'touchstart', 'mousedown'].forEach(function (k) {
      window.addEventListener(k, function (e) { if (auto && !(e.target.closest && e.target.closest('.ctl'))) stopAuto(); }, {passive: true});
    });
    window.addEventListener('keydown', function (e) {
      if (auto && ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', ' ', 'Home', 'End'].indexOf(e.key) >= 0) stopAuto();
    });
    track.onclick = function (e) {
      var r = track.getBoundingClientRect(); stopAuto(); seekTo(total * Math.max(0, Math.min(1, (e.clientY - r.top) / r.height)), true);
    };

    // ---- each frame of the browser
    var loop = function (now) {
      requestAnimationFrame(loop);
      var dt = last === null ? 0 : Math.min(.1, (now - last) / 1000); last = now;
      var target = tOfScroll();
      if (auto) {
        var s = segAt(T0);
        if (s.kind === 'video') {
          var v = s.v, loc = T0 - s.t0;
          want(s); want(segs[s.k + 1]);
          if (shownV !== v) showVideo(s, loc, true);
          if (v.paused && v.readyState >= 2) {
            if (Math.abs(v.currentTime - loc) > .05) v.currentTime = loc;
            if (loc < s.dur - .05) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); }
          } else if (!v.paused && !v.seeking) T0 = s.t0 + v.currentTime;
          if (v.ended || loc >= s.dur - .04) { v.pause(); T0 = s.t0 + s.dur + 1e-3; }
        } else T0 += dt;
        if (T0 >= total) { T0 = total; stopAuto(); }
        seekTo(T0, false);
        shown = T0;
      } else if (!TAU || Math.abs(target - shown) < .004) shown = target;
      else shown += (target - shown) * (1 - Math.exp(-dt / TAU));
      if (!onScreen()) { if (shownV && !shownV.paused) shownV.pause(); liveHide(); screen.classList.remove('shown'); return; }
      screen.classList.add('shown');
      var seg = segAt(shown), local = shown - seg.t0;
      if (seg.kind === 'live') {
        liveLoad(seg);
        var before = segs[seg.k - 1];
        if (before && before.v) showVideo(before, before.dur);       // under the viewer: the end of step 2
        if (!liveRender(seg, local) && before && before.v) { /* viewer not ready: the picture stays */ }
      } else {
        showVideo(seg, local, auto);
        liveHide();
        var nx = segs[seg.k + 1];
        if (nx && nx.kind === 'live' && local > seg.dur * .5) liveLoad(nx);   // ready by the end of the step
      }
      cards(seg, local);
      ctl.querySelector('.fill').style.height = (shown / total * 100) + '%';
      screen.classList.toggle('at-end', shown >= total - .05);
      screen.classList.toggle('at-start', shown < 1.2);
    };
    window.addEventListener('resize', function () { layout(); if (liveOn) live.dataset.box = ''; });

    // media/film.js (a script: read also when the page is opened as a file), else media/film.json
    if (window.TOPS_FILM) build(window.TOPS_FILM);
    else fetch('media/film.json').then(function (r) { return r.json(); }).then(build, function () {
      cap.querySelector('h2').textContent = 'media/film.json ?'; cap.classList.add('in');
    });
    window.__film = {get t() { return shown; }, get total() { return total; }, segs: segs,
                     get free() { return free; }, get auto() { return auto; }, seek: function (t) { stopAuto(); seekTo(t, false); }};
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
