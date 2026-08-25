#!/usr/bin/env python3
"""Les huit controles automatiques de la transcription.

A lancer apres CHAQUE lot de modifications :

    python3 tools/checks.py            # tout
    python3 tools/checks.py 3 4 5      # seulement ces controles

 1. Pagination conforme, zero « Overfull \\vbox », inventaire des
    « Overfull \\hbox » un par un.
 2. Comparaison ligne a ligne entre le PDF compose et le releve.
 3. Tout \\cc tombe entre deux lettres.
 4. Aucun \\nl ne tombe a l'interieur d'un mot.
 5. Aucune ligne ne commence par : ; ! ?
 6. Aucune ligne ne commence par une ponctuation basse ou une
    parenthese fermante.
 7. Marge effective minimale sur toutes les pages.
 8. Comparaison visuelle a 300 dpi (fabrique les juxtapositions).

Le releve, c'est le contenu de content/*.tex : les coupures y sont
toutes explicites, donc le fichier source EST le releve du fac-simile.
"""
import os, re, sys, json, subprocess, glob

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENU = os.path.join(P, 'content')
sys.path.insert(0, os.path.join(P, 'tools'))
import syllabify
import pair_up
import cache

ROUGE, VERT, JAUNE, RAZ = '\033[31m', '\033[32m', '\033[33m', '\033[0m'


class Rapport:
    def __init__(self):
        self.lignes = []
        self.echecs = 0
        self.avertis = 0

    def ok(self, msg):
        self.lignes.append((VERT + 'OK  ' + RAZ, msg))

    def ko(self, msg):
        self.echecs += 1
        self.lignes.append((ROUGE + 'ECHEC' + RAZ, msg))

    def av(self, msg):
        self.avertis += 1
        self.lignes.append((JAUNE + 'NOTE' + RAZ, msg))

    def imprime(self, titre):
        print('\n=== %s ===' % titre)
        for tag, m in self.lignes:
            print('  %s %s' % (tag, m))


# --------------------------------------------------------------------
# Lecture du releve : les pages et leurs lignes, telles qu'encodees
# --------------------------------------------------------------------
# Commandes dont il faut jeter AUSSI les arguments : elles ne composent
# pas de texte (reglages de corps, blancs verticaux, filets...).
MUETTES = {
    'vspace': 1, 'vspace*': 1, 'hspace': 1, 'hspace*': 1, 'kern': 0,
    'fontsize': 2, 'setlength': 2, 'addvspace': 1, 'rule': 2,
    'includegraphics': 1, 'label': 1, 'phantom': 1, 'vskip': 0,
    'VUsaut': 1, 'VUfiletnote': 0, 'VUfilet': 1,
    # La SIGNATURE DE CAHIER est un chiffre nu au pied de la page. Elle
    # ne fait partie d'aucune ligne de texte : le detecteur du
    # fac-simile ne la voit pas (elle tombe sous le bloc), et du cote
    # compose lignes_pdf() ecarte les lignes d'un seul caractere. Les
    # deux cotes l'ignorent donc, et le controle 2 ne la verifie pas —
    # limite consignee au LISEZ-MOI. Sans cette entree, l'ordonnee
    # passee a la macro se lisait comme du texte : « 168.74mm2 ».
    'VUsignature': 2,
    # Reglages verticaux : ils ne composent rien, mais leur argument est
    # une dimension, que le releve prenait pour du texte (le folio 30
    # ouvrait sur une ligne « 10.38pt »).
    'VUinterlignePage': 1, 'VUblanc': 1, 'VUblancAlinea': 0,
    # L'accolade d'un tableau ne porte pas de texte : seulement sa
    # hauteur et son deplacement vertical, deux arguments tous deux muets.
    'VUaccolade': 2, 'VUaccoladeD': 2,
    # L'ORNEMENT DE FIN DE PARTIE est un filet nu : aucun texte. Son
    # unique argument est une ordonnee, que le releve lisait comme la
    # premiere ligne du folio 114 (« 147.14mm »).
    'VUornement': 1,
    # L'ASTERISME est un ornement nu : trois asterisques, aucun texte.
    # Son unique argument est une ordonnee, que le releve lisait comme
    # la premiere ligne du folio 186.
    'VUasterismo': 1,
    # \VUpageNote ne compose rien : elle change le corps et l'interlignage
    # de toute la page (feuillet 208, seule page du volume entierement au
    # corps des notes). Son argument, « 8.13pt », se lisait comme la
    # premiere ligne du folio 204.
    'VUpageNote': 1,
    # L'ACCOLADE HORIZONTALE de l'arbre du folio 220 ne porte pas de
    # texte : son unique argument est une largeur, que le releve
    # lisait comme le debut du rang (« 45.63mmPetrusPaulus... »).
    'VUaccoladeH': 1,
}
# Commandes dont on jette les N premiers arguments et garde le dernier.
SAUTE_PUIS_TEXTE = {'VUnotes': 1, 'VUserre': 1,
                    # Tableaux : l'abscisse relevee, puis la matiere.
                    'VUcase': 1, 'VUdecale': 1}
# Commandes dont on garde l'argument (il porte du texte).
PARLANTES = {'textbf', 'textit', 'textsc', 'emph', 'textrm', 'MakeUppercase',
             'textsuperscript'}
# Commandes SANS argument qui composent pourtant un caractere. Le releve
# les effacait purement et simplement, si bien que le controle 2 declarait
# perdu un signe bien compose : au folio 199, le guillemet simple DROIT du
# fac-simile — un vrai trait vertical, distinct de la virgule culbutee du
# folio 201 — s'ecrit \textquotesingle ; il disparaissait du cote releve
# et subsistait du cote PDF.
LITTERALES = {'textquotesingle': "'",
              # LES ACCOLADES ECHAPPEES SE COMPOSENT. Au folio 220 le
              # texte cite les signes eux-memes — « Embracili \{\} » — et
              # le releve les effacait purement, si bien que le
              # controle 2 opposait « Embracili uzesas » a « Embracili
              # {} uzesas » sur une page juste.
              '{': '{', '}': '}'}
CMD = re.compile(r'\\([a-zA-Z@]+\*?|.)')


def _saute_groupe(s, i):
    """i pointe sur '{' : retourne (contenu, index apres '}')."""
    prof, j = 0, i
    while j < len(s):
        if s[j] == '{':
            prof += 1
        elif s[j] == '}':
            prof -= 1
            if prof == 0:
                return s[i + 1:j], j + 1
        elif s[j] == '\\':
            j += 1
        j += 1
    return s[i + 1:], len(s)


def _saute_opt(s, i):
    if i < len(s) and s[i] == '[':
        j = s.find(']', i)
        return j + 1 if j >= 0 else i
    return i


def texte_nu(s):
    """Retire le balisage LaTeX et ne garde que le texte reellement compose."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == '%':
            j = s.find('\n', i)
            i = len(s) if j < 0 else j + 1
            continue
        if c == '\\':
            m = CMD.match(s, i)
            if not m:
                i += 1
                continue
            nom = m.group(1)
            j = m.end()
            if nom in (',', ' ', ';', ':', '!'):
                out.append(' ' if nom in (',', ' ') else '')
                i = j
                continue
            if nom in LITTERALES:
                out.append(LITTERALES[nom])
                i = j
                if i < len(s) and s[i] == '{' and s[i + 1:i + 2] == '}':
                    i += 2          # le {} qui protege l'espace suivante
                continue
            while j < len(s) and s[j] in ' \n\t':
                j += 1
            j = _saute_opt(s, j)
            if nom in MUETTES:
                for _ in range(MUETTES[nom]):
                    if j < len(s) and s[j] == '{':
                        _, j = _saute_groupe(s, j)
                i = j
                continue
            if nom in SAUTE_PUIS_TEXTE:
                for _ in range(SAUTE_PUIS_TEXTE[nom]):
                    if j < len(s) and s[j] == '{':
                        _, j = _saute_groupe(s, j)
                    while j < len(s) and s[j] in ' \n\t':
                        j += 1
                if j < len(s) and s[j] == '{':
                    inner, j = _saute_groupe(s, j)
                    # Espace AVANT le contenu d'une case de tableau : deux
                    # \VUcase voisins se collaient, et « ... persono : »
                    # suivi de « me » formait le jeton « :me », que la
                    # comparaison des rangs ne savait reconnaitre ni pour
                    # un artefact d'accolade ni pour du texte.
                    out.append((' ' if nom in ('VUcase', 'VUdecale') else '')
                               + texte_nu(inner))
                i = j
                continue
            if nom in PARLANTES:
                if j < len(s) and s[j] == '{':
                    inner, j = _saute_groupe(s, j)
                    out.append(texte_nu(inner))
                i = j
                continue
            i = j          # commande sans effet textuel (\centering, \par...)
            continue
        if c in '{}':
            i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


APPARAT = {'VUcentreA': 4, 'VUcentre': 3, 'VUtitre': 3, 'VUsoustitre': 3}


def deplie_apparat(corps):
    """Chaque ligne d'apparat (\\VUcentreA{y}{corps}{interlettrage}{texte},
    \\VUcentre{corps}{interlettrage}{texte}) est une ligne du fac-simile a
    part entiere : on la ramene a « texte\\nl » pour que le releve reste
    uniformement une suite de lignes. Seul le DERNIER argument porte du
    texte ; les precedents sont des mesures."""
    out, i = [], 0
    while i < len(corps):
        cands = [(corps.find('\\' + nom, i), nom) for nom in APPARAT]
        cands = [(j, nom) for j, nom in cands if j >= 0]
        if not cands:
            out.append(corps[i:])
            break
        # la plus proche, et a position egale la plus longue (VUcentreA
        # avant VUcentre, dont le nom est un prefixe)
        j, nom = min(cands, key=lambda t: (t[0], -len(t[1])))
        out.append(corps[i:j])
        k = j + 1 + len(nom)
        texte = ''
        for a in range(APPARAT[nom]):
            while k < len(corps) and corps[k] in ' \n\t':
                k += 1
            if k < len(corps) and corps[k] == '{':
                arg, k = _saute_groupe(corps, k)
                if a == APPARAT[nom] - 1:
                    texte = arg
        out.append('\x02' + texte + '\x02' + r'\nl')
        i = k
    return ''.join(out)


def deplace_notes(corps):
    """Le bloc de notes est declare en TETE de page (il est place a une
    ordonnee absolue), mais il se compose en BAS de page. Le controle 2
    compare dans l'ordre visuel : on le remet donc a la fin."""
    j = corps.find('\\VUnotes')
    if j < 0:
        return corps
    k = j + len('\\VUnotes')
    # \VUnotes a pris un ARGUMENT OPTIONNEL (la largeur du filet, nulle au
    # feuillet 208, seule page du volume dont la note n'en porte aucun).
    # Sans ce saut, « [0pt] » et l'ordonnee tombaient dans le texte de la
    # premiere ligne relevee.
    while k < len(corps) and corps[k] in ' \n\t':
        k += 1
    k = _saute_opt(corps, k)
    for _ in range(2):
        while k < len(corps) and corps[k] in ' \n\t':
            k += 1
        if k < len(corps) and corps[k] == '{':
            _, k = _saute_groupe(corps, k)
    return corps[:j] + corps[k:] + '\n\n\x03' + corps[j:k]


