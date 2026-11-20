# -*- coding: utf-8 -*-
"""Check of the page in a headless Edge: the film at chosen times (scrolling: forwards, backwards), the 3D view of
step 3 (tour, taken in hand, back to the tour), Play; prints the state and writes a picture of each moment.

    python tools/serve.py 8840 &   then   python tools/check_site.py <folder for the pictures> [--port 8840] [--w 1440 --h 900]
"""
import argparse, base64, io, json, os, sys, time

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..', 'env', 'hubgui', 'tools', 'help'))
from cdp import Browser      # noqa: E402

ERRS = "window.__errs = []; addEventListener('error', e => __errs.push(String(e.message)));" \
       " addEventListener('unhandledrejection', e => __errs.push(String(e.reason)));"
STATE = """JSON.stringify((() => { const s = document.querySelector('.screen'), F = window.__film, v = [...s.querySelectorAll('.v')];
  const w = s.querySelector('.live iframe').contentWindow, site = (() => { try { return w.__site; } catch (e) { return null; } })();
  return {y: Math.round(scrollY), t: F && +F.t.toFixed(2), total: F && +F.total.toFixed(1), cls: s.className,
    cap: s.querySelector('.cap.in h2') ? s.querySelector('.cap h2').textContent : '',
    v: v.filter(e => e.classList.contains('on')).map(e => ({src: (e.getAttribute('src') || '').split('/').pop(), t: +e.currentTime.toFixed(2),
      paused: e.paused, rs: e.readyState})),
    sw: document.documentElement.scrollWidth, w: innerWidth, screen: Math.round(s.getBoundingClientRect().left),
    live: [...['left', 'top', 'width', 'height']].map(k => parseFloat(s.querySelector('.live').style[k]) | 0),
    viewer: site ? {time: site.getTime().map(x => +x.toFixed(2)), layer: w.document.getElementById('layersCur').textContent,
                    cam: site.getPose().pos.map(x => +x.toFixed(1))} : null}; })())"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--port', type=int, default=8840)
    ap.add_argument('--w', type=int, default=1440)
    ap.add_argument('--h', type=int, default=900)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    b = Browser('http://127.0.0.1:%d/app/?t=%d' % (a.port, time.time()), width=a.w, height=a.h, port=9345, gpu=True, init_js=ERRS)
    n = [0]

    def shot(tag):
        n[0] += 1
        st = json.loads(b.js(STATE))
        print(tag, json.dumps(st, ensure_ascii=False))
        d = b.cmd('Page.captureScreenshot', format='jpeg', quality=70)['data']
        open(os.path.join(a.out, '%02d_%s.jpg' % (n[0], tag)), 'wb').write(base64.b64decode(d))
        return st

    def wheel_to(t, step=120):
        """Scrolls like a wheel until the film is at t (seconds)."""
        for _ in range(400):
            cur = b.js('(scrollY - document.getElementById("film").offsetTop) / Math.max(70, innerHeight * .13)')
            if abs(cur - t) * max(70, a.h * .13) < step:
                b.js('scrollTo({top: document.getElementById("film").offsetTop + %f * Math.max(70, innerHeight * .13), behavior: "instant"})' % t)
                break
            b.wheel(a.w * .5, a.h * .5, step if t > cur else -step)
            time.sleep(.03)
        time.sleep(1.2)

    def png():
        return Image.open(io.BytesIO(base64.b64decode(b.cmd('Page.captureScreenshot', format='png')['data']))).convert('RGB')

    def at(t, wait=2.0):
        b.js('__film.seek(%f)' % t)
        t0 = time.time()
        while abs(b.js('__film.t') - t) > .003 and time.time() - t0 < 20:
            time.sleep(.2)
        time.sleep(wait)
        return png()

    try:
        time.sleep(2)
        shot('landing')
        b.js("document.getElementById('film').scrollIntoView()"); time.sleep(1.5)
        segs = json.loads(b.js("JSON.stringify(__film.segs.map(s => [s.id, s.kind, s.t0, s.dur]))"))
        print('segments', segs)
        # the seams of the viewer: the picture of the film just before / after it, against the viewer just after / before
        with open(os.path.join(HERE, '..', 'media', 'film.json'), encoding='utf-8') as fh:
            live = json.load(fh)['live']
        k = next(i for i, s in enumerate(segs) if s[1] == 'live')
        bx = json.loads(b.js("(() => { const W = innerWidth, H = innerHeight, s = Math.min(W / 1440, H / 900);"
                             " return JSON.stringify([(W - 1440 * s) / 2, (H - 900 * s) / 2, s]); })()"))
        r = live['rect']
        box = tuple(int(round(v)) for v in (bx[0] + r[0] * bx[2], bx[1] + r[1] * bx[2],
                                             bx[0] + (r[0] + r[2]) * bx[2], bx[1] + (r[1] + r[3]) * bx[2]))
        t3, t4 = segs[k][2], segs[k][2] + segs[k][3]
        for name, (ta, tb) in (('film -> 3D', (t3 - .05, t3 + .005)), ('3D -> film', (t4 - .005, t4 + .05))):
            A, B = at(ta).crop(box), at(tb).crop(box)
            h = ImageChops.difference(A, B).convert('L').histogram()
            print('seam %s: mean difference in the 3D view %.1f / 255' % (name, sum(i * v for i, v in enumerate(h)) / sum(h)))
            pair = Image.new('RGB', (A.width * 2 + 8, A.height), 'white'); pair.paste(A, (0, 0)); pair.paste(B, (A.width + 8, 0))
            pair.save(os.path.join(a.out, 'seam_%s.jpg' % ('in' if ta < t4 - 1 else 'out')), quality=85)
        for sid, kind, t0, dur in segs:
            if kind == 'video':
                for f in (.3, .6, .97):
                    wheel_to(t0 + dur * f); shot('%s_%02d' % (sid, int(f * 100)))
            else:
                for u in (.8, 5, 12, 18, 26, dur - .8):
                    wheel_to(t0 + u); time.sleep(.6); shot('%s_u%04.1f' % (sid, u))
        # the 3D view taken in hand, then the tour again
        live = next(s for s in segs if s[1] == 'live')
        wheel_to(live[2] + 18)
        b.js("document.querySelector('.live iframe').contentWindow.dispatchEvent(new PointerEvent('pointerdown'))")
        time.sleep(.5)
        print('free', b.js('__film.free'))
        b.js("document.querySelector('.live iframe').contentWindow.__site.pose({pos: [30, 3, 30], target: [0, 3, 0], fov: 60})")
        time.sleep(.5); shot('free')
        b.js("document.querySelector('.tour .resume').click()"); time.sleep(1.2); shot('resumed')
        # backwards
        wheel_to(segs[1][2] + segs[1][3] * .5); shot('back_s2')
        # Play: the page scrolls by itself
        b.js("document.querySelector('.ctl .play').click()"); time.sleep(4)
        s1 = shot('auto_1'); time.sleep(3); s2 = shot('auto_2')
        print('play advances %.2f s of film in 3 s' % (s2['t'] - s1['t']))
        b.js("document.querySelector('.ctl .play').click()")
        b.js("scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})"); time.sleep(1.5); shot('after')
        print('errors', b.js("JSON.stringify(window.__errs || [])"))
    finally:
        b.close()


if __name__ == '__main__':
    main()
