#!/usr/bin/env python3
"""Generator of a FIRST DRAFT, and measurement of its error rate.

The idea: produce the transcription mechanically, so that proofreading has
to VERIFY rather than to TYPE. Two components:

  * the line breaks come from the facsimile's line boxes, hence without
    OCR -- that is already reliable, as the checks show;
  * the TEXT of each line comes from a line-by-line OCR, each line being
    cut out and enlarged before being read.

Before trusting anything, we measure. The ten pages already transcribed by
hand serve as ground truth: we compare the automatic draft with that
transcription, line by line, and return the error rate per character. A
first draft whose error rate is unknown is worth no more than no first
draft at all.
"""
import os, sys, re, json, subprocess, unicodedata
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG
import cache
import checks as C

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(P, 'scan', 'jet')
os.makedirs(TMP, exist_ok=True)


def ocr_lines(leaf, margin=6, scale=3):
    """Line-by-line OCR: each box is cut out, enlarged, read on its own."""
    d = cache.leaf(leaf)
    norm, gm, ang = PG.prepared_img(leaf)
    H, W = norm.shape
    out = []
    for k, l in enumerate(d['lines']):
        y0 = max(0, l['y0'] - margin); y1 = min(H, l['y1'] + margin)
        x0 = max(0, l['x0'] - margin); x1 = min(W, l['x1'] + margin)
        sub = norm[y0:y1, x0:x1]
        if sub.size == 0:
            out.append('')
            continue
        sub = cv2.resize(sub, None, fx=scale, fy=scale,
                         interpolation=cv2.INTER_CUBIC)
        fp = os.path.join(TMP, 'l%04d_%03d.png' % (leaf, k))
        cv2.imwrite(fp, sub)
        subprocess.run(['tesseract', fp, fp[:-4], '--psm', '7', '-l', 'eng'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t = ''
        if os.path.exists(fp[:-4] + '.txt'):
            t = open(fp[:-4] + '.txt', encoding='utf-8', errors='replace').read()
        out.append(' '.join(t.split()))
        os.remove(fp)
    return out


def _norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('’', "'").replace('«', '<<').replace('»', '>>')
    s = s.replace('—', '--').replace('---', '--')
    return re.sub(r'\s+', ' ', s).strip()


def distance(a, b):
    """Levenshtein, for the error rate per character."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, that in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (that != cb)))
        prev = cur
    return prev[-1]


def measure(pages_ref):
    """Compares the automatic draft with the manual transcription, page by page."""
    total_d = total_n = 0
    for pg in pages_ref:
        f = pg.get('leaf')
        if not f:
            continue
        f = int(f)
        waiting = [_norm(l['text'] + ('-' if l['break'] == 'cc' else ''))
               for l in pg['lines'] if l['text']]
        got = [_norm(x) for x in ocr_lines(f)]
        # The folio is set by \VUfolio: it does not belong to the
        # transcription. Recognising it by the pattern of its text failed as
        # soon as the OCR read it badly -- and the whole page was then compared
        # one rank out, which gave 90 % error where the OCR made only three. We
        # therefore rely on the cached GEOMETRIC DETECTION.
        if cache.leaf(f).get('folio_detecte'):
            got = got[1:]
        n = min(len(waiting), len(got))
        d = sum(distance(waiting[k], got[k]) for k in range(n))
        c = sum(len(waiting[k]) for k in range(n))
        d += sum(len(waiting[k]) for k in range(n, len(waiting)))
        c += sum(len(waiting[k]) for k in range(n, len(waiting)))
        total_d += d; total_n += c
        print('  folio %-3s : %2d lines transcribed, %2d read — %5.1f %% error'
              % (pg['folio'] or ('f%s' % f), len(waiting), len(got),
                 100.0 * d / max(c, 1)), flush=True)
    print('\n  OVERALL ERROR RATE: %.1f %% per character (%d of %d)'
          % (100.0 * total_d / max(total_n, 1), total_d, total_n))
    return total_d / max(total_n, 1)


if __name__ == '__main__':
    pages = C.read_transcription()
    ref = [p for p in pages if p.get('leaf') and int(p['leaf']) >= 15]
    print('Measurement of the automatic first draft against the manual transcription:\n')
    measure(ref)
