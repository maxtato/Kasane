# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random, sys, math, json
import numpy as np

BASE   = "/Users/maximetatopoulos/App Max/Niko"
ASSETS = os.path.join(BASE, "assets")
OUT    = os.path.join(BASE, "cartes")
os.makedirs(OUT, exist_ok=True)

# Format bridge : 57 x 89 mm. La maquette a ete dessinee sur une carte de
# 1050 px de large, donc toutes les cotes sont exprimees dans ces unites puis
# converties a l'echelle de sortie par E(). Changer DPI change la definition
# sans toucher a la mise en page.
DPI = 600
CARTE_MM = (57, 89)
MAQUETTE_L = 1050

W = round(CARTE_MM[0] / 25.4 * DPI)
H = round(CARTE_MM[1] / 25.4 * DPI)
ECH = W / MAQUETTE_L


def E(v):
    """Convertit une cote de la maquette vers l'echelle de sortie."""
    return round(v * ECH)


RADIUS = 0        # les fichiers sortent rectangulaires, papier jusqu'au bord.
                  # L'arrondi des coins est fait par la coupe a l'impression,
                  # il n'a donc pas a etre dessine ici.
MARGE  = E(110)   # marge unique, elle commande toutes les positions
PAPER  = (237, 230, 216)
INK    = (22, 20, 18)

MULTI   = True    # autant de formes que le chiffre, au lieu d'une seule
# Disposition des coins. Par defaut : chiffre en haut a gauche, couleur en
# japonais en haut a droite, cartouche rouge en bas a gauche, paysage en bas a
# droite. En mode symetrique, le paysage et la couleur disparaissent, et le
# chiffre comme le cartouche sont reportes a l'oppose tete-beche : la carte se
# lit alors de la meme facon dans les deux sens, comme une carte a jouer.
COINS_SYMETRIQUES = False
SOLO_AU_CENTRE = True   # forme unique posee au milieu de la carte, pas au milieu
                        # de l'espace libre entre le chiffre et le paysage

# Hauteur du chiffre en haut a gauche.
NUM_H = E(268)

# Taille d'une forme, identique sur les 64 cartes : elle est calee sur le cas le
# plus contraint, le carre de quatre formes. GAP peut etre negatif, les formes se
# chevauchent alors legerement par les coins.
CELL = E(405)
GAP  = E(0)   # negatif : les cadres des formes se chevauchent un peu par
                # les coins, les traits eux-memes ne se touchent pas

# La carte a une seule forme n'a aucune contrainte de voisinage, sa forme peut
# donc respirer davantage que celles des cartes 2, 3 et 4.
CELL_CHIFFRE = {"1": E(547)}

# Zone centrale reservee aux formes : elle commence sous le chiffre et s'arrete
# juste au-dessus du paysage. Tout se deduit de la marge.
ZONE_TOP_PAD, ZONE_BAS_PAD = E(24), E(18)


def zone():
    y = MARGE + NUM_H + ZONE_TOP_PAD
    bas = H - MARGE - PAY_H - ZONE_BAS_PAD
    return MARGE, y, W - 2 * MARGE, bas - y

# Positions en demi-pas depuis le centre de la zone.
DISPOSITIONS = {
    "1": [(0, 0)],                                    # une forme, centree
    "2": [(0, -1), (0, 1)],                           # l'une sous l'autre
    "3": [(0, -1), (-1, 1), (1, 1)],                  # pyramide
    "4": [(-1, -1), (1, -1), (-1, 1), (1, 1)],        # carre
}

COULEURS = [("rouge", "ROUGE"), ("bleu", "BLEU"), ("jaune", "JAUNE"), ("vert", "VERT")]
# Teintes relevees sur l'encre des formes elles-memes, pour que la pastille et
# les formes de la carte soient exactement de la meme couleur.
RVB = {"rouge": (196, 4, 5), "bleu": (2, 58, 122),
       "jaune": (223, 142, 5), "vert": (5, 59, 28)}
FORMES   = ["cercle", "triangle", "carre", "croix"]
CHIFFRES = ["1", "2", "3", "4"]


