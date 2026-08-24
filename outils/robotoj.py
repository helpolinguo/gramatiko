#!/usr/bin/env python3
"""Tire de la Gramatiko ses versions LISIBLES PAR LES MACHINES.

POURQUOI. La page pese 1,2 Mo pour 467 Ko de texte : le reste est du
balisage et 284 Ko de CSS en ligne. Qui veut LIRE la grammaire — un
robot d'indexation, un aspirateur, un modele de langue — paie donc deux
fois et demie le prix du texte, et doit encore le degager.

Le decoupage PAR CHAPITRE est l'essentiel. Une grammaire ne se lit pas
d'un bout a l'autre : on y cherche un point. Qui veut savoir comment se
forme le pluriel n'a pas a charger les cinquante chapitres. C'est la que
l'economie se fait, bien plus que dans la compression.

  gramatiko.md          le livre entier, d'un tenant.
  chapitri/<nomo>.md    un fichier par chapitre.
  chapitri/index.md     la table, avec la taille de chacun : de quoi
                        choisir AVANT de telecharger.

Engendres, jamais edites a la main. La source reste index.html.

    python3 outils/robotoj.py
"""

import os
import re
import sys
from pathlib import Path

# CE DOSSIER PORTE SON PROPRE « html.py ». Comme le script est lance depuis
# outils/, ce fichier-la vient EN TETE du chemin de recherche et masque le
# module standard du meme nom. On retire donc le dossier du script avant
# d'importer, faute de quoi « html.unescape » n'existe pas.
sys.path[:] = [d for d in sys.path
               if os.path.abspath(d) != os.path.dirname(os.path.abspath(__file__))]
import html as modul_html  # noqa: E402
from html.parser import HTMLParser  # noqa: E402

RACINO = Path(__file__).resolve().parent.parent
CHAPITRI = RACINO / 'chapitri'

ENTETE = '<!-- Engendre par outils/robotoj.py depuis index.html. Ne pas editer. -->\n'
FONTO = 'Transskribita de https://ido.help/gramatiko/\n'


