#!/usr/bin/env python3
"""Controle des BLANCS QUI ENTOURENT LES TITRES, par appariement a
l'ORDONNEE et non au rang.

Le premier balayage appariait la ligne composee a la ligne du fac-simile
par leur RANG dans la page. C'est faux des que les deux comptages
different d'une unite -- une ligne courte perdue par le detecteur, deux
lignes serrees soudees par pdftotext -- et il suffit d'un ecart pour que
tout ce qui suit soit apparie de travers. Sur les 51 titres du volume,
ce balayage en donnait 23 hors tolerance, dont des ecarts de 110 a 228
px qui n'etaient que de faux appariements.

On apparie donc par la POSITION. Les deux pages ne sont pas dans le meme
repere : le scan a son propre decalage vertical, page par page. Mais ce
decalage est une CONSTANTE par page, et il se trouve sans rien supposer
du comptage : on essaie tous les decalages plausibles et l'on garde
celui qui apparie le plus de lignes a moins de huit pixels. C'est un
vote, non une hypothese.

Un titre n'est ensuite mesure que si SES DEUX VOISINS sont apparies eux
aussi, et apparies dans l'ordre : faute de quoi le blanc compare ne
serait pas le meme blanc. Ce qui ne peut pas etre etabli est dit tel
quel plutot que compte comme bon.

    python3 outils/titres.py            # tous les titres
    python3 outils/titres.py 173 176    # ces feuillets seulement
"""
import os, re, sys, subprocess
import numpy as np

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(P, 'outils'))
import page as PG

PX2MM = 25.4 / 300.0
TOL_APPARIEMENT = 10     # px : deux lignes appariees
TOL_BLANC = 14           # px = 1,2 mm : au-dela, le blanc est faux
PREMIER_FEUILLET = 3     # le volume commence a la couverture imprimee


def titres_source():
    """[(feuillet, texte)] dans l'ordre du volume."""
    out = []
    for f in ('contenu/00-liminaires.tex', 'contenu/10-parto1.tex',
              'contenu/20-parto2.tex'):
        feu = None
        for l in open(os.path.join(P, f), encoding='utf-8'):
            m = re.search(r'\\begin\{VUpage\}\[(\d+)\]', l)
            if m:
                feu = int(m.group(1))
            m = re.search(r'\\VUtitre\{[^}]*\}\{[^}]*\}\{(.*)$', l)
            if m:
                t = m.group(1)
                # \VUetroit{facteur}{texte} : le facteur n'est pas du texte
                t = re.sub(r'\\VUetroit\{[\d.]+\}', ' ', t)
                t = re.sub(r'\\[A-Za-z]+(\[[^\]]*\])?', ' ', t)
                t = re.sub(r'[{}\\]', ' ', t)
                out.append((feu, ' '.join(t.split()), f))
    return out


def bandes(img, seuil, minink=4, fus=3, hmin=6):
    """Rangees d'encre d'une image : le MEME algorithme des deux cotes.

    C'est ce point qui a fait echouer le premier essai d'appariement par
    ordonnee. On y prenait, du cote compose, le yMin de pdftotext -- le
    haut de la BOITE DE FONTE, constant d'une ligne a l'autre -- et, du
    cote fac-simile, le haut de l'ENCRE, qui monte ou descend de dix
    pixels selon que la ligne porte ou non des ascendantes. Les deux
    grandeurs ne sont pas commensurables, et aucun decalage constant ne
    pouvait les apparier : le vote rendait n'importe quoi.
    On appelle donc PG.lines_of DES DEUX COTES : le meme decoupage en
    lignes sur la page composee, rendue a 300 dpi et seuillee, et sur le
    fac-simile. Les deux y0 sont alors la meme grandeur.
    """
    ink = (img < seuil).sum(axis=1)
    out, d = [], None
    for y, v in enumerate(ink):
        if v >= minink and d is None:
            d = y
        elif v < minink and d is not None:
            out.append((d, y - 1))
            d = None
    if d is not None:
        out.append((d, img.shape[0] - 1))
    mg = []
    for b in out:
        if mg and b[0] - mg[-1][1] <= fus:
            mg[-1] = (mg[-1][0], b[1])
        else:
            mg.append(b)
    return [{'y0': a, 'y1': b} for a, b in mg if b - a >= hmin]


