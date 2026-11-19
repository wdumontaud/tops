# -*- coding: utf-8 -*-
"""Recorder of the film of the site: a headless Edge driven on a hub started for tests (port 8811, never the hub in
use on 8800), filmed by the screencast of the page (frames when something changes, with their time), then resampled
at a constant rate and encoded to MP4 by the encoder of the hub (core/videoenc.py, no ffmpeg).

One take, cut into steps: the page of the site plays step k when it is reached by scrolling, and step k+1 starts on
the picture where step k ended (one continuous film).

    r = Rec('http://127.0.0.1:8811/')
    r.start(); ...; r.mark('s2_scene'); ...; with r.cut(): <wait for Domus>; ...; r.stop(MEDIA, first='s1_open')

The cursor is drawn in the page (OVERLAY_JS of the help captures); the page has a storage of its own (OWN_STORE):
nothing filmed reaches the settings of the hub.
"""
import base64, contextlib, io, json, os, shutil, sys, tempfile, threading, time, urllib.request

import websocket
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
HUB = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'env', 'hubgui'))
sys.path.insert(0, os.path.join(HUB, 'tools', 'help'))
sys.path.insert(0, HUB)
from cdp import Browser, OVERLAY_JS, OWN_STORE      # noqa: E402

W, H = 1440, 900
FPS = 30
BITRATE = 5_000_000      # bits/s of the clips (a page on the web: ~0.13 bit per pixel and frame)
SHOT_Q = 72              # JPEG of the screencast: 92 gives 12 pictures/s on a full screen 3D view, 72 about 24
DUMP = os.environ.get('TOPS_FILM_DUMP')        # folder: one picture every 2 s of film, to check a take

# what the film opens: the demo project (tools/film/demo_project.py) in the realistic 3D view, with its neighbourhood
DEMO = {'hub.form.xdomf90': {'idf': 'demo_street'},
        'xdomf90_real': '1', 'xdomf90_decor': {'mode': 'quarter', 'shadows': True}}


