# -*- coding: utf-8 -*-
"""The film of the site, in one take cut into steps (media/<step>.mp4, key frames every few frames: the page plays
the film by scrolling, forwards and backwards; each step starts on the last picture of the one before it).

  s1_open     TOPS opens (start page), the home, a click on the Domus co-simulation: the demo project in the 3D view
  s2_scene    the urban scene is changed in the form, seen at once on the urban plan; the button beside Run
              (Regenerate IDF) writes the idf and the 3D view shows the new scene (the Domus sizing is cut out):
              canyon_street_1 again, the project of the optimisation and of the simulation that follow
  (s3_view)   not filmed: the page puts the viewer itself over the 3D view of the last picture of s2 (viewer/index.html,
              export_viewer.py) and moves it as one scrolls; media/film.json gives where the 3D view is in the picture,
              its camera and its time (the viewer of the page ends there, the film goes on from that picture)
  s4_weather  the Weather window: the stations of the map, La Rochelle, its present and future climates, the present
              climate kept (the one of the optimisation and of the simulation that follow)
  s5_optim    the Optimisation mode: the level-set design (my 10), genetic algorithm, objective flux, the estimate of Run,
              Run (a run of the film: NSGA2_RUNS = the sandbox, hub "hubfilm"), the hub while it runs, the wait cut, the
              run stopped (off the film), then the run of canyon_street_1 done on the cluster opened from the pill
              (a copy of it in the sandbox: RUN_SHOWN)

Before a take (the demo project must be in its first state, the terminal of the hub empty):
    1. hub for the film: launch.json "hubfilm" (8811, optimisation runs in Documents/test/site_opt/runs, with a copy
       of RUN_SHOWN; after a take: the run of the film and its temp_opti/nsga_flux_<token> of "Domus - FMU" to the recycle bin)
    2. python tools/film/demo_regen.py         (demo_street back to the scene of the film)
    3. hub for the film started again            (its terminal empty)
    4. python tools/film/take.py
    5. python tools/film/probe.py <png>           (the 3D view of the hub back on demo_street: s5 ends on canyon_street_1)
    6. python tools/film/export_viewer.py         (the viewer of the last scene, step 3)
"""
import argparse, json, os, sys, time

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
VIEW_JS = "document.getElementById('view').contentWindow.eval(%s)"
# where the 3D view is, and what it shows (camera, time): the viewer of the page takes it over from there
VIEW_STATE = VIEW_JS % json.dumps("JSON.stringify({pose: {pos: camera.position.toArray(), target: controls.target.toArray(),"
                                  " fov: camera.fov}, time: [dayIdx, hour], home: HOME.pos.distanceTo(camera.position) < 1e-6})")
VIEW_RECT = "(() => { const q = document.getElementById('view').getBoundingClientRect(); return [q.left, q.top, q.width, q.height]; })()"

# a tab of the Geometry panel: the copy shown in its header (ux-tabs.js headTabs), not the hidden original
PTAB = """(() => { const b = [...document.querySelectorAll('#pGeom .ux-ptabs button')]
  .find(e => e.textContent.trim() === %s && e.offsetWidth); if (!b) return null;
  const r = b.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()"""
# the panels back at the top (a job scrolls its terminal into view)
TOP = """(() => { let e = document.getElementById('pGeom').parentElement;
  while (e && e.scrollHeight <= e.clientHeight + 1) e = e.parentElement;
  if (e) e.scrollTo({top: 0}); return !!e; })()"""
# an element by selector and text (start of its text): its centre
TXY = """(() => { const e = [...document.querySelectorAll(%s)].find(x => x.textContent.trim().startsWith(%s) && x.offsetWidth);
  if (!e) return null; const q = e.getBoundingClientRect(); return [q.left + q.width / 2, q.top + q.height / 2]; })()"""

# the Weather window shows the end of the Copernicus key of this computer: a check mark only in the film
NO_KEY = """(() => { if (!document.getElementById('filmNoKey')) { const s = document.createElement('style'); s.id = 'filmNoKey';
  s.textContent = '#uxMapDlg .cds .st{font-size:0!important}#uxMapDlg .cds .st::after{content:"✓";font-size:12px}';
  document.head.appendChild(s); }
  const e = document.querySelector('#uxMapDlg .cds .st'); return !e || getComputedStyle(e).fontSize === '0px'; })()"""
