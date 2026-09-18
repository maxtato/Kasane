# -*- coding: utf-8 -*-
"""Version 4 : la V3 -- coins tete-beche, ni paysage ni couleur en japonais --
posee sur la tache de lavis beige qui sert desormais de fond a toute la serie.
Les chiffres et les formes y sont aussi un cran plus grands."""
import os, sys, importlib.util

ICI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "gen", os.path.join(ICI, "2-generer-cartes.py"))
gen = importlib.util.module_from_spec(_spec)
sys.modules["gen"] = gen
_spec.loader.exec_module(gen)

gen.COINS_SYMETRIQUES = True   # le chiffre et le cartouche occupent les 4 coins
gen.FOND = True                # tache de fond, commune aux 64 cartes

gen.OUT = "/Users/maximetatopoulos/App Max/Niko/cartes V4"
os.makedirs(gen.OUT, exist_ok=True)

if __name__ == "__main__":
    print(f"chiffre {gen.NUM_H} de haut, formes de {gen.CELL} "
          f"(empreinte {2 * gen.CELL + gen.GAP} pour {gen.W - 2 * gen.MARGE} entre marges)")
    for c in gen.CHIFFRES:
        for col, fr in gen.COULEURS:
            for f in gen.FORMES:
                gen.make_card(c, col, f, fr).save(
                    os.path.join(gen.OUT, f"carte-{gen.key(c, col, f)}.png"))
    print("cartes V4 ecrites:", len(os.listdir(gen.OUT)))
