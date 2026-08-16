#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PAGE DE LECTURE du volume : contenu/*.tex -> index.html.

Le fac-simile est compose LIGNE A LIGNE ; une page de lecture ne peut
pas l'etre. Cet outil ne reformate donc pas le releve, il le RELIT :
il rend a chaque alinea sa continuite (\\nl, \\cc, \\parplein,
\\VUcontinue), rattache chaque note a l'appel qui la demande, et garde
du fac-simile les deux seules choses qui servent au lecteur -- le folio,
qui renvoie au PDF, et la hierarchie parties / chapitres / vedettes.

Il est REJOUABLE : rien n'est ecrit a la main dans index.html, tout est
tire du releve. Recomposer le volume et rejouer l'outil suffit.

    python3 outils/html.py            # ecrit index.html
    python3 outils/html.py --konto    # comptages seuls, n'ecrit rien

CE QUI EST DELIBEREMENT LAISSE DE COTE
  -- les feuillets 3 a 7 (couverture imprimee, faux-titre, page de
     titre) : ce sont des pages d'apparat, composees a l'ordonnee
     mesuree, qui ne se lisent pas au fil du texte ;
  -- le TABELO (feuillets 229 et suivants) et les annonces de
     l'editeur : le TABELO est un index de renvois vers des folios,
     la page de lecture a sa propre navigation et sa propre recherche ;
     c'est aussi ce qui ecarte les trois \\VUtitre du feuillet 236,
     qui sont des titres de rubrique et non des chapitres ;
  -- les filets, ornements et fleurons : ils sont poses a une ordonnee
     absolue, ils n'appartiennent pas au flux du texte.

LE TEXTE N'EST JAMAIS CORRIGE. Les coquilles de 1925 sont conservees ;
l'outil ne touche qu'a ce qui est composition (coupures de ligne,
espacement a la francaise) et jamais a la lettre.
"""
import os
import re
import sys
from collections import OrderedDict

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENU = os.path.join(RACINE, 'contenu')
FICHIERS = ['00-liminaires.tex', '10-parto1.tex', '20-parto2.tex']
SORTIE = os.path.join(RACINE, 'index.html')

# Le PDF depose a cote de la page. Page du PDF = folio + 2 : le PDF
# commence au feuillet 3 (couverture imprimee) et le folio 1 est au
# feuillet 5. Verifie aux deux bornes -- folio 11 -> page 13,
# folio 225 -> page 227.
PDF = 'gramatiko.pdf'
PDF_DECALAGE = 2

# Le portrait de l'auteur, en tete de la page. Le PNG du scan est un
# demi-teinte a couche alpha : l'encre est NOIRE, le papier TRANSPARENT.
# Une balise <img> le rendrait noir sur noir en mode sombre ; on n'en
# garde donc que l'ALPHA, pose en MASQUE sur un bloc dont le fond est la
# couleur d'encre du theme. Le portrait suit alors l'encre du texte,
# dans les deux modes, comme la suit toute autre lettre de la page.
#   -- 650 px de large : le fac-simile en fait 726, et sa trame de
#      demi-teinte ne supporte pas d'etre reduite beaucoup plus ;
#   -- 8 niveaux d'alpha : la trame est un GRAIN, non un degrade ; huit
#      niveaux en sont indiscernables a l'oeil et divisent par quatre le
#      poids du PNG (194 ko contre 730).
PORTRAIT = os.path.join(RACINE, 'ornamenti', 'portreto-3.png')
PORTRAIT_FEUILLET = 7     # la page de titre, ou la planche est posee
PORTRAIT_LARGEUR = 650
PORTRAIT_NIVEAUX = 8
PORTRAIT_TITRE = 'Portreto dil autoro'

# Le folio 224 (feuillet 228) est un ADDENDUM : il ne porte qu'une
# phrase et deux articles, et la phrase dit elle-meme ou les deux
# articles appartiennent -- « pos til p. 82 ». La page de lecture les y
# remet, avec leur folio 224 et le renvoi au PDF qui va avec.
ADDENDUM_FEUILLET = 228
ADDENDUM_CHAPITRE = 'PREPOZICIONI.'
ADDENDUM_VEDETTE = 'Til'
# L'avis au lecteur. Une page qui deplace du texte doit le dire ; on le
# dit en ido, et entre crochets, comme toute intervention d'editeur.
ADDENDUM_AVIS = (
    'La originalo omisis ca du prepozicioni e pozis li ye la fino di '
    'la libro, p. 224 ; ca pagino ridonas li a la loko quan la verko '
    'ipsa indikas.')

# Les quatre groupes du volume, par feuillet de debut. Les bornes sont
# celles du releve de structure (LISEZ-MOI, 3.1). Les APENDICI forment
# un groupe A PART : le fac-simile les enchaine a la suite de la
# deuxieme partie, mais ce sont dix etudes autonomes, listees comme
# telles au folio 232, et non la queue du chapitre sur la composition.
PARTIES = [
    (8,   'Introdukto'),
    (13,  'Unesma parto \u2014 MORFOLOGIO E SINTAXO'),
    (119, 'Duesma parto \u2014 VORTIFADO'),
    (183, 'APENDICI'),
]
FEUILLET_PREMIER = 8      # avant : couverture, faux-titre, titre
FEUILLET_DERNIER = 228    # apres : TABELO, liste des apendici, annonces

# Ordonnee (mm) qui separe, sur une page d'apparat, ce qui se lit AVANT
# le corps de ce qui se lit APRES. \VUcentreA et consorts sont declares
# en tete de page mais poses a une ordonnee mesuree : sans ce tri, les
# signatures du folio 4 remonteraient au-dessus du texte qu'elles signent.
APPARAT_SEUIL = 60.0


# ------------------------------------------------------------------
# 1. LES COMMENTAIRES
# ------------------------------------------------------------------
def sans_commentaires(s):
    """Oter les commentaires LaTeX.

    Deux cas, et ils ne font pas la meme chose :
      -- un `%` en tete de ligne : la ligne entiere disparait, saut de
         ligne compris ;
      -- un `%` en fin de ligne : il mange la fin de la ligne ET le saut
         de ligne, donc il COLLE la ligne suivante a celle-ci. C'est de
         cette facon que le releve ecrit `\\VUnotes{...}{%` sans ouvrir
         d'espace parasite en tete de note.
    """
    sortie = []
    for ligne in s.split('\n'):
        m = re.search(r'(?<!\\)%', ligne)
        if m is None:
            sortie.append(ligne + '\n')
        elif ligne[:m.start()].strip() == '':
            pass                       # ligne de commentaire : rien du tout
        else:
            sortie.append(ligne[:m.start()])   # sans saut de ligne : on colle
    return ''.join(sortie)


# ------------------------------------------------------------------
# 2. LECTURE DES ARGUMENTS
# ------------------------------------------------------------------
def lire_groupe(s, i):
    """s[i] doit etre `{` (espaces admises avant). Rend (contenu, i_apres)."""
    while i < len(s) and s[i] in ' \n\t':
        i += 1
    if i >= len(s) or s[i] != '{':
        return '', i
    prof, j = 1, i + 1
    while j < len(s) and prof:
        if s[j] == '\\':
            j += 2
            continue
        if s[j] == '{':
            prof += 1
        elif s[j] == '}':
            prof -= 1
        j += 1
    return s[i + 1:j - 1], j


def lire_option(s, i):
    while i < len(s) and s[i] in ' \n\t':
        i += 1
    if i < len(s) and s[i] == '[':
        j = s.index(']', i)
        return s[i + 1:j], j + 1
    return None, i


def lire_args(s, i, n, opt=False):
    o = None
    if opt:
        o, i = lire_option(s, i)
    args = []
    for _ in range(n):
        a, i = lire_groupe(s, i)
        args.append(a)
    return o, args, i


def mm(x):
    """Une longueur du releve, en millimetres. mm, pt ou pouces."""
    m = re.match(r'\s*(-?[\d.]+)\s*(mm|pt|cm|in)?', x or '')
    if not m:
        return 0.0
    v = float(m.group(1))
    return {'mm': v, 'pt': v * 25.4 / 72.27, 'cm': v * 10,
            'in': v * 25.4, None: v}[m.group(2)]


# ------------------------------------------------------------------
# 3. LE TEXTE COURANT
# ------------------------------------------------------------------
# Les macros qui n'ont d'effet que sur la composition : leur argument est
# du texte, l'habillage disparait.
TRANSPARENTES = {'VUetroit': (2, 1), 'VUserre': (2, 1), 'VUdecale': (2, 1),
                 'VUcentreDA': (5, 4), 'textnormal': (1, 0), 'mbox': (1, 0)}
BALISES = {'VUgras': ('<b>', '</b>'), 'textbf': ('<b>', '</b>'),
           'textit': ('<i>', '</i>'), 'emph': ('<i>', '</i>'),
           'textsc': ('<span class="pk">', '</span>'),
           'textsuperscript': ('<sup>', '</sup>')}
LITTERAUX = {'textquotesingle': "'", 'nl': ' ', 'cc': '', ' ': ' ',
             '/': '',
             '{': '{', '}': '}', '%': '%', '&': '&amp;', '#': '#',
             '_': '_', 'relax': '', 'par': '\n\n', 'noindent': '',
             'ignorespaces': '', 'hfil': ' ', 'hfill': ' ',
             'VUaccolade': None, 'VUaccoladeD': None, 'VUaccoladeH': None}

resistantes = OrderedDict()   # macro -> nombre de rencontres non traitees


def echappe(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# Le module html de la bibliotheque standard est masque par CE fichier :
# le repertoire du script passe avant, et `import html` se rendrait
# lui-meme. Les deux fonctions dont on a besoin tiennent en trois lignes.
def desechappe(t):
    return (t.replace('&lt;', '<').replace('&gt;', '>')
             .replace('&nbsp;', '\u00a0').replace('&amp;', '&'))


def saute_blancs(s, i):
    """Apres un MOT de controle (\\nl, \\cc, \\VUcontinue...), TeX avale les
    blancs qui suivent -- mais pas une ligne blanche, qui reste une fin
    d'alinea. C'est de cette regle que depend le recollage des mots
    coupes d'une page a l'autre : `konso\\cc` puis `nanti` doivent donner
    `konsonanti`, et non `konso nanti`."""
    j = i
    while j < len(s) and s[j] in ' \t':
        j += 1
    if j < len(s) and s[j] == '\n':
        k = j + 1
        while k < len(s) and s[k] in ' \t':
            k += 1
        if k >= len(s) or s[k] != '\n':
            # k >= len(s) : la macro finit la page. Le blanc est avale
            # tout de meme, sans quoi un mot coupe au pied d'une page
            # (\\cc en derniere ligne) reprendrait avec une espace.
            return k
    return j


# ------------------------------------------------------------------
# 2 bis. UNE ACCOLADE QUI S'ETIRE
# ------------------------------------------------------------------
# Le glyphe { d'une fonte NE S'ETIRE PAS : il vaut une ligne, et rien de
# plus. Pose entre les trois rangees de points du folio 220 il ne coiffe
# rien -- c'est la premiere des deux plaintes du commanditaire.
#
# Trois voies s'offraient : etirer le glyphe par scaleY, dessiner
# l'accolade avec des bords arrondis en CSS, ou tracer un SVG en ligne.
#   -- scaleY allonge le fut mais etire aussi les courbes : la pointe
#      d'une accolade triplee de hauteur devient une tache, et la forme
#      depend de la fonte que le lecteur a. Ecarte.
#   -- les bords arrondis demandent quatre quarts de cercle et deux
#      futs, donc plusieurs elements par accolade, dont les raccords se
#      disjoignent des que le navigateur arrondit une demi-decimale ;
#      et tout serait a refaire pour l'horizontale. Ecarte.
#   -- LE SVG EN LIGNE : un seul trace, aucun raccord, la meme
#      mecanique dans les deux sens. `preserveAspectRatio="none"` etire
#      le dessin sur la boite exacte qu'on lui donne, si haute ou si
#      large soit-elle, et `vector-effect:non-scaling-stroke` garde au
#      trait son epaisseur -- sans quoi le fut d'une accolade triplee
#      serait trois fois plus gras que le texte. Retenu.
#
# Les traces suivent le fac-simile du folio 220 (scan/pages/f0224.jpg,
# encre x 786-796 y 877-995 pour la verticale, x 524-1063 y 1339-1355
# pour l'horizontale) : une accolade maigre a pointe peu saillante, et
# une horizontale presque plate a spicule central.
AKOLADI = {
    # Ouvrante : pointe a gauche, au milieu ; boite haute et etroite.
    'akol': ('0 0 10 100',
             # LES EXTREMITES S'INCURVENT A L'OPPOSE DE LA POINTE.
             # Le premier trace les ramenait vers elle : les trois bouts
             # regardaient du meme cote, ce qu'aucune accolade ne fait.
             # Dans le dessin ordinaire, la pointe centrale saille d'un
             # cote et les deux bouts se retournent de l'autre, au-dela
             # de l'aplomb des epaules.
             'M8.6 1C5.8 5 6 12 6 22L6 40C6 46 4 49 .8 50'
             'C4 51 6 54 6 60L6 78C6 88 5.8 95 8.6 99',
             'akv'),
    # Fermante : la meme, retournee (x devient 10-x).
    'akolD': ('0 0 10 100',
              'M1.4 1C4.2 5 4 12 4 22L4 40C4 46 6 49 9.2 50'
              'C6 51 4 54 4 60L4 78C4 88 4.2 95 1.4 99',
              'akd'),
    # Horizontale : pointe en haut, au milieu ; boite large et basse.
    'akolH': ('0 0 100 10',
              'M.8 9C16 5.9 30 5.7 47 5.7C48.4 5.7 49.2 4.2 50 1.2'
              'C50.8 4.2 51.6 5.7 53 5.7C70 5.7 84 5.9 99.2 9',
              'akh'),
}


def akolo(genre):
    """L'accolade `genre` en SVG, prete a etre etiree par le CSS."""
    vb, trace, classe = AKOLADI[genre]
    # `vector-effect` est pose en ATTRIBUT et non en CSS : tous les
    # navigateurs lisent l'attribut de presentation, la propriete CSS du
    # meme nom est plus recente -- et c'est sur un iPad que le defaut a
    # ete vu.
    return ('<span class="akol %s" aria-hidden="true">'
            '<svg viewBox="%s" preserveAspectRatio="none">'
            '<path vector-effect="non-scaling-stroke" d="%s"/>'
            '</svg></span>' % (classe, vb, trace))


