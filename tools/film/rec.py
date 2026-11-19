# -*- coding: utf-8 -*-
"""Recorder of the clips of the site: a headless Edge driven on a hub started for tests (port 8811, never the
hub in use on 8800), filmed by the screencast of the page (frames when something changes, with their time),
then resampled at a constant rate and encoded to MP4 by the encoder of the hub (core/videoenc.py, no ffmpeg).

    from rec import Rec
    r = Rec('http://127.0.0.1:8811/')
    r.start(); ... r.glide_to('#runBtn'); r.click('#runBtn'); r.pause(1.5) ...; r.stop('media/open.mp4')

The cursor is drawn in the page (OVERLAY_JS of the help captures); the page has a storage of its own (OWN_STORE):
nothing filmed reaches the settings of the hub.
"""
import base64, io, json, os, shutil, sys, tempfile, threading, time, urllib.request

import websocket
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
HUB = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'env', 'hubgui'))
sys.path.insert(0, os.path.join(HUB, 'tools', 'help'))
sys.path.insert(0, HUB)
from cdp import Browser, OVERLAY_JS, OWN_STORE      # noqa: E402

W, H = 1440, 900
FPS = 30


# what a clip opens: the demo project (tools/film/demo_project.py) in the realistic 3D view, with its neighbourhood
DEMO = {'hub.form.xdomf90': {'idf': 'demo_street'},
        'xdomf90_real': '1', 'xdomf90_decor': {'mode': 'quarter', 'shadows': True}}


def store_js(settings, store=None):
    """Storage of a new user + the settings of the hub wanted (theme...) + other keys (written once: the clip
    can change them)."""
    keys = dict(store or {}, **{'hub.settings': settings})
    return OWN_STORE + ''.join(
        "try { if (localStorage.getItem(%s) === null) localStorage.setItem(%s, %s); } catch (e) {}\n"
        % (json.dumps(k), json.dumps(k), json.dumps(v if isinstance(v, str) else json.dumps(v)))
        for k, v in keys.items())


class Rec:
    def __init__(self, url, settings=None, port=9341, width=W, height=H, store=DEMO, gpu=True):
        self.b = Browser(url, width=width, height=height, port=port, gpu=gpu,
                         init_js=store_js(settings or {'theme': 'cream'}, store))
        self.port, self.frames, self.rec = port, [], False
        self.x, self.y = width * .62, height * .55
        self._lock = threading.Lock()

    # ---- screencast on a second connection to the same page ------------------------------------------------------
    def start(self):
        # the page driven, not another one of Edge (a sign-in / sync prompt can open beside it)
        tabs = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % self.port))
        url = self.b.js('location.href')
        page = next(t for t in tabs if t['type'] == 'page' and t.get('url') == url)
        self.ws2 = websocket.create_connection(page['webSocketDebuggerUrl'], max_size=None, suppress_origin=True)
        self.frames, self.rec, self.t0 = [], True, time.time()
        self.ws2.send(json.dumps({'id': 1, 'method': 'Page.startScreencast',
                                  'params': {'format': 'jpeg', 'quality': 92, 'everyNthFrame': 1}}))
        self.th = threading.Thread(target=self._pump, daemon=True)
        self.th.start()
        self.cursor()

    def _pump(self):
        n = 100
        while self.rec:
            try:
                m = json.loads(self.ws2.recv())
            except Exception:
                break
            if m.get('method') == 'Page.screencastFrame':
                p = m['params']
                with self._lock:
                    self.frames.append((time.time() - self.t0, p['data']))
                n += 1
                self.ws2.send(json.dumps({'id': n, 'method': 'Page.screencastFrameAck',
                                          'params': {'sessionId': p['sessionId']}}))

    def stop(self, out, trim_start=0.0, tail=0.4):
        """Ends the film, writes `out` (.mp4, or .webm beside it if no H.264). Returns the path written."""
        self.pause(tail)
        self.rec = False
        try:
            self.ws2.send(json.dumps({'id': 2, 'method': 'Page.stopScreencast'}))
            self.ws2.close()
        except Exception:
            pass
        with self._lock:
            fr = [f for f in self.frames]
        end = time.time() - self.t0
        if len(fr) < 10:
            raise RuntimeError('only %d frames filmed: nothing written' % len(fr))
        tmp = tempfile.mkdtemp(prefix='tops_film_')
        try:
            paths, reps = [], []
            # constant rate: the frame shown at each tick is the last one received before it
            ticks = int((end - trim_start) * FPS)
            j = 0
            for k in range(ticks):
                t = trim_start + k / FPS
                while j + 1 < len(fr) and fr[j + 1][0] <= t:
                    j += 1
                if paths and reps and last == j:
                    reps[-1] += 1
                    continue
                im = Image.open(io.BytesIO(base64.b64decode(fr[j][1]))).convert('RGB')
                if im.size != (W, H):
                    im = im.resize((W, H), Image.LANCZOS)
                p = os.path.join(tmp, '%05d.png' % len(paths))
                im.save(p, compress_level=1)
                paths.append(p)
                reps.append(1)
                last = j
            from core.videoenc import encode
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            res = encode(paths, out, FPS, repeat=reps)
            poster = os.path.splitext(out)[0] + '.jpg'          # last picture: shown before / after the clip
            Image.open(paths[-1]).save(poster, quality=86)
            first = os.path.splitext(out)[0] + '_first.jpg'
            Image.open(paths[0]).save(first, quality=86)
            print('%s: %d pictures, %.1f s, %.1f MB' % (os.path.basename(res), len(paths), ticks / FPS,
                                                       os.path.getsize(res) / 1e6))
            return res
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # ---- page --------------------------------------------------------------------------------------------------
    def js(self, expr):
        return self.b.js(expr)

    def goto(self, url, wait=0):
        self.b.cmd('Page.navigate', url=url)
        if wait:
            self.pause(wait)

    def wait(self, cond, timeout=30):
        t = time.time()
        while time.time() - t < timeout:
            try:
                if self.b.js(cond):
                    return True
            except Exception:
                pass
            time.sleep(.1)
        raise TimeoutError(cond)

    def cursor(self, down=False):
        try:
            self.b.js(OVERLAY_JS)
            self.b.js('__cap.cur(%f,%f,%s)' % (self.x, self.y, 'true' if down else 'false'))
        except Exception:
            pass

    def hide_cursor(self):
        try:
            self.b.js(OVERLAY_JS)
            self.b.js('__cap.cur(-100,-100,false)')
        except Exception:
            pass

    def pause(self, s):
        time.sleep(s)

    def center(self, sel):
        return self.b.center(sel)

    def glide(self, x, y, dur=.7):
        """Moves the cursor like a hand (ease in / out), the page receives the mouse moves (hover states)."""
        x0, y0, n = self.x, self.y, max(2, int(dur * 50))
        for i in range(1, n + 1):
            f = i / n
            f = f * f * (3 - 2 * f)
            self.x, self.y = x0 + (x - x0) * f, y0 + (y - y0) * f
            self.b.move(self.x, self.y)
            self.cursor()
            time.sleep(dur / n)

    def click(self, target, dur=.7, after=.5):
        x, y = self.center(target) if isinstance(target, str) else target
        self.glide(x, y, dur)
        self.cursor(True)
        time.sleep(.12)
        self.b.click(x, y)
        time.sleep(.1)
        self.cursor(False)
        time.sleep(after)

    def close(self):
        self.rec = False
        self.b.close()