def store_js(settings, store=None):
    """Storage of a new user + the settings of the hub wanted (theme...) + other keys (written once: the film
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
        self.w, self.h = width, height
        self._lock = threading.Lock()
        # times: seconds since the epoch, the clock of the frames (metadata.timestamp = when the page drew them;
        # they arrive late when the page is busy: never the time of arrival)
        self.marks = []                 # (time, name of the step starting there)
        self.cuts = []                  # (begin, end) left out of the film
        self.lag = 0.0                  # largest delay of arrival of a frame

    # ---- screencast on a second connection to the same page ------------------------------------------------------
    def start(self):
        # the page driven, not another one of Edge (a sign-in / sync prompt can open beside it)
        tabs = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % self.port))
        url = self.b.js('location.href')
        page = next(t for t in tabs if t['type'] == 'page' and t.get('url') == url)
        self.ws2 = websocket.create_connection(page['webSocketDebuggerUrl'], max_size=None, suppress_origin=True)
        self.frames, self.rec, self.t0 = [], True, time.time()
        self.ws2.send(json.dumps({'id': 1, 'method': 'Page.startScreencast',
                                  'params': {'format': 'jpeg', 'quality': SHOT_Q, 'everyNthFrame': 1}}))
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
                ts = p.get('metadata', {}).get('timestamp') or time.time()
                with self._lock:
                    self.frames.append((ts, p['data']))
                    self.lag = max(self.lag, time.time() - ts)
                n += 1
                self.ws2.send(json.dumps({'id': n, 'method': 'Page.screencastFrameAck',
                                          'params': {'sessionId': p['sessionId']}}))

    def mark(self, name):
        """The step `name` starts here."""
        self.marks.append((time.time(), name))

    @contextlib.contextmanager
    def cut(self):
        """What happens in the block is left out of the film (a wait); the film goes on with the picture of the end."""
        t = time.time()
        try:
            yield
        finally:
            self.cuts.append((t, time.time()))

    def _film_time(self, ts):
        """Time in the film of the moment ts (cuts removed; a moment in a cut = its end)."""
        f = ts - self.t0
        for a, b in self.cuts:
            if ts >= b:
                f -= b - a
            elif ts > a:
                f -= ts - a
        return f

    def stop(self, media, first, tail=0.4):
        """Ends the film, writes one clip per step in `media` (<name>.mp4, <name>.jpg = last picture,
        <name>_first.jpg). `first`: name of the step started by start(). Returns the paths written."""
        self.pause(tail)
        t_end = time.time()
        # the frames drawn before the end may still be on their way
        t = time.time()
        while time.time() - t < 60:
            with self._lock:
                if self.frames and self.frames[-1][0] >= t_end - .05:
                    break
            time.sleep(.2)
        self.b.js('1')                                      # a last frame is drawn when the page is idle
        time.sleep(1)
        self.rec = False
        try:
            self.ws2.send(json.dumps({'id': 2, 'method': 'Page.stopScreencast'}))
            self.ws2.close()
        except Exception:
            pass
        with self._lock:
            # film time of each frame; in a cut only the last frame counts (shown when the film goes on)
            fr = sorted((self._film_time(ts), d) for ts, d in self.frames if ts <= t_end)
        print('frames %d, largest delay of arrival %.1f s' % (len(fr), self.lag))
        end = self._film_time(t_end)
        if len(fr) < 10:
            raise RuntimeError('only %d frames filmed: nothing written' % len(fr))
        bounds = [(0.0, first)] + [(self._film_time(t), n) for t, n in self.marks]
        # ticks of the whole film; a step = its ticks: the last picture of a step and the first of the next are two
        # pictures in a row of the film
        ticks = int(end * FPS)
        cuts = [int(round(t * FPS)) for t, _ in bounds] + [ticks]
        from core.videoenc import encode
        os.makedirs(media, exist_ok=True)
        out = []
        j = 0
        for (t, name), k0, k1 in zip(bounds, cuts[:-1], cuts[1:]):
            tmp = tempfile.mkdtemp(prefix='tops_film_')
            try:
                paths, reps, last = [], [], None
                for k in range(k0, k1):
                    tk = k / FPS
                    while j + 1 < len(fr) and fr[j + 1][0] <= tk:
                        j += 1
                    if paths and last == j:
                        reps[-1] += 1
                        continue
                    im = Image.open(io.BytesIO(base64.b64decode(fr[j][1]))).convert('RGB')
                    if im.size != (W, H):
                        im = im.resize((W, H), Image.LANCZOS)
                    p = os.path.join(tmp, '%05d.png' % len(paths))
                    im.save(p, compress_level=1)
                    if DUMP and k % (2 * FPS) == 0:      # pictures to look at: one every 2 s of film
                        os.makedirs(DUMP, exist_ok=True)
                        im.save(os.path.join(DUMP, '%s_%05.1f.jpg' % (name, (k - k0) / FPS)), quality=70)
                    paths.append(p)
                    reps.append(1)
                    last = j
                for attempt in (1, 2, 3):          # the encoder page fails now and then ("Failed to fetch")
                    try:
                        res = encode(paths, os.path.join(media, name + '.mp4'), FPS, repeat=reps, bitrate=BITRATE)
                        break
                    except RuntimeError as e:
                        print('encoding %s, attempt %d: %s' % (name, attempt, e))
                        if attempt == 3:
                            raise
                Image.open(paths[-1]).save(os.path.join(media, name + '.jpg'), quality=86)
                Image.open(paths[0]).save(os.path.join(media, name + '_first.jpg'), quality=86)
                print('%s: %d pictures, %.1f s, %.1f MB' % (os.path.basename(res), len(paths), (k1 - k0) / FPS,
                                                           os.path.getsize(res) / 1e6))
                out.append(res)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        return out

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
        call = '__cap.cur(%f,%f,%s)' % (self.x, self.y, 'true' if down else 'false')
        try:
            self.b.js("window.__cap ? (%s, 1) : 0" % call) or (self.b.js(OVERLAY_JS), self.b.js(call))
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
        x0, y0, t0 = self.x, self.y, time.time()
        while True:                                 # by the clock: the time of a move is `dur` whatever the calls cost
            f = min(1.0, (time.time() - t0) / dur)
            g = f * f * (3 - 2 * f)
            self.x, self.y = x0 + (x - x0) * g, y0 + (y - y0) * g
            self.b.move(self.x, self.y)
            self.cursor()
            if f >= 1:
                break
            time.sleep(.012)

    def click(self, target, dur=.7, after=.5):
        x, y = self.center(target) if isinstance(target, str) else target
        self.glide(x, y, dur)
        self.cursor(True)
        time.sleep(.12)
        self.b.click(x, y)
        time.sleep(.1)
        self.cursor(False)
        time.sleep(after)

    def type_in(self, sel, text, dur=.7, per_char=.12):
        """Clicks a field, selects what it holds, types `text` like a hand, Enter."""
        self.click(sel, dur, after=.25)
        self.js("(() => { const e = document.querySelector(%s); e.focus(); e.select && e.select(); })()" % json.dumps(sel))
        time.sleep(.25)
        for ch in text:
            self.b.type(ch)
            time.sleep(per_char)
        time.sleep(.2)
        self.b.key('Enter', 13)
        time.sleep(.2)

    def close(self):
        self.rec = False
        self.b.close()
