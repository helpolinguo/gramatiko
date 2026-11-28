#!/usr/bin/env python3
"""THE PDF CARRIES A REAL SPACE BETWEEN WORDS.

pdfTeX writes no space character: between two words it moves the pen, a
negative number in a TJ array, or a new Tm where the font changes. A reader
finds the words again by the gaps, and its guess fails on a line set tight:
folio 16's « Ma, pro ke la nomi di la sep dii semanala ne esas kom- », its
spaces shrunk to 1.83 pt (0.18 em), came out of Apple Books' search as
« Ma,prokelanomidilasepdiisemanalaneesaskom ». 427 lines of the volume have
a gap between words under 0.185 em.

pdfTeX's own remedy, \\pdfinterwordspaceon, was tried and given up. In the
pdfTeX of TeX Live 2023 (1.40.25) it writes a space only where the gap
reaches 0.185 em of the type size -- not on the tight lines, which are the
ones that fail -- and none at all where a space meets a change of font,
« revuo *Progreso* » coming out « revuoProgreso ». Its threshold follows
the size written in the PDF; neither \\fontdimen2 nor \\fontdimen6 moves it.

So the space is written here, after pdflatex, into the finished PDF: at each
gap between words, a space glyph of pdfTeX's own space font (PdfTeX-Space,
the font \\pdfinterwordspaceon uses, mapped to U+0020, taken whole from
pdfTeX's own output: see space_font), sized so that its advance IS the
gap. Nothing is drawn and nothing moves: the glyph after the space starts
where the kern used to put it.

WHAT IS A GAP BETWEEN WORDS. Measured on the volume: kerns between letters
lie within 0.05 em of their run's letter level, gaps between words 0.15 em
and more beyond it; the threshold, 0.12 em, sits in the empty valley. The
letter level is zero in an ordinary run; in a LETTERSPACED one -- the notes
(\\lsstyle), the titles, the apparatus set with \\textls -- every glyph is a
string of its own, and the level is the lower quartile of the kerns between
single letters (see letter_level, and the four readings given up there). It
is taken run by run, not line by line: the Tabelo's leader dots, a run of
their own, would lend the whole line their spacing.

A run is paired with the previous run OF ITS OWN LINE (see process), and the
space between them written at the end of the first.

Usage: python3 tools/word_spaces.py gramatiko.pdf     (rewrites it in place)
"""
import os
import subprocess
import sys
import tempfile

import pypdf
from pypdf.generic import (ArrayObject, ByteStringObject, ContentStream,
                           FloatObject, NameObject, NumberObject)

GAP = 0.12            # em beyond the run's letter level
SPACE_FONT = NameObject('/FWsp')
SPACE_WIDTH = None    # the width of the space glyph, read from pdfTeX's font
MARK = NameObject('/GramatikoWordSpaces')   # in the document info: done once


def is_num(e):
    return isinstance(e, (NumberObject, FloatObject))


def raw(e):
    return bytes(e.original_bytes)


