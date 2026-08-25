#!/usr/bin/env python3
"""Mesure du CARDAGE d'une page du fac-simile.

Le compositeur justifie ses pages verticalement. Mesure faite sur les
feuillets 20 a 39 : la derniere ligne de base tombe a 145,3 mm sous le
folio, a 0,3 mm pres, quel que soit le nombre de lignes de la page. Quand
la matiere ne remplit pas la justification, il repartit le surplus :

  -- des lames uniformes entre toutes les lignes du corps, ce qui fait
     passer le pas de 41,45 px (interlignage courant, 9,88 pt) a la
     valeur propre a la page ;
  -- des blancs plus larges aux articulations : fin d'alinea, ouverture
     d'une enumeration, reprise du discours apres des exemples.

Cet outil rend les deux : le pas regulier de la page, et la liste des
pas qui en depassent, avec l'exces a inscrire dans un \\VUblanc.

Il travaille sur les LIGNES DE BASE, jamais sur les hauts de ligne : le
haut depend des ascendantes de la ligne et bruite de +/- 8 px, de quoi
noyer un blanc d'un point et demi.

    python3 tools/carding.py 34
    python3 tools/carding.py 34 35 36
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baselines as LB

PX2PT = 72.27 / 300.0
# Pas courant du volume, mesure sur les feuillets 20, 24, 30, 32, 37, 38 :
# 41,3 a 41,6 px. C'est \VUinterligne = 9,88 pt.
PAS_COURANT = 41.45
# Un pas de note vaut 32,8 px : tout ce qui est en dessous de 38 px
# appartient au bloc des notes, qui n'est pas carde (il est cale a part
# par \VUnotes) et ne doit pas entrer dans la mediane du corps.
PAS_NOTE_MAX = 38.0


def mesure(feuillet):
    """(pas regulier du corps, liste des exces, lignes, bases)."""
    fl, bs, _ = LB.analyse(feuillet, verbose=False)
    pas = []
    for k in range(1, len(bs)):
        if bs[k] is None or bs[k - 1] is None:
            continue
        pas.append((k, bs[k] - bs[k - 1]))
    # Le pas qui descend du FOLIO a la premiere ligne du corps n'est pas
    # une articulation : il est fixe par la marge superieure, non par un
    # blanc d'alinea. Compte comme tel, il annoncait un exces de 48 px
    # « avant la ligne 1 », et le blanc pose en consequence ecartait la
    # page de son modele au lieu de l'en rapprocher (folio 13 : la derive
    # passait de 26 a 58 px).
    folio = bool(fl) and (fl[0]['x1'] - fl[0]['x0']
                          < 0.25 * max(l['x1'] - l['x0'] for l in fl))
    if folio:
        pas = [(k, d) for k, d in pas if k > 1]
    corps = [d for _, d in pas if PAS_NOTE_MAX < d < 48.0]
    if not corps:
        return None, [], fl, bs
    reg = float(np.median(corps))
    exces = []
    for k, d in pas:
        # On ne retient que les pas du corps : un pas qui suit une ligne
        # de note, ou qui franchit le filet, ne se carde pas.
        if d <= PAS_NOTE_MAX or d > 130.0:
            continue
        e = d - reg
        if e > 3.0:                      # 3 px = 0,7 pt : sous le bruit
            exces.append((k, d, e))
    return reg, exces, fl, bs


def rapport(feuillet):
    reg, exces, fl, bs = mesure(feuillet)
    if reg is None:
        print('feuillet %d : pas de corps mesurable' % feuillet)
        return
    print('=== feuillet %d : %d lignes' % (feuillet, len(fl)))
    print('    pas regulier du corps : %.2f px = %.2f pt%s'
          % (reg, reg * PX2PT,
             '' if abs(reg - PAS_COURANT) < 0.6 else '   <-- PAGE CARDEE'))
    if abs(reg - PAS_COURANT) >= 0.6:
        print('    -> \\VUinterlignePage{%.2fpt}' % (reg * PX2PT))
    if not exces:
        print('    aucun blanc d\'articulation')
        return
    print('    blancs d\'articulation (exces sur le pas regulier) :')
    for k, d, e in exces:
        larg = fl[k - 1]['x1'] - fl[k - 1]['x0']
        pleine = np.percentile([l['x1'] - l['x0'] for l in fl], 80)
        fin = 'fin d\'alinea' if larg < 0.97 * pleine else 'ligne pleine'
        print('      avant la ligne %2d : pas %.1f px, exces %.1f px '
              '= \\VUblanc{%.2fpt}   (%s au-dessus)'
              % (k, d, e, e * PX2PT, fin))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        rapport(int(a))