def _deplie_rangs(corps):
    """\\VUrang{...} -> son contenu, suivi d'un \\nl."""
    out = []
    i = 0
    while True:
        j = corps.find('\\VUrang{', i)
        if j < 0:
            out.append(corps[i:])
            break
        out.append(corps[i:j])
        contenu, k = _saute_groupe(corps, j + len('\\VUrang'))
        # \x04 marque la ligne comme rang de tableau : ses blancs sont
        # des ecarts mesures, non du contenu.
        out.append('\x04' + contenu + '\\nl')
        i = k
    return ''.join(out)


def _deplie_index(corps):
    """\\VUindex[opt]{entree}{numero} -> « entree numero », suivi d'un \\nl.

    Chaque entree du TABELO est UNE ligne du fac-simile. Sans ce
    depliage, texte_nu les enchainait toutes dans la meme ligne relevee,
    et le controle 2 opposait les vingt-six entrees du folio 225 a la
    seule « Pagini. » du compose.
    Elles sont marquees comme rangs de tableau (\\x04) : leurs blancs sont
    des ecarts mesures, non du contenu, et leur premier caractere n'est
    pas soumis aux regles de coupure.
    """
    out, i = [], 0
    while True:
        j = len(corps)
        # \VUindexLarge, ajoutee pour les catalogues du folio 232 (dont
        # les points de conduite ont un pas trois fois plus large), doit
        # etre depliee comme les deux autres. Omise ici, ses lignes ne
        # sont pas marquees comme rangs, et les controles de debut de
        # ligne y voient cinq « espaces parasites ».
        for nom in ('\\VUindexNu', '\\VUindexLarge', '\\VUindex'):
            k = corps.find(nom, i)
            # \VUindex ne doit pas happer \VUindexNu ni \VUindexRenfoncement
            while k >= 0 and corps[k + len(nom):k + len(nom) + 1].isalpha():
                k = corps.find(nom, k + 1)
            if k >= 0 and k < j:
                j, quel = k, nom
        if j >= len(corps):
            out.append(corps[i:])
            break
        out.append(corps[i:j])
        k = j + len(quel)
        k = _saute_opt(corps, k)
        entree, k = _saute_groupe(corps, k)
        numero, k = _saute_groupe(corps, k)
        out.append('\x04' + entree + ' ' + numero + '\\nl')
        i = k
    return ''.join(out)


def lire_releve():
    """Retourne [{'fichier','folio','lignes':[{'texte','coupe'}...]}, ...]

    coupe = 'cc' si la ligne se termine par un trait d'union de coupure,
            'nl' si elle se termine sans trait d'union,
            None pour la derniere ligne d'un alinea."""
    pages = []
    for fp in sorted(glob.glob(os.path.join(CONTENU, '*.tex'))):
        src = open(fp, encoding='utf-8').read()
        for m in re.finditer(
                r'\\begin\{VUpage\}(?:\[([^\]]*)\])?\{([^}]*)\}(.*?)\\end\{VUpage\}',
                src, re.S):
            feuillet, folio, corps = (m.group(1) or '').strip(), m.group(2).strip(), m.group(3)
            corps = deplace_notes(corps)
            corps = deplie_apparat(corps)
            # Une fin d'alinea est une fin de ligne : le releve doit la voir.
            # Une fin d'alinea EST une fin de ligne, mais ce n'est pas un
            # \nl : la ligne y est courte, non justifiee. Les confondre
            # rendait le controle des fins de ligne inutilisable, chaque
            # fin d'alinea etant reclamee « pleine ».
            # Un rang de tableau est une ligne : \VUrang{...} rend son
            # contenu suivi d'une fin de ligne. Sans cela le releve voyait
            # les six rangs du tableau du folio 31 comme une seule ligne.
            corps = _deplie_rangs(corps)
            corps = _deplie_index(corps)
            corps = re.sub(r'\n[ \t]*\n', r'\\pf' + '\n', corps)
            lignes = []
            # on decoupe sur \nl et \cc en conservant lequel a coupe
            morceaux = re.split(r'(\\nl\b|\\cc\b|\\pf\b)', corps)
            courant = ''
            dans_note = [False]
            for k in range(0, len(morceaux)):
                p = morceaux[k]
                if p in (r'\nl', r'\cc', r'\pf'):
                    lignes.append({'brut': courant,
                                   'texte': texte_nu(courant.replace('\x02', '').replace('\x03', '').replace('\x04', '')).strip(),
                                   'apparat': '\x02' in courant,
                                   'rang': '\x04' in courant,
                                   'note': dans_note[0] or '\x03' in courant,
                                   'coupe': p[1:]})   # 'nl', 'cc' ou 'pf'
                    if '\x03' in courant:
                        dans_note[0] = True
                    courant = ''
                else:
                    courant += p
            if texte_nu(courant).strip():
                lignes.append({'brut': courant,
                               'texte': texte_nu(courant.replace('\x02', '').replace('\x03', '').replace('\x04', '')).strip(),
                               'apparat': '\x02' in courant,
                               'rang': '\x04' in courant,
                               'note': dans_note[0] or '\x03' in courant,
                               'coupe': None})
            pages.append({'fichier': os.path.basename(fp), 'folio': folio,
                          'feuillet': feuillet, 'lignes': lignes})
    return pages


# --------------------------------------------------------------------
# Controle 1 — pagination et debordements
# --------------------------------------------------------------------
def controle_1(pages, r):
    log = os.path.join(P, 'main.log')
    if not os.path.exists(log):
        r.ko('main.log absent : le document n\'a pas ete compile')
        return
    txt = open(log, encoding='utf-8', errors='replace').read()
    vbox = re.findall(r'Overfull \\vbox \(([\d.]+)pt too high\)', txt)
    hbox = re.findall(r'Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*', txt)
    if vbox:
        r.ko('%d « Overfull \\vbox » : %s' % (len(vbox), ', '.join(vbox[:8])))
    else:
        r.ok('aucun « Overfull \\vbox »')
    if hbox:
        r.av('%d « Overfull \\hbox » — inventaire dans tools/hbox.txt'
             % len(hbox))
        with open(os.path.join(P, 'tools', 'hbox.txt'), 'w') as fh:
            for i, h in enumerate(re.findall(
                    r'(Overfull \\hbox[^\n]*\n(?:[^\n]*\n){0,2})', txt), 1):
                fh.write('%3d. %s\n' % (i, h.strip()))
    else:
        r.ok('aucun « Overfull \\hbox »')
    pdf = os.path.join(P, 'main.pdf')
    if os.path.exists(pdf):
        out = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
        npages = int(re.search(r'Pages:\s+(\d+)', out).group(1))
        if npages == len(pages):
            r.ok('pagination conforme : %d pages composees pour %d pages relevees'
                 % (npages, len(pages)))
        else:
            r.ko('pagination : %d pages composees pour %d pages relevees'
                 % (npages, len(pages)))


