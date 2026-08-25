#!/usr/bin/env python3
"""Mesure la geometrie du bloc de texte et l'interlignage sur une page.

Toutes les mesures sont en pixels a 300 dpi, converties en millimetres
et en points TeX (1 pt = 1/72.27 in ; 300 px = 1 in).
"""
import os, sys, json
import numpy as np
import cv2

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(P, 'scan', 'pages')
DPI = 300.0
PX2MM = 25.4 / DPI
PX2PT = 72.27 / DPI          # points TeX
PX2BP = 72.0 / DPI           # points PostScript


def load_norm(n):
    im = cv2.imread(os.path.join(PAGES, 'f%04d.jpg' % n), cv2.IMREAD_GRAYSCALE)
    bg = cv2.medianBlur(cv2.resize(im, None, fx=0.1, fy=0.1), 21)
    bg = cv2.resize(bg, (im.shape[1], im.shape[0]))
    norm = np.clip(im.astype(np.float32) / np.maximum(bg.astype(np.float32), 1) * 200, 0, 255)
    return norm.astype(np.uint8)


def deskew(norm):
    bw = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    small = cv2.resize(bw, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    h, w = small.shape
    best, ba = -1, 0.0
    for a in np.arange(-2.0, 2.01, 0.05):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1.0)
        r = cv2.warpAffine(small, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=0)
        pr = r.sum(axis=1).astype(np.float64)
        s = ((pr[1:] - pr[:-1]) ** 2).sum()
        if s > best:
            best, ba = s, a
    H, W = norm.shape
    M = cv2.getRotationMatrix2D((W / 2, H / 2), ba, 1.0)
    return cv2.warpAffine(norm, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=255), ba


def analyse(n, verbose=True):
    norm = load_norm(n)
    norm, ang = deskew(norm)
    H, W = norm.shape
    bw = (norm < 150).astype(np.uint8)
    # ignore les bords (ombre de reliure, tranche)
    m = int(0.03 * W)
    bw[:, :m] = 0
    bw[:, W - m:] = 0
    rows = bw.sum(axis=1)
    cols = bw.sum(axis=0)
    thr_r = max(3, rows.max() * 0.02)
    thr_c = max(3, cols.max() * 0.02)
    ys = np.where(rows > thr_r)[0]
    xs = np.where(cols > thr_c)[0]
    if len(ys) == 0:
        return None
    # lignes de texte : segments contigus de rows > seuil
    onoff = (rows > thr_r).astype(np.int8)
    d = np.diff(onoff)
    starts = list(np.where(d == 1)[0] + 1)
    ends = list(np.where(d == -1)[0] + 1)
    if onoff[0]: starts.insert(0, 0)
    if onoff[-1]: ends.append(len(onoff))
    lines = [(s, e) for s, e in zip(starts, ends) if e - s >= 8]
    base = [(s + e) / 2 for s, e in lines]
    steps = np.diff(base) if len(base) > 1 else np.array([])
    res = {
        'leaf': n, 'skew': round(float(ang), 3),
        'img_w': W, 'img_h': H,
        'ink_x0': int(xs[0]), 'ink_x1': int(xs[-1]),
        'ink_y0': int(ys[0]), 'ink_y1': int(ys[-1]),
        'block_w_px': int(xs[-1] - xs[0] + 1),
        'block_w_mm': round((xs[-1] - xs[0] + 1) * PX2MM, 2),
        'n_lines': len(lines),
        'line_h_med': float(np.median([e - s for s, e in lines])) if lines else 0,
        'lines': [[int(s), int(e)] for s, e in lines],
    }
    if len(steps):
        med = float(np.median(steps))
        res['step_med_px'] = round(med, 2)
        res['step_med_pt'] = round(med * PX2PT, 2)
        res['steps'] = [round(float(x), 1) for x in steps]
    if verbose:
        print(json.dumps({k: v for k, v in res.items() if k not in ('lines', 'steps')}, indent=1))
    return res


if __name__ == '__main__':
    out = {}
    for n in [int(x) for x in sys.argv[1:]]:
        r = analyse(n)
        if r: out[n] = r
    with open(os.path.join(P, 'tools', 'measures.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
