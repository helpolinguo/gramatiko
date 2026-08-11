#!/usr/bin/env python3
"""Classifieur d'ENRICHISSEMENT par le CONTENU, non par l'image.

Le classifieur visuel (outils/enrichi.py) a echoue : le demi-gras etroit
du fac-simile a un rapport encre/largeur qui recouvre celui du romain.

Mais l'enrichissement de ce livre n'est pas decoratif, il est SEMANTIQUE.
La regle, relevee au § 3.3 du LISEZ-MOI :

    gras     = la forme IDISTE citee en vedette
    italique = ce qui est cite d'une AUTRE LANGUE
    romain   = le texte courant, qui est en ido lui aussi

La difficulte n'est donc pas gras contre italique — c'est une question de
langue, et le vocabulaire la tranche. Elle est gras contre romain : les
deux sont en ido, et seul le CONTEXTE dit si le mot est cite ou employe.

Trois indices, tous tires du texte :

  1. un mot cite suit un marqueur : « = », « Ex. : », « quale », « per »,
     ou une enumeration deja commencee ;
  2. un mot suivi d'un nom de langue (Franca, Germana, Angla...) est cite
     de cette langue, donc italique ;
  3. un mot absent du lexique ido du volume est etranger, donc italique.

Le lexique ido se construit tout seul : ce sont les mots que le releve
compose en ROMAIN, c'est-a-dire le texte courant. Il grandit a chaque
page transcrite, et le classifieur avec lui.
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LANGUES = {'franca', 'germana', 'angla', 'italiana', 'hispana', 'latina',
           'rusa', 'portugalana', 'esperanto', 'espo', 'poloniana',
           'suediana', 'daniana', 'greka', 'araba'}
# mots qui introduisent une citation
MARQUEURS = {'ex', 'exemple', 'quale', 'kom', 'per', 'yen', 'nome'}


def mots(ligne):
    return re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]*", ligne)


class Classifieur:
    def __init__(self, lexique_ido, lexique_ital):
        self.ido = lexique_ido
        self.ital = lexique_ital

    def classe(self, suite, k):
        """suite : liste de mots de la ligne ; k : indice du mot."""
        m = suite[k].lower().strip("'-")
        suiv = suite[k + 1].lower() if k + 1 < len(suite) else ''
        prec = suite[k - 1].lower() if k > 0 else ''

        # 2. suivi d'un nom de langue -> cite de cette langue
        if suiv in LANGUES:
            return 'ital'
        # 3. mot atteste comme etranger dans le volume
        if m in self.ital and m not in self.ido:
            return 'ital'
        # mot inconnu du lexique ido et court : probablement cite
        if m not in self.ido:
            if prec in LANGUES or prec in MARQUEURS:
                return 'ital'
            return 'ital' if len(m) > 2 else 'gras'
        # 1. lettre isolee : c'est presque toujours une vedette
        if len(m) == 1:
            return 'ital' if prec in LANGUES or suiv in LANGUES else 'gras'
        return 'rom'


def construis_lexiques(pages, sauf=None):
    """Lexiques tires du releve : romain -> ido ; italique -> etranger."""
    ido, ital = set(), set()
    for pg in pages:
        if sauf is not None and pg.get('feuillet') == sauf:
            continue
        for l in pg['lignes']:
            for mot, cls in extrait(l['brut']):
                m = mot.lower().strip("'-")
                if cls == 'rom':
                    ido.add(m)
                elif cls == 'ital':
                    ital.add(m)
    return ido, ital


BAL = re.compile(r'\\(VUgras|textit|textsc)\s*\{')


def extrait(brut):
    """(mot, classe) attendus, lus du releve LaTeX."""
    out, i, pile = [], 0, []
    while i < len(brut):
        m = BAL.match(brut, i)
        if m:
            pile.append('gras' if m.group(1) == 'VUgras' else 'ital')
            i = m.end(); continue
        c = brut[i]
        if c == '}':
            if pile: pile.pop()
            i += 1; continue
        if c == '{':
            i += 1; continue
        if c == '\\':
            j = i + 1
            while j < len(brut) and brut[j].isalpha():
                j += 1
            i = max(j, i + 2); continue
        if c.isalpha() or c in 'ÀÁÂÄÈÉÊËÌÍÎÏÒÓÔÖÙÚÛÜàáâäèéêëìíîïòóôöùúûü':
            j = i
            while j < len(brut) and (brut[j].isalpha() or brut[j] in "'-"
                                     or brut[j] in 'àáâäèéêëìíîïòóôöùúûü'):
                j += 1
            out.append((brut[i:j], pile[-1] if pile else 'rom'))
            i = j; continue
        i += 1
    return out


if __name__ == '__main__':
    import controles as C
    pages = [p for p in C.lire_releve() if p.get('feuillet')
             and int(p['feuillet']) >= 15]
    conf = {}
    # validation croisee : chaque page est classee avec un lexique
    # construit SANS elle, pour ne pas se mesurer sur ce qu'on a appris.
    for pg in pages:
        ido, ital = construis_lexiques(pages, sauf=pg['feuillet'])
        cl = Classifieur(ido, ital)
        for l in pg['lignes']:
            att = extrait(l['brut'])
            if not att:
                continue
            suite = [m for m, _ in att]
            for k, (mot, vrai) in enumerate(att):
                pred = cl.classe(suite, k)
                conf[(vrai, pred)] = conf.get((vrai, pred), 0) + 1
    tot = sum(conf.values())
    just = sum(v for (a, b), v in conf.items() if a == b)
    romtot = sum(v for (a, _), v in conf.items() if a == 'rom')
    print('Classifieur par le CONTENU (validation croisee page par page)')
    print('  mots compares : %d' % tot)
    print('  exactitude    : %.1f %%' % (100.0 * just / max(tot, 1)))
    print('  reference « tout romain » : %.1f %%' % (100.0 * romtot / max(tot, 1)))
    print('\n  matrice (attendu -> predit rom / gras / ital) :')
    for a in ('rom', 'gras', 'ital'):
        n = sum(v for (x, _), v in conf.items() if x == a)
        r = conf.get((a, a), 0)
        print('    %-5s %6d %6d %6d     rappel %5.1f %%' % (
            a, conf.get((a, 'rom'), 0), conf.get((a, 'gras'), 0),
            conf.get((a, 'ital'), 0), 100.0 * r / max(n, 1)))
