# -*- coding: utf-8 -*-
"""Demo project of the films: a copy of canyon_street_1 (idf + form of the project), never the original.

    python tools/film/demo_project.py make     # mod/xdomf90/idf/demo_street.idf + #demo_street/{hub_params,hub_run_params}.json
    python tools/film/demo_project.py keep     # once the films are made: moved to Documents\\test\\site_demo (sandbox)

The hub can only read projects in mod/xdomf90/idf (xd_base.IDF_DIR): the copy lives there while the films are made.
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IDF = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..', 'env', 'mod', 'xdomf90', 'idf'))
SRC, NAME = 'canyon_street_1', 'demo_street'
KEEP = os.path.join(os.path.expanduser('~'), 'Documents', 'test', 'site_demo')


def make():
    dst = os.path.join(IDF, NAME + '.idf')
    if os.path.exists(dst):
        sys.exit('%s exists already' % dst)
    shutil.copy2(os.path.join(IDF, SRC + '.idf'), dst)
    os.makedirs(os.path.join(IDF, '#' + NAME))
    for f in ('hub_params.json', 'hub_run_params.json'):
        with open(os.path.join(IDF, '#' + SRC, f), encoding='utf-8') as fh:
            d = json.load(fh)
        d['idf'] = NAME
        if isinstance(d.get('params'), dict):
            d['params']['idf'] = NAME
        with open(os.path.join(IDF, '#' + NAME, f), 'w', encoding='utf-8') as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
    print('made', dst)


def keep():
    os.makedirs(KEEP, exist_ok=True)
    for f in (NAME + '.idf', '#' + NAME):
        p = os.path.join(IDF, f)
        if os.path.exists(p):
            shutil.move(p, os.path.join(KEEP, f))
            print('moved', f, '->', KEEP)
    runs = os.path.join(os.path.dirname(IDF), 'runs', NAME)        # the simulations of the film (step s7_sim)
    if os.path.exists(runs):
        shutil.move(runs, os.path.join(KEEP, 'runs_' + NAME))
        print('moved', runs, '->', KEEP)
    print('left: the caches of %s in C:/Domus - FMU (if any) and its entry in idf/hub_sizing.json' % NAME)


if __name__ == '__main__':
    {'make': make, 'keep': keep}[sys.argv[1]]()
