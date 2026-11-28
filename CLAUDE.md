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

    make -f build.mk          # gramatiko.pdf, then its word spaces (pypdf)
    make -f build.mk checks   # the twelve checks

Two of them are expected to speak, and a third figure that moves without
a reason is a defect, not a detail:

* **check 11 (carding)** fails on **7** pages, all under 3.8 mm;
* **check 10** flags folio **136**, which has never been settled.

Then the page and its machine-readable forms, which come from the
transcription and from nothing else:

    python3 tools/html.py             # 868 anchors, 1231 paragraphs, 412 notes
    python3 tools/machine_readable.py # 49 chapters, 1692 blocks, 492,517 bytes
    python3 tools/temi.py             # 9 topics over 1643 blocks, 171,661 bytes
    python3 tools/afixi.py            # 65 affixes (43 + 19 + 3), 133,424 bytes
    python3 tools/witnesses.py        # 148 witnesses, exits non-zero if one is lost

**THE FIGURES ABOVE HAVE MOVED FOURTEEN TIMES. THE FIRST TIME:** `gramatiko.md` gave
492,417 bytes and `temi/` 171,327 — the line here said 171,328, off by one
since it was written. A word broken across a line of the facsimile comes
back as two runs, the transcription reopening the emphasis on the second
half, so « maledukita » was `<i>male</i><i>dukita</i>`. The page is right
either way, two touching italic runs drawing as one; **the Markdown was
not**: it became « male\*\*dukita\* », which is unmatched markup and an
unreadable word for whoever reads the `.md` rather than the page.
MEASURED: 127 such words, 40 of them in SUFIXI — ama|bas, deses|timo,
male|dukita, paro|ladar, pik|turo, skul|tata. `as_markdown()` now joins two
runs of the SAME tag with nothing between them, which is invisible because
they already drew as one, and the space is what tells this apart from two
separate emphasised words. 124 of the 127 are joined; the other 3 are
text-plus-bold across a folio mark, which is well-formed already.

**And `temi/kondicionalo.md` went from 20 blocks to 21 by that alone** — the
recovered block is a note in which « kondicionalo » had been split, so no
search for it could ever have found it. A topic file is only as complete as
the text it searches.

**THE SECOND TIME, two notes came back.** On folios 82 and 98 note (1) was
chained to note (2) by a `\nl`, the fault the journal records at folios
59–63, 74, 93, 101, 104 and 106. In the PDF note (1) was justified across the measure and note (2)
lost its indent; on the page, `html.py` read « (1) … (2) … » as one note,
so each call (2) pointed at nothing and each note (2) sat under the call
(1). Separated: 410 → 412 notes, 857 → 859 anchors, 1690 → 1692 blocks,
491,595 → 491,601 bytes, and `temi.py` searches 1643 blocks where it
searched 1641; no topic file changes.

**AND THE VOLUME HAD NOT COMPILED SINCE 23a3d74.** That commit moved
`ornamenti/` to `ornaments/` and renamed two plates, and the four
`\includegraphics` kept the old names; `gramatiko.pdf` was the build of
16 August. Repointed, the volume compiles again, and is pixel-identical
to that build, rendered at 100 dpi, on 234 of its 236 pages: the other
two are folios 82 and 98.

**THE THIRD TIME, two misreadings of the facsimile.** Folio 12 reads
« ma **a**, **e** recevas », transcribed « ma **a** e recevas »; folio 100
reads « ∛2 = radiko tria di du », transcribed « 3/2 », a fraction.
491,601 → 491,607 bytes: five for « , **e** », one because « ∛ » is three
bytes where « / » was one. Nothing else moves: no topic, no affix, no
anchor, and the PDF differs from the previous build on those two pages
only, each in the one line — in its pixels and in its text.

**THE FOURTH TIME, the exponents.** The Markdown kept the text of
`<sup>` and lost its raising: « 1,000,000² » read « 1,000,0002 », « 2³ »
« 23 ». The 14 numeric superscripts, all exponents, are now Unicode
superscript digits; the 179 letter ones (« 1ro », « 2e ») stay flat.
491,607 → 491,618 bytes. And seven of the fourteen are in a table the
Markdown does not carry at all: it keeps headings, paragraphs and notes,
and drops the 8 tables and 13 centred lines of the page — the pronouns of
folio 32 and the passive of folio 50 among them. Recorded in the journal;
not yet corrected.

