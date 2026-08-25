#!/usr/bin/env python3
"""Releve de structure : folios imprimes, titres, elements recurrents.

Base sur l'OCR grossier (scan/ocr/*.txt), qui suffit pour reperer
l'organisation du volume mais n'est jamais utilise pour le texte lui-meme.
"""
import os, re, json, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCR = os.path.join(P, 'scan', 'ocr')

FOLIO = re.compile(r'^[\s\-—–_=~.]*(\d{1,3})[\s\-—–_=~.]*$')


def folio_of(lines):
    """Cherche le folio dans les 3 premieres lignes non vides."""
    seen = 0
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        seen += 1
        if seen > 3:
            break
        m = FOLIO.match(s)
        if m:
            return int(m.group(1))
        # folio colle a un mot parasite
        m2 = re.match(r'^[\s\-—–]*(\d{1,3})[\s\-—–]+$', s)
        if m2:
            return int(m2.group(1))
    return None


def main():
    rows = []
    for n in range(1, 241):
        fp = os.path.join(OCR, 'f%04d.txt' % n)
        if not os.path.exists(fp):
            rows.append((n, None, 0, ''))
            continue
        txt = open(fp, encoding='utf-8', errors='replace').read()
        lines = txt.split('\n')
        nz = [l for l in lines if l.strip()]
        rows.append((n, folio_of(lines), len(nz),
                     ' / '.join(l.strip()[:60] for l in nz[:3])))
    for n, f, c, head in rows:
        print('%3d  folio=%-5s lignes=%-3d  %s' % (n, f, c, head))
    with open(os.path.join(P, 'tools', 'structure_brute.json'), 'w') as fh:
        json.dump([{'leaf': n, 'folio': f, 'nlines': c, 'head': h} for n, f, c, h in rows], fh, indent=1)


if __name__ == '__main__':
    main()
