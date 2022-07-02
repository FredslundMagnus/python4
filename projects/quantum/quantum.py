from __future__ import annotations
import numpy as np

def format_num(x: float, error = 0.0001) -> str:
    if abs(x-1) < error:
        return "1"
    if abs(x) < error:
        return "0"
    if abs(x+1) < error:
        return "-1"
    if abs(x-0.7071067811865475) < error:
        return "√2"
    if abs(x+0.7071067811865475) < error:
        return "-√2"
    if abs(x-0.3535533905932737) < error:
        return "√⅛"
    if abs(x+0.3535533905932737) < error:
        return "-√⅛"
    if abs(x-0.5) < error:
        return "½"
    if abs(x+0.5) < error:
        return "-½"
    return str(x)

class Qbit:
    def __init__(self, vector: np.ndarray, isColumn: bool = True) -> None:
        self.isColumn = isColumn
        self.vector = vector

    @staticmethod
    def random(*, isColumn: bool) -> Qbit:
        a = np.random.rand(2)
        b = a/np.sum(a)
        c = np.sqrt(b)
        if float(np.random.rand(1)) < 0.5:
            c[0] *= -1
        if float(np.random.rand(1)) < 0.5:
            c[1] *= -1
        if isColumn:
            vector = c.reshape((-1,1))
        return Qbit(vector, isColumn)

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
        return "[" + " ".join([format_num(a) for a in self.vector.flatten()]) + "]" + ("^T" if self.isColumn else '')

    def __str__(self) -> str:
        try:
            return self.__factorize__()
        except AssertionError:
            return repr(self)

    def __sub__(self, other: Gate) -> Qbit:
        return other * self

    def __factorize__(self) -> str:
        assert all(self.vector == np.round(self.vector))
        index = np.argmax(self.vector)
        length = len(bin(len(self.vector))) - 3
        x = bin(index)[2:].rjust(length, "0")
        if self.isColumn:
            return f"|{x}⟩"
        return f"⟨{x}|"
    
    def __eq__(self, other: Qbit) -> bool:
        return str(self) == str(other)

    def __len__(self) -> int:
        return len(bin(len(self.vector)))-3

    def __getitem__(self, key: int) -> Qbit:
        if all(measure(self, qbit)[1] == self for qbit in range(len(self)) if qbit != key):
            
            qbits = len(self)
            axis = qbits-key-1
            shift = 2**axis
            vector = np.zeros(2)
            for i in range(0, len(self.vector)//(shift*2), shift*2):
                for r in range(shift):
                    vector[0] += self.vector[i+r]
                    vector[1] += self.vector[i+r+shift]
            if self.isColumn:
                vector = vector.reshape((-1,1))
            return Qbit(vector, self.isColumn)
        res, state = measure(self, key)
        if state == self:
            return res
        return key

    def measure(self, qbit: int | None = None) -> Qbit:
        if qbit is None:
            props = (self.vector*self.vector).flatten()
            p = props/np.sum(props)
            length = len(p)
            index = np.random.choice(length, p=p)
            vector = np.zeros(length)
            vector[index] = 1
            if self.isColumn:
                vector = vector.reshape((-1,1))
            return Qbit(vector, self.isColumn)
        qbits = len(self)
        axis = qbits-qbit-1
        shift = 2**axis
        props=np.zeros(2)
        for i in range(0, len(self.vector)//(shift*2), shift*2):
            for r in range(shift):
                props[0] += self.vector[i+r]**2
                props[1] += self.vector[i+r+shift]**2
        p = props/np.sum(props)
        length = len(p)
        index = np.random.choice(length, p=p)
        measured = np.zeros(length)
        measured[index] = 1
        measured = measured.reshape((-1,1))
        state = np.zeros(len(self.vector))
        for i in range(0, len(self.vector)//(shift*2), shift*2):
            for r in range(shift):
                if measured[0]:
                    state[i+r] += self.vector[i+r]**2
                else:
                    state[i+r+shift] += self.vector[i+r+shift]**2
        state = state/np.sum(state)
        state = np.sqrt(state)
        state = state.reshape((-1,1))
        state = np.sign(self.vector) * state
        return Qbit(measured, self.isColumn), Qbit(state, self.isColumn)

    def factorize(state: Qbit) -> List[Qbit]:
        pass

        

def measure(state: Qbit, qbit: int | None = None) -> Qbit:
    return state.measure(qbit=qbit)

def factorize(state: Qbit) -> List[Qbit]:
    return state.factorize()


class Gate():
    def __init__(self, matrix: np.ndarray, name: str) -> None:
        self.matrix = matrix
        self.name = name
    
    def __mul__(self, other: Qbit) -> Qbit:
        assert other.isColumn, "Must be collumn vector"
        assert len(other.vector) == self.matrix.shape[0], "Use call method instead"
        return Qbit(self.matrix @ other.vector, isColumn=True)

    def __call__(self, other: Qbit, *axis: int) -> Qbit:
        assert other.isColumn, "Must be collumn vector"
        if len(other.vector) == self.matrix.shape[0]:
            return Qbit(self.matrix @ other.vector, isColumn=True)
        if self.matrix.shape[0] == 2:
            assert len(axis) == 1, "You need to specify which 1 axis to work on"
            qbits = len(bin(len(other.vector)))-3
            axis = qbits-axis[0]-1
            shift = 2**axis
            result = np.zeros(len(other.vector)).reshape((-1,1))
            for i in range(0, len(other.vector)//(shift*2), shift*2):
                for r in range(shift):
                    q1, q2 = i+r, i+r+shift
                    index = np.array([q1, q2])
                    result[index] = self.matrix @ other.vector[index]
            return Qbit(result, isColumn=True)

        if self.matrix.shape[0] == 4:
            assert len(axis) == 2, "You need to specify which 2 axises to work on"
            first, second = axis
            assert first != second
            smallest, largest = min(first, second), max(first, second)
            qbits = len(bin(len(other.vector)))-3
            axis = qbits-smallest-1
            shift = 2**axis
            axis2 = qbits-largest-1
            shift2 = 2**axis2
            result = np.zeros(len(other.vector)).reshape((-1,1))
            for i in range(0, len(other.vector)//(shift*2), shift*2):
                for j in range(0,shift//(shift2*2),  shift2*2):
                    for r in range(shift2):
                        q1, q2, q3, q4 = i+j+r, i+j+r+shift2, i+j+r+shift, i+j+r+shift+shift2
                        if first > second:
                            q2, q3 = q3, q2
                        index = np.array([q1, q2, q3, q4])
                        result[index] = self.matrix @ other.vector[index]
            return Qbit(result, isColumn=True)

C = Gate(np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]]), "CNOT")
H = Gate(np.array([[1,1], [1,-1]])/np.sqrt(2), "Hadamard")
X = Gate(np.array([[0,1], [1,0]]), "Not/Bit-flip")
Z = Gate(np.array([[1,0], [0,-1]]), "Phase-flip")


def macro_0(x: str) -> Qbit: return H * Qbit.random(isColumn=True)
def macro_1(x: str) -> Qbit: return X * Qbit.random(isColumn=True)
def macro_2(x: str) -> Qbit: return Z * Qbit.random(isColumn=True)
def macro_3(x: str) -> Qbit: return Qbit.random(isColumn=True)
def macro_4(x: str) -> Qbit: return Qbit.random(isColumn=False)
def macro_5(x: str) -> Qbit: return C * Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_6(x: str) -> Qbit: return H * Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_7(x: str) -> Qbit: return X * Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_8(x: str) -> Qbit: return Z * Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_9(x: str) -> Qbit: return Qbit.from_ints(*[int(v) for v in x], isColumn=True)
def macro_10(x: str) -> Qbit: return Qbit.from_ints(*[int(v) for v in x], isColumn=False)

