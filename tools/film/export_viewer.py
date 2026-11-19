# -*- coding: utf-8 -*-
"""The 3D viewer of the hub for the page of the site (step 3: the visitor walks through the scene himself, the page
moves the camera, the time and the layers as one scrolls until he takes the view).

    python tools/film/export_viewer.py [--port 8811] [--idf demo_street]

Takes the viewer the hub for tests wrote for the last scene of the take (_runs/xdomf90/idf_preview_<port>_<pc>.html,
self-contained: the scene is in the page) and writes viewer/index.html + viewer/vendor/ (three.js r128 of the hub):
  - the scripts of the hub (/vendor/...) read next to the page;
  - no Studio (pictures, videos: they need the hub), no tooltips of the hub;
  - the layer "View factors" shows the view factors of the Studio (computed as the FMU, asked here to the hub:
    /view_factors), not the estimates of the viewer;
  - in the page of the site: the wheel scrolls the page, Ctrl + wheel (pinch of a touchpad) zooms; window.__site:
    what the page drives (camera, time, layer);
  - the look of the film the first time (realistic, the quarter around, sun path), as in the take (rec.DEMO);
  - checked: no path of this computer nor e-mail address in the page.
"""
import argparse, json, os, re, shutil, socket, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, '..', '..'))
HUB = os.path.normpath(os.path.join(SITE, '..', '..', 'env', 'hubgui'))
OUT = os.path.join(SITE, 'viewer')
VENDOR = ('three.min.js', 'OrbitControls.js', 'Sky.js')

# the look of the 3D view of the film (rec.DEMO), given at each visit: the viewer starts over the picture of the film
# and must show the same (touch screens, phones: no shadows of the quarter, lighter)
FIRST = {'xdomf90_real': '1', 'xdomf90_decor': json.dumps({'mode': 'quarter', 'shadows': True}),
         'xdomf90_hudfold': '1', 'xdomf90_sunpath': '1', 'xdomf90_layers_open': '0', 'xdomf90_lw': '0'}
HEAD = ('<script>/* site: the look of the 3D view of the film */ (() => { try { const F = %s;'
        ' if (matchMedia("(pointer: coarse)").matches) F.xdomf90_decor = %s;'
        ' for (const k in F) localStorage.setItem(k, F[k]); } catch (e) {} })();'
        '</script>\n' % (json.dumps(FIRST), json.dumps(json.dumps({'mode': 'quarter', 'shadows': False}))))

