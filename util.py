from PyQt6.QtGui import QColor
from enum import Enum

#############################################################################

def simplifiedName(text: str):
    for c in "()[]{}":
        text = text.replace(c, '')
    return text.strip()

#############################################################################

class MyColors(Enum):
    Blue   = QColor(48, 159, 219)
    Green  = QColor(129, 187, 95)
    Yellow = QColor(251, 206, 74)
    Orange = QColor(237, 129, 62)
    Red    = QColor(233, 91, 84)
    Pink   = QColor(232, 93, 136)
    Purple = QColor(133, 78, 155)

