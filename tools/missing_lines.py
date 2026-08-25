#!/usr/bin/env python3
"""Screens for the facsimile lines the detector does not see.

    TO BE RUN OVER A WHOLE BATCH BEFORE COMPOSING, never after.

Six lines escaped the detector in twenty-four pages: "homi." (f69),
"kazo." (f80), "yare." (f84), "longa." (f85), "pos til." (f86), "pro li."
(f91). All short, all at the end of a paragraph, all too pale to cross
the ink threshold. I found them one by one, by eye, re-reading the bands
-- a method that works and cannot be verified.

Yet they announce themselves, and by a simple measurement.

    A DOUBLE PITCH IS NOT A WHITE SPACE.

The volume's current pitch is 41.5 px. A pitch of 82.8 px where the
regular pitch is 41.5 is not a white space of 41.3 px: it is A MISSING
LINE followed by an ordinary pitch. The criterion is nearness to the
DOUBLE: |d - 2p| small, and not |d - p| large.

THIS CRITERION ALONE DOES NOT SUFFICE, and it had to be measured to
notice. Run over the six known cases, it finds only three. The other
three -- "kazo." (f80), "longa." (f85) -- carry a WHITE SPACE after the
missing line: their pitch is 105.9 px, neither p nor 2p, and the test
lets it through. And "homi." (f69) is in the NOTES, whose pitch is
34.6 px and not 41.5: the double to look for is not the same.

Hence the form adopted. The regular pitch is measured LOCALLY, on either
side of the rule, and any pitch greater than one and a half times that
local pitch is reported with BOTH ITS READINGS: "white space of x px" and
"missing line plus white space of y px". The tool does not decide -- it
cannot, both readings being sometimes plausible -- but it no longer lets
anything past in silence. The eye decides, at the facsimile, and it now
knows where to look.

Two precautions, drawn from the real cases:

  * the pitch that crosses the notes' RULE is 60 to 155 px without
    anything being missing. We exclude it by locating the rule
    (tools/rule.py);
  * the pitch descending from the folio to the first line is not a body
    pitch; it is excluded as in tools/carding.py.

What is left is reported with the ordinate at which to look for the
absent line, so that one can go and read it in the facsimile.

A PITCH IS MEASURED BETWEEN TWO LINES, SO THE LAST ONE ESCAPES THE TEST.
"pos til." (f86) is the last line of its page: nothing follows it, no
pitch betrays it. It is seen otherwise -- by the INK REMAINING BELOW the
last line detected. Measured on the batch's six leaves: 866 px where it
is missing, 4 to 65 px everywhere else (descenders and dust). The
threshold is set at 200 px, well clear on both sides.

WHAT IT IS WORTH, MEASURED.

  * on the six leaves where a line really is missing (69, 80, 84, 85, 86,
    91), it finds ALL SIX;
  * on six sound leaves already composed and verified (70 to 75), it
    reports seven pitches -- seven false positives.

It is therefore not a verdict but a SCREENING: it reduces the search from
"re-read every line of every page" to "check one place per page". The
verdict "clean double, no white space" has always proved right; the "two
readings" are to be settled by eye.

    python3 tools/missing_lines.py 86 87 88 89 90 91
    python3 tools/missing_lines.py --all        # all 240 leaves
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baselines as LB
import rule as FI

PX2MM = 25.4 / 300.0


class RuleNotFound(Exception):
    """The notes' rule was not found: the local pitch is doubtful."""
    def __str__(self):
        return ('notes\u2019 rule not found — the local pitch would mix '
                'body and notes; leaf not screened')