# Filtre de vieillissement pose sur la carte terminee : il agit donc aussi sur
# le chiffre, les formes et le paysage, ce qui les fait appartenir au meme papier.
# Filtre de vieillissement pose sur la carte terminee : il agit donc aussi sur
# le chiffre, les formes et le paysage, ce qui les fait appartenir au meme papier.
# Tous les reglages passent par AGE, ce qui permet de comparer des effets.
AGE = dict(            # variante F du comparatif : fibres de papier
    desat=0.08,          # part de desaturation
    sepia=(1.026, 1.000, 0.950),
    taches=0.0,          # pas d'aureoles d'humidite, c'est ce qui voilait l'image
    taches_echelle=10,
    taches_flou=E(6),
    grain=0.06,          # grain du papier
    grain_sigma=16,      # plus petit = grain plus contraste
    fibres=0.07,         # stries horizontales du papier
    bords=0.0,           # le fond de papier assombrit deja les bords
    piqures=round(160 * ECH ** 2),         # piqures d'encre
    rayures=0,           # eraflures fines
    nettete=0.0,         # renforcement de nettete
)


def vieillir(rgb, seed, cfg=None):
    c = dict(AGE) if cfg is None else dict(cfg)
    rnd = random.Random(seed ^ 0x5EED)
    a = np.asarray(rgb).astype(np.float32)
    h, w = a.shape[:2]

    if c["desat"]:
        gris = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
        a = a * (1 - c["desat"]) + gris[..., None] * c["desat"]
    a *= np.array(c["sepia"], dtype=np.float32)

    if c["taches"]:
        e = max(2, c["taches_echelle"])
        t = Image.effect_noise((max(2, w // e), max(2, h // e)), 110)
        t = t.resize((w, h), Image.BICUBIC)
        if c["taches_flou"]:
            t = t.filter(ImageFilter.GaussianBlur(c["taches_flou"]))
        tn = np.asarray(t).astype(np.float32) / 255.0
        a *= (1 - c["taches"] * np.clip((tn - 0.5) * 2, 0, 1))[..., None]

    if c["grain"]:
        g = np.asarray(Image.effect_noise((w, h), c["grain_sigma"])).astype(np.float32)
        a *= (1 + c["grain"] * (g / 255.0 - 0.5))[..., None]

    if c["fibres"]:
        lignes = np.asarray(Image.effect_noise((w, max(2, h // 3)), 40)
                            .resize((w, h), Image.BILINEAR)).astype(np.float32)
        a *= (1 + c["fibres"] * (lignes / 255.0 - 0.5))[..., None]

    if c["bords"]:
        b = Image.new("L", (w, h), 0)
        ImageDraw.Draw(b).rounded_rectangle([E(46), E(46), w - 1 - E(46), h - 1 - E(46)],
                                            RADIUS, fill=255)
        v = np.asarray(b.filter(ImageFilter.GaussianBlur(E(38)))).astype(np.float32) / 255.0
        a *= (1 - c["bords"] * (1 - v))[..., None]

    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    if c["nettete"]:
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=int(c["nettete"] * 100),
                                                 threshold=2))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(c["piqures"]):
        x, y = rnd.randint(10, w - 10), rnd.randint(10, h - 10)
        r = E(rnd.choice([0, 0, 1, 1, 2]))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(92, 74, 52, rnd.randint(20, 70)))
    for _ in range(c["rayures"]):
        x, y = rnd.randint(30, w - 30), rnd.randint(30, h - 30)
        lg = rnd.randint(40, 220)
        ang = rnd.uniform(-0.35, 0.35) + rnd.choice([0, math.pi / 2])
        d.line([x, y, x + lg * math.cos(ang), y + lg * math.sin(ang)],
               fill=(120, 104, 80, rnd.randint(14, 34)), width=1)
    return img


def paper_texture(w, h, seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h), PAPER)
    # grain fin
    noise = Image.effect_noise((w, h), 26).convert("L")
    img = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.055)
    # nuages de vieillissement
    small = Image.effect_noise((w // 22, h // 22), 90).convert("L")
    small = small.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(E(24)))
    stain = Image.new("RGB", (w, h), (185, 169, 139))
    img = Image.composite(stain, img, small.point(lambda v: int(max(0, v - 150) * 0.9)))
    # quelques taches
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(16):
        x, y = rnd.randint(0, w), rnd.randint(0, h)
        r = E(rnd.randint(30, 150))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(170, 148, 112, rnd.randint(6, 16)))
    img = img.filter(ImageFilter.GaussianBlur(0.4 * ECH))
    # assombrissement des bords
    vig = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vig)
    vd.rounded_rectangle([E(8), E(8), w - 1 - E(8), h - 1 - E(8)],
                         max(0, RADIUS - E(8)), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(E(26)))
    dark = Image.new("RGB", (w, h), (214, 203, 181))
    img = Image.composite(img, dark, vig)
    return img


