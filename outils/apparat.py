#!/usr/bin/env python3
"""Calibration des LIGNES D'APPARAT (titres, faux-titre, titres de partie).

Une ligne de titre est definie par deux mesures prises sur le fac-simile :
  * la hauteur de capitale  -> donne le CORPS ;
  * la largeur d'encre      -> donne l'INTERLETTRAGE, une fois le corps connu.

Le corps se deduit de la hauteur de capitale parce que ces lignes sont
tout en capitales : il n'y a pas de hauteur d'x a mesurer.

Usage :
    python3 outils/apparat.py <feuillet>
        -> liste les lignes de la page avec leurs mesures brutes
    python3 outils/apparat.py <feuillet> --regle "TEXTE DE LA LIGNE" <index>
        -> calcule corps et interlettrage pour cette ligne
"""
import os, sys, re, json, subprocess
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX2MM, PX2PT = PG.PX2MM, PG.PX2PT

# Rapports hauteur-de-capitale / corps, mesures par outils/fontes.tex.
CAP_SUR_CORPS = {'XCharter-TLF': 0.680}


def lignes_apparat(n, seuil_largeur=0.03):
    """Comme page.block, mais sans rejeter les lignes courtes : sur une page
    de titre, « DI LA » est une ligne a part entiere."""
    norm, gm, ang = PG.prepared(n)
    H, W = gm.shape
    band = cv2.morphologyEx(gm, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_RECT, (61, 3)))
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(
        (band > 0).astype(np.uint8), 8)
    keep = np.zeros((H, W), np.uint8)
    for i in range(1, nlab):
        x, y, w, h, a = stats[i]
        if w < seuil_largeur * W or h > 0.10 * H or w / max(h, 1) < 1.2:
            continue
        # on ecarte les tranches : elles collent au bord de l'image
        if x < 0.02 * W or x + w > 0.98 * W:
            continue
        keep[lab == i] = 1
    gm2 = gm * keep
    return PG.lines_of(gm2, min_ink=3), norm, gm2


def hauteur_capitale(gm2, y0, y1):
    """Mode des hauteurs de glyphe sur la bande [y0,y1] : les lignes de
    titre etant tout en capitales, c'est la hauteur de capitale."""
    sub = (gm2[y0:y1] > 0).astype(np.uint8)
    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(sub, 8)
    hs = [stats[i][3] for i in range(1, nlab) if stats[i][4] >= 20]
    if not hs:
        return None
    return float(np.median(hs))


def largeur_naturelle(texte, corps_pt, fonte='XCharter-TLF', gras=False):
    """Largeur du texte compose sans interlettrage, en points TeX."""
    tex = r"""\documentclass{article}\usepackage[T1]{fontenc}\usepackage{XCharter}
\newlength{\Wq}\begin{document}\pagestyle{empty}
\fontfamily{%s}\fontsize{%.3fpt}{%.3fpt}\selectfont%s
\settowidth{\Wq}{%s}\typeout{LARGEUR=\the\Wq}\mbox{}\end{document}""" % (
        fonte, corps_pt, corps_pt, '\\bfseries' if gras else '', texte)
    d = os.path.join(P, 'outils', '.tmp')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'w.tex'), 'w') as fh:
        fh.write(tex)
    subprocess.run(['pdflatex', '-interaction=nonstopmode', 'w.tex'],
                   cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = open(os.path.join(d, 'w.log'), encoding='utf-8', errors='replace').read()
    m = re.search(r'LARGEUR=([\d.]+)pt', log)
    return float(m.group(1)) if m else None


def regle(texte, largeur_px, cap_px, fonte='XCharter-TLF', gras=False):
    """Corps et interlettrage (en 1/1000 de cadratin, unite de microtype)."""
    corps = cap_px * PX2PT / CAP_SUR_CORPS[fonte]
    cible = largeur_px * PX2PT
    nat = largeur_naturelle(texte, corps, fonte, gras)
    if nat is None:
        return None
    # microtype ajoute <t>/1000 cadratin apres CHAQUE caractere ;
    # sur une ligne centree, le dernier ajout est retire par \textls.
    n = max(len(texte) - 1, 1)
    track = (cible - nat) / (corps * n) * 1000.0
    return {'texte': texte, 'gras': gras, 'corps_pt': round(corps, 2),
            'largeur_cible_pt': round(cible, 2), 'largeur_nue_pt': round(nat, 2),
            'interlettrage': int(round(track)),
            'cap_mm': round(cap_px * PX2MM, 3),
            'largeur_mm': round(largeur_px * PX2MM, 2)}


if __name__ == '__main__':
    n = int(sys.argv[1])
    lignes, norm, gm2 = lignes_apparat(n)
    if '--regle' not in sys.argv:
        print('feuillet %d — %d lignes' % (n, len(lignes)))
        for k, l in enumerate(lignes):
            cap = hauteur_capitale(gm2, l['y0'], l['y1'])
            print('  [%d] y=%4d  largeur=%4d px (%.2f mm)  cap=%s px (%.3f mm)'
                  % (k, l['y0'], l['x1'] - l['x0'], (l['x1'] - l['x0']) * PX2MM,
                     cap, (cap or 0) * PX2MM))
    else:
        i = sys.argv.index('--regle')
        texte = sys.argv[i + 1]
        k = int(sys.argv[i + 2])
        l = lignes[k]
        cap = hauteur_capitale(gm2, l['y0'], l['y1'])
        gras = '--gras' in sys.argv
        print(json.dumps(regle(texte, l['x1'] - l['x0'], cap, gras=gras),
                         ensure_ascii=False, indent=1))
