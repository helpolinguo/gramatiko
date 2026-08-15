# Compilation du volume : « make -f komp.mk ».
# « make -f komp.mk controles » relance les onze verifications (§ 8).
# Le PDF porte le nom sous lequel il est publie, et non celui de sa
# source : « -jobname » suffit, il n'y a donc ni copie a tenir a jour
# ni deux fichiers de 1,7 Mo dans le depot. Le nom compte : la page de
# lecture et ses 1441 renvois de folio pointent tous gramatiko.pdf.
gramatiko.pdf: main.tex preambule.tex contenu/*.tex
	pdflatex -interaction=nonstopmode -jobname=gramatiko main.tex

controles: gramatiko.pdf
	python3 outils/controles.py

.PHONY: controles
