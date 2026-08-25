#!/usr/bin/env python3
"""Preparation of a facsimile page, and location of its text block.

Cropping to "the light area" is deceptive: the fore-edge of the
neighbouring leaves is light too, and the shadow of the binding eats one
edge. We therefore locate the text block by the GLYPHS themselves:
connected components of a size compatible with characters of about 10 pt
at 300 dpi.
"""
import os, sys, json
import numpy as np
import cv2

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(P, 'scan', 'pages')
DPI = 300.0
PX2MM = 25.4 / DPI
PX2PT = 72.27 / DPI      # TeX point
PX2BP = 72.0 / DPI       # PostScript point


def normalise_img(gray):
    """Evens out the ground (yellowed paper, shadow of the binding)."""
    small = cv2.resize(gray, None, fx=0.08, fy=0.08, interpolation=cv2.INTER_AREA)
    bg = cv2.medianBlur(small, 31)
    bg = cv2.resize(bg, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_CUBIC)
    n = gray.astype(np.float32) / np.maximum(bg.astype(np.float32), 1.0) * 210.0
    return np.clip(n, 0, 255).astype(np.uint8)


def glyph_mask(norm):
    """Binary mask keeping only components of glyph size."""
    bw = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(bw, 8)
    keep = np.zeros(nlab, np.uint8)
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        if 3 <= h <= 70 and 2 <= w <= 90 and a >= 8 and a <= 3000 and w / max(h, 1) < 12:
            keep[i] = 1
    return keep[lab] * 255


def deskew(norm, gm):
    """Angle by maximising the contrast of the horizontal projection."""
    s = cv2.resize(gm, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    h, w = s.shape
    best, ba = -1.0, 0.0
    for a in np.arange(-2.5, 2.51, 0.05):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), float(a), 1.0)
        r = cv2.warpAffine(s, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=0)
        pr = r.sum(axis=1).astype(np.float64)
        sc = float(((pr[1:] - pr[:-1]) ** 2).sum())
        if sc > best:
            best, ba = sc, float(a)
    H, W = norm.shape
    M = cv2.getRotationMatrix2D((W / 2, H / 2), ba, 1.0)
    rot = cv2.warpAffine(norm, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=255)
    rotg = cv2.warpAffine(gm, M, (W, H), flags=cv2.INTER_NEAREST, borderValue=0)
    return rot, rotg, ba


def prepared_img(n):
    """Normalised image + glyph mask, both deskewed. No cropping."""
    g = cv2.imread(os.path.join(PAGES, 'f%04d.jpg' % n), cv2.IMREAD_GRAYSCALE)
    norm = normalise_img(g)
    gm = glyph_mask(norm)
    return deskew(norm, gm)


