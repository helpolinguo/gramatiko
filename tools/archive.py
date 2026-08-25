#!/usr/bin/env python3
"""THE DELIVERY ARCHIVE: a ZIP, with gramatiko.pdf at the root.

Six lost containers have shown that the only reliable copy is the one the
commissioner holds. The format of that copy must therefore not depend on
what I happen to remember from one time to the next: it is written down
here.

    python3 tools/archive.py [path.zip]

The scan (167 MB) and the git repository stay outside: the archive carries
the SOURCE and the COMPOSED VOLUME, not the workshop.

The samples go in first. An archive delivered without them would be the
surest way of freezing a loss.
"""
import os, subprocess, sys, zipfile

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# At the root of the archive: the source, the composed volume, the page.
FILES = ['main.tex', 'preamble.tex', 'build.mk', 'README.md', 'LICENSE',
            '.nojekyll', 'index.html', 'gramatiko.pdf']
FOLDERS = ['content', 'ornaments', 'tools', 'docs']
# What is not delivered: the leavings of compilation and the caches.
LEAVINGS = ('.aux', '.log', '.out', '.toc', '.pyc', '.synctex.gz')
OUTSIDE = {'__pycache__', '.git', 'scan'}


def file_paths():
    for f in FILES:
        p = os.path.join(R, f)
        if os.path.exists(p):
            yield p, f
        else:
            print('  MISSING: %s' % f, file=sys.stderr)
    for d in FOLDERS:
        for root, sous, names in os.walk(os.path.join(R, d)):
            sous[:] = [x for x in sous if x not in OUTSIDE]
            for n in sorted(names):
                if n.endswith(LEAVINGS):
                    continue
                p = os.path.join(root, n)
                yield p, os.path.relpath(p, R)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 \
        else os.path.join('/tmp', 'kompleta-gramatiko.zip')

    t = subprocess.run([sys.executable, os.path.join(R, 'tools/witnesses.py')],
                       capture_output=True, text=True)
    print(t.stdout.strip())
    if t.returncode:
        sys.exit('witnesses in default: nothing is delivered')

    pdf = os.path.join(R, 'gramatiko.pdf')
    if not os.path.exists(pdf):
        sys.exit('gramatiko.pdf missing: compose the volume before delivering')

    n = 0
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path_of, inside in file_paths():
            z.write(path_of, inside)
            n += 1
    print('%s  %d files, %d kB'
          % (out_path, n, os.path.getsize(out_path) // 1024))


if __name__ == '__main__':
    main()
