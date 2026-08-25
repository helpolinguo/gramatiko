#!/usr/bin/env python3
"""Applies a page's measured vertical justification to the content file.

See docs/journal.md, section 7 bis. The compositor justifies his pages
vertically; tools/carding.py measures the pitch proper to the page and the
white space at its articulations. This tool matches those measurements
with the paragraph boundaries of the source, and replaces the ordinary
\\VUblancAlinea with a \\VUblanc{...} where the facsimile calls for a
wider one.

The matching is done by LINE NUMBER, never by rank of white space: a white
space may be missing on either side, and matching by rank would shift every
following value by one notch.

    python3 tools/apply_carding.py 30          # proposes, writes nothing
    python3 tools/apply_carding.py 30 --write   # writes
"""
import os, re, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carding
import checks as C

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX2PT = 72.27 / 300.0
# Ordinary paragraph space, already set everywhere by \VUblancAlinea.
ORDINARY_WHITE_PX = 1.86 / PX2PT          # 7.72 px
# Under 3 px (0.7 pt) the deviation is below the noise of the baseline
# measurement: we leave the ordinary white space.
THRESHOLD_PX = 3.0


def _page(folio):
    """"30" designates the FOLIO; "f34" designates the facsimile leaf.

    Confusing the two was a trap: folio 26 is carried by leaf 30, and an
    undifferentiated search served the wrong page without reporting
    anything.
    """
    pages = C.read_transcription()
    s = str(folio)
    if s.startswith('f'):
        for pg in pages:
            if pg['leaf'] == s[1:]:
                return pg
        return None
    for pg in pages:
        if pg['folio'] == s:
            return pg
    return None