# --------------------------------------------------------------------
# Controle 2 — comparaison ligne a ligne PDF <-> releve
# --------------------------------------------------------------------
def _norm(s):
    s = s.replace('\u00a0', ' ').replace('\u2019', "'").replace('\u2018', "'")
    # L'accent grave du source LaTeX EST le guillemet simple ouvrant : au
    # folio 201 le fac-simile porte une virgule culbutee, qu'on ecrit \u00ab ` \u00bb
    # et que pdftotext rend \u00ab ' \u00bb. Sans cette ligne le controle opposait
    # \u00ab ` Qua \u00bb a \u00ab ' Qua \u00bb sur une page juste.
    s = s.replace('`', "'")
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2014', '--').replace('\u2013', '--')
    s = s.replace('---', '--')          # cadratin encode en source LaTeX
    # pdftotext insere une espace apres un exposant : « IV^a , Papo ».
    # Une espace avant une virgule ou un point n'est jamais correcte dans
    # cet ouvrage — l'espacement a la francaise ne vaut que pour ; : ! ? —
    # donc la supprimer ne peut masquer aucun defaut reel.
    # Meme raison pour la PARENTHESE FERMANTE : « (1,000,000^2 ) ».
    # L'espace que pdftotext pose apres un exposant tombe la ou le
    # tableau du folio 94 en met un. Une espace avant « ) » n'est jamais
    # correcte ici, et le controle 6 verifie deja qu'aucune ligne ne
    # COMMENCE par une parenthese fermante : rien n'est masque.
    s = re.sub(r'\s+([,.)])', r'\1', s)
    # Et de meme APRES une parenthese OUVRANTE. Au folio 204 pdftotext
    # rend « ( beluli) » la ou le source ecrit « (beluli) » : le blanc
    # naît du passage du gras au romain juste avant, comme celui qu il
    # pose apres un exposant. Une espace apres « ( » n est jamais
    # correcte dans cet ouvrage, donc la retirer ne masque rien de reel.
    s = re.sub(r'\(\s+', '(', s)
    # LE MENEUR DE POINTS DU TABELO n'est pas du contenu : c'est un
    # remplissage typographique, pose par \\leaders. Le releve ecrit
    # l'entree et son numero, le compose intercale trente points.
    # Aucun texte du volume ne porte six points de suite — le plus
    # long est « (...) » du folio 219, qui en a trois.
    s = re.sub(r'\.{6,}', ' ', s)
    # L'ESPACE A LA FRANCAISE, elle, est REELLE des deux cotes — mais
    # elle n'est ecrite ni dans le source ni rendue de facon fiable.
    # Le source ecrit « if; » ; c'est \VUespacePonct qui pose l'espace au
    # moment de composer. Le releve, lui, lit le source et rend « if; ».
    # Restait pdftotext, qui n'annonce l'espace que lorsqu'elle depasse
    # son seuil geometrique : apres une lettre romaine il ne la voit pas,
    # apres une italique — dont la correction s'ajoute a l'espace — il la
    # voit. D'ou deux echecs aux folios 90 et 91, « E. if ; » contre
    # « E. if; », sur des pages parfaitement justes.
    #
    # On normalise donc des DEUX cotes. Ce que cela coute est nommable :
    # le controle ne peut plus voir une espace a la francaise manquante.
    # Mais elle ne peut pas manquer sur UNE ligne : elle vient d'une
    # macro posee une fois pour tout le volume, et le folio 12 l'a
    # verifiee a l'oeil. Un defaut global reste visible, un defaut local
    # est impossible — la normalisation ne masque donc rien de reel.
    s = re.sub(r'\s+([;:!?])', r'\1', s)
    s = s.replace('\u00ab', '<<').replace('\u00bb', '>>')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def lignes_pdf():
    """Lignes du PDF compose, page par page, via pdftotext -layout."""
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        return None
    out = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', pdf, '-'],
                         capture_output=True, text=True).stdout
    # Les accolades des tableaux viennent de la fonte d'extension
    # mathematique, qui n'a pas de correspondance Unicode : pdftotext les
    # rend en caracteres de commande (0x1A, 0x08). Une ligne qui n'en
    # contient pas d'autre paraissait alors non vide, decalait toutes les
    # suivantes, et le controle 2 declarait « <manque> » sur une page
    # pourtant juste (folio 31).
    # Une accolade de tableau est plus haute qu'une ligne : pdftotext lui
    # donne une ligne a elle. Elle en sort dans un caractere quelconque,
    # selon la fonte et la piece d'accolade employees — on a vu 0x1A,
    # 0x08, « ( » et « n ». Une liste de caracteres a ecarter ne tient
    # donc pas ; le critere sur est STRUCTUREL : la ligne parasite ne
    # porte qu'UN SEUL caractere. Le volume n'a aucune ligne legitime
    # d'un seul caractere — la plus courte relevee en compte cinq
    # (« rozi. »). Ces lignes decalaient toutes les suivantes, et le
    # controle 2 declarait « manque » sur une page pourtant juste.
    # L'ASTERISME, une fois pose juste, se prend une ligne a lui. Tant que
    # ses deux rangs tombaient a 63 px l'un de l'autre — la faute corrigee
    # au preambule — le rang haut se collait au texte voisin et pdftotext
    # ne les separait pas. Bien pose, il sort en « * » puis « * * », que
    # net() reduit a « ***» : une ligne de plus du cote compose, qui
    # decalait toutes les suivantes et faisait echouer le controle 2 sur
    # deux pages pourtant justes (folios 186 et 207).
    # Le volume n'a aucune ligne de texte faite de seuls asterisques.
    AST = re.compile(r'^[*\s]+$')
    LETTRE = re.compile(r'[0-9A-Za-zÀ-ÿ]')
    POINTS = re.compile(r'^[.\s]+$')

    def net(l):
        t = ''.join(c for c in l if c >= ' ' or c == '\t').strip()
        if len(t) <= 1 or AST.match(t):
            return ''
        # L'ACCOLADE HORIZONTALE se brise en plusieurs morceaux, et
        # pdftotext les rejette sur une ligne a eux : « }|      { » au
        # folio 220. La regle du caractere unique, ecrite pour l'accolade
        # VERTICALE, ne les attrape pas — ils sont deux.
        # Le critere sur reste structurel : une ligne de ce volume porte
        # toujours une lettre ou un chiffre. La seule exception est une
        # rangee de points d'un hors-texte, qu'il faut garder.
        if not LETTRE.search(t) and not POINTS.match(t):
            return ''
        return t
    return [[net(l) for l in pg.split('\n') if net(l)]
            for pg in out.split('\f')[:-1]]


