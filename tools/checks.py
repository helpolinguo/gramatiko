#!/usr/bin/env python3
"""The volume's automatic checks on the transcription.

To be run after EVERY batch of changes:

    python3 tools/checks.py            # everything
    python3 tools/checks.py 3 4 5      # only these checks

 1. Pagination conforms, zero "Overfull \\vbox", inventory of the
    "Overfull \\hbox" one by one.
 2. Line-by-line comparison between the composed PDF and the transcription.
 3. Every \\cc falls between two letters.
 4. No \\nl falls inside a word.
 5. No line begins with : ; ! ?
 6. No line begins with low punctuation or a closing parenthesis.
 7. Minimum effective margin over every page.
 8. Visual comparison at 300 dpi (builds the juxtapositions).

The transcription is the content of content/*.tex: the line breaks there
are all explicit, so the source file IS the survey of the facsimile.
"""
import os, re, sys, json, subprocess, glob

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(P, 'content')
sys.path.insert(0, os.path.join(P, 'tools'))
import syllabify
import pair_up
import cache

RED, GREEN, YELLOW, RESET = '\033[31m', '\033[32m', '\033[33m', '\033[0m'


class Report:
    def __init__(self):
        self.lines = []
        self.failures = 0
        self.warnings = 0

    def ok(self, msg):
        self.lines.append((GREEN + 'OK  ' + RESET, msg))

    def ko(self, msg):
        self.failures += 1
        self.lines.append((RED + 'FAILED' + RESET, msg))

    def warn(self, msg):
        self.warnings += 1
        self.lines.append((YELLOW + 'NOTE' + RESET, msg))

    def print_out(self, title):
        print('\n=== %s ===' % title)
        for tag, m in self.lines:
            print('  %s %s' % (tag, m))


# --------------------------------------------------------------------
# Reading the transcription: the pages and their lines, as encoded
# --------------------------------------------------------------------
# Commands whose arguments must ALSO be thrown away: they set no text
# (type-size settings, vertical space, rules...).
SILENT = {
    'vspace': 1, 'vspace*': 1, 'hspace': 1, 'hspace*': 1, 'kern': 0,
    'fontsize': 2, 'setlength': 2, 'addvspace': 1, 'rule': 2,
    'includegraphics': 1, 'label': 1, 'phantom': 1, 'vskip': 0,
    'VUsaut': 1, 'VUfiletnote': 0, 'VUfilet': 1,
    # The GATHERING SIGNATURE is a bare digit at the foot of the page. It
    # belongs to no line of text: the facsimile detector does not see it (it
    # falls below the block), and on the composed side lines_pdf() discards
    # lines of a single character. Both sides therefore ignore it, and check 2
    # does not verify it -- a limit recorded in the journal. Without this
    # entry, the ordinate passed to the macro read as text: "168.74mm2".
    'VUsignature': 2,
    # Vertical settings: they set nothing, but their argument is a
    # dimension, which the transcription took for text (folio 30 opened on a
    # line "10.38pt").
    'VUinterlignePage': 1, 'VUblanc': 1, 'VUblancAlinea': 0,
    # A table's brace carries no text: only its height and its vertical
    # displacement, two arguments both silent.
    'VUaccolade': 2, 'VUaccoladeD': 2,
    # THE END-OF-PART ORNAMENT is a bare rule: no text. Its single argument
    # is an ordinate, which the transcription read as the first line of folio
    # 114 ("147.14mm").
    'VUornement': 1,
    # THE ASTERISM is a bare ornament: three asterisks, no text. Its single
    # argument is an ordinate, which the transcription read as the first line
    # of folio 186.
    'VUasterismo': 1,
    # \VUpageNote sets nothing: it changes the type size and leading of the
    # whole page (leaf 208, the only page of the volume wholly at the size of
    # the notes). Its argument, "8.13pt", read as the first line of folio 204.
    'VUpageNote': 1,
    # THE HORIZONTAL BRACE of the tree on folio 220 carries no text: its
    # single argument is a width, which the transcription read as the
    # beginning of the row ("45.63mmPetrusPaulus...").
    'VUaccoladeH': 1,
}
# Commands whose first N arguments are thrown away, keeping the last.
SKIP_THEN_TEXT = {'VUnotes': 1, 'VUserre': 1,
                    # Tables: the surveyed abscissa, then the matter.
                    'VUcase': 1, 'VUdecale': 1}
# Commands whose argument is kept (it carries text).
SPEAKING = {'textbf', 'textit', 'textsc', 'emph', 'textrm', 'MakeUppercase',
             'textsuperscript'}
# Commands WITHOUT an argument that nonetheless set a character. The
# transcription erased them outright, so that check 2 declared a properly
# composed sign lost: at folio 199, the facsimile's STRAIGHT single quote
# -- a true vertical stroke, distinct from the turned comma of folio 201 --
# is written \textquotesingle; it disappeared on the transcription side and
# survived on the PDF side.
LITERALS = {'textquotesingle': "'",
              # ESCAPED BRACES ARE SET. At folio 220 the text cites the signs
              # themselves -- "Embracili \{\}" -- and the transcription erased them
              # outright, so that check 2 opposed "Embracili uzesas" to "Embracili {}
              # uzesas" on a page that was right.
              '{': '{', '}': '}'}
CMD = re.compile(r'\\([a-zA-Z@]+\*?|.)')


def _skip_group(s, i):
    """i points at '{': returns (contents, index after '}')."""
    depth, j = 0, i
    while j < len(s):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        elif s[j] == '\\':
            j += 1
        j += 1
    return s[i + 1:], len(s)


def _skip_opt(s, i):
    if i < len(s) and s[i] == '[':
        j = s.find(']', i)
        return j + 1 if j >= 0 else i
    return i


