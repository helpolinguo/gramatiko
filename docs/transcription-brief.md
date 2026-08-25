# Consigne pour le relevé d'un folio

Tu relèves **un** folio du fac-similé de la *Kompleta Gramatiko Detaloza
di la Linguo Internaciona Ido*, L. de Beaufront, Meier-Heucke, 1925 —
ouvrage du domaine public, scanné par le commanditaire, qui demande une
transcription diplomatique.

Le projet est dans `/root/kompleta-gramatiko`. **Tu ne composes rien
toi-même** : tu rends un bloc LaTeX, que l'assembleur vérifiera et
posera. Tu n'écris dans aucun fichier du projet.

---

## 1. La règle qui prime sur toutes les autres

**Une ligne du fac-similé = une ligne du bloc rendu.** Aucune coupure
n'est laissée à LaTeX. Chaque fin de ligne porte une marque explicite :

* `\nl` — la ligne finit sur un mot entier ;
* `\cc` — la ligne finit sur une coupure de mot (le tiret est composé par
  la macro : **ne l'écris pas**) ;
* rien — c'est la dernière ligne d'un alinéa ;
* `\parplein` — dernière ligne d'un alinéa qui court jusqu'à la marge de
  droite (`fin` proche de 0 dans la géométrie).

`\\` est **interdit**.

## 2. Le texte

Le livre est en ido. Tu ne corriges rien : **les coquilles de l'original
se conservent telles quelles**, et tu les signales dans ton rapport.

Tu lis le fac-similé, pas ta mémoire de l'ido. Un mot qui te paraît
étrange est probablement ce qui est imprimé.

## 3. L'enrichissement

* **Gras** (`\VUgras{...}`) : une forme ido citée en vedette, ou un
  exemple donné en évidence.
* *Italique* (`\textit{...}`) : tout ce qui est cité d'une autre langue,
  et les termes grammaticaux cités.

**Une graisse douteuse ne se tranche jamais sur la bande.** Agrandis
(voir § 6). Sur ce projet, neuf premières lectures de graisse sur neuf
se sont révélées fausses avant agrandissement.

## 4. Les blancs de mot dans la source

Convention vérifiée sur le corpus composé (440 contre 31, 82 contre 1,
9 contre 975) :

* `;` `?` `!` s'écrivent **collés** au mot qui précède ;
* `:` s'écrit **espacé**.

Les catcodes actifs posent l'espace fine à la composition. Les guillemets
sont `«` et `»`, l'apostrophe `'`, le tiret long `---`, le signe de
paragraphe le caractère littéral `§` (jamais `\S{}`).

## 5. Les notes de bas de page

Elles vont dans un bloc `\VUnotes{ordonnée}{...}` placé **en tête** de la
page, juste après `\begin{VUpage}`. **Chaque note est un alinéa** — une
ligne blanche les sépare dans la source. Ne les enchaîne jamais par
`\nl`. Une note qui continue celle du folio précédent s'ouvre par
`\VUcontinue`.

L'ordonnée t'est donnée dans le fichier de géométrie (« notes ... mm »).

## 6. Les outils

* `python3 /tmp/geo.py <feuillet>` — pour chaque ligne : `y0`, la ligne
  de base, `ind` (renfoncement en px depuis la marge), `fin` (distance à
  la marge de droite) et la largeur. `ind` autour de +45..+55 = alinéa ;
  `ind` autour de 0 = au fer. `fin` proche de 0 = ligne justifiée.
* `python3 /tmp/z.py <feuillet> <y0> <y1> <x0> <x1> <facteur> <suffixe>`
  → écrit `/tmp/z<suffixe>.png`, que tu lis avec l'outil `Read`. **C'est
  ainsi que se tranche toute lecture douteuse.** Un facteur de 3 à 5.
* Les bandes déjà produites : `scan/H<feuillet>_0.png`, `_1`, `_2`.
* La géométrie de ton feuillet : `/tmp/geo<feuillet>.txt`.

## 7. La forme du bloc rendu

```
\begin{VUpage}[<feuillet>]{<folio>}
\VUnotes{<ordonnée>mm}{%
(1) première note.

(2) deuxième note.%
}

<première ligne>\nl
<deuxième ligne>\cc
...
```

* `\VUcontinue` ouvre la page **si et seulement si** la première ligne du
  corps est au fer (`ind` proche de 0). Si elle est renfoncée, ne le mets
  pas. C'est la faute que j'ai commise cinq fois.
* Une ligne vide sépare deux alinéas.
* N'écris **aucun** `\VUblanc` : l'assembleur les pose par mesure.
* Les titres centrés (`\VUtitre`) : signale-les, donne leur texte, ne
  tente pas d'en calculer le corps.

## 8. Ce que tu rends

1. Le bloc LaTeX complet, sans commentaire à l'intérieur.
2. La liste des lignes que tu as dû agrandir et ce que l'agrandissement
   a montré.
3. Les coquilles de l'original que tu conserves.
4. Tout doute que tu n'as pas su lever, **nommé** plutôt que deviné.

Un doute déclaré vaut mieux qu'une invention. L'assembleur relit chaque
bloc contre le fac-similé avant de le poser.
