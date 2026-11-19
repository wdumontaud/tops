# -*- coding: utf-8 -*-
"""Gives the demo project (demo_street, a copy of canyon_street_1) the first scene of the film: the form of
canyon_street_1 with START changed, applied by the Regenerate IDF button of the hub for tests (8811). Not filmed.
Step 2 of the film types FINAL back: the scene is then canyon_street_1 again, the project of the optimisation and of
the simulation that follow.

    python tools/film/demo_regen.py [--port 8811]
"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec      # noqa: E402
from demo_project import IDF, NAME      # noqa: E402

SRC_PARAMS = os.path.join(IDF, '#canyon_street_1', 'hub_params.json')
START = {'rows_1': 1, 'DX': 7, 'floors_1': 3}          # one more row behind, a wider street, one more floor
with open(SRC_PARAMS, encoding='utf-8') as _f:
    TARGET = json.load(_f)['values']                     # canyon_street_1
FINAL = {k: TARGET[k] for k in START}
SCENE = dict(TARGET, **START)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8811)
    a = ap.parse_args()
    idf = os.path.join(IDF, NAME + '.idf')
    t0 = os.path.getmtime(idf)
    r = Rec('http://127.0.0.1:%d/?model=xdomf90' % a.port, gpu=False)
    try:
        r.wait("!!document.querySelector('.home-card')", 60)
        r.js("(() => { const c = [...document.querySelectorAll('.home-card')].find(e => /co-simulation/i.test(e.textContent));"
             " (c.querySelector('button') || c).click(); })()")
        r.wait("document.getElementById('f_idf') && document.getElementById('f_idf').value === %s" % json.dumps(NAME), 60)
        r.pause(4)
        r.js('applyFormValues(%s)' % json.dumps(SCENE))
        r.pause(1)
        print('form', r.js('JSON.stringify(Object.fromEntries(Object.entries(collectParams()).filter(([k]) => %s.includes(k))))'
                           % json.dumps(list(START))))
        r.js("document.getElementById('refreshBtn').click()")
        t = time.time()
        while os.path.getmtime(idf) == t0:
            if time.time() - t > 600:
                raise TimeoutError('idf not rewritten')
            time.sleep(1)
        print('idf rewritten after %.0f s' % (time.time() - t))
        # then the sizing, the long-wave scene, the sun of the facade: the form of the project is saved at the end
        r.wait("typeof JOBS !== 'undefined' && !JOBS.some(j => j.status === 'running')", 900)
        r.pause(3)
        with open(os.path.join(IDF, '#' + NAME, 'hub_params.json'), encoding='utf-8') as fh:
            v = json.load(fh)['values']
        bad = {k: v.get(k) for k in SCENE if str(v.get(k)) != str(SCENE[k])}
        print('job done after %.0f s; saved form %s' % (time.time() - t, bad or 'as wanted'))
    finally:
        r.close()


if __name__ == '__main__':
    main()
