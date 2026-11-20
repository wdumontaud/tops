# -*- coding: utf-8 -*-
"""Still of the co-simulation as a clip would open it (demo project, realistic 3D view): to choose the scene.

    python tools/film/probe.py out.png [--port 8811] [--js "<code run in the page once the view is there>"]
"""
import argparse, base64, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec      # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--port', type=int, default=8811)
    ap.add_argument('--js', default='')
    ap.add_argument('--wait', type=float, default=6)
    a = ap.parse_args()
    r = Rec('http://127.0.0.1:%d/?model=xdomf90' % a.port)
    try:
        r.wait("!!document.querySelector('.home-card')", 60)
        r.pause(1)
        r.js("(() => { const c = [...document.querySelectorAll('.home-card')].find(e => /co-simulation/i.test(e.textContent));"
             " (c.querySelector('button') || c).click(); })()")
        r.wait("!!document.querySelector('#view') && document.querySelector('#view').contentDocument"
               " && !!document.querySelector('#view').contentDocument.querySelector('canvas')", 90)
        r.pause(a.wait)
        if a.js:
            print(r.js(a.js))
            r.pause(a.wait)
        d = r.b.cmd('Page.captureScreenshot', format='png')['data']
        open(a.out, 'wb').write(base64.b64decode(d))
        print('fps', r.js("(async () => { const w = document.querySelector('#view').contentWindow; let n = 0;"
                          " const t = performance.now(); await new Promise(res => { const f = () => { n++;"
                          " if (performance.now() - t < 1000) w.requestAnimationFrame(f); else res(); };"
                          " w.requestAnimationFrame(f); }); return n; })()"))
    finally:
        r.close()


if __name__ == '__main__':
    main()
