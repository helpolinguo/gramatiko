#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""READING PAGE for the volume: content/*.tex -> index.html.

The facsimile is set LINE BY LINE; a reading page cannot be. This tool
therefore does not reformat the transcription, it RE-READS it: it gives
each paragraph back its continuity (\\nl, \\cc, \\parplein,
\\VUcontinue), attaches each note to the call that asks for it, and keeps
from the facsimile the only two things that serve the reader -- the folio,
which points into the PDF, and the hierarchy of parts / chapters /
headwords.

It is REPLAYABLE: nothing is written by hand into index.html, everything
is drawn from the transcription. Recompose the volume and replay the tool.

    python3 tools/html.py            # writes index.html
    python3 tools/html.py --count    # counts only, writes nothing

WHAT IS DELIBERATELY LEFT ASIDE
  -- leaves 3 to 7 (printed cover, half-title, title page): these are
     apparatus pages, set at measured ordinates, which are not read in
     the run of the text;
  -- the TABELO (leaves 229 onwards) and the publisher's advertisements:
     the TABELO is an index of folio references, and the reading page has
     its own navigation and its own search; this is also what excludes
     the three \\VUtitre of leaf 236, which are section headings and not
     chapters;
  -- rules, ornaments and fleurons: they are laid at absolute ordinates,
     they do not belong to the flow of the text.