# after the script of the viewer (its globals: THREE, scene, camera, controls, setTime, viewOf, setLw, lwOn...)
TAIL = r'''<script>/* site (tools/film/export_viewer.py): view factors of the Studio, wheel, what the page drives */
(() => {
'use strict';
const inPage = window.parent !== window;
// ---- the wheel scrolls the page; Ctrl + wheel (pinch of a touchpad) zooms; in full screen the wheel zooms
addEventListener('wheel', e => {
  if (!inPage || e.ctrlKey || document.fullscreenElement) return;
  e.preventDefault(); e.stopImmediatePropagation();
  const k = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? innerHeight : 1;
  try { parent.scrollBy({top: e.deltaY * k, behavior: 'instant'}); } catch (er) {}
}, {capture: true, passive: false});
// the bars of the view, shown on hover in the hub (embedded): shown by the page while the view fills the screen
const hudCss = document.createElement('style');
hudCss.textContent = ['#timebar', '#hud', '#compass'].map(e => 'html.embedded.site-hud body:not(:hover) ' + e).join(',') + '{opacity:1}';
document.head.appendChild(hudCss);
if (inPage) document.querySelectorAll('#hint span').forEach(s => { if (/scroll = zoom/.test(s.textContent)) s.textContent = 'Ctrl + scroll = zoom'; });

// ---- view factors of the Studio (v3dstudio.js vfBuild: density dF/dA, log scale), in place of the estimates
const R = __VFR__;
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const dens = R.elements.filter(e => e.F > 0).map(e => e.F / e.A);
const hi = Math.max(...dens, 1e-12), lo = Math.max(Math.min(...dens), hi * 1e-4), L = Math.log(hi) - Math.log(lo);
const vfColor = e => !(e.F > 0) ? '#4a4f57' : lwMapColor(L > 1e-12 ? (Math.log(hi) - Math.log(clamp(e.F / e.A, lo, hi))) / L : 0);
const SPAN_B = (() => {
  const a = [Infinity, Infinity, Infinity], b = [-Infinity, -Infinity, -Infinity];
  faceMeshes.forEach(f => { if (f.type === 'ground') return; f.verts.forEach(v => v.forEach((x, i) => { a[i] = Math.min(a[i], x); b[i] = Math.max(b[i], x); })); });
  return isFinite(a[0]) ? Math.max(b[0] - a[0], b[2] - a[2], 5) : span;
})();
const near = e => Math.max(...[1, 3].map(j => Math.hypot(...[0, 1, 2].map(a => e.pts[j][a] - e.pts[0][a])))) <= SPAN_B;
let grp = null;
function build() {
  const Fa = R.facade, ctr = new THREE.Vector3(...Fa.P0.map((v, j) => v + 0.5 * Fa.W * Fa.ex[j] + 0.5 * Fa.H * Fa.ey[j]));
  const vis = grp ? grp.visible : false;
  if (grp) { scene.remove(grp); grp.traverse(o => { o.geometry && o.geometry.dispose(); o.material && o.material.dispose(); }); }
  const pos = [], col = [], line = [], n = new THREE.Vector3(), c = new THREE.Color();
  R.elements.forEach(e => {
    if (!near(e)) return;
    const p = e.pts.map(v => new THREE.Vector3(...v));
    n.subVectors(p[1], p[0]).cross(new THREE.Vector3().subVectors(p[3], p[0])).normalize();
    const cen = p.reduce((a, b) => a.add(b.clone()), new THREE.Vector3()).multiplyScalar(0.25);
    if (n.dot(ctr.clone().sub(cen)) < 0) n.negate();
    const q = p.map(v => v.clone().addScaledVector(n, Math.abs(n.y) > 0.9 ? (realOn ? 0.17 : 0.06) : 0.03));
    c.set(vfColor(e)); if (realOn) c.convertSRGBToLinear();
    [0, 1, 2, 0, 2, 3].forEach(i => { pos.push(q[i].x, q[i].y, q[i].z); col.push(c.r, c.g, c.b); });
    [0, 1, 1, 2, 2, 3, 3, 0].forEach(i => line.push(q[i].x, q[i].y, q[i].z));
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  const m = new THREE.MeshBasicMaterial({vertexColors: true, side: THREE.DoubleSide, toneMapped: false, fog: false,
    polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4});
  const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(line, 3));
  grp = new THREE.Group();
  grp.add(new THREE.Mesh(g, m));
  grp.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({color: 0x0a0e13, transparent: true, opacity: 0.35})));
  const sl = [];
  R.strips_y.forEach((y, i) => { if (i % 5 && i !== R.strips_y.length - 1) return;
    const a = Fa.P0.map((v, j) => v + y * Fa.ey[j] + 0.05 * Fa.n[j]), b = a.map((v, j) => v + Fa.W * Fa.ex[j]); sl.push(...a, ...b); });
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sl, 3));
  grp.add(new THREE.LineSegments(sg, new THREE.LineBasicMaterial({color: 0xffffff, transparent: true, opacity: 0.7})));
  grp.visible = vis; scene.add(grp);
}
build();
window.v3dOnReal = () => { build(); invalidate(); };
const lgd = document.getElementById('lwLegend'), chk = document.getElementById('lwChk'), tog = document.getElementById('lwToggle');
const pct = v => (v * 100).toFixed(1) + ' %', fmt = v => v >= 1 ? v.toFixed(2) : v >= 0.01 ? v.toFixed(3) : v.toExponential(1);
lgd.innerHTML = '<div style="font-weight:600;margin-bottom:3px">View factors of the studied facade</div>'
  + '<div style="opacity:.8;margin-bottom:4px">computed as the wall model (FMU)</div>'
  + '<div style="height:8px;border-radius:3px;background:linear-gradient(90deg,' + LW_MAP.join(',') + ')"></div>'
  + '<div style="display:flex;justify-content:space-between;margin:2px 0 5px;font:10px \'Cascadia Mono\',Consolas,monospace;opacity:.8">'
  + '<span>' + fmt(hi) + ' m⁻²</span><span>dF/dA, log</span><span>' + fmt(lo) + '</span></div>'
  + '<div>sky ' + pct(R.sky) + ' · ground ' + pct(R.soil) + ' · surroundings ' + pct(R.ext) + '</div>';
tog.hidden = false;
tog.title = 'Surfaces seen by the studied facade, coloured by their view factor density, computed as the wall model';
setLw = on => {
  if (on) exclusiveOverlay('lw');
  lwOn = on; lwGroup.visible = false; grp.visible = on;
  lgd.style.display = on ? 'block' : 'none'; chk.checked = on;
  updLayers(); invalidate();
};
chk.onchange = () => setLw(chk.checked);
if (lwOn) setLw(true); else lwGroup.visible = false;

// ---- what the page of the site drives (its scrolling): camera, time, layer
const v3 = a => new THREE.Vector3(...a);
window.__site = {
  ready: true,
  pose(p) { flight = null; camera.position.copy(v3(p.pos)); controls.target.copy(v3(p.target));
    if (p.fov && Math.abs(camera.fov - p.fov) > 1e-6) { camera.fov = p.fov; camera.updateProjectionMatrix(); }
    controls.update(); invalidate(); },
  getPose() { return {pos: camera.position.toArray(), target: controls.target.toArray(), fov: camera.fov}; },
  view(name) { const v = viewOf(name); return {pos: v.pos.toArray(), target: v.target.toArray(), fov: v.fov}; },
  time(day, h) { if (playing) setPlaying(false); if (day !== dayIdx || Math.abs(h - hour) > 1e-4) { dayF = day; setTime(day, h); } invalidate(); },
  getTime() { return [dayIdx, hour]; },
  layer(name) {
    const sh = document.getElementById('shChk');
    if (name === 'lw') { if (!lwOn) setLw(true); }
    else if (name === 'sh') { if (!sh.checked) { sh.checked = true; sh.onchange(); } }
    else { exclusiveOverlay(null); document.getElementById('noneChk').checked = true; updLayers(); }
    invalidate();
  },
  tool(name) { document.querySelectorAll('#tools button[data-v]').forEach(b => b.classList.toggle('on', b.dataset.v === name)); },
  resize() { dispatchEvent(new Event('resize')); invalidate(); },
  hud(on) { document.documentElement.classList.toggle('site-hud', !!on); }
};
})();
</script>
'''

