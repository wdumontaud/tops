# Site de TOPS

Page d'accueil (téléchargement par code, version 2026.11, Windows / Linux), puis **le film** : un seul écran plein
(l'application sur toute la largeur et la hauteur, sans fenêtre autour), tenu en place pendant qu'on défile.
**Le défilement est le temps du film** (`PX` = 13 % de la hauteur de l'écran par seconde) : il avance quand on
descend, recule quand on remonte, s'arrête quand on s'arrête (lissé sur ~0,1 s : la molette va par crans). Le bouton
▶ (en haut, avec la barre de tout le film) fait défiler la page tout seul à la vitesse du film (les extraits sont
alors lus, pas cherchés) ; toute action de la main l'arrête. « Regarder comme une vidéo » sur l'accueil = ▶ depuis le
début. Une carte décrit chaque étape pendant ses 7 premières secondes ; des points à droite montrent où l'on est.
La barre du site s'efface en descendant. Thème crème de TOPS, français / anglais (FR | EN, gardé dans le navigateur).

**Étape 3 = la vraie vue 3D** (`viewer/`), pas un film : elle se pose sur la vue 3D de la dernière image de
l'étape 2 (même cadre, même caméra, même heure : `media/film.json` `live`), grandit jusqu'à tout l'écran, puis le
défilement la conduit (visite guidée de `KEYS` dans `js/site.js` : tour de la rue, soleil de midi au lendemain
après-midi avec la nuit et les fenêtres éclairées, heures d'ensoleillement, facteurs de forme du Studio, vue de la
rue, retour) et elle se repose sur la vue 3D de l'image où reprend l'étape 4. Tout est fonction du temps du film
(dans les deux sens). Le visiteur la prend en main quand il veut (glisser = tourner, Ctrl + molette ou pincer =
zoomer, la molette seule fait défiler la page ; écran tactile : toucher d'abord) ; « Reprendre la visite guidée »
rend la main au défilement (retour en douceur), comme la fin de l'étape.

## Fichiers
- `index.html` (`#film` : `.screen` + une `.step` par étape : `data-id` = `media/<id>.mp4`, `data-t` / `data-p` =
  clés des textes, `data-live` + `data-dur` = page posée sur l'image pendant `data-dur` s de film),
  `css/site.css`, `js/site.js` (textes FR / EN dans `T` ; `window.__film` pour les essais).
- `assets/tops.png` : icône de TOPS.
- `media/<étape>.mp4` (image clé toutes les 6 images : on y cherche à tout instant) + `.jpg` (dernière image) +
  `_first.jpg` (première, affiche de la vidéo). `media/film.json` : durées des extraits, taille de l'image, cadre de
  la vue 3D dans l'image, sa caméra et son heure à la fin de l'étape 2. Étapes filmées : `s1_open` (ouverture →
  accueil → co-simulation sur la démo), `s2_scene` (plan Urban plan, rangées / DX / étages, bouton à côté de Run,
  nouvelle scène ; l'attente du dimensionnement Domus est coupée), `s4_weather` (fenêtre Weather : carte des
  stations, La Rochelle, climat futur, nouvelle période 2050, climat actuel gardé), `s5_optim` (mode Optimisation,
  level-set 6 × 10, génétique, objectif flux, 200 individus, période d'un an, estimation de Run, Run d'un **run fictif**
  — runs génétiques du hub de film dans `Documents\test\site_opt\runs` —, puis, dans la coupe, run fictif arrêté et run
  `canyon_street_1 ls6x10 LaRochelle flux` fait au cluster (copié dans ce dossier) ouvert : même nom dans le film, on
  ne voit ni l'arrêt ni la liste), `s6_results` (onglet Section = meilleur dessin de chaque génération, figures en
  plein écran : Convergence, Interface, Interfaces ; Load #4198 into the form), `s7_sim` (mode Simulation, 14-17 juillet,
  sorties « temperature and fluxes field », Run : vraie co-simulation de ~30 s sur la démo, terminal replié à la fin).
  **Dans la page filmée** (`ALIAS` de take.py, texte seulement, jamais ce qui part au hub) : `demo_street` s'affiche
  `canyon_street_1`, le dossier env `C:\TOPS`, les dossiers de l'utilisateur `C:\Users\user`. La démo part de canyon_street_1
  modifié (une rangée derrière, DX 7, 3 étages) et l'étape 2 la ramène à canyon_street_1, le projet de l'optimisation
  et de la simulation qui suivent. La fin de la clé Copernicus de la fenêtre Weather est cachée pendant la prise.
- `viewer/` : la visionneuse de la scène (`tools/film/export_viewer.py`, depuis celle du hub de test : sans Studio,
  scripts three.js dans `viewer/vendor/`, aspect du film à chaque visite ; couche View factors = facteurs de forme du
  Studio calculés comme la FMU, demandés au hub de test ; molette = défilement de la page, Ctrl + molette = zoom ;
  `window.__site` = ce que la page conduit).
- `tools/film/take.py` : la prise (étapes filmées à la suite). `tools/film/rec.py` : tournage (Edge sans fenêtre sur
  un hub de test 8811, carte graphique pour la 3D, screencast daté par l'heure de rendu, coupes `cut()`, repères
  `mark()`, 30 images/s, JPEG 85, 10 Mbit/s, curseur animé dans la page (`GLIDE_JS`), encodage par `core/videoenc.py` du hub avec `gop`). Stockage propre à la page :
  thème crème, projet `demo_street`, vue 3D réaliste avec le quartier (`DEMO`). `TOPS_FILM_DUMP=<dossier>` : une
  image toutes les 2 s.
- `tools/film/demo_project.py make | keep` : projet de démonstration `demo_street` (copie de canyon_street_1 dans
  `mod/xdomf90/idf`, seul dossier lu par le hub) ; `keep` le range dans `Documents\test\site_demo` à la fin.
  `tools/film/demo_regen.py` : le remet dans l'état du début du film par le bouton Regenerate IDF.
- `tools/serve.py` : aperçu local (requêtes Range, comme GitHub Pages : sans elles, pas de saut dans une vidéo).
  `tools/check_site.py <dossier>` : parcours du film dans Edge sans fenêtre (temps, vidéos, vue 3D prise en main,
  lecture ▶ ; ses captures montrent mal les vidéos, les états mesurés font foi).

## Refaire le film
1. Hub du film : configuration `hubfilm` de `env/hubgui/.claude/launch.json` (port 8811, jamais le hub 8800 ;
   `NSGA2_RUNS` = `Documents\test\site_opt\runs`, qui doit contenir la copie du run flux et pas le run fictif).
2. `python tools/film/demo_regen.py` (la démo revient à son état de départ ; la prise la modifie).
3. Relancer le hub de test (terminal vide), puis `python tools/film/take.py`.
4. La vue 3D du hub revient sur demo_street (la prise finit sur canyon_street_1) : **`python tools/film/demo_regen.py --final`** (scène et période de la fin de s2, par Regenerate :
   la vue 3D du hub est rendue autrement après Regenerate ; la page fond l'image et la vue en 0,8 s aux deux bouts), puis
   `python tools/film/export_viewer.py` (visionneuse de la scène, avec ses facteurs de forme, nom canyon_street_1).
   Run fictif et son `C:\Domus - FMU\temp_opti\nsga_flux_<jeton>` à la corbeille.
5. Vérifier `media/` (premières et dernières images, `TOPS_FILM_DUMP`) avant de publier : aucune donnée personnelle.

## Pas encore fait
- Étape suivante : les champs dans la paroi (onglets Temperature field, flux de la simulation de s7).
- Netteté sur écrans fins : double densité = 12 images/s seulement (`SCALE` de rec.py), non retenue.
- Service du téléchargement par code (codes, 5 dernières versions, e-mail aux détenteurs d'un code).