# Beyond this ratio to the local pitch, the pitch is reported. 1.5 lets
# the ordinary white spaces through (up to 1.4 p) and catches everything
# that could hide a line.
MIN_RATIO = 1.5
# Margin around the exact double: within it, the reading "missing line
# with no white space" is the only plausible one and we say so.
TOLERANCE = 4.5
# A WHITE SPACE CANNOT BE NEGATIVE. If d - 2p falls clearly below zero,
# the reading "missing line + white space" would require a negative white
# space: it is impossible, and the pitch is only an ordinary white space.
# Without this guard the tool reported twenty-two pitches for six leaves,
# nineteen of them with a "white space" of -13 to -18 px -- pure noise.
MIN_WHITE = -3.0
# Ink tolerated below the last line detected: descenders and dust.
MAX_TAIL_INK = 200
TAIL_HEIGHT = 70          # px scanned below the last line
# A line of text fits in a single band of rows. We require that
# TAIL_CONCENTRATION of the tail ink fall within TAIL_WINDOW consecutive
# rows: 0.95 measured on the real line of leaf 86, 0.63 on the foxing of
# leaf 105.
TAIL_WINDOW = 30
TAIL_CONCENTRATION = 0.85
# ONE BAND MAY HIDE TWO, ON THE FACSIMILE SIDE AS WELL. The same fault
# as the one repaired in cache.compose: when a descender touches the
# ascender of the next line, no row is empty and the two lines make only
# one. On leaf 97, the final band measures 57 px for a median of 27 -- it
# carries the last two lines of note (17). Neither the double pitch nor
# the tail ink sees it: the pitch counts it as one, and nothing follows
# it. We report any band appreciably taller than the local median.
BAND_RATIO = 1.7


def tail(leaf):
    """Ink remaining below the last line detected, in dark pixels.

    INK ALONE DOES NOT SUFFICE: it must be ORGANISED INTO A LINE. On leaf
    105 the lower margin is speckled with foxing -- 907 px of scattered
    dots, beyond the threshold of 200 -- and the test announced a missing
    last line where there is nothing but dust.
    The right criterion is not the QUANTITY of ink -- 868 px where the
    line exists (f86), 907 where there is only foxing (f105): the two are
    equal. Nor is it the peak per row: the foxing gives 125 against the
    real line's 56, hence the wrong way round.
    It is the VERTICAL CONCENTRATION. A line of text fits in a single band
    of rows: 95 % of its ink falls within 30 consecutive rows. The foxing
    covers the whole margin -- only 63 %. The threshold is set at 0.85,
    well clear on both sides.
    """
    import page as PG
    import numpy as np
    norm, gm, _ = PG.prepared_img(leaf)
    gm2, span = PG.text_region(gm)
    fl = LB.analysis(leaf, verbose=False)[0]
    if not fl or span is None:
        return 0
    y_bottom = fl[-1]['y1']
    band = (norm[y_bottom + 6:y_bottom + 6 + TAIL_HEIGHT, span[0]:span[1]] < 175)
    if not band.size or not band.sum():
        return 0
    rows_of = band.sum(axis=1)
    total = int(band.sum())
    if len(rows_of) <= TAIL_WINDOW:
        return total
    dense = max(int(rows_of[i:i + TAIL_WINDOW].sum())
                for i in range(len(rows_of) - TAIL_WINDOW))
    if dense < TAIL_CONCENTRATION * total:
        return 0
    return total


def welded_bands(leaf):
    """[(rank, height, median height)] of the bands carrying two lines."""
    fl = LB.analysis(leaf, verbose=False)[0]
    if len(fl) < 8:
        return []
    h = [l['y1'] - l['y0'] for l in fl]
    med = float(np.median(h))
    if med <= 0:
        return []
    return [(k, h[k], med) for k in range(1, len(fl))
            if h[k] >= BAND_RATIO * med]


