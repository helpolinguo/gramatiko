#!/usr/bin/env python3
"""Juge de GRAISSE : epaisseur des futs, mot par mot.

Trois fois de suite je me suis trompe sur la graisse d'une ligne, dans
un sens puis dans l'autre. L'oeil ne suffit pas a taille reelle, et
l'agrandissement lui-meme laisse des doutes quand le papier a bu l'encre.
La densite d'encre (encre / largeur) ne suffit pas non plus : elle depend
de la forme des lettres, et au folio 51 elle donnait 7,3 a 8,9 pour des
mots dont les uns sont gras et les autres romains.

Ce qui tranche est l'EPAISSEUR DU FUT : la longueur mediane des
sequences horizontales de pixels encres. Etalonnage sur le tableau du
folio 31, ou la graisse est certaine :

    « tam » (gras)      5,0 px        « egaleso » (romain)  3,0 px
    « kam » (gras)      4,0 px

et au folio 51 :

    « frapar, donar, lektar » (gras)   4,0 px
    « quale en la transitivi » (rom.)  3,0 px

Le seuil est donc a 3,5 px. Le demi-gras de ce volume est etroit : il ne
se distingue pas par la chasse, mais bien par le fut.

LIMITE, constatee des le premier emploi : la mesure ne vaut que la ou le
papier est PLAT. Au feuillet 55 un pli traverse la page ; sur la ligne
qui le franchit, l'outil declare gras jusqu'aux mots dont on sait qu'ils
sont romains (« verbo », « subjekto »), l'ombre du pli epaississant tout.
Sur la ligne suivante, hors du pli, il separe nettement « frapar, donar,
lektar » a 4,0 px de « quale en la transitivi » a 3,0. Avant de conclure,
verifier donc que la bande mesuree ne traverse ni pli ni ombre de
reliure — un verdict uniforme sur toute une ligne est le signe qu'elle
en traverse un.

    python3 outils/graisse.py 55 1576 1610
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

SEUIL = 3.5


def futs(gm2, a, b, u, v):
    sub = (gm2[a:b, u:v] > 0)
    runs = []
    for row in sub:
        c = 0
        for p in row:
            if p:
                c += 1
            elif c:
                runs.append(c); c = 0
        if c:
            runs.append(c)
    runs = [r for r in runs if r <= 14]      # au-dela, c'est un filet
    return float(np.median(runs)) if runs else 0.0


def ligne(feuillet, y0, y1, gap=14):
    """Rend [(x0, x1, fut, verdict)] pour chaque amas de la bande."""
    norm, gm, ang = PG.prepared(feuillet)
    gm2, span = PG.text_region(gm)
    x0 = span[0]
    band = (gm2[y0:y1] > 0)
    col = band.sum(axis=0)
    xs = np.nonzero(col)[0]
    if not len(xs):
        return []
    amas = []
    s = p = xs[0]
    for x in xs[1:]:
        if x - p > gap:
            amas.append((s, p)); s = x
        p = x
    amas.append((s, p))
    out = []
    for u, v in amas:
        f = futs(gm2, y0, y1, u, v + 1)
        out.append((u - x0, v - x0, f, 'GRAS' if f >= SEUIL else 'romain'))
    return out


if __name__ == '__main__':
    n, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    for u, v, f, q in ligne(n, a, b):
        print('  %4d-%4d  fut %.1f px  %s' % (u, v, f, q))
