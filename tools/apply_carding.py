#!/usr/bin/env python3
"""Pose le cardage mesure d'une page dans le fichier de contenu.

Voir LISEZ-MOI, § 7 bis. Le compositeur justifie ses pages verticalement ;
tools/carding.py mesure le pas propre a la page et les blancs de ses
articulations. Cet outil fait le rapprochement entre ces mesures et les
frontieres d'alinea du source, et remplace le \\VUblancAlinea ordinaire
par un \\VUblanc{...} la ou le fac-simile en demande un plus large.

Le rapprochement se fait par NUMERO DE LIGNE, jamais par rang de blanc :
un blanc peut manquer d'un cote comme de l'autre, et un appariement par
rang ferait glisser toutes les valeurs suivantes d'un cran.

    python3 tools/apply_carding.py 30          # propose, n'ecrit rien
    python3 tools/apply_carding.py 30 --pose   # ecrit
"""
import os, re, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carding
import checks as C

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX2PT = 72.27 / 300.0
# Blanc d'alinea ordinaire, deja pose partout par \VUblancAlinea.
BLANC_ORDINAIRE_PX = 1.86 / PX2PT          # 7,72 px
# En deca de 3 px (0,7 pt) l'ecart est sous le bruit de la mesure des
# lignes de base : on laisse le blanc ordinaire.
SEUIL_PX = 3.0


def _page(folio):
    """« 30 » designe le FOLIO ; « f34 » designe le feuillet du fac-simile.

    Confondre les deux etait un piege : le folio 26 est porte par le
    feuillet 30, et une recherche indifferenciee servait la mauvaise page
    sans rien signaler.
    """
    pages = C.lire_releve()
    s = str(folio)
    if s.startswith('f'):
        for pg in pages:
            if pg['feuillet'] == s[1:]:
                return pg
        return None
    for pg in pages:
        if pg['folio'] == s:
            return pg
    return None


