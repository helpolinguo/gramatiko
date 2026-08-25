#!/usr/bin/env python3
"""Check of the WHITE SPACE AROUND TITLES, by matching on the ORDINATE
and not on the rank.

The first sweep matched the composed line to the facsimile line by their
RANK in the page. That is wrong as soon as the two counts differ by one --
a short line missed by the detector, two tight lines welded by pdftotext --
and one discrepancy is enough for everything that follows to be matched
askew. Of the volume's 51 titles, that sweep gave 23 out of tolerance,
including deviations of 110 to 228 px that were nothing but false matches.

We therefore match by POSITION. The two pages are not in the same frame:
the scan has its own vertical offset, page by page. But that offset is a
CONSTANT per page, and it is found without assuming anything about the
counts: we try every plausible offset and keep the one that matches the
most lines to within eight pixels. It is a vote, not a hypothesis.

A title is then measured only if BOTH ITS NEIGHBOURS are matched too, and
matched in order: failing which the white space compared would not be the
same white space. What cannot be established is stated as such rather than
counted as good.

    python3 tools/titles.py            # every title
    python3 tools/titles.py 173 176    # these leaves only
"""
import os, re, sys, subprocess
import numpy as np

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(P, 'tools'))
import page as PG

PX2MM = 25.4 / 300.0
TOL_MATCH = 10     # px: two matched lines
TOL_WHITE = 14           # px = 1.2 mm: beyond this, the white space is wrong
FIRST_LEAF_NUM = 3     # the volume begins at the printed cover


def source_titles():
    """[(leaf, text)] in the order of the volume."""
    out = []
    for f in ('content/00-front-matter.tex', 'content/10-part1.tex',
              'content/20-part2.tex'):
        feu = None
        for l in open(os.path.join(P, f), encoding='utf-8'):
            m = re.search(r'\\begin\{VUpage\}\[(\d+)\]', l)
            if m:
                feu = int(m.group(1))
            m = re.search(r'\\VUtitre\{[^}]*\}\{[^}]*\}\{(.*)$', l)
            if m:
                t = m.group(1)
                # \VUetroit{factor}{text}: the factor is not text
                t = re.sub(r'\\VUetroit\{[\d.]+\}', ' ', t)
                t = re.sub(r'\\[A-Za-z]+(\[[^\]]*\])?', ' ', t)
                t = re.sub(r'[{}\\]', ' ', t)
                out.append((feu, ' '.join(t.split()), f))
    return out


def bands(img, threshold, minink=4, merged=3, hmin=6):
    """Rows of ink of an image: the SAME algorithm on both sides.

    This is the point on which the first attempt at matching by ordinate
    failed. There we took, on the composed side, pdftotext's yMin -- the
    top of the FONT BOX, constant from one line to the next -- and, on the
    facsimile side, the top of the INK, which rises or falls by ten pixels
    according to whether the line carries ascenders. The two quantities are
    not commensurable, and no constant offset could match them: the vote
    returned anything at all.
    We therefore call PG.lines_of ON BOTH SIDES: the same division into
    lines on the composed page, rendered at 300 dpi and thresholded, and on
    the facsimile. The two y0 are then the same quantity.
    """
    ink = (img < threshold).sum(axis=1)
    out, d = [], None
    for y, v in enumerate(ink):
        if v >= minink and d is None:
            d = y
        elif v < minink and d is not None:
            out.append((d, y - 1))
            d = None
    if d is not None:
        out.append((d, img.shape[0] - 1))
    mg = []
    for b in out:
        if mg and b[0] - mg[-1][1] <= merged:
            mg[-1] = (mg[-1][0], b[1])
        else:
            mg.append(b)
    return [{'y0': a, 'y1': b} for a, b in mg if b - a >= hmin]