THE TEXT IS NEVER CORRECTED. The typos of 1925 are kept; the tool touches
only what is composition (line breaks, French spacing) and never the
letter.
"""
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'content')
FILES = ['00-front-matter.tex', '10-part1.tex', '20-part2.tex']
OUTPUT = os.path.join(ROOT, 'index.html')

# The PDF sits beside the page. PDF page = folio + 2: the PDF begins at
# leaf 3 (printed cover) and folio 1 is on leaf 5. Checked at both bounds
# -- folio 11 -> page 13, folio 225 -> page 227.
PDF = 'gramatiko.pdf'
PDF_OFFSET = 2

# The author's portrait, at the head of the page. The scan's PNG is a
# halftone with an alpha channel: the ink is BLACK, the paper TRANSPARENT.
# An <img> tag would render it black on black in dark mode; we therefore
# keep only the ALPHA, laid as a MASK over a block whose ground is the
# theme's ink colour. The portrait then follows the ink of the text, in
# both modes, as does every other letter on the page.
#   -- 650 px wide: the facsimile is 726, and its halftone screen does not
#      bear being reduced much further;
#   -- 8 levels of alpha: the screen is a GRAIN, not a gradient; eight
#      levels are indistinguishable to the eye and divide the PNG's weight
#      by four (194 kB against 730).
PORTRAIT = os.path.join(ROOT, 'ornaments', 'portrait-3.png')
PORTRAIT_LEAF = 7     # the title page, where the plate is laid
PORTRAIT_WIDTH = 650
PORTRAIT_LEVELS = 8
PORTRAIT_TITLE = 'Portreto dil autoro'

# Folio 224 (leaf 228) is an ADDENDUM: it carries one sentence and two
# entries, and the sentence itself says where the two entries belong --
# "pos til p. 82". The reading page puts them back there, with their folio
# 224 and the PDF reference that goes with it.
ADDENDUM_LEAF = 228
ADDENDUM_CHAPTER = 'PREPOZICIONI.'
# The headword as `headword_case` sets it: in lower case.
ADDENDUM_HEADWORD = 'til'
# The notice to the reader. A page that moves text must say so; we say it
# in Ido, and in square brackets, as with any editorial intervention.
ADDENDUM_NOTICE = (
    'La originalo omisis ca du prepozicioni e pozis li ye la fino di '
    'la libro, p. 224 ; ca pagino ridonas li a la loko quan la verko '
    'ipsa indikas.')

# The volume's four groups, by opening leaf. The bounds are those of the
# structural survey (docs/journal.md, 3.1). The APENDICI form a group
# APART: the facsimile runs them on after the second part, but they are ten
# self-contained studies, listed as such at folio 232, and not the tail of
# the chapter on composition.
PARTS = [
    (8,   'Introdukto'),
    (13,  'Unesma parto \u2014 MORFOLOGIO E SINTAXO'),
    (119, 'Duesma parto \u2014 VORTIFADO'),
    (183, 'APENDICI'),
]
FIRST_LEAF = 8      # before: cover, half-title, title
LAST_LEAF = 228    # after: TABELO, list of appendices, advertisements

# The ordinate (mm) which separates, on an apparatus page, what is read
# BEFORE the body from what is read AFTER. \VUcentreA and its kind are
# declared at the head of the page but laid at a measured ordinate: without
# this sorting, the signatures of folio 4 would rise above the text they
# sign.
APPARATUS_THRESHOLD = 60.0


# ------------------------------------------------------------------
# 1. THE COMMENTS
# ------------------------------------------------------------------
def strip_comments(s):
    """Strip LaTeX comments.

    Two cases, and they do not do the same thing:
      -- a `%` at the head of a line: the whole line disappears, newline
         included;
      -- a `%` at the end of a line: it eats the rest of the line AND the
         newline, so it JOINS the next line to this one. That is how the
         transcription writes `\\VUnotes{...}{%` without opening a stray
         space at the head of a note.
    """
    out = []
    for line in s.split('\n'):
        m = re.search(r'(?<!\\)%', line)
        if m is None:
            out.append(line + '\n')
        elif line[:m.start()].strip() == '':
            pass                       # a comment line: nothing at all
        else:
            out.append(line[:m.start()])   # no newline: we join
    return ''.join(out)


# ------------------------------------------------------------------
# 2. READING THE ARGUMENTS
# ------------------------------------------------------------------
def read_group(s, i):
    """s[i] must be `{` (spaces allowed before). Returns (contents, i_after)."""
    while i < len(s) and s[i] in ' \n\t':
        i += 1
    if i >= len(s) or s[i] != '{':
        return '', i
    depth, j = 1, i + 1
    while j < len(s) and depth:
        if s[j] == '\\':
            j += 2
            continue
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
        j += 1
    return s[i + 1:j - 1], j


def read_option(s, i):
    while i < len(s) and s[i] in ' \n\t':
        i += 1
    if i < len(s) and s[i] == '[':
        j = s.index(']', i)
        return s[i + 1:j], j + 1
    return None, i


def read_args(s, i, n, opt=False):
    o = None
    if opt:
        o, i = read_option(s, i)
    args = []
    for _ in range(n):
        a, i = read_group(s, i)
        args.append(a)
    return o, args, i


def mm(x):
    """A length from the transcription, in millimetres. mm, pt or inches."""
    m = re.match(r'\s*(-?[\d.]+)\s*(mm|pt|cm|in)?', x or '')
    if not m:
        return 0.0
    v = float(m.group(1))
    return {'mm': v, 'pt': v * 25.4 / 72.27, 'cm': v * 10,
            'in': v * 25.4, None: v}[m.group(2)]


# ------------------------------------------------------------------
# 3. THE RUNNING TEXT
# ------------------------------------------------------------------
# Macros that bear only on composition: their argument is text, the
# wrapping disappears.
TRANSPARENT = {'VUetroit': (2, 1), 'VUserre': (2, 1), 'VUdecale': (2, 1),
                 'VUcentreDA': (5, 4), 'textnormal': (1, 0), 'mbox': (1, 0)}
TAGS = {'VUgras': ('<b>', '</b>'), 'textbf': ('<b>', '</b>'),
           'textit': ('<i>', '</i>'), 'emph': ('<i>', '</i>'),
           'textsc': ('<span class="pk">', '</span>'),
           'textsuperscript': ('<sup>', '</sup>')}
LITERALS = {'textquotesingle': "'", 'nl': ' ', 'cc': '', ' ': ' ',
             '/': '',
             '{': '{', '}': '}', '%': '%', '&': '&amp;', '#': '#',
             '_': '_', 'relax': '', 'par': '\n\n', 'noindent': '',
             'ignorespaces': '', 'hfil': ' ', 'hfill': ' ',
             'VUaccolade': None, 'VUaccoladeD': None, 'VUaccoladeH': None}

unhandled = OrderedDict()   # macro -> number of untreated encounters


def escape(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# The standard library's html module is shadowed by THIS file: the
# script's directory comes first, and `import html` would return itself.
# The two functions we need fit in three lines.
def unescape(t):
    return (t.replace('&lt;', '<').replace('&gt;', '>')
             .replace('&nbsp;', '\u00a0').replace('&amp;', '&'))


def skip_space(s, i):
    """After a control WORD (\\nl, \\cc, \\VUcontinue...), TeX swallows the
    whitespace that follows -- but not a blank line, which stays the end of
    a paragraph. It is on this rule that the rejoining of words broken
    across pages depends: `konso\\cc` then `nanti` must give `konsonanti`,
    and not `konso nanti`."""
    j = i
    while j < len(s) and s[j] in ' \t':
        j += 1
    if j < len(s) and s[j] == '\n':
        k = j + 1
        while k < len(s) and s[k] in ' \t':
            k += 1
        if k >= len(s) or s[k] != '\n':
            # k >= len(s): the macro ends the page. The whitespace is swallowed
            # all the same, failing which a word broken at the foot of a page
            # (\\cc on the last line) would resume with a space.
            return k
    return j


# ------------------------------------------------------------------
# 2 bis. A BRACE THAT STRETCHES
# ------------------------------------------------------------------
# A font's { glyph DOES NOT STRETCH: it is worth one line, and no more.
# Set between the three rows of dots of folio 220 it caps nothing -- the
# first of the commissioner's two complaints.
#
# Three ways offered themselves: stretch the glyph by scaleY, draw the
# brace with rounded borders in CSS, or trace an inline SVG.
#   -- scaleY lengthens the stem but stretches the curves too: the point
#      of a brace tripled in height becomes a blot, and the shape depends
#      on whichever font the reader has. Rejected.
#   -- rounded borders need four quarter-circles and two stems, hence
#      several elements per brace, whose joins come apart as soon as the
#      browser rounds half a decimal; and everything would have to be
#      done again for the horizontal. Rejected.
#   -- THE INLINE SVG: one path, no joins, the same mechanism in both
#      directions. `preserveAspectRatio="none"` stretches the drawing over
#      the exact box it is given, however tall or wide, and
#      `vector-effect:non-scaling-stroke` keeps the stroke its weight --
#      without which the stem of a tripled brace would be three times
#      heavier than the text. Kept.
#
# The paths follow the facsimile of folio 220 (scan/pages/f0224.jpg, ink
# x 786-796 y 877-995 for the vertical, x 524-1063 y 1339-1355 for the
# horizontal): a light brace with a barely salient point, and a nearly
# flat horizontal with a central spike.
BRACES = {
    # Opening: point to the left, in the middle; box tall and narrow.
    'akol': ('0 0 10 100',
             # THE EXTREMITIES CURVE AWAY FROM THE POINT.
             # The first path brought them back towards it: all three ends
             # looked the same way, which no brace does. In the ordinary
             # drawing, the central point juts out one side and the two ends
             # turn back the other, beyond the plumb of the shoulders.
             'M8.6 1C5.8 5 6 12 6 22L6 40C6 46 4 49 .8 50'
             'C4 51 6 54 6 60L6 78C6 88 5.8 95 8.6 99',
             'akv'),
    # Closing: the same, reversed (x becomes 10-x).
    'akolD': ('0 0 10 100',
              'M1.4 1C4.2 5 4 12 4 22L4 40C4 46 6 49 9.2 50'
              'C6 51 4 54 4 60L4 78C4 88 4.2 95 1.4 99',
              'akd'),
    # Horizontal: point at the top, in the middle; box wide and low.
    'akolH': ('0 0 100 10',
              'M.8 9C16 5.9 30 5.7 47 5.7C48.4 5.7 49.2 4.2 50 1.2'
              'C50.8 4.2 51.6 5.7 53 5.7C70 5.7 84 5.9 99.2 9',
              'akh'),
}


def brace_svg(kind):
    """The `kind` brace as SVG, ready to be stretched by the CSS."""
    vb, path, css_class = BRACES[kind]
    # `vector-effect` is set as an ATTRIBUTE and not in CSS: every browser
    # reads the presentation attribute, whereas the CSS property of the
    # same name is more recent -- and it was on an iPad that the fault was
    # seen.
    return ('<span class="akol %s" aria-hidden="true">'
            '<svg viewBox="%s" preserveAspectRatio="none">'
            '<path vector-effect="non-scaling-stroke" d="%s"/>'
            '</svg></span>' % (css_class, vb, path))


def inline(s):
    """Convert a run of inline TeX to HTML. Never breaks a line: that is the
    whole point of the reading page."""
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            m = re.match(r'\\([A-Za-z]+|.)', s[i:])
            name = m.group(1)
            i += m.end()
            if name.isalpha():
                i = skip_space(s, i)
            if name in TAGS:
                a, i = read_group(s, i)
                o, f = TAGS[name]
                out.append(o + inline(a) + f)
            elif name in TRANSPARENT:
                nb, keep = TRANSPARENT[name]
                _, args, i = read_args(s, i, nb)
                out.append(inline(args[keep]))
            elif name == 'textls':
                _, args, i = read_args(s, i, 1, opt=True)
                out.append(inline(args[0]))
            elif name == 'VUtitreAppel':
                # The note call on the "Averto" title: it is text, and it is a
                # call like any other.
                _, args, i = read_args(s, i, 1, opt=True)
                out.append(' ' + inline(args[0]))
            elif name in ('VUaccolade', 'VUaccoladeD'):
                _, args, i = read_args(s, i, 2)
                out.append(brace_svg('akol' if name == 'VUaccolade' else 'akolD'))
            elif name == 'VUaccoladeH':
                _, args, i = read_args(s, i, 1)
                out.append(brace_svg('akolH'))
            elif name in LITERALS:
                out.append(LITERALS[name] or '')
            elif name in ('fontsize', 'selectfont', 'normalfont', 'bfseries',
                         'itshape', 'lsstyle', 'centering'):
                if name == 'fontsize':
                    _, _, i = read_args(s, i, 2)
            else:
                unhandled[name] = unhandled.get(name, 0) + 1
        elif c == '{':
            a, i = read_group(s, i)
            out.append(inline(a))
        elif c == '}':
            i += 1
        elif s.startswith('---', i):
            out.append('\u2014')
            i += 3
        elif s.startswith('--', i):
            out.append('\u2013')
            i += 2
        elif c == '~':
            out.append('\u00a0')
            i += 1
        elif c == '\n':
            out.append(' ')
            i += 1
        else:
            out.append(escape(c))
            i += 1
    return ''.join(out)


NARROW_NBSP = '\u202f'   # narrow no-break space


def french_spacing(t):
    """The facsimile's French spacing, rendered NON-BREAKING.

    The transcription sets an ordinary space; on screen it breaks at the
    end of a line and leaves an orphaned semicolon. We set a narrow space
    only where the facsimile put a space: never do we add one where the
    original has none -- the original alternates the two usages, and it is
    the original that is right.
    """
    t = re.sub(r' +([;:!?])', NARROW_NBSP + r'\1', t)
    t = re.sub(r'\u00ab +', '\u00ab' + NARROW_NBSP, t)
    t = re.sub(r' +\u00bb', NARROW_NBSP + '\u00bb', t)
    t = re.sub(r'  +', ' ', t)
    return t


def plain_text(h):
    """The text alone of an HTML fragment (for titles and headwords)."""
    return unescape(re.sub(r'<[^>]+>', '', h)).strip()


# ------------------------------------------------------------------
# 3 bis. THE HEADWORD OF A PARAGRAPH
# ------------------------------------------------------------------
# WHAT A HEADWORD IS, AND NOT WHAT IT LOOKS LIKE.
#
# The previous rule said: "a paragraph that opens in bold is a sub-entry".
# It was typographic, and the typography of 1925 does not separate what
# needs separating. The volume sets its headwords in bold (`anti.`,
# `-em-`, `Tra`, `B`) BUT ALSO its example sentences entire -- hence, in
# the panel, entries such as "El mortis, tri monati ante nun, pos longa
# sufri...". And conversely it writes true entries WITHOUT bold: the
# sixteen articles of the chapter PUNTIZADO (`Punto`, `Komo`,
# `Bi-punto`...) are in italic, and the chapter had no entry at all.
#
# The rule adopted therefore reads what the line DOES, not what it wears:
#
#   1. HEAD. After the optional folio reference and rule number
#      ("96. ---"), the paragraph must open with a set-off passage: bold,
#      italic or small capitals. That is the head.
#   2. CUT AT THE MARK OF DEFINITION. If the head itself carries "=", ":"
#      or an em dash, the headword is WHAT PRECEDES -- the volume sets
#      "Dum ke : dum ke il esis malada", entry then example, in a single
#      weight. A SENTENCE must still follow the mark: with no sentence,
#      the line is not a definition but an enumeration ("Pose : milion;
#      miliard"), and it opens nothing.
#   3. A HEADWORD IS SHORT: 80 characters and 12 words at most. This is a
#      guard rail and not the criterion -- the longest in the volume runs
#      to 63 ("Cadie, camatine, cavespere, casemane, canokte, camonate,
#      cayare"), and the two bounds reject no paragraph on their own.
#   4. A HEADWORD IS NOT A SENTENCE. This is the test that carries all the
#      work, and Ido makes it certain: a conjugated verb ends in -as, -is,
#      -os, -us or -ez, without exception. "La tero movas", "Me turnas la
#      roto", "Notez bone, ke..." are therefore examples, whatever their
#      weight. A sentence break in the middle of the head ("... pos longa
#      sufri. Qua pensabus...") says the same thing.
#   5. OUTSIDE BOLD, THE MARK IS REQUIRED. Bold serves in this volume only
#      for the headword or the example, and 4 excludes the example; but
#      italic serves EVERY cited word -- there are five thousand of them.
#      A head that is not in bold therefore counts only if a mark of
#      definition follows it: "=", ":", a full stop, a dash, or the
#      opening of a gloss "( [ { <<". That is what distinguishes "Punto
#      (.) uzesas...", an article, from "Polko, valso, e. c., esas dansi",
#      an example.
#
# What the rule lets through, and which we state rather than pass over in
# silence: "Nula -n" and "Anke nula -n en" (SINTAXO) are fragments of
# sentence, short and without a verb; nothing mechanical distinguishes
# them from a headword.
#
# No `^` anchor in these patterns: `Pattern.match(s, pos)` already sets
# the reading at `pos`, but `^` does not follow it there -- it holds only
# at the true beginning of the string. With it, every paragraph preceded
# by a space or by the folio reference escaped the reading.
FOLIO_HEAD = re.compile(r'<a class="fol"[^>]*>[^<]*</a>')
# "3. ---", "93. --", "16. --": the number, its full stop, its dash.
PARA_NUMBER = re.compile(r'\d+(?:\s*bis)?\.\s*[\u2014\u2013-]?\s*')
# THE NOTE CALL SET BEFORE THE HEAD. At folio 130 "equi-" and "ko-" carry
# one -- an asterisk to which no note answers, the original's typo, which
# we keep -- and it falls BEFORE the bold. The call is not the headword;
# nor must it prevent the headword being read, failing which the chapter
# PREFIXI TEKNIKALA had one entry out of the three the TABELO itself gives
# it: "Prefixi teknikala (equi-, ko-, mono-)".
CALL_BEFORE_HEAD = re.compile(r'(?:<a class="apelo"[^>]*>.*?</a>|\*)'
                       r'[\s\u00a0\u202f]*')
# The three ways the volume sets off a head. The flag says whether the
# weight suffices on its own (see 5 above).
SET_OFF_HEAD = ((re.compile(r'<b>(.*?)</b>'), True),
                 (re.compile(r'<i>(.*?)</i>'), False),
                 (re.compile(r'<span class="pk">(.*?)</span>'), False))
# GUARD RAIL, NOT CRITERION: it is the sentence test (4) that excludes the
# examples. The longest headword in the volume runs to 63 characters --
# "Cadie, camatine, cavespere, casemane, canokte, camonate, cayare" -- and
# the fullest to 10 words; at 80 characters and 12 words, these two bounds
# reject no paragraph today on their own.
HEADWORD_CHARS = 80
HEADWORD_WORDS = 12
# The mark of definition that FOLLOWS the head: "=", ":", a full stop, a
# dash, or the opening of a gloss.
DEF_MARK = re.compile(r'[\s\u00a0\u202f]*[=:.\u2013\u2014(\[{\u00ab]')
# The same mark, but INSIDE the head: there it cuts.
DEF_CUT = re.compile(r'[\s\u00a0\u202f][=:\u2013\u2014][\s\u00a0\u202f]')
# IDO'S CONJUGATED VERB. Five endings, no exception: the language was
# built for it. Two letters of root at least, so as not to read a verb in
# the morpheme "-as" of the chapter on the verb.
IDO_VERB = re.compile(r'(?<![-\w\u2011])(\w{2,}(?:as|is|os|us|ez))\b')
# The Ido words that carry a verbal ending without being verbs. All belong
# to the closed class -- adverbs and prepositions.
NOT_VERBS = {'plus', 'minus', 'depos', 'bis', 'gratis'}
# A sentence that ends another in the middle of the head.
SENTENCE_BREAK = re.compile(r'[.!?]\s+[A-Z\u00c0-\u00de]')


def is_sentence(t):
    """True if `t` is a SENTENCE and not a name.

    The conjugated verb is the proof. A proper name met in the run of the
    text -- "Paris", "Adolfus" -- carries the same ending without being a
    verb; we discard it only if it does not open the head, for a verb in
    the imperative does open one ("Notez bone, ke...").
    """
    for m in IDO_VERB.finditer(t):
        word = m.group(1)
        if word.lower() in NOT_VERBS:
            continue
        if m.start() > 0 and word[:1].isupper():
            continue
        return True
    return bool(SENTENCE_BREAK.search(t))


def headword(h):
    """(headword text, offset after the set-off head, head in bold).

    Returns (None, -1, False) when the paragraph carries none. The offset
    serves the chain button: it is set against the WHOLE head, not after
    its first piece -- failing which it would slip between the "e" and the
    "o" of folio 11. The third member says whether the facsimile set the
    head IN BOLD; that is what separates the cited word from the section
    heading (see 3 ter).
    """
    i = 0
    m = FOLIO_HEAD.match(h)
    if m:
        i = m.end()
    while i < len(h) and h[i] in ' \t\n':
        i += 1
    m = CALL_BEFORE_HEAD.match(h, i)
    if m:
        i = m.end()
    m = PARA_NUMBER.match(h, i)
    if m:
        i = m.end()
    m = CALL_BEFORE_HEAD.match(h, i)
    if m:
        i = m.end()
    for pattern, alone in SET_OFF_HEAD:
        m = pattern.match(h, i)
        if m:
            break
    else:
        return None, -1, False
    pieces, end = [m.group(1)], m.end()
    # THE HEAD IS WHAT THE FACSIMILE SET IN ONE PIECE, not what the
    # transcription cut into pieces. Two passages of the same weight rejoin
    # only if NOTHING bare separates them: the end of a line (`\nl`, a
    # space), the word break (`\cc`, nothing at all), or the comma of a
    # double headword -- "e, o" reads, "<b>a</b>, e <b>b</b>" does not.
    # Without this the article "Ante ke; pos ke; depos ke o de kande", which
    # the volume sets over two lines, lost its example and looked to be no
    # more than an enumeration.
    while True:
        for joiner in (', ', ' ', ''):
            if not h.startswith(joiner, end):
                continue
            m = pattern.match(h, end + len(joiner))
            if m:
                pieces.append(joiner + m.group(1))
                end = m.end()
                break
        else:
            break
    t = plain_text(''.join(pieces))
    if not t:
        return None, -1, False
    # 2. The mark of definition carried by the head itself.
    cut = False
    m = DEF_CUT.search(t)
    if m:
        before, after = t[:m.start()].strip(), t[m.end():].strip()
        if not is_sentence(after) or not before:
            return None, -1, False
        t, cut = before, True
    # 3. A headword is short.
    if len(t) > HEADWORD_CHARS or len(t.split()) > HEADWORD_WORDS:
        return None, -1, False
    # 4. A headword is not a sentence.
    if is_sentence(t):
        return None, -1, False
    # 5. Outside bold, the mark is required -- unless the head already
    #    carried its own, in which case it is proved.
    if not alone and not cut:
        carry_on = unescape(re.sub(r'<[^>]+>', '', h[end:]))
        if not DEF_MARK.match(carry_on):
            return None, -1, False
    return t, end, alone


# ------------------------------------------------------------------
# 3 ter. THE CASE OF THE HEADWORD
# ------------------------------------------------------------------
# TWO CLASSES OF ENTRY, AND ONE CASE FOR EACH.
#
# 1. THE CITED WORD -- "ube", "anti-", "-ul", "kam". The entry IS the Ido
#    form the article treats; its case is the word's. THE FACSIMILE'S
#    CAPITAL IS NOT THE WORD'S, IT IS THE PARAGRAPH'S: the volume sets its
#    entries in the run of the text, the one that opens a paragraph takes
#    the sentence capital, those that follow keep their lower case. The
#    word itself has not changed. Three proofs, taken from the
#    transcription:
#
#      -- folio 12, the consonants. The article for the first is numbered
#         ("3. --- B = b en l'Italiana"), the twenty-one others are not:
#         the panel listed "B, c, d, f, g, h...". One capital, and it is
#         the letter that carries it.
#      -- folios 62-63, the adverbs of place. "Interne" opens its
#         paragraph, "extere, supre, infre, avane, dope, latere, dextre,
#         sinistre, proxime, fore, cirkume" follow theirs: one capital for
#         eleven lower case, in ONE SINGLE enumeration.
#      -- the same word, twice, in both cases: "des-" at folio 124 and
#         "Des-" at folio 125. Nothing distinguishes them but the place in
#         the paragraph.
#
#    These entries therefore go to lower case, word by word -- "Seko di la
#    Vorti" would have gained nothing by keeping its capital in the middle
#    -- EXCEPT THE PROPER NAME. The transcription carries only five, and
#    the list can be checked: of 235 capitalised headwords, only 18 are
#    NEVER attested in lower case elsewhere in the volume, and 16 of those
#    18 are common words whose only use is the headword itself ("Tarde",
#    "Posmorge", "Puntaro"...).
#
# 2. THE SECTION HEADING -- "Punto", "Indikativo prezenta", "Adverbi di
#    quanteso", "Remarki". The entry cites nothing: it NAMES what the
#    article treats, in metalanguage. A heading carries the capital, and
#    it keeps it.
#
# WHAT SEPARATES THE TWO: THE WEIGHT. The volume reserves bold for Ido
# forms -- this is already what rule 5 of `headword()` says -- and sets in
# ITALIC or SMALL CAPITALS what is not cited but named: the sixteen
# articles of PUNTIZADO, the paradigm of VERBO, the topics of VORTORDINO.
# The 38 entries so set are all headings, without exception.
#
# WHAT THE RULE DOES NOT READ, AND WHICH WE NAME RATHER THAN PASS OVER:
# six headings that the facsimile sets IN BOLD, in the place and in the
# exact form of a cited word -- "Radiki. --- Li esas verbala o nomala" is
# in no way distinguishable from "anti. --- Ta prefixo esis l'objekto di
# la decido". No mechanical mark separates them; we therefore name them
# one by one.
BOLD_HEADINGS = {
    'La plaso dil komplemento di irga prepoziciono',
    'Radiki.', 'Dezinenci.', 'Konsequo.', 'Praktikal moyeno.',
    'Konsequi.',
}
PROPER_NAMES = {'Europa', 'Afrika', 'Amerika', 'Azia', 'Usa'}
# What bounds a word: the space and the punctuation of a list. The full
# stop is among them -- "Radiki." reads "Radiki" -- and the hyphen is not:
# "Duadek-e-ok" is one word.
HEADWORD_WORD = re.compile(r'[^\s,;:.()\[\]\u00ab\u00bb]+')


def headword_case(t, bold):
    """The case of the class: the word's, or a heading's.

    The section heading takes the capital and keeps it -- the volume gives
    it one everywhere, save on the four lines of folio 48 which it writes
    in lower case and which folio 49 takes up in capitals ("antea pasinto"
    / "Antea pasinto"): an entry in the panel cannot depend on the place of
    a paragraph, nor may the same heading appear there twice in two ways.
    """
    if not t:
        return t
    if not bold or t in BOLD_HEADINGS:
        return t[:1].upper() + t[1:]

    def bas(m):
        word = m.group(0)
        if word in PROPER_NAMES:
            return word
        return word[:1].lower() + word[1:]

    return HEADWORD_WORD.sub(bas, t)


# 4. THE TRAVERSAL OF THE TRANSCRIPTION
# ------------------------------------------------------------------
# Block macros whose argument is thrown away: they lay only white space, a
# rule or an ornament -- that is, page layout.
SILENT = {
    'VUsaut': 1, 'VUblanc': 1, 'VUblancAlinea': 0, 'VUinterlignePage': 1,
    'VUpageSerre': 2, 'VUfilet': 1, 'VUfiletnote': 0, 'VUfleuron': 0,
    'VUpageIndex': 0, 'vspace': 1, 'vspace*': 1, 'setlength': 2,
    'renewcommand': 2, 'newcommand': 2, 'VUmarqueCachee': 0,
    'nointerlineskip': 0, 'VUplanche': 1, 'VUimageA': 3, 'VUfolio': 1,
}
SILENT_OPT = {'VUornement': 1, 'VUfiletA': 2, 'VUplancheA': 2}
# The TABELO entries: the reading page does not take them up.
INDEX = {'VUindex': 3, 'VUindexNu': 3, 'VUindexLarge': 3}


class Block(object):
    __slots__ = ('kind', 'frags', 'chap', 'head', 'html', 'notes_here', 'x',
                 'ident', 'notice')

    def __init__(self, kind, frags=None, html=None, x=0.0):
        self.kind = kind        # tit sub p cen fer rango tab
        self.frags = frags or []  # [(leaf, folio, html)]
        self.html = html
        self.chap = None
        self.head = None
        self.notes_here = []            # notes attached to this block
        self.ident = None
        self.notice = None          # editor's notice laid under the block
        self.x = x


class Transcription(object):

    def __init__(self):
        self.blocks = []
        self.chapters = []       # {title, block, leaf, folio, part}
        self.notes = OrderedDict()  # (leaf, number) -> {'html','id'}
        self.page_notes = {}      # leaf -> [numbers]
        self.pages = []           # (leaf, folio)
        self.leaf = 0
        self.folio = 0
        self.folios = {}
        self.cur = []             # fragments of the paragraph in hand
        self.carry_on = False        # the next paragraph rejoins the previous one
        self.parplein = False     # \parplein seen, and nothing set since
        self.last_note = None
        self.note_size_page = False    # whole page set at the size of the notes
        self.rows = []           # table being built up
        self.centred = False       # ... and whether it is centred on the measure
        self.apparatus = []
        self.parts_seen = []

    # -- paragraphs -------------------------------------------------
    def add(self, t):
        if not t:
            return
        self.parplein = False
        if self.cur and self.cur[-1][0] == self.leaf:
            self.cur[-1][2] += t
        else:
            self.cur.append([self.leaf, self.folio, t])

    def close_para(self, flush=True):
        """Close the paragraph in hand, and REJOIN it to the previous one if
        the transcription says it is no more than its continuation.

        Two marks, and only one is authoritative. `\\VUcontinue` opens a
        paragraph that resumes flush left: it is the facsimile's own mark,
        and it cannot be read otherwise. `\\parplein`, for its part, reads
        from the other edge -- it justifies the last line of a page -- but
        the transcription also uses it mid-page, for a paragraph whose last
        line fills the measure without continuing anything at all (65 uses
        out of 114). It therefore counts only WHEN IT ENDS A PAGE, and we
        rejoin then only if nothing has been set since."""
        if flush:
            self.flush_rows()
        frags = [(f, fo, french_spacing(h)) for f, fo, h in self.cur
                 if h.strip()]
        self.cur = []
        if not frags:
            return
        prev = None
        for b in reversed(self.blocks):
            if b.kind == 'p':
                prev = b
                break
            if b.kind not in ('cen', 'orn', 'fer'):
                break
        if self.carry_on and prev is not None:
            prev.frags = prev.frags + frags
            self.carry_on = False
            return
        self.carry_on = False
        b = Block('p', frags)
        t, _, bold = headword(frags[0][2])
        b.head = headword_case(t, bold)
        self.blocks.append(b)

    # -- tables -----------------------------------------------------
    def flush_rows(self):
        if not self.rows:
            return
        rows, self.rows = self.rows, []
        centred, self.centred = self.centred, False
        self.blocks.append(table_html(rows, self.leaf, self.folio,
                                  centred))

    # -- notes ------------------------------------------------------
    def note(self, body):
        """Unstack a \\VUnotes block into numbered notes.

        A page's block carries the notes called IN that page, and numbers
        them from (1) -- or from (*) when the facsimile uses the asterisk.
        A paragraph that does not open with a call is the continuation of
        the previous note: continuation on the same page (a new paragraph
        of the note), or continuation from the page before when the note
        overruns -- and then the sentence must be rejoined, not a paragraph
        opened (folios 203-204).
        """
        f = self.leaf
        self.page_notes.setdefault(f, [])
        # What, in a note, is only page layout.
        body = re.sub(r'\\(VUblancAlinea|VUcontinue|parplein)(?![A-Za-z])',
                       '', body)
        body = re.sub(r'\\(VUblanc|VUsaut)\{[^{}]*\}', '', body)
        current = None
        first = True
        for para in re.split(r'\n\s*\n', body):
            if not para.strip():
                continue
            h = french_spacing(inline(para))
            if not plain_text(h):
                continue
            # A note's mark, as the facsimile writes it: "(1)", "(*)" -- or a
            # BARE ASTERISK, on leaves 74 and 122. The last was not read: the
            # paragraph, having no recognised mark, passed for the continuation
            # of the previous note and was welded to it. On leaf 122 the note
            # "Bibliografio" thus ended up stuck to note (2) of the page before,
            # and the asterisk of the title "REGULI DI DERIVADO *" no longer
            # called anything.
            #
            # The call to look for in the text is kept AS IT IS: a note marked
            # "(*)" (leaves 166, 191, 208) is called by "(*)", a note marked with
            # a bare asterisk by a bare asterisk. Confusing them would have broken
            # the former.
            bare = plain_text(h).lstrip()
            m = re.match(r'\((\d+|\*)\)', bare) or re.match(r'(\*)', bare)
            if m:
                num = m.group(1)
                key = (f, num)
                self.notes[key] = {'paras': [h.strip()], 'id': 'nt%d-%s' % (f, num),
                                   'leaf': f, 'num': num, 'block': None,
                                   'apel': m.group(0)}
                self.page_notes[f].append(num)
                current = key
            elif first and current is None and self.last_note:
                # Head of block with no call: the note from the previous page
                # continues, and the sentence rejoins.
                target = self.last_note
                # A NOTE THAT SPANS TWO PAGES rejoins without a space only if
                # it ends on a WORD BREAK. Without this test, "... esas sempre"
                # and "plu sekura ..." gave "sempreplu": the fragment ended on a
                # whole word, and a space was needed. The silent rejoining stays
                # right when the mark is a \cc, which extraction has already
                # resolved by welding the two halves.
                self.n_rejoined = getattr(self, 'n_rejoined', 0)
                _prev_para = self.notes[target]['paras'][-1]
                if _prev_para and not _prev_para.endswith(('-', '\u2011')) \
                        and not _prev_para.rstrip().endswith('-') \
                        and h[:1] not in ('', ' '):
                    _prev_para = _prev_para.rstrip() + ' '
                    self.n_rejoined += 1
                self.notes[target]['paras'][-1] = _prev_para + h.lstrip()
                current = target
            elif current is not None:
                self.notes[current]['paras'].append(h.strip())
            first = False
        if current:
            self.last_note = current

    # -- pages ------------------------------------------------------
    def page(self, leaf, folio, body):
        self.leaf = leaf
        self.folio = self.folios[leaf]
        self.pages.append((leaf, self.folio))
        # A \parplein that ended the previous page: the paragraph
        # continues here, even if the transcriber did not set \VUcontinue.
        if self.parplein:
            self.carry_on = True
            self.parplein = False
        if getattr(self, 'asterism', False):
            # no large skip has appeared: better the asterism misplaced
            # than lost. We lay it before changing page.
            self.close_para()
            self.blocks.append(Block('orn', [(self.leaf, self.folio,
                                            '\u2042')]))
        self.asterism = False
        self.note_size_page = False
        self.apparatus = []
        # The newline that follows \begin{VUpage} is not text: left as it
        # is, it opened a space at the head of the page and separated the
        # two halves of a word broken on the previous leaf.
        self.page_blocks(body.lstrip(' \n\t'))
        self.flush_rows()
        for y, h in sorted(self.apparatus):
            if y >= APPARATUS_THRESHOLD:
                self.blocks.append(Block('cen', [(leaf, self.folio, h)]))

    def page_blocks(self, s):
        """Traversal of a page at the level of BLOCKS. Anything that is not a
        block macro falls into the paragraph in hand."""
        i, n = 0, len(s)
        buffer = []

        def flush_buffer():
            if buffer:
                self.add(inline(''.join(buffer)))
                del buffer[:]

        while i < n:
            # blank line = end of paragraph
            m = re.match(r'\n[ \t]*\n\s*', s[i:])
            if m:
                flush_buffer()
                self.close_para()
                i += m.end()
                continue
            if s[i] == '\\':
                mm_ = re.match(r'\\([A-Za-z]+\*?)', s[i:])
                if mm_:
                    name = mm_.group(1)
                    j = i + mm_.end()
                    handled, i2 = self.block_macro(name, s, j, flush_buffer)
                    if handled:
                        i = i2
                        continue
            buffer.append(s[i])
            i += 1
        flush_buffer()
        self.close_para()

    def block_macro(self, name, s, i, flush_buffer):
        """Returns (handled, position). Inline macros are left to the text
        converter."""
        # BEFORE the silent macros: without this \VUsaut is swallowed here
        # and the waiting asterism never finds its skip.
        if name == 'VUsaut' and getattr(self, 'asterism', False):
            _, args, i = read_args(s, i, 1)
            v = re.match(r'\s*(-?[\d.]+)\s*mm', args[0] or '')
            if v and float(v.group(1)) >= 5.0:
                self.close_para()
                self.blocks.append(Block('orn', [(self.leaf, self.folio,
                                                '\u2042')]))
                self.asterism = False
            return True, i
        if name in SILENT:
            _, _, i = read_args(s, i, SILENT[name])
            return True, i
        if name in SILENT_OPT:
            _, _, i = read_args(s, i, SILENT_OPT[name], opt=True)
            return True, i
        if name in INDEX:
            _, _, i = read_args(s, i, INDEX[name], opt=True)
            return True, i
        if name == 'VUnotes':
            flush_buffer()
            _, args, i = read_args(s, i, 2, opt=True)
            self.note(args[1])
            return True, i
        if name == 'VUpageNote':
            _, _, i = read_args(s, i, 1)
            self.note_size_page = True
            return True, i
        if name in ('VUtitre', 'VUsoustitre', 'VUcentre'):
            flush_buffer()
            self.close_para()
            _, args, i = read_args(s, i, 3)
            h = french_spacing(inline(args[2]).strip())
            kind = {'VUtitre': 'tit', 'VUsoustitre': 'sub',
                     'VUcentre': 'cen'}[name]
            self.parplein = False
            b = Block(kind, [(self.leaf, self.folio, h)])
            self.blocks.append(b)
            if kind == 'tit':
                self.chapters.append({'title': plain_text(h), 'block': b,
                                       'leaf': self.leaf,
                                       'folio': self.folio})
            return True, i
        if name in ('VUcentreA', 'VUcentreDA', 'VUsignature', 'VUcaseA'):
            flush_buffer()
            nb = {'VUcentreA': 4, 'VUcentreDA': 5, 'VUsignature': 2,
                  'VUcaseA': 5}[name]
            _, args, i = read_args(s, i, nb)
            y = mm(args[0])
            if name == 'VUcaseA':
                h = (french_spacing(inline(args[3]).strip()) + ' \u00b7 '
                     + french_spacing(inline(args[4]).strip()))
            else:
                h = french_spacing(inline(args[-1]).strip())
            if name == 'VUsignature' and re.fullmatch(r'[0-9]+\*?', h or ''):
                # Gathering signature: a printer's mark at the foot of the first
                # page of a gathering, not a word of the volume.
                h = ''
            if h:
                self.apparatus.append((y, h))
                if y < APPARATUS_THRESHOLD:
                    # Apparatus line at the head of a page: on the preliminary
                    # pages this is the title of the piece (KONSTATO.), and it
                    # opens a chapter as a \VUtitre does.
                    b = Block('tit', [(self.leaf, self.folio, h)])
                    self.blocks.append(b)
                    self.chapters.append({'title': plain_text(h), 'block': b,
                                           'leaf': self.leaf,
                                           'folio': self.folio})
            return True, i
        if name == 'VUauFer':
            flush_buffer()
            self.close_para()
            _, args, i = read_args(s, i, 2)
            self.parplein = False
            self.blocks.append(Block('fer', [(self.leaf, self.folio,
                                            french_spacing(inline(args[1])))]))
            return True, i
        if name == 'VUasterismo':
            # THE ASTERISM IS LAID AT AN ABSOLUTE ORDINATE, and declared at
            # the head of the page like every element of null height: taking
            # it where it is written would place it at the top of the page.
            # At folio 209 it fell between "c)" and "d)" whereas the facsimile
            # lays it far lower, above "On dicis". The volume's rule says where
            # to put it back: an element laid at an absolute ordinate DOES NOT
            # OPEN ITS OWN WHITE SPACE, it needs a matching \VUsaut in the
            # flow. It is therefore to that skip that the asterism belongs. We
            # hold it back and lay it at the first large skip on the same page.
            _, _, i = read_args(s, i, 1)
            self.asterism = True
            return True, i
        if name == 'VUtabloCentrita':
            # Sets nothing: it says only that the table which follows is
            # centred on the measure. It precedes the rows, so it must not
            # close the table in hand.
            flush_buffer()
            self.centred = True
            return True, i
        if name == 'VUrang':
            flush_buffer()
            # Without `flush=False`, each row would close the table the
            # previous row had just opened: a table of six rows came out as
            # six tables of one row.
            self.close_para(flush=False)
            _, args, i = read_args(s, i, 1)
            self.parplein = False
            self.rows.append(row_cells(args[0]))
            return True, i
        if name == 'parplein':
            flush_buffer()
            # \parplein stands in for the page's last line mark: the line does
            # end, it is simply justified. Without this space, the paragraph
            # rejoined on the next page would weld two words together (folio 7:
            # "renkontrar" + "en l'uzado").
            self.add(' ')
            self.close_para()
            self.parplein = True
            return True, skip_space(s, i)
        if name == 'VUcontinue':
            flush_buffer()
            # Continuation of the previous page's paragraph: we rejoin.
            self.carry_on = bool(self.blocks)
            self.parplein = False
            return True, skip_space(s, i)
        return False, i


# Not the baselines of the body: \VUinterligne from the preamble. None
# of the pages with tables calls \VUinterlignePage, so this pitch holds
# for all of them; it serves to read the HEIGHT of a brace as a NUMBER OF
# ROWS.
LINE_PITCH = 9.99 * 25.4 / 72.27      # mm
# What separates two cells of the same row once the columns are undone: a
# space does not suffice, "Petrus Paulus Ioannes Maria" would read as a
# sentence.
CELL_GAP = '<span class="ec"></span>'


def row_cells(s):
    """The \\VUcase of one row.

    Each cell returns a dictionary: its measured abscissa, its HTML, and
    -- if it is a brace -- its height and the displacement of its centre,
    as the transcriber measured them on the facsimile. Those two numbers
    are the only thing that says HOW MANY ROWS the brace gathers: it is
    from them that the grouping is deduced.
    """
    out = []
    i = 0
    while i < len(s):
        m = re.compile(r'\\VUcase\b').search(s, i)
        if not m:
            break
        _, args, i = read_args(s, m.end(), 2)
        raw = args[1]
        a = re.search(r'\\VUaccolade(D|H)?\{([^{}]*)\}(?:\{([^{}]*)\})?', raw)
        kind, height, gap = None, 0.0, 0.0
        if a:
            kind = {'': 'akol', 'D': 'akolD', 'H': 'akolH'}[a.group(1) or '']
            height, gap = mm(a.group(2)), mm(a.group(3) or '0pt')
        # The vertical offset of an ORDINARY cell. At folio 31 "de o ek"
        # and "Superlativo" are not on a row of the table: the facsimile
        # lays them HALFWAY between two, and the transcription says so with
        # \VUdecale. The number was until now lost -- the cell fell back
        # onto the row above, far from the point of its brace. A brace's own
        # offset is not read here: it already has its own (folio 220).
        d = re.search(r'\\VUdecale\{([^{}]*)\}', raw)
        offset = mm(d.group(1)) if (d and kind is None) else 0.0
        out.append({'x': mm(args[0]), 'h': french_spacing(inline(raw).strip()),
                    'k': kind, 'height': height, 'gap': gap,
                    'offset': offset})
    return out


def merge_leaders(rows):
    """Leader dots are not cells.

    The transcription lays them one by one, at their measured abscissa.
    Left as they are, they open five empty columns per table, and the
    numbers stop lining up from one row to the next. We fold them back
    into the cell that precedes them -- so they have a cell nowhere."""
    clean = []
    for r in rows:
        merged = []
        for c in r:
            if plain_text(c['h']) == '.' and merged \
                    and set(plain_text(merged[-1]['h'])) == {'.'}:
                merged[-1] = dict(merged[-1], h=merged[-1]['h'] + '.')
            else:
                merged.append(c)
        line = []
        for c in merged:
            if set(plain_text(c['h'])) == {'.'} and len(plain_text(c['h'])) > 1:
                c = dict(c, h='<span class="kond">%s</span>' % c['h'],
                         k='kond')
                if line and line[-1]['k'] not in ('akol', 'akolD',
                                                    'akolH'):
                    line[-1] = dict(line[-1],
                                     h=line[-1]['h'] + ' ' + c['h'])
                    continue
            line.append(c)
        clean.append(line)
    return clean


# ------------------------------------------------------------------
# 4 bis. WHAT THE BRACE MEANS
# ------------------------------------------------------------------
# A grid of columns renders the POSITION of the words; it does not render
# what the facsimile's brace states, which is a GROUPING: a term, and the
# forms it caps. On a narrow screen the grid scatters and the brace floats
# alone in its cell -- folio 31 becomes undecipherable there.
#
# The grouping is not guessed: it is MEASURED. `\VUaccolade{h}{d}` gives
# the height of the brace and the displacement of its centre; the height
# divided by the line pitch gives the number of rows gathered, the
# displacement says on which row the centre falls. At folio 31: 27.2 pt =
# 3 rows centred on the second, 15.7 pt = 2 rows, 17.4 pt = 2 rows. It is
# the facsimile that says so, not the tool that supposes it.
def span(c, r, total):
    """The rows a brace laid at row `r` caps: (first, count). Its measured
    height divided by the line pitch gives the number of rows, the
    displacement of its centre says where they begin. It is the same
    measurement that serves the rendering in groups and the grid: a
    brace's cell spans its rows (rowspan), and the path stretches over
    them."""
    n = max(1, int(round(c['height'] / LINE_PITCH)))
    centred = r - c['gap'] / LINE_PITCH
    a = int(round(centred - (n - 1) / 2.0))
    return max(0, min(a, total - n)), n


def groups(rows):
    """The groups that the opening braces gather."""
    gs = []
    for r, line in enumerate(rows):
        for c in line:
            if c['k'] == 'akol':
                a, n = span(c, r, len(rows))
                gs.append({'rows': list(range(a, a + n)), 'x': c['x'],
                           'brace': c, 'title': None, 'children': []})
            elif c['k'] == 'akolH':
                # The HORIZONTAL brace of folio 220: point at the top, it
                # attaches the row carrying it to the row above.
                gs.append({'rows': [r], 'x': c['x'], 'brace': c,
                           'title': None, 'children': [], 'points_up': True})
    for g in gs:
        cands = [c for r in g['rows'] for c in rows[r]
                 if c['x'] < g['x'] and c['k'] not in ('akol', 'akolD',
                                                       'akolH', 'kond')]
        if not cands:
            # The plate of folio 220 has nothing but dots for material:
            # the row of dots to the left of the brace IS the term it caps
            # ("un lineo unlatere").
            cands = [c for r in g['rows'] for c in rows[r]
                     if c['x'] < g['x'] and c['k'] == 'kond']
        if g.get('points_up'):
            # Its title is on the previous row, not to its left.
            r0 = g['rows'][0] - 1
            cands = [c for c in (rows[r0] if r0 >= 0 else [])
                     if c['k'] is None]
            g['title'] = cands[-1] if cands else None
            if g['title'] is not None:
                g['rang_titre'] = r0
        elif cands:
            g['title'] = max(cands, key=lambda c: c['x'])
            g['rang_titre'] = [r for r in g['rows']
                               if g['title'] in rows[r]][0]
    gs = [g for g in gs if g['title'] is not None]
    # One group nests inside another when its TITLE is one of the other's
    # members -- and not when its rows are contained in them: at folio 31
    # the two lower groups overlap by one row without either containing the
    # other, and it is indeed "relatanta", title of the first, that is a
    # member of the second.
    for g in gs:
        parents = [h for h in gs if h is not g and h['x'] < g['x']
                 and g.get('rang_titre') in h['rows']
                 and g['title'] is not h['title']]
        g['parent'] = min(parents, key=lambda h: len(h['rows'])) if parents else None
    for g in gs:
        if g['parent'] is not None:
            g['parent']['children'].append(g)
    return closers(rows, gs)


def closers(rows, gs):
    """The CLOSING braces, and the place they take in the tree.

    An opening brace names ON THE LEFT what it gathers on the right; a
    closing one does the reverse. The volume carries only one, at folio
    31: it attaches "maxim" and "minim" to "de o ek". For want of being
    read, it opened no group and stayed an INLINE brace, one row tall,
    set against "maxim" alone -- which is not what the facsimile says.

    Its span is measured like the others' (`span`). What it encloses are
    the opening groups ALL of whose rows fall within its own: at folio 31
    the group "relatanta". It then slips between them and their parent --
    "Superlativo" -- so that the tree stays a tree and the rows covered do
    not change.
    """
    total = len(rows)
    for r, line in enumerate(rows):
        for c in line:
            if c['k'] != 'akolD':
                continue
            a, n = span(c, r, total)
            g = {'rows': list(range(a, a + n)), 'x': c['x'], 'brace': c,
                 'title': None, 'children': [], 'parent': None, 'closing': True}
            # Its title is on the RIGHT, and it is the nearest.
            cands = [d for q in g['rows'] for d in rows[q]
                     if d['x'] > g['x'] and d['k'] is None]
            if not cands:
                continue
            g['title'] = min(cands, key=lambda d: d['x'])
            g['rang_titre'] = [q for q in g['rows']
                               if g['title'] in rows[q]][0]
            inside = [h for h in gs if not h.get('closing')
                      and rows_covered(h) <= set(g['rows'])]
            # The most enclosing of them: those whose parent lies outside
            # the closing brace. It is they that become its children; it
            # takes their place beside their parent.
            roots = [h for h in inside if h['parent'] not in inside]
            # WHEN IT COVERS EXACTLY ONE GROUP, it does not make one more
            # storey: it is laid at the end of the same one. The facsimile
            # does not show two nested bands but ONE band of two rows, held
            # between an opening brace on the left and a closing one on the
            # right -- and the superfluous storey cost, on a tablet screen,
            # the few pixels by which the "k" of "de o ek" left the panel.
            if len(roots) == 1 \
                    and rows_covered(roots[0]) == set(g['rows']):
                h = roots[0]
                h['ferme_brace'], h['ferme_titre'] = c, g['title']
                continue
            g['parent'] = roots[0]['parent'] if roots else None
            for h in roots:
                if h['parent'] is not None:
                    h['parent']['children'].remove(h)
                h['parent'] = g
                g['children'].append(h)
            if g['parent'] is not None:
                g['parent']['children'].append(g)
            gs.append(g)
    return gs


def rows_covered(g):
    s = set(g['rows']) | {g.get('rang_titre')}
    for e in g['children']:
        s |= rows_covered(e)
    return {r for r in s if r is not None}


def render_group(g, rows, taken):
    """A group: its title, the brace, then its members.

    The brace is no longer replaced by a rule: it is the facsimile's own
    path that is laid between the title and the members, and the CSS
    stretches it over their whole height. The group with the point at the
    top -- the family tree of folio 220 -- stacks the same three pieces
    from top to bottom instead of ranging them left to right: title,
    horizontal brace, members.
    """
    taken.add(id(g['brace']))
    taken.add(id(g['title']))
    # The closing brace laid at the end of the same group: reserved now,
    # or the traversal would count it among the members.
    suffix = ''
    if g.get('ferme_brace') is not None:
        taken.add(id(g['ferme_brace']))
        taken.add(id(g['ferme_titre']))
        suffix = ('%s<div class="gr-t">%s</div>'
                   % (g['ferme_brace']['h'], g['ferme_titre']['h']))
    members = []
    # The closing brace is the same piece reversed: what it gathers is on
    # its LEFT, and the name it gives them on its right.
    close_para = g.get('closing', False)
    covered_set = sorted(rows_covered(g))
    for r in covered_set:
        child = None
        for e in g['children']:
            if r in rows_covered(e):
                child = e
                break
        if child is not None:
            if r == min(rows_covered(child)):
                members.append(render_group(child, rows, taken))
            continue
        cells = [c for c in rows[r]
                 if (c['x'] < g['x'] if close_para else c['x'] > g['x'])
                 and id(c) not in taken and c is not g['title']]
        for c in cells:
            taken.add(id(c))
        if cells:
            members.append('<div class="gr-m">%s</div>' % CELL_GAP.join(
                c['h'] for c in cells))
    if close_para:
        return ('<div class="gr gd"><div class="gr-l">%s</div>%s'
                '<div class="gr-t">%s</div></div>'
                % (''.join(members), g['brace']['h'], g['title']['h']))
    css_class = ' grh' if g.get('points_up') else (' gf' if suffix else '')
    return ('<div class="gr%s"><div class="gr-t">%s</div>%s'
            '<div class="gr-l">%s</div>%s</div>'
            % (css_class, g['title']['h'],
               g['brace']['h'], ''.join(members), suffix))


def edge(g, rows):
    """The leftmost abscissa a group occupies.

    What, on a row, falls TO THE LEFT of a group without belonging to it
    -- the number "28." at folio 31 -- is recognised by this. Comparing it
    with the BRACE's abscissa sufficed as long as they all opened to the
    right: the title was then the leftmost piece. A closing brace ranges
    its members to the left of its stroke; measuring them against it would
    have put them outside, then inside, hence twice.
    """
    xs = [g['title']['x'], g['x']]
    if g.get('closing'):
        xs += [c['x'] for r in rows_covered(g) for c in rows[r]
               if c['x'] < g['x']]
    xs += [edge(e, rows) for e in g['children']]
    return min(xs)


def render_groups(rows, gs, alone_flag=False):
    """The whole table, rendered in groups: whatever belongs to no brace
    stays a line, in the facsimile's order."""
    taken = set()
    stems = [g for g in gs if g['parent'] is None]
    opens = {}
    for g in stems:
        opens.setdefault(min(rows_covered(g)), []).append(g)
    covered = {}
    for g in stems:
        for r in rows_covered(g):
            covered[r] = g
    out = []
    for r in range(len(rows)):
        # What, on this row, falls TO THE LEFT of the brace without being its
        # title: at folio 31, the paragraph number "28.".
        g = covered.get(r)
        if g is not None:
            before = [c for c in rows[r] if c['x'] < edge(g, rows)
                     and c is not g['title'] and c['k'] != 'akol'
                     and id(c) not in taken]
            for c in before:
                taken.add(id(c))
                out.append('<div class="gr-x">%s</div>' % c['h'])
        for gg in opens.get(r, []):
            out.append(render_group(gg, rows, taken))
        if g is None:
            cells = [c for c in rows[r] if id(c) not in taken]
            if cells:
                out.append('<div class="gr-x">%s</div>'
                           % CELL_GAP.join(c['h'] for c in cells))
    # `alone`: the rendering in groups is the ONLY one -- it therefore
    # appears on a wide screen too, where the rule that hides it must not
    # reach it.
    return '<div class="grupi%s">%s</div>' % (' sola' if alone_flag else '',
                                              ''.join(out))


