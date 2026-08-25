#!/usr/bin/env python3
"""LIST OF WITNESSES: one characteristic string per fix.

Five lost containers have shown that "git log" proves nothing: last time
the history was coherent and the FILES were not. What detects the failure
is to look, for each fix, for a string that can be there only if it is in
place.

    python3 tools/witnesses.py     # exits 1 if a witness is missing
"""
import os, re, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = [
 # (label, file, expected string, minimum count)
 ('folio 82: Ultre alone in bold', 'content/10-part1.tex',
  '\\VUgras{Ultre} esas', 1),
 ('clickable references in the Tabelo', 'preamble.tex', '\\VUlienOuvre', 3),
 ('gap before a wide number', 'preamble.tex',
  '\\newcommand{\\VUindexEcart}', 1),
 ('PDF named gramatiko', 'build.mk', 'jobname=gramatiko', 1),
 ('title of folio 3 compressed', 'content/00-front-matter.tex',
  '\\VUetroit{0.702}', 1),
 ('KONSTATO compressed', 'content/00-front-matter.tex',
  '\\VUetroit{0.793}', 1),
 ('Averto compressed', 'content/00-front-matter.tex',
  '\\VUetroit{0.822}', 1),
 ('cover title compressed', 'content/00-front-matter.tex',
  '\\VUetroit{0.668}', 1),
 ('PUNTIZADO widened', 'content/20-part2.tex', '\\VUetroit{0.857}', 1),
 ('white space of folio 21', 'content/10-part1.tex', '\\VUsaut{6.47mm}', 1),
 ('white space of folio 122', 'content/20-part2.tex', '\\VUsaut{6.93mm}', 1),
 ('white space of folio 169', 'content/20-part2.tex', '\\VUsaut{6.90mm}', 1),
 ('white space of folio 195', 'content/20-part2.tex', '\\VUsaut{11.17mm}', 1),
 ('hidden mark', 'preamble.tex', '\\VUmarqueCachee', 2),
 ('plate at an absolute ordinate', 'preamble.tex', '\\VUplancheA', 2),
 ('portrait set upright (width)', 'preamble.tex',
  '\\VUplancheLargeur}{61.30mm}', 1),
 ('portrait set upright (ordinate)', 'content/00-front-matter.tex',
  '\\VUplancheA{55.88mm}', 1),
 ('vignette set upright', 'content/00-front-matter.tex',
  '\\VUimageA{104.72mm}{22.38mm}', 1),
 ('bookmarks: APENDICI group', 'content/90-marks.tex',
  'count -10 {APENDICI}', 1),
 ('bookmarks: Tabelo page 227', 'content/90-marks.tex',
  'goto page 227 {/Fit} count 0 {TABELO', 1),
 ('page: Introdukto', 'tools/html.py', 'Introdukto', 1),
 ('page: header height measured', 'tools/html.py', 'observerBand', 4),
 ('page: chefa vorti', 'tools/html.py', 'Chefa vorti', 1),
 ('page: en la tota libro', 'tools/html.py', 'tota libro', 1),
 ('page: old anchors caught', 'tools/html.py',
  'function findAnchor', 1),
 ('page: rejoined notes counted', 'tools/html.py', 'n_rejoined', 2),
 ('page: asterism at its white space', 'tools/html.py', 'self.aster', 3),
 ('page: ends of the braces', 'tools/html.py', 'M8.6 1C5.8', 1),
 ('page: notice on the two prepozicioni', 'tools/html.py',
  'ridonas li a la loko', 1),
 # Folio 31: the CLOSING brace. For want of being read, it attached only
 # "maxim" to "de o ek", and the name fell back half a line too high.
 # Three witnesses: the reading of the closing brace, its merging into the
 # group it covers, and the half-height offset in columns.
 ('folio 31: closing brace read', 'tools/html.py',
  'def closers', 1),
 ('folio 31: closing brace merged into the group', 'tools/html.py',
  "ferme_brace", 3),
 # The cell laid half-way between two rows: the set that collects them,
 # and the class the column rendering emits for them. The witness used to
 # count a local variable; a class the page carries is the sturdier anchor.
 ('folio 31: cell at half height in columns', 'tools/html.py',
  "mid.add(", 1),
 ('folio 31: half-height class emitted', 'tools/html.py',
  "'mez'", 1),
 ('folio 31: unbreakable member', 'tools/html.py',
  '.gr-m{white-space:nowrap}', 1),
 ('folio 31: left edge of a group', 'tools/html.py',
  'def edge', 1),
 # Folio 220: the two diagrams are centred on the measure. The mark is
 # set from the scan (equal left and right margins), not by eye; three
 # witnesses, one per piece.
 ('folio 220: centring mark', 'preamble.tex',
  '\\newcommand{\\VUtabloCentrita}', 1),
 ('folio 220: both diagrams marked', 'content/20-part2.tex',
  '\\VUtabloCentrita', 2),
 ('folio 220: centring rendered', 'tools/html.py',
  '.centrita{display:flex', 1),
 # THE BARE ASTERISK is a note mark (leaves 74 and 122), and the call is
 # looked for in the very form the facsimile uses -- "(*)" on leaves 166,
 # 191, 208, the bare asterisk on the other two. Confusing them would
 # break the former.
 ('note with a bare asterisk read', 'tools/html.py',
  "re.match(r'(\\*)', bare)", 1),
 ('call looked for in its own form', 'tools/html.py',
  "note['apel']", 1),
 # Folio 130: the call set BEFORE the head must not hide the headword.
 # The TABELO itself names the chapter's three: equi-, ko-, mono-.
 ('call before the head: headword read', 'tools/html.py',
  'CALL_BEFORE_HEAD', 3),
 # Folio 31: the group carrying a closing brace does not stretch, or the
 # brace is thrown against the right edge of the panel.
 ('closing brace against its members', 'tools/html.py',
  '.gr.gf>.gr-l{flex:0 1 auto}', 1),
 # The headword is judged on what it IS, not on its weight: an example
 # sentence does not open a section, an entry in italic does. Five
 # witnesses, one per piece of the rule.
 ('page: example excluded by its verb', 'tools/html.py',
  'IDO_VERB', 2),
 ('page: non-verbal words spared', 'tools/html.py',
  "NOT_VERBS = {'plus'", 1),
 ('page: head in italic or small capitals', 'tools/html.py',
  'SET_OFF_HEAD', 2),
 ('page: cut at the mark of definition', 'tools/html.py',
  'DEF_CUT', 2),
 ('page: shortened anchor caught', 'tools/html.py',
  "if(id.indexOf(x+'-')===0", 1),
 # TWO CLASSES OF ENTRY, AND ONE CASE FOR EACH. The cited word takes the
 # case of the word -- the facsimile capitalises the entry that OPENS a
 # paragraph and leaves in lower case those that follow ("Interne" folio
 # 62, "extere, supre, infre..." folio 63) -- the five proper names
 # excepted; the section heading keeps its capital. The weight separates
 # them: bold cites, italic and small capitals name. Four witnesses: the
 # rule, the weight returned by `headword()`, the list of proper names,
 # and that of the six headings set in bold.
 ('page: headword in the case of the word', 'tools/html.py',
  'headword_case', 3),
 ('page: weight of the head returned', 'tools/html.py',
  'return t, end, alone', 1),
 ('page: proper names capitalised', 'tools/html.py',
  "PROPER_NAMES = {'Europa'", 1),
 ('page: section headings in bold', 'tools/html.py',
  'BOLD_HEADINGS', 2),
 ('publication: .nojekyll', '.nojekyll', None, 0),
]
SIZES = [('ornaments/portrait-3.png', 724, 1066),
           ('ornaments/vignette-3.png', 256, 251),
           ('ornaments/fleuron-232.png', 209, 25)]


