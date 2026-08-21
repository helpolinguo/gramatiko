# Kompleta Gramatiko Detaloza — transcription LaTeX

Transcription diplomatique de *Kompleta Gramatiko Detaloza di la Linguo
Internaciona Ido*, L. de Beaufront, Editerio Meier-Heucke, Esch-Alzette
(Luxemburgia), 1925. Ouvrage dans le domaine public (publié en 1925 ;
auteur mort en 1935).

Objectif : **une ligne du fac-similé = une ligne du PDF**, même pagination,
même folios, mêmes coupures, mêmes changements de corps.

---

## 1. État d'avancement

| Étape | État |
|---|---|
| Découpage du scan en feuillets | fait (240 feuillets) |
| Relevé de structure | fait (§ 3) |
| Calibration | fait (§ 4), vérifiée sur le folio 11 |
| Syllabateur ido (`outils/silabifo.py`) | fait (§ 6) |
| Contrôles automatiques (`outils/controles.py`) | fait ; le 11 (cardage) reste en échec sur **7** pages, à moins de 3,8 mm ; le 10 signale le folio 136, non tranché |
| Transcription | feuillets 5–7 et 9 (relevés), 15 à **238** (227 pages sur 240) ; le corps du volume, les dix appendices, le TABELO et les annonces sont clos |
| Reste | le liminaire (feuillets 1–4, 8, 9–14) et les gardes (239–240) |

Le projet compile en permanence (`make -f komp.mk` ou `pdflatex main.tex`).
Le fichier de compilation s'appelle `komp.mk` et non `Makefile` : le pont
vers le disque refuse d'ecrire un fichier portant ce dernier nom.

---

## 2. Le fac-similé

`de Beaufront 1925.pdf` : 121 pages produites par Simple Scan, images JPEG
RGB à 300 dpi. La page 1 et la page 121 sont des images simples (plats de
la reliure) ; les 119 autres sont des **doubles pages**.

