# -*- coding: utf-8 -*-
"""Geometry of canyon_street_1 (and a few variants of its parameters) for the prototype page.

Reads the hub parameters of the project, builds each variant with the same code as the hub
(py2idf.urbanGeometry) into a temporary folder (never in env/mod/xdomf90/idf), reads the faces
back (idf_parser) and writes ../data/scene.json and ../data/scene.js.

    python tools/make_scene.py
"""
import io, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(HERE, '..', '..', '..', 'env')
PY = os.path.join(ENV, 'mod', 'xdomf90', 'lib', 'py')
sys.path.insert(0, PY)
sys.path.insert(0, os.path.join(ENV, 'hubgui'))

import py2idf                                   # noqa: E402
from idf_parser import parse_idf                # noqa: E402
from xd_base import URBAN_TEMPLATE              # noqa: E402
from xd_params import _pipeline_params          # noqa: E402
from xd_form import schema                      # noqa: E402

DEFAULTS = {f['name']: f.get('default') for g in schema()['groups'] for f in g['fields'] if 'name' in f}
BASE = dict(DEFAULTS, country='FRA', city='LaRochelle', **json.load(io.open(os.path.join(ENV, 'mod', 'xdomf90', 'idf', '#canyon_street_1', 'hub_params.json'),
                         encoding='utf-8'))['values'])

# story of the chapter: the real project, then what a few parameters do to the scene
VARIANTS = [
    ('base', 'canyon_street_1', {}),
    ('floors', 'Studied building: 4 floors', {'floors_1': 4}),
    ('street', 'Wider street: 10 m', {'floors_1': 4, 'DX': 10}),
    ('flat', 'No pitched roofs', {'floors_1': 4, 'DX': 10, 'roofs': 'off'}),
]


def build(values, tmp):
    p = _pipeline_params(values)
    sc = p['layout']
    out = os.path.join(tmp, 'v.idf')
    with open(os.devnull, 'w') as dn:
        so, sys.stdout = sys.stdout, dn
        try:
            py2idf.urbanGeometry(URBAN_TEMPLATE, sc['zones'], soil=sc['soil'], studied=sc['studied'],
                                 heating=False, out=out, windows=p['windows'], stack=p['stack'],
                                 roofs=p.get('roofs'), walls=p.get('walls'), bands=p.get('bands', 1))
        finally:
            sys.stdout = so
    b = parse_idf(out)
    r = lambda v: [round(x, 3) for x in v]
    faces = [{'z': s['zone'], 'k': s.get('kind') or '', 'v': [r(v) for v in s['vertices']]}
             for s in b['surfaces'] if s['zone'].lower() != 'infinita']
    return {'faces': faces, 'stack': list(p['stack'] or []), 'north': b.get('north')}


def main():
    res = {'lat': 46.16, 'lon': -1.15, 'tz': 1.0, 'city': 'La Rochelle', 'variants': []}
    with tempfile.TemporaryDirectory() as tmp:
        for key, label, change in VARIANTS:
            v = build(dict(BASE, **change), tmp)
            v.update(key=key, label=label)
            res['variants'].append(v)
            print(key, len(v['faces']), 'faces')
    dest = os.path.join(HERE, '..', 'data', 'scene.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    txt = json.dumps(res, separators=(',', ':'))
    io.open(dest, 'w', encoding='utf-8').write(txt)
    # same data as a script: the page also opens by a double click (file://, no fetch)
    io.open(dest[:-2], 'w', encoding='utf-8').write('window.SCENE=' + txt + ';\n')
    print(dest, os.path.getsize(dest) // 1024, 'kB')


if __name__ == '__main__':
    main()
