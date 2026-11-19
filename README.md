# Prototype du site TOPS : chapitre « la scène »

Page qui défile : la vraie géométrie de `canyon_street_1` en 3D (three.js), pilotée par le défilement.

| Étape | Ce qui se passe |
|---|---|
| Titre | la rue tourne doucement, fin d'après-midi |
| 01 | les contours des faces de l'idf s'allument (303 faces, 35 zones) |
| 02 | la zone étudiée ressort, le reste s'assombrit |
| 03 | 4 niveaux → rue de 10 m → sans toits en pente → retour au projet (vraies variantes) |
| 04 | une journée du 21 juin à La Rochelle, ombres en temps réel |
| 05 | la caméra descend dans la rue devant la façade étudiée |

## Fichiers
- `index.html`, `css/site.css`, `js/story.js` : la page.
- `vendor/three.min.js` : three.js r128 (licence MIT, copie de celle du hub).
- `data/scene.json` / `data/scene.js` : géométrie des 4 variantes (même contenu ; le `.js` permet d'ouvrir la page
  sans serveur).
- `tools/make_scene.py` : refait `data/` avec le code du hub (`py2idf.urbanGeometry` dans un dossier temporaire ;
  les idf d'env ne sont pas touchés). Variantes : liste `VARIANTS`.
- `tools/serve.py` : aperçu local.

## Commandes
```
python tools/serve.py            # http://127.0.0.1:8840/
python tools/make_scene.py       # après un changement de canyon_street_1 ou des variantes
```

## Suite prévue
- Chapitres 06+ : formulaire et lancement (extraits vidéo en boucle), résultats d'optimisation (Plotly animé),
  champs du cas optimisé (carte de température pilotée par le défilement).
- La vidéo de 2-3 min = enregistrement de cette page avec un défilement automatique.
