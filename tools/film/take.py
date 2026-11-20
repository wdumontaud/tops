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
  s5_optim    the Optimisation mode: the level-set design (my 10), genetic algorithm, objective flux, 200 individuals, a
              year, the estimate of Run, Run (a run of the film: NSGA2_RUNS = the sandbox, hub "hubfilm"), the hub while
              it runs; in the cut, the run of the film stopped and the run of canyon_street_1 done on the cluster opened
              from the pill (a copy in the sandbox: RUN_SHOWN, same name in the film): as if Run had launched it
  s6_results  the Section tab (best design of each generation), the figures on the whole page (Convergence, Interface,
              Interfaces), Load # into the form
  s7_sim      the Simulation mode, three days of July, outputs with fields, Run: a real co-simulation on demo_street
              (shown as canyon_street_1: ALIAS), never on canyon_street_1; the field movies read in the cut
  s8_fields   the results on the whole page: Domus, then the field movies (temperature, horizontal and vertical flux),
              played once over the three days

Before a take (the demo project must be in its first state, the terminal of the hub empty):
    1. hub for the film: launch.json "hubfilm" (8811, optimisation runs in Documents/test/site_opt/runs, with a copy
       of RUN_SHOWN only)
    2. python tools/film/demo_regen.py         (demo_street back to the scene of the film)
    3. hub for the film started again            (its terminal empty)
    4. python tools/film/take.py
    5. python tools/film/demo_regen.py --final   (the 3D view of the hub back on the scene of the end of s2)
    6. python tools/film/export_viewer.py         (the viewer of that scene, step 3)
    7. to the recycle bin: the run of the film (OPT_RUNS) and its temp_opti/nsga_flux_<token> of "Domus - FMU"; the
       simulation of s7 stays in mod/xdomf90/runs/demo_street (demo_project.py keep moves it at the end)
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
RUN_SHOWN = 'canyon_street_1 ls6x10 LaRochelle flux'          # its row in the panel of the pill (copy of the env run;
#                                                               the run of the film has the same name in the film: finished)
# the side panel scrolled by the wheel until an element is in its middle: its centre (None: not shown)
SIDE_AT = """(() => { const e = document.querySelector(%s); if (!e) return null; const q = e.getBoundingClientRect();
  return [q.left + q.width / 2, q.top + q.height / 2, innerHeight]; })()"""
RUNNING = "JOBS.some(j => j.status === 'running')"
# the demo project (a copy of canyon_street_1) carries the name of canyon_street_1 in the film: one project, the one of the
# optimisation run shown (the page of the film only: its text, never what is sent to the hub)
DEMO_IDF = 'demo_street'
# the page of the film shows no folder of this computer (the user's name is in it): they become C:\TOPS, C:\Users\user
ENV_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'env'))
HOME_DIR = os.path.normpath(os.path.expanduser('~'))
ALIAS = {DEMO_IDF: 'canyon_street_1', ENV_DIR: 'C:\\TOPS', ENV_DIR.replace('\\', '/'): 'C:/TOPS',
         HOME_DIR: 'C:\\Users\\user', HOME_DIR.replace('\\', '/'): 'C:/Users/user'}
ALIAS_JS = r"""(() => { const A = %s, keys = Object.keys(A).sort((a, b) => b.length - a.length);
  const re = new RegExp(keys.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'g');
  const fix = n => { if (n.nodeType === 3) { if (keys.some(k => n.data.indexOf(k) >= 0)) n.data = n.data.replace(re, m => A[m]); return; }
    if (n.nodeType !== 1 || n.tagName === 'SCRIPT' || n.tagName === 'STYLE') return;
    const w = document.createTreeWalker(n, NodeFilter.SHOW_TEXT); const all = []; let t; while ((t = w.nextNode())) all.push(t); all.forEach(fix); };
  const start = () => { fix(document.documentElement);
    new MutationObserver(ms => ms.forEach(m => m.type === 'characterData' ? fix(m.target) : m.addedNodes.forEach(fix)))
      .observe(document.documentElement, {subtree: true, childList: true, characterData: true}); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start(); })();
""" % json.dumps(ALIAS)
SIM_START, SIM_END = '2001-07-14T00:00', '2001-07-17T00:00'      # the simulation of the best design: three summer days
STOP = "(() => { const j = JOBS.find(j => j.status === 'running'); if (j) post('/stop', {job: j.key}); return !!j; })()"

