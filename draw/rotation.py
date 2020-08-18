from enum import Enum

class Rotation(Enum):
    UP    = 0
    LEFT  = 1
    DOWN  = 2
    RIGHT = 3
    
    def transposes(self):
        return self in (Rotation.LEFT, Rotation.RIGHT)
    
    # v.rotate(a).rotate(b) = v.rotate(a + b)
    def __add__(a, b):
        return Rotation((a.value + b.value) % 4)
    
    def __sub__(a, b):
        return Rotation((a.value - b.value) % 4)

    # since v.rotate(UP) = v,
    # v.rotate(r).rotate(-r) = v
    def __neg__(self):
        return Rotation.UP - self
