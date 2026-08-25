#!/usr/bin/env python3
"""TENTATIVE REFUTEE — depistage de la graisse par l'epaisseur des futs.

    CE PROGRAMME NE MARCHE PAS. Il est conserve pour que l'essai ne soit
    pas refait, et parce qu'un depistage rate se documente comme un
    depistage reussi.

Passe sur les 46 pages composees, il a signale 313 lignes, dont les
premieres au folio 12 — page verifiee trois fois et confirmee par le
lecteur. Ce ne sont pas 313 erreurs, c'est un faux positif systematique.

La cause est mesurable. L'epaisseur du fut ne prend, a 300 dpi, que deux
valeurs utiles : 3 ou 4 pixels. Les distributions par page le montrent —
mediane 3 a 4, neuvieme decile 4,0, et cela sur des pages dont l'une est
presque toute romaine et l'autre chargee de gras. En suréchantillonnant
la bande d'un facteur 4 avant de mesurer, on gagne un peu de finesse mais
pas assez : au folio 51, les mots gras rendent 4,00 et les romains 3,75,
un quart de pixel d'ecart.

Ce que l'outil sait faire malgre tout, et qui reste utile, est de
COMPARER DEUX AMAS VOISINS D'UNE MEME LIGNE : la meme encre, le meme
papier, le meme instant de numerisation. C'est ainsi qu'il a tranche la
graisse des verbes cites du folio 51. Voir tools/weight.py, qui garde
cet usage-la. Ce qu'il ne sait pas faire est de juger une ligne dans
l'absolu, ni de comparer deux pages entre elles.

Le depistage a l'echelle du volume reste donc a inventer. Le controle 9,
qui compare l'encre de MA ligne a celle du modele, est le bon principe —
la meme mesure des deux cotes — et sa faiblesse est ailleurs : son
appariement glisse des qu'une ligne courte manque au releve.

Description de l'essai :

Confronte la GRAISSE relevee a la graisse composee, page par page.

Trois erreurs de graisse signalees en six tours : il en reste
probablement. Plutot que d'attendre qu'on me les montre, on mesure.

Pour chaque ligne du fac-simile, on decoupe la bande en amas et on mesure
l'epaisseur du fut de chacun (tools/weight.py). On en tire la part des
amas gras. Du releve, on tire la part des CARACTERES enfermes dans un
\\VUgras. Les deux parts doivent concorder ; quand elles s'ecartent de
plus d'un tiers, la ligne est signalee.

Ce n'est pas un controle de plus : c'est un depistage, et il rend des
faux positifs. Deux causes connues :

  * une ligne qui franchit un pli du papier ou l'ombre de la reliure voit
    tous ses futs epaissis, et l'outil la declare grasse d'un bout a
    l'autre. Le signe est un verdict UNIFORME sur toute la ligne ;
  * les amas ne sont pas les mots : la virgule qui suit un mot gras
    s'agglomere a lui, un « : » isole donne un fut de 5 px.

On rend donc les deux parts et le detail, pour que l'oeil tranche.

    python3 tools/weight_sweep.py          # toutes les pages
    python3 tools/weight_sweep.py 51 54    # ces folios
"""
import os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG
import cache
import checks as C
import weight

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# En deca de cet ecart, la mesure et le releve concordent assez.
TOLERANCE = 0.34
# Une ligne de moins de six amas ne se juge pas : trop peu d'echantillons.
AMAS_MIN = 6


def part_grasse_relevee(brut):
    """Part des caracteres du texte enfermes dans un \\VUgras."""
    net = C.texte_nu(brut.replace('\x02', '').replace('\x03', '')
                     .replace('\x04', '')).strip()
    if not net:
        return None
    gras = 0
    i = 0
    while True:
        j = brut.find('\\VUgras', i)
        if j < 0:
            break
        k = brut.find('{', j)
        if k < 0:
            break
        prof = 0
        m = k
        while m < len(brut):
            if brut[m] == '{' and brut[m - 1] != '\\':
                prof += 1
            elif brut[m] == '}' and brut[m - 1] != '\\':
                prof -= 1
                if prof == 0:
                    break
            m += 1
        gras += len(C.texte_nu(brut[k + 1:m]).strip())
        i = m + 1
    return min(1.0, gras / max(len(net), 1))


def balaye(folios=None, rapport=True):
    pages = C.lire_releve()
    suspectes = []
    for pg in pages:
        fo = pg['folio'] or ('f' + (pg.get('feuillet') or '?'))
        if folios and fo not in folios:
            continue
        try:
            feuillet = int(pg['feuillet']) if pg['feuillet'] else int(pg['folio']) + 4
        except (ValueError, TypeError):
            continue
        fl = cache.feuillet(feuillet)['lignes']
        lg = [l for l in pg['lignes'] if l['texte']]
        dec = 1 if (fl and fl[0]['x1'] - fl[0]['x0']
                    < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
        if len(lg) + dec != len(fl):
            continue                       # comptes divergents : on passe
        for i, l in enumerate(lg):
            if l.get('note') or l.get('apparat') or l.get('rang'):
                continue                   # corps courant seulement
            f = fl[i + dec]
            amas = graisse.ligne(feuillet, f['y0'], f['y1'] + 1)
            if len(amas) < AMAS_MIN:
                continue
            mes = sum(1 for _, _, w, _ in amas if w >= graisse.SEUIL) / len(amas)
            rel = part_grasse_relevee(l['brut'])
            if rel is None:
                continue
            if abs(mes - rel) > TOLERANCE:
                suspectes.append((fo, i + 1, mes, rel, l['texte'][:52],
                                  all(w >= graisse.SEUIL for _, _, w, _ in amas)))
    if rapport:
        print('%d ligne(s) suspecte(s) :\n' % len(suspectes))
        for fo, k, mes, rel, t, uni in suspectes:
            print('  folio %-4s ligne %2d : mesure %3.0f %% gras, releve %3.0f %%%s'
                  % (fo, k, 100 * mes, 100 * rel,
                     '   [verdict UNIFORME : pli probable]' if uni else ''))
            print('        %s' % t)
    return suspectes


if __name__ == '__main__':
    balaye(set(sys.argv[1:]) or None)
