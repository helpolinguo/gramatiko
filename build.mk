# Compiling the volume: « make -f build.mk ».
# « make -f build.mk checks » reruns the twelve verifications (§ 8).
# The PDF carries the name it is published under, and not that of its
# source: « -jobname » is enough, so there is neither a copy to keep up
# to date nor two files of 1.7 MB in the repository. The name matters:
# the reading page and its 1441 folio references all point at
# gramatiko.pdf.
# pdfTeX writes no space character between words; a reader finds them by
# the gaps, and loses them on a line set tight (Apple Books merged folio
# 16's « Ma, pro ke la nomi... »). tools/word_spaces.py writes a real,
# invisible space into every gap of the finished PDF: nothing on the page
# moves. See the journal, « A real space between words ».
gramatiko.pdf: main.tex preamble.tex content/*.tex tools/word_spaces.py
	pdflatex -interaction=nonstopmode -jobname=gramatiko main.tex
	python3 tools/word_spaces.py gramatiko.pdf

checks: gramatiko.pdf
	python3 tools/checks.py

.PHONY: checks
