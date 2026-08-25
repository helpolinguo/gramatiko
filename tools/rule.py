#!/usr/bin/env python3
"""Detection du FILET DE NOTE, et calcul de son ordonnee de composition.

Reperer le filet par « le plus grand blanc de la page » ne marche pas :
sur une page portant un titre de section, le blanc du titre est plus
grand, et l'on place alors le bloc de notes des centimetres trop haut.

Le filet est un objet reconnaissable en soi : un trait horizontal
continu, haut de un a trois pixels, long d'une vingtaine de millimetres,
cale sur la marge de gauche, et seul sur sa ligne. On le cherche donc
comme tel, dans la moitie basse de la page.

L'ordonnee rendue est celle qu'attend \\VUnotes, c'est-a-dire une distance
au bord SUPERIEUR DU PAPIER. Elle ne peut pas se lire directement sur le
scan : chaque image du scan a son propre decalage vertical, le papier n'y
occupant pas la meme place. On la calcule donc relativement a la premiere
ligne de corps, dont on sait qu'elle tombe a \\VUmargeSup :

    ordonnee = VUmargeSup + (y_filet - y_premiere_ligne) x 25,4/300
"""
import os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

VU_MARGE_SUP_MM = 24.30      # doit suivre \VUmargeSup du preambule


def trouve_filet(feuillet, verbose=False):
    """Retourne (y_filet, largeur_px) ou None."""
    norm, gm, ang = PG.prepared(feuillet)
    H, W = norm.shape
    sombre = (norm < 185).astype(np.uint8)
    # Un filet numerise est rarement continu : quelques pixels clairs le
    # coupent ici et la (au folio 11, la coupure suffisait a le faire
    # manquer). On soude donc les interruptions de trois pixels au plus.
    sombre = cv2.morphologyEx(sombre, cv2.MORPH_CLOSE,
                              np.ones((1, 7), np.uint8))
    # colonne de texte, pour savoir ou commence la marge de gauche
    gm2, span = PG.text_region(gm)
    if span is None:
        return None
    x0 = span[0]
    best = None
    # LA FENETRE DE RECHERCHE COMMENCAIT TROP BAS. Fixee a 0,45 H, elle
    # supposait que le bloc des notes occupe au plus la moitie inferieure
    # de la page. C'est vrai de presque toutes, mais pas du feuillet 97,
    # dont le filet tombe a 0,29 H (la page est aux trois quarts en
    # notes), ni du 93, a 0,40 H. Sur ces deux-la le detecteur rendait
    # « filet non trouve » — et tools/missing_lines.py, prive du
    # filet, melangeait le pas du corps a celui des notes.
    #
    # Elargir la FERMETURE de 7 a 11 px les trouvait aussi, mais rendait
    # de FAUX filets : y=1680 long 140 px au feuillet 93 la ou le vrai
    # est a 782 avec ses 213 px reglementaires. Une ligne de texte soudee
    # passait pour un filet. On a donc rejete ce remede — un detecteur
    # qui se trompe en silence vaut moins qu'un detecteur qui echoue.
    # LA FENETRE PARTAIT TROP BAS — troisieme cause de « filet non
    # trouve ». Fixee a 0,25 H, elle supposait que le bloc de notes
    # occupe au plus les trois quarts inferieurs. C'est faux des que la
    # page est peu remplie : au feuillet 180, qui clot la deuxieme
    # partie, le filet tombe a y = 377 pour une fenetre partant de 520 ;
    # au feuillet 194 il est a 450 pour une fenetre partant de 516. Dans
    # les deux cas le filet passe les tests de longueur et de reste — il
    # n'est jamais examine.
    # On descend donc a 0,10 H. Verifie sur vingt-deux feuillets temoins :
    # aucun filet deja trouve n'est perdu ni deplace.
    for y in range(int(0.10 * H), int(0.95 * H)):
        ligne = sombre[y]
        # On cherche le premier pixel sombre AU VOISINAGE de la marge, puis
        # la longueur du segment continu qui en part. Demarrer le comptage
        # a une abscisse fixe ne marchait pas : quelques pixels blancs
        # avant le filet suffisaient a donner une longueur nulle.
        fen = ligne[max(0, x0 - 15):x0 + 40]
        nz = np.nonzero(fen)[0]
        if nz.size == 0:
            continue
        depart = max(0, x0 - 15) + int(nz[0])
        n = 0
        while depart + n < W and ligne[depart + n]:
            n += 1
        # UN FILET DE NOTE MESURE ENTRE 201 ET 246 px, mesure sur les
        # vingt-six feuillets temoins : c'est une constante du volume,
        # non une grandeur libre. La fenetre valait 140 a 470 px, et
        # cette largeur a coute deux fausses lectures :
        #   -- au feuillet 199, un trait parasite de 154 px passait pour
        #      le filet et donnait 161,63 mm au lieu de 107,74 ; le bloc
        #      de notes, pose si bas, debordait la page en perdant une
        #      ligne ;
        #   -- au feuillet 231, page du TABELO sans aucune note, les
        #      EMPATTEMENTS SOUDES de la vedette demi-grasse
        #      « Konjuncioni : » formaient une plage continue de 185 px
        #      partant de la marge, et passaient les trois tests.
        # On resserre a 195-260 px. Verifie sur vingt-six feuillets
        # temoins : aucun filet reel n'est perdu (le plus court mesure
        # 201 px au feuillet 42, le plus long 246 au feuillet 34), et
        # les deux faux tombent.
        if not (195 <= n <= 260):
            continue
        # le reste de la COLONNE DE TEXTE doit etre vide (le bord de
        # l'image, lui, porte souvent la tranche du feuillet voisin)
        #
        # UN PIXEL DE TROP FAISAIT PERDRE LE FILET. Au feuillet 162 ce
        # test rendait reste = 7 pour le seuil 6 : deux pixels de salete
        # au milieu, et CINQ AU BORD DU PAPIER. text_region ne rogne pas
        # toujours ce bord — il rendait ici span[1] = 1405 quand la
        # colonne de texte s'arrete vers 1390 — si bien que la tranche du
        # feuillet voisin comptait comme de l'encre. On retire donc une
        # marge de securite a droite avant de sommer. Trois feuillets du
        # meme lot etaient declares « filet introuvable » pour ce motif.
        BORD = 25
        queue = ligne[depart + n + 30:max(depart + n + 30, span[1] - BORD)]
        reste = queue.sum()
        # CINQUIEME CAUSE DE « FILET INTROUVABLE » : une salete AU MILIEU
        # de la colonne. Au feuillet 213 le filet est parfait — 214 px,
        # cale sur la marge, franc a l'oeil — mais dix pixels de crasse a
        # x = 1073 portaient le reste a 10 pour un seuil de 6, et le
        # candidat tombait. La marge BORD, posee pour la tranche du
        # feuillet voisin, ne protege que du bord droit.
        #
        # Un total ne distingue pas dix pixels de salete d'une ligne de
        # texte : c'est la FORME qui les separe. Une ligne de texte donne
        # des suites longues et nombreuses ; une salete, une ou deux
        # suites courtes. On juge donc sur la plus longue suite continue,
        # et l'on gonfle le seuil du total en consequence. Verifie sur
        # vingt-six feuillets temoins : aucun filet deja trouve n'est
        # perdu ni deplace, et le 213 est retrouve.
        if reste:
            d = np.diff(np.concatenate(([0], (queue > 0).astype(np.int8), [0])))
            deb = np.nonzero(d == 1)[0]
            fin = np.nonzero(d == -1)[0]
            suite = int((fin - deb).max()) if deb.size else 0
        else:
            suite = 0
        # Ce qui separe une salete d'une ligne de texte n'est ni le
        # nombre de taches ni leur ecartement — deux poussieres aux deux
        # bouts de la colonne sont tres ecartees et ne pesent rien (c'est
        # le cas des feuillets 93 et 194, qu'un critere d'etendue a fait
        # perdre le temps d'un essai). C'est la QUANTITE d'encre, et la
        # TAILLE du plus gros amas. Au feuillet 213 la crasse fait dix
        # pixels d'un seul tenant ; la rangee de texte qui precede le
        # filet en porte cent cinquante-quatre, en suites bien plus
        # longues. Les deux seuils separent les deux cas largement.
        if suite > 12 or reste > 30:
            continue
        # ON RETIENT LE CANDIDAT LE PLUS PROCHE DE LA LONGUEUR
        # REGLEMENTAIRE, NON LE PLUS LONG. Le filet de note mesure
        # 210 a 216 px sur les vingt-six feuillets temoins — c'est une
        # constante du volume, non une grandeur libre. Retenir le plus
        # long faisait choisir, au feuillet 199, un faux filet de 154 px
        # situe 640 px plus bas que le vrai, long de 212 px : l'ordonnee
        # sortait a 161,63 mm au lieu de 107,74, et le bloc de notes,
        # pose si bas, debordait la page en perdant une ligne.
        # C'EST LA QUATRIEME PANNE DE CE DETECTEUR, ET LA PIRE : les
        # trois autres le font echouer, celle-ci le fait mentir.
        FILET_LONGUEUR = 213
        if best is None or abs(n - FILET_LONGUEUR) < abs(best[1] - FILET_LONGUEUR):
            best = (y, n)
    if verbose and best:
        print('  filet trouve a y=%d, long de %d px (%.1f mm)'
              % (best[0], best[1], best[1] * PG.PX2MM))
    return best


