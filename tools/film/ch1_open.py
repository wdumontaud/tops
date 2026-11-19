# -*- coding: utf-8 -*-
"""Clip 1: TOPS opens (start page), the home of the hub, a click on the Domus co-simulation card.

    hub for tests first: launch.json "hubtest" (8811)
    python tools/film/ch1_open.py [--port 8811]
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec      # noqa: E402

MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'media')

CARD = """(() => { const c = [...document.querySelectorAll('.home-card')]
  .find(e => /co-simulation/i.test(e.textContent)); if (!c) return null;
  const r = c.getBoundingClientRect(); return [r.left + r.width * .5, r.top + r.height * .45]; })()"""


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
        r.pause(2.4)                                       # the co-simulation, ready to be set
        r.hide_cursor()
        r.stop(os.path.join(MEDIA, 'ch1_open.mp4'))
    finally:
        r.close()


if __name__ == '__main__':
    main()