def inline(s):
    """Convertir en HTML une suite d'inline TeX. Ne coupe jamais une
    ligne : c'est tout le propos de la page de lecture."""
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            m = re.match(r'\\([A-Za-z]+|.)', s[i:])
            nom = m.group(1)
            i += m.end()
            if nom.isalpha():
                i = saute_blancs(s, i)
            if nom in BALISES:
                a, i = lire_groupe(s, i)
                o, f = BALISES[nom]
                out.append(o + inline(a) + f)
            elif nom in TRANSPARENTES:
                nb, garde = TRANSPARENTES[nom]
                _, args, i = lire_args(s, i, nb)
                out.append(inline(args[garde]))
            elif nom == 'textls':
                _, args, i = lire_args(s, i, 1, opt=True)
                out.append(inline(args[0]))
            elif nom == 'VUtitreAppel':
                # L'appel de note du titre « Averto » : c'est du texte,
                # et c'est un appel comme un autre.
                _, args, i = lire_args(s, i, 1, opt=True)
                out.append(' ' + inline(args[0]))
            elif nom in ('VUaccolade', 'VUaccoladeD'):
                _, args, i = lire_args(s, i, 2)
                out.append(akolo('akol' if nom == 'VUaccolade' else 'akolD'))
            elif nom == 'VUaccoladeH':
                _, args, i = lire_args(s, i, 1)
                out.append(akolo('akolH'))
            elif nom in LITTERAUX:
                out.append(LITTERAUX[nom] or '')
            elif nom in ('fontsize', 'selectfont', 'normalfont', 'bfseries',
                         'itshape', 'lsstyle', 'centering'):
                if nom == 'fontsize':
                    _, _, i = lire_args(s, i, 2)
            else:
                resistantes[nom] = resistantes.get(nom, 0) + 1
        elif c == '{':
            a, i = lire_groupe(s, i)
            out.append(inline(a))
        elif c == '}':
            i += 1
        elif s.startswith('---', i):
            out.append('\u2014')
            i += 3
        elif s.startswith('--', i):
            out.append('\u2013')
            i += 2
        elif c == '~':
            out.append('\u00a0')
            i += 1
        elif c == '\n':
            out.append(' ')
            i += 1
        else:
            out.append(echappe(c))
            i += 1
    return ''.join(out)


FINE = '\u202f'   # espace fine insecable


def typographie(t):
    """L'espacement a la francaise du fac-simile, rendu INSECABLE.

    Le releve pose une espace ordinaire ; a l'ecran elle se coupe en fin
    de ligne et laisse un point-virgule orphelin. On ne pose de fine que
    la ou le fac-simile a mis une espace : jamais on n'en ajoute une ou
    l'original n'en a pas -- l'original alterne les deux usages, et c'est
    lui qui a raison.
    """
    t = re.sub(r' +([;:!?])', FINE + r'\1', t)
    t = re.sub(r'\u00ab +', '\u00ab' + FINE, t)
    t = re.sub(r' +\u00bb', FINE + '\u00bb', t)
    t = re.sub(r'  +', ' ', t)
    return t


def texte_nu(h):
    """Le texte seul d'un fragment HTML (pour les titres et les vedettes)."""
    return desechappe(re.sub(r'<[^>]+>', '', h)).strip()


# ------------------------------------------------------------------
# 3 bis. LA VEDETTE D'UN ALINEA
# ------------------------------------------------------------------
# Un alinea qui S'OUVRE par un passage en gras est une sous-entree, et
# c'est ce que liste le volet de droite : les 4 000 autres passages en
# gras du volume n'en sont pas. La regle est bonne, mais elle lisait
# l'ouverture trop etroitement, et manquait deux facons qu'a le
# fac-simile d'ecrire une vedette comme les autres.
#
#   -- LE NUMERO D'ALINEA NE COMPTE PAS. « 3. --- B = b en l'Italiana »
#      ouvre l'article B exactement comme « c = c Germana » ouvre celui
#      de c : le volume ne numerote que le premier alinea d'une suite.
#      Le chapitre des consonnes y perdait sa vedette B, et celui des
#      prepositions ses quarante-deux entrees, de Ad a Ye.
#   -- UNE VEDETTE PEUT ETRE DOUBLE. Au folio 11 l'article traite les
#      deux voyelles ensemble : « e, o apertita o klozita ». Les deux
#      lettres sont en gras, la virgule entre elles ne l'est pas ; la
#      vedette est « e, o », et non « e ».
#
# Rien n'est ajoute au texte : on lit seulement plus loin dans la ligne
# que le fac-simile a composee.
# Pas d'ancre `^` dans ces deux motifs : `Pattern.match(s, pos)` cale
# deja la lecture sur `pos`, mais `^` n'y suit pas -- il ne vaut qu'au
# vrai debut de la chaine. Avec lui, tout alinea precede d'une espace
# ou du renvoi de folio echappait a la lecture.
FOLIO_TETE = re.compile(r'<a class="fol"[^>]*>[^<]*</a>')
# « 3. --- », « 93. -- », « 16. — » : le numero, son point, son tiret.
NUMERO_ALINEA = re.compile(r'\d+(?:\s*bis)?\.\s*[\u2014\u2013-]?\s*')
GRAS_TETE = re.compile(r'<b>(.*?)</b>')


def vedette(h):
    """(texte de la vedette, offset apres son dernier `</b>`).

    Rend (None, -1) quand l'alinea n'en porte pas. L'offset sert au
    bouton en chaine : il se pose contre la vedette ENTIERE, non apres
    son premier morceau -- sans quoi il se glisserait entre le « e » et
    le « o » du folio 11.
    """
    i = 0
    m = FOLIO_TETE.match(h)
    if m:
        i = m.end()
    while i < len(h) and h[i] in ' \t\n':
        i += 1
    m = NUMERO_ALINEA.match(h, i)
    if m:
        i = m.end()
    m = GRAS_TETE.match(h, i)
    if not m:
        return None, -1
    bouts, fin = [m.group(1)], m.end()
    # Une vedette double, et pas davantage : la virgule qui lie les
    # morceaux doit etre NUE -- « e, o » se lit, « <b>a</b>, e <b>b</b> »
    # non.
    while h[fin:fin + 2] == ', ':
        m = GRAS_TETE.match(h, fin + 2)
        if not m:
            break
        bouts.append(m.group(1))
        fin = m.end()
    return texte_nu(', '.join(bouts)) or None, fin


# ------------------------------------------------------------------
# 4. LE PARCOURS DU RELEVE
# ------------------------------------------------------------------
# Macros de bloc dont l'argument est jete : elles ne posent que du blanc,
# du filet ou de l'ornement, c'est-a-dire de la mise en page.
MUETTES = {
    'VUsaut': 1, 'VUblanc': 1, 'VUblancAlinea': 0, 'VUinterlignePage': 1,
    'VUpageSerre': 2, 'VUfilet': 1, 'VUfiletnote': 0, 'VUfleuron': 0,
    'VUpageIndex': 0, 'vspace': 1, 'vspace*': 1, 'setlength': 2,
    'renewcommand': 2, 'newcommand': 2, 'VUmarqueCachee': 0,
    'nointerlineskip': 0, 'VUplanche': 1, 'VUimageA': 3, 'VUfolio': 1,
}
MUETTES_OPT = {'VUornement': 1, 'VUfiletA': 2, 'VUplancheA': 2}
# Les entrees du TABELO : la page de lecture ne les reprend pas.
INDEX = {'VUindex': 3, 'VUindexNu': 3, 'VUindexLarge': 3}


class Bloc(object):
    __slots__ = ('genre', 'frags', 'chap', 'ved', 'html', 'noti', 'x',
                 'ident', 'avis')

    def __init__(self, genre, frags=None, html=None, x=0.0):
        self.genre = genre        # tit sub p cen fer rango tab
        self.frags = frags or []  # [(feuillet, folio, html)]
        self.html = html
        self.chap = None
        self.ved = None
        self.noti = []            # notes rattachees a ce bloc
        self.ident = None
        self.avis = None          # avis d'editeur pose sous le bloc
        self.x = x


class Releve(object):

    def __init__(self):
        self.blocs = []
        self.chapitres = []       # {titre, bloc, feuillet, folio, part}
        self.notes = OrderedDict()  # (feuillet, numero) -> {'html','id'}
        self.notes_page = {}      # feuillet -> [numeros]
        self.pages = []           # (feuillet, folio)
        self.feuillet = 0
        self.folio = 0
        self.folios = {}
        self.cur = []             # fragments de l'alinea en cours
        self.suite = False        # le prochain alinea recolle au precedent
        self.parplein = False     # \parplein vu, et rien compose depuis
        self.derniere_note = None
        self.page_note = False    # page entiere composee au corps des notes
        self.rangs = []           # tableau en cours de constitution
        self.apparat = []
        self.parties_vues = []

    # -- alineas ----------------------------------------------------
    def ajoute(self, t):
        if not t:
            return
        self.parplein = False
        if self.cur and self.cur[-1][0] == self.feuillet:
            self.cur[-1][2] += t
        else:
            self.cur.append([self.feuillet, self.folio, t])

    def ferme(self, vider=True):
        """Fermer l'alinea courant, et le RECOLLER au precedent si le
        releve dit qu'il n'en est que la suite.

        Deux marques, et une seule fait foi. `\\VUcontinue` ouvre un
        alinea qui reprend au fer a gauche : c'est la marque du fac-simile
        lui-meme, elle ne peut pas se lire autrement. `\\parplein`, lui,
        se lit sur l'autre bord -- il justifie la derniere ligne d'une
        page -- mais le releve l'emploie aussi en cours de page, pour un
        alinea dont la derniere ligne remplit la mesure sans rien
        continuer du tout (65 emplois sur 114). Il ne vaut donc que
        LORSQU'IL TERMINE UNE PAGE, et l'on ne recolle alors que si rien
        n'a ete compose depuis."""
        if vider:
            self.vide_rangs()
        frags = [(f, fo, typographie(h)) for f, fo, h in self.cur
                 if h.strip()]
        self.cur = []
        if not frags:
            return
        prec = None
        for b in reversed(self.blocs):
            if b.genre == 'p':
                prec = b
                break
            if b.genre not in ('cen', 'orn', 'fer'):
                break
        if self.suite and prec is not None:
            prec.frags = prec.frags + frags
            self.suite = False
            return
        self.suite = False
        b = Bloc('p', frags)
        b.ved = vedette(frags[0][2])[0]
        self.blocs.append(b)

    # -- tableaux ---------------------------------------------------
    def vide_rangs(self):
        if not self.rangs:
            return
        rangs, self.rangs = self.rangs, []
        self.blocs.append(tableau(rangs, self.feuillet, self.folio))

    # -- notes ------------------------------------------------------
    def note(self, corps):
        """Depiler un bloc \\VUnotes en notes numerotees.

        Le bloc d'une page porte les notes appelees DANS cette page, et
        les numerote a partir de (1) -- ou de (*) quand le fac-simile
        emploie l'asterisque. Un alinea qui ne s'ouvre pas par un appel
        est la suite de la note precedente : suite de la meme page (c'est
        un nouvel alinea de la note), ou suite de la page d'avant quand
        la note deborde -- et il faut alors recoller la phrase, non
        ouvrir un alinea (folios 203-204).
        """
        f = self.feuillet
        self.notes_page.setdefault(f, [])
        # Ce qui, dans une note, n'est que de la mise en page.
        corps = re.sub(r'\\(VUblancAlinea|VUcontinue|parplein)(?![A-Za-z])',
                       '', corps)
        corps = re.sub(r'\\(VUblanc|VUsaut)\{[^{}]*\}', '', corps)
        courante = None
        premier = True
        for para in re.split(r'\n\s*\n', corps):
            if not para.strip():
                continue
            h = typographie(inline(para))
            if not texte_nu(h):
                continue
            m = re.match(r'\((\d+|\*)\)', texte_nu(h).lstrip())
            if m:
                num = m.group(1)
                cle = (f, num)
                self.notes[cle] = {'paras': [h.strip()], 'id': 'nt%d-%s' % (f, num),
                                   'feuillet': f, 'num': num, 'bloc': None}
                self.notes_page[f].append(num)
                courante = cle
            elif premier and courante is None and self.derniere_note:
                # Tete de bloc sans appel : la note de la page precedente
                # se poursuit, et la phrase se recolle.
                cible = self.derniere_note
                # UNE NOTE QUI ENJAMBE DEUX PAGES ne se recolle sans
                # espace que si elle finit sur une COUPURE DE MOT. Sans
                # ce test, « ... esas sempre » et « plu sekura ... »
                # donnaient « sempreplu » : le fragment finissait sur un
                # mot entier, et il y fallait une espace. Le recollage
                # muet reste juste quand la marque est un \cc, que
                # l'extraction a deja resolu en soudant les deux moities.
                self.n_recol = getattr(self, 'n_recol', 0)
                _av = self.notes[cible]['paras'][-1]
                if _av and not _av.endswith(('-', '\u2011')) \
                        and not _av.rstrip().endswith('-') \
                        and h[:1] not in ('', ' '):
                    _av = _av.rstrip() + ' '
                    self.n_recol += 1
                self.notes[cible]['paras'][-1] = _av + h.lstrip()
                courante = cible
            elif courante is not None:
                self.notes[courante]['paras'].append(h.strip())
            premier = False
        if courante:
            self.derniere_note = courante

    # -- pages ------------------------------------------------------
    def page(self, feuillet, folio, corps):
        self.feuillet = feuillet
        self.folio = self.folios[feuillet]
        self.pages.append((feuillet, self.folio))
        # Un \parplein qui terminait la page precedente : l'alinea
        # continue ici, meme si le releveur n'a pas pose \VUcontinue.
        if self.parplein:
            self.suite = True
            self.parplein = False
        if getattr(self, 'aster', False):
            # aucun grand saut n'a paru : mieux vaut l'asterisme mal place
            # que perdu. On le pose avant de changer de page.
            self.ferme()
            self.blocs.append(Bloc('orn', [(self.feuillet, self.folio,
                                            '\u2042')]))
        self.aster = False
        self.page_note = False
        self.apparat = []
        # Le saut de ligne qui suit \begin{VUpage} n'est pas du texte :
        # laisse tel quel, il ouvrait une espace en tete de page et
        # separait les deux moities d'un mot coupe au feuillet precedent.
        self.bloc_page(corps.lstrip(' \n\t'))
        self.vide_rangs()
        for y, h in sorted(self.apparat):
            if y >= APPARAT_SEUIL:
                self.blocs.append(Bloc('cen', [(feuillet, self.folio, h)]))

    def bloc_page(self, s):
        """Parcours d'une page au niveau des BLOCS. Tout ce qui n'est pas
        une macro de bloc tombe dans l'alinea en cours."""
        i, n = 0, len(s)
        tampon = []

        def deverse():
            if tampon:
                self.ajoute(inline(''.join(tampon)))
                del tampon[:]

        while i < n:
            # ligne blanche = fin d'alinea
            m = re.match(r'\n[ \t]*\n\s*', s[i:])
            if m:
                deverse()
                self.ferme()
                i += m.end()
                continue
            if s[i] == '\\':
                mm_ = re.match(r'\\([A-Za-z]+\*?)', s[i:])
                if mm_:
                    nom = mm_.group(1)
                    j = i + mm_.end()
                    fait, i2 = self.macro_bloc(nom, s, j, deverse)
                    if fait:
                        i = i2
                        continue
            tampon.append(s[i])
            i += 1
        deverse()
        self.ferme()

    def macro_bloc(self, nom, s, i, deverse):
        """Rend (traitee, position). Les macros inline sont laissees au
        convertisseur de texte."""
        # AVANT les macros muettes : sans cela \VUsaut est avale ici et
        # l'asterisme en attente ne trouve jamais son saut.
        if nom == 'VUsaut' and getattr(self, 'aster', False):
            _, args, i = lire_args(s, i, 1)
            v = re.match(r'\s*(-?[\d.]+)\s*mm', args[0] or '')
            if v and float(v.group(1)) >= 5.0:
                self.ferme()
                self.blocs.append(Bloc('orn', [(self.feuillet, self.folio,
                                                '\u2042')]))
                self.aster = False
            return True, i
        if nom in MUETTES:
            _, _, i = lire_args(s, i, MUETTES[nom])
            return True, i
        if nom in MUETTES_OPT:
            _, _, i = lire_args(s, i, MUETTES_OPT[nom], opt=True)
            return True, i
        if nom in INDEX:
            _, _, i = lire_args(s, i, INDEX[nom], opt=True)
            return True, i
        if nom == 'VUnotes':
            deverse()
            _, args, i = lire_args(s, i, 2, opt=True)
            self.note(args[1])
            return True, i
        if nom == 'VUpageNote':
            _, _, i = lire_args(s, i, 1)
            self.page_note = True
            return True, i
        if nom in ('VUtitre', 'VUsoustitre', 'VUcentre'):
            deverse()
            self.ferme()
            _, args, i = lire_args(s, i, 3)
            h = typographie(inline(args[2]).strip())
            genre = {'VUtitre': 'tit', 'VUsoustitre': 'sub',
                     'VUcentre': 'cen'}[nom]
            self.parplein = False
            b = Bloc(genre, [(self.feuillet, self.folio, h)])
            self.blocs.append(b)
            if genre == 'tit':
                self.chapitres.append({'titre': texte_nu(h), 'bloc': b,
                                       'feuillet': self.feuillet,
                                       'folio': self.folio})
            return True, i
        if nom in ('VUcentreA', 'VUcentreDA', 'VUsignature', 'VUcaseA'):
            deverse()
            nb = {'VUcentreA': 4, 'VUcentreDA': 5, 'VUsignature': 2,
                  'VUcaseA': 5}[nom]
            _, args, i = lire_args(s, i, nb)
            y = mm(args[0])
            if nom == 'VUcaseA':
                h = (typographie(inline(args[3]).strip()) + ' \u00b7 '
                     + typographie(inline(args[4]).strip()))
            else:
                h = typographie(inline(args[-1]).strip())
            if nom == 'VUsignature' and re.fullmatch(r'[0-9]+\*?', h or ''):
                # Signature de cahier : une marque de l'imprimeur au pied
                # de la premiere page d'un cahier, non un mot du volume.
                h = ''
            if h:
                self.apparat.append((y, h))
                if y < APPARAT_SEUIL:
                    # Ligne d'apparat en tete de page : sur les pages
                    # liminaires c'est le titre de la piece (KONSTATO.),
                    # et il ouvre un chapitre comme un \VUtitre.
                    b = Bloc('tit', [(self.feuillet, self.folio, h)])
                    self.blocs.append(b)
                    self.chapitres.append({'titre': texte_nu(h), 'bloc': b,
                                           'feuillet': self.feuillet,
                                           'folio': self.folio})
            return True, i
        if nom == 'VUauFer':
            deverse()
            self.ferme()
            _, args, i = lire_args(s, i, 2)
            self.parplein = False
            self.blocs.append(Bloc('fer', [(self.feuillet, self.folio,
                                            typographie(inline(args[1])))]))
            return True, i
        if nom == 'VUasterismo':
            # L'ASTERISME EST POSE A UNE ORDONNEE ABSOLUE, et declare en
            # tete de page comme tous les elements de hauteur nulle : le
            # prendre ou il est ecrit le placerait au haut de la page.
            # Au folio 209 il tombait entre « c) » et « d) » quand le
            # fac-simile le pose bien plus bas, au-dessus de « On dicis ».
            # La regle du volume donne ou le remettre : un element pose a
            # une ordonnee absolue N'OUVRE PAS SON PROPRE BLANC, il lui
            # faut un \VUsaut correspondant dans le flux. C'est donc a ce
            # saut-la que l'asterisme appartient. On le met en attente et
            # on le pose au premier grand saut de la meme page.
            _, _, i = lire_args(s, i, 1)
            self.aster = True
            return True, i
        if nom == 'VUrang':
            deverse()
            # Sans `vider=False`, chaque rang fermerait le tableau que le
            # rang precedent venait d'ouvrir : un tableau de six rangees
            # sortait en six tableaux d'une rangee.
            self.ferme(vider=False)
            _, args, i = lire_args(s, i, 1)
            self.parplein = False
            self.rangs.append(cases(args[0]))
            return True, i
        if nom == 'parplein':
            deverse()
            # \parplein tient lieu de la derniere marque de ligne de la
            # page : la ligne finit bien, simplement elle est justifiee.
            # Sans cette espace, l'alinea recolle page suivante souderait
            # deux mots (folio 7 : « renkontrar » + « en l'uzado »).
            self.ajoute(' ')
            self.ferme()
            self.parplein = True
            return True, saute_blancs(s, i)
        if nom == 'VUcontinue':
            deverse()
            # Suite de l'alinea de la page precedente : on recolle.
            self.suite = bool(self.blocs)
            self.parplein = False
            return True, saute_blancs(s, i)
        return False, i


