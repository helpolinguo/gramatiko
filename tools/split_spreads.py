#!/usr/bin/env python3
"""Cuts the scan's images (double pages) into single pages.

PDF page 1        -> front cover (single image)
PDF pages 2..120  -> double pages (verso left + recto right)
PDF page 121      -> back cover (single image)

Output: scan/pages/f0001.png ... (sequential numbering of the leaves) with
scan/pages/index.tsv giving the correspondence.
"""
import os, sys, json
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(P, 'scan', 'raw')
OUT = os.path.join(P, 'scan', 'pages')
os.makedirs(OUT, exist_ok=True)


def find_gutter(gray):
    """Finds the column of the fold: the darkest at the centre of the image."""
    h, w = gray.shape
    band = gray[int(h * 0.15):int(h * 0.85), :]
    col = band.mean(axis=0)
    lo, hi = int(w * 0.40), int(w * 0.60)
    return lo + int(np.argmin(col[lo:hi]))


def main():
    files = sorted(f for f in os.listdir(RAW) if f.endswith('.jpg'))
    rows = []
    leaf = 0
    for i, fn in enumerate(files):
        im = Image.open(os.path.join(RAW, fn))
        w, h = im.size
        single = w < h  # portrait => single page
        if single:
            leaf += 1
            name = 'f%04d.jpg' % leaf
            im.save(os.path.join(OUT, name), quality=92, optimize=False)
            rows.append((name, fn, 'single', 0, w))
        else:
            g = np.asarray(im.convert('L'), dtype=np.float32)
            cut = find_gutter(g)
            for side, box in (('L', (0, 0, cut, h)), ('R', (cut, 0, w, h))):
                leaf += 1
                name = 'f%04d.jpg' % leaf
                im.crop(box).save(os.path.join(OUT, name), quality=92, optimize=False)
                rows.append((name, fn, side, box[0], box[2]))
        if i % 10 == 0:
            print(i, fn, flush=True)
    with open(os.path.join(OUT, 'index.tsv'), 'w') as fh:
        fh.write('leaf\tsource\tside\tx0\tx1\n')
        for r in rows:
            fh.write('\t'.join(str(x) for x in r) + '\n')
    print('total leaves:', leaf)


if __name__ == '__main__':
    main()