def rounded_card(seed):
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tex = paper_texture(W, H, seed).convert("RGBA")
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], RADIUS, fill=255)
    card.paste(tex, (0, 0), mask)
    return card


def fit(im, box_w=None, box_h=None):
    w, h = im.size
    s = min(box_w / w if box_w else 1e9, box_h / h if box_h else 1e9)
    return im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)


with open(os.path.join(ASSETS, "formes-cadres.json")) as _fh:
    CADRES = json.load(_fh)


def forme_calibree(forme, couleur, taille=None):
    """Redimensionne la forme pour que son motif, eclaboussures exclues, occupe
    exactement `taille` en largeur comme en hauteur. Renvoie l'image et le centre du
    motif dans cette image, pour pouvoir la poser au bon endroit."""
    nom = f"forme-{forme}-{couleur}"
    t = CELL if taille is None else taille
    x0, y0, x1, y1 = CADRES[nom]
    im = A(nom)
    sx, sy = t / (x1 - x0), t / (y1 - y0)
    im = im.resize((round(im.width * sx), round(im.height * sy)), Image.LANCZOS)
    return im, ((x0 + x1) / 2 * sx, (y0 + y1) / 2 * sy)


# Pastille du coin haut droit : le rectangle peint qui portait le chiffre
# japonais, rempli de la couleur de la carte, avec la forme evidee dedans --
# c'est le papier qu'on lit au travers, pas une encre plus claire.
PASTILLE_SRC = "cartouche-1"
PASTILLE_H = E(215)     # hauteur du rectangle peint, eclaboussures exclues
PASTILLE_FORME = 0.58   # part du petit cote du rectangle occupee par la forme

_PASTILLES = {}


def pastille(couleur, forme):
    """Renvoie la pastille et le cadre du rectangle peint dans l'image, les
    projections d'encre exclues : c'est sur ce cadre qu'on aligne le coin, pas
    sur le fichier, sinon les eclaboussures decaleraient la pastille."""
    cle = (couleur, forme)
    if cle in _PASTILLES:
        return _PASTILLES[cle]
    from scipy import ndimage

    a = np.asarray(A(PASTILLE_SRC).getchannel("A"))
    # le chiffre japonais etait evide dans la peinture : on rebouche, le bord
    # au pinceau et les eclaboussures sont conserves tels quels
    plein = ndimage.binary_fill_holes(a > 128)
    alpha = np.maximum(a, plein * 255).astype(np.float32)

    # cadre du rectangle seul, pour la mise a l'echelle comme pour le calage
    lab, n = ndimage.label(plein)
    tailles = ndimage.sum(plein, lab, range(1, n + 1))
    ys, xs = ndimage.find_objects(lab)[int(np.argmax(tailles))]

    e = PASTILLE_H / (ys.stop - ys.start)
    im = Image.fromarray(np.dstack([
        np.broadcast_to(np.array(RVB[couleur], dtype=np.float32), alpha.shape + (3,)),
        alpha]).astype(np.uint8))
    im = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
    cadre = (round(xs.start * e), round(ys.start * e),
             round(xs.stop * e), round(ys.stop * e))

    # la forme se pose au centre du rectangle, puis se retire de son opacite
    cote = round(min(cadre[2] - cadre[0], cadre[3] - cadre[1]) * PASTILLE_FORME)
    shp, (mcx, mcy) = forme_calibree(forme, "noir", cote)
    m = shp.getchannel("A")
    trou = Image.new("L", im.size, 0)
    trou.paste(m, (round((cadre[0] + cadre[2]) / 2 - mcx),
                   round((cadre[1] + cadre[3]) / 2 - mcy)), m)
    av = np.asarray(im.getchannel("A")).astype(np.float32)
    av *= 1 - np.asarray(trou).astype(np.float32) / 255.0
    im.putalpha(Image.fromarray(av.astype(np.uint8)))

    _PASTILLES[cle] = (im, cadre)
    return _PASTILLES[cle]


