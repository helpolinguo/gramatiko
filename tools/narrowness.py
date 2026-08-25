#!/usr/bin/env python3
"""ETROITESSE DES TITRES : le caractere compose est-il trop large ?

Le volume pose le corps sur la hauteur de capitale et l'interlettrage
sur la largeur de ligne. Cette regle donne toujours la bonne geometrie
d'ensemble -- mais elle est MUETTE sur le dessin des lettres. Quand le
caractere du fac-simile est plus etroit que XCharter, l'interlettrage
doit devenir negatif pour que la ligne rentre, et les lettres se
soudent : la ligne a la bonne largeur et devient illisible.

C'etait le cas de « KONSTATO. » (folio 4), compose en UN SEUL amas de
174 px pour 216 px et sept amas au fac-simile, et d'« Averto »
(folio 5). Ni l'un ni l'autre n'aurait ete vu par un controle de
largeur : leur largeur etait « juste ».

On mesure donc, des deux cotes, la LARGEUR DE LETTRE rapportee a la
hauteur de capitale, et le nombre d'amas -- deux lettres qui se touchent
n'en font qu'un. Le facteur a passer a \\VUetroit est le rapport des deux
rapports.

    python3 tools/narrowness.py            # tous les titres
    python3 tools/narrowness.py 8 9        # ces feuillets
"""
import os, sys, re
import numpy as np
import cv2

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(P, 'tools'))
import titles as T
import page as PG

SEUIL_FACTEUR = 0.93     # en deca, le caractere compose est trop large


def lettres(img, y0, y1, x0, x1, seuil, aire=20):
    """(nombre d'amas, largeur mediane, hauteur maximale). Un amas est un
    groupe de colonnes encrees : deux lettres soudees n'en font qu'un, et
    c'est precisement ce qu'on veut compter."""
    sub = (img[y0:y1 + 1, x0:x1 + 1] < seuil).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(sub, 8)
    L = sorted([s for s in st[1:] if s[4] >= aire], key=lambda s: s[0])
    if not L:
        return 0, 0, 0
    return len(L), float(np.median([s[2] for s in L])), int(max(s[3] for s in L))


def analyse(feuillet, cle):
    pdfpage = feuillet - 3 + 1
    comp, txt = T.lignes_composees(pdfpage)
    fac = T.lignes_facsimile(feuillet)
    yt = [y for y, t in txt if cle.upper() in t.upper()]
    if not yt:
        return None
    i = min(range(len(comp)), key=lambda k: abs(comp[k]['y0'] - yt[0]))
    d = T._decalage(comp, fac)
    cible = comp[i]['y0'] - d
    j = min(range(len(fac)), key=lambda k: abs(fac[k]['y0'] - cible))
    if abs(fac[j]['y0'] - cible) > 30:
        return 'titre non localise au fac-simile'
    ci, fj = comp[i], fac[j]
    nc, wc, hc = lettres(T.image_composee(pdfpage), ci['y0'], ci['y1'],
                         ci['x0'], ci['x1'], 170)
    norm, gm, ang = PG.prepared(feuillet)
    nf, wf, hf = lettres(norm, fj['y0'], fj['y1'], fj['x0'], fj['x1'], 175)
    if not (hc and hf and wc):
        return 'mesure impossible'
    return {'comp': (nc, wc, hc, ci['x1'] - ci['x0']),
            'fac': (nf, wf, hf, fj['x1'] - fj['x0']),
            'facteur': (wf / hf) / (wc / hc)}


if __name__ == '__main__':
    voulus = {int(a) for a in sys.argv[1:]}
    serres, sains, muets = [], 0, []
    for feu, txt, fich in T.titres_source():
        if voulus and feu not in voulus:
            continue
        cle = txt.split()[0] if txt.split() else ''
        cle = re.sub(r'[^A-Za-z]', '', cle)
        r = analyse(feu, cle) if cle else None
        nom = '%-24s folio %3d' % (txt[:24], feu - 4)
        if r is None or isinstance(r, str):
            muets.append((nom, r or 'titre introuvable'))
            continue
        nc, wc, hc, lc = r['comp']
        nf, wf, hf, lf = r['fac']
        f = r['facteur']
        # LE FACTEUR N'A DE SENS QUE SI LES LETTRES COMPOSEES SONT
        # SEPAREES. Des qu'elles se soudent, la « largeur de lettre »
        # mesuree est celle d'un amas de deux ou trois lettres, et le
        # facteur qu'on en tire est absurde : au folio 217 il sortait a
        # 0,208, au folio 11 a 0,380. Ces titres sont bien serres -- le
        # nombre d'amas le dit -- mais leur facteur doit se prendre
        # ailleurs, sur les titres du volume ou les lettres tiennent
        # encore leur rang.
        soude = nc < nf - 1
        if soude or f < SEUIL_FACTEUR:
            serres.append((nom, nc, nf, f, wc, hc, wf, hf, soude))
    mesurables = [x[3] for x in serres if not x[8]]
    for nom, nc, nf, f, wc, hc, wf, hf, soude in serres:
        if soude:
            print('  X  %s : %d amas composes pour %d releves — LETTRES '
                  'SOUDEES, facteur non mesurable ici' % (nom, nc, nf))
        else:
            print('  X  %s : %d amas pour %d ; lettre/capitale %.3f contre '
                  '%.3f  ->  \\VUetroit{%.3f}'
                  % (nom, nc, nf, wc / hc, wf / hf, f))
    if mesurables:
        print('\nfacteur mesurable sur %d titres : mediane %.3f, de %.3f a %.3f'
              % (len(mesurables), float(np.median(mesurables)),
                 min(mesurables), max(mesurables)))
    for nom, m in muets:
        print('  ?  %s : %s' % (nom, m))
    print('\n%d titres serres, %d non etablis' % (len(serres), len(muets)))
