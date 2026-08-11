#!/usr/bin/env python3
"""OCR grossier de toutes les pages, pour le RELEVE DE STRUCTURE seulement.

Le resultat n'est JAMAIS utilise tel quel pour placer une coupure de ligne :
il sert a reperer les folios, les titres et l'organisation du volume.
Chaque page est d'abord desinclinee et normalisee localement.
"""
import os, sys, subprocess, json
import numpy as np
import cv2

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(P, 'scan', 'pages')
OUT = os.path.join(P, 'scan', 'ocr')
os.makedirs(OUT, exist_ok=True)


def deskew_angle(bw):
    """Angle d'inclinaison estime par projection horizontale (variance max)."""
    small = cv2.resize(bw, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    best, ba = -1, 0.0
    h, w = small.shape
    for a in np.arange(-2.0, 2.01, 0.1):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1.0)
        r = cv2.warpAffine(small, M, (w, h), flags=cv2.INTER_NEAREST,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        proj = r.sum(axis=1).astype(np.float64)
        score = ((proj[1:] - proj[:-1]) ** 2).sum()
        if score > best:
            best, ba = score, a
    return ba


def prep(path):
    im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    # normalisation locale du contraste (papier jauni, ombre de reliure)
    bg = cv2.medianBlur(cv2.resize(im, None, fx=0.1, fy=0.1), 21)
    bg = cv2.resize(bg, (im.shape[1], im.shape[0]))
    norm = np.clip(im.astype(np.float32) / np.maximum(bg.astype(np.float32), 1) * 200, 0, 255)
    norm = norm.astype(np.uint8)
    bw = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    a = deskew_angle(bw)
    h, w = norm.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1.0)
    norm = cv2.warpAffine(norm, M, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    return norm, a


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 240
    meta = {}
    for n in range(lo, hi + 1):
        src = os.path.join(PAGES, 'f%04d.jpg' % n)
        if not os.path.exists(src):
            continue
        norm, a = prep(src)
        dst = os.path.join(OUT, 'f%04d.png' % n)
        cv2.imwrite(dst, norm)
        subprocess.run(['tesseract', dst, os.path.join(OUT, 'f%04d' % n),
                        '-l', 'eng', '--psm', '6'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        meta[n] = {'skew': round(float(a), 2)}
        print(n, a, flush=True)
    with open(os.path.join(OUT, 'meta_%d_%d.json' % (lo, hi)), 'w') as fh:
        json.dump(meta, fh)


if __name__ == '__main__':
    main()