# the changes of step 2 (each one seen at once on the urban plan): back to canyon_street_1
CHANGES = [('#f_' + k, str(FINAL[k])) for k in ('rows_1', 'DX', 'floors_1')]


def txq(r, sel, txt):
    """An element by selector and its exact text: its centre."""
    xy = r.js("(() => { const e = [...document.querySelectorAll(%s)].find(x => x.textContent.trim() === %s && x.offsetWidth);"
              " if (!e) return null; const q = e.getBoundingClientRect(); return [q.left + q.width / 2, q.top + q.height / 2]; })()"
              % (json.dumps(sel), json.dumps(txt)))
    if not xy:
        raise RuntimeError('not in the page: %s %s' % (sel, txt))
    return tuple(xy)


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
    # the period of the run shown (a year): its name is the one of the run shown (period chip)
    r.js("(() => { for (const [k, v] of [['f_t_start', '2001-01-01T00:00'], ['f_t_end', '2002-01-01T00:00']]) {"
         " const f = document.getElementById(k); f.value = v; f.dispatchEvent(new Event('input', {bubbles: true}));"
         " f.dispatchEvent(new Event('change', {bubbles: true})); } })()")
    r.pause(.5)
    r.click('#modeSwitch button:nth-child(2)', dur=1.0, after=2.2)     # Optimisation: the design in the Section
    x, y = side_to(r, '#f_ls_my')
    r.type_in('#f_ls_my', '10', dur=.7, per_char=.14)                    # level-set: 6 x 10 functions
    r.js('document.activeElement.blur()')         # the form takes it now (on the click of Run: the click is lost)
    r.pause(1.6)
    side_to(r, '#f_opt_method', .35, .55)
    pick(r, '#f_opt_method', 'genetic', 1.4)                             # genetic algorithm (NSGA-II)
    side_to(r, '#f_opt_objectives', .4, .66)
    pick(r, '#f_opt_objectives', 'flux', 1.4)                            # the heat flux through the internal face
    side_to(r, '#f_opt_pop', .45, .7)
    r.type_in('#f_opt_pop', '200', dur=.8, per_char=.14)                 # 200 individuals, as the run shown
    r.js('document.activeElement.blur()')
    r.pause(1.0)
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
    r.hide_cursor()
    r.pause(5.0)                                                         # the run starts: terminal, pill, Stop
    # the time of the run cut: the film goes on with the run of the cluster, finished (same name in the film: ALIAS).
    # The run of the film is stopped and the run shown opened from the pill, all in the cut (never seen).
    with r.cut():
        r.js(STOP)
        r.pause(3)
        r.js(STOP)                                                       # again: its Domus runs killed
        r.wait('!' + RUNNING, 300)
        r.click('#uxPill', dur=.1, after=1.5)
        xy = r.js("(() => { const t = [...document.querySelectorAll('tr')].find(t => t.textContent.includes(%s) && /finished/.test(t.textContent) && t.offsetWidth);"
                  " if (!t) return null; const q = t.getBoundingClientRect(); return [q.left + 90, q.top + q.height / 2]; })()"
                  % json.dumps(RUN_SHOWN))
        if not xy:
            raise RuntimeError('not in the runs: ' + RUN_SHOWN)
        r.click(tuple(xy), dur=.1, after=.5)
        r.wait("document.getElementById('f_idf').value === 'canyon_street_1'", 30)
        if r.js("!!document.getElementById('uxRuns') && !!document.getElementById('uxRuns').offsetWidth"):
            r.b.key('Escape', 27)
        r.js("setCollapsed(document.getElementById('pTerm'), true)")      # the terminal of the run of the film
        r.js(TOP)
        r.hide_cursor()
        r.pause(6)                                                       # its figures drawn
    r.pause(2.0)


