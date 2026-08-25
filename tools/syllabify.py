#!/usr/bin/env python3
"""Ido syllabifier -- the line breaks the volume admits.

SPECIFICATION: the work itself, appendix "Puntizado", folio 220,
paragraph "Seko di la Vorti. [D. 485]":

    "On admisas kompleta libereso en la seko di la vorti de lineo a
      lineo, ecepte ke singla parto devas kontenar vokalo, e ke la
      digrami o diftongi devas ne dividesar. Ex. on darfas sekar tale
      la vorto mustar : mu-star, mus-tar, o must-ar. Ma neutro,
      mashino sekesas neu-tro, ma-shino, e ne ne-utro, mas-hino."

In other words, the break is free on TWO conditions only:
  1. each of the two parts contains at least one vowel;
  2. the break does not fall inside a digraph or a diphthong.

Digraphs (folio 13, "PRONUNCO DIL KONSONANTI E DIGRAMI"): ch, sh, qu.
  -- q is always followed by u (folio 14): qu is indivisible;
  -- gn is NOT a digraph: the book writes reg-no, dig-na (folio 13).
Diphthongs: au, eu (folio 17: "Evitez sorgoze facar ek au, eu du silabi
  en ta vorti").

This module serves chiefly as a CHECK: every break in the facsimile is
transcribed by hand; the syllabifier verifies that they conform. A
non-conforming break is either a typo of the original (to be kept and
reported) or an error of transcription (to be corrected).
"""
import re
import unicodedata

VOWELS = set('aeiou')
DIGRAPHS = ('ch', 'sh', 'qu')
DIPHTHONGS = ('au', 'eu')
UNBREAKABLE = DIGRAPHS + DIPHTHONGS


def _fold_in(word):
    """Lower case without accents, for the analysis (the book accents very little)."""
    s = unicodedata.normalize('NFD', word.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def unbreakable_positions(word):
    """Indices i such that a break between word[i-1] and word[i] is
    forbidden because it would split a digraph or a diphthong."""
    m = _fold_in(word)
    forbidden = set()
    for j in range(len(m) - 1):
        if m[j:j + 2] in UNBREAKABLE:
            forbidden.add(j + 1)
    return forbidden


def breaks(word):
    """Every break admitted. Returns the list of indices i: the line ends
    with word[:i] and resumes with word[i:]."""
    m = _fold_in(word)
    if not m.isalpha():
        return []
    forbidden = unbreakable_positions(word)
    out = []
    for i in range(1, len(m)):
        if i in forbidden:
            continue
        if not (set(m[:i]) & VOWELS):      # left part with no vowel
            continue
        if not (set(m[i:]) & VOWELS):      # right part with no vowel
            continue
        out.append(i)
    return out


def conforming(left, right):
    """Does the break left|right conform to D. 485? Returns (boolean,
    reason)."""
    g, d = _fold_in(left), _fold_in(right)
    if not g or not d:
        return False, 'partie vide'
    if not (set(g) & VOWELS):
        return False, 'the left part contains no vowel'
    if not (set(d) & VOWELS):
        return False, 'the right part contains no vowel'
    joiner = g[-1] + d[0]
    if joiner in UNBREAKABLE:
        what = 'digramme' if joiner in DIGRAPHS else 'diphtongue'
        return False, 'break inside the %s « %s »' % (what, joiner)
    return True, ''


def hyphenation_pattern(word):
    """The word with a hyphen at every admitted break, in the format
    \\hyphenation{...} expects."""
    cs = breaks(word)
    out, prev = [], 0
    for i in cs:
        out.append(word[prev:i])
        prev = i
    out.append(word[prev:])
    return '-'.join(out)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for m in sys.argv[1:]:
            print('%-16s %s' % (m, hyphenation_pattern(m)))
    else:
        # check on the examples the book itself gives
        attempts = [
            ('mustar', ['mu-star', 'mus-tar', 'must-ar']),
            ('neutro', ['neu-tro']),
            ('mashino', ['ma-shino']),
        ]
        for word, expected_all in attempts:
            got = ['%s-%s' % (word[:i], word[i:]) for i in breaks(word)]
            print('%-9s -> %s' % (word, ' '.join(got)))
            for a in expected_all:
                print('    %-12s %s' % (a, 'OK' if a in got else 'MANQUE'))
        for bad in ['ne-utro', 'mas-hino']:
            g, d = bad.split('-')
            ok, why = conforming(g, d)
            print('%-10s rejete ? %s  (%s)' % (bad, 'oui' if not ok else 'NON', why))