# Pas des lignes de base du corps : \VUinterligne du preambule. Aucune
# des pages a tableau n'appelle \VUinterlignePage, donc ce pas vaut pour
# toutes ; il sert a lire la HAUTEUR d'une accolade en NOMBRE DE RANGS.
PAS_LIGNE = 9.99 * 25.4 / 72.27      # mm
# Ce qui separe deux cases d'un meme rang une fois les colonnes defaites :
# une espace ne suffit pas, « Petrus Paulus Ioannes Maria » se lirait
# comme une phrase.
ECART = '<span class="ec"></span>'


def cases(s):
    """Les \\VUcase d'un rang.

    Chaque case rend un dictionnaire : son abscisse mesuree, son HTML, et
    -- si c'est une accolade -- sa hauteur et le deplacement de son
    centre, tels que le releveur les a mesures sur le fac-simile. Ces
    deux nombres sont la seule chose qui dise COMBIEN DE RANGS l'accolade
    rassemble : c'est d'eux que se deduit le groupement.
    """
    out = []
    i = 0
    while i < len(s):
        m = re.compile(r'\\VUcase\b').search(s, i)
        if not m:
            break
        _, args, i = lire_args(s, m.end(), 2)
        brut = args[1]
        a = re.search(r'\\VUaccolade(D|H)?\{([^{}]*)\}(?:\{([^{}]*)\})?', brut)
        genre, haut, ecart = None, 0.0, 0.0
        if a:
            genre = {'': 'akol', 'D': 'akolD', 'H': 'akolH'}[a.group(1) or '']
            haut, ecart = mm(a.group(2)), mm(a.group(3) or '0pt')
        out.append({'x': mm(args[0]), 'h': typographie(inline(brut).strip()),
                    'k': genre, 'haut': haut, 'ecart': ecart})
    return out


def fusionne_conduite(rangs):
    """Les points de conduite ne sont pas des cases.

    Le releve les pose un a un, a leur abscisse mesuree. Laisses tels
    quels ils ouvrent cinq colonnes vides par tableau, et les nombres
    cessent de s'aligner d'un rang a l'autre. On les refond dans la case
    qui les precede -- ils n'ont donc de case nulle part."""
    propres = []
    for r in rangs:
        fusion = []
        for c in r:
            if texte_nu(c['h']) == '.' and fusion \
                    and set(texte_nu(fusion[-1]['h'])) == {'.'}:
                fusion[-1] = dict(fusion[-1], h=fusion[-1]['h'] + '.')
            else:
                fusion.append(c)
        ligne = []
        for c in fusion:
            if set(texte_nu(c['h'])) == {'.'} and len(texte_nu(c['h'])) > 1:
                c = dict(c, h='<span class="kond">%s</span>' % c['h'],
                         k='kond')
                if ligne and ligne[-1]['k'] not in ('akol', 'akolD',
                                                    'akolH'):
                    ligne[-1] = dict(ligne[-1],
                                     h=ligne[-1]['h'] + ' ' + c['h'])
                    continue
            ligne.append(c)
        propres.append(ligne)
    return propres


# ------------------------------------------------------------------
# 4 bis. CE QUE L'ACCOLADE VEUT DIRE
# ------------------------------------------------------------------
# Une grille de colonnes rend la POSITION des mots ; elle ne rend pas ce
# que l'accolade du fac-simile enonce, qui est un GROUPEMENT : un terme,
# et les formes qu'il coiffe. Sur un ecran etroit la grille se disperse
# et l'accolade flotte seule dans sa case -- le folio 31 y devient
# indechiffrable.
#
# Le groupement ne se devine pas : il se MESURE. `\VUaccolade{h}{d}`
# donne la hauteur de l'accolade et le deplacement de son centre ; la
# hauteur divisee par le pas des lignes donne le nombre de rangs
# rassembles, le deplacement dit sur quel rang le centre tombe. Au folio
# 31 : 27,2 pt = 3 rangs centres sur le deuxieme, 15,7 pt = 2 rangs,
# 17,4 pt = 2 rangs. C'est le fac-simile qui le dit, non l'outil qui le
# suppose.
def etendue(c, r, total):
    """Les rangs qu'une accolade posee au rang `r` coiffe : (premier,
    nombre). Sa hauteur relevee divisee par le pas des lignes donne le
    nombre de rangs, le deplacement de son centre dit ou ils commencent.
    C'est la meme mesure qui sert au rendu en groupes et a la grille :
    la case d'une accolade traverse ses rangs (rowspan), et le trace s'y
    etire."""
    n = max(1, int(round(c['haut'] / PAS_LIGNE)))
    centre = r - c['ecart'] / PAS_LIGNE
    a = int(round(centre - (n - 1) / 2.0))
    return max(0, min(a, total - n)), n


def groupes(rangs):
    """Les groupes que les accolades ouvrantes rassemblent."""
    gs = []
    for r, ligne in enumerate(rangs):
        for c in ligne:
            if c['k'] == 'akol':
                a, n = etendue(c, r, len(rangs))
                gs.append({'rangs': list(range(a, a + n)), 'x': c['x'],
                           'brace': c, 'titre': None, 'enfants': []})
            elif c['k'] == 'akolH':
                # L'accolade HORIZONTALE du folio 220 : pointe en haut,
                # elle rattache le rang qui la porte au rang du dessus.
                gs.append({'rangs': [r], 'x': c['x'], 'brace': c,
                           'titre': None, 'enfants': [], 'haut': True})
    for g in gs:
        cands = [c for r in g['rangs'] for c in rangs[r]
                 if c['x'] < g['x'] and c['k'] not in ('akol', 'akolD',
                                                       'akolH', 'kond')]
        if not cands:
            # Le hors-texte du folio 220 n'a pour matiere que des points :
            # la rangee de points qui est a gauche de l'accolade EST le
            # terme qu'elle coiffe (« un lineo unlatere »).
            cands = [c for r in g['rangs'] for c in rangs[r]
                     if c['x'] < g['x'] and c['k'] == 'kond']
        if g.get('haut'):
            # Son titre est au rang precedent, non a sa gauche.
            r0 = g['rangs'][0] - 1
            cands = [c for c in (rangs[r0] if r0 >= 0 else [])
                     if c['k'] is None]
            g['titre'] = cands[-1] if cands else None
            if g['titre'] is not None:
                g['rang_titre'] = r0
        elif cands:
            g['titre'] = max(cands, key=lambda c: c['x'])
            g['rang_titre'] = [r for r in g['rangs']
                               if g['titre'] in rangs[r]][0]
    gs = [g for g in gs if g['titre'] is not None]
    # Un groupe s'emboite dans un autre quand son TITRE est l'un des
    # membres de l'autre -- et non quand ses rangs y sont compris : au
    # folio 31 les deux groupes du bas se chevauchent d'un rang sans que
    # l'un contienne l'autre, et c'est bien « relatanta », titre du
    # premier, qui est membre du second.
    for g in gs:
        peres = [h for h in gs if h is not g and h['x'] < g['x']
                 and g.get('rang_titre') in h['rangs']
                 and g['titre'] is not h['titre']]
        g['pere'] = min(peres, key=lambda h: len(h['rangs'])) if peres else None
    for g in gs:
        if g['pere'] is not None:
            g['pere']['enfants'].append(g)
    return gs


def rangs_couverts(g):
    s = set(g['rangs']) | {g.get('rang_titre')}
    for e in g['enfants']:
        s |= rangs_couverts(e)
    return {r for r in s if r is not None}


def rendu_groupe(g, rangs, pris):
    """Un groupe : son titre, l'accolade, puis ses membres.

    L'accolade n'est plus remplacee par un filet : c'est le trace du
    fac-simile lui-meme qui est pose entre le titre et les membres, et
    le CSS l'etire sur toute leur hauteur. Le groupe a pointe en haut --
    l'arbre genealogique du folio 220 -- empile les trois memes pieces
    de haut en bas au lieu de les ranger de gauche a droite : titre,
    accolade horizontale, membres.
    """
    pris.add(id(g['brace']))
    pris.add(id(g['titre']))
    membres = []
    couverts = sorted(rangs_couverts(g))
    for r in couverts:
        enfant = None
        for e in g['enfants']:
            if r in rangs_couverts(e):
                enfant = e
                break
        if enfant is not None:
            if r == min(rangs_couverts(enfant)):
                membres.append(rendu_groupe(enfant, rangs, pris))
            continue
        cells = [c for c in rangs[r] if c['x'] > g['x']
                 and id(c) not in pris and c is not g['titre']]
        for c in cells:
            pris.add(id(c))
        if cells:
            membres.append('<div class="gr-m">%s</div>' % ECART.join(
                c['h'] for c in cells))
    return ('<div class="gr%s"><div class="gr-t">%s</div>%s'
            '<div class="gr-l">%s</div></div>'
            % (' grh' if g.get('haut') else '', g['titre']['h'],
               g['brace']['h'], ''.join(membres)))