def propose(folio):
    """[(rank of the \\VUblancAlinea in the page, facsimile line, excess px)]"""
    pg = _page(folio)
    if pg is None:
        raise SystemExit('page %s absent from the transcription' % folio)
    leaf = int(pg['leaf']) if pg['leaf'] else int(pg['folio']) + 4
    reg, excess, fl, _ = carding.measure(leaf)
    if reg is None:
        raise SystemExit('leaf %d: no measurable body' % leaf)
    # The folio counts as a line of the facsimile but not of the transcription.
    offset = 1 if (fl and fl[0]['x1'] - fl[0]['x0']
                     < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
    # Paragraph boundaries of the BODY, in the order of the source. The line
    # following the boundary carries index i+1 in the transcription.
    boundaries = []           # (rank, facsimile index of the following line)
    row = 0
    # Lines WITHOUT TEXT (an apparatus macro alone, a remnant of the
    # division) do not appear in the facsimile: counted here, they shifted the
    # index of every following boundary, and the measured white space no
    # longer found its place (folio 25: the excess of 24.8 px before line 31
    # stayed unapplied, with nothing to report it).
    lines = [l for l in pg['lines'] if l['text']]
    for i, l in enumerate(lines):
        if l.get('note') or l['break'] != 'pf':
            continue
        if i + 1 >= len(lines) or lines[i + 1].get('note'):
            continue          # last paragraph of the page, or the passage to the notes
        row += 1
        boundaries.append((row, i + 1 + offset))
    par_ligne = {k: e for k, _, e in excess}
    out = []
    for row, k in boundaries:
        # A BOUNDARY WITHOUT EXCESS IS NOT A BOUNDARY WITHOUT MEASUREMENT: it is
        # a boundary WITHOUT WHITE SPACE. The paragraph space of 1.86 pt is not a
        # constant of the volume -- on leaf 20, the sixteen pitches of the body
        # are all 41.0 to 41.9 px, boundaries included. Treating an absence of
        # excess as an absence of measurement left in place six \VUblancAlinea
        # the original does not have, and the page dropped 32 px over its height.
        # \VUblanc REPLACES \VUblancAlinea, it is not added to it: the value to
        # apply is therefore the WHOLE excess, not the excess less the ordinary
        # space. Diminished, it left the page 7.7 px too high under each
        # articulation -- enough for folios 59 and 63 to fail check 11, and
        # invisible everywhere else. The ordinary space serves only to decide
        # whether there is cause to touch anything.
        e = par_ligne.get(k, 0.0)
        d = e - ORDINARY_WHITE_PX
        if abs(d) < THRESHOLD_PX:
            continue
        out.append((row, k, e, e if d > 0 else d))
    return pg, reg, out, offset


def _mask_notes(body):
    """The \\VUnotes block replaced by blanks, the line endings kept.

    The indices therefore do not move, and the body's blank lines stay
    detectable. Overwriting the line endings too -- which the first version
    did -- welded the matter preceding the block to that following it, and
    the line count went askew.

    The block's bounds are taken by COUNTING BRACES: the body of a note
    itself contains braces, and lines reduced to a closing brace.
    """
    mask = list(body)
    for m in re.finditer(r'\\VUnotes\{', body):
        i = m.end() - 1
        depth = 0
        while i < len(body):
            if body[i] == '{' and body[i - 1] != '\\':
                depth += 1
            elif body[i] == '}' and body[i - 1] != '\\':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        for j in range(m.start(), min(i + 1, len(body))):
            if mask[j] != '\n':
                mask[j] = ' '
    return ''.join(mask)


# Apparatus macros: each composes ONE line on its own. Without them, the
# count of the source's lines fell one behind the transcription's per
# title, and the measured white space was applied several lines too high
# (folio 12: 41 px of drift became 77).
APPARATUS = re.compile(r'\\(VUtitre|VUcentre|VUcentreA)\b')
SEPARATOR = re.compile(r'\\nl\b|\\cc\b|\n[ \t]*\n')


def lines_of_source(body):
    """[(number of the composed line, start, end)] for each paragraph boundary.

    The number is that of the line FOLLOWING the boundary, counted as the
    transcription does: a line ends on \\nl, on \\cc, or on a blank line,
    and each apparatus macro is worth a whole line. (start, end) delimit
    the \\VUblancAlinea or the \\VUblanc already applied, or else the
    position where it would have to be written.
    """
    mask_of = _mask_notes(body)
    out = []
    n = 0            # composed lines already seen
    pos = 0
    for m in SEPARATOR.finditer(mask_of):
        fore_edge = mask_of[pos:m.start()]
        # the slice's apparatus macros each count as one line
        napp = len(APPARATUS.findall(fore_edge))
        rest_of = APPARATUS.sub('', fore_edge)
        n += napp
        if C.plain_text(rest_of).strip():
            n += 1
        pos = m.end()
        if not m.group(0).startswith('\\'):        # blank line
            j = m.end()
            while True:                            # possible comments
                mc = re.match(r'%[^\n]*\n', mask_of[j:])
                if not mc:
                    break
                j += mc.end()
            mb = re.match(r'\\VUblanc(?:Alinea\b|\{[^}]*\})[^\n]*\n', mask_of[j:])
            out.append((n, j, j + mb.end() if mb else j))
    return out


def _page_body(src, folio):
    """(start, end) of the body of the VUpage carrying this folio in src."""
    s = str(folio)
    for m in re.finditer(
            r'\\begin\{VUpage\}(?:\[([^\]]*)\])?\{([^}]*)\}(.*?)\\end\{VUpage\}',
            src, re.S):
        # The same trap as in _page: "30" is a FOLIO. Accepting the leaf as well
        # served the page \VUpage[30]{26} when folio 30 was asked for, and the
        # anchoring on the text obviously found nothing -- with nothing to
        # indicate the confusion.
        if s.startswith('f'):
            if (m.group(1) or '').strip() == s[1:]:
                return m.start(3), m.end(3)
        elif m.group(2).strip() == s:
            return m.start(3), m.end(3)
    return None


def apply_at(folio, write_out=False):
    pg, reg, props, offset = propose(folio)
    print('=== folio %s (leaf %s) — regular pitch %.2f px = %.2f pt'
          % (pg['folio'] or '?', pg['leaf'], reg, reg * PX2PT))
    if abs(reg - carding.CURRENT_PITCH) >= 0.6:
        print('    page vertically justified: \\VUinterlignePage{%.2fpt}' % (reg * PX2PT))
    if not props:
        print('    no articulation white space to apply')
        return
    fp = os.path.join(P, 'content', pg['fichier'])
    src = open(fp, encoding='utf-8').read()
    bounds = _page_body(src, pg['folio'] or pg['leaf'])
    if bounds is None:
        raise SystemExit('page not found in %s' % fp)
    a, b = bounds
    body = src[a:b]
    lg = [l for l in pg['lines'] if l['text']]
    # THE ANCHORING IS DONE ON THE TEXT, not on a rank nor on a line count.
    # Two attempts failed before this one: counting the source's boundaries
    # (wrong as soon as a title separates two, the facsimile putting a white
    # space there and the source a \VUsaut), then counting the composed lines
    # (wrong because of the apparatus macros and the comments). The
    # transcription, for its part, keeps for each line the fragment of source
    # it comes from: we look for that fragment, and the \VUblancAlinea it
    # carries at its head is the one to change. No index arithmetic is left,
    # hence no slip is possible.
    replace = []
    for _, k, e, d in props:
        i = k - offset
        if not (0 <= i < len(lg)):
            print('    line %2d: outside the transcription' % k)
            continue
        raw = lg[i]['brut']
        if '\\VUblancAlinea' not in raw:
            print('    line %2d: excess %.1f px — the line « %s » does not follow '
                  'an ordinary paragraph boundary (title? by hand)'
                  % (k, e, lg[i]['text'][:40]))
            continue
        if body.count(raw) != 1:
            print('    line %2d: ambiguous fragment (%d occurrences)'
                  % (k, body.count(raw)))
            continue
        p = body.index(raw) + raw.index('\\VUblancAlinea')
        if d <= 0:
            print('    line %2d: no white space in the facsimile -> the ordinary '
                  'space is removed  before « %s »' % (k, lg[i]['text'][:38]))
        else:
            print('    line %2d: excess %.1f px -> \\VUblanc{%.2fpt}  before « %s »'
                  % (k, e, d * PX2PT, lg[i]['text'][:38]))
        replace.append((p, d))
    if not write_out:
        print('    (nothing written; --write to apply)')
        return
    for p, d in sorted(replace, reverse=True):
        fresh = ('%% no white space in the facsimile' if d <= 0
                else '\\VUblanc{%.2fpt}%% measured in the facsimile' % (d * PX2PT))
        body = body[:p] + fresh + body[p + len('\\VUblancAlinea'):]
    open(fp, 'w', encoding='utf-8').write(src[:a] + body + src[b:])
    print('    applied in content/%s' % pg['fichier'])


if __name__ == '__main__':
    write_out = '--write' in sys.argv
    for a in sys.argv[1:]:
        if a.startswith('--'):
            continue
        apply_at(a, write_out)
