/* TOPS — prototype of the "scene" chapter: a three.js view of canyon_street_1 driven by the scroll.
   Story time s = index of the step + progress inside it (0..1). Everything (camera, buildings, light)
   is a function of s, so scrolling back and forth plays the story both ways. */
(function () {
  'use strict';
  var D = window.SCENE;
  var canvas = document.getElementById('scene');
  var steps = Array.prototype.slice.call(document.querySelectorAll('.step'));
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- helpers
  var clamp = function (x, a, b) { return Math.max(a, Math.min(b, x)); };
  var ease = function (t) { t = clamp(t, 0, 1); return t * t * t * (t * (t * 6 - 15) + 10); };   // smootherstep
  var win = function (s, a, b) { return ease((s - a) / (b - a)); };
  var V3 = THREE.Vector3;

  // ---------- renderer, scene
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.9;

  var scene = new THREE.Scene();
  var BG_NIGHT = new THREE.Color('#0b0f15'), BG_DAY = new THREE.Color('#2a3a4f');
  scene.background = BG_NIGHT.clone();
  scene.fog = new THREE.Fog(scene.background, 70, 170);
  var camera = new THREE.PerspectiveCamera(38, 1, 0.1, 600);

  var hemi = new THREE.HemisphereLight('#c9dcff', '#3a3026', 0.55);
  scene.add(hemi);
  var sun = new THREE.DirectionalLight('#fff1dc', 2.2);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -36; sun.shadow.camera.right = 36;
  sun.shadow.camera.top = 36; sun.shadow.camera.bottom = -36;
  sun.shadow.camera.near = 1; sun.shadow.camera.far = 160;
  sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.06;
  scene.add(sun); scene.add(sun.target);

  // ground beyond the ±50 m of the idf, lost in the fog
  var far = new THREE.Mesh(new THREE.CircleGeometry(400, 64),
    new THREE.MeshStandardMaterial({ color: '#2b2722', roughness: 1 }));
  far.rotation.x = -Math.PI / 2; far.position.y = -0.03; far.receiveShadow = true;
  scene.add(far);

  // ---------- colors
  var COL = {
    ground: '#2b2622', zone1: '#ff8a3d', studied: '#e8dcc6', window: '#8fb3d1', overhang: '#b9b4ab',
    roof: '#b8674d', other: ['#d9ccb8', '#cdbfa9', '#c7c3b8'], dim: '#262c34'
  };
  var buildingOf = function (z) {
    if (z === 'Zone 1') return 'Zone 1';
    if (z === 'Solo 01') return 'ground';
    if (z === 'Overhangs') return 'S';        // window reveals and balconies of the studied building: move with it
    return z.split('_')[0];
  };
  var colorOf = function (f) {
    if (f.k === 'window') return COL.window;
    if (f.z === 'Zone 1') return COL.zone1;
    if (f.z === 'Solo 01') return COL.ground;
    if (f.z === 'Overhangs') return COL.overhang;
    if (/_roof$/.test(f.z)) return COL.roof;
    var b = f.z.split('_')[0];
    if (b === 'S') return COL.studied;
    var h = 0; for (var i = 0; i < b.length; i++) h += b.charCodeAt(i);
    return COL.other[h % COL.other.length];
  };

  // ---------- meshes: one group per (variant, building), faces fan-triangulated, one material per color
  var mats = {};
  var matOf = function (hex) {
    if (!mats[hex]) {
      var m = hex === COL.window
        ? new THREE.MeshStandardMaterial({ color: hex, roughness: .25, metalness: .35, side: THREE.DoubleSide })
        : new THREE.MeshStandardMaterial({ color: hex, roughness: .88, side: THREE.DoubleSide });
      m.userData.base = new THREE.Color(hex);
      // faces pushed back a little: the outlines of the idf faces stay on top
      m.polygonOffset = true; m.polygonOffsetFactor = 1; m.polygonOffsetUnits = 1;
      mats[hex] = m;
    }
    return mats[hex];
  };
  var lineMat = new THREE.LineBasicMaterial({ color: '#ffb877', transparent: true, opacity: 0, depthTest: true });
  var buildGroup = function (faces) {
    var byCol = {};
    faces.forEach(function (f) { (byCol[colorOf(f)] = byCol[colorOf(f)] || []).push(f); });
    var g = new THREE.Group();
    Object.keys(byCol).forEach(function (hex) {
      var pos = [];
      byCol[hex].forEach(function (f) {
        var v = f.v;
        for (var i = 1; i + 1 < v.length; i++) pos.push(v[0][0], v[0][1], v[0][2], v[i][0], v[i][1], v[i][2], v[i + 1][0], v[i + 1][1], v[i + 1][2]);
      });
      var geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      geo.computeVertexNormals();
      var m = new THREE.Mesh(geo, matOf(hex));
      m.castShadow = hex !== COL.ground; m.receiveShadow = true;
      g.add(m);
    });
    // outlines of the idf faces (step 01: "the scene is written in the idf")
    var seg = [];
    faces.forEach(function (f) {
      if (f.z === 'Solo 01') return;
      var v = f.v;
      for (var i = 0; i < v.length; i++) { var a = v[i], b = v[(i + 1) % v.length]; seg.push(a[0], a[1], a[2], b[0], b[1], b[2]); }
    });
    if (seg.length) {
      var lg = new THREE.BufferGeometry();
      lg.setAttribute('position', new THREE.Float32BufferAttribute(seg, 3));
      g.add(new THREE.LineSegments(lg, lineMat));
    }
    return g;
  };

  // the story of step 03: the project, three changes, back to the project
  var SEQ = [
    { v: 'base', label: 'canyon_street_1', code: 'le projet' },
    { v: 'floors', label: 'Bâtiment étudié sur 4 niveaux', code: 'floors_1 : 2 → 4' },
    { v: 'street', label: 'Rue élargie', code: 'DX : 5 → 10 m' },
    { v: 'flat', label: 'Sans toits en pente', code: 'roofs : all → off' },
    { v: 'base', label: 'Retour au projet', code: 'canyon_street_1' }
  ];
  var VAR = {};
  D.variants.forEach(function (v) {
    var by = {};
    v.faces.forEach(function (f) { var b = buildingOf(f.z); (by[b] = by[b] || []).push(f); });
    VAR[v.key] = { sig: {}, groups: {} };
    Object.keys(by).forEach(function (b) {
      VAR[v.key].sig[b] = JSON.stringify(by[b]);
      var g = buildGroup(by[b]);
      g.visible = false;
      g.userData.b = b;
      scene.add(g);
      VAR[v.key].groups[b] = g;
    });
  });
  var NZONES = {};
  D.variants[0].faces.forEach(function (f) { NZONES[f.z] = 1; });
  var IDF_COUNT = D.variants[0].faces.length + ' faces · ' + Object.keys(NZONES).length + ' zones';

  // glow on the studied facade (z = 0 face of Zone 1)
  var glow = new THREE.Mesh(new THREE.PlaneGeometry(4, 3),
    new THREE.MeshBasicMaterial({ color: COL.zone1, transparent: true, opacity: 0, depthWrite: false }));
  glow.position.set(0, 1.5, 0.04);
  scene.add(glow);

  // ---------- sun (NOAA, 21 June, standard time of the site)
  var sunAt = function (hour) {
    var doy = 172, g = 2 * Math.PI / 365 * (doy - 1 + (hour - 12) / 24);
    var eqt = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g) - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));
    var decl = 0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g) - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g) - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
    var tst = hour * 60 + eqt + 4 * D.lon - 60 * D.tz;
    var ha = (tst / 4 - 180) * Math.PI / 180, lat = D.lat * Math.PI / 180;
    var cz = Math.sin(lat) * Math.sin(decl) + Math.cos(lat) * Math.cos(decl) * Math.cos(ha);
    var alt = Math.asin(clamp(cz, -1, 1));
    var az = Math.atan2(Math.sin(ha), Math.cos(ha) * Math.sin(lat) - Math.tan(decl) * Math.cos(lat)) + Math.PI;  // from north, clockwise
    // scene: x east, y up, z south (north of the idf = -z)
    return { alt: alt, dir: new V3(Math.sin(az) * Math.cos(alt), Math.sin(alt), -Math.cos(az) * Math.cos(alt)) };
  };

  // ---------- camera keys, one per step (+ the end)
  var KEYS = [
    { p: [58, 46, 70], t: [-3, 2, 8] },     // hero
    { p: [40, 30, 52], t: [-3, 2, 8] },     // 01 build
    { p: [5, 13, 17], t: [0, 1.8, 0] },     // 02 Zone 1, over the opposite row
    { p: [-34, 40, 56], t: [-3, 3, 9] },    // 03 variants: the whole street, from the south-west
    { p: [30, 30, 44], t: [-2, 2, 6] },     // 04 sun: the facade and the shadows on the street
    { p: [3.2, 2.6, 4.7], t: [0, 1.5, 0] }, // 05 facade, from the street
    { p: [2.4, 2.2, 4.2], t: [0, 1.5, 0] }  // end
  ].map(function (k) { return { p: new V3().fromArray(k.p), t: new V3().fromArray(k.t) }; });

  // ---------- scroll -> story time
  var nav = document.getElementById('dots');
  steps.forEach(function (el, i) {
    var a = document.createElement('a'); a.href = '#'; a.setAttribute('aria-label', 'Étape ' + i);
    a.onclick = function (e) { e.preventDefault(); window.scrollTo({ top: el.offsetTop, behavior: reduce ? 'auto' : 'smooth' }); };
    nav.appendChild(a);
  });
  var dots = nav.children;
  var vlist = document.getElementById('vlist');
  SEQ.forEach(function (q) {
    var li = document.createElement('li');
    li.innerHTML = '<span>' + q.label + '</span><code>' + q.code + '</code>';
    vlist.appendChild(li);
  });
  var storyTime = function () {
    var y = window.scrollY + window.innerHeight * 0.5;
    for (var i = steps.length - 1; i >= 0; i--) {
      var el = steps[i];
      // the hero starts at the top of the page (its centre line is already half way down at load)
      if (i === 0) return clamp(window.scrollY / (el.offsetHeight - window.innerHeight * 0.5 || 1), 0, 1);
      if (y >= el.offsetTop) return i + clamp((y - el.offsetTop) / el.offsetHeight, 0, 1);
    }
    return 0;
  };

  // ---------- state of the scene at story time s
  var chip = document.getElementById('chip'), clock = document.getElementById('clock'), clockH = document.getElementById('clockH');
  var IDX = { hero: 0, build: 1, zone: 2, variants: 3, sun: 4, facade: 5 };
  var want = { p: KEYS[0].p.clone(), t: KEYS[0].t.clone() }, cur = null;
  var lastStep = -1, lastSeq = -1, lastChip = '';

  var apply = function (s, time) {
    // camera
    var i = Math.min(KEYS.length - 2, Math.floor(s)), f = ease(s - i);
    // hold the wide view during the changes and during the day of sun
    if (i === IDX.variants || i === IDX.sun) f = ease((s - i - .6) / .4);
    want.p.lerpVectors(KEYS[i].p, KEYS[i + 1].p, f);
    want.t.lerpVectors(KEYS[i].t, KEYS[i + 1].t, f);
    if (!reduce) {        // slow turn around the target: wide on the title, a breath afterwards
      var amp = 0.05 + 0.3 * (1 - win(s, 0.2, 0.9));
      var a = Math.sin(time * 0.00011) * amp, o = want.p.clone().sub(want.t);
      o.applyAxisAngle(new V3(0, 1, 0), a); want.p.copy(want.t).add(o);
    }

    // outlines of the idf faces during step 01
    lineMat.opacity = 0.85 * win(s, 0.55, 1.05) * (1 - win(s, 1.7, 2.0));

    // buildings: the variants of step 03
    var rise = function () { return 1; };
    var vt = clamp((s - IDX.variants - .08) / .8, 0, 1) * (SEQ.length - 1);
    var k = Math.min(SEQ.length - 2, Math.floor(vt)), fk = vt - k;
    var A = VAR[SEQ[k].v], B = VAR[SEQ[k + 1].v];
    Object.keys(VAR).forEach(function (key) {
      Object.keys(VAR[key].groups).forEach(function (b) { VAR[key].groups[b].visible = false; });
    });
    var all = {}; Object.keys(A.groups).concat(Object.keys(B.groups)).forEach(function (b) { all[b] = 1; });
    Object.keys(all).forEach(function (b) {
      var r = b === 'ground' ? 1 : rise(b);
      var same = A.sig[b] && A.sig[b] === B.sig[b];
      var show = function (g, h) { if (!g || h <= 0.001) return; g.visible = true; g.scale.set(1, h, 1); };
      if (same || s < IDX.variants) { show(A.groups[b], r); return; }
      show(A.groups[b], r * (1 - ease(fk / .42)));
      show(B.groups[b], r * ease((fk - .58) / .42));
    });

    // highlight of Zone 1 (steps 02 and 05)
    var dim = win(s, 1.65, 2.1) * (1 - win(s, 2.75, 3.1)) + win(s, 4.75, 5.2);
    Object.keys(mats).forEach(function (hex) {
      var m = mats[hex];
      if (hex === COL.zone1) { m.emissive = m.emissive || new THREE.Color(); m.emissive.set(COL.zone1).multiplyScalar(.35 * dim); return; }
      if (hex === COL.ground) return;
      m.color.copy(m.userData.base).lerp(new THREE.Color(COL.dim), dim * .78);
    });
    glow.material.opacity = win(s, 4.8, 5.3) * (0.18 + 0.1 * Math.sin(time * 0.003));

    // sun: 17 h until step 04, a whole day during it, 15 h after
    var hour = s < IDX.sun ? 19.6 - 2.6 * win(s, 0.2, 1.2) : s < IDX.sun + 1 ? 5.5 + 16 * clamp((s - IDX.sun - .05) / .9, 0, 1) : 15;
    var S = sunAt(hour), day = clamp(Math.sin(S.alt) * 3, 0, 1);
    sun.position.copy(S.dir).multiplyScalar(80).add(new V3(-3, 0, 6));
    sun.target.position.set(-3, 0, 6);
    sun.intensity = 2.0 * day;
    sun.color.set(S.alt < 0.25 ? '#ffc58f' : '#fff1dc');
    hemi.intensity = 0.25 + 0.4 * day;
    scene.background.copy(BG_NIGHT).lerp(BG_DAY, 0.55 * day);
    scene.fog.color.copy(scene.background);

    // text and HUD
    var st = Math.min(steps.length - 1, Math.floor(s + .12));
    if (st !== lastStep) {
      steps.forEach(function (el, j) { el.classList.toggle('on', j === st); dots[j].classList.toggle('on', j === st); });
      lastStep = st;
    }
    var inVar = s > IDX.variants + .05 && s < IDX.variants + .97, q = Math.round(vt);
    var inIdf = s > IDX.build - .1 && s < IDX.build + .75;
    chip.classList.toggle('on', inVar || inIdf);
    var txt = inIdf ? 'canyon_street_1.idf &nbsp;<code>' + IDF_COUNT + '</code>'
      : SEQ[q].label + ' &nbsp;<code>' + SEQ[q].code + '</code>';
    if (txt !== lastChip) { chip.innerHTML = txt; lastChip = txt; }
    if (q !== lastSeq) {
      Array.prototype.forEach.call(vlist.children, function (li, j) { li.classList.toggle('on', j === q); });
      lastSeq = q;
    }
    clock.classList.toggle('on', s > IDX.sun - .05 && s < IDX.sun + 1);
    var hh = Math.floor(hour), mm = Math.floor((hour - hh) * 60 / 5) * 5;
    clockH.textContent = (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
  };

  // ---------- loop
  var resize = function () {
    var w = window.innerWidth, h = window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.fov = w < 720 ? 52 : 38;                 // phones: wider lens, the scene stays in frame
    camera.updateProjectionMatrix();
  };
  window.addEventListener('resize', resize);
  resize();

  var last = 0, renderMs = 0;
  var frame = function (time) {
    time = time || 0;
    apply(storyTime(), time);
    if (!cur) cur = { p: want.p.clone(), t: want.t.clone() };
    // damping in time, not per frame (same glide at 30, 60 or 144 images/s): ~0.2 s time constant
    var dt = Math.min(0.5, last ? (time - last) / 1000 : 0.016); last = time;
    var k = reduce ? 1 : 1 - Math.exp(-dt / 0.2);
    cur.p.lerp(want.p, k); cur.t.lerp(want.t, k);
    camera.position.copy(cur.p); camera.lookAt(cur.t);
    var t0 = performance.now();
    renderer.render(scene, camera);
    renderMs = performance.now() - t0;
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
  window.TOPS_DEBUG = { camera: camera, want: want, get cur() { return cur; }, get renderMs() { return renderMs; }, storyTime: storyTime };
})();
