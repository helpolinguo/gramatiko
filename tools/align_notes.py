#!/usr/bin/env python3
"""Cale l'ordonnee du bloc de notes sur celle du fac-simile.

L'ordonnee passee a \\VUnotes est d'abord estimee sur le FILET, releve par
tools/rule.py. Le filet est un trait pale de 0,4 pt : selon le seuil et
la fermeture employes, on tombe sur sa premiere rangee sombre ou sur son
milieu, et le bloc entier se decale de 1 a 3 mm. Mesure sur les pages
composees : l'ecart entre les notes et le corps allait de -26 a +33 px
d'une page a l'autre. Ce n'est donc pas une erreur de formule, mais le
bruit du releve du filet, page par page.

On le corrige sur ce qui se mesure bien : les LIGNES DE BASE des notes.
L'ecart moyen entre les notes composees et les notes du fac-simile,
l'ecart du corps une fois retire, se retranche de l'ordonnee.

    python3 tools/align_notes.py            # mesure, n'ecrit rien
    python3 tools/align_notes.py --pose     # ecrit
"""
import os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache
import checks as C

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX2MM = 25.4 / 300.0
# En deca de 4 px (0,34 mm) la correction est sous le bruit du decoupage
# en lignes : on ne touche pas.
SEUIL_PX = 4.0


def ecarts():
    """{folio: (ecart_px, fichier)} pour les pages a notes mesurables."""
    pages = C.lire_releve()
    comp = cache.compose(os.path.join(P, 'main.pdf'), len(pages))
    out = {}
    for i, pg in enumerate(pages, 1):
        fo = pg['folio']
        if not fo.isdigit() or i not in comp:
            continue
        feuillet = int(pg['feuillet']) if pg['feuillet'] else int(fo) + 4
        cl = comp[i]['lignes']
        fl = cache.feuillet(feuillet)['lignes']
        if not fl or len(cl) != len(fl):
            continue
        lg = [l for l in pg['lignes'] if l['texte']]
        dec = 1 if (fl[0]['x1'] - fl[0]['x0']
                    < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
        if len(lg) + dec != len(fl):
            continue
        note = np.array([False] * dec + [bool(l.get('note')) for l in lg])
        corps = ~note
        corps[:dec] = False
        if note.sum() < 3 or corps.sum() < 3:
            continue
        d = np.array([c['y0'] - a['y0'] for a, c in zip(fl, cl)], float)
        out[fo] = (float(d[note].mean() - d[corps].mean()), pg['fichier'])
    return out


def pose(ecrire=False):
    n = 0
    for folio, (e, fichier) in sorted(ecarts().items(), key=lambda t: int(t[0])):
        marque = '' if abs(e) < SEUIL_PX else '  <-- a caler'
        print('folio %-4s ecart notes/corps %+6.1f px = %+5.2f mm%s'
              % (folio, e, e * PX2MM, marque))
        if abs(e) < SEUIL_PX or not ecrire:
            continue
        fp = os.path.join(P, 'content', fichier)
        src = open(fp, encoding='utf-8').read()
        m = re.search(r'(\\begin\{VUpage\}(?:\[[^\]]*\])?\{%s\}.*?'
                      r'\\VUnotes\{)([0-9.]+)mm(\})' % re.escape(folio),
                      src, re.S)
        if not m:
            print('        (pas de \\VUnotes sur cette page)')
            continue
        neuf = float(m.group(2)) - e * PX2MM
        src = src[:m.start(2)] + ('%.2f' % neuf) + src[m.end(2):]
        open(fp, 'w', encoding='utf-8').write(src)
        print('        %s mm -> %.2f mm' % (m.group(2), neuf))
        n += 1
    if ecrire:
        print('%d page(s) calee(s) ; recompiler puis relancer pour converger.' % n)


if __name__ == '__main__':
    pose('--pose' in sys.argv)