def table_html(rows, leaf, folio, centred=False):
    """Render a run of \\VUrang.

    Three possible outputs, according to what the transcription holds:
      -- a row of a single cell is not a table, it is a set-off line: it
         keeps its measured indent;
      -- a table with no brace comes out as a <table>, its columns
         recovered by grouping nearby abscissas (5 mm from one to the
         next), which is wide against the play of the measurement and
         narrow against the spacing of the volume's columns;
      -- a table WITH BRACES comes out TWICE: in columns for the wide
         screen, in groups for the narrow one. The CSS shows only one at a
         time. The horizontal brace, for its part, comes out in groups
         only: its grid says nothing to anybody.
    """
    clean = merge_leaders(rows)

    if all(len(r) <= 1 for r in clean):
        h = ''.join('<div class="rango" style="padding-left:%.1f%%">%s</div>'
                    % (min(c['x'] / 91.69 * 100, 60), c['h'])
                    for r in clean for c in r)
        return Block('rango', [(leaf, folio, h)])

    gs = groups(clean)
    horizontal = any(c['k'] == 'akolH' for r in clean for c in r)

    # The columns. Nearby abscissas are grouped (5 mm from one to the next),
    # which is wide against the play of the measurement and narrow against
    # the spacing of the volume's columns.
    #
    # BUT a brace no longer shares the text's cell. As long as it did --
    # stuck to the left of "egaleso" at folio 31, of the leader dots at
    # folio 220 -- no cell belonged to it in its own right, so nothing could
    # span the rows it caps. It therefore detaches from its group and takes
    # a column TO ITS LEFT: at folio 31 as at folio 220 the brace always
    # precedes what it gathers. The rest of the group remains ONE column --
    # without which "Komparativo" and "relatanta", which the brace separates
    # by 5.7 mm, would have ranged in two columns and the table of folio 31
    # would have gaped.
    AK = ('akol', 'akolD', 'akolH')
    axes = sorted({(c['x'], c['k'] in AK) for r in clean for c in r})
    chunks, prev = [], None
    for x, ak in axes:
        if prev is None or x - prev > 5.0:
            chunks.append([])
        chunks[-1].append((x, ak))
        prev = x
    cols = []
    for p in chunks:
        prev = None
        for x, ak in p:
            if ak and (prev is None or x - prev > 5.0):
                cols.append((x, True))
            if ak:
                prev = x
        text = [x for x, ak in p if not ak]
        if text:
            cols.append((min(text), False))

    def column(c):
        """The column of a cell: the nearest OF THE SAME NATURE."""
        ak = c['k'] in AK
        cand = [j for j in range(len(cols)) if cols[j][1] == ak]
        return min(cand or range(len(cols)),
                   key=lambda j: abs(cols[j][0] - c['x']))

    # A brace's cell spans the rows it caps: it is carried to the first
    # of them, with the rowspan the measurement gives, and the following
    # rows no longer open a cell in that column. It is that cell, three
    # rows tall at folio 220, that the path fills.
    grid = [[[] for _ in cols] for _ in clean]
    scope, sub, mid = {}, set(), set()
    for r, line in enumerate(clean):
        for c in line:
            j = column(c)
            if c['k'] in ('akol', 'akolD'):
                a, n = span(c, r, len(clean))
                if n > 1 and all(not grid[q][j] and (q, j) not in sub
                                 for q in range(a, a + n)):
                    grid[a][j].append(c['h'])
                    scope[(a, j)] = n
                    sub.update((q, j) for q in range(a + 1, a + n))
                    continue
            # The cell the facsimile lays HALFWAY between two rows. In
            # columns it cannot float: it takes the two rows it straddles
            # and centres itself in them -- which puts it back opposite the
            # point of its brace, which covers the same two rows. Without
            # this "de o ek" stayed stuck to the row of "maxim", half a
            # line too high.
            if c['offset']:
                pos = r - c['offset'] / LINE_PITCH
                a = int(pos)
                if abs(pos - a - 0.5) < 0.25 and 0 <= a < len(clean) - 1 \
                        and all(not grid[q][j] and (q, j) not in sub
                                for q in (a, a + 1)):
                    grid[a][j].append(c['h'])
                    scope[(a, j)] = 2
                    mid.add((a, j))
                    sub.add((a + 1, j))
                    continue
            grid[r][j].append(c['h'])
    lines = []
    for r in range(len(clean)):
        tds = []
        for j in range(len(cols)):
            if (r, j) in sub:
                continue
            n = scope.get((r, j), 1)
            kl = (['ak'] if cols[j][1] else []) \
                + (['mez'] if (r, j) in mid else [])
            tds.append('<td%s%s>%s</td>'
                       % (' class="%s"' % ' '.join(kl) if kl else '',
                          ' rowspan="%d"' % n if n > 1 else '',
                          ' '.join(grid[r][j])))
        lines.append('<tr>' + ''.join(tds) + '</tr>')
    table = '<table class="tab">' + ''.join(lines) + '</table>'

    # The table the facsimile centres on the measure (marked by
    # \VUtabloCentrita, from the scan) must be centred too in a column
    # whose width is not the volume's: it is the ratio to the measure that
    # carries over, not the indent in millimetres.
    def rendered(x):
        return ('<div class="centrita">%s</div>' % x) if centred else x

    if not gs:
        return Block('tab', [(leaf, folio, rendered(table))])
    if horizontal:
        return Block('tab', [(leaf, folio,
                             rendered(render_groups(clean, gs, alone_flag=True)))])
    return Block('tab', [(leaf, folio,
                         rendered('<div class="larja">%s</div>%s'
                               % (table, render_groups(clean, gs))))])


