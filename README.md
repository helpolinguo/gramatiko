# Kompleta Gramatiko Detaloza

A diplomatic transcription of **_Kompleta Gramatiko Detaloza di la Linguo
Internaciona Ido_**, L. de Beaufront, Editerio Meier-Heucke, Esch-Alzette
(Luxembourg), 1925 — typeset in LaTeX and published as a searchable reading
page at [**ido.help/gramatiko**](https://ido.help/gramatiko/).

The rule the whole project answers to: **one line of the facsimile is one line
of the PDF** — same pagination, same folios, same line breaks, same changes of
type size. The 1925 typos are kept.

This is one of three books gathered at [ido.help](https://ido.help/); the other
two are [tabeli](https://github.com/helpolinguo/tabeli) and
[dicionario](https://github.com/helpolinguo/dicionario), and the front door is
[helpolinguo.github.io](https://github.com/helpolinguo/helpolinguo.github.io).

## Layout

```
main.tex             the volume: one \input per part
preamble.tex         every setting and every macro, each justified by measurement
content/*.tex        the transcription itself — the source of everything
build.mk             make -f build.mk           -> gramatiko.pdf
                     make -f build.mk controles -> the checks
index.html           the reading page      }  generated: see below
gramatiko.md         the book laid flat    }
chapitri/*.md        one file per chapter  }
ornaments/           the three cut plates: portrait, vignette, fleuron
tools/               the measuring, generating and checking tools
docs/journal.md      why every value is what it is
docs/transcription-brief.md  how a leaf is surveyed
```

## Building

```sh
make -f build.mk                 # gramatiko.pdf
python3 tools/html.py            # index.html, from content/*.tex
python3 tools/machine_readable.py # gramatiko.md and chapitri/*.md, from index.html
make -f build.mk controles       # the twelve checks
```

`index.html`, `gramatiko.md` and `chapitri/*.md` are **generated, never edited
by hand**: anything that must change is changed in `content/` or in `tools/`.
The build file is named `build.mk` rather than `Makefile` for a reason recorded
in the journal.

The LaTeX build needs `pdflatex` with XCharter and newtx. The tools need
Python 3 with `numpy`, `Pillow` and `opencv-python`; the scan-facing ones also
want `pdftotext` and `pdfinfo` (poppler). The 167 MB scan is not in the
repository — the transcription and the composed volume are.

## The checks

`tools/checks.py` runs twelve checks against the facsimile, and they are the
spine of the project: pagination and overflows, a line-by-line comparison of
the composed PDF with the transcription, the rules governing `\nl` and `\cc`,
forbidden line openings, effective margins, a visual juxtaposition at 300 dpi,
ink weight, the alignment of line openings and endings, vertical drift, and
that each note is a paragraph.

`tools/witnesses.py` is the other half: one characteristic string per fix, so
that a lost container or a bad merge is detected rather than discovered later.
It exits non-zero if any fix has gone missing.

## A note on language

The source is in English — comments, identifiers, filenames and commits. Three
things deliberately stay as they are:

- **The interface is in Ido**: the reading page's text, its accessible names
  and its tooltips, and the URLs of its sections.
- **The `\VU…` macros keep their names.** They are the vocabulary in which the
  facsimile was recorded, and `content/*.tex` is the diplomatic transcription —
  the one thing in this repository that does not move.
- **The generated page's own class names and anchors keep theirs.** An anchor
  is an address: `#alfabeto` is cited, bookmarked and linked to, and renaming
  it would break every link ever copied.

Translating the source changed nothing a reader of the site can see.

## Licence

The code in this repository is under the **MIT Licence** — see
[`LICENSE`](LICENSE). Copyright © 2026 Gilles-Philippe Morin.

The **work transcribed here is in the public domain in Canada**, where this
project is maintained: it was published in 1925 and its author died in 1935,
more than fifty years before Canada's 2022 term extension, which did not
restore expired copyrights. Copyright terms differ from country to country;
readers elsewhere should satisfy themselves of the position under their own
law. The transcription, the typesetting, the tools and the reading page are
this project's own work, and are covered by the licence above.
