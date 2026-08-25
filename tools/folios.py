#!/usr/bin/env python3
"""Survey of the printed folios.

Method: we crop to the paper, detect the lines of text, then OCR ONLY the
box of the first line (the folio is always alone on its line, centred, in
the form "-- 26 --").
"""
import os, re, sys, json, subprocess
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crop as C

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(P, 'scan', 'folio')
os.makedirs(TMP, exist_ok=True)

NUM = re.compile(r'\d{1,3}')


def analysis(n):
    img, ang, box = C.prepared_img(n, pad=0.005)
    lines, bw = C.text_lines(img)
    H, W = img.shape
    if not lines:
        return {'folio': None, 'raw': '', 'nlines': 0, 'blank': True}
    l0 = lines[0]
    # the folio is a short, centred line, in the first tenth
    width_of = l0['x1'] - l0['x0']
    cen = (l0['x0'] + l0['x1']) / 2 / W
    short = width_of < 0.30 * W
    high = l0['y0'] < 0.12 * H
    centered = 0.38 < cen < 0.62
    raw = ''
    val = None
    if short and high and centered:
        pad = 12
        sub = img[max(0, l0['y0'] - pad):l0['y1'] + pad,
                  max(0, l0['x0'] - pad):l0['x1'] + pad]
        sub = cv2.resize(sub, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        fp = os.path.join(TMP, 'f%04d.png' % n)
        cv2.imwrite(fp, sub)
        subprocess.run(['tesseract', fp, fp[:-4], '--psm', '7',
                        '-c', 'tessedit_char_whitelist=0123456789-— '],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tp = fp[:-4] + '.txt'
        if os.path.exists(tp):
            raw = open(tp, encoding='utf-8', errors='replace').read().strip()
        m = NUM.findall(raw.replace(' ', ''))
        if m:
            val = int(m[0])
    return {'folio': val, 'raw': raw.replace('\n', ' ')[:24],
            'nlines': len(lines), 'first_w': round(width_of / W, 3),
            'first_c': round(cen, 3), 'first_y': round(l0['y0'] / H, 3),
            'skew': ang, 'W': W, 'H': H}


if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    out = {}
    for n in range(lo, hi + 1):
        try:
            r = analysis(n)
        except Exception as e:
            r = {'folio': None, 'raw': 'ERR %s' % e}
        out[n] = r
        print(n, r.get('folio'), repr(r.get('raw', '')), r.get('nlines'), flush=True)
    with open(os.path.join(P, 'tools', 'folios_%d_%d.json' % (lo, hi)), 'w') as fh:
        json.dump(out, fh, indent=1)