def coeur(im):
    """Centre du motif principal d'une image, eclaboussures exclues. Les
    chiffres et les taches portent des projections asymetriques : se caler sur
    le cadre du fichier decale le dessin de plusieurs pour cent. On prend donc
    la plus grosse composante connexe du masque d'opacite dilate, comme pour
    les formes."""
    from scipy import ndimage
    m = np.asarray(im)[..., 3] > 24
    d = max(4, round(min(im.size) * 0.04))
    lab, n = ndimage.label(ndimage.binary_dilation(m, np.ones((d, d))))
    if not n:
        return im.width / 2, im.height / 2
    tailles = ndimage.sum(m, lab, range(1, n + 1))
    y, x = ndimage.find_objects(lab)[int(np.argmax(tailles))]
    return (x.start + x.stop) / 2, (y.start + y.stop) / 2


def A(name):
    return Image.open(os.path.join(ASSETS, name + ".png")).convert("RGBA")


# Les quatre paysages n'ont pas le meme cadrage d'origine. On garde la partie
# utile de chacun, puis on les ramene tous au meme rapport pour qu'ils occupent
# la meme surface sur la carte.
# Le paysage se pose en bas a droite. Les quatre fichiers sont ramenes a la meme
# hauteur, donc a la meme ligne de base, mais ils n'ont pas la meme proportion :
# la vague est deux fois plus large que haute, la pagode plus de trois fois. On
# definit donc une fenetre qui part juste a droite du cartouche rouge et va
# jusqu'a la marge droite, et tout ce qui depasse est coupe a gauche.
PAY_H = E(295)          # hauteur commune des quatre paysages
PAY_ECART = E(16)       # toute petite marge avec le cartouche rouge


PAY_SEUIL_BASE = 0.05   # part de la masse d'encre maximale au-dela de laquelle
                        # une ligne est consideree comme faisant partie du dessin


def paysage(couleur, bord_cartouche):
    """Renvoie le paysage a la hauteur commune, coupe a gauche si besoin, et la
    hauteur de sa traine de lavis pale. Les quatre dessins ne finissent pas de la
    meme facon : il reste 41 px de brume sous les montagnes rouges contre 3 px
    sous la vague. Poser sur le bas du fichier mettait donc le rouge 30 px plus
    haut que les autres, on pose donc sur la derniere ligne vraiment dessinee."""
    im = A(f"paysage-{couleur}")
    e = PAY_H / im.height
    im = im.resize((round(im.width * e), PAY_H), Image.LANCZOS)
    largeur = (W - MARGE) - (bord_cartouche + PAY_ECART)
    if im.width > largeur:
        im = im.crop((im.width - largeur, 0, im.width, im.height))

    prof = np.asarray(im)[..., 3].astype(np.float32).sum(axis=1)
    dense = np.where(prof > PAY_SEUIL_BASE * prof.max())[0]
    return im, im.height - 1 - int(dense.max())



# Paysages a l'encre poses en fond des deux quarts opposes de la carte. Ils sont
# tires au sort carte par carte, et celui du bas est le meme retourne a 180 :
# comme le chiffre et le cartouche, le decor se lit pareil dans les deux sens.
# Tache de lavis posee en fond de toutes les cartes, sous le chiffre, le
# cartouche et les formes. Elle est identique partout : c'est le fond du jeu,
# pas un decor tire au sort.
FOND = True
FOND_OPACITE = 1.0      # la discretion vient de la teinte, pas de la transparence
FOND_LARGEUR = 1.0      # part de la largeur de carte occupee par la tache
# La tache arrive en gris neutre, qui tranche sur le papier chaud. On la
# reteinte donc dans la gamme du papier : seule sa luminosite est conservee,
# etalee entre ces deux tons. Le clair est un papier a peine assombri, le
# sombre un papier bruni -- en s'assombrissant, un papier se sature, il ne vire
# pas au gris.
FOND_RETEINTE = True    # False : on garde la couleur du fichier telle quelle
FOND_CLAIR  = (230, 219, 198)
FOND_SOMBRE = (210, 189, 159)

_FOND = None


def tache_fond():
    """Tache mise a l'echelle de la carte et voilee, calculee une seule fois."""
    global _FOND
    if _FOND is not None:
        return _FOND
    im = A("tache-fond")
    im = fit(im, box_w=round(W * FOND_LARGEUR))
    a = np.asarray(im).astype(np.float32)
    if not FOND_RETEINTE:
        a[..., 3] *= FOND_OPACITE
        _FOND = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        return _FOND
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    peint = a[..., 3] > 8
    if peint.any():
        bas, haut = np.percentile(lum[peint], (2, 98))
        t = np.clip((lum - bas) / max(haut - bas, 1), 0, 1)
    else:
        t = np.zeros_like(lum)
    clair = np.array(FOND_CLAIR, dtype=np.float32)
    sombre = np.array(FOND_SOMBRE, dtype=np.float32)
    a[..., :3] = sombre + (clair - sombre) * t[..., None]
    a[..., 3] *= FOND_OPACITE
    _FOND = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return _FOND