def ordonnee(feuillet, verbose=False):
    """Ordonnee de composition du filet, en mm depuis le bord du papier."""
    f = trouve_filet(feuillet, verbose)
    if f is None:
        return None
    norm, gm, ang = PG.prepared(feuillet)
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
    if not fl:
        return None
    premiere = fl[1]['y0'] if f0 else fl[0]['y0']
    # ATTENTION : le calcul suppose que la premiere ligne reperee est la
    # premiere ligne de CORPS, celle qui tombe a \VUmargeSup. Si la page
    # ouvre sur un titre de section (folio 11), cette ligne est plus basse,
    # et il faut ajouter le blanc qui la precede dans la composition.
    # On le signale plutot que de rendre un chiffre faux en silence.
    largeur_premiere = fl[1]['x1'] - fl[1]['x0'] if f0 else fl[0]['x1'] - fl[0]['x0']
    plein = max(l['x1'] - l['x0'] for l in fl)
    suspect = largeur_premiere < 0.45 * plein
    o = VU_MARGE_SUP_MM + (f[0] - premiere) * PG.PX2MM
    return (o, suspect)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        n = int(a)
        print('feuillet %d (folio %d) :' % (n, n - 4))
        r = ordonnee(n, verbose=True)
        if r is None:
            print('  filet non trouve')
        else:
            o, suspect = r
            print('  ordonnee de \\VUnotes : %.2f mm%s' % (
                o, '   *** la page ouvre sur un titre : ajouter le blanc '
                   'qui le precede ***' if suspect else ''))
