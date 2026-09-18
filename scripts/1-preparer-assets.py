from PIL import Image, ImageFilter
import os
SRC="/Users/maximetatopoulos/App Max/Niko"
OUT=os.path.join(SRC,"assets")
os.makedirs(OUT,exist_ok=True)

def crop(im):
    return im.crop(im.getbbox())

# 1. Kanji couleurs : JPG blanc -> alpha (noir conserve)
kanji={"rouge":"IMG_8559.jpg","bleu":"IMG_8560.jpg","jaune":"IMG_8561.jpg","vert":"IMG_8562.jpg"}
for name,f in kanji.items():
    im=Image.open(os.path.join(SRC,f)).convert("L")
    # alpha = inverse de la luminance, contraste renforce
    a=im.point(lambda v: 0 if v>225 else (255 if v<110 else int((225-v)/115*255)))
    rgba=Image.new("RGBA",im.size,(17,17,17,255)); rgba.putalpha(a)
    crop(rgba).save(os.path.join(OUT,f"kanji-couleur-{name}.png"))

# 2. Cercle bleu manquant. Le dossier fournit les cercles rouge, vert et jaune
#    mais pas le bleu, on le reconstitue depuis le rouge. La teinte est prise sur
#    les trois formes bleues existantes, et la luminosite est recalee sur leur
#    moyenne mesuree : une simple recolorisation donnait un cercle nettement plus
#    sombre que le triangle, le carre et la croix.
import numpy as np

REFS = ["211A77A0-1FFD-4B86-BFAA-4AF0CAF8D1F5.PNG",   # carre bleu
        "870F0A31-C4FF-4EFD-B4FE-A2310FFA9634.PNG",   # triangle bleu
        "0B26DA45-1CA0-4778-A702-A5FF7F4BC5C9.PNG"]   # croix bleue


def moyenne_encre(chemin):
    a = np.asarray(Image.open(chemin).convert("RGBA")).astype(np.float32)
    return a[..., :3][a[..., 3] > 200].mean(0)


cible = np.mean([moyenne_encre(os.path.join(SRC, f)) for f in REFS], axis=0)
print("bleu de reference des trois autres formes:", cible.round(1))

rouge = Image.open(os.path.join(SRC, "21AFF584-B733-4A65-B1A4-DC1D6E9F94ED.PNG")).convert("RGBA")
a = np.asarray(rouge).astype(np.float32)
rgb, alpha = a[..., :3], a[..., 3]
opaque = alpha > 200

# la luminosite relative du pixel rouge pilote l'intensite du bleu
lum = (rgb @ np.array([0.35, 0.45, 0.20], dtype=np.float32)) / 255.0
k = 0.55 + 0.9 * lum
out = np.stack([cible[i] * k for i in range(3)], axis=-1)

# recalage par canal sur la moyenne des trois autres formes
for i in range(3):
    m = out[..., i][opaque].mean()
    if m > 1:
        out[..., i] *= cible[i] / m
out = np.clip(out, 0, 255)
res = np.dstack([out, alpha]).astype(np.uint8)
cercle = Image.fromarray(res)
print("cercle bleu obtenu:", np.asarray(cercle).astype(np.float32)[..., :3][opaque].mean(0).round(1))
crop(cercle).save(os.path.join(OUT, "forme-cercle-bleu.png"))