def rendu_grupi(rangs, gs, sola=False):
    """Le tableau entier, rendu en groupes : ce qui n'appartient a aucune
    accolade reste une ligne, dans l'ordre du fac-simile."""
    pris = set()
    racines = [g for g in gs if g['pere'] is None]
    ouvre = {}
    for g in racines:
        ouvre.setdefault(min(rangs_couverts(g)), []).append(g)
    couvert = {}
    for g in racines:
        for r in rangs_couverts(g):
            couvert[r] = g
    out = []
    for r in range(len(rangs)):
        # Ce qui, sur ce rang, tombe A GAUCHE de l'accolade sans etre son
        # titre : au folio 31, le numero « 28. » du paragraphe.
        g = couvert.get(r)
        if g is not None:
            avant = [c for c in rangs[r] if c['x'] < g['x']
                     and c is not g['titre'] and c['k'] != 'akol']
            for c in avant:
                pris.add(id(c))
                out.append('<div class="gr-x">%s</div>' % c['h'])
        for gg in ouvre.get(r, []):
            out.append(rendu_groupe(gg, rangs, pris))
        if g is None:
            cells = [c for c in rangs[r] if id(c) not in pris]
            if cells:
                out.append('<div class="gr-x">%s</div>'
                           % ECART.join(c['h'] for c in cells))
    # `sola` : le rendu en groupes est le SEUL -- il parait donc aussi
    # sur ecran large, ou la regle qui le masque ne doit pas l'atteindre.
    return '<div class="grupi%s">%s</div>' % (' sola' if sola else '',
                                              ''.join(out))


def tableau(rangs, feuillet, folio):
    """Rendre une suite de \\VUrang.

    Trois sorties possibles, selon ce que le releve contient :
      -- un rang d'une seule case n'est pas un tableau, c'est une ligne
         detachee : elle garde son retrait mesure ;
      -- un tableau sans accolade sort en <table>, colonnes retrouvees en
         groupant les abscisses proches (5 mm de proche en proche), ce
         qui est large devant le jeu de la mesure et etroit devant
         l'ecart des colonnes du volume ;
      -- un tableau A ACCOLADES sort DEUX FOIS : en colonnes pour
         l'ecran large, en groupes pour l'ecran etroit. Le CSS n'en
         montre qu'une a la fois. L'accolade horizontale, elle, ne sort
         qu'en groupes : sa grille ne dit rien a personne.
    """
    propres = fusionne_conduite(rangs)

    if all(len(r) <= 1 for r in propres):
        h = ''.join('<div class="rango" style="padding-left:%.1f%%">%s</div>'
                    % (min(c['x'] / 91.69 * 100, 60), c['h'])
                    for r in propres for c in r)
        return Bloc('rango', [(feuillet, folio, h)])

    gs = groupes(propres)
    horizontale = any(c['k'] == 'akolH' for r in propres for c in r)

    # Les colonnes. Les abscisses proches se regroupent (5 mm de proche
    # en proche), ce qui est large devant le jeu de la mesure et etroit
    # devant l'ecart des colonnes du volume.
    #
    # MAIS une accolade ne partage plus la case du texte. Tant qu'elle
    # la partageait -- collee a gauche de « egaleso » au folio 31, des
    # points de conduite au folio 220 -- aucune case ne lui appartenait
    # en propre, donc rien ne pouvait s'etendre sur les rangs qu'elle
    # coiffe. Elle se detache donc de son groupe et prend une colonne A
    # SA GAUCHE : au folio 31 comme au folio 220 l'accolade precede
    # toujours ce qu'elle rassemble. Le reste du groupe demeure UNE
    # colonne -- sans quoi « Komparativo » et « relatanta », que
    # l'accolade separe de 5,7 mm, se seraient rangees dans deux
    # colonnes et le tableau du folio 31 aurait bee.
    AK = ('akol', 'akolD', 'akolH')
    axes = sorted({(c['x'], c['k'] in AK) for r in propres for c in r})
    paquets, prec = [], None
    for x, ak in axes:
        if prec is None or x - prec > 5.0:
            paquets.append([])
        paquets[-1].append((x, ak))
        prec = x
    cols = []
    for p in paquets:
        prec = None
        for x, ak in p:
            if ak and (prec is None or x - prec > 5.0):
                cols.append((x, True))
            if ak:
                prec = x
        texte = [x for x, ak in p if not ak]
        if texte:
            cols.append((min(texte), False))

    def colonne(c):
        """La colonne d'une case : la plus proche DE MEME NATURE."""
        ak = c['k'] in AK
        cand = [j for j in range(len(cols)) if cols[j][1] == ak]
        return min(cand or range(len(cols)),
                   key=lambda j: abs(cols[j][0] - c['x']))

    # La case d'une accolade traverse les rangs qu'elle coiffe : elle
    # est portee au premier d'entre eux, avec le rowspan que la mesure
    # donne, et les rangs suivants n'ouvrent plus de case dans cette
    # colonne. C'est cette case-la, haute de trois rangs au folio 220,
    # que le trace remplit.
    grille = [[[] for _ in cols] for _ in propres]
    portee, sous = {}, set()
    for r, ligne in enumerate(propres):
        for c in ligne:
            j = colonne(c)
            if c['k'] in ('akol', 'akolD'):
                a, n = etendue(c, r, len(propres))
                if n > 1 and all(not grille[q][j] and (q, j) not in sous
                                 for q in range(a, a + n)):
                    grille[a][j].append(c['h'])
                    portee[(a, j)] = n
                    sous.update((q, j) for q in range(a + 1, a + n))
                    continue
            grille[r][j].append(c['h'])
    lignes = []
    for r in range(len(propres)):
        tds = []
        for j in range(len(cols)):
            if (r, j) in sous:
                continue
            n = portee.get((r, j), 1)
            tds.append('<td%s%s>%s</td>'
                       % (' class="ak"' if cols[j][1] else '',
                          ' rowspan="%d"' % n if n > 1 else '',
                          ' '.join(grille[r][j])))
        lignes.append('<tr>' + ''.join(tds) + '</tr>')
    table = '<table class="tab">' + ''.join(lignes) + '</table>'

    if not gs:
        return Bloc('tab', [(feuillet, folio, table)])
    if horizontale:
        return Bloc('tab', [(feuillet, folio,
                             rendu_grupi(propres, gs, sola=True))])
    return Bloc('tab', [(feuillet, folio, '<div class="larja">%s</div>%s'
                         % (table, rendu_grupi(propres, gs)))])


def table_folios(pages):
    """feuillet -> folio, pour toutes les pages du volume.

    Le folio n'est pas imprime sur toute page : ni sur celles qui ouvrent
    une partie, ni sur celles qui ouvrent un chapitre, ni sur les
    blanches. Le prendre « au dernier connu » suffit tant qu'on lit dans
    l'ordre, mais pas en tete : le premier feuillet lu (8, la KONSTATO)
    precede le premier folio imprime (6, au feuillet 10) et n'aurait donc
    aucun antecedent. On interpole donc depuis le folio connu LE PLUS
    PROCHE, avant ou apres -- un feuillet vaut un folio, sans exception
    dans ce volume.
    """
    connus = sorted((f, fo) for f, fo in pages if fo is not None)
    table = {}
    for f, _ in pages:
        g, fo = min(connus, key=lambda c: abs(c[0] - f))
        table[f] = fo + (f - g)
    return table


# ------------------------------------------------------------------
# 5. LES APPELS DE NOTE
# ------------------------------------------------------------------
def rattache_notes(rel):
    """Rattacher chaque note a l'appel qui la demande.

    Le bloc \\VUnotes d'une page porte les notes appelees DANS cette page
    et les numerote a partir de (1) : c'est donc dans les fragments de
    cette page-la, et nulle part ailleurs, qu'il faut chercher `(n)`. Un
    alinea qui court sur deux pages garde ses fragments separes ; c'est
    ce qui permet de ne pas confondre le (1) d'une page avec celui de la
    suivante.

    Trois recours, dans cet ordre, parce que le volume emploie les trois :
      1. l'appel dans le texte courant de la page ;
      2. l'appel dans une AUTRE note de la meme page -- une note peut en
         appeler une autre (folios 162 et 187, appels en asterisque) : la
         note appelee se pose alors sous l'alinea qui porte l'appelante ;
      3. le renvoi en toutes lettres. Au folio 90 le texte ne porte
         aucun appel (2) : il dit « (Videz infre la noto 2.) ». C'est
         l'original qui est ainsi, et l'on ne le corrige pas ; la note se
         pose sous cet alinea-la.
    """
    attente = {f: list(nums) for f, nums in rel.notes_page.items()}

    def pose(cle, bloc):
        rel.notes[cle]['bloc'] = bloc
        bloc.noti.append(cle)
        attente[cle[0]].remove(cle[1])

    def marque(h, appel, note):
        p = trouve_appel(h, appel)
        if p < 0:
            return h, False
        return (h[:p] + '<a class="apelo" href="#%s" data-nt="%s">%s</a>'
                % (note['id'], note['id'], appel) + h[p + len(appel):]), True

    # 1. l'appel dans le texte courant
    for b in rel.blocs:
        neuf = []
        for (f, fo, h) in b.frags:
            for num in list(attente.get(f) or ()):
                h, trouve = marque(h, '(%s)' % num, rel.notes[(f, num)])
                if trouve:
                    pose((f, num), b)
            neuf.append((f, fo, h))
        b.frags = neuf

    # 2. l'appel loge dans une autre note de la meme page
    for cle, note in list(rel.notes.items()):
        if note['bloc'] is None:
            continue
        for autre in list(attente.get(cle[0]) or ()):
            for k, para in enumerate(note['paras']):
                para2, trouve = marque(para, '(%s)' % autre,
                                       rel.notes[(cle[0], autre)])
                if trouve:
                    note['paras'][k] = para2
                    pose((cle[0], autre), note['bloc'])
                    break

    # 3. le renvoi en toutes lettres, puis le dernier alinea de la page
    orphelines = []
    for cle, note in rel.notes.items():
        if note['bloc'] is not None:
            continue
        f, num = cle
        cible, renvoi = None, None
        for b in rel.blocs:
            for (ff, fo, h) in b.frags:
                if ff != f:
                    continue
                cible = b
                if re.search(r'noto\s*%s' % re.escape(num), texte_nu(h)):
                    renvoi = b
        if renvoi is not None:
            renvoi.noti.append(cle)
            note['bloc'] = renvoi
            note['renvoi'] = True
        elif cible is not None:
            cible.noti.append(cle)
            note['bloc'] = cible
            note['orfa'] = True
        orphelines.append(cle)
    return orphelines


def trouve_appel(h, appel):
    """Position de `(n)` dans un fragment HTML, hors balise."""
    i = 0
    while True:
        p = h.find(appel, i)
        if p < 0:
            return -1
        if h.count('<', 0, p) == h.count('>', 0, p):
            return p
        i = p + 1


# ------------------------------------------------------------------
# 6. STRUCTURE
# ------------------------------------------------------------------
def structure(rel):
    """Parties -> chapitres. Les chapitres sont ranges par le feuillet ou
    leur titre est compose."""
    parties = [{'label': lab, 'debut': f, 'chapitres': []}
               for f, lab in PARTIES]
    for ch in rel.chapitres:
        p = None
        for cand in parties:
            if ch['feuillet'] >= cand['debut']:
                p = cand
        p['chapitres'].append(ch)
        ch['partie'] = p
    return [p for p in parties if p['chapitres']]


# ------------------------------------------------------------------
# 6 quater. LE PORTRAIT, RENDU EN MASQUE
# ------------------------------------------------------------------
def masque_portrait():
    """Le PNG du portrait, reduit a SA SEULE COUCHE ALPHA, en data:.

    Le fac-simile est une similigravure : l'encre y est noire, le papier
    transparent. Rendue par un `<img>`, elle serait noire sur noir en
    mode sombre -- c'est un defaut qui ne se voit pas tant qu'on ne
    regarde pas. On ne garde donc AUCUNE couleur : le PNG produit ne
    porte que l'alpha, et le CSS le pose en masque sur un bloc dont le
    fond est `var(--enk)`. Le portrait est alors de l'encre, comme le
    reste de la page, et suit le theme.

    Le PNG sort en palette : les huit niveaux d'alpha tiennent dans un
    tRNS de huit octets, la palette elle-meme est toute noire et ne sert
    a rien -- seul l'alpha est lu. C'est la forme la plus legere qui
    reste un PNG ordinaire.
    """
    import base64
    import io
    from PIL import Image

    im = Image.open(PORTRAIT).convert('RGBA')
    haut = int(round(im.height * PORTRAIT_LARGEUR / float(im.width)))
    alpha = im.resize((PORTRAIT_LARGEUR, haut), Image.LANCZOS).getchannel('A')

    n = PORTRAIT_NIVEAUX
    pas = 256.0 / n
    index = alpha.point(lambda v: min(int(v / pas), n - 1))
    p = index.convert('P')
    p.putpalette([0, 0, 0] * 256)
    trns = bytes(int(round(i * 255.0 / (n - 1))) for i in range(n))

    tampon = io.BytesIO()
    p.save(tampon, 'PNG', optimize=True, transparency=trns)
    brut = tampon.getvalue()
    uri = 'data:image/png;base64,' + base64.b64encode(brut).decode('ascii')
    return uri, PORTRAIT_LARGEUR, haut, len(brut)


# La legende du fac-simile, telle qu'elle est gravee sous le portrait.
# « de Beaufront » en petites capitales, « Ido » en italique : c'est la
# composition du volume, non un choix de la page.
LEGENDE = ('Markezo L. <span class="pk">de Beaufront</span>, precipua '
           'autoro di <i>Ido</i>')


