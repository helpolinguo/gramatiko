#!/usr/bin/env python3
"""Calibration of the TYPE SIZE: x-height and cap height measured on the
facsimile, in millimetres.

Method: in each line of text we take the connected components (the
glyphs). The x-height is the mode of the heights of the glyphs WITHOUT
ascender or descender (a, c, e, m, n, o, r, s, u, v, w, x, z), which are
by far the most numerous population; we therefore read it as the lower
peak of the histogram of heights.
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
    """Heights of the running text's glyphs (folio and notes discarded)."""
    norm, gm, ang = PG.prepared_img(n)
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


def x_height_val(n):
    hs, _ = glyph_heights(n)
    if len(hs) < 100:
        return None
    # histogram of heights: the lowest and most populous peak = x-height
    cnt = np.bincount(hs, minlength=61)
    lo = 8
    peak = lo + int(np.argmax(cnt[lo:40]))
    # refinement: weighted mean around the peak
    sl = slice(peak - 2, peak + 3)
    w = cnt[sl].astype(float)
    xs = np.arange(peak - 2, peak + 3)
    x_height = float((xs * w).sum() / w.sum())
    # cap height: secondary peak above 1.25*xh
    hi = cnt[int(1.25 * x_height):int(2.1 * x_height)]
    cap = int(1.25 * x_height) + int(np.argmax(hi)) if len(hi) else None
    return {'leaf': n, 'x_px': round(x_height, 2), 'x_mm': round(x_height * PX2MM, 3),
            'x_pt': round(x_height * PX2PT, 3),
            'cap_px': cap, 'cap_mm': round(cap * PX2MM, 3) if cap else None,
            'cap_pt': round(cap * PX2PT, 3) if cap else None,
            'n_glyphes': int(len(hs))}


if __name__ == '__main__':
    res = []
    for a in sys.argv[1:]:
        r = x_height_val(int(a))
        if r:
            res.append(r)
            print(json.dumps(r), flush=True)
    if res:
        print('--- medianes ---')
        print('x-height     : %.3f mm  (%.2f pt TeX)' % (
            np.median([r['x_mm'] for r in res]), np.median([r['x_pt'] for r in res])))
        caps = [r['cap_mm'] for r in res if r['cap_mm']]
        if caps:
            print('cap height   : %.3f mm (%.2f pt TeX)' % (
                np.median(caps), np.median([r['cap_pt'] for r in res if r['cap_pt']])))