def step_results(r):
    r.x, r.y = r.w * .55, r.h * .62
    r.cursor()
    r.click(txy(r, '#pGeom .ux-ptabs button', 'Section'), dur=.9, after=.4)   # the best design of each generation
    r.glide(r.w * .45, r.h * .5, .8)
    r.pause(6.5)
    r.click('#pGraphs .ux-fullbtn', dur=1.0, after=2.6)                       # the figures on the whole page
    r.glide(r.w * .5, r.h * .55, .9)
    r.pause(3.0)                                                              # Convergence
    r.click(txq(r, '#pGraphs button', 'Interface'), dur=.9, after=4.2)       # the reference and the best design
    r.click(txq(r, '#pGraphs button', 'Interfaces'), dur=.9, after=4.6)      # the best of the generations
    r.b.key('Escape', 27)
    r.pause(1.2)
    r.click(txy(r, '#pGraphs button', 'Load #'), dur=1.0, after=.5)          # the best design into the form
    r.glide(r.w * .6, r.h * .45, .8)
    r.wait(VIEW_READY, 60)                                                    # the 3D view of the form again
    r.pause(3.0)


def step_sim(r):
    r.x, r.y = r.w * .5, r.h * .5
    r.cursor()
    r.click('#modeSwitch button:nth-child(1)', dur=1.0, after=1.6)          # Simulation: the best design in the form
    # the simulation runs on the demo project (copy of canyon_street_1, same name in the film), never on canyon_street_1:
    # the idf changed and the form put back as it was (changing the idf loads the form of its project)
    with r.cut():
        r.js("window.__snap = collectParams(); (() => { const f = document.getElementById('f_idf'); f.value = %s;"
             " f.dispatchEvent(new Event('change', {bubbles: true})); })()" % json.dumps(DEMO_IDF))
        r.pause(5)
        for _ in range(6):                          # the form of the project may still be arriving: again until it holds
            r.js("applyFormValues(Object.assign({}, __snap, {idf: %s})); saveFormValues(); autoPreview();" % json.dumps(DEMO_IDF))
            r.pause(5)
            diff = r.js("(() => { const p = collectParams(); return JSON.stringify(Object.keys(__snap).filter(k => k !== 'idf'"
                        " && JSON.stringify(p[k]) !== JSON.stringify(__snap[k])).map(k => [k, String(__snap[k]).slice(0, 40), String(p[k]).slice(0, 40)])); })()")
            if diff == '[]':
                break
        if diff != '[]' or r.js("document.getElementById('f_idf').value") != DEMO_IDF:
            raise RuntimeError('the form of the simulation is not the design loaded: %s' % diff)
        r.js(TOP)
        r.pause(2)
    side_to(r, '#f_t_start', .35, .55)
    pick(r, '#f_t_start', SIM_START, 1.0)                                     # three summer days (date fields: set)
    pick(r, '#f_t_end', SIM_END, 1.2)
    side_to(r, '#f_model_output', .4, .66)
    pick(r, '#f_model_output', 'temperature and fluxes field', 1.4)         # the fields in the wall, kept
    if r.js("document.getElementById('f_t_end').value") != SIM_END:
        raise RuntimeError('the period of the simulation is not set')
    x, y = r.center('#runBtn')
    r.glide(x - 50, y + 40, .8)
    r.glide(x, y, .4)
    r.pause(2.2)                                                              # its tooltip: the time it takes
    r.click((x, y), dur=.2, after=.4)
    r.wait(RUNNING, 20)
    r.glide(r.w * .62, r.h * .80, 1.0)
    r.hide_cursor()
    r.pause(5.0)                                                              # Domus and the wall model: the terminal
    with r.cut():                                                             # the time of the simulation
        r.wait('!' + RUNNING, 3600)
        r.js("setCollapsed(document.getElementById('pTerm'), true)")          # its results, not the terminal
        r.js(TOP)
        r.pause(6)
        warm_fields(r)                                                        # s8: its field movies shown at once
        r.js(TOP)
        r.pause(2)
    r.pause(4.5)                                                              # done: its results


