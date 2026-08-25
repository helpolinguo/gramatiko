#!/usr/bin/env python3
"""Sets the ordinate of the note block against that of the facsimile.

The ordinate passed to \\VUnotes is first estimated from the RULE, surveyed
by tools/rule.py. The rule is a pale 0.4 pt stroke: according to the
threshold and the closing used, one lands on its first dark row or on its
middle, and the whole block shifts by 1 to 3 mm. Measured on the composed
pages: the gap between notes and body ran from -26 to +33 px from one page
to another. It is therefore not an error of formula, but the noise of the
rule survey, page by page.

We correct it on what measures well: the BASELINES of the notes. The mean
gap between the composed notes and the facsimile's notes, once the body's
gap is taken off, is subtracted from the ordinate.

    python3 tools/align_notes.py            # measures, writes nothing
    python3 tools/align_notes.py --write     # writes
"""
import os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache
import checks as C

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX2MM = 25.4 / 300.0
# Under 4 px (0.34 mm) the correction is below the noise of the division
# into lines: we leave it alone.
THRESHOLD_PX = 4.0


def gaps():
    """{folio: (gap_px, file)} for the pages with measurable notes."""
    pages = C.read_transcription()
    comp = cache.compose(os.path.join(P, 'main.pdf'), len(pages))
    out = {}
    for i, pg in enumerate(pages, 1):
        fo = pg['folio']
        if not fo.isdigit() or i not in comp:
            continue
        leaf = int(pg['leaf']) if pg['leaf'] else int(fo) + 4
        cl = comp[i]['lines']
        fl = cache.leaf(leaf)['lines']
        if not fl or len(cl) != len(fl):
            continue
        lg = [l for l in pg['lines'] if l['text']]
        dec = 1 if (fl[0]['x1'] - fl[0]['x0']
                    < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
        if len(lg) + dec != len(fl):
            continue
        note = np.array([False] * dec + [bool(l.get('note')) for l in lg])
        body = ~note
        body[:dec] = False
        if note.sum() < 3 or body.sum() < 3:
            continue
        d = np.array([c['y0'] - a['y0'] for a, c in zip(fl, cl)], float)
        out[fo] = (float(d[note].mean() - d[body].mean()), pg['fichier'])
    return out


def apply_at(write_out=False):
    n = 0
    for folio, (e, file_path) in sorted(gaps().items(), key=lambda t: int(t[0])):
        mark = '' if abs(e) < THRESHOLD_PX else '  <-- to set'
        print('folio %-4s notes/body gap %+6.1f px = %+5.2f mm%s'
              % (folio, e, e * PX2MM, mark))
        if abs(e) < THRESHOLD_PX or not write_out:
            continue
        fp = os.path.join(P, 'content', file_path)
        src = open(fp, encoding='utf-8').read()
        m = re.search(r'(\\begin\{VUpage\}(?:\[[^\]]*\])?\{%s\}.*?'
                      r'\\VUnotes\{)([0-9.]+)mm(\})' % re.escape(folio),
                      src, re.S)
        if not m:
            print('        (no \\VUnotes on this page)')
            continue
        fresh = float(m.group(2)) - e * PX2MM
        src = src[:m.start(2)] + ('%.2f' % fresh) + src[m.end(2):]
        open(fp, 'w', encoding='utf-8').write(src)
        print('        %s mm -> %.2f mm' % (m.group(2), fresh))
        n += 1
    if write_out:
        print('%d page(s) aligned; recompile and re-run to converge.' % n)


if __name__ == '__main__':
    apply_at('--write' in sys.argv)
