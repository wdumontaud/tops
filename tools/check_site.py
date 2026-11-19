# -*- coding: utf-8 -*-
"""Check of the page in a headless Edge: scrolls through the film step by step, prints the state of the videos and
writes a picture of each moment.

    python tools/serve.py 8840 &   then   python tools/check_site.py <folder for the pictures> [--port 8840] [--w 1440 --h 900]
"""
import argparse, base64, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'env', 'hubgui', 'tools', 'help'))
from cdp import Browser      # noqa: E402

STATE = """JSON.stringify((() => { const s = document.querySelector('.screen'), v = [...s.querySelectorAll('.v')];
  return {y: Math.round(scrollY), cls: s.className, cap: s.querySelector('.cap h2').textContent,
    v: v.map(e => ({k: e.dataset.k, on: e.classList.contains('on'), t: +e.currentTime.toFixed(2),
                    d: +(e.duration || 0).toFixed(2), paused: e.paused, rs: e.readyState})),
    top: document.querySelector('.top').className, sw: document.documentElement.scrollWidth, w: innerWidth,
    screen: Math.round(s.getBoundingClientRect().left), live: s.querySelector('.live').className,
    liveBox: [...['left', 'top', 'width', 'height']].map(k => s.querySelector('.live').style[k])}; })())"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--port', type=int, default=8840)
    ap.add_argument('--w', type=int, default=1440)
    ap.add_argument('--h', type=int, default=900)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    b = Browser('http://127.0.0.1:%d/?t=%d' % (a.port, time.time()), width=a.w, height=a.h, port=9345, gpu=False)
    n = [0]

    def shot(tag):
        n[0] += 1
        st = json.loads(b.js(STATE))
        print(tag, json.dumps(st))
        d = b.cmd('Page.captureScreenshot', format='jpeg', quality=70)['data']
        open(os.path.join(a.out, '%02d_%s.jpg' % (n[0], tag)), 'wb').write(base64.b64decode(d))

    try:
        time.sleep(2)
        shot('landing')
        top = b.js("document.getElementById('film').offsetTop")
        n_steps = b.js("document.querySelectorAll('.step').length")

        def scroll(y):          # by steps, like a wheel (the page reacts to the scroll events)
            y0 = b.js('scrollY')
            for i in range(1, 9):
                b.js('scrollTo(0, %d)' % (y0 + (y - y0) * i / 8))
                time.sleep(.04)

        scroll(top * .5); time.sleep(1); shot('between')
        for k in range(n_steps):
            scroll(top + k * a.h); time.sleep(3); shot('s%d_start' % (k + 1))
            t = time.time()
            while not b.js("document.querySelector('.screen').classList.contains('ended')") and time.time() - t < 120:
                time.sleep(.5)
            time.sleep(1.5); shot('s%d_end' % (k + 1))
            if b.js("!!document.querySelectorAll('.step')[%d].dataset.live" % k):
                t = time.time()
                while not b.js("document.querySelector('.screen').classList.contains('live-on')") and time.time() - t < 30:
                    time.sleep(.5)
                time.sleep(1); shot('s%d_live' % (k + 1))
                c = b.js("(() => { const r = document.querySelector('.live .gate').getBoundingClientRect();"
                         " return [r.left + r.width / 2, r.top + r.height / 2]; })()")
                b.click(*c); time.sleep(1); shot('s%d_walk' % (k + 1))
                print('viewer time', b.js("document.querySelector('.live iframe').contentWindow.eval('[dayIdx, hour]')"))
        scroll(top); time.sleep(2); shot('back_s1')
        scroll(top + (n_steps - .8) * a.h); time.sleep(3); shot('back_last')
        scroll(top + (n_steps + .2) * a.h); time.sleep(2); shot('after')
        print('errors', b.js("JSON.stringify(window.__errs || [])"))
    finally:
        b.close()


if __name__ == '__main__':
    main()
