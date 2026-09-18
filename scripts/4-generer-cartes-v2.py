# -*- coding: utf-8 -*-
"""Version 2 : une seule forme par carte, quel que soit le chiffre, et chiffre
en haut a gauche a sa taille d'origine."""
import sys, os
sys.path.insert(0, "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad")
import gen

gen.MULTI = False
gen.NUM_H = gen.E(390)        # chiffre un cran en dessous
gen.CELL  = gen.E(570)        # taille du motif, identique sur les 64 cartes
gen.PAY_H = gen.E(340)     # une seule forme ici, le paysage peut rester ample

gen.OUT = "/Users/maximetatopoulos/App Max/Niko/cartes V2"
os.makedirs(gen.OUT, exist_ok=True)

zx, zy, zw, zh = gen.zone()
haut_forme = gen.H // 2 - gen.CELL // 2
bas_paysage = gen.H - gen.MARGE - gen.PAY_H
print(f"chiffre finit a {gen.MARGE + gen.NUM_H}, forme {haut_forme} -> {haut_forme + gen.CELL} "
      f"centree sur {gen.H // 2}, paysage a partir de {bas_paysage}")

for c in gen.CHIFFRES:
    for col, fr in gen.COULEURS:
        for f in gen.FORMES:
            img = gen.make_card(c, col, f, fr)
            img.save(os.path.join(gen.OUT, f"carte-{gen.key(c, col, f)}.png"))
print("cartes V2 ecrites:", len(os.listdir(gen.OUT)))
