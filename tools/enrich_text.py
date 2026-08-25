#!/usr/bin/env python3
"""Classifier of EMPHASIS by CONTENT, not by image.

The visual classifier (tools/enrich.py) failed: the facsimile's narrow
semi-bold has an ink/width ratio that overlaps the roman's.

But this book's emphasis is not decorative, it is SEMANTIC. The rule,
recorded in section 3.3 of the journal:

    bold    = the IDO form cited as a headword
    italic  = what is cited from ANOTHER LANGUAGE
    roman   = the running text, which is in Ido as well

The difficulty is therefore not bold against italic -- that is a question
of language, and the vocabulary settles it. It is bold against roman: both
are in Ido, and only the CONTEXT says whether the word is cited or used.

Three indications, all drawn from the text:

  1. a cited word follows a marker: "=", "Ex. :", "quale", "per", or an
     enumeration already begun;
  2. a word followed by the name of a language (Franca, Germana, Angla...)
     is cited from that language, hence italic;
  3. a word absent from the volume's Ido lexicon is foreign, hence italic.

The Ido lexicon builds itself: it is the words the transcription sets in
ROMAN, that is the running text. It grows with every page transcribed, and
the classifier with it.
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LANGUAGES = {'franca', 'germana', 'angla', 'italiana', 'hispana', 'latina',
           'rusa', 'portugalana', 'esperanto', 'espo', 'poloniana',
           'suediana', 'daniana', 'greka', 'araba'}
# words that introduce a citation
MARKERS = {'ex', 'exemple', 'quale', 'kom', 'per', 'yen', 'nome'}


def words(line):
    return re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]*", line)


class Classifier:
    def __init__(self, ido_lexicon, italic_lexicon):
        self.ido = ido_lexicon
        self.italic = italic_lexicon

    def cls_name(self, rest, k):
        """run: list of the line's words; k: index of the word."""
        m = rest[k].lower().strip("'-")
        next_one = rest[k + 1].lower() if k + 1 < len(rest) else ''
        prev = rest[k - 1].lower() if k > 0 else ''

        # 2. followed by a language name -> cited from that language
        if next_one in LANGUAGES:
            return 'ital'
        # 3. word attested as foreign in the volume
        if m in self.italic and m not in self.ido:
            return 'ital'
        # word unknown to the Ido lexicon and short: probably cited
        if m not in self.ido:
            if prev in LANGUAGES or prev in MARKERS:
                return 'ital'
            return 'ital' if len(m) > 2 else 'gras'
        # 1. isolated letter: it is nearly always a headword
        if len(m) == 1:
            return 'ital' if prev in LANGUAGES or next_one in LANGUAGES else 'gras'
        return 'rom'


def build_lexicons(pages, except_for=None):
    """Lexicons drawn from the transcription: roman -> Ido; italic -> foreign."""
    ido, italic = set(), set()
    for pg in pages:
        if except_for is not None and pg.get('leaf') == except_for:
            continue
        for l in pg['lines']:
            for word, cls in extract(l['brut']):
                m = word.lower().strip("'-")
                if cls == 'rom':
                    ido.add(m)
                elif cls == 'ital':
                    italic.add(m)
    return ido, italic


SWEEP = re.compile(r'\\(VUgras|textit|textsc)\s*\{')


def extract(raw):
    """Expected (word, class), read from the LaTeX transcription."""
    out, i, stack = [], 0, []
    while i < len(raw):
        m = SWEEP.match(raw, i)
        if m:
            stack.append('gras' if m.group(1) == 'VUgras' else 'ital')
            i = m.end(); continue
        c = raw[i]
        if c == '}':
            if stack: stack.pop()
            i += 1; continue
        if c == '{':
            i += 1; continue
        if c == '\\':
            j = i + 1
            while j < len(raw) and raw[j].isalpha():
                j += 1
            i = max(j, i + 2); continue
        if c.isalpha() or c in 'ÀÁÂÄÈÉÊËÌÍÎÏÒÓÔÖÙÚÛÜàáâäèéêëìíîïòóôöùúûü':
            j = i
            while j < len(raw) and (raw[j].isalpha() or raw[j] in "'-"
                                     or raw[j] in 'àáâäèéêëìíîïòóôöùúûü'):
                j += 1
            out.append((raw[i:j], stack[-1] if stack else 'rom'))
            i = j; continue
        i += 1
    return out


if __name__ == '__main__':
    import checks as C
    pages = [p for p in C.read_transcription() if p.get('leaf')
             and int(p['leaf']) >= 15]
    conf = {}
    # cross-validation: each page is classified with a lexicon built
    # WITHOUT it, so as not to measure ourselves on what we have learnt.
    for pg in pages:
        ido, italic = build_lexicons(pages, except_for=pg['leaf'])
        cl = Classifier(ido, italic)
        for l in pg['lines']:
            waiting = extract(l['brut'])
            if not waiting:
                continue
            rest = [m for m, _ in waiting]
            for k, (word, true_val) in enumerate(waiting):
                pred = cl.cls_name(rest, k)
                conf[(true_val, pred)] = conf.get((true_val, pred), 0) + 1
    total = sum(conf.values())
    just = sum(v for (a, b), v in conf.items() if a == b)
    roman_total = sum(v for (a, _), v in conf.items() if a == 'rom')
    print('Classifier by CONTENT (cross-validation page by page)')
    print('  words compared: %d' % total)
    print('  exactitude    : %.1f %%' % (100.0 * just / max(total, 1)))
    print('  reference « tout romain » : %.1f %%' % (100.0 * roman_total / max(total, 1)))
    print('\n  matrix (expected -> predicted rom / bold / ital):')
    for a in ('rom', 'gras', 'ital'):
        n = sum(v for (x, _), v in conf.items() if x == a)
        r = conf.get((a, a), 0)
        print('    %-5s %6d %6d %6d     rappel %5.1f %%' % (
            a, conf.get((a, 'rom'), 0), conf.get((a, 'gras'), 0),
            conf.get((a, 'ital'), 0), 100.0 * r / max(n, 1)))
