from utils import Types
from utils import Mode

class Parametre:
    """
    Classe parametre qui contient , type TYPE_INTEGER ou TYPE_BOOLEAN, mode en Mode
    """
    def __init__(self, type: Types, mode : Mode):
        """
        Constructeur de la fonction variable
        """
        self.type = type
        self.mode = mode

    def __str__(self) -> str:
        return "param: %s %s"%(self.type, self.mode)