`outils/split_spreads.py` détecte la pliure (colonne la plus sombre au
centre de l'image) et découpe : **240 feuillets**, `scan/pages/f0001.jpg` …
`f0240.jpg`.

**Correspondance : `folio imprimé = numéro de feuillet − 4`.**
Vérifiée à la lecture directe sur les feuillets 11 (p. 7), 30 (p. 26),
232 (p. 228), et par OCR du folio sur 35 feuillets répartis de 10 à 234.

---

## 3. Relevé de structure

### 3.1 Découpage du volume

| Feuillets | Folios | Contenu |
|---|---|---|
| 1–2 | — | Plat avant, percaline brune, titre doré : `L. DE BEAUFRONT` / filet orné / `KOMPLETA GRAMATIKO` / `DETALOZA` |
| 3 | — | Couverture imprimée : auteur, titre, `DI LA`, `LINGUO INTERNACIONA`, `IDO`, **vignette** (étoile à six branches, `LINGUO INTERNACIONA / IDO / DI LA DELEGITARO`), éditeur, `1925`, `Imprimita en Luxemburg.` — `Preco : 2 Suisa Franki.` |
| 4 | — | verso blanc |
| 5 | 1 | Faux-titre |
| 6 | 2 | blanc |
| 7 | 3 | Titre |
| 8 | 4 | verso |
| 9–12 | 5–8 | **AVERTO** (avant-propos), avec notes |
| 13 | 9 | Titre de partie : `Iᵃ PARTO` / filet / `MORFOLOGIO E SINTAXO` |
| 14 | 10 | blanc |
| 15–118 | 11–114 | **Première partie** — texte |
| 119 | 115 | Titre de partie : `DUESMA PARTO` / filet / `VORTIFADO` / `PER DERIVO O PER KOMPOZO` |
| 120 | 116 | blanc |
| 121–180 | 117–176 | **Deuxième partie** — texte, se termine par `FINO.` |
| 181–182 | 177–178 | blancs |
| 183–228 | 179–224 | **APENDICI** (10 appendices, § 3.2) |
| 229–235 | 225–231 | **TABELO** — index analytique |
| 236 | 232 | Liste des `APENDICI` ; **fleuron** ; `MONDO-BIBLIOTEKO` ; `RADIO-LEXIKI` |
| 237–238 | 233–234 | Annonces de l'éditeur (`MONDO — Revuo por la Mondo-Linguo`, périodiques et ouvrages idistes) |
| 239–240 | — | Garde et plat arrière |

### 3.2 Les dix appendices (d'après la liste, folio 232)

1. L'acentizo en Ido — 179
2. La pluralo per *-i* — 183
3. Genro e maskulismo — 188
4. Substantivigo dil adjektivo — 195
5. Ca, ta e qua — 205
6. La Konjugo-sistemo di Ido — 206
7. Vortordino — 215
8. Puntizado — 217
9. Nomi. Adresi — 222
10. Formuli di politeso en letri — 223

### 3.3 La règle d'enrichissement

C'est la règle la plus importante pour transcrire ce livre juste, et elle
est parfaitement systématique :

* **gras** = la lettre ou la forme *idiste* citée en vedette — le `u` de
  « La sono **u** devas », le `w` de « la litero **u** = **w** », les
  lettres de l'alphabet énumérées ;
* *italique* = tout ce qui est cité d'une **autre langue** — valeur
  phonétique, mot étranger, titre d'ouvrage : « **c** = *c* Germana en
  *Ceres* o *z* Italiana en *zio*, o *ts* ».

Une même lettre change donc de casse dans la même ligne selon qu'elle
désigne l'ido ou une langue nationale. C'est discret et facile à manquer :
les premières pages transcrites contenaient six omissions de ce type,
toutes du même genre.

### 3.4 Éléments récurrents

* **Folio** : centré en tête, sous la forme `— 26 —` (demi-cadratins de part
  et d'autre). Pas de titre courant.
* **Titres de section** : capitales espacées, grasses, centrées, suivies
  d'un point : `ALFABETO.`, `PRONUNCO DIL VOKALI.`
* **Paragraphes numérotés** : `21. — ` en début d'alinéa, le numéro en
  chiffres romains droits.
* **Notes de bas de page** : filet court (~25 mm) à gauche, puis les notes
  dans un corps plus petit, appelées `(1)`, `(2)`.
* **Styles** : romain pour le texte ; *italique* pour les mots cités, les
  titres d'ouvrages et de revues (*Progreso*, *Grammaire complète*) ;
  **gras** pour les formes ido en vedette ; petites capitales pour les noms
  propres (`COUTURAT`, `DYER`, `MEIER`).
* **Espacement à la française** avant `; : ! ?` et à l'intérieur des
  guillemets `« »` : nettement visible (`kontenas 26 literi : kin vokali,`).
  Les macros du préambule le reproduiront.
* **Marques de cahier** : un chiffre au pied de la première page de certains
  cahiers (un `8` au bas du folio 225). **À relever systématiquement.**
* **Filets** : filet court sous l'auteur au titre ; filet sous les titres de
  partie ; filet de note ; filet long avant le fleuron du folio 232.

---

## 4. Calibration

Toutes les mesures sont prises sur le scan à 300 dpi, après désinclinaison
et égalisation locale du fond (`outils/page.py`). Le bloc de texte est
repéré **par les glyphes eux-mêmes** : on ne peut pas se fier au recadrage
sur « la zone claire », la tranche des feuillets voisins étant claire elle
aussi. Les composantes connexes de taille de caractère sont soudées en
lignes, et les composantes hautes et étroites (tranches) sont rejetées.

### 4.1 Résultats

| Grandeur | Mesure | Valeur retenue |
|---|---|---|
| Justification | médiane 91,69 mm sur 223 pages, σ = 1,36 mm | `\VUtexteLargeur = 91.69mm` |
| Interlignage du corps | 41 px (mode net, 85 pages) = 3,47 mm | `\VUinterligne = 9.88pt` |
| Interlignage des notes | 33,25 px = 2,82 mm | `\VUinterligneNote = 8.01pt` |
| Approche des notes | +78 millièmes de cadratin | `\VUtrackingNote = 78` |
| Hauteur d'x, corps | 1,729 mm = 4,92 pt TeX | — |
| Hauteur d'x, notes | 1,338 mm = 3,81 pt (0,774 × corps) | — |
| Ordonnée du folio | médiane 221 px = 18,71 mm | `\VUfolioY = 18.71mm` |
| Ordonnée de la 1ʳᵉ ligne | médiane 287 px = 24,30 mm | `\VUmargeSup = 24.30mm` |
| Hauteur du bloc | jusqu'à 1850 px = 156,63 mm | `\VUtexteHauteur = 132.4mm` |
| Format du papier | image 117,2 × 176,9 mm, rogne et ombre déduites | 116 × 182 mm |

La dispersion de 1,36 mm sur la justification vient de la numérisation
(distance variable au capteur : la largeur des images de double page va de
2680 à 2818 px), pas de l'imprimé : les valeurs individuelles se groupent
très serré autour de 91,7 mm sur les pages de texte plein.

### 4.2 Choix du corps et de la fonte

Deux critères indépendants, tous deux sans échelle :

1. **Hauteur d'x rapportée à la justification** : 1,729 / 91,69 = 0,018 86.
2. **Chasse** : largeur naturelle, mesurée par `\settowidth`, de six lignes
   pleines relevées à la main sur le folio 26, comparée aux 260,7 pt de la
   justification.

Résultats à 10 pt nominal (`outils/fontes.tex`), corps déduit du critère 2,
hauteur d'x qui en résulte comparée aux 4,92 pt mesurés :

| Fonte | Corps déduit | Hauteur d'x obtenue | Écart |
|---|---|---|---|
| Latin Modern (cmr) | 10,12 pt | 4,36 pt | −11 % |
| Times (ptm) | 11,10 pt | 5,09 pt | +3,5 % |
| Palatino (ppl) | 10,04 pt | 4,86 pt | −1,2 % |
| New Century (pnc) | 9,56 pt | 4,61 pt | −6,3 % |
| Utopia (put) | 9,92 pt | 4,97 pt | +1,0 % |
| **XCharter** | **10,16 pt** | **4,94 pt** | **+0,4 %** |

**Retenu : XCharter à 10,2 pt.** C'est la seule fonte disponible ici qui
satisfasse les deux critères à moins de 0,5 % : romaine de transition à
fort œil, empattements fins et horizontaux, axe vertical — la famille du
caractère employé par l'imprimeur luxembourgeois. Latin Modern, souvent
choisi par réflexe pour un imprimé de cette époque, donne des lettres
visiblement trop petites pour la chasse : à la taille qui fait tomber les
lignes au bon endroit, sa hauteur d'x est inférieure de 11 %.

Le choix est isolé dans une seule constante (`\VUfonte`) : il pourra être
changé sans toucher au contenu.

### 4.3 Le gras vient d'une autre famille

Le gras du fac-similé est un **demi-gras étroit**, comme il est d'usage
dans les fontes allemandes et luxembourgeoises de l'époque : il n'est pas
proportionné à son romain. Celui de XCharter est large.

Mesure sur le folio 12, ligne « la chefa esforco di la voco :… » : le
passage gras occupe 575 px, soit 138,5 pt, contre 151,4 pt en XCharter
gras à 10,2 pt — **9 % de trop**, assez pour que « neutra. » ne tienne
plus dans la ligne.

La première hypothèse était que le typographe avait serré cette ligne.
Elle est fausse, et c'est la mesure qui l'a dit : les blancs inter-mots
du fac-similé y valent 3,85 pt, contre 2,6 pt dans ma composition. Les
espaces de l'original sont **plus larges** que les miennes, et la ligne
tient quand même : ce sont donc les lettres qui sont trop larges, pas les
espaces qui sont trop grandes.

Vérification du romain, sur quatre lignes du folio 11 entièrement
romaines : écart médian **−0,9 %**. Le romain est juste ; seul le gras
est en cause. (Au passage, la calibration du § 4.2 s'appuyait sur six
lignes du folio 26 dont plusieurs sont en gras dans l'original : son
accord à 0,4 % tenait pour partie de la chance. Le contrôle sur lignes
purement romaines, lui, est propre.)

Deux remèdes, tous deux essayés :

| | corps requis | écart de largeur | effet visible |
|---|---|---|---|
| XCharter gras réduit | 9,2 pt | −10 % | capitales grasses nettement rapetissées |
| **newtx gras** | **10,0 pt** | **−2 %** | hauteur de capitale à 1,4 % de la mesure |

**Retenu : newtx gras à 10,0 pt** (`\VUfonteGras`, `\VUcorpsGras`), employé
par la macro `\VUgras`. Mélanger deux familles est inhabituel, mais c'est
ici le parti le plus fidèle : l'original fait exactement cela — un romain
large et un demi-gras étroit qui ne sont pas de la même coupe.

> **À revérifier** après composition des cinq premières pages, par
> juxtaposition à 300 dpi (contrôle 8). Si la chasse dérive, c'est le corps
> qu'il faut reprendre, pas les espaces.

---

## 5. Vérification du folio 11

Première page de texte courant composée, avec titre de section, alinéas
numérotés et bloc de notes. Résultat mesuré sur le rendu à 300 dpi :

| | fac-similé | composé |
|---|---|---|
| ordonnée de la 1ʳᵉ ligne | 461 px | 460 px |
| pas des lignes | 40,0 px | 41,0 px |
| nombre de lignes | 32 | 32 |

Toutes les coupures tombent au même endroit qu'à l'original. Les huit
contrôles passent. La juxtaposition est dans `controle/juxta/`.

Deux écarts subsistent, tous deux documentés au § 8.

---

## 6. Syllabation de l'ido

La règle est énoncée par l'ouvrage lui-même, appendice *Puntizado*,
folio 220, sous le titre **Seko di la Vorti. [D. 485]** : la coupure est
libre, à deux conditions seulement — chaque partie doit contenir une
voyelle, et les digrammes ou diphtongues ne doivent pas être divisés.
Le livre donne ses propres exemples : *mustar* se coupe en `mu-star`,
`mus-tar` ou `must-ar` ; mais *neutro* et *mashino* se coupent `neu-tro`
et `ma-shino`, jamais `ne-utro` ni `mas-hino`.

Inventaire retenu, tiré du corps de l'ouvrage :

* digrammes : `ch`, `sh`, `qu` (folio 13, « Pronunco dil konsonanti e
  digrami » ; folio 14 : *q* est toujours suivi de *u*) ;
* diphtongues : `au`, `eu` (folio 17) ;
* `gn` n'est **pas** un digramme : le livre l'écrit `reg-no`, `dig-na`.

`outils/silabifo.py` implémente cette règle et se vérifie sur les
exemples du livre. Il sert de **contrôle** : le contrôle 3 vérifie que
chaque `\cc` encodé est conforme à D. 485. Une coupure non conforme est
soit une coquille de l'original, soit une erreur de relevé.

Comme la règle ido est aussi permissive, un fichier `\hyphenation{...}`
n'apporterait presque rien : la césure automatique de TeX est de toute
façon désactivée, toutes les coupures étant relevées une par une.

---

## 7. Macros

| Macro | Rôle |
|---|---|
| `\nl` | fin de ligne **sans** trait d'union |
| `\cc` | fin de ligne **avec** trait d'union (le trait est composé) |
| `\parsuite` | `\parfillskip=0pt` : justifie la dernière ligne d'un alinéa |
| `VUpage` | une page du fac-similé, dans une minipage de hauteur fixe |
| `\VUfolio` | folio centré `— n —` |

### Les notes sont interlettrées

Deux mesures se contredisaient sur le corps des notes : la hauteur d'x
donnait 7,8 pt, la largeur des lignes en réclamait 9,3. Aucun corps ne
satisfait les deux — parce que l'original ne joue pas sur le corps mais
sur l'**approche** : les notes sont composées interlettrées, usage courant
pour le petit texte de cette époque.

Sans cela mes lignes de note naissaient 15 % trop courtes, et TeX comblait
en étirant les espaces-mots, qui devenaient béants. Mesure sur quatre
lignes de note entièrement romaines du folio 14 : +77, +83, +79, +75
millièmes de cadratin. Retenu : **+78**.

Conséquence pour les contrôles : `pdftotext` lit l'approche comme une
espace (« vokali e , o »). Les lignes de note se comparent donc blancs
ôtés, comme les lignes d'apparat.

### Le gras est proportionnel, jamais absolu

`\VUgras` fixait d'abord le corps en dur à 10,0 pt. Dans les notes,
composées à 7,9 pt, les lettres grasses ressortaient donc d'un tiers trop
grosses. Le gras est maintenant défini par un **rapport** au corps courant
(`\VUratioGras` = 0,98) : il suit le texte, les notes, ou tout autre corps
où il apparaît.

### Les espaces-mots sont insécables

`\nl` force une coupure à la fin de la ligne, mais n'empêche pas TeX d'en
placer une **avant** si la matière ne tient pas. Une ligne 0,7 % trop
large se recoupait donc toute seule, en silence, sans même produire
d'`Overfull \hbox` — c'est arrivé au folio 13. Les espaces rendus
insécables, le seul point de coupure légal d'une ligne est celui que le
relevé a placé : une ligne trop large devient un `Overfull \hbox`, que le
contrôle 1 inventorie. La faute passe du silence au bruit. Les espaces
gardent toute leur élasticité : la justification est intacte.

### Toute ordonnée se mesure depuis le FOLIO

C'est la règle qui a manqué trois fois, sous trois déguisements : blocs de
notes, titres de section, puis blocs de notes à nouveau. Chaque image du
scan a son propre décalage vertical — le papier n'y occupe pas la même
place. Une ordonnée lue sur le bord de l'image est donc fausse d'une
quantité qui varie d'une page à l'autre, jusqu'à 10 mm.

La seule référence sûre est le **folio**, dont la position composée est
fixée par `\VUfolioY`. Toute ordonnée se calcule donc ainsi :

    ordonnée = \VUfolioY + (y_mesuré − y_folio) × 25,4/300

`\VUmargeSup` ne convient **pas** comme référence : c'est la position
médiane de la première ligne de corps sur l'ensemble du volume, et une
page qui ouvre par un titre n'y place pas sa première ligne. Au folio 18,
la mesurer depuis `\VUmargeSup` donnait 71,63 mm au lieu de 84,75, et le
bloc de notes remontait dans le texte courant.

### Un titre peut se trouver au-dessus de la marge

Le folio 18 ouvre par un titre de section placé à 20,57 mm du bord, soit
**au-dessus** de `\VUmargeSup` (24,30 mm) : le blanc qui le précède est
donc négatif. Posé positif, il repoussait les douze lignes de corps par
dessus le bloc de notes, et le texte se composait par-dessus lui-même.
Le contrôle 2 l'a vu immédiatement — il extrayait deux lignes fondues en
une (`laniucelo`), signature d'un chevauchement.

`\VUmargeSup` est la position **médiane** de la première ligne, pas un
plancher : sur une page qui ouvre par un titre, l'ordonnée se mesure comme
partout ailleurs et le blanc peut être négatif.

### Fin d'alinéa : `\parplein` et `\VUcontinue`

`\parfillskip` est un paramètre **global**. Posé une fois au début d'une
page, il justifiait la dernière ligne de tous les alinéas suivants — au
folio 15, plusieurs fins de paragraphe se retrouvaient tirées jusqu'à la
marge. `\parplein` l'enferme donc dans un groupe refermé aussitôt après le
`\par` qui l'utilise, et **termine** l'alinéa au lieu de l'ouvrir.
`\parsuite` est conservé sous son ancien nom mais ne doit plus servir.

`\VUcontinue` ouvre un alinéa qui continue la page précédente : pas de
renfoncement, la ligne reprend au fer à gauche. Le folio 15 commence ainsi
par la fin d'un mot coupé au folio 14.

`\\` n'est **jamais** employé : il désactive la justification de la ligne.
`\hyphenpenalty`, `\exhyphenpenalty` et `\pretolerance` interdisent à TeX
de décider lui-même d'une coupure ; toutes les coupures sont relevées.

---

### Placement absolu

Les lignes d'apparat (titres, faux-titre), le folio et les blocs de notes
sont placés à une **ordonnée mesurée** et occupent une hauteur nulle :
aucun ne peut en déplacer un autre, ni migrer d'une page à l'autre. Le
texte courant, lui, s'écoule normalement depuis `\VUmargeSup` avec un
interlignage fixe — c'est ainsi que l'original est composé.

Conséquence pratique : **`\VUnotes` se déclare en tête de page**, juste
après `\begin{VUpage}`, même si les notes se composent en bas. Le
contrôle 2 rétablit l'ordre visuel avant de comparer.

---

## 7 bis. La page est justifiée VERTICALEMENT : le cardage

Découvert au folio 30, après vingt et une pages composées, et c'est le
manquement le plus grave relevé jusqu'ici.

Le compositeur ne laisse pas ses pages finir où elles veulent. Mesure
faite sur les feuillets 20 à 39 (`outils/lignesbase.py`) : **la dernière
ligne de base tombe à 145,3 mm sous le folio, à 0,3 mm près, quel que
soit le nombre de lignes de la page** — 36 lignes au feuillet 34, 48 au
feuillet 33, même bas de page. Les deux seules exceptions du lot sont les
feuillets 22 et 26, qui terminent une section et s'arrêtent plus haut.

Quand la matière ne remplit pas la justification, il répartit le surplus.
Deux moyens, tous deux visibles :

* des **lames uniformes entre toutes les lignes du corps** : le pas passe
  de 41,45 px (interlignage courant, 9,88 pt) à la valeur propre à la
  page. Le feuillet 34 est à 43,11 px, soit 10,38 pt ;
* des **blancs plus larges aux articulations** : fin d'alinéa, ouverture
  d'une énumération, reprise du discours après des exemples.

Le premier moyen a failli m'échapper. Un pas de 43,11 px au lieu de 41,45
peut passer pour un défaut du scan ; trois mesures le réfutent :

1. la largeur pleine des lignes vaut 1083 px au feuillet 34 comme
   partout ailleurs — l'échelle horizontale est normale ;
2. le pas des **notes** de la même page vaut 32,83 px, exactement comme
   aux feuillets 30, 32, 35, 36, 37 — un étirement vertical du scan les
   aurait allongées elles aussi ;
3. la distance du folio à la première ligne de base vaut 114,3 px au
   feuillet 34 comme aux feuillets 28, 32 et 38.

Le scan est donc juste dans les deux axes, et c'est bien le plomb qui est
cardé.

**Le blanc ordinaire entre alinéas — et sa correction.** Sur les
feuillets 15 à 44, les excès mesurés se répartissent en deux
populations : 27 valeurs sur 32 se serrent entre 7 et 9 px — médiane
7,71 px = **1,86 pt** —, les autres sont franchement plus grandes (16 px
et au-delà) et propres à leur page. Je composais la première à zéro :
d'où une dérive qui atteignait 104 px (8,8 mm) au folio 12.

Mais **ce blanc n'est pas une constante du volume**, et l'avoir cru l'a
été une erreur symétrique de la première. Au feuillet 20, les seize pas
du corps valent tous 41,0 à 41,9 px, frontières d'alinéa comprises :
cette page-là n'en a aucun. Les six `\VUblancAlinea` que j'y avais posés
la faisaient descendre de 32 px sur sa hauteur.

La règle est donc : **une frontière sans excès mesuré n'est pas une
frontière sans mesure, c'est une frontière sans blanc.**
`poser_cardage.py` sait maintenant ôter un blanc autant qu'en poser, et
le balayage des 28 pages composées a fait tomber les échecs du contrôle
11 de huit à cinq.

Le bloc de notes, lui, n'en a pas : les pas du feuillet 34 valent 32,8 px
d'un bout à l'autre, y compris à la reprise de la note (2). `\VUnotes`
pose donc `\parskip` à zéro.

**Les trois macros.**

| macro | rôle |
|---|---|
| `\VUinterlignePage{10.38pt}` | pas propre à une page cardée ; juste après `\begin{VUpage}` |
| `\VUblancAlinea` | blanc ordinaire entre deux alinéas, 1,86 pt |
| `\VUblanc{3.75pt}` | blanc plus large à une articulation ; l'excès mesuré, **diminué** du blanc ordinaire quand il le remplace |

`\VUblancAlinea` s'écrit, il n'est pas mis en `\parskip` : au sommet
d'une minipage la colle de `\parskip` subsiste et décalerait toute la
page d'autant. Il obéit donc à la même règle que les coupures de ligne —
ce qui est composé est écrit.

**L'outil.** `python3 outils/cardage.py 34` rend le pas régulier de la
page et la liste des excès, chacun converti en `\VUblanc` prêt à poser.
Il travaille sur les lignes de base, jamais sur les hauts de ligne : le
haut dépend des ascendantes et bruite de ± 8 px, de quoi noyer un blanc
d'un point et demi.

**Le contrôle.** Le contrôle 11 compare la position verticale de chaque
ligne composée à celle de son modèle, décalage constant retiré. C'est lui
qui aurait dû exister depuis le début : les contrôles 2 et 10 étaient
tous deux satisfaits pendant que la page dérivait de 8 mm. Le texte était
juste ligne à ligne, mais aucune ligne ne tombait en face de la sienne.

---

## 7 ter. Le premier tableau (folio 31)

Il ne se laisse pas décrire comme une grille. « Superlativo » et
« de o ek » tombent **à mi-hauteur** entre deux lignes, chacun centré sur
la portée de l'accolade qui le désigne. Les six rangs, eux, sont bien sur
la grille du volume : lignes de base à 413, 454, 495 px pour le groupe
« Komparativo », 561, 602,5 et 643,5 px pour le groupe « Superlativo »,
soit le pas courant de 41 px.

La règle du volume est donc tenue — un rang du fac-similé fait une ligne
du composé — et chaque élément est posé à l'abscisse relevée :

| macro | rôle |
|---|---|
| `\VUrang{...}` | un rang, c'est-à-dire une ligne |
| `\VUcase{41.15mm}{Supereso}` | matière posée à l'abscisse relevée, sans largeur propre |
| `\VUdecale{-0.5\baselineskip}{...}` | ce qui est posé entre deux lignes |
| `\VUaccolade{22.4pt}` | accolade de la hauteur relevée |

Les quatre accolades, étendues relevées au fac-similé (seuil 180,
fenêtres étroites autour de chaque trait) :

| accolade | portée | y | hauteur | centre |
|---|---|---|---|---|
| Komparativo | Supereso → infreso, par egaleso | 382–498 | 116 px = 27,9 pt | 440 |
| relatanta / absoluta | rangs B et C | — | 72 px = 17,4 pt | 607,5 |
| Supereso / infreso | rangs A et B | 531–596 | 65 px = 15,7 pt | 566 |
| maxim / minim | rangs A et B, **fermante** | 543–612 | 69 px = 16,6 pt | 577,5 |

La quatrième est une accolade **fermante** : elle rassemble ce qui est à
sa gauche et désigne « de o ek », à sa droite. Son centre tombe d'ailleurs
sur la ligne de base de ces mots. Les trois autres sont ouvrantes, la
pointe au milieu de leur portée.

Une accolade se pose **hauteur et profondeur nulles**. Sans cela, celle de
27 pt du groupe « Komparativo » faisait une ligne de 27 pt de haut, et le
rang suivant s'en trouvait écarté : la rangée « egaleso » tombait plus
loin de « Supereso » que de « infreso ». Le centre d'une accolade posée
sur une ligne de base tombe sur l'axe mathématique, soit 10,4 px au-dessus
de cette ligne à 300 dpi : c'est de là que se comptent les déplacements
relevés.

Quatre pièges, tous rencontrés :

**Une suite de `\VUcase` laissée libre dans le paragraphe ne tient pas.**
À l'intérieur d'une `VUpage` — où l'espace est active et l'espace-mot
élastique — TeX trouvait à couper entre les boîtes : chaque élément du
tableau descendait d'une ligne, et le tableau se composait en escalier.
Enfermés dans la boîte de `\VUrang`, ils n'offrent plus aucun point de
coupure. Le même code hors de `VUpage` fonctionnait, ce qui a coûté
plusieurs essais avant de regarder au bon endroit.

**Les accolades n'ont pas de correspondance Unicode.** Elles viennent de
la fonte d'extension mathématique, et `pdftotext` les rend en caractères
arbitraires, variables selon la pièce d'accolade employée : on a vu
0x1A, 0x08, « ( », « n » et « o ». Une liste de caractères à écarter ne
tient donc pas ; le critère sûr est structurel. Quand l'accolade est plus
haute que la ligne, elle obtient une ligne à elle : `lignes_pdf` écarte
les lignes d'un seul caractère — le volume n'en a aucune de légitime, la
plus courte relevée en compte cinq (« rozi. »). Quand elle tombe à la
hauteur d'un rang, elle se mêle à ses mots : le contrôle 2 compare alors
le rang **sans ses jetons d'une lettre**, des deux côtés. Ce que cela
coûte doit se dire : le « o » de « de o ek » n'est plus vérifié par le
contrôle 2 au folio 31 ; tout le reste du rang l'est, et le contrôle
l'annonce à chaque exécution.

**Un élément posé entre deux lignes sort du rang pour `pdftotext`**, qui
le rejette sur une ligne à lui. Deux remèdes selon le sens : « de o ek »
est recollé au rang par le contrôle 2, tant que la réunion rapproche du
relevé ; « Superlativo » est rattaché au rang du dessus, abaissé d'une
demi-ligne, plutôt qu'au rang du dessous relevé d'autant — la position
composée est la même, et c'est ainsi que l'extraction le groupe.

La graisse suit la règle du volume : la colonne des formes citées (plu,
tam, min, kam, maxim, minim, tre) est en gras ; les noms des degrés
(Supereso, egaleso, infreso, relatanta, absoluta) et « de o ek » sont en
romain. Vérifié à la loupe sur un agrandissement × 3 — la mesure de
densité d'encre seule ne tranchait pas, le demi-gras étroit n'étant
guère plus dense que le romain.

---

## 7 quater. Deux réglages faux du cardage, et comment ils sont sortis

Neuf pages gardaient un résidu vertical de 1,3 à 2,4 mm que je mettais
sur le compte du bruit de mesure. C'était faux : deux réglages étaient en
cause, et l'un et l'autre se lisent dans un seul chiffre.

**L'interlignage courant était trop court de 0,11 pt.** `\VUinterligne`
valait 9,88 pt, tiré du **mode des hauts de ligne** relevé sur 85 pages :
41 px à 300 dpi. Mais le haut d'une ligne dépend des ascendantes qu'elle
porte — c'est la raison même pour laquelle `outils/lignesbase.py` existe
— et le mode d'une grandeur bruitée tombe sur l'entier le plus proche.
41 px n'était pas une mesure, c'était un arrondi. Sur les lignes de base,
le pas vaut 41,45 px, soit 9,986 pt. L'écart de 0,43 px par ligne est
invisible sur une ligne ; sur les quarante d'une page il fait 17 px, soit
1,4 mm — exactement le résidu inexpliqué. Posé à 9,99 pt, il tombe :
douze pages en échec au contrôle 11 avant, cinq après. Essais voisins :
9,94 pt en laisse huit, 9,96 pt cinq, 10,02 pt sept. On retient la valeur
**mesurée**, non la meilleure du balayage.

La leçon est étroite et vaut d'être retenue : **le mode d'une grandeur
bruitée n'est pas sa valeur, c'est l'entier le plus proche de sa valeur.**
Partout où une mesure est tombée sur un entier rond, se demander si
l'entier vient de l'objet ou de l'arrondi.

**Et `\VUblanc` recevait l'excès diminué du blanc ordinaire.**
`poser_cardage` calculait `excès − 1,86 pt` — ce que le préambule
documentait comme voulu. Mais `\VUblanc` **remplace** le
`\VUblancAlinea`, il ne s'y ajoute pas : chaque articulation était donc
7,7 px trop serrée. À un blanc large par page, l'erreur restait sous la
tolérance et ne se voyait nulle part ; aux folios 59 et 63 elle a fait
basculer le contrôle 11. Les 47 valeurs déjà posées ont été relevées de
1,86 pt ; les blancs placés à la main, reconnaissables à leur commentaire
propre, portaient déjà l'excès entier et n'ont pas été touchés.

Les deux erreurs allaient dans le même sens — page trop haute — et se
sont donc additionnées sans jamais se compenser, ce qui explique qu'aucun
essai de réglage isolé n'avait rien donné auparavant.

---

## 7 quinquies. Les signatures de cahier

Le fac-similé porte un **chiffre nu au pied de la première page de chaque
cahier**, à gauche, sous le bloc de texte. Je les avais laissés passer
pendant soixante pages ; l'un d'eux — le `3` du folio 65 — est apparu
dans une juxtaposition et j'ai balayé le volume pour trouver les autres.

Le relevé est complet et régulier : feuillets 37, 69, 101, 133, 165, 197,
229, soit les folios 33, 65, 97, 129, 161, 193, 225, portant 2, 3, 4, 5,
6, 7, 8. Les cahiers font donc **seize feuillets, trente-deux pages**, et
le premier n'est pas signé — usage courant. Un huitième cahier serait
signé 9 au folio 257, qui n'existe pas : le volume s'arrête avant.

Deux mesures, prises sur les sept :

* abscisse **2,88 mm** de la marge de gauche (médiane ; les sept valeurs
  vont de 2,71 à 3,30 mm, la dispersion venant du scan) ;
* le chiffre a exactement la hauteur de ceux du folio, 27 px : il est
  composé **au corps courant**, pas en petit.

L'ordonnée, elle, se passe **page par page**, comme celle de `\VUnotes`,
et c'est le folio 225 qui l'impose : sa page finit une section et
s'arrête court, et son chiffre remonte à 146,4 mm quand les six autres
tombent tous à 168,7 mm. La signature suit donc la **dernière ligne de
la page**, non une ordonnée absolue du volume. Une constante — qui aurait
marché sur six pages sur sept — l'aurait trahi sans rien signaler.

Trois des sept sont posées : folios 33, 65 et 97. La quatrième s'est
signalée d'elle-même — le `4` du folio 97 est apparu dans la
juxtaposition, à l'endroit exact que le relevé annonçait. Restent les
folios 129, 161, 193 et 225, dont les ordonnées sont déjà mesurées.

Limite consignée : **aucun contrôle ne vérifie la signature.** Du côté du
fac-similé le détecteur ne la voit pas (elle tombe sous le bloc de
texte) ; du côté composé, `lignes_pdf()` écarte les lignes d'un seul
caractère. Les deux côtés l'ignorent donc symétriquement, ce qui vaut
mieux qu'un faux écart, mais laisse le placement non vérifié : il a été
contrôlé à l'œil sur les folios 33 et 65, et devra l'être sur les cinq
autres à mesure qu'ils se composeront.

---

## 8. Les douze contrôles

`python3 outils/controles.py` les lance tous ; `outils/controles.py 3 5`
n'en lance que certains. Ils sont à relancer après chaque lot.

Deux d'entre eux méritent un mot :

Le **contrôle 3** ne se contente pas de vérifier qu'un `\cc` tombe entre
deux lettres : il passe la coupure au syllabateur et la refuse si elle
viole D. 485.

Le **contrôle 10** est né d'un défaut que le contrôle 2 ne pouvait pas
voir. Une espace rendue active a le code de catégorie 13 et non 10 : TeX
ne l'escamote donc plus après un mot de contrôle, et `\noindent en`
composait une espace bien réelle en tête de ligne. Le contrôle 2 compare
du texte, et son texte est dépouillé de ses blancs de bord — l'écart lui
était invisible, alors qu'il saute aux yeux en géométrie : la ligne
commençait à 159 px quand toutes les autres commencent à 144.

Le contrôle vérifie donc que chaque début de ligne occupe l'une des trois
seules positions possibles : la marge, la marge plus un renfoncement
(d'alinéa ou de note), ou le centre. L'espace active escamote maintenant
d'elle-même quand rien n'a encore été composé sur la ligne, ce qui rétablit
le comportement normal de TeX.

Le **contrôle 9** a été ajouté après coup : le contrôle 2 compare le
texte, pas le balisage, et un passage en gras oublié lui échappait — c'est
arrivé au folio 11, où l'énumération des lettres de l'alphabet est en gras
dans l'original. Il compare la quantité d'encre de chaque ligne,
fac-similé contre composé, groupée par corps (texte courant, note, ligne
d'apparat) d'après le relevé lui-même.

Deux approches ont été essayées et abandonnées avant celle-là. Comparer
l'encre de la ligne entière sans grouper : le rapport est dominé par le
corps, pas par la graisse, et le contrôle signalait treize lignes sur une
page correcte. Comparer le profil d'encre *le long* de la ligne, pour
localiser la zone fautive : le décalage des mots entre les deux
compositions produit un bruit qui noie le signal — le test donnait
exactement le même résultat avec et sans le gras.

Sa sensibilité est mesurée, non supposée : sur la ligne des consonnes du
folio 11, le retrait du gras fait passer l'écart de 0 à **+24 %**. Mais
quelques lettres grasses isolées dans une ligne romaine restent sous les
+5 % : **il attrape les enrichissements étendus, pas les ponctuels.**

Le **contrôle 4** a d'abord été écrit naïvement — signaler tout `\nl`
entre deux fragments alphabétiques — et signalait alors une ligne sur
deux, donc rien. Il ne signale plus que la vraie signature d'un trait
d'union perdu : la soudure des deux fragments est un mot attesté ailleurs
dans le relevé, **et** l'un des deux fragments n'est jamais attesté comme
mot entier.

---

## 8 bis. Coupure de mot d'une page à l'autre

Le fac-similé coupe un mot au pied du folio 14, la fin passant au folio 15
(`be-` / `zonus`). Le contrôle 3 cherche donc la suite d'un mot coupé dans
le **même flux** — le texte courant continue en texte courant, la note en
note — et au besoin sur la page suivante. Le bloc de notes étant ramené en
fin de page pour l'ordre visuel, sans ce filtre il cherchait la fin du mot
dans l'appel de note qui le suit. Quand la page suivante n'est pas encore
relevée, il diffère la vérification au lieu de conclure.

## 8 ter. Ce qui a été réparé avant de reprendre la transcription

Quatre défauts, découverts en chaîne à partir d'un seul symptôme — onze
écarts inexpliqués au contrôle des fins de ligne.

1. **Ordonnée des blocs de notes.** Elles étaient lues sur le `y` brut du
   scan, qui inclut le décalage propre à chaque image. Il faut la calculer
   relativement à la première ligne de corps. Au folio 15, l'erreur valait
   8,5 mm. `outils/filet.py` détecte le filet **en tant que filet** (trait
   horizontal continu, tolérant de petites coupures) au lieu de le
   confondre avec le plus grand blanc de la page — ce qui échouait sur
   toute page portant un titre de section. L'outil signale les pages où sa
   référence est douteuse (celles qui ouvrent sur un titre) au lieu de
   rendre un chiffre faux en silence.

   Dérive verticale après correction, sur les cinq pages de texte :
   +1,96 %, −0,31 %, +1,11 %, +0,25 %, −0,92 %, soit 2,3 mm au pire contre
   10,1 mm avant.

2. **Longueur du filet** : 18,0 mm mesurés, contre 20,5 posés au jugé.

3. **Fin d'alinéa confondue avec `\nl`.** L'analyseur du relevé
   transformait toute fin d'alinéa en `\nl`, si bien que le contrôle
   réclamait « pleine » une ligne qui doit être courte. Une fin d'alinéa
   porte maintenant sa propre marque (`pf`).

4. **Le folio comptait comme une ligne de texte** dans la comparaison,
   décalant toute la page d'un rang.

Et une leçon de méthode : la vérification des fins de ligne se fait
**contre le relevé**, non contre le fac-similé. Le relevé sait déjà quelles
lignes terminent un alinéa ; passer par le fac-similé imposait un
appariement, dont le moindre glissement produisait une douzaine de faux
positifs. Le contrôle le plus fiable est celui qui interroge la source la
mieux connue.

## 8 quater. Coût des contrôles

`outils/cache.py`. Les contrôles 8, 9 et 10 refaisaient chacun le même
travail : rendre la page composée à 300 dpi, et analyser le feuillet du
fac-similé — dont la désinclinaison essaie cinquante et une rotations.

Deux caches, de natures différentes. Le **fac-similé ne change jamais** :
son analyse est écrite sur disque une fois pour toutes. Les 240 feuillets
ont été préchauffés en 100 secondes ; ce coût ne se représentera plus. Le
**composé change à chaque compilation** : il est rendu en une seule passe
pour tout le document, partagée par les trois contrôles.

| | avant | après |
|---|---|---|
| suite complète, 10 pages | 27 s | 8,3 s |

Le temps restant est presque entièrement celui de `pdftoppm` sur le PDF
composé, qui croît linéairement : de l'ordre d'une à deux minutes pour le
volume entier. Ce n'est plus un obstacle.

**Mais les contrôles n'étaient pas le goulot.** Ils vérifient ; ils ne
transcrivent pas. Le coût réel d'une page est la lecture du fac-similé à
pleine résolution — trois ou quatre bandes d'image à lire à l'œil, les
coupures relevées une par une, et pour chaque lettre citée l'arbitrage
entre gras et italique. C'est irréductible tant que le relevé est fait à
la main.

Ce qui débloquerait le volume est d'une autre nature : un **générateur de
premier jet**, qui produirait le relevé mécaniquement et laisserait à la
relecture le rôle de vérifier plutôt que de saisir. Les pièces existent
déjà — les boîtes de lignes du fac-similé donnent les coupures sans OCR,
et la mesure d'encre par mot permettrait de classer gras, italique et
romain. Il resterait à écrire l'OCR ligne à ligne et le classifieur, puis
à mesurer leur taux d'erreur avant de leur faire confiance.

## 8 quinquies. Le premier jet automatique : ce qui marche, ce qui ne marche pas

Mesuré contre les dix pages relevées à la main, qui servent de vérité
terrain.

**Le texte : environ 3 %.** L'OCR ligne à ligne — chaque boîte de ligne
découpée, agrandie, lue seule — donne 2,5 à 5,3 % d'erreur par caractère
sur les pages où l'alignement tient. Les coupures de ligne, elles, ne
passent pas par l'OCR : elles viennent des boîtes du fac-similé et sont
déjà fiables. C'est utilisable comme brouillon.

Un premier chiffre de 48 % venait d'un décalage d'un rang, le folio étant
compté d'un côté et pas de l'autre — le même défaut qui avait neutralisé
le contrôle 10. En se fiant à la détection géométrique du folio plutôt
qu'à sa lecture, on tombe à 16 %, et à ~3 % sur les pages alignées.

**L'enrichissement : échec.** `outils/enrichi.py` mesure pour chaque mot
l'épaisseur du trait et la pente du cisaillement, normalisées par la
médiane de la ligne. Résultat sur 1214 mots :

| | |
|---|---|
| exactitude du classifieur | 74,6 % |
| **exactitude en prédisant « romain » partout** | **86,9 %** |
| gras — rappel / précision | 46 % / 16 % |
| italique — rappel / précision | 76 % / 41 % |

**Le classifieur fait moins bien que de ne rien classer.** Il désigne 157
mots romains comme gras et manque 31 gras sur 70.

La cause est la même particularité typographique qui a compliqué la
composition : le gras du fac-similé est un **demi-gras étroit**, non
proportionné à son romain — c'est pour cela qu'il a fallu lui donner une
autre famille. Étroit *et* gras, son rapport encre/largeur recouvre celui
du romain, et la mesure d'épaisseur ne les sépare plus. Ce qui rend cette
typographie intéressante est exactement ce qui met le détecteur en échec.

**Conséquence.** Le premier jet peut porter le texte, pas les
enrichissements — or ceux-ci sont la moitié du travail sur ce livre, et
la moitié où se sont logées toutes les erreurs signalées à la relecture.
La transcription reste donc page à page, avec l'OCR comme brouillon.

### Et par le contenu ? Essaye aussi, echoue aussi

L'enrichissement de ce livre etant **semantique** et non decoratif, on
peut esperer le deduire du texte plutot que de l'image.
`outils/enrichi_texte.py` : lexique ido tire des mots composes en romain,
lexique etranger tire des mots en italique, plus des indices de contexte
(noms de langue, marqueurs de citation). Validation croisee, chaque page
classee avec un lexique construit sans elle.

| | |
|---|---|
| exactitude | 64,8 % |
| référence « tout romain » | 80,2 % |
| rappel du gras | 37 % |

Encore moins bon que le classifieur visuel. La règle « mot absent du
lexique ido → étranger » noie tout : avec dix pages, le lexique est trop
maigre, et 633 mots romains sont pris pour de l'italique.

En cherchant ensuite les régularités dans les données plutôt que dans mes
suppositions, le signe `=` est apparu 24 fois devant un passage
italique — piste apparemment forte. Vérifiée, elle se dissout : de part et
d'autre de `=`, les deux voisins sont italiques (20 et 24 contre 4 et 1
gras). Le gras se trouve plus à gauche, séparé du signe.

**Le fond du problème.** La règle est réelle, et un lecteur l'applique
sans peine — mais elle repose sur la distinction entre un mot *employé* et
un mot *mentionné*, qui demande le sens de la phrase et non des indices
locaux. Les deux sont en ido et se ressemblent en tout point.

Le lexique grandit toutefois à chaque page transcrite. L'essai mérite
d'être refait quand il couvrira cinquante pages plutôt que dix.

### Les lignes « à 94 % » : le contrôle mesurait la mauvaise chose

Le contrôle 10 déclarait courtes des lignes que le relevé donne pleines,
sur les folios 18 et 19. Deux hypothèses ont été proposées et démenties
par la mesure : les blancs du titre, puis l'élasticité de l'espace-mot —
cette dernière après avoir constaté que l'espace du fac-similé vaut
4,58 pt contre 2,84 pour XCharter. Posée telle quelle, cette valeur faisait
passer les échecs de 7 à 48 : les 4,58 pt sont la largeur **après**
justification, non au repos. J'avais mesuré le résultat, pas le réglage.

La réponse est venue de `\tracingparagraphs`, qui donne la décision de TeX
et non son résultat : **`b=0`**, badness nulle. TeX considérait ces lignes
comme parfaitement remplies — et il avait raison.

Une première ligne d'alinéa est **renfoncée de `\VUalinea`** : sa largeur
vaut donc 94 % de la justification alors que son bord droit touche
exactement la marge. Le contrôle comparait des largeurs ; ce qui définit
une ligne pleine, c'est qu'elle **atteigne la marge de droite**. Corrigé,
les sept échecs tombent à un.

Leçon de méthode : quand deux hypothèses successives sont démenties, le
problème est souvent dans l'instrument et non dans l'objet. Observer la
décision plutôt que le résultat l'a montré en une commande.

### Clipper, ne pas rejeter

`text_region` rejetait les composantes débordant de la colonne de texte.
Au folio 20, quatre lignes très chargées en italique se soudent en **une
seule composante de 165 px de haut** — le pli du papier, visible en
diagonale sur ce feuillet, fait le pont entre elles. Cette composante
unique dépassait la colonne de **trois pixels**, et les quatre lignes
disparaissaient d'un coup : un dixième de la page.

Une composante qui déborde un peu reste du texte. On lui **coupe ce qui
sort** au lieu de la jeter. Les comptes de lignes des douze feuillets déjà
transcrits sont inchangés ou meilleurs, et les justifications restent
entre 91,4 et 92,5 mm.

Reste une ligne très courte (« rozi. », cinq caractères) qui passe encore
sous le seuil d'encre de `lines_of`. Elle n'affecte que le relevé
géométrique du fac-similé, non la transcription : l'appariement du
contrôle 9 tolère un manquant, et le contrôle 10 compare le composé au
relevé, pas au fac-similé.

### Le folio pâle du feuillet 26

Sur ce feuillet le folio est trop pâle pour franchir le seuil de
`folio_ligne` : la page se relève donc sans lui, et toute ordonnée
calculée à partir de sa première ligne détectée est fausse de 5 mm.
Position relevée à la main : y = 165. À traiter proprement en abaissant
le seuil de `folio_ligne`, ce qui n'a pas encore été fait — les deux
tentatives précédentes de toucher à un seuil de détection ont chacune
cassé autre chose, et le cas mérite d'être mesuré sur plusieurs feuillets
avant d'être corrigé.

### Une énumération est une suite d'alinéas

Sous « 12. — », le fac-similé aligne une douzaine d'entrées courtes. Je
les avais chaînées par des coupures explicites, ce qui leur ôtait leur
renfoncement **et** les faisait justifier de force. Mesure : elles
commencent toutes à +4,5 à +4,8 mm de la marge — soit `\VUalinea` — et
leurs largeurs vont de 29 % à 96 % de la justification.

Chaque entrée est donc un **alinéa à part entière** : le renfoncement et
la dernière ligne courte viennent alors tout seuls. Quand une entrée
déborde sur une seconde ligne, celle-ci revient au fer à gauche, comme
n'importe quelle continuation d'alinéa. Composé : +4,66 mm et des largeurs
de 29 à 95 %, contre 29 à 96 % au fac-similé.

**Et un piège du relevé lui-même :** un commentaire LaTeX contenant `\nl`
est découpé par le parseur, qui sépare les lignes avant de retirer les
commentaires. Le contrôle 2 l'a vu immédiatement — du texte de commentaire
apparaissait dans le relevé. Ne pas écrire de macro de coupure dans un
commentaire.

### Le détecteur de filet échoue sur les pages à notes très longues

Au folio 29, dix lignes de corps pour trente-huit de notes : le filet
remonte si haut que le bloc de notes le suit de très près, et
`outils/filet.py` ne le trouve pas — sa condition « rien d'autre sur la
ligne du filet » n'est plus vérifiée. Relevé à la main : y = 610.

L'outil rend `None` plutôt qu'une valeur fausse, ce qui est le
comportement voulu. À reprendre si le cas se répète.

## 8 sexies. Deux soupçons du contrôle 9 écartés au folio 32

Le contrôle 9 a signalé deux lignes portant plus d'encre au fac-similé
qu'au composé — la signature d'un enrichissement oublié. Vérification
faite sur un agrandissement, les deux sont des faux positifs :

* la ligne de note « grande, kande li laudas… » (+ 15 %) est
  entièrement romaine ;
* la dernière ligne du corps, « Lu (quale li) esas uzata *por la 3
  genri* (2)… » (+ 24 %), porte exactement les enrichissements composés.

Le rapport d'encre supporte mal les lignes courtes et les lignes très
enrichies : le demi-gras étroit y pèse peu, l'italique beaucoup. C'est
une limite connue du contrôle, qui n'émet d'ailleurs que des notes.

## 8 septies. Une ligne de note trop pâle au feuillet 37 — et pourquoi je n'ai pas corrigé le détecteur

La ligne « *lua, lia.* » — courte, entièrement en italique — porte 537
pixels d'encre sur 88 colonnes : c'est bien une ligne. Mais sa projection
horizontale culmine à 50 quand le seuil de la page, calculé sur son
maximum, est à 48. Le fac-similé est donc relevé à 40 lignes au lieu de
41, la mise en correspondance glisse d'un rang, et les contrôles 9 et 11
ne couvrent plus la page.

Deux réparations ont été essayées et **toutes deux abandonnées** :

* couper les bandes trop hautes à leur vallée la plus creuse — sans
  effet, car les deux lignes ne sont pas soudées : la seconde est
  simplement invisible au seuil ;
* rattraper les lignes pâles dans les trous, avec un seuil abaissé au
  quart — cela retrouve des lignes ailleurs qui n'en sont pas : les
  folios 19, 20 et 23, jusque-là justes, se mettaient à dériver de 15 à
  40 px.

Le détecteur est donc laissé tel quel et la page transcrite à la main,
ses 41 lignes relevées à l'œil. **Le cas s'est reproduit au feuillet 40**,
dont la dernière ligne de note (« XI, 296.) ») culmine à 68 : le relevé
donne 37 lignes pour 38 — celui-là, le rattrapage des lignes pâles le
retrouve depuis. Mais deux autres lui échappent encore, trop courtes
pour franchir le critère d'encre : « lua, lia. » au feuillet 37 (0,086)
et « en -u. » au feuillet 46 (0,07), contre 0,12 exigés. Il faut s'attendre à le revoir chaque fois
qu'une ligne courte tombe en fin de note, et vérifier ces pages-là par
la juxtaposition. C'est la même limite que le folio pâle du
feuillet 26. Baisser un seuil global pour une page sur quarante coûte
plus qu'il ne rapporte ; la vérification de cette page-là se fait par la
juxtaposition visuelle, où la composition se superpose exactement au
modèle.

## 8 octies. Le contrôle 9 a eu raison contre moi (folio 35)

Deux lignes — « De ta regulo konsequas ke : » et celle qui la suit —
paraissaient grasses sur une vue d'ensemble de la page, et je les avais
composées ainsi. Le contrôle 9 les a signalées à −24 % et −17 % : le
composé plus chargé que le modèle. Vérification à l'agrandissement × 1,9,
elles sont en romain ; ce qui les alourdissait n'était que l'encre
étalée dans le papier.

C'est la première fois que ce contrôle corrige une lecture faite à l'œil
plutôt que l'inverse. Il vaut donc mieux, sur une ligne signalée, aller
voir à fort grossissement que se fier à l'impression d'ensemble — le
demi-gras étroit de ce livre se distingue mal du romain empâté à taille
réelle.

## 8 nonies. Un folio réduit à ses deux chiffres (feuillet 42)

Les cadratins qui encadrent le folio sont plats et larges : le masque de
glyphes les rejette (rapport largeur/hauteur supérieur à 12). D'ordinaire
cela ne fait rien, mais au feuillet 42 il ne reste alors que « 38 »,
soudé sur 60 px — moins que les 0,04 W = 63 px exigés d'une ligne par
`text_region`. La page était relevée **sans folio**, avec une ligne de
moins que la réalité, et les contrôles 9 et 11 la sautaient.

`folio_ligne` accepte désormais un second masque, fouillé si le premier
ne donne rien : le masque de glyphes brut, borné à la colonne de texte.
Le folio se retrouve, et la couverture du contrôle 11 passe de 16 à
19 pages — le folio 22, jusque-là non mesuré, y a gagné le blanc de
36,7 px qui lui manquait devant son paragraphe 12.

## 8 decies. Quand ce sont les lignes COMPOSÉES qui se soudent (folio 39)

Jusqu'ici les défauts de découpage venaient du fac-similé. Au folio 39
c'est le rendu de ma propre page qui en souffre : deux lignes très
chargées en gras se soudent dans la projection du PNG rendu à 300 dpi —
une bande de 72 px portant 15 253 pixels d'encre, soit exactement deux
lignes. Le composé est relevé à 35 lignes pour 36, et les contrôles 9
et 11 sautent la page.

Ce n'est pas une erreur de composition : le contrôle 2 déclare la page
identique ligne à ligne au relevé, le contrôle 10 vérifie ses débuts et
fins de ligne, et la juxtaposition la superpose au modèle. Mais cela
rappelle que `cache.compose` découpe le composé avec la même méthode
fragile que `page.py` découpe le fac-similé, et qu'elle mériterait le
même soin — le rattrapage des lignes pâles n'a d'équivalent d'aucun côté
pour les lignes soudées.

## 8 undecies. Un pli du papier qui masque le folio (feuillet 48)

Le pli traverse la page en diagonale et coupe la hauteur du folio. Le
trait qu'il laisse portait l'étendue de la bande à 396 px, centrée à
0,703 : `folio_ligne` rejetait le folio comme trop large et décentré, et
la page se relevait avec une ligne de moins.

Le détecteur examine désormais les **amas** de la bande, séparés par plus
de 40 px de blanc, et non son étendue totale ; le premier amas qui a la
taille et la position d'un folio est retenu. Le pli forme un amas à part,
trop étroit et trop à droite, et n'est plus confondu avec le chiffre.

## 8 duodecies. Le premier jet automatique, mesuré sur 36 pages

Mesure refaite au folio 44, avec 36 pages de vérité terrain au lieu des
dix du premier essai (`python3 outils/premierjet.py`, environ 9 minutes).

Sur les 24 pages où le compte de lignes concorde, le taux d'erreur par
caractère de l'OCR ligne à ligne est de **4,1 % en médiane** — soit deux
caractères faux par ligne de cinquante-cinq. Les dix autres pages
affichent 10 à 85 %, mais ce n'est pas l'OCR qui échoue : ce sont les
pages dont le relevé du fac-similé perd une ligne courte, ce qui décale
la comparaison, plus le tableau du folio 31, qui n'est pas du texte
courant.

Ce que cela change et ce que cela ne change pas :

* les **coupures de ligne** viennent de la géométrie, pas de l'OCR :
  c'est la partie difficile, et elle est déjà fiable ;
* les **lettres** peuvent venir du premier jet : la relecture n'a plus à
  saisir, seulement à corriger deux caractères par ligne ;
* l'**enrichissement**, lui, n'est pas fourni du tout, et **67 % des
  1319 lignes relevées en portent un**. C'est là que passe le temps, et
  les deux classifieurs essayés ont perdu contre la ligne de base (74,6 %
  contre 86,9 % pour le visuel, 64,8 % contre 80,2 % pour le lexical).

Conclusion : le premier jet supprime la saisie, non la lecture. Il permet
de traiter plusieurs folios par tour, mais pas de se passer de l'œil.

## 8 terdecies. Quatre folios en un tour : ce que l'essai a montré

Premier lot de quatre (folios 45 à 48) au lieu d'un. Résultat honnête :
**les contrôles 1 à 10 passent tous**, 1499 débuts de ligne vérifiés, et
le texte des quatre pages est juste du premier coup. Mais deux choses ont
coûté des passes supplémentaires, et ce sont les mêmes deux qui
résistaient déjà à l'unité :

* **le blanc au-dessus d'un titre.** Au folio 46 mon `\VUsaut` estimé
  était trop grand de 89 px, et le bloc de notes — placé, lui, à
  l'ordonnée relevée — s'est retrouvé par-dessus les dernières lignes du
  corps. Le contrôle 2 l'a vu immédiatement (« -os En » au lieu de la
  ligne attendue), mais il a fallu mesurer puis recomposer. **La leçon
  est de mesurer le blanc du titre sur les lignes de base AVANT de
  composer**, comme aux folios 36 et 38, jamais de l'estimer ;
* **le cardage fin.** Les folios 47 et 48 gardent 1,3 et 2,2 mm de
  dérive, avec un profil en deux marches que ni `poser_cardage` ni une
  reprise à la main n'ont réduit.

Conclusion : quatre folios par tour est tenable pour le **texte**, qui
est le gros du travail ; ce qui ne suit pas est le réglage vertical des
pages à titre. Le rythme raisonnable est donc de quatre folios quand
aucun ne porte de titre, deux quand l'un d'eux en porte un.

## 8 quaterdecies. Deux lectures démenties à l'agrandissement

Signalées par l'utilisateur, et instructives dans les deux sens :

* au folio 45, « Plure = pluri kune. » n'est pas la suite de l'alinéa du
  folio précédent : le fac-similé la renfonce de 49 px, soit le
  renfoncement ordinaire. J'avais mis un `\VUcontinue` de trop ;
* aux folios 46 et 47, le mot « ton » n'est pas en petites capitales. À
  taille réelle ses lettres en ont l'air ; à l'agrandissement × 2,4 ce
  sont des bas-de-casse ordinaires.

Le second cas est le pendant exact de celui du folio 35, où le contrôle 9
m'avait corrigé une lecture faite à l'œil. La règle qui se dégage vaut
pour tout le volume : **à taille réelle, la graisse et la casse de ce
caractère ne se jugent pas.** Un doute se tranche à l'agrandissement, pas
autrement.

Troisième occurrence au folio 51, et je m'y suis trompé **deux fois** :
d'abord en composant les trois dernières lignes du corps entièrement en
gras, puis, l'erreur signalée, en les passant entièrement au romain. La
vérité est entre les deux, et c'est exactement la règle d'enrichissement
du volume : les lignes sont romaines, les deux séries de verbes cités —
« venar, arivar, kreskar » et « frapar, donar, lektar » — sont en gras.

La densité d'encre, que j'avais cru pouvoir ériger en critère, ne
tranchait pas : elle donnait 7,3 à 8,9 pour des mots dont les uns sont
gras et les autres romains, parce qu'elle dépend de la forme des lettres
autant que de leur graisse. Ce qui tranche est l'**épaisseur du fût** —
la longueur médiane des séquences horizontales de pixels encrés :

| | fût médian |
|---|---|
| « tam », « kam » (gras, folio 31) | 4,0 à 5,0 px |
| « egaleso » (romain, folio 31) | 3,0 px |
| « frapar, donar, lektar » (folio 51) | 4,0 px |
| « quale en la transitivi » (folio 51) | 3,0 px |

`outils/graisse.py` rend ce verdict amas par amas. **Sa limite est
inscrite dans son en-tête et a été constatée dès le premier emploi** : la
mesure ne vaut que là où le papier est plat. Sur la ligne qui franchit le
pli du feuillet 55, l'outil déclare gras jusqu'aux mots dont on sait
qu'ils sont romains. Un verdict uniforme sur toute une ligne est le signe
qu'elle traverse un pli ou l'ombre de la reliure.

## 8 quindecies. Le folio ôté trop tard (contrôle 10)

Le contrôle 10 ôtait le folio de la liste des lignes composées **entre**
ses deux boucles : celle des fins de ligne travaillait donc alignée, mais
celle des débuts était décalée d'un rang, `lg[k]` répondant pour la ligne
précédente. Le défaut est resté invisible tant qu'aucune page n'avait de
ligne au renfoncement inhabituel ; au folio 50 il a accusé un rang de
tableau d'un « espace parasite » de 120 px qui était en réalité son
renfoncement relevé — l'exemption des rangs ne tombait pas sur la bonne
ligne.

Le folio est désormais ôté une seule fois, avant les deux boucles.

## 8 sexdecies. Le dépistage de la graisse à l'échelle du volume : essai raté

Trois erreurs de graisse signalées en six tours donnaient à penser qu'il
en restait. J'ai donc passé `outils/graisse.py` sur les 46 pages
composées, en confrontant la part d'amas jugés gras à la part de
caractères que j'avais enfermés dans un `\VUgras`.

**L'essai a échoué**, et c'est instructif. Le balayage a signalé 313
lignes, dont les premières au folio 12 — page vérifiée trois fois et
confirmée par le lecteur. Ce ne sont pas 313 erreurs mais un faux positif
systématique, et sa cause se mesure : à 300 dpi l'épaisseur du fût ne
prend que deux valeurs utiles, 3 ou 4 pixels. Les distributions par page
sont indiscernables — médiane 3 à 4, neuvième décile 4,0 — que la page
soit presque toute romaine ou chargée de gras. En suréchantillonnant la
bande d'un facteur 4 on gagne un peu de finesse, pas assez : au folio 51
les mots gras rendent 4,00 et les romains 3,75.

Ce que la mesure sait faire, et qui reste acquis, est de **comparer deux
amas voisins d'une même ligne** : même encre, même papier, même instant
de numérisation. C'est ainsi qu'elle a tranché les verbes cités du
folio 51. Elle ne sait pas juger une ligne dans l'absolu, ni comparer
deux pages.

Le dépistage à l'échelle du volume reste donc à inventer. Le contrôle 9 a
le bon principe — la même mesure des deux côtés, mon encre contre celle
du modèle — et sa faiblesse est ailleurs : son appariement glisse dès
qu'une ligne courte manque au relevé. **C'est là qu'il faut travailler,
et non chercher un meilleur juge de graisse.**

## 8 septendecies. Écrire les frontières d'alinéa dès la composition

Au folio 55 j'ai d'abord laissé des lignes blanches nues, sans marqueur,
en me disant que `poser_cardage` les remplirait. Il ne le peut pas : il
remplace un `\VUblancAlinea`, il n'en invente pas. Résultat, six
frontières sont restées à zéro là où le fac-similé met ses 8 px, et la
page dérivait de 64 px sur sa hauteur — le contrôle 11 l'a vue, mais
après coup.

**La règle est donc d'écrire `\VUblancAlinea` à chaque frontière dès la
composition**, sans se demander si le fac-similé en veut un : l'outil
l'ôtera si la mesure dit zéro, et l'ajustera sinon. Un marqueur de trop
se corrige tout seul ; un marqueur manquant ne se voit qu'à la dérive.

## 8 undevicies. Six folios en un tour (58 à 63)

Le rythme demandé — quatre à six folios par tour — tient, à une
condition : **mesurer tout le lot d'un coup avant d'écrire une ligne.**
Les six feuillets 62 à 67 ont été passés en une commande à
`cardage.py`, `filet.py` et à la géométrie des lignes, puis les dix-huit
bandes d'image lues d'affilée. Aucun des six n'a exigé de retour au
scan, sauf quatre agrandissements ponctuels pour trancher une graisse
douteuse (`-e` du folio 58, `to esas` et `France` des notes) — et les
quatre ont démenti ma première lecture, ce qui confirme qu'un doute de
graisse ne se tranche jamais à la taille de la bande.

Ce lot-là a rendu davantage que six pages : c'est en le composant que
les deux réglages faux du cardage sont sortis (§ 7 quater). Ils étaient
sous les yeux depuis quarante pages, invisibles tant qu'aucune page ne
portait à la fois beaucoup de lignes et un blanc large.

Deux pièges rencontrés, tous deux attrapés par les contrôles :

* **Le `§` écrit `\S{}`.** `texte_nu` ne le rend pas, `pdftotext` si :
  le contrôle 2 signalait un écart qui n'existait pas dans le PDF. Écrire
  le caractère littéral `§`, comme au folio 15.
* **Chaque note est un alinéa.** Aux folios 59, 60, 62 et 63 j'avais
  enchaîné les notes (1), (2), (3)… par des `\nl`, en les prenant pour
  les lignes d'un même bloc. Le fac-similé renfonce le premier mot de
  chacune : ce sont des alinéas. Enchaînées, la dernière ligne de chaque
  note se trouvait justifiée de force — c'est ainsi que le contrôle 10 a
  vu « donema. » tirée à 22 % de la mesure.

---

## 8 vicies. Six autres folios (64 à 69), et une ligne qui manque

Deuxième lot de six. Même méthode qu'au § 8 undevicies : tout mesurer
d'un coup, lire les dix-huit bandes d'affilée, ne retourner au scan que
pour les doutes de graisse. Quatre agrandissements cette fois, et
**les quatre ont démenti ma première lecture** — « diferanta kam ici? »
du folio 65 n'est pas gras, « (Progreso, II, 165.) » du folio 68 n'est
pas italique, « Me ne savas precize... » du folio 69 n'est pas gras. Le
compte est maintenant de huit démentis sur huit. La règle est donc
ferme : **une graisse douteuse ne se tranche jamais à la taille de la
bande**, seulement à l'agrandissement.

Le folio 67 portait le premier titre depuis longtemps, `PREPOZICIONI.`.
Blancs mesurés sur les lignes de base *avant* de composer, comme la leçon
du folio 46 l'exige : 123,3 px au-dessus, 90,4 px au-dessous, d'où 6,92
et 4,14 mm à ajouter au pas. Corps et interlettrage tirés de
`outils/apparat.py 71 --regle PREPOZICIONI. 13 --gras`.

Une ligne du fac-similé échappe encore au détecteur : le `homi.` du
folio 65, deux syllabes en italique au haut d'un bloc de notes, trop peu
d'encre pour franchir le seuil. C'est le septième cas (feuillets 37, 46,
53, 57, 60, 61, 69). La page est composée à la main et les contrôles 9 et
11 la sautent, les comptes divergeant d'une unité. Le dommage reste
borné parce que la ligne manquante est **dans les notes** : `poser_cardage`
n'apparie que les frontières du corps, dont les indices sont tous
antérieurs, et aucun blanc ne glisse. Si un jour la ligne manquante tombe
dans le corps, ce ne sera plus vrai.

---

## 8 unetvicies. Douze folios (70 à 81), et la ligne manquante passe dans le corps

Deux lots de six dans le même tour. Le rythme tient, et les contrôles ont
attrapé tout ce qu'ils devaient attraper. Trois choses valent d'être
notées.

**Le détecteur de lignes a raté quatre lignes de plus, et trois d'entre
elles sont dans le corps.** `kazo.` au folio 76, `yare.` au folio 80,
`longa.` au folio 81 — toutes courtes, toutes en fin d'alinéa, trop peu
d'encre pour franchir le seuil. C'est exactement le cas que j'avais
annoncé comme dangereux au § 8 vicies : tant que la ligne manquante était
dans les *notes*, `poser_cardage` ne s'en apercevait pas, parce qu'il
n'apparie que les frontières du corps, toutes d'indice inférieur. Dans le
corps, tous les indices suivants glissent d'une unité et l'outil poserait
chaque blanc une ligne trop haut, **sans rien signaler**.

Ces trois pages ont donc été cardées **à la main**, sur les lignes de
base, la ligne manquante rétablie à son pas. Le calcul est simple et vaut
d'être écrit une fois : si deux lignes de base successives sont séparées
de 105,9 px là où le pas régulier vaut 41,5, ce n'est pas un blanc de
64,4 px — c'est une ligne manquante *plus* un blanc de 23,0 px. Les
blancs ainsi retrouvés (23,0 à 28,6 px) tombent exactement dans la
fourchette des autres ouvertures de paragraphe numéroté de ces pages,
ce qui les confirme.

**Deux pages sans notes du tout.** Folios 71 et 75 : `outils/filet.py`
rend « filet non trouvé », et c'est ici la bonne réponse, pas un échec.
Le signe qui distingue les deux cas est le pas : une page à notes a un
bloc de pas courts (33 px) ; ces deux-là n'ont que des pas de 39 à 42.

**Un pli du papier faisait accuser une page juste.** Le contrôle 10
signalait au folio 79 une première ligne au fer à gauche alors qu'à
l'agrandissement elle est nettement renfoncée. La cause : une pliure
traverse la marge de gauche du feuillet 83, et le détecteur prend sa
trace pour le début de la ligne. Le remède reprend le raisonnement déjà
employé dans `outils/page.py` pour le folio — **lire en amas, non en
étendue** : un pli donne un amas mince (≤ 7 px) séparé du reste de la
ligne par un blanc bien plus large qu'une espace-mot (≥ 22 px), une
lettre touche ses voisines. Le contrôle ne corrige pas la mesure, il la
**déclare non faite** et le dit. Passé sur les 73 pages, le détecteur ne
se déclenche que sur celle-là.

---

## 8 duoetvicies. Le dépistage des lignes manquantes (`outils/lignes_manquantes.py`)

Six lignes du fac-similé ont échappé au détecteur en vingt-quatre pages :
`homi.` (f69), `kazo.` (f80), `yare.` (f84), `longa.` (f85), `pos til.`
(f86), `pro li.` (f91). Toutes courtes, toutes en fin d'alinéa, toutes
trop pâles pour franchir le seuil d'encre. Je les ai trouvées une à une,
à l'œil, en relisant les bandes — méthode qui marche et **qui ne se
vérifie pas**. Sur les 165 pages restantes, elle finirait par en laisser
passer une, et une ligne absente **dans le corps** décale toutes les
frontières suivantes : `poser_cardage` poserait chaque blanc une ligne
trop haut sans rien signaler.

Elles se signalent pourtant seules. **Un pas double n'est pas un blanc.**
Un pas de 82,8 px là où le pas régulier vaut 41,5 n'est pas un blanc de
41,3 px, c'est une ligne manquante suivie d'un pas ordinaire. Le critère
est la proximité au *double*.

Ce critère seul ne suffit pas, et il a fallu le mesurer pour s'en
apercevoir : passé sur les six cas connus, il n'en trouvait que trois.
Trois corrections l'ont complété, chacune tirée d'un cas réel :

* **Le pas se mesure localement.** Le bloc des notes est composé à
  34,6 px, le corps à 41,5. Juger une ligne de note au pas du corps
  faisait manquer `homi.`, dont le double vaut 69 px et non 83.
* **Une ligne manquante peut être suivie d'un blanc.** `kazo.` et
  `longa.` donnent 105,9 px — ni *p* ni 2*p*. L'outil rend donc les
  **deux lectures** de tout grand pas : « blanc de x » ou « ligne
  manquante + blanc de y ». Il ne tranche pas ; il ne peut pas.
* **Un blanc ne peut pas être négatif.** Sans ce garde-fou, l'outil
  signalait vingt-deux pas pour six feuillets, dont dix-neuf avec un
  « blanc » de −13 à −18 px. Du bruit pur.
* **Un pas se mesure entre deux lignes, donc la dernière échappe au
  test.** `pos til.` termine sa page : rien ne la suit. Elle se voit à
  l'encre restant **sous** la dernière ligne détectée — 868 px là où
  elle manque, 4 à 65 px sur les feuillets sains.

Ce qu'il vaut, mesuré : sur les six feuillets où une ligne manque
vraiment, il les trouve **tous les six** ; sur six feuillets sains déjà
composés et vérifiés (70 à 75), il signale **sept faux positifs**. Ce
n'est donc pas un verdict, c'est un dépistage : il ramène la recherche de
« relire chaque ligne de chaque page » à « vérifier un endroit par
page ». Le verdict « double net, aucun blanc » s'est jusqu'ici toujours
révélé juste ; les « deux lectures » se tranchent à l'œil.

**À lancer sur tout un lot avant de composer, jamais après.**

*Note de fonctionnement* : la suite complète dépasse maintenant deux
minutes (101 pages, douze contrôles, un rendu à 300 dpi par page). La
lancer avec un délai large, ou par contrôle isolé —
`python3 outils/controles.py 12` — pendant la composition d'un lot.

---

## 8 teretvicies. Une bande peut en cacher deux (folio 87)

Le dépistage des lignes manquantes a payé dès son premier emploi : il a
trouvé `tismo.` au folio 86 et `pro li.` au folio 87, cette dernière avec
le verdict le plus sûr qu'il rende — « double net, aucun blanc », 82,8 px
pour un pas local de 41,5. Les deux pages sont cardées à la main.

Mais le folio 87 a fait échouer deux contrôles à la fois, et le défaut
n'était **pas** dans la page. Le contrôle 10 l'accusait d'un `\VUcontinue`
de trop ; le contrôle 11 y voyait 48 mm… 48 px de dérive. Rendue, la page
est juste : « 105. » est bien renfoncé.

La cause est dans le découpage de MA page composée, non dans le modèle.
`cache.compose` sépare les lignes sur les rangées **sans** encre. Il
suffit qu'un jambage touche l'ascendante de la ligne suivante pour
qu'aucune rangée ne soit vide : les deux premières lignes du corps se
sont soudées en une seule bande, qui a pris l'abscisse de la **seconde**
— au fer à gauche. Le fac-similé ne montre pas le défaut, son
interlignage étant plus large : c'est un artefact de ma composition, et
il se corrige à la source plutôt que dans chaque contrôle.

Toute bande sensiblement plus haute que la médiane de la page est donc
fendue à la rangée la moins encrée de sa partie centrale. Avec un
garde-fou, mesuré lui aussi : posé sans lui, le fendeur a coupé les
**accolades** du tableau du folio 31 et rendu un fragment d'accolade à
+21 px de la marge — que le contrôle 10 a aussitôt signalé, à juste
titre. On exige donc que chaque morceau porte au moins 40 % de l'encre
d'une ligne médiane. Un fragment d'accolade n'y arrive pas, la bande
reste entière, et l'on préfère une bande soudée — que les contrôles
savent signaler — à une bande inventée.

Le gain se mesure : les débuts de ligne vérifiés passent de 2834 à 2995,
et le contrôle 11 couvre 56 pages au lieu de 50, des pages entières
n'étant plus écartées pour cause de comptes divergents.

---

## 8 quateretvicies. La fenêtre du détecteur de filet commençait trop bas

Le dépistage des lignes manquantes s'est retourné contre moi au premier
lot suivant : sur les feuillets 93 et 97, il annonçait un « pas local de
33,1 px » pour des lignes de **corps**, qui en valent 41,5, et concluait
à trois lignes manquantes imaginaires.

La cause remonte à `outils/filet.py`. Privé du filet, le pas local
retombe sur la médiane de **toute** la page — qui, sur une page chargée
de notes, vaut celui des notes. Or le détecteur de filet échouait
précisément sur ces deux feuillets-là.

**Premier remède, essayé et rejeté.** Élargir la fermeture morphologique
de 7 à 11 px les trouve : le détecteur passe de 20 à 16 échecs sur 93
feuillets. Mais il rend alors de **faux** filets — au feuillet 93,
`y = 1680` sur 140 px là où le vrai est à 782 avec ses 213 px
réglementaires : une ligne de texte soudée passait pour un filet. Un
détecteur qui se trompe en silence vaut moins qu'un détecteur qui échoue,
et le remède est écarté.

**La vraie cause.** La fenêtre de recherche partait de 0,45 × H : elle
supposait que le bloc des notes occupe au plus la moitié inférieure de la
page. C'est vrai de presque toutes — mais le feuillet 97 est aux trois
quarts en notes et son filet tombe à 0,29 × H ; celui du 93 à 0,40 × H.
Fenêtre ramenée à 0,25 × H, **onze** feuillets sont récupérés (22, 33,
36, 51, 53, 65, 69, 73, 74, 93, 97) et les échecs tombent de 20 à 9.

La vérification est indépendante et vaut d'être notée : quatre de ces
onze filets — ceux des feuillets 65, 69, 73 et 74 — avaient été relevés
**à la main** lors de leur composition, à 926, 638, 859 et 879 px. Le
détecteur corrigé rend exactement ces quatre valeurs. Ce n'est pas moi
qui confirme l'outil, ce sont deux mesures indépendantes qui concordent.

Leçon générale, la troisième du même genre après le mode arrondi (§ 7
quater) et le pli du papier (§ 8 unetvicies) : **quand un outil échoue,
chercher son hypothèse cachée avant d'élargir ses seuils.** Élargir le
seuil traitait le symptôme et fabriquait des faux positifs ; l'hypothèse
fausse — « les notes sont dans la moitié basse » — était réparable
exactement.

---

## 8 quinetvicies. Ce que seule la juxtaposition attrape

Les folios 88 et 89 portaient chacun une ligne invisible au détecteur —
`sur...).` et `S. ó, ú.` — l'une et l'autre annoncées par
`outils/lignes_manquantes.py` avant que je compose, et vérifiées à
l'agrandissement. C'est le régime de croisière voulu : l'outil dit où
regarder, l'œil tranche, la page est cardée à la main.

Deux fautes ont pourtant survécu à tous les contrôles automatiques, et
il faut dire pourquoi.

* **`Sufias` pour `Suficas`** (folio 88). Aucun contrôle ne pouvait la
  voir : le contrôle 2 compare mon PDF à **mon propre relevé**, et les
  deux portaient la même faute. C'est la juxtaposition du contrôle 8 —
  fac-similé et composé côte à côte — qui l'a rendue visible, puis
  l'agrandissement qui l'a confirmée.
* **`rempl-/sesas` pour `rempla-/sesas`** (folio 89). Le contrôle 3
  vérifie que chaque `\cc` tombe entre deux lettres et respecte D. 485 —
  ce que les deux coupures font. Le `a` est simplement effacé par le
  scan, et seul l'agrandissement montre qu'il y avait quelque chose.

La leçon n'est pas nouvelle mais elle mérite d'être écrite : **les
contrôles vérifient la fidélité du composé au relevé, jamais celle du
relevé au fac-similé.** Cette seconde fidélité-là n'a qu'un juge, la
juxtaposition, et elle se regarde page par page. Ne pas la sauter sous
prétexte que les douze contrôles passent.

Le folio 110 l'a confirmé une fois de plus, et pour la **graisse** cette
fois : j'y avais composé en gras tout un alinéa (« Remarkez, ke la
propoziciono… ») et l'expression « por ke », que le fac-similé donne en
romain. Les douze contrôles passaient. Seule la juxtaposition l'a montré,
et l'agrandissement l'a confirmé — huitième et neuvième démentis d'une
lecture de graisse sur neuf.

---

## 8 sesetvicies. Une bande soudée, et l'espace à la française

Le dépistage a gagné un troisième test, et le contrôle 2 a perdu un faux
échec. Les deux viennent du même lot.

**Une bande peut en cacher deux, du côté du fac-similé aussi.** J'avais
réparé ce défaut dans `cache.compose` pour ma page composée (§ 8
teretvicies) sans voir qu'il valait aussi pour le modèle. Au feuillet 97,
la dernière bande mesure 57 px pour une médiane de 27 : elle porte les
deux dernières lignes de la note (17). Ni le pas double ni l'encre de
queue ne la voient — le pas la compte pour une seule ligne, et rien ne la
suit. `lignes_manquantes.py` signale désormais toute bande sensiblement
plus haute que la médiane locale. Passé sur dix feuillets déjà composés
et vérifiés (70 à 79), il n'en signale aucune ; sur le 97, il trouve la
bonne.

**L'espace à la française faisait échouer deux pages justes.** Le source
écrit `if;` ; c'est `\VUespacePonct` qui pose l'espace au moment de
composer. Le relevé, lui, lit le source et rend `if;`. Restait
`pdftotext`, qui n'annonce l'espace que lorsqu'elle dépasse son seuil
géométrique : après une lettre romaine il ne la voit pas, après une
**italique** — dont la correction s'ajoute à l'espace — il la voit. D'où
deux échecs aux folios 90 et 91, `E. if ;` contre `E. if;`, sur des pages
parfaitement justes. Quatre-vingts pages avaient passé par chance.

`_norm` normalise donc l'espace devant `; : ! ?` des **deux** côtés, comme
elle le faisait déjà devant `,` et `.`. Ce que cela coûte se nomme : le
contrôle ne peut plus voir une espace à la française manquante. Mais elle
ne peut pas manquer sur *une* ligne — elle vient d'une macro posée une
fois pour tout le volume, vérifiée à l'œil au folio 12. Un défaut global
resterait visible, un défaut local est impossible : la normalisation ne
masque donc rien de réel.

Troisième `\S{}` écrit pour `§` (après les folios 59 et 90) : le relevé
ne le rend pas, `pdftotext` si. Écrire toujours le caractère littéral.

**Le folio 93 a cumulé les trois défauts du détecteur** — filet à 0,29 H,
ligne `hike.` invisible, dernière bande soudée — et les trois ont été
annoncés par `lignes_manquantes.py` avant que je compose. C'est
exactement ce que l'outil est là pour faire, et c'est la première page
où il l'a fait seul, sans que j'aie rien cherché à l'œil.

Reste une faute qu'il ne pouvait pas voir et que le contrôle 10 a prise :
j'avais de nouveau enchaîné les dix-sept notes par des `\nl` au lieu de
les traiter en alinéas. Le fac-similé renfonce le premier mot de chacune.
Troisième récidive (folios 59-63, 74, 93) : **dans un bloc de notes,
chaque note est un alinéa, jamais une ligne de plus.**

---

## 8 septetvicies. Le deuxième tableau du volume (folio 94), et une limite du dépistage

Le folio 94 ouvre la matière des nombres : un titre `NOMBRI.`, et le
deuxième tableau du volume après celui du folio 31. Celui-ci est plus
simple — quatre rangs, deux colonnes, et des **points de conduite**. Les
abscisses se relèvent comme au folio 31, en amas, la marge du bloc à
x = 225 px : les mots à 7,7 mm, la première colonne de chiffres à
50,6 mm, la seconde à 69,3 mm, et l'en-tête à 45,8 et 73,4 mm.

Les points, eux, tombent sur une **grille régulière** de pas 4,68 mm
(21,61 / 26,28 / 30,96 / 35,63 / 40,30 mm) : chaque rang porte ceux qui
suivent son mot — cinq pour « Miliono », trois pour « Quadriliono ». Un
des points de la deuxième rangée est trop pâle pour être mesuré ; la
grille dit où il est, et c'est plus sûr que la mesure.

**Une limite du dépistage, nommée.** `lignes_manquantes.py` a signalé ici
deux pas doubles, aux lignes 6 et 7. Ce ne sont pas des lignes absentes :
ce sont les blancs du **titre**. Un titre précédé d'un blanc de 40 px
donne un pas de 82 px, que le test lit comme un double. L'outil ne peut
pas les distinguer — et c'est précisément pourquoi il rend deux lectures
au lieu de trancher. Le réflexe à garder : sur une page qui porte un
titre, les deux pas qui l'encadrent sont toujours signalés, et ce sont
toujours des blancs.

Quatrième `\VUcontinue` de trop (après les folios 45, 55 et 21), attrapé
par le contrôle 10 comme les trois précédents. Le contrôle 2 a par
ailleurs révélé que `pdftotext` pose une espace **après un exposant**,
même devant une parenthèse fermante : `(1,000,000^2 )`. `_norm` la
normalise désormais comme elle le faisait déjà devant `,` et `.` — le
contrôle 6 vérifie par ailleurs qu'aucune ligne ne commence par une
parenthèse fermante, donc rien n'est masqué.

---

## 8 duodetricies. Contrôle 12 — chaque note est un alinéa

Quatre récidives de la même faute (folios 59-63, 74, 93, 106) : les notes
d'un bloc enchaînées par des `\nl` au lieu d'être traitées en alinéas. Le
fac-similé renfonce le premier mot de chacune. Le contrôle 10 la
rattrapait à chaque fois, mais **après coup et par un symptôme indirect**
— « le relevé la donne pleine mais elle ne fait que 17 % ». On mesure
donc la chose elle-même : le fac-similé renfonce *n* lignes du bloc, le
source doit y compter *n* alinéas.

Écrit, le contrôle a trouvé **deux fautes que rien n'avait vues** — folios
101 et 104, où deux notes étaient enchaînées. Le contrôle 10 ne pouvait
pas les voir : leurs lignes ne sont ni trop courtes ni trop longues, elles
sont simplement au mauvais endroit.

Trois faux positifs ont dû être écartés avant cela, et chacun a appris
quelque chose :

* **Un alinéa ouvert par `\VUcontinue` n'est pas renfoncé** — c'est la
  suite d'une note commencée au folio précédent. Quatre pages justes
  accusées.
* **Une bande soudée fausse l'abscisse** : soudée à sa voisine, une bande
  prend le `x0` de la plus à gauche, et une ligne renfoncée passe pour
  être à la marge. La page est déclarée non jugée.
* **Une trace parasite dans la marge aussi.** Au folio 29, `Decido 586` se
  mesure à +7 px là où l'agrandissement la montre renfoncée comme ses
  deux voisines : deux mouchetures de 2 et 6 px traînent dans sa marge.
  Le détecteur écrit pour le pli du folio 79 ne les voyait pas — il
  n'examinait que l'amas de tête. **Les traces vont par plusieurs** : il
  saute désormais tous les amas minces avant de mesurer le blanc.

C'est la troisième fois qu'une mesure d'abscisse est défaite par de la
saleté ou un pli, et la troisième fois que le remède est le même : lire
en amas, jamais en étendue, et déclarer non mesuré plutôt que d'accuser.

**Quatrième faux positif, et il portait sur la marge elle-même.** Le
contrôle prenait la marge du bloc pour le **minimum des abscisses des
lignes de note** — ce qui suppose qu'au moins une ligne du bloc soit au
fer à gauche, c'est-à-dire qu'au moins une note occupe deux lignes. Au
folio 114 les deux notes tiennent chacune sur une ligne : toutes deux
renfoncées, le minimum *valait* le renfoncement, l'écart tombait à zéro,
et le contrôle accusait de `\nl` une page qui n'en portait pas.

Deux remèdes ont été essayés, et le premier était pire que le mal :

* **Médiane des abscisses du corps** : vingt et une pages justes mises en
  échec. Le corps du folio 34 est une liste dont seize lignes sur vingt
  sont renfoncées de 52 px — leur médiane *est* le renfoncement.
* **Constante du recueil** : impossible. Le rognage suit le bord du
  papier et non la justification, si bien que la marge oscille de 49 à
  280 px selon le feuillet, recto et verso alternés.

La marge se mesure donc page à page et sur **toutes** les bandes, tête de
page exceptée : corps ou notes, une page en porte toujours quelques-unes
au fer. On en prend le **décile** et non le minimum, pour qu'une saleté
isolée ne la tire pas vers la gauche ; et si le minimum s'en écarte de
plus de 10 px, quelque chose traîne hors justification et la page n'est
pas jugée. Les 68 pages à notes passent.

La leçon vaut plus que le correctif : **une référence prise à l'intérieur
de l'échantillon qu'on mesure s'effondre dès que l'échantillon est
homogène.** Elle valait pour le minimum pris dans les notes ; elle valait
encore pour la médiane prise dans un corps tout renfoncé.

---

## 8 undetricies. L'ornement de fin de partie

Le folio 114 ferme la première partie, et la juxtaposition l'a montré ce
qu'aucun contrôle ne cherchait : sous le bloc de notes, dans le blanc,
**un filet court et centré**. Rien ne le signalait — les contrôles
comparent le composé au relevé, et le relevé ne le portait pas.

Mesures au feuillet 118 : 305 px = **25,8 mm**, centre à 766 px quand le
milieu de la justification est à 766,5 — centré, donc. Son profil
d'encre est celui du filet de note (pic à 209 contre 193, même
demi-largeur de deux rangées) : c'est le même filet maigre, seule la
longueur change. Il est distant du filet de note de 275 px = 23,3 mm, et
c'est ainsi que son ordonnée a été posée, faute d'un rognage mesuré pour
ce feuillet : 147,14 mm. Le composé le rend à 275 px du filet de note, à
moins d'un pixel.