def suspects(leaf):
    """[(rank, pitch, regular pitch, ordinate at which to look)]"""
    fl, bs, _ = LB.analysis(leaf, verbose=False)
    if len(fl) < 6:
        return []
    folio = fl[0]['x1'] - fl[0]['x0'] < 0.25 * max(l['x1'] - l['x0'] for l in fl)
    pitch = []
    for k in range(1, len(bs)):
        if bs[k] is None or bs[k - 1] is None:
            continue
        if folio and k == 1:
            continue
        pitch.append((k, bs[k] - bs[k - 1]))
    f = FI.find_rule(leaf)
    y_rule = f[0] if f else None
    # WITHOUT THE RULE, THE LOCAL PITCH IS NOT MEASURABLE, and that must be
    # said. tools/rule.py fails on a few leaves (93, 97 among others). The
    # local pitch then fell back on the median of the WHOLE page, which on a
    # page heavy with notes is 33 px and not 41.5: the tool read "local pitch
    # 33.1" for lines of body text and announced three missing lines that did
    # not exist. A false measurement returned without warning is worth less
    # than no measurement at all.
    if y_rule is None:
        bloc = [d for _, d in pitch if 30.0 < d < 48.0]
        if bloc and max(bloc) - min(bloc) > 5.0:
            raise RuleNotFound(leaf)

    def local_pitch(k):
        """Regular pitch of the BLOCK in which line k falls: body or notes.

        The block of notes is set at 34.6 px, the body at 41.5. Judging a
        note line by the body's pitch made "homi." on folio 65 be missed,
        whose double pitch is 69 px and not 83.
        """
        if y_rule is None:
            same_ones = [d for j, d in pitch if 30.0 < d < 48.0]
        else:
            before = bs[k - 1] < y_rule
            same_ones = [d for j, d in pitch if 30.0 < d < 48.0
                     and (bs[j - 1] < y_rule) == before]
        if len(same_ones) < 4:
            same_ones = [d for _, d in pitch if 30.0 < d < 48.0]
        return float(np.median(same_ones)) if same_ones else None

    out = []
    for k, d in pitch:
        # the pitch that crosses the notes' rule is not judged: it is 60 to
        # 155 px without anything whatever being missing.
        if y_rule is not None and bs[k - 1] < y_rule < bs[k]:
            continue
        p = local_pitch(k)
        if p is None or d < MIN_RATIO * p:
            continue
        if d - 2 * p < MIN_WHITE:
            continue
        out.append((k, d, p, bs[k - 1] + p, abs(d - 2 * p) <= TOLERANCE))
    return out


def ratio(leaves):
    total = 0
    doubtful = 0
    for n in leaves:
        try:
            s = suspects(n)
        except RuleNotFound as e:
            print('leaf %-4d folio %-4d : %s' % (n, n - 4, e))
            doubtful += 1
            continue
        except Exception as e:
            print('leaf %d: %s' % (n, e))
            continue
        for k, d, p, y, strip_stray in s:
            total += 1
            if strip_stray:
                print('leaf %-4d folio %-4d line %2d: pitch %.1f px for a '
                      'local pitch of %.1f — MISSING LINE about y = %.0f px '
                      '(clean double, no white space)' % (n, n - 4, k, d, p, y))
            else:
                print('leaf %-4d folio %-4d line %2d: pitch %.1f px for a '
                      'local pitch of %.1f\n        two readings: white space of '
                      '%.1f px  OR  missing line about y = %.0f px + white space '
                      'of %.1f px' % (n, n - 4, k, d, p, d - p, y, d - 2 * p))
        try:
            q = tail(n)
        except Exception:
            q = 0
        try:
            for k, h, med in welded_bands(n):
                total += 1
                print('leaf %-4d folio %-4d line %2d: band of %d px for '
                      'a median of %.0f — TWO WELDED LINES probable'
                      % (n, n - 4, k, h, med))
        except Exception:
            pass
        if q > MAX_TAIL_INK:
            total += 1
            print('leaf %-4d folio %-4d : %d px of ink BELOW the last '
                  'line detected — LAST LINE MISSING probable'
                  % (n, n - 4, q))
    print('\n%d probable missing line(s) over %d leaf/leaves%s.'
          % (total, len(leaves),
             ', %d not screened for want of a rule' % doubtful if doubtful else ''))
    if total:
        print('Read them in the facsimile BEFORE composing: a line absent '
              'from the body shifts every following boundary, and\n'
              'tools/apply_carding.py would apply each white space one line '
              'too high without reporting anything.')
    return total


if __name__ == '__main__':
    if '--all' in sys.argv:
        ratio(range(5, 241))
    else:
        ratio([int(a) for a in sys.argv[1:] if not a.startswith('--')])
