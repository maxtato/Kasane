# -*- coding: utf-8 -*-
"""Retire les projections de peinture isolees autour du lettrage du dos.

On ne touche qu'a la bande claire qui entoure le nom : les vagues bleues et les
fleurs gardent leurs eclaboussures. Le lettrage lui-meme, et tout ce qui le
touche a douze pixels pres, est protege. Les taches restantes sont bouchees par
la couleur du fond le plus proche, puis adoucies."""
import os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

BASE = "/Users/maximetatopoulos/App Max/Niko"
SRC = os.path.join(BASE, "assets", "9B33C97D-BDCC-45D2-AAF1-7A765F172061.PNG")
OUT = os.path.join(BASE, "assets", "dos-nettoye.png")

COTE_MINI = 28        # en deca, la tache est retiree
AIRE_LETTRAGE = 400   # au-dela, c'est du dessin : lettres latines et katakana
MARGE_LETTRAGE = 12   # rayon de protection autour de ce dessin


def nettoyer(chemin):
    im = Image.open(chemin).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]

    # la bande claire autour du nom, vue de loin pour ignorer les taches
    flou = np.asarray(Image.fromarray(lum.astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(34))).astype(np.float32)
    # on s'eloigne franchement des vagues : boucher une tache a cheval sur le
    # bleu laisserait une bavure grise
    clair = ndimage.binary_erosion(flou > 150, np.ones((21, 21), bool))

    # le lettrage : les grandes masses d'encre, elargies d'une marge
    encre = lum < 95
    lab, n = ndimage.label(encre)
    aires = ndimage.sum(encre, lab, range(1, n + 1))
    grandes = np.isin(lab, np.nonzero(aires > AIRE_LETTRAGE)[0] + 1)
    protege = ndimage.binary_dilation(
        grandes, ndimage.generate_binary_structure(2, 2), iterations=MARGE_LETTRAGE)

    taches = ((encre | ((r > 110) & (r - np.maximum(g, b) > 55)))
              & clair & ~protege)

    lab, n = ndimage.label(taches)
    boites = ndimage.find_objects(lab)
    petites = []
    for i, s in enumerate(boites):
        if max(s[0].stop - s[0].start, s[1].stop - s[1].start) >= COTE_MINI:
            continue
        # la tache doit etre entouree de creme, sinon le bouchage se verrait
        y0, y1 = max(0, s[0].start - 8), s[0].stop + 8
        x0, x1 = max(0, s[1].start - 8), s[1].stop + 8
        if clair[y0:y1, x0:x1].all():
            petites.append(i + 1)
    aretirer = ndimage.binary_dilation(np.isin(lab, petites), np.ones((5, 5), bool))

    # bouchage : chaque pixel retire prend la couleur du fond le plus proche
    _, idx = ndimage.distance_transform_edt(aretirer, return_indices=True)
    rempli = a[idx[0], idx[1]]
    doux = np.asarray(Image.fromarray(rempli.astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)
    a = np.where(aretirer[..., None], doux, a)
    return Image.fromarray(a.astype(np.uint8)), len(petites), n


if __name__ == "__main__":
    img, retirees, total = nettoyer(SRC)
    img.save(OUT)
    print(f"{retirees} taches retirees sur {total} reperees, {total - retirees} gardees")
    print("ecrit:", OUT)