D'où `\VUornement{ordonnée}`, bâti comme `\VUnotes` — placé en tête de
page, de hauteur nulle, il ne pousse rien.

Deux choses à retenir :

* **Les contrôles ne cherchent que ce qu'on leur a décrit.** Un filet que
  le relevé ignore est invisible à tous les douze. Seule la juxtaposition
  le montre, et il faut regarder **le blanc** de la page autant que son
  texte.
* Ajouter une macro muette oblige à l'inscrire dans `MUETTES` de
  `controles.py`, sans quoi son argument se lit comme du texte : le
  contrôle 2 a ouvert le folio 114 sur une ligne « 147.14mm ».

Le second ornement du volume est à attendre à la fin de la deuxième
partie, et ainsi de suite : à chaque fin de partie, regarder le blanc.

---

## 8 vicies. Le faux-titre de la deuxième partie (feuillets 119-120)

Le feuillet 119 est une page d'apparat, bâtie comme le faux-titre du
volume : trois lignes placées chacune à son ordonnée mesurée, de hauteur
nulle, plus le filet court. Le feuillet 120 est blanc — le détecteur n'y
trouve aucune ligne, comme au feuillet 6.

**La graisse de `VORTIFADO`.** À première vue la ligne est grasse : elle
est plus noire que ses deux voisines. Elle ne l'est pas, et les deux
mesures qui le montrent valent d'être retenues.

* Les rapports fût/capitale de la page — 0,140, 0,175, 0,160 — tombent
  tous dans la fourchette du faux-titre du feuillet 5, dont les trois
  lignes sont romaines et donnent 0,152, 0,167 et 0,146. **Le fût ne
  sépare rien**, une fois de plus.
* Ramenée par interpolation à la hauteur de capitale de `LINGUO
  INTERNACIONA IDO`, la ligne lui est superposable : mêmes empattements,
  même O, même R. C'est le même romain, plus grand.

Ce qui trompe l'œil, c'est le corps : 14,17 pt contre 10,10 et 8,86 pt
sur la même page. **Une ligne plus grande paraît plus grasse.** C'est la
dixième fois qu'une graisse jugée à vue se révèle fausse à
l'agrandissement, et la première où la cause est la taille.

**L'interlettrage d'`apparat.py` demande une retouche sur le composé.**
L'outil déduit l'interlettrage de la largeur mesurée et d'une largeur nue
estimée par une composition d'essai. Cette estimation se dégrade quand la
ligne porte beaucoup de blancs de mot : `PER DERIVO O PER KOMPOZO` en
compte quatre et sortait 2,54 mm trop courte, soit 4,3 %. Corrigés sur le
composé (201 → 219 et 227 → 261), les quatre écarts de la page tombent à
0,08, 0,00, 0,08 et 0,51 mm — mieux que le faux-titre du volume, déjà
accepté, qui est à 0,26, 0,42 et 1,27 mm.

La règle générale : **`apparat.py` donne un point de départ, pas une
valeur** ; toute ligne d'apparat se remesure sur le composé.

---

## 8 unvicies. Les titres, et le biais d'`apparat.py`

Six folios composés d'un coup (117 à 122) ont apporté **neuf lignes de
titre**, plus que tout le reste du volume réuni. Trois choses en sont
sorties.

**Le folio manquant.** Le folio 117 ouvre la deuxième partie et **ne
porte pas de folio courant** : la tête de page est nue, vérifié à
l'agrandissement. Son champ folio reste donc vide. À l'inverse le folio
122 en porte un que le détecteur de lignes **n'a pas vu** — la première
bande de sa géométrie est le titre `AFIXI.`, non le folio. Les deux cas
se sont présentés dans le même lot, en sens contraires : **la tête de
page se regarde, elle ne se déduit pas du relevé géométrique.**

