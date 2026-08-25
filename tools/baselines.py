#!/usr/bin/env python3
"""Measurement of the BASELINES, and of the white space between paragraphs.

The top of a line (y0) depends on whether that line has ascenders: it
varies by several pixels from one line to the next without the composition
changing. That is too noisy to decide whether the facsimile leaves white
space between its paragraphs.

The baseline, on the other hand, is stable: it is the ordinate on which
the letters without descenders sit, that is the MODE of the glyph bottoms
within the line's band. The descenders (g, j, p, q, y) form a second
group, lower and far less numerous.
"""
import os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG


def bases(gm2, lines):
    """Ordinate of the baseline of each line of text."""
    out = []
    for l in lines:
        sub = (gm2[l['y0']:l['y1'] + 1] > 0).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(sub, 8)
        bottom = [st[i][1] + st[i][3] for i in range(1, n) if st[i][4] >= 12]
        if len(bottom) < 4:
            out.append(None)
            continue
        h = np.bincount(np.array(bottom), minlength=sub.shape[0] + 2)
        # the mode, refined by centroid over +/- 2 px
        pk = int(np.argmax(h))
        lo, hi = max(0, pk - 2), min(len(h), pk + 3)
        w = h[lo:hi].astype(float)
        xs = np.arange(lo, hi)
        out.append(l['y0'] + float((xs * w).sum() / max(w.sum(), 1)))
    return out


def analysis(leaf, verbose=True):
    norm, gm, ang = PG.prepared_img(leaf)
    gm2, span = PG.text_region(gm)
    fl = PG.lines_of(gm2)
    # Fallback mask: gm bounded to the text column. text_region sometimes
    # erases the folio (leaf 42).
    _sec = gm.copy()
    if span:
        _sec[:, :max(0, span[0] - 12)] = 0
        _sec[:, min(_sec.shape[1], span[1] + 13):] = 0
    f0 = PG.folio_line(gm2, fl, _sec)
    if f0:
        fl.insert(0, f0)
    bs = bases(gm2, fl)
    pitch = []
    for k in range(1, len(bs)):
        if bs[k] is None or bs[k - 1] is None:
            continue
        pitch.append((k, bs[k] - bs[k - 1], fl[k - 1]['x1'] - fl[k - 1]['x0']))
    if verbose:
        print('leaf %d: %d lines' % (leaf, len(fl)))
    return fl, bs, pitch


if __name__ == '__main__':
    full_ref = {}
    short, long = [], []
    for f in [int(x) for x in sys.argv[1:]] or [16, 17, 18, 19]:
        fl, bs, pitch = analysis(f)
        full = max(l['x1'] - l['x0'] for l in fl)
        for k, p, larg in pitch:
            if not (25 < p < 75):
                continue
            # was the PRECEDING line full (mid-paragraph) or short (end of
            # paragraph)? The pitch following an end of paragraph carries the
            # inter-paragraph white space, if there is any.
            (long if larg > 0.94 * full else short).append(p)
    def stat(v, name):
        if not v:
            print('%-28s no sample' % name); return None
        a = np.array(v)
        print('%-28s n=%3d  mediane %.2f px = %.2f pt' % (
            name, len(a), np.median(a), np.median(a) * PG.PX2PT))
        return float(np.median(a))
    print()
    m1 = stat(long, 'pitch mid-paragraph')
    m2 = stat(short, 'pitch after an end of paragraph')
    if m1 and m2:
        print('\ninter-paragraph white space = %.2f px = %.2f pt (%.2f mm)' % (
            m2 - m1, (m2 - m1) * PG.PX2PT, (m2 - m1) * PG.PX2MM))
