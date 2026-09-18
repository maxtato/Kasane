# -*- coding: utf-8 -*-
"""Comparatif d'effets de vieillissement sur une meme carte."""
import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad")
from PIL import Image, ImageDraw, ImageFont
import gen

SP = "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad"
CARTE = ("2", "bleu", "triangle", "BLEU")     # beaucoup de papier nu, effets bien visibles

BASE = dict(desat=0, sepia=(1.0, 1.0, 1.0), taches=0, taches_echelle=18, taches_flou=16,
            grain=0, grain_sigma=20, fibres=0, bords=0, piqures=0, rayures=0, nettete=0)


def cfg(**kw):
    c = dict(BASE); c.update(kw); return c


EFFETS = [
    ("A  aucun", cfg()),
    ("B  grain fin seul", cfg(grain=0.09, grain_sigma=14, piqures=120)),
    ("C  sepia + grain", cfg(desat=0.10, sepia=(1.03, 1.0, 0.935), grain=0.08,
                             grain_sigma=16, piqures=150)),
    ("D  taches fines", cfg(taches=0.10, taches_echelle=7, taches_flou=4,
                            grain=0.05, grain_sigma=18, piqures=150)),
    ("E  taches larges", cfg(taches=0.10, taches_echelle=26, taches_flou=22,
                             grain=0.05, grain_sigma=18, piqures=150)),
    ("F  fibres papier", cfg(desat=0.08, sepia=(1.03, 1.0, 0.94), fibres=0.07,
                             grain=0.06, grain_sigma=16, piqures=160)),
    ("G  complet + nettete", cfg(desat=0.10, sepia=(1.03, 1.0, 0.935), taches=0.08,
                                 taches_echelle=10, taches_flou=6, grain=0.07,
                                 grain_sigma=16, bords=0.10, piqures=160, nettete=0.55)),
    ("H  usure marquee", cfg(desat=0.16, sepia=(1.04, 1.0, 0.92), taches=0.13,
                             taches_echelle=9, taches_flou=5, grain=0.08,
                             grain_sigma=14, bords=0.16, piqures=260, rayures=40,
                             nettete=0.45)),
]

orig = gen.vieillir
cartes = []
for nom, c in EFFETS:
    gen.vieillir = lambda rgb, seed, _c=c: orig(rgb, seed, _c)
    cartes.append((nom, gen.make_card(*CARTE)))
gen.vieillir = orig

FOND = (250, 248, 244)
f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)


def plat(im, size=None):
    bg = Image.new("RGB", im.size, FOND); bg.paste(im, (0, 0), im)
    return bg.resize(size, Image.LANCZOS) if size else bg


# planche 1 : cartes entieres
sc = 0.30
tw, th = int(gen.W * sc), int(gen.H * sc)
pad, lab = 16, 36
s = Image.new("RGB", (4 * (tw + pad) + pad, 2 * (th + pad + lab) + pad), (236, 230, 220))
d = ImageDraw.Draw(s)
for i, (nom, im) in enumerate(cartes):
    x = pad + (i % 4) * (tw + pad); y = pad + (i // 4) * (th + pad + lab)
    s.paste(plat(im, (tw, th)), (x, y))
    d.text((x + 2, y + th + 8), nom, font=f, fill=(50, 42, 34))
s.save(f"{SP}/effets_cartes.png")

# planche 2 : detail a taille reelle, zone de papier nu a droite du chiffre
box = (600, 150, 1000, 550)
cw, ch = box[2] - box[0], box[3] - box[1]
s = Image.new("RGB", (4 * (cw + pad) + pad, 2 * (ch + pad + lab) + pad), (236, 230, 220))
d = ImageDraw.Draw(s)
for i, (nom, im) in enumerate(cartes):
    x = pad + (i % 4) * (cw + pad); y = pad + (i // 4) * (ch + pad + lab)
    s.paste(plat(im).crop(box), (x, y))
    d.text((x + 2, y + ch + 8), nom, font=f, fill=(50, 42, 34))
s.save(f"{SP}/effets_detail.png")
print("ok")
