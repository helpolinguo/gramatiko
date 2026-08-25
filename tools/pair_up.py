#!/usr/bin/env python3
"""Matching of the facsimile's lines with the composed lines.

Checks 9 and 10 compared the two pages RANK BY RANK, after verifying that
the number of lines coincided -- and skipped the page otherwise. That was
their gravest defect: line detection is out by one often enough (a pale
folio, a short line, a speck of ink), and the page was then declared not
comparable. The checks therefore returned a green verdict on the very
pages that needed examining: tested by reintroducing a known fault, the
check on paragraph endings did not see it, for want of having compared
the page.

We therefore match the lines by their VERTICAL POSITION. The facsimile
and the composed page having, by construction, the same layout, a line of
the first falls at the same height as the corresponding line of the
second, up to the scanning offset -- the paper does not occupy the same
place in every image of the scan.

Two stages:
  1. estimate the global vertical offset between the two runs;
  2. match by dynamic programming, which allows a supernumerary line on
     either side without derailing all the rest.

The function returns the list of pairs (facsimile index, composed index)
and the indices left alone, which the caller may report.
"""

# MAX_GAP must stay clearly BELOW the leading (41 px): at 40 px, a line
# could match its neighbour as well as itself, and the matching slipped
# by one rank over a whole page without the total cost suffering. At
# 16 px, such a slip is forbidden.
MAX_GAP = 16.0
# The gap must cost more than the worst lawful match, or the algorithm
# prefers to skip lines rather than match them.
GAP_COST = 22.0


def _centres(lines):
    return [(a + b) / 2.0 for a, b in lines]


def estimate_transform(cf, cc):
    """Affine transformation y_composed = a * y_fac + b that best
    superimposes the two runs.

    A simple offset does not suffice: the scanning does not have the same
    scale from one page to another (the width of the double-page images
    runs from 2680 to 2818 px, that is 5 %). On a page of forty lines, a
    scale error of 2 % drifts by more than thirty pixels between top and
    bottom -- enough to match each line with its neighbour, which produces
    a characteristic alternation of false positives.

    We therefore fit scale and offset by least squares on the
    nearest-neighbour pairs, iterated (iterative closest point).
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
            if abs(d - p) < 3 * GAP_COST:
                xs.append(y); ys.append(d)
        if len(xs) < 3:
            break
        n = len(xs)
        mx = sum(xs) / n; my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        denom = sum((x - mx) ** 2 for x in xs)
        if denom <= 0:
            break
        na = num / denom
        if not (0.9 < na < 1.1):        # guard rail: the scale stays near 1
            na = 1.0
        nb = my - na * mx
        if abs(na - a) < 1e-6 and abs(nb - b) < 1e-3:
            a, b = na, nb
            break
        a, b = na, nb
    return a, b


def matched(fac_lines, lines_comp):
    """lines_*: runs of pairs (y0, y1). Returns (pairs, fac_alone,
    comp_alone)."""
    cf = _centres(fac_lines)
    cc = _centres(lines_comp)
    if not cf or not cc:
        return [], list(range(len(cf))), list(range(len(cc)))
    a, b = estimate_transform(cf, cc)
    n, m = len(cf), len(cc)
    # dynamic programming: monotone matching with gaps
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
                if e <= MAX_GAP:
                    v = d[i][j] + e
                    if v < d[i + 1][j + 1]:
                        d[i + 1][j + 1] = v
                        ch[i + 1][j + 1] = ('=', i, j)
            if i < n:
                v = d[i][j] + GAP_COST
                if v < d[i + 1][j]:
                    d[i + 1][j] = v
                    ch[i + 1][j] = ('f', i, j)
            if j < m:
                v = d[i][j] + GAP_COST
                if v < d[i][j + 1]:
                    d[i][j + 1] = v
                    ch[i][j + 1] = ('c', i, j)
    pairs_of, sf, sc = [], [], []
    i, j = n, m
    while i or j:
        mv = ch[i][j]
        if mv is None:
            break
        k, pi, pj = mv
        if k == '=':
            pairs_of.append((pi, pj))
        elif k == 'f':
            sf.append(pi)
        else:
            sc.append(pj)
        i, j = pi, pj
    pairs_of.reverse(); sf.reverse(); sc.reverse()
    return pairs_of, sf, sc


if __name__ == '__main__':
    a = [(100, 130), (140, 170), (180, 210), (260, 290)]
    b = [(105, 135), (145, 175), (185, 215), (222, 228), (265, 295)]
    c, sf, sc = matched(a, b)
    print('couples :', c)
    print('facsimile only:', sf, ' composed only:', sc)