# ------------------------------------------------------------------
# 7. SORTIE
# ------------------------------------------------------------------
GABARIT = u"""<!DOCTYPE html><html lang="io"><meta charset="utf-8">
<title>Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--enk:#1a1a1a;--pap:#fbfaf7;--sub:#6b6560;--acc:#7a4b2a;--lin:#e2ddd5;--flag:#b4552d}
@media(prefers-color-scheme:dark){:root{--enk:#e8e4de;--pap:#16161a;--sub:#9a938c;--acc:#d69a6a;--lin:#2c2c33;--flag:#e08a5c}}
*{box-sizing:border-box}
body{margin:0;background:var(--pap);color:var(--enk);
 font:16px/1.55 "Iowan Old Style",Palatino,"Palatino Linotype",Georgia,serif}
header{position:sticky;top:0;background:var(--pap);border-bottom:1px solid var(--lin);
 padding:14px 20px 12px;z-index:20}
/* Le bouton de telechargement s'ancre en haut a droite du titre. Sur ecran
   etroit il perd son texte et ne garde que l'icone : la barre de recherche a
   besoin de toute la largeur. */
.tito{display:flex;align-items:flex-start;gap:12px;justify-content:space-between}
.dl{flex:none;display:inline-flex;align-items:center;gap:6px;text-decoration:none;
 border:1px solid var(--lin);border-radius:7px;padding:6px 11px;color:var(--acc);
 background:var(--pap);font-size:13px;font-weight:600;white-space:nowrap;
 transition:background .12s,border-color .12s}
.dl:hover{background:var(--lin);border-color:var(--acc)}
.dl svg{display:block;width:15px;height:15px;stroke:currentColor;fill:none;
 stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
@media (max-width:560px){.dl span{display:none}.dl{padding:7px 9px}}
h1{margin:0 0 2px;font-size:17px;font-weight:600;letter-spacing:.01em}
.sub{color:var(--sub);font-size:12.5px;margin-bottom:10px}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
input[type=search]{flex:1 1 260px;min-width:160px;padding:8px 11px;border:1px solid var(--lin);
 border-radius:7px;background:var(--pap);color:var(--enk);font:inherit;font-size:16px}
/* 16px exacte, e ne min: Safari sur iPhone zomas automate sur irga kampo di
   qua la litero-grandeso esas sub 16px, kande onu tushas lu. La altra
   solvuro -- maximum-scale=1 en la meta viewport -- impedus anke la zomo per
   la fingri, do la lekteblesa por qui bezonas lu. */
input[type=search]:focus{outline:2px solid var(--acc);outline-offset:-1px}
.tir{display:none;flex:none;border:1px solid var(--lin);border-radius:7px;
 background:var(--pap);color:var(--acc);font:600 12.5px/1 system-ui,sans-serif;
 padding:9px 11px;cursor:pointer}
.tir:hover{background:var(--lin)}

/* --- Tri panelo. Sur komputoro: tabelo dil materio, texto, chefa vorti.
   La du lateral paneli ruliras aparte de la texto : la lekto dil texto
   ne movas li. --- */
main{display:grid;grid-template-columns:250px minmax(0,1fr) 230px;
 max-width:1360px;margin:0 auto;gap:0}
/* Les volets lateraux se collent SOUS l'en-tete, dont la hauteur varie
   (deux lignes de titre sur iPad). Fixee a 97 px, la valeur cachait le
   haut du volet — le premier intitule passait sous la barre. Elle suit
   maintenant --kapo, mesuree par le script. */
nav,aside{position:sticky;top:var(--kapo,97px);
 height:calc(100vh - var(--kapo,97px));overflow-y:auto;
 padding:16px 14px 60px;font-family:system-ui,sans-serif;font-size:13px}
nav{border-right:1px solid var(--lin)}
aside{border-left:1px solid var(--lin)}
nav .parto{margin:14px 0 5px;font-size:11px;letter-spacing:.07em;text-transform:uppercase;
 color:var(--sub);font-weight:700}
nav a,aside a{display:block;padding:3px 6px;border-radius:5px;text-decoration:none;
 color:var(--enk);line-height:1.35}
nav a{font-size:12.5px}
nav a:hover,aside a:hover{background:var(--lin)}
nav a.nun,aside a.nun{color:var(--acc);font-weight:700;background:rgba(122,75,42,.07)}
aside .kapo{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--sub);
 font-weight:700;margin-bottom:8px}
aside a{font-size:12.5px;color:var(--sub)}
#vednav{display:none}
#vednav a{font-size:12px;color:var(--sub)}

/* La folio se pose EN DEHORS du texte, 3,6 em a gauche de lui -- 3,6 em
   de SON corps a elle, 11 px, soit 40 px. Le blanc de gauche n'en
   mesurait que 34 : des que la colonne centrale cessait d'etre plus
   large que le bloc -- sous 1160 px, donc sur tout iPad -- la folio
   sortait du bloc et mordait de 6 px sur le volet de la table des
   matieres. Le blanc de gauche loge desormais la folio et son air ; la
   largeur maximale grandit d'autant, pour que la JUSTIFICATION du texte
   ne change pas d'un point sur ordinateur. */
#kont{padding:26px 58px 140px 58px;max-width:728px;margin:0 auto;position:relative}
.p{margin:0 0 .62em;text-align:justify;text-indent:1.3em;position:relative;
 hyphens:auto;-webkit-hyphens:auto}
.tit{font-weight:700;text-align:center;letter-spacing:.08em;font-size:15px;
 margin:2.2em 0 1em;position:relative}
/* La baro esas glutinoza : irga ancero devas haltar sub ol. */
/* La marge de defilement doit valoir la hauteur REELLE de l'en-tete
   collant. Fixee en dur — 112 px ici, 215 px sur telephone — elle
   mentait des que l'en-tete changeait de hauteur : sur iPad, le titre
   passe sur deux lignes sans que la regle du telephone s'applique, et
   le haut de la section visee disparaissait sous la barre de recherche.
   La hauteur est donc mesuree au chargement et a chaque redimension,
   et deposee dans --kapo ; les valeurs en dur ne servent plus que de
   secours avant que le script ait tourne. */
.tit,.p,.rangi,.cen,.sub2,.noto,.avizo,.fig{
 scroll-margin-top:calc(var(--kapo,112px) + 12px)}
.sub2{text-align:center;font-style:normal;margin:-.6em 0 1em;color:var(--sub);
 position:relative}
.cen{text-align:center;margin:.9em 0;position:relative}
.fer{text-align:right;margin:.9em 0;position:relative}
.orn{text-align:center;color:var(--sub);margin:1.4em 0;letter-spacing:.3em}
.rango{margin:.1em 0;text-indent:0}
.rangi{margin:.8em 0;position:relative}
/* --- L'ACCOLADE. Le glyphe { d'une fonte ne s'etire pas ; ce trace-ci,
   oui : preserveAspectRatio="none" le plaque sur la boite exacte que le
   CSS lui donne -- trois rangs de haut, ou toute la largeur d'une
   fratrie -- et vector-effect:non-scaling-stroke garde au trait
   l'epaisseur d'un plein de la fonte, quel que soit l'etirement.
   La regle ci-dessous est la mesure par defaut : une accolade EN
   LIGNE, haute d'une ligne, pour celles qui n'ouvrent aucun groupe --
   le « } » de « de o ek », au folio 31, sur ecran etroit. Les trois
   contextes qui l'etirent la surchargent plus bas. --- */
.akol{display:inline-block;vertical-align:-.28em;width:.34em;height:1.2em;
 color:var(--sub)}
.akol.akh{width:2.2em;height:.6em;vertical-align:.1em}
.akol svg{display:block;width:100%;height:100%;overflow:visible}
.akol path{fill:none;stroke:currentColor;stroke-width:.085em;
 stroke-linecap:round;stroke-linejoin:round}

.tab{border-collapse:collapse;margin:.9em 0 .9em 1em;font-size:.97em}
.tab td{padding:1px 10px 1px 0;vertical-align:middle}
/* La case d'une accolade traverse les rangs qu'elle coiffe (rowspan) :
   le trace s'y cale en absolu, du haut du premier rang au bas du
   dernier -- seule maniere sure d'obtenir la hauteur exacte d'un
   groupe de rangs, qu'aucune mesure en em ne connait.
   MAIS un contenu en position absolue ne compte pour rien dans la
   largeur d'une colonne : `width` n'y etant qu'un voeu, la case tombait
   a ZERO des que le tableau du folio 31 se serrait -- entre 900 et
   1000 px de fenetre -- et l'accolade disparaissait. La largeur est
   donc portee par les BLANCS de la case, que la mise en table ne peut
   pas reduire : le blanc de gauche fait la largeur du trace, celui de
   droite l'ecart a la colonne suivante. */
.tab td.ak{position:relative;padding:0 .4em 0 .75em}
.tab td.ak>.akol{position:absolute;top:1px;right:.4em;bottom:1px;left:0;
 width:auto;height:auto}
/* Une colonne de plus par accolade, c'est le tableau du folio 31 plus
   large de 50 px : sous 1000 px de fenetre il debordait sur le volet
   de droite. Le seuil du rendu en groupes est donc remonte a 1200 px
   (voir plus bas) ; ce garde-fou-ci ne sert plus que si le lecteur
   grossit assez le corps pour qu'un tableau passe encore -- il defile
   alors dans sa colonne plutot que d'en sortir. */
.larja{max-width:100%;overflow-x:auto}
/* Le meme tableau, dit deux fois : en colonnes pour l'ecran large, en
   groupes pour l'ecran etroit. Un seul des deux parait a la fois. */
.grupi{display:none;text-indent:0;margin:.9em 0}
.grupi.sola{display:block;margin-left:1em}
.gr{display:flex;align-items:center;gap:7px;margin:.1em 0;min-width:0}
.gr-t{flex:none}
/* Le filet qui tenait lieu d'accolade a cede la place a l'accolade
   elle-meme : etiree par align-self:stretch sur toute la hauteur des
   membres, pointe en face du titre. */
.gr-l{flex:1 1 auto;min-width:0;padding-left:3px}
.gr>.akol{flex:none;align-self:stretch;width:.55em;height:auto}
.gr-m,.gr-x{margin:.12em 0}
.ec{display:inline-block;width:.75em}
.gr-x{text-indent:0}
/* Le groupe A POINTE EN HAUT -- l'arbre genealogique du folio 220 :
   les trois memes pieces, empilees au lieu d'etre rangees. La boite est
   dimensionnee par son contenu (inline-flex), donc l'accolade, etiree
   en travers, prend exactement la largeur des noms qu'elle coiffe ; les
   marges negatives lui rendent le leger debord du fac-simile (45,63 mm
   d'encre pour 42 mm de noms). */
.gr.grh{display:inline-flex;flex-direction:column;align-items:center;
 gap:1px;text-align:center;vertical-align:top}
.grh>.gr-l{padding-left:0;width:100%}
.grh>.akol{align-self:stretch;width:auto;height:.62em;margin:0 -.4em}
/* LE SEUIL ENTRE LES DEUX RENDUS. Il ne se choisit pas au juge : il se
   calcule. Le plus large tableau du volume -- « GRADI KOMPARALA », au
   folio 31 -- veut 430 px pour tenir sans qu'aucune case se brise, plus
   son retrait de 16 px. La colonne centrale en offre
   min(728, largeur - 480) - 116. Il y faut donc 1042 px de fenetre,
   au strict.
   Au strict, c'est-a-dire avec la fonte d'essai. Le lecteur peut en
   avoir une plus large -- la page va chercher Iowan, Palatino puis
   Georgia -- et un tableau qui deborde ne deborde pas un peu : les
   rangees se brisent, les termes tombent sous les termes, et l'accolade
   ne coiffe plus les rangs qu'elle vise puisque ces rangs ont double de
   hauteur. C'est exactement ce que le commanditaire a vu sur son iPad.
   Le seuil est donc pose a 1200 px, avec 150 px de marge : AUCUN iPad en
   mode paysage n'atteint cette largeur -- 1194 px pour le plus grand des
   11 pouces -- et tous recoivent donc le rendu en groupes, qui se plie a
   toute largeur. La grille reste ce qu'elle doit etre : un supplement
   d'ecran large, jamais un pis-aller. */
@media (max-width:1200px){.larja{display:none}.grupi{display:block}}
.kond{color:var(--sub);letter-spacing:.28em}
.pk{font-variant:small-caps}
b{font-weight:700}

/* --- La planche liminara. Le scan est une similigravure a couche
   alpha : l'encre en noir, le papier transparent. Une <img> deviendrait
   noire sur noir en mode sombre ; l'alpha sert donc de MASQUE sur un
   bloc colore.
   MAIS UNE PHOTOGRAPHIE N'EST PAS DE L'ENCRE. Un premier etat donnait
   au masque la couleur du texte, var(--enk) : le portrait suivait
   l'encre, et en mode sombre il paraissait EN NEGATIF — cheveux et
   veston clairs, visage sombre. Le principe etait bon pour un trait,
   faux pour une demi-teinte.
   La planche est donc traitee comme ce qu'elle est : une photographie
   POSEE SUR DU PAPIER. Le carton garde son fond clair et l'encre son
   noir dans les DEUX modes ; en mode sombre la planche se detache sur
   la page comme un tirage colle dans un livre. C'est la seule maniere
   de la garder positive. --- */
.fig{margin:.6em 0 2.6em;text-align:center;position:relative}
.karto{width:min(350px,76%);margin:0 auto;padding:15px 15px 12px;
 border-radius:3px;background:#fbfaf7;border:1px solid #e2ddd5}
@media(prefers-color-scheme:dark){.karto{border-color:#3a3a42;
 box-shadow:0 1px 10px rgba(0,0,0,.5)}}
/* La data: URI esas skribita NUR UN FOYO, en variablo : la du proprieti
   -- kun prefixo e sen ol -- duopligus 260 ko dil arkivo. */
.portreto{width:100%;aspect-ratio:__PORTRETO_RATIO__;margin:0 auto;
 background:#1a1a1a;
 --masko:url("__PORTRETO__");
 -webkit-mask-image:var(--masko);mask-image:var(--masko);
 -webkit-mask-size:contain;mask-size:contain;
 -webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;
 -webkit-mask-position:center;mask-position:center}
.legendo{margin-top:.9em;font-size:12.5px;color:var(--sub);
 font-family:system-ui,sans-serif;letter-spacing:.01em}
.legendo .pk{font-variant:small-caps;letter-spacing:.04em}

/* --- L'avis d'editeur. Entre crochets, au corps des notes : la page
   ne peut pas deplacer un texte du volume sans le dire. --- */
.avizo{margin:1.4em 0 .8em;padding:8px 12px;border-left:2px solid var(--lin);
 font-size:14px;color:var(--sub);text-indent:0;position:relative}
.avizo .edit{display:block;margin-top:.4em;font-family:system-ui,sans-serif;
 font-size:12.5px;font-style:normal}

/* --- La chenulo qua kopias la adreso dil sekciono. Sur komputoro ol
   restas nevidebla til ke la mueo pasas sur la titulo ; sur telefono
   ol esas sempre videbla, kun celo di 44 px. --- */
/* Ol stacas en la marjeno DEXTRA, quale la folio en la sinistra : tale
   ol prenas NULA spaco en la texto -- un chenulo en-lineala lasus
   truo de 21 px pos singla del 322 chefa vorti, mem kande ol es nevidebla,
   e la justifikuro montrus lu. `text-indent:0` esas necesa : un
   inline-block heredas la retreto dil alineo ed aplikas ol a su ipsa. */
.lig{color:var(--sub);text-decoration:none;line-height:0;text-indent:0;
 display:inline-block;padding:0 4px;
 position:absolute;right:-2em;top:.2em;
 opacity:0;transition:opacity .12s,color .12s}
.lig svg{width:13px;height:13px;display:block;
 stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;
 stroke-linejoin:round}
.lig:hover,.lig:focus-visible{color:var(--acc);opacity:1}
.tit>.lig{top:50%;transform:translateY(-50%)}
.tit:hover>.lig,.p:hover>.lig,.avizo:hover>.lig,.fig:hover>.lig,
.lig:focus-visible{opacity:1}
/* Ecran tactile : nulo pasas sur la titulo, do la chenulo restas
   sempre videbla, e sua celo mezuras 44 px sen chanjar la lineo-alteso
   -- la pseudo-elemento kreskas la celo, ne la desegno. */
@media (hover:none){
 .lig{opacity:.6}
 .lig::after{content:"";position:absolute;left:50%;top:50%;width:44px;
  height:44px;transform:translate(-50%,-50%)}
}
/* La konfirmo « Kopiita ». Ol montresas e efacesas ; ol ne movas nulo. */
#kopito{position:fixed;left:50%;bottom:26px;transform:translate(-50%,14px);
 background:var(--enk);color:var(--pap);border-radius:7px;padding:8px 14px;
 font:600 13px/1.3 system-ui,sans-serif;z-index:60;opacity:0;
 pointer-events:none;transition:opacity .18s,transform .18s;
 max-width:min(92vw,520px);text-align:center}
#kopito.ap{opacity:.94;transform:translate(-50%,0)}
#kopito.manu{pointer-events:auto;background:var(--pap);color:var(--enk);
 border:1px solid var(--acc);opacity:1}
#kopito input{width:min(72vw,380px);margin-top:6px;padding:5px 7px;font:inherit;
 font-weight:400;font-size:12px;border:1px solid var(--lin);border-radius:5px;
 background:var(--pap);color:var(--enk)}

/* --- La folio. Ol montresas en la marjeno kande ol komencas la alineo,
   e en la texto ipsa kande la pagino chanjas meze di alineo : la loko
   dil pagino-chanjo esas ipsa un informo dil fac-similo. Ol duktas al
   justa pagino dil PDF (pagino = folio + 2). --- */
.fol{font:600 11px/1 system-ui,sans-serif;color:var(--sub);text-decoration:none;
 border-bottom:1px dotted var(--lin);padding:1px 3px;border-radius:3px}
.fol:hover{color:var(--flag);border-color:var(--flag)}
.p>.fol:first-child,.tit>.fol:first-child,.cen>.fol:first-child,
.rangi>.fol:first-child,.sub2>.fol:first-child,.avizo>.fol:first-child,
.fig>.fol:first-child{position:absolute;left:-3.6em;top:.25em;
 border:0;text-indent:0}
.p>.fol:first-child+*,.p>.fol:first-child{text-indent:0}

/* --- La noti esas faldita. La apelo restas en la texto, klikebla ; la
   noto apertesas sub la alineo qua vokas ol. --- */
.apelo{color:var(--flag);text-decoration:none;font-size:.85em;vertical-align:.35em;
 cursor:pointer;padding:0 1px}
.apelo:hover{text-decoration:underline}
.noto{margin:-.3em 0 .8em 1.3em;padding:8px 12px;border-left:2px solid var(--lin);
 font-size:14px;color:var(--sub);text-align:justify;display:none}
.noto.ap{display:block}
.noto .nnum{font-weight:700;color:var(--acc)}

#rez{padding:20px 34px 120px;max-width:760px;margin:0 auto;display:none}
#rez .nombro{color:var(--sub);font-size:12.5px;margin:0 0 14px;font-family:system-ui,sans-serif}
#rez article{padding:11px 0;border-bottom:1px solid var(--lin);cursor:pointer}
#rez .kap{font-size:11.5px;color:var(--acc);font-family:system-ui,sans-serif;
 letter-spacing:.03em;margin-bottom:3px}
#rez .ext{margin:0}
mark{background:rgba(214,154,106,.34);color:inherit;border-radius:2px}
.brilo{animation:brilo 1.8s ease-out}
@keyframes brilo{from{background:rgba(214,154,106,.42)}to{background:transparent}}

/* --- Sur telefono, un sola panelo. La du altri divenas tiradili, e la
   baro restas. --- */
@media (max-width:900px){
 main{grid-template-columns:minmax(0,1fr)}
 .tir{display:block}
 nav,aside{position:fixed;top:0;height:100vh;width:min(80vw,320px);z-index:30;
  background:var(--pap);padding-top:18px;transform:translateX(-105%);
  transition:transform .18s ease;box-shadow:0 0 24px rgba(0,0,0,.18)}
 aside{right:0;left:auto;transform:translateX(105%)}
 nav.ap,aside.ap{transform:translateX(0)}
 /* Une SOLA rangeo d'utensili sur telefono : la baza flex-bazo di
    260 px pulsus la kampo sub la butono. */
 input[type=search]{flex:1 1 120px;min-width:0}
 /* Le passage des colonnes aux groupes ne se fait plus ici : il se fait
    a 1000 px, un cran plus haut. */
 /* Un sol tirado sur telefono : la chefa vorti dil chapitro nuna montresas
    en la tabelo dil materio ipsa, sub la chapitro. */
 aside{display:none}
 #vednav{display:block;margin:2px 0 6px 12px;border-left:2px solid var(--lin);
  padding-left:8px}
 #kont{padding:20px 18px 120px}
 .tit,.p,.rangi,.cen,.sub2,.noto,.avizo,.fig{
  scroll-margin-top:calc(var(--kapo,215px) + 12px)}
 .p>.fol:first-child,.tit>.fol:first-child,.cen>.fol:first-child,
 .rangi>.fol:first-child,.sub2>.fol:first-child,.avizo>.fol:first-child,
 .fig>.fol:first-child{position:static;border-bottom:1px dotted var(--lin);
  margin-right:.4em}
 .karto{width:min(280px,72%)}
 /* Sur telefono ne restas marjeno dextra : la chenulo rivenas en la
    fluo, quale la folio. Ol es sempre videbla, do la spaco quan ol
    prenas es voluta e ne surprenas la lekto. */
 .lig{position:static;transform:none;vertical-align:-2px;padding:0 5px}
 .tit>.lig{transform:none}
 .lig svg{display:inline-block}
 #vualo{position:fixed;inset:0;background:rgba(0,0,0,.34);z-index:25;display:none}
 #vualo.ap{display:block}
 .tab{font-size:.9em}
}
</style>
<header>
<div class="tito">
<h1>Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido</h1>
<a class="dl" href="__PDF__" download title="Deskargar la gramatiko (PDF)">
<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12"/><path d="M7 11l5 5 5-5"/><path d="M4 20h16"/></svg><span>Deskargar</span></a>
</div>
<div class="sub">L. de Beaufront &middot; Esch-Alzette, Meier-Heucke, 1925 &middot; __SUB__</div>
<div class="bar">
 <button class="tir" id="tirL" aria-label="Tabelo di la materio">&#9776; Materio</button>
 <input type="search" id="q" placeholder="Serchez en la tota libro&hellip;" autocomplete="off">
</div>
</header>
<main>
<nav id="nav">__NAV__<div id="vednav"></div></nav>
<div><div id="kont">__KONT__</div><div id="rez"></div></div>
<aside id="vede"><div class="kapo">Chefa vorti dil chapitro</div><div id="vedlist"></div></aside>
</main>
<div id="vualo"></div>
<div id="kopito" role="status" aria-live="polite"></div>
<script>
var VED=__VED__;            // chapitro -> [id, chefa vorto]
/* Hauteur reelle de l'en-tete collant, deposee dans --kapo. On la
   remesure au redimensionnement ET apres le chargement des fontes :
   une fonte a serif plus haute que la fonte de secours peut faire
   passer le titre sur une ligne de plus. */
function mezurKapo(){var h=document.querySelector('header');
 if(h)document.documentElement.style.setProperty('--kapo',h.offsetHeight+'px');}
mezurKapo();
/* A l'ouverture d'une URL a ancre, le navigateur defile AVANT que le
   script ait mesure l'en-tete : il emploie la valeur de secours, et la
   section visee se loge sous la barre. On refait donc le defilement une
   fois la mesure prise — et encore apres les fontes, qui peuvent
   changer la hauteur du titre. */
/* Une ancre qui ne resout plus doit etre rattrapee, non perdue. Six
   adresses ont change le jour ou la detection des chefa vorti a ete
   corrigee : « ...-vokali-e » est devenu « ...-vokali-e-o », et les
   entrees nouvelles ont pris le rang sans suffixe en repoussant celles
   qui l'occupaient. Un lien copie avant ce jour-la ne trouvait plus sa
   cible, et la page s'ouvrait en tete SANS RIEN DIRE.
   On ne fige pas une table des anciennes adresses : elle vieillirait a
   son tour, et il faudrait la tenir a chaque correction. On cherche la
   cible par PARENTE — l'ancre allongee d'un membre (e -> e-o), ou le
   meme nom a un suffixe de rang pres. Ce qui n'a pas de parent laisse
   la page ou elle est, comme avant. */
function trovAncro(h){
 var id=h.slice(1).replace(/^#/,''), el=null, i, x;
 try{el=document.getElementById(id)}catch(e){}
 if(el)return el;
 var t=[].slice.call(document.querySelectorAll('[id]'));
 for(i=0;i<t.length;i++){x=t[i].id;
  if(x.indexOf(id+'-')===0&&!/^\d+$/.test(x.slice(id.length+1)))return t[i];}
 var nu=id.replace(/-\d+$/,'');
 for(i=0;i<t.length;i++){x=t[i].id;
  if(x===nu||x.replace(/-\d+$/,'')===nu)return t[i];}
 return null;}
function viziAncro(){var h=location.hash;
 if(h.length<2)return;
 var el=trovAncro(h);
 if(el)el.scrollIntoView();}
mezurKapo(); viziAncro();
addEventListener('load',function(){mezurKapo();viziAncro();});
addEventListener('resize',function(){var av=margoObs();mezurKapo();
 /* Si la hauteur de l'en-tete a change, la bande de l'observateur est
    perimee : rootMargin ne se modifie pas apres coup, il faut le
    refaire. */
 if(margoObs()!==av&&window.refarObservilo)window.refarObservilo();});
addEventListener('orientationchange',mezurKapo);
if(document.fonts&&document.fonts.ready)
 document.fonts.ready.then(function(){mezurKapo();viziAncro();});
var kont=document.getElementById('kont'), rez=document.getElementById('rez');

/* --- La noti. Un sola askoltilo por la tota volumo : 700 apeli ne
   meritas 700 askoltili. --- */
document.addEventListener('click',function(e){
 var a=e.target.closest('.apelo'); if(!a) return;
 e.preventDefault();
 var n=document.getElementById(a.dataset.nt); if(!n) return;
 n.classList.toggle('ap');
 if(n.classList.contains('ap')){
   var r=n.getBoundingClientRect();
   if(r.bottom>innerHeight) n.scrollIntoView({block:'nearest',behavior:'smooth'});
 }
});

/* --- La chenulo : ol kopias l'adreso absoluta dil sekciono.
   Tri gradi, nam la pagino apertesas ofte per file:// , ube la
   Clipboard API mankas o refuzas :
     1. navigator.clipboard.writeText ;
     2. kampo provizora + document.execCommand('copy') ;
     3. l'adreso montresas, selektita, por kopio manuala. --- */
var kopito=document.getElementById('kopito'), horlojo=null;
function diro(txt,manu){
 clearTimeout(horlojo);
 kopito.classList.toggle('manu',!!manu);
 kopito.textContent=txt;
 kopito.classList.add('ap');
 if(!manu) horlojo=setTimeout(function(){kopito.classList.remove('ap')},1500);
 return kopito;
}
function manuale(url){
 var b=diro('Kopiez la ligilo :',true);
 var i=document.createElement('input');
 i.readOnly=true; i.value=url;
 b.appendChild(i); i.focus(); i.select();
 /* Ol restas til ke on klikas altre : sen to l'adreso desaparus ante
    ke on povus kopiar ol. */
 /* Ol klozesas ye la unesma kliko EXTERE : kliko sur la kampo ipsa
    devas povar selektar la texto. */
 setTimeout(function(){
  document.addEventListener('click',function f(ev){
   if(kopito.contains(ev.target)) return;
   kopito.classList.remove('ap','manu');
   document.removeEventListener('click',f)})},0);
}
function repli(url){
 var t=document.createElement('textarea');
 t.value=url; t.setAttribute('readonly','');
 t.style.cssText='position:fixed;top:0;left:0;width:1px;height:1px;opacity:0';
 document.body.appendChild(t);
 t.select(); t.setSelectionRange(0,url.length);
 var ok=false; try{ok=document.execCommand('copy')}catch(e){ok=false}
 document.body.removeChild(t);
 if(ok) diro('Kopiita'); else manuale(url);
}
document.addEventListener('click',function(e){
 var a=e.target.closest('.lig'); if(!a) return;
 e.preventDefault();
 /* L'adreso ABSOLUTA : a.href ja esas solvita dal navigilo, anke sub
    file:// . On ne rikonstruktas ol de location, qua povus portar altra
    ancero. */
 var url=a.href;
 if(navigator.clipboard&&navigator.clipboard.writeText){
  navigator.clipboard.writeText(url).then(function(){diro('Kopiita')},
                                          function(){repli(url)});
 } else repli(url);
});

/* --- La du tiradili sur telefono. --- */
var nav=document.getElementById('nav'), vede=document.getElementById('vede'),
    vualo=document.getElementById('vualo');
function klozar(){nav.classList.remove('ap');vualo.classList.remove('ap')}
document.getElementById('tirL').onclick=function(){
 var o=nav.classList.contains('ap');
 if(o) klozar(); else {nav.classList.add('ap');vualo.classList.add('ap')}};
vualo.onclick=klozar;
/* Delegita askoltilo : la chefa vorti dil tabelo di materio kreesas e
   rikreesas ye singla chanjo di chapitro, do li ne povus recevar sua
   propra askoltilo. */
nav.addEventListener('click',function(e){
 if(e.target.closest('a')&&innerWidth<=900) klozar()});

/* --- Quala chapitro on lektas. IntersectionObserver, ne skrol-askoltilo :
   ol ne rulas kodexo che singla pixelo dil skrolo. --- */
var blokii=[].slice.call(kont.querySelectorAll('[data-ch]'));
var navA={}, chapNun=null;
document.querySelectorAll('nav a[data-ch]').forEach(function(a){navA[a.dataset.ch]=a});
var vedNun='';
function marqueVed(vd){
 if(vd) vedNun=vd;
 document.querySelectorAll('#vedlist a,#vednav a').forEach(function(a){
   a.classList.toggle('nun',a.getAttribute('href')==='#'+vedNun)});
}
function chapitro(c){
 if(c===chapNun) return; chapNun=c;
 for(var k in navA) navA[k].classList.toggle('nun',k===c);
 var a=navA[c]; if(a) a.scrollIntoView({block:'nearest'});
 var v=VED[c]||[];
 var liens=v.map(function(x){
   return '<a href="#'+x[0]+'" title="'+x[2]+'">'+x[1]+'</a>'}).join('');
 document.getElementById('vedlist').innerHTML=liens||
   '<div style="color:var(--sub)">(nula chefa vorto en ca chapitro)</div>';
 /* Sur telefono la chefa vorti sequas sua chapitro en la tabelo dil materio :
    la listo transportesas sub la ligilo dil chapitro nuna. */
 var nv=document.getElementById('vednav');
 nv.innerHTML=liens;
 if(a) a.insertAdjacentElement('afterend',nv);
 /* La listo jus rifacesis : la marko dil nuna chefa vorto perdesis kun ol,
    e nula nova intersekto venos ripozar ol. On ripozas ol quik. */
 marqueVed(null);
}
var vidata={};
/* La bande de decision de l'observateur commencait a -100px : encore une
   hauteur d'en-tete supposee. Sur iPad, ou l'en-tete mesure 133 px, elle
   s'ouvrait AU-DESSUS de la barre, si bien qu'un bloc long encore
   visible en haut — « -eg- », haut de 442 px — l'emportait sur celui
   qu'on venait d'atteindre. Le volet designait donc l'entree du dessus.
   La bande suit maintenant la hauteur mesuree, et l'observateur est
   refait quand elle change. */
function margoObs(){
 var h=parseInt(getComputedStyle(document.documentElement)
        .getPropertyValue('--kapo'),10)||100;
 return (-(h+14))+'px 0px -55% 0px';}
function fObs(es){
 es.forEach(function(e){if(e.isIntersecting)vidata[e.target.dataset.i]=e.target;
                        else delete vidata[e.target.dataset.i]});
 var ks=Object.keys(vidata).map(Number).sort(function(a,b){return a-b});
 if(!ks.length) return;
 /* La maxim supera bloko vidata -- ma ne un rando de bloko: pos salto ad
    ancero, la bloko precedanta ofte ankore montras dek pixeli sub la
    baro, e la lekto semblus esar ankore che ol. */
 var top=vidata[ks[0]];
 for(var z=0;z<ks.length;z++){
  if(vidata[ks[z]].getBoundingClientRect().bottom>130){top=vidata[ks[z]];break}
 }
 chapitro(top.dataset.ch);
 marqueVed(top.dataset.vd||nunVed(ks[0]));
}
var obs=new IntersectionObserver(fObs,{rootMargin:margoObs()});
function nunVed(i){for(var k=i;k>=0;k--){var b=blokii[k];
  if(b&&b.dataset.vd) return b.dataset.vd;} return ''}
blokii.forEach(function(b,i){b.dataset.i=i;obs.observe(b)});
/* Refaire l'observateur avec la bande a jour : rootMargin est fige a la
   creation. Appele quand la hauteur de l'en-tete change. */
window.refarObservilo=function(){
 obs.disconnect();
 obs=new IntersectionObserver(fObs,{rootMargin:margoObs()});
 blokii.forEach(function(b){obs.observe(b)});};
chapitro(blokii.length?blokii[0].dataset.ch:null);

/* --- La sercho. La indexo konstruktesas ye la kargo de la DOM ipsa :
   la texto ja esas en la pagino, ol ne bezonas duesma kopio en JSON --
   to duopligus la pezo dil arkivo por nulo. Sercho lineala sur 700 000
   signi kustas kelka milisekundi. --- */
var IDX=null;
function indexo(){
 if(IDX) return IDX; IDX=[];
 kont.querySelectorAll('.p,.tit,.cen,.rangi,.noto,.sub2,.fer,.avizo,.legendo').forEach(function(el){
  /* La folio-numeri ne apartenas al texto dil volumo : sen ca kopio la
     extrakti komencus per « 12Ma, se la renkontro... », e sercho pri
     « 12ma » trovus lo quo nulatempe skribesis. */
  var k=el.cloneNode(true);
  k.querySelectorAll('.fol').forEach(function(f){f.remove()});
  /* Un tabelo kun akoladi esas skribita du foyi en la pagino ; sen ca
     efaco la texto duopligesus en la indexo e en la extrakti. */
  k.querySelectorAll('.grupi:not(.sola)').forEach(function(g){g.remove()});
  var t=k.textContent.replace(/\\s+/g,' ').trim();
  if(t) IDX.push([el,t,t.toLowerCase()]);
 });
 return IDX;
}
function nomChap(el){
 var b=el.closest('[data-ch]')||el.previousElementSibling;
 var c=b&&b.dataset?b.dataset.ch:null;
 var n=c&&navA[c]?navA[c].textContent:'';
 return el.classList.contains('noto')?n+' \u00b7 noto':n;
}
var minu=null;
document.getElementById('q').addEventListener('input',function(e){
 clearTimeout(minu); var v=e.target.value.trim();
 minu=setTimeout(function(){serchez(v)},130);
});
function serchez(v){
 /* display='' ne suffit pas : ol nur efacas la stilo en-lineala, e la
    folio-stilo #rez{display:none} riprenas la manuo. */
 if(v.length<2){rez.style.display='none';kont.style.display='';return}
 var q=v.toLowerCase(), I=indexo(), out=[], n=0;
 for(var k=0;k<I.length;k++){
  var p=I[k][2].indexOf(q); if(p<0) continue; n++;
  if(out.length<300){
   var t=I[k][1], a=Math.max(0,p-70), b=Math.min(t.length,p+v.length+110);
   out.push('<article data-k="'+k+'"><div class="kap">'+esc(nomChap(I[k][0]))
    +'</div><p class="ext">'+(a?'&hellip;':'')+esc(t.slice(a,p))+'<mark>'
    +esc(t.substr(p,v.length))+'</mark>'+esc(t.slice(p+v.length,b))
    +(b<t.length?'&hellip;':'')+'</p></article>');
  }
 }
 rez.innerHTML='<p class="nombro">'+(n?n+' trovaji'+(n>300?' (montresas la 300 unesma)':'')
  :'Nula trovajo')+'</p>'+out.join('');
 rez.style.display='block';kont.style.display='none';
 scrollTo(0,0);
}
function esc(s){return s.replace(/[&<>]/g,function(c){
 return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
rez.addEventListener('click',function(e){
 var a=e.target.closest('article'); if(!a) return;
 var el=IDX[+a.dataset.k][0];
 rez.style.display='none';kont.style.display='';
 if(el.classList.contains('noto')){el.classList.add('ap');}
 el.scrollIntoView({block:'center'});
 el.classList.remove('brilo');void el.offsetWidth;el.classList.add('brilo');
});
/* Un ligilo direta a noto (gramatiko.html#nt36-1) devas apertar ol :
   hashchange ne pafas ye la kargo dil pagino, do on vokas ol du foyi. */
function perAncero(){
 var el=document.getElementById(location.hash.slice(1));
 if(!el) return;
 if(el.classList.contains('noto')){el.classList.add('ap');
  el.scrollIntoView({block:'center'});}
 /* Salto ad ancero ne sempre chanjas quo intersekas : on marfas
    direte la chapitro e la chefa vorto vizata. */
 if(el.dataset.ch) chapitro(el.dataset.ch);
 if(el.dataset.vd) marqueVed(el.dataset.vd);
}
addEventListener('hashchange',perAncero);
perAncero();
</script>
"""


