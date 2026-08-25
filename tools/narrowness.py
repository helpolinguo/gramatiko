#!/usr/bin/env python3
"""NARROWNESS OF THE TITLES: is the composed face too wide?

The volume sets the type size from the cap height and the letter-spacing
from the line width. That rule always gives the right overall geometry --
but it is SILENT on the drawing of the letters. When the facsimile's face
is narrower than XCharter, the letter-spacing has to go negative for the
line to fit, and the letters weld together: the line has the right width
and becomes illegible.

That was the case of "KONSTATO." (folio 4), composed as a SINGLE cluster
of 174 px for 216 px and seven clusters in the facsimile, and of "Averto"
(folio 5). Neither would have been caught by a check on width: their
width was "right".

We therefore measure, on both sides, the LETTER WIDTH relative to the cap
height, and the number of clusters -- two letters that touch make only
one. The factor to pass to \\VUetroit is the ratio of the two ratios.

    python3 tools/narrowness.py            # every title
    python3 tools/narrowness.py 8 9        # these leaves
"""
import os, sys, re
import numpy as np
import cv2

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(P, 'tools'))
import titles as T
import page as PG

THRESHOLD_FACTOR = 0.93     # below this, the composed face is too wide


def letters(img, y0, y1, x0, x1, threshold, area=20):
    """(number of clusters, median width, maximum height). A cluster is a
    group of inked columns: two welded letters make only one, and that is
    precisely what we want to count."""
    sub = (img[y0:y1 + 1, x0:x1 + 1] < threshold).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(sub, 8)
    L = sorted([s for s in st[1:] if s[4] >= area], key=lambda s: s[0])
    if not L:
        return 0, 0, 0
    return len(L), float(np.median([s[2] for s in L])), int(max(s[3] for s in L))


def analysis(leaf, key):
    pdfpage = leaf - 3 + 1
    comp, txt = T.composed_lines(pdfpage)
    fac = T.facsimile_lines(leaf)
    y_top = [y for y, t in txt if key.upper() in t.upper()]
    if not y_top:
        return None
    i = min(range(len(comp)), key=lambda k: abs(comp[k]['y0'] - y_top[0]))
    d = T._offset(comp, fac)
    target = comp[i]['y0'] - d
    j = min(range(len(fac)), key=lambda k: abs(fac[k]['y0'] - target))
    if abs(fac[j]['y0'] - target) > 30:
        return 'title not located in the facsimile'
    here, fj = comp[i], fac[j]
    nc, wc, hc = letters(T.composed_image(pdfpage), here['y0'], here['y1'],
                         here['x0'], here['x1'], 170)
    norm, gm, ang = PG.prepared_img(leaf)
    nf, wf, hf = letters(norm, fj['y0'], fj['y1'], fj['x0'], fj['x1'], 175)
    if not (hc and hf and wc):
        return 'measurement impossible'
    return {'comp': (nc, wc, hc, here['x1'] - here['x0']),
            'fac': (nf, wf, hf, fj['x1'] - fj['x0']),
            'facteur': (wf / hf) / (wc / hc)}


if __name__ == '__main__':
    wanted = {int(a) for a in sys.argv[1:]}
    tight, sound, silent = [], 0, []
    for feu, txt, fname in T.source_titles():
        if wanted and feu not in wanted:
            continue
        key = txt.split()[0] if txt.split() else ''
        key = re.sub(r'[^A-Za-z]', '', key)
        r = analysis(feu, key) if key else None
        name = '%-24s folio %3d' % (txt[:24], feu - 4)
        if r is None or isinstance(r, str):
            silent.append((name, r or 'title not found'))
            continue
        nc, wc, hc, lc = r['comp']
        nf, wf, hf, lf = r['fac']
        f = r['facteur']
        # THE FACTOR MEANS SOMETHING ONLY IF THE COMPOSED LETTERS ARE
        # SEPARATE. As soon as they weld, the "letter width" measured is
        # that of a cluster of two or three letters, and the factor drawn
        # from it is absurd: at folio 217 it came out at 0.208, at folio 11
        # at 0.380. Those titles are indeed tight -- the cluster count says
        # so -- but their factor must be taken elsewhere, from the volume's
        # titles where the letters still keep their rank.
        welded = nc < nf - 1
        if welded or f < THRESHOLD_FACTOR:
            tight.append((name, nc, nf, f, wc, hc, wf, hf, welded))
    measurable = [x[3] for x in tight if not x[8]]
    for name, nc, nf, f, wc, hc, wf, hf, welded in tight:
        if welded:
            print('  X  %s: %d composed clusters for %d surveyed — LETTERS '
                  'WELDED, factor not measurable here' % (name, nc, nf))
        else:
            print('  X  %s: %d clusters for %d; letter/capital %.3f against '
                  '%.3f  ->  \\VUetroit{%.3f}'
                  % (name, nc, nf, wc / hc, wf / hf, f))
    if measurable:
        print('\nfactor measurable on %d titles: median %.3f, from %.3f to %.3f'
              % (len(measurable), float(np.median(measurable)),
                 min(measurable), max(measurable)))
    for name, m in silent:
        print('  ?  %s : %s' % (name, m))
    print('\n%d tight titles, %d not established' % (len(tight), len(silent)))