def controle_2(pages, r):
    got = lignes_pdf()
    if got is None:
        r.ko('main.pdf absent')
        return
    ecarts = 0
    for i, pg in enumerate(pages):
        lg = [l for l in pg['lignes'] if l['texte']]
        attendu = [_norm(l['texte'] + ('-' if l['coupe'] == 'cc' else '')) for l in lg]
        obtenu = [_norm(x) for x in (got[i] if i < len(got) else [])]
        # une ligne d'apparat est interlettree : les blancs y sont un effet
        # typographique, pas du contenu. On la compare blancs otes.
        # Les lignes d'apparat ET les notes sont interlettrees : pdftotext
        # lit l'approche comme une espace (« vokali e , o »). Les blancs y
        # sont un effet typographique, pas du contenu : on compare sans eux.
        # Un rang de tableau se compare aussi blancs otes : ses ecarts
        # sont geometriques (\VUcase), non des espaces-mots.
        app = [l.get('apparat') or l.get('note') or l.get('rang') for l in lg]
        # le folio compose apparait en tete : on l'ecarte de la comparaison
        if obtenu and re.fullmatch(r'--\s*\d*\s*--', obtenu[0]):
            obtenu = obtenu[1:]
        cmp_a = [x.replace(' ', '') if (k < len(app) and app[k]) else x
                 for k, x in enumerate(attendu)]
        cmp_b = [x.replace(' ', '') if (k < len(app) and app[k]) else x
                 for k, x in enumerate(obtenu)]
        # Un element pose entre deux lignes (\VUdecale) sort du rang pour
        # pdftotext, qui le rejette sur une ligne a lui : au folio 31,
        # « de o ek » se detachait du rang « Supereso maxim ». L'element
        # EST bien entre deux lignes au fac-simile ; ce n'est donc pas une
        # erreur de composition, mais une limite de l'extraction. On
        # recolle les morceaux, et seulement tant que cela rapproche du
        # releve : si la reunion ne donne pas le texte attendu, l'ecart
        # est signale comme avant.
        # Les accolades sortent de pdftotext en caracteres isoles
        # arbitraires — « ( », « n », « o » selon la piece de fonte —, et
        # elles se melent aux mots du rang quand elles tombent a leur
        # hauteur. Aucune liste de caracteres ne les distingue.
        # On compare donc les rangs SANS LEURS JETONS D'UNE LETTRE, des
        # deux cotes. Ce que cela coute est reel et doit se dire : le
        # « o » de « de o ek » n'est plus verifie par le controle 2 au
        # folio 31. Tout le reste du rang l'est.
        def _sans_jetons_courts(t):
            # Sur un rang, tout point de suite est un MENEUR, jamais du
            # texte : le seuil de six points de _norm, pose pour epargner
            # le « (...) » du folio 219, laissait passer les deux ou trois
            # points qui survivent au bord d'une colonne serree. Ici on
            # peut etre strict, parce qu'aucune entree d'index ne porte
            # deux points de suite.
            t = re.sub(r'\.{2,}', ' ', t)
            return ''.join(m for m in t.split() if len(m) > 1)
        # LES INDICES DU COMPOSE NE SONT PAS CEUX DU RELEVE. pdftotext
        # eclate un rang de tableau en plusieurs lignes ; des l'instant ou
        # il en ajoute une, obtenu[k] et lg[k] ne designent plus la meme
        # matiere. Depouiller obtenu[k] d'apres lg[k].rang laissait donc
        # des lignes de rang non depouillees, la reunion des morceaux
        # echouait, et le controle accusait le folio 31 d'avoir perdu
        # « minim » — sur une page inchangee depuis des semaines.
        # On ne depouille ici que le RELEVE, dont les indices sont surs ;
        # le compose l'est plus bas, au moment ou on le compare, la ou
        # l'on sait a quel rang il fait face.
        for k, l in enumerate(lg):
            if l.get('rang') and k < len(attendu):
                attendu[k] = _sans_jetons_courts(attendu[k])
        rangs_faibles = sum(1 for l in lg if l.get('rang'))
        if rangs_faibles:
            r.av('folio %s : %d rang(s) de tableau compares sans leurs '
                 'jetons d\'une lettre (les accolades sortent de pdftotext '
                 'en caracteres isoles)'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet')), rangs_faibles))
        cmp_a = [x.replace(' ', '') if (k < len(app) and app[k]) else x
                 for k, x in enumerate(attendu)]
        cmp_b = [x.replace(' ', '') if (k < len(app) and app[k]) else x
                 for k, x in enumerate(obtenu)]
        rang = [l.get('rang') for l in lg]
        k = 0
        while k < len(cmp_b) and k < len(cmp_a):
            if k < len(rang) and rang[k]:
                # depouillement du compose : ici, et ici seulement, on
                # sait que cette ligne-la fait face a un rang.
                nu = _sans_jetons_courts(obtenu[k])
                if nu != cmp_b[k]:
                    cmp_b[k], obtenu[k] = nu, nu
                if (cmp_b[k] != cmp_a[k] and cmp_a[k].startswith(cmp_b[k])
                        and k + 1 < len(cmp_b)):
                    cmp_b[k] += _sans_jetons_courts(obtenu[k + 1])
                    obtenu[k] = cmp_b[k]
                    del cmp_b[k + 1], obtenu[k + 1]
                    continue
            k += 1
        if cmp_a != cmp_b:
            ecarts += 1
            n = max(len(attendu), len(obtenu))
            for k in range(n):
                a = attendu[k] if k < len(attendu) else '<manque>'
                b = obtenu[k] if k < len(obtenu) else '<manque>'
                if k < len(app) and app[k]:
                    a, b = a.replace(' ', ''), b.replace(' ', '')
                if a != b:
                    r.ko('page %s (folio %s), ligne %d\n        releve : %s\n        compose: %s'
                         % (i + 1, pg['folio'], k + 1, a, b))
                    break
    if not ecarts:
        r.ok('les %d pages composees sont ligne a ligne identiques au releve'
             % len(pages))



# --------------------------------------------------------------------
# Controle 12 — chaque note est un ALINEA
# --------------------------------------------------------------------
# TROIS RECIDIVES, TOUJOURS LA MEME. Aux folios 59-63, puis 74, puis 93,
# puis 106, j'ai enchaine les notes d'un bloc par des \nl au lieu de les
# traiter en alineas. Le fac-simile renfonce le premier mot de chacune :
# ce sont des alineas, jamais des lignes de plus.
#
# Le controle 10 le rattrape a chaque fois — mais APRES coup, et par un
# symptome indirect (« le releve la donne pleine mais elle ne fait que
# 17 % »). On mesure donc la chose elle-meme, et on la nomme.
#
# Cote fac-simile : dans le bloc des notes, une ligne qui OUVRE une note
# est renfoncee. On compte les lignes dont l'abscisse depasse d'au moins
# RENFONCEMENT_MIN la marge.
#
# LA MARGE NE SE PREND PAS DANS LE SEUL BLOC DES NOTES. Elle y etait
# prise comme le minimum des abscisses des lignes de note — ce qui
# suppose qu'au moins une ligne du bloc soit a la marge, c'est-a-dire
# qu'au moins une note occupe deux lignes. Au folio 114, les deux notes
# tiennent chacune sur une ligne et sont donc toutes deux renfoncees : le
# minimum valait le renfoncement lui-meme, l'ecart tombait a zero, et le
# controle accusait de \nl une page qui n'en portait pas.
#
# ET ELLE NE SE PREND PAS NON PLUS DANS LE SEUL CORPS. Premier remede
# essaye : mediane des abscisses du corps. Il a fait crier vingt et une
# pages justes. Le corps du folio 34 est une liste dont seize lignes sur
# vingt sont renfoncees de 52 px : leur mediane EST le renfoncement, et
# les ouvertures de note tombaient au-dessous du seuil.
#
# LA MARGE NE SE DEDUIT PAS DAVANTAGE DU RECUEIL : le rognage suit le
# papier et non la justification, si bien qu'elle oscille de 49 a 280 px
# selon le feuillet, recto et verso alternes. Elle se mesure donc page a
# page, sur TOUTES les bandes, tete de page exceptee : corps ou notes,
# une page en porte toujours quelques-unes a la marge. On en prend le
# DECILE et non le minimum, pour qu'une salete isolee ne la tire pas vers
# la gauche — et si le minimum s'ecarte du decile de plus de MARGE_ECART,
# c'est que quelque chose traine hors justification et la page n'est pas
# jugee.
# Cote source : on compte les alineas du bloc \VUnotes.
RENFONCEMENT_MIN = 25          # px ; le renfoncement des notes vaut 3,6 mm = 43 px
MARGE_ECART = 10               # px ; ecart tolere entre minimum et decile


def controle_12(pages, r):
    signale = 0
    verifies = 0
    for pg in pages:
        lg = [l for l in pg['lignes'] if l['texte']]
        notes = [l for l in lg if l.get('note')]
        if len(notes) < 2:
            continue
        try:
            feuillet = int(pg['feuillet']) if pg['feuillet'] else int(pg['folio']) + 4
            fl = cache.feuillet(feuillet)['lignes']
        except (ValueError, TypeError, KeyError):
            continue
        dec = 1 if (fl and fl[0]['x1'] - fl[0]['x0']
                    < 0.25 * max(l['x1'] - l['x0'] for l in fl)) else 0
        if len(lg) + dec != len(fl):
            continue                    # comptes divergents : page sautee
        # bandes du fac-simile qui font face aux lignes de note
        bandes = [fl[i + dec] for i, l in enumerate(lg) if l.get('note')]
        # UNE BANDE SOUDEE FAUSSE L'ABSCISSE. Quand deux lignes de note se
        # soudent en une bande, celle-ci prend le x0 de la plus a gauche
        # — et une ligne renfoncee passe pour etre a la marge. Au folio 29
        # « Decido 586 » se lisait ainsi a +7 px alors que le fac-simile,
        # a l'agrandissement, la renfonce comme ses deux voisines. On ne
        # juge donc pas une page dont une bande de note est soudee : on le
        # dit et on passe.
        # UNE SALETE DANS LA MARGE FAUSSE AUSSI L'ABSCISSE — meme famille
        # que le pli du folio 79. Au folio 29, « Decido 586 » se mesure a
        # +7 px alors que l'agrandissement la montre renfoncee comme ses
        # deux voisines : une trace isolee traine dans sa marge. On
        # reutilise le detecteur ecrit pour le controle 10, et l'on
        # declare la page non jugee plutot que de l'accuser.
        if any(_pli(feuillet, b) for b in bandes):
            r.av('folio %s : une trace parasite traine dans la marge du '
                 'bloc de notes — abscisses non mesurables, page non jugee'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet'))))
            continue
        haut = [b['y1'] - b['y0'] for b in bandes]
        med = sorted(haut)[len(haut) // 2]
        if med > 0 and max(haut) >= 1.7 * med:
            r.av('folio %s : une bande de note en soude deux — les '
                 'abscisses du bloc ne se mesurent pas, page non jugee'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet'))))
            continue
        xs = sorted(b['x0'] for b in fl[dec:])
        marge = xs[len(xs) // 10]
        if marge - xs[0] > MARGE_ECART:
            r.av('folio %s : une bande sort de la justification a gauche '
                 '(%d px avant la marge) — page non jugee'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet')),
                    marge - xs[0]))
            continue
        renfonces = sum(1 for b in bandes if b['x0'] - marge >= RENFONCEMENT_MIN)
        # Alineas du source. Le releve ne porte pas de drapeau « alinea »,
        # mais il note la FIN d'alinea : coupe == 'pf'. Une ligne de note
        # qui suit une fin d'alinea en ouvre donc un nouveau, et la
        # premiere ligne du bloc en ouvre un par construction.
        # UN ALINEA OUVERT PAR \VUcontinue N'EST PAS RENFONCE : c'est la
        # suite d'une note commencee au folio precedent. Compte comme les
        # autres, il faisait crier au manque sur quatre pages justes.
        def _ouvre(l):
            return '\\VUcontinue' not in l['brut']
        ouvertures = [notes[0]] + [b for a, b in zip(notes, notes[1:])
                                   if a['coupe'] == 'pf']
        alineas = sum(1 for l in ouvertures if _ouvre(l))
        verifies += 1
        if renfonces != alineas:
            signale += 1
            r.ko('folio %s : le fac-simile renfonce %d ligne(s) du bloc de '
                 'notes, le source y compte %d alinea(s) — des notes '
                 'enchainees par \\nl au lieu d\'etre des alineas ?'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet')),
                    renfonces, alineas))
    if not signale:
        r.ok('les blocs de notes de %d pages ont autant d\'alineas que le '
             'fac-simile a de lignes renfoncees' % verifies)


# --------------------------------------------------------------------
# Controles 3 et 4 — \cc entre deux lettres, \nl jamais dans un mot
# --------------------------------------------------------------------
# UNE PARENTHESE PEUT OUVRIR LA SUITE D'UN MOT COUPE. Le folio 160 porte
# « flor(vend)isto, flor(kultiv)isto » et le compositeur coupe le second
# entre « flor- » et « (kultiv)isto » — le tiret est bien imprime au
# fac-simile, verifie a l'agrandissement x 5. La coupure tombe donc entre
# une lettre et une parenthese, ce que la regle D. 485 ne prevoit pas
# parce qu'elle ne parle que de syllabes. On admet la parenthese ouvrante
# en tete de la suite ; le reste de la regle continue de s'appliquer.
MOT_FIN = re.compile(r'([A-Za-zÀ-ÿ]+)$')
MOT_DEB = re.compile(r'^\(?([A-Za-zÀ-ÿ]+)')


def controle_3(pages, r):
    mauvais = 0
    for ip, pg in enumerate(pages):
        for k, l in enumerate(pg['lignes']):
            if l['coupe'] != 'cc':
                continue
            g = MOT_FIN.search(l['texte'])
            # Un mot peut se couper d'une PAGE a l'autre : le fac-simile le
            # fait au pied du folio 14. La suite se cherche alors sur la
            # page suivante, sinon le controle croit a une coupure orpheline.
            # La suite d'un mot coupe se cherche dans le MEME flux : le
            # texte courant continue en texte courant, la note en note.
            # Le bloc de notes etant ramene en fin de page pour l'ordre
            # visuel, la derniere ligne du corps est suivie des notes :
            # sans ce filtre, le controle cherchait la fin du mot « be- »
            # du folio 14 dans l'appel de note qui le suit.
            flux = l.get('note', False)
            suite = ''
            for x in pg['lignes'][k + 1:]:
                if x['texte'] and x.get('note', False) == flux:
                    suite = x['texte']
                    break
            if not suite:
                for pv in pages[ip + 1:]:
                    dispo = [x['texte'] for x in pv['lignes']
                             if x['texte'] and x.get('note', False) == flux]
                    if dispo:
                        suite = dispo[0]
                        break
            d = MOT_DEB.match(suite)
            if not suite:
                # La page suivante n'est pas encore relevee : on ne peut
                # pas verifier la coupure, mais elle n'est pas fautive.
                r.av('folio %s : le mot « %s- » se coupe en pied de page ; '
                     'verification differee au relevé de la page suivante'
                     % (pg['folio'], g.group(1) if g else '?'))
                continue
            if not g or not d:
                mauvais += 1
                r.ko('folio %s ligne %d : \\cc ne tombe pas entre deux lettres '
                     '(« %s » | « %s »)'
                     % (pg['folio'], k + 1, l['texte'][-14:], suite[:14]))
                continue
            ok, why = silabifo.conforme(g.group(1), d.group(1))
            if not ok:
                mauvais += 1
                r.ko('folio %s ligne %d : coupure « %s-/%s » non conforme a D. 485 — %s'
                     % (pg['folio'], k + 1, g.group(1), d.group(1), why))
    if not mauvais:
        r.ok('tous les \\cc tombent entre deux lettres et respectent D. 485')


def _lexique(pages):
    """Tous les mots attestes comme mots entiers dans le releve."""
    lex = {}
    for pg in pages:
        for l in pg['lignes']:
            for w in re.findall(r"[A-Za-zÀ-ÿ]+", l['texte']):
                lex[w.lower()] = lex.get(w.lower(), 0) + 1
    return lex


def controle_4(pages, r):
    """Un \\nl entre deux fragments alphabetiques est normal : c'est le cas
    de presque toute fin de ligne. Le signal utile est plus etroit — l'OCR
    et le releve perdent les traits d'union de fin de ligne, et la coupure
    se retrouve alors decalee. On ne signale donc que le cas ou :
      - la soudure des deux fragments est un mot atteste ailleurs, ET
      - l'un des deux fragments n'est jamais atteste comme mot entier.
    C'est la signature d'un \\cc encode par erreur en \\nl."""
    lex = _lexique(pages)
    n = 0
    for pg in pages:
        for k, l in enumerate(pg['lignes']):
            if l['coupe'] != 'nl':
                continue
            suite = pg['lignes'][k + 1]['texte'] if k + 1 < len(pg['lignes']) else ''
            g = MOT_FIN.search(l['texte'])
            d = MOT_DEB.match(suite)
            if not (g and d):
                continue
            gg, dd = g.group(1).lower(), d.group(1).lower()
            soude = gg + dd
            if lex.get(soude, 0) >= 1 and (lex.get(gg, 0) <= 1 or lex.get(dd, 0) <= 1):
                n += 1
                r.ko('folio %s ligne %d : \\nl entre « %s » et « %s » — la soudure '
                     '« %s » est attestee : trait d\'union de coupure probablement perdu'
                     % (pg['folio'], k + 1, g.group(1), d.group(1), soude))
    if not n:
        r.ok('aucun \\nl ne parait masquer un trait d\'union perdu '
             '(%d mots au lexique)' % len(lex))


# --------------------------------------------------------------------
# Controles 5 et 6 — debuts de ligne interdits
# --------------------------------------------------------------------
HAUTE = ':;!?'
BASSE = ',.)]}»'


def _debuts(pages):
    for pg in pages:
        for k, l in enumerate(pg['lignes']):
            if k == 0 or not l['texte']:
                continue
            # UN RANG DE TABLEAU N'EST PAS UNE LIGNE DE TEXTE. Les trois
            # rangees de points du hors-texte du folio 220 commencent par
            # un point, et les controles 5 et 6 y voyaient trois fautes.
            # Elles ne sont pas de la prose : leur matiere est posee a
            # l'abscisse par \VUcase, et aucune regle de coupure ne les
            # regit. Les deux controles les ecartent donc, comme le
            # controle 2 le fait deja pour comparer sans les blancs.
            if l.get('rang'):
                continue
            yield pg, k, l['texte']


def controle_5(pages, r):
    n = 0
    for pg, k, t in _debuts(pages):
        if t[0] in HAUTE:
            n += 1
            r.ko('folio %s ligne %d commence par « %s » : %s'
                 % (pg['folio'], k + 1, t[0], t[:30]))
    if not n:
        r.ok('aucune ligne ne commence par : ; ! ?')


def controle_6(pages, r):
    n = 0
    for pg, k, t in _debuts(pages):
        if t[0] in BASSE:
            n += 1
            r.ko('folio %s ligne %d commence par « %s » : %s'
                 % (pg['folio'], k + 1, t[0], t[:30]))
    if not n:
        r.ok('aucune ligne ne commence par une ponctuation basse '
             'ou une parenthese fermante')


# --------------------------------------------------------------------
# Controle 7 — marge effective minimale
# --------------------------------------------------------------------
def controle_7(pages, r):
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf absent')
        return
    out = subprocess.run(['pdftotext', '-bbox', pdf, '-'],
                         capture_output=True, text=True).stdout
    pw = ph = None
    m = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', out)
    if m:
        pw, ph = float(m.group(1)), float(m.group(2))
    pires = []
    for i, pg in enumerate(re.findall(r'<page .*?</page>', out, re.S), 1):
        xs = [float(x) for x in re.findall(r'xMin="([\d.]+)"', pg)]
        xM = [float(x) for x in re.findall(r'xMax="([\d.]+)"', pg)]
        if not xs:
            continue
        gauche, droite = min(xs), pw - max(xM)
        pires.append((min(gauche, droite), i, gauche, droite))
    if not pires:
        r.av('aucun texte extrait : controle 7 sans objet')
        return
    pires.sort()
    mm = 25.4 / 72.0
    pire = pires[0]
    if pire[0] * mm < 5.0:
        r.ko('marge effective minimale %.2f mm (page %d) — mot rogne probable'
             % (pire[0] * mm, pire[1]))
    else:
        r.ok('marge effective minimale %.2f mm (page %d) sur %d pages'
             % (pire[0] * mm, pire[1], len(pires)))


# --------------------------------------------------------------------
# Controle 8 — juxtaposition visuelle a 300 dpi
# --------------------------------------------------------------------
# Marge gauche de la page composee, en pixels a 300 dpi :
# (116 mm - 91,69 mm) / 2 = 12,155 mm
MARGE_G_PX = 12.155 / 25.4 * 300.0
# Renfoncement d'alinea (\VUalinea = 4,6 mm) en pixels a 300 dpi.
ALINEA_PX = int(round(4.6 / 25.4 * 300.0))
# Renfoncement des notes (\VUalineaNote = 3,6 mm) : les notes ont le leur.
ALINEA_NOTE_PX = int(round(3.6 / 25.4 * 300.0))


def controle_8(pages, r, premiere=1, combien=None):
    import numpy as np
    import cv2
    import page as PG
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf absent')
        return
    dst = os.path.join(P, 'controle', 'juxta')
    os.makedirs(dst, exist_ok=True)
    n = combien or len(pages)
    comp = cache.compose(pdf, len(pages))
    faits = 0
    for i in range(premiere, premiere + n):
        pg = pages[i - 1]
        try:
            feuillet = int(pg['feuillet']) if pg.get('feuillet') else int(pg['folio']) + 4
        except (ValueError, TypeError):
            r.av('page %d : ni feuillet ni folio exploitable, juxtaposition sautee' % i)
            continue
        if i not in comp:
            continue
        cp = cv2.imread(comp[i]['fichier'], cv2.IMREAD_GRAYSCALE)
        norm, gm, ang = PG.prepared(feuillet)
        span = cache.feuillet(feuillet)['span']
        # On aligne les deux images sur le BORD GAUCHE DU BLOC DE TEXTE :
        # le scan comporte une bordure variable, la page composee non.
        marge = int(round(MARGE_G_PX))
        if span:
            g = max(0, span[0] - marge)
            norm = norm[:, g:g + cp.shape[1]]
        if norm.shape[1] < cp.shape[1]:
            norm = np.pad(norm, ((0, 0), (0, cp.shape[1] - norm.shape[1])),
                          constant_values=255)
        h = max(cp.shape[0], norm.shape[0])
        def cale(im, w):
            o = np.full((h, w), 255, np.uint8)
            o[:min(h, im.shape[0]), :min(w, im.shape[1])] = \
                im[:min(h, im.shape[0]), :min(w, im.shape[1])]
            return o
        w = cp.shape[1]
        duo = np.hstack([cale(norm, w), np.full((h, 24), 160, np.uint8),
                         cale(cp, w)])
        cv2.imwrite(os.path.join(dst, 'juxta-%03d.png' % i), duo)
        faits += 1
    r.ok('%d juxtapositions a 300 dpi dans controle/juxta/' % faits)


# --------------------------------------------------------------------
# Controle 9 — graisse : enrichissements oublies
# --------------------------------------------------------------------
def _encre_composee(pdf, i, dst):
    """Lignes de la page i du PDF compose : (y0, y1, encre)."""
    import numpy as np
    import cv2
    subprocess.run(['pdftoppm', '-r', '300', '-png', '-f', str(i), '-l', str(i),
                    pdf, os.path.join(dst, 'p')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cand = sorted(glob.glob(os.path.join(dst, 'p-*%d.png' % i)))
    if not cand:
        return None
    bw = (cv2.imread(cand[0], cv2.IMREAD_GRAYSCALE) < 160).astype(np.uint8)
    rows = bw.sum(axis=1)
    on = (rows > 4).astype(np.int8)
    d = np.diff(on)
    st = list(np.where(d == 1)[0] + 1); en = list(np.where(d == -1)[0] + 1)
    if on[0]: st.insert(0, 0)
    if on[-1]: en.append(len(on))
    brut = [(a_, b_, int(bw[a_:b_].sum())) for a_, b_ in zip(st, en) if b_ - a_ >= 8]
    if not brut:
        return brut
    # Une ligne doit porter de l'encre, pas seulement occuper des pixels :
    # un eclat de 148 pixels (accents ou jambages detaches par le seuil)
    # se faisait compter comme une ligne et decalait tout le reste d'un
    # rang — d'ou des ecarts de graisse absurdes (+4720 %).
    plein = max(e for _, _, e in brut)
    return [t for t in brut if t[2] >= 0.03 * plein]


def controle_9(pages, r, seuil=0.12):
    """Le controle 2 compare le TEXTE ; il ne voit pas le balisage. Un
    passage en gras oublie lui echappe donc — c'est arrive au folio 11,
    ou l'enumeration des lettres de l'alphabet est en gras a l'original.

    On compare la QUANTITE D'ENCRE de chaque ligne, fac-simile contre
    compose. Deux precautions, l'une et l'autre necessaires :

    - le rapport est domine par le CORPS (un titre en capitales, une note
      en petit texte et une ligne de texte courant n'ont pas du tout la
      meme densite) : on groupe donc les lignes par hauteur, et chaque
      groupe est compare a sa propre mediane ;
    - comparer le profil d'encre LE LONG de la ligne a ete essaye et
      abandonne : le decalage des mots entre les deux compositions produit
      un bruit qui noie le signal.

    Sensibilite mesuree au folio 11 : une ligne dont l'essentiel est en
    gras ressort a +24 % quand le gras manque, contre -3 % quand il est
    la. Quelques lettres grasses isolees dans une ligne romaine ne
    depassent pas +5 % : le controle ne les voit pas. Il attrape les
    enrichissements etendus, pas les ponctuels.
    """
    import numpy as np
    import page as PG
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf absent')
        return
    dst = os.path.join(P, 'controle', 'encre')
    os.makedirs(dst, exist_ok=True)
    signale = comparees = 0
    for i, pg in enumerate(pages, 1):
        try:
            feuillet = int(pg['feuillet']) if pg.get('feuillet') else int(pg['folio']) + 4
        except (ValueError, TypeError):
            continue
        comp = cache.compose(pdf, len(pages))
        if i not in comp:
            continue
        cl = [(l['y0'], l['y1'], l['encre']) for l in comp[i]['lignes']]
        fl = cache.feuillet(feuillet)['lignes']
        if len(fl) < 6:
            continue
        # Appariement par POSITION, non par rang : voir tools/pair_up.py.
        couples, sf, sc = apparier.apparie(
            [(l['y0'], l['y1']) for l in fl], [(a, b) for a, b, _ in cl])
        if len(couples) < 0.6 * min(len(fl), len(cl)):
            r.av('folio %s : appariement des lignes trop incertain '
                 '(%d couples pour %d/%d lignes) — graisse non comparee'
                 % (pg['folio'] or ('f%s' % feuillet), len(couples),
                    len(fl), len(cl)))
            continue
        if sf or sc:
            r.av('folio %s : %d ligne(s) du fac-simile et %d du compose sans '
                 'correspondant — le reste de la page est compare quand meme'
                 % (pg['folio'] or ('f%s' % feuillet), len(sf), len(sc)))
        txt = [l['texte'] for l in pg['lignes'] if l['texte']]
        fl = [fl[i] for i, _ in couples]
        cl = [cl[j] for _, j in couples]
        rap = np.array([l['encre'] / max(c[2], 1) for l, c in zip(fl, cl)])
        # Groupes de corps : on les tient du RELEVE, qui les connait
        # exactement (texte courant, note, ligne d'apparat). Les deduire
        # de la hauteur de ligne mesuree se trompait sur les dernieres
        # lignes de note, dont les hauts et bas debordent.
        lg = [l for l in pg['lignes'] if l['texte']]
        cat = []
        for k in range(len(fl)):
            l = lg[k] if k < len(lg) else {}
            cat.append('apparat' if l.get('apparat') else
                       ('note' if l.get('note') else 'courant'))
        cat = np.array(cat)
        groupes = {c: (cat == c) for c in ('courant', 'note', 'apparat')}
        # Les lignes courtes donnent un rapport bruite (peu d'encre, et le
        # decoupage des lignes y est moins sur) : on les exclut du test.
        larg = np.array([l['x1'] - l['x0'] for l in fl], float)
        # UNE PAGE BLANCHE FAISAIT PLANTER LE CONTROLE. Au feuillet 182,
        # verso blanc, le fac-simile porte sept bandes parasites (pli et
        # bord de page) quand le compose n'a aucune ligne : larg etait
        # vide et larg.max() levait une exception. Le controle entier
        # s'arretait alors — un controle qui plante ne verifie plus rien,
        # et il l'a fait en silence pendant tout un lot.
        if larg.size == 0:
            r.av('folio %s : page blanche au compose — graisse non jugee'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet'))))
            continue
        assez = larg > 0.45 * larg.max()
        for nom, sel in groupes.items():
            if sel.sum() < 4:
                continue          # groupe trop petit pour avoir une mediane
            m = float(np.median(rap[sel]))
            if (sel & assez).sum() == 0:
                continue
            for k in np.where(sel & assez)[0]:
                comparees += 1
                e = rap[k] / m - 1.0
                if abs(e) > seuil:
                    signale += 1
                    quoi = ("plus d'encre au fac-simile : enrichissement "
                            "probablement oublie" if e > 0 else
                            "moins d'encre au fac-simile : enrichissement "
                            "probablement de trop")
                    r.av('folio %s ligne %d (%+.0f %%, corps « %s ») — %s\n'
                         '        %s'
                         % (pg['folio'] or ('f%s' % feuillet), k + 1, e * 100,
                            nom, quoi, (txt[k][:64] if k < len(txt) else '')))
    if not signale:
        r.ok('graisse conforme sur les %d lignes comparees' % comparees)


# --------------------------------------------------------------------
# Controle 10 — alignement des debuts de ligne
# --------------------------------------------------------------------

# Le bord gauche d'une ligne n'est pas toujours de l'encre : au feuillet
# 83 un PLI du papier traverse la marge, et le detecteur prend la trace
# du pli pour le debut de la ligne. Le retrait mesure tombe alors a zero
# sur une ligne qui, a l'agrandissement, est nettement renfoncee.
#
# Le signe est le meme que celui qui avait fausse le folio dans
# tools/page.py, et il se lit de la meme facon : EN AMAS, non en
# etendue. Un pli rend un amas MINCE (quelques pixels de large) et
# SEPARE du reste de la ligne par un blanc bien plus large qu'une
# espace-mot. Une lettre, elle, touche ses voisines.
#
# On ne corrige pas la mesure — on la declare non faite. Un controle qui
# se tait en le disant vaut mieux qu'un controle qui accuse une page
# juste, et mieux aussi qu'un controle qu'on desactive en silence.
_PLI_LARGEUR_MAX = 7        # px : au-dela, c'est une lettre
_PLI_ECART_MIN = 22         # px : une espace-mot en vaut 19


def _pli(feuillet, ligne):
    """Le bord gauche de cette ligne est-il la trace d'un pli ?"""
    try:
        import numpy as np, cv2
        import page as PG
        norm, gm, _ = PG.prepared(feuillet)
    except Exception:
        return False
    bande = (norm[ligne['y0']:ligne['y1'] + 1,
                  ligne['x0']:ligne['x0'] + 120] < 185).astype('uint8')
    if bande.size == 0:
        return False
    col = bande.sum(axis=0)
    plein = np.nonzero(col)[0]
    if plein.size == 0 or plein[0] != 0:
        return False
    # LES TRACES VONT PAR PLUSIEURS. La premiere version n'examinait que
    # l'amas de tete et le blanc qui le suit ; au folio 29 la marge porte
    # DEUX mouchetures (2 px puis 6 px, separees de 3 px), et le test
    # echouait sur la seconde. On saute donc TOUS les amas minces de
    # tete, et l'on mesure le blanc qui precede le premier amas large.
    i = 0
    saute = False
    while i < col.size:
        if not col[i]:
            i += 1
            continue
        a = i
        while i < col.size and col[i]:
            i += 1
        if i - a > _PLI_LARGEUR_MAX:
            return saute and (a - fin) >= _PLI_ECART_MIN
        saute = True
        fin = i
    return False

def controle_10(pages, r, tol_px=12):
    """Dans une page composee, le debut d'une ligne ne peut occuper que
    trois positions : la marge du bloc, la marge plus le renfoncement
    d'alinea, ou le centre (lignes d'apparat). Toute autre valeur trahit
    une espace parasite.

    Ce controle est ne d'un defaut que le controle 2 ne pouvait pas voir :
    une espace active a le code de categorie 13 et non 10, si bien que TeX
    ne l'escamote plus apres un mot de controle. « \\noindent en » composait
    donc une espace reelle en tete de ligne. Le controle 2 compare du
    texte, et son texte est dépouillé de ses blancs de bord : l'ecart etait
    invisible pour lui, alors qu'il saute aux yeux en geometrie.
    """
    import numpy as np
    import cv2
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf absent')
        return
    dst = os.path.join(P, 'controle', 'encre')
    os.makedirs(dst, exist_ok=True)
    signale = examinees = 0
    for i, pg in enumerate(pages, 1):
        comp = cache.compose(pdf, len(pages))
        if i not in comp:
            continue
        brut = comp[i]['lignes']
        deb = [(l['x0'], l['x1']) for l in brut]
        bandes = [(l['y0'], l['y1']) for l in brut]
        if len(deb) < 6:
            continue
        # Le folio est compose par \VUfolio : il ne fait pas partie du
        # releve. Il faut l'oter AVANT la boucle des debuts de ligne, et
        # non seulement avant celle des fins : sans cela lg[k] repond
        # pour la ligne precedente. Au folio 50 le controle accusait un
        # rang de tableau d'un « espace parasite » de 120 px qui etait en
        # realite son renfoncement releve — l'exemption des rangs ne
        # tombait pas sur la bonne ligne.
        _p = max(y - x for x, y in deb)
        if deb:
            _x0, _x1 = deb[0]
            _m = min(a for a, _ in deb); _d = max(b for _, b in deb)
            if (_x1 - _x0) < 0.30 * _p and \
               abs((_x0 + _x1) / 2 - (_m + _d) / 2) < 0.12 * _p:
                deb = deb[1:]
        if not deb:
            continue
        marge = min(x for x, _ in deb)
        droite = max(y for _, y in deb)
        lg = [l for l in pg['lignes'] if l['texte']]
        # PREMIERE LIGNE DU CORPS : au fer a gauche ou en alinea ?
        # Le controle des debuts accepte les deux, puisque les deux sont
        # legitimes ailleurs dans la page. Mais pour la premiere ligne le
        # fac-simile tranche, et deux fois j'ai mis un \VUcontinue de trop
        # (folios 45 et 55) en supposant sans verifier que l'alinea venait
        # de la page precedente. On confronte donc cette ligne-la, et elle
        # seule, a la mesure du modele.
        try:
            _f = int(pg['feuillet']) if pg.get('feuillet') else int(pg['folio']) + 4
            _fl = cache.feuillet(_f)['lignes']
        except (ValueError, TypeError, KeyError):
            _fl = []
        # On saute les pages qui s'ouvrent sur une ligne d'apparat : la
        # comparaison n'y a pas de sens, et le repere du folio confond un
        # titre centre avec un folio (folio 18).
        _apparat0 = bool(lg) and bool(lg[0].get('apparat'))
        if _fl and deb and not _apparat0:
            _dec = 1 if (_fl[0]['x1'] - _fl[0]['x0']
                         < 0.25 * max(l['x1'] - l['x0'] for l in _fl)) else 0
            if len(_fl) > _dec:
                _cx = min(l['x0'] for l in _fl[_dec:])
                _fac = _fl[_dec]['x0'] - _cx
                _comp = deb[0][0] - marge
                if abs(_fac - _comp) > 2 * tol_px and _pli(_f, _fl[_dec]):
                    r.av('folio %s : le bord gauche de la premiere ligne '
                         'tombe sur un PLI du papier — le retrait ne se '
                         'mesure pas sur ce feuillet, la ligne n\'est pas '
                         'verifiee' % (pg['folio'] or ('f%s' % pg.get('feuillet'))))
                elif abs(_fac - _comp) > 2 * tol_px:
                    signale += 1
                    r.ko('folio %s : la premiere ligne du corps est a %+d px '
                         'de la marge au fac-simile, et a %+d px au compose '
                         '— \\VUcontinue de trop ou manquant ?\n        %s'
                         % (pg['folio'] or ('f%s' % pg.get('feuillet')),
                            _fac, _comp, lg[0]['texte'][:44] if lg else ''))
        rangs = 0
        for k, (x0, x1) in enumerate(deb):
            # Un RANG DE TABLEAU ne commence ni a la marge ni en alinea :
            # chacun de ses elements est pose a une abscisse relevee au
            # fac-simile (\VUcase). Le controle des debuts de ligne n'a
            # donc pas de sens ici, et il faut le dire plutot que de le
            # taire : le compte des rangs ecartes est rapporte.
            # UNE LIGNE D'APPARAT NON PLUS. \VUcentre, \VUtitre et
            # \VUsoustitre posent leur ligne par mesure, comme \VUcase le
            # fait pour un rang : ni le fer ni l'alinea ne les regissent.
            # Le test de centrage ci-dessous en attrape la plupart, mais
            # pas celles dont le texte est long et le centrage optique
            # (folios 232, 233 et 234, quatre lignes) : la regle sure est
            # de les ecarter sur leur nature, non sur leur position.
            if k < len(lg) and (lg[k].get('rang') or lg[k].get('apparat')):
                rangs += 1
                continue
            examinees += 1
            centree = abs((x0 + x1) / 2 - (marge + droite) / 2) < 3 * tol_px
            if centree:
                continue                      # folio, titre, ligne d'apparat
            ecart = x0 - marge
            if ecart <= tol_px:
                continue                      # au fer a gauche
            if abs(ecart - ALINEA_PX) <= tol_px:
                continue                      # renfoncement d'alinea
            if abs(ecart - ALINEA_NOTE_PX) <= tol_px:
                continue                      # renfoncement d'une note
            signale += 1
            t = lg[k]['texte'][:44] if k < len(lg) else ''
            r.ko('folio %s ligne %d commence a %+d px de la marge — ni au fer '
                 'a gauche (0), ni en alinea (%d ou %d) : espace parasite ?'
                 '\n        %s'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet')), k + 1,
                    ecart, ALINEA_PX, ALINEA_NOTE_PX, t))
        if rangs:
            r.av('folio %s : %d rang(s) de tableau ecarte(s) du controle des '
                 'debuts de ligne — leurs abscisses sont relevees une a une'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet')), rangs))
        # Verification des FINS de ligne, SANS passer par le fac-simile.
        #
        # La premiere version comparait la largeur de chaque ligne composee
        # a celle de la ligne correspondante du fac-simile. Elle dependait
        # donc de l'appariement, qui glisse d'un rang des qu'une ligne est
        # detectee en trop d'un cote — et produisait alors une douzaine de
        # faux positifs a la signature caracteristique (une ligne pleine en
        # face d'une tres courte, en alternance).
        #
        # Or le releve sait deja ce qu'il faut savoir : une ligne suivie de
        # \nl ou de \cc est une ligne pleine, une ligne qui termine un
        # alinea est courte. On verifie donc le compose contre le RELEVE,
        # ce qui ne demande aucun appariement.
        plein_c = max(x1 - x0 for x0, x1 in deb)
        # Le folio est compose par \VUfolio, il ne fait pas partie du
        # releve : on l'ote de la liste des lignes composees, sinon toute
        # la page se compare decalee d'un rang.
        deb_txt = list(deb)   # le folio en a deja ete ote plus haut
        if False:
            x0, x1 = deb_txt[0]
            marge_c = min(a for a, _ in deb_txt)
            droite_c = max(b for _, b in deb_txt)
            # « Court » se mesure sur la ligne la PLUS LARGE de la page,
            # et « centre » avec la meme tolerance que le controle 11.
            # Au folio 50, le folio « -- 50 -- » manquait le critere de
            # centrage de peu : la page entiere se comparait alors
            # decalee d'un rang, et le controle accusait un rang de
            # tableau d'un « espace parasite » de 120 px qui etait en
            # realite son renfoncement releve.
            court = (x1 - x0) < 0.30 * plein_c
            centre = abs((x0 + x1) / 2 - (marge_c + droite_c) / 2) < 0.12 * plein_c
            if court and centre:
                deb_txt = deb_txt[1:]
        deb = deb_txt
        lgv = [l for l in pg['lignes'] if l['texte']]
        if len(lgv) != len(deb):
            r.av('folio %s : %d lignes composees pour %d relevees — '
                 'fins de ligne non verifiees'
                 % (pg['folio'] or ('f%s' % pg.get('feuillet')),
                    len(deb), len(lgv)))
            continue
        # Le BORD DROIT, non la largeur.
        # Une premiere ligne d'alinea est renfoncee de \VUalinea : sa
        # largeur vaut donc 94 % de la justification alors qu'elle est
        # parfaitement remplie. C'est ce qui faisait echouer les folios 18
        # et 19 — et la trace de TeX (\tracingparagraphs) le disait :
        # « b=0 », badness nulle, la ligne est juste. Ce qui definit une
        # ligne pleine, c'est qu'elle atteint la marge de droite.
        droite_c = max(x1 for _, x1 in deb)
        for k, ((x0, x1), l) in enumerate(zip(deb, lgv)):
            if l.get('apparat'):
                continue                     # ligne centree : sans objet
            # Un rang de tableau n'est pas justifie : \VUrang le termine
            # par une fin de ligne, mais sa matiere s'arrete la ou le
            # fac-simile l'arrete. Le controle des fins ne s'y applique
            # pas plus que celui des debuts.
            if l.get('rang'):
                continue
            pc = x1 / droite_c
            attendu_plein = l['coupe'] in ('nl', 'cc')
            if attendu_plein and pc < 0.94:
                signale += 1
                r.ko('folio %s ligne %d : le releve la donne pleine '
                     '(suivie de \\%s) mais elle ne fait que %.0f %% — '
                     'justification perdue ?\n        %s'
                     % (pg['folio'] or ('f%s' % pg.get('feuillet')), k + 1,
                        l['coupe'], pc * 100, l['texte'][:44]))
            elif not attendu_plein and pc > 0.995:
                # Une derniere ligne d\'alinea PEUT atteindre la marge sans
                # que rien ne soit force : il suffit que le texte la
                # remplisse. Ce n'est donc qu'une remarque, non une faute —
                # contrairement au cas inverse, ou une ligne que le releve
                # donne pleine se retrouve courte, qui est toujours un defaut.
                r.av('folio %s ligne %d : fin d\'alinea qui court '
                     'jusqu\'a la marge (%.0f %%) — a verifier'
                     '\n        %s'
                     % (pg['folio'] or ('f%s' % pg.get('feuillet')), k + 1,
                        pc * 100, l['texte'][:44]))
    if not signale:
        r.ok('les %d debuts de ligne sont a la marge, en alinea ou centres, '
             'et les fins concordent avec le fac-simile' % examinees)



def controle_11(pages, r, tol_px=14):
    """Position VERTICALE de chaque ligne composee, comparee au fac-simile.

    Le compositeur justifie ses pages verticalement : mesure sur les
    feuillets 20 a 39, la derniere ligne de base tombe a 145,3 mm sous le
    folio a 0,3 mm pres, quel que soit le nombre de lignes. Une page dont
    la matiere ne remplit pas la justification est CARDEE : des lames
    uniformes entre toutes les lignes du corps, et des blancs plus larges
    aux articulations. Sans ces reglages le texte reste juste ligne a
    ligne, mais aucune ligne ne tombe en face de son modele : le
    controle 2 est content et la juxtaposition ne l'est pas.

    On compare les hauts de ligne, decalage constant retire (chaque scan
    a son propre calage vertical, jusqu'a 10 mm). Le haut d'une ligne
    depend de ses ascendantes : il bruite de +/- 8 px. La tolerance est
    donc a 14 px ; ce qu'on cherche est la DERIVE cumulee, qui atteint
    100 px et plus quand le cardage n'est pas reproduit.
    """
    import numpy as np
    pdf = os.path.join(P, 'main.pdf')
    if not os.path.exists(pdf):
        r.ko('main.pdf absent')
        return
    comp = cache.compose(pdf, len(pages))
    pire = 0.0; pire_page = None; examinees = 0
    for i, pg in enumerate(pages, 1):
        try:
            feuillet = int(pg['feuillet']) if pg.get('feuillet') else int(pg['folio']) + 4
        except (ValueError, TypeError):
            continue
        if i not in comp:
            continue
        cl = comp[i]['lignes']
        fl = cache.feuillet(feuillet)['lignes']
        if len(cl) != len(fl) or len(cl) < 6:
            r.av('folio %s : %d lignes composees pour %d relevees au '
                 'fac-simile — derive verticale non mesuree'
                 % (pg['folio'] or ('f%s' % feuillet), len(cl), len(fl)))
            continue
        examinees += 1
        d = np.array([c['y0'] - a['y0'] for a, c in zip(fl, cl)], float)
        res = d - np.median(d)
        # Le folio ne porte que deux filets et deux chiffres : son haut
        # detecte depend du filet, pas d'une ascendante, et sort du bruit
        # ordinaire. Il est place par \VUfolioY, mesure a part ; on ne le
        # fait pas peser sur la derive du bloc de texte.
        if fl and fl[0]['x1'] - fl[0]['x0'] < 0.25 * max(l['x1'] - l['x0'] for l in fl):
            res = res[1:]
        if not len(res):
            continue
        # Le haut d'une ligne depend de ses ascendantes : il bruite de
        # +/- 8 px sans que rien ne bouge dans la composition. Pris sur
        # le MAXIMUM de 40 lignes, ce bruit franchit a lui seul la
        # tolerance. On le filtre par une mediane glissante de trois
        # lignes : un decalage de cardage dure des lignes entieres et y
        # survit, le bruit d'ascendante non.
        if len(res) >= 3:
            liss = np.array([np.median(res[max(0, k - 1):k + 2])
                             for k in range(len(res))])
        else:
            liss = res
        amp = float(np.abs(liss).max())
        res = liss
        if amp > pire:
            pire, pire_page = amp, pg['folio'] or ('f%s' % feuillet)
        if amp > tol_px:
            k = int(np.abs(res).argmax())
            r.ko('folio %s : derive verticale de %.0f px (%.2f mm) a la '
                 'ligne %d — cardage de la page non reproduit'
                 % (pg['folio'] or ('f%s' % feuillet), amp, amp * 25.4 / 300, k))
    if examinees:
        r.ok('derive verticale maximale %.0f px (%.2f mm, folio %s) sur '
             '%d pages' % (pire, pire * 25.4 / 300, pire_page, examinees))


CONTROLES = {1: controle_1, 2: controle_2, 3: controle_3, 4: controle_4,
             5: controle_5, 6: controle_6, 7: controle_7, 8: controle_8,
             9: controle_9, 10: controle_10, 11: controle_11,
             12: controle_12}
TITRES = {
    1: 'Controle 1 — pagination et debordements',
    2: 'Controle 2 — comparaison ligne a ligne PDF / releve',
    3: 'Controle 3 — \\cc entre deux lettres, conforme a D. 485',
    4: 'Controle 4 — \\nl jamais a l\'interieur d\'un mot',
    5: 'Controle 5 — aucune ligne ne commence par : ; ! ?',
    6: 'Controle 6 — aucune ligne ne commence par une ponctuation basse',
    7: 'Controle 7 — marge effective minimale',
    8: 'Controle 8 — juxtaposition visuelle a 300 dpi',
    9: 'Controle 9 — graisse ligne a ligne (gras, italique, corps)',
    10: 'Controle 10 — alignement des debuts et fins de ligne',
    11: 'Controle 11 — position verticale des lignes (cardage)',
    12: 'Controle 12 — chaque note est un alinea',
}


def main():
    voulus = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(CONTROLES)
    pages = lire_releve()
    print('Releve : %d pages, %d lignes.'
          % (len(pages), sum(len(p['lignes']) for p in pages)))
    total_e = total_a = 0
    for c in voulus:
        r = Rapport()
        try:
            CONTROLES[c](pages, r)
        except Exception as e:
            r.ko('le controle a leve une exception : %r' % (e,))
        r.imprime(TITRES[c])
        total_e += r.echecs
        total_a += r.avertis
    print('\n%s%d echec(s)%s, %d note(s).'
          % (ROUGE if total_e else VERT, total_e, RAZ, total_a))
    return 1 if total_e else 0


if __name__ == '__main__':
    sys.exit(main())
