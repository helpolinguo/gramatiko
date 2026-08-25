#!/usr/bin/env python3
"""ATTEMPT REFUTED -- screening for weight by the thickness of the stems.

    THIS PROGRAM DOES NOT WORK. It is kept so that the attempt is not made
    again, and because a failed screening documents itself as a successful
    one does.

Run over the 46 composed pages, it reported 313 lines, the first of them
at folio 12 -- a page verified three times and confirmed by the reader.
These are not 313 errors, it is a systematic false positive.

The cause is measurable. The thickness of the stem takes, at 300 dpi, only
two useful values: 3 or 4 pixels. The per-page distributions show it --
median 3 to 4, ninth decile 4.0, and that on pages one of which is almost
wholly roman and the other heavy with bold. By oversampling the band by a
factor of 4 before measuring, one gains a little finesse but not enough: at
folio 51, the bold words return 4.00 and the roman 3.75, a quarter of a
pixel apart.

What the tool can do all the same, and what remains useful, is to COMPARE
TWO NEIGHBOURING CLUSTERS ON THE SAME LINE: the same ink, the same paper,
the same instant of scanning. That is how it settled the weight of the
cited verbs of folio 51. See tools/weight.py, which keeps that use. What it
cannot do is judge a line in the absolute, nor compare two pages with each
other.

Screening at the scale of the volume therefore remains to be invented.
Check 9, which compares the ink of MY line with that of the model, is the
right principle -- the same measurement on both sides -- and its weakness
lies elsewhere: its matching slips as soon as a short line is missing from
the transcription.

Description of the attempt:

Confronts the WEIGHT surveyed with the weight composed, page by page.

Three errors of weight reported in six rounds: there are probably more.
Rather than wait to be shown them, we measure.

For each line of the facsimile, we cut the band into clusters and measure
the stem thickness of each (tools/weight.py). From that we get the share of
bold clusters. From the transcription, we get the share of CHARACTERS
enclosed in a \\VUgras. The two shares should agree; when they differ by
more than a third, the line is reported.

This is not one more check: it is a screening, and it returns false
positives. Two known causes:

  * a line that crosses a fold in the paper or the shadow of the binding
    has all its stems thickened, and the tool declares it bold from end to
    end. The sign is a UNIFORM verdict over the whole line;
  * clusters are not words: the comma following a bold word agglomerates
    to it, an isolated ":" gives a stem of 5 px.

We therefore return both shares and the detail, for the eye to settle.

    python3 tools/weight_sweep.py          # every page
    python3 tools/weight_sweep.py 51 54    # these folios
"""
import os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG
import cache
import checks as C
import weight

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Below this gap, measurement and transcription agree well enough.
TOLERANCE = 0.34
# A line of fewer than six clusters is not judged: too few samples.
MIN_CLUSTER = 6


def bold_share_surveyed(raw):
    """Share of the text's characters enclosed in a \\VUgras."""
    strip_stray = C.plain_text(raw.replace('\x02', '').replace('\x03', '')
                     .replace('\x04', '')).strip()
    if not strip_stray:
        return None
    bold = 0
    i = 0
    while True:
        j = raw.find('\\VUgras', i)
        if j < 0:
            break
        k = raw.find('{', j)
        if k < 0:
            break
        depth = 0
        m = k
        while m < len(raw):
            if raw[m] == '{' and raw[m - 1] != '\\':
                depth += 1
            elif raw[m] == '}' and raw[m - 1] != '\\':
                depth -= 1
                if depth == 0:
                    break
            m += 1
        bold += len(C.plain_text(raw[k + 1:m]).strip())
        i = m + 1
    return min(1.0, bold / max(len(strip_stray), 1))


def sweep(folios=None, ratio=True):
    pages = C.read_transcription()
    suspect_lines = []
    for pg in pages:
        fo = pg['folio'] or ('f' + (pg.get('leaf') or '?'))
        if folios and fo not in folios:
            continue
        try:
            leaf = int(pg['leaf']) if pg['leaf'] else int(pg['folio']) + 4
        except (ValueError, TypeError):
            continue
        fl = cache.leaf(leaf)['lines']
        lg = [l for l in pg['lines'] if l['text']]
        dec = 1 if (fl and fl[0]['x1'] - fl[0]['x0']
                    < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
        if len(lg) + dec != len(fl):
            continue                       # diverging counts: we pass
        for i, l in enumerate(lg):
            if l.get('note') or l.get('apparat') or l.get('rang'):
                continue                   # running text only
            f = fl[i + dec]
            cluster = weight.line(leaf, f['y0'], f['y1'] + 1)
            if len(cluster) < MIN_CLUSTER:
                continue
            mes = sum(1 for _, _, w, _ in cluster if w >= weight.THRESHOLD) / len(cluster)
            rel = bold_share_surveyed(l['brut'])
            if rel is None:
                continue
            if abs(mes - rel) > TOLERANCE:
                suspect_lines.append((fo, i + 1, mes, rel, l['text'][:52],
                                  all(w >= weight.THRESHOLD for _, _, w, _ in cluster)))
    if ratio:
        print('%d suspect line(s):\n' % len(suspect_lines))
        for fo, k, mes, rel, t, uniform in suspect_lines:
            print('  folio %-4s line %2d: measured %3.0f %% bold, transcribed %3.0f %%%s'
                  % (fo, k, 100 * mes, 100 * rel,
                     '   [verdict UNIFORME : pli probable]' if uniform else ''))
            print('        %s' % t)
    return suspect_lines


if __name__ == '__main__':
    sweep(set(sys.argv[1:]) or None)
