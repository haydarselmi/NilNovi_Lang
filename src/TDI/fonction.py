from utils import Types
# from utils import Mode

class Fonction:
    """
    Contient nom en String, type en Types(bool ou int), args(Variable, Mode)
    """
    
    def __init__(self, nom : str, type : Types = None, args = []):
        """
        Constructeur de la classe Fonction
        """
        self.nom = nom
        self.type = type
        self.args = args
        self.initialise = True

    def __str__(self) -> str:
        return "%s %s -> %s"%(self.nom, [str(param) for param in self.args], self.type)
    
    def setParams(self, args):
        self.args = args

    def setType(self, type):
        self.type = type