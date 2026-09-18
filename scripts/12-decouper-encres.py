# -*- coding: utf-8 -*-
"""Decoupe la planche de paysages a l'encre en motifs individuels detoures."""
import os, numpy as np
from PIL import Image, ImageFilter

BASE = "/Users/maximetatopoulos/App Max/Niko"
# Les planches de paysages, toutes montees en grille de motifs separes par du
# blanc. On garde les versions claires : les foncees ecrasent le papier.
PLANCHES = [
    "09B823FA-AD9C-4DA0-B082-2DF9B7F49D32.PNG",
    "8A65BDA4-8872-4BA5-80AB-B4607E75D66A.PNG",
    "2C13EA25-6DE1-47BD-994A-43E31C05F129.PNG",
]
DST  = os.path.join(BASE, "assets", "encres")
SEUIL = 6          # au-dela de ce niveau d'encre on considere le pixel peint
VIDE  = 5          # largeur mini d'une bande blanche pour separer deux motifs

# Les motifs sortent de la planche a 220 px de large et sont poses a plus de
# 700 px sur la carte : on les reechantillonne une bonne fois pour toutes plutot
# que de les laisser s'interpoler a chaque composition.
AGRANDIR = 3
NETTETE = (2, 55, 3)      # rayon, force, seuil du masque flou

# Les traits fins tres denses -- tiges de bambou, portique, branches -- montent a
# l'opacite maximale pendant que le lavis autour plafonne vers 0.2. Une fois la
# tache posee en filigrane, on ne voyait plus qu'eux. On ecrase donc le haut de
# l'echelle : en dessous du COUDE rien ne bouge, au-dessus l'opacite tend vers
# PLAFOND sans jamais l'atteindre.
COUDE = 0.34
PLAFOND = 0.56
ECLAIRCIR = 0.0    # part de blanc melangee a l'encre

def bandes(profil, vide):
    """Retourne les intervalles [debut, fin) ou le profil est non nul."""
    plein = profil > 0
    res, deb = [], None
    for i, p in enumerate(plein):
        if p and deb is None:
            deb = i
        elif not p and deb is not None:
            if i - deb > 0:
                res.append([deb, i])
            deb = None
    if deb is not None:
        res.append([deb, len(plein)])
    # fusionne les intervalles separes par moins de `vide` pixels
    fus = []
    for d, f in res:
        if fus and d - fus[-1][1] < vide:
            fus[-1][1] = f
        else:
            fus.append([d, f])
    return fus

def tasser(a):
    """Ecrase le haut de l'echelle d'opacite pour que les traits fins ne sortent
    plus du lavis. Continu et de pente 1 au coude, donc sans cassure visible."""
    t = a / 255.0
    haut = t > COUDE
    marge = PLAFOND - COUDE
    t[haut] = COUDE + marge * (1 - np.exp(-(t[haut] - COUDE) / marge))
    return t * 255.0


def detourer(rgb, alpha):
    """Retire le blanc : l'opacite vient de la densite d'encre."""
    a = tasser(alpha.astype(np.float32))
    couv = np.maximum(alpha.astype(np.float32), 1)[..., None]
    col = (rgb.astype(np.float32) - (255 - couv)) / couv * 255
    col = np.clip(col, 0, 255)
    col += (255 - col) * ECLAIRCIR
    out = np.dstack([col, a]).astype(np.uint8)
    img = Image.fromarray(out.astype(np.uint8), "RGBA")
    if AGRANDIR > 1:
        img = img.resize((img.width * AGRANDIR, img.height * AGRANDIR),
                         Image.LANCZOS)
        img = img.filter(ImageFilter.UnsharpMask(*NETTETE))
    return img

os.makedirs(DST, exist_ok=True)
for f in os.listdir(DST):
    os.remove(os.path.join(DST, f))

n = 0
for planche in PLANCHES:
    src = np.asarray(Image.open(os.path.join(BASE, "assets", planche)).convert("RGB"))
    encre = 255 - src.min(axis=2)
    masque = encre > SEUIL
    for x0, x1 in bandes(masque.sum(axis=0), 20):
        colonne = masque[:, x0:x1]
        for y0, y1 in bandes(colonne.sum(axis=1), VIDE):
            bloc = masque[y0:y1, x0:x1]
            if bloc.sum() < 3000:
                continue
            # recadrage serre sur le motif
            ys, xs = np.where(bloc)
            ry0, ry1 = y0 + ys.min(), y0 + ys.max() + 1
            rx0, rx1 = x0 + xs.min(), x0 + xs.max() + 1
            a = encre[ry0:ry1, rx0:rx1].copy()
            a[a <= SEUIL] = 0
            img = detourer(src[ry0:ry1, rx0:rx1], a)
            n += 1
            img.save(os.path.join(DST, f"encre-{n:02d}.png"))
            print(f"encre-{n:02d}.png  {img.width}x{img.height}  ({planche[:8]})")
print("motifs:", n)
