# -*- coding: utf-8 -*-
"""Version 3 : pas de paysage, pas de couleur en japonais. Le chiffre et son
cartouche rouge occupent les quatre coins, reportes tete-beche a l'oppose, comme
sur une carte a jouer : la carte se lit pareil dans les deux sens."""
import sys, os
sys.path.insert(0, "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad")
import gen

gen.COINS_SYMETRIQUES = True
# sans paysage, les formes peuvent occuper toute la hauteur libre : c'est la
# largeur entre les marges qui les limite desormais
gen.CELL = gen.E(385)
gen.CELL_CHIFFRE = {"1": gen.E(520)}

gen.OUT = "/Users/maximetatopoulos/App Max/Niko/cartes V3"
os.makedirs(gen.OUT, exist_ok=True)

half = (gen.CELL + gen.GAP) // 2
print(f"chiffre {gen.MARGE + gen.NUM_H} en haut, formes "
      f"{gen.H // 2 - half - gen.CELL // 2} a {gen.H // 2 + half + gen.CELL // 2}, "
      f"chiffre du bas a partir de {gen.H - gen.MARGE - gen.NUM_H}")
print(f"empreinte {2 * gen.CELL + gen.GAP} pour {gen.W - 2 * gen.MARGE} de large")

for c in gen.CHIFFRES:
    for col, fr in gen.COULEURS:
        for f in gen.FORMES:
            gen.make_card(c, col, f, fr).save(
                os.path.join(gen.OUT, f"carte-{gen.key(c, col, f)}.png"))
print("cartes V3 ecrites:", len(os.listdir(gen.OUT)))
