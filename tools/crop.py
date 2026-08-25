#!/usr/bin/env python3
"""Isolates the PAPER area of a scanned page, then measures the text block.

The scan contains, around the useful page: the shadow of the binding
(dark), the fore-edge of the neighbouring leaves (light, striped) and the
scanner's ground. We locate the paper by its lightness: it is the largest
light and homogeneous component of the image.
"""
import os, sys, json
import numpy as np
import cv2

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(P, 'scan', 'pages')
DPI = 300.0
PX2MM = 25.4 / DPI
PX2PT = 72.27 / DPI


def paper_box(gray):
    """Rectangle of the paper: largest light component."""
    h, w = gray.shape
    small = cv2.resize(gray, (w // 8, h // 8), interpolation=cv2.INTER_AREA)
    blur = cv2.GaussianBlur(small, (9, 9), 0)
    thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    thr = cv2.morphologyEx(thr, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(thr, 8)
    if nlab <= 1:
        return 0, 0, w, h
    i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    x, y, width_w, hh = stats[i, :4]
    return int(x) * 8, int(y) * 8, int(x + width_w) * 8, int(y + hh) * 8


def normalise_img(gray):
    bg = cv2.medianBlur(cv2.resize(gray, None, fx=0.1, fy=0.1), 21)
    bg = cv2.resize(bg, (gray.shape[1], gray.shape[0]))
    n = np.clip(gray.astype(np.float32) / np.maximum(bg.astype(np.float32), 1) * 200, 0, 255)
    return n.astype(np.uint8)


def deskew(img):
    bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    s = cv2.resize(bw, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    h, w = s.shape
    best, ba = -1.0, 0.0
    for a in np.arange(-2.0, 2.01, 0.05):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1.0)
        r = cv2.warpAffine(s, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=0)
        pr = r.sum(axis=1).astype(np.float64)
        sc = float(((pr[1:] - pr[:-1]) ** 2).sum())
        if sc > best:
            best, ba = sc, a
    H, W = img.shape
    M = cv2.getRotationMatrix2D((W / 2, H / 2), ba, 1.0)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=255), ba


def prepared_img(n, pad=0.02):
    """Returns the image of the paper, deskewed and normalised."""
    g = cv2.imread(os.path.join(PAGES, 'f%04d.jpg' % n), cv2.IMREAD_GRAYSCALE)
    x0, y0, x1, y1 = paper_box(g)
    dx = int((x1 - x0) * pad); dy = int((y1 - y0) * pad)
    x0, y0 = x0 + dx, y0 + dy
    x1, y1 = x1 - dx, y1 - dy
    crop = g[y0:y1, x0:x1]
    crop = normalise_img(crop)
    crop, ang = deskew(crop)
    return crop, ang, (x0, y0, x1, y1)


def text_lines(img, frac=0.012):
    bw = (img < 150).astype(np.uint8)
    h, w = bw.shape
    m = int(0.02 * w)
    bw[:, :m] = 0; bw[:, w - m:] = 0
    bw[:int(0.01 * h), :] = 0; bw[int(0.99 * h):, :] = 0
    rows = bw.sum(axis=1)
    thr = max(4, rows.max() * frac)
    on = (rows > thr).astype(np.int8)
    d = np.diff(on)
    st = list(np.where(d == 1)[0] + 1); en = list(np.where(d == -1)[0] + 1)
    if on[0]: st.insert(0, 0)
    if on[-1]: en.append(len(on))
    lines = []
    for s, e in zip(st, en):
        if e - s < 10:
            continue
        seg = bw[s:e]
        c = seg.sum(axis=0)
        xs = np.where(c > 0)[0]
        if len(xs) == 0:
            continue
        lines.append({'y0': int(s), 'y1': int(e), 'x0': int(xs[0]), 'x1': int(xs[-1])})
    return lines, bw


def analysis(n):
    img, ang, box = prepared_img(n)
    lines, bw = text_lines(img)
    H, W = img.shape
    if not lines:
        return {'leaf': n, 'empty': True, 'img_w': W, 'img_h': H}
    x0 = min(l['x0'] for l in lines); x1 = max(l['x1'] for l in lines)
    # measure width: median of the "full" lines (>= 90 % of the max)
    widths = sorted(l['x1'] - l['x0'] for l in lines)
    full = [w for w in widths if w > 0.92 * widths[-1]]
    just = float(np.median(full)) if full else widths[-1]
    tops = [l['y0'] for l in lines]
    steps = np.diff(tops)
    steps = steps[(steps > 20) & (steps < 80)]
    return {
        'leaf': n, 'skew': round(ang, 2), 'paper_box': box,
        'img_w': W, 'img_h': H,
        'ink_x0': x0, 'ink_x1': x1,
        'just_px': round(just, 1), 'just_mm': round(just * PX2MM, 2), 'just_pt': round(just * PX2PT, 2),
        'n_lines': len(lines),
        'y_first': lines[0]['y0'], 'y_last': lines[-1]['y1'],
        'step_med': round(float(np.median(steps)), 2) if len(steps) else None,
        'step_pt': round(float(np.median(steps)) * PX2PT, 2) if len(steps) else None,
        'xh_med': round(float(np.median([l['y1'] - l['y0'] for l in lines])), 1),
    }


if __name__ == '__main__':
    res = {}
    for a in sys.argv[1:]:
        r = analysis(int(a))
        res[a] = r
        print(json.dumps(r), flush=True)
    with open(os.path.join(P, 'tools', 'crop_measures.json'), 'w') as fh:
        json.dump(res, fh, indent=1)
