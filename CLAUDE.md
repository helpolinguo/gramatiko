# Working notes

This file says how we work on this repository. The *what* is in
`README.md`, which is the project's documentation; we do not repeat it
here, we point at it.

## Branches and pull requests

**The project lives on `main`**, which is the default branch.

We never write to `main` directly. We work on a branch, and bring it in
through a **pull request whose base is `main`**, opened as a draft. A
branch always starts again from the current `main`:

    git fetch origin main
    git checkout -B <branch> origin/main

**A branch is named after its subject**, in English, in lower case, the
words joined by hyphens: `claude/working-notes`,
`claude/check-labels`, `claude/leaves-15-20`. No session identifier, no
random suffix — a name like that says nothing six months later, and it
lies the moment the branch serves something other than what it was
opened for. The `claude/` prefix stays: it says who held the pen.

A merged pull request is finished: it cannot carry a sequel. The next
piece of work starts again from `main`, and it is a new pull request.

## What we check before pushing

The volume compiles, always, and the twelve checks run against it:

    make -f build.mk          # gramatiko.pdf
    make -f build.mk checks   # the twelve checks

Two of them are expected to speak, and a third figure that moves without
a reason is a defect, not a detail:

* **check 11 (carding)** fails on **7** pages, all under 3.8 mm;
* **check 10** flags folio **136**, which has never been settled.

Then the page and its machine-readable forms, which come from the
transcription and from nothing else:

    python3 tools/html.py             # 857 anchors, 1231 paragraphs, 410 notes
    python3 tools/machine_readable.py # 49 chapters, 1690 blocks, 492,417 bytes
    python3 tools/temi.py             # 9 topics over 1641 blocks, 171,328 bytes
    python3 tools/witnesses.py        # 56 witnesses, exits non-zero if one is lost

`tools/witnesses.py` is the guard against a lost container and a bad
merge: one characteristic string per fix already made. When a rename
moves an identifier a witness names, the witness is repointed — it is
not deleted.

Several of these want the scan, which is **not in the repository**
(167 MB, `scan/pages/f0001.jpg` … `f0240.jpg`), and `pdflatex`,
`pdftotext` and `pdfinfo`. Where those are missing, say so rather than
reporting a check as passed.

## Four rules that are not negotiable

**THE SOURCE DOES NOT MOVE.** `content/*.tex` reproduces the facsimile
as it stands, the printer's typos of 1925 included. One line of the
facsimile is one line of the PDF. What is corrected is corrected in the
tools or in the preamble, never in the transcription.

**A MEASUREMENT IS NOT AN ESTIMATE.** The whites that frame a title are
measured on the baselines, before composition; they are never deduced
from the pitch. And a doubtful weight is never decided on the strip:
enlarge it. On this volume, **nine first readings of weight out of nine**
turned out to be wrong before enlargement — the ink spreads, and a roman
at actual size looks bold.

**`temi/` QUOTES THE BOOK AND WRITES NO GRAMMAR.** Every block in it is
lifted verbatim from `chapitri/`; the one editorial act is the list of
search terms in `TOPICS` at the head of `tools/temi.py`, and each file
prints the terms that built it so the choice can be judged. A rule of
grammar composed here rather than quoted would be indistinguishable, to
a reader, from Beaufront's own — which is the failure the whole of
`temi/` exists to prevent.

**THE BOOK NUMBERS LESS THAN HALF OF ITSELF.** 139 paragraphs carry a
number; 723 blocks and 249,254 bytes carry none, and 27 of the 49
chapters have no number anywhere. Anything keyed to the numbers alone
drops more than half the corpus — `temi.py` did, in its first cut, and
lost the passage where Beaufront argues against the accusative. Cite by
number where there is one, by chapter and block rank where there is not.
And two numbers do not behave: **§ 28 does not exist** and **§ 55 is
used twice**.

**§ 32 WAS THE THIRD, AND IT IS NOW FIXED — the count above was 138,
and the line for html.py above still read « 856 anchors, 1230 paragraphs »
for a while after: § 32 becoming its own paragraph moved both by one, and
the figure was corrected only when the checks were next run. A number
written by hand in a second place is a number that will be wrong there.**
The transcription had it right all along, at the head of its own line in
`content/10-part1.tex`; what lost it was `\parplein`, which marks the
last line of a page as full and from that infers the paragraph runs on.
It does, almost always. At § 32 it does not: the paragraph ends on a
full line and a numbered one begins overleaf. `close_para()` now refuses
to rejoin a block that OPENS WITH A PARAGRAPH NUMBER, that being
Beaufront's own mark for the start of one. It splits exactly one block
in the whole book, and gives § 32 an anchor on the reading page besides.

**A PRODUCED FILE IS NOT A PLACE WHERE ONE WRITES.** `index.html`,
`gramatiko.md`, `chapitri/*.md` and `temi/*.md` are regenerated — `temi/`
is EMPTIED at every run, so a file left there under an old name goes;
an edit made in them
by hand disappears at the next build. What must change is changed in
`content/` or in `tools/` — the page's own markup and style live in the
`TEMPLATE` string at the head of `tools/html.py`, not in a separate
file.

This one has been paid for. `index.html` carried **four** hand-edits the
generator knew nothing about — the machine-readable head block, the
header's `padding-inline`, the search field's iOS attributes and the
back-button link. Every `make` silently destroyed them.

**A NAME TOKEN IS NOT ALWAYS A NAME.** A keyword argument of numpy's, a
key in a dictionary we read back, a marker in a template: those are data
wearing a name's clothes, and a rename must skip them. The published
anchors and `chapitri/` are the same thing at the scale of the site — an
anchor is an address. See the note on language at the end of
`README.md`.

## Writing

Commit messages and code comments **in English**, in the house style: the
finding at the head and in capitals, measurements rather than
suppositions, the approaches tried and then abandoned recorded, and an
earlier assertion that has become false corrected **where it is
written**.

The `\VU…` macros keep their names, for the same reason the source does
not move: they are the vocabulary in which the facsimile was recorded.

`docs/journal.md` is in French. It is the record of how the work was
done, written as it was done; it is not translated, and a new entry is
written in English at the end. `docs/transcription-brief.md`, which is
the instruction still handed to whoever surveys a leaf, is in English.
