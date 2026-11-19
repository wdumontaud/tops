# Site de TOPS

Page d'accueil (téléchargement par code, version 2026.11, Windows / Linux) puis des chapitres : chacun montre un
extrait filmé de la vraie application, lancé quand il arrive à l'écran, avec « Continuer ↓ » à la fin.
Thème crème de TOPS, français / anglais (bouton FR | EN, choix gardé dans le navigateur).

## Fichiers
- `index.html`, `css/site.css`, `js/site.js` (textes FR / EN dans `T`).
- `assets/tops.png` : icône de TOPS.
- `media/chN_*.mp4` + `.jpg` (dernière image) + `_first.jpg` (première image, affichée avant la lecture).
- `tools/film/rec.py` : tournage (Edge sans fenêtre sur un hub de test 8811, screencast, 30 images/s, encodage par
  `core/videoenc.py` du hub). `tools/film/chN_*.py` : un scénario par chapitre.
- `tools/serve.py` : aperçu local.

## Refaire un extrait
1. Hub de test : configuration `hubtest` de `env/hubgui/.claude/launch.json` (port 8811, jamais le hub 8800).
2. `python tools/film/ch1_open.py`
3. Vérifier `media/` (première et dernière image) avant de publier.

## Pas encore fait
- Chapitres 2+ : paramétrage (projet de démonstration copié de canyon_street_1, gardé ensuite dans le bac à sable),
  vue 3D interactive à la fin, météo, optimisation, résultats, champs.
- Service du téléchargement par code (codes, 5 dernières versions, e-mail aux détenteurs d'un code).
