from utils import Types
# from utils import Mode

class Procedure:
    """
    Contient nom en String, args(Variable, Mode)
    """
    def __init__(self, nom : str, args = []):
        """
        Constructeur de la classe Procedure
        """
        self.nom = nom
        self.args = args
        self.initialise = True

    def __str__(self) -> str:
        return "%s %s"%(self.nom, [str(param) for param in self.args])
    
    def setParams(self, args):
        self.args = args