#!/usr/bin/env python3
"""Generateur de PREMIER JET, et mesure de son taux d'erreur.

L'idee : produire le releve mecaniquement, pour que la relecture ait a
VERIFIER plutot qu'a SAISIR. Deux briques :

  * les coupures de ligne viennent des boites de lignes du fac-simile,
    donc sans OCR — c'est deja fiable, les controles le montrent ;
  * le TEXTE de chaque ligne vient d'un OCR ligne a ligne, chaque ligne
    etant decoupee et agrandie avant d'etre lue.

Avant de faire confiance a quoi que ce soit, on mesure. Les dix pages
deja relevees a la main servent de verite terrain : on compare le jet
automatique a ce relevé, ligne par ligne, et on rend le taux d'erreur
par caractere. Un premier jet dont on ignore le taux d'erreur ne vaut
pas mieux que pas de premier jet du tout.
"""
import os, sys, re, json, subprocess, unicodedata
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG
import cache
import controles as C

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(P, 'scan', 'jet')
os.makedirs(TMP, exist_ok=True)


def ocr_lignes(feuillet, marge=6, echelle=3):
    """OCR ligne a ligne : chaque boite est decoupee, agrandie, lue seule."""
    d = cache.feuillet(feuillet)
    norm, gm, ang = PG.prepared(feuillet)
    H, W = norm.shape
    out = []
    for k, l in enumerate(d['lignes']):
        y0 = max(0, l['y0'] - marge); y1 = min(H, l['y1'] + marge)
        x0 = max(0, l['x0'] - marge); x1 = min(W, l['x1'] + marge)
        sub = norm[y0:y1, x0:x1]
        if sub.size == 0:
            out.append('')
            continue
        sub = cv2.resize(sub, None, fx=echelle, fy=echelle,
                         interpolation=cv2.INTER_CUBIC)
        fp = os.path.join(TMP, 'l%04d_%03d.png' % (feuillet, k))
        cv2.imwrite(fp, sub)
        subprocess.run(['tesseract', fp, fp[:-4], '--psm', '7', '-l', 'eng'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t = ''
        if os.path.exists(fp[:-4] + '.txt'):
            t = open(fp[:-4] + '.txt', encoding='utf-8', errors='replace').read()
        out.append(' '.join(t.split()))
        os.remove(fp)
    return out


def _norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('’', "'").replace('«', '<<').replace('»', '>>')
    s = s.replace('—', '--').replace('---', '--')
    return re.sub(r'\s+', ' ', s).strip()


def distance(a, b):
    """Levenshtein, pour le taux d'erreur par caractere."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def mesure(pages_ref):
    """Compare le jet automatique au releve manuel, page par page."""
    total_d = total_n = 0
    for pg in pages_ref:
        f = pg.get('feuillet')
        if not f:
            continue
        f = int(f)
        att = [_norm(l['texte'] + ('-' if l['coupe'] == 'cc' else ''))
               for l in pg['lignes'] if l['texte']]
        got = [_norm(x) for x in ocr_lignes(f)]
        # Le folio est compose par \VUfolio : il n'appartient pas au releve.
        # Le reconnaitre au motif de son texte echouait des que l'OCR le
        # lisait mal — et la page entiere se comparait alors decalee d'un
        # rang, ce qui donnait 90 % d'erreur la ou l'OCR n'en faisait que
        # trois. On se fie donc a la DETECTION GEOMETRIQUE mise en cache.
        if cache.feuillet(f).get('folio_detecte'):
            got = got[1:]
        n = min(len(att), len(got))
        d = sum(distance(att[k], got[k]) for k in range(n))
        c = sum(len(att[k]) for k in range(n))
        d += sum(len(att[k]) for k in range(n, len(att)))
        c += sum(len(att[k]) for k in range(n, len(att)))
        total_d += d; total_n += c
        print('  folio %-3s : %2d lignes relevees, %2d lues — %5.1f %% d\'erreur'
              % (pg['folio'] or ('f%s' % f), len(att), len(got),
                 100.0 * d / max(c, 1)), flush=True)
    print('\n  TAUX D\'ERREUR GLOBAL : %.1f %% par caractere (%d sur %d)'
          % (100.0 * total_d / max(total_n, 1), total_d, total_n))
    return total_d / max(total_n, 1)


if __name__ == '__main__':
    pages = C.lire_releve()
    ref = [p for p in pages if p.get('feuillet') and int(p['feuillet']) >= 15]
    print('Mesure du premier jet automatique contre le releve manuel :\n')
    mesure(ref)
