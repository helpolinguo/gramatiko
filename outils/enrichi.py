#!/usr/bin/env python3
"""Classifieur d'ENRICHISSEMENT : gras, italique ou romain, mot par mot.

C'est la piece qui manque au premier jet. L'OCR rend le texte ; il ne dit
rien de la casse typographique. Or sur ce livre la distinction porte la
moitie du sens — le gras marque la forme idiste citee en vedette,
l'italique ce qui est cite d'une autre langue — et c'est la que se sont
logees toutes les corrections signalees a la relecture.

Deux mesures, prises sur chaque mot du fac-simile :

  * la GRAISSE : epaisseur moyenne du trait, estimee par le rapport de
    l'encre au nombre de colonnes encrees. Un demi-gras a le trait plus
    epais qu'un romain de meme corps.
  * la PENTE : angle du cisaillement horizontal qui rend la projection
    verticale la plus contrastee. Un italique penche, un romain non.

Les deux sont normalisees par la MEDIANE DE LA LIGNE, ce qui absorbe les
variations d'encrage et de corps d'une page a l'autre.

Le classifieur ne vaut que par son taux d'erreur : on le mesure contre
les pages deja relevees a la main, ou l'on sait pour chaque mot s'il est
gras, italique ou romain.
"""
import os, sys, re, json
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG
import cache


def mots_de_ligne(norm, gm2, l, seuil_blanc=7):
    """Decoupe une ligne en mots : segments separes par un blanc large."""
    band = (gm2[l['y0']:l['y1'] + 1, l['x0']:l['x1'] + 1] > 0)
    if band.size == 0:
        return []
    col = band.sum(axis=0)
    vide = (col == 0).astype(np.int8)
    d = np.diff(vide)
    st = list(np.where(d == 1)[0] + 1)
    en = list(np.where(d == -1)[0] + 1)
    coupures = [(a, b) for a, b in zip(st, en) if b - a >= seuil_blanc]
    bornes, prev = [], 0
    for a, b in coupures:
        if a - prev > 3:
            bornes.append((prev, a))
        prev = b
    if band.shape[1] - prev > 3:
        bornes.append((prev, band.shape[1]))
    return [(l['x0'] + a, l['x0'] + b, band[:, a:b]) for a, b in bornes]


def graisse(m):
    """Epaisseur moyenne du trait : encre par colonne encree."""
    col = m.sum(axis=0)
    nz = col[col > 0]
    return float(nz.mean()) if nz.size else 0.0


def pente(m, angles=np.arange(-0.40, 0.41, 0.05)):
    """Cisaillement qui rend la projection verticale la plus contrastee.
    Un italique a une pente nettement positive, un romain une pente nulle."""
    h, w = m.shape
    if h < 6 or w < 6:
        return 0.0
    best, ba = -1.0, 0.0
    ys = np.arange(h) - h / 2.0
    for a in angles:
        dec = (ys * a).astype(int)
        acc = np.zeros(w + 2 * int(abs(dec).max() + 1))
        off = int(abs(dec).max() + 1)
        for y in range(h):
            r = m[y]
            if not r.any():
                continue
            acc[off + dec[y]:off + dec[y] + w] += r
        v = float(((acc[1:] - acc[:-1]) ** 2).sum())
        if v > best:
            best, ba = v, float(a)
    return ba


def analyse_page(feuillet):
    """Pour chaque mot : graisse et pente, normalisees par la ligne."""
    d = cache.feuillet(feuillet)
    norm, gm, ang = PG.prepared(feuillet)
    gm2, span = PG.text_region(gm)
    out = []
    for l in d['lignes']:
        mots = mots_de_ligne(norm, gm2, l)
        if len(mots) < 3:
            out.append([])
            continue
        g = [graisse(m) for _, _, m in mots]
        p = [pente(m) for _, _, m in mots]
        gm_ = float(np.median(g)) or 1.0
        pm_ = float(np.median(p))
        out.append([{'x0': a, 'x1': b,
                     'graisse': round(g[k] / gm_, 3),
                     'pente': round(p[k] - pm_, 3)}
                    for k, (a, b, _) in enumerate(mots)])
    return out


# ---------------------------------------------------------------- mesure
BAL = re.compile(r'\\(VUgras|textit|textsc)\s*\{')


def verite(brut):
    """Suite des (mot, classe) attendue, lue du releve LaTeX."""
    out, i, pile = [], 0, []
    while i < len(brut):
        m = BAL.match(brut, i)
        if m:
            pile.append('gras' if m.group(1) == 'VUgras' else 'ital')
            i = m.end()
            continue
        c = brut[i]
        if c == '}':
            if pile:
                pile.pop()
            i += 1
            continue
        if c == '{':
            i += 1
            continue
        if c == '\\':
            j = i + 1
            while j < len(brut) and brut[j].isalpha():
                j += 1
            i = max(j, i + 2)
            continue
        if c.isalpha():
            j = i
            while j < len(brut) and (brut[j].isalpha() or brut[j] in "'-"):
                j += 1
            out.append((brut[i:j], pile[-1] if pile else 'rom'))
            i = j
            continue
        i += 1
    return out


if __name__ == '__main__':
    import controles as C
    pages = C.lire_releve()
    seuils = {'gras': 1.10, 'ital': 0.06}
    conf = {}
    for pg in pages:
        f = pg.get('feuillet')
        if not f or int(f) < 15:
            continue
        mesures = analyse_page(int(f))
        att = []
        for l in pg['lignes']:
            if l['texte']:
                att.append(verite(l['brut']))
        n = min(len(att), len(mesures) - (1 if cache.feuillet(int(f))['folio_detecte'] else 0))
        dec = 1 if cache.feuillet(int(f))['folio_detecte'] else 0
        for k in range(n):
            a, b = att[k], mesures[k + dec]
            if len(a) != len(b):
                continue
            for (mot, cls), mes in zip(a, b):
                pred = ('gras' if mes['graisse'] > seuils['gras']
                        else 'ital' if mes['pente'] > seuils['ital'] else 'rom')
                conf[(cls, pred)] = conf.get((cls, pred), 0) + 1
    tot = sum(conf.values())
    just = sum(v for (a, b), v in conf.items() if a == b)
    print('Classifieur d\'enrichissement, mesure sur les pages relevees a la main')
    print('  mots compares : %d' % tot)
    if tot:
        print('  exactitude    : %.1f %%' % (100.0 * just / tot))
        print('\n  matrice (attendu -> predit) :')
        for a in ('rom', 'gras', 'ital'):
            ligne = '    %-5s' % a
            for b in ('rom', 'gras', 'ital'):
                ligne += ' %6d' % conf.get((a, b), 0)
            print(ligne + '     (colonnes : rom gras ital)')
