# -*- coding: utf-8 -*-
"""Local preview of the site: python tools/serve.py [port]  (default 8840, 127.0.0.1 only).

Answers Range requests like GitHub Pages: without them a browser cannot seek in a video (the film shows the last
picture of a step when one scrolls back up)."""
import functools, http.server, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
port = int(os.environ.get('PORT') or (sys.argv[1] if len(sys.argv) > 1 else 8840))   # PORT: preview of the app


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        self._left = None
        m = re.match(r'bytes=(\d*)-(\d*)$', self.headers.get('Range', ''))
        path = self.translate_path(self.path)
        if not m or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        a = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2) or 0))
        b = min(int(m.group(2)), size - 1) if m.group(1) and m.group(2) else size - 1
        if a >= size:
            self.send_error(416)
            return None
        f = open(path, 'rb')
        f.seek(a)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', 'bytes %d-%d/%d' % (a, b, size))
        self.send_header('Content-Length', str(b - a + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        self._left = b - a + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, '_left', None)
        if left is None:
            return super().copyfile(source, outputfile)
        while left > 0:
            buf = source.read(min(65536, left))
            if not buf:
                break
            outputfile.write(buf)
            left -= len(buf)

    def end_headers(self):
        if not getattr(self, '_left', None):
            self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()


handler = functools.partial(Handler, directory=ROOT)
print('http://127.0.0.1:%d/' % port, flush=True)
http.server.ThreadingHTTPServer(('127.0.0.1', port), handler).serve_forever()