def texto(h: str) -> str:
    """Un fragment de HTML en Markdown.

    Les reperes de folio s'en vont : ce sont des ancres vers le PDF, sans
    valeur pour qui lit le texte. L'italique et le gras restent — dans
    une grammaire ils distinguent l'exemple de la regle, et cette
    distinction porte du sens.
    """
    h = re.sub(r'<a[^>]*class="fol"[^>]*>.*?</a>', '', h, flags=re.S)
    h = re.sub(r'<i>(.*?)</i>', r'*\1*', h, flags=re.S)
    h = re.sub(r'<em>(.*?)</em>', r'*\1*', h, flags=re.S)
    h = re.sub(r'<b>(.*?)</b>', r'**\1**', h, flags=re.S)
    h = re.sub(r'<strong>(.*?)</strong>', r'**\1**', h, flags=re.S)
    h = re.sub(r'<br\s*/?>', '  \n', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = modul_html.unescape(h)
    h = re.sub(r'[ \t ]+', ' ', h)
    return re.sub(r' *\n *', '\n', h).strip()


class Kolektanto(HTMLParser):
    """Ramasse les blocs de premier rang du corps : intitules, alineas, notes.

    ON N'EMPLOIE PAS D'EXPRESSION REGULIERE ICI, et c'est deliberе : un
    alinea peut contenir un tableau, un groupe, une liste — donc d'autres
    « div ». Une expression reguliere qui cherche le « /div » fermant en
    compte un de trop ou un de moins des que l'imbrication varie, et c'est
    exactement ce qui faisait perdre un alinea sur 1230. Un analyseur, lui,
    compte la profondeur ; il ne peut pas se tromper.
    """

    SPECOJ = ('tit', 'p', 'noto')

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.blokoj = []
        self.nuna = None
        self.profundo = 0
        self.peci = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        klaso = (a.get('class') or '').split()
        if self.nuna is None and tag == 'div' and klaso and klaso[0] in self.SPECOJ:
            self.nuna = {'speco': klaso[0], 'ch': a.get('data-ch'), 'id': a.get('id')}
            self.profundo = 1
            self.peci = []
            return
        if self.nuna is not None:
            if tag == 'div':
                self.profundo += 1
            self.peci.append(self.get_starttag_text() or '')

    def handle_endtag(self, tag):
        if self.nuna is None:
            return
        if tag == 'div':
            self.profundo -= 1
            if self.profundo == 0:
                self.nuna['texto'] = texto(''.join(self.peci))
                self.blokoj.append(self.nuna)
                self.nuna = None
                return
        self.peci.append('</%s>' % tag)

    def handle_startendtag(self, tag, attrs):
        if self.nuna is not None:
            self.peci.append(self.get_starttag_text() or '')

    def handle_data(self, d):
        if self.nuna is not None:
            self.peci.append(d)

    def handle_entityref(self, n):
        if self.nuna is not None:
            self.peci.append('&%s;' % n)

    def handle_charref(self, n):
        if self.nuna is not None:
            self.peci.append('&#%s;' % n)


def blokusi(s: str) -> list:
    """Parcourt le corps et rend la suite des blocs, dans l'ordre du livre.

    L'ordre EST la structure du livre : une note doit rester ou l'auteur
    l'a mise, et un alinea sous l'intitule qui le commande.
    """
    korpo = re.search(r'<main\b.*?</main>', s, re.S)
    k = Kolektanto()
    k.feed(korpo.group(0) if korpo else s)
    return k.blokoj


def nomizar(t: str) -> str:
    """Le titre d'un chapitre, ramene a une ligne et depouille.

    Le livre compose ses intitules en gras ; « texto » rend fidelement ce
    gras en asterisques. Dans un TITRE de Markdown ils n'ont plus lieu
    d'etre — le titre est deja un titre — et dans la table ils se
    verraient en toutes lettres a l'interieur du lien. On les retire.
    """
    t = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t.rstrip('.').strip() or t


def main() -> None:
    s = (RACINO / 'index.html').read_text(encoding='utf-8')
    blokoj = blokusi(s)

    # Regrouper par chapitre, en gardant l'ordre.
    chapitri, nuna = [], None
    for b in blokoj:
        if b['speco'] == 'tit':
            nuna = {'id': b['id'], 'titolo': nomizar(b['texto']), 'blokoj': []}
            chapitri.append(nuna)
        elif nuna is not None:
            nuna['blokoj'].append(b)

    CHAPITRI.mkdir(exist_ok=True)
    for vieux in CHAPITRI.glob('*.md'):
        vieux.unlink()

    def korpo_de(c):
        lin = []
        for b in c['blokoj']:
            if not b['texto']:
                continue
            lin.append(('> ' + b['texto'].replace('\n', '\n> ')) if b['speco'] == 'noto'
                       else b['texto'])
        return '\n\n'.join(lin)

    # Un fichier par chapitre.
    tabelo = []
    for c in chapitri:
        korpo = korpo_de(c)
        dosiero = CHAPITRI / f'{c["id"]}.md'
        dosiero.write_text(
            f'{ENTETE}\n# {c["titolo"]}\n\n'
            f'Ek *Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido*, '
            f'L. de Beaufront, 1925.\n{FONTO}\n---\n\n{korpo}\n',
            encoding='utf-8')
        tabelo.append((c['id'], c['titolo'], dosiero.stat().st_size,
                       len(c['blokoj'])))

    # La table, avec les tailles : choisir avant de telecharger.
    lin = [ENTETE, '# Kompleta Gramatiko — chapitri\n',
           'L. de Beaufront, *Kompleta Gramatiko Detaloza di la Linguo '
           'Internaciona Ido*, Esch-Alzette, Meier-Heucke, 1925.\n', FONTO,
           'Singla chapitro esas apartra dosiero. La grandeso esas indikata '
           'por ke on povez selektar ANTE deskargar.\n',
           '| chapitro | titolo | alinei | grandeso |',
           '| --- | --- | ---: | ---: |']
    for i, (idd, tit, gr, n) in enumerate(tabelo, 1):
        lin.append(f'| {i} | [{tit}]({idd}.md) | {n} | {gr // 1024 or 1} Ko |')
    (CHAPITRI / 'index.md').write_text('\n'.join(lin) + '\n', encoding='utf-8')

    # Le livre entier.
    tuto = [ENTETE, '# Kompleta Gramatiko Detaloza di la Linguo Internaciona Ido\n',
            'L. de Beaufront · Esch-Alzette, Meier-Heucke, 1925 · '
            f'{len(chapitri)} chapitri\n', FONTO, '---\n']
    for c in chapitri:
        tuto.append(f'## {c["titolo"]}\n')
        tuto.append(korpo_de(c) + '\n')
    (RACINO / 'gramatiko.md').write_text('\n'.join(tuto), encoding='utf-8')

    print(f'  {len(chapitri)} chapitres, {len(blokoj)} blocs')
    print(f'  gramatiko.md      {(RACINO / "gramatiko.md").stat().st_size:>9,} octets')
    moy = sum(t[2] for t in tabelo) // max(len(tabelo), 1)
    print(f'  chapitri/         {len(tabelo)} fichiers, {moy:,} octets en moyenne, '
          f'le plus gros {max(t[2] for t in tabelo):,}')


if __name__ == '__main__':
    main()
