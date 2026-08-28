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
                     make -f build.mk checks    -> the checks
index.html           the reading page      }  generated: see below
gramatiko.md         the book laid flat    }
chapitri/*.md        one file per chapter  }
temi/*.md            one file per topic    }
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
python3 tools/temi.py            # temi/*.md, from chapitri/*.md
make -f build.mk checks          # the twelve checks
```

`index.html`, `gramatiko.md`, `chapitri/*.md` and `temi/*.md` are
**generated, never edited by hand**: anything that must change is changed in `content/` or in `tools/`.
The build file is named `build.mk` rather than `Makefile` for a reason recorded
in the journal.

The LaTeX build needs `pdflatex` with XCharter and newtx. The tools need
Python 3 with `numpy`, `Pillow` and `opencv-python`; the scan-facing ones also
want `pdftotext`, `pdfinfo` and `pdftoppm` (poppler). The 167 MB scan is not in the
repository — the transcription and the composed volume are.

## One file per topic

`chapitri/` answers *how is the plural formed* — there is a chapter called
LA PLURALO EN IDO. It does not answer **what does this grammar say about the
`-n` ending**, because there is no chapter about it: the discussion lies in
SINTAXO, VORTORDINO, ADVERBI and four more. A topic that cuts across chapters
had no address, and what has no address cannot be fetched, only guessed at.

`temi/` gives nine such topics one. Each file holds **the book's own blocks**,
verbatim — no sentence of grammar is composed there. The editorial act is the
choice of search terms, and it is therefore printed at the head of every file
so a reader can see what was searched for and judge it.

| topic | blocks | | topic | blocks |
| --- | ---: | --- | --- | ---: |
| akuzativo (the `-n` ending) | 47 | | pasivo | 41 |
| subjekto | 41 | | kondicionalo | 20 |
| komplemento | 53 | | imperativo | 10 |
| participo | 47 | | negado | 10 |
| infinitivo | 35 | | | |

**MEASURED, AND IT CHANGED THE DESIGN: Beaufront numbered less than half of
his own book.** 138 paragraphs carry a number, § 1 to § 140 — but 723 blocks,
249 254 bytes, carry none, and 27 of the 49 chapters have no number anywhere,
`sufixi.md` (88 kB) and `vortordino.md` among them. A first cut of `temi.py`
keyed everything to the numbers and so dropped all of it — including the one
passage where Beaufront argues against the accusative outright, which is the
whole reason the `-n` topic exists.

The unit is therefore **the block**, and the number is a label it carries when
the book gives it one. A block inside § 126 is cited `§ 126`; a block in an
unnumbered chapter is cited by chapter and rank. Every citation stays
checkable against a printed copy and nothing is out of reach.

Three facts about the numbering, recorded in `temi/index.md` because a model
citing a number needs them: **§ 28 does not exist** in the transcription —
GRADI KOMPARALA, which sits between § 27 and § 29, carries no number at all;
**§ 32 is in the text but not findable by number**, its number having been run
onto the end of the preceding paragraph; and **§ 55 appears twice**, both times
in ADVERBI, so citing "§ 55" does not identify one of them.

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

The source is in English — comments, identifiers, filenames and commits. Four
things deliberately stay as they are:

- **The interface is in Ido**: the reading page's text, its accessible names
  and its tooltips, and the URLs of its sections.
- **The `\VU…` macros keep their names.** They are the vocabulary in which the
  facsimile was recorded, and `content/*.tex` is the diplomatic transcription —
  the one thing in this repository that does not move.
- **The generated page's own class names and anchors keep theirs.** An anchor
  is an address: `#alfabeto` is cited, bookmarked and linked to, and renaming
  it would break every link ever copied.
- **`chapitri/` keeps its name**, for the same reason: it is published at
  `https://ido.help/gramatiko/chapitri/index.md` and named in `/llms.txt`,
  where other programs read it.

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
