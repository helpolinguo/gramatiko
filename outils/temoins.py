#!/usr/bin/env python3
"""LISTE DE TEMOINS : une chaine caracteristique par correctif.

Cinq pertes de conteneur ont montre que « git log » ne prouve rien : la
derniere fois l'historique etait coherent et les FICHIERS ne l'etaient
pas. Ce qui detecte la panne, c'est de chercher, pour chaque correctif,
une chaine qui ne peut se trouver que s'il est en place.

    python3 outils/temoins.py     # sort 1 si un temoin manque
"""
import os, re, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = [
 # (libelle, fichier, chaine attendue, nombre minimal)
 ('folio 82 : Ultre seul en gras', 'contenu/10-parto1.tex',
  '\\VUgras{Ultre} esas', 1),
 ('renvois cliquables du Tabelo', 'preambule.tex', '\\VUlienOuvre', 3),
 ('ecart avant un numero large', 'preambule.tex',
  '\\newcommand{\\VUindexEcart}', 1),
 ('PDF nomme gramatiko', 'komp.mk', 'jobname=gramatiko', 1),
 ('titre du folio 3 comprime', 'contenu/00-liminaires.tex',
  '\\VUetroit{0.702}', 1),
 ('KONSTATO comprime', 'contenu/00-liminaires.tex',
  '\\VUetroit{0.793}', 1),
 ('Averto comprime', 'contenu/00-liminaires.tex',
  '\\VUetroit{0.822}', 1),
 ('titre de couverture comprime', 'contenu/00-liminaires.tex',
  '\\VUetroit{0.668}', 1),
 ('PUNTIZADO elargi', 'contenu/20-parto2.tex', '\\VUetroit{0.857}', 1),
 ('blanc du folio 21', 'contenu/10-parto1.tex', '\\VUsaut{6.47mm}', 1),
 ('blanc du folio 122', 'contenu/20-parto2.tex', '\\VUsaut{6.93mm}', 1),
 ('blanc du folio 169', 'contenu/20-parto2.tex', '\\VUsaut{6.90mm}', 1),
 ('blanc du folio 195', 'contenu/20-parto2.tex', '\\VUsaut{11.17mm}', 1),
 ('marque cachee', 'preambule.tex', '\\VUmarqueCachee', 2),
 ('planche a ordonnee absolue', 'preambule.tex', '\\VUplancheA', 2),
 ('portrait redresse (largeur)', 'preambule.tex',
  '\\VUplancheLargeur}{61.30mm}', 1),
 ('portrait redresse (ordonnee)', 'contenu/00-liminaires.tex',
  '\\VUplancheA{55.88mm}', 1),
 ('vignette redressee', 'contenu/00-liminaires.tex',
  '\\VUimageA{104.72mm}{22.38mm}', 1),
 ('signets : groupe APENDICI', 'contenu/90-signeti.tex',
  'count -10 {APENDICI}', 1),
 ('signets : Tabelo page 227', 'contenu/90-signeti.tex',
  'goto page 227 {/Fit} count 0 {TABELO', 1),
 ('page : Introdukto', 'outils/html.py', 'Introdukto', 1),
 ('page : hauteur d en-tete mesuree', 'outils/html.py', 'margoObs', 4),
 ('page : chefa vorti', 'outils/html.py', 'Chefa vorti', 1),
 ('page : en la tota libro', 'outils/html.py', 'tota libro', 1),
 ('page : anciennes ancres rattrapees', 'outils/html.py',
  'function trovAncro', 1),
 ('page : notes recollees comptees', 'outils/html.py', 'n_recol', 2),
 ('page : asterisme a son blanc', 'outils/html.py', 'self.aster', 3),
 ('page : bouts des accolades', 'outils/html.py', 'M8.6 1C5.8', 1),
 ('page : avis sur les deux prepozicioni', 'outils/html.py',
  'ridonas li a la loko', 1),
 # Folio 31 : l'accolade FERMANTE. Faute d'etre lue, elle ne rattachait
 # que « maxim » a « de o ek », et le nom retombait un demi-interligne
 # trop haut. Trois temoins : la lecture de la fermante, sa fusion dans
 # le groupe qu'elle couvre, et le decalage de mi-hauteur en colonnes.
 ('folio 31 : accolade fermante lue', 'outils/html.py',
  'def fermantes', 1),
 ('folio 31 : fermante fondue au groupe', 'outils/html.py',
  "ferme_brace", 3),
 ('folio 31 : case a mi-hauteur en colonnes', 'outils/html.py',
  'mezo', 3),
 ('folio 31 : membre insecable', 'outils/html.py',
  '.gr-m{white-space:nowrap}', 1),
 ('folio 31 : bord gauche d\'un groupe', 'outils/html.py',
  'def bord', 1),
 # Folio 220 : les deux schemas sont centres sur la justification. La
 # marque se pose d'apres le scan (marges gauche et droite egales), non
 # d'apres l'oeil ; trois temoins, un par piece.
 ('folio 220 : marque de centrage', 'preambule.tex',
  '\\newcommand{\\VUtabloCentrita}', 1),
 ('folio 220 : les deux schemas marques', 'contenu/20-parto2.tex',
  '\\VUtabloCentrita', 2),
 ('folio 220 : centrage rendu', 'outils/html.py',
  '.centrita{display:flex', 1),
 # L'ASTERISQUE NUE est une marque de note (feuillets 74 et 122), et
 # l'appel se cherche sous la forme meme que le fac-simile emploie --
 # « (*) » aux feuillets 166, 191, 208, l'asterisque nue aux deux
 # autres. Les confondre casserait les premiers.
 ('note a asterisque nue lue', 'outils/html.py',
  "re.match(r'(\\*)', nu)", 1),
 ('appel cherche sous sa forme propre', 'outils/html.py',
  "note['apel']", 1),
 # La vedette se juge sur ce qu'elle EST, non sur sa graisse : une
 # phrase d'exemple n'ouvre pas une section, une entree en italique en
 # ouvre une. Cinq temoins, un par piece de la regle.
 ('page : exemple ecarte par son verbe', 'outils/html.py',
  'VERBE_IDO', 2),
 ('page : mots non verbaux epargnes', 'outils/html.py',
  "NON_VERBI = {'plus'", 1),
 ('page : tete italique ou petites capitales', 'outils/html.py',
  'TETE_DETACHEE', 2),
 ('page : coupe a la marque de definition', 'outils/html.py',
  'COUPE_DEF', 2),
 ('page : ancre raccourcie rattrapee', 'outils/html.py',
  "if(id.indexOf(x+'-')===0", 1),
 ('publication : .nojekyll', '.nojekyll', None, 0),
]
TAILLES = [('ornamenti/portreto-3.png', 724, 1066),
           ('ornamenti/vinieto-3.png', 256, 251),
           ('ornamenti/fleuron-232.png', 209, 25)]


