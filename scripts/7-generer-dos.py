# -*- coding: utf-8 -*-
"""Dos des cartes. Pose l'illustration entiere sur le papier des cartes, avec la
meme marge, les memes coins et le meme filtre de vieillissement que le recto.

Usage : python3 7-generer-dos.py [chemin de l'image]
Sans argument, prend DOS_SRC."""
import sys, os
sys.path.insert(0, "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad")
from PIL import Image, ImageDraw
import gen

BASE = "/Users/maximetatopoulos/App Max/Niko"
SORTIE = os.path.join(BASE, "dos.png")
DOS_SRC = os.path.join(BASE, "assets",
                       "A0A00499-AA49-470A-8995-BB9F4ED8DD6F.PNG")

# L'illustration est posee sur le meme papier que le recto, avec une marge de
# papier identique sur les quatre cotes, egale a celle des cartes. Comme elle
# est de proportion plus large que le cadre ainsi defini, elle est mise a
# l'echelle sur la hauteur puis rognee a gauche et a droite, a parts egales.
# La marge sert aussi de fond perdu : une decoupe imprecise entame le papier,
# pas le motif.
DOS_MARGE = gen.MARGE     # meme marge que le recto, sur les quatre cotes


def dos(chemin):
    cadre = (gen.W - 2 * DOS_MARGE, gen.H - 2 * DOS_MARGE)

    im = Image.open(chemin).convert("RGBA")
    e = max(cadre[0] / im.width, cadre[1] / im.height)
    im = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
    gx, gy = (im.width - cadre[0]) // 2, (im.height - cadre[1]) // 2
    rogne = (gx, gy)
    im = im.crop((gx, gy, gx + cadre[0], gy + cadre[1]))

    card = gen.rounded_card(0x0D05)
    card.alpha_composite(im, (DOS_MARGE, DOS_MARGE))

    base = Image.new("RGB", (gen.W, gen.H), gen.PAPER)
    base.paste(card, (0, 0), card)
    out = gen.vieillir(base, 0x0D05).convert("RGBA")
    masque = Image.new("L", (gen.W, gen.H), 0)
    ImageDraw.Draw(masque).rounded_rectangle([0, 0, gen.W - 1, gen.H - 1],
                                             gen.RADIUS, fill=255)
    out.putalpha(masque)
    return out, cadre, e, rogne


if __name__ == "__main__":
    chemin = sys.argv[1] if len(sys.argv) > 1 else DOS_SRC
    print("source:", os.path.basename(chemin))
    img, cadre, e, rogne = dos(chemin)
    img.save(SORTIE)
    print(f"marge {DOS_MARGE} px sur les quatre cotes, cadre {cadre[0]}x{cadre[1]}")
    print(f"echelle {e:.3f}, rogne de {rogne[0]} px a gauche et a droite "
          f"et {rogne[1]} px en haut et en bas")
    print("ecrit:", SORTIE, img.size)