def folio_table(pages):
    """leaf -> folio, for every page of the volume.

    The folio is not printed on every page: not on those opening a part,
    nor on those opening a chapter, nor on the blanks. Taking it "from the
    last one known" suffices as long as one reads in order, but not at the
    head: the first leaf read (8, the KONSTATO) precedes the first printed
    folio (6, on leaf 10) and would therefore have no antecedent. We
    interpolate instead from the NEAREST known folio, before or after --
    one leaf is one folio, without exception in this volume.
    """
    known = sorted((f, fo) for f, fo in pages if fo is not None)
    table = {}
    for f, _ in pages:
        g, fo = min(known, key=lambda c: abs(c[0] - f))
        table[f] = fo + (f - g)
    return table


# ------------------------------------------------------------------
# 5. THE NOTE CALLS
# ------------------------------------------------------------------
def attach_notes(rel):
    """Attach each note to the call that asks for it.

    A page's \\VUnotes block carries the notes called IN that page and
    numbers them from (1): it is therefore in that page's fragments, and
    nowhere else, that `(n)` must be looked for. A paragraph running over
    two pages keeps its fragments separate; that is what allows one page's
    (1) not to be confused with the next page's.

    Three recourses, in this order, because the volume uses all three:
      1. the call in the page's running text;
      2. the call in ANOTHER note on the same page -- a note may call
         another (folios 162 and 187, asterisk calls): the note called is
         then laid under the paragraph carrying the calling one;
      3. the reference spelled out in words. At folio 90 the text carries
         no call (2): it says "(Videz infre la noto 2.)". The original is
         thus, and we do not correct it; the note is laid under that
         paragraph.
    """
    pending = {f: list(nums) for f, nums in rel.page_notes.items()}

    def place_at(key, bloc):
        rel.notes[key]['block'] = bloc
        bloc.notes_here.append(key)
        pending[key[0]].remove(key[1])

    def mark(h, call, note):
        p = find_call(h, call)
        if p < 0:
            return h, False
        return (h[:p] + '<a class="apelo" href="#%s" data-nt="%s">%s</a>'
                % (note['id'], note['id'], call) + h[p + len(call):]), True

    # 1. the call in the running text
    for b in rel.blocks:
        fresh = []
        for (f, fo, h) in b.frags:
            for num in list(pending.get(f) or ()):
                note = rel.notes[(f, num)]
                h, found = mark(h, note['apel'], note)
                if found:
                    place_at((f, num), b)
            fresh.append((f, fo, h))
        b.frags = fresh

    # 2. the call lodged in another note on the same page
    for key, note in list(rel.notes.items()):
        if note['block'] is None:
            continue
        for other in list(pending.get(key[0]) or ()):
            for k, para in enumerate(note['paras']):
                n_other = rel.notes[(key[0], other)]
                para2, found = mark(para, n_other['apel'], n_other)
                if found:
                    note['paras'][k] = para2
                    place_at((key[0], other), note['block'])
                    break

    # 3. the reference spelled out, then the page's last paragraph
    orphans = []
    for key, note in rel.notes.items():
        if note['block'] is not None:
            continue
        f, num = key
        target, ref = None, None
        for b in rel.blocks:
            for (ff, fo, h) in b.frags:
                if ff != f:
                    continue
                target = b
                if re.search(r'noto\s*%s' % re.escape(num), plain_text(h)):
                    ref = b
        if ref is not None:
            ref.notes_here.append(key)
            note['block'] = ref
            note['ref'] = True
        elif target is not None:
            target.notes_here.append(key)
            note['block'] = target
            note['orphan'] = True
        orphans.append(key)
    return orphans


