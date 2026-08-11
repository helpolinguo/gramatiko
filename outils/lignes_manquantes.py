#!/usr/bin/env python3
"""Depiste les lignes du fac-simile que le detecteur ne voit pas.

    A LANCER SUR TOUT UN LOT AVANT DE COMPOSER, jamais apres.

Six lignes ont echappe au detecteur en vingt-quatre pages : « homi. »
(f69), « kazo. » (f80), « yare. » (f84), « longa. » (f85), « pos til. »
(f86), « pro li. » (f91). Toutes courtes, toutes en fin d'alinea, toutes
trop pales pour franchir le seuil d'encre. Je les ai trouvees une a une,
a l'oeil, en relisant les bandes — methode qui marche et qui ne se
verifie pas.

Or elles se signalent seules, et par une mesure simple.

    UN PAS DOUBLE N'EST PAS UN BLANC.

Le pas courant du volume vaut 41,5 px. Un pas de 82,8 px la ou le pas
regulier vaut 41,5 n'est pas un blanc de 41,3 px : c'est UNE LIGNE
MANQUANTE suivie d'un pas ordinaire. Le critere est la proximite au
DOUBLE : |d - 2p| petit, et non |d - p| grand.

CE CRITERE SEUL NE SUFFIT PAS, et il a fallu le mesurer pour s'en
apercevoir. Passe sur les six cas connus, il n'en trouve que trois. Les
trois autres — « kazo. » (f80), « longa. » (f85) — portent un BLANC
apres la ligne manquante : leur pas vaut 105,9 px, ni p ni 2p, et le
test le laisse filer. Et « homi. » (f69) est dans les NOTES, dont le pas
vaut 34,6 px et non 41,5 : le double a chercher n'est pas le meme.

D'ou la forme retenue. Le pas regulier se mesure LOCALEMENT, de part et
d'autre du filet, et tout pas superieur a une fois et demie ce pas local
est signale avec SES DEUX LECTURES : « blanc de x px » et « ligne
manquante plus blanc de y px ». L'outil ne tranche pas — il ne peut pas,
les deux lectures etant parfois toutes deux plausibles — mais il ne
laisse plus rien passer en silence. C'est l'oeil qui tranche, au
fac-simile, et il sait desormais ou regarder.

Deux precautions, tirees des cas reels :

  * le pas qui franchit le FILET des notes vaut 60 a 155 px sans qu'il
    manque rien. On l'exclut en reperant le filet (outils/filet.py) ;
  * le pas qui descend du folio a la premiere ligne n'est pas un pas de
    corps ; il est exclu comme dans outils/cardage.py.

Ce qui reste est signale avec l'ordonnee ou chercher la ligne absente,
pour qu'on aille la lire au fac-simile.

UN PAS SE MESURE ENTRE DEUX LIGNES, DONC LA DERNIERE ECHAPPE AU TEST.
« pos til. » (f86) est la derniere ligne de sa page : rien ne la suit,
aucun pas ne la trahit. Elle se voit autrement — a l'ENCRE RESTANT SOUS
la derniere ligne detectee. Mesure sur les six feuillets du lot : 866 px
la ou elle manque, 4 a 65 px partout ailleurs (jambages et poussiere).
Le seuil est pose a 200 px, au large des deux cotes.

CE QU'IL VAUT, MESURE.

  * sur les six feuillets ou une ligne manque vraiment (69, 80, 84, 85,
    86, 91), il les trouve TOUS LES SIX ;
  * sur six feuillets sains deja composes et verifies (70 a 75), il
    signale sept pas — sept faux positifs.

Ce n'est donc pas un verdict, c'est un DEPISTAGE : il ramene la
recherche de « relire chaque ligne de chaque page » a « verifier un
endroit par page ». Le verdict « double net, aucun blanc » s'est
toujours revele juste ; les « deux lectures » sont a trancher a l'oeil.

    python3 outils/lignes_manquantes.py 86 87 88 89 90 91
    python3 outils/lignes_manquantes.py --tout        # les 240 feuillets
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lignesbase as LB
import filet as FI

PX2MM = 25.4 / 300.0


class Filet_introuvable(Exception):
    """Le filet des notes n'a pas ete trouve : le pas local est douteux."""
    def __str__(self):
        return ('filet des notes introuvable — le pas local melangerait '
                'corps et notes ; feuillet non depiste')
