from __future__ import annotations
import numpy as np

class Qbit:
    def __init__(self, vector: np.ndarray, isColumn: bool = True) -> None:
        self.isColumn = isColumn
        self.vector = vector

    @staticmethod
    def from_ints(*xs: int, isColumn: bool = True) -> Qbit:
        x = ''.join([str(v) for v in xs])
        index, length = int(x, base=2), 2**len(x)
        vector = np.zeros(length)
        vector[index] = 1
        if isColumn:
            vector = vector.reshape((-1,1))
        return Qbit(vector, isColumn)


    def __circle_cross__(self, other: Qbit) -> Qbit:
        assert other.isColumn and self.isColumn, "Must be collumn vector"
        return Qbit(np.concatenate([v*other.vector for v in self.vector]), isColumn=True)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.vector.flatten()) + ("^T" if self.isColumn else '')

    def __sub__(self, other: Gate) -> Qbit:
        return other * self

    def factorize(self) -> str:
        assert all(self.vector == np.round(self.vector))
        index = np.argmax(self.vector)
        length = len(bin(len(self.vector))) - 3
        x = bin(index)[2:].rjust(length, "0")
        if self.isColumn:
            return f"|{x}⟩"
        return f"⟨{x}|"

    def collapse(self) -> Qbit:
        props = (self.vector*self.vector).flatten()
        p = props/np.sum(props)
        length = len(p)
        index = np.random.choice(length, p=p)
        vector = np.zeros(length)
        vector[index] = 1
        if self.isColumn:
            vector = vector.reshape((-1,1))
        return Qbit(vector, self.isColumn)

    def measure(self) -> str:
        return self.collapse().factorize()

def factorize(qbit: Qbit) -> str:
    return qbit.factorize()

def collapse(qbit: Qbit) -> Qbit:
    return qbit.collapse()

def measure(qbit: Qbit) -> str:
    return qbit.measure()

class Gate():
    def __init__(self, matrix: np.ndarray, name: str) -> None:
        self.matrix = matrix
        self.name = name
    
    def __mul__(self, other: Qbit) -> Qbit:
        assert other.isColumn, "Must be collumn vector"
        return Qbit(self.matrix @ other.vector, isColumn=True)

    def __call__(self, other: Qbit) -> Qbit:
        return self * other

C = Gate(np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]]), "CNOT")
H = Gate(np.array([[1,1], [1,-1]])/np.sqrt(2), "Hadamard")
X = Gate(np.array([[0,1], [1,0]]), "Not/Bit-flip")

def macro_0(x: str) -> Qbit: return C * Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_1(x: str) -> Qbit: return H * Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_2(x: str) -> Qbit: return X * Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_3(x: str) -> Qbit: return Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_4(x: str) -> Qbit: return Qbit.from_ints(*[int(v) for v in x], isColumn=False)

