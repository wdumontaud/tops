# -*- coding: utf-8 -*-
"""The 3D viewer of the hub for the page of the site (end of step 3: the visitor walks through the scene himself).

    python tools/film/export_viewer.py [--port 8811]

Takes the viewer the hub for tests wrote for the last scene of the take (_runs/xdomf90/idf_preview_<port>_<pc>.html,
self-contained: the scene is in the page) and writes viewer/index.html + viewer/vendor/ (three.js r128 of the hub):
  - the scripts of the hub (/vendor/...) read next to the page;
  - no Studio (pictures, videos, view factors: they need the hub), no tooltips of the hub;
  - the look of the film the first time (realistic, the quarter around, sun path), as in the take (rec.DEMO);
  - checked: no path of this computer nor e-mail address in the page.
"""
import argparse, json, os, re, shutil, socket, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, '..', '..'))
HUB = os.path.normpath(os.path.join(SITE, '..', '..', 'env', 'hubgui'))
OUT = os.path.join(SITE, 'viewer')
VENDOR = ('three.min.js', 'OrbitControls.js', 'Sky.js')

# the look of the film (rec.DEMO), given only when the visitor has not chosen another one in this viewer
FIRST = {'xdomf90_real': '1', 'xdomf90_decor': json.dumps({'mode': 'quarter', 'shadows': True}),
         'xdomf90_hudfold': '1', 'xdomf90_sunpath': '1', 'xdomf90_layers_open': '0'}
HEAD = ('<script>/* site: the look of the film the first time */ (() => { try { const F = %s;'
        ' for (const k in F) if (localStorage.getItem(k) === null) localStorage.setItem(k, F[k]); } catch (e) {} })();'
        '</script>\n' % json.dumps(FIRST))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8811)
    a = ap.parse_args()
    src = os.path.join(HUB, '_runs', 'xdomf90', 'idf_preview_%d_%s.html' % (a.port, socket.gethostname().lower()))
    with open(src, encoding='utf-8') as fh:
        s = fh.read()
    n0 = len(s)

    def sub(pat, rep, count=1):
        nonlocal s
        s, k = re.subn(pat, rep, s)
        if k != count:
            sys.exit('export_viewer: %r found %d times (%d expected): the viewer of the hub has changed' % (pat, k, count))

    sub(r'<script src="/vendor/three\.min\.js"></script>', '<script src="vendor/three.min.js"></script>')
    sub(r"\['/vendor/OrbitControls\.js', '/vendor/Sky\.js'\]", "['vendor/OrbitControls.js', 'vendor/Sky.js']")
    sub(r'<!-- studio \(pictures, videos, view factors\): files of the hub -->\s*<link[^>]*v3dstudio\.css">'
        r'<script src="/js/v3dstudio\.js"></script><script src="/js/ux-tip\.js"></script>', '')
    sub(r'\s*<button id="studioBtn".*?</button>', '')
    sub(r'<title>IDF — 3D viewer</title>', '<title>TOPS — 3D view</title>')
    sub(r'(<head><meta charset="utf-8">)', r'\1\n' + HEAD.replace('\\', '\\\\'))
    if re.search(r'''["']/(?:vendor|js|css)/''', s):
        sys.exit('export_viewer: a file of the hub is still read: %s' % re.findall(r'["\'](/(?:vendor|js|css)/[^"\']*)', s))
    bad = re.findall(r'[A-Za-z]:\\\\|Users[\\/]|OneDrive|[\w.+-]+@[\w-]+\.[A-Za-z]{2,}', s)
    if bad:
        sys.exit('export_viewer: private text in the viewer: %s' % sorted(set(bad))[:5])

    os.makedirs(os.path.join(OUT, 'vendor'), exist_ok=True)
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)
    for f in VENDOR:
        shutil.copy2(os.path.join(HUB, 'web', 'vendor', f), os.path.join(OUT, 'vendor', f))
    print('viewer/index.html (%d -> %d characters) + vendor/%s' % (n0, len(s), ', '.join(VENDOR)))


if __name__ == '__main__':
    main()