def quartile(xs):
    """The lower quartile, interpolated."""
    xs = sorted(xs)
    pos = 0.25 * (len(xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def letter_level(arr):
    """The letter level of a run, in em (positive: letters spread).

    A run is LETTERSPACED when nearly every glyph is a string of its own --
    85 % of its strings, four at least -- or when its strings are single
    letters and nothing else. Its level is the LOWER QUARTILE of the kerns
    between two single glyphs that are both letters or digits: 0.07-0.08 em
    in the notes (\\lsstyle), 0.09-0.11 in the title, 0.21 in « (Apendico
    5ma.) », 0.26 in « DIL A ». The quartile, because between single glyphs
    stand both the kerns between LETTERS, the lower ones, and those between
    one-letter WORDS, the higher -- Ido has many: « e », « a », « o ». A run
    that is letterspaced but not all letters is held under 0.3 em; a word
    tracked in a title, « I|d|o », « D|A », may be wider. Any other run: zero.

    FOUR CUTS GIVEN UP, each on the volume's own runs.
    1. The median kern of a letterspaced run. The roman run
       `,|-392|e|-393|n|-65|e|-393|:` of folio 65's « flori, e ne : li » has
       five single glyphs and a median of 0.39 em, a gap between WORDS: the
       run lost its spaces, « flori,ene:li », as did seventy-odd others, most
       on folios 217-218.
    2. The kerns cut at their largest jump. One kern of the font decides it:
       `P|-78|r|-78|o|-78|g|-78|r|46|.` cut between the full stop's -0.046
       and the letters' 0.078: « P r o g r. ».
    3. The commonest kern between single glyphs, in any run: on folio 121's
       tight line, `a|-184|m` and `s|-184|v` agreed, and its gaps between
       words, 0.184 em, became its letter level.
    4. The commonest kern, in letterspaced runs only. Font kerning cuts
       ordinary words into single glyphs: folio 98's `,|-320|e|-320|l|-14|a|
       -320|d|27|u|13|esma|-320|:` is seven single glyphs in eight, and its
       two gaps of 0.32 em agreed -- « triacent,eladuesma:deketri »."""
    strings = [raw(e) for e in arr if not is_num(e)]
    alnum = [-float(arr[i]) / 1000 for i in range(1, len(arr) - 1)
             if is_num(arr[i]) and not is_num(arr[i - 1]) and not is_num(arr[i + 1])
             and len(raw(arr[i - 1])) == 1 and len(raw(arr[i + 1])) == 1
             and chr(raw(arr[i - 1])[0]).isalnum() and chr(raw(arr[i + 1])[0]).isalnum()]
    if not alnum:
        return 0.0
    if all(len(x) == 1 and chr(x[0]).isalpha() for x in strings):
        return quartile(alnum)
    if len(strings) < 4 or sum(1 for x in strings if len(x) == 1) < 0.85 * len(strings):
        return 0.0
    level = quartile(alnum)
    return level if level < 0.3 else 0.0


def space_font(writer):
    """pdfTeX's own space font, AS pdfTeX EMBEDS IT: a one-line document is
    set by pdftex with \\pdfinterwordspaceon in a scratch directory, and its
    PdfTeX-Space font -- program, descriptor, widths, ToUnicode -- is copied
    into the volume. Returns the font and the width of its glyph.

    THE FIRST EMBEDDING, GIVEN UP ON THE COMMISSIONER'S iPAD. The font had
    been built here from dummy-space.pfb as found in TeX Live: the program
    as it stands, a descriptor of my own (FontBBox [0 0 0 0]), a ToUnicode
    like pdfTeX's. Every reader at hand read its spaces -- pdfminer, poppler
    -- and Apple Books did not: folio 16 still came back « Ma,prokelanomidi
    lasepdii... ». Three test files, the same three pages, the same gaps,
    only the space font differing (28 November 2026): that one, ignored;
    pdfTeX's own object, copied from a pdfTeX output, read -- « Ma, pro ke
    la nomi di la sep dii semanala »; a space of Helvetica, read too.
    pdfTeX's is kept: it is embedded, like every other font of the volume,
    where Helvetica would be the one font left out. Which of the
    differences Apple's reader minds -- the bounding box, the program pdfTeX
    rewrites and subsets, the name -- was not sought: the object that works
    is taken whole, from pdfTeX itself.

    \\input glyphtounicode and \\pdfgentounicode=1 are what give it its
    ToUnicode under plain pdftex; so set, it is byte for byte the font that
    LaTeX's pdfTeX writes, and the one the iPad read."""
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, 'space.tex'), 'w') as fh:
            fh.write('\\input glyphtounicode \\pdfgentounicode=1 '
                     '\\pdfinterwordspaceon a\\pdffakespace b\\bye\n')
        subprocess.run(['pdftex', '-interaction=nonstopmode', 'space.tex'],
                       cwd=d, capture_output=True, check=True)
        reader = pypdf.PdfReader(os.path.join(d, 'space.pdf'))
        for ref in reader.pages[0]['/Resources']['/Font'].values():
            font = ref.get_object()
            if str(font['/BaseFont']).endswith('PdfTeX-Space'):
                width = float(font['/Widths'][0])
                return font.clone(writer).indirect_reference, width
    raise SystemExit('word_spaces: pdftex wrote no PdfTeX-Space font')


def num(x):
    """A number written to 8 decimals. At 6, the advance was the kern's to
    within 2.3e-6 pt, and that was enough to flip 27 pixels of folio 43 at
    100 dpi, a glyph lying on a rounding boundary; at 8 no page moves."""
    s = ('%.8f' % x).rstrip('0').rstrip('.')
    return FloatObject(s)


class Fonts:
    """Glyph widths of the page's fonts, to find where a run ends."""
    def __init__(self, page):
        self.w = {}
        res = page.get('/Resources')
        fonts = res.get_object().get('/Font') if res else None
        for name, ref in (fonts.get_object().items() if fonts else []):
            f = ref.get_object()
            if '/Widths' in f and '/FirstChar' in f:
                first = int(f['/FirstChar'])
                ws = [float(x) for x in f['/Widths'].get_object()]
                self.w[name] = (first, ws)

    def advance(self, font, data):
        if font not in self.w:
            return None
        first, ws = self.w[font]
        tot = 0.0
        for c in data:
            j = c - first
            tot += ws[j] if 0 <= j < len(ws) else 0.0
        return tot / 1000


