#import "Enssat.typ":*
#show: doc => conf(
  titre: [ Modèle de rapport "Enssat" ],
  auteurs: (
    (
      nom: "Pierre Alain",
      email: "alain@enssat.fr",
    ),
    (
      nom: "Damien Lolive",
      email: "lolive@enssat.fr",
    ),
  ),
  annee: 2023,
  promotion: "Info3",
  module: "Développement logiciel",
  bibliographie: "rapport.bib",
  doc,
) 
 
= Introduction
#lorem(300)

== Un paragraphe avec un tableau
#lorem(300)

#figure(table(
    columns: 4,
    [t], [1], [2], [3],
    [y], [0.3s], [0.4s], [0.8s],
  ),
  caption: [Un tableau avec des nombres.],
) 

== Un paragraphe avec une image
#lorem(300)

Et il ne faut pas oublier de citer ce template Enssat #cite("template-enssat").
 
#figure(
  image("Enssat-UnivRennes_RVB.png"),
  caption: [Le logo de l'Enssat et de l'Université]
)

== Un paragraphe final
#lorem(300)
 
 ceci est un test. 
 
= Conclusion
#lorem(300)