def main():
    mal = []
    for lib, f, ch, n in T:
        p = os.path.join(R, f)
        if not os.path.exists(p):
            mal.append('%-38s FICHIER ABSENT (%s)' % (lib, f)); continue
        if ch is None:
            continue
        v = open(p, encoding='utf-8', errors='replace').read().count(ch)
        if v < n:
            mal.append('%-38s %d trouve(s), %d attendu(s)' % (lib, v, n))
    try:
        import cv2
        for f, w, h in TAILLES:
            im = cv2.imread(os.path.join(R, f), cv2.IMREAD_UNCHANGED)
            if im is None:
                mal.append('%-38s ABSENT' % f); continue
            if (im.shape[1], im.shape[0]) != (w, h):
                mal.append('%-38s %d x %d, attendu %d x %d — cliche NON '
                           'REDRESSE ?' % (f, im.shape[1], im.shape[0], w, h))
    except ImportError:
        pass
    pdf = os.path.join(R, 'gramatiko.pdf')
    if os.path.exists(pdf):
        r = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True)
        m = re.search(r'Pages:\s+(\d+)', r.stdout)
        if m and m.group(1) != '236':
            mal.append('%-38s %s pages, 236 attendues' % ('le volume',
                                                          m.group(1)))
    else:
        mal.append('%-38s ABSENT' % 'gramatiko.pdf')
    print('%d temoins verifies' % (len(T) + len(TAILLES) + 1))
    if mal:
        print('\n%d MANQUENT :' % len(mal))
        for x in mal:
            print('  ' + x)
        return 1
    print('aucun correctif perdu.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
