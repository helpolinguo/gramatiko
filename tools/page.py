#!/usr/bin/env python3
"""Preparation d'une page du fac-simile et reperage du bloc de texte.

Le recadrage sur "la zone claire" est trompeur : la tranche des feuillets
voisins est claire elle aussi, et l'ombre de la reliure mange un bord.
On repere donc le bloc de texte par les GLYPHES eux-memes : composantes
connexes de taille compatible avec des caracteres de corps ~10 pt a 300 dpi.
"""
import os, sys, json
import numpy as np
import cv2

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(P, 'scan', 'pages')
DPI = 300.0
PX2MM = 25.4 / DPI
PX2PT = 72.27 / DPI      # point TeX
PX2BP = 72.0 / DPI       # point PostScript


def normalise(gray):
    """Egalise le fond (papier jauni, ombre de reliure)."""
    small = cv2.resize(gray, None, fx=0.08, fy=0.08, interpolation=cv2.INTER_AREA)
    bg = cv2.medianBlur(small, 31)
    bg = cv2.resize(bg, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_CUBIC)
    n = gray.astype(np.float32) / np.maximum(bg.astype(np.float32), 1.0) * 210.0
    return np.clip(n, 0, 255).astype(np.uint8)


def glyph_mask(norm):
    """Masque binaire ne gardant que les composantes de taille de glyphe."""
    bw = cv2.threshold(norm, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(bw, 8)
    keep = np.zeros(nlab, np.uint8)
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        if 3 <= h <= 70 and 2 <= w <= 90 and a >= 8 and a <= 3000 and w / max(h, 1) < 12:
            keep[i] = 1
    return keep[lab] * 255


def deskew(norm, gm):
    """Angle par maximisation du contraste de la projection horizontale."""
    s = cv2.resize(gm, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    h, w = s.shape
    best, ba = -1.0, 0.0
    for a in np.arange(-2.5, 2.51, 0.05):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), float(a), 1.0)
        r = cv2.warpAffine(s, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=0)
        pr = r.sum(axis=1).astype(np.float64)
        sc = float(((pr[1:] - pr[:-1]) ** 2).sum())
        if sc > best:
            best, ba = sc, float(a)
    H, W = norm.shape
    M = cv2.getRotationMatrix2D((W / 2, H / 2), ba, 1.0)
    rot = cv2.warpAffine(norm, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=255)
    rotg = cv2.warpAffine(gm, M, (W, H), flags=cv2.INTER_NEAREST, borderValue=0)
    return rot, rotg, ba


def prepared(n):
    """Image normalisee + masque de glyphes, tout desincline. Aucun recadrage."""
    g = cv2.imread(os.path.join(PAGES, 'f%04d.jpg' % n), cv2.IMREAD_GRAYSCALE)
    norm = normalise(g)
    gm = glyph_mask(norm)
    return deskew(norm, gm)


