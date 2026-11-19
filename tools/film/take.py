# -*- coding: utf-8 -*-
"""The film of the site, in one take cut into steps (media/<step>.mp4; each step starts on the last picture of the
one before it: the page plays them one after the other as the visitor scrolls, one continuous film).

  s1_open   TOPS opens (start page), the home, a click on the Domus co-simulation: the demo project in the 3D view
  s2_scene  the urban scene is changed in the form, seen at once on the urban plan; the button beside Run
            (Regenerate IDF) writes the idf and the 3D view shows the new scene (the Domus sizing is cut out):
            canyon_street_1 again, the project of the optimisation and of the simulation that follow
  s3_view   the 3D view in full screen: turned round, the time played (sun, shadows, passers-by), the hours of sun
            on the faces, the view factors of the studied facade (Studio, computed as the FMU: cut out), the street
            at eye level, back to the 3D view. The page then puts the viewer itself in place of the film
            (viewer/index.html, made by export_viewer.py from the viewer of the hub at the end of the take)

Before a take (the demo project must be in its first state, the terminal of the hub empty):
    1. hub for tests: launch.json "hubtest" (8811)
    2. python tools/film/demo_regen.py         (demo_street back to the scene of the film)
    3. hub for tests started again               (its terminal empty)
    4. python tools/film/take.py
    5. python tools/film/export_viewer.py         (the viewer of the last scene, for the end of step 3)
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec      # noqa: E402
from demo_regen import START, FINAL, TARGET      # noqa: E402

MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'media')

CARD = """(() => { const c = [...document.querySelectorAll('.home-card')]
  .find(e => /co-simulation/i.test(e.textContent)); if (!c) return null;
  const r = c.getBoundingClientRect(); return [r.left + r.width * .5, r.top + r.height * .45]; })()"""
VIEW_READY = ("(() => { const d = document.getElementById('view').contentDocument;"
              " return !!d && !!d.querySelector('canvas') && location.href !== ''; })()")
VIEW_URL = "document.getElementById('view').contentWindow.location.href"

# a tab of the Geometry panel: the copy shown in its header (ux-tabs.js headTabs), not the hidden original
PTAB = """(() => { const b = [...document.querySelectorAll('#pGeom .ux-ptabs button')]
  .find(e => e.textContent.trim() === %s && e.offsetWidth); if (!b) return null;
  const r = b.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()"""
# the panels back at the top (a job scrolls its terminal into view)
TOP = """(() => { let e = document.getElementById('pGeom').parentElement;
  while (e && e.scrollHeight <= e.clientHeight + 1) e = e.parentElement;
  if (e) e.scrollTo({top: 0}); return !!e; })()"""

# an element of the 3D viewer (iframe #view), by selector (and text): its centre in the coordinates of the page
VXY = """(() => { const f = document.getElementById('view'), r = f.getBoundingClientRect(), d = f.contentDocument;
  const sel = %s, txt = %s;
  const e = txt ? [...d.querySelectorAll(sel)].find(x => x.textContent.trim().startsWith(txt) && x.offsetWidth)
                : d.querySelector(sel);
  if (!e) return null; const q = e.getBoundingClientRect();
  return [r.left + q.left + q.width / 2, r.top + q.top + q.height / 2]; })()"""
# full screen of the viewer (its button): the browser of the take has no full screen, the viewer is laid over the
# whole page instead, as the application shows it (hubwindow.py fullscreen)
FS = """(() => { if (!document.getElementById('filmFs')) { const s = document.createElement('style'); s.id = 'filmFs';
  s.textContent = '#view.film-fs{position:fixed!important;left:0!important;top:0!important;width:100vw!important;'
    + 'height:100vh!important;max-width:none!important;max-height:none!important;z-index:99990!important;'
    + 'border:0!important;border-radius:0!important;margin:0!important;transform:none!important}';
  document.head.appendChild(s); }
  const v = document.getElementById('view'); v.classList.add('film-fs');
  v.contentWindow.dispatchEvent(new Event('resize'));
  const r = v.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()"""
VIEW_JS = "document.getElementById('view').contentWindow.eval(%s)"
# the thumb of the hour slider of the viewer at hour h (None: where it is), in the coordinates of the page
HXY = """(() => { const f = document.getElementById('view'), R = f.getBoundingClientRect();
  const s = f.contentDocument.getElementById('hourSlider'), q = s.getBoundingClientRect(), h = %s;
  const lo = +s.min, hi = +s.max, k = ((h === null ? +s.value : h) - lo) / (hi - lo), th = 16;
  return [R.left + q.left + th / 2 + k * (q.width - th), R.top + q.top + q.height / 2]; })()"""
HOUR_END = 14.0          # the hour of the sun at the end of step 3 (the viewer of the page starts there)

# the changes of step 2 (each one seen at once on the urban plan): back to canyon_street_1
CHANGES = [('#f_' + k, str(FINAL[k])) for k in ('rows_1', 'DX', 'floors_1')]


def step_open(r, hub):
    r.hide_cursor()
    r.pause(2.6)                                       # the start page, as when TOPS is launched
    r.goto(hub + '/')
    r.wait("!!document.querySelector('.home-card') && document.querySelector('.home-card').offsetWidth > 0", 60)
    r.wait("!document.getElementById('splash') || getComputedStyle(document.getElementById('splash')).display === 'none'"
           " || document.getElementById('splash').hidden", 30)
    r.pause(1.6)
    r.cursor()
    xy = r.js(CARD)
    r.glide(xy[0] - 160, xy[1] + 60, .5)
    r.pause(.3)
    r.click(tuple(xy), dur=.9, after=.2)
    r.wait("!document.querySelector('#uxHome') || document.querySelector('#uxHome').hidden"
           " || !document.querySelector('.home-card').offsetWidth", 30)
    r.hide_cursor()
    r.wait(VIEW_READY, 90)                              # the demo project in the realistic 3D view
    r.pause(4.5)


def step_scene(r):
    r.x, r.y = 900, 300
    r.cursor()
    r.click(tuple(r.js(PTAB % json.dumps('Urban plan'))), dur=.9, after=1.4)
    r.wait("SEC_VIEW === 'plan'", 5)
    for sel, val in CHANGES:
        r.type_in(sel, val, dur=.7, per_char=.1)
        r.pause(1.1)
    url = r.js(VIEW_URL)
    x, y = r.center('#refreshBtn')
    r.glide(x - 40, y + 30, .7)
    r.pause(.3)
    r.glide(x, y, .4)
    r.pause(.9)                                         # its tooltip: Regenerate IDF
    r.click((x, y), dur=.2, after=2.2)                  # the terminal shows the idf written
    with r.cut():                                       # Domus sizes the heating / cooling of the new scene
        r.wait('%s !== %s' % (VIEW_URL, json.dumps(url)), 900)
        r.wait(VIEW_READY, 90)
        r.js(TOP)
        r.pause(2.5)
    r.glide(1250, 250, 1.0)
    r.hide_cursor()
    r.pause(4.0)                                        # the new scene in the 3D view


def vxy(r, sel, txt=None):
    xy = r.js(VXY % (json.dumps(sel), json.dumps(txt)))
    if not xy:
        raise RuntimeError('not in the viewer: %s %s' % (sel, txt or ''))
    return tuple(xy)


def drag(r, x1, y1, dur, button='left'):
    """Drags in the page from the cursor (OrbitControls of the viewer: left turns, right pans)."""
    import time
    b = {'left': 1, 'right': 2}[button]
    x0, y0 = r.x, r.y
    r.cursor(True)
    r.b._mouse('mousePressed', x0, y0, button, b, 1)
    t0 = time.time()
    while True:
        f = min(1.0, (time.time() - t0) / dur)
        g = f * f * (3 - 2 * f)
        r.x, r.y = x0 + (x1 - x0) * g, y0 + (y1 - y0) * g
        r.b._mouse('mouseMoved', r.x, r.y, button, b)
        r.cursor(True)
        if f >= 1:
            break
        time.sleep(.012)
    r.b._mouse('mouseReleased', x1, y1, button, 0, 1)
    r.cursor(False)


def wheel(r, dy, n, dur):
    import time
    for _ in range(n):
        r.b.wheel(r.x, r.y, dy)
        time.sleep(dur / n)


def show_vf(r, on):
    """The view factor elements on the scene (Studio, View factors): its check box, checked as asked."""
    state = VIEW_JS % json.dumps('!!v3d.O.vfShow')
    for _ in range(2):
        if r.js(state) == on:
            return
        r.click(vxy(r, '#v3dDock label', 'Show the elements'), dur=.7, after=.3)
    if r.js(state) != on:
        raise RuntimeError('view factor elements not %s' % ('shown' if on else 'hidden'))


def step_view(r):
    r.cursor()
    r.click(vxy(r, '#fsBtn'), dur=.9, after=.15)         # full screen
    rect = r.js(FS)
    if [round(v) for v in rect] != [0, 0, r.w, r.h]:
        raise RuntimeError('the viewer is not over the whole page: %s' % rect)
    r.pause(1.0)
    r.glide(r.w * .56, r.h * .46, .7)                    # turned round the scene
    drag(r, r.w * .30, r.h * .43, 2.0)
    r.pause(.3)
    drag(r, r.w * .52, r.h * .50, 1.5)
    r.pause(.2)
    wheel(r, -120, 4, .8)                               # a little closer
    r.pause(.6)
    r.click(vxy(r, '#playBtn'), dur=.9, after=4.0)       # the period played: sun, shadows, passers-by
    r.click(vxy(r, '#playBtn'), dur=.3, after=.5)
    r.glide(*r.js(HXY % 'null'), .7)                     # the sun of the afternoon, by the hour slider
    drag(r, r.js(HXY % HOUR_END)[0], r.y, 2.2)
    r.pause(.5)
    r.click(vxy(r, '#layersBtn'), dur=.8, after=.5)      # hours of direct sun on the faces
    r.click(vxy(r, '#shToggle'), dur=.6, after=2.8)
    r.click(vxy(r, '#noneChk'), dur=.5, after=.4)
    r.click(vxy(r, '#layersBtn'), dur=.5, after=.4)
    r.click(vxy(r, '#studioBtn'), dur=.8, after=.7)      # Studio: view factors of the studied facade
    r.click(vxy(r, '#v3dDock .tab', 'View factors'), dur=.7, after=1.0)
    r.click(vxy(r, '#v3dDock .btn.go'), dur=.6, after=.4)
    with r.cut():                                        # computed as the FMU does
        r.wait(VIEW_JS % json.dumps('!!(window.v3d && v3d.VFR)'), 600)
        r.pause(.8)
    show_vf(r, True)
    r.pause(1.6)
    r.glide(r.w * .30, r.h * .52, .6)
    drag(r, r.w * .16, r.h * .50, 1.4)
    r.pause(1.5)
    show_vf(r, False)
    r.pause(.3)
    r.click(vxy(r, '#v3dDock .x'), dur=.6, after=.6)
    r.click(vxy(r, '#tools button[data-v=street]'), dur=.9, after=3.2)      # in the street, at eye level
    r.click(vxy(r, '#tools button[data-v=persp]'), dur=.7, after=1.0)       # back to the 3D view
    r.glide(r.w * .62, r.h * .40, .7)
    r.hide_cursor()
    r.pause(1.8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8811)
    a = ap.parse_args()
    hub = 'http://127.0.0.1:%d' % a.port
    r = Rec(hub + '/splash.html?mode=hold')
    try:
        r.wait("document.readyState === 'complete'")
        r.pause(.6)
        r.start()
        step_open(r, hub)
        vals = r.js('JSON.stringify(collectParams())')
        vals = json.loads(vals)
        bad = {k: vals.get(k) for k in ('rows_1', 'DX', 'floors_1') if str(vals.get(k)) != str(START[k])}
        if bad:
            raise SystemExit('demo_street is not in its first state (%s): run demo_regen.py' % bad)
        r.mark('s2_scene')
        step_scene(r)
        vals = json.loads(r.js('JSON.stringify(collectParams())'))
        diff = {k: (vals.get(k), v) for k, v in TARGET.items() if k in vals and str(vals[k]) != str(v)}
        print('scene after step 2 vs canyon_street_1:', diff or 'same')
        r.mark('s3_view')
        step_view(r)
        # where the time of the viewer is at the end: the page gives it to the viewer put in place of the film
        day, hour = r.js(VIEW_JS % json.dumps('[dayIdx, hour]'))
        with open(os.path.join(MEDIA, 's3_view.json'), 'w', encoding='utf-8') as fh:
            json.dump({'day': day, 'hour': round(hour, 3)}, fh)
        r.stop(MEDIA, first='s1_open')
    finally:
        r.close()


if __name__ == '__main__':
    main()
