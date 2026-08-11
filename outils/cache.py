#!/usr/bin/env python3
"""Cache des analyses, partage par les controles 8, 9 et 10.

Ces trois controles refaisaient chacun le meme travail : rendre la page
composee en image a 300 dpi, et analyser le feuillet du fac-simile. Sur
dix pages cela coutait 27 secondes, dont l'essentiel en desinclinaison
du scan — une operation qui essaie cinquante et une rotations.

Deux caches, de natures differentes :

  * le FAC-SIMILE ne change jamais. Son analyse est donc ecrite sur
    disque une fois pour toutes (scan/cache/), et relue ensuite.
  * le COMPOSE change a chaque compilation. Il est rendu en une seule
    passe pour tout le document, et garde en memoire le temps du
    processus.
"""
import os, json, glob, subprocess, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(P, 'scan', 'cache')
os.makedirs(CACHE, exist_ok=True)

_compose = None


def feuillet(n):
    """Analyse du feuillet n du fac-simile : lignes, encre, colonne.
    Lue du disque si elle y est — le fac-simile ne bouge pas."""
    fp = os.path.join(CACHE, 'f%04d.json' % n)
    if os.path.exists(fp):
        with open(fp) as fh:
            return json.load(fh)
    norm, gm, ang = PG.prepared(n)
    gm2, span = PG.text_region(gm)
    fl = PG.lines_of(gm2)
    # Masque de secours : gm borne a la colonne de texte. text_region
    # efface parfois le folio (feuillet 42).
    _sec = gm.copy()
    if span:
        _sec[:, :max(0, span[0] - 12)] = 0
        _sec[:, min(_sec.shape[1], span[1] + 13):] = 0
    f0 = PG.folio_ligne(gm2, fl, _sec)
    if f0:
        fl.insert(0, f0)
    lignes = []
    for l in fl:
        lignes.append({'y0': l['y0'], 'y1': l['y1'], 'x0': l['x0'], 'x1': l['x1'],
                       'encre': int((gm2[l['y0']:l['y1']] > 0).sum())})
    d = {'feuillet': n, 'skew': round(ang, 3), 'H': int(gm2.shape[0]),
         'W': int(gm2.shape[1]), 'span': list(span) if span else None,
         'folio_detecte': bool(f0), 'lignes': lignes}
    with open(fp, 'w') as fh:
        json.dump(d, fh)
    return d


