# Compiling the volume: « make -f build.mk ».
# « make -f build.mk checks » reruns the twelve verifications (§ 8).
# The PDF carries the name it is published under, and not that of its
# source: « -jobname » is enough, so there is neither a copy to keep up
# to date nor two files of 1.7 MB in the repository. The name matters:
# the reading page and its 1441 folio references all point at
# gramatiko.pdf.
gramatiko.pdf: main.tex preamble.tex content/*.tex
	pdflatex -interaction=nonstopmode -jobname=gramatiko main.tex

checks: gramatiko.pdf
	python3 tools/checks.py

.PHONY: checks