def find_call(h, call):
    """Position of `(n)` in an HTML fragment, outside any tag."""
    i = 0
    while True:
        p = h.find(call, i)
        if p < 0:
            return -1
        if h.count('<', 0, p) == h.count('>', 0, p):
            return p
        i = p + 1


# ------------------------------------------------------------------
# 6. STRUCTURE
# ------------------------------------------------------------------
def structure(rel):
    """Parts -> chapters. The chapters are ordered by the leaf on which
    their title is set."""
    parties = [{'label': lab, 'start': f, 'chapters': []}
               for f, lab in PARTS]
    for ch in rel.chapters:
        p = None
        for cand in parties:
            if ch['leaf'] >= cand['start']:
                p = cand
        p['chapters'].append(ch)
        ch['partie'] = p
    return [p for p in parties if p['chapters']]


# ------------------------------------------------------------------
# 6 quater. THE PORTRAIT, RENDERED AS A MASK
# ------------------------------------------------------------------
def portrait_mask():
    """The portrait's PNG, reduced to ITS ALPHA CHANNEL ALONE, as a data: URI.

    The facsimile is a halftone: the ink there is black, the paper
    transparent. Rendered by an `<img>`, it would be black on black in dark
    mode -- a fault one does not see until one looks. We therefore keep NO
    colour at all: the PNG produced carries only the alpha, and the CSS
    lays it as a mask over a block whose ground is `var(--enk)`. The
    portrait is then ink, like the rest of the page, and follows the theme.

    The PNG comes out as a palette image: the eight levels of alpha fit in
    an eight-byte tRNS, and the palette itself is all black and serves no
    purpose -- only the alpha is read. It is the lightest form that remains
    an ordinary PNG.
    """
    import base64
    import io
    from PIL import Image

    im = Image.open(PORTRAIT).convert('RGBA')
    height = int(round(im.height * PORTRAIT_WIDTH / float(im.width)))
    alpha = im.resize((PORTRAIT_WIDTH, height), Image.LANCZOS).getchannel('A')

    n = PORTRAIT_LEVELS
    pas = 256.0 / n
    index = alpha.point(lambda v: min(int(v / pas), n - 1))
    p = index.convert('P')
    p.putpalette([0, 0, 0] * 256)
    trns = bytes(int(round(i * 255.0 / (n - 1))) for i in range(n))

    buffer = io.BytesIO()
    p.save(buffer, 'PNG', optimize=True, transparency=trns)
    raw = buffer.getvalue()
    uri = 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')
    return uri, PORTRAIT_WIDTH, height, len(raw)


# The facsimile's caption, as it is engraved under the portrait.
# "de Beaufront" in small capitals, "Ido" in italic: it is the volume's
# composition, not a choice of the page.
CAPTION = ('Markezo L. <span class="pk">de Beaufront</span>, precipua '
           'autoro di <i>Ido</i>')