# 3. Copies recadrees et nommees de tous les autres assets
mapping={
 "forme-cercle-rouge":"21AFF584-B733-4A65-B1A4-DC1D6E9F94ED.PNG",
 "forme-cercle-vert":"6741DA08-9D42-4D06-9F5C-419C50696544.PNG",
 "forme-cercle-jaune":"7BFF1178-57D3-4EDA-A9B6-538A6A64A19A.PNG",
 "forme-triangle-rouge":"C2690259-DB16-4AF5-8FD2-FE4DE9EBBB62.PNG",
 "forme-triangle-bleu":"870F0A31-C4FF-4EFD-B4FE-A2310FFA9634.PNG",
 "forme-triangle-jaune":"49D5FAF8-B95C-4329-AD55-AF6213A4BC78.PNG",
 "forme-triangle-vert":"3685C84D-86B4-4A81-9B83-83A0D2536D73.PNG",
 "forme-carre-rouge":"D9E28C57-7DE9-4684-8930-6ECA83ED1A9E.PNG",
 "forme-carre-bleu":"211A77A0-1FFD-4B86-BFAA-4AF0CAF8D1F5.PNG",
 "forme-carre-jaune":"9F6EB97D-E4A8-4033-A282-8872F501B71B.PNG",
 "forme-carre-vert":"8EA35E64-36F2-40DE-BA58-FA25B67670AE.PNG",
 "forme-croix-rouge":"8FFB6C1C-3F44-4145-84A0-ED307D38D40F.PNG",
 "forme-croix-bleu":"0B26DA45-1CA0-4778-A702-A5FF7F4BC5C9.PNG",
 "forme-croix-jaune":"C26D327C-8C17-4A97-87B9-24B0A39DB1CC.PNG",
 "forme-croix-vert":"C30C0114-2855-4A80-85E1-BBBC374A10BA.PNG",
 "chiffre-1":"49B292B0-020C-4736-ADD6-4C8FEE1C7468.PNG",
 "chiffre-2":"C981C8C0-CBC8-4E1F-8367-F9EB425F296D.PNG",
 "chiffre-3":"E37FFDD9-9137-4EE1-B268-ADA875C8C49E.PNG",
 "chiffre-4":"0FF86A6E-5350-403D-9C0D-A3A197C3A262.PNG",
 "cartouche-1":"22716A6B-E481-45C1-AAE6-CB88AB3C6272.PNG",
 "cartouche-2":"7C03BCF5-2A55-4FAF-8548-97369DE686F5.PNG",
 "cartouche-3":"DDAAE8FC-50EA-442A-9992-C81861B1DDA7.PNG",
 "cartouche-4":"F1C39CA5-B0C4-4E71-8462-4839BF330453.PNG",
 "paysage-rouge":"D7E6C662-0499-449C-A533-F6E89C191708.PNG",
 "paysage-bleu":"3E991EEA-61CD-45D1-8905-1E6FB2FD617A.PNG",
 "paysage-vert":"54100D32-B34D-4977-9B02-283674EC9FD6.PNG",
 "paysage-jaune":"7C18521A-F77A-4F0F-A82D-035C307A7639.PNG",
}
def source(f):
    """Les premieres images sont a la racine de Niko, les suivantes ont ete
    deposees dans assets. On regarde les deux."""
    a = os.path.join(SRC, f)
    return a if os.path.exists(a) else os.path.join(OUT, f)


for name,f in mapping.items():
    crop(Image.open(source(f)).convert("RGBA")).save(os.path.join(OUT,name+".png"))

# 3b. Le paysage rouge peint sa neige et sa brume en blanc opaque : 3,8 pour cent
#     de ses pixels, contre zero pour les trois autres. Pose sur le papier creme,
#     ce blanc se voit comme une tache. On inverse donc sa composition sur blanc :
#     l'opacite devient la densite d'encre, et la couleur est desaturee du blanc
#     qu'elle contenait. Le papier se voit alors a travers tout le lavis.
import numpy as _np


def blanc_vers_transparence(im):
    a = _np.asarray(im.convert("RGBA")).astype(_np.float32)
    rgb, alpha = a[..., :3], a[..., 3]
    densite = 255.0 - rgb.min(axis=2)          # 0 sur le blanc, 255 sur le noir
    d = _np.maximum(densite, 1.0)[..., None]
    couleur = _np.clip((rgb - (255.0 - densite)[..., None]) / d * 255.0, 0, 255)
    return Image.fromarray(
        _np.dstack([couleur, alpha * densite / 255.0]).astype(_np.uint8))


_rouge = os.path.join(OUT, "paysage-rouge.png")
blanc_vers_transparence(Image.open(_rouge)).save(_rouge)
print("paysage rouge detoure du blanc peint")
# 4. Reteinte de la vague : le bleu d'origine est trop vif et trop clair face au
#    bleu de la forme et aux trois autres paysages, qui sont des lavis d'encre.
#    On uniformise sa teinte sur le bleu de la forme, on assombrit les mediums et
#    on laisse les hautes lumieres partir vers le gris.
import numpy as np, colorsys

NAVY = (0, 43, 99)
H_T = colorsys.rgb_to_hsv(*[c / 255 for c in NAVY])[0]


