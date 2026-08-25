#!/usr/bin/env python3
"""Measurement of the VERTICAL JUSTIFICATION of a facsimile page.

The compositor justifies his pages vertically. Measured on leaves 20 to
39: the last baseline falls 145.3 mm below the folio, to within 0.3 mm,
whatever the number of lines on the page. When the matter does not fill
the measure, he distributes the surplus:

  -- uniform leads between all the lines of the body, which takes the
     pitch from 41.45 px (the current leading, 9.88 pt) to the value
     proper to the page;
  -- wider white space at the articulations: end of paragraph, opening of
     an enumeration, resumption of the discourse after examples.

This tool returns both: the page's regular pitch, and the list of pitches
that exceed it, with the excess to be entered in a \\VUblanc.

It works on the BASELINES, never on the tops of lines: the top depends on
the line's ascenders and is noisy to +/- 8 px, enough to drown a white
space of a point and a half.

    python3 tools/carding.py 34
    python3 tools/carding.py 34 35 36
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baselines as LB

PX2PT = 72.27 / 300.0
# Current pitch of the volume, measured on leaves 20, 24, 30, 32, 37, 38:
# 41.3 to 41.6 px. That is \VUinterligne = 9.88 pt.
CURRENT_PITCH = 41.45
# A note pitch is 32.8 px: anything below 38 px belongs to the block of
# notes, which is not vertically justified (it is set separately by
# \VUnotes) and must not enter the median of the body.
MAX_NOTE_PITCH = 38.0


def measure(leaf):
    """(regular pitch of the body, list of excesses, lines, baselines)."""
    fl, bs, _ = LB.analysis(leaf, verbose=False)
    pitch = []
    for k in range(1, len(bs)):
        if bs[k] is None or bs[k - 1] is None:
            continue
        pitch.append((k, bs[k] - bs[k - 1]))
    # The pitch descending from the FOLIO to the first line of the body is
    # not an articulation: it is fixed by the top margin, not by a
    # paragraph space. Counted as one, it announced an excess of 48 px
    # "before line 1", and the white space set in consequence moved the
    # page away from its model instead of towards it (folio 13: the drift
    # went from 26 to 58 px).
    folio = bool(fl) and (fl[0]['x1'] - fl[0]['x0']
                          < 0.25 * max(l['x1'] - l['x0'] for l in fl))
    if folio:
        pitch = [(k, d) for k, d in pitch if k > 1]
    body = [d for _, d in pitch if MAX_NOTE_PITCH < d < 48.0]
    if not body:
        return None, [], fl, bs
    reg = float(np.median(body))
    excess = []
    for k, d in pitch:
        # We keep only the pitches of the body: a pitch that follows a note
        # line, or that crosses the rule, is not vertically justified.
        if d <= MAX_NOTE_PITCH or d > 130.0:
            continue
        e = d - reg
        if e > 3.0:                      # 3 px = 0.7 pt: below the noise
            excess.append((k, d, e))
    return reg, excess, fl, bs


def ratio(leaf):
    reg, excess, fl, bs = measure(leaf)
    if reg is None:
        print('leaf %d: no measurable body' % leaf)
        return
    print('=== leaf %d: %d lines' % (leaf, len(fl)))
    print('    regular pitch of the body: %.2f px = %.2f pt%s'
          % (reg, reg * PX2PT,
             '' if abs(reg - CURRENT_PITCH) < 0.6 else '   <-- PAGE VERTICALLY JUSTIFIED'))
    if abs(reg - CURRENT_PITCH) >= 0.6:
        print('    -> \\VUinterlignePage{%.2fpt}' % (reg * PX2PT))
    if not excess:
        print('    no articulation white space')
        return
    print('    articulation white space (excess over the regular pitch):')
    for k, d, e in excess:
        larg = fl[k - 1]['x1'] - fl[k - 1]['x0']
        full_line = np.percentile([l['x1'] - l['x0'] for l in fl], 80)
        end_pos = 'end of paragraph' if larg < 0.97 * full_line else 'full line'
        print('      before line %2d: pitch %.1f px, excess %.1f px '
              '= \\VUblanc{%.2fpt}   (%s above)'
              % (k, d, e, e * PX2PT, end_pos))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        ratio(int(a))