# Au-dela de ce rapport au pas local, le pas est signale. 1,5 laisse
# passer les blancs ordinaires (jusqu'a 1,4 p) et retient tout ce qui
# pourrait cacher une ligne.
RAPPORT_MIN = 1.5
# Marge autour du double exact : en deca, la lecture « ligne manquante
# sans blanc » est la seule plausible et on le dit.
TOLERANCE = 4.5
# UN BLANC NE PEUT PAS ETRE NEGATIF. Si d - 2p tombe nettement sous zero,
# la lecture « ligne manquante + blanc » exigerait un blanc negatif :
# elle est impossible, et le pas n'est qu'un blanc ordinaire. Sans ce
# garde-fou l'outil signalait vingt-deux pas pour six feuillets, dont
# dix-neuf avec un « blanc » de -13 a -18 px — du bruit pur.
BLANC_MIN = -3.0
# Encre toleree sous la derniere ligne detectee : jambages et poussiere.
ENCRE_QUEUE_MAX = 200
QUEUE_HAUTEUR = 70          # px scrutes sous la derniere ligne
# Une ligne de texte tient dans une seule bande de rangees. On exige que
# QUEUE_CONCENTRATION de l'encre de queue entre dans QUEUE_FENETRE
# rangees consecutives : 0,95 mesure sur la vraie ligne du feuillet 86,
# 0,63 sur les rousseurs du feuillet 105.
QUEUE_FENETRE = 30
QUEUE_CONCENTRATION = 0.85
# UNE BANDE PEUT EN CACHER DEUX, DU COTE DU FAC-SIMILE AUSSI. Le meme
# defaut que celui repare dans cache.compose (§ 8 teretvicies) : quand
# un jambage touche l'ascendante de la ligne suivante, aucune rangee
# n'est vide et les deux lignes n'en font qu'une. Au feuillet 97, la
# bande finale mesure 57 px pour une mediane de 27 — elle porte les deux
# dernieres lignes de la note (17). Ni le pas double ni l'encre de queue
# ne la voient : le pas la compte pour une, et rien ne la suit.
# On signale toute bande sensiblement plus haute que la mediane locale.
BANDE_RAPPORT = 1.7


def queue(feuillet):
    """Encre restant sous la derniere ligne detectee, en pixels sombres.

    L'ENCRE SEULE NE SUFFIT PAS : elle doit etre ORGANISEE EN LIGNE. Au
    feuillet 105, la marge inferieure est piquee de rousseurs — 907 px
    de points epars, au-dela du seuil de 200 — et le test annoncait une
    derniere ligne absente la ou il n'y a que de la poussiere.
    Le bon critere n'est pas la QUANTITE d'encre — 868 px la ou la ligne
    existe (f86), 907 la ou il n'y a que des rousseurs (f105) : les deux
    se valent. Ce n'est pas non plus le pic par rangee : les rousseurs
    en donnent 125 contre 56 a la vraie ligne, donc a l'envers.
    C'est la CONCENTRATION VERTICALE. Une ligne de texte tient dans une
    seule bande de rangees : 95 % de son encre entre dans 30 rangees
    consecutives. Les rousseurs, elles, couvrent toute la marge — 63 %
    seulement. Le seuil est pose a 0,85, au large des deux cotes.
    """
    import page as PG
    import numpy as np
    norm, gm, _ = PG.prepared(feuillet)
    gm2, span = PG.text_region(gm)
    fl = LB.analyse(feuillet, verbose=False)[0]
    if not fl or span is None:
        return 0
    yb = fl[-1]['y1']
    bande = (norm[yb + 6:yb + 6 + QUEUE_HAUTEUR, span[0]:span[1]] < 175)
    if not bande.size or not bande.sum():
        return 0
    rangees = bande.sum(axis=1)
    total = int(bande.sum())
    if len(rangees) <= QUEUE_FENETRE:
        return total
    dense = max(int(rangees[i:i + QUEUE_FENETRE].sum())
                for i in range(len(rangees) - QUEUE_FENETRE))
    if dense < QUEUE_CONCENTRATION * total:
        return 0
    return total


def bandes_soudees(feuillet):
    """[(rang, hauteur, hauteur mediane)] des bandes qui portent deux lignes."""
    fl = LB.analyse(feuillet, verbose=False)[0]
    if len(fl) < 8:
        return []
    h = [l['y1'] - l['y0'] for l in fl]
    med = float(np.median(h))
    if med <= 0:
        return []
    return [(k, h[k], med) for k in range(1, len(fl))
            if h[k] >= BANDE_RAPPORT * med]