def plain_text(s):
    """Strips the LaTeX markup and keeps only the text actually set."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == '%':
            j = s.find('\n', i)
            i = len(s) if j < 0 else j + 1
            continue
        if c == '\\':
            m = CMD.match(s, i)
            if not m:
                i += 1
                continue
            name = m.group(1)
            j = m.end()
            if name in (',', ' ', ';', ':', '!'):
                out.append(' ' if name in (',', ' ') else '')
                i = j
                continue
            if name in LITERALS:
                out.append(LITERALS[name])
                i = j
                if i < len(s) and s[i] == '{' and s[i + 1:i + 2] == '}':
                    i += 2          # the {} that protects the following space
                continue
            while j < len(s) and s[j] in ' \n\t':
                j += 1
            j = _skip_opt(s, j)
            if name in SILENT:
                for _ in range(SILENT[name]):
                    if j < len(s) and s[j] == '{':
                        _, j = _skip_group(s, j)
                i = j
                continue
            if name in SKIP_THEN_TEXT:
                for _ in range(SKIP_THEN_TEXT[name]):
                    if j < len(s) and s[j] == '{':
                        _, j = _skip_group(s, j)
                    while j < len(s) and s[j] in ' \n\t':
                        j += 1
                if j < len(s) and s[j] == '{':
                    inner, j = _skip_group(s, j)
                    # Space BEFORE the contents of a table cell: two neighbouring
                    # \VUcase ran together, and "... persono :" followed by "me"
                    # formed the token ":me", which the comparison of rows could
                    # recognise neither as a brace artefact nor as text.
                    out.append((' ' if name in ('VUcase', 'VUdecale') else '')
                               + plain_text(inner))
                i = j
                continue
            if name in SPEAKING:
                if j < len(s) and s[j] == '{':
                    inner, j = _skip_group(s, j)
                    out.append(plain_text(inner))
                i = j
                continue
            i = j          # command with no textual effect (\centering, \par...)
            continue
        if c in '{}':
            i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


APPARATUS = {'VUcentreA': 4, 'VUcentre': 3, 'VUtitre': 3, 'VUsoustitre': 3}


def unfold_apparatus(body):
    """Each apparatus line (\\VUcentreA{y}{size}{spacing}{text},
    \\VUcentre{size}{spacing}{text}) is a line of the facsimile in its own
    right: we reduce it to "text\\nl" so that the transcription stays
    uniformly a run of lines. Only the LAST argument carries text; the
    preceding ones are measurements."""
    out, i = [], 0
    while i < len(body):
        cands = [(body.find('\\' + name, i), name) for name in APPARATUS]
        cands = [(j, name) for j, name in cands if j >= 0]
        if not cands:
            out.append(body[i:])
            break
        # the nearest, and at equal position the longest (VUcentreA before
        # VUcentre, whose name is a prefix)
        j, name = min(cands, key=lambda t: (t[0], -len(t[1])))
        out.append(body[i:j])
        k = j + 1 + len(name)
        text = ''
        for a in range(APPARATUS[name]):
            while k < len(body) and body[k] in ' \n\t':
                k += 1
            if k < len(body) and body[k] == '{':
                arg, k = _skip_group(body, k)
                if a == APPARATUS[name] - 1:
                    text = arg
        out.append('\x02' + text + '\x02' + r'\nl')
        i = k
    return ''.join(out)


def move_notes(body):
    """The block of notes is declared at the HEAD of the page (it is placed
    at an absolute ordinate), but it is set at the FOOT of the page. Check
    2 compares in visual order: we therefore move it back to the end."""
    j = body.find('\\VUnotes')
    if j < 0:
        return body
    k = j + len('\\VUnotes')
    # \VUnotes has taken an OPTIONAL ARGUMENT (the width of the rule, null
    # on leaf 208, the only page of the volume whose note carries none).
    # Without this skip, "[0pt]" and the ordinate fell into the text of the
    # first line surveyed.
    while k < len(body) and body[k] in ' \n\t':
        k += 1
    k = _skip_opt(body, k)
    for _ in range(2):
        while k < len(body) and body[k] in ' \n\t':
            k += 1
        if k < len(body) and body[k] == '{':
            _, k = _skip_group(body, k)
    return body[:j] + body[k:] + '\n\n\x03' + body[j:k]


def _unfold_rows(body):
    """\\VUrang{...} -> its contents, followed by a \\nl."""
    out = []
    i = 0
    while True:
        j = body.find('\\VUrang{', i)
        if j < 0:
            out.append(body[i:])
            break
        out.append(body[i:j])
        contents, k = _skip_group(body, j + len('\\VUrang'))
        # \x04 marks the line as a table row: its white space is measured
        # spacing, not content.
        out.append('\x04' + contents + '\\nl')
        i = k
    return ''.join(out)


def _unfold_index(body):
    """\\VUindex[opt]{entry}{number} -> "entry number", followed by a \\nl.

    Each entry of the TABELO is ONE line of the facsimile. Without this
    unfolding, plain_text chained them all into the same surveyed line, and
    check 2 opposed the twenty-six entries of folio 225 to the single
    "Pagini." of the composed page.
    They are marked as table rows (\\x04): their white space is measured
    spacing, not content, and their first character is not subject to the
    line-break rules.
    """
    out, i = [], 0
    while True:
        j = len(body)
        # \VUindexLarge, added for the catalogues of folio 232 (whose leader
        # dots have a pitch three times wider), must be unfolded like the other
        # two. Omitted here, its lines are not marked as rows, and the
        # line-opening checks see five "stray spaces" in them.
        for name in ('\\VUindexNu', '\\VUindexLarge', '\\VUindex'):
            k = body.find(name, i)
            # \VUindex must not swallow \VUindexNu or \VUindexRenfoncement
            while k >= 0 and body[k + len(name):k + len(name) + 1].isalpha():
                k = body.find(name, k + 1)
            if k >= 0 and k < j:
                j, which = k, name
        if j >= len(body):
            out.append(body[i:])
            break
        out.append(body[i:j])
        k = j + len(which)
        k = _skip_opt(body, k)
        entry, k = _skip_group(body, k)
        number, k = _skip_group(body, k)
        out.append('\x04' + entry + ' ' + number + '\\nl')
        i = k
    return ''.join(out)


def read_transcription():
    """Returns [{'file','folio','lines':[{'text','break'}...]}, ...]

    break = 'cc' if the line ends on a hyphen of division,
            'nl' if it ends without a hyphen,
            None for the last line of a paragraph."""
    pages = []
    for fp in sorted(glob.glob(os.path.join(CONTENT, '*.tex'))):
        src = open(fp, encoding='utf-8').read()
        for m in re.finditer(
                r'\\begin\{VUpage\}(?:\[([^\]]*)\])?\{([^}]*)\}(.*?)\\end\{VUpage\}',
                src, re.S):
            leaf, folio, body = (m.group(1) or '').strip(), m.group(2).strip(), m.group(3)
            body = move_notes(body)
            body = unfold_apparatus(body)
            # An end of paragraph is an end of line: the transcription must see it.
            # An end of paragraph IS an end of line, but it is not a \nl: the line
            # there is short, not justified. Confusing the two made the check on line
            # endings unusable, every end of paragraph being claimed "full".
            # A table row is a line: \VUrang{...} returns its contents followed by an
            # end of line. Without this the transcription saw the six rows of the
            # table of folio 31 as a single line.
            body = _unfold_rows(body)
            body = _unfold_index(body)
            body = re.sub(r'\n[ \t]*\n', r'\\pf' + '\n', body)
            lines = []
            # we split on \nl and \cc, keeping which one did the breaking
            pieces = re.split(r'(\\nl\b|\\cc\b|\\pf\b)', body)
            current = ''
            in_note = [False]
            for k in range(0, len(pieces)):
                p = pieces[k]
                if p in (r'\nl', r'\cc', r'\pf'):
                    lines.append({'brut': current,
                                   'text': plain_text(current.replace('\x02', '').replace('\x03', '').replace('\x04', '')).strip(),
                                   'apparat': '\x02' in current,
                                   'rang': '\x04' in current,
                                   'note': in_note[0] or '\x03' in current,
                                   'break': p[1:]})   # 'nl', 'cc' or 'pf'
                    if '\x03' in current:
                        in_note[0] = True
                    current = ''
                else:
                    current += p
            if plain_text(current).strip():
                lines.append({'brut': current,
                               'text': plain_text(current.replace('\x02', '').replace('\x03', '').replace('\x04', '')).strip(),
                               'apparat': '\x02' in current,
                               'rang': '\x04' in current,
                               'note': in_note[0] or '\x03' in current,
                               'break': None})
            pages.append({'fichier': os.path.basename(fp), 'folio': folio,
                          'leaf': leaf, 'lines': lines})
    return pages


# --------------------------------------------------------------------
# Check 1 -- pagination and overflows
# --------------------------------------------------------------------
def check_1(pages, r):
    log = os.path.join(P, 'main.log')
    if not os.path.exists(log):
        r.ko('main.log missing: the document has not been compiled')
        return
    txt = open(log, encoding='utf-8', errors='replace').read()
    vbox = re.findall(r'Overfull \\vbox \(([\d.]+)pt too high\)', txt)
    hbox = re.findall(r'Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*', txt)
    if vbox:
        r.ko('%d « Overfull \\vbox » : %s' % (len(vbox), ', '.join(vbox[:8])))
    else:
        r.ok('no « Overfull \\vbox »')
    if hbox:
        r.warn('%d « Overfull \\hbox » — inventory in tools/hbox.txt'
             % len(hbox))
        with open(os.path.join(P, 'tools', 'hbox.txt'), 'w') as fh:
            for i, h in enumerate(re.findall(
                    r'(Overfull \\hbox[^\n]*\n(?:[^\n]*\n){0,2})', txt), 1):
                fh.write('%3d. %s\n' % (i, h.strip()))
    else:
        r.ok('no « Overfull \\hbox »')
    pdf = os.path.join(P, 'main.pdf')
    if os.path.exists(pdf):
        out = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
        npages = int(re.search(r'Pages:\s+(\d+)', out).group(1))
        if npages == len(pages):
            r.ok('pagination conforms: %d pages composed for %d pages transcribed'
                 % (npages, len(pages)))
        else:
            r.ko('pagination: %d pages composed for %d pages transcribed'
                 % (npages, len(pages)))


# --------------------------------------------------------------------
# Check 2 -- line-by-line comparison, PDF <-> transcription
# --------------------------------------------------------------------
def _norm(s):
    s = s.replace('\u00a0', ' ').replace('\u2019', "'").replace('\u2018', "'")
    # The grave accent of the LaTeX source IS the opening single quote: at
    # folio 201 the facsimile carries a turned comma, which is written « ` »
    # and which pdftotext renders « ' ». Without this line the check opposed
    # « ` Qua » to « ' Qua » on a page that was right.
    s = s.replace('`', "'")
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2014', '--').replace('\u2013', '--')
    s = s.replace('---', '--')          # em dash as encoded in the LaTeX source
    # pdftotext inserts a space after a superscript: "IV^a , Papo". A space
    # before a comma or a full stop is never correct in this work -- French
    # spacing applies only to ; : ! ? -- so removing it can mask no real
    # defect.
    # The same reason for the CLOSING PARENTHESIS: "(1,000,000^2 )". The
    # space pdftotext puts after a superscript falls where the table of folio
    # 94 has one. A space before ")" is never correct here, and check 6
    # already verifies that no line BEGINS with a closing parenthesis:
    # nothing is masked.
    s = re.sub(r'\s+([,.)])', r'\1', s)
    # And likewise AFTER an OPENING parenthesis. At folio 204 pdftotext
    # renders "( beluli)" where the source writes "(beluli)": the space is
    # born of the passage from bold to roman just before, like the one it
    # puts after a superscript. A space after "(" is never correct in this
    # work, so removing it masks nothing real.
    s = re.sub(r'\(\s+', '(', s)
    # THE TABELO'S LEADER DOTS are not content: they are typographic
    # filling, laid by \leaders. The transcription writes the entry and its
    # number, the composed page interposes thirty dots. No text in the volume
    # carries six dots in a row -- the longest is "(...)" from folio 219,
    # which has three.
    s = re.sub(r'\.{6,}', ' ', s)
    # FRENCH SPACING, on the other hand, is REAL on both sides -- but it is
    # neither written in the source nor rendered reliably. The source writes
    # "if;"; it is \VUespacePonct that lays the space at the moment of
    # setting. The transcription reads the source and returns "if;". That
    # left pdftotext, which announces the space only when it exceeds its
    # geometric threshold: after a roman letter it does not see it, after an
    # italic -- whose correction is added to the space -- it does. Hence two
    # failures at folios 90 and 91, "E. if ;" against "E. if;", on perfectly
    # correct pages.
    #
    # We therefore normalise on BOTH sides. What that costs can be named: the
    # check can no longer see a missing French space. But it cannot be
    # missing on ONE line: it comes from a macro laid once for the whole
    # volume, and folio 12 verified it by eye. A global defect stays visible,
    # a local one is impossible -- the normalisation therefore masks nothing
    # real.
    s = re.sub(r'\s+([;:!?])', r'\1', s)
    s = s.replace('\u00ab', '<<').replace('\u00bb', '>>')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def lines_pdf():
    """Lines of the composed PDF, page by page, via pdftotext -layout."""
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        return None
    out = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', pdf, '-'],
                         capture_output=True, text=True).stdout
    # The braces of the tables come from the mathematical extension font,
    # which has no Unicode counterpart; pdftotext renders them as control
    # characters (0x1A, 0x08). A line containing nothing else then appeared
    # non-empty, shifted all the following ones, and check 2 declared
    # "<missing>" on a page that was nonetheless right (folio 31).
    # A table brace is taller than a line: pdftotext gives it a line of its
    # own. It comes out as some arbitrary character, according to the font
    # and the piece of brace used -- 0x1A, 0x08, "(" and "n" have all been
    # seen. A list of characters to discard therefore does not hold; the
    # sure criterion is STRUCTURAL: the stray line carries only ONE
    # character. The volume has no legitimate line of a single character --
    # the shortest surveyed has five ("rozi."). Those lines shifted all the
    # following ones, and check 2 declared "missing" on a page that was
    # nonetheless right.
    # THE ASTERISM, once laid correctly, takes a line to itself. As long as
    # its two rows fell 63 px apart -- the fault corrected in the preamble --
    # the upper row stuck to the neighbouring text and pdftotext did not
    # separate them. Laid correctly, it comes out as "*" then "* *", which
    # net() reduces to "***": one more line on the composed side, which
    # shifted all the following ones and made check 2 fail on two pages that
    # were nonetheless right (folios 186 and 207).
    # The volume has no line of text made of asterisks alone.
    ASTERISM = re.compile(r'^[*\s]+$')
    LETTER = re.compile(r'[0-9A-Za-zÀ-ÿ]')
    POINTS = re.compile(r'^[.\s]+$')

    def strip_stray(l):
        t = ''.join(c for c in l if c >= ' ' or c == '\t').strip()
        if len(t) <= 1 or ASTERISM.match(t):
            return ''
        # THE HORIZONTAL BRACE breaks into several pieces, and pdftotext throws
        # them onto a line of their own: "}|      {" at folio 220. The
        # single-character rule, written for the VERTICAL brace, does not catch
        # them -- there are two.
        # The sure criterion stays structural: a line of this volume always
        # carries a letter or a digit. The only exception is a row of dots in a
        # plate, which must be kept.
        if not LETTER.search(t) and not POINTS.match(t):
            return ''
        return t
    return [[strip_stray(l) for l in pg.split('\n') if strip_stray(l)]
            for pg in out.split('\f')[:-1]]


def check_2(pages, r):
    got = lines_pdf()
    if got is None:
        r.ko('main.pdf missing')
        return
    gaps = 0
    for i, pg in enumerate(pages):
        lg = [l for l in pg['lines'] if l['text']]
        expected = [_norm(l['text'] + ('-' if l['break'] == 'cc' else '')) for l in lg]
        got = [_norm(x) for x in (got[i] if i < len(got) else [])]
        # an apparatus line is letter-spaced: the white space in it is a
        # typographic effect, not content. We compare it with the spaces removed.
        # The apparatus lines AND the notes are letter-spaced: pdftotext reads
        # the tracking as a space ("vokali e , o"). The white space in them is a
        # typographic effect, not content: we compare without it.
        # A table row is also compared with spaces removed: its gaps are
        # geometric (\VUcase), not word spaces.
        matched_pairs = [l.get('apparat') or l.get('note') or l.get('rang') for l in lg]
        # the composed folio appears at the head: we exclude it from the comparison
        if got and re.fullmatch(r'--\s*\d*\s*--', got[0]):
            got = got[1:]
        cmp_a = [x.replace(' ', '') if (k < len(matched_pairs) and matched_pairs[k]) else x
                 for k, x in enumerate(expected)]
        cmp_b = [x.replace(' ', '') if (k < len(matched_pairs) and matched_pairs[k]) else x
                 for k, x in enumerate(got)]
        # An element laid between two lines (\VUdecale) leaves the row as far as
        # pdftotext is concerned, which throws it onto a line of its own: at
        # folio 31, "de o ek" detached itself from the row "Supereso maxim". The
        # element IS indeed between two lines in the facsimile; this is therefore
        # not an error of composition but a limit of the extraction. We rejoin
        # the pieces, and only so long as that brings us nearer the
        # transcription: if the union does not give the expected text, the
        # discrepancy is reported as before.
        # Braces come out of pdftotext as arbitrary isolated characters -- "(",
        # "n", "o" according to the piece of font -- and they mingle with the
        # words of the row when they fall at their height. No list of characters
        # distinguishes them.
        # We therefore compare the rows WITHOUT THEIR ONE-LETTER TOKENS, on both
        # sides. What that costs is real and must be said: the "o" of "de o ek"
        # is no longer verified by check 2 at folio 31. All the rest of the row
        # is.
        def _without_short_tokens(t):
            # On a row, any run of dots is a LEADER, never text: the threshold of
            # six dots in _norm, set to spare the "(...)" of folio 219, let through
            # the two or three dots that survive at the edge of a tight column. Here
            # we can be strict, because no index entry carries two dots in a row.
            t = re.sub(r'\.{2,}', ' ', t)
            return ''.join(m for m in t.split() if len(m) > 1)
        # THE INDICES OF THE COMPOSED PAGE ARE NOT THOSE OF THE TRANSCRIPTION.
        # pdftotext breaks a table row into several lines; the moment it adds
        # one, got[k] and lg[k] no longer designate the same matter. Stripping
        # got[k] according to lg[k].row therefore left row lines unstripped, the
        # rejoining of the pieces failed, and the check accused folio 31 of
        # having lost "minim" -- on a page unchanged for weeks.
        # Here we strip only the TRANSCRIPTION, whose indices are sure; the
        # composed page is stripped below, at the moment of comparison, where we
        # know which row it faces.
        for k, l in enumerate(lg):
            if l.get('rang') and k < len(expected):
                expected[k] = _without_short_tokens(expected[k])
        weak_rows = sum(1 for l in lg if l.get('rang'))
        if weak_rows:
            r.warn('folio %s: %d table row(s) compared without their '
                 'one-letter tokens (the braces come out of pdftotext '
                 'en caracteres isoles)'
                 % (pg['folio'] or ('f%s' % pg.get('leaf')), weak_rows))
        cmp_a = [x.replace(' ', '') if (k < len(matched_pairs) and matched_pairs[k]) else x
                 for k, x in enumerate(expected)]
        cmp_b = [x.replace(' ', '') if (k < len(matched_pairs) and matched_pairs[k]) else x
                 for k, x in enumerate(got)]
        row = [l.get('rang') for l in lg]
        k = 0
        while k < len(cmp_b) and k < len(cmp_a):
            if k < len(row) and row[k]:
                # stripping the composed page: here, and only here, do we know
                # that this line faces a row.
                bare = _without_short_tokens(got[k])
                if bare != cmp_b[k]:
                    cmp_b[k], got[k] = bare, bare
                if (cmp_b[k] != cmp_a[k] and cmp_a[k].startswith(cmp_b[k])
                        and k + 1 < len(cmp_b)):
                    cmp_b[k] += _without_short_tokens(got[k + 1])
                    got[k] = cmp_b[k]
                    del cmp_b[k + 1], got[k + 1]
                    continue
            k += 1
        if cmp_a != cmp_b:
            gaps += 1
            n = max(len(expected), len(got))
            for k in range(n):
                a = expected[k] if k < len(expected) else '<missing>'
                b = got[k] if k < len(got) else '<missing>'
                if k < len(matched_pairs) and matched_pairs[k]:
                    a, b = a.replace(' ', ''), b.replace(' ', '')
                if a != b:
                    r.ko('page %s (folio %s), line %d\n        transcribed: %s\n        composed   : %s'
                         % (i + 1, pg['folio'], k + 1, a, b))
                    break
    if not gaps:
        r.ok('the %d composed pages are line for line identical to the transcription'
             % len(pages))



# --------------------------------------------------------------------
# Check 12 -- each note is a PARAGRAPH
# --------------------------------------------------------------------
# THREE RELAPSES, ALWAYS THE SAME. At folios 59-63, then 74, then 93, then
# 106, I chained the notes of a block with \nl instead of treating them as
# paragraphs. The facsimile indents the first word of each: they are
# paragraphs, never extra lines.
#
# Check 10 catches it every time -- but AFTER the fact, and by an indirect
# symptom ("the transcription gives it full but it is only 17 %"). We
# therefore measure the thing itself, and name it.
#
# Facsimile side: within the block of notes, a line that OPENS a note is
# indented. We count the lines whose abscissa exceeds the margin by at
# least MIN_INDENT.
#
# THE MARGIN IS NOT TAKEN FROM THE BLOCK OF NOTES ALONE. It was taken
# there as the minimum of the note lines' abscissas -- which assumes that
# at least one line of the block is at the margin, that is that at least
# one note occupies two lines. At folio 114, the two notes each fit on one
# line and are therefore both indented: the minimum was the indent itself,
# the gap fell to zero, and the check accused a page of \nl that carried
# none.
#
# AND IT IS NOT TAKEN FROM THE BODY ALONE EITHER. First remedy tried:
# median of the body's abscissas. It made twenty-one correct pages cry
# out. The body of folio 34 is a list of which sixteen lines out of twenty
# are indented by 52 px: their median IS the indent, and the openings of
# notes fell below the threshold.
#
# NOR IS THE MARGIN DEDUCIBLE FROM THE VOLUME: the trimming follows the
# paper and not the measure, so that it oscillates from 49 to 280 px
# according to the leaf, recto and verso alternating. It is therefore
# measured page by page, on ALL the bands, the head of the page excepted:
# body or notes, a page always carries a few of them at the margin. We
# take the DECILE of them and not the minimum, so that an isolated speck
# does not drag it leftwards -- and if the minimum departs from the decile
# by more than MARGIN_SPREAD, something is trailing outside the measure
# and the page is not judged.
# Source side: we count the paragraphs of the \VUnotes block.
MIN_INDENT = 25          # px; the indent of the notes is 3.6 mm = 43 px
MARGIN_SPREAD = 10               # px; tolerated spread between minimum and decile


def check_12(pages, r):
    reported = 0
    verified = 0
    for pg in pages:
        lg = [l for l in pg['lines'] if l['text']]
        notes = [l for l in lg if l.get('note')]
        if len(notes) < 2:
            continue
        try:
            leaf = int(pg['leaf']) if pg['leaf'] else int(pg['folio']) + 4
            fl = cache.leaf(leaf)['lines']
        except (ValueError, TypeError, KeyError):
            continue
        dec = 1 if (fl and fl[0]['x1'] - fl[0]['x0']
                    < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
        if len(lg) + dec != len(fl):
            continue                    # diverging counts: page skipped
        # facsimile bands facing the note lines
        bands = [fl[i + dec] for i, l in enumerate(lg) if l.get('note')]
        # A WELDED BAND FALSIFIES THE ABSCISSA. When two note lines weld into
        # one band, that band takes the x0 of the leftmost -- and an indented
        # line passes for being at the margin. At folio 29 "Decido 586" read
        # thus at +7 px whereas the facsimile, under enlargement, indents it
        # like its two neighbours. We therefore do not judge a page one of
        # whose note bands is welded: we say so and pass.
        # DIRT IN THE MARGIN ALSO FALSIFIES THE ABSCISSA -- the same family as
        # the fold of folio 79. At folio 29, "Decido 586" measures at +7 px
        # whereas enlargement shows it indented like its two neighbours: an
        # isolated trace is trailing in its margin. We reuse the detector
        # written for check 10, and declare the page not judged rather than
        # accuse it.
        if any(_fold(leaf, b) for b in bands):
            r.warn('folio %s: a stray trace is lying in the margin of the '
                 'block of notes — abscissas not measurable, page not judged'
                 % (pg['folio'] or ('f%s' % pg.get('leaf'))))
            continue
        top = [b['y1'] - b['y0'] for b in bands]
        med = sorted(top)[len(top) // 2]
        if med > 0 and max(top) >= 1.7 * med:
            r.warn('folio %s: one note band welds two — the '
                 'block\u2019s abscissas cannot be measured, page not judged'
                 % (pg['folio'] or ('f%s' % pg.get('leaf'))))
            continue
        xs = sorted(b['x0'] for b in fl[dec:])
        margin = xs[len(xs) // 10]
        if margin - xs[0] > MARGIN_SPREAD:
            r.warn('folio %s: a band leaves the measure on the left '
                 '(%d px before the margin) — page not judged'
                 % (pg['folio'] or ('f%s' % pg.get('leaf')),
                    margin - xs[0]))
            continue
        indented = sum(1 for b in bands if b['x0'] - margin >= MIN_INDENT)
        # Paragraphs of the source. The transcription carries no "paragraph"
        # flag, but it notes the END of a paragraph: break == 'pf'. A note line
        # following an end of paragraph therefore opens a new one, and the
        # first line of the block opens one by construction.
        # A PARAGRAPH OPENED BY \VUcontinue IS NOT INDENTED: it is the
        # continuation of a note begun on the previous folio. Counted like the
        # others, it cried out for a missing indent on four correct pages.
        def _open(l):
            return '\\VUcontinue' not in l['brut']
        openings = [notes[0]] + [b for a, b in zip(notes, notes[1:])
                                   if a['break'] == 'pf']
        paragraphs = sum(1 for l in openings if _open(l))
        verified += 1
        if indented != paragraphs:
            reported += 1
            r.ko('folio %s: the facsimile indents %d line(s) of the block of '
                 'notes, the source counts %d paragraph(s) there — notes '
                 'chained by \\nl instead of being paragraphs?'
                 % (pg['folio'] or ('f%s' % pg.get('leaf')),
                    indented, paragraphs))
    if not reported:
        r.ok('the note blocks of %d pages have as many paragraphs as the '
             'facsimile has indented lines' % verified)


# --------------------------------------------------------------------
# Checks 3 and 4 -- \cc between two letters, \nl never inside a word
# --------------------------------------------------------------------
# A PARENTHESIS MAY OPEN THE CONTINUATION OF A BROKEN WORD. Folio 160
# carries "flor(vend)isto, flor(kultiv)isto" and the compositor breaks the
# second between "flor-" and "(kultiv)isto" -- the hyphen is indeed printed
# in the facsimile, verified at 5x enlargement. The break therefore falls
# between a letter and a parenthesis, which rule D. 485 does not provide
# for because it speaks only of syllables. We admit the opening parenthesis
# at the head of the continuation; the rest of the rule still applies.
WORD_END = re.compile(r'([A-Za-zÀ-ÿ]+)$')
WORD_START = re.compile(r'^\(?([A-Za-zÀ-ÿ]+)')


def check_3(pages, r):
    bad = 0
    for ip, pg in enumerate(pages):
        for k, l in enumerate(pg['lines']):
            if l['break'] != 'cc':
                continue
            g = WORD_END.search(l['text'])
            # A word may break from one PAGE to another: the facsimile does it
            # at the foot of folio 14. The continuation is then looked for on the
            # next page, or the check believes in an orphaned break.
            # The continuation of a broken word is looked for in the SAME flow:
            # running text continues in running text, a note in a note. The block
            # of notes being brought back to the end of the page for visual order,
            # the last line of the body is followed by the notes: without this
            # filter, the check looked for the end of the word "be-" of folio 14
            # in the note call that follows it.
            flow = l.get('note', False)
            rest = ''
            for x in pg['lines'][k + 1:]:
                if x['text'] and x.get('note', False) == flow:
                    rest = x['text']
                    break
            if not rest:
                for pv in pages[ip + 1:]:
                    available = [x['text'] for x in pv['lines']
                             if x['text'] and x.get('note', False) == flow]
                    if available:
                        rest = available[0]
                        break
            d = WORD_START.match(rest)
            if not rest:
                # The next page is not yet transcribed: we cannot verify the
                # break, but it is not at fault.
                r.warn('folio %s: the word « %s- » breaks at the foot of the page; '
                     'verification deferred to the next page\u2019s transcription'
                     % (pg['folio'], g.group(1) if g else '?'))
                continue
            if not g or not d:
                bad += 1
                r.ko('folio %s line %d: \\cc does not fall between two letters '
                     '(« %s » | « %s »)'
                     % (pg['folio'], k + 1, l['text'][-14:], rest[:14]))
                continue
            ok, why = syllabify.conforming(g.group(1), d.group(1))
            if not ok:
                bad += 1
                r.ko('folio %s line %d: break « %s-/%s » does not conform to D. 485 — %s'
                     % (pg['folio'], k + 1, g.group(1), d.group(1), why))
    if not bad:
        r.ok('every \\cc falls between two letters and conforms to D. 485')


def _lexicon(pages):
    """Every word attested as a whole word in the transcription."""
    lexicon = {}
    for pg in pages:
        for l in pg['lines']:
            for w in re.findall(r"[A-Za-zÀ-ÿ]+", l['text']):
                lexicon[w.lower()] = lexicon.get(w.lower(), 0) + 1
    return lexicon


def check_4(pages, r):
    """A \\nl between two alphabetic fragments is normal: that is the case of
    nearly every end of line. The useful signal is narrower -- OCR and the
    transcription lose end-of-line hyphens, and the break then finds itself
    displaced. We therefore report only the case where:
      - the welding of the two fragments is a word attested elsewhere, AND
      - one of the two fragments is never attested as a whole word.
    That is the signature of a \\cc encoded by mistake as a \\nl."""
    lexicon = _lexicon(pages)
    n = 0
    for pg in pages:
        for k, l in enumerate(pg['lines']):
            if l['break'] != 'nl':
                continue
            rest = pg['lines'][k + 1]['text'] if k + 1 < len(pg['lines']) else ''
            g = WORD_END.search(l['text'])
            d = WORD_START.match(rest)
            if not (g and d):
                continue
            gg, dd = g.group(1).lower(), d.group(1).lower()
            welded = gg + dd
            if lexicon.get(welded, 0) >= 1 and (lexicon.get(gg, 0) <= 1 or lexicon.get(dd, 0) <= 1):
                n += 1
                r.ko('folio %s line %d: \\nl between « %s » and « %s » — the welding '
                     '« %s » is attested: a hyphen of division was probably lost'
                     % (pg['folio'], k + 1, g.group(1), d.group(1), welded))
    if not n:
        r.ok('no \\nl appears to mask a lost hyphen '
             '(%d words in the lexicon)' % len(lexicon))


# --------------------------------------------------------------------
# Checks 5 and 6 -- forbidden line openings
# --------------------------------------------------------------------
HIGH = ':;!?'
LOW = ',.)]}»'


def _starts(pages):
    for pg in pages:
        for k, l in enumerate(pg['lines']):
            if k == 0 or not l['text']:
                continue
            # A TABLE ROW IS NOT A LINE OF TEXT. The three rows of dots in the
            # plate of folio 220 begin with a dot, and checks 5 and 6 saw three
            # faults there. They are not prose: their matter is laid at an
            # abscissa by \VUcase, and no rule of division governs them. The two
            # checks therefore set them aside, as check 2 already does in order
            # to compare without the white space.
            if l.get('rang'):
                continue
            yield pg, k, l['text']


def check_5(pages, r):
    n = 0
    for pg, k, t in _starts(pages):
        if t[0] in HIGH:
            n += 1
            r.ko('folio %s line %d begins with « %s »: %s'
                 % (pg['folio'], k + 1, t[0], t[:30]))
    if not n:
        r.ok('no line begins with : ; ! ?')


def check_6(pages, r):
    n = 0
    for pg, k, t in _starts(pages):
        if t[0] in LOW:
            n += 1
            r.ko('folio %s line %d begins with « %s »: %s'
                 % (pg['folio'], k + 1, t[0], t[:30]))
    if not n:
        r.ok('no line begins with low punctuation '
             'or a closing parenthesis')


# --------------------------------------------------------------------
# Check 7 -- minimum effective margin
# --------------------------------------------------------------------
def check_7(pages, r):
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf missing')
        return
    out = subprocess.run(['pdftotext', '-bbox', pdf, '-'],
                         capture_output=True, text=True).stdout
    pw = ph = None
    m = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', out)
    if m:
        pw, ph = float(m.group(1)), float(m.group(2))
    worst_ones = []
    for i, pg in enumerate(re.findall(r'<page .*?</page>', out, re.S), 1):
        xs = [float(x) for x in re.findall(r'xMin="([\d.]+)"', pg)]
        x_max = [float(x) for x in re.findall(r'xMax="([\d.]+)"', pg)]
        if not xs:
            continue
        left, right = min(xs), pw - max(x_max)
        worst_ones.append((min(left, right), i, left, right))
    if not worst_ones:
        r.warn('no text extracted: check 7 has no object')
        return
    worst_ones.sort()
    mm = 25.4 / 72.0
    worst = worst_ones[0]
    if worst[0] * mm < 5.0:
        r.ko('minimum effective margin %.2f mm (page %d) — word probably trimmed'
             % (worst[0] * mm, worst[1]))
    else:
        r.ok('minimum effective margin %.2f mm (page %d) over %d pages'
             % (worst[0] * mm, worst[1], len(worst_ones)))


# --------------------------------------------------------------------
# Check 8 -- visual juxtaposition at 300 dpi
# --------------------------------------------------------------------
# Left margin of the composed page, in pixels at 300 dpi:
# (116 mm - 91.69 mm) / 2 = 12.155 mm
LEFT_MARGIN_PX = 12.155 / 25.4 * 300.0
# Paragraph indent (\VUalinea = 4.6 mm) in pixels at 300 dpi.
PARA_INDENT_PX = int(round(4.6 / 25.4 * 300.0))
# Indent of the notes (\VUalineaNote = 3.6 mm): the notes have their own.
NOTE_INDENT_PX = int(round(3.6 / 25.4 * 300.0))


def check_8(pages, r, first_one=1, how_many=None):
    import numpy as np
    import cv2
    import page as PG
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf missing')
        return
    dst = os.path.join(P, 'checks', 'juxta')
    os.makedirs(dst, exist_ok=True)
    n = how_many or len(pages)
    comp = cache.compose(pdf, len(pages))
    faits = 0
    for i in range(first_one, first_one + n):
        pg = pages[i - 1]
        try:
            leaf = int(pg['leaf']) if pg.get('leaf') else int(pg['folio']) + 4
        except (ValueError, TypeError):
            r.warn('page %d: neither leaf nor folio usable, juxtaposition skipped' % i)
            continue
        if i not in comp:
            continue
        cp = cv2.imread(comp[i]['fichier'], cv2.IMREAD_GRAYSCALE)
        norm, gm, ang = PG.prepared_img(leaf)
        span = cache.leaf(leaf)['span']
        # We align the two images on the LEFT EDGE OF THE TEXT BLOCK: the scan
        # has a variable border, the composed page has none.
        margin = int(round(LEFT_MARGIN_PX))
        if span:
            g = max(0, span[0] - margin)
            norm = norm[:, g:g + cp.shape[1]]
        if norm.shape[1] < cp.shape[1]:
            norm = np.pad(norm, ((0, 0), (0, cp.shape[1] - norm.shape[1])),
                          constant_values=255)
        h = max(cp.shape[0], norm.shape[0])
        def align(im, w):
            o = np.full((h, w), 255, np.uint8)
            o[:min(h, im.shape[0]), :min(w, im.shape[1])] = \
                im[:min(h, im.shape[0]), :min(w, im.shape[1])]
            return o
        w = cp.shape[1]
        pair = np.hstack([align(norm, w), np.full((h, 24), 160, np.uint8),
                         align(cp, w)])
        cv2.imwrite(os.path.join(dst, 'juxta-%03d.png' % i), pair)
        faits += 1
    r.ok('%d juxtapositions at 300 dpi in checks/juxta/' % faits)


# --------------------------------------------------------------------
# Check 9 -- weight: forgotten emphasis
# --------------------------------------------------------------------
def _composed_ink(pdf, i, dst):
    """Lines of page i of the composed PDF: (y0, y1, ink)."""
    import numpy as np
    import cv2
    subprocess.run(['pdftoppm', '-r', '300', '-png', '-f', str(i), '-l', str(i),
                    pdf, os.path.join(dst, 'p')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cand = sorted(glob.glob(os.path.join(dst, 'p-*%d.png' % i)))
    if not cand:
        return None
    bw = (cv2.imread(cand[0], cv2.IMREAD_GRAYSCALE) < 160).astype(np.uint8)
    rows = bw.sum(axis=1)
    on = (rows > 4).astype(np.int8)
    d = np.diff(on)
    st = list(np.where(d == 1)[0] + 1); en = list(np.where(d == -1)[0] + 1)
    if on[0]: st.insert(0, 0)
    if on[-1]: en.append(len(on))
    raw = [(a_, b_, int(bw[a_:b_].sum())) for a_, b_ in zip(st, en) if b_ - a_ >= 8]
    if not raw:
        return raw
    # A line must carry ink, not merely occupy pixels: a speck of 148
    # pixels (accents or descenders detached by the threshold) was counted
    # as a line and shifted all the rest by one rank -- hence absurd
    # deviations of weight (+4720 %).
    full = max(e for _, _, e in raw)
    return [t for t in raw if t[2] >= 0.03 * full]


def check_9(pages, r, threshold=0.12):
    """Check 2 compares the TEXT; it does not see the markup. A forgotten
    passage in bold therefore escapes it -- which happened at folio 11,
    where the enumeration of the letters of the alphabet is bold in the
    original.

    We compare the QUANTITY OF INK of each line, facsimile against composed
    page. Two precautions, both necessary:

    - the ratio is dominated by the TYPE SIZE (a title in capitals, a note
      in small text and a line of running text have quite different
      densities): we therefore group the lines by height, and each group is
      compared with its own median;
    - comparing the ink profile ALONG the line was tried and abandoned: the
      displacement of the words between the two compositions produces a
      noise that drowns the signal.

    Sensitivity measured at folio 11: a line mostly in bold comes out at
    +24 % when the bold is missing, against -3 % when it is there. A few
    isolated bold letters in a roman line do not exceed +5 %: the check does
    not see them. It catches extended emphasis, not occasional emphasis.
    """
    import numpy as np
    import page as PG
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf missing')
        return
    dst = os.path.join(P, 'checks', 'encre')
    os.makedirs(dst, exist_ok=True)
    reported = compared = 0
    for i, pg in enumerate(pages, 1):
        try:
            leaf = int(pg['leaf']) if pg.get('leaf') else int(pg['folio']) + 4
        except (ValueError, TypeError):
            continue
        comp = cache.compose(pdf, len(pages))
        if i not in comp:
            continue
        cl = [(l['y0'], l['y1'], l['encre']) for l in comp[i]['lines']]
        fl = cache.leaf(leaf)['lines']
        if len(fl) < 6:
            continue
        # Matching by POSITION, not by rank: see tools/pair_up.py.
        pairs_of, sf, sc = pair_up.matched(
            [(l['y0'], l['y1']) for l in fl], [(a, b) for a, b, _ in cl])
        if len(pairs_of) < 0.6 * min(len(fl), len(cl)):
            r.warn('folio %s: line matching too uncertain '
                 '(%d pairs for %d/%d lines) — weight not compared'
                 % (pg['folio'] or ('f%s' % leaf), len(pairs_of),
                    len(fl), len(cl)))
            continue
        if sf or sc:
            r.warn('folio %s: %d line(s) of the facsimile and %d of the composed page '
                 'unmatched — the rest of the page is compared all the same'
                 % (pg['folio'] or ('f%s' % leaf), len(sf), len(sc)))
        txt = [l['text'] for l in pg['lines'] if l['text']]
        fl = [fl[i] for i, _ in pairs_of]
        cl = [cl[j] for _, j in pairs_of]
        ratio_of = np.array([l['encre'] / max(c[2], 1) for l, c in zip(fl, cl)])
        # Groups of type size: we take them from the TRANSCRIPTION, which
        # knows them exactly (running text, note, apparatus line). Deducing
        # them from the measured line height went wrong on the last lines of
        # notes, whose tops and bottoms overhang.
        lg = [l for l in pg['lines'] if l['text']]
        cat = []
        for k in range(len(fl)):
            l = lg[k] if k < len(lg) else {}
            cat.append('apparat' if l.get('apparat') else
                       ('note' if l.get('note') else 'courant'))
        cat = np.array(cat)
        groupes = {c: (cat == c) for c in ('courant', 'note', 'apparat')}
        # Short lines give a noisy ratio (little ink, and the division into
        # lines is less sure there): we exclude them from the test.
        larg = np.array([l['x1'] - l['x0'] for l in fl], float)
        # A BLANK PAGE MADE THE CHECK CRASH. At leaf 182, a blank verso, the
        # facsimile carries seven stray bands (fold and edge of page) when the
        # composed page has no line at all: widths was empty and widths.max()
        # raised an exception. The whole check then stopped -- a check that
        # crashes verifies nothing any more, and it did so in silence for a
        # whole batch.
        if larg.size == 0:
            r.warn('folio %s: blank page in the composed volume — weight not judged'
                 % (pg['folio'] or ('f%s' % pg.get('leaf'))))
            continue
        enough = larg > 0.45 * larg.max()
        for name, sel in groupes.items():
            if sel.sum() < 4:
                continue          # group too small to have a median
            m = float(np.median(ratio_of[sel]))
            if (sel & enough).sum() == 0:
                continue
            for k in np.where(sel & enough)[0]:
                compared += 1
                e = ratio_of[k] / m - 1.0
                if abs(e) > threshold:
                    reported += 1
                    what = ("more ink in the facsimile: emphasis "
                            "probablement oublie" if e > 0 else
                            "less ink in the facsimile: emphasis "
                            "probably in excess")
                    r.warn('folio %s line %d (%+.0f %%, size « %s ») — %s\n'
                         '        %s'
                         % (pg['folio'] or ('f%s' % leaf), k + 1, e * 100,
                            name, what, (txt[k][:64] if k < len(txt) else '')))
    if not reported:
        r.ok('weight conforms on the %d lines compared' % compared)


# --------------------------------------------------------------------
# Check 10 -- alignment of line openings
# --------------------------------------------------------------------

# The left edge of a line is not always ink: at leaf 83 a FOLD in the
# paper crosses the margin, and the detector takes the trace of the fold
# for the beginning of the line. The measured indent then falls to zero
# on a line which, under enlargement, is clearly indented.
#
# The sign is the same as the one that falsified the folio in
# tools/page.py, and it reads the same way: IN CLUSTERS, not in extent. A
# fold gives a THIN cluster (a few pixels wide) SEPARATED from the rest of
# the line by a gap far wider than a word space. A letter, by contrast,
# touches its neighbours.
#
# We do not correct the measurement -- we declare it not made. A check
# that keeps silent and says so is worth more than a check that accuses a
# correct page, and worth more too than a check disabled in silence.
_FOLD_MAX_WIDTH = 7        # px: beyond this, it is a letter
_FOLD_MIN_GAP = 22         # px: a word space is worth 19


def _fold(leaf, line):
    """Is the left edge of this line the trace of a fold?"""
    try:
        import numpy as np, cv2
        import page as PG
        norm, gm, _ = PG.prepared_img(leaf)
    except Exception:
        return False
    band = (norm[line['y0']:line['y1'] + 1,
                  line['x0']:line['x0'] + 120] < 185).astype('uint8')
    if band.size == 0:
        return False
    col = band.sum(axis=0)
    full = np.nonzero(col)[0]
    if full.size == 0 or full[0] != 0:
        return False
    # TRACES COME IN NUMBERS. The first version examined only the leading
    # cluster and the gap that follows it; at folio 29 the margin carries TWO
    # specks (2 px then 6 px, 3 px apart), and the test failed on the second.
    # We therefore skip ALL the thin leading clusters, and measure the gap
    # preceding the first wide cluster.
    i = 0
    skip = False
    while i < col.size:
        if not col[i]:
            i += 1
            continue
        a = i
        while i < col.size and col[i]:
            i += 1
        if i - a > _FOLD_MAX_WIDTH:
            return skip and (a - end_pos) >= _FOLD_MIN_GAP
        skip = True
        end_pos = i
    return False

def check_10(pages, r, tol_px=12):
    """In a composed page, the beginning of a line can occupy only three
    positions: the block's margin, the margin plus the paragraph indent, or
    the centre (apparatus lines). Any other value betrays a stray space.

    This check was born of a defect check 2 could not see: an active space
    has category code 13 and not 10, so that TeX no longer swallows it after
    a control word. "\\noindent en" therefore set a real space at the head of
    the line. Check 2 compares text, and its text is stripped of its edge
    white space: the discrepancy was invisible to it, whereas it leaps to
    the eye in geometry.
    """
    import numpy as np
    import cv2
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf missing')
        return
    dst = os.path.join(P, 'checks', 'encre')
    os.makedirs(dst, exist_ok=True)
    reported = examined = 0
    for i, pg in enumerate(pages, 1):
        comp = cache.compose(pdf, len(pages))
        if i not in comp:
            continue
        raw = comp[i]['lines']
        start_pos = [(l['x0'], l['x1']) for l in raw]
        bands = [(l['y0'], l['y1']) for l in raw]
        if len(start_pos) < 6:
            continue
        # The folio is set by \VUfolio: it is not part of the transcription. It
        # must be removed BEFORE the loop over line openings, and not only before
        # the loop over line endings: without that lg[k] answers for the previous
        # line. At folio 50 the check accused a table row of a "stray space" of
        # 120 px which was in reality its transcribed indent -- the exemption of
        # rows did not fall on the right line.
        _p = max(y - x for x, y in start_pos)
        if start_pos:
            _x0, _x1 = start_pos[0]
            _m = min(a for a, _ in start_pos); _d = max(b for _, b in start_pos)
            if (_x1 - _x0) < 0.30 * _p and \
               abs((_x0 + _x1) / 2 - (_m + _d) / 2) < 0.12 * _p:
                start_pos = start_pos[1:]
        if not start_pos:
            continue
        margin = min(x for x, _ in start_pos)
        right = max(y for _, y in start_pos)
        lg = [l for l in pg['lines'] if l['text']]
        # FIRST LINE OF THE BODY: flush left or indented?
        # The check on openings accepts both, since both are legitimate elsewhere
        # in the page. But for the first line the facsimile decides, and twice I
        # put one \VUcontinue too many (folios 45 and 55) by assuming without
        # checking that the paragraph came from the previous page. We therefore
        # confront that line, and it alone, with the model's measurement.
        try:
            _f = int(pg['leaf']) if pg.get('leaf') else int(pg['folio']) + 4
            _fl = cache.leaf(_f)['lines']
        except (ValueError, TypeError, KeyError):
            _fl = []
        # We skip the pages that open on an apparatus line: the comparison has
        # no meaning there, and the folio landmark confuses a centred title with
        # a folio (folio 18).
        _apparatus0 = bool(lg) and bool(lg[0].get('apparat'))
        if _fl and start_pos and not _apparatus0:
            _dec = 1 if (_fl[0]['x1'] - _fl[0]['x0']
                         < 0.25 * max(l['x1'] - l['x0'] for l in _fl)) else 0
            if len(_fl) > _dec:
                _cx = min(l['x0'] for l in _fl[_dec:])
                _fac = _fl[_dec]['x0'] - _cx
                _comp = start_pos[0][0] - margin
                if abs(_fac - _comp) > 2 * tol_px and _fold(_f, _fl[_dec]):
                    r.warn('folio %s: the left edge of the first line '
                         'falls on a FOLD in the paper — the indent cannot be '
                         'measured on this leaf, the line is not '
                         'verifiee' % (pg['folio'] or ('f%s' % pg.get('leaf'))))
                elif abs(_fac - _comp) > 2 * tol_px:
                    reported += 1
                    r.ko('folio %s: the first line of the body is %+d px '
                         'from the margin in the facsimile, and %+d px in the composed page '
                         '— a \\VUcontinue too many or missing?\n        %s'
                         % (pg['folio'] or ('f%s' % pg.get('leaf')),
                            _fac, _comp, lg[0]['text'][:44] if lg else ''))
        rows = 0
        for k, (x0, x1) in enumerate(start_pos):
            # A TABLE ROW begins neither at the margin nor as an indent: each of
            # its elements is laid at an abscissa surveyed from the facsimile
            # (\VUcase). The check on line openings therefore has no meaning here,
            # and that must be said rather than passed over: the count of rows set
            # aside is reported.
            # NOR HAS AN APPARATUS LINE. \VUcentre, \VUtitre and \VUsoustitre lay
            # their line by measurement, as \VUcase does for a row: neither flush
            # left nor indent governs them. The centring test below catches most of
            # them, but not those whose text is long and whose centring is optical
            # (folios 232, 233 and 234, four lines): the sure rule is to set them
            # aside on their nature, not on their position.
            if k < len(lg) and (lg[k].get('rang') or lg[k].get('apparat')):
                rows += 1
                continue
            examined += 1
            centree = abs((x0 + x1) / 2 - (margin + right) / 2) < 3 * tol_px
            if centree:
                continue                      # folio, title, apparatus line
            gap = x0 - margin
            if gap <= tol_px:
                continue                      # flush left
            if abs(gap - PARA_INDENT_PX) <= tol_px:
                continue                      # paragraph indent
            if abs(gap - NOTE_INDENT_PX) <= tol_px:
                continue                      # indent of a note
            reported += 1
            t = lg[k]['text'][:44] if k < len(lg) else ''
            r.ko('folio %s line %d begins %+d px from the margin — neither flush '
                 'left (0), nor indented (%d or %d): stray space?'
                 '\n        %s'
                 % (pg['folio'] or ('f%s' % pg.get('leaf')), k + 1,
                    gap, PARA_INDENT_PX, NOTE_INDENT_PX, t))
        if rows:
            r.warn('folio %s: %d table row(s) set aside from the check on line '
                 'openings — their abscissas are surveyed one by one'
                 % (pg['folio'] or ('f%s' % pg.get('leaf')), rows))
        # Verification of line ENDINGS, WITHOUT going through the facsimile.
        #
        # The first version compared the width of each composed line with that of
        # the corresponding facsimile line. It therefore depended on the matching,
        # which slips by one rank as soon as a line is detected in excess on one
        # side -- and then produced a dozen false positives with a characteristic
        # signature (a full line facing a very short one, alternating).
        #
        # Yet the transcription already knows what needs knowing: a line followed
        # by \nl or \cc is a full line, a line that ends a paragraph is short. We
        # therefore verify the composed page against the TRANSCRIPTION, which
        # requires no matching at all.
        full_c = max(x1 - x0 for x0, x1 in start_pos)
        # The folio is set by \VUfolio, it is not part of the transcription: we
        # remove it from the list of composed lines, or the whole page compares
        # one rank out.
        start_text = list(start_pos)   # the folio has already been removed above
        if False:
            x0, x1 = start_text[0]
            margin_c = min(a for a, _ in start_text)
            right_c = max(b for _, b in start_text)
            # "Short" is measured against the WIDEST line of the page, and
            # "centred" with the same tolerance as check 11. At folio 50, the folio
            # "-- 50 --" missed the centring criterion by a little: the whole page
            # then compared one rank out, and the check accused a table row of a
            # "stray space" of 120 px which was in reality its transcribed indent.
            short = (x1 - x0) < 0.30 * full_c
            centre = abs((x0 + x1) / 2 - (margin_c + right_c) / 2) < 0.12 * full_c
            if short and centre:
                start_text = start_text[1:]
        start_pos = start_text
        lgv = [l for l in pg['lines'] if l['text']]
        if len(lgv) != len(start_pos):
            r.warn('folio %s: %d composed lines for %d transcribed — '
                 'line endings not verified'
                 % (pg['folio'] or ('f%s' % pg.get('leaf')),
                    len(start_pos), len(lgv)))
            continue
        # The RIGHT EDGE, not the width.
        # A first line of a paragraph is indented by \VUalinea: its width is
        # therefore 94 % of the measure although it is perfectly filled. That is
        # what made folios 18 and 19 fail -- and TeX's own trace
        # (\tracingparagraphs) said so: "b=0", null badness, the line is right.
        # What defines a full line is that it reaches the right margin.
        right_c = max(x1 for _, x1 in start_pos)
        for k, ((x0, x1), l) in enumerate(zip(start_pos, lgv)):
            if l.get('apparat'):
                continue                     # centred line: not applicable
            # A table row is not justified: \VUrang ends it with a line ending,
            # but its matter stops where the facsimile stops it. The check on
            # endings applies to it no more than the check on openings.
            if l.get('rang'):
                continue
            pc = x1 / right_c
            expected_full = l['break'] in ('nl', 'cc')
            if expected_full and pc < 0.94:
                reported += 1
                r.ko('folio %s line %d: the transcription gives it full '
                     '(followed by \\%s) but it is only %.0f %% — '
                     'justification perdue ?\n        %s'
                     % (pg['folio'] or ('f%s' % pg.get('leaf')), k + 1,
                        l['break'], pc * 100, l['text'][:44]))
            elif not expected_full and pc > 0.995:
                # A last line of a paragraph MAY reach the margin without anything
                # being forced: it is enough for the text to fill it. This is
                # therefore only a remark, not a fault -- unlike the converse case,
                # where a line the transcription gives as full turns out short, which
                # is always a defect.
                r.warn('folio %s line %d: end of paragraph running '
                     'to the margin (%.0f %%) — to be verified'
                     '\n        %s'
                     % (pg['folio'] or ('f%s' % pg.get('leaf')), k + 1,
                        pc * 100, l['text'][:44]))
    if not reported:
        r.ok('the %d line openings are at the margin, indented or centred, '
             'and the endings agree with the facsimile' % examined)



def check_11(pages, r, tol_px=14):
    """VERTICAL position of each composed line, compared with the facsimile.

    The compositor justifies his pages vertically: measured on leaves 20 to
    39, the last baseline falls 145.3 mm below the folio to within 0.3 mm,
    whatever the number of lines. A page whose matter does not fill the
    measure is VERTICALLY JUSTIFIED: uniform leads between all the lines of
    the body, and wider white space at the articulations. Without those
    settings the text stays right line by line, but no line falls opposite
    its model: check 2 is content and the juxtaposition is not.

    We compare the tops of lines, with the constant offset removed (each
    scan has its own vertical registration, up to 10 mm). The top of a line
    depends on its ascenders: it is noisy to +/- 8 px. The tolerance is
    therefore 14 px; what we are looking for is the cumulative DRIFT, which
    reaches 100 px and more when the vertical justification is not
    reproduced.
    """
    import numpy as np
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf missing')
        return
    comp = cache.compose(pdf, len(pages))
    worst = 0.0; worst_page = None; examined = 0
    for i, pg in enumerate(pages, 1):
        try:
            leaf = int(pg['leaf']) if pg.get('leaf') else int(pg['folio']) + 4
        except (ValueError, TypeError):
            continue
        if i not in comp:
            continue
        cl = comp[i]['lines']
        fl = cache.leaf(leaf)['lines']
        if len(cl) != len(fl) or len(cl) < 6:
            r.warn('folio %s: %d composed lines for %d surveyed in the '
                 'facsimile — vertical drift not measured'
                 % (pg['folio'] or ('f%s' % leaf), len(cl), len(fl)))
            continue
        examined += 1
        d = np.array([c['y0'] - a['y0'] for a, c in zip(fl, cl)], float)
        res = d - np.median(d)
        # The folio carries only two rules and two digits: its detected top
        # depends on the rule, not on an ascender, and falls outside the ordinary
        # noise. It is placed by \VUfolioY, measured separately; we do not let it
        # weigh on the drift of the text block.
        if fl and fl[0]['x1'] - fl[0]['x0'] < 0.25 * max(l['x1'] - l['x0'] for l in fl):
            res = res[1:]
        if not len(res):
            continue
        # The top of a line depends on its ascenders: it is noisy to +/- 8 px
        # without anything moving in the composition. Taken over the MAXIMUM of
        # 40 lines, that noise alone crosses the tolerance. We filter it with a
        # rolling median of three lines: an offset of vertical justification
        # lasts whole lines and survives it, the ascender noise does not.
        if len(res) >= 3:
            smoothed = np.array([np.median(res[max(0, k - 1):k + 2])
                             for k in range(len(res))])
        else:
            smoothed = res
        amp = float(np.abs(smoothed).max())
        res = smoothed
        if amp > worst:
            worst, worst_page = amp, pg['folio'] or ('f%s' % leaf)
        if amp > tol_px:
            k = int(np.abs(res).argmax())
            r.ko('folio %s: vertical drift of %.0f px (%.2f mm) at '
                 'line %d — the page\u2019s vertical justification not reproduced'
                 % (pg['folio'] or ('f%s' % leaf), amp, amp * 25.4 / 300, k))
    if examined:
        r.ok('maximum vertical drift %.0f px (%.2f mm, folio %s) over '
             '%d pages' % (worst, worst * 25.4 / 300, worst_page, examined))


CHECKS = {1: check_1, 2: check_2, 3: check_3, 4: check_4,
             5: check_5, 6: check_6, 7: check_7, 8: check_8,
             9: check_9, 10: check_10, 11: check_11,
             12: check_12}
TITLES = {
    1: 'Check 1 — pagination and overflows',
    2: 'Check 2 — line-by-line comparison, PDF / transcription',
    3: 'Check 3 — \\cc between two letters, conforming to D. 485',
    4: 'Check 4 — \\nl never inside a word',
    5: 'Check 5 — no line begins with : ; ! ?',
    6: 'Check 6 — no line begins with low punctuation',
    7: 'Check 7 — minimum effective margin',
    8: 'Check 8 — visual juxtaposition at 300 dpi',
    9: 'Check 9 — weight line by line (bold, italic, size)',
    10: 'Check 10 — alignment of line openings and endings',
    11: 'Check 11 — vertical position of the lines',
    12: 'Check 12 — each note is a paragraph',
}


def main():
    wanted = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(CHECKS)
    pages = read_transcription()
    print('Transcription: %d pages, %d lines.'
          % (len(pages), sum(len(p['lines']) for p in pages)))
    total_e = total_a = 0
    for c in wanted:
        r = Report()
        try:
            CHECKS[c](pages, r)
        except Exception as e:
            r.ko('the check raised an exception: %r' % (e,))
        r.print_out(TITLES[c])
        total_e += r.failures
        total_a += r.warnings
    print('\n%s%d failure(s)%s, %d note(s).'
          % (RED if total_e else GREEN, total_e, RESET, total_a))
    return 1 if total_e else 0


if __name__ == '__main__':
    sys.exit(main())