**THE FIFTH TIME, the Spanish accents, set by decision.** Nine Spanish
words the transcription reads without their accents, as the volume very
probably prints them — « acuatico », « heroina », « habias », « partis »
and five more, folios 12, 158, 208 and 209 — are now set with them, by `\VUcorrige` (see the rule below). One byte each:
491,618 → 491,627 in `gramatiko.md`, 133,039 → 133,040 in `afixi/`
(« heroína », under `-in-`).

**THE SIXTH TIME, the typos ruled on one by one.** On 27 November 2026 the
commissioner went through every typo and irregularity the survey had
recorded, and six typos it had missed. 84 rulings to correct, set by 94
`\VUcorrige`; 28 recorded « typos » that are not typos — « ciencal », « direte »,
« lon », « solvor », « esor », « specala », « Ofical »… are Ido, or the
book's own usage — their notes corrected; 41 kept as printed. And on the
way, **17 misreadings of the transcription**, corrected in it: « specal »
read « special » eight times, and weights read roman that the page prints
bold on folios 131, 134, 142, 160, 162 and 163 — the survey's bold/roman
calls in part 2 are not to be trusted without enlarging. Then thirteen
foreign words the 1925 print misforms — Spanish « tambien », « bune »,
« alreador », « come si »…, Italian « diffati », « pero », Portuguese
« ja », the title « Grammarie Complète » — each confirmed on the spreads
and ruled corrected. 491,627 → 491,891 bytes in `gramatiko.md`, 171,550 →
171,572 in `temi/`, 133,040 → 133,238 in `afixi/`; anchors, paragraphs,
notes and blocks unchanged. See the journal, « Typos and irregularities
ruled on » and « Foreign words misformed in the print ».

**THE SEVENTH TIME, typos the survey never recorded.** Found by scanning
the transcription — one-off words a letter from a common one, quotation
marks and brackets that close nothing — and each confirmed on the spreads:
« replusas », « voltivo », « komplimenti », « genetivo », « rimarkigez »,
« la sua, Ex, : » and six faulty quotations, all ruled corrected; and one
more misreading, a bracket the transcription had added at folio 63; and
folio 173's second list, « internaciona, dukapa, trifolia », « longhara »,
read roman and printed bold. 491,891 → 491,934 bytes in `gramatiko.md`,
171,572 → 171,591 in `temi/`.
About forty other unclosed quotations were listed in the journal, not
yet checked against the page — checked since: the eighth time.

**THE EIGHTH TIME, the unclosed quotations.** All 44 looked at on the
spreads: none misread; nine run on and close later, seven are the book's
way (one » closing two nested quotations, or a quotation reopened after
an ellipsis), and 28 close nowhere — one already ruled kept (folio 189),
27 ruled corrected by the commissioner, each at the place proposed,
by `\VUcorrige{}{ »}`. 491,934 → 492,069 bytes in `gramatiko.md`, five
bytes a mark; 171,591 → 171,611 in `temi/`, 133,238 → 133,268 in
`afixi/`; anchors, paragraphs, notes and blocks unchanged. See the
journal, « Unclosed quotations checked against the page ».

**THE NINTH TIME, the weights, checked against the spreads.** Folios 12 to
232, every weight in doubt enlarged and measured within its line: the
transcription had misread it on 71 leaves of both parts — bold runs that
took in a roman « o », « Ex. : » or the author's gloss; examples, cited
forms and endings read roman; four italics that are upright — all
corrected in it. Three typos of the print set by `\VUcorrige` (folios 55,
96, 195), and one ruling of 27 November withdrawn: folio 198's endings are
bold in the print, not irregular. 492,069 → 492,453 bytes in
`gramatiko.md`, 171,611 → 171,649 in `temi/`, 133,268 → 133,416 in
`afixi/`; **anchors 859 → 868**: nine time adverbs that are bold now have
one, and the four that a shortened headword would have moved are KEPT by
`KEPT_ADDRESSES` in `tools/html.py` — a weight corrected must not move an
address. The affix headwords are all bold — the commissioner's ruling, on
the book, against what two of them look like on the photographs: see the
journal, « The affix headwords are bold ».

**THE TENTH TIME, rulings looked at again, on the book.** Two anomalies
kept on 27 November are corrected like their kind — folio 189's unclosed
quotation, folio 171's « bisenca.. » — and the book settles four weights
against the survey or the photographs: folio 186's four « -i » and folio
75's « en », « ek » are bold (the second a correction of this pass
reversed); folio 144's « pedi » and folio 141's « -ier » are bold in 1925,
which makes the first a misreading rather than a typo and gives the
second's \VUcorrige its true first argument. 492,453 → 492,481 bytes in
`gramatiko.md`; nothing else moves. See the journal, « Rulings looked at
again, on the book ».

