#!/usr/bin/env python3
"""LISTE DE TEMOINS : une chaine caracteristique par correctif.

Cinq pertes de conteneur ont montre que « git log » ne prouve rien : la
derniere fois l'historique etait coherent et les FICHIERS ne l'etaient
pas. Ce qui detecte la panne, c'est de chercher, pour chaque correctif,
une chaine qui ne peut se trouver que s'il est en place.

    python3 tools/witnesses.py     # sort 1 si un temoin manque
"""
import os, re, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = [
 # (libelle, fichier, chaine attendue, nombre minimal)
 ('folio 82 : Ultre seul en gras', 'content/10-part1.tex',
  '\\VUgras{Ultre} esas', 1),
 ('renvois cliquables du Tabelo', 'preamble.tex', '\\VUlienOuvre', 3),
 ('ecart avant un numero large', 'preamble.tex',
  '\\newcommand{\\VUindexEcart}', 1),
 ('PDF nomme gramatiko', 'build.mk', 'jobname=gramatiko', 1),
 ('titre du folio 3 comprime', 'content/00-front-matter.tex',
  '\\VUetroit{0.702}', 1),
 ('KONSTATO comprime', 'content/00-front-matter.tex',
  '\\VUetroit{0.793}', 1),
 ('Averto comprime', 'content/00-front-matter.tex',
  '\\VUetroit{0.822}', 1),
 ('titre de couverture comprime', 'content/00-front-matter.tex',
  '\\VUetroit{0.668}', 1),
 ('PUNTIZADO elargi', 'content/20-part2.tex', '\\VUetroit{0.857}', 1),
 ('blanc du folio 21', 'content/10-part1.tex', '\\VUsaut{6.47mm}', 1),
 ('blanc du folio 122', 'content/20-part2.tex', '\\VUsaut{6.93mm}', 1),
 ('blanc du folio 169', 'content/20-part2.tex', '\\VUsaut{6.90mm}', 1),
 ('blanc du folio 195', 'content/20-part2.tex', '\\VUsaut{11.17mm}', 1),
 ('marque cachee', 'preamble.tex', '\\VUmarqueCachee', 2),
 ('planche a ordonnee absolue', 'preamble.tex', '\\VUplancheA', 2),
 ('portrait redresse (largeur)', 'preamble.tex',
  '\\VUplancheLargeur}{61.30mm}', 1),
 ('portrait redresse (ordonnee)', 'content/00-front-matter.tex',
  '\\VUplancheA{55.88mm}', 1),
 ('vignette redressee', 'content/00-front-matter.tex',
  '\\VUimageA{104.72mm}{22.38mm}', 1),
 ('signets : groupe APENDICI', 'content/90-marks.tex',
  'count -10 {APENDICI}', 1),
 ('signets : Tabelo page 227', 'content/90-marks.tex',
  'goto page 227 {/Fit} count 0 {TABELO', 1),
 ('page : Introdukto', 'tools/html.py', 'Introdukto', 1),
 ('page : hauteur d en-tete mesuree', 'tools/html.py', 'margoObs', 4),
 ('page : chefa vorti', 'tools/html.py', 'Chefa vorti', 1),
 ('page : en la tota libro', 'tools/html.py', 'tota libro', 1),
 ('page : anciennes ancres rattrapees', 'tools/html.py',
  'function trovAncro', 1),
 ('page : notes recollees comptees', 'tools/html.py', 'n_recol', 2),
 ('page : asterisme a son blanc', 'tools/html.py', 'self.aster', 3),
 ('page : bouts des accolades', 'tools/html.py', 'M8.6 1C5.8', 1),
 ('page : avis sur les deux prepozicioni', 'tools/html.py',
  'ridonas li a la loko', 1),
 # Folio 31 : l'accolade FERMANTE. Faute d'etre lue, elle ne rattachait
 # que « maxim » a « de o ek », et le nom retombait un demi-interligne
 # trop haut. Trois temoins : la lecture de la fermante, sa fusion dans
 # le groupe qu'elle couvre, et le decalage de mi-hauteur en colonnes.
 ('folio 31 : accolade fermante lue', 'tools/html.py',
  'def fermantes', 1),
 ('folio 31 : fermante fondue au groupe', 'tools/html.py',
  "ferme_brace", 3),
 ('folio 31 : case a mi-hauteur en colonnes', 'tools/html.py',
  'mezo', 3),
 ('folio 31 : membre insecable', 'tools/html.py',
  '.gr-m{white-space:nowrap}', 1),
 ('folio 31 : bord gauche d\'un groupe', 'tools/html.py',
  'def bord', 1),
 # Folio 220 : les deux schemas sont centres sur la justification. La
 # marque se pose d'apres le scan (marges gauche et droite egales), non
 # d'apres l'oeil ; trois temoins, un par piece.
 ('folio 220 : marque de centrage', 'preamble.tex',
  '\\newcommand{\\VUtabloCentrita}', 1),
 ('folio 220 : les deux schemas marques', 'content/20-part2.tex',
  '\\VUtabloCentrita', 2),
 ('folio 220 : centrage rendu', 'tools/html.py',
  '.centrita{display:flex', 1),
 # L'ASTERISQUE NUE est une marque de note (feuillets 74 et 122), et
 # l'appel se cherche sous la forme meme que le fac-simile emploie --
 # « (*) » aux feuillets 166, 191, 208, l'asterisque nue aux deux
 # autres. Les confondre casserait les premiers.
 ('note a asterisque nue lue', 'tools/html.py',
  "re.match(r'(\\*)', nu)", 1),
 ('appel cherche sous sa forme propre', 'tools/html.py',
  "note['apel']", 1),
 # Folio 130 : l'appel pose AVANT la tete ne doit pas cacher la vedette.
 # Le TABELO nomme lui-meme les trois du chapitre : equi-, ko-, mono-.
 ('appel avant la tete : vedette lue', 'tools/html.py',
  'APEL_TETE', 3),
 # Folio 31 : le groupe qui porte une fermante ne s'etire pas, sans quoi
 # l'accolade est rejetee contre le bord droit du volet.
 ('fermante contre ses membres', 'tools/html.py',
  '.gr.gf>.gr-l{flex:0 1 auto}', 1),
 # La vedette se juge sur ce qu'elle EST, non sur sa graisse : une
 # phrase d'exemple n'ouvre pas une section, une entree en italique en
 # ouvre une. Cinq temoins, un par piece de la regle.
 ('page : exemple ecarte par son verbe', 'tools/html.py',
  'VERBE_IDO', 2),
 ('page : mots non verbaux epargnes', 'tools/html.py',
  "NON_VERBI = {'plus'", 1),
 ('page : tete italique ou petites capitales', 'tools/html.py',
  'TETE_DETACHEE', 2),
 ('page : coupe a la marque de definition', 'tools/html.py',
  'COUPE_DEF', 2),
 ('page : ancre raccourcie rattrapee', 'tools/html.py',
  "if(id.indexOf(x+'-')===0", 1),
 # DEUX CLASSES D'ENTREES, ET UNE CASSE POUR CHACUNE. Le mot cite prend
 # la casse du mot -- le fac-simile capitalise l'entree qui OUVRE un
 # alinea et laisse en minuscule celles qui suivent (« Interne » folio
 # 62, « extere, supre, infre... » folio 63) --, les cinq noms propres
 # exceptes ; le titre de rubrique garde sa capitale. La graisse les
 # separe : le gras cite, l'italique et les petites capitales nomment.
 # Quatre temoins : la regle, la graisse rendue par `vedette()`, la
 # liste des noms propres, celle des six titres composes en gras.
 ('page : vedette a la casse du mot', 'tools/html.py',
  'casse_vedette', 3),
 ('page : graisse de la tete rendue', 'tools/html.py',
  'return t, fin, seule', 1),
 ('page : noms propres capitalises', 'tools/html.py',
  "NOMI_PROPRA = {'Europa'", 1),
 ('page : titres de rubrique en gras', 'tools/html.py',
  'RUBRIKI_GRASA', 2),
 ('publication : .nojekyll', '.nojekyll', None, 0),
]
TAILLES = [('ornaments/portrait-3.png', 724, 1066),
           ('ornaments/vignette-3.png', 256, 251),
           ('ornaments/fleuron-232.png', 209, 25)]


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
