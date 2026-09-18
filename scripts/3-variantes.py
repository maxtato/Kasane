# -*- coding: utf-8 -*-
"""Balayage de reglages : hauteur du chiffre, taille de la forme, ecart."""
import sys, importlib
sys.path.insert(0, "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad")
from PIL import Image, ImageDraw, ImageFont
import gen

SP = "/private/tmp/claude-501/-Users-maximetatopoulos-App-Max/c1880ffe-fa40-4dae-8023-eb4240f6d0cc/scratchpad"

# (nom, hauteur chiffre, taille forme, ecart)
VARIANTES = [
    ("V01", 300, 380,  30),
    ("V02", 300, 400,   5),
    ("V03", 300, 405, -10),
    ("V04", 270, 400,  20),
    ("V05", 270, 415,   0),
    ("V06", 270, 430, -25),
    ("V07", 240, 430,   5),
    ("V08", 240, 440, -15),
    ("V09", 240, 450, -35),
    ("V10", 210, 460, -25),
]

CARTE = ("4", "vert", "croix", "VERT")     # le cas le plus dense
CARTE2 = ("2", "bleu", "triangle", "BLEU")  # la diagonale

def render(v, carte):
    _, nh, cell, gap = v
    gen.NUM_H, gen.CELL, gen.GAP = nh, cell, gap
    zx, zy, zw, zh = gen.zone()
    assert 2 * cell + gap <= zh, f"{v[0]}: debordement vertical {2*cell+gap} > {zh}"
    assert 2 * cell + gap <= zw, f"{v[0]}: debordement horizontal"
    return gen.make_card(*carte)


def sheet(carte, out, scale=0.30):
    f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
    tiles = []
    for v in VARIANTES:
        im = render(v, carte)
        im = im.resize((int(gen.W * scale), int(gen.H * scale)), Image.LANCZOS)
        tiles.append((v, im))
    tw, th = tiles[0][1].size
    cols, pad, lab = 5, 18, 40
    rows = (len(tiles) + cols - 1) // cols
    s = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + lab) + pad), (74, 52, 36))
    d = ImageDraw.Draw(s)
    for i, (v, im) in enumerate(tiles):
        x = pad + (i % cols) * (tw + pad)
        y = pad + (i // cols) * (th + pad + lab)
        s.paste(im, (x, y))
        d.text((x + 2, y + th + 8),
               f"{v[0]}  {v[1]} / {v[2]} / {v[3]:+d}", font=f, fill=(245, 238, 222))
    s.save(out)
    print(out, s.size)


sheet(CARTE, f"{SP}/variantes_4.png")
sheet(CARTE2, f"{SP}/variantes_2.png")