**Le sous-titre.** Sous `DERIVADO PER AFIXI.` et sous `REGULI DI
DERIVADO *.`, le fac-similé pose des lignes centrées en **bas de casse
italique, au corps du texte courant** — hauteur de capitale 21 px comme
les lignes de corps, contre 29 px pour le titre qui les surmonte.
`\VUtitre` les composerait en demi-gras capitales. D'où `\VUsoustitre`,
même macro sans la fonte grasse. Il a fallu l'inscrire dans `APPARAT` de
`controles.py`, faute de quoi le contrôle 2 lisait ses mesures comme du
texte.

**`apparat.py` surestime l'interlettrage du demi-gras d'environ 6 %.**
Les six titres en capitales sont sortis de 0,76 à 3,22 mm trop larges,
soit un écart constant de −32 à −48 millièmes de cadratin à retrancher.
Le biais n'avait jamais sauté aux yeux parce que jusqu'ici les titres
venaient un par page. Corrigés sur le composé, les neuf titres tombent à
0,51 mm au pire, et sept d'entre eux sous 0,2 mm.

**Piège de mesure, à ne pas refaire :** j'ai d'abord voulu corriger en
comparant la **largeur de boîte** LaTeX (`\settowidth`) à la largeur
mesurée au fac-similé. Les deux ne sont pas commensurables — la boîte
contient les approches latérales et l'interlettrage traînant du dernier
caractère, le fac-similé ne donne que l'**encre**. La correction se
mesure sur la page composée, jamais sur une boîte.

---

## 8 duovicies. La rousseur et la lettre cassée

Six folios de plus (123 à 128), tous des pages de corps sans titre. Deux
choses en sont sorties, l'une sur l'outil, l'autre sur le livre.

**Le test de queue s'est encore trompé, deux fois de suite.** Aux
feuillets 128 et 129 il annonçait « dernière ligne manquante probable »
sur 549 et 764 px d'encre sous la dernière ligne détectée. Agrandie, il
n'y a là que de la **rousseur** — des piqûres de papier, denses mais
sans structure de ligne. C'est la deuxième famille de faux positifs de ce
test après le folio 101, et la leçon ne change pas : **le dépistage
signale, il ne tranche pas.** Un signalement se lit au fac-similé avant
de composer quoi que ce soit.

En regard, le verdict **« double net, aucun blanc »** a de nouveau eu
raison : au feuillet 132 il annonçait une ligne perdue dans le bloc de
notes, et elle y était — `IV, 68.)`, deuxième et dernière ligne de la
note (2), longue de 160 px seulement. Le détecteur perd les lignes très
courtes. Ce verdict-là ne s'est encore jamais trompé.

**Une lettre cassée n'est pas une coquille — mais on transcrit quand
même ce qui est imprimé.** La note (4) du folio 128 porte `automooilo`.
Agrandi dix fois, le constat est net : la lettre litigieuse n'a **aucune
encre au-dessus de la hauteur d'x**, alors que la hampe du `l` voisin,
huit pixels plus loin, et le point du `i` s'impriment noirs et pleins.
C'est un `o`. Que la cause soit une sorte cassée dans la casse du
compositeur ou une erreur de composition, la transcription diplomatique
donne la page telle qu'elle est et signale l'écart — elle ne restitue pas
un `b` que le papier ne porte pas.

---

## 8 tervicies. Le premier démenti du « double net », et deux erreurs à moi

Six folios de plus (129 à 134). Le lot a démenti deux choses que je
tenais pour acquises, et l'une des deux était mon propre travail.

**« Double net, aucun blanc » a enfin tort.** Le verdict n'avait jamais
failli en cent vingt pages. Au feuillet 136 il annonçait une ligne
perdue ; le profil d'encre sur **toute la largeur de la page** donne zéro
pixel encré des rangées 768 à 819, deux poussières exceptées. La cause
est identifiée et elle est structurelle : le blanc qui **précède** un
titre centré vaut ici presque exactement deux pas, ce que le dépisteur
lit comme un double net sans blanc. Le verdict reste le plus sûr des
trois, mais il n'est plus infaillible, et **la page à titre est sa zone
aveugle**.

**Un cadrage qui commence après la marge fait disparaître un mot.** Le
dépisteur signalait de l'encre sous la dernière ligne du feuillet 137.
Je l'ai agrandie et déclarée jambage — mon cadrage partait de x = 120
quand la marge de la page est à x = 71. Le mot était coupé hors du
cadre ; je n'en voyais que la fin, qui ressemble en effet à une descente
de jambage. Le releveur, lui, a mesuré l'encre à x 71–160 et l'a lue :
c'était un mot entier, seul sur sa ligne. **Un cadrage de vérification
part toujours de la marge de la page, jamais d'une valeur ronde.**

**Le blanc d'un titre est l'excès, pas l'excès moins le pas.** Aux
feuillets 135 j'ai posé 4,13 mm et 0,85 mm là où il fallait 7,74 et
4,45 : j'avais retranché le pas une seconde fois d'une valeur qui
l'était déjà. Le dépisteur donne le blanc, `\VUsaut` le prend tel quel.

**Ce qui reste ouvert, et pourquoi je ne l'ai pas forcé.** Deux pages du
lot gardent une dérive : le folio 130, dont le titre ouvre la page et
tombe 2,54 mm trop bas, et le folio 131, dont la dérive s'accumule ligne
à ligne jusqu'à 4,70 mm malgré `\VUinterlignePage`. J'ai essayé un
`\VUsaut` négatif au folio 130 : la juxtaposition montre le titre venu
buter dans le folio courant, c'est-à-dire un remède pire que le mal.
Je l'ai retiré. **Une page à titre en tête n'obéit pas au même modèle
vertical que les autres, et ce modèle reste à établir** — sur mesures,
pas sur essais.

---

## 8 quatervicies. Douze folios d'un coup, et ce que la panne a appris

Le lecteur a demandé douze folios. Les douze agents lancés ensemble ont
**tous été tués par une surcharge serveur** (529) après avoir dépensé
près d'un million de jetons, et leurs transcriptions ont été perdues :
`SendMessage` répond « No transcript found ». Relancés **par vagues de
quatre**, les douze ont abouti sans un seul échec.

**La leçon est opérationnelle et vaut d'être retenue : quatre agents en
parallèle passent là où douze échouent.** Le débit réel est meilleur en
trois vagues de quatre qu'en une vague de douze, puisqu'une vague perdue
est intégralement à refaire.

**Cinq lignes invisibles retrouvées sur ce lot, toutes très courtes.**
C'est désormais la signature du défaut : le détecteur perd les lignes de
moins de 200 px, et le dépisteur les déclare « sans blanc » parce que
leur encre par rangée tombe à 30 px là où une ligne pleine en donne 300.
La consigne de relevé le dit maintenant explicitement, et deux releveurs
ont trouvé leur ligne sur ce seul indice. L'une d'elles n'était **pas
signalée du tout** (feuillet 147) : elle a été trouvée parce que le
compte des lignes ne tombait pas juste.

**Un filet que l'outil ne voit pas.** Au feuillet 143 le filet des notes
est si pâle qu'il ne devient continu qu'à un seuil de 210, quand le
détecteur seuille à 185 — d'où « filet introuvable » et l'impossibilité
de dépister la page. Trouvé au profil d'encre, il est à sa place
ordinaire, long de 210 px. **Un filet introuvable n'est pas un filet
absent** ; c'est un seuil trop haut.

**Ce qui reste ouvert.** Le contrôle 10 signale au folio 136 un
`\VUcontinue` de trop : le fac-similé donnerait la première ligne à
+60 px de la marge, le composé à +10. Le releveur soutient que le +60
est un artefact — la ligne commence par un signe « = » très pâle dont le
détecteur ne saisit que la moitié droite. L'agrandissement va dans son
sens, mais la mesure au pixel est brouillée par l'ombre de reliure de ce
feuillet. **Je laisse le contrôle en échec plutôt que de trancher sur
une mesure que je sais contaminée.**

---

## 8 quinvicies. Seize folios, et un filet perdu pour un pixel

Seize folios en quatre vagues de quatre — la cadence trouvée au lot
précédent, après qu'une vague de douze eut été entièrement perdue. Les
quatre vagues ont abouti sans un échec.

**Le filet perdu pour un pixel.** Trois feuillets du lot étaient déclarés
« filet introuvable », donc non dépistables. Le relevé du feuillet 162 a
trouvé le filet à la main *et* diagnostiqué la cause dans
`outils/filet.py`. Le test « rien d'autre sur la ligne du filet » sommait
l'encre jusqu'à `span[1]`, borne que `text_region` ne rogne pas toujours :
la tranche du feuillet voisin comptait comme de l'encre. Le total sortait
à **7 pour un seuil de 6** — un pixel de trop. Une marge de 25 px retirée
à droite récupère le feuillet 162 (à l'ordonnée exacte mesurée à la main)
et le feuillet 164.

**Deux feuillets restent hors de portée, et pour une autre cause : le
filet y est trop pâle.** Au feuillet 143 il ne devient continu qu'à un
seuil de 210, au feuillet 163 qu'à **220**, quand l'outil seuille à 185.
Les deux ont été mesurés à la main. Abaisser le seuil global serait
tentant et dangereux — il ferait passer du texte pour du filet. On note
donc la limite plutôt que de la forcer.

**Neuf lignes invisibles retrouvées**, toutes très courtes, deux d'entre
elles sans qu'aucun dépistage les ait signalées — trouvées parce que le
compte des lignes ne tombait pas juste.

**Une ligature parasite.** Le folio 150 cite le suffixe `-ij-` ; la fonte
le composait en **ĳ**, la ligature néerlandaise. Le contrôle 2 l'a vu.
Rompue par `\/`. À surveiller partout où le livre cite `ij`.

**Une exception admise au contrôle 3.** Le folio 160 coupe
`flor(kultiv)isto` entre `flor-` et sa parenthèse ; le tiret est bien
imprimé, vérifié à l'agrandissement. La règle D. 485 ne parle que de
syllabes et ne prévoyait pas la parenthèse. Le contrôle l'admet
désormais en tête de suite, le reste de la règle valant toujours.

---

## 8 sesvicies. Le filet manqué pour deux raisons différentes

Quatre folios de plus (163 à 166), et une leçon d'outil qui vaut d'être
notée parce que je m'y suis trompé.

**Le filet du feuillet 169 n'était pas trop pâle.** Aux feuillets 143 et
163, la cause était le seuil — le trait n'y devient continu qu'à 210 et
220 quand l'outil seuille à 185. J'ai supposé la même cause ici. Le
releveur a montré que non : au seuil ordinaire le filet passe déjà le
test de longueur (186 px), et c'est le **test du reste** qui le rejette.
Deux saletés à x 1301-1335 — la tranche du feuillet voisin — donnent
`reste = 23` pour un seuil de 6, alors que la colonne de texte s'arrête
vers 1170. La marge fixe `BORD = 25`, posée après le feuillet 162, ne
suffit pas à cette distance.

**Deux causes distinctes derrière le même message d'erreur.** « Filet
introuvable » recouvre au moins un problème de seuil et un problème de
borne droite. Les confondre conduit à corriger la mauvaise.

**Et le remède évident ne marche pas.** J'ai essayé de remplacer la marge
fixe par une borne mesurée — la dernière colonne portant de l'encre sur
au moins vingt rangées. Le détecteur a alors échoué sur **tous** les
feuillets, y compris ceux qu'il trouvait auparavant. Je n'ai pas cherché
plus loin et j'ai remis l'état antérieur : `BORD = 25` retrouve les
feuillets 162, 164 et 169, et laisse le 143 et le 163 au relevé manuel.
**Un outil qui marche pour trois pages sur cinq vaut mieux qu'un outil
cassé pour cinq sur cinq**, et la borne juste reste à trouver.

---

## 8 septvicies. Seize folios, et la troisième cause du filet perdu

Seize folios en quatre vraies vagues de quatre. **La leçon de méthode du
tour précédent était la bonne, et je l'avais mal appliquée** : décrire une
vague puis n'envoyer qu'un agent ne parallélise rien. Quatre appels dans
*un seul message* s'exécutent ensemble ; c'est ce qui a permis les seize.

**« Filet introuvable » recouvre TROIS pannes distinctes.** Aux deux
déjà connues — seuil trop haut (feuillets 143, 163, 173, 175, 177) et
saleté hors colonne (169) — le feuillet 180 en ajoute une troisième :
**le filet est au-dessus de la fenêtre de recherche**. `filet.py` part de
0,25 H ; sur cette page presque vide, qui clôt la deuxième partie, le
bloc de notes remonte à y = 377 quand la fenêtre commence à 520. Le filet
passe les deux tests — il n'est jamais examiné. Le même message d'erreur
a donc maintenant trois causes, et chacune appelle un remède différent.

**Un contrôle qui plante ne vérifie plus rien, et il l'a fait en
silence.** Le contrôle 9 levait une exception sur le feuillet 182, verso
blanc : le fac-similé y porte sept bandes parasites (pli, bord de page)
quand le composé n'a aucune ligne, et `larg.max()` sur un tableau vide
arrête le contrôle **entier**. Il ne jugeait donc plus aucune page du
volume. Corrigé par une garde explicite.

**Les pages d'appendice n'ont pas de notes**, et il fallait le prouver
plutôt que le supposer : les releveurs ont vérifié le profil d'encre aux
trois seuils sous la dernière ligne. Ce qui apparaît à 210 et 220 est le
fond du papier, uniforme, sans structure — pas un filet.

**Neuf lignes invisibles retrouvées**, toutes très courtes. L'une d'elles
valide la correction de cadrage tirée du feuillet 137 : le signalement
« encre sous la dernière ligne » s'était révélé trois fois de la rousseur,
et une fois un mot entier que j'avais pris pour un jambage faute d'avoir
cadré à gauche de la marge. Le releveur, cadrant 47 px avant la marge,
l'a lu sans hésiter.

---

## 8 duodetricies. L'astérisme, et ce qu'un ornement neuf coûte

Quatre folios seulement ce tour-ci, et il faut dire pourquoi : **un
ornement inconnu du volume a mangé le temps de trois vagues.**

Le folio 186 porte un **astérisme** — trois astérisques en triangle,
entre deux alinéas, là où la première partie se contentait d'un filet.
Mesures : les deux astérisques bas à x 798 et 858, celui du haut à 828,
soit exactement leur milieu ; un vrai triangle isocèle, centré sur la
justification. D'où `\VUasterismo`.

**Trois erreurs successives, qui valent d'être notées parce qu'elles
tiennent toutes au même malentendu.**

1. *L'ordonnée brute du scan.* J'ai posé l'ordonnée lue sur l'image
   préparée, sans le décalage de rognage propre au feuillet. L'ornement
   est tombé en plein texte. L'ordonnée d'un élément placé se calcule
   **toujours** relativement à la première ligne de corps de la même
   page, jamais en absolu sur le scan.
2. *Le `\baselineskip` dans le vbox.* Ma macro plaçait le second rang
   par `\vskip \VUasterismoHaut - \baselineskip`, ce qui mêlait un
   réglage mesuré à un ressort ambiant. `\offinterlineskip` et un
   `\vskip` nu font ce qu'on croit qu'ils font.
3. **La faute de fond : un ornement de hauteur nulle n'ouvre pas son
   blanc.** `\VUasterismo` ne pousse rien, comme `\VUornement` ; mais
   l'astérisme, lui, est *dans le flux* du fac-similé et y occupe
   82,5 px. Sans `\VUsaut`, tout le texte qui suit remontait, et
   l'ornement, posé juste, chevauchait des lignes qui n'étaient pas à
   leur place. **Un élément placé absolument suppose que le flux réserve
   sa place** : les deux vont ensemble, et je les avais dissociés.

Reste une limite consignée plutôt que forcée : le contrôle 2 lit les
astérisques comme la fin de la ligne précédente, l'ornement tombant à sa
hauteur. Même famille que le `FINO.` du folio 176 — le composé est juste,
c'est le modèle d'ordre du relevé qui ne prévoit pas un signe posé hors
du flux. Vérifié à la juxtaposition.

**Et la ligature `ij` est revenue** (folio 185, un mot français cité).
Elle avait déjà frappé au folio 150. À surveiller partout où le livre
cite du français.

---

## 8 undetricies. La troisième cause du filet, enfin corrigée

Quatre folios, et la réparation d'un outil que j'avais cassé en voulant
le réparer trop vite au tour précédent.

**La fenêtre de recherche du filet partait trop bas.** C'est la cause (c),
repérée au feuillet 180 et confirmée nettement au feuillet 194 : le filet
y est à y = 450 quand la fenêtre commence à 516. Il passe les deux tests
— longueur 213 px, reste 2 — et n'est simplement jamais examiné. Le
relevé du feuillet 194 a fait mieux que le signaler : il a rejoué le
détecteur avec la seule fenêtre élargie et montré qu'il le trouve aussitôt.

**Cette fois j'ai testé avant d'adopter.** Vingt-deux feuillets témoins,
mesurés avant et après le passage de 0,25 H à 0,10 H : **deux gagnés
(180 et 194), aucun perdu, aucun déplacé.** C'est exactement la
vérification qui manquait au tour précédent, où une « amélioration » non
testée avait cassé le détecteur sur toutes les pages à la fois.

Il reste la cause (a), la plus fréquente — le filet trop pâle, dont
l'extrémité gauche tombe sous le seuil, si bien que la longueur retombe
à 1 px avant même le test du reste. Deux feuillets de ce lot en relèvent
encore. Baisser le seuil global reste tentant et dangereux : il ferait
passer du texte pour du filet. Les releveurs le mesurent à la main, et
c'est pour l'instant la bonne réponse.

**Une note de méthode sur `outils/graisse.py`.** Au feuillet 191 il rend
« GRAS » pour les vingt-deux lignes du corps, sans exception. Un verdict
uniforme n'est pas une mesure : c'est le signe que la page est trop
encrée ou trop ombrée pour l'outil. Le releveur l'a écarté et tranché à
l'œil. À retenir comme critère de rejet de l'outil lui-même.

---

## 8 tricies. Deux signatures posées faux depuis trois lots

Quatre folios, et la découverte d'une erreur que j'avais commise deux
fois sans le voir.

**Une ordonnée se calcule relativement à la page, jamais en absolu.**
C'était déjà la leçon de l'astérisme. Je ne l'avais pas appliquée aux
**signatures de cahier** : je posais l'ordonnée lue sur le scan, sans le
décalage de rognage propre au feuillet. Les trois signatures du volume
étaient donc **7 à 8 mm trop haut** — et je ne l'ai vu que parce que la
troisième est venue buter dans la dernière ligne du bloc de notes, ce
que le contrôle 2 a signalé (« 7maristo, » au lieu de « quale maristo, »).

Recalculées relativement à la première ligne de corps, les trois valeurs
tombent à **168,15 / 169,50 / 170,01 mm** — c'est-à-dire dans le
voisinage immédiat des 168,7 mm que le préambule enregistrait déjà comme
la valeur relevée sur six des sept pages signées. Cette concordance est
la vraie vérification : trois pages indépendantes, trois valeurs à moins
de 2 mm l'une de l'autre, là où mes chiffres antérieurs se dispersaient
sur 2,5 mm autour d'une valeur fausse.

**Ce que cela dit du contrôle.** Les deux premières signatures étaient
fausses depuis trois lots et aucun contrôle ne les voyait : elles
tombaient dans un blanc, sans rien heurter. Ce n'est pas la mesure qui
les a rattrapées, c'est une collision fortuite. Un élément placé
absolument dans une zone vide n'est vérifié par rien — il faudrait un
contrôle qui compare sa position à celle du fac-similé, comme le
contrôle 11 le fait pour les lignes.

**Une ligne invisible qui était la PREMIÈRE du corps** (feuillet 198) —
le cas le plus conséquent, puisqu'une première ligne absente décale toute
la page. Aucun dépistage ne l'avait signalée : le releveur l'a trouvée
parce que son compte de lignes ne tombait pas juste. C'est la deuxième
fois que le comptage seul rattrape ce que le dépisteur laisse passer.

---

## 8 untricies. La quatrième panne du filet, et la seule qui mente

Quatre folios, et la découverte de la panne la plus dangereuse de ce
détecteur.

**Les trois pannes connues le font échouer. La quatrième le fait
mentir.** Au feuillet 199, le vrai filet est à y = 1174, long de ses
212 px réglementaires — mais son extrémité gauche est trop pâle (c'est la
cause (a) : n retombe à 1). Il n'est donc pas candidat. Or **un autre
trait, 640 px plus bas et long de 154 px seulement, passe tous les
tests** : le détecteur le retient et rend 161,63 mm au lieu de 107,74.

Posé si bas, le bloc de notes débordait la page et **y perdait une
ligne** — c'est le contrôle 2 qui l'a signalé (« ligne 25 : `<manque>` »),
pas le détecteur, qui n'avait rien à signaler puisqu'il croyait avoir
trouvé. Une panne silencieuse ne se rattrape que par un contrôle en aval.

**Ce que le relevé disait déjà.** Le releveur avait écrit noir sur blanc
que le filet des notes est à y = 1174. J'ai posé la valeur de l'outil
sans la confronter à la sienne. **Quand un releveur donne une mesure que
l'outil donne aussi, il faut les comparer, pas en choisir une.**

**Garde ajoutée, et son honnête limite.** Le filet mesure 210 à 216 px
sur vingt-six feuillets témoins : c'est une constante du volume, non une
grandeur libre. Le détecteur retient désormais le candidat **le plus
proche de 213 px**, non le plus long. Testé : trois filets se déplacent
d'un pixel (0,08 mm), aucun n'est perdu. **Mais cette garde ne corrige
pas le feuillet 199** — le vrai filet n'y étant pas candidat, aucune
règle de choix ne peut le préférer. Elle protège les cas où les deux
candidats se présentent ; elle ne remplace pas la lecture du releveur.

---

## 8 duodevicies. Le `\VUcontinue` de trop, et le contrôle qui le trouve

Trois fois j'ai ouvert une page par `\VUcontinue` — qui compose au fer à
gauche, pour un alinéa venu de la page précédente — là où le fac-similé
renfonce. Folio 45, folio 55, tous deux signalés par le lecteur ; et un
troisième au folio 21, que personne n'avait vu.

La cause est toujours la même : je suppose la continuité au lieu de la
mesurer. Le renfoncement se lit pourtant d'un coup d'œil dans les données
déjà relevées — 49, 58 et 56 px respectivement, contre le renfoncement
ordinaire de 54.

Le contrôle 10 confronte désormais **la première ligne du corps** de
chaque page à sa mesure au fac-similé, et elle seule : ailleurs dans la
page, fer à gauche et renfoncement sont l'un et l'autre légitimes, mais
pour cette ligne-là le modèle tranche. C'est ainsi que le folio 21 est
sorti. Le contrôle saute les pages qui s'ouvrent sur une ligne d'apparat,
où la comparaison n'a pas de sens.

## 9. Coquilles de l'original

Conservées telles quelles.

* **Folio 63, note (3).** La note ouvre sur `Me pagis a lu cirkume dek
  franki »` : le guillemet **ouvrant** manque. Le fermant, lui, est bien
  là, et les trois citations suivantes de la même note sont correctement
  encadrées. C'est donc un oubli de composition, non un usage.
* **Le numéro de section 55 sert deux fois.** Folio 63 : « 55. — La
  *adverbi di maniero* esas : » ; folio 66 : « 55. — L'*adverbi di
  afirmo, nego o dubo* esas : ». La numérotation reprend ensuite à 56 au
  folio 67, si bien que le second 55 est de trop et qu'aucun numéro n'a
  été sauté : c'est le premier qui aurait dû être 54 bis, ou le second
  56. Conservé tel quel.
* **Folio 68, note (1) : `dicernebla.Ol`.** Le point n'est suivi d'aucune
  espace. Mesuré à l'agrandissement, l'écart entre le point et l'`O` vaut
  ce qu'il vaut entre deux lettres d'un même mot.

## 9 bis. Les indices du composé ne sont pas ceux du relevé (folio 31)

Le contrôle 2 s'est mis à signaler, au folio 31, un « minim » manquant
sur une page inchangée depuis des semaines et vérifiée à l'œil. J'ai
d'abord consigné l'échec sans l'expliquer plutôt que d'élargir une
tolérance. Voici la cause, trouvée depuis.

`pdftotext` éclate un rang de tableau en plusieurs lignes de sortie : le
rang « Supereso maxim … de o ek » en donne trois. Le contrôle sait
recoller ces morceaux — mais il dépouillait d'abord les rangs de leurs
jetons d'une lettre (les débris d'accolade) **en indexant le composé par
les numéros du relevé**. Or dès que `pdftotext` ajoute une ligne,
`obtenu[k]` et `lg[k]` ne désignent plus la même matière : des lignes de
rang restaient non dépouillées, la réunion des morceaux échouait, et
l'écart remontait.

Ce qui a déclenché la panne est instructif : rien dans la page. C'est le
passage de `\VUinterligne` de 9,88 à 9,99 pt (§ 7 quater) qui a déplacé
« minim » de quelques dixièmes de point — assez pour que `pdftotext` lui
donne une ligne à lui. **Un réglage vertical juste peut faire tomber un
contrôle mal indexé, très loin de l'endroit qu'on retouchait.**

Le dépouillement se fait désormais au moment de la comparaison, là où
l'on sait à quel rang chaque ligne composée fait face. Le relevé, dont
les indices sont sûrs, se dépouille comme avant.

---

## 10. Limites connues

* **La fonte n'est pas celle de l'original.** XCharter reproduit la
  hauteur d'x, la chasse et donc les coupures de ligne, mais c'est une
  romaine plus large que le caractère luxembourgeois. Sur les lignes de
  titre, l'interlettrage calculé absorbe cette différence : la ligne a la
  bonne largeur et la bonne hauteur de capitale, mais la texture n'est
  pas identique. Visible sur le faux-titre.
* **Le cardage : deux réglages étaient faux, tous deux trouvés en
  composant les folios 58 à 63.** La dérive maximale est tombée de
  104 px (8,8 mm) à 28 px (2,4 mm), et le nombre de pages en échec de
  douze à **deux** : le feuillet 15 (page de titre de la première
  partie, 28 px) et le folio 22 (14 px, tout juste au-dessus de la
  tolérance). Voir § 7 quater.
* Les blancs qui encadrent un **titre courant** ne se déduisent pas : ils
  se mesurent. Aux feuillets 15, 16 et 28, les `\VUsaut` posés d'après
  l'apparat étaient trop courts de 22 à 46 px.
* Le contrôle 11 ne mesure pas les pages dont le nombre de lignes détecté
  diffère entre le fac-similé et le composé — huit pages à ce jour. C'est
  un défaut du découpage en lignes, pas de la composition, mais il laisse
  ces pages sans surveillance verticale.
