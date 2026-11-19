# -*- coding: utf-8 -*-
"""Local preview of the site: python tools/serve.py [port]  (default 8840, 127.0.0.1 only)."""
import functools, http.server, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
port = int(os.environ.get('PORT') or (sys.argv[1] if len(sys.argv) > 1 else 8840))   # PORT: preview of the app
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
print('http://127.0.0.1:%d/' % port, flush=True)
http.server.ThreadingHTTPServer(('127.0.0.1', port), handler).serve_forever()
