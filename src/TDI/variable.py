from utils import Types

class Variable:
    """
    Classe variable qui contient nom en String, type TYPE_INTEGER ou TYPE_BOOLEAN, adresse en int
    """
    def __init__(self, nom : str, type: Types, adresse : int):
        """
        Constructeur de la fonction variable
        """
        self.nom = nom
        self.type = type
        self.adresse = adresse
        self.initialise = False

    def __str__(self) -> str:
        return "%s (%s) @%d"%(self.nom, str(self.type), self.adresse)
    