def main():
    badly = []
    for free, f, ch, n in T:
        p = os.path.join(R, f)
        if not os.path.exists(p):
            badly.append('%-38s FILE MISSING (%s)' % (free, f)); continue
        if ch is None:
            continue
        v = open(p, encoding='utf-8', errors='replace').read().count(ch)
        if v < n:
            badly.append('%-38s %d found, %d expected' % (free, v, n))
    try:
        import cv2
        for f, w, h in SIZES:
            im = cv2.imread(os.path.join(R, f), cv2.IMREAD_UNCHANGED)
            if im is None:
                badly.append('%-38s MISSING' % f); continue
            if (im.shape[1], im.shape[0]) != (w, h):
                badly.append('%-38s %d x %d, expected %d x %d — plate NOT '
                           'SET UPRIGHT?' % (f, im.shape[1], im.shape[0], w, h))
    except ImportError:
        pass
    pdf = os.path.join(R, 'gramatiko.pdf')
    if os.path.exists(pdf):
        r = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True)
        m = re.search(r'Pages:\s+(\d+)', r.stdout)
        if m and m.group(1) != '236':
            badly.append('%-38s %s pages, 236 expected' % ('the volume',
                                                          m.group(1)))
    else:
        badly.append('%-38s MISSING' % 'gramatiko.pdf')
    print('%d witnesses checked' % (len(T) + len(SIZES) + 1))
    if badly:
        print('\n%d IN DEFAULT:' % len(badly))
        for x in badly:
            print('  ' + x)
        return 1
    print('no fix lost.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