# Le bouton en chaine. C'est un VRAI lien : sans JavaScript il mene
# quand meme a l'ancre, et le menu contextuel du navigateur y offre
# « copier l'adresse du lien ». Le clic, lui, est intercepte et copie.
CHAINON = ('<a class="lig" href="#%s" data-lig="%s" '
           'aria-label="Kopiar la ligilo di %s" title="Kopiar la ligilo">'
           '<svg viewBox="0 0 24 24" aria-hidden="true">'
           '<path d="M10 13.5a4 4 0 0 0 5.7.3l3-3a4 4 0 0 0-5.7-5.7l-1.7 1.7"/>'
           '<path d="M14 10.5a4 4 0 0 0-5.7-.3l-3 3a4 4 0 0 0 5.7 5.7l1.7-1.7"/>'
           '</svg></a>')


def lien_ancre(ident, quoi):
    return CHAINON % (ident, ident, echappe((quoi or '').strip(' .,;:')))


def bloc_html(b, indice_chap, notes):
    frags = []
    for k, (f, fo, h) in enumerate(b.frags):
        if k == 0 or b.frags[k - 1][1] != fo:
            lien = '<a class="fol" href="%s#page=%d" title="Folio %d en la PDF">%d</a>' \
                   % (PDF, fo + PDF_DECALAGE, fo, fo)
            # Aucune espace ajoutee autour du folio : elle est deja dans
            # le texte quand le fac-simile en a une, et il ne faut pas
            # d'espace du tout quand la page coupe un mot (folio 14-15,
            # « be- / zonus »).
            frags.append(lien + h)
        else:
            frags.append(h)
    # Les fragments se joignent SANS rien : l'espace de fin de ligne
    # est deja dans le texte (\nl), et son absence l'est aussi (\cc).
    corps = ''.join(frags).strip()
    cls = {'p': 'p', 'tit': 'tit', 'sub': 'sub2', 'cen': 'cen', 'fer': 'fer',
           'orn': 'orn', 'rango': 'rangi', 'tab': 'rangi',
           'avizo': 'avizo', 'fig': 'fig'}[b.genre]
    attrs = ' data-ch="%s"' % indice_chap if indice_chap is not None else ''
    ident = ''
    if b.ved:
        attrs += ' data-vd="%s"' % b.ident
        ident = ' id="%s"' % b.ident
    if b.genre in ('tit', 'fig'):
        ident = ' id="%s"' % b.ident
    # Le bouton en chaine : a droite du titre de chapitre, contre la
    # vedette qu'il adresse. Il ne parait qu'ou il y a une ancre --
    # ailleurs il n'aurait rien a copier.
    if b.genre == 'tit':
        corps += lien_ancre(b.ident, texte_nu(corps))
    elif b.genre == 'fig':
        corps += lien_ancre(b.ident, PORTRAIT_TITRE)
    elif b.ved:
        # Contre la vedette, non en bout d'alinea : la vedette EST le
        # titre de l'entree, et c'est elle que l'adresse designe. La
        # coupe se relit par la meme fonction que la detection : posee
        # au premier `</b>` venu, elle tombait entre le « e » et le
        # « o » d'une vedette double.
        coupe = vedette(corps)[1]
        if coupe < 0:
            coupe = corps.find('</b>')
            coupe = coupe + 4 if coupe >= 0 else -1
        if coupe >= 0:
            corps = corps[:coupe] + lien_ancre(b.ident, b.ved) + corps[coupe:]
    if b.avis:
        corps += ('<span class="edit">[&#8239;%s&#8239;]</span>'
                  % echappe(b.avis))
    out = ['<div class="%s"%s%s>%s</div>' % (cls, ident, attrs, corps)]
    for cle in b.noti:
        nt = notes[cle]
        # Une note dont l'appel manque au fac-simile est posee sous
        # l'alinea qui la nomme ; on le dit plutot que de le taire.
        marque = ('<span class="nfl">apelo ne trovita en la pagino</span>'
                  if nt.get('orfa') else '')
        corps = ''.join('<p>%s</p>' % t for t in nt['paras'])
        out.append('<div class="noto" id="%s">%s%s</div>'
                   % (nt['id'], corps, marque))
    return ''.join(out)


