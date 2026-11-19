# Site de TOPS

Page d'accueil (téléchargement par code, version 2026.11, Windows / Linux) puis des chapitres : un titre court, puis
un extrait filmé de la vraie application sur toute la largeur et la hauteur de l'écran (sans fenêtre autour ; la barre
du site s'efface en descendant), lancé quand il arrive à l'écran, avec « Continuer ↓ » à la fin.
Thème crème de TOPS, français / anglais (bouton FR | EN, choix gardé dans le navigateur).

## Fichiers
- `index.html`, `css/site.css`, `js/site.js` (textes FR / EN dans `T`).
- `assets/tops.png` : icône de TOPS.
- `media/chN_*.mp4` + `.jpg` (dernière image) + `_first.jpg` (première image, affichée avant la lecture).
- `tools/film/rec.py` : tournage (Edge sans fenêtre sur un hub de test 8811, carte graphique pour la 3D, screencast,
  30 images/s, encodage par `core/videoenc.py` du hub). Stockage propre à la page : thème crème, projet `demo_street`,
  vue 3D réaliste avec le quartier (`DEMO`). `tools/film/chN_*.py` : un scénario par chapitre.
- `tools/film/demo_project.py make | keep` : projet de démonstration `demo_street` (copie de canyon_street_1 dans
  `mod/xdomf90/idf`, seul dossier lu par le hub) ; `keep` le range dans `Documents\test\site_demo` à la fin.
  `tools/film/demo_regen.py` : lui donne la scène des films (3 étages, 4 appartements, une rangée derrière,
  orientation 160°, 10-14 juin) par le bouton Regenerate IDF. `tools/film/probe.py` : image de contrôle.
- `tools/serve.py` : aperçu local.

## Refaire un extrait
1. Hub de test : configuration `hubtest` de `env/hubgui/.claude/launch.json` (port 8811, jamais le hub 8800),
   relancé juste avant (terminal vide). Projet `demo_street` présent (sinon `demo_project.py make` puis `demo_regen.py`).
2. `python tools/film/ch1_open.py`
3. Vérifier `media/` (première et dernière image) avant de publier.

## Pas encore fait
- Chapitres 2+ : paramétrage (sur `demo_street`, rangé ensuite dans le bac à sable),
  vue 3D interactive à la fin, météo, optimisation, résultats, champs.
- Service du téléchargement par code (codes, 5 dernières versions, e-mail aux détenteurs d'un code).