# a country of the map of the Weather window (its outline): its centre
COUNTRY = """(() => { const p = [...document.querySelectorAll('#uxMapDlg svg .land path')].find(x => x._f && x._f.c && x._f.c.code === %s);
  if (!p) return null; const q = p.getBoundingClientRect(); return [q.left + q.width / 2, q.top + q.height / 2]; })()"""

# the optimisation runs of the hub of the film (launch.json "hubfilm"): the run of the film is written there, never in env
OPT_RUNS = os.path.join(os.path.expanduser('~'), 'Documents', 'test', 'site_opt', 'runs')
RUN_SHOWN = 'canyon_street_1 ls6x10 LaRochelle flux'          # its row in the panel of the pill (copy of the env run)
# the side panel scrolled by the wheel until an element is in its middle: its centre (None: not shown)
SIDE_AT = """(() => { const e = document.querySelector(%s); if (!e) return null; const q = e.getBoundingClientRect();
  return [q.left + q.width / 2, q.top + q.height / 2, innerHeight]; })()"""
RUNNING = "JOBS.some(j => j.status === 'running')"
STOP = "(() => { const j = JOBS.find(j => j.status === 'running'); if (j) post('/stop', {job: j.key}); return !!j; })()"

# the changes of step 2 (each one seen at once on the urban plan): back to canyon_street_1
CHANGES = [('#f_' + k, str(FINAL[k])) for k in ('rows_1', 'DX', 'floors_1')]


def txy(r, sel, txt):
    xy = r.js(TXY % (json.dumps(sel), json.dumps(txt)))
    if not xy:
        raise RuntimeError('not in the page: %s %s' % (sel, txt))
    return tuple(xy)


def wheel(r, dy, n, dur):
    import time
    for _ in range(n):
        r.b.wheel(r.x, r.y, dy)
        time.sleep(dur / n)


def side_to(r, sel, lo=.3, hi=.62):
    """Wheel on the side panel until `sel` is between lo and hi of the height: its centre."""
    import time
    r.glide(170, r.h * .55, .6)
    last = None
    for _ in range(80):
        x, y, h = r.js(SIDE_AT % json.dumps(sel))
        if lo * h <= y <= hi * h or (last is not None and abs(y - last) < 1 and 40 < y < h - 40):
            return x, y                             # in the middle, or the end of the panel (still in view)
        last = y
        r.b.wheel(r.x, r.y, 100 if y > hi * h else -100)
        time.sleep(.07)
    raise RuntimeError('not reached in the side panel: %s (at %s of %s)' % (sel, y, h))


def pick(r, sel, value, after=1.0):
    """A choice of a list of the form: the cursor clicks it (the list of Edge is not filmed), the value is set."""
    import time
    r.glide(*r.center(sel), .8)
    r.cursor(True)
    time.sleep(.15)
    r.cursor(False)
    r.pause(.35)
    r.js("(() => { const f = document.querySelector(%s); f.value = %s; f.dispatchEvent(new Event('input', {bubbles: true}));"
         " f.dispatchEvent(new Event('change', {bubbles: true})); })()" % (json.dumps(sel), json.dumps(value)))
    r.pause(after)


def evals(run):
    """Evaluations written by the run of the film (folder of the form, under OPT_RUNS)."""
    p = os.path.join(OPT_RUNS, *run.split('/'), 'evals.jsonl')
    try:
        with open(p, encoding='utf-8') as fh:
            return sum(1 for ln in fh if ln.strip())
    except OSError:
        return 0


def step_open(r, hub):
    r.hide_cursor()
    r.pause(2.0)                                       # the start page, as when TOPS is launched
    r.goto(hub + '/')
    r.wait("!!document.querySelector('.home-card') && document.querySelector('.home-card').offsetWidth > 0", 60)
    r.wait("!document.getElementById('splash') || getComputedStyle(document.getElementById('splash')).display === 'none'"
           " || document.getElementById('splash').hidden", 30)
    r.pause(1.2)
    r.cursor()
    xy = r.js(CARD)
    r.glide(xy[0] - 160, xy[1] + 60, .5)
    r.pause(.3)
    r.click(tuple(xy), dur=.9, after=.2)
    r.wait("!document.querySelector('#uxHome') || document.querySelector('#uxHome').hidden"
           " || !document.querySelector('.home-card').offsetWidth", 30)
    r.hide_cursor()
    r.wait(VIEW_READY, 90)                              # the demo project in the realistic 3D view
    r.pause(3.0)