def poser_fond(card):
    im = tache_fond()
    card.alpha_composite(im, ((W - im.width) // 2, (H - im.height) // 2))


def make_card(chiffre, couleur, forme, label_fr):
    seed = hash((chiffre, couleur, forme)) & 0xFFFF
    card = rounded_card(seed)

    if FOND:
        poser_fond(card)

    # Les quatre coins : le chiffre en chiffres arabes en haut a gauche, la
    # couleur en japonais en haut a droite, le meme chiffre en japonais dans son
    # cartouche rouge en bas a gauche, le paysage en bas a droite.
    num = fit(A(f"chiffre-{chiffre}"), box_h=NUM_H, box_w=int(NUM_H * 0.97))
    card.alpha_composite(num, (MARGE, MARGE))

    if COINS_SYMETRIQUES:
        # plus de japonais : la couleur et la forme se lisent dans la pastille
        pst, cadre = pastille(couleur, forme)
        px, py = W - MARGE - cadre[2], MARGE - cadre[1]
        card.alpha_composite(pst, (px, py))
        card.alpha_composite(pst.rotate(180),
                             (W - px - pst.width, H - py - pst.height))
        card.alpha_composite(num.rotate(180),
                             (W - MARGE - num.width, H - MARGE - num.height))
    else:
        crt = fit(A(f"cartouche-{chiffre}"), box_h=E(140), box_w=E(140))
        kj = fit(A(f"kanji-couleur-{couleur}"), box_h=E(132), box_w=E(150))
        card.alpha_composite(kj, (W - MARGE - kj.width, MARGE + E(12)))
        card.alpha_composite(crt, (MARGE, H - MARGE - crt.height))
        # le paysage est coupe juste a droite du cartouche rouge
        pay, traine = paysage(couleur, MARGE + crt.width)
        card.alpha_composite(pay, (W - MARGE - pay.width,
                                   H - MARGE - pay.height + traine))

    zx, zy, zw, zh = zone()
    # les formes se centrent sur le milieu de la carte, pas sur le milieu de
    # l'espace libre : le chiffre est petit et le paysage bas, ce milieu-la
    # tombait 70 px trop haut
    gcx, gcy = W // 2, H // 2
    if MULTI:
        half = (CELL + GAP) // 2
        shp, (mcx, mcy) = forme_calibree(forme, couleur,
                                         CELL_CHIFFRE.get(chiffre, CELL))
        for ox, oy in DISPOSITIONS[chiffre]:
            cxx, cyy = gcx + ox * half, gcy + oy * half
            card.alpha_composite(shp, (round(cxx - mcx), round(cyy - mcy)))
    else:
        # une seule forme, quel que soit le chiffre, calibree comme les autres
        shp, (mcx, mcy) = forme_calibree(forme, couleur)
        cx, cy = (W // 2, H // 2) if SOLO_AU_CENTRE else (gcx, gcy)
        card.alpha_composite(shp, (round(cx - mcx), round(cy - mcy)))

    # aplati sur le papier, vieilli, puis on rend les coins arrondis au fichier
    base = Image.new("RGB", (W, H), PAPER)
    base.paste(card, (0, 0), card)
    out = vieillir(base, seed).convert("RGBA")
    # l'alpha vient de la decoupe de la carte, pas de la composition
    masque = Image.new("L", (W, H), 0)
    ImageDraw.Draw(masque).rounded_rectangle([0, 0, W - 1, H - 1], RADIUS, fill=255)
    out.putalpha(masque)
    return out


def key(chiffre, couleur, forme):
    return f"{chiffre}-{couleur}-{forme}"


if __name__ == "__main__":
    todo = sys.argv[1:] or ["all"]
    combos = [(c, col, f, fr) for c in CHIFFRES for col, fr in COULEURS for f in FORMES]
    if todo != ["all"]:
        combos = [x for x in combos if key(x[0], x[1], x[2]) in todo]
    for c, col, f, fr in combos:
        img = make_card(c, col, f, fr)
        p = os.path.join(OUT, f"carte-{key(c, col, f)}.png")
        img.save(p)
        print(p)
