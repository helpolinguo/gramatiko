#!/usr/bin/env python3
"""Detection of the NOTE RULE, and computation of its typeset ordinate.

Locating the rule by "the largest white space on the page" does not work:
on a page carrying a section heading, the heading's white space is larger,
and the block of notes is then placed centimetres too high.

The rule is an object recognisable in itself: a continuous horizontal
stroke, one to three pixels tall, some twenty millimetres long, set on the
left margin, and alone on its line. We therefore look for it as such, in
the lower half of the page.

The ordinate returned is the one \\VUnotes expects, that is a distance from
the TOP EDGE OF THE PAPER. It cannot be read directly from the scan: each
scanned image has its own vertical offset, the paper not occupying the same
place in it. We therefore compute it relative to the first line of the
body, which we know falls at \\VUmargeSup:

    ordinate = VUmargeSup + (y_rule - y_first_line) x 25.4/300
"""
import os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

VU_TOP_MARGIN_MM = 24.30      # must follow \VUmargeSup from the preamble


def find_rule(leaf, verbose=False):
    """Returns (y_rule, width_px) or None."""
    norm, gm, ang = PG.prepared_img(leaf)
    H, W = norm.shape
    dark = (norm < 185).astype(np.uint8)
    # A scanned rule is rarely continuous: a few light pixels cut it here and
    # there (at folio 11, the break was enough to make it be missed). We
    # therefore weld interruptions of at most three pixels.
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE,
                              np.ones((1, 7), np.uint8))
    # text column, so as to know where the left margin begins
    gm2, span = PG.text_region(gm)
    if span is None:
        return None
    x0 = span[0]
    best = None
    # THE SEARCH WINDOW BEGAN TOO LOW. Fixed at 0.45 H, it assumed that the
    # block of notes occupies at most the lower half of the page. That is
    # true of nearly all of them, but not of leaf 97, whose rule falls at
    # 0.29 H (the page is three-quarters notes), nor of 93, at 0.40 H. On
    # those two the detector returned "rule not found" -- and
    # tools/missing_lines.py, deprived of the rule, mixed the pitch of the
    # body with that of the notes.
    #
    # Widening the CLOSING from 7 to 11 px found them too, but returned FALSE
    # rules: y=1680, 140 px long on leaf 93 where the real one is at 782 with
    # its regulation 213 px. A welded line of text passed for a rule. We
    # therefore rejected that remedy -- a detector that goes wrong in silence
    # is worth less than one that fails.
    # THE WINDOW STARTED TOO LOW -- the third cause of "rule not found".
    # Fixed at 0.25 H, it assumed the block of notes occupies at most the
    # lower three quarters. That is false as soon as the page is lightly
    # filled: on leaf 180, which closes the second part, the rule falls at
    # y = 377 for a window starting at 520; on leaf 194 it is at 450 for a
    # window starting at 516. In both cases the rule passes the tests of
    # length and of remainder -- it is never examined.
    # We therefore go down to 0.10 H. Checked on twenty-two sample leaves: no
    # rule already found is lost or displaced.
    for y in range(int(0.10 * H), int(0.95 * H)):
        line = dark[y]
        # We look for the first dark pixel NEAR the margin, then the length of
        # the continuous segment starting from it. Beginning the count at a fixed
        # abscissa did not work: a few white pixels before the rule were enough
        # to give a length of zero.
        fen = line[max(0, x0 - 15):x0 + 40]
        nz = np.nonzero(fen)[0]
        if nz.size == 0:
            continue
        start_at = max(0, x0 - 15) + int(nz[0])
        n = 0
        while start_at + n < W and line[start_at + n]:
            n += 1
        # A NOTE RULE MEASURES BETWEEN 201 AND 246 px, measured on the
        # twenty-six sample leaves: it is a constant of the volume, not a free
        # quantity. The window was 140 to 470 px, and that width cost two false
        # readings:
        #   -- on leaf 199, a stray stroke of 154 px passed for the rule and
        #      gave 161.63 mm instead of 107.74; the block of notes, set so low,
        #      overran the page and lost a line;
        #   -- on leaf 231, a TABELO page with no note at all, the WELDED SERIFS
        #      of the semi-bold headword "Konjuncioni :" formed a continuous run
        #      of 185 px starting from the margin, and passed all three tests.
        # We tighten to 195-260 px. Checked on twenty-six sample leaves: no real
        # rule is lost (the shortest measures 201 px on leaf 42, the longest 246
        # on leaf 34), and the two false ones fall.
        if not (195 <= n <= 260):
            continue
        # the rest of the TEXT COLUMN must be empty (the edge of the image,
        # for its part, often carries the fore-edge of the neighbouring leaf)
        #
        # ONE PIXEL TOO MANY LOST THE RULE. On leaf 162 this test returned
        # remainder = 7 for a threshold of 6: two pixels of dirt in the middle,
        # and FIVE AT THE EDGE OF THE PAPER. text_region does not always trim
        # that edge -- here it returned span[1] = 1405 when the text column stops
        # around 1390 -- so that the neighbouring leaf's fore-edge counted as
        # ink. We therefore take off a safety margin on the right before summing.
        # Three leaves of the same batch were declared "rule not found" for this
        # reason.
        EDGE = 25
        tail = line[start_at + n + 30:max(start_at + n + 30, span[1] - EDGE)]
        rest_of = tail.sum()
        # FIFTH CAUSE OF "RULE NOT FOUND": dirt IN THE MIDDLE of the column. On
        # leaf 213 the rule is perfect -- 214 px, set on the margin, clean to the
        # eye -- but ten pixels of grime at x = 1073 carried the remainder to 10
        # for a threshold of 6, and the candidate fell. The EDGE margin, set for
        # the neighbouring leaf's fore-edge, protects only against the right
        # edge.
        #
        # A total does not distinguish ten pixels of dirt from a line of text:
        # it is the SHAPE that separates them. A line of text gives long and
        # numerous runs; dirt, one or two short runs. We therefore judge on the
        # longest continuous run, and inflate the threshold of the total
        # accordingly. Checked on twenty-six sample leaves: no rule already found
        # is lost or displaced, and 213 is found again.
        if rest_of:
            d = np.diff(np.concatenate(([0], (tail > 0).astype(np.int8), [0])))
            start_pos = np.nonzero(d == 1)[0]
            end_pos = np.nonzero(d == -1)[0]
            rest = int((end_pos - start_pos).max()) if start_pos.size else 0
        else:
            rest = 0
        # What separates dirt from a line of text is neither the number of
        # specks nor their spread -- two motes at the two ends of the column are
        # very far apart and weigh nothing (this is the case of leaves 93 and
        # 194, which a criterion of extent lost for the space of one attempt). It
        # is the QUANTITY of ink, and the SIZE of the largest cluster. On leaf
        # 213 the grime is ten pixels in one piece; the row of text preceding the
        # rule carries a hundred and fifty-four, in far longer runs. The two
        # thresholds separate the two cases amply.
        if rest > 12 or rest_of > 30:
            continue
        # WE KEEP THE CANDIDATE NEAREST THE REGULATION LENGTH, NOT THE LONGEST.
        # The note rule measures 210 to 216 px on the twenty-six sample leaves --
        # a constant of the volume, not a free quantity. Keeping the longest made
        # it choose, on leaf 199, a false rule of 154 px situated 640 px below
        # the real one, which is 212 px long: the ordinate came out at 161.63 mm
        # instead of 107.74, and the block of notes, set so low, overran the page
        # and lost a line.
        # THIS IS THE FOURTH FAILURE OF THIS DETECTOR, AND THE WORST: the other
        # three make it fail, this one makes it lie.
        RULE_LENGTH = 213
        if best is None or abs(n - RULE_LENGTH) < abs(best[1] - RULE_LENGTH):
            best = (y, n)
    if verbose and best:
        print('  rule found at y=%d, %d px long (%.1f mm)'
              % (best[0], best[1], best[1] * PG.PX2MM))
    return best