def text_region(gm):
    """Isole le bloc de texte : on soude les glyphes en lignes, puis on garde
    les composantes larges et basses (une ligne de texte). Les tranches des
    feuillets voisins donnent des composantes hautes et etroites : rejetees."""
    H, W = gm.shape
    # --- Colonne de texte etablie AVANT la soudure -----------------------
    # La soudure (61, 3) comble les blancs de moins de 61 px. Au bord droit
    # du feuillet 34, la tranche du feuillet voisin laisse des eclats a
    # 38 px du dernier caractere : la soudure les agglomere a la ligne, la
    # composante s'etend jusqu'au bord de l'image, et TOUTES les bornes
    # calculees ensuite (percentiles, clippage) heritent du bruit. Il faut
    # donc borner la colonne avant de souder.
    # Critere de densite : une colonne de pixels a l'interieur du bloc de
    # texte est traversee par presque toutes les lignes ; un eclat de
    # tranche n'en touche que quelques-unes. Mesure sur 34 feuillets
    # repartis dans le volume : la largeur trouvee vaut 1083 px sur la
    # grande majorite d'entre eux, soit exactement \VUtexteLargeur
    # (91,69 mm a 300 dpi) — la borne est donc juste, et non seulement
    # plausible.
    _col = (gm > 0).sum(axis=0)
    if _col.max() > 0:
        _thr = max(3.0, 0.15 * np.percentile(_col, 90))
        _xs = np.nonzero(_col > _thr)[0]
        if len(_xs):
            _runs = []
            _s = _p = _xs[0]
            for _x in _xs[1:]:
                # 40 px : au feuillet 34 les eclats de tranche sont a 40 px
                # du dernier caractere ; une valeur plus large les rattache
                # a la colonne et annule tout le benefice. Verifie sur 34
                # feuillets : aucune colonne legitime n'est scindee, y
                # compris celle du tableau du feuillet 35.
                if _x - _p > 40:
                    _runs.append((_s, _p)); _s = _x
                _p = _x
            _runs.append((_s, _p))
            _c0, _c1 = max(_runs, key=lambda r: r[1] - r[0])
            # 12 px de battement : de quoi laisser passer un trait d'union
            # ou une virgule en debord sans laisser rentrer la tranche.
            gm = gm.copy()
            gm[:, :max(0, _c0 - 12)] = 0
            gm[:, min(W, _c1 + 13):] = 0
    band = cv2.morphologyEx(gm, cv2.MORPH_CLOSE, cv2.getStructuringElement(
        cv2.MORPH_RECT, (61, 3)))
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats((band > 0).astype(np.uint8), 8)
    keep = np.zeros((H, W), np.uint8)
    boxes = []
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        # Les bords de l'image sont du bruit de numerisation (bord du
        # plateau, tranche du feuillet voisin) : on les ecarte d'abord.
        # Sans cela, une barre parasite en haut de page se faisait compter
        # comme une ligne, et le folio, plus etroit, se faisait rejeter :
        # le compte de lignes ne tombait plus juste et le controle 9
        # sautait la page — precisement la ou les erreurs se cachent.
        if y < 0.015 * H or y + h > 0.985 * H:
            continue
        if w < 0.04 * W:           # trop court, meme pour un folio
            continue
        if h > 0.10 * H:           # trop haut : c'est une tranche, pas une ligne
            continue
        if w / max(h, 1) < 2.0:
            continue
        keep[lab == i] = 1
        boxes.append((x, y, x + w, y + h))
    if not boxes:
        return gm, None
    # Colonne de texte etablie par la premiere passe : la recuperation
    # ci-dessous s'y limite, sinon elle ramene les tranches des feuillets
    # voisins, qui partagent la meme bande verticale (essaye : la
    # justification du feuillet 15 passait de 91,6 a 103,4 mm).
    _xs0 = np.percentile([b[0] for b in boxes], 10)
    _xs1 = np.percentile([b[2] for b in boxes], 90)
    _tol = 0.04 * W
    # Passe de nettoyage : la premiere passe ne borne pas la colonne, et
    # une bavure de numerisation assez large et assez plate y passait pour
    # une ligne, debordant de 200 px a droite. La ligne detectee etait
    # alors trop large, son encre fausse, et le controle 9 sortait des
    # ecarts absurdes (+4702 %). On elimine ces composantes, puis on
    # recalcule la colonne sur ce qui reste.
    # On CLIPPE a la colonne au lieu de REJETER ce qui en depasse.
    # Rejeter etait dangereux : au folio 20, quatre lignes tres chargees
    # en italique se soudent en une seule composante de 165 px de haut
    # (le pli du papier fait le pont), laquelle depasse la colonne de
    # trois pixels — et les quatre lignes disparaissaient d'un coup.
    # Une composante qui deborde un peu reste du texte : on lui coupe ce
    # qui sort, on ne la jette pas.
    propres = [b for b in boxes
               if b[0] >= _xs0 - _tol and b[2] <= _xs1 + _tol]
    if len(propres) >= max(4, 0.5 * len(boxes)):
        g0 = max(0, int(_xs0 - _tol)); g1 = min(W, int(_xs1 + _tol) + 1)
        keep[:, :g0] = 0
        keep[:, g1:] = 0
        boxes = [(max(b[0], g0), b[1], min(b[2], g1), b[3]) for b in boxes
                 if b[2] > g0 and b[0] < g1]
        _xs0 = np.percentile([b[0] for b in boxes], 10)
        _xs1 = np.percentile([b[2] for b in boxes], 90)
    # Deuxieme passe : on recupere les fragments courts qui appartiennent
    # a une ligne deja retenue. Une ligne comme « 3. --- B = b en ... »
    # se scinde en plusieurs composantes, les blancs autour du cadratin et
    # du signe d'egalite depassant la largeur de soudure ; le fragment de
    # gauche etait alors rejete comme trop court, et la ligne se trouvait
    # amputee de son debut — ce qui fausse a la fois sa largeur et son
    # encre, donc les controles 9 et la mesure de justification.
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        if keep[y + h // 2, x + w // 2] or h > 0.10 * H:
            continue
        if y < 0.015 * H or y + h > 0.985 * H:
            continue
        # Tolerance BEAUCOUP plus serree que celle du clippage. Cette passe
        # accepte des composantes courtes ; au bord droit du feuillet 34 les
        # eclats de la tranche voisine (x = 1348..1365, 8 a 17 px de large)
        # tombaient sous l'ancienne tolerance de 0,04 W = 55 px et se
        # faisaient recuperer parce qu'ils partagent l'ordonnee d'une vraie
        # ligne : la largeur relevee montait a 1365 px sur la moitie de la
        # page, et le controle 10, qui compare les bords droits, aurait
        # declare debordantes des lignes correctement justifiees.
        # 0,012 W = 16 px laisse passer un trait d'union ou une virgule en
        # debord, pas la tranche.
        _tolr = 0.012 * W
        if x < _xs0 - _tolr or x + w > _xs1 + _tolr:
            continue
        for bx0, by0, bx1, by1 in boxes:
            recouvre = min(y + h, by1) - max(y, by0)
            if recouvre > 0.5 * min(h, by1 - by0):
                keep[lab == i] = 1
                break
    xs0 = np.array([b[0] for b in boxes]); xs1 = np.array([b[2] for b in boxes])
    # marge gauche : quantile bas robuste ; marge droite : quantile haut
    x0 = int(np.percentile(xs0, 10)); x1 = int(np.percentile(xs1, 90))
    return (gm * keep), (x0, x1)


def lines_of(gm, min_ink=None):
    """Lignes de texte : segments de la projection horizontale du masque."""
    rows = (gm > 0).sum(axis=1)
    if rows.max() == 0:
        return []
    thr = min_ink if min_ink else max(5, rows.max() * 0.06)
    on = (rows > thr).astype(np.int8)
    d = np.diff(on)
    st = list(np.where(d == 1)[0] + 1)
    en = list(np.where(d == -1)[0] + 1)
    if on[0]: st.insert(0, 0)
    if on[-1]: en.append(len(on))
    # --- Rattrapage des lignes PALES -----------------------------------
    # Le seuil se calcule sur le maximum de la page : une ligne courte,
    # ou toute en italique, peut passer dessous. Trois pages l'ont montre
    # (feuillets 40 et 41 : « XI, 296.) », « misas. », « ici, iti. »), et
    # le fac-simile s'en trouvait releve a une ou deux lignes de moins que
    # la realite — les controles 9 et 11 sautaient alors la page.
    # Abaisser le seuil partout souderait des lignes ailleurs (essaye : le
    # feuillet 200 tombait de 39 a 32 lignes). On ne le baisse donc que
    # DANS LES TROUS, et on n'accepte la trouvaille que si elle a l'encre
    # d'une vraie ligne.
    # Le discriminant est l'ENCRE RAPPORTEE A LA LIGNE MEDIANE. Mesure sur
    # les feuillets 19 a 25, 37, 40 et 41 : les vraies lignes manquantes
    # pesent 0,142 a 0,162 ; les fragments de jambage et les eclats, de
    # 0,024 a 0,089. Le seuil est pose a 0,12, au milieu de cet ecart.
    # Ce que cela ne rattrape pas : « lua, lia. » du feuillet 37, a 0,086,
    # tombe du mauvais cote. On ne descend pas plus bas pour la seule
    # raison qu'une page en profiterait — trois autres y perdraient.
    paires = [(a, b) for a, b in zip(st, en) if b - a >= 9]
    if len(paires) >= 5:
        _enc = sorted(int((gm[a:b] > 0).sum()) for a, b in paires)
        _med = _enc[len(_enc) // 2]
        _pas = sorted(paires[k + 1][0] - paires[k][0]
                      for k in range(len(paires) - 1))
        _pm = _pas[len(_pas) // 2]
        zones = [(paires[k][1], paires[k + 1][0])
                 for k in range(len(paires) - 1)
                 if paires[k + 1][0] - paires[k][0] >= 1.35 * _pm]
        # apres la derniere ligne : c'est la que tombe la fin d'une note
        zones.append((paires[-1][1], min(len(rows), paires[-1][1] + 2 * _pm)))
        for a, b in zones:
            if b - a < 12:
                continue
            on2 = (rows[a:b] > 0.3 * thr).astype(np.int8)
            d2 = np.diff(on2)
            s2 = list(np.where(d2 == 1)[0] + 1)
            e2 = list(np.where(d2 == -1)[0] + 1)
            if on2[0]: s2.insert(0, 0)
            if on2[-1]: e2.append(len(on2))
            for p, q in zip(s2, e2):
                if q - p < 12:
                    continue
                seg = (gm[a + p:a + q] > 0)
                if len(np.where(seg.sum(axis=0) > 0)[0]) < 60:
                    continue
                if seg.sum() < 0.12 * _med:
                    continue
                paires.append((a + p, a + q))
        paires.sort()
        st = [a for a, _ in paires]
        en = [b for _, b in paires]
    out = []
    for s, e in zip(st, en):
        if e - s < 9:
            continue
        seg = (gm[s:e] > 0)
        c = seg.sum(axis=0)
        xs = np.where(c > 0)[0]
        if len(xs) < 20:
            continue
        out.append({'y0': int(s), 'y1': int(e), 'x0': int(xs[0]), 'x1': int(xs[-1]),
                    'ink': int(seg.sum())})
    return out


def folio_ligne(gm, lignes, secours=None):
    """Le folio « -- 12 -- » porte tres peu d'encre : il passe sous le
    seuil de detection des lignes, calcule sur le maximum de la page.
    L'abaisser ferait fusionner des lignes voisines ailleurs (essaye :
    le feuillet 200 tombait de 39 a 32 lignes). On le cherche donc a
    part, dans le haut de la page, avec un seuil bas, et seulement s'il
    n'a pas deja ete trouve.

    `secours` est un second masque, fouille si le premier ne donne rien.
    Il sert quand text_region a efface le folio : les cadratins qui
    l'encadrent sont plats et larges, donc rejetes des le masque de
    glyphes, et il ne reste que les chiffres. Au feuillet 42 le folio se
    reduit ainsi a « 38 », soude sur 60 px — moins que les 0,04 W = 63 px
    exiges d'une ligne. La page etait alors relevee sans folio, et les
    controles 9 et 11 la sautaient.
    """
    r = _cherche_folio(gm, lignes)
    if r is None and secours is not None:
        r = _cherche_folio(secours, lignes)
    return r


def _cherche_folio(gm, lignes):
    H, W = gm.shape

    def est_folio(l):
        larg = l['x1'] - l['x0']
        centre = (l['x0'] + l['x1']) / 2 / W
        return larg < 0.22 * W and 0.35 < centre < 0.65 and l['y0'] < 0.13 * H

    if lignes and est_folio(lignes[0]):
        return None                      # deja detecte
    # on ne cherche qu'AU-DESSUS de la premiere ligne trouvee
    haut = int(0.13 * H)
    if lignes:
        haut = min(haut, max(0, lignes[0]['y0'] - 15))
    if haut < 20:
        return None
    sous = gm[:haut]
    rows = (sous > 0).sum(axis=1)
    if rows.max() < 4:
        return None
    on = (rows > 3).astype(np.int8)
    d = np.diff(on)
    st = list(np.where(d == 1)[0] + 1); en = list(np.where(d == -1)[0] + 1)
    if on[0]: st.insert(0, 0)
    if on[-1]: en.append(len(on))
    for s, e in zip(st, en):
        if e - s < 9:
            continue
        seg = (sous[s:e] > 0)
        xs = np.where(seg.sum(axis=0) > 0)[0]
        if len(xs) < 8:
            continue
        # On examine les AMAS de la bande, non son etendue totale. Un pli
        # du papier laisse un trait diagonal qui traverse la hauteur du
        # folio : au feuillet 48 il portait l'etendue a 396 px, centre a
        # 0,703, et le folio se faisait rejeter comme trop large et
        # decentre. Chaque amas est teste a part ; le premier qui a la
        # taille et la position d'un folio est retenu.
        amas = []
        _s = _p = xs[0]
        for _x in xs[1:]:
            if _x - _p > 40:
                amas.append((_s, _p)); _s = _x
            _p = _x
        amas.append((_s, _p))
        for a0, a1 in amas:
            if a1 - a0 < 20:
                continue
            larg = a1 - a0
            centre = (a0 + a1) / 2 / W
            # court, centre : c'est un folio, pas une ligne de texte
            if larg < 0.22 * W and 0.35 < centre < 0.65:
                return {'y0': int(s), 'y1': int(e), 'x0': int(a0), 'x1': int(a1),
                        'ink': int((sous[s:e, a0:a1 + 1] > 0).sum())}
    return None


def block(n):
    """Geometrie du bloc de texte d'une page."""
    norm, gm, ang = prepared(n)
    H, W = norm.shape
    gm2, span = text_region(gm)
    ls = lines_of(gm2)
    f = folio_ligne(gm2, ls)
    if f:
        ls.insert(0, f)
    if not ls:
        return {'leaf': n, 'blank': True, 'skew': ang, 'W': W, 'H': H}
    # marge gauche : mode des debuts de ligne (tres stable en texte courant)
    lefts = np.array([l['x0'] for l in ls])
    rights = np.array([l['x1'] for l in ls])
    left = float(np.percentile(lefts, 25))
    right = float(np.percentile(rights, 75))
    just = right - left
    tops = [l['y0'] for l in ls]
    steps = np.diff(tops)
    steps = steps[(steps > 22) & (steps < 70)]
    return {
        'leaf': n, 'skew': round(ang, 2), 'W': W, 'H': H,
        'n_lines': len(ls),
        'left': round(left, 1), 'right': round(right, 1), 'span': span,
        'just_px': round(just, 1),
        'just_mm': round(just * PX2MM, 2),
        'just_pt': round(just * PX2PT, 2),
        'y_first': ls[0]['y0'], 'y_last': ls[-1]['y1'],
        'step_px': round(float(np.median(steps)), 2) if len(steps) else None,
        'step_pt': round(float(np.median(steps)) * PX2PT, 2) if len(steps) else None,
        'lines': ls,
    }


if __name__ == '__main__':
    for a in sys.argv[1:]:
        b = block(int(a))
        b.pop('lines', None)
        print(json.dumps(b), flush=True)
