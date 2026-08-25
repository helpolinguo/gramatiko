#!/usr/bin/env python3
"""L'ARCHIVE DE LIVRAISON : un ZIP, avec gramatiko.pdf a la racine.

Six pertes de conteneur ont montre que la seule copie fiable est celle
que le commanditaire detient. Le format de cette copie ne doit donc pas
dependre de ce dont je me souviens d'une fois sur l'autre : il est ecrit
ici.

    python3 tools/archive.py [chemin.zip]

Le scan (167 Mo) et le depot git restent dehors : l'archive porte la
SOURCE et le VOLUME COMPOSE, non l'atelier.

Les temoins passent d'abord. Une archive livree sans eux serait le
moyen le plus sur de figer une perte.
"""
import os, subprocess, sys, zipfile

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A la racine de l'archive : la source, le volume compose, la page.
FICHIERS = ['main.tex', 'preamble.tex', 'build.mk', 'LISEZ-MOI.md',
            '.nojekyll', 'index.html', 'gramatiko.pdf']
DOSSIERS = ['content', 'ornaments', 'tools']
# Ce qui ne se livre pas : les rebuts de compilation et les caches.
REBUTS = ('.aux', '.log', '.out', '.toc', '.pyc', '.synctex.gz')
HORS = {'__pycache__', '.git', 'scan'}


def fichiers():
    for f in FICHIERS:
        p = os.path.join(R, f)
        if os.path.exists(p):
            yield p, f
        else:
            print('  ABSENT : %s' % f, file=sys.stderr)
    for d in DOSSIERS:
        for rac, sous, noms in os.walk(os.path.join(R, d)):
            sous[:] = [x for x in sous if x not in HORS]
            for n in sorted(noms):
                if n.endswith(REBUTS):
                    continue
                p = os.path.join(rac, n)
                yield p, os.path.relpath(p, R)


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 \
        else os.path.join('/tmp', 'kompleta-gramatiko.zip')

    t = subprocess.run([sys.executable, os.path.join(R, 'tools/witnesses.py')],
                       capture_output=True, text=True)
    print(t.stdout.strip())
    if t.returncode:
        sys.exit('temoins en defaut : rien n\'est livre')

    pdf = os.path.join(R, 'gramatiko.pdf')
    if not os.path.exists(pdf):
        sys.exit('gramatiko.pdf manque : composer le volume avant de livrer')

    n = 0
    with zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for chemin, dedans in fichiers():
            z.write(chemin, dedans)
            n += 1
    print('%s  %d fichiers, %d ko'
          % (sortie, n, os.path.getsize(sortie) // 1024))


if __name__ == '__main__':
    main()
