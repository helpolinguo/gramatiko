#!/usr/bin/env python3
"""Syllabateur ido — coupures de fin de ligne admises.

SPECIFICATION : l'ouvrage lui-meme, appendice « Puntizado », folio 220,
paragraphe « Seko di la Vorti. [D. 485] » :

    « On admisas kompleta libereso en la seko di la vorti de lineo a
      lineo, ecepte ke singla parto devas kontenar vokalo, e ke la
      digrami o diftongi devas ne dividesar. Ex. on darfas sekar tale
      la vorto mustar : mu-star, mus-tar, o must-ar. Ma neutro,
      mashino sekesas neu-tro, ma-shino, e ne ne-utro, mas-hino. »

Autrement dit, la coupure est libre a DEUX conditions seulement :
  1. chacune des deux parties contient au moins une voyelle ;
  2. la coupure ne tombe pas a l'interieur d'un digramme ni d'une
     diphtongue.

Digrammes (folio 13, « PRONUNCO DIL KONSONANTI E DIGRAMI ») : ch, sh, qu.
  — q est toujours suivi de u (folio 14) : qu est indivisible ;
  — gn n'est PAS un digramme : le livre l'ecrit reg-no, dig-na (folio 13).
Diphtongues : au, eu (folio 17 : « Evitez sorgoze facar ek au, eu du
  silabi en ta vorti »).

Ce module sert surtout de CONTROLE : toutes les coupures du fac-simile
sont relevees a la main ; le syllabateur verifie qu'elles sont conformes.
Une coupure non conforme est soit une coquille de l'original (a conserver
et a signaler), soit une erreur de releve (a corriger).
"""
import re
import unicodedata

VOYELLES = set('aeiou')
DIGRAMMES = ('ch', 'sh', 'qu')
DIPHTONGUES = ('au', 'eu')
INSECABLES = DIGRAMMES + DIPHTONGUES


def _plie(mot):
    """Minuscules sans accents, pour l'analyse (le livre accentue tres peu)."""
    s = unicodedata.normalize('NFD', mot.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def positions_insecables(mot):
    """Indices i tels qu'une coupure entre mot[i-1] et mot[i] est interdite
    parce qu'elle scinderait un digramme ou une diphtongue."""
    m = _plie(mot)
    interdit = set()
    for j in range(len(m) - 1):
        if m[j:j + 2] in INSECABLES:
            interdit.add(j + 1)
    return interdit


def coupures(mot):
    """Toutes les coupures admises. Retourne la liste des indices i :
    la ligne se termine par mot[:i] et reprend par mot[i:]."""
    m = _plie(mot)
    if not m.isalpha():
        return []
    interdit = positions_insecables(mot)
    out = []
    for i in range(1, len(m)):
        if i in interdit:
            continue
        if not (set(m[:i]) & VOYELLES):      # partie gauche sans voyelle
            continue
        if not (set(m[i:]) & VOYELLES):      # partie droite sans voyelle
            continue
        out.append(i)
    return out


def conforme(gauche, droite):
    """La coupure gauche|droite est-elle conforme a D. 485 ?
    Retourne (booleen, motif)."""
    g, d = _plie(gauche), _plie(droite)
    if not g or not d:
        return False, 'partie vide'
    if not (set(g) & VOYELLES):
        return False, 'la partie gauche ne contient pas de voyelle'
    if not (set(d) & VOYELLES):
        return False, 'la partie droite ne contient pas de voyelle'
    joint = g[-1] + d[0]
    if joint in INSECABLES:
        quoi = 'digramme' if joint in DIGRAMMES else 'diphtongue'
        return False, 'coupure a l\'interieur du %s « %s »' % (quoi, joint)
    return True, ''


def motif_hyphenation(mot):
    """Le mot avec un trait d'union a chaque coupure admise,
    au format attendu par \\hyphenation{...}."""
    cs = coupures(mot)
    out, prev = [], 0
    for i in cs:
        out.append(mot[prev:i])
        prev = i
    out.append(mot[prev:])
    return '-'.join(out)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for m in sys.argv[1:]:
            print('%-16s %s' % (m, motif_hyphenation(m)))
    else:
        # controle sur les exemples donnes par le livre lui-meme
        essais = [
            ('mustar', ['mu-star', 'mus-tar', 'must-ar']),
            ('neutro', ['neu-tro']),
            ('mashino', ['ma-shino']),
        ]
        for mot, attendus in essais:
            got = ['%s-%s' % (mot[:i], mot[i:]) for i in coupures(mot)]
            print('%-9s -> %s' % (mot, ' '.join(got)))
            for a in attendus:
                print('    %-12s %s' % (a, 'OK' if a in got else 'MANQUE'))
        for mauvais in ['ne-utro', 'mas-hino']:
            g, d = mauvais.split('-')
            ok, why = conforme(g, d)
            print('%-10s rejete ? %s  (%s)' % (mauvais, 'oui' if not ok else 'NON', why))
