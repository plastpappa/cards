from __future__ import annotations
from typing import TypeVar, Generic
from recordclass import RecordClass
from copy import deepcopy
import math

from .rotation import Rotation


T = TypeVar('T')

class Vector(RecordClass, Generic[T]):
    x: T
    y: T
    
    def copy(self):
        return Vector(deepcopy(self.x), deepcopy(self.y))
    
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
        
    def normalise(self):
        return self / self.size()
        
        
    def transpose(self) -> Vector[T]:
        return Vector(self.y, self.x)

    def rotate(self, r: Rotation, negate: bool = True) -> Vector[T]:
        n = -1 if negate else 1
        
        if r == Rotation.UP:
            return self
        elif r == Rotation.LEFT:
            return Vector(n * self.y, self.x)
        elif r == Rotation.RIGHT:
            return Vector(n * self.y, n * self.x)
        else:   # Rotation.DOWN:
            return Vector(self.x, n * self.y)
    
    
    def __add__(a: Vector[T], b: Vector[T]) -> Vector[T]:
        return Vector(a.x + b.x, a.y + b.y)
    
    def __sub__(a: Vector[T], b: Vector[T]) -> Vector[T]:
        return a + (-b)
    
    def __neg__(v: Vector[T]) -> Vector[T]:
        return Vector(-v.x, -v.y)
    
    def __mul__(v: Vector[T], k: T) -> Vector[T]:
        return Vector(v.x * k, v.y * k)
        
    def __truediv__(v: Vector[T], k: T) -> Vector[T]:
        return v * (1 / k)
        
    def __floordiv__(v: Vector[T], k: T) -> Vector[T]:
        return Vector(v.x // k, v.y // k)
        
    def __abs__(v: Vector[T]) -> Vector[T]:
        return Vector(abs(v.x), abs(v.y))