# ------------------------------------------------------------------
# 7. OUTPUT
# ------------------------------------------------------------------
TEMPLATE = u"""<!DOCTYPE html><html lang="io"><meta charset="utf-8">
<title>Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido</title>
<meta name="viewport" content="width=device-width,initial-scale=1">

<!-- ===================================================================
     FOR THE MACHINES — what search engines and crawlers read.
     ===================================================================
     The page is built for the eye; these lines make it legible to what
     has no eyes.

     "description" and "canonical" serve search engines. The "alternate"
     link announces the Markdown version: that is the form a robot that
     comes to READ rather than to look should take — it costs a
     fraction of this page's weight, the markup being gone.

     The JSON-LD block says what this document IS: a book, its author,
     its date, its language. An engine that understands it no longer has
     to guess.

     The overall map is in /llms.txt, at the root, which speaks for all
     four pages at once.
     =================================================================== -->
<meta name="description" content="Transskribo integra dil Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido (L. de Beaufront, Esch-Alzette, Meier-Heucke, 1925) : 49 chapitri, 1230 alinei, 410 noti. Serchebla, ed ofrata anke po chapitro en formo lektebla da mashini (Markdown).">
<link rel="canonical" href="https://ido.help/gramatiko/">
<link rel="alternate" type="text/markdown" href="gramatiko.md" title="Texto pura, por lekto da mashini">
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Book",
 "name": "Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido",
 "author": {
  "@type": "Person",
  "name": "L. de Beaufront"
 },
 "datePublished": "1925",
 "inLanguage": "io",
 "url": "https://ido.help/gramatiko/",
 "isAccessibleForFree": true,
 "isPartOf": {
  "@type": "WebSite",
  "name": "ido.help",
  "url": "https://ido.help/"
 },
 "encoding": [
  {
   "@type": "MediaObject",
   "encodingFormat": "text/markdown",
   "contentUrl": "https://ido.help/gramatiko/gramatiko.md"
  }
 ]
}
</script>
<link rel="stylesheet" href="/shared.css">
<script src="/shared.js" defer></script>
<style>
:root{--enk:#1a1a1a;--pap:#fbfaf7;--sub:#6b6560;--acc:#7a4b2a;--lin:#e2ddd5;--flag:#b4552d}
@media(prefers-color-scheme:dark){:root{--enk:#e8e4de;--pap:#16161a;--sub:#9a938c;--acc:#d69a6a;--lin:#2c2c33;--flag:#e08a5c}}
*{box-sizing:border-box}
body{margin:0;background:var(--pap);color:var(--enk);
 font:16px/1.55 "Iowan Old Style",Palatino,"Palatino Linotype",Georgia,serif}
header{position:sticky;top:0;background:var(--pap);border-bottom:1px solid var(--lin);
 padding:14px 20px 12px;z-index:20;

 /* --- THE HEADER FOLLOWS THE BODY. --------------------------------
    The band spans the whole width, and that is intended: its ground and
    the rule beneath it must go from edge to edge. But what it CARRIES
    must stop where the body stops. Otherwise, on a very wide viewport,
    the title and the search bar go on spreading while the three panels
    have already frozen at 1360px and centred. This was seen on a Vision
    Pro, whose viewport is far wider than any computer screen.

    The side inset is therefore 20 px while the viewport is narrow, then
    half of whatever overflows the 1360px of "main". The two boxes then
    coincide exactly, at every width beyond.

    It is placed AFTER the short form, which it replaces only on the two
    sides: a browser that does not know "max" discards this line and
    keeps the 20 px of the previous one, so that the header becomes what
    it was, breaking nothing. */
 padding-inline:max(20px, (100% - 1360px) / 2)}
/* The download button anchors at the top right of the title. On a narrow
   screen it drops its text and keeps only the icon: the search bar needs
   the whole width. */
.tito{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}
.dl{flex:none;display:inline-flex;align-items:center;gap:6px;text-decoration:none;
 border:1px solid var(--lin);border-radius:7px;padding:6px 11px;color:var(--acc);
 background:var(--pap);font-size:13px;font-weight:600;white-space:nowrap;
 transition:background .12s,border-color .12s}
.dl:hover{background:var(--lin);border-color:var(--acc)}
.dl svg{display:block;width:15px;height:15px;stroke:currentColor;fill:none;
 stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
@media (max-width:560px){.dl span{display:none}.dl{padding:7px 9px}}
h1{margin:0 0 2px;font-size:17px;font-weight:600;letter-spacing:.01em}
.sub{color:var(--sub);font-size:12.5px;margin-bottom:10px}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
input[type=search]{flex:1 1 260px;min-width:160px;padding:8px 11px;border:1px solid var(--lin);
 border-radius:7px;background:var(--pap);color:var(--enk);font:inherit;font-size:16px}
/* 16px exactly, and not less: Safari on iPhone zooms automatically on any
   field whose type size is under 16px when it is touched. The other cure
   -- maximum-scale=1 in the viewport meta -- would also prevent pinch
   zoom, and with it the legibility of those who need it. */
input[type=search]:focus{outline:2px solid var(--acc);outline-offset:-1px}
.tir{display:none;flex:none;border:1px solid var(--lin);border-radius:7px;
 background:var(--pap);color:var(--acc);font:600 12.5px/1 system-ui,sans-serif;
 padding:9px 11px;cursor:pointer}
.tir:hover{background:var(--lin)}

/* --- Three panels. On a computer: table of contents, text, headwords.
   The two side panels scroll separately from the text: reading the text
   does not move them. --- */
main{display:grid;grid-template-columns:250px minmax(0,1fr) 230px;
 max-width:1360px;margin:0 auto;gap:0}
/* The side panels stick UNDER the header, whose height varies (two lines
   of title on iPad). Fixed at 97 px, the value hid the top of the panel --
   the first entry passed under the bar. It now follows --kapo, measured by
   the script. */
nav,aside{position:sticky;top:var(--kapo,97px);
 height:calc(100vh - var(--kapo,97px));overflow-y:auto;
 padding:16px 14px 60px;font-family:system-ui,sans-serif;font-size:13px}
nav{border-right:1px solid var(--lin)}
aside{border-left:1px solid var(--lin)}
nav .parto{margin:14px 0 5px;font-size:11px;letter-spacing:.07em;text-transform:uppercase;
 color:var(--sub);font-weight:700}
nav a,aside a{display:block;padding:3px 6px;border-radius:5px;text-decoration:none;
 color:var(--enk);line-height:1.35}
nav a{font-size:12.5px}
nav a:hover,aside a:hover{background:var(--lin)}
nav a.nun,aside a.nun{color:var(--acc);font-weight:700;background:rgba(122,75,42,.07)}
aside .kapo{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--sub);
 font-weight:700;margin-bottom:8px}
aside a{font-size:12.5px;color:var(--sub)}
#vednav{display:none}
#vednav a{font-size:12px;color:var(--sub)}

/* The folio sits OUTSIDE the text, 3.6 em to its left -- 3.6 em of ITS OWN
   size, 11 px, that is 40 px. The left white space measured only 34: as
   soon as the central column stopped being wider than the block -- below
   1160 px, hence on every iPad -- the folio left the block and bit 6 px
   into the table of contents. The left white space now houses the folio
   and its air; the maximum width grows by as much, so that the
   JUSTIFICATION of the text does not shift by a point on a computer. */
#kont{padding:26px 58px 140px 58px;max-width:728px;margin:0 auto;position:relative}
.p{margin:0 0 .62em;text-align:justify;text-indent:1.3em;position:relative;
 hyphens:auto;-webkit-hyphens:auto}
.tit{font-weight:700;text-align:center;letter-spacing:.08em;font-size:15px;
 margin:2.2em 0 1em;position:relative}
/* The bar is sticky: any anchor must come to rest below it. */
/* The scroll margin must equal the REAL height of the sticky header.
   Hard-coded -- 112 px here, 215 px on a phone -- it lied as soon as the
   header changed height: on iPad the title goes onto two lines without the
   phone rule applying, and the top of the target section disappeared under
   the search bar. The height is therefore measured at load and at every
   resize, and deposited in --kapo; the hard-coded values now serve only as
   a fallback before the script has run. */
.tit,.p,.rangi,.cen,.sub2,.noto,.avizo,.fig{
 scroll-margin-top:calc(var(--kapo,112px) + 12px)}
.sub2{text-align:center;font-style:normal;margin:-.6em 0 1em;color:var(--sub);
 position:relative}
.cen{text-align:center;margin:.9em 0;position:relative}
.fer{text-align:right;margin:.9em 0;position:relative}
.orn{text-align:center;color:var(--sub);margin:1.4em 0;letter-spacing:.3em}
.rango{margin:.1em 0;text-indent:0}
.rangi{margin:.8em 0;position:relative}
/* --- THE BRACE. A font's { glyph does not stretch; this path does:
   preserveAspectRatio="none" flattens it onto the exact box the CSS gives
   it -- three rows tall, or the whole width of a sibling set -- and
   vector-effect:non-scaling-stroke keeps the stroke the weight of a stem
   of the font, whatever the stretch.
   The rule below is the default measure: an INLINE brace, one line tall,
   for those that open no group -- the "}" of "de o ek", at folio 31, on a
   narrow screen. The three contexts that stretch it override it below. --- */
.akol{display:inline-block;vertical-align:-.28em;width:.34em;height:1.2em;
 color:var(--sub)}
.akol.akh{width:2.2em;height:.6em;vertical-align:.1em}
.akol svg{display:block;width:100%;height:100%;overflow:visible}
.akol path{fill:none;stroke:currentColor;stroke-width:.085em;
 stroke-linecap:round;stroke-linejoin:round}

.tab{border-collapse:collapse;margin:.9em 0 .9em 1em;font-size:.97em}
.tab td{padding:1px 10px 1px 0;vertical-align:middle}
/* The cell straddling two rows (see the grid): centred between them. */
.tab td.mez{vertical-align:middle}
/* A brace's cell spans the rows it caps (rowspan): the path is set within
   it absolutely, from the top of the first row to the bottom of the last
   -- the only sure way of getting the exact height of a group of rows,
   which no measurement in em knows.
   BUT content in absolute position counts for nothing in a column's width:
   `width` being only a wish there, the cell fell to ZERO as soon as the
   table of folio 31 tightened -- between 900 and 1000 px of window -- and
   the brace disappeared. The width is therefore carried by the cell's
   PADDING, which table layout cannot reduce: the left padding makes the
   width of the path, the right one the gap to the next column. */
.tab td.ak{position:relative;padding:0 .4em 0 .75em}
.tab td.ak>.akol{position:absolute;top:1px;right:.4em;bottom:1px;left:0;
 width:auto;height:auto}
/* One more column per brace means the table of folio 31 is 50 px wider:
   below 1000 px of window it overflowed onto the right panel. The
   threshold for the group rendering is therefore raised to 1200 px (see
   below); this guard rail now serves only if the reader enlarges the type
   enough for a table to still get through -- it then scrolls within its
   column rather than leaving it. */
.larja{max-width:100%;overflow-x:auto}
/* The table centred on the measure. The left indent of the two renderings
   (1 em) then ceases to mean anything: it is the symmetry that carries the
   measure, not the distance from the edge. */
.centrita{display:flex;flex-direction:column;align-items:center}
.centrita .tab{margin-left:0;margin-right:0}
.centrita .grupi.sola{margin-left:0}
/* The same table, said twice: in columns for the wide screen, in groups
   for the narrow one. Only one of the two appears at a time. */
/* The same guard rail as for the columns (.larja): if a group exceeds the
   panel's width all the same, it scrolls there instead of leaving it. */
.grupi{display:none;text-indent:0;margin:.9em 0;max-width:100%;
 overflow-x:auto}
.grupi.sola{display:block;margin-left:1em}
.gr{display:flex;align-items:center;gap:7px;margin:.1em 0;min-width:0}
.gr-t{flex:none}
/* The rule that stood in for the brace has given way to the brace itself:
   stretched by align-self:stretch over the whole height of the members,
   its point opposite the title. */
/* The block of members does not go below the width of the widest of them:
   that is what keeps "Supereso  maxim" in one piece. If the panel does not
   suffice, it is .grupi that scrolls. */
.gr-l{flex:1 1 auto;min-width:0}
.gr:not(.grh)>.gr-l{min-width:min-content}
.gr>.akol{flex:none;align-self:stretch;width:.55em;height:auto}
/* The group WITH A CLOSING BRACE -- folio 31: the same three pieces in
   reverse order, members then brace then title. The block of members does
   not stretch (flex:0 1 auto), or the name would be thrown against the
   right edge instead of following the point. */
.gr.gd>.gr-l{flex:0 1 auto;padding-left:0;padding-right:3px}
/* The group carrying a closing brace AT ITS END. The block of members must
   not stretch: stretched, it pushes the brace and its name against the
   right edge of the panel, and "de o ek" ended up half a column from
   "maxim", whereas the facsimile separates them by 3.3 mm out of 92. What
   the measurement states is a NEIGHBOURHOOD, not a right alignment. The
   fault appears only at INTERMEDIATE widths: at 390 and 950 px the panel
   is exactly as wide as the table, and with no slack to distribute the
   stretching produces nothing. */
.gr.gf>.gr-l{flex:0 1 auto}
/* A group caught inside another tightens its gaps: at folio 31 the inner
   group has four of them -- title, brace, members, brace, title -- and at
   7 px each they took from the text the room by which the "k" of "de o ek"
   left the panel. */
.gr .gr{gap:4px}
/* A table cell does not break. As long as the deepest group of folio 31
   had only two storeys, the room never ran short; the closing brace adds a
   third, and "Supereso maxim" broke in two on an iPad -- whereas "infreso
   minim", a hair shorter, held. Two lines of members set differently no
   longer mean anything. */
.gr-m,.gr-x{margin:.12em 0}
.gr-m{white-space:nowrap}
.ec{display:inline-block;width:.75em}
.gr-x{text-indent:0}
/* The group WITH THE POINT AT THE TOP -- the family tree of folio 220: the
   same three pieces, stacked instead of ranged. The box is sized by its
   content (inline-flex), so the brace, stretched across, takes exactly the
   width of the names it caps; the negative margins give it back the slight
   overhang of the facsimile (45.63 mm of ink for 42 mm of names). */
.gr.grh{display:inline-flex;flex-direction:column;align-items:center;
 gap:1px;text-align:center;vertical-align:top}
.grh>.gr-l{padding-left:0;width:100%}
.grh>.akol{align-self:stretch;width:auto;height:.62em;margin:0 -.4em}
/* THE THRESHOLD BETWEEN THE TWO RENDERINGS. It is not chosen by eye: it is
   calculated. The widest table in the volume -- "GRADI KOMPARALA", at
   folio 31 -- wants 430 px to hold without any cell breaking, plus its
   16 px indent. The central column offers min(728, width - 480) - 116.
   1042 px of window are therefore needed, strictly.
   Strictly, that is, with the test font. The reader may have a wider one
   -- the page asks for Iowan, then Palatino, then Georgia -- and a table
   that overflows does not overflow a little: the rows break, terms fall
   under terms, and the brace no longer caps the rows it aims at, since
   those rows have doubled in height. That is exactly what the commissioner
   saw on his iPad.
   The threshold is therefore set at 1200 px, with 150 px of margin: NO
   iPad in landscape reaches that width -- 1194 px for the largest of the
   11-inch ones -- and all of them therefore get the group rendering, which
   bends to any width. The grid stays what it should be: a bonus of the
   wide screen, never a makeshift. */
@media (max-width:1200px){.larja{display:none}.grupi{display:block}}
/* On a narrow phone the deepest group in the volume -- "GRADI KOMPARALA",
   three storeys and two braces -- no longer fits the column. We give it
   back what we can by tightening the gaps and the type; what still exceeds
   scrolls, rather than being cut. */
@media (max-width:420px){
 .grupi{font-size:.93em}
 .gr{gap:5px}.gr .gr{gap:3px}
 .grupi .ec{width:.5em}}
.kond{color:var(--sub);letter-spacing:.28em}
.pk{font-variant:small-caps}
b{font-weight:700}

/* --- The frontispiece plate. The scan is a halftone with an alpha
   channel: the ink in black, the paper transparent. An <img> would become
   black on black in dark mode; the alpha therefore serves as a MASK over a
   coloured block.
   BUT A PHOTOGRAPH IS NOT INK. A first state gave the mask the colour of
   the text, var(--enk): the portrait followed the ink, and in dark mode it
   appeared IN NEGATIVE -- light hair and jacket, dark face. The principle
   was right for a line drawing, wrong for a halftone.
   The plate is therefore treated as what it is: a photograph LAID ON
   PAPER. The card keeps its light ground and the ink its black in BOTH
   modes; in dark mode the plate stands out from the page like a print
   pasted into a book. It is the only way to keep it positive. --- */
.fig{margin:.6em 0 2.6em;text-align:center;position:relative}
.karto{width:min(350px,76%);margin:0 auto;padding:15px 15px 12px;
 border-radius:3px;background:#fbfaf7;border:1px solid #e2ddd5}
@media(prefers-color-scheme:dark){.karto{border-color:#3a3a42;
 box-shadow:0 1px 10px rgba(0,0,0,.5)}}
/* The data: URI is written ONLY ONCE, in a variable: the two properties
   -- with prefix and without -- would double 260 kB of the file. */
.portreto{width:100%;aspect-ratio:__PORTRETO_RATIO__;margin:0 auto;
 background:#1a1a1a;
 --masko:url("__PORTRETO__");
 -webkit-mask-image:var(--masko);mask-image:var(--masko);
 -webkit-mask-size:contain;mask-size:contain;
 -webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;
 -webkit-mask-position:center;mask-position:center}
.legendo{margin-top:.9em;font-size:12.5px;color:var(--sub);
 font-family:system-ui,sans-serif;letter-spacing:.01em}
.legendo .pk{font-variant:small-caps;letter-spacing:.04em}

/* --- The editorial notice. In square brackets, at the size of the notes:
   the page cannot move a text of the volume without saying so. --- */
.avizo{margin:1.4em 0 .8em;padding:8px 12px;border-left:2px solid var(--lin);
 font-size:14px;color:var(--sub);text-indent:0;position:relative}
.avizo .edit{display:block;margin-top:.4em;font-family:system-ui,sans-serif;
 font-size:12.5px;font-style:normal}

/* --- The chain link that copies the section's address. On a computer it
   stays invisible until the mouse passes over the title; on a phone it is
   always visible, with a 44 px target. --- */
/* It stands in the RIGHT margin, as the folio does in the left: that way
   it takes NO room in the text -- an inline chain link would leave a hole
   of 21 px after each of the 322 headwords, even when invisible, and the
   justification would show it. `text-indent:0` is necessary: an
   inline-block inherits the paragraph's indent and applies it to itself. */
.lig{color:var(--sub);text-decoration:none;line-height:0;text-indent:0;
 display:inline-block;padding:0 4px;
 position:absolute;right:-2em;top:.2em;
 opacity:0;transition:opacity .12s,color .12s}
.lig svg{width:13px;height:13px;display:block;
 stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;
 stroke-linejoin:round}
.lig:hover,.lig:focus-visible{color:var(--acc);opacity:1}
.tit>.lig{top:50%;transform:translateY(-50%)}
.tit:hover>.lig,.p:hover>.lig,.avizo:hover>.lig,.fig:hover>.lig,
.lig:focus-visible{opacity:1}
/* Touch screen: nothing passes over the title, so the chain link stays
   always visible, and its target measures 44 px without changing the line
   height -- the pseudo-element grows the target, not the drawing. */
@media (hover:none){
 .lig{opacity:.6}
 .lig::after{content:"";position:absolute;left:50%;top:50%;width:44px;
  height:44px;transform:translate(-50%,-50%)}
}
/* The "Kopiita" confirmation. It shows and fades; it moves nothing. */
#kopito{position:fixed;left:50%;bottom:26px;transform:translate(-50%,14px);
 background:var(--enk);color:var(--pap);border-radius:7px;padding:8px 14px;
 font:600 13px/1.3 system-ui,sans-serif;z-index:60;opacity:0;
 pointer-events:none;transition:opacity .18s,transform .18s;
 max-width:min(92vw,520px);text-align:center}
#kopito.ap{opacity:.94;transform:translate(-50%,0)}
#kopito.manu{pointer-events:auto;background:var(--pap);color:var(--enk);
 border:1px solid var(--acc);opacity:1}
#kopito input{width:min(72vw,380px);margin-top:6px;padding:5px 7px;font:inherit;
 font-weight:400;font-size:12px;border:1px solid var(--lin);border-radius:5px;
 background:var(--pap);color:var(--enk)}

/* --- The folio. It shows in the margin when it begins the paragraph, and
   in the text itself when the page changes mid-paragraph: the place of the
   page break is itself a piece of information from the facsimile. It leads
   to the right page of the PDF (page = folio + 2). --- */
.fol{font:600 11px/1 system-ui,sans-serif;color:var(--sub);text-decoration:none;
 border-bottom:1px dotted var(--lin);padding:1px 3px;border-radius:3px}
.fol:hover{color:var(--flag);border-color:var(--flag)}
.p>.fol:first-child,.tit>.fol:first-child,.cen>.fol:first-child,
.rangi>.fol:first-child,.sub2>.fol:first-child,.avizo>.fol:first-child,
.fig>.fol:first-child{position:absolute;left:-3.6em;top:.25em;
 border:0;text-indent:0}
.p>.fol:first-child+*,.p>.fol:first-child{text-indent:0}

/* --- The notes are folded. The call stays in the text, clickable; the
   note opens under the paragraph that calls it. --- */
.apelo{color:var(--flag);text-decoration:none;font-size:.85em;vertical-align:.35em;
 cursor:pointer;padding:0 1px}
.apelo:hover{text-decoration:underline}
.noto{margin:-.3em 0 .8em 1.3em;padding:8px 12px;border-left:2px solid var(--lin);
 font-size:14px;color:var(--sub);text-align:justify;display:none}
.noto.ap{display:block}
.noto .nnum{font-weight:700;color:var(--acc)}

#rez{padding:20px 34px 120px;max-width:760px;margin:0 auto;display:none}
#rez .nombro{color:var(--sub);font-size:12.5px;margin:0 0 14px;font-family:system-ui,sans-serif}
#rez article{padding:11px 0;border-bottom:1px solid var(--lin);cursor:pointer}
#rez .kap{font-size:11.5px;color:var(--acc);font-family:system-ui,sans-serif;
 letter-spacing:.03em;margin-bottom:3px}
#rez .ext{margin:0}
mark{background:rgba(214,154,106,.34);color:inherit;border-radius:2px}
.brilo{animation:brilo 1.8s ease-out}
@keyframes brilo{from{background:rgba(214,154,106,.42)}to{background:transparent}}

/* --- On a phone, a single panel. The other two become drawers, and the
   bar stays. --- */
@media (max-width:900px){
 main{grid-template-columns:minmax(0,1fr)}
 .tir{display:block}
 nav,aside{position:fixed;top:0;height:100vh;width:min(80vw,320px);z-index:30;
  background:var(--pap);padding-top:18px;transform:translateX(-105%);
  transition:transform .18s ease;box-shadow:0 0 24px rgba(0,0,0,.18)}
 aside{right:0;left:auto;transform:translateX(105%)}
 nav.ap,aside.ap{transform:translateX(0)}
 /* A SINGLE row of controls on a phone: the 260 px flex basis would
    push the field below the button. */
 input[type=search]{flex:1 1 120px;min-width:0}
 /* The switch from columns to groups no longer happens here: it happens
    at 1200 px, one notch higher. */
 /* One drawer only on a phone: the current chapter's headwords show in
    the table of contents itself, under the chapter. */
 aside{display:none}
 #vednav{display:block;margin:2px 0 6px 12px;border-left:2px solid var(--lin);
  padding-left:8px}
 #kont{padding:20px 18px 120px}
 .tit,.p,.rangi,.cen,.sub2,.noto,.avizo,.fig{
  scroll-margin-top:calc(var(--kapo,215px) + 12px)}
 .p>.fol:first-child,.tit>.fol:first-child,.cen>.fol:first-child,
 .rangi>.fol:first-child,.sub2>.fol:first-child,.avizo>.fol:first-child,
 .fig>.fol:first-child{position:static;border-bottom:1px dotted var(--lin);
  margin-right:.4em}
 .karto{width:min(280px,72%)}
 /* On a phone no right margin is left: the chain link comes back into
    the flow, like the folio. It is always visible, so the room it takes
    is intended and does not surprise the reading. */
 .lig{position:static;transform:none;vertical-align:-2px;padding:0 5px}
 .tit>.lig{transform:none}
 .lig svg{display:inline-block}
 #vualo{position:fixed;inset:0;background:rgba(0,0,0,.34);z-index:25;display:none}
 #vualo.ap{display:block}
 .tab{font-size:.9em}
}
</style>
<header>
<div class="tito">
<h1>Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido</h1>
<a class="dl" href="__PDF__" download title="Deskargar la gramatiko (PDF)">
<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12"/><path d="M7 11l5 5 5-5"/><path d="M4 20h16"/></svg><span>Deskargar</span></a>
</div>
<div class="sub">L. de Beaufront &middot; Esch-Alzette, Meier-Heucke, 1925 &middot; __SUB__</div>
<div class="bar">
 <button class="tir" id="tirL" aria-label="Tabelo di la materio">&#9776; Materio</button>
 <input type="search" id="q" placeholder="Serchez en la tota libro&hellip;" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false">
</div>
</header>
<main>
<nav id="nav">__NAV__<div id="vednav"></div></nav>
<div><div id="kont">__KONT__</div><div id="rez"></div></div>
<aside id="vede"><div class="kapo">Chefa vorti dil chapitro</div><div id="vedlist"></div></aside>
</main>
<div id="vualo"></div>
<div id="kopito" role="status" aria-live="polite"></div>
<script>
var HEADS=__VED__;            // setChapter -> [id, chefa vorto]
/* The real height of the sticky header, deposited in --kapo. We measure it
   again on resize AND after the fonts have loaded: a serif font taller than
   the fallback can push the title onto one more line. */
function measureHeader(){var h=document.querySelector('header');
 if(h)document.documentElement.style.setProperty('--kapo',h.offsetHeight+'px');}
measureHeader();
/* On opening a URL with an anchor, the browser scrolls BEFORE the script
   has measured the header: it uses the fallback value, and the target
   section lodges under the bar. We therefore redo the scroll once the
   measurement is taken -- and again after the fonts, which can change the
   height of the title. */
/* An anchor that no longer resolves must be caught, not lost. Six
   addresses changed the day the detection of headwords was corrected:
   "...-vokali-e" became "...-vokali-e-o", and the new entries took the
   unsuffixed rank, pushing out those that held it. A link copied before
   that day no longer found its target, and the page opened at the top
   SAYING NOTHING.
   We do not freeze a table of old addresses: it would age in its turn, and
   would have to be kept up at every correction. We look for the target by
   KINSHIP -- the anchor lengthened by one member (e -> e-o), or the same
   name up to a rank suffix. Whatever has no kin leaves the page where it
   is, as before. */
function findAnchor(h){
 var id=h.slice(1).replace(/^#/,''), el=null, i, x;
 try{el=document.getElementById(id)}catch(e){}
 if(el)return el;
 var t=[].slice.call(document.querySelectorAll('[id]'));
 for(i=0;i<t.length;i++){x=t[i].id;
  if(x.indexOf(id+'-')===0&&!/^\d+$/.test(x.slice(id.length+1)))return t[i];}
 var nu=id.replace(/-\d+$/,'');
 for(i=0;i<t.length;i++){x=t[i].id;
  if(x===nu||x.replace(/-\d+$/,'')===nu)return t[i];}
 /* THE SHORTENED anchor. The day the detection of headwords stopped
    taking example sentences for entries, twenty-four addresses
    disappeared, and three grew shorter:
    "...-dum-ke-dum-ke-il-esis-malada" became "...-dum-ke". The kinship
    then reads the other way: we look for the LONGEST existing identifier
    of which the old address is the extension, cut on a hyphen. The three
    shortened ones find their entry again; the other twenty-one, which
    designated an example the panel no longer lists, find at least the
    article or the chapter that carried them -- "#verbo-la-tero-movas"
    leads to VERBO. */
 var lg=null;
 for(i=0;i<t.length;i++){x=t[i].id;
  if(id.indexOf(x+'-')===0&&(!lg||x.length>lg.id.length))lg=t[i];}
 return lg;}
function visitAnchor(){var h=location.hash;
 if(h.length<2)return;
 var el=findAnchor(h);
 if(el)el.scrollIntoView();}
measureHeader(); visitAnchor();
addEventListener('load',function(){measureHeader();visitAnchor();});
addEventListener('resize',function(){var wasBand=observerBand();measureHeader();
 /* If the header's height has changed, the observer's band is out of
    date: rootMargin cannot be modified after the fact, it has to be
    remade. */
 if(observerBand()!==wasBand&&window.remakeObserver)window.remakeObserver();});
addEventListener('orientationchange',measureHeader);
if(document.fonts&&document.fonts.ready)
 document.fonts.ready.then(function(){measureHeader();visitAnchor();});
var bodyEl=document.getElementById('kont'), resultsEl=document.getElementById('rez');

/* --- The notes. A single listener for the whole volume: 700 calls do not
   deserve 700 listeners. --- */
document.addEventListener('click',function(e){
 var a=e.target.closest('.apelo'); if(!a) return;
 e.preventDefault();
 var n=document.getElementById(a.dataset.nt); if(!n) return;
 n.classList.toggle('ap');
 if(n.classList.contains('ap')){
   var r=n.getBoundingClientRect();
   if(r.bottom>innerHeight) n.scrollIntoView({block:'nearest',behavior:'smooth'});
 }
});

/* --- The chain link: it copies the section's absolute address.
   Three degrees, since the page is often opened by file://, where the
   Clipboard API is missing or refuses:
     1. navigator.clipboard.writeText;
     2. a temporary field + document.execCommand('copy');
     3. the address is shown, selected, for manual copying. --- */
var toastEl=document.getElementById('kopito'), toastTimer=null;
function say(txt,manu){
 clearTimeout(toastTimer);
 toastEl.classList.toggle('manu',!!manu);
 toastEl.textContent=txt;
 toastEl.classList.add('ap');
 if(!manu) toastTimer=setTimeout(function(){toastEl.classList.remove('ap')},1500);
 return toastEl;
}
function manualCopy(url){
 var b=say('Kopiez la ligilo :',true);
 var i=document.createElement('input');
 i.readOnly=true; i.value=url;
 b.appendChild(i); i.focus(); i.select();
 /* It stays until one clicks elsewhere: without that the address would
    vanish before one could copy it. */
 /* It closes at the first click OUTSIDE: a click on the field itself
    must be able to select the text. */
 setTimeout(function(){
  document.addEventListener('click',function f(ev){
   if(toastEl.contains(ev.target)) return;
   toastEl.classList.remove('ap','manu');
   document.removeEventListener('click',f)})},0);
}
function fallbackCopy(url){
 var t=document.createElement('textarea');
 t.value=url; t.setAttribute('readonly','');
 t.style.cssText='position:fixed;top:0;left:0;width:1px;height:1px;opacity:0';
 document.body.appendChild(t);
 t.select(); t.setSelectionRange(0,url.length);
 var ok=false; try{ok=document.execCommand('copy')}catch(e){ok=false}
 document.body.removeChild(t);
 if(ok) say('Kopiita'); else manualCopy(url);
}
document.addEventListener('click',function(e){
 var a=e.target.closest('.lig'); if(!a) return;
 e.preventDefault();
 /* The ABSOLUTE address: a.href is already resolved by the browser, even
    under file://. We do not rebuild it from location, which could carry
    another anchor. */
 var url=a.href;
 if(navigator.clipboard&&navigator.clipboard.writeText){
  navigator.clipboard.writeText(url).then(function(){say('Kopiita')},
                                          function(){fallbackCopy(url)});
 } else fallbackCopy(url);
});

/* --- The two drawers on a phone. --- */
var navEl=document.getElementById('nav'), asideEl=document.getElementById('vede'),
    veilEl=document.getElementById('vualo');
function closeDrawer(){navEl.classList.remove('ap');veilEl.classList.remove('ap')}
document.getElementById('tirL').onclick=function(){
 var o=navEl.classList.contains('ap');
 if(o) closeDrawer(); else {navEl.classList.add('ap');veilEl.classList.add('ap')}};
veilEl.onclick=closeDrawer;
/* Delegated listener: the headwords in the table of contents are created
   and recreated at every change of chapter, so they could not have their
   own listener. */
navEl.addEventListener('click',function(e){
 if(e.target.closest('a')&&innerWidth<=900) closeDrawer()});

/* --- Which chapter one is reading. IntersectionObserver, not a scroll
   listener: it does not run code at every pixel of the scroll. --- */
var blocks=[].slice.call(bodyEl.querySelectorAll('[data-ch]'));
var navLinks={}, curChapter=null;
document.querySelectorAll('nav a[data-ch]').forEach(function(a){navLinks[a.dataset.ch]=a});
var curHead='';
function markHead(vd){
 if(vd) curHead=vd;
 document.querySelectorAll('#vedlist a,#vednav a').forEach(function(a){
   a.classList.toggle('nun',a.getAttribute('href')==='#'+curHead)});
}
function setChapter(c){
 if(c===curChapter) return; curChapter=c;
 for(var k in navLinks) navLinks[k].classList.toggle('nun',k===c);
 var a=navLinks[c]; if(a) a.scrollIntoView({block:'nearest'});
 var v=HEADS[c]||[];
 var links=v.map(function(x){
   return '<a href="#'+x[0]+'" title="'+x[2]+'">'+x[1]+'</a>'}).join('');
 document.getElementById('vedlist').innerHTML=links||
   '<div style="color:var(--sub)">(nula chefa vorto en ca chapitro)</div>';
 /* On a phone the headwords follow their chapter in the table of
    contents: the list is moved under the current chapter's link. */
 var navHeads=document.getElementById('vednav');
 navHeads.innerHTML=links;
 if(a) a.insertAdjacentElement('afterend',navHeads);
 /* The list has just been rebuilt: the mark on the current headword was
    lost with it, and no new intersection will come to set it again. We
    set it at once. */
 markHead(null);
}
var visible={};
/* The observer's decision band began at -100px: another assumed header
   height. On iPad, where the header measures 133 px, it opened ABOVE the
   bar, so that a long block still visible at the top -- "-eg-", 442 px
   tall -- won over the one just reached. The panel therefore designated
   the entry above. The band now follows the measured height, and the
   observer is remade when it changes. */
function observerBand(){
 var h=parseInt(getComputedStyle(document.documentElement)
        .getPropertyValue('--kapo'),10)||100;
 return (-(h+14))+'px 0px -55% 0px';}
function onIntersect(es){
 es.forEach(function(e){if(e.isIntersecting)visible[e.target.dataset.i]=e.target;
                        else delete visible[e.target.dataset.i]});
 var keys=Object.keys(visible).map(Number).sort(function(a,b){return a-b});
 if(!keys.length) return;
 /* The topmost block seen -- but not an edge of a block: after a jump to
    an anchor, the preceding block often still shows ten pixels below the
    bar, and the reading would seem to be still at it. */
 var top=visible[keys[0]];
 for(var z=0;z<keys.length;z++){
  if(visible[keys[z]].getBoundingClientRect().bottom>130){top=visible[keys[z]];break}
 }
 setChapter(top.dataset.ch);
 markHead(top.dataset.vd||headAbove(keys[0]));
}
var observer=new IntersectionObserver(onIntersect,{rootMargin:observerBand()});
function headAbove(i){for(var k=i;k>=0;k--){var b=blocks[k];
  if(b&&b.dataset.vd) return b.dataset.vd;} return ''}
blocks.forEach(function(b,i){b.dataset.i=i;observer.observe(b)});
/* Remake the observer with the band up to date: rootMargin is frozen at
   creation. Called when the header's height changes. */
window.remakeObserver=function(){
 observer.disconnect();
 observer=new IntersectionObserver(onIntersect,{rootMargin:observerBand()});
 blocks.forEach(function(b){observer.observe(b)});};
setChapter(blocks.length?blocks[0].dataset.ch:null);

/* --- The search. The index is built from the DOM itself at load: the text
   is already in the page, it does not need a second copy in JSON -- that
   would double the file's weight for nothing. A linear search over 700,000
   characters costs a few milliseconds. --- */
var INDEX=null;
function buildIndex(){
 if(INDEX) return INDEX; INDEX=[];
 bodyEl.querySelectorAll('.p,.tit,.cen,.rangi,.noto,.sub2,.fer,.avizo,.legendo').forEach(function(el){
  /* The folio numbers do not belong to the volume's text: without this
     copy the extracts would begin with "12Ma, se la renkontro...", and a
     search for "12ma" would find what was never written. */
  var k=el.cloneNode(true);
  k.querySelectorAll('.fol').forEach(function(f){f.remove()});
  /* A table with braces is written twice in the page; without this
     deletion the text would be doubled in the index and in the extracts. */
  k.querySelectorAll('.grupi:not(.sola)').forEach(function(g){g.remove()});
  var t=k.textContent.replace(/\\s+/g,' ').trim();
  if(t) INDEX.push([el,t,t.toLowerCase()]);
 });
 return INDEX;
}
function chapterName(el){
 var b=el.closest('[data-ch]')||el.previousElementSibling;
 var c=b&&b.dataset?b.dataset.ch:null;
 var n=c&&navLinks[c]?navLinks[c].textContent:'';
 return el.classList.contains('noto')?n+' \u00b7 noto':n;
}
var searchTimer=null;
document.getElementById('q').addEventListener('input',function(e){
 clearTimeout(searchTimer); var v=e.target.value.trim();
 searchTimer=setTimeout(function(){search(v)},130);
});
function search(v){
 /* display='' does not suffice: it only clears the inline style, and the
    sheet's rule #rez{display:none} takes over again. */
 if(v.length<2){resultsEl.style.display='none';bodyEl.style.display='';return}
 var q=v.toLowerCase(), I=buildIndex(), out=[], n=0;
 for(var k=0;k<I.length;k++){
  var p=I[k][2].indexOf(q); if(p<0) continue; n++;
  if(out.length<300){
   var t=I[k][1], a=Math.max(0,p-70), b=Math.min(t.length,p+v.length+110);
   out.push('<article data-k="'+k+'"><div class="kap">'+esc(chapterName(I[k][0]))
    +'</div><p class="ext">'+(a?'&hellip;':'')+esc(t.slice(a,p))+'<mark>'
    +esc(t.substr(p,v.length))+'</mark>'+esc(t.slice(p+v.length,b))
    +(b<t.length?'&hellip;':'')+'</p></article>');
  }
 }
 resultsEl.innerHTML='<p class="nombro">'+(n?n+' trovaji'+(n>300?' (montresas la 300 unesma)':'')
  :'Nula trovajo')+'</p>'+out.join('');
 resultsEl.style.display='block';bodyEl.style.display='none';
 scrollTo(0,0);
}
function esc(s){return s.replace(/[&<>]/g,function(c){
 return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
resultsEl.addEventListener('click',function(e){
 var a=e.target.closest('article'); if(!a) return;
 var el=INDEX[+a.dataset.k][0];
 resultsEl.style.display='none';bodyEl.style.display='';
 if(el.classList.contains('noto')){el.classList.add('ap');}
 el.scrollIntoView({block:'center'});
 el.classList.remove('brilo');void el.offsetWidth;el.classList.add('brilo');
});
/* A link straight to a note (gramatiko.html#nt36-1) must open it:
   hashchange does not fire at page load, so we call it twice. */
function onAnchor(){
 var el=document.getElementById(location.hash.slice(1));
 if(!el) return;
 if(el.classList.contains('noto')){el.classList.add('ap');
  el.scrollIntoView({block:'center'});}
 /* A jump to an anchor does not always change what intersects: we mark
    the target chapter and headword directly. */
 if(el.dataset.ch) setChapter(el.dataset.ch);
 if(el.dataset.vd) markHead(el.dataset.vd);
}
addEventListener('hashchange',onAnchor);
onAnchor();
</script>
<a class="ido-home" href="/">Ido</a>
"""