def propose(folio):
    """[(rang du \\VUblancAlinea dans la page, ligne fac-simile, exces px)]"""
    pg = _page(folio)
    if pg is None:
        raise SystemExit('page %s absente du releve' % folio)
    feuillet = int(pg['feuillet']) if pg['feuillet'] else int(pg['folio']) + 4
    reg, exces, fl, _ = cardage.mesure(feuillet)
    if reg is None:
        raise SystemExit('feuillet %d : pas de corps mesurable' % feuillet)
    # Le folio compte pour une ligne du fac-simile mais pas du releve.
    decalage = 1 if (fl and fl[0]['x1'] - fl[0]['x0']
                     < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
    # Frontieres d'alinea du CORPS, dans l'ordre du source. La ligne qui
    # suit la frontiere porte l'indice i+1 dans le releve.
    frontieres = []           # (rang, indice fac-simile de la ligne suivante)
    rang = 0
    # Les lignes SANS TEXTE (une macro d'apparat seule, un reste de
    # decoupage) ne paraissent pas au fac-simile : comptees ici, elles
    # decalaient l'indice de toutes les frontieres suivantes, et le blanc
    # mesure ne retrouvait plus sa place (folio 25 : l'exces de 24,8 px
    # devant la ligne 31 restait non pose, sans que rien le signale).
    lignes = [l for l in pg['lignes'] if l['texte']]
    for i, l in enumerate(lignes):
        if l.get('note') or l['coupe'] != 'pf':
            continue
        if i + 1 >= len(lignes) or lignes[i + 1].get('note'):
            continue          # dernier alinea de la page, ou passage aux notes
        rang += 1
        frontieres.append((rang, i + 1 + decalage))
    par_ligne = {k: e for k, _, e in exces}
    out = []
    for rang, k in frontieres:
        # UNE FRONTIERE SANS EXCES N'EST PAS UNE FRONTIERE SANS MESURE :
        # c'est une frontiere SANS BLANC. Le blanc d'alinea de 1,86 pt
        # n'est pas une constante du volume — au feuillet 20, les seize
        # pas du corps valent tous 41,0 a 41,9 px, frontieres comprises.
        # Traiter l'absence d'exces comme une absence de mesure laissait
        # en place six \VUblancAlinea que l'original n'a pas, et la page
        # descendait de 32 px sur sa hauteur.
        # \VUblanc REMPLACE \VUblancAlinea, il ne s'y ajoute pas : la
        # valeur a poser est donc l'EXCES ENTIER, non l'exces diminue du
        # blanc ordinaire. Diminue, il laissait la page 7,7 px trop haute
        # sous chaque articulation — assez pour que les folios 59 et 63
        # echouent au controle 11, et invisible partout ailleurs. Le
        # blanc ordinaire ne sert qu'a decider s'il y a lieu de toucher.
        e = par_ligne.get(k, 0.0)
        d = e - BLANC_ORDINAIRE_PX
        if abs(d) < SEUIL_PX:
            continue
        out.append((rang, k, e, e if d > 0 else d))
    return pg, reg, out, decalage


def _masque_notes(corps):
    """Le bloc \\VUnotes remplace par des blancs, les fins de ligne gardees.

    Les indices ne bougent donc pas, et les lignes blanches du corps
    restent detectables. Ecraser aussi les fins de ligne — ce que faisait
    la premiere version — soudait la matiere qui precede le bloc a celle
    qui le suit, et le compte des lignes partait de travers.

    Les bornes du bloc se prennent par COMPTAGE D'ACCOLADES : le corps
    d'une note contient lui-meme des accolades, et des lignes reduites a
    une accolade fermante.
    """
    masque = list(corps)
    for m in re.finditer(r'\\VUnotes\{', corps):
        i = m.end() - 1
        prof = 0
        while i < len(corps):
            if corps[i] == '{' and corps[i - 1] != '\\':
                prof += 1
            elif corps[i] == '}' and corps[i - 1] != '\\':
                prof -= 1
                if prof == 0:
                    break
            i += 1
        for j in range(m.start(), min(i + 1, len(corps))):
            if masque[j] != '\n':
                masque[j] = ' '
    return ''.join(masque)


# Macros d'apparat : chacune compose UNE ligne a elle seule. Sans elles,
# le compte des lignes du source retardait d'une unite par titre sur
# celui du releve, et le blanc mesure se posait plusieurs lignes trop
# haut (folio 12 : 41 px de derive devenus 77).
APPARAT = re.compile(r'\\(VUtitre|VUcentre|VUcentreA)\b')
SEPARATEUR = re.compile(r'\\nl\b|\\cc\b|\n[ \t]*\n')


def lignes_source(corps):
    """[(numero de ligne composee, debut, fin)] pour chaque frontiere d'alinea.

    Le numero est celui de la ligne qui SUIT la frontiere, compte comme
    le fait le releve : une ligne s'acheve sur \\nl, sur \\cc, ou sur une
    ligne blanche, et chaque macro d'apparat vaut une ligne entiere.
    (debut, fin) delimitent le \\VUblancAlinea ou le \\VUblanc deja pose,
    ou bien la position ou il faudrait l'ecrire.
    """
    masq = _masque_notes(corps)
    out = []
    n = 0            # lignes composees deja vues
    pos = 0
    for m in SEPARATEUR.finditer(masq):
        tranche = masq[pos:m.start()]
        # les macros d'apparat de la tranche comptent chacune pour une ligne
        napp = len(APPARAT.findall(tranche))
        reste = APPARAT.sub('', tranche)
        n += napp
        if C.texte_nu(reste).strip():
            n += 1
        pos = m.end()
        if not m.group(0).startswith('\\'):        # ligne blanche
            j = m.end()
            while True:                            # commentaires eventuels
                mc = re.match(r'%[^\n]*\n', masq[j:])
                if not mc:
                    break
                j += mc.end()
            mb = re.match(r'\\VUblanc(?:Alinea\b|\{[^}]*\})[^\n]*\n', masq[j:])
            out.append((n, j, j + mb.end() if mb else j))
    return out


def _corps_page(src, folio):
    """(debut, fin) du corps de la VUpage portant ce folio dans src."""
    s = str(folio)
    for m in re.finditer(
            r'\\begin\{VUpage\}(?:\[([^\]]*)\])?\{([^}]*)\}(.*?)\\end\{VUpage\}',
            src, re.S):
        # Le meme piege que dans _page : « 30 » est un FOLIO. Accepter
        # aussi le feuillet renvoyait la page \VUpage[30]{26} quand on
        # demandait le folio 30, et l'ancrage sur le texte ne trouvait
        # evidemment rien — sans que rien n'indique la confusion.
        if s.startswith('f'):
            if (m.group(1) or '').strip() == s[1:]:
                return m.start(3), m.end(3)
        elif m.group(2).strip() == s:
            return m.start(3), m.end(3)
    return None


def pose(folio, ecrire=False):
    pg, reg, props, decalage = propose(folio)
    print('=== folio %s (feuillet %s) — pas regulier %.2f px = %.2f pt'
          % (pg['folio'] or '?', pg['feuillet'], reg, reg * PX2PT))
    if abs(reg - cardage.PAS_COURANT) >= 0.6:
        print('    page cardee : \\VUinterlignePage{%.2fpt}' % (reg * PX2PT))
    if not props:
        print('    aucun blanc d\'articulation a poser')
        return
    fp = os.path.join(P, 'content', pg['fichier'])
    src = open(fp, encoding='utf-8').read()
    bornes = _corps_page(src, pg['folio'] or pg['feuillet'])
    if bornes is None:
        raise SystemExit('page introuvable dans %s' % fp)
    a, b = bornes
    corps = src[a:b]
    lg = [l for l in pg['lignes'] if l['texte']]
    # L'ANCRAGE SE FAIT SUR LE TEXTE, non sur un rang ni sur un compte de
    # lignes. Deux tentatives ont echoue avant celle-ci : compter les
    # frontieres du source (fausse des qu'un titre en separe deux, le
    # fac-simile y mettant un blanc et le source un \VUsaut), puis
    # compter les lignes composees (fausse par les macros d'apparat et
    # les commentaires). Le releve, lui, conserve pour chaque ligne le
    # fragment de source dont elle vient : on cherche ce fragment, et le
    # \VUblancAlinea qu'il porte en tete est celui qu'il faut changer.
    # Aucun calcul d'indice ne subsiste, donc aucun glissement possible.
    remplace = []
    for _, k, e, d in props:
        i = k - decalage
        if not (0 <= i < len(lg)):
            print('    ligne %2d : hors du releve' % k)
            continue
        brut = lg[i]['brut']
        if '\\VUblancAlinea' not in brut:
            print('    ligne %2d : exces %.1f px — la ligne « %s » ne suit pas '
                  'une frontiere d\'alinea ordinaire (titre ? a la main)'
                  % (k, e, lg[i]['texte'][:40]))
            continue
        if corps.count(brut) != 1:
            print('    ligne %2d : fragment ambigu (%d occurrences)'
                  % (k, corps.count(brut)))
            continue
        p = corps.index(brut) + brut.index('\\VUblancAlinea')
        if d <= 0:
            print('    ligne %2d : aucun blanc au fac-simile -> le blanc '
                  'ordinaire est ote  avant « %s »' % (k, lg[i]['texte'][:38]))
        else:
            print('    ligne %2d : exces %.1f px -> \\VUblanc{%.2fpt}  avant « %s »'
                  % (k, e, d * PX2PT, lg[i]['texte'][:38]))
        remplace.append((p, d))
    if not ecrire:
        print('    (rien ecrit ; --pose pour appliquer)')
        return
    for p, d in sorted(remplace, reverse=True):
        neuf = ('%% aucun blanc au fac-simile' if d <= 0
                else '\\VUblanc{%.2fpt}%% mesure au fac-simile' % (d * PX2PT))
        corps = corps[:p] + neuf + corps[p + len('\\VUblancAlinea'):]
    open(fp, 'w', encoding='utf-8').write(src[:a] + corps + src[b:])
    print('    pose dans content/%s' % pg['fichier'])


if __name__ == '__main__':
    ecrire = '--pose' in sys.argv
    for a in sys.argv[1:]:
        if a.startswith('--'):
            continue
        pose(a, ecrire)
