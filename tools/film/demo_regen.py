# -*- coding: utf-8 -*-
"""Gives the demo project (demo_street, a copy of canyon_street_1) the scene of the films: the form values below,
applied by the Regenerate IDF button of the hub for tests (8811). Not filmed.

    python tools/film/demo_regen.py [--port 8811]
"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec      # noqa: E402
from demo_project import IDF, NAME      # noqa: E402

DAY = 86400
SCENE = {'floors_1': 3, 'apts_1': 4, 'rows_1': 1, 'orient': 160,
         't_start': 160 * DAY, 't_end': 164 * DAY}         # 10 - 14 June: summer trees, cooling


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
                           % json.dumps(list(SCENE))))
        r.js("document.getElementById('refreshBtn').click()")
        t = time.time()
        while os.path.getmtime(idf) == t0:
            if time.time() - t > 600:
                raise TimeoutError('idf not rewritten')
            time.sleep(1)
        r.pause(5)
        print('idf rewritten after %.0f s' % (time.time() - t))
    finally:
        r.close()


if __name__ == '__main__':
    main()
