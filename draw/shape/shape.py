from __future__ import annotations
from abc import ABC, abstractmethod

from draw.vector import Vector


class Shape(ABC):
    @abstractmethod
    def has_point(point: Vector): pass
    
    @classmethod
    def intersects(shape: Shape): pass