KEEP = ('pts', 'A', 'F', 'g')


def view_factors(port, idf):
    """The view factors of the Studio for the scene of the project (hub for tests: /view_factors), kept small."""
    def post(d):
        q = urllib.request.Request('http://127.0.0.1:%d/view_factors' % port, data=json.dumps(d).encode(),
                                   headers={'Content-Type': 'application/json'})
        return json.load(urllib.request.urlopen(q, timeout=600))
    t = time.time()
    while True:
        r = post({'model': 'xdomf90', 'params': {'idf': idf}})
        if not r.get('ok'):
            sys.exit('export_viewer: view factors: %s' % r.get('error'))
        if not r.get('running'):
            break
        if time.time() - t > 900:
            sys.exit('export_viewer: view factors not computed after 15 min')
        time.sleep(1)
    rd = lambda v: round(v, 4) if isinstance(v, float) else [rd(x) for x in v] if isinstance(v, list) else v
    out = {'facade': {k: rd(v) for k, v in r['facade'].items()}, 'strips_y': rd(r['strips_y']),
           'sky': r['sky'], 'soil': r['soil'], 'ext': r['ext'], 'fmu': r.get('fmu'),
           'elements': [{k: (rd(e[k]) if k == 'pts' else e[k]) for k in KEEP} for e in r['elements']]}
    print('view factors: %d elements, sky %.3f ground %.3f surroundings %.3f (%s)'
          % (len(out['elements']), r['sky'], r['soil'], r['ext'], 'strips of the FMU' if r.get('fmu') else 'strips of 5 cm'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8811)
    ap.add_argument('--idf', default='demo_street')
    a = ap.parse_args()
    src = os.path.join(HUB, '_runs', 'xdomf90', 'idf_preview_%d_%s.html' % (a.port, socket.gethostname().lower()))
    with open(src, encoding='utf-8') as fh:
        s = fh.read()
    n0 = len(s)
    if not re.search(r'"idf_name":\s*%s' % re.escape(json.dumps(a.idf)), s):
        sys.exit('export_viewer: the viewer of the hub shows another project than %s' % a.idf)

    def sub(pat, rep, count=1):
        nonlocal s
        s, k = re.subn(pat, rep, s)
        if k != count:
            sys.exit('export_viewer: %r found %d times (%d expected): the viewer of the hub has changed' % (pat, k, count))

    sub(r'<script src="/vendor/three\.min\.js"></script>', '<script src="vendor/three.min.js"></script>')
    sub(r"\['/vendor/OrbitControls\.js', '/vendor/Sky\.js'\]", "['vendor/OrbitControls.js', 'vendor/Sky.js']")
    tail = TAIL.replace('__VFR__', json.dumps(view_factors(a.port, a.idf), separators=(',', ':')))
    sub(r'<!-- studio \(pictures, videos, view factors\): files of the hub -->\s*<link[^>]*v3dstudio\.css">'
        r'<script src="/js/v3dstudio\.js"></script><script src="/js/ux-tip\.js"></script>', lambda m: tail)
    sub(r'\s*<button id="studioBtn".*?</button>', '')
    sub(r'<title>IDF — 3D viewer</title>', '<title>TOPS — 3D view</title>')
    sub(r'(<head><meta charset="utf-8">)', lambda m: m.group(1) + '\n' + HEAD)
    if re.search(r'''["']/(?:vendor|js|css)/''', s):
        sys.exit('export_viewer: a file of the hub is still read: %s' % re.findall(r'["\'](/(?:vendor|js|css)/[^"\']*)', s))
    bad = re.findall(r'[A-Za-z]:\\\\|Users[\\/]|OneDrive|[\w.+-]+@[\w-]+\.[A-Za-z]{2,}', s)
    if bad:
        sys.exit('export_viewer: private text in the viewer: %s' % sorted(set(bad))[:5])

    os.makedirs(os.path.join(OUT, 'vendor'), exist_ok=True)
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)
    for f in VENDOR:
        shutil.copy2(os.path.join(HUB, 'web', 'vendor', f), os.path.join(OUT, 'vendor', f))
    print('viewer/index.html (%d -> %d characters) + vendor/%s' % (n0, len(s), ', '.join(VENDOR)))


if __name__ == '__main__':
    main()
