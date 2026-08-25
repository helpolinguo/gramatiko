# Brief for the transcription of a folio

You are recording **one** folio of the facsimile of the *Kompleta
Gramatiko Detaloza di la Linguo Internaciona Ido*, L. de Beaufront,
Meier-Heucke, 1925 — a public-domain work, scanned by the maintainer,
who asks for a diplomatic transcription.

**You typeset nothing yourself**: you hand back a LaTeX block, which the
assembler will check and lay. You write in no file of the project.

---

## 1. The rule that overrides every other

**One line of the facsimile = one line of the block handed back.** No
break is left to LaTeX. Every line end carries an explicit mark:

* `\nl` — the line ends on a whole word;
* `\cc` — the line ends on a broken word (the hyphen is set by the
  macro: **do not write it**);
* nothing — this is the last line of a paragraph;
* `\parplein` — the last line of a paragraph that runs to the right
  margin (`fin` close to 0 in the geometry).

`\\` is **forbidden**.

## 2. The text

The book is in Ido. You correct nothing: **the original's typos are kept
as they stand**, and you report them.

You read the facsimile, not your memory of Ido. A word that looks strange
to you is probably what is printed.

## 3. The enrichment

* **Bold** (`\VUgras{...}`): an Ido form quoted as a headword, or an
  example given prominence.
* *Italic* (`\textit{...}`): everything quoted from another language, and
  grammatical terms quoted as terms.

**A doubtful weight is never decided on the strip.** Enlarge (see § 6).
On this project, nine first readings of weight out of nine turned out to
be wrong before enlargement.

## 4. Word spaces in the source

A convention checked against the composed corpus (440 against 31, 82
against 1, 9 against 975):

* `;` `?` `!` are written **tight** against the word before them;
* `:` is written **spaced**.

Active catcodes lay the thin space at composition. The quotation marks
are `«` and `»`, the apostrophe `'`, the em dash `---`, the paragraph
sign the literal character `§` (never `\S{}`).

## 5. Footnotes

They go in a `\VUnotes{ordinate}{...}` block placed **at the head** of the
page, just after `\begin{VUpage}`. **Each note is a paragraph** — a blank
line separates them in the source. Never chain them with `\nl`. A note
continuing one from the previous folio opens with `\VUcontinue`.

The ordinate is given to you in the geometry file (« notes ... mm »).

## 6. The tools

* The geometry of a leaf: for each line, `y0`, the baseline, `ind` (the
  indent in pixels from the margin), `fin` (the distance to the right
  margin) and the width. `ind` around +45..+55 = a new paragraph; `ind`
  around 0 = flush left. `fin` close to 0 = a justified line.
  `tools/baselines.py` measures the baselines and the white between
  paragraphs; `tools/crop.py` measures the text block.
* A close-up of a doubtful spot: crop the scan to the band, enlarge it
  three to five times, write it to a PNG and read it with the `Read`
  tool. **That is how every doubtful reading is decided.**
* The scan itself is not in the repository: ask the maintainer for the
  leaf you are working on.

## 7. The shape of the block handed back

```
\begin{VUpage}[<leaf>]{<folio>}
\VUnotes{<ordinate>mm}{%
(1) first note.

(2) second note.%
}

<first line>\nl
<second line>\cc
...
```

* `\VUcontinue` opens the page **if and only if** the first line of the
  body is flush left (`ind` close to 0). If it is indented, leave it out.
  That is the mistake made five times.
* A blank line separates two paragraphs.
* Write **no** `\VUblanc`: the assembler lays them by measurement.
* Centred titles (`\VUtitre`): report them, give their text, do not try
  to work out their size.

## 8. What you hand back

1. The complete LaTeX block, with no comment inside it.
2. The list of the lines you had to enlarge, and what the enlargement
   showed.
3. The original's typos that you are keeping.
4. Every doubt you could not settle, **named** rather than guessed.

A declared doubt is worth more than an invention. The assembler reads
every block against the facsimile before laying it.
