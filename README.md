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
afixi/*.md           one file per affix    }
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
python3 tools/afixi.py           # afixi/*.md, from chapitri/*.md
make -f build.mk checks          # the twelve checks
```

`index.html`, `gramatiko.md`, `chapitri/*.md`, `temi/*.md` and
`afixi/*.md` are
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
his own book.** 139 paragraphs carry a number, § 1 to § 140 — but 723 blocks,
249 254 bytes, carry none, and 27 of the 49 chapters have no number anywhere,
`sufixi.md` (88 kB) and `vortordino.md` among them. A first cut of `temi.py`
keyed everything to the numbers and so dropped all of it — including the one
passage where Beaufront argues against the accusative outright, which is the
whole reason the `-n` topic exists.

The unit is therefore **the block**, and the number is a label it carries when
the book gives it one. A block inside § 126 is cited `§ 126`; a block in an
unnumbered chapter is cited by chapter and rank. Every citation stays
checkable against a printed copy and nothing is out of reach.

Two facts about the numbering, recorded in `temi/index.md` because a model
citing a number needs them: **§ 28 does not exist** in the transcription —
GRADI KOMPARALA, which sits between § 27 and § 29, carries no number at all;
and **§ 55 appears twice**, both times in ADVERBI, so citing "§ 55" does not
identify one of them.

**There was a third, and it is fixed: § 32.** The count above read 138 before
it. `\parplein` marks a page's last line as full and infers from that that
the paragraph runs on — true almost everywhere, false at § 32, where the
paragraph ends on a full line and a numbered one begins overleaf. The
transcription was never wrong: `content/10-part1.tex` has `32. ---` at the
head of its own line, like § 31 and § 33. `close_para()` in `tools/html.py`
now refuses to rejoin a block that OPENS WITH A PARAGRAPH NUMBER, that being
Beaufront's own mark for the start of one. It splits exactly one block in the
whole book, and gives § 32 an anchor on the reading page besides.

## One file per affix

Ido builds its vocabulary by derivation, and the Dicionario holds only the
**roots**: `kovrilo`, `skribilo`, `dometo`, `hundino` are none of them
headwords, and 9,473 articles will not yield one of them. What yields them
is the affix — and the affix lived in `SUFIXI`, 89 kB of continuous prose.
So the cheapest question the site can be asked, *what does `-il-` do*, cost
90 kB, and the reader still had to find the right paragraph inside it.

`afixi/` gives each of the **65 affixes** its own address — 43 suffixes, 19
prefixes, 3 technical prefixes — holding the book's own paragraphs on it,
from the head that opens it to the head that opens the next. 2 kB on
average. **No rule of grammar is composed there**: this is the discipline of
`temi/`, applied to a division the book itself makes.

It needs no search terms, and `temi/` does. `temi/` collects topics that
*cross* the chapters and must search for them, which is an editorial act it
prints in every file. An affix crosses nothing: Beaufront opens its
discussion with the affix in bold, a stop and a dash, and closes it by
opening the next.

**THE HEAD IS NOT ALWAYS SET THE SAME WAY, AND THAT COST FIVE AFFIXES.**
The stop falls inside the bold in most of the book — `**-ach-.** —` — and
**outside it** in five places: `**-ar-**. —`, and the same for `-atr-`,
`-e-`, `-ebl-` and `-ind-`. A pattern admitting only the first form reports
55 affixes and looks right, and two of the five it silently drops are
**`-ebl-` and `-ind-`** — which are among the most used suffixes in the
language. The technical prefixes carry a third asterisk besides —
`***equi-.**` against `**mono-.**` — and admitting only two loses `equi-`
and `ko-`, two thirds of that chapter.

The dash is what keeps the pattern honest. Paragraphs open with a bold word
often enough — `**Parolo** esas frazo`, `**Posiblo** = ...` — and none of
them carries the dash that follows an affix.

**The index line is mechanical.** Form, the chapter it stands in, the first
example **the book prints**, and the weight. `Ex. :` is Beaufront's own
mark, and what follows it is the example in whatever emphasis he set it —
bold under `-il-` (`pektilo`), italic under `bi` (`biciklo`), and none at
all under `-iz-` (`Ex. : armizar`). Where he writes no `Ex. :`, the bold
runs are taken, and the italic after them.

A candidate must carry the affix's letters **where the affix goes**: a
suffix sits immediately before the grammatical ending, which is the book's
own rule of derivation. Without that test `Franca` answered for `-an-` —
the letters are in it, in the middle, and the word is not a derivation at
all. `auto` is the one affix left without an example, and honestly so: its
examples stand in the chapter's opening footnote, not in its own section.

`sen-` gets no file, because the book gives it no head: it is discussed
under `ne-`, and that is where it stays.

## The checks

`tools/checks.py` runs twelve checks against the facsimile, and they are the
spine of the project: pagination and overflows, a line-by-line comparison of
the composed PDF with the transcription, the rules governing `\nl` and `\cc`,
forbidden line openings, effective margins, a visual juxtaposition at 300 dpi,
ink weight, the alignment of line openings and endings, vertical drift, and
that each note is a paragraph.

`tools/witnesses.py` is the other half: one characteristic string per fix, so
that a lost container or a bad merge is detected rather than discovered later.
It exits non-zero if any fix has gone missing. It checks **56** witnesses.

**CHECK 4 REPORTS ONE FAILURE, AND IT IS CORRECT AS TRANSCRIBED. DO NOT
"FIX" IT.**

    folio 174 line 38: \nl between « sen » and « fingro » — the welding
    « senfingro » is attested: a hyphen of division was probably lost

The heuristic is sound and the conclusion is wrong here, for the one reason
that cannot be coded around: **the passage is about the difference between
the two forms.** Beaufront writes, in a note on `senfingro` — *Progreso*,
VII, 495 —

> Se *senfingri* povas dicernesar de *sen fingri*, *senfingro* (homo) povas
> tam bone dicernesar de *sen fingro*.

*If* senfingri *can be told from* sen fingri, *then* senfingro *(a person)
can be told just as well from* sen fingro. The check fires because the
welded form is attested — it is, three lines above, and again on the same
line — while `fingro` alone is rare, which in this passage it deliberately
is. Welding the two would make the sentence say that `senfingro` can be
told from `senfingro`, and destroy the distinction the note exists to draw.

`content/20-part2.tex` line 3716 shows the transcriber welding correctly
where a hyphen of division really is there — `interna\cc cionajo` — so the
`\nl` four lines later is a choice, not an oversight.

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
