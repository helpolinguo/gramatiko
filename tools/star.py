#!/usr/bin/env python3
"""ORIENTATION OF THE STAR on the vignette (leaf 3, the cover).

Why this tool exists. The cover's vignette -- the emblem of Ido, a
six-pointed star in a disc -- leaned, and it took three attempts to set
it upright:

  1. I first measured the BASELINES OF THE THREE LETTERS at the centre of
     the star, and concluded that it was straight to within 0.096 degree.
     Those letters are small and engraved; their serifs do not define a
     baseline to a tenth of a degree. The measurement measured only its
     own noise.
  2. I then took the top point and the bottom point, which gave one
     degree -- the right order of magnitude -- but I turned THE WRONG WAY,
     for want of checking the result afterwards. The deviation went from
     1.27 to 2.32 degrees.
  3. The star is not regular: engraved by hand, its points depart from
     their place by 1.1 to 2.9 degrees and its hollows by 0.02 to 4.0. A
     single point, or even two opposite points, chiefly measures its own
     defect.

Hence the method adopted: survey ALL TWELVE VERTICES -- six points and
six hollows -- and take their circular mean. The points fall on
theta0 + k*60 and the hollows on theta0 + 30 + k*60; at harmonic 12, all
twelve therefore contribute equally, and the irregularity of the
engraving averages out instead of weighing on one point.

    python3 tools/star.py                  # the composed vignette
    python3 tools/star.py --scan           # the raw scan of leaf 3
    python3 tools/star.py --trial 1.05     # what +1.05 deg would give

THE LAST FORM IS THE MOST USEFUL: a rotation is verified by applying it,
then measuring again. If the deviation has grown, the sign is wrong.
"""
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIGNETTE = os.path.join(ROOT, 'ornaments', 'vignette-3.png')
LEAF = 3
# Window in which the vignette lies on the deskewed scan of leaf 3.
WINDOW = (1150, 1500, 420, 800)


def _from_scan(angle=0.0):
    """The disc drawn from the raw scan, deskewed with the page and then,
    if asked, rotated by `angle` about the centre of the disc."""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import page as PG
    norm, gm, ang = PG.prepared_img(LEAF)
    raw = cv2.imread(os.path.join(ROOT, 'scan', 'pages',
                                  'f%04d.jpg' % LEAF), 0)
    h, w = raw.shape
    ground = int(np.median(raw))
    M = cv2.getRotationMatrix2D((w / 2., h / 2.), ang, 1.0)
    img = cv2.warpAffine(raw, M, (w, h), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=ground)
    if angle:
        M = cv2.getRotationMatrix2D((603., 1331.), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT,
                             borderValue=ground)
    y0, y1, x0, x1 = WINDOW
    s = img[y0:y1, x0:x1]
    # The cover's paper is tinted and grainy: an absolute threshold counts
    # the grain as ink there. We divide by a blurred ground.
    m = cv2.GaussianBlur(s, (0, 0), 25)
    return np.clip(s.astype(float) / np.maximum(m, 1) * 200,
                   0, 255).astype(np.uint8)


