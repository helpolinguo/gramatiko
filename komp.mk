# Compilation du volume : « make -f komp.mk ».
# « make -f komp.mk controles » relance les onze verifications (§ 8).
main.pdf: main.tex preambule.tex contenu/*.tex
	pdflatex -interaction=nonstopmode main.tex

controles: main.pdf
	python3 outils/controles.py

.PHONY: controles
