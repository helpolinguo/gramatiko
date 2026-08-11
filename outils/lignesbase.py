#!/usr/bin/env python3
"""Mesure des LIGNES DE BASE, et du blanc entre alineas.

Le haut d'une ligne (y0) depend de la presence d'ascendantes dans cette
ligne : il varie de plusieurs pixels d'une ligne a l'autre sans que la
composition change. C'est trop bruite pour decider si le fac-simile
laisse ou non un blanc entre ses alineas.

La ligne de base, elle, est stable : c'est l'ordonnee ou se posent les
lettres sans jambage, c'est-a-dire le MODE des bas de glyphe dans la
bande de la ligne. Les jambages (g, j, p, q, y) forment un second groupe,
plus bas et bien moins nombreux.
"""
import os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG


def bases(gm2, lignes):
    """Ordonnee de la ligne de base de chaque ligne de texte."""
    out = []
    for l in lignes:
        sub = (gm2[l['y0']:l['y1'] + 1] > 0).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(sub, 8)
        bas = [st[i][1] + st[i][3] for i in range(1, n) if st[i][4] >= 12]
        if len(bas) < 4:
            out.append(None)
            continue
        h = np.bincount(np.array(bas), minlength=sub.shape[0] + 2)
        # le mode, affine par barycentre sur +/- 2 px
        pk = int(np.argmax(h))
        lo, hi = max(0, pk - 2), min(len(h), pk + 3)
        w = h[lo:hi].astype(float)
        xs = np.arange(lo, hi)
        out.append(l['y0'] + float((xs * w).sum() / max(w.sum(), 1)))
    return out


def analyse(feuillet, verbose=True):
    norm, gm, ang = PG.prepared(feuillet)
    gm2, span = PG.text_region(gm)
    fl = PG.lines_of(gm2)
    # Masque de secours : gm borne a la colonne de texte. text_region
    # efface parfois le folio (feuillet 42).
    _sec = gm.copy()
    if span:
        _sec[:, :max(0, span[0] - 12)] = 0
        _sec[:, min(_sec.shape[1], span[1] + 13):] = 0
    f0 = PG.folio_ligne(gm2, fl, _sec)
    if f0:
        fl.insert(0, f0)
    bs = bases(gm2, fl)
    pas = []
    for k in range(1, len(bs)):
        if bs[k] is None or bs[k - 1] is None:
            continue
        pas.append((k, bs[k] - bs[k - 1], fl[k - 1]['x1'] - fl[k - 1]['x0']))
    if verbose:
        print('feuillet %d : %d lignes' % (feuillet, len(fl)))
    return fl, bs, pas


if __name__ == '__main__':
    plein_ref = {}
    court, longue = [], []
    for f in [int(x) for x in sys.argv[1:]] or [16, 17, 18, 19]:
        fl, bs, pas = analyse(f)
        plein = max(l['x1'] - l['x0'] for l in fl)
        for k, p, larg in pas:
            if not (25 < p < 75):
                continue
            # la ligne PRECEDENTE etait-elle pleine (milieu d'alinea) ou
            # courte (fin d'alinea) ? Le pas qui suit une fin d'alinea
            # porte le blanc inter-alinea, s'il existe.
            (longue if larg > 0.94 * plein else court).append(p)
    def stat(v, nom):
        if not v:
            print('%-28s aucun echantillon' % nom); return None
        a = np.array(v)
        print('%-28s n=%3d  mediane %.2f px = %.2f pt' % (
            nom, len(a), np.median(a), np.median(a) * PG.PX2PT))
        return float(np.median(a))
    print()
    m1 = stat(longue, 'pas en milieu d alinea')
    m2 = stat(court, 'pas apres une fin d alinea')
    if m1 and m2:
        print('\nblanc inter-alinea = %.2f px = %.2f pt (%.2f mm)' % (
            m2 - m1, (m2 - m1) * PG.PX2PT, (m2 - m1) * PG.PX2MM))