def step_scene(r):
    r.x, r.y = 900, 300
    r.cursor()
    r.click(tuple(r.js(PTAB % json.dumps('Urban plan'))), dur=.9, after=1.2)
    r.wait("SEC_VIEW === 'plan'", 5)
    for sel, val in CHANGES:
        r.type_in(sel, val, dur=.7, per_char=.1)
        r.pause(1.0)
    url = r.js(VIEW_URL)
    x, y = r.center('#refreshBtn')
    r.glide(x - 40, y + 30, .7)
    r.pause(.3)
    r.glide(x, y, .4)
    r.pause(.9)                                         # its tooltip: Regenerate IDF
    r.click((x, y), dur=.2, after=2.0)                  # the terminal shows the idf written
    with r.cut():                                       # Domus sizes the heating / cooling of the new scene
        r.wait('%s !== %s' % (VIEW_URL, json.dumps(url)), 900)
        r.wait(VIEW_READY, 90)
        r.js(TOP)
        r.pause(2.5)
    # the mouse off the 3D view: its bars fade out (shown on hover), as in the viewer of the page that takes over
    r.glide(640, 780, 1.0)
    r.hide_cursor()
    r.pause(2.5)                                        # the new scene in the 3D view


def step_weather(r):
    r.x, r.y = r.w * .45, r.h * .45
    r.cursor()
    r.click('.ux-city', dur=1.0, after=.2)              # the weather of the project: one button of the form
    r.wait("!document.getElementById('uxMapBg').hidden && !!document.querySelector('#uxMapDlg .card .cl')", 15)
    if not r.js(NO_KEY):
        raise RuntimeError('the end of the Copernicus key would be filmed')
    r.pause(1.8)
    r.click('#uxMapDlg .card .back', dur=.9, after=1.4)                           # the stations of France
    r.click(txy(r, '#uxMapDlg .crumbs button', 'World'), dur=.9, after=1.6)       # the regions of the world
    r.click(txy(r, '#uxMapDlg .ov .pill', 'Europe'), dur=.9, after=1.4)           # Europe: its countries
    for code in ('DEU', 'ESP'):                                                     # their stations (tooltips)
        xy = r.js(COUNTRY % json.dumps(code))
        if xy:
            r.glide(xy[0], xy[1], .9)
            r.pause(1.1)
    r.click('#uxMapDlg .search input', dur=.9, after=.2)                          # a station by its name
    for ch in 'La Roch':
        r.b.type(ch)
        r.pause(.12)
    r.pause(1.0)
    r.click('#uxMapDlg aside .list .row', dur=.8, after=1.4)                      # its card: its climates
    r.wait("!!document.querySelector('#uxMapDlg .card .cl') && /Rochelle/.test(document.querySelector('#uxMapDlg .card .id b').textContent)", 10)
    if not r.js(NO_KEY):
        raise RuntimeError('the end of the Copernicus key would be filmed')
    r.click(txy(r, '#uxMapDlg .card label.cl', 'Future'), dur=1.0, after=1.6)     # a future climate (RCP 8.5)
    r.type_in('#uxMapDlg .card .y0', '2050', dur=.8, per_char=.14)                  # a new one: 2050-2079
    r.pause(1.8)
    r.click(txy(r, '#uxMapDlg .card label.cl', 'Present'), dur=.9, after=1.0)    # the present climate kept
    r.click('#uxMapDlg .use .go', dur=.8, after=1.6)
    r.wait("document.getElementById('uxMapBg').hidden", 5)
    r.glide(r.w * .5, r.h * .62, .8)
    r.hide_cursor()
    r.pause(1.6)