def image_composee(pdfpage):
    import cv2, glob, tempfile
    d = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-r', '300', '-f', str(pdfpage), '-l',
                    str(pdfpage), '-gray', '-png',
                    os.path.join(P, 'main.pdf'), os.path.join(d, 'p')],
                   check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    g = cv2.imread(glob.glob(os.path.join(d, 'p*.png'))[0], 0)
    for x in glob.glob(os.path.join(d, 'p*.png')):
        os.remove(x)
    os.rmdir(d)
    return g


def lignes_composees(pdfpage):
    """(bandes d'encre, texte par ligne). Le texte sert a RECONNAITRE le
    titre ; les ordonnees, a l'apparier. Les deux listes n'ont pas
    forcement la meme longueur -- pdftotext separe des lignes que le
    profil d'encre soude -- et on ne s'en sert que pour situer le titre
    dans la page, jamais pour compter."""
    x = os.path.join(P, 'outils', '.tmp', 'titres.xml')
    os.makedirs(os.path.dirname(x), exist_ok=True)
    subprocess.run(['pdftotext', '-f', str(pdfpage), '-l', str(pdfpage),
                    '-bbox-layout', os.path.join(P, 'main.pdf'), x],
                   check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    s = open(x, encoding='utf-8').read()
    txt = []
    for a, b in re.findall(
            r'<line xMin="[\d.]+" yMin="([\d.]+)"[^>]*>(.*?)</line>', s, re.S):
        txt.append((float(a) * 300 / 72.0, ' '.join(re.sub(r'<[^>]+>', ' ', b).split())))
    import numpy as np
    img = image_composee(pdfpage)
    gm = ((img < 170) * 255).astype(np.uint8)
    return PG.lines_of(gm), txt


def lignes_facsimile(feuillet):
    """Bandes d'encre du fac-simile, dans la colonne de texte, FOLIO
    COMPRIS : la page composee le porte, et l'oublier decalerait tout
    l'appariement d'un rang."""
    norm, gm, ang = PG.prepared(feuillet)
    gm2, span = PG.text_region(gm)
    fl = PG.lines_of(gm2)
    sec = gm.copy()
    if span:
        sec[:, :max(0, span[0] - 12)] = 0
        sec[:, min(sec.shape[1], span[1] + 13):] = 0
    f0 = PG.folio_ligne(gm2, fl, sec)
    if f0:
        fl = [f0] + fl
    return fl


def _decalage(comp, fac):
    """Le decalage vertical de la page composee sur le fac-simile, par
    VOTE : on essaie tous les decalages plausibles et l'on garde celui
    qui apparie le plus de lignes. Aucune hypothese sur le comptage."""
    cand = sorted({round(c['y0'] - f['y0']) for c in comp for f in fac})
    best, bestn = 0, -1
    for d in cand:
        n = sum(1 for c in comp
                if min(abs(c['y0'] - (f['y0'] + d)) for f in fac)
                <= TOL_APPARIEMENT)
        if n > bestn:
            best, bestn = d, n
    return best


def apparie(comp, fac):
    """(decalage, {i composee -> j fac-simile}) par ALIGNEMENT MONOTONE.

    L'appariement etait d'abord glouton : on parcourait les lignes
    composees dans l'ordre et l'on prenait pour chacune la ligne du
    fac-simile la plus proche encore libre. Cela suffit tant que les
    deux pages se suivent, mais une ligne appariee tot AFFAME sa
    voisine : au folio 169 le titre etait bien apparie et ses deux
    voisins declares « non apparies » pour cette seule raison, ce qui
    rendait le controle muet la ou il devait parler.

    On resout donc l'alignement en entier, par programmation dynamique
    (Needleman et Wunsch), avec deux proprietes que le glouton n'a pas :
    l'ORDRE est impose -- deux lignes ne peuvent pas se croiser -- et le
    choix est GLOBAL, chaque paire etant retenue pour ce qu'elle vaut
    dans le meilleur alignement, non pour son rang.

    Une paire rapporte TOL_APPARIEMENT - ecart, donc d'autant plus
    qu'elle est franche ; un saut coute GAP. Le saut est bon marche a
    dessein : une ligne manquante d'un cote est un accident ordinaire du
    decoupage, et il vaut mieux la sauter que forcer une fausse paire.
    """
    if not comp or not fac:
        return 0, {}
    d = _decalage(comp, fac)
    n, m = len(comp), len(fac)
    GAP = -1.0
    S = np.full((n + 1, m + 1), -np.inf)
    S[0, :] = np.arange(m + 1) * GAP
    S[:, 0] = np.arange(n + 1) * GAP
    ori = np.zeros((n + 1, m + 1), np.int8)     # 1 paire, 2 saut i, 3 saut j
    ori[0, 1:] = 3
    ori[1:, 0] = 2
    for i in range(1, n + 1):
        ci = comp[i - 1]['y0']
        for j in range(1, m + 1):
            e = abs(ci - (fac[j - 1]['y0'] + d))
            best, k = S[i - 1, j] + GAP, 2
            if S[i, j - 1] + GAP > best:
                best, k = S[i, j - 1] + GAP, 3
            if e <= TOL_APPARIEMENT:
                v = S[i - 1, j - 1] + (TOL_APPARIEMENT - e)
                if v > best:
                    best, k = v, 1
            S[i, j], ori[i, j] = best, k
    paires = {}
    i, j = n, m
    while i > 0 or j > 0:
        k = ori[i, j]
        if k == 1:
            paires[i - 1] = j - 1
            i -= 1
            j -= 1
        elif k == 2:
            i -= 1
        else:
            j -= 1
    return d, paires


def controle(feuillet, texte):
    pdfpage = feuillet - PREMIER_FEUILLET + 1
    comp, txt = lignes_composees(pdfpage)
    fac = lignes_facsimile(feuillet)
    cle = re.sub(r'[^A-Za-z]', '', texte.split()[0]).upper() if texte.split() else ''
    yt = [y for y, t in txt
          if cle and cle in re.sub(r'[^A-Za-z]', '', t).upper()]
    if not yt:
        return ('titre introuvable dans la page composee', None, None)
    # la bande d'encre qui porte le titre : celle dont le haut est le
    # plus proche du yMin de pdftotext, a une demi-interligne pres
    i = min(range(len(comp)), key=lambda k: abs(comp[k]['y0'] - yt[0]))
    if abs(comp[i]['y0'] - yt[0]) > 25:
        return ('titre non retrouve dans le profil d\'encre', None, None)
    d, paires = apparie(comp, fac)
    if i not in paires:
        return ('titre non apparie au fac-simile', None, None)
    j = paires[i]
    res = {}
    for cote, di in (('avant', -1), ('apres', +1)):
        ii, jj = i + di, j + di
        if not (0 <= ii < len(comp) and 0 <= jj < len(fac)):
            res[cote] = None                    # bord de page : rien a mesurer
        elif paires.get(ii) != jj:
            res[cote] = 'voisin non apparie'
        else:
            cb = abs(comp[i]['y0'] - comp[ii]['y0'])
            fb = abs(fac[j]['y0'] - fac[jj]['y0'])
            res[cote] = (fb, cb, cb - fb)
    return (None, res, d)


if __name__ == '__main__':
    voulus = {int(a) for a in sys.argv[1:]}
    T = titres_source()
    mauvais = incertains = bons = 0
    for feu, txt, fich in T:
        if voulus and feu not in voulus:
            continue
        err, res, d = controle(feu, txt)
        nom = '%-26s folio %3s' % (txt[:26], feu - 4)
        if err:
            incertains += 1
            print('  ?  %s : %s' % (nom, err))
            continue
        pb = []
        inc = False
        for cote in ('avant', 'apres'):
            r = res[cote]
            if r is None:
                continue
            if isinstance(r, str):
                inc = True
                pb.append('%s : %s' % (cote, r))
            elif abs(r[2]) > TOL_BLANC:
                pb.append('%s : fac %d, compose %d, %+d px = %+.2f mm'
                          % (cote, r[0], r[1], r[2], r[2] * PX2MM))
        if pb and not inc:
            mauvais += 1
            print('  X  %s : %s' % (nom, ' ; '.join(pb)))
        elif inc:
            incertains += 1
            print('  ?  %s : %s' % (nom, ' ; '.join(pb)))
        else:
            bons += 1
    print('\n%d titres : %d justes, %d faux, %d non etablis'
          % (bons + mauvais + incertains, bons, mauvais, incertains))