# The chain button. It is a REAL link: without JavaScript it still leads
# to the anchor, and the browser's context menu offers "copy link
# address" there. The click, for its part, is intercepted and copies.
CHAIN_LINK = ('<a class="lig" href="#%s" data-lig="%s" '
           'aria-label="Kopiar la ligilo di %s" title="Kopiar la ligilo">'
           '<svg viewBox="0 0 24 24" aria-hidden="true">'
           '<path d="M10 13.5a4 4 0 0 0 5.7.3l3-3a4 4 0 0 0-5.7-5.7l-1.7 1.7"/>'
           '<path d="M14 10.5a4 4 0 0 0-5.7-.3l-3 3a4 4 0 0 0 5.7 5.7l1.7-1.7"/>'
           '</svg></a>')


def anchor_link(ident, what):
    return CHAIN_LINK % (ident, ident, escape((what or '').strip(' .,;:')))


def block_html(b, chap_index, notes):
    frags = []
    for k, (f, fo, h) in enumerate(b.frags):
        if k == 0 or b.frags[k - 1][1] != fo:
            lien = '<a class="fol" href="%s#page=%d" title="Folio %d en la PDF">%d</a>' \
                   % (PDF, fo + PDF_OFFSET, fo, fo)
            # No space added around the folio: it is already in the text
            # when the facsimile has one, and no space at all is wanted
            # when the page breaks a word (folio 14-15, "be- / zonus").
            frags.append(lien + h)
        else:
            frags.append(h)
    # The fragments join with NOTHING: the end-of-line space is already
    # in the text (\nl), and its absence is too (\cc).
    body = ''.join(frags).strip()
    cls = {'p': 'p', 'tit': 'tit', 'sub': 'sub2', 'cen': 'cen', 'fer': 'fer',
           'orn': 'orn', 'rango': 'rangi', 'tab': 'rangi',
           'avizo': 'avizo', 'fig': 'fig'}[b.kind]
    attrs = ' data-ch="%s"' % chap_index if chap_index is not None else ''
    ident = ''
    if b.head:
        attrs += ' data-vd="%s"' % b.ident
        ident = ' id="%s"' % b.ident
    if b.kind in ('tit', 'fig'):
        ident = ' id="%s"' % b.ident
    # The chain button: to the right of the chapter title, against the
    # headword it addresses. It appears only where there is an anchor --
    # elsewhere it would have nothing to copy.
    if b.kind == 'tit':
        body += anchor_link(b.ident, plain_text(body))
    elif b.kind == 'fig':
        body += anchor_link(b.ident, PORTRAIT_TITLE)
    elif b.head:
        # Against the headword, not at the end of the paragraph: the headword
        # IS the entry's title, and it is what the address designates. The cut
        # is re-read by the same function as the detection: laid at the first
        # `</b>` that came, it fell between the "e" and the "o" of a double
        # headword.
        cut_at = headword(body)[1]
        if cut_at < 0:
            cut_at = body.find('</b>')
            cut_at = cut_at + 4 if cut_at >= 0 else -1
        if cut_at >= 0:
            body = body[:cut_at] + anchor_link(b.ident, b.head) + body[cut_at:]
    if b.notice:
        body += ('<span class="edit">[&#8239;%s&#8239;]</span>'
                  % escape(b.notice))
    out = ['<div class="%s"%s%s>%s</div>' % (cls, ident, attrs, body)]
    for key in b.notes_here:
        nt = notes[key]
        # A note whose call is missing from the facsimile is laid under the
        # paragraph that names it; we say so rather than pass it over.
        mark = ('<span class="nfl">apelo ne trovita en la pagino</span>'
                  if nt.get('orphan') else '')
        body = ''.join('<p>%s</p>' % t for t in nt['paras'])
        out.append('<div class="noto" id="%s">%s%s</div>'
                   % (nt['id'], body, mark))
    return ''.join(out)


