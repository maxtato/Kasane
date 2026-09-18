# -*- coding: utf-8 -*-
"""Jokers de la V4 : memes coins tete-beche que les jokers V3, poses sur la
tache de lavis beige qui sert de fond a toute la serie."""
import os, sys, importlib.util
from PIL import Image, ImageDraw

ICI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "gen", os.path.join(ICI, "2-generer-cartes.py"))
gen = importlib.util.module_from_spec(_spec)
sys.modules["gen"] = gen
_spec.loader.exec_module(gen)

OUT = "/Users/maximetatopoulos/App Max/Niko/jokers V4"
os.makedirs(OUT, exist_ok=True)

W, H, M, E = gen.W, gen.H, gen.MARGE, gen.E

MOT_L       = E(300)   # largeur du mot JOKER, dans le coin
CARTOUCHE_L = E(255)   # largeur du cartouche japonais

TAILLE_CHIFFRE = E(860)
TAILLE_FORME   = E(680)
TAILLE_TACHE   = E(900)


def joker(genre, valeur):
    seed = hash(("joker4", genre, valeur)) & 0xFFFF
    card = gen.rounded_card(seed)
    if gen.FOND:
        gen.poser_fond(card)

    mot = gen.fit(gen.A("joker-mot"), box_w=MOT_L)
    crt = gen.fit(gen.A("joker-cartouche"), box_w=CARTOUCHE_L)
    card.alpha_composite(mot, (M, M))
    card.alpha_composite(crt, (W - M - crt.width, M))
    card.alpha_composite(crt.rotate(180), (M, H - M - crt.height))
    card.alpha_composite(mot.rotate(180), (W - M - mot.width, H - M - mot.height))

    cx, cy = W // 2, H // 2
    if genre in ("chiffre", "couleur"):
        el = gen.fit(gen.A(f"chiffre-{valeur}" if genre == "chiffre" else f"tache-{valeur}"),
                     box_h=TAILLE_CHIFFRE if genre == "chiffre" else TAILLE_TACHE,
                     box_w=W - 2 * M)
        # on centre sur le dessin lui-meme, pas sur le cadre du fichier : les
        # projections d'encre sont asymetriques et decalaient le 2 et le 3
        mcx, mcy = gen.coeur(el)
        card.alpha_composite(el, (round(cx - mcx), round(cy - mcy)))
    else:
        el, (mcx, mcy) = gen.forme_calibree(valeur, "noir", TAILLE_FORME)
        card.alpha_composite(el, (round(cx - mcx), round(cy - mcy)))

    base = Image.new("RGB", (W, H), gen.PAPER)
    base.paste(card, (0, 0), card)
    out = gen.vieillir(base, seed).convert("RGBA")
    masque = Image.new("L", (W, H), 0)
    ImageDraw.Draw(masque).rounded_rectangle([0, 0, W - 1, H - 1], gen.RADIUS, fill=255)
    out.putalpha(masque)
    return out


if __name__ == "__main__":
    for genre, vals in [("chiffre", gen.CHIFFRES),
                        ("couleur", [c for c, _ in gen.COULEURS]),
                        ("forme", gen.FORMES)]:
        for v in vals:
            joker(genre, v).save(os.path.join(OUT, f"joker-{genre}-{v}.png"))
    print("jokers V4 ecrits:", len(os.listdir(OUT)))