def ordinate(leaf, verbose=False):
    """Typeset ordinate of the rule, in mm from the edge of the paper."""
    f = find_rule(leaf, verbose)
    if f is None:
        return None
    norm, gm, ang = PG.prepared_img(leaf)
    gm2, span = PG.text_region(gm)
    fl = PG.lines_of(gm2)
    # Fallback mask: gm bounded to the text column. text_region sometimes
    # erases the folio (leaf 42).
    _sec = gm.copy()
    if span:
        _sec[:, :max(0, span[0] - 12)] = 0
        _sec[:, min(_sec.shape[1], span[1] + 13):] = 0
    f0 = PG.folio_line(gm2, fl, _sec)
    if f0:
        fl.insert(0, f0)
    if not fl:
        return None
    first_one = fl[1]['y0'] if f0 else fl[0]['y0']
    # CAUTION: the computation assumes that the first line found is the
    # first line of the BODY, the one that falls at \VUmargeSup. If the page
    # opens on a section heading (folio 11), that line is lower, and the
    # white space preceding it in the composition must be added.
    # We report it rather than return a false figure in silence.
    first_width = fl[1]['x1'] - fl[1]['x0'] if f0 else fl[0]['x1'] - fl[0]['x0']
    full = max(l['x1'] - l['x0'] for l in fl)
    suspect = first_width < 0.45 * full
    o = VU_TOP_MARGIN_MM + (f[0] - first_one) * PG.PX2MM
    return (o, suspect)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        n = int(a)
        print('leaf %d (folio %d):' % (n, n - 4))
        r = ordinate(n, verbose=True)
        if r is None:
            print('  rule not found')
        else:
            o, suspect = r
            print('  ordinate of \\VUnotes: %.2f mm%s' % (
                o, '   *** the page opens on a title: add the white space '
                   'that precedes it ***' if suspect else ''))