def runs_of(ops, fonts):
    """Every text-showing operator with its line, start and end (in the
    coordinates of Tm's translation, Tm being diagonal)."""
    out = {}
    tm = tlm = [1, 0, 0, 1, 0, 0]
    font, size, bt = None, None, 0
    for i, (operands, op) in enumerate(ops):
        if op == b'BT':
            bt += 1
            tm = tlm = [1, 0, 0, 1, 0, 0]
        elif op == b'Tf':
            font, size = operands[0], float(operands[1])
        elif op == b'Tm':
            tm = tlm = [float(x) for x in operands]
        elif op == b'Td':
            tx, ty = float(operands[0]), float(operands[1])
            tlm = [tlm[0], tlm[1], tlm[2], tlm[3],
                   tlm[4] + tx * tlm[0] + ty * tlm[2], tlm[5] + tx * tlm[1] + ty * tlm[3]]
            tm = tlm
        elif op in (b'TJ', b'Tj'):
            arr = operands[0] if op == b'TJ' else [operands[0]]
            x0 = tm[4]
            adv = 0.0
            ok = True
            for e in arr:
                if is_num(e):
                    adv += -float(e) / 1000 * size
                else:
                    a = fonts.advance(font, raw(e))
                    if a is None:
                        ok = False
                        break
                    adv += a * size
            diag = abs(tm[1]) < 1e-9 and abs(tm[2]) < 1e-9
            out[i] = {'bt': bt, 'y': tm[5], 'x0': x0, 'x1': x0 + adv * tm[0] if ok else None,
                      'a': tm[0], 'font': font, 'size': size, 'diag': diag,
                      'L': letter_level(arr) if op == b'TJ' else 0.0}
            if ok:
                tm = [tm[0], tm[1], tm[2], tm[3], tm[4] + adv * tm[0], tm[5] + adv * tm[1]]
    return out


def space_ops(width_text, font, size):
    """A space whose advance is `width_text` (text space), then the font back."""
    s = width_text / (SPACE_WIDTH / 1000)
    return [([SPACE_FONT, num(s)], b'Tf'),
            ([ByteStringObject(b' ')], b'Tj'),
            ([font, FloatObject(size)], b'Tf')]


def process(page, writer, font_ref, stats):
    fonts = Fonts(page)
    cs = ContentStream(page.get_contents(), writer)
    ops = cs.operations
    runs = runs_of(ops, fonts)
    order = sorted(runs)
    # Gaps between runs: each run against the PREVIOUS RUN OF ITS OWN LINE
    # -- not the previous run of the stream. Folio 31's table sets a large
    # brace on another baseline between « Komparativo » and « egaleso »; paired
    # with the run next to it in the stream, each word met the brace, and
    # the gap between them went unseen. A superscript is of its line (within
    # 0.6 of the size), and pairs like any other run.
    after = {}
    for n, b in enumerate(order):
        rb = runs[b]
        if not rb['diag']:
            continue
        for a in reversed(order[:n]):
            ra = runs[a]
            if ra['bt'] != rb['bt']:
                break
            if not ra['diag'] or abs(ra['y'] - rb['y']) > 0.6 * ra['size'] * abs(ra['a'] or 1):
                continue
            if ra['x1'] is not None and ra['a']:
                gap = rb['x0'] - ra['x1']
                em = gap / (abs(ra['a']) * ra['size'])
                if em >= max(ra['L'], rb['L'], 0.0) + GAP and a not in after:
                    after[a] = gap / ra['a']          # in text space
            break
    new = []
    for i, (operands, op) in enumerate(ops):
        if op == b'TJ' and i in runs and runs[i]['diag']:
            r = runs[i]
            arr = operands[0]
            cur = []
            for k, e in enumerate(arr):
                if is_num(e) and 0 < k < len(arr) - 1 and not is_num(arr[k - 1]) \
                        and not is_num(arr[k + 1]) \
                        and -float(e) / 1000 - max(r['L'], 0.0) >= GAP:
                    new.append(([ArrayObject(cur)], b'TJ'))
                    new.extend(space_ops(-float(e) / 1000 * r['size'], r['font'], r['size']))
                    stats['inside'] += 1
                    cur = []
                else:
                    cur.append(e)
            new.append(([ArrayObject(cur)], b'TJ'))
        else:
            new.append((operands, op))
        if i in after:
            r = runs[i]
            new.extend(space_ops(after[i], r['font'], r['size']))
            stats['between'] += 1
    cs.operations = new
    page.replace_contents(cs)
    res = page['/Resources'].get_object()
    res['/Font'].get_object()[SPACE_FONT] = font_ref


def main(path):
    reader = pypdf.PdfReader(path)
    info = reader.metadata or {}
    if MARK in info:
        print('word_spaces: %s already carries its spaces' % path)
        return
    writer = pypdf.PdfWriter(clone_from=reader, keep_initial_header=True)
    global SPACE_WIDTH
    font_ref, SPACE_WIDTH = space_font(writer)
    stats = {'inside': 0, 'between': 0}
    for page in writer.pages:
        process(page, writer, font_ref, stats)
        page.compress_content_streams()
    writer.add_metadata({MARK: 'yes'})
    tmp = path + '.tmp'
    with open(tmp, 'wb') as fh:
        writer.write(fh)
    os.replace(tmp, path)
    print('word_spaces: %d spaces in runs, %d between runs, %s %d bytes'
          % (stats['inside'], stats['between'], path, os.path.getsize(path)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'gramatiko.pdf')
