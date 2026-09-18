# -*- coding: utf-8 -*-
"""Jokers : un par possibilite. Quatre jokers de chiffre, quatre de couleur,
quatre de forme. Meme papier, meme marge et meme filtre que les cartes."""
import sys, os
sys.path.insert(0, "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad")
from PIL import Image, ImageDraw
import gen

OUT = "/Users/maximetatopoulos/App Max/Niko/jokers"
os.makedirs(OUT, exist_ok=True)

W, H, M = gen.W, gen.H, gen.MARGE

MOT_L       = gen.E(400)    # largeur du lettrage JOKER, en haut
CARTOUCHE_L = gen.E(330)    # largeur du rectangle japonais, en bas
ECART       = gen.E(40)     # respiration autour de la zone centrale

TAILLE_CHIFFRE = gen.E(860)   # hauteur du chiffre
TAILLE_FORME   = gen.E(680)   # cote du motif de la forme, mesure comme sur les cartes
TAILLE_TACHE   = gen.E(900)   # hauteur de la tache de couleur


def joker(genre, valeur):
    seed = hash(("joker", genre, valeur)) & 0xFFFF
    card = gen.rounded_card(seed)

    mot = gen.fit(gen.A("joker-mot"), box_w=MOT_L)
    card.alpha_composite(mot, ((W - mot.width) // 2, M))

    crt = gen.fit(gen.A("joker-cartouche"), box_w=CARTOUCHE_L)
    card.alpha_composite(crt, ((W - crt.width) // 2, H - M - crt.height))

    haut = M + mot.height + ECART
    bas = H - M - crt.height - ECART
    cx, cy = W // 2, (haut + bas) // 2

    if genre == "chiffre":
        el = gen.fit(gen.A(f"chiffre-{valeur}"), box_h=TAILLE_CHIFFRE, box_w=W - 2 * M)
        card.alpha_composite(el, (cx - el.width // 2, cy - el.height // 2))
    elif genre == "couleur":
        el = gen.fit(gen.A(f"tache-{valeur}"), box_h=TAILLE_TACHE, box_w=W - 2 * M)
        card.alpha_composite(el, (cx - el.width // 2, cy - el.height // 2))
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


JOKERS = ([("chiffre", c) for c in gen.CHIFFRES]
          + [("couleur", c) for c, _ in gen.COULEURS]
          + [("forme", f) for f in gen.FORMES])

if __name__ == "__main__":
    m = gen.fit(gen.A("joker-mot"), box_w=MOT_L)
    c = gen.fit(gen.A("joker-cartouche"), box_w=CARTOUCHE_L)
    print(f"mot {m.size}, cartouche {c.size}, "
          f"zone centrale de {M + m.height + ECART} a {H - M - c.height - ECART}")
    for genre, valeur in JOKERS:
        joker(genre, valeur).save(os.path.join(OUT, f"joker-{genre}-{valeur}.png"))
    print("jokers ecrits:", len(os.listdir(OUT)))