def _rendu_tout(pdf, npages):
    dst = os.path.join(P, 'controle', 'rendu')
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(os.path.join(dst, 'p-*.png')):
        os.remove(f)
    subprocess.run(['pdftoppm', '-r', '300', '-png', pdf,
                    os.path.join(dst, 'p')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst



# Une BANDE PEUT EN CACHER DEUX. La decoupe ci-dessus separe les lignes
# sur les rangees SANS encre. Il suffit qu'une jambage touche l'ascendante
# de la ligne suivante pour qu'aucune rangee ne soit vide et que les deux
# lignes n'en fassent qu'une. C'est arrive au folio 87 : les deux
# premieres lignes du corps se sont soudees, la bande a pris l'abscisse
# de la SECONDE (au fer a gauche), et le controle 10 a accuse d'un
# \VUcontinue de trop une page qui n'en avait pas besoin — pendant que le
# controle 11 y voyait 48 px de derive.
#
# Le fac-simile ne montre pas le defaut : son interlignage scanne plus
# large. C'est donc un artefact de MA page, pas du modele, et il se
# corrige ici plutot que dans chaque controle.
#
# On fend toute bande sensiblement plus haute que la mediane de la page,
# a la rangee la MOINS encree de sa partie centrale — la ou passe la
# frontiere entre deux lignes.
# MAIS UNE BANDE HAUTE N'EST PAS TOUJOURS DEUX LIGNES. Au folio 31, les
# accolades du tableau montent sur 27 pt : leurs bandes depassent la
# mediane sans rien cacher, et fendues elles rendaient un morceau d'accolade
# a +21 px de la marge, que le controle 10 a aussitot signale — a juste
# titre, puisque ce morceau ne commence ni au fer a gauche ni en alinea.
# On exige donc que CHAQUE MORCEAU PORTE L'ENCRE D'UNE VRAIE LIGNE. Un
# fragment d'accolade n'en porte qu'une fraction, et la bande reste
# entiere. Sinon on renonce a fendre : mieux vaut une bande soudee, que
# les controles savent signaler, qu'une bande inventee.
FEND_RAPPORT = 1.55      # au-dela de ce rapport a la mediane, on fend
FEND_ENCRE_MIN = 0.40    # part de l'encre mediane exigee de chaque morceau


def _fend_bandes(lignes, bw):
    """Separe les bandes qui contiennent visiblement deux lignes."""
    import numpy as np
    if len(lignes) < 5:
        return lignes
    med = float(np.median([l['y1'] - l['y0'] for l in lignes]))
    encre_med = float(np.median([l['encre'] for l in lignes]))
    if med <= 0:
        return lignes
    out = []
    for l in lignes:
        h = l['y1'] - l['y0']
        if h < FEND_RAPPORT * med:
            out.append(l)
            continue
        n = max(2, int(round(h / med)))
        bornes = [l['y0']]
        for k in range(1, n):
            cible = l['y0'] + int(round(k * h / n))
            lo = max(l['y0'] + 4, cible - int(0.3 * med))
            hi = min(l['y1'] - 4, cible + int(0.3 * med))
            if hi <= lo:
                bornes = None
                break
            prof = bw[lo:hi].sum(axis=1)
            bornes.append(lo + int(np.argmin(prof)))
        if bornes is None:
            out.append(l)
            continue
        bornes.append(l['y1'])
        morceaux = []
        for a, b in zip(bornes[:-1], bornes[1:]):
            if b - a < 8:
                morceaux = None
                break
            xs = np.where(bw[a:b].sum(axis=0) > 0)[0]
            if len(xs) < 20:
                morceaux = None
                break
            morceaux.append({'y0': int(a), 'y1': int(b), 'x0': int(xs[0]),
                             'x1': int(xs[-1]), 'encre': int(bw[a:b].sum())})
        if morceaux and min(m['encre'] for m in morceaux) >= FEND_ENCRE_MIN * encre_med:
            out.extend(morceaux)
        else:
            out.append(l)
    return out

def compose(pdf, npages):
    """Lignes de chaque page composee : (y0, y1, x0, x1, encre).
    Une seule passe de rendu pour tout le document."""
    global _compose
    if _compose is not None:
        return _compose
    dst = _rendu_tout(pdf, npages)
    out = {}
    for fp in sorted(glob.glob(os.path.join(dst, 'p-*.png'))):
        i = int(os.path.basename(fp).split('-')[1].split('.')[0])
        bw = (cv2.imread(fp, cv2.IMREAD_GRAYSCALE) < 160).astype(np.uint8)
        rows = bw.sum(axis=1)
        on = (rows > 4).astype(np.int8)
        d = np.diff(on)
        st = list(np.where(d == 1)[0] + 1)
        en = list(np.where(d == -1)[0] + 1)
        if on[0]: st.insert(0, 0)
        if on[-1]: en.append(len(on))
        brut = []
        for a, b in zip(st, en):
            if b - a < 8:
                continue
            xs = np.where(bw[a:b].sum(axis=0) > 0)[0]
            if len(xs) < 20:
                continue
            brut.append({'y0': int(a), 'y1': int(b), 'x0': int(xs[0]),
                         'x1': int(xs[-1]), 'encre': int(bw[a:b].sum())})
        if brut:
            plein = max(l['encre'] for l in brut)
            brut = [l for l in brut if l['encre'] >= 0.03 * plein]
        brut = _fend_bandes(brut, bw)
        out[i] = {'fichier': fp, 'lignes': brut}
    _compose = out
    return out


def vide_cache_compose():
    global _compose
    _compose = None


if __name__ == '__main__':
    import time
    if '--prechauffe' in sys.argv:
        # remplit le cache du fac-simile pour tous les feuillets
        lo = int(sys.argv[sys.argv.index('--prechauffe') + 1])
        hi = int(sys.argv[sys.argv.index('--prechauffe') + 2])
        t = time.time()
        for n in range(lo, hi + 1):
            feuillet(n)
            if n % 10 == 0:
                print('  %d  (%.0f s)' % (n, time.time() - t), flush=True)
        print('cache du fac-simile : feuillets %d a %d, %.0f s'
              % (lo, hi, time.time() - t))
