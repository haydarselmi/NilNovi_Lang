# Modèle typst pour les rapports Enssat

Le but de ce dépôt est de pouvoir avoir un modèle pour les rapports utilisable avec [typst](https://github.com/typst/typst/).

Pour utiliser le modèle, Vous devez récupérer les fichiers :
- `Enssat-UnivRennes_RVB.png` qui est affichée sur la page de garde
- `enssat.typ` qui donne les propriétés de la page de garde, table des matières, table des figures (tableaux, images, etc.), corps du document, bibliographie

Vous trouverez dans le fichier `rapport.typ` un exemple d'utilisation du modèle et dans `rapport.bib` un exemple de fichier de bibliographie.

Pour compiler votre rapport, il suffit d'utiliser la commande `typst compile rapport.typ`.