def retint(im, sat=0.60, grey=0.45, gamma=1.45, vmax=0.88):
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    v2 = np.power(v, gamma) * vmax
    s2 = s * sat * (1.0 - grey * v)
    h6 = H_T * 6
    i6 = int(h6) % 6
    f = h6 - int(h6)
    p_, q_, t_ = v2 * (1 - s2), v2 * (1 - s2 * f), v2 * (1 - s2 * (1 - f))
    chan = [(v2, t_, p_), (q_, v2, p_), (p_, v2, t_),
            (p_, q_, v2), (t_, p_, v2), (v2, p_, q_)][i6]
    out = np.dstack(list(chan) + [alpha]) * 255
    return Image.fromarray(out.astype(np.uint8))


brut = Image.open(os.path.join(OUT, "paysage-bleu.png")).convert("RGBA")
brut.save(os.path.join(OUT, "paysage-bleu-brut.png"))
retint(brut).save(os.path.join(OUT, "paysage-bleu.png"))
print("vague reteintee")

# 5. Mesure du motif principal de chaque forme. Les 16 fichiers sources n'ont ni
#    le meme cadrage ni la meme marge d'eclaboussures : le carre vert fait 926 px
#    de large quand le jaune en fait 1053. On releve donc, pour chaque forme, la
#    boite du trait lui-meme, eclaboussures exclues, et la generation s'en sert
#    pour donner a toutes exactement la meme empreinte.
import json
from scipy import ndimage


def core_bbox(im, dilate=9):
    a = np.asarray(im.convert("RGBA"))[..., 3] > 40
    big = ndimage.binary_dilation(a, np.ones((dilate, dilate), bool))
    lab, n = ndimage.label(big)
    sizes = ndimage.sum(big, lab, range(1, n + 1))
    m = (lab == int(np.argmax(sizes)) + 1) & a
    ys, xs = np.where(m)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


cadres = {}
for f in ["cercle", "triangle", "carre", "croix"]:
    for c in ["rouge", "bleu", "jaune", "vert"]:
        k = f"forme-{f}-{c}"
        cadres[k] = core_bbox(Image.open(os.path.join(OUT, k + ".png")))
with open(os.path.join(OUT, "formes-cadres.json"), "w") as fh:
    json.dump(cadres, fh, indent=1, sort_keys=True)
print("cadres mesures:", len(cadres))

# 6. Elements des jokers. Ces six fichiers arrivent sur fond blanc opaque : on
#    inverse la composition sur blanc pour retrouver la couleur et l'alpha.
JOKER_SRC = {
    "joker-cartouche": "166D2716-0B63-4B7B-BB73-D98DA9D506E0.PNG",   # rectangle ジョーカー
    "joker-mot":       "6E827567-2F00-4B0A-9999-3C79797CDD0C.jpg",   # lettrage JOKER
    "tache-jaune":     "2378F37D-7A4C-498F-A36F-5B3F1B01A561.PNG",
    "tache-vert":      "DC797CEA-718A-4E7C-9AAD-711AA84F09E5.PNG",
    "tache-bleu":      "376794D3-1CE7-48B0-9D18-648FDE0A457F.PNG",
    "tache-rouge":     "CD1E8E63-0055-48F6-8FE2-D085A213A432.PNG",
    "logo-kasane":     "4A5D3453-CE8C-4221-AE58-938695FA3E2C.PNG",   # lettrage du titre
}

# La tache de fond arrive deja detouree, avec son canal alpha : elle est juste
# recopiee sous un nom lisible pour que le generateur la trouve.
FOND_SRC = "4D9EB9A3-7711-461B-9FC7-CDC3A15FED64.PNG"


