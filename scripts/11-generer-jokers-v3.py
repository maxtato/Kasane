# -*- coding: utf-8 -*-
"""Jokers assortis a la V3 : le mot JOKER en haut a gauche, son equivalent
japonais dans le cartouche rouge en haut a droite, et les deux reportes
tete-beche en bas. Le joker se lit donc pareil dans les deux sens, comme les
cartes de la V3."""
import sys, os
sys.path.insert(0, "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad")
from PIL import Image, ImageDraw
import gen

OUT = "/Users/maximetatopoulos/App Max/Niko/jokers V3"
os.makedirs(OUT, exist_ok=True)

W, H, M, E = gen.W, gen.H, gen.MARGE, gen.E

MOT_L       = E(230)   # largeur du mot JOKER, dans le coin
CARTOUCHE_L = E(200)   # largeur du cartouche japonais

TAILLE_CHIFFRE = E(860)
TAILLE_FORME   = E(680)
TAILLE_TACHE   = E(900)


def joker(genre, valeur):
    seed = hash(("joker3", genre, valeur)) & 0xFFFF
    card = gen.rounded_card(seed)

    mot = gen.fit(gen.A("joker-mot"), box_w=MOT_L)
    crt = gen.fit(gen.A("joker-cartouche"), box_w=CARTOUCHE_L)
    card.alpha_composite(mot, (M, M))
    card.alpha_composite(crt, (W - M - crt.width, M))
    card.alpha_composite(crt.rotate(180), (M, H - M - crt.height))
    card.alpha_composite(mot.rotate(180), (W - M - mot.width, H - M - mot.height))

    cx, cy = W // 2, H // 2
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


if __name__ == "__main__":
    m = gen.fit(gen.A("joker-mot"), box_w=MOT_L)
    c = gen.fit(gen.A("joker-cartouche"), box_w=CARTOUCHE_L)
    print(f"mot {m.size}, cartouche {c.size}, "
          f"zone centrale de {M + m.height} a {H - M - m.height}")
    for genre, vals in [("chiffre", gen.CHIFFRES),
                        ("couleur", [c for c, _ in gen.COULEURS]),
                        ("forme", gen.FORMES)]:
        for v in vals:
            joker(genre, v).save(os.path.join(OUT, f"joker-{genre}-{v}.png"))
    print("jokers V3 ecrits:", len(os.listdir(OUT)))