# ------------------------------------------------------------------
# 6 bis. LES IDENTIFIANTS D'ANCRE
# ------------------------------------------------------------------
# Une ancre est une ADRESSE : elle est citee, mise en signet, collee
# dans une note de bas de page. Elle doit donc survivre a la
# recomposition du volume -- et c'est pourquoi rien de POSITIONNEL n'y
# entre. Ni le rang de l'alinea, ni l'ordre du fichier, ni le numero du
# chapitre : inserer un paragraphe au folio 12 les decalerait tous.
#
# LA REGLE, en trois lignes :
#   1. chapitre           -> ardoise(titre du chapitre)
#   2. vedette            -> ardoise(titre du chapitre) + '-' + ardoise(vedette)
#   3. collision          -> suffixe '-2', '-3'... dans l'ordre du texte.
#
# Un HACHAGE ferait aussi bien contre les collisions, mais il donnerait
# une adresse illisible et, surtout, il changerait entierement au
# moindre caractere corrige. Le suffixe numerique, lui, ne bouge que
# pour les entrees qui portent VRAIMENT le meme nom.
ARDOISE_LONGUEUR = 40      # au plus, coupe sur un mot entier

# Ce que la translitteration doit rendre avant de tomber sur la regle
# generale. Le volume est en ido, qui n'a pas de diacritique ; ces
# equivalences sont la pour le jour ou le releve en portera.
ARDOISE_LETTRES = {
    'æ': 'ae', 'œ': 'oe', 'ß': 'ss', 'ø': 'o',
    'đ': 'd', 'ł': 'l', 'þ': 'th', 'ð': 'd',
}


def ardoise(t):
    """Le slug d'un titre ou d'une vedette : SON TEXTE, et rien d'autre.

    Minuscules, diacritiques deposes, tout ce qui n'est pas [a-z0-9]
    rendu en tiret, tirets fusionnes et rognes aux deux bouts. La
    coupure se fait sur un mot entier, pour que l'adresse reste lisible
    -- et jamais au milieu d'un mot, ce qui la rendrait indevinable.
    """
    import unicodedata
    t = unicodedata.normalize('NFKD', t or '')
    t = ''.join(ARDOISE_LETTRES.get(c, c) for c in t)
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
    if len(t) > ARDOISE_LONGUEUR:
        court = t[:ARDOISE_LONGUEUR].rsplit('-', 1)[0]
        # Un premier mot plus long que la mesure : on coupe net, il n'y
        # a pas de bord de mot ou s'arreter.
        t = court or t[:ARDOISE_LONGUEUR]
    return t.strip('-')


class Ancres(object):
    """Le registre des identifiants, et le seul endroit qui les donne.

    Il tient la trace de ce qui est deja pris et attribue le suffixe des
    homonymes DANS L'ORDRE DU TEXTE : la premiere « Til » de PREPOZICIONI
    est `prepozicioni-til`, la deuxieme `prepozicioni-til-2`. Deux
    executions sur le meme releve rendent donc les memes adresses.
    """

    def __init__(self):
        self.pris = {}        # identifiant -> ce qu'il designe
        self.doubles = []     # collisions vues, pour le compte rendu

    def reserve(self, ident, quoi):
        """Un identifiant impose du dehors (les notes). Sans suffixe :
        s'il se repetait, c'est le controle final qui doit le dire."""
        if ident in self.pris:
            self.doubles.append((ident, quoi, self.pris[ident]))
        self.pris[ident] = quoi
        return ident

    def neuf(self, base, quoi, defaut='sekciono'):
        base = base or defaut
        ident = base
        k = 1
        while ident in self.pris:
            k += 1
            ident = '%s-%d' % (base, k)
        if k > 1:
            self.doubles.append((base, quoi, self.pris[base]))
        self.pris[ident] = quoi
        return ident


