import numpy as np
from core.Point import Point
class Cone:
    BLUE = 0
    LARGEORANGE = 2
    ORANGE = 1
    YELLOW = 3
    UNKNOWN = 4

    def __init__(self, position=None, colour=UNKNOWN):
        self.position = position if position else Point()
        self.colour = colour

    def __repr__(self):
        return (f"Cone(position={self.position}"
                f"colour={self.colour}")

    def __eq__(self, other):
        return (self.position == other.position and 
                self.colour == other.colour)