def star_from_scan(norm):
    """The light star enclosed in the dark disc."""
    b = cv2.morphologyEx((norm < 150).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((13, 13), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, 8)
    i = max(range(1, n), key=lambda k: st[k][4])
    d = (lab == i).astype(np.uint8)
    # The disc is a ring: we fill it to seize what it encloses, then
    # remove the ring itself.
    ff = d.copy()
    mask = np.zeros((d.shape[0] + 2, d.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 1)
    full = ((ff == 0) | (d == 1)).astype(np.uint8)
    inte = cv2.erode(full, np.ones((21, 21), np.uint8))
    light = ((inte > 0) & (norm >= 150)).astype(np.uint8)
    nb, lb, sb, _ = cv2.connectedComponentsWithStats(light, 8)
    j = max(range(1, nb), key=lambda k: sb[k][4])
    return _close((lb == j).astype(np.uint8))


def star_from_plate(path_of=VIGNETTE):
    """The star drawn from the cut-out plate: there it is the large
    TRANSPARENT area enclosed by the opaque disc."""
    im = cv2.imread(path_of, cv2.IMREAD_UNCHANGED)
    if im is None or im.shape[2] < 4:
        raise SystemExit('%s : png a couche alpha attendu' % path_of)
    a = im[:, :, 3]
    H, W = a.shape
    n, lab, st, _ = cv2.connectedComponentsWithStats(
        (a < 110).astype(np.uint8), 8)
    # those that do not touch the edge: the outside is light too
    inside = [k for k in range(1, n)
              if st[k][0] > 2 and st[k][1] > 2
              and st[k][0] + st[k][2] < W - 2 and st[k][1] + st[k][3] < H - 2]
    if not inside:
        raise SystemExit('star not found in %s' % path_of)
    j = max(inside, key=lambda k: st[k][4])
    return _close((lab == j).astype(np.uint8))


def _close(E):
    """The word at the centre of the star is dark: it pierces a hole there
    that would drop the centroid onto a letter. We fill it in."""
    E = cv2.morphologyEx(E, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
    return cv2.morphologyEx(E, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))


def vertices(E, nbin=2880):
    """The twelve vertices, from the radial profile taken on the CONTOUR.

    Casting rays from the centre gives the same profile but depends on the
    sampling step; the contour is already the boundary. Each vertex is
    refined by parabolic interpolation over three samples: without that
    the resolution would be that of the step, 0.125 degree, of the same
    order as what we are looking for.
    """
    cont, _ = cv2.findContours(E, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    C = max(cont, key=cv2.contourArea).reshape(-1, 2).astype(float)
    cx, cy = C[:, 0].mean(), C[:, 1].mean()
    th = (np.degrees(np.arctan2(cy - C[:, 1], C[:, 0] - cx)) + 360) % 360
    r = np.hypot(C[:, 0] - cx, cy - C[:, 1])
    depth = np.full(nbin, np.nan)
    for k, v in zip((th / 360 * nbin).astype(int) % nbin, r):
        if np.isnan(depth[k]) or v > depth[k]:
            depth[k] = v
    ok = ~np.isnan(depth)
    depth = np.interp(np.arange(nbin), np.arange(nbin)[ok], depth[ok],
                     period=nbin)
    kernel = np.ones(15) / 15.
    depth = np.convolve(np.r_[depth[-14:], depth, depth[:14]],
                       kernel, 'same')[14:-14]

    def extremes(maxi):
        out = []
        for i in range(nbin):
            a, b, c = depth[(i - 1) % nbin], depth[i], depth[(i + 1) % nbin]
            if (b > a and b >= c) if maxi else (b < a and b <= c):
                denom = a - 2 * b + c
                d = 0.5 * (a - c) / denom if denom else 0.0
                out.append(((i + d) * 360.0 / nbin % 360, b))
        return out

    def six(cands, maxi):
        cands.sort(key=lambda z: -z[1] if maxi else z[1])
        taken = []
        for ang, _v in cands:
            if all(min(abs(ang - p), 360 - abs(ang - p)) > 25 for p in taken):
                taken.append(ang)
            if len(taken) == 6:
                break
        return sorted(taken)

    return (cx, cy), six(extremes(True), True), six(extremes(False), False)


def orientation(points, hollows):
    """(theta0, concentration). theta0 is the angle of a point, modulo 60
    degrees. The concentration says how far the twelve vertices agree: 1
    for a perfect star, 0 for noise."""
    z = sum(np.exp(1j * np.radians(12 * a)) for a in points) \
        + sum(np.exp(1j * np.radians(12 * a)) for a in hollows)
    return np.degrees(np.angle(z)) / 12.0 % 30, abs(z) / 12.0


def vertical_gap(theta0):
    """The deviation from the vertical, in [-15, +15]. Positive: the star
    leans anticlockwise."""
    return ((theta0 - 90 + 15) % 30) - 15


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--scan' in args or '--trial' in args:
        a = 0.0
        if '--trial' in args:
            a = float(args[args.index('--trial') + 1])
        E = star_from_scan(_from_scan(a))
        what = 'scan of leaf %d, rotated by %+.3f deg' % (LEAF, a)
    else:
        E = star_from_plate()
        what = os.path.relpath(VIGNETTE, ROOT)
    (cx, cy), P, V = vertices(E)
    t0, R = orientation(P, V)
    print('%s' % what)
    print('  centre    (%.1f, %.1f)' % (cx, cy))
    print('  POINTES   ' + ' '.join('%7.2f' % a for a in P))
    print('  CREUX     ' + ' '.join('%7.2f' % a for a in V))
    print('  theta0    %.3f deg (modulo 60)   concentration %.3f'
          % (t0 + 60, R))
    e = vertical_gap(t0)
    print('  DEVIATION FROM THE VERTICAL: %+.3f deg' % e)
    if abs(e) > 0.25:
        print('  -> to set it upright, rotate by %+.3f deg ABOUT THE CENTRE'
              ' OF THE DISC,' % -e)
        print('     then MEASURE AGAIN: if the deviation has grown, the sign is'
              ' faux.')
    else:
        print('  -> upright (under a quarter of a degree).')
