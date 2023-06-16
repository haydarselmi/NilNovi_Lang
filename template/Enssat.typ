//  _____   _       ____    ____    ____    _____ 
// /  __/  / \  /| / ___\  / ___\  /  _ \  /__ __\
// |  \    | |\ || |    \  |    \  | / \|    / \  
// |  /_   | | \|| \___ |  \___ |  | |-||    | |  
// \____\  \_/  \| \____/  \____/  \_/ \|    \_/  
//                                                

#let conf(
  titre: none,
  auteurs: (),
  module: none,
  promotion: none,
  annee: 0,
  bibliographie: none,
  doc,
) = {
  set text(lang:"fr")

  show "Enssat": smallcaps
  show link: underline

//  _____   ____    ____    ____    _____ 
// /  __/  /  _ \  /  __\  /  _ \  /  __/ 
// | |  _  | / \|  |  \/|  | | \|  |  \   
// | |_//  | |-||  |    /  | |_/|  |  /_  
// \____\  \_/ \|  \_/\_\  \____/  \____\ 
//                                        

  set page(
    paper: "a4",
    header: grid(
        columns: (1fr,) * calc.min(auteurs.len(), 4),
        row-gutter: 24pt,
        ..auteurs.map(auteur =>
          [#auteur.nom\
            #link("mailto:" + auteur.email)]
        ),
      ),
    footer: align(center, scale(x:60%, y:60%, image("Enssat-UnivRennes_RVB.png")))
  )
  grid(
    columns: (1fr, 1fr),
    row-gutter: 12pt,
    // attention ici le " fermant est sur la ligne suivante...
    //    et les espaces supplémentaires sont affichés.
    text(17pt, smallcaps("Module : 
    " + module)),
    text(17pt, smallcaps("Année " + str(annee)+ " : 
    " + promotion)),
  )
  v(200pt)
  align(center, text(30pt, titre))
  pagebreak()


//  _____   ____    ____    _       _____   ____  
// /__ __\ /  _ \  /  _ \  / \     /  __/  / ___\ 
//   / \   | / \|  | | //  | |     |  \    |    \ 
//   | |   | |-||  | |_\\  | |_/\  |  /_   \___ | 
//   \_/   \_/ \|  \____/  \____/  \____\  \____/ 
//                                                

  set text(size: 11pt)
  set par(justify: true)
  set heading(numbering: "1.a.i")
  show heading: smallcaps
  set list(marker: [--])

  set page(
    paper: "a4",
    numbering: "1", // numéros des pages
    number-align: center,
    header: text(0.95em, smallcaps(module + " : " + titre)),
    // hacky: dans la suite une page de numéro 0 n'a pas de compteur...
    footer: (locate(loc => {
      if (counter(page).at(loc).first() != 0) {
        align(center, counter(page).display())
      }
    }))
  )

  // table des matières
  // force à ne pas avoir de numéro de page sur la table des matières
  counter(page).update(0)
  outline()

  // table des figures s'il y en a
  locate( loc =>
    if (counter(figure).final(loc).first() > 0) {
      pagebreak()
      counter(page).update(0) // voir au dessus
      outline(
        title: [Liste des figures],
        target: figure,
      )
    }
  )

//  ____    ____    ____    _       _       _____   _       _____ 
// /  _ \  /  _ \  /   _\  / \ /\  / \__/| /  __/  / \  /| /__ __\
// | | \|  | / \|  |  /    | | ||  | |\/|| |  \    | |\ ||   / \  
// | |_/|  | \_/|  |  \_   | \_/|  | |  || |  /_   | | \||   | |  
// \____/  \____/  \____/  \____/  \_/  \| \____\  \_/  \|   \_/  
//                                                                

  pagebreak()
  counter(page).update(1)
  doc

// ____      _     ____    _         _     ____    _____   ____    ____    ____    _         _     _____ 
///  _ \    / \   /  _ \  / \       / \   /  _ \  /  __/  /  __\  /  _ \  /  __\  / \ /|    / \   /  __/ 
//| | //    | |   | | //  | |       | |   | / \|  | |  _  |  \/|  | / \|  |  \/|  | |_||    | |   |  \   
//| |_\\    | |   | |_\\  | |_/\    | |   | \_/|  | |_//  |    /  | |-||  |  __/  | | ||    | |   |  /_  
//\____/    \_/   \____/  \____/    \_/   \____/  \____\  \_/\_\  \_/ \|  \_/     \_/ \|    \_/   \____\ 
//                                                                                                       

  if (bibliographie != none) {
    pagebreak()
    bibliography(bibliographie)
  }

}
