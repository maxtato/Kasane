# -*- coding: utf-8 -*-
"""Export des images du jeu pour le navigateur. Les fichiers d'impression font
1346 x 2102 px et 2 Mo chacun, inutilisables dans une page. On sort ici des JPEG
de 300 px de large, aplatis sur le papier."""
import os
from PIL import Image

BASE = "/Users/maximetatopoulos/App Max/Niko"
JEU = os.path.join(BASE, "jeu", "img")
LARGEUR = 300
QUALITE = 82
PAPIER = (237, 230, 216)

CHIFFRES = ["1", "2", "3", "4"]
COULEURS = ["rouge", "bleu", "jaune", "vert"]
FORMES = ["cercle", "triangle", "carre", "croix"]


def exporter(src, dst):
    im = Image.open(src)
    if im.mode == "RGBA":
        fond = Image.new("RGB", im.size, PAPIER)
        fond.paste(im, (0, 0), im)
        im = fond
    else:
        im = im.convert("RGB")
    h = round(im.height * LARGEUR / im.width)
    im.resize((LARGEUR, h), Image.LANCZOS).save(dst, quality=QUALITE, optimize=True)


n = 0
# Seules les series aux coins tete-beche sont embarquees : un artifact publie
# plafonne a 256 fichiers, et les quatre series en font 295.
for version, dossier in [("v3", "cartes V3"), ("v4", "cartes V4")]:
    out = os.path.join(JEU, version)
    os.makedirs(out, exist_ok=True)
    for c in CHIFFRES:
        for col in COULEURS:
            for f in FORMES:
                nom = f"carte-{c}-{col}-{f}"
                exporter(os.path.join(BASE, dossier, nom + ".png"),
                         os.path.join(out, nom + ".jpg"))
                n += 1

# chaque serie embarquee a ses propres jokers, assortis a ses coins tete-beche
for dossier, sortie in [("jokers V3", "jokers-v3"), ("jokers V4", "jokers-v4")]:
    out = os.path.join(JEU, sortie)
    os.makedirs(out, exist_ok=True)
    for genre, vals in [("chiffre", CHIFFRES), ("couleur", COULEURS), ("forme", FORMES)]:
        for v in vals:
            nom = f"joker-{genre}-{v}"
            exporter(os.path.join(BASE, dossier, nom + ".png"),
                     os.path.join(out, nom + ".jpg"))
            n += 1

exporter(os.path.join(BASE, "dos.png"), os.path.join(JEU, "dos.jpg"))
n += 1

# le lettrage du titre garde sa transparence : il se pose sur le fond de la page
logo = Image.open(os.path.join(BASE, "assets", "logo-kasane.png")).convert("RGBA")
logo.thumbnail((520, 520), Image.LANCZOS)
logo.save(os.path.join(JEU, "logo.png"))
n += 1
print(f"{n} images exportees en {LARGEUR} px de large")