# ------------------------------------------------------------------
# 6 bis. THE ANCHOR IDENTIFIERS
# ------------------------------------------------------------------
# An anchor is an ADDRESS: it is cited, bookmarked, pasted into a
# footnote. It must therefore survive the volume's recomposition -- and
# that is why nothing POSITIONAL goes into it. Not the paragraph's rank,
# not the file's order, not the chapter's number: inserting a paragraph at
# folio 12 would shift them all.
#
# THE RULE, in three lines:
#   1. chapter   -> slug(chapter title)
#   2. headword  -> slug(chapter title) + '-' + slug(headword)
#   3. collision -> suffix '-2', '-3'... in the order of the text.
#
# A HASH would do as well against collisions, but it would give an
# illegible address and, above all, it would change entirely at the least
# character corrected. The numeric suffix moves only for entries that
# REALLY bear the same name.
SLUG_LENGTH = 40      # at most, cut on a whole word

# What the transliteration must render before falling back on the general
# rule. The volume is in Ido, which has no diacritic; these equivalences
# are here against the day the transcription carries some.
SLUG_LETTERS = {
    'æ': 'ae', 'œ': 'oe', 'ß': 'ss', 'ø': 'o',
    'đ': 'd', 'ł': 'l', 'þ': 'th', 'ð': 'd',
}


def slug(t):
    """The slug of a title or a headword: ITS TEXT, and nothing else.

    Lower case, diacritics dropped, everything that is not [a-z0-9]
    rendered as a hyphen, hyphens merged and trimmed at both ends. The cut
    is made on a whole word, so that the address stays legible -- and never
    in the middle of a word, which would make it unguessable.
    """
    import unicodedata
    t = unicodedata.normalize('NFKD', t or '')
    t = ''.join(SLUG_LETTERS.get(c, c) for c in t)
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
    if len(t) > SLUG_LENGTH:
        short = t[:SLUG_LENGTH].rsplit('-', 1)[0]
        # A first word longer than the measure: we cut short, there is no
        # word boundary to stop at.
        t = short or t[:SLUG_LENGTH]
    return t.strip('-')


class Anchors(object):
    """The register of identifiers, and the only place that issues them.

    It keeps track of what is already taken and assigns the suffix of
    homonyms IN THE ORDER OF THE TEXT: the first "Til" of PREPOZICIONI is
    `prepozicioni-til`, the second `prepozicioni-til-2`. Two runs on the
    same transcription therefore yield the same addresses.
    """

    def __init__(self):
        self.taken = {}        # identifier -> what it designates
        self.duplicates = []     # collisions seen, for the report

    def reserve(self, ident, what):
        """An identifier imposed from outside (the notes). No suffix: if it
        were repeated, it is the final check that must say so."""
        if ident in self.taken:
            self.duplicates.append((ident, what, self.taken[ident]))
        self.taken[ident] = what
        return ident

    def fresh(self, base, what, default='sekciono'):
        base = base or default
        ident = base
        k = 1
        while ident in self.taken:
            k += 1
            ident = '%s-%d' % (base, k)
        if k > 1:
            self.duplicates.append((base, what, self.taken[base]))
        self.taken[ident] = what
        return ident


# What a URL fragment admits without encoding (RFC 3986): the
# unreserved characters, the sub-delimiters, ":" and "@". The volume's
# notes carry a `*` -- it is ugly, but it is lawful, and the asterisk is
# the facsimile's own call mark.
FRAGMENT_SAFE = re.compile(r"[A-Za-z0-9._~!$&'()*+,;=:@-]+\Z")


def check_anchors(doc):
    """Check, ON THE PAGE AS WRITTEN, that no `id` is repeated.

    The register can guarantee only what passes through it; the check, for
    its part, re-reads the document produced -- the only proof worth
    anything, since it is the document that carries the addresses.

    Returns (number of identifiers, repetitions, identifiers a URL would
    have to encode). Only the REPETITIONS are a fault: two sections at the
    same address means an address that no longer designates.
    """
    idents = re.findall(r'\sid="([^"]*)"', doc)
    seen, duplicates, lefts = set(), [], []
    for i in idents:
        if i in seen:
            duplicates.append(i)
        seen.add(i)
    for i in sorted(seen):
        if not i or not FRAGMENT_SAFE.match(i):
            lefts.append(i)
    return len(idents), sorted(set(duplicates)), lefts


# ------------------------------------------------------------------
# 6 ter. THE ADDENDUM OF FOLIO 224
# ------------------------------------------------------------------
def reinstate_addendum(rel):
    """Put `tra` and `trans` back in the place the volume gives them.

    Folio 224 carries one sentence only -- "Hike ni pozas la du
    prepozicioni tra e trans omisita pos til p. 82" -- and the two entries
    it announces. It is not a section: it is a printer's catching-up, and
    it says itself where its content belongs. The reading page carries it
    there, cutting nothing: the two entries keep folio 224 and its
    reference into the PDF, and the original's sentence precedes them,
    followed by the editorial notice.

    Nothing is hard-coded: the target is found by CONTENT -- the chapter
    bearing the wanted title, the last entry bearing the wanted headword.
    If the volume is recomposed and folio 224 disappears, the function
    finds nothing to move and does nothing.

    Returns (number of blocks moved, text left on the leaf, target).
    """
    to_move = [b for b in rel.blocks
                  if b.frags and all(f == ADDENDUM_LEAF
                                     for f, _, _ in b.frags)]
    if not to_move:
        return 0, 0, None
    # None of these blocks may hold part of another page: otherwise the
    # move would carry off text that is not its own.
    rest = sum(1 for b in rel.blocks for f, _, _ in b.frags
                if f == ADDENDUM_LEAF and b not in to_move)

    # The target: in the wanted chapter, the LAST entry for the wanted
    # headword -- the article `til` runs over three paragraphs, and it is
    # after the third that the volume refers.
    start = None
    for k, b in enumerate(rel.blocks):
        if b.kind == 'tit' and plain_text(b.frags[0][2]) == ADDENDUM_CHAPTER:
            start = k
            break
    if start is None:
        return 0, rest, None
    end = len(rel.blocks)
    for k in range(start + 1, len(rel.blocks)):
        if any(c['block'] is rel.blocks[k] for c in rel.chapters):
            end = k
            break
    target = None
    for k in range(start, end):
        if rel.blocks[k].head == ADDENDUM_HEADWORD:
            target = rel.blocks[k]
    if target is None:
        return 0, rest, None

    # The original's sentence opens the group moved: it is not an entry, it
    # announces them. To it we attach the editorial notice.
    to_move[0].kind = 'avizo'
    to_move[0].notice = ADDENDUM_NOTICE

    # We remove first and insert after: the target's index is re-read
    # AFTER the removal, or it would designate another block.
    for b in to_move:
        rel.blocks.remove(b)
    place = rel.blocks.index(target) + 1
    rel.blocks[place:place] = to_move
    return len(to_move), rest, plain_text(target.frags[0][2])[:40]


def write_page(rel, parties, stats):
    # THE IDENTIFIERS. Nothing positional: the chapter title for the
    # chapter, the chapter title and the headword for the headword. The
    # register assigns the suffixes of homonyms, in the order of the text.
    # The notes reserve their identifier first, so that a slug cannot come
    # and take it from them.
    anchors = Anchors()
    for nt in rel.notes.values():
        anchors.reserve(nt['id'], 'noto')
    for ch in rel.chapters:
        ch['id'] = anchors.fresh(slug(ch['title']), ch['title'], 'chapitro')
        ch['block'].ident = ch['id']
    chap_id = [ch['id'] for ch in rel.chapters]

    heads_by_chap = {}
    parts = []
    for b in rel.blocks:
        cid = chap_id[b.chap] if b.chap is not None else None
        if b.head:
            base = slug(b.head)
            b.ident = anchors.fresh('%s-%s' % (cid, base) if cid else base,
                                  b.head, 'chefa vorto')
            # The FILTER is upstream, in `headword()`: no example sentence
            # reaches here any more. What remains here is only a column
            # measurement: the few headwords that are lists -- "Cadie,
            # camatine, cavespere...", 63 characters -- do not fit in
            # 230 px. The whole title is kept in the tooltip.
            lab = b.head.rstrip(' .,;:')
            short = lab if len(lab) <= 42 else lab[:41].rsplit(' ', 1)[0] + '\u2026'
            heads_by_chap.setdefault(cid, []).append(
                [b.ident, escape(short), escape(lab)])
        parts.append(block_html(b, cid, rel.notes))

    nav = []
    for p in parties:
        nav.append('<div class="parto">%s</div>' % escape(p['label']))
        for ch in p['chapters']:
            nav.append('<a href="#%s" data-ch="%s">%s</a>'
                       % (ch['id'], ch['id'], escape(ch['title'])))
    import json
    sub = '%d chapitri &middot; %d alinei &middot; %d noti' % (
        stats['chapters'], stats['paragraphs'], stats['notes'])
    uri, width, height, weight = stats['portrait']
    doc = (TEMPLATE.replace('__NAV__', ''.join(nav))
           .replace('__KONT__', ''.join(parts))
           .replace('__VED__', json.dumps(heads_by_chap, ensure_ascii=False))
           .replace('__SUB__', sub)
           .replace('__PORTRETO__', uri)
           .replace('__PORTRETO_RATIO__', '%d / %d' % (width, height))
           .replace('__PDF__', PDF))
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(doc)
    return doc, anchors


# ------------------------------------------------------------------
# 8. RUN
# ------------------------------------------------------------------
def main():
    rel = Transcription()
    # First pass: the folio of each leaf, ALL pages taken together --
    # including those the reading page does not take up, which carry printed
    # folios that are very useful for the interpolation.
    raw = []
    for name in FILES:
        s = strip_comments(open(os.path.join(CONTENT, name),
                                   encoding='utf-8').read())
        for m in re.finditer(r'\\begin\{VUpage\}(\[[^\]]*\])?\{([^}]*)\}', s):
            leaf = int((m.group(1) or '[0]')[1:-1] or 0)
            fo = m.group(2).strip()
            raw.append((leaf, int(fo) if fo else None))
    rel.folios = folio_table(raw)

    for name in FILES:
        s = strip_comments(open(os.path.join(CONTENT, name),
                                   encoding='utf-8').read())
        for m in re.finditer(r'\\begin\{VUpage\}(\[[^\]]*\])?\{([^}]*)\}',
                             s):
            leaf = int((m.group(1) or '[0]')[1:-1] or 0)
            end = s.index('\\end{VUpage}', m.end())
            if not (FIRST_LEAF <= leaf <= LAST_LEAF):
                continue
            rel.page(leaf, m.group(2), s[m.end():end])
    rel.close_para()

    orphans = attach_notes(rel)

    # The addendum of folio 224, put back where the volume places it.
    moved, left_on_224, target = reinstate_addendum(rel)

    # THE PORTRAIT. It opens the page, before the KONSTATO, and counts as a
    # chapter for the table of contents -- but its block is not a title: it
    # is the plate itself, with its caption.
    portrait = portrait_mask()
    # The plate is on leaf 7, the title page, with the caption below --
    # the folio in the margin points there. The CHAPTER, for its part, is
    # dated from the first leaf read: it is by the leaf that the structure
    # ranges chapters into parts.
    fig = Block('fig', [(PORTRAIT_LEAF, rel.folios[PORTRAIT_LEAF],
                        '<div class="karto"><div class="portreto" role="img" '
                        'aria-label="%s"></div></div>'
                        '<div class="legendo">%s</div>'
                        % (plain_text(CAPTION), CAPTION))])
    rel.blocks.insert(0, fig)
    rel.chapters.insert(0, {'title': PORTRAIT_TITLE, 'block': fig,
                             'leaf': FIRST_LEAF,
                             'folio': rel.folios[FIRST_LEAF]})

    # attach each block to its chapter. The block that opens a chapter is
    # not necessarily a title -- the portrait is not one; what counts is
    # being entered in the register of chapters.
    tetes = {id(c['block']): i for i, c in enumerate(rel.chapters)}
    k = -1
    for b in rel.blocks:
        if id(b) in tetes:
            k = tetes[id(b)]
        b.chap = k if k >= 0 else None
    parties = structure(rel)

    stats = {
        'pages': len(rel.pages),
        'chapters': len(rel.chapters),
        'paragraphs': sum(1 for b in rel.blocks if b.kind == 'p'),
        'notes': len(rel.notes),
        'notes_on_call': sum(1 for n in rel.notes.values()
                           if n['block'] is not None and not n.get('orphan')
                           and not n.get('ref')),
        'notes_on_ref': sum(1 for n in rel.notes.values() if n.get('ref')),
        'orphans': len(orphans),
        'headwords': sum(1 for b in rel.blocks if b.head),
        'tables': sum(1 for b in rel.blocks if b.kind == 'tab'),
        'braced': sum(1 for b in rel.blocks if b.kind == 'tab'
                       and 'class="grupi' in b.frags[0][2]),
        'rows': sum(1 for b in rel.blocks if b.kind == 'rango'),
        # The second rendering of a table with braces -- always at the tail of
        # the fragment -- is not more text: we count only once what the page
        # says twice.
        'characters': sum(len(plain_text(re.sub(r'<div class="grupi">.*$', '', h,
                                          flags=re.S)))
                      for b in rel.blocks for _, _, h in b.frags),
        'portrait': portrait,
        'moved': moved,
        'left_on_224': left_on_224,
        'target224': target,
    }
    print('pages read          %5d' % stats['pages'])
    print('chapters            %5d' % stats['chapters'])
    for p in parties:
        print('   %-42s %3d' % (p['label'], len(p['chapters'])))
    print('paragraphs          %5d' % stats['paragraphs'])
    print('notes               %5d  of which %d laid on their call, %d on a '
          'reference spelled out, %d with no call found'
          % (stats['notes'], stats['notes_on_call'], stats['notes_on_ref'],
             stats['orphans'] - stats['notes_on_ref']))
    if orphans:
        print('   call absent from the page text: %s'
              % ', '.join('leaf %d, note (%s)' % c for c in orphans))
    print('headwords           %5d' % stats['headwords'])
    print('tables              %5d  of which %d with braces, rendered also in '
          'groups for the narrow screen' % (stats['tables'], stats['braced']))
    print('set-off lines       %5d runs' % stats['rows'])
    print('characters of text  %5d' % stats['characters'])
    print('portrait            %5d x %d px, %d kB of PNG (alpha only)'
          % (portrait[1], portrait[2], portrait[3] // 1024))
    print('addendum folio 224  %5d blocks put back after \u00ab %s \u00bb, %d '
          'block(s) left on leaf %d'
          % (moved, target or '?', left_on_224, ADDENDUM_LEAF))
    if unhandled:
        print('MACROS NOT HANDLED: %s'
              % ', '.join('%s x%d' % (k, v) for k, v in unhandled.items()))

    if '--count' not in sys.argv:
        doc, anchors = write_page(rel, parties, stats)
        # THE UNIQUENESS CHECK. It is done on the page AS WRITTEN, not on the
        # register: it is the document that carries the addresses, and so it is
        # the document that must be re-read.
        n, duplicates, lefts = check_anchors(doc)
        print('anchors             %5d identifiers, %s'
              % (n, 'NO DUPLICATES' if not duplicates
                 else 'DUPLICATES: ' + ', '.join(duplicates)))
        if anchors.duplicates:
            print('   homonyms separated by a suffix (%d): %s'
                  % (len(anchors.duplicates),
                     ', '.join(sorted({d[0] for d in anchors.duplicates}))))
        if lefts:
            print('   lawful but needing encoding in a URL: %s'
                  % ', '.join(lefts))
        if duplicates:
            sys.exit('identifiers repeated: the page is not addressable')
        print('notes rejoined with a space  %d' % getattr(rel,'n_rejoined',0))
        print('wrote %s (%d kB)' % (OUTPUT, len(doc.encode('utf-8')) // 1024))


if __name__ == '__main__':
    main()
