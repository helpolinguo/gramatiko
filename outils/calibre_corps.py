#!/usr/bin/env python3
"""Calibration du CORPS : hauteur d'x et hauteur de capitale mesurees
sur le fac-simile, en millimetres.

Methode : dans chaque ligne de texte, on prend les composantes connexes
(les glyphes). La hauteur d'x est le mode des hauteurs des glyphes SANS
hampe ni jambage (a, c, e, m, n, o, r, s, u, v, w, x, z), qui forment de
loin la population la plus nombreuse ; on la lit donc comme le pic
inferieur de l'histogramme des hauteurs.
"""
import os, sys, json
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX2MM = PG.PX2MM
PX2PT = PG.PX2PT


def glyph_heights(n, ymin_frac=0.10, ymax_frac=0.80):
    """Hauteurs des glyphes du texte courant (on ecarte folio et notes)."""
    norm, gm, ang = PG.prepared(n)
    gm2, span = PG.text_region(gm)
    H, W = gm2.shape
    sub = gm2[int(ymin_frac * H):int(ymax_frac * H), :]
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats((sub > 0).astype(np.uint8), 8)
    hs, tops, bots = [], [], []
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        if a < 25 or h < 6 or h > 60 or w < 4 or w > 60:
            continue
        hs.append(h); tops.append(y); bots.append(y + h)
    return np.array(hs), (norm, gm2, span, ang)


def xheight(n):
    hs, _ = glyph_heights(n)
    if len(hs) < 100:
        return None
    # histogramme des hauteurs : le pic le plus bas et le plus peuple = hauteur d'x
    cnt = np.bincount(hs, minlength=61)
    lo = 8
    peak = lo + int(np.argmax(cnt[lo:40]))
    # affinage : moyenne ponderee autour du pic
    sl = slice(peak - 2, peak + 3)
    w = cnt[sl].astype(float)
    xs = np.arange(peak - 2, peak + 3)
    xh = float((xs * w).sum() / w.sum())
    # hauteur de capitale : pic secondaire au-dessus de 1.25*xh
    hi = cnt[int(1.25 * xh):int(2.1 * xh)]
    cap = int(1.25 * xh) + int(np.argmax(hi)) if len(hi) else None
    return {'leaf': n, 'x_px': round(xh, 2), 'x_mm': round(xh * PX2MM, 3),
            'x_pt': round(xh * PX2PT, 3),
            'cap_px': cap, 'cap_mm': round(cap * PX2MM, 3) if cap else None,
            'cap_pt': round(cap * PX2PT, 3) if cap else None,
            'n_glyphes': int(len(hs))}


if __name__ == '__main__':
    res = []
    for a in sys.argv[1:]:
        r = xheight(int(a))
        if r:
            res.append(r)
            print(json.dumps(r), flush=True)
    if res:
        print('--- medianes ---')
        print('hauteur d x  : %.3f mm  (%.2f pt TeX)' % (
            np.median([r['x_mm'] for r in res]), np.median([r['x_pt'] for r in res])))
        caps = [r['cap_mm'] for r in res if r['cap_mm']]
        if caps:
            print('hauteur de cap: %.3f mm (%.2f pt TeX)' % (
                np.median(caps), np.median([r['cap_pt'] for r in res if r['cap_pt']])))
