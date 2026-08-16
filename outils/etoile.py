#!/usr/bin/env python3
"""ORIENTATION DE L'ETOILE de la vignette (feuillet 3, la couverture).

Pourquoi cet outil existe. La vignette de la couverture — l'embleme de
l'Ido, une etoile a six branches dans un disque — penchait, et il a
fallu trois essais pour la redresser :

  1. J'ai d'abord mesure les LIGNES DE BASE DES TROIS LETTRES au centre
     de l'etoile, et conclu qu'elle etait droite a 0,096 degre pres. Ces
     lettres sont petites et gravees ; leurs empattements ne definissent
     pas une ligne de base au dixieme de degre. La mesure ne mesurait
     que son propre bruit.
  2. J'ai ensuite pris la pointe haute et la pointe basse, qui donnaient
     un degre — la bonne grandeur — mais j'ai tourne DANS LE MAUVAIS
     SENS, faute d'avoir verifie le resultat apres coup. L'ecart est
     passe de 1,27 a 2,32 degre.
  3. L'etoile n'est pas reguliere : gravee a la main, ses pointes
     s'ecartent de leur place de 1,1 a 2,9 degre et ses creux de 0,02 a
     4,0. Un seul point, ou meme deux points opposes, mesure surtout son
     propre defaut.

D'ou la methode retenue : relever LES DOUZE SOMMETS — six pointes et six
creux — et en prendre la moyenne circulaire. Les pointes tombent sur
theta0 + k*60 et les creux sur theta0 + 30 + k*60 ; a l'harmonique 12,
les douze contribuent donc a parts egales, et l'irregularite de la
gravure se moyenne au lieu de peser sur un point.

    python3 outils/etoile.py                  # la vignette composee
    python3 outils/etoile.py --scan           # le scan brut du feuillet 3
    python3 outils/etoile.py --essai 1.05     # ce que donnerait +1,05 deg

LA DERNIERE FORME EST LA PLUS UTILE : une rotation se verifie en la
posant, puis en remesurant. Si l'ecart a grandi, le signe est faux.
"""
import os
import sys

import cv2
import numpy as np

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIGNETTE = os.path.join(RACINE, 'ornamenti', 'vinieto-3.png')
FEUILLET = 3
# Fenetre ou la vignette se trouve sur le scan desincline du feuillet 3.
FENETRE = (1150, 1500, 420, 800)


def _du_scan(angle=0.0):
    """Le disque tire du scan brut, desincline de la page puis, si on le
    demande, tourne de `angle` autour du centre du disque."""
    sys.path.insert(0, os.path.join(RACINE, 'outils'))
    import page as PG
    norm, gm, ang = PG.prepared(FEUILLET)
    raw = cv2.imread(os.path.join(RACINE, 'scan', 'pages',
                                  'f%04d.jpg' % FEUILLET), 0)
    h, w = raw.shape
    fond = int(np.median(raw))
    M = cv2.getRotationMatrix2D((w / 2., h / 2.), ang, 1.0)
    img = cv2.warpAffine(raw, M, (w, h), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=fond)
    if angle:
        M = cv2.getRotationMatrix2D((603., 1331.), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT,
                             borderValue=fond)
    y0, y1, x0, x1 = FENETRE
    s = img[y0:y1, x0:x1]
    # Le papier de la couverture est teinte et grenu : un seuil absolu y
    # compte le grain pour de l'encre. On divise par un fond floute.
    m = cv2.GaussianBlur(s, (0, 0), 25)
    return np.clip(s.astype(float) / np.maximum(m, 1) * 200,
                   0, 255).astype(np.uint8)


