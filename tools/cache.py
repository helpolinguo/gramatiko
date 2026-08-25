#!/usr/bin/env python3
"""Cache of the analyses, shared by checks 8, 9 and 10.

These three checks each redid the same work: render the composed page as
an image at 300 dpi, and analyse the facsimile leaf. Over ten pages that
cost 27 seconds, most of it in deskewing the scan -- an operation that
tries fifty-one rotations.

Two caches, of different natures:

  * the FACSIMILE never changes. Its analysis is therefore written to
    disk once and for all (scan/cache/), and read back afterwards.
  * the COMPOSED page changes at every compilation. It is rendered in a
    single pass for the whole document, and kept in memory for the life
    of the process.
"""
import os, json, glob, subprocess, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(P, 'scan', 'cache')
os.makedirs(CACHE, exist_ok=True)

_composed = None


def leaf(n):
    """Analysis of leaf n of the facsimile: lines, ink, column. Read from
    disk if it is there -- the facsimile does not move."""
    fp = os.path.join(CACHE, 'f%04d.json' % n)
    if os.path.exists(fp):
        with open(fp) as fh:
            return json.load(fh)
    norm, gm, ang = PG.prepared_img(n)
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
    lines = []
    for l in fl:
        lines.append({'y0': l['y0'], 'y1': l['y1'], 'x0': l['x0'], 'x1': l['x1'],
                       'encre': int((gm2[l['y0']:l['y1']] > 0).sum())})
    d = {'leaf': n, 'skew': round(ang, 3), 'H': int(gm2.shape[0]),
         'W': int(gm2.shape[1]), 'span': list(span) if span else None,
         'folio_detecte': bool(f0), 'lines': lines}
    with open(fp, 'w') as fh:
        json.dump(d, fh)
    return d


def _render_all(pdf, npages):
    dst = os.path.join(P, 'checks', 'rendu')
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(os.path.join(dst, 'p-*.png')):
        os.remove(f)
    subprocess.run(['pdftoppm', '-r', '300', '-png', pdf,
                    os.path.join(dst, 'p')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst



# ONE BAND MAY HIDE TWO. The division above separates lines on the rows
# WITHOUT ink. It is enough for one descender to touch the ascender of the
# next line for no row to be empty and for the two lines to make only one.
# This happened at folio 87: the first two lines of the body welded
# together, the band took the abscissa of the SECOND (flush left), and
# check 10 accused a page of one \VUcontinue too many when it needed none
# -- while check 11 saw 48 px of drift in it.
#
# The facsimile does not show the fault: its scanned leading is wider. It
# is therefore an artefact of MY page, not of the model, and it is
# corrected here rather than in each check.
#
# We split any band appreciably taller than the page median, at the row
# with the LEAST ink in its central part -- where the boundary between two
# lines passes.
# BUT A TALL BAND IS NOT ALWAYS TWO LINES. At folio 31, the table's braces
# rise over 27 pt: their bands exceed the median without hiding anything,
# and split they yielded a piece of brace at +21 px from the margin, which
# check 10 at once reported -- rightly, since that piece begins neither
# flush left nor as an indent.
# We therefore require that EACH PIECE CARRY THE INK OF A REAL LINE. A
# fragment of brace carries only a fraction of it, and the band stays
# whole. Otherwise we give up splitting: better a welded band, which the
# checks know how to report, than an invented one.
SPLIT_RATIO = 1.55      # beyond this ratio to the median, we split
SPLIT_MIN_INK = 0.40    # share of the median ink required of each piece


def _split_bands(lines, bw):
    """Separates the bands that visibly contain two lines."""
    import numpy as np
    if len(lines) < 5:
        return lines
    med = float(np.median([l['y1'] - l['y0'] for l in lines]))
    median_ink = float(np.median([l['encre'] for l in lines]))
    if med <= 0:
        return lines
    out = []
    for l in lines:
        h = l['y1'] - l['y0']
        if h < SPLIT_RATIO * med:
            out.append(l)
            continue
        n = max(2, int(round(h / med)))
        bounds = [l['y0']]
        for k in range(1, n):
            target = l['y0'] + int(round(k * h / n))
            lo = max(l['y0'] + 4, target - int(0.3 * med))
            hi = min(l['y1'] - 4, target + int(0.3 * med))
            if hi <= lo:
                bounds = None
                break
            depth = bw[lo:hi].sum(axis=1)
            bounds.append(lo + int(np.argmin(depth)))
        if bounds is None:
            out.append(l)
            continue
        bounds.append(l['y1'])
        pieces = []
        for a, b in zip(bounds[:-1], bounds[1:]):
            if b - a < 8:
                pieces = None
                break
            xs = np.where(bw[a:b].sum(axis=0) > 0)[0]
            if len(xs) < 20:
                pieces = None
                break
            pieces.append({'y0': int(a), 'y1': int(b), 'x0': int(xs[0]),
                             'x1': int(xs[-1]), 'encre': int(bw[a:b].sum())})
        if pieces and min(m['encre'] for m in pieces) >= SPLIT_MIN_INK * median_ink:
            out.extend(pieces)
        else:
            out.append(l)
    return out

def compose(pdf, npages):
    """Lines of each composed page: (y0, y1, x0, x1, ink). A single
    rendering pass for the whole document."""
    global _composed
    if _composed is not None:
        return _composed
    dst = _render_all(pdf, npages)
    out = {}
    for fp in sorted(glob.glob(os.path.join(dst, 'p-*.png'))):
        i = int(os.path.basename(fp).split('-')[1].split('.')[0])
        bw = (cv2.imread(fp, cv2.IMREAD_GRAYSCALE) < 160).astype(np.uint8)
        rows = bw.sum(axis=1)
        on = (rows > 4).astype(np.int8)
        d = np.diff(on)
        st = list(np.where(d == 1)[0] + 1)
        en = list(np.where(d == -1)[0] + 1)
        if on[0]: st.insert(0, 0)
        if on[-1]: en.append(len(on))
        raw = []
        for a, b in zip(st, en):
            if b - a < 8:
                continue
            xs = np.where(bw[a:b].sum(axis=0) > 0)[0]
            if len(xs) < 20:
                continue
            raw.append({'y0': int(a), 'y1': int(b), 'x0': int(xs[0]),
                         'x1': int(xs[-1]), 'encre': int(bw[a:b].sum())})
        if raw:
            full = max(l['encre'] for l in raw)
            raw = [l for l in raw if l['encre'] >= 0.03 * full]
        raw = _split_bands(raw, bw)
        out[i] = {'fichier': fp, 'lines': raw}
    _composed = out
    return out


def clear_composed_cache():
    global _composed
    _composed = None


if __name__ == '__main__':
    import time
    if '--warm' in sys.argv:
        # fills the facsimile cache for every leaf
        lo = int(sys.argv[sys.argv.index('--warm') + 1])
        hi = int(sys.argv[sys.argv.index('--warm') + 2])
        t = time.time()
        for n in range(lo, hi + 1):
            leaf(n)
            if n % 10 == 0:
                print('  %d  (%.0f s)' % (n, time.time() - t), flush=True)
        print('facsimile cache: leaves %d to %d, %.0f s'
              % (lo, hi, time.time() - t))