# the field movie of a tab of the Graphs panel drawn (its colour bar: T, qx, qy) and its player shown
FIELD_READY = """(() => { const g = document.getElementById('graphsModel'), b = document.getElementById('modelBar');
  const c = g && g.data && g.data[0] && g.data[0].colorbar && g.data[0].colorbar.title;
  return !!c && %s.test(c.text || '') && !!b && !b.hidden && !!b.offsetWidth; })()"""


FIELD_TABS = [('Temperature field', '/^T/'), ('Horizontal flux', '/^q<sub>x/'), ('Vertical flux', '/^q<sub>y/')]
DOMUS_READY = "(() => { const b = [...document.querySelectorAll('#pGraphs button.dom')].find(e => e.offsetWidth); return !!b && b.classList.contains('on'); })()"


def warm_fields(r):
    """The field movies of the run read once (off the film: each tab then shows at once), the Domus tab back."""
    for tab, unit in FIELD_TABS:
        r.js("(() => { const e = [...document.querySelectorAll('#pGraphs button')].find(x => x.textContent.trim() === %s && x.offsetWidth);"
             " e.click(); })()" % json.dumps(tab))
        r.wait(FIELD_READY % unit, 120)
        r.pause(.5)
    r.js("[...document.querySelectorAll('#pGraphs button.dom')].find(e => e.offsetWidth).click()")
    r.wait(DOMUS_READY, 60)
    r.pause(2)


def field_tab(r, tab, after):
    unit = dict(FIELD_TABS)[tab]
    x, y = txq(r, '#pGraphs button', tab)
    if r.y > y + 30:                                    # up beside the maps, then along the tabs: no tooltip of the maps
        r.glide(r.x, y + 18, .6)
    r.click((x, y), dur=.7, after=.1)
    t0 = time.time()
    r.wait(FIELD_READY % unit, 60)
    print('  %s drawn in %.1f s' % (tab, time.time() - t0))
    r.pause(after)


def step_fields(r):
    r.js("(() => { const s = document.getElementById('modelSpeed'); s.value = '1'; s.dispatchEvent(new Event('change')); })()")
    r.x, r.y = r.w * .55, r.h * .7
    r.cursor()
    r.click('#pGraphs .ux-fullbtn', dur=1.0, after=2.4)                      # the results on the whole page (Domus)
    field_tab(r, 'Temperature field', 1.6)                                    # the wall: its temperature
    r.click('#modelPlay', dur=.9, after=.3)                                   # the three days (once: no loop)
    t0 = time.time()
    loop = r.js("movieCount / (movieFps * (+document.getElementById('modelSpeed').value || 1))")
    rest = (r.w * .85, r.h * .82)                                             # off the maps (their tooltips)
    r.glide(*rest, 1.0)
    r.pause(6.6)                                                              # the sun on the outer face, the nights
    field_tab(r, 'Horizontal flux', .3)                                       # the heat flux across the wall
    r.glide(*rest, .9)
    r.pause(3.6)
    field_tab(r, 'Vertical flux', .3)                                         # along it: the blocks of the design
    r.glide(*rest, .9)
    r.pause(3.0)
    field_tab(r, 'Temperature field', .3)
    r.glide(*rest, .9)
    r.hide_cursor()
    left = loop - .6 - (time.time() - t0)
    print('  movie: %.1f s, %.1f s left' % (loop, left))
    r.pause(max(.5, min(2.5, left)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8811)
    a = ap.parse_args()
    hub = 'http://127.0.0.1:%d' % a.port
    r = Rec(hub + '/splash.html?mode=hold', extra_js=ALIAS_JS)
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
        r.mark('s6_results')
        step_results(r)
        r.mark('s7_sim')
        step_sim(r)
        r.mark('s8_fields')
        step_fields(r)
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