**THE ELEVENTH TIME, two letters.** Folio 24 prints « transkribo » with
one s twice — the book's only two, against seven « transskrib- », each
checked on the spreads — and the commissioner ruled both typos:
« transskribo », by `\VUcorrige`. 492,481 → 492,483 bytes in
`gramatiko.md`. (Folio 181's « filosôfio » → « filozôfio », ruled the same
day, moved no figure: a z for an s; nor did « Iosef », « tante male » and
the four « prizent- » after it.)

**THE TWELFTH TIME, one letter less.** Two new scans for the typos the
first had missed — stems one letter from a much commoner stem, whatever
their count; an adjective in -a before an adverb in -e — found three, each
confirmed on the spreads and ruled corrected: « konstrastus » (folio 200),
« Cigari », « cigari » (44, 167). 492,483 → 492,482 bytes in
`gramatiko.md`. See the journal, « Kontrastus; sigari ».

**THE THIRTEENTH TIME, two full stops**, both seen by the commissioner
and confirmed on the spreads: folio 74's note (1) ends on a comma, and
ends there (folio 75's notes open on a new (1)); folio 207's « ... ke me
ne eroris pri ca punto » closes its section with no stop before the
asterism. Ruled corrected, by `\VUcorrige`. 492,482 → 492,483 bytes in
`gramatiko.md`, the added stop; the other is a comma for a stop.
`temi/index.md`'s unnumbered bytes go 249,417 → 249,418, which makes the
figure under « THE BOOK NUMBERS LESS THAN HALF » true again: it had been
one byte high since the twelfth time. See the journal, « Two full stops ».

**THE FOURTEENTH TIME, 29 spaces**, and not one letter. A note that runs
over to the next page ends its page on `…word%` and resumes overleaf
after `\VUcontinue`; `html.py` stripped the `\VUcontinue` as layout, then
took the space it left behind for the one between the words, and stripped
that too. 29 notes were welded across the page from the first build of
the reading page — « frazotradukenda » (folio 73), « olpovas »,
« quaamas », « lor meamariajo » — and the Markdown with them. Found
when folio 65's note, continued from 64, got the `\VUcontinue` it lacked
and came out « sempreplu ». 492,483 → 492,517 bytes in `gramatiko.md`,
171,649 → 171,661 in `temi/`, 133,416 → 133,424 in `afixi/`; anchors,
paragraphs, notes and blocks unchanged. See the journal, « Page-end lines
that end their note ».

`tools/witnesses.py` is the guard against a lost container and a bad
merge: one characteristic string per fix already made. When a rename
moves an identifier a witness names, the witness is repointed — it is
not deleted.

The PDF's text layer is written twice: by pdflatex, and then by
`tools/word_spaces.py`, which puts a real space character into every gap
between words. A change to that tool is checked by rendering every page
against the previous build: not one pixel may move.

Several of these want the scan, which is **not in the repository**
(167 MB, `scan/pages/f0001.jpg` … `f0240.jpg`), and `pdflatex`,
`pdftotext` and `pdfinfo`. Where those are missing, say so rather than
reporting a check as passed.

## Four rules that are not negotiable

**THE SOURCE DOES NOT MOVE.** `content/*.tex` reproduces the facsimile
as it stands, the printer's typos of 1925 included. One line of the
facsimile is one line of the PDF. What is corrected is corrected in the
tools or in the preamble, never in the transcription.
A correction the commissioner orders to the LETTER is marked where it
stands, `\VUcorrige{as printed}{as set}`: the 1925 reading stays in the
transcription as the first argument, and the preamble sets the second —
make the macro give `#1` and the volume is the 1925 print again. Its uses
so far: the Spanish accents, and the commissioner's rulings of 27 November
2026 on the typos and irregularities the survey recorded. It is not a
licence to correct a typo on one's own judgement: a typo stays until the
commissioner rules on it, and a NEW one found is recorded in its leaf's
note and put to the commissioner. A MISREADING of the transcription is
another matter — it is corrected in the transcription, where it was made.

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
number; 723 blocks and 249,431 bytes carry none (the bytes move with
every correction of the text: `temi/index.md` gives them as last counted —
this line said 249,254 long after it stopped being true), and 27 of the 49
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
