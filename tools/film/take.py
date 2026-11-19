# -*- coding: utf-8 -*-
"""The film of the site, in one take cut into steps (media/<step>.mp4; each step starts on the last picture of the
one before it: the page plays them one after the other as the visitor scrolls, one continuous film).

  s1_open   TOPS opens (start page), the home, a click on the Domus co-simulation: the demo project in the 3D view
  s2_scene  the urban scene is changed in the form, seen at once on the urban plan; the button beside Run
            (Regenerate IDF) writes the idf and the 3D view shows the new scene (the Domus sizing is cut out)

Before a take (the demo project must be in its first state, the terminal of the hub empty):
    1. hub for tests: launch.json "hubtest" (8811)
    2. python tools/film/demo_regen.py         (demo_street back to the scene of the film)
    3. hub for tests started again               (its terminal empty)
    4. python tools/film/take.py
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec      # noqa: E402
from demo_regen import SCENE      # noqa: E402

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

# the changes of step 2 (each one seen at once on the urban plan)
CHANGES = [('#f_rows_1', '2'), ('#f_DX', '7'), ('#f_floors_1', '4')]


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
        bad = {k: vals.get(k) for k in ('rows_1', 'DX', 'floors_1') if str(vals.get(k)) != str(SCENE[k])}
        if bad:
            raise SystemExit('demo_street is not in its first state (%s): run demo_regen.py' % bad)
        r.mark('s2_scene')
        step_scene(r)
        r.stop(MEDIA, first='s1_open')
    finally:
        r.close()


if __name__ == '__main__':
    main()
