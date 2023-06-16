from enum import Enum

class Types(Enum):
    """
    TYPE_INTEGER \n
    TYPE_BOOLEAN
    """
    TYPE_INTEGER = "int"
    TYPE_BOOLEAN = "bool"

    def __str__(self) -> str:
        return self.value

class Mode(Enum):
    """
    MODE_IN \n
    MODE_INOUT
    """
    MODE_IN = "in"
    MODE_INOUT = "inout"

    def __str__(self) -> str:
        return self.value