def suspects(feuillet):
    """[(rang, pas, pas regulier, ordonnee ou chercher)]"""
    fl, bs, _ = LB.analyse(feuillet, verbose=False)
    if len(fl) < 6:
        return []
    folio = fl[0]['x1'] - fl[0]['x0'] < 0.25 * max(l['x1'] - l['x0'] for l in fl)
    pas = []
    for k in range(1, len(bs)):
        if bs[k] is None or bs[k - 1] is None:
            continue
        if folio and k == 1:
            continue
        pas.append((k, bs[k] - bs[k - 1]))
    f = FI.trouve_filet(feuillet)
    y_filet = f[0] if f else None
    # SANS LE FILET, LE PAS LOCAL N'EST PAS MESURABLE, et il faut le dire.
    # outils/filet.py echoue sur quelques feuillets (93, 97 entre autres).
    # Le pas local retombait alors sur la mediane de TOUTE la page, qui
    # sur une page chargee de notes vaut 33 px et non 41,5 : l'outil
    # lisait « pas local 33,1 » pour des lignes de corps et annoncait
    # trois lignes manquantes qui n'existaient pas. Une mesure fausse
    # rendue sans avertissement vaut moins que pas de mesure du tout.
    if y_filet is None:
        bloc = [d for _, d in pas if 30.0 < d < 48.0]
        if bloc and max(bloc) - min(bloc) > 5.0:
            raise Filet_introuvable(feuillet)

    def pas_local(k):
        """Pas regulier du BLOC ou tombe la ligne k : corps ou notes.

        Le bloc des notes est compose a 34,6 px, le corps a 41,5. Juger
        une ligne de note au pas du corps faisait manquer « homi. » du
        folio 65, dont le pas double vaut 69 px et non 83.
        """
        if y_filet is None:
            memes = [d for j, d in pas if 30.0 < d < 48.0]
        else:
            avant = bs[k - 1] < y_filet
            memes = [d for j, d in pas if 30.0 < d < 48.0
                     and (bs[j - 1] < y_filet) == avant]
        if len(memes) < 4:
            memes = [d for _, d in pas if 30.0 < d < 48.0]
        return float(np.median(memes)) if memes else None

    out = []
    for k, d in pas:
        # le pas qui franchit le filet des notes ne se juge pas : il vaut
        # 60 a 155 px sans qu'il manque quoi que ce soit.
        if y_filet is not None and bs[k - 1] < y_filet < bs[k]:
            continue
        p = pas_local(k)
        if p is None or d < RAPPORT_MIN * p:
            continue
        if d - 2 * p < BLANC_MIN:
            continue
        out.append((k, d, p, bs[k - 1] + p, abs(d - 2 * p) <= TOLERANCE))
    return out


def rapport(feuillets):
    total = 0
    douteux = 0
    for n in feuillets:
        try:
            s = suspects(n)
        except Filet_introuvable as e:
            print('feuillet %-4d folio %-4d : %s' % (n, n - 4, e))
            douteux += 1
            continue
        except Exception as e:
            print('feuillet %d : %s' % (n, e))
            continue
        for k, d, p, y, net in s:
            total += 1
            if net:
                print('feuillet %-4d folio %-4d ligne %2d : pas %.1f px pour un '
                      'pas local de %.1f — LIGNE MANQUANTE vers y = %.0f px '
                      '(double net, aucun blanc)' % (n, n - 4, k, d, p, y))
            else:
                print('feuillet %-4d folio %-4d ligne %2d : pas %.1f px pour un '
                      'pas local de %.1f\n        deux lectures : blanc de '
                      '%.1f px  OU  ligne manquante vers y = %.0f px + blanc '
                      'de %.1f px' % (n, n - 4, k, d, p, d - p, y, d - 2 * p))
        try:
            q = queue(n)
        except Exception:
            q = 0
        try:
            for k, h, med in bandes_soudees(n):
                total += 1
                print('feuillet %-4d folio %-4d ligne %2d : bande de %d px pour '
                      'une mediane de %.0f — DEUX LIGNES SOUDEES probables'
                      % (n, n - 4, k, h, med))
        except Exception:
            pass
        if q > ENCRE_QUEUE_MAX:
            total += 1
            print('feuillet %-4d folio %-4d : %d px d\'encre SOUS la derniere '
                  'ligne detectee — DERNIERE LIGNE MANQUANTE probable'
                  % (n, n - 4, q))
    print('\n%d ligne(s) manquante(s) probable(s) sur %d feuillet(s)%s.'
          % (total, len(feuillets),
             ', %d non depiste(s) faute de filet' % douteux if douteux else ''))
    if total:
        print('Les lire au fac-simile AVANT de composer : une ligne absente '
              'dans le corps decale toutes les frontieres suivantes, et\n'
              'outils/poser_cardage.py poserait chaque blanc une ligne trop '
              'haut sans rien signaler.')
    return total


if __name__ == '__main__':
    if '--tout' in sys.argv:
        rapport(range(5, 241))
    else:
        rapport([int(a) for a in sys.argv[1:] if not a.startswith('--')])
