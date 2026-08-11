#!/usr/bin/env python3
"""Appariement des lignes du fac-simile et des lignes composees.

Les controles 9 et 10 comparaient les deux pages RANG PAR RANG, apres
avoir verifie que le nombre de lignes coincidait — et sautaient la page
sinon. C'etait leur defaut le plus grave : la detection de lignes se
trompe d'une unite assez souvent (un folio pale, une ligne courte, un
eclat d'encre), et la page etait alors declaree non comparable. Les
controles rendaient donc un verdict vert sur les pages meme qu'il aurait
fallu examiner : eprouve en reintroduisant une faute connue, le controle
des fins d'alinea ne l'a pas vue, faute d'avoir compare la page.

On apparie donc les lignes par leur POSITION VERTICALE. Le fac-simile et
le compose ayant, par construction, la meme mise en page, une ligne du
premier tombe a la meme hauteur que la ligne correspondante du second, a
l'offset de numerisation pres — le papier n'occupe pas la meme place dans
toutes les images du scan.

Deux etapes :
  1. estimer l'offset vertical global entre les deux suites ;
  2. apparier par programmation dynamique, ce qui autorise une ligne
     surnumeraire de part et d'autre sans faire derailler tout le reste.

La fonction rend la liste des couples (indice fac-simile, indice compose)
et les indices restes seuls, que l'appelant peut signaler.
"""

# ECART_MAX doit rester nettement INFERIEUR a l'interligne (41 px) : a
# 40 px, une ligne pouvait s'apparier a sa voisine aussi bien qu'a
# elle-meme, et l'appariement glissait d'un rang sur toute une page sans
# que le cout total en souffre. A 16 px, un tel glissement est interdit.
ECART_MAX = 16.0
# Le trou doit couter plus cher que le pire appariement licite, sinon
# l'algorithme prefere sauter des lignes plutot que de les apparier.
TROU = 22.0


def _centres(lignes):
    return [(a + b) / 2.0 for a, b in lignes]


def estime_transfo(cf, cc):
    """Transformation affine y_compose = a * y_fac + b qui superpose au
    mieux les deux suites.

    Un simple decalage ne suffit pas : la numerisation n'a pas la meme
    echelle d'une page a l'autre (la largeur des images de double page va
    de 2680 a 2818 px, soit 5 %). Sur une page de quarante lignes, une
    erreur d'echelle de 2 % fait deriver de plus de trente pixels entre le
    haut et le bas — assez pour apparier chaque ligne avec sa voisine, ce
    qui produit une alternance caracteristique de faux positifs.

    On ajuste donc echelle et decalage par moindres carres sur les couples
    au plus proche voisin, iteres (algorithme du point le plus proche).
    """
    if len(cf) < 2 or len(cc) < 2:
        return 1.0, (sum(cc) / len(cc)) - (sum(cf) / len(cf)) if cf and cc else 0.0
    a = (max(cc) - min(cc)) / max(max(cf) - min(cf), 1e-6)
    b = min(cc) - a * min(cf)
    for _ in range(8):
        xs, ys = [], []
        for y in cf:
            p = a * y + b
            d = min(cc, key=lambda z: abs(z - p))
            if abs(d - p) < 3 * TROU:
                xs.append(y); ys.append(d)
        if len(xs) < 3:
            break
        n = len(xs)
        mx = sum(xs) / n; my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        if den <= 0:
            break
        na = num / den
        if not (0.9 < na < 1.1):        # garde-fou : l'echelle reste proche de 1
            na = 1.0
        nb = my - na * mx
        if abs(na - a) < 1e-6 and abs(nb - b) < 1e-3:
            a, b = na, nb
            break
        a, b = na, nb
    return a, b


def apparie(lignes_fac, lignes_comp):
    """lignes_* : suites de couples (y0, y1). Retourne (couples, seuls_fac,
    seuls_comp)."""
    cf = _centres(lignes_fac)
    cc = _centres(lignes_comp)
    if not cf or not cc:
        return [], list(range(len(cf))), list(range(len(cc)))
    a, b = estime_transfo(cf, cc)
    n, m = len(cf), len(cc)
    # programmation dynamique : appariement monotone avec trous
    INF = float('inf')
    d = [[INF] * (m + 1) for _ in range(n + 1)]
    ch = [[None] * (m + 1) for _ in range(n + 1)]
    d[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            if d[i][j] == INF:
                continue
            if i < n and j < m:
                e = abs((a * cf[i] + b) - cc[j])
                if e <= ECART_MAX:
                    v = d[i][j] + e
                    if v < d[i + 1][j + 1]:
                        d[i + 1][j + 1] = v
                        ch[i + 1][j + 1] = ('=', i, j)
            if i < n:
                v = d[i][j] + TROU
                if v < d[i + 1][j]:
                    d[i + 1][j] = v
                    ch[i + 1][j] = ('f', i, j)
            if j < m:
                v = d[i][j] + TROU
                if v < d[i][j + 1]:
                    d[i][j + 1] = v
                    ch[i][j + 1] = ('c', i, j)
    couples, sf, sc = [], [], []
    i, j = n, m
    while i or j:
        mv = ch[i][j]
        if mv is None:
            break
        k, pi, pj = mv
        if k == '=':
            couples.append((pi, pj))
        elif k == 'f':
            sf.append(pi)
        else:
            sc.append(pj)
        i, j = pi, pj
    couples.reverse(); sf.reverse(); sc.reverse()
    return couples, sf, sc


if __name__ == '__main__':
    a = [(100, 130), (140, 170), (180, 210), (260, 290)]
    b = [(105, 135), (145, 175), (185, 215), (222, 228), (265, 295)]
    c, sf, sc = apparie(a, b)
    print('couples :', c)
    print('seuls fac-simile :', sf, ' seuls compose :', sc)
