import numpy as np, cv2, sys

def masque_etoile(img, y0=1150, y1=1500, x0=420, x1=800):
    s = img[y0:y1, x0:x1]
    m = cv2.GaussianBlur(s,(0,0),25)
    norm = np.clip(s.astype(float)/np.maximum(m,1)*200, 0, 255).astype(np.uint8)
    b = cv2.morphologyEx((norm<150).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((13,13),np.uint8))
    n,lab,st,cen = cv2.connectedComponentsWithStats(b,8)
    i = max(range(1,n), key=lambda k: st[k][4])
    d = (lab==i).astype(np.uint8)
    plein = d.copy()
    ff = d.copy(); mm = np.zeros((d.shape[0]+2,d.shape[1]+2),np.uint8)
    cv2.floodFill(ff, mm, (0,0), 1)
    plein = ((ff==0)|(d==1)).astype(np.uint8)          # disque plein
    inte = cv2.erode(plein, np.ones((21,21),np.uint8)) # on ecarte l'anneau
    clair = ((inte>0) & (norm>=150)).astype(np.uint8)
    nb,lb,sb,cb = cv2.connectedComponentsWithStats(clair,8)
    j = max(range(1,nb), key=lambda k: sb[k][4])
    E = (lb==j).astype(np.uint8)
    E = cv2.morphologyEx(E, cv2.MORPH_CLOSE, np.ones((27,27),np.uint8))   # avale le mot
    E = cv2.morphologyEx(E, cv2.MORPH_OPEN,  np.ones((5,5),np.uint8))
    return E, (x0,y0)

def sommets(E, nbin=2880):
    """Les 12 sommets de l'etoile : 6 pointes et 6 creux, par le profil
    radial pris sur le CONTOUR, non par lancer de rayons."""
    cont,_ = cv2.findContours(E, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    C = max(cont, key=cv2.contourArea).reshape(-1,2).astype(float)   # (x,y)
    cx, cy = C[:,0].mean(), C[:,1].mean()
    th = (np.degrees(np.arctan2(cy-C[:,1], C[:,0]-cx))+360) % 360
    r  = np.hypot(C[:,0]-cx, cy-C[:,1])
    prof = np.full(nbin, np.nan)
    idx = (th/360*nbin).astype(int) % nbin
    for k,v in zip(idx,r):
        if np.isnan(prof[k]) or v>prof[k]: prof[k]=v
    ok = ~np.isnan(prof)
    prof = np.interp(np.arange(nbin), np.arange(nbin)[ok], prof[ok], period=nbin)
    k = np.ones(15)/15.
    prof = np.convolve(np.r_[prof[-14:],prof,prof[:14]], k, 'same')[14:-14]
    ang = np.arange(nbin)*360.0/nbin
    def extremes(sig, maxi):
        out=[]
        for i in range(nbin):
            a,b,c = sig[(i-1)%nbin], sig[i], sig[(i+1)%nbin]
            if (b>a and b>=c) if maxi else (b<a and b<=c):
                den = (a-2*b+c)
                d = 0.5*(a-c)/den if den!=0 else 0.0
                out.append(((i+d)*360.0/nbin % 360, b))
        return out
    def garde(l, n=6):
        l = sorted(l, key=lambda z:-z[1] if True else 0)
        pris=[]
        for a,v in sorted(l, key=lambda z: -z[1]):
            if all(min(abs(a-p),360-abs(a-p))>25 for p in pris): pris.append(a)
            if len(pris)==n: break
        return sorted(pris)
    P = garde(extremes(prof,True))
    mn = extremes(prof,False)
    mn = sorted(mn, key=lambda z: z[1])
    pris=[]
    for a,v in mn:
        if all(min(abs(a-p),360-abs(a-p))>25 for p in pris): pris.append(a)
        if len(pris)==6: break
    V = sorted(pris)
    return (cx,cy), P, V, prof

def orientation(P, V):
    """Moyenne circulaire sur les DOUZE sommets : chaque pointe doit
    tomber sur theta0+k*60, chaque creux sur theta0+30+k*60. En prenant
    l'harmonique 12 des uns et des autres, les douze contribuent a
    parts egales, et l'irregularite de l'etoile se moyenne au lieu de
    peser sur un seul point."""
    z = sum(np.exp(1j*np.radians(12*a)) for a in P) \
      + sum(np.exp(1j*np.radians(12*a)) for a in V)
    t0 = np.degrees(np.angle(z))/12.0 % 30
    return t0, abs(z)/12.0

if __name__ == '__main__':
    img = np.load(sys.argv[1])
    E,(ox,oy) = masque_etoile(img)
    (cx,cy), P, V, prof = sommets(E)
    print('centre du contour : (%.1f, %.1f) dans la fenetre'%(cx,cy))
    print('POINTES :', ' '.join('%7.2f'%a for a in P))
    print('CREUX   :', ' '.join('%7.2f'%a for a in V))
    t0, R = orientation(P,V)
    cible = 90.0 % 30
    ec = ((t0 - cible + 15) % 30) - 15
    print('theta0 (mod 30) = %.3f   concentration %.4f'%(t0,R))
    print('ECART A LA VERTICALE : %+.3f degre'%ec)
    print('  ecarts pointe par pointe :',
          ' '.join('%+.2f'%(((a-90+30)%60)-30) for a in P))
    print('  ecarts creux par creux   :',
          ' '.join('%+.2f'%(((a-60+30)%60)-30) for a in V))
