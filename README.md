# Site de TOPS

Page d'accueil (téléchargement par code, version 2026.11, Windows / Linux), puis **le film** : un seul écran plein
(l'application sur toute la largeur et la hauteur, sans fenêtre autour), tenu en place pendant qu'on défile. Chaque
écran de défilement = une étape, jouée quand on l'atteint ; elle commence sur la dernière image de la précédente (une
seule prise découpée) : rien n'est empilé, on voit une vidéo continue. À la fin d'une étape : « Continuer : <étape
suivante> ↓ » et ↻ ; une carte décrit l'étape à son début puis s'efface ; des points à droite montrent où l'on est.
En remontant, l'étape atteinte montre sa dernière image. La barre du site s'efface en descendant.
Une étape avec `data-live` finit sur l'application elle-même : à la fin de l'étape 3, la vraie visionneuse 3D
(`viewer/`) remplace le film, dans le même cadre, à l'heure et au point de vue de la dernière image ; elle ne prend la
souris qu'après un clic (« Cliquez pour vous promener dans la vue 3D »), sinon la molette fait défiler la page.
Thème crème de TOPS, français / anglais (bouton FR | EN, choix gardé dans le navigateur).

## Fichiers
- `index.html` (`#film` : `.screen` + une `.step` par étape, `data-clip`, `data-t` / `data-p` = clés des textes),
  `css/site.css`, `js/site.js` (textes FR / EN dans `T`).
- `assets/tops.png` : icône de TOPS.
- `media/<étape>.mp4` + `.jpg` (dernière image) + `_first.jpg` (première image). Étapes : `s1_open` (ouverture →
  accueil → co-simulation sur la démo), `s2_scene` (plan Urban plan, rangées 1 → 2, DX 5 → 7, étages 3 → 4, bouton à
  côté de Run, nouvelle scène dans la vue 3D ; l'attente du dimensionnement Domus est coupée). La démo part de
  canyon_street_1 modifié (une rangée derrière, DX 7, 3 étages) et l'étape 2 la ramène à canyon_street_1, le projet
  de l'optimisation et de la simulation qui suivent. `s3_view` (vue 3D en plein écran, rotation, période jouée,
  heure réglée, heures d'ensoleillement, facteurs de forme calculés comme la FMU — calcul coupé —, vue de la rue,
  retour à la vue 3D ; `s3_view.json` = jour et heure de la fin).
- `viewer/` : la visionneuse de la dernière scène (`tools/film/export_viewer.py`, depuis celle du hub de test :
  sans Studio, scripts three.js dans `viewer/vendor/`, aspect du film à la première visite).
- `tools/film/take.py` : la prise (toutes les étapes à la suite). `tools/film/rec.py` : tournage (Edge sans fenêtre
  sur un hub de test 8811, carte graphique pour la 3D, screencast daté par l'heure de rendu, coupes `cut()`, repères
  `mark()`, 30 images/s, encodage par `core/videoenc.py` du hub). Stockage propre à la page : thème crème, projet
  `demo_street`, vue 3D réaliste avec le quartier (`DEMO`). `TOPS_FILM_DUMP=<dossier>` : une image toutes les 2 s.
- `tools/film/demo_project.py make | keep` : projet de démonstration `demo_street` (copie de canyon_street_1 dans
  `mod/xdomf90/idf`, seul dossier lu par le hub) ; `keep` le range dans `Documents\test\site_demo` à la fin.
  `tools/film/demo_regen.py` : le remet dans l'état du début du film (3 étages, 4 appartements, une rangée derrière,
  DX 5, orientation 160°, 10-14 juin) par le bouton Regenerate IDF. `tools/film/probe.py` : image de contrôle.
- `tools/serve.py` : aperçu local (requêtes Range, comme GitHub Pages : sans elles, pas de saut dans une vidéo).
  `tools/check_site.py <dossier>` : parcours du film dans Edge sans fenêtre (états des vidéos ; ses captures
  montrent mal les vidéos, les tailles mesurées font foi).

## Refaire le film
1. Hub de test : configuration `hubtest` de `env/hubgui/.claude/launch.json` (port 8811, jamais le hub 8800).
2. `python tools/film/demo_regen.py` (la démo revient à son état de départ ; la prise la modifie).
3. Relancer le hub de test (terminal vide), puis `python tools/film/take.py`.
3b. `python tools/film/export_viewer.py` (visionneuse de la scène de fin).
4. Vérifier `media/` (premières et dernières images, `TOPS_FILM_DUMP`) avant de publier : aucune donnée personnelle.

## Pas encore fait
- Étapes suivantes : météo, optimisation de canyon_street_1, résultats, courte simulation avec champs, champs.
- Service du téléchargement par code (codes, 5 dernières versions, e-mail aux détenteurs d'un code).