* L'interlignage composé est de 41,0 px contre 40,0 px mesurés au folio
  11 (le mode sur l'ensemble du volume est 41). À revoir si l'écart se
  confirme sur un plus grand nombre de pages.
* Les ordonnées des pages d'apparat sont mesurées depuis le bord de
  l'**image** du scan, non depuis celui du papier : l'erreur est de
  l'ordre de 1 à 2 mm et varie d'une page à l'autre. Sans conséquence sur
  le texte courant, qui s'écoule depuis une marge fixe.
* **Le caractère des titres est un troisième dessin.** Le fac-similé
  emploie pour ses titres de section un gras étroit à empattements
  rectangulaires, distinct à la fois de son romain et du demi-gras de son
  texte. Aucune fonte disponible ici ne s'en approche : les titres sont
  composés dans le demi-gras étroit du texte, à la bonne largeur et à la
  bonne hauteur de capitale, mais le dessin des lettres diffère
  visiblement. Voir `controle/juxta/`.
* Un `Overfull \hbox` de 0,55 pt subsiste sur une ligne de note. Il est
  typographiquement négligeable et volontairement laissé visible : c'est
  le dispositif qui fonctionne.
* **Le contrôle 9 laisse quelques lignes non appariées par page** (3 à 8
  selon les pages) et le dit. Le contrôle 10 ne peut pas vérifier les fins
  de ligne sur deux pages, où le nombre de lignes composées détectées ne
  correspond pas au relevé, et il le dit aussi. Ces deux checks
  **dégradent proprement** : ils annoncent ce qu'ils n'ont pas pu vérifier
  au lieu de rendre un vert non mérité. C'est ce qui manquait.

* **Le comptage des lignes bloquait les contrôles 9 et 10.** Tous deux
  exigent que le nombre de lignes détectées sur le fac-similé et sur le
  composé coïncide, et sautent la page sinon. Le folio 15 en est là
  (35 contre 36). C'est **le défaut le plus grave du dispositif** : la
  vérification des fins d'alinéa a été écrite pour attraper la fuite de
  `\parfillskip`, et en la réintroduisant pour l'éprouver, elle ne l'a pas
  vue — parce qu'elle avait sauté la page. Les deux contrôles doivent
  apparier les lignes **par position verticale**, non par rang dans une
  liste. C'est le prochain chantier, et rien de sérieux ne peut avancer
  avant.
* **Le contrôle 9 saute encore certaines pages.** Il exige que le nombre
  de lignes détectées sur le fac-similé et sur le composé coïncide, et
  refuse de conclure sinon. Le folio 13 est dans ce cas (41 contre 42) :
  une ligne courte tombe d'un côté du seuil d'encre et pas de l'autre.
  C'est la faiblesse la plus gênante du dispositif, puisque **les pages
  qu'il saute sont exactement celles où les erreurs se cachent** : c'est
  en le voyant sauter le folio 12 qu'on s'est aperçu qu'il avait laissé
  passer six omissions d'enrichissement. À reprendre par un appariement
  des lignes par position plutôt que par simple comptage.
* Les marques de cahier n'ont pas encore été relevées systématiquement.
* L'OCR (`scan/ocr/`) n'a servi qu'au relevé de structure. Il n'est jamais
  utilisé pour le texte ni pour placer une coupure.

## 8 duoetricies. Une page entière au corps des notes, et une note sans filet

Le feuillet 208 (folio 204) est la page la plus singulière du volume, et
la géométrie le disait sans le dire : `pas -1.00 px`, `filet NON TROUVÉ`,
`exces : aucun`, quarante-six lignes là où les pages voisines en portent
quarante. Trois échecs d'outils sur la même page.

Les trois n'ont qu'une cause. **La note (1) ouverte au folio 203 déborde
et occupe le folio 204 tout entier.** La dernière ligne de note du 203
s'achève sur « ad omna », que la première ligne du 204 continue par
« ideo abstraktita ». Il n'y a donc pas de corps ordinaire sur cette
page : elle est composée d'un bout à l'autre au corps des notes.

Mesuré, non supposé : hauteur d'x de 15 à 16 px sur les quarante-six
lignes, contre 19 à 20 px pour le corps ordinaire du feuillet 207 et
15 à 16 px pour ses notes ; pas des lignes de base 33,76 px = 8,13 pt de
bout en bout, contre 41,5 px au corps ordinaire.

Ce qui rendait `pas -1.00` : le détecteur mesurait `y0`, le sommet
d'encre, qui saute de dix pixels selon les hampes de la ligne. Sur une
page dont toutes les lignes ont le même pas, ce bruit suffit à empêcher
le calcul. **La ligne de base, elle, était stable** — `outils/lignesbase.py`
existait déjà pour cette raison, mais le calcul du pas ne s'en sert pas.

**Et il n'y a réellement pas de filet.** Cherché au pixel : aucune encre
entre y=1688 et y=1735, quand celui du feuillet 207 se lève net à 213 px.
Le compositeur n'avait rien dont il eût dû distinguer sa note (\*) : la
page était déjà tout entière au corps des notes. C'est la seule page du
volume dans ce cas.

Deux macros neuves, toutes deux minimales :

* `\VUnotes` prend un **argument optionnel**, la largeur du filet. À
  `0pt` le filet disparaît sans que rien ne bouge : `\rule` garde sa
  hauteur de 0,4 pt, donc le blanc qui suit reste celui d'une page à
  filet, ce qui est bien ce que montre le fac-similé.
* `\VUpageNote{8.13pt}` compose la page entière au corps des notes.

Une **ligne manquait à la géométrie** : « bela. », 65 px de large, sous
le seuil du détecteur. C'est la panne connue des lignes très courtes, et
elle s'est trouvée ici par l'écart de 107 px entre deux lignes — le même
écart qu'aurait laissé un filet, ce qui aurait pu tromper.

### Ce que l'argument optionnel a cassé, et que les contrôles ont dit

Ajouter un argument optionnel à une macro déjà relevée par
`outils/controles.py` casse le relevé en deux endroits, et le contrôle 2
l'a annoncé aussitôt : `releve : [0pt]145.97mm(*) Se on postulas...`.
`deplace_notes()` sautait deux groupes obligatoires sans regarder s'il y
avait un crochet devant. Corrigé. `\VUpageNote` a fait de même à sa
manière : `releve : 8.13pt` comme première ligne du folio 204 — la macro
manquait à la table `MUETTES`.

Deux pannes du même genre, toutes deux **trouvées par le contrôle et non
par la lecture**. Une macro neuve qui ne compose pas de texte doit être
déclarée muette le jour où on l'écrit, pas le jour où le contrôle proteste.

## 8 teretricies. Deux sortes de guillemet simple, et un blanc de note plus large

Le fac-similé emploie **deux sortes distinctes de guillemet simple**, et
il a fallu deux releveurs travaillant en parallèle pour s'en apercevoir :
chacun avait vu la sienne, et ni l'un ni l'autre ne pouvait savoir que
l'autre existait. Vérifié à ×16 :

* folio 199 — un **trait vertical droit**, incliné, sans panse : ce n'est
  pas l'apostrophe du volume (celle de `L'amantu`, en virgule à tête
  bulbeuse, est sur la même ligne pour comparaison). On l'écrit
  `\textquotesingle{}`.
* folio 201 — une **vraie virgule culbutée** ouvrante et son apostrophe
  fermante. On les écrit `` ` `` et `'`.

Le contrôle 2 a immédiatement protesté sur les deux pages, pour deux
raisons opposées : le relevé effaçait `\textquotesingle`, macro sans
argument que rien ne prenait en charge, tandis que pdftotext rend la
virgule culbutée par une apostrophe droite. D'où une table `LITTERALES`
— les commandes sans argument qui composent pourtant un caractère — et la
normalisation de l'accent grave.

Sur le folio 206, le **blanc entre le filet et la première note est plus
large qu'ailleurs** : 48 px au fac-similé, quand le feuillet 209 en donne
27 et que `\VUsautFilet` en pose 19. Le filet, lui, est bien à sa place
(y = 1744, 213 px, vérifié à l'œil et par `outils/filet.py`). On a donc
ajouté le surplus **dans** le bloc de notes, plutôt que de descendre le
filet de 20 px pour caler le texte : le filet est visible, on ne le
déplace pas pour rattraper autre chose.

Enfin, le `499` du folio 200, que le releveur donnait en italique, est
**romain** : aucune inclinaison à ×6 face au `II,` romain qui le précède.
Une lecture d'agent qui se donne pour tranchée peut ne pas l'être ; la
juxtaposition à ×6 coûte moins que la correction d'après coup.

## 8 quateretricies. L'astérisme était faux depuis six lots, et rien ne l'a dit

La macro `\VUasterismo`, écrite au folio 186, empilait ses deux rangs :
un `\vskip`, la première `\hbox`, un second `\vskip`, la seconde `\hbox`.
Or **une `\hbox` contenant un astérisque a la hauteur de l'astérisque** —
29 px au corps courant — qui s'ajoutait aux 34 px du `\vskip`. Les deux
rangs tombaient à 63 px l'un de l'autre là où le fac-similé les met à 21.
L'ornement s'étalait sur trois interlignes au lieu d'un.

L'erreur est du même genre que celle de l'astérisme lui-même trois lots
plus tôt (§ 8 duodetricies) : **une boîte qu'on croit sans hauteur en a
une**. Elle a duré six lots.

**Pourquoi rien ne l'a dit.** Les deux rangs de l'astérisme sont trop
maigres pour le détecteur de lignes du fac-similé : la page comptait donc
une ligne composée de plus que le modèle, et le contrôle 11 la sautait —
en le disant, mais en la sautant. C'est exactement la faiblesse que ce
fichier nomme depuis le début : **les pages qu'un contrôle saute sont
celles où les fautes se cachent.** Le contrôle 2, lui, échouait bien sur
le folio 186 depuis le début, mais sur une ligne voisine, ce qui donnait à
son échec l'air d'un désaccord de lecture et non d'un défaut de
composition.

Chaque rang est maintenant dans sa propre boîte de hauteur nulle, à son
ordonnée propre, comme le font déjà `\VUcentreA` et `\VUsignature` :
aucune des deux ne peut plus pousser l'autre. Mesures reprises sur les
**deux** astérismes du volume, feuillets 190 et 211 : rang haut à y = 483
et 1434, rang bas à y = 503 et 1455 — 20 et 21 px, un seul et même
ornement. L'argument de la macro devient l'ordonnée du rang **supérieur**.

Bien posé, l'astérisme se prend une ligne à lui dans `pdftotext`, ce qu'il
ne faisait pas tant qu'il chevauchait le texte. `lignes_pdf()` écarte donc
maintenant les lignes faites de seuls astérisques, comme elle écartait
déjà les lignes d'un seul caractère. **Les deux échecs du contrôle 2 aux
folios 186 et 207 sont tombés du même coup** : le premier était ouvert
depuis l'introduction de l'ornement.

## 8 quinetricies. La cinquième cause de « filet introuvable »

Au feuillet 213 le filet est parfait — y = 1372, 214 px, calé sur la
marge, franc à l'œil. Il était pourtant perdu : **dix pixels de crasse à
x = 1073, au milieu de la colonne**, portaient le « reste » à 10 pour un
seuil de 6. La marge `BORD`, posée trois lots plus tôt pour la tranche du
feuillet voisin, ne protège que du bord droit.

Le remède qui ne marche pas est le premier venu : relever le seuil du
total. Un total ne distingue pas dix pixels de saleté d'une ligne de
texte. **C'est la forme qui les sépare** — une ligne de texte donne
beaucoup d'encre en suites longues, une saleté un seul petit amas. On juge
donc désormais sur la taille du plus gros amas (≤ 12 px) et sur le total
(≤ 30 px).

Un premier essai ajoutait un critère d'**étendue** — l'écartement entre le
premier et le dernier pixel d'encre. Il a fait perdre les feuillets 93 et
194, où deux poussières isolées aux deux bouts de la colonne sont très
écartées et ne pèsent rien. Vingt-six feuillets témoins ont été passés
avant et après chaque version : c'est le banc d'essai qui a rattrapé
l'erreur, pas la relecture.

État du détecteur : **cinq causes de panne rencontrées, quatre corrigées**.
La cinquième — le faux filet du feuillet 199 — reste ouverte, et reste la
seule qui fasse mentir l'outil plutôt qu'échouer.

## 8 sesetricies. Deux pages sans note, et deux blancs de note plus larges

Le feuillet 212 **ne porte aucune note** : cherché au pixel sur toute la
hauteur, hors de la fenêtre de `outils/filet.py` et avec un seuil de
longueur abaissé à 60 px, aucun candidat. « Filet non trouvé » y est la
bonne réponse — c'est la première fois du volume.

Conséquence : la note (2) du folio 207, qui s'achève sur « p. 266, » sans
fermer sa parenthèse, **ne continue nulle part**. Elle est coupée dans
l'original. Conservée telle quelle.

Aux folios 206 et 210, le blanc entre le filet et la première note vaut
48 et 52 px, quand le feuillet 209 en donne 27 et que `\VUsautFilet` en
pose 19. Dans les deux cas le filet est bien à sa place, mesuré et vérifié
à l'œil. Le surplus a donc été ajouté **dans** le bloc, plutôt que de
descendre le filet pour caler le texte : le filet est visible, on ne le
déplace pas pour rattraper autre chose.

## 8 septetricies. Le hors-texte du folio 220, et une accolade qui n'existait pas

Le folio 220 porte deux hors-texte, et la géométrie n'en annonçait aucun :
34 lignes détectées pour 37 objets réels.

Les trois manquantes sont les **rangées de points** qui accompagnent
l'accolade verticale — six points de 5 px chacune, très loin sous le
seuil du détecteur. Elles ont été retrouvées par l'arithmétique, non par
l'œil : lignes de base 828,2 — 911 — 952 — 993 — 1075,8, soit des écarts
de 2, 1, 1, 2 pas exactement. La grille était intacte ; c'est le
détecteur qui ne voyait rien.

L'**accolade horizontale** de l'arbre généalogique est la seule du
volume, d'où `\VUaccoladeH`, posée comme les autres sans hauteur ni
profondeur. Le releveur a tranché son orientation et celle de l'accolade
verticale par une mesure et non à l'œil : à 4 px de large, l'œil ne
suffit pas. Il a relevé pour chaque rangée le milieu du trait et cherché
où tombe l'extremum, en **calibrant sur l'accolade connue du folio 31**.
Verdict : l'accolade verticale est ouvrante, pointe vers l'unique rangée
— ce que la page énonce trois lignes plus bas, « *la pinto devas turnesar
ad l'unika lineo* ». La page se vérifie elle-même.

### Ce que pdftotext fait d'une accolade horizontale

Elle se brise en morceaux, et l'extraction les éparpille : un `z` collé à
« Ludovikus » sur la ligne du dessus, et une ligne à eux, `}|      {`.
La règle du caractère unique, écrite pour l'accolade verticale, ne les
attrapait pas — ils sont deux. Le critère sûr reste **structurel** : une
ligne de ce volume porte toujours une lettre ou un chiffre ; la seule
exception est une rangée de points de hors-texte, qu'il faut garder.
`lignes_pdf()` écarte donc maintenant les lignes sans lettre ni chiffre
qui ne sont pas faites de points.

Le `z`, lui, était déjà traité : le contrôle 2 compare les rangs de
tableau sans leurs jetons d'une lettre, mécanisme écrit pour le folio 31.

Trois autres pannes du même genre, toutes trouvées par les contrôles et
non par la lecture : les accolades échappées `\{\}` que le relevé
effaçait alors que le texte les **cite** (folio 220) ; `\VUaccoladeH`
absente de `MUETTES`, dont l'argument se lisait comme du texte ; et les
contrôles 5 et 6 qui voyaient trois fautes dans les rangées de points,
faute de savoir qu'un rang de tableau n'est pas de la prose.

## 8 duodequadragies. Huit pages sans note, et le filet court qui échappe trois fois

Le lot a produit **huit pages sans aucun bloc de notes** — folios 212,
213, 215, 216, 219, 220, 221, 222. Pour chacune, « filet non trouvé »
est la bonne réponse et non une panne, et chacune a été vérifiée : le
balayage grossier y signale toujours des segments de 100 à 170 px, et
l'agrandissement montre toujours des lignes de texte soudées par la
fermeture morphologique. Un vrai filet mesure 210 à 216 px et se cale sur
la marge ; aucun de ces segments ne fait ni l'un ni l'autre.

En revanche le **filet court centré de fin de section** a échappé au
détecteur **trois fois** dans ce lot (folios 215, 217 et 222), comme il
avait échappé au feuillet 187. Le masque de glyphes le rejette : trop
large pour un caractère, trop court pour une ligne. On ne le trouve que
par l'écart entre deux lignes de base — 162 px au folio 217, 189 px au
folio 222, là où la liste d'excès ne signalait rien du tout.

C'est le pendant exact de l'astérisme du folio 212, caché dans un
intervalle valant exactement quatre pas. **Ce que le détecteur ne voit
pas ne produit pas d'excès** : l'absence d'excès n'est donc jamais une
preuve d'absence.

## 8 undequadragies. Le TABELO — une mise en page qui n'est celle d'aucune autre page

L'index analytique s'ouvre au folio 225 et ne ressemble à rien de ce qui
précède. Trois différences, toutes mesurées :

* **le corps est plus petit** — hauteur d'x de 16 à 17 px contre 21 px
  pour le texte courant, soit 10,2 × 17/21 = **8,26 pt** ;
* **l'interlignage est plus serré** — 40,94 px = 9,86 pt ;
* **chaque entrée porte un meneur de points** au pas de 17,25 px =
  4,16 pt, puis un numéro de page **calé au fer droit**.

D'où trois macros neuves : `\VUpageIndex`, `\VUindex` et `\VUindexNu`
(pour les têtes de rubrique, qui n'ont pas de points de conduite).

**La justification, elle, n'a pas changé.** La géométrie annonçait 976 à
980 px là où le volume en compte 1083, et c'était un **artefact de
`text_region`** : la colonne des numéros est séparée des points par un
blanc de 73 px, et le clippage de colonne la coupait net. Le releveur
l'a vu en mesurant l'encre lui-même au lieu de croire l'outil.

**Les points s'arrêtent tous à la même abscisse**, y compris devant un
numéro large comme « 46 e 51 » : ce n'est donc pas un blanc fixe après
les points, mais une **colonne de largeur fixe** où le numéro se cale au
fer droit. Écrit en blanc fixe — mon premier jet — « 46 e 51 » venait
manger ses propres points.

### Deux mensonges du détecteur de filet, coup sur coup

Aux folios 225 et 226, `outils/filet.py` a rendu une ordonnée là où il
n'y a **aucune note**. Au folio 226 on sait pourquoi : il a pris **le
meneur de points** de l'entrée « an » — une ligne d'encre horizontale de
900 px — pour un filet. C'est la même panne qu'au folio 195, mais par une
autre cause : le détecteur ne ment plus faute de candidat, il ment parce
que la page contient désormais des traits horizontaux qui n'en sont pas.

Les deux fois, c'est le releveur qui a tranché, en cherchant lui-même le
plus long segment horizontal de la page. Le folio 225 n'en porte qu'un de
155 px — un **filet centré, cinquième longueur du volume** après 90-100,
202 et 296 px.

### Ce que l'index a cassé dans les contrôles

Trois pannes, toutes annoncées par le contrôle 2 dès la première
compilation : `texte_nu` ne connaissait pas `\VUindex` et enchaînait les
vingt-six entrées du folio 225 **dans une seule ligne relevée** ; le
meneur de points du composé n'était pas normalisé ; et `\VUpageIndex`
manquait à `MUETTES`.

Le dépliage suit le modèle de `\VUrang` : chaque entrée devient une ligne
marquée comme rang de tableau. Les meneurs sont normalisés par un critère
qui se dit — **aucun texte du volume ne porte six points de suite**, le
plus long étant le « (...) » du folio 219, qui en a trois.

### Une erreur de pose à moi, et ce qu'elle a coûté

J'ai ajouté les macros de l'index **à la fin de `preambule.tex`**, c'est-à-dire
**après son `\endinput`**. Elles n'ont jamais été lues, et la compilation
a échoué sur « Undefined control sequence ». Le fichier se termine par un
`\endinput` depuis le début ; je ne l'avais jamais regardé, ayant toujours
inséré mes macros au milieu. Un `cat >>` sur un fichier qu'on n'a pas lu
jusqu'au bout ne vaut pas mieux qu'une supposition.

## 8 quadragies. Le détecteur perd un tiers d'une page, et la fenêtre du filet se referme

Le feuillet 234 a produit la panne la plus grave du détecteur de lignes
depuis le début du projet. La géométrie annonçait **vingt-six lignes pour
une page qui en porte quarante** : le bloc détecté s'arrêtait à y = 1300,
et les treize dernières entrées de l'index tombaient hors de lui. Les
bandes `scan/H234_*.png`, découpées sur ce même bloc, **ne les montraient
même pas** — un releveur qui s'y serait fié n'aurait pas pu les voir.

Ce n'était plus une ligne courte perdue, comme les six retrouvées jusqu'ici,
mais **un tiers de la page**. Et l'excès de 52,4 px que la géométrie
signalait au milieu du bloc était la somme de deux choses sans rapport :
une ligne entière sautée (40 px) et le blanc de rubrique (12 px).

Le compte indépendant — profil d'encre par rangée, sans aucun critère de
largeur — donne 42 bandes là où la géométrie en voyait 26. **C'est ce
compte-là qu'il faut faire sur toute page dont le nombre de lignes
surprend**, et non croire le fichier.

### La fenêtre de longueur du filet, enfin resserrée

`outils/filet.py` cherchait un trait de **140 à 470 px**. Cette largeur a
coûté trois fausses lectures, dont une qui a fait perdre une ligne
composée :

* feuillet 199 — un trait parasite de 154 px passait pour le filet et
  donnait 161,63 mm au lieu de 107,74 ; le bloc de notes, posé si bas,
  débordait la page ;
* feuillet 226 — un **meneur de points** de l'index, ligne d'encre
  horizontale de 900 px, était pris pour un filet de note ;
* feuillet 231 — les **empattements soudés** de la vedette demi-grasse
  « Konjuncioni : » formaient une plage continue de 185 px partant de la
  marge, et passaient les trois tests.

Or un filet de note est une **constante du volume** : mesuré sur les
vingt-six feuillets témoins, il fait de 201 à 246 px. La fenêtre est donc
ramenée à 195-260 px. Vérifié sur les témoins : aucun filet réel n'est
perdu, et **les deux faux tombent** — dont celui du feuillet 199, ouvert
depuis plusieurs lots.

C'était la quatrième panne du détecteur, la seule qui le faisait mentir.
Elle est close.

### La position n'emporte pas la graisse

Dans le TABELO, une entrée au fer n'est pas nécessairement en demi-gras :
au folio 227, **six lignes au fer sur dix sont en romain maigre**, et au
folio 230 une seule des quatre. Seules les têtes de section le sont. La
consigne de relevé le dit maintenant explicitement — c'est le genre de
règle qu'on croit tenir d'une page et qui se dément à la suivante.

### Un numéro trop large pour sa colonne

La colonne des numéros de l'index a été mesurée au folio 225, dont le plus
large est « 46 e 51 ». Le folio 229 porte « 107 e 110 », qui déborde, et
les points venaient courir **sous** lui : le contrôle 2 lisait
« 107..110 ». `\VUindex` distingue désormais les deux cas — un numéro
ordinaire garde l'arrêt constant des points, mesuré sur le fac-similé ; un
numéro surlarge les repousse de sa seule surlargeur.

### Une sixième longueur de filet

Le filet centré qui annonce la deuxième partie du TABELO mesure **178 px**,
longueur inconnue jusqu'ici : le volume en comptait déjà de 90-100, 155,
202 et 296. Il n'apparaissait dans **aucun excès** — l'intervalle qui le
porte vaut 186,5 px et la liste n'annonçait que les blancs des titres,
plus bas. Sixième filet manqué par le détecteur, sixième retrouvé par le
relevé.

## 8 unetquadragies. L'espace de travail a reculé de deux lots

Le conteneur est revenu à un état antérieur : le dépôt git avait perdu
ses deux derniers commits — **et son reflog avec** —, le fichier de
contenu s'arrêtait au feuillet 226, et `/tmp` avait été vidé. Ce n'était
pas une annulation que git pouvait défaire : les objets n'existaient
plus.

**Ce qui a sauvé le lot, c'est la copie déposée chez le commanditaire.**
Les cinq fichiers modifiés lui sont remis après chaque lot ; son
`contenu/20-parto2.tex` faisait 376 680 octets contre 356 804 dans le
conteneur. Les huit folios, les macros du TABELO, la prise en charge de
l'index dans les contrôles et la fenêtre resserrée du détecteur de filet
ont été repris **tels quels**, sans rien recomposer, et les onze échecs
d'avant la perte se sont retrouvés à l'identique — ce qui vaut preuve
que la copie était bien la bonne.

Trois choses à en retenir, dans l'ordre où elles coûtent :

1. **La seule sauvegarde qui a servi était ailleurs.** Un dépôt git local
   ne protège pas contre la disparition du dépôt. Depuis ce lot, un
   `git bundle` complet est déposé chez le commanditaire à chaque lot, à
   côté des fichiers de travail : il contient tout l'historique et se
   reclone d'une commande.
2. **Je l'ai découvert sur une erreur de compilation, pas en regardant.**
   J'avais empilé un lot neuf sur un dépôt amputé sans jamais vérifier
   son état. Un `git log -1` avant d'écrire aurait montré le recul.
3. **Ce qui vit dans `/tmp` ne vit pas.** Les scripts de travail, les
   géométries, le fleuron découpé : tout était à refaire. Ce qui doit
   survivre doit être dans le dépôt.

## 8 duoetquadragies. Les deux dernières pages sont composées hors du cadre

Les feuillets 237 et 238 — les opinions sur l'Ido, puis le catalogue de
la revue *MONDO* — ne suivent pas la mise en page du volume : hauteur d'x
de 15 à 17 px contre 21, pas des lignes de base de 33 px contre 41,45, et
**aucun folio imprimé**. Les deux vont de pair : ce sont des pages hors
frame, ajoutées à la fin.

`\VUinterlignePage` ne suffisait pas à les rendre, et l'échec est
instructif : elle pose bien un `\baselineskip` de 7,90 pt, mais **TeX ne
l'emploie que si les lignes ne se chevauchent pas.** Dès que l'interligne
demandé descend sous la hauteur naturelle des boîtes, il l'abandonne pour
`\lineskip`, et le pas composé remontait à 45 px là où le fac-similé en
donne 33. La page débordait de 25 mm et perdait sa dernière ligne. D'où
`\VUpageSerre`, qui met `\lineskiplimit` à `-\maxdimen` : le
chevauchement est voulu, il faut le dire à TeX.

Le feuillet 237 demande en outre 1614 px pour un bloc qui n'en offre que
1564 : sa page **monte plus haut que `\VUmargeSup`**. Faute de folio pour
la caler, les 9 mm de remontée sont pris sur le débordement mesuré et non
sur une lecture. C'est un ajustement, et il est écrit comme tel dans le
fichier de contenu.

**Quatre échecs restent ouverts sur ces trois pages**, tous du contrôle 2
et tous de même famille : quand les lignes se touchent presque,
`pdftotext` les fusionne, et la comparaison ligne à ligne perd son
appui — 27 lignes extraites pour 46 composées au feuillet 237. Le
contrôle ne dit pas que la page est fausse ; il dit qu'il ne sait pas la
lire. À reprendre par un appariement des lignes **par position
verticale** plutôt que par rang, ce que ce fichier réclame depuis le
début pour les contrôles 9 et 10.

## 8 teretquadragies. La page de titre, et une planche

Le feuillet 7 est la page de titre, et elle ne porte **pas une seule
ligne de texte courant** : dix éléments d'apparat, tous centrés sur un
même axe optique à moins de deux pixels près.

Le détecteur y a fait les deux fautes à la fois. Il a **perdu deux
lignes** — `LINGUO INTERNACIONA IDO`, dont les capitales de 77 px
dépassent son filtre de hauteur, et `DA`, large de 41 px — et il en a
**inventé six**, qui sont des artefacts de la trame de la similigravure.
C'est la première page du volume où il fabrique des lignes qui n'existent
pas ; jusqu'ici il n'en avait jamais rendu que de vraies, ou rien.

**La planche.** Un portrait photographique de l'auteur, en similigravure
encadrée d'un filet, 722 × 1066 px. Le cadre est incliné de 0,3 degré par
rapport à la composition : il appartient donc au cliché, il n'est pas
composé. Comme le fleuron du folio 232, la planche est **découpée du
scan** — c'est le second et dernier endroit du volume où la transcription
cesse d'être une composition pour devenir un fac-similé.

**Deux choses restent ouvertes sur cette page, et il faut les dire :**

1. **Les largeurs d'apparat ne sont pas calibrées.** Deux des lignes
   dépassent la justification au fac-similé — `LINGUO INTERNACIONA IDO`
   mesure 1164 px pour les 1083 du volume, mesuré trois fois — et
   `\VUcentre` compose un paragraphe : une ligne plus large que la mesure
   ne déborde pas, elle se replie. La boucle « mesurer le composé,
   corriger l'interlettrage » ne converge donc pas ici, et je l'ai
   arrêtée plutôt que de la poursuivre à l'aveugle. Il faut une macro qui
   pose une ligne d'apparat **sans mesure**, en débord assumé.

2. **La page n'offre aucun point de calage** : ni folio, ni ligne de
   corps. Ses ordonnées sont posées en flux sur les écarts mesurés, avec
   un premier blanc choisi pour que le bloc tombe où il tombe au
   fac-similé. C'est un ajustement, écrit comme tel dans le fichier.

## 8 quateretquadragies. Ce que le liminaire réserve encore

L'AVERTO (feuillets 9 à 12) est relevé et vérifié : quatre pages, dont la
dernière porte **deux signatures calées à droite** — `L. DE BEAUFRONT.`
puis `L. B.` — et un filet centré de 197 px en pied. La seconde signature
manquait à la géométrie, et le releveur a trouvé pourquoi : elle porte
769 px d'encre contre 6882 pour une ligne pleine, soit un rapport de
0,112 pour un seuil posé à 0,12. **Elle tombe à huit millièmes du
seuil** — le même cas que « lua, lia. » du feuillet 37, que le code
signale déjà en commentaire.

Reste à relever : les **couvertures et gardes** (feuillets 1 à 4 et 240),
qui portent beaucoup d'encre — de 132 000 à 603 000 pixels — et ne sont
donc pas les pages blanches que le relevé de structure annonçait ; le
**verso du titre** (feuillet 8, 57 000 px) ; et le **faux-titre de
première partie** (feuillet 13). Les feuillets 2, 14 et 239 sont, eux,
réellement blancs.

---

## Le volume est complet — 240 feuillets, 240 pages

Les onze feuillets qui manquaient ont été relevés et composés. Quatre
points du présent document étaient faux et sont corrigés ici.

**Les feuillets 1 et 240 ne sont pas des couvertures imprimées.** Ce
sont les deux plats d'un cartonnage d'éditeur en percaline brune à grain
maroquin, dont le titre est estampé à chaud à la feuille d'or. Le fond
médian vaut 56 en luminance : 99,8 % de l'image passe sous le seuil 140,
et aucun détecteur du projet ne peut y travailler. La dorure, très usée,
ne subsiste qu'en liseré au fond de la gravure, **plus clair que le
fond** — 4 283 px au-dessus de 150, soit 0,14 % de l'image. Le détecteur
qui marche est donc l'inverse de l'ordinaire : `L > 150`, puis rejet des
composantes de moins de 6 px. Le second plat est **nu** : aucune dorure,
aucun filet. Et le filet du premier plat **n'est pas orné**, contrairement
à ce que disait la section 3.1 : filet maigre droit à bouts francs,
vérifié à ×12 aux deux extrémités.

Le caractère des plats est **étroit** — chasse lettre à lettre 49,0 px
sur `KOMPLETA` et 48,8 sur `GRAMATIKO`, le `O` de `DETALOZA` mesurant
32 px de large pour 55 de haut (rapport 0,58 quand une romaine ordinaire
est vers 0,75). Il vaut environ 79 % de la largeur de XCharter, et il est
interlettré d'environ 100 millièmes. En posant, selon la règle du projet,
le corps sur la hauteur de capitale et l'interlettrage sur la largeur,
l'interlettrage sort négatif : la géométrie est juste, le dessin des
lettres ne l'est pas. Aucune romaine condensée n'est installée ici (uaq,
ugq, ptm, pbk essayées : toutes aussi larges ou plus larges à hauteur de
capitale égale). La percaline, son grain et l'or ne sont pas rendus.

**Le feuillet 3 est la couverture imprimée**, conservée à la reliure : le
volume porte donc les deux. Sa vignette — l'emblème de l'Ido, étoile à
six branches cerclée de la légende — est le troisième et dernier cliché
découpé du scan, avec le portrait du feuillet 7 et le fleuron du folio
232.

**Le feuillet 4 n'est pas un verso blanc** mais une page pleine de
43 lignes, « QUO ESAS IDO? », composée au pas des notes (33 px = 7,95 pt)
comme les annonces des feuillets 237-238. Sa convention d'enrichissement
est **inversée** par rapport au corps d'ouvrage : les mots ido en vedette
y sont en italique et non en gras. C'est cohérent — cette page est un
texte d'éditeur, non du corps du volume — et c'est conservé tel quel.

**Le feuillet 8** porte la KONSTATO de l'Akademio Idista. Sa page est
délibérément aérée : pas des lignes de base 13,89 pt contre 9,99 au corps
courant, **à corps inchangé**. Son bloc de signature n'est pas centré sur
la justification mais sur un axe propre, déplacé de 16,46 mm à droite,
constant à un pixel près sur les quatre lignes.

**Les feuillets 2, 14 et 239 sont vierges**, ce que confirment leurs
luminances moyennes (195, 193).

### Cinq macros nouvelles

`\VUfiletA` pose un filet à ordonnée absolue et à **épaisseur mesurée** —
`\VUornement` pose toujours 0,4 pt, ce qui suffit aux filets du corps
d'ouvrage mais non à ceux des plats et de la couverture, épais de 2 à
8 px. `\VUcaseA` pose deux éléments sur une même ligne de base, aux deux
fers d'une mesure donnée : le feuillet 3 en donne le seul exemple du
volume. `\VUcentreDA` centre sur un axe déplacé. `\VUimageA` généralise
`\VUplancheA` à un fichier quelconque. `\VUauFer` cale une ligne à droite
avec un recul mesuré, pour les deux signatures du folio 8.

### Ce que j'ai appris en composant l'AVERTO

Les relevés des feuillets 9 à 12 étaient justes, mais trois choses ont
demandé une mesure de plus.

L'**ordonnée des blocs de notes** a dû être recalée sur les lignes de base
des notes composées, par la méthode d'`outils/caler_notes.py` : 123,36 →
122,78 mm au folio 5, 132,67 → 133,14 au 6, 146,14 → 147,07 au 7. Le
relevé du filet est bruité de 1 à 3 mm selon le seuil ; les lignes de
base, elles, se mesurent bien.

Les **deux blancs de signature du folio 8** valent 23 et 41 px. Sans eux
la page perdait 64 px sur ses dix dernières lignes. Ils n'étaient pas
dans le relevé parce que le détecteur avait perdu la signature `L. B.` —
769 px d'encre contre 6882 pour une ligne pleine, soit 0,112 pour un
seuil posé à 0,12 : elle tombe à huit millièmes du seuil.

Le **corps et l'interlettrage du titre « Averto »** : 15,66 pt pour 45 px
de capitale, −105 d'interlettrage pour 148 px de largeur, obtenus par
itération au pixel. C'est le seul titre du volume qui ne soit pas en
capitales.

### LA PANNE LA PLUS COÛTEUSE DE CETTE SESSION : LE MAUVAIS MOTEUR

Je compilais à l'**xelatex**. Le volume se compile au **pdflatex**
(`komp.mk`). Sous xelatex, microtype désactive le tracking **en silence**
— il émet bien deux avertissements en tête de journal, « The tracking
feature only works with pdftex » et « Letterspacing currently doesn't
work with xetex », mais rien ensuite : toutes les lignes d'apparat
sortaient à leur largeur naturelle, et j'ai passé plusieurs itérations à
chercher des interlettrages qui ne pouvaient rien changer. C'est la même
famille de panne que le détecteur de filet qui ment : un outil qui échoue
franchement coûte moins qu'un outil qui échoue en silence.

**Toujours vérifier le moteur avant d'ajuster une largeur.** Une fois
sous pdflatex, les neuf lignes du feuillet 7 et les trois du feuillet 5
ont convergé en trois itérations : écart maximal 2 px sur 1153.

### La page de titre était fausse, et le flux en était la cause

Le premier état du feuillet 7 était posé **en flux**, avec un blanc de
tête choisi à l'œil, faute de folio et de ligne de corps où s'accrocher.
La comparaison du rendu au fac-similé a montré que **chaque blanc y était
trop court**, la page se comprimant de 139 px du haut vers le bas.

Elle est reprise en ordonnées **absolues** :

    ordonnée = (haut_des_capitales − bord_du_papier) × 25,4/300 + C

où C = 5,84 mm est la part de la marge de tête que la numérisation rogne.
C n'est pas un chiffre libre : il se mesure sur les pages de texte, où la
première ligne de corps tombe par construction à `\VUmargeSup`, par
C = 24,30 − (y_ligne − y_papier) × 25,4/300. Médiane 5,84 mm sur 33 pages,
écart-type 1,5 mm hors pages de titre. Un releveur l'a recalculée
indépendamment sur 34 pages : 5,82 mm, écart-type 1,15. C'est la seule
grandeur approchée de ces pages, et elle porte sur la position d'ensemble,
non sur les écarts internes, qui sont mesurés au pixel.

Le haut des capitales du fac-similé doit être corrigé de l'étalement de
l'encre : (hauteur_fac − hauteur_composé)/2, soit 0,5 à 6 px selon le
corps.

**La planche du feuillet 7 comprenait sa légende**, qui était donc
composée deux fois. Elle est recoupée à `rot[636:1707, 328:1054]`.

### Une réserve enregistrée, non vérifiée : le feuillet 119

Le releveur du feuillet 13 soutient, mesures à l'appui, que le
**feuillet 119 est posé 7,7 mm trop haut**. Ses ordonnées sont les
`y × 25,4/300` bruts d'`apparat.py`, ce qui suppose que la première rangée
du recadrage soit le bord du papier ; sur la prise dont il sort, la
rangée 0 est déjà du papier (moyenne 191) et le bord n'est pas dans
l'image. Mesuré sur le feuillet 118, même prise : sa première ligne de
corps est à y = 196 px alors que la page composée la met à 287, soit
91 px = 7,7 mm de marge de tête coupés. Le contrôle 11 ne peut pas le
voir : il retire le décalage constant, et il saute de toute façon les
pages de moins de six lignes.

**Le feuillet 119 n'a pas été touché.** La réserve est enregistrée ici ;
elle demande sa propre vérification, et si elle se confirme, les mêmes
soupçons pèsent sur les feuillets 5 et 13, qui suivent le même précédent.

### Contrôles ouverts

Aux onze anciens s'ajoutent : le feuillet 12, dont la dernière ligne de
corps tombe à 12 px de sa place pour une tolérance de 11 — l'excès de
8,5 px que le fac-similé porte devant elle est plus probablement du bruit
de détection qu'une conduite du compositeur, et je ne l'ai pas écrit ; et
le feuillet 4, dont la composition serrée défait le découpage en lignes
des deux côtés à la fois, de sorte qu'il a fallu le caler sur sa dernière
ligne (qui tombe au pixel) plutôt que ligne à ligne.

---

## Les clichés sont détourés, et la reliure sort du volume

**Les trois clichés découpés du scan étaient posés opaques**, avec leur
carré de papier autour. Le pire était le fleuron du folio 232, qui
n'était même pas un gris : le fichier avait été tiré du masque de
glyphes (`gm`) et non de l'image, si bien que le fond était **noir** et
l'ornement clair — un rectangle noir au bas de la page.

Ils sont tous trois recoupés du scan brut désincliné et pourvus d'une
**couche alpha** : l'encre est noire, le papier transparent, et le blanc
de la page compose le fond. Deux traitements, parce que les objets sont
de deux natures :

- **trait** (fleuron du folio 232, vignette de la couverture) : seuil
  d'Otsu, puis `alpha = (papier − pixel) / (papier − encre)` où les deux
  bornes sont les moyennes des deux classes. Les histogrammes sont
  franchement bimodaux — la vignette a son encre entre 0 et 74 et son
  papier entre 143 et 218 — de sorte que le grain de la couverture, très
  grossier, devient complètement transparent sans que le noir du disque
  s'éclaircisse. Un premier essai à `médiane du bord ± k × écart-type`
  laissait justement le disque à mi-teinte : sur un support aussi
  moucheté, le bruit du bord n'est pas la bonne mesure.
- **similigravure** (le portrait du feuillet 7) : rampe linéaire du
  niveau du papier mesuré sur les trois pixels du bord jusqu'au noir. La
  demi-teinte doit garder sa gamme ; seule la marge de papier autour du
  cliché devient transparente.

Le recoupage du fleuron a changé sa largeur (209 px au lieu de 215) :
`\VUfleuronLargeur` passe de 17,19 à 17,70 mm pour que l'encre retombe
sur ses 203 px. Vérifié : 204 px composés.

**La reliure ne fait plus partie du volume.** La transcription commence
et finit à la **couverture imprimée**, papier vert — feuillets 3 et 4 en
tête, 237 et 238 en queue. Les feuillets 1 et 240, les deux plats du
cartonnage en percaline brune à titre doré, et les feuillets 2 et 239,
les gardes qui les doublent, sont relevés et décrits plus haut mais ne
sont plus composés : ils appartiennent à l'exemplaire, non à l'édition.
Le volume fait donc **236 pages**.

Le papier de la couverture se reconnaît à la mesure : RVB médian
177/163/139 aux feuillets 3 et 4, 177/169/152 et 176/175/161 aux 237 et
238, contre 237/210/184 au papier du corps d'ouvrage.


---

## Trois retouches, et une mesure qui manquait au volume

**Le titre de la couverture était comprimé, et pour une raison de
caractère.** Sur le feuillet 3, la largeur de lettre du titre vaut
**0,63 de la hauteur de capitale** (34 px pour 54) ; XCharter au même
corps en donne **0,943**. En posant, selon la règle du projet, le corps
sur la hauteur de capitale et l'interlettrage sur la largeur de ligne,
la géométrie tombait juste mais l'interlettrage devait descendre à −138
pour rentrer : les vingt-cinq lettres se soudaient en trois amas, là où
le fac-similé en montre vingt-sept séparés par trois pixels de blanc.

D'où `\VUetroit`, qui comprime horizontalement de 0,668 et rend à
l'interlettrage une valeur positive (+112). Résultat : 998 px pour 995
visés, 25 amas distincts, largeur de lettre 33 px pour 34 mesurés.
**La compression déforme le dessin des lettres : c'est un choix, non une
mesure**, et il n'est pris que là où les lettres se touchent. La ligne
`LINGUO INTERNACIONA`, dont le rapport vaut 0,87 contre 0,94, n'en a pas
besoin et n'y est pas soumise.

**La vignette gardait le carré de son découpage.** Le détourage par
seuil rendait bien le grain de la couverture transparent, mais les
angles conservaient assez d'alpha pour dessiner un carré autour du
disque. Le disque est maintenant ajusté (centre et rayon pris sur la
plus grande composante fermée : 120 px = 20,3 mm) et un **masque
circulaire** adouci sur 1,5 px annule tout ce qui est hors du cercle.
Alpha nul aux quatre coins, vérifié.

### La couverture est composée sur une mesure plus large que le volume

C'est ce que le débordement du dernier feuillet révélait, et c'est une
mesure qui manquait au projet. Les lignes pleines du feuillet 238
mesurent **1172 à 1210 px (99 à 102 mm)** quand la justification du
corps d'ouvrage vaut **1083 px (91,7 mm)**. Les lignes qui suivent le
titre débordent donc la marge de droite **au fac-similé même** : ce
n'est pas un défaut de composition.

Ce qui l'était : ma ligne courait à 1225 px, jusqu'au bord du papier.
Son interlettrage est calé sur les 1172 px mesurés — 1180 composés, bord
droit à 1323 px au lieu de 1367 sur une page large de 1371.

**Réserve nommée** : la mesure de la couverture n'est connue qu'à
quelques millimètres près, le grain du papier vert brouillant le bord
des lignes. Les feuillets 3, 4, 237 et 238 sont tous concernés ; seul le
238 a été recalé.

### Les vingt-trois débordements du volume, mesurés

Après correction, en millimètres : 4,9 — 3,9 — 2,4 — 1,5 — 1,2 — 1,1 —
1,1 — 0,9 — 0,8 — 0,7 — 0,7 — 0,6 — 0,6 — 0,6 — 0,5 — 0,5 — 0,5 — 0,4 —
0,4 — 0,4 — 0,3 — 0,2, plus celui de 8,0 mm qui est la ligne de
couverture ci-dessus. **Huit dépassent le millimètre.** Les plus gros
sont sur les pages de couverture, dont la mesure est plus large ; les
autres, tous inférieurs à 1,5 mm, sont le débord ordinaire d'une ligne
justifiée dont le dernier mot ne rentre pas tout à fait. **Ils n'ont pas
été vérifiés un à un contre le fac-similé** : c'est un contrôle ouvert.

---

## Les blancs des titres : quatre corrigés, un relevé à faire

Le titre du folio 169 était serré des deux côtés. Mesuré : le fac-similé
laisse **124 px avant et 99 après**, la composition n'en donnait que
**53 et 31** — près de 6 mm manquants de chaque côté.

La cause est mécanique et se cherche à la grammaire du fichier : sur les
51 `\VUtitre` du volume, **quatre n'avaient aucun `\VUsaut` ni avant ni
après** — folios 130, 168, 169 et 172. Les quatre sont corrigés sur leurs
blancs mesurés, et retombent exactement sur le fac-similé (89/89, 90/90,
124/99, 99/99). Aucune page ne déborde.

**Mais un balayage des 51 titres en signale 23 hors d'une tolérance de
14 px (1,2 mm)**, dont plusieurs de plus de 100 px. Ce chiffre est à
prendre pour ce qu'il vaut : l'appariement du titre composé au titre du
fac-similé s'y fait au rang, non à la position, et sur les pages qui
portent plusieurs titres ou dont le détecteur perd une ligne, il apparie
faux — les écarts de +110 à +228 px des folios 215 à 232 en sont
probablement. Deux titres ne sont pas mesurables du tout.

**C'est donc un contrôle ouvert, non un verdict.** Ce qu'il faudrait :
apparier par ordonnée et non par rang, comme le demande déjà le contrôle
des pages composées serré, puis reprendre les titres un à un.

### Le second grief, horizontal, est de même famille que celui de la couverture

Au folio 169, le titre composé mesure 784 px pour 774 au fac-similé — la
largeur est juste. Mais ses lettres se soudent en **dix amas** avec 1 px
de blanc médian, parce que l'interlettrage doit descendre à −45 pour que
la ligne rentre : la capitale de XCharter est plus large que celle du
fac-similé, et l'interlettrage paie la différence. C'est exactement ce
qui a été mesuré et corrigé sur la couverture, où le rapport atteignait
0,63 contre 0,943. Ici l'écart est moindre et `\VUetroit` n'a pas été
appliqué — mais le remède existe, et le choix de s'en servir ou non
reste à faire titre par titre.

---

## L'appariement par ordonnée : l'outil est écrit, la reprise ne l'est pas

`outils/titres.py` remplace l'appariement au rang par un appariement à la
position. Deux choses ont dû être corrigées avant qu'il donne quoi que
ce soit de fiable.

**Les deux ordonnées n'étaient pas la même grandeur.** Du côté composé je
prenais le `yMin` de `pdftotext`, qui est le haut de la *boîte de fonte*
— constant d'une ligne à l'autre ; du côté fac-similé, le haut de
l'*encre*, qui monte ou descend de dix pixels selon que la ligne porte ou
non des ascendantes. Aucun décalage constant ne pouvait les apparier.
`PG.lines_of` est donc appelé **des deux côtés** : sur la page composée
rendue à 300 dpi et seuillée, et sur le fac-similé. Sur le feuillet 173
cela donne 38 lignes contre 37, et 31 paires.

**Le décalage vertical se trouve par vote**, non par hypothèse : on essaie
tous les décalages plausibles et l'on garde celui qui apparie le plus de
lignes à moins de dix pixels. Un titre n'est mesuré que si ses deux
voisins sont appariés eux aussi, et dans l'ordre.

### Ce que l'outil a immédiatement révélé, et qui m'était échappé

**Ma correction du folio 169 était trop forte de 2,1 mm.** Je l'avais
« vérifiée » en comparant un blanc mesuré sur les boîtes de fonte à un
blanc mesuré sur l'encre : les deux ne sont pas comparables, et le titre
se retrouvait 25 px trop bas alors que ses voisins étaient en place. Le
blanc avant passe de 5,97 à 3,85 mm et celui d'après de 5,79 à 7,91, de
sorte que le texte qui suit ne bouge pas. Le titre tombe maintenant au
même écart que ses voisins (34 px contre 34).

C'est la leçon à retenir : **une vérification qui compare deux grandeurs
de natures différentes ne vérifie rien**, et elle est plus dangereuse que
pas de vérification du tout, parce qu'elle rassure.

### Ce qui reste à faire

L'appariement est encore **glouton** : il attribue les paires dans
l'ordre des lignes composées et marque les lignes du fac-similé comme
prises, si bien qu'une ligne appariée tôt peut affamer sa voisine. Au
folio 169 le titre est correctement apparié mais ses deux voisins sont
déclarés « non appariés » pour cette seule raison. **Il faut un
alignement monotone** — une programmation dynamique du type Needleman
et Wunsch, qui impose que l'ordre soit respecté et choisit le meilleur
appariement global au lieu du premier venu.

Tant que ce n'est pas fait, le balayage des 51 titres rendra surtout des
« non établis ». **La reprise des titres n'est donc pas faite**, et le
chiffre de 23 titres hors tolérance du balayage précédent reste ce qu'il
était : un artefact d'appariement, à ne pas prendre pour un verdict.

---

## L'alignement monotone est écrit ; l'obstacle a changé de nature

`apparie()` ne procède plus au plus proche voisin libre mais résout
l'alignement en entier, par programmation dynamique (Needleman et
Wunsch). Deux propriétés que le glouton n'avait pas : **l'ordre est
imposé** — deux lignes ne peuvent pas se croiser — et **le choix est
global**, chaque paire étant retenue pour ce qu'elle vaut dans le
meilleur alignement, non pour son rang. Une paire rapporte
`TOL_APPARIEMENT − écart`, donc d'autant plus qu'elle est franche ; un
saut coûte 1, à dessein bon marché : une ligne manquante d'un côté est
un accident ordinaire du découpage, et mieux vaut la sauter que forcer
une fausse paire.

L'affamement a disparu. Au feuillet 173 : 31 paires sur 38 lignes
composées et 37 relevées, décalage 27 px trouvé par vote, et les écarts
des lignes appariées sont remarquablement stables — 30, 29, 34, 34, 34.

**Mais le verdict du folio 169 n'a pas changé, et pour une raison qui
n'est plus celle-là.** Autour du titre, les deux découpages ne comptent
pas le même nombre de lignes : la composition en a une que le relevé n'a
pas juste avant le titre, et le relevé en a une que la composition n'a
pas juste après. Ce ne sont donc pas les mêmes voisins, et le contrôle a
raison de refuser de comparer deux blancs qui ne mesurent pas la même
chose.

### Ce qui reste, précisément

Trois choses, dans cet ordre :

1. **Savoir laquelle des deux lectures a tort** sur ces lignes-là. Une
   ligne non appariée est soit une ligne que `PG.lines_of` invente sur la
   page composée, soit une ligne qu'il perd sur le fac-similé — c'est
   exactement le genre de panne que ce document recense depuis le début
   (lignes courtes sous 200 px perdues, lignes fantômes de la trame). Il
   faut regarder les deux images à ces ordonnées, et non arbitrer par le
   calcul.
2. **Assouplir la règle des voisins** : mesurer le blanc entre le titre
   et son plus proche voisin *apparié*, en défalquant les interlignes
   ordinaires qui les séparent, plutôt que d'exiger le voisin immédiat.
   Cela rendrait mesurables les titres dont un seul côté est net.
3. Alors seulement, **reprendre les 51 titres**.

**La reprise n'est toujours pas faite**, et le chiffre de 23 titres hors
tolérance reste sans valeur. Ce qui est acquis : deux causes d'erreur de
l'outil sont éliminées — les grandeurs incommensurables, puis
l'appariement glouton — et une sur-correction réelle a été retrouvée au
folio 169.

---

## Deux corrections, dont une qui annule une conclusion antérieure

### Le folio 195 : le titre tombait sur le filet

`SUBSTANTIVIGO DIL ADJEKTIVO.` chevauchait le petit filet centré qui le
surmonte. La cause est la règle déjà écrite dans ce document, et que
j'avais malgré tout enfreinte : **un élément posé à une ordonnée absolue
n'ouvre pas son propre blanc**. `\VUornement` pose le filet à 45,17 mm en
hauteur nulle — ordonnée juste, vérifiée à 45,22 mm par la mesure — mais
le flux, lui, ignorait qu'il devait lui faire place, et le titre venait
se loger dessus.

Le relevé de la page donne, une fois les deux repères ramenés au même
zéro (la première ligne de corps, à `\VUmargeSup`) : filet à 436, titre à
530, sous-titre à 600, corps à 678. La composition les mettait à 533,
537, 593 et 676 — le titre 93 px trop haut. Les blancs corrigés (3,30 →
11,17 mm avant le titre, 1,10 → 2,29 après), la page tombe juste de bout
en bout : titre 630/630, sous-titre 700/700, dernière ligne 1908/1909.

### La couverture n'est PAS composée plus large que le volume

**Ma conclusion précédente était fausse, et la cause mérite d'être
retenue.** J'avais mesuré les lignes du feuillet 238 à 1172-1210 px et
conclu que la couverture avait sa propre justification, plus large que
les 1083 px du volume — donc que le débordement était fidèle.

Ces largeurs venaient du **grain du papier vert**, qu'un simple seuillage
compte pour de l'encre : le bord des lignes s'en trouvait gonflé d'une
centaine de pixels. Reprises avec `PG.lines_of`, qui travaille sur un
masque de glyphes et non sur un seuil, les mêmes lignes donnent une
largeur maximale de **1108 px** et une médiane de **1047**, pour une
justification de 1083. La couverture est donc composée sur la mesure du
volume, et les deux lignes qui suivent le titre n'avaient aucune raison
de déborder. Leur interlettrage est calé sur les 1079 et 1046 px
mesurés ; la première passe de 1225 à 1086 px.

C'est la deuxième fois dans ce chantier qu'une mesure prise au seuil sur
un papier sale conclut de travers — après le filet de note du feuillet
199. **Sur les papiers teintés et grenus, seul le masque de glyphes
mesure quelque chose.**

Reste un écart : la ligne `Redaktero...` tient 1085 px pour 1046 mesurés,
et l'interlettrage ne la réduit plus — ses petites capitales n'y sont pas
soumises. 3,3 mm de trop, dans la page ; non résolu.

---

## L'étroitesse des titres : une panne systématique du volume

`KONSTATO.` (folio 4) était composé en **un seul amas de 174 px** là où le
fac-similé en montre sept, pour 216 px. `Averto` (folio 5) était dans le
même cas. Aucun contrôle de largeur ne pouvait les voir : leur largeur
était « juste ».

La cause est dans la règle même du projet. Le corps se pose sur la
hauteur de capitale, l'interlettrage sur la largeur de ligne : cela donne
toujours la bonne géométrie d'ensemble, **et cela ne dit rien du dessin
des lettres**. Quand le caractère du fac-similé est plus étroit que
XCharter, l'interlettrage doit devenir négatif pour que la ligne rentre,
et les lettres se soudent. Le mal est d'autant plus grand que le titre
est court : moins il y a de blancs pour absorber la différence, plus
chacun est écrasé.

`outils/etroitesse.py` mesure, des deux côtés, la **largeur de lettre
rapportée à la hauteur de capitale**, et compte les **amas** — deux
lettres qui se touchent n'en font qu'un.

### Ce que le balayage des 51 titres a rendu

**38 titres sont serrés**, 6 non établis, 7 sains. Sur les 20 dont les
lettres composées tiennent encore leur rang — les seuls où le facteur se
mesure — il vaut **0,857 de médiane, entre 0,758 et 0,905**. Sur les 18
autres les lettres sont déjà soudées : le nombre d'amas les dénonce, mais
la « largeur de lettre » qu'on y mesure est celle d'un amas de deux ou
trois lettres, et le facteur qu'on en tirerait est absurde — 0,208 au
folio 217, 0,380 au folio 11. L'outil le dit maintenant au lieu
d'imprimer un chiffre.

**Le caractère de titre du volume est donc environ 14 % plus étroit que
XCharter**, et cette différence se paie depuis le début en interlettrage
négatif. C'est le même fait que sur la couverture (facteur 0,668, un cas
extrême) et sur les plats de la reliure.

### Les deux titres corrigés

`KONSTATO.` : `\VUetroit{0,793}` et interlettrage +119 — 215 px pour 216
mesurés, **neuf amas** comme au fac-similé, lettres de 23 à 24 px pour
23 relevés. `Averto` : `\VUetroit{0,822}` et interlettrage −8 — les six
lettres tombent à 37, 25, 22, 22, 17, 25 px pour 37, 25, 20, 21, 16, 23
au fac-similé.

### Ce qui reste

Les 36 autres titres serrés ne sont **pas** corrigés. Chacun demande son
propre facteur — pris sur ses lettres quand elles sont séparées, sur la
médiane du volume quand elles sont soudées — puis une résolution de
l'interlettrage par itération, comme les deux ci-dessus. C'est un lot,
pas une retouche. Six titres ne sont pas localisés du tout par l'outil et
demandent d'abord ce diagnostic-là.

**Rappel de méthode, deux fois vérifié dans ce chantier :** `\VUetroit`
déforme le dessin des lettres. C'est un choix, non une mesure, et il ne
se justifie que là où les lettres se touchent.

---

## Deux additions modernes, et le folio 169 rattrapé une seconde fois

### Le folio 169, mesuré comme il fallait dès le début

Le titre avait trop de blanc dessous et pas assez dessus. Mesuré avec
`titres.py` — donc `PG.lines_of` des deux côtés — la composition donnait
88 px avant et 142 après pour 124 et 99 relevés. Blancs portés à 6,90 et
4,27 mm : la page rend 124 et 100. C'est la troisième reprise de ce
titre, et la première qui parte d'une mesure commensurable.

### Les signets du PDF

`contenu/90-signeti.tex` pose **57 signets** sur deux niveaux : les pièces
liminaires et les deux parties au premier, les 47 titres de section au
second, sous la partie qui les contient.

Ils sont écrits avec la primitive `\pdfoutline` de pdfTeX, **et non avec
hyperref**. Ce n'est pas un caprice : hyperref redéfinit `\parindent`,
`\baselineskip` et la mise en boîte, et ce volume a sa pagination gelée
au dixième de millimètre. La primitive, elle, n'écrit que dans le
catalogue du PDF. `goto page N` vise la page par son rang, sans ancre à
poser dans le texte — donc sans ajouter le moindre objet à la page.
Vérifié : 236 pages avant, 236 après, aucune ligne déplacée, aucun
`Overfull \vbox`.

Le texte des signets est réduit à l'ASCII, le catalogue PDF n'acceptant
que PDFDocEncoding ou l'UTF-16 ; les seuls caractères concernés sont les
chevrons, rendus par des guillemets droits.

### La marque cachée

Chaque page porte, en tête et invisible :

> Gilles-Philippe Morin kompris, skanis e direktis la transskribo di ca
> libro.

Elle est composée en **mode de rendu 3** (`3 Tr`) : le texte entre dans
le flux de la page, il est indexé, cherchable, et `pdftotext` le rend —
mais il n'est **pas peint**. Aucun pixel n'en sort, ni à l'écran à
n'importe quel grossissement, ni à l'impression. Ce n'est pas du blanc
sur blanc, qui se verrait en sélectionnant ou en changeant de fond :
c'est du texte que le moteur de rendu saute. Par surcroît, le corps est
de 0,4 pt et la boîte qui la porte est de hauteur **et** de largeur
nulles, de sorte qu'elle ne peut déplacer aucun élément.

Posée par l'environnement `VUpage`, elle est donc sur les **236 pages** —
compté, pas supposé.

**Conséquence à connaître pour les contrôles** : `pdftotext` rend
maintenant une ligne de plus par page. Les contrôles qui comparent le
texte extrait au relevé doivent l'écarter. Ceux qui travaillent sur
l'image — `titres.py`, `etroitesse.py`, tout ce qui passe par
`PG.lines_of` — ne la voient pas, puisqu'elle n'est jamais peinte.

---

## La page de lecture (`index.html`)

Le volume a maintenant, à côté du PDF, une page de lecture autonome sur
le modèle de celle du *Dicionario* : même palette, même fonte, même
bouton de téléchargement, interface en ido. Elle est produite par
`outils/html.py`, rejouable — deux exécutions donnent le même md5 — de
sorte qu'elle se régénère après chaque recomposition du volume.

**Ce qu'elle contient** : 49 chapitres, 1 231 alinéas, 408 notes toutes
rattachées à leur appel, 384 vedettes, 454 403 signes. Aucune ressource
réseau : un seul fichier de 780 ko, données comprises.

**La mise en page** : trois volets sur ordinateur — table des matières à
gauche, texte au centre, vedettes du chapitre à droite —, un seul volet
et deux tiroirs sur téléphone, barre de recherche collante en tête. Les
notes sont repliées et s'ouvrent au clic ; le folio paraît en marge et
ouvre `gramatiko.pdf` à la bonne page (page = folio + 2).

**Le texte est reflué, non fac-similé** : `\nl` devient une espace, `\cc`
recolle le mot coupé. C'est le contraire exact de ce que fait le PDF, et
c'est voulu — l'un sert à consulter le livre, l'autre à le lire.

### Trois pièges de l'extraction, notés pour la prochaine fois

**`\parplein` ne veut pas dire « l'alinéa continue ».** Sur ses 114
emplois, 65 sont en cours de page et suivis d'un nouvel alinéa : la
macro justifie la dernière ligne, elle ne dit rien de la suite. La marque
qui fait foi est `\VUcontinue` en tête de la page suivante.

**Le folio ne s'interpole pas « au dernier connu ».** Le feuillet 8
précède le premier folio imprimé du volume ; la règle naïve lui donnait 8.
On prend donc le folio imprimé le plus proche, avant **ou après**.

**Les mots coupés d'une page à l'autre** — dix-neuf dans le volume — ne
se recollent qu'en appliquant la règle TeX d'avalement des blancs après
un mot de contrôle, et en jetant le saut de ligne qui suit
`\begin{VUpage}`.

Le fichier `gramatiko.pdf` est une copie de `main.pdf` sous le nom que la
page attend.

### Le téléphone : un seul tiroir, et l'accolade rendue par ce qu'elle veut dire

Deux reprises après essai sur iPhone.

**Le bouton « Vedeti » est retiré du DOM sur téléphone**, non pas masqué :
il occupait une deuxième rangée dans l'en-tête. Les vedettes du chapitre
courant sont désormais dépliées **dans le tiroir « Materio »**, sous le
lien de ce chapitre. L'en-tête du téléphone ne porte plus qu'une rangée,
mesurée à 43 px au lieu de 85. Il y fallait une correction de plus : le
`flex-basis` de 260 px du champ de recherche, hérité du *Dicionario*,
poussait encore le champ sous le bouton.

**Les tableaux à accolades étaient illisibles à 390 px** — colonnes
dispersées, accolades seules dans leur case, points de conduite occupant
des cases vides. Le remède tient à ce que l'accolade *signifie* : un
groupement. Et ce groupement se **mesure** — `\VUaccolade{hauteur}{décalage}`
donne la hauteur de l'accolade et le déplacement de son centre ; divisée
par le pas des lignes, la hauteur livre le nombre de rangs rassemblés.
Le tableau est donc écrit deux fois dans la page, le CSS n'en montrant
qu'une : colonnes au-dessus de 900 px, groupes emboîtés en dessous.

Deux bogues sont tombés à cette occasion : les points de conduite se
collaient à l'accolade au folio 220 et y faisaient disparaître une
rangée, et l'arbre généalogique du même folio, marqué comme les autres,
se trouvait **masqué sur ordinateur** — il avait disparu sans que rien le
signale.

### L'accolade s'étire enfin — un tracé, deux orientations

Les deux imperfections que la reprise précédente laissait derrière elle
n'en faisaient qu'une, et le commanditaire l'a vue sur iPad, au
folio 220 : **l'accolade ne coiffait rien**. Le `{` du schéma de
l'`embracilo` était un glyphe d'une ligne posé à côté de trois rangées de
points de conduite — lesquelles sont ici le *contenu*, le livre
schématisant des lignes de texte par des points. Et l'accolade
horizontale de l'arbre généalogique — `Ludovikus` au-dessus de
`Petrus Paulus Ioannes Maria` — sortait en simple barre verticale entre
le premier nom et les autres, alors que le texte vient d'annoncer qu'elle
peut s'employer aussi horizontalement, dans les arbres généalogiques.

**Le glyphe d'une fonte ne s'étire pas.** Trois voies étaient ouvertes :

| voie | pourquoi elle a été écartée, ou retenue |
|---|---|
| `scaleY` sur le glyphe | allonge le fût mais étire aussi les courbes ; la pointe d'une accolade triplée de hauteur devient une tache, et la forme dépend de la fonte du lecteur |
| bords arrondis en CSS | quatre quarts de cercle et deux fûts, donc plusieurs éléments par accolade, dont les raccords se disjoignent dès que le navigateur arrondit une demi-décimale — et tout serait à refaire pour l'horizontale |
| **SVG en ligne** | **retenu** : un seul tracé, aucun raccord, la même mécanique dans les deux sens |

Le SVG porte `preserveAspectRatio="none"` — le dessin se plaque sur la
boîte exacte que le CSS lui donne, trois rangs de haut ou toute la
largeur d'une fratrie — et `vector-effect="non-scaling-stroke"`, sans
quoi le fût d'une accolade triplée serait trois fois plus gras que le
texte. L'attribut est posé **dans le balisage et non en CSS** : la
propriété CSS du même nom est plus récente que l'attribut de
présentation, et c'est sur un iPad que le défaut a été vu. Les deux
tracés suivent le fac-similé du folio 220 (`scan/pages/f0224.jpg`, encre
x 786-796 y 877-995 pour la verticale, x 524-1063 y 1339-1355 pour
l'horizontale) : une accolade maigre à pointe peu saillante, une
horizontale presque plate à spicule central.

**Ce qui donne sa boîte à l'accolade** est la mesure déjà relevée, non une
estimation : `\VUaccolade{hauteur}{décalage}` sert désormais aux deux
rendus, par une seule fonction `etendue()`.

* En **colonnes**, la case de l'accolade traverse ses rangs — un
  `rowspan` calculé — et le tracé s'y cale en absolu, du haut du premier
  rang au bas du dernier. C'est la seule manière sûre d'obtenir la
  hauteur exacte d'un groupe de rangs, qu'aucune mesure en `em` ne
  connaît.
* En **groupes**, le filet qui tenait lieu d'accolade a cédé la place à
  l'accolade elle-même, étirée par `align-self:stretch` sur toute la
  hauteur des membres, pointe en face du titre.
* Le groupe **à pointe en haut** — l'arbre généalogique — empile les
  trois mêmes pièces au lieu de les ranger : titre, accolade
  horizontale, membres. La boîte étant dimensionnée par son contenu
  (`inline-flex`), l'accolade prend exactement la largeur des noms
  qu'elle coiffe, et deux marges négatives lui rendent le léger débord du
  fac-similé — 45,63 mm d'encre pour 42 mm de noms.

**Trois pièges rencontrés en chemin**, tous vus à l'écran et non devinés :

1. **Une accolade ne peut pas partager sa case avec du texte.** Tant
   qu'elle la partageait — collée à gauche de « egaleso » au folio 31,
   des points de conduite au folio 220 — aucune case ne lui appartenait
   en propre, donc rien ne pouvait s'étendre. Elle prend donc une
   colonne, **à sa gauche** : dans tout le volume l'accolade précède ce
   qu'elle rassemble. Mais le reste du groupe demeure **une** colonne,
   sans quoi « Komparativo » et « relatanta », que l'accolade sépare de
   5,7 mm, se seraient rangés dans deux colonnes et le tableau du
   folio 31 aurait béé.
2. **Un contenu en position absolue ne compte pour rien dans la largeur
   d'une colonne.** `width` n'y étant qu'un vœu, la case tombait à
   **zéro** dès que le tableau du folio 31 se serrait, et l'accolade
   disparaissait entre 900 et 1000 px de fenêtre. La largeur est donc
   portée par les **blancs** de la case, que la mise en table ne peut pas
   réduire : le blanc de gauche fait la largeur du tracé, celui de droite
   l'écart à la colonne suivante.
3. **Une colonne de plus par accolade, c'est le tableau du folio 31 plus
   large de 50 px** — 404 px au lieu de 354. Sous 1000 px de fenêtre il
   débordait sur le volet de droite. Le seuil du passage aux groupes a
   donc été remonté de 900 à 1000 px — puis à **1200 px**, la marge
   s'étant révélée trop courte : voir plus bas, « le seuil se calcule ».
   `.larja` reste par sûreté un conteneur défilant, pour le lecteur qui
   grossirait assez le corps pour qu'un tableau passe encore.

**Vérifié par capture**, en clair et en sombre, à 1400, 1024 et 390 px,
plus un balayage de 320 à 1400 px : l'accolade a partout une taille
réelle, aucun tableau ne sort de sa colonne, et les trois seuls blocs du
volume qui changent sont les deux schémas du folio 220 et le tableau du
folio 31 — les 1 726 autres sont identiques à l'octet près.

Reste une imperfection, dite : l'accolade **fermante** du folio 31 —
celle de « de o ek » — n'ouvre aucun groupe, sa portée croisant celle de
l'accolade ouvrante ; sur écran étroit elle demeure donc une accolade en
ligne, haute d'une ligne. Elle est tracée par le même SVG, mais la boîte
d'une seule ligne est trois fois moins élancée que le dessin, qui s'y
écrase un peu.

> **Levée.** Voir « L'accolade fermante du folio 31 » ci-dessous.

### Six retours d'iPad : la marge, le seuil, et deux vedettes manquantes

Sixième passage de relecture, six points relevés par le commanditaire sur
son iPad. Le troisième est un changement de texte demandé ; les autres
sont des défauts.

**La folio mordait sur le volet de gauche.** Elle se pose *en dehors* du
texte, 3,6 em à sa gauche — 3,6 em de son corps à elle, 11 px, soit 40 px.
Le blanc de gauche du bloc n'en mesurait que 34 : dès que la colonne
centrale cessait d'être plus large que le bloc — sous 1 160 px, donc sur
tout iPad — la folio sortait du bloc et empiétait de 6 px sur la table des
matières. Le blanc de gauche loge maintenant la folio **et son air**
(58 px, soit 18 px de jeu), et la largeur maximale du bloc grandit
d'autant, 680 → 728 px, pour que la **justification du texte ne change pas
d'un point** sur ordinateur : 612 px de mesure avant comme après. C'est le
texte qui cède la place, non le volet — et seulement là où la place
manque.

**Le seuil entre les deux rendus se calcule, il ne se choisit pas.** Le
passage précédent l'avait posé à 1 000 px, mesure prise sur la largeur
*minimale* du tableau du folio 31. C'était trop court : ce qu'il faut,
c'est sa largeur **naturelle**, celle où aucune case ne se brise, et elle
vaut 430 px, plus 16 px de retrait. La colonne centrale offre
`min(728, largeur − 480) − 116`, d'où 1 042 px de fenêtre au strict —
*avec la fonte d'essai*. Le lecteur peut en avoir une plus large (la page
cherche Iowan, puis Palatino, puis Georgia), et un tableau qui déborde ne
déborde pas un peu : les rangées se brisent, les termes tombent sous les
termes, et l'accolade ne coiffe plus les rangs qu'elle vise puisque ces
rangs ont doublé de hauteur. C'est exactement ce que montrait la capture
reçue. Le seuil est donc porté à **1 200 px**, avec 150 px de marge :
aucun iPad en mode paysage n'atteint cette largeur — 1 194 px pour le plus
grand des onze pouces — et tous reçoivent donc le rendu en groupes, qui se
plie à toute largeur. **La grille redevient ce qu'elle doit être : un
supplément d'écran large, jamais un pis-aller.**

**Deux façons d'écrire une vedette que la détection ne lisait pas.** La
règle — « un alinéa qui s'ouvre par un passage en gras est une
sous-entrée » — est bonne ; elle lisait l'ouverture trop étroitement.

| ce qui manquait | ce que le fac-similé compose | ce qu'on lisait |
|---|---|---|
| le **numéro d'alinéa** ne compte pas | « 3. — **B** = *b* en l'Italiana » | rien |
| une vedette peut être **double** | « **e**, **o** apertita o klozita » | `e` |

Le volume ne numérote que le premier alinéa d'une suite : `3. — B` ouvre
l'article B exactement comme `c = c Germana` ouvre celui de c. Et
l'article du folio 11 traite les deux voyelles ensemble, les deux lettres
en gras, la virgule entre elles nue. Rien n'a été ajouté au texte : on lit
seulement plus loin dans la ligne que le fac-similé a composée. Le bouton
en chaîne se pose désormais contre la vedette **entière** — posé au
premier `</b>` venu, il se glissait entre le « e » et le « o ».

Le gain dépasse les deux cas signalés, et c'est le même défaut :
**367 vedettes au lieu de 322**. Le chapitre des prépositions, qui
numérote chacune de ses entrées, n'en listait aucune ; il rend maintenant
ses quarante-deux articles, de `Ad` à `Ye`.

**Le prix à payer, et il faut le dire : six ancres changent d'adresse.**
`#pronunco-dil-vokali-e` devient `#pronunco-dil-vokali-e-o`,
`…-konsonanti-e-digrami-m` devient `…-m-n` ; et comme le suffixe de
collision s'attribue *dans l'ordre du texte*, les nouvelles entrées `De`,
`Til`, `Ultre` prennent la place sans suffixe et repoussent d'un rang
celles qui l'occupaient. C'est le seul cas où la règle d'identifiant a
bougé depuis qu'elle est écrite, et la raison en est légitime — le
contenu dont l'ancre se déduit était mal lu — mais un lien copié vers
l'une de ces six adresses ne résout plus.

**Ce qui ne s'est pas reproduit.** Le surlignage du volet de droite était
donné pour décalé au chapitre des consonnes : cliquer `ch`, voir `z`
surligné. **Le défaut ne se reproduit pas sur le fichier courant**, dans
aucun des quatre chemins essayés — clic dans le volet, lien profond
`#…-ch`, tiroir du téléphone, défilement continu — pour les vingt-deux
vedettes du chapitre, à 1 400 comme à 1 024 px. La cause supposée ne peut
d'ailleurs pas jouer : le surlignage compare des **identifiants**
(`href === '#' + vedNun`), jamais des textes, et la brièveté des vedettes
n'y change rien. La capture venait donc, selon toute vraisemblance, d'une
version antérieure — ce que le commanditaire soupçonnait lui-même.

### L'adresse d'une section : une règle fondée sur le contenu

Chaque titre de chapitre et chaque vedette porte désormais, à sa droite,
un **bouton en chaîne** qui copie l'URL absolue de la section. Discret —
couleur `--sub`, révélé au survol sur ordinateur ; sur écran tactile
(`@media (hover:none)`) il reste visible et sa cible est portée à 44 px
par un pseudo-élément, qui grossit la zone sensible sans toucher à
l'interligne. Sur ordinateur le bouton est **absolu, dans la marge de
droite**, en vis-à-vis du folio qui est dans celle de gauche : il ne
prend donc aucune place dans le texte. En ligne, il aurait laissé un
trou de 21 px après chacune des 384 vedettes, visible même invisible,
puisque la justification l'aurait montré. *(Piège au passage : un
`inline-block` hérite du `text-indent` de l'alinéa et se l'applique à
lui-même — d'où le `text-indent:0` obligatoire.)*

La copie se fait en trois paliers, parce que la page s'ouvre souvent en
`file://`, où l'API du presse-papiers manque ou refuse :
`navigator.clipboard.writeText`, puis un champ temporaire avec
`document.execCommand('copy')`, puis, en dernier recours, l'affichage de
l'URL sélectionnée pour copie manuelle. La confirmation, « Kopiita »,
s'efface au bout d'une seconde et demie. Le bouton reste un **vrai
lien** : sans JavaScript il mène quand même à l'ancre, et le menu
contextuel du navigateur y offre « copier l'adresse du lien ».

**LA RÈGLE D'IDENTIFIANT — c'est le point qui compte.** Une ancre est
une adresse : elle est citée, mise en signet, collée dans une note. Elle
doit survivre à la recomposition du volume. **Rien de positionnel n'y
entre donc** — ni le rang de l'alinéa, ni l'ordre du fichier, ni le
numéro du chapitre : insérer un paragraphe au folio 12 les décalerait
tous. Elle se déduit du seul **contenu** :

1. **chapitre** → `ardoise(titre du chapitre)` ;
2. **vedette** → `ardoise(titre du chapitre)` + `-` + `ardoise(vedette)` ;
3. **collision** → suffixe `-2`, `-3`… attribué **dans l'ordre du
   texte**, la première occurrence restant sans suffixe.

`ardoise()` — le slug — fait ceci, et rien d'autre : minuscules,
diacritiques déposés (NFKD, plus une table pour `æ œ ß ø đ ł þ ð`), tout
ce qui n'est pas `[a-z0-9]` rendu en tiret, tirets fusionnés et rognés
aux deux bouts, coupure à 40 signes **sur un mot entier** — jamais au
milieu d'un mot, ce qui rendrait l'adresse indevinable. Ainsi
`PREPOZICIONI.` → `#prepozicioni`, et sa vedette `Til` →
`#prepozicioni-til`. Un **hachage** ferait aussi bien contre les
collisions, mais il donnerait une adresse illisible et, surtout, il
changerait entièrement à la moindre coquille corrigée ; le suffixe
numérique, lui, ne bouge que pour les entrées qui portent vraiment le
même nom. Les identifiants de note (`nt<feuillet>-<numéro>`) sont
**réservés d'abord**, pour qu'aucune ardoise ne vienne les leur prendre.

**Le contrôle d'unicité est programmatique**, et il se fait sur la page
**écrite**, non sur le registre : c'est le document qui porte les
adresses. `controle_ancres()` relit tous les `id="…"` du fichier produit
et l'outil s'arrête en erreur si l'un se répète. Il dit aussi, sans
échouer, ceux qu'une URL devrait encoder. Au dernier passage : **790
identifiants, aucun doublon**, quatre homonymes départagés par un
suffixe (`prepozicioni-til`, `adverbi-proxime`, `prefixi-des`,
`sufixi-il`). Deux exécutions rendent le même md5.

### Le portrait ouvre la page — et l'alpha sert de masque, non d'image

La page s'ouvre sur le portrait de l'auteur, planche du feuillet 7, avec
la légende du fac-similé et son folio en marge ; il paraît dans la table
des matières comme un chapitre, avant la KONSTATO.

**Le piège, et il ne se voit pas tant qu'on ne regarde pas :** le PNG du
scan est une similigravure à couche alpha — l'encre y est **noire**, le
papier **transparent**. Une balise `<img>` l'aurait rendu **noir sur
noir en mode sombre**. On n'en garde donc **aucune couleur** : le PNG
incorporé ne porte que l'**alpha**, et le CSS le pose en `mask-image` /
`-webkit-mask-image` sur un bloc dont le fond est `var(--enk)`. Le
portrait est alors de l'encre, comme le reste de la page, et suit le
thème. Vérifié sur capture dans les deux modes.

Deux mesures pour le poids, la page devant rester autonome : **650 px**
de large (le fac-similé en fait 726, et sa trame ne supporte pas d'être
réduite beaucoup plus) et **8 niveaux d'alpha** — la trame est un
*grain*, non un dégradé ; huit niveaux en sont indiscernables à l'œil et
divisent par quatre le poids du PNG, 194 ko au lieu de 730. Le PNG sort
en palette, les huit niveaux tenant dans un `tRNS` de huit octets. La
`data:` URI est écrite **une seule fois**, dans une variable CSS : la
répéter pour la propriété préfixée et la propriété nue coûtait 260 ko.
La page pèse 1,15 Mo.

*Conséquence assumée, et qui se voit :* la planche est une photographie
en demi-teinte, non un trait. En mode sombre, l'encre s'éclaircissant
comme celle du texte, le portrait se lit en **négatif**. C'est la suite
exacte du principe « le portrait est de l'encre » ; le retour au positif
demanderait de traiter la planche non comme de l'encre mais comme une
photographie sur papier, avec un fond clair maintenu dans les deux
modes. Le choix est ouvert.

### Le folio 224 était un addendum : il est remis à sa place

Le folio 224 (feuillet 228) ne porte qu'une phrase et deux articles.
L'original y annonce qu'il place là les deux prépositions **tra** et
**trans**, omises, et **qu'elles vont après *til*, p. 82**. Ce n'est pas
une section : c'est un rattrapage d'imprimeur, et **le livre dit
lui-même où son contenu appartient**. La page de lecture l'y porte.

Les deux articles gardent leur **folio 224** et son renvoi au PDF —
`gramatiko.pdf#page=226`, la règle du volume restant page = folio + 2 —
et paraissent **à leur rang dans le volet des vedettes** de PREPOZICIONI,
juste après les deux entrées `Til`. Le folio 224 ne forme plus de
section à part : le compte rendu de l'outil le vérifie et affiche
« 3 blocs remis après *Til signifikas…*, 0 bloc resté au feuillet 228 ».
Aucun texte ne s'y perd — la phrase de l'original est conservée telle
quelle, en tête du groupe déplacé ; la comparaison des mots de la page
avant et après ne montre aucune perte.

La page ne peut pas déplacer du texte sans le dire. Elle le dit en ido,
et **entre crochets**, comme toute intervention d'éditeur : « *La
originalo omisis ca du artikli e pozis li ye la fino dil volumo, sur la
folio 224 ; ca pagino redonas li al loko quan la libro ipsa indikas.* »

**Rien n'est en dur dans le déplacement** : la cible se retrouve par le
contenu — le chapitre qui porte le titre voulu, la **dernière** entrée
qui porte la vedette voulue (`til` court sur trois alinéas, et c'est
après le troisième que le volume renvoie). Si le volume est recomposé et
que le folio 224 disparaît, la fonction ne trouve rien à déplacer et ne
fait rien.

L'outil demande désormais **Pillow**, pour réduire le portrait et n'en
tirer que la couche alpha.

### Le portrait en mode sombre : une photographie n'est pas de l'encre

Le premier état donnait au masque la couleur du texte, `var(--enk)`, pour
que le portrait « suive l'encre » dans les deux modes. Le principe est
juste pour un trait — le fleuron, la vignette — et **faux pour une
demi-teinte** : en mode sombre le portrait paraissait **en négatif**,
cheveux et veston clairs, visage sombre.

La planche est donc traitée comme ce qu'elle est : une photographie
**posée sur du papier**. Le carton garde son fond clair et l'encre son
noir dans les deux modes ; en mode sombre la planche se détache sur la
page comme un tirage collé dans un livre. C'est la seule façon de la
garder positive.

À retenir : le même procédé — l'alpha en masque — sert deux objets de
natures différentes. Pour le trait, la couleur suit l'encre ; pour la
demi-teinte, elle ne le doit pas.

### Publier sur GitHub Pages : le fichier `.nojekyll`

GitHub Pages fait par défaut passer le dépôt par **Jekyll**, qui rend les
`.md` et interprète au passage la syntaxe de gabarits **Liquid**. Or
Liquid analyse le texte **avant** Markdown, donc **y compris dans les
blocs de code** : l'accolade ouvrante suivie d'un pour-cent qui termine la ligne
`\VUnotes{<ordonnée>mm}{` dans `outils/CONSIGNE-RELEVE.md` y passe pour
l'ouverture d'une balise et fait échouer la publication entière.

Le remède n'est pas d'échapper cette séquence — le dépôt n'a rien à
faire de Jekyll. Il ne publie pas un site de billets : il publie **un seul fichier
HTML autonome**. Un fichier vide nommé **`.nojekyll`** à la racine du
dépôt suffit à désactiver toute la chaîne, et GitHub Pages sert alors les
fichiers tels quels.

    touch .nojekyll && git add .nojekyll && git commit -m ".nojekyll"

Le fichier est versé au dépôt. Conséquence à connaître : `LISEZ-MOI.md`
ne sera plus rendu en page web — ce qui est bien, `index.html` étant la
page du volume.

### « Chefa vorto », non « vedeto »

L'interface disait « Vedeti dil chapitro ». C'était un faux ami de ma
part : j'avais transposé en ido le terme typographique français
*vedette* — le mot en tête d'un article — sans vérifier qu'en ido
**`vedeto` a le sens de sentinelle**, du français *vedette* militaire et
non de la vedette d'imprimerie. Le mot juste est **`chefa vorto`**.

Les libellés visibles et la prose des commentaires sont corrigés. Les
identifiants internes (`#vede`, `#vedlist`, `.ved`) sont laissés tels
quels : ce n'est pas de l'ido, et les renommer décrocherait le
JavaScript sans rien gagner. **Les URL ne sont pas touchées** : elles
sont bâties sur le titre du chapitre et le mot lui-même, jamais sur le
nom de la catégorie — aucun lien déjà copié ne se rompt.

À retenir pour la suite : le vocabulaire de l'interface est en ido, et
un terme technique français ne s'y transporte pas par simple suffixe.

### La marge de défilement doit se mesurer, non se supposer

Les ancres portaient une `scroll-margin-top` fixée en dur : 112 px, et
215 px sous la règle du téléphone. Elle mentait dès que l'en-tête collant
changeait de hauteur. **Sur iPad, le titre passe sur deux lignes sans que
la règle du téléphone s'applique** : l'en-tête y mesure 133 px, et le
haut de la section visée disparaissait sous la barre de recherche.

La hauteur est désormais mesurée et déposée dans `--kapo` — au
chargement, au redimensionnement, au changement d'orientation, et **après
le chargement des fontes**, une fonte à empattements plus haute que la
fonte de secours pouvant faire passer le titre sur une ligne de plus. Les
valeurs en dur ne servent plus que de secours avant que le script ait
tourné. Vérifié à 1500, 1024, 768 et 390 px : la section visée tombe
toujours à 12 px sous la barre.

### Si « Deskargar » rend un fichier nommé `gramatiko.pdf.html`

Ce nom est la signature d'une **page d'erreur HTML téléchargée sous le
nom du PDF** : l'attribut `download` enregistre les octets reçus, et le
navigateur ajoute l'extension correspondant au type renvoyé par le
serveur. Autrement dit, `gramatiko.pdf` n'est pas à l'adresse demandée —
le lien est juste, le fichier manque. À vérifier en ouvrant l'adresse du
PDF directement dans le navigateur.

### Le PDF porte désormais son nom de publication

Le volume se compilait en `main.pdf`, du nom de sa source, alors que la
page de lecture et ses 1 441 renvois de folio demandent tous
`gramatiko.pdf` — d'où un bouton « Deskargar » qui rendait une page
d'erreur.

Le remède n'est pas de copier le fichier après coup : une copie se
périme, et le dépôt porterait deux fois 1,7 Mo. `pdflatex` prend un
`-jobname` :

    pdflatex -interaction=nonstopmode -jobname=gramatiko main.tex

La source garde son nom, le produit porte le sien. `komp.mk` est à jour,
ainsi que les dix-huit références des outils (`controles.py`,
`titres.py`, `caler_notes.py`).

Le champ de recherche dit maintenant « Serchez en la tota **libro** » et
non « volumo ».

### Deux restes du même défaut : la hauteur d'en-tête supposée

La mesure de `--kapo` avait corrigé les ancres, mais deux endroits
gardaient la valeur en dur.

**Les volets latéraux** se collaient à `top:97px`. Sur iPad, où l'en-tête
mesure 133 px, le haut du volet passait donc sous la barre — d'où le
premier intitulé, `Introdukto`, à demi caché. Ils suivent maintenant
`--kapo`.

**L'ouverture d'une URL à ancre** défilait avant que le script ait
mesuré : le navigateur emploie la valeur de secours, et la section visée
se logeait sous la barre. Le défilement est donc **refait** une fois la
mesure prise, puis encore après le chargement des fontes.

Vérifié à 1500, 1024 et 390 px, en arrivant par `#prepozicioni` : la
section tombe à 12 px sous la barre, le volet commence à son bord exact,
et le premier intitulé est entièrement visible.

Le groupe s'intitule désormais **`Introdukto`** et non `Liminari`.

### La quatrième hauteur d'en-tête supposée : l'observateur

Cliquer `-em-` dans le volet des chefa vorti menait bien au bon endroit —
le lien était juste — mais le volet **désignait ensuite l'entrée du
dessus**, `-eg-`. Le lien n'était pas en cause : le surlignage l'était.

`IntersectionObserver` décide de l'entrée courante sur une bande définie
par `rootMargin:'-100px 0px -55% 0px'`. Encore une hauteur d'en-tête en
dur. Sur iPad, où l'en-tête mesure 133 px, la bande s'ouvrait **au-dessus
de la barre** : un bloc long encore visible en haut — `-eg-` fait 442 px
— y entrait, et l'emportait sur celui qu'on venait d'atteindre.

La bande suit maintenant la hauteur mesurée. Comme `rootMargin` est figé
à la création, l'observateur est **refait** quand la hauteur change.
Vérifié à 1500 et 1024 px : `-eg-`, `-em-` et `-er-` désignent chacun
leur propre entrée, sans erreur JavaScript.

**C'est la quatrième occurrence du même défaut** — après les ancres, les
volets latéraux et l'arrivée par URL. La leçon vaut d'être répétée :
quand une valeur est écrite en dur, il faut chercher **toutes** ses
occurrences, pas seulement celle qui a fait mal. J'ai corrigé les trois
premières en croyant chaque fois avoir fini.

### Une vedette se reconnaît à ce qu'elle est, non à sa graisse

La règle précédente — « un alinéa qui s'ouvre par du gras est une
sous-entrée » — était **typographique, et la typographie de 1925 ne
sépare pas ce qu'il faut**. Le volume compose en gras ses vedettes
(`anti.`, `-em-`, `Tra`, `B`) *et* ses phrases d'exemple tout entières ;
le volet listait donc des phrases, `El mortis, tri monati ante nun, pos
longa sufri. Qua pen…`. Et il écrit de vraies entrées **sans gras** : les
dix-sept articles de PUNTIZADO — `Punto`, `Komo`, `Bi-punto`,
`Cito-hoketi` — sont en italique, et le chapitre n'avait **aucune**
entrée.

**La règle retenue lit ce que la ligne fait, non ce qu'elle porte.** Cinq
pièces, dans `vedette()` :

| | |
|---|---|
| **1. la tête** | après le renvoi de folio et le numéro de règle facultatifs (« 96. — »), l'alinéa doit s'ouvrir par un passage détaché : **gras, italique ou petites capitales**. Deux passages de même graisse se rejoignent si rien de nu ne les sépare — fin de ligne (`\nl`), mot coupé (`\cc`), ou la virgule d'une vedette double (`e, o`) |
| **2. la coupe** | si la tête porte elle-même `=`, `:` ou un tiret cadratin, **la vedette est ce qui précède** : le volume compose « *Dum ke : dum ke il esis malada* » d'une seule graisse, entrée puis exemple. Encore faut-il qu'une **phrase** suive la marque ; sans phrase, la ligne est une énumération (« *Pose : milion; miliard* ») et n'ouvre rien |
| **3. la brièveté** | 80 signes, 12 mots. **Garde-fou et non critère** : la plus longue vedette du volume en fait 63 (`Cadie, camatine, cavespere, casemane, canokte, camonate, cayare`), et ces deux bornes ne rejettent aujourd'hui aucun alinéa à elles seules |
| **4. ce n'est pas une phrase** | **le test qui porte tout le travail**, et l'ido le rend sûr : un verbe conjugué s'y termine par **-as, -is, -os, -us, -ez**, sans exception. `La tero movas`, `Me turnas la roto`, `Notez bone, ke…` sont donc des exemples, quelle que soit leur graisse. Une rupture de phrase au milieu de la tête (`… pos longa sufri. Qua pensabus…`) dit la même chose |
| **5. hors du gras, il faut la marque** | le gras ne sert dans ce volume qu'à la vedette ou à l'exemple, et le 4 écarte l'exemple ; mais l'**italique sert à tout mot cité** — il y en a cinq mille. Une tête qui n'est pas en gras ne vaut donc que si une marque de définition la suit : `=`, `:`, un point, un tiret, ou l'ouverture d'une glose `( [ { «`. C'est ce qui distingue « *Punto* (.) uzesas… », article, de « *Polko, valso*, e. c., esas dansi », exemple |

Deux exceptions étaient nécessaires au test du verbe, et elles sont de
classe fermée : `plus` (dans `Ne plus`) et `depos` portent une désinence
verbale sans être des verbes. Un nom propre rencontré au fil de la
phrase — `Paris`, `Adolfus` — porte la même finale ; on ne l'écarte que
s'il **n'ouvre pas** la tête, car un verbe à l'impératif, lui, l'ouvre
bel et bien (`Notez bone, ke…`).

**Le compte : 367 vedettes avant, 384 après** — 27 perdues, 44 gagnées.

*Les 27 perdues.* Vingt-quatre sont des **phrases d'exemple**, et c'est
tout le propos : `Lo facenda postulos longa tempo e multa lukti` et `Il
esas mortinta de tri monati, e vu ne savas lo!` (les deux seules entrées
de PRONOMO « LO », qui n'en a donc plus) ; six de VERBO (`La tero movas`,
`Me turnas la roto`, `Paris komunikas telefone kun Lyon`, `Me chanjis
depos mea yuneso…`, `Mea chapelo pendis an arboro…`, `Natante la fisho
movas…`) ; six de PREPOZICIONI (`El mortis, tri monati ante nun…`, `De
lua nasko il sempre montris…`, `On bone remarkez, ke de esas neutila…`,
`La konquesto di Anglia da la Normandi igis…`, `Ido povas distingar tote
certe l'autori…`, `Ek darfas uzesar metafore…`) ; quatre de SINTAXO
(`Quon vu dicas? Quan vu vidas?…`, `Quala vu judikas`, `Mem pos kom n ne
esas uzenda…`, et `Anke nula -n en : Me nomizis Adolfus mea filiulo`,
raccourcie en `Anke nula -n en`) ; `Notez bone, ke la Franca vorto
« fois »…` et `Pose : milion; miliard` de NOMBRI ; `No, me ne povas
asentar, ke la hipopotamo havas boko` de SUFIXI ; `Me recevis letro
skribita en linguo ne konocata da me` — la seule entrée de VORTORDINO,
qui n'en a donc plus. **Les trois autres ne sont pas des pertes mais des
raccourcissements** : `Ante ke; pos ke; depos ke o de kande : depos ke,
de kande` → `Ante ke; pos ke; depos ke o de kande`, `Dum ke : dum ke il
esis malada` → `Dum ke`, `Segun quante : segun quante me povos…` →
`Segun quante` ; et `Cadie, camatine, cavespere, casemane, canokte,
camonate` retrouve son dernier membre, `cayare`.

*Les 44 gagnées.* **Dix-sept à PUNTIZADO**, qui n'avait rien : `Punto`,
`Mayuskuli`, `Komo`, `Punto-komo`, `Bi-punto`, `Puntaro`, `Parentezi`,
`Kramponi`, `Streketo`, `Seko di la Vorti`, `Streko`, `Cito-hoketi`,
`Noto-referi`, `Klamo-punto`, `Question-punto`, `Apostrofo`, `Generala
remarko`. **Seize à VERBO**, le paradigme que le volume met en italique
et que les désinences en gras encadraient déjà : `antea pasinto`, `antea
futuro`, `antea kondicionalo`, `antea volitivo`, `Indikativo prezenta /
pasinta / futura`, `Kondicionalo prezenta`, `Volitivo prezenta`,
`Infinitivo prezenta / pasinta / futura`, `Antea pasinto / futuro /
kondicionalo / volitivo`. Puis six titres de section que l'italique ou
les petites capitales portaient seuls — `Adverbi di quanteso`,
`Prepozicioni kun verbi`, `Direta questioni`, `Nedireta questioni`,
`Remarki` (NOMBRI, en petites capitales) — et les cinq raccourcies
ci-dessus.

**Ce que la règle laisse passer, et qu'on dit plutôt que de le taire.**
`Nula -n` et `Anke nula -n en` (SINTAXO, qui n'a plus qu'elles) sont des
morceaux de phrase, courts et sans verbe : **rien de mécanique ne les
distingue d'une vedette**. À l'inverse, six topiques de VORTORDINO
(`L'atributo`, `L'adjektivo`, `L'adverbo`, `La questionanta vorti`, `La
participo`) et `Adjektivo` de SINTAXO sont en italique **sans marque de
définition** : la règle 5 les écarte, et le chapitre VORTORDINO se
retrouve sans entrée. C'est le prix de la règle 5, et il est assumé —
sans elle, `Polko, valso`, `Kruela` et `Treege`, qui sont des mots cités
dans une discussion, entreraient au volet.

Les chapitres de prose continue restent vides, comme il se doit :
KONJUGO-SISTEMO DI IDO affiche « *nula chefa vorto en ca chapitro* » — ses
alinéas `a)`, `b)`, `c)`, `d)` en italique sont suivis d'une parenthèse
fermante, non d'une marque de définition.

**Vingt-quatre ancres disparaissent, et il faut le dire** : toutes
désignaient une phrase d'exemple, sauf trois qui se raccourcissent
(`#konjuncioni-dum-ke-dum-ke-il-esis-malada` →
`#konjuncioni-dum-ke`, `#konjuncioni-segun-quante-segun-quante-me-povos-me`
→ `#konjuncioni-segun-quante`,
`#sintaxo-anke-nula-n-en-me-nomizis-adolfus-mea` →
`#sintaxo-anke-nula-n-en`). Aucun suffixe de collision ne bouge : les
quatre homonymes départagés le restent à l'identique. Le repli
`trovAncro` ne jouait pas ici — il cherchait une ancre **allongée**, et
c'est l'inverse qui s'est produit. Il cherche donc aussi, en dernier
recours, **le plus long identifiant existant dont l'adresse demandée soit
le prolongement**, coupé sur un tiret : les trois raccourcies retrouvent
leur entrée, et les vingt et une autres retrouvent au moins l'article ou
le chapitre qui les portait — `#verbo-la-tero-movas` mène à VERBO,
`#prepozicioni-de-lua-nasko-il-sempre-montris-extrema` à l'article `De`.
Vérifié dans le navigateur sur les cinq cas, plus l'ancienne
`#pronunco-dil-vokali-e`, qui continue de trouver `…-e-o` par l'autre
repli.

**Vérifié par capture**, en clair et en sombre, à 1400 et 390 px :
PUNTIZADO porte ses dix-sept entrées, PREPOZICIONI n'en a plus une seule
qui soit une phrase, VERBO range son paradigme dans l'ordre du texte,
KONJUGO-SISTEMO reste vide, le tiroir « Materio » du téléphone déplie les
dix-sept entrées sous le lien du chapitre, et le surlignage du volet suit
le clic (`Streko`, `Cito-hoketi`, `Apostrofo`). La page pèse 1 206 ko,
porte 852 identifiants sans doublon, et deux exécutions rendent le même
md5.

---

## Quatrième perte, et la première où la sauvegarde venait du commanditaire

Le conteneur a perdu `outils/html.py`, `index.html`, `.nojekyll`,
`outils/etoile.py`, les macros de renvoi du préambule et le `-jobname` de
`komp.mk`. La transcription LaTeX, elle, a tenu.

Aucune copie n'était joignable : le pont vers le disque du commanditaire
était coupé depuis plusieurs lots, et les dépôts avaient donc échoué en
silence. **C'est le commanditaire qui a renvoyé l'archive**, depuis les
fichiers que la conversation lui avait livrés.

Ce qu'il a fallu reprendre à la main après la restauration, l'archive
étant antérieure de quelques minutes à deux correctifs :

- la correction du folio 82 (`Ultre` seul en gras) ;
- les trois macros de renvoi du Tabelo, absentes du préambule restauré ;
- `\VUindexEcart`, employé deux fois et défini nulle part — la même
  incohérence qu'à la troisième perte, et le même symptôme :
  « Undefined control sequence » sur un fichier qui *semblait* complet.

État vérifié : 236 pages, 256 renvois dans le Tabelo, aucune erreur de
compilation ; page de lecture régénérée à 1 179 ko, `Introdukto`,
« Chefa vorti », « en la tota libro » et la mesure de l'en-tête tous
présents.

**Reste perdu** : `outils/etoile.py`, le relevé des douze sommets de
l'étoile. Le résultat qu'il a produit — la vignette redressée — est dans
`ornamenti/`, mais l'outil qui permettrait de refaire la mesure est à
réécrire.

**La leçon, quatre fois payée** : une sauvegarde qui échoue en silence
n'est pas une sauvegarde. Le dépôt sur le disque du commanditaire doit
être *vérifié* à chaque lot, et son échec traité comme un incident, non
comme une gêne à mentionner en fin de réponse.

### L'astérisme se pose à son blanc, non là où il est déclaré

Au folio 207 l'astérisme paraissait entre `c)` et `d)`, alors que le
fac-similé le pose bien plus bas, au-dessus de « On dicis… ». La cause
est celle qui court dans tout ce volume : **un élément posé à une
ordonnée absolue est déclaré en tête de page**, et l'extracteur le
prenait là où il est écrit.

La règle du volume dit où le remettre : un élément de hauteur nulle
**n'ouvre pas son propre blanc**, il lui faut un `\VUsaut` correspondant
dans le flux. C'est donc à ce saut-là qu'il appartient. L'astérisme est
mis en attente et posé au premier `\VUsaut` d'au moins 5 mm de la même
page ; s'il n'en paraît aucun, un filet de sécurité le pose avant la
page suivante — mieux vaut mal placé que perdu.

**Un piège d'ordre de dispatch a coûté un essai** : la branche ajoutée
était placée après le tableau des macros muettes, qui avale `\VUsaut`.
Elle n'était donc jamais atteinte, et l'astérisme partait sur le filet de
sécurité, en tête de page. Déplacée avant ce tableau, elle fonctionne.

Les trois astérismes tombent maintenant devant « Nun ni videz… »
(folio 186), « On dicis… » (207) et « Pro quo ne… » (212).

### Les deux points restés ouverts

**Les anciennes adresses d'ancre résolvent de nouveau.** Six avaient
changé le jour où la détection des chefa vorti a été corrigée, et un lien
copié avant ce jour-là ne trouvait plus sa cible : la page s'ouvrait en
tête, sans rien dire. Plutôt que de figer une table des anciennes
adresses — qui vieillirait à son tour et serait à tenir à chaque
correction — la cible se cherche par **parenté** : l'ancre allongée d'un
membre (`…-e` → `…-e-o`), ou le même nom à un suffixe de rang près. Ce
qui n'a pas de parent laisse la page où elle est, comme avant. Vérifié
sur les trois adresses connues et sur une adresse inventée.

**Les notes recollées sans espace étaient deux.** Le générateur les
compte désormais et l'affiche à chaque exécution : « notes recollées avec
espace — 2 ». C'était la réponse manquante à la question posée avec
« sempreplu ». Le chiffre est petit, mais il n'était pas connu ; il l'est
maintenant à chaque régénération, et une remontée signalerait une
régression.

### `outils/etoile.py`, réécrit — et une réserve sur sa seconde voie

L'outil perdu est réécrit. Il relève les **douze sommets** de l'étoile —
six pointes, six creux —, affine chacun par interpolation parabolique sur
le profil radial du contour, puis en prend la moyenne circulaire à
l'harmonique 12, où les douze contribuent à parts égales. Le préambule du
fichier raconte les trois essais qui ont mené à cette méthode, dont les
deux ratés : la mesure sur les lettres du centre, qui ne mesurait que son
bruit, et la rotation appliquée dans le mauvais sens faute d'avoir
vérifié le résultat.

Il offre pour cela `--essai <angle>` : on pose la rotation, on remesure,
et si l'écart a grandi le signe est faux. C'est la leçon du deuxième
raté, transformée en commande.

**Réserve, et elle compte.** L'outil a deux voies d'entrée, et **une
seule est fiable** :

- sur le **scan** (`--scan`, `--essai`), il est cohérent : +1,101 degré
  au brut, −0,149 après rotation de −1,101 ;
- sur le **cliché détouré**, il a rendu +13,8 degrés sur une vignette que
  la voie du scan donne droite. Le masque circulaire rogne
  vraisemblablement la pointe des branches, ce qui déstabilise le choix
  des six extrêmes.

**Ne pas se fier à la lecture du cliché tant que ce point n'est pas
repris.** La voie du scan, elle, a servi à refaire le redressement.

La restauration avait d'ailleurs ramené la vignette **d'origine**, non
redressée : le travail de redressement avait été perdu avec le reste et a
dû être refait.

### Le redressement des clichés avait été perdu, lui aussi

La restauration avait ramené les clichés **d'origine**, non redressés, et
rien ne le signalait : une planche penchée d'un degré a l'air normale
tant qu'on ne la mesure pas. Il a fallu que le commanditaire s'en doute.

Refaits, tous deux par la voie du scan :

| cliché | inclinaison mesurée | après |
|---|---|---|
| portrait (feuillet 7) | −0,760° | +0,134 / −0,059 sur les deux bords |
| vignette (feuillet 3) | +1,101° | −0,149° |

Le fleuron du folio 232, lui, était droit et l'est resté (209 × 25 px,
inchangé).

