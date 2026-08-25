#!/usr/bin/env python3
"""Classifier of EMPHASIS: bold, italic or roman, word by word.

This is the piece the first draft lacks. OCR yields the text; it says
nothing of the typographic case. Yet in this book the distinction carries
half the meaning -- bold marks the Ido form cited as a headword, italic
what is cited from another language -- and that is where every correction
reported at proofreading has lodged.

Two measurements, taken on each word of the facsimile:

  * the WEIGHT: mean thickness of the stroke, estimated by the ratio of
    the ink to the number of inked columns. A semi-bold has a thicker
    stroke than a roman of the same size.
  * the SLOPE: angle of the horizontal shear that makes the vertical
    projection most contrasted. An italic slopes, a roman does not.

Both are normalised by the LINE'S MEDIAN, which absorbs the variations of
inking and of size from one page to another.

The classifier is worth only its error rate: we measure it against the
pages already transcribed by hand, where we know for each word whether it
is bold, italic or roman.
"""
import os, sys, re, json
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG
import cache


def words_of_line(norm, gm2, l, white_threshold=7):
    """Divides a line into words: segments separated by a wide space."""
    band = (gm2[l['y0']:l['y1'] + 1, l['x0']:l['x1'] + 1] > 0)
    if band.size == 0:
        return []
    col = band.sum(axis=0)
    empty = (col == 0).astype(np.int8)
    d = np.diff(empty)
    st = list(np.where(d == 1)[0] + 1)
    en = list(np.where(d == -1)[0] + 1)
    breaks = [(a, b) for a, b in zip(st, en) if b - a >= white_threshold]
    bounds, prev = [], 0
    for a, b in breaks:
        if a - prev > 3:
            bounds.append((prev, a))
        prev = b
    if band.shape[1] - prev > 3:
        bounds.append((prev, band.shape[1]))
    return [(l['x0'] + a, l['x0'] + b, band[:, a:b]) for a, b in bounds]


def weight(m):
    """Mean thickness of the stroke: ink per inked column."""
    col = m.sum(axis=0)
    nz = col[col > 0]
    return float(nz.mean()) if nz.size else 0.0


def slope(m, angles=np.arange(-0.40, 0.41, 0.05)):
    """Shear that makes the vertical projection most contrasted. An italic
    has a clearly positive slope, a roman a null one."""
    h, w = m.shape
    if h < 6 or w < 6:
        return 0.0
    best, ba = -1.0, 0.0
    ys = np.arange(h) - h / 2.0
    for a in angles:
        dec = (ys * a).astype(int)
        acc = np.zeros(w + 2 * int(abs(dec).max() + 1))
        off = int(abs(dec).max() + 1)
        for y in range(h):
            r = m[y]
            if not r.any():
                continue
            acc[off + dec[y]:off + dec[y] + w] += r
        v = float(((acc[1:] - acc[:-1]) ** 2).sum())
        if v > best:
            best, ba = v, float(a)
    return ba


def analyse_page(leaf):
    """For each word: weight and slope, normalised by the line."""
    d = cache.leaf(leaf)
    norm, gm, ang = PG.prepared_img(leaf)
    gm2, span = PG.text_region(gm)
    out = []
    for l in d['lines']:
        words = words_of_line(norm, gm2, l)
        if len(words) < 3:
            out.append([])
            continue
        g = [weight(m) for _, _, m in words]
        p = [slope(m) for _, _, m in words]
        gm_ = float(np.median(g)) or 1.0
        pm_ = float(np.median(p))
        out.append([{'x0': a, 'x1': b,
                     'graisse': round(g[k] / gm_, 3),
                     'pente': round(p[k] - pm_, 3)}
                    for k, (a, b, _) in enumerate(words)])
    return out


# ---------------------------------------------------------------- measure
SWEEP = re.compile(r'\\(VUgras|textit|textsc)\s*\{')


def truth(raw):
    """The expected run of (word, class), read from the LaTeX transcription."""
    out, i, stack = [], 0, []
    while i < len(raw):
        m = SWEEP.match(raw, i)
        if m:
            stack.append('gras' if m.group(1) == 'VUgras' else 'ital')
            i = m.end()
            continue
        c = raw[i]
        if c == '}':
            if stack:
                stack.pop()
            i += 1
            continue
        if c == '{':
            i += 1
            continue
        if c == '\\':
            j = i + 1
            while j < len(raw) and raw[j].isalpha():
                j += 1
            i = max(j, i + 2)
            continue
        if c.isalpha():
            j = i
            while j < len(raw) and (raw[j].isalpha() or raw[j] in "'-"):
                j += 1
            out.append((raw[i:j], stack[-1] if stack else 'rom'))
            i = j
            continue
        i += 1
    return out


if __name__ == '__main__':
    import checks as C
    pages = C.read_transcription()
    thresholds = {'gras': 1.10, 'ital': 0.06}
    conf = {}
    for pg in pages:
        f = pg.get('leaf')
        if not f or int(f) < 15:
            continue
        measures = analyse_page(int(f))
        waiting = []
        for l in pg['lines']:
            if l['text']:
                waiting.append(truth(l['brut']))
        n = min(len(waiting), len(measures) - (1 if cache.leaf(int(f))['folio_detecte'] else 0))
        dec = 1 if cache.leaf(int(f))['folio_detecte'] else 0
        for k in range(n):
            a, b = waiting[k], measures[k + dec]
            if len(a) != len(b):
                continue
            for (word, cls), mes in zip(a, b):
                pred = ('gras' if mes['graisse'] > thresholds['gras']
                        else 'ital' if mes['pente'] > thresholds['ital'] else 'rom')
                conf[(cls, pred)] = conf.get((cls, pred), 0) + 1
    total = sum(conf.values())
    just = sum(v for (a, b), v in conf.items() if a == b)
    print('Emphasis classifier, measured on the pages transcribed by hand')
    print('  words compared: %d' % total)
    if total:
        print('  exactitude    : %.1f %%' % (100.0 * just / total))
        print('\n  matrice (attendu -> predit) :')
        for a in ('rom', 'gras', 'ital'):
            line = '    %-5s' % a
            for b in ('rom', 'gras', 'ital'):
                line += ' %6d' % conf.get((a, b), 0)
            print(line + '     (columns: rom bold ital)')