def detourer_blanc(im, seuil=248):
    """Retire un fond blanc : alpha = 255 - min(R,V,B), puis on annule la
    premultiplication par le blanc pour retrouver la teinte d'origine."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    alpha = 255.0 - a.min(axis=2)
    alpha[a.min(axis=2) >= seuil] = 0.0
    k = np.maximum(alpha, 1.0) / 255.0
    coul = np.clip((a - (255.0 - alpha)[..., None]) / k[..., None], 0, 255)
    out = np.dstack([coul, alpha]).astype(np.uint8)
    return Image.fromarray(out)


for nom, f in JOKER_SRC.items():
    chemin = os.path.join(SRC, f)
    if not os.path.exists(chemin):                     # les fichiers ont ete
        chemin = os.path.join(OUT, f)                  # deposes dans assets
    crop(detourer_blanc(Image.open(chemin))).save(os.path.join(OUT, nom + ".png"))

# Formes en noir, pour les jokers de forme : on garde le trace et on remplace la
# couleur par l'encre, en conservant les nuances de pression du pinceau.
for f in ["cercle", "triangle", "carre", "croix"]:
    src = Image.open(os.path.join(OUT, f"forme-{f}-rouge.png")).convert("RGBA")
    a = np.asarray(src).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3]
    lum = rgb.max(axis=2) / 255.0                      # 1 = pleine couleur
    val = 18 + 52 * (1.0 - lum)                        # encre plus ou moins dense
    noir = np.dstack([val, val, val, alpha]).astype(np.uint8)
    Image.fromarray(noir).save(os.path.join(OUT, f"forme-{f}-noir.png"))

cadres.update({f"forme-{f}-noir": cadres[f"forme-{f}-rouge"]
               for f in ["cercle", "triangle", "carre", "croix"]})
with open(os.path.join(OUT, "formes-cadres.json"), "w") as fh:
    json.dump(cadres, fh, indent=1, sort_keys=True)
print("elements joker ecrits")

# 7. Taches des jokers de couleur. Livrees plus claires et plus saturees que les
#    formes du meme nom, de 11 a 14 points de luminance pour le bleu, le jaune et
#    le vert. On recale chaque canal sur la moyenne d'encre des quatre formes de
#    cette couleur, en laissant de cote les canaux quasi nuls ou un gain n'a pas
#    de sens.
def moyenne_opaque(chemin):
    a = np.asarray(Image.open(chemin).convert("RGBA")).astype(np.float32)
    return a[..., :3][a[..., 3] > 200].mean(0)


for c in ["rouge", "bleu", "jaune", "vert"]:
    cible = np.mean([moyenne_opaque(os.path.join(OUT, f"forme-{s}-{c}.png"))
                     for s in ["cercle", "triangle", "carre", "croix"]], axis=0)
    chemin = os.path.join(OUT, f"tache-{c}.png")
    a = np.asarray(Image.open(chemin).convert("RGBA")).astype(np.float32)
    rgb, alpha = a[..., :3].copy(), a[..., 3]
    op = alpha > 200
    for i in range(3):
        m = rgb[..., i][op].mean()
        if m < 4 or cible[i] < 4:            # canal negligeable, on n'y touche pas
            continue
        rgb[..., i] *= min(2.5, max(0.4, cible[i] / m))
    tache = np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)
    Image.fromarray(tache).save(chemin)
    obtenu = np.asarray(tache).astype(np.float32)[..., :3][op].mean(0)
    print(f"  tache {c:6} cible {cible.round(0).astype(int)} obtenu {obtenu.round(0).astype(int)}")
print("taches recalees sur les formes")

# 8. Ligne de base des paysages. Chaque fichier se termine par une traine de
#    lavis presque transparente, plus ou moins longue : 21 px sous les montagnes
#    rouges contre 3 px sous la vague. Comme la pose se fait sur le bas du
#    fichier, le rouge se retrouvait pose 13 px plus haut que les autres. On
#    coupe donc cette traine pour que le bas du fichier soit le bas du dessin.
for c in ["rouge", "bleu", "jaune", "vert"]:
    chemin = os.path.join(OUT, f"paysage-{c}.png")
    im = Image.open(chemin).convert("RGBA")
    prof = np.asarray(im)[..., 3].astype(np.float32).sum(axis=1)
    dense = np.where(prof > 0.015 * prof.max())[0]
    bas = int(dense.max()) + 1
    if bas < im.height:
        im.crop((0, 0, im.width, bas)).save(chemin)
    print(f"  paysage {c:6} traine coupee : {im.height - bas:3d} px, "
          f"hauteur {im.height} -> {bas}")
print("lignes de base alignees")

print("assets ecrits:",len(os.listdir(OUT)))


# --- tache de fond ---------------------------------------------------------
_fond = Image.open(os.path.join(ASSETS, FOND_SRC)).convert("RGBA")
_fond.save(os.path.join(ASSETS, "tache-fond.png"))
print("tache-fond.png", _fond.size)