**Contrôle rapide après toute restauration** : les tailles suffisent à
dire si le redressement est là. Portrait redressé 724 × 1066 px, non
redressé 726 × 1071 ; vignette redressée 256 × 251, d'origine 241 × 249.
Une taille est plus vite lue qu'un angle.

### `outils/temoins.py` — la liste de témoins, enfin écrite

Cinq pertes de conteneur ont montré que **`git log` ne prouve rien** : à
la dernière, l'historique était cohérent et les fichiers ne l'étaient
pas. Ce qui détecte la panne, c'est de chercher, pour chaque correctif,
une chaîne qui ne peut se trouver que s'il est en place.

L'outil vérifie **34 témoins** : trente chaînes caractéristiques, les
trois tailles de cliché — qui disent d'un coup d'œil si le redressement
est là — et le nombre de pages du PDF. Il sort en erreur si l'un manque.

    python3 outils/temoins.py

Il a immédiatement trouvé **six régressions** que rien d'autre ne
signalait, et que le volume compilait sans se plaindre : le titre du
folio 3 et `PUNTIZADO` revenus à leur composition trop large, les blancs
des folios 21 et 122, et — celle que le commanditaire avait vue — le
groupe `APENDICI` des signets, avec le renvoi du Tabelo à la mauvaise
page.

