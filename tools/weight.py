#!/usr/bin/env python3
"""Judge of WEIGHT: thickness of the stems, word by word.

Three times running I was wrong about the weight of a line, first one way
then the other. The eye does not suffice at actual size, and the
enlargement itself leaves doubts when the paper has drunk the ink. Ink
density (ink / width) does not suffice either: it depends on the shape of
the letters, and at folio 51 it gave 7.3 to 8.9 for words some of which
are bold and others roman.

What settles it is the THICKNESS OF THE STEM: the median length of the
horizontal runs of inked pixels. Calibrated on the table of folio 31,
where the weight is certain:

    "tam" (bold)      5.0 px        "egaleso" (roman)  3.0 px
    "kam" (bold)      4.0 px

and at folio 51:

    "frapar, donar, lektar" (bold)   4.0 px
    "quale en la transitivi" (rom.)  3.0 px

The threshold is therefore 3.5 px. This volume's semi-bold is narrow: it
is distinguished not by its width but by its stem.

LIMIT, observed at the first use: the measurement is worth something only
where the paper is FLAT. On leaf 55 a fold crosses the page; on the line
that crosses it, the tool declares bold even the words we know to be roman
("verbo", "subjekto"), the fold's shadow thickening everything. On the next
line, clear of the fold, it cleanly separates "frapar, donar, lektar" at
4.0 px from "quale en la transitivi" at 3.0. Before concluding, therefore,
check that the band measured crosses neither a fold nor the shadow of the
binding -- a uniform verdict over a whole line is the sign that it crosses
one.

    python3 tools/weight.py 55 1576 1610
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

THRESHOLD = 3.5


def stems(gm2, a, b, u, v):
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
    runs = [r for r in runs if r <= 14]      # beyond this, it is a rule
    return float(np.median(runs)) if runs else 0.0


def line(leaf, y0, y1, gap=14):
    """Returns [(x0, x1, stem, verdict)] for each cluster of the band."""
    norm, gm, ang = PG.prepared_img(leaf)
    gm2, span = PG.text_region(gm)
    x0 = span[0]
    band = (gm2[y0:y1] > 0)
    col = band.sum(axis=0)
    xs = np.nonzero(col)[0]
    if not len(xs):
        return []
    cluster = []
    s = p = xs[0]
    for x in xs[1:]:
        if x - p > gap:
            cluster.append((s, p)); s = x
        p = x
    cluster.append((s, p))
    out = []
    for u, v in cluster:
        f = stems(gm2, y0, y1, u, v + 1)
        out.append((u - x0, v - x0, f, 'GRAS' if f >= THRESHOLD else 'romain'))
    return out


if __name__ == '__main__':
    n, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    for u, v, f, q in line(n, a, b):
        print('  %4d-%4d  fut %.1f px  %s' % (u, v, f, q))