def text_region(gm):
    """Isolates the text block: we weld the glyphs into lines, then keep the
    components that are wide and low (a line of text). The fore-edges of
    neighbouring leaves give components that are tall and narrow: rejected."""
    H, W = gm.shape
    # --- Text column established BEFORE the welding --------------------
    # The welding (61, 3) fills gaps of less than 61 px. At the right edge of
    # leaf 34, the fore-edge of the neighbouring leaf leaves fragments 38 px
    # from the last character: the welding agglomerates them into the line,
    # the component extends to the edge of the image, and EVERY bound
    # computed afterwards (percentiles, clipping) inherits the noise. The
    # column must therefore be bounded before welding.
    # Density criterion: a column of pixels inside the text block is crossed
    # by nearly every line; a fragment of fore-edge touches only a few.
    # Measured on 34 leaves spread through the volume: the width found is
    # 1083 px on the great majority of them, which is exactly
    # \VUtexteLargeur (91.69 mm at 300 dpi) -- the bound is therefore right,
    # and not merely plausible.
    _col = (gm > 0).sum(axis=0)
    if _col.max() > 0:
        _thr = max(3.0, 0.15 * np.percentile(_col, 90))
        _xs = np.nonzero(_col > _thr)[0]
        if len(_xs):
            _runs = []
            _s = _p = _xs[0]
            for _x in _xs[1:]:
                # 40 px: on leaf 34 the fore-edge fragments are 40 px from the
                # last character; a wider value reattaches them to the column and
                # cancels the whole benefit. Checked on 34 leaves: no legitimate
                # column is split, including that of the table on leaf 35.
                if _x - _p > 40:
                    _runs.append((_s, _p)); _s = _x
                _p = _x
            _runs.append((_s, _p))
            _c0, _c1 = max(_runs, key=lambda r: r[1] - r[0])
            # 12 px of play: enough to let a hyphen or a comma hang out
            # without letting the fore-edge in.
            gm = gm.copy()
            gm[:, :max(0, _c0 - 12)] = 0
            gm[:, min(W, _c1 + 13):] = 0
    band = cv2.morphologyEx(gm, cv2.MORPH_CLOSE, cv2.getStructuringElement(
        cv2.MORPH_RECT, (61, 3)))
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats((band > 0).astype(np.uint8), 8)
    keep = np.zeros((H, W), np.uint8)
    boxes = []
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        # The edges of the image are scanning noise (edge of the platen,
        # fore-edge of the neighbouring leaf): we discard them first. Without
        # this, a stray bar at the top of a page counted as a line, and the
        # folio, being narrower, was rejected: the line count no longer came
        # out right and check 9 skipped the page -- precisely where the errors
        # hide.
        if y < 0.015 * H or y + h > 0.985 * H:
            continue
        if w < 0.04 * W:           # too short, even for a folio
            continue
        if h > 0.10 * H:           # too tall: that is a fore-edge, not a line
            continue
        if w / max(h, 1) < 2.0:
            continue
        keep[lab == i] = 1
        boxes.append((x, y, x + w, y + h))
    if not boxes:
        return gm, None
    # Text column established by the first pass: the recovery below is
    # confined to it, or it brings back the fore-edges of neighbouring
    # leaves, which share the same vertical band (tried: the measure of
    # leaf 15 went from 91.6 to 103.4 mm).
    _xs0 = np.percentile([b[0] for b in boxes], 10)
    _xs1 = np.percentile([b[2] for b in boxes], 90)
    _tol = 0.04 * W
    # Cleaning pass: the first pass does not bound the column, and a
    # scanning smear wide enough and flat enough passed there for a line,
    # overhanging by 200 px on the right. The line detected was then too
    # wide, its ink wrong, and check 9 produced absurd deviations (+4702 %).
    # We eliminate those components, then recompute the column on what is
    # left.
    # We CLIP to the column instead of REJECTING what overhangs it.
    # Rejecting was dangerous: at folio 20, four lines heavily set in italic
    # weld into a single component 165 px tall (the fold of the paper
    # bridges them), which overhangs the column by three pixels -- and the
    # four lines disappeared at a stroke. A component that overhangs a
    # little is still text: we cut off what sticks out, we do not throw it
    # away.
    clean = [b for b in boxes
               if b[0] >= _xs0 - _tol and b[2] <= _xs1 + _tol]
    if len(clean) >= max(4, 0.5 * len(boxes)):
        g0 = max(0, int(_xs0 - _tol)); g1 = min(W, int(_xs1 + _tol) + 1)
        keep[:, :g0] = 0
        keep[:, g1:] = 0
        boxes = [(max(b[0], g0), b[1], min(b[2], g1), b[3]) for b in boxes
                 if b[2] > g0 and b[0] < g1]
        _xs0 = np.percentile([b[0] for b in boxes], 10)
        _xs1 = np.percentile([b[2] for b in boxes], 90)
    # Second pass: we recover the short fragments belonging to a line
    # already kept. A line such as "3. --- B = b en ..." splits into several
    # components, the white space around the em dash and the equals sign
    # exceeding the welding width; the left-hand fragment was then rejected
    # as too short, and the line found itself docked of its beginning --
    # which falsifies both its width and its ink, hence check 9 and the
    # measurement of the text width.
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        if keep[y + h // 2, x + w // 2] or h > 0.10 * H:
            continue
        if y < 0.015 * H or y + h > 0.985 * H:
            continue
        # Tolerance MUCH tighter than that of the clipping. This pass accepts
        # short components; at the right edge of leaf 34 the fragments of the
        # neighbouring fore-edge (x = 1348..1365, 8 to 17 px wide) fell under
        # the old tolerance of 0.04 W = 55 px and were recovered because they
        # share the ordinate of a real line: the width recorded rose to 1365 px
        # over half the page, and check 10, which compares right-hand edges,
        # would have declared correctly justified lines to be overhanging.
        # 0.012 W = 16 px lets a hanging hyphen or comma through, not the
        # fore-edge.
        _tolr = 0.012 * W
        if x < _xs0 - _tolr or x + w > _xs1 + _tolr:
            continue
        for bx0, by0, bx1, by1 in boxes:
            overlaps = min(y + h, by1) - max(y, by0)
            if overlaps > 0.5 * min(h, by1 - by0):
                keep[lab == i] = 1
                break
    xs0 = np.array([b[0] for b in boxes]); xs1 = np.array([b[2] for b in boxes])
    # left margin: robust low quantile; right margin: high quantile
    x0 = int(np.percentile(xs0, 10)); x1 = int(np.percentile(xs1, 90))
    return (gm * keep), (x0, x1)


def lines_of(gm, min_ink=None):
    """Lines of text: segments of the horizontal projection of the mask."""
    rows = (gm > 0).sum(axis=1)
    if rows.max() == 0:
        return []
    thr = min_ink if min_ink else max(5, rows.max() * 0.06)
    on = (rows > thr).astype(np.int8)
    d = np.diff(on)
    st = list(np.where(d == 1)[0] + 1)
    en = list(np.where(d == -1)[0] + 1)
    if on[0]: st.insert(0, 0)
    if on[-1]: en.append(len(on))
    # --- Recovery of PALE lines ----------------------------------------
    # The threshold is computed on the page maximum: a short line, or one
    # wholly in italic, can fall below it. Three pages showed this (leaves
    # 40 and 41: "XI, 296.)", "misas.", "ici, iti."), and the facsimile was
    # recorded with one or two lines fewer than the reality -- checks 9 and
    # 11 then skipped the page.
    # Lowering the threshold everywhere would weld lines together elsewhere
    # (tried: leaf 200 fell from 39 to 32 lines). We therefore lower it only
    # IN THE GAPS, and accept the find only if it has the ink of a real
    # line.
    # The discriminant is the INK RELATIVE TO THE MEDIAN LINE. Measured on
    # leaves 19 to 25, 37, 40 and 41: the real missing lines weigh 0.142 to
    # 0.162; the fragments of descenders and the specks, 0.024 to 0.089. The
    # threshold is set at 0.12, in the middle of that gap.
    # What this does not recover: "lua, lia." on leaf 37, at 0.086, falls on
    # the wrong side. We do not go lower for the sole reason that one page
    # would gain by it -- three others would lose.
    pairs = [(a, b) for a, b in zip(st, en) if b - a >= 9]
    if len(pairs) >= 5:
        _enc = sorted(int((gm[a:b] > 0).sum()) for a, b in pairs)
        _med = _enc[len(_enc) // 2]
        _pitch = sorted(pairs[k + 1][0] - pairs[k][0]
                      for k in range(len(pairs) - 1))
        _pm = _pitch[len(_pitch) // 2]
        zones = [(pairs[k][1], pairs[k + 1][0])
                 for k in range(len(pairs) - 1)
                 if pairs[k + 1][0] - pairs[k][0] >= 1.35 * _pm]
        # after the last line: that is where the end of a note falls
        zones.append((pairs[-1][1], min(len(rows), pairs[-1][1] + 2 * _pm)))
        for a, b in zones:
            if b - a < 12:
                continue
            on2 = (rows[a:b] > 0.3 * thr).astype(np.int8)
            d2 = np.diff(on2)
            s2 = list(np.where(d2 == 1)[0] + 1)
            e2 = list(np.where(d2 == -1)[0] + 1)
            if on2[0]: s2.insert(0, 0)
            if on2[-1]: e2.append(len(on2))
            for p, q in zip(s2, e2):
                if q - p < 12:
                    continue
                seg = (gm[a + p:a + q] > 0)
                if len(np.where(seg.sum(axis=0) > 0)[0]) < 60:
                    continue
                if seg.sum() < 0.12 * _med:
                    continue
                pairs.append((a + p, a + q))
        pairs.sort()
        st = [a for a, _ in pairs]
        en = [b for _, b in pairs]
    out = []
    for s, e in zip(st, en):
        if e - s < 9:
            continue
        seg = (gm[s:e] > 0)
        c = seg.sum(axis=0)
        xs = np.where(c > 0)[0]
        if len(xs) < 20:
            continue
        out.append({'y0': int(s), 'y1': int(e), 'x0': int(xs[0]), 'x1': int(xs[-1]),
                    'ink': int(seg.sum())})
    return out


def folio_line(gm, lines, fallback=None):
    """The folio "-- 12 --" carries very little ink: it falls under the
    line-detection threshold, which is computed on the page maximum.
    Lowering it would fuse neighbouring lines elsewhere (tried: leaf 200
    fell from 39 to 32 lines). We therefore look for it separately, in
    the top of the page, with a low threshold, and only if it has not
    already been found.

    `fallback` is a second mask, searched if the first yields nothing. It
    serves when text_region has erased the folio: the em dashes framing
    it are flat and wide, hence rejected by the glyph mask, and only the
    digits remain. On leaf 42 the folio is thus reduced to "38", welded
    over 60 px -- less than the 0.04 W = 63 px required of a line. The
    page was then recorded without a folio, and checks 9 and 11 skipped
    it.
    """
    r = _find_folio(gm, lines)
    if r is None and fallback is not None:
        r = _find_folio(fallback, lines)
    return r


def _find_folio(gm, lines):
    H, W = gm.shape

    def is_folio(l):
        larg = l['x1'] - l['x0']
        centre = (l['x0'] + l['x1']) / 2 / W
        return larg < 0.22 * W and 0.35 < centre < 0.65 and l['y0'] < 0.13 * H

    if lines and is_folio(lines[0]):
        return None                      # already detected
    # we look only ABOVE the first line found
    top = int(0.13 * H)
    if lines:
        top = min(top, max(0, lines[0]['y0'] - 15))
    if top < 20:
        return None
    sous = gm[:top]
    rows = (sous > 0).sum(axis=1)
    if rows.max() < 4:
        return None
    on = (rows > 3).astype(np.int8)
    d = np.diff(on)
    st = list(np.where(d == 1)[0] + 1); en = list(np.where(d == -1)[0] + 1)
    if on[0]: st.insert(0, 0)
    if on[-1]: en.append(len(on))
    for s, e in zip(st, en):
        if e - s < 9:
            continue
        seg = (sous[s:e] > 0)
        xs = np.where(seg.sum(axis=0) > 0)[0]
        if len(xs) < 8:
            continue
        # We examine the CLUSTERS of the band, not its total extent. A fold in
        # the paper leaves a diagonal stroke crossing the height of the folio:
        # on leaf 48 it carried the extent to 396 px, centred at 0.703, and the
        # folio was rejected as too wide and off-centre. Each cluster is tested
        # separately; the first that has the size and position of a folio is
        # kept.
        cluster = []
        _s = _p = xs[0]
        for _x in xs[1:]:
            if _x - _p > 40:
                cluster.append((_s, _p)); _s = _x
            _p = _x
        cluster.append((_s, _p))
        for a0, a1 in cluster:
            if a1 - a0 < 20:
                continue
            larg = a1 - a0
            centre = (a0 + a1) / 2 / W
            # short, centred: that is a folio, not a line of text
            if larg < 0.22 * W and 0.35 < centre < 0.65:
                return {'y0': int(s), 'y1': int(e), 'x0': int(a0), 'x1': int(a1),
                        'ink': int((sous[s:e, a0:a1 + 1] > 0).sum())}
    return None


def block(n):
    """Geometry of a page's text block."""
    norm, gm, ang = prepared_img(n)
    H, W = norm.shape
    gm2, span = text_region(gm)
    ls = lines_of(gm2)
    f = folio_line(gm2, ls)
    if f:
        ls.insert(0, f)
    if not ls:
        return {'leaf': n, 'blank': True, 'skew': ang, 'W': W, 'H': H}
    # left margin: mode of the line starts (very stable in running text)
    lefts = np.array([l['x0'] for l in ls])
    rights = np.array([l['x1'] for l in ls])
    left = float(np.percentile(lefts, 25))
    right = float(np.percentile(rights, 75))
    just = right - left
    tops = [l['y0'] for l in ls]
    steps = np.diff(tops)
    steps = steps[(steps > 22) & (steps < 70)]
    return {
        'leaf': n, 'skew': round(ang, 2), 'W': W, 'H': H,
        'n_lines': len(ls),
        'left': round(left, 1), 'right': round(right, 1), 'span': span,
        'just_px': round(just, 1),
        'just_mm': round(just * PX2MM, 2),
        'just_pt': round(just * PX2PT, 2),
        'y_first': ls[0]['y0'], 'y_last': ls[-1]['y1'],
        'step_px': round(float(np.median(steps)), 2) if len(steps) else None,
        'step_pt': round(float(np.median(steps)) * PX2PT, 2) if len(steps) else None,
        'lines': ls,
    }


if __name__ == '__main__':
    for a in sys.argv[1:]:
        b = block(int(a))
        b.pop('lines', None)
        print(json.dumps(b), flush=True)