**À passer après chaque restauration, et avant chaque livraison.** Il
coûte une seconde. Quand un correctif s'ajoute, son témoin s'ajoute avec
lui : c'est la seule discipline qui ait résisté à ces cinq pertes.

## L'accolade fermante du folio 31

Signalée sur iPad : « la petite accolade qui devrait relier *minim* et
*maxim* à *de o ek* ne relie finalement que *maxim*, et le positionnement
de *de o ek* est un peu difficile à lire ». Les deux défauts tiennent au
même oubli, et le second existait aussi en colonnes.

### Ce que le relevé disait déjà

Le fac-similé porte quatre accolades au folio 31. Trois ouvrent à droite,
la quatrième ferme à gauche :

| accolade | abscisse | hauteur | décalage | rangs |
| --- | --- | --- | --- | --- |
| Komparativo | 37,68 mm | 27,2 pt | +1,23 pt | 0 – 2 |
| relatanta | 36,83 mm | 15,7 pt | −3,71 pt | 3 – 4 |
| Superlativo | 19,39 mm | 17,4 pt | −3,71 pt | 4 – 5 |
| **de o ek** | **77,30 mm** | **16,6 pt** | **−6,48 pt** | **3 – 4** |

16,6 pt valent 1,66 interligne, donc **deux rangs** — la mesure disait
depuis toujours que cette accolade couvre *maxim* **et** *minim*. Ce qui
manquait n'était pas la mesure : c'était sa lecture. `groupes()` ne
construisait de groupe que pour `\VUaccolade` et `\VUaccoladeH` ;
`\VUaccoladeD` ne tombait dans aucun cas et restait une accolade **en
ligne**, haute d'un rang, posée contre le seul terme de son propre rang.

