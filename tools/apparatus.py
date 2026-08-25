#!/usr/bin/env python3
"""Calibration of the APPARATUS LINES (titles, half-title, part titles).

A title line is defined by two measurements taken on the facsimile:
  * the cap height    -> gives the TYPE SIZE;
  * the width of ink  -> gives the LETTER-SPACING, once the size is known.

The size is deduced from the cap height because these lines are wholly in
capitals: there is no x-height to measure.

Usage:
    python3 tools/apparatus.py <leaf>
        -> lists the page's lines with their raw measurements
    python3 tools/apparatus.py <leaf> --rule "TEXT OF THE LINE" <index>
        -> computes size and letter-spacing for that line
"""
import os, sys, re, json, subprocess
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX2MM, PX2PT = PG.PX2MM, PG.PX2PT

# Cap-height / type-size ratios, measured by tools/fonts.tex.
CAP_OVER_SIZE = {'XCharter-TLF': 0.680}


def apparatus_lines(n, width_threshold=0.03):
    """Like page.block, but without rejecting short lines: on a title page,
    "DI LA" is a line in its own right."""
    norm, gm, ang = PG.prepared_img(n)
    H, W = gm.shape
    band = cv2.morphologyEx(gm, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_RECT, (61, 3)))
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(
        (band > 0).astype(np.uint8), 8)
    keep = np.zeros((H, W), np.uint8)
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        if w < width_threshold * W or h > 0.10 * H or w / max(h, 1) < 1.2:
            continue
        # we discard the fore-edges: they cling to the edge of the image
        if x < 0.02 * W or x + w > 0.98 * W:
            continue
        keep[lab == i] = 1
    gm2 = gm * keep
    return PG.lines_of(gm2, min_ink=3), norm, gm2


def cap_height(gm2, y0, y1):
    """Mode of the glyph heights on the band [y0,y1]: the title lines being
    wholly in capitals, this is the cap height."""
    sub = (gm2[y0:y1] > 0).astype(np.uint8)
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(sub, 8)
    hs = [stats[i][3] for i in range(1, nlab) if stats[i][4] >= 20]
    if not hs:
        return None
    return float(np.median(hs))


def natural_width(text, body_pt, font='XCharter-TLF', bold=False):
    """Width of the composed text without letter-spacing, in TeX points."""
    tex = r"""\documentclass{article}\usepackage[T1]{fontenc}\usepackage{XCharter}
\newlength{\Wq}\begin{document}\pagestyle{empty}
\fontfamily{%s}\fontsize{%.3fpt}{%.3fpt}\selectfont%s
\settowidth{\Wq}{%s}\typeout{LARGEUR=\the\Wq}\mbox{}\end{document}""" % (
        font, body_pt, body_pt, '\\bfseries' if bold else '', text)
    d = os.path.join(P, 'tools', '.tmp')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'w.tex'), 'w') as fh:
        fh.write(tex)
    subprocess.run(['pdflatex', '-interaction=nonstopmode', 'w.tex'],
                   cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = open(os.path.join(d, 'w.log'), encoding='utf-8', errors='replace').read()
    m = re.search(r'LARGEUR=([\d.]+)pt', log)
    return float(m.group(1)) if m else None


def rule_of(text, width_px, cap_px, font='XCharter-TLF', bold=False):
    """Type size and letter-spacing (in 1/1000 em, microtype's unit)."""
    body = cap_px * PX2PT / CAP_OVER_SIZE[font]
    target = width_px * PX2PT
    nat = natural_width(text, body, font, bold)
    if nat is None:
        return None
    # microtype adds <t>/1000 em after EACH character; on a centred line,
    # the last addition is taken back by \textls.
    n = max(len(text) - 1, 1)
    track = (target - nat) / (body * n) * 1000.0
    return {'text': text, 'gras': bold, 'corps_pt': round(body, 2),
            'largeur_cible_pt': round(target, 2), 'largeur_nue_pt': round(nat, 2),
            'interlettrage': int(round(track)),
            'cap_mm': round(cap_px * PX2MM, 3),
            'largeur_mm': round(width_px * PX2MM, 2)}


if __name__ == '__main__':
    n = int(sys.argv[1])
    lines, norm, gm2 = apparatus_lines(n)
    if '--rule' not in sys.argv:
        print('leaf %d — %d lines' % (n, len(lines)))
        for k, l in enumerate(lines):
            cap = cap_height(gm2, l['y0'], l['y1'])
            print('  [%d] y=%4d  width=%4d px (%.2f mm)  cap=%s px (%.3f mm)'
                  % (k, l['y0'], l['x1'] - l['x0'], (l['x1'] - l['x0']) * PX2MM,
                     cap, (cap or 0) * PX2MM))
    else:
        i = sys.argv.index('--rule')
        text = sys.argv[i + 1]
        k = int(sys.argv[i + 2])
        l = lines[k]
        cap = cap_height(gm2, l['y0'], l['y1'])
        bold = '--bold' in sys.argv
        print(json.dumps(rule_of(text, l['x1'] - l['x0'], cap, bold=bold),
                         ensure_ascii=False, indent=1))