def composed_image(pdfpage):
    import cv2, glob, tempfile
    d = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-r', '300', '-f', str(pdfpage), '-l',
                    str(pdfpage), '-gray', '-png',
                    os.path.join(P, 'gramatiko.pdf'), os.path.join(d, 'p')],
                   check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    g = cv2.imread(glob.glob(os.path.join(d, 'p*.png'))[0], 0)
    for x in glob.glob(os.path.join(d, 'p*.png')):
        os.remove(x)
    os.rmdir(d)
    return g


def composed_lines(pdfpage):
    """(bands of ink, text per line). The text serves to RECOGNISE the title;
    the ordinates, to match it. The two lists do not necessarily have the
    same length -- pdftotext separates lines that the ink profile welds --
    and we use them only to situate the title in the page, never to
    count."""
    x = os.path.join(P, 'tools', '.tmp', 'titles.xml')
    os.makedirs(os.path.dirname(x), exist_ok=True)
    subprocess.run(['pdftotext', '-f', str(pdfpage), '-l', str(pdfpage),
                    '-bbox-layout', os.path.join(P, 'gramatiko.pdf'), x],
                   check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    s = open(x, encoding='utf-8').read()
    txt = []
    for a, b in re.findall(
            r'<line xMin="[\d.]+" yMin="([\d.]+)"[^>]*>(.*?)</line>', s, re.S):
        txt.append((float(a) * 300 / 72.0, ' '.join(re.sub(r'<[^>]+>', ' ', b).split())))
    import numpy as np
    img = composed_image(pdfpage)
    gm = ((img < 170) * 255).astype(np.uint8)
    return PG.lines_of(gm), txt


def facsimile_lines(leaf):
    """Bands of ink of the facsimile, within the text column, FOLIO
    INCLUDED: the composed page carries it, and forgetting it would shift
    the whole matching by one rank."""
    norm, gm, ang = PG.prepared_img(leaf)
    gm2, span = PG.text_region(gm)
    fl = PG.lines_of(gm2)
    sec = gm.copy()
    if span:
        sec[:, :max(0, span[0] - 12)] = 0
        sec[:, min(sec.shape[1], span[1] + 13):] = 0
    f0 = PG.folio_line(gm2, fl, sec)
    if f0:
        fl = [f0] + fl
    return fl


def _offset(comp, fac):
    """The vertical offset of the composed page on the facsimile, by VOTE:
    we try every plausible offset and keep the one that matches the most
    lines. No assumption about the counts."""
    cand = sorted({round(c['y0'] - f['y0']) for c in comp for f in fac})
    best, bestn = 0, -1
    for d in cand:
        n = sum(1 for c in comp
                if min(abs(c['y0'] - (f['y0'] + d)) for f in fac)
                <= TOL_MATCH)
        if n > bestn:
            best, bestn = d, n
    return best


def matched(comp, fac):
    """(offset, {i composed -> j facsimile}) by MONOTONE ALIGNMENT.

    The matching was at first greedy: we walked the composed lines in order
    and took for each the nearest facsimile line still free. That suffices
    as long as the two pages keep step, but a line matched early STARVES
    its neighbour: at folio 169 the title was matched correctly and both
    its neighbours declared "not matched" for that reason alone, which left
    the check silent where it ought to have spoken.

    We therefore solve the alignment whole, by dynamic programming
    (Needleman and Wunsch), with two properties the greedy method lacks:
    the ORDER is imposed -- two lines cannot cross -- and the choice is
    GLOBAL, each pair being kept for what it is worth in the best
    alignment, not for its rank.

    A pair scores TOL_MATCH - deviation, hence the more the cleaner it is;
    a gap costs GAP. The gap is cheap by design: a line missing on one side
    is an ordinary accident of the division, and it is better to skip it
    than to force a false pair.
    """
    if not comp or not fac:
        return 0, {}
    d = _offset(comp, fac)
    n, m = len(comp), len(fac)
    GAP = -1.0
    S = np.full((n + 1, m + 1), -np.inf)
    S[0, :] = np.arange(m + 1) * GAP
    S[:, 0] = np.arange(n + 1) * GAP
    origin = np.zeros((n + 1, m + 1), np.int8)     # 1 pair, 2 skip i, 3 skip j
    origin[0, 1:] = 3
    origin[1:, 0] = 2
    for i in range(1, n + 1):
        here = comp[i - 1]['y0']
        for j in range(1, m + 1):
            e = abs(here - (fac[j - 1]['y0'] + d))
            best, k = S[i - 1, j] + GAP, 2
            if S[i, j - 1] + GAP > best:
                best, k = S[i, j - 1] + GAP, 3
            if e <= TOL_MATCH:
                v = S[i - 1, j - 1] + (TOL_MATCH - e)
                if v > best:
                    best, k = v, 1
            S[i, j], origin[i, j] = best, k
    pairs = {}
    i, j = n, m
    while i > 0 or j > 0:
        k = origin[i, j]
        if k == 1:
            pairs[i - 1] = j - 1
            i -= 1
            j -= 1
        elif k == 2:
            i -= 1
        else:
            j -= 1
    return d, pairs


def check(leaf, text):
    pdfpage = leaf - FIRST_LEAF_NUM + 1
    comp, txt = composed_lines(pdfpage)
    fac = facsimile_lines(leaf)
    key = re.sub(r'[^A-Za-z]', '', text.split()[0]).upper() if text.split() else ''
    y_top = [y for y, t in txt
          if key and key in re.sub(r'[^A-Za-z]', '', t).upper()]
    if not y_top:
        return ('title not found in the composed page', None, None)
    # the band of ink carrying the title: the one whose top is nearest
    # pdftotext's yMin, to within half a line
    i = min(range(len(comp)), key=lambda k: abs(comp[k]['y0'] - y_top[0]))
    if abs(comp[i]['y0'] - y_top[0]) > 25:
        return ('title not found again in the ink profile', None, None)
    d, pairs = matched(comp, fac)
    if i not in pairs:
        return ('title not matched to the facsimile', None, None)
    j = pairs[i]
    res = {}
    for side, di in (('avant', -1), ('apres', +1)):
        ii, jj = i + di, j + di
        if not (0 <= ii < len(comp) and 0 <= jj < len(fac)):
            res[side] = None                    # edge of page: nothing to measure
        elif pairs.get(ii) != jj:
            res[side] = 'neighbour not matched'
        else:
            cb = abs(comp[i]['y0'] - comp[ii]['y0'])
            fb = abs(fac[j]['y0'] - fac[jj]['y0'])
            res[side] = (fb, cb, cb - fb)
    return (None, res, d)


if __name__ == '__main__':
    wanted = {int(a) for a in sys.argv[1:]}
    T = source_titles()
    bad = uncertain = good = 0
    for feu, txt, fname in T:
        if wanted and feu not in wanted:
            continue
        err, res, d = check(feu, txt)
        name = '%-26s folio %3s' % (txt[:26], feu - 4)
        if err:
            uncertain += 1
            print('  ?  %s : %s' % (name, err))
            continue
        pb = []
        inc = False
        for side in ('avant', 'apres'):
            r = res[side]
            if r is None:
                continue
            if isinstance(r, str):
                inc = True
                pb.append('%s : %s' % (side, r))
            elif abs(r[2]) > TOL_WHITE:
                pb.append('%s: fac %d, composed %d, %+d px = %+.2f mm'
                          % (side, r[0], r[1], r[2], r[2] * PX2MM))
        if pb and not inc:
            bad += 1
            print('  X  %s : %s' % (name, ' ; '.join(pb)))
        elif inc:
            uncertain += 1
            print('  ?  %s : %s' % (name, ' ; '.join(pb)))
        else:
            good += 1
    print('\n%d titles: %d right, %d wrong, %d not established'
          % (good + bad + uncertain, good, bad, uncertain))