def etoile_du_scan(norm):
    """L'etoile claire enclose dans le disque sombre."""
    b = cv2.morphologyEx((norm < 150).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((13, 13), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, 8)
    i = max(range(1, n), key=lambda k: st[k][4])
    d = (lab == i).astype(np.uint8)
    # Le disque est un anneau : on le remplit pour saisir ce qu'il
    # enferme, puis on retire l'anneau lui-meme.
    ff = d.copy()
    masque = np.zeros((d.shape[0] + 2, d.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, masque, (0, 0), 1)
    plein = ((ff == 0) | (d == 1)).astype(np.uint8)
    inte = cv2.erode(plein, np.ones((21, 21), np.uint8))
    clair = ((inte > 0) & (norm >= 150)).astype(np.uint8)
    nb, lb, sb, _ = cv2.connectedComponentsWithStats(clair, 8)
    j = max(range(1, nb), key=lambda k: sb[k][4])
    return _ferme((lb == j).astype(np.uint8))


def etoile_du_cliche(chemin=VIGNETTE):
    """L'etoile tiree du cliche detoure : elle y est la grande plage
    TRANSPARENTE enclose par le disque opaque."""
    im = cv2.imread(chemin, cv2.IMREAD_UNCHANGED)
    if im is None or im.shape[2] < 4:
        raise SystemExit('%s : png a couche alpha attendu' % chemin)
    a = im[:, :, 3]
    H, W = a.shape
    n, lab, st, _ = cv2.connectedComponentsWithStats(
        (a < 110).astype(np.uint8), 8)
    # celles qui ne touchent pas le bord : l'exterieur est clair aussi
    dedans = [k for k in range(1, n)
              if st[k][0] > 2 and st[k][1] > 2
              and st[k][0] + st[k][2] < W - 2 and st[k][1] + st[k][3] < H - 2]
    if not dedans:
        raise SystemExit('etoile non trouvee dans %s' % chemin)
    j = max(dedans, key=lambda k: st[k][4])
    return _ferme((lab == j).astype(np.uint8))


def _ferme(E):
    """Le mot au centre de l'etoile est sombre : il y perce un trou qui
    ferait tomber le centroide sur une lettre. On le comble."""
    E = cv2.morphologyEx(E, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
    return cv2.morphologyEx(E, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))


def sommets(E, nbin=2880):
    """Les douze sommets, par le profil radial pris sur le CONTOUR.

    Le lancer de rayons depuis le centre donne le meme profil mais
    dépend du pas d'echantillonnage ; le contour, lui, est deja la
    frontiere. Chaque sommet est affine par interpolation parabolique
    sur trois echantillons : sans cela la resolution serait celle du
    pas, 0,125 degre, du meme ordre que ce qu'on cherche.
    """
    cont, _ = cv2.findContours(E, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    C = max(cont, key=cv2.contourArea).reshape(-1, 2).astype(float)
    cx, cy = C[:, 0].mean(), C[:, 1].mean()
    th = (np.degrees(np.arctan2(cy - C[:, 1], C[:, 0] - cx)) + 360) % 360
    r = np.hypot(C[:, 0] - cx, cy - C[:, 1])
    prof = np.full(nbin, np.nan)
    for k, v in zip((th / 360 * nbin).astype(int) % nbin, r):
        if np.isnan(prof[k]) or v > prof[k]:
            prof[k] = v
    ok = ~np.isnan(prof)
    prof = np.interp(np.arange(nbin), np.arange(nbin)[ok], prof[ok],
                     period=nbin)
    noyau = np.ones(15) / 15.
    prof = np.convolve(np.r_[prof[-14:], prof, prof[:14]],
                       noyau, 'same')[14:-14]

    def extremes(maxi):
        out = []
        for i in range(nbin):
            a, b, c = prof[(i - 1) % nbin], prof[i], prof[(i + 1) % nbin]
            if (b > a and b >= c) if maxi else (b < a and b <= c):
                den = a - 2 * b + c
                d = 0.5 * (a - c) / den if den else 0.0
                out.append(((i + d) * 360.0 / nbin % 360, b))
        return out

    def six(cands, maxi):
        cands.sort(key=lambda z: -z[1] if maxi else z[1])
        pris = []
        for ang, _v in cands:
            if all(min(abs(ang - p), 360 - abs(ang - p)) > 25 for p in pris):
                pris.append(ang)
            if len(pris) == 6:
                break
        return sorted(pris)

    return (cx, cy), six(extremes(True), True), six(extremes(False), False)


def orientation(pointes, creux):
    """(theta0, concentration). theta0 est l'angle d'une pointe, modulo
    60 degres. La concentration dit combien les douze sommets
    s'accordent : 1 pour une etoile parfaite, 0 pour du bruit."""
    z = sum(np.exp(1j * np.radians(12 * a)) for a in pointes) \
        + sum(np.exp(1j * np.radians(12 * a)) for a in creux)
    return np.degrees(np.angle(z)) / 12.0 % 30, abs(z) / 12.0


def ecart_vertical(theta0):
    """L'ecart a la verticale, dans [-15, +15]. Positif : l'etoile
    penche dans le sens inverse des aiguilles."""
    return ((theta0 - 90 + 15) % 30) - 15


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--scan' in args or '--essai' in args:
        a = 0.0
        if '--essai' in args:
            a = float(args[args.index('--essai') + 1])
        E = etoile_du_scan(_du_scan(a))
        quoi = 'scan du feuillet %d, tourne de %+.3f deg' % (FEUILLET, a)
    else:
        E = etoile_du_cliche()
        quoi = os.path.relpath(VIGNETTE, RACINE)
    (cx, cy), P, V = sommets(E)
    t0, R = orientation(P, V)
    print('%s' % quoi)
    print('  centre    (%.1f, %.1f)' % (cx, cy))
    print('  POINTES   ' + ' '.join('%7.2f' % a for a in P))
    print('  CREUX     ' + ' '.join('%7.2f' % a for a in V))
    print('  theta0    %.3f deg (modulo 60)   concentration %.3f'
          % (t0 + 60, R))
    e = ecart_vertical(t0)
    print('  ECART A LA VERTICALE : %+.3f deg' % e)
    if abs(e) > 0.25:
        print('  -> pour redresser, tourner de %+.3f deg AUTOUR DU CENTRE'
              ' DU DISQUE,' % -e)
        print('     puis REMESURER : si l\'ecart a grandi, le signe est'
              ' faux.')
    else:
        print('  -> droite (sous le quart de degre).')