# Ce qu'un fragment d'URL admet sans encodage (RFC 3986) : les
# caracteres non reserves, les sous-delimiteurs, « : » et « @ ». Les
# notes du volume portent un `*` -- c'est laid, mais c'est licite, et
# l'astérisque est la marque d'appel du fac-simile lui-meme.
FRAGMENT_LICITE = re.compile(r"[A-Za-z0-9._~!$&'()*+,;=:@-]+\Z")


def controle_ancres(doc):
    """Verifier, SUR LA PAGE ECRITE, qu'aucun `id` ne se repete.

    Le registre ne peut garantir que ce qui passe par lui ; le controle,
    lui, relit le document produit -- c'est la seule preuve qui vaille,
    puisque c'est le document qui porte les adresses.

    Rend (nombre d'identifiants, repetitions, identifiants qu'une URL
    devrait encoder). Seules les REPETITIONS sont une faute : deux
    sections a la meme adresse, c'est une adresse qui ne designe plus.
    """
    idents = re.findall(r'\sid="([^"]*)"', doc)
    vus, doubles, gauches = set(), [], []
    for i in idents:
        if i in vus:
            doubles.append(i)
        vus.add(i)
    for i in sorted(vus):
        if not i or not FRAGMENT_LICITE.match(i):
            gauches.append(i)
    return len(idents), sorted(set(doubles)), gauches


# ------------------------------------------------------------------
# 6 ter. L'ADDENDUM DU FOLIO 224
# ------------------------------------------------------------------
def reintegre_addendum(rel):
    """Remettre `tra` et `trans` a la place que le volume leur donne.

    Le folio 224 ne porte qu'une phrase -- « Hike ni pozas la du
    prepozicioni tra e trans omisita pos til p. 82 » -- et les deux
    articles annonces. Ce n'est pas une section : c'est un rattrapage
    d'imprimeur, et il dit lui-meme ou son contenu appartient. La page
    de lecture l'y porte, sans rien retrancher : les deux articles
    gardent le folio 224 et son renvoi au PDF, et la phrase de
    l'original les precede, suivie de l'avis d'editeur.

    Rien n'est en dur : la cible se retrouve par le CONTENU -- le
    chapitre qui porte le titre voulu, la derniere entree qui porte la
    vedette voulue. Si le volume est recompose et que le folio 224
    disparait, la fonction ne trouve rien a deplacer et ne fait rien.

    Rend (nombre de blocs deplaces, texte reste au feuillet, cible).
    """
    a_deplacer = [b for b in rel.blocs
                  if b.frags and all(f == ADDENDUM_FEUILLET
                                     for f, _, _ in b.frags)]
    if not a_deplacer:
        return 0, 0, None
    # Aucun de ces blocs ne doit tenir une part d'une autre page : sinon
    # le deplacement emporterait du texte qui n'est pas a lui.
    reste = sum(1 for b in rel.blocs for f, _, _ in b.frags
                if f == ADDENDUM_FEUILLET and b not in a_deplacer)

    # La cible : dans le chapitre voulu, la DERNIERE entree de la
    # vedette voulue -- l'article `til` court sur trois alineas, et
    # c'est apres le troisieme que le volume renvoie.
    debut = None
    for k, b in enumerate(rel.blocs):
        if b.genre == 'tit' and texte_nu(b.frags[0][2]) == ADDENDUM_CHAPITRE:
            debut = k
            break
    if debut is None:
        return 0, reste, None
    fin = len(rel.blocs)
    for k in range(debut + 1, len(rel.blocs)):
        if any(c['bloc'] is rel.blocs[k] for c in rel.chapitres):
            fin = k
            break
    cible = None
    for k in range(debut, fin):
        if rel.blocs[k].ved == ADDENDUM_VEDETTE:
            cible = rel.blocs[k]
    if cible is None:
        return 0, reste, None

    # La phrase de l'original ouvre le groupe deplace : elle n'est pas
    # un article, elle les annonce. On lui attache l'avis d'editeur.
    a_deplacer[0].genre = 'avizo'
    a_deplacer[0].avis = ADDENDUM_AVIS

    # On retire d'abord, on insere ensuite : l'indice de la cible se
    # relit APRES le retrait, sans quoi il designerait un autre bloc.
    for b in a_deplacer:
        rel.blocs.remove(b)
    place = rel.blocs.index(cible) + 1
    rel.blocs[place:place] = a_deplacer
    return len(a_deplacer), reste, texte_nu(cible.frags[0][2])[:40]


def ecrire(rel, parties, stats):
    # LES IDENTIFIANTS. Rien de positionnel : le titre du chapitre pour
    # le chapitre, le titre du chapitre et la vedette pour la vedette.
    # Le registre attribue les suffixes des homonymes, dans l'ordre du
    # texte. Les notes reservent d'abord leur identifiant, pour qu'une
    # ardoise ne puisse pas venir le leur prendre.
    ancres = Ancres()
    for nt in rel.notes.values():
        ancres.reserve(nt['id'], 'noto')
    for ch in rel.chapitres:
        ch['id'] = ancres.neuf(ardoise(ch['titre']), ch['titre'], 'chapitro')
        ch['bloc'].ident = ch['id']
    ident_chap = [ch['id'] for ch in rel.chapitres]

    ved_par_chap = {}
    morceaux = []
    for b in rel.blocs:
        cid = ident_chap[b.chap] if b.chap is not None else None
        if b.ved:
            base = ardoise(b.ved)
            b.ident = ancres.neuf('%s-%s' % (cid, base) if cid else base,
                                  b.ved, 'chefa vorto')
            # L'etiquette du volet est TRONQUEE, non filtree : le volume
            # ouvre aussi des alineas par une phrase entiere en gras
            # (des exemples), et ce sont des sous-entrees comme les
            # autres -- simplement leur vedette ne tient pas dans une
            # colonne de 230 px.
            lab = b.ved.rstrip(' .,;:')
            court = lab if len(lab) <= 42 else lab[:41].rsplit(' ', 1)[0] + '\u2026'
            ved_par_chap.setdefault(cid, []).append(
                [b.ident, echappe(court), echappe(lab)])
        morceaux.append(bloc_html(b, cid, rel.notes))

    nav = []
    for p in parties:
        nav.append('<div class="parto">%s</div>' % echappe(p['label']))
        for ch in p['chapitres']:
            nav.append('<a href="#%s" data-ch="%s">%s</a>'
                       % (ch['id'], ch['id'], echappe(ch['titre'])))
    import json
    sub = '%d chapitri &middot; %d alinei &middot; %d noti' % (
        stats['chapitres'], stats['alineas'], stats['notes'])
    uri, larg, haut, poids = stats['portreto']
    doc = (GABARIT.replace('__NAV__', ''.join(nav))
           .replace('__KONT__', ''.join(morceaux))
           .replace('__VED__', json.dumps(ved_par_chap, ensure_ascii=False))
           .replace('__SUB__', sub)
           .replace('__PORTRETO__', uri)
           .replace('__PORTRETO_RATIO__', '%d / %d' % (larg, haut))
           .replace('__PDF__', PDF))
    with open(SORTIE, 'w', encoding='utf-8') as f:
        f.write(doc)
    return doc, ancres


# ------------------------------------------------------------------
# 8. MARCHE
# ------------------------------------------------------------------
def main():
    rel = Releve()
    # Premiere passe : le folio de chaque feuillet, TOUTES pages
    # confondues -- y compris celles que la page de lecture ne reprend
    # pas, qui portent des folios imprimes bien utiles a l'interpolation.
    brut = []
    for nom in FICHIERS:
        s = sans_commentaires(open(os.path.join(CONTENU, nom),
                                   encoding='utf-8').read())
        for m in re.finditer(r'\\begin\{VUpage\}(\[[^\]]*\])?\{([^}]*)\}', s):
            feuillet = int((m.group(1) or '[0]')[1:-1] or 0)
            fo = m.group(2).strip()
            brut.append((feuillet, int(fo) if fo else None))
    rel.folios = table_folios(brut)

    for nom in FICHIERS:
        s = sans_commentaires(open(os.path.join(CONTENU, nom),
                                   encoding='utf-8').read())
        for m in re.finditer(r'\\begin\{VUpage\}(\[[^\]]*\])?\{([^}]*)\}',
                             s):
            feuillet = int((m.group(1) or '[0]')[1:-1] or 0)
            fin = s.index('\\end{VUpage}', m.end())
            if not (FEUILLET_PREMIER <= feuillet <= FEUILLET_DERNIER):
                continue
            rel.page(feuillet, m.group(2), s[m.end():fin])
    rel.ferme()

    orphelines = rattache_notes(rel)

    # L'addendum du folio 224, remis a la place que le volume lui donne.
    deplaces, reste224, cible = reintegre_addendum(rel)

    # LE PORTRAIT. Il ouvre la page, avant la KONSTATO, et compte comme
    # un chapitre pour la table des matieres -- mais son bloc n'est pas
    # un titre : c'est la planche elle-meme, avec sa legende.
    portreto = masque_portrait()
    # La planche est au feuillet 7, la page de titre, avec la legende
    # que voici -- le folio en marge y renvoie. Le CHAPITRE, lui, est
    # date du premier feuillet lu : c'est par le feuillet que la
    # structure range les chapitres en parties.
    fig = Bloc('fig', [(PORTRAIT_FEUILLET, rel.folios[PORTRAIT_FEUILLET],
                        '<div class="karto"><div class="portreto" role="img" '
                        'aria-label="%s"></div></div>'
                        '<div class="legendo">%s</div>'
                        % (texte_nu(LEGENDE), LEGENDE))])
    rel.blocs.insert(0, fig)
    rel.chapitres.insert(0, {'titre': PORTRAIT_TITRE, 'bloc': fig,
                             'feuillet': FEUILLET_PREMIER,
                             'folio': rel.folios[FEUILLET_PREMIER]})

    # rattacher chaque bloc a son chapitre. Le bloc qui ouvre un
    # chapitre n'est pas forcement un titre -- le portrait n'en est pas
    # un ; c'est d'etre inscrit au releve des chapitres qui compte.
    tetes = {id(c['bloc']): i for i, c in enumerate(rel.chapitres)}
    k = -1
    for b in rel.blocs:
        if id(b) in tetes:
            k = tetes[id(b)]
        b.chap = k if k >= 0 else None
    parties = structure(rel)

    stats = {
        'pages': len(rel.pages),
        'chapitres': len(rel.chapitres),
        'alineas': sum(1 for b in rel.blocs if b.genre == 'p'),
        'notes': len(rel.notes),
        'notes_appel': sum(1 for n in rel.notes.values()
                           if n['bloc'] is not None and not n.get('orfa')
                           and not n.get('renvoi')),
        'notes_renvoi': sum(1 for n in rel.notes.values() if n.get('renvoi')),
        'orphelines': len(orphelines),
        'vedettes': sum(1 for b in rel.blocs if b.ved),
        'tableaux': sum(1 for b in rel.blocs if b.genre == 'tab'),
        'akoladi': sum(1 for b in rel.blocs if b.genre == 'tab'
                       and 'class="grupi' in b.frags[0][2]),
        'rangs': sum(1 for b in rel.blocs if b.genre == 'rango'),
        # Le second rendu d'un tableau a accolades n'est pas du texte de
        # plus : on ne le compte qu'une fois.
        # Le second rendu d'un tableau a accolades -- toujours en queue
        # du fragment -- n'est pas du texte de plus : on ne compte qu'une
        # fois ce que la page dit deux fois.
        'signes': sum(len(texte_nu(re.sub(r'<div class="grupi">.*$', '', h,
                                          flags=re.S)))
                      for b in rel.blocs for _, _, h in b.frags),
        'portreto': portreto,
        'deplaces': deplaces,
        'reste224': reste224,
        'cible224': cible,
    }
    print('pages lues          %5d' % stats['pages'])
    print('chapitres           %5d' % stats['chapitres'])
    for p in parties:
        print('   %-42s %3d' % (p['label'], len(p['chapitres'])))
    print('alineas             %5d' % stats['alineas'])
    print('notes               %5d  dont %d posees sur leur appel, %d sur un '
          'renvoi en toutes lettres, %d sans appel retrouve'
          % (stats['notes'], stats['notes_appel'], stats['notes_renvoi'],
             stats['orphelines'] - stats['notes_renvoi']))
    if orphelines:
        print('   appel absent du texte de la page : %s'
              % ', '.join('feuillet %d, note (%s)' % c for c in orphelines))
    print('vedettes            %5d' % stats['vedettes'])
    print('tableaux            %5d  dont %d a accolades, rendus aussi en '
          'groupes pour l\'ecran etroit' % (stats['tableaux'], stats['akoladi']))
    print('lignes detachees    %5d suites' % stats['rangs'])
    print('signes de texte     %5d' % stats['signes'])
    print('portrait            %5d x %d px, %d ko de PNG (alpha seule)'
          % (portreto[1], portreto[2], portreto[3] // 1024))
    print('addendum folio 224  %5d blocs remis apres « %s », %d bloc(s) '
          'restes au feuillet %d'
          % (deplaces, cible or '?', reste224, ADDENDUM_FEUILLET))
    if resistantes:
        print('MACROS NON TRAITEES : %s'
              % ', '.join('%s x%d' % (k, v) for k, v in resistantes.items()))

    if '--konto' not in sys.argv:
        doc, ancres = ecrire(rel, parties, stats)
        # LE CONTROLE D'UNICITE. Il se fait sur la page ECRITE, non sur
        # le registre : c'est le document qui porte les adresses, et
        # c'est donc lui qu'il faut relire.
        n, doubles, gauches = controle_ancres(doc)
        print('ancres              %5d identifiants, %s'
              % (n, 'AUCUN DOUBLON' if not doubles
                 else 'DOUBLONS : ' + ', '.join(doubles)))
        if ancres.doubles:
            print('   homonymes departages par un suffixe (%d) : %s'
                  % (len(ancres.doubles),
                     ', '.join(sorted({d[0] for d in ancres.doubles}))))
        if gauches:
            print('   licites mais a encoder dans une URL : %s'
                  % ', '.join(gauches))
        if doubles:
            sys.exit('identifiants repetes : la page n\'est pas adressable')
        print('notes recollees avec espace  %d' % getattr(rel,'n_recol',0))
        print('ecrit %s (%d ko)' % (SORTIE, len(doc.encode('utf-8')) // 1024))


if __name__ == '__main__':
    main()