### La règle, et pourquoi elle est symétrique

Une ouvrante nomme à **gauche** ce qu'elle rassemble à droite ; une
fermante fait l'inverse. C'est la même pièce retournée, et `fermantes()`
la lit comme telle : portée par `etendue()`, titre au plus proche voisin
**de droite**, membres à **gauche** du trait.

Restait à la placer dans l'arbre. Les rangs 3 – 4 sont exactement ceux du
groupe « relatanta » ; deux boîtes emboîtées auraient dit ce qu'une seule
dit mieux, et le fac-similé ne montre pas deux bandes gigognes mais **une**
bande de deux rangs, prise entre une ouvrante à gauche et une fermante à
droite. Quand une fermante couvre exactement un groupe, elle se pose donc
**au bout de celui-ci** plutôt que par-dessus. Le cas général — une
fermante qui couvre plusieurs groupes, ou aucun — garde son propre étage
(`.gr.gd`, membres puis accolade puis titre) ; il ne se présente nulle
part dans ce volume et n'est vérifié que par deux essais montés à la main.

### Le demi-interligne, en colonnes aussi

`\VUdecale{-4,82 pt}` abaisse « de o ek » d'un **demi-interligne** : le
fac-similé le pose à mi-hauteur entre deux rangs, en face de la pointe de
son accolade. La page de lecture ignorait ce nombre depuis toujours, et
le nom retombait sur le rang de « maxim » — un demi-interligne trop haut,
d'où le « difficile à lire ». En colonnes une case ne peut pas flotter :
elle prend donc les **deux rangs** qu'elle chevauche et s'y centre
(`rowspan`, `td.mez`), ce qui la remet en face de la pointe. La règle vaut
pour toute case ainsi décalée : « Superlativo », qui a le même défaut au
même endroit, est corrigé du même coup.

### Ce que la place a coûté

Un étage de plus, c'est quatre intervalles de plus, et le tableau du
folio 31 est le plus profond du volume. Trois réglages en découlent, tous
mesurés plutôt que devinés :

* **une case de tableau ne se brise pas** (`.gr-m{white-space:nowrap}`,
  et un bloc de membres qui ne descend pas sous `min-content`) — sans
  quoi « Supereso maxim » se coupait en deux quand « infreso minim »,
  d'un cheveu plus court, tenait, ce qui ne veut plus rien dire ;
* **les groupes emboîtés resserrent leurs intervalles** (7 px → 4 px) ;
* sous 420 px, corps et intervalles se resserrent encore, et ce qui
  dépasse malgré tout **défile** au lieu d'être coupé.

Balayage de 360 à 1 366 px : **plus rien ne dépasse à aucune largeur**,
alors que le « k » de « de o ek » sortait du volet de 4 px à 390 et à
950 px — la largeur même de l'iPad d'où venait le signalement.

### Un effet de bord, corrigé au passage

Ce qui, sur un rang, tombe à gauche d'un groupe sans lui appartenir — le
numéro « 28. » — se reconnaissait en le comparant à l'abscisse de
l'**accolade**. C'était juste tant que toutes ouvraient à droite : le
titre était alors la pièce la plus à gauche. Une fermante range ses
membres à gauche de son trait ; les mesurer contre lui les mettait
dehors, puis dedans — donc **deux fois**. `bord()` compare désormais à
l'abscisse la plus à gauche que le groupe occupe réellement. Le folio 31
en sort **identique à l'octet près** ; ce sont les deux essais montés à
la main qui montraient le doublon.

### Contrôle

Le seul bloc du volume qui change est le tableau du folio 31 : 22
fragments, dont deux cases de la version en colonnes. Cinq témoins
s'ajoutent (44 en tout).

## Les deux schémas du folio 220, centrés sur la justification

Demandé : que le « dots table » soit centré sur la page HTML. Il l'était
déjà dans le volume — mais pour une raison qui ne se transporte pas
telle quelle.

### Ce que le scan dit

Relevé sur `scan/r0224.png`, bloc de texte x 41 – 1123, justification
1082 px :

| bande | marge gauche | marge droite | écart |
| --- | --- | --- | --- |
| schéma à points | 449 px (41,5 %) | 458 px (42,3 %) | 9 px |
| « Ludovikus » | 449 px (41,5 %) | 450 px (41,6 %) | 1 px |
| accolade horizontale | 270 px (25,0 %) | 274 px (25,3 %) | 4 px |
| *(ligne de texte pleine)* | 0 px | 1 px | 1 px |

Les deux schémas sont donc centrés, à un pixel près pour l'arbre, à neuf
sur 1 082 pour les points. Le tableau du folio 31, lui, ne l'est pas :
ses marges sont nulles, il **remplit** la mesure. La différence est
mesurable, et c'est elle qui décide — non l'allure.

### Pourquoi le volume n'avait rien à corriger

Dans le volume les abscisses sont **absolues** : `\VUcase{38,10 mm}` pose
le premier point à 38,10 mm du bord du bloc, et comme la mesure fait
91,69 mm le centrage en découle. Rien à faire, donc, du côté du PDF.

Sur la page de lecture la colonne n'a **pas** la largeur du volume : elle
varie de 324 à 692 px selon l'appareil. Un retrait de 38,10 mm converti
en pourcentage y donnerait n'importe quoi, et le retrait fixe de 1 em des
deux rendus collait les schémas à gauche. **Ce qui se transporte d'une
mesure à l'autre, c'est le rapport — ici la symétrie**, non l'écart au
bord.

### La marque

`\VUtabloCentrita` précède les rangs. Elle ne compose rien — elle est
définie comme vide, et le volume sort **identique** (236 pages, 0 erreur).
Elle n'existe que pour dire à la page de lecture ce que la mesure du
fac-similé énonce. Elle se pose d'après le scan, jamais d'après l'œil :
marges gauche et droite égales, et **toutes deux notables** — sans cette
seconde condition, un bloc qui remplit la mesure (marges nulles, donc
égales) serait déclaré centré, et le folio 31 aurait basculé avec.

Le rendu suit les deux sorties, colonnes et groupes : à 390, 950 et
1 500 px, les deux schémas ont désormais **exactement** la même marge de
part et d'autre. Le seul changement dans le corps de la page est
l'ajout de deux `<div class="centrita">` ; les 1 726 autres blocs sont
identiques à l'octet près.

### Livraison

À partir d'ici l'archive est un **ZIP**, et `gramatiko.pdf` s'y trouve à
la racine. `outils/arkivo.py` la fabrique, pour que le format ne dépende
pas de ce dont je me souviens :

    python3 outils/arkivo.py        # verifie les temoins, puis ecrit le ZIP

## L'astérisque nue est une marque de note

Signalé : l'astérisque après « REGULI DI DERIVADO » devrait ouvrir la
note qui lui répond. Elle n'ouvrait rien — et la note, elle, avait
disparu dans une autre.

### Deux façons d'appeler une note, dont une seule était lue

Le volume marque ses notes de trois manières, et le relevé les
transcrit telles quelles :

| marque | feuillets | lue |
| --- | --- | --- |
| `(1)`, `(2)`, … | partout | oui |
| `(*)` | 166, 191, 208 | oui |
| `*` **nue** | 74, 122 | **non** |

`note()` ne reconnaissait qu'une marque entre parenthèses. Un alinéa
sans marque reconnue est, par construction, la **suite de la note
précédente** : c'est ce qui recolle les notes qui débordent d'une page
sur l'autre. L'alinéa `*Bibliografio.` tombait donc dans cette règle et
se soudait à la note (2) du feuillet 121, à la fin de laquelle on le
retrouvait. N'existant pas comme note, il n'avait pas d'identifiant, et
l'astérisque du titre n'avait rien à appeler.

Le feuillet 74 avait le même défaut, non signalé : sa note (2) faisait
1 399 signes au lieu de 463, ayant avalé la note à l'astérisque qui la
suit.

### Ce qu'il ne fallait pas casser

Chercher l'appel d'une note « astérisque » sous la forme `*` aurait
détruit les trois notes `(*)` des feuillets 166, 191 et 208, dont
l'appel porte ses parenthèses. **L'appel se cherche donc sous la forme
même que le fac-similé emploie**, retenue avec la note (`apel`) au
moment où on la lit — non reconstruite à partir de son numéro.

Le volume porte par ailleurs cinq astérisques qui **ne sont pas** des
appels, et qu'il fallait laisser en repos :

* feuillet 65 — `« on » * never`, l'astérisque du linguiste, qui marque
  une forme fautive ;
* feuillet 121 — `Ni nomizas * morfemo`, de même ;
* feuillet 134 — `*equi-.` et `*ko-.`, deux appels **auxquels ne répond
  aucune note** : coquille de l'original, déjà relevée et conservée ;
* feuillet 225 — `steleti (*) o kruci (†)`, où le texte *parle* des
  astérisques au lieu d'en porter une.

Aucune ne devient un lien : la recherche n'a lieu que pour une note
effectivement présente au pied de **cette** page, et aucune de ces
pages n'en porte à l'astérisque. Vérifié une à une.

### Contrôle

Les notes passent de 408 à 410, et le recollage abusif d'un alinéa
disparaît (2 → 1). Les cinq notes à l'astérisque ont chacune exactement
un appel, les trois `(*)` ayant gardé leurs parenthèses. Le corps de la
page change en quinze fragments, tous aux feuillets 74, 121 et 122.
Deux témoins s'ajoutent (49 en tout).

## L'appel posé avant la tête cachait la vedette (folio 130)

Demandé : que `*equi-` et `*ko-` soient des « chefa vorti » au chapitre
PREFIXI TEKNIKALA. Le chapitre n'en portait qu'une, `mono-`.

### Pourquoi deux des trois manquaient

`vedette()` lit la tête d'un alinéa après avoir sauté ce qui n'est pas
elle : le renvoi de folio, puis le numéro d'alinéa. Ce qui suit doit
être la tête détachée — gras, italique ou petites capitales. Au folio
130 les deux alinéas s'ouvrent ainsi :

    130 *<b>equi-.</b> — Ol signifikas egala…
    130 *<b>ko-.</b>   — Ol renkontresas en kosinuso…

L'astérisque tombe **entre** le renvoi de folio et le gras. La tête ne
s'y trouvait donc pas là où on la cherchait, et l'alinéa passait pour
du texte courant. `mono-`, qui n'en porte pas, était lu sans peine —
d'où une entrée au lieu de trois.

Cette astérisque est un appel de note **auquel ne répond aucune note** :
c'est la coquille de l'original, relevée de longue date au feuillet 134
et conservée. Elle reste donc visible dans le texte ; elle cesse
seulement d'empêcher la lecture de la tête.

### Que le volume nomme lui-même les trois

Ce n'est pas une appréciation : l'entrée du TABELO l'écrit,

    Prefixi teknikala (equi-, ko-, mono-) . . . 130

et les trois alinéas ont exactement la même facture — un préfixe en
gras, suivi du tiret de définition et de la glose. Les traiter
autrement revenait à laisser une marque typographique décider à la
place de la structure, ce que la règle des « chefa vorti » a
précisément pour objet d'éviter.

### Portée

`APEL_TETE` saute un appel — asterisque nue, ou appel déjà transformé en
lien — de part et d'autre du numéro d'alinéa. Les vedettes passent de
384 à 386 : **exactement les deux attendues**, dans l'ordre du TABELO,
aucun autre chapitre du volume ne bougeant. Le corps de la page change
en vingt fragments, tous dans ces deux alinéas. Un témoin s'ajoute
(50 en tout).

## L'accolade fermante rejetée contre le bord, et le balayage des vedettes

### 1. Aucun autre chapitre n'a le défaut du folio 130

Le défaut n'était pas « une vedette manquante » mais une classe précise :
**la tête détachée précédée d'un appel de note**. Balayage du volume —
pour chaque alinéa, ce qui sépare le renvoi de folio (et le numéro) de
la première tête en gras, italique ou petites capitales :

* **150 alinéas** ont quelque chose devant leur tête ; dans tous les cas
  sauf deux, ce quelque chose est **du texte** — « La », « L' », « On
  uzas », « Ni vidis »… Ce sont des phrases ordinaires contenant un mot
  en italique, non des vedettes. Élargir la règle pour les prendre
  fabriquerait des vedettes fausses par centaines : « La *demonstrativ
  adjektivi*… » n'est pas une entrée, c'est une phrase.
* **2 alinéas** ont devant leur tête un préfixe qui ne contient **aucune
  lettre** — un appel seul : `*equi-` et `*ko-`, au folio 130, déjà
  corrigés.

Le volume n'en porte pas d'autre. Le critère est reproductible : un
préfixe fait uniquement d'un appel (astérisque, croix, appel déjà mis en
lien, numéro entre parenthèses).

### 2. L'accolade fermante était rejetée contre le bord droit

`.gr-l` — le bloc des membres — portait `flex:1 1 auto`, donc il
**s'étirait** jusqu'au bord du volet. L'accolade fermante et « de o ek »,
placés après lui, s'en trouvaient poussés tout à droite : à 1 150 px,
« de o ek » se retrouvait à une demi-colonne de « maxim », alors que le
fac-similé les sépare de **3,3 mm sur 92** — un voisinage, non un
alignement à droite.

Pourquoi les vérifications précédentes ne l'avaient pas vu : le rendu en
groupes n'avait été regardé qu'à 390 et 950 px, deux largeurs où le volet
est **exactement** aussi large que le tableau. Sans jeu à distribuer,
l'étirement ne produit rien. Il fallait une largeur **intermédiaire**
pour que le défaut paraisse — et c'est désormais la leçon retenue pour
tout ce qui touche à ces deux rendus : mesurer aussi entre les bornes,
non seulement aux bornes.

Le groupe qui porte une fermante à son bout reçoit la classe `gf`, et son
bloc de membres ne s'étire plus. L'accolade suit le dernier membre à
1–3 px près, à **toutes** les largeurs de 360 à 1 200 px, et rien ne
déborde. Un seul fragment change dans le corps de la page : une classe.
Un témoin s'ajoute (51 en tout).

## La casse des « chefa vorti » : deux classes d'entrées, une casse pour chacune

Le volet de droite rangeait côte à côte les deux casses du même volume :
`B, c, d, f, g, h…` pour les consonnes, `Interne` suivi de `extere,
supre, infre, avane…` pour les adverbes de lieu. Sur 386 vedettes, **235
portaient une capitale**, 90 une minuscule, 61 commençaient par un tiret
ou une parenthèse (`-ul`, `-ez`, `O(d)… o(d)`).

### 1. Le mot cité : la capitale du fac-similé n'est pas la sienne

Elle est celle de l'**alinéa**. Le volume compose ses entrées au fil du
texte : celle qui ouvre un alinéa prend la capitale de phrase, celles qui
suivent dans le même alinéa gardent leur minuscule. Le mot, lui, n'a pas
changé. Trois preuves prises au relevé :

| ce qu'on lit au volet | ce que fait le fac-similé |
| --- | --- |
| `B`, puis `c`, `d`, `f`, `g`… | folio 12 : l'article de la première consonne est **numéroté** (« 3. — **B** = *b* en l'Italiana »), les vingt-et-un autres ne le sont pas |
| `Interne`, puis `extere`, `supre`, `infre`… | folios 62-63 : **une seule énumération**, une capitale pour onze minuscules — `Interne` ouvre son alinéa, les onze autres suivent le leur |
| `des-` **et** `Des-` | folios 124 et 125 : **le même morphème, deux fois, dans les deux casses**. Rien ne les distingue que la place dans l'alinéa |

Ces entrées passent donc à la casse du mot, **mot par mot** — `Seko di la
Vorti` n'aurait rien gagné à garder la capitale de son milieu —, **sauf
le nom propre** : `NOMI_PROPRA = {Europa, Afrika, Amerika, Azia, Usa}`.

La liste ne se juge pas mot à mot, elle se contrôle sur le volume
entier : des 235 vedettes capitalisées, **18 seulement ne sont jamais
attestées en minuscule ailleurs dans le texte** ; et sur ces 18, **16
sont des mots communs dont l'unique emploi du volume est la vedette
elle-même** — `Tarde`, `Posmorge`, `Ulube`, `Irgequale`, `Konsente`,
`Puntaro`, `Klamo-punto`… Restent `Europa, Afrika, Amerika, Azia` (folio
25) et `Usa` (folio 26). Le contrôle est rejouable : recomposer le volume
et recompter suffit à savoir si la liste doit s'allonger.

### 2. Le titre de rubrique : il porte la capitale, et il la garde

`Punto`, `Komo`, `Bi-punto` (PUNTIZADO), `Indikativo prezenta` et le
paradigme de VERBO, `Adverbi di quanteso`, `Prepozicioni kun verbi`,
`Direta questioni`, `Remarki` : ces entrées ne **citent** rien, elles
**nomment** ce dont l'article traite, en métalangue. Un titre porte la
capitale. **44 vedettes** sont de cette classe.

**Ce qui sépare les deux classes, c'est la graisse.** Le volume réserve
le gras aux formes de l'ido — c'est déjà ce que dit la règle 5 de
`vedette()`, à laquelle les entrées en italique doivent une marque de
définition pour être lues — et compose en **italique** ou en **petites
capitales** ce qu'il ne cite pas mais nomme. Les **38 entrées ainsi
composées sont toutes des titres, sans exception**. `vedette()` rend donc
un troisième rang, la graisse de la tête, et `casse_vedette()` s'y règle.

**Ce que la règle ne lit pas, et qu'on nomme plutôt que de le taire** :
**six titres que le fac-similé compose en gras**, à la place et sous la
forme exactes d'un mot cité — `Radiki. — Li esas verbala o nomala` ne se
distingue en rien de `anti. — Ta prefixo esis l'objekto di la decido`.
Aucune marque mécanique ne les sépare ; ils sont donc nommés un par un
dans `RUBRIKI_GRASA` : `La plaso dil komplemento di irga prepoziciono`,
`Radiki.`, `Dezinenci.`, `Konsequo.`, `Praktikal moyeno.`, `Konsequi.`

**Un titre reçoit sa capitale même là où le fac-similé ne la lui donne
pas.** Le folio 48 écrit `antea pasinto, antea futuro, antea
kondicionalo, antea volitivo` en bas de casse, et le folio 49 reprend les
quatre mêmes titres en capitale : c'est encore la place dans l'alinéa qui
décide. Le volet ne peut pas faire dépendre une entrée de cet accident,
ni afficher deux fois le même titre de deux façons — il lit `Antea
pasinto` aux deux folios.

### Ce qui ne bouge pas : les adresses et le texte

* **Les 856 ancres sont identiques, une à une.** `ardoise()` passait déjà
  tout en minuscules : `#pronunco-dil-konsonanti-e-digrami-b` était déjà
  ce qu'il est. Aucun lien déposé, aucun signet, aucun renvoi ne change —
  ce qui est la raison pour laquelle ce correctif pouvait être fait tard.
* **Le corps de la page est octet pour octet le même.** La lettre du
  fac-similé n'est jamais corrigée, capitale d'alinéa comprise. Ne
  changent que les **197 intitulés du volet** (et leurs infobulles) et
  les **197 libellés `aria-label`** du bouton en chaîne, qui nomment
  l'entrée à copier. Le diff de `index.html` ne contient rien d'autre,
  vérifié balise par balise.

Après correctif, **46 vedettes portent une capitale** : les 44 titres de
rubrique, et les deux entrées de noms propres.

Quatre témoins s'ajoutent — la règle, la graisse rendue par `vedette()`,
la liste des noms propres, celle des six titres composés en gras —,
**55 en tout**.