def step_optim(r):
    r.x, r.y = r.w * .5, r.h * .5
    r.cursor()
    r.click('#modeSwitch button:nth-child(2)', dur=1.0, after=2.2)     # Optimisation: the design in the Section
    x, y = side_to(r, '#f_ls_my')
    r.type_in('#f_ls_my', '10', dur=.7, per_char=.14)                    # level-set: 6 x 10 functions
    r.js('document.activeElement.blur()')         # the form takes it now (on the click of Run: the click is lost)
    r.pause(1.6)
    side_to(r, '#f_opt_method', .35, .55)
    pick(r, '#f_opt_method', 'genetic', 1.4)                             # genetic algorithm (NSGA-II)
    side_to(r, '#f_opt_objectives', .4, .66)
    pick(r, '#f_opt_objectives', 'flux', 1.4)                            # the heat flux through the internal face
    run = r.js("document.getElementById('f_opt_run').value")
    if not run.startswith('xdomf90/') or r.js("document.getElementById('f_opt_where').value") != 'local':
        raise RuntimeError('the run of the film must be local: %s' % run)
    if not os.path.isdir(OPT_RUNS):
        raise RuntimeError('no folder of the runs of the film (hub "hubfilm"): ' + OPT_RUNS)
    if os.path.isdir(os.path.join(OPT_RUNS, *run.split('/'))):     # Run would resume it: its old output in the terminal
        raise RuntimeError('the run of the film is already there (to the recycle bin first): ' + run)
    x, y = r.center('#runBtn')
    r.glide(x - 50, y + 40, .8)
    r.glide(x, y, .4)
    r.pause(2.6)                                                         # its tooltip: evaluations, time
    r.click((x, y), dur=.2, after=.4)
    r.wait(RUNNING, 20)
    r.glide(r.w * .62, r.h * .80, 1.0)
    r.pause(4.0)                                                         # the run starts: terminal, pill
    with r.cut():                                                        # the first evaluations
        t = time.time()
        while evals(run) < 6 and time.time() - t < 1500:
            time.sleep(2)
        r.pause(2)
    r.pause(4.0)                                                         # evaluations done, the pill moves
    with r.cut():                                                        # the run of the film stopped: never shown
        r.js(STOP)
        r.wait('!' + RUNNING, 300)
        r.pause(2)
    r.click('#uxPill', dur=1.0, after=1.6)                               # the runs: the one done on the cluster
    xy = r.js("(() => { const t = [...document.querySelectorAll('tr')].find(t => t.textContent.includes(%s) && t.offsetWidth);"
              " if (!t) return null; const q = t.getBoundingClientRect(); return [q.left + 90, q.top + q.height / 2]; })()"
              % json.dumps(RUN_SHOWN))
    if not xy:
        raise RuntimeError('not in the runs: ' + RUN_SHOWN)
    r.glide(xy[0] + 140, xy[1] - 40, .7)
    r.pause(1.0)
    r.click(tuple(xy), dur=.6, after=.5)
    r.wait("document.getElementById('f_idf').value === 'canyon_street_1'", 30)
    r.glide(r.w * .55, r.h * .5, .9)
    r.hide_cursor()
    r.pause(5.0)                                                         # its best designs, its convergence


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
        # the 3D view at the end of step 2: the viewer of the page (step 3) starts and ends there
        live = json.loads(r.js(VIEW_STATE))
        live['rect'] = [round(v, 1) for v in r.js(VIEW_RECT)]
        if not live.pop('home'):
            print('warning: the camera of the 3D view is not its default one')
        r.mark('s4_weather')
        step_weather(r)
        r.mark('s5_optim')
        step_optim(r)
        r.stop(MEDIA, first='s1_open')
        film = {'frame': [r.w, r.h], 'clips': {n: round(d, 3) for n, d in r.durations}, 'live': live}
        with open(os.path.join(MEDIA, 'film.json'), 'w', encoding='utf-8') as fh:
            json.dump(film, fh, indent=1)
        with open(os.path.join(MEDIA, 'film.js'), 'w', encoding='utf-8') as fh:     # read as a script (page opened as a file)
            fh.write('window.TOPS_FILM = %s;\n' % json.dumps(film))
        print('film.json', json.dumps(film))
    finally:
        r.close()


if __name__ == '__main__':
    main()
