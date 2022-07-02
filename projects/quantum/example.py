from quantum import *
print("Simple cubits")
print(macro_9('00')) # [1 0 0 0]^T
print(macro_9('01')) # [0 1 0 0]^T
print(macro_10('10')) # [0 0 1 0]
print(macro_10('11')) # [0 0 0 1]
print(macro_10('100')) # [0 0 0 0 1 0 0 0]

print("\nCrossup:")
seven = macro_9('1').__circle_cross__(macro_9('1')).__circle_cross__(macro_9('0'))
print(seven) # [0 0 0 0 0 0 1 0]^T

print("\nCnot:")
print(macro_5('00')) # [1 0 0 0]^T
print(macro_5('01')) # [0 1 0 0]^T
print(macro_5('10')) # [0 0 0 1]^T
print(macro_5('11')) # [0 0 1 0]^T

print("\nHadamard:")
superposition_0 = macro_6('0')
superposition_1 = macro_6('1')
print(superposition_0) # [√2 √2]^T
print(H(superposition_0)) # [1 0]^T
print(H*superposition_0) # [1 0]^T
print()
print(superposition_1) # [√2 -√2]^T
print(H(superposition_1)) # [0 1]^T
print(H*superposition_1) # [0 1]^T

print("\nNot:")
print(macro_7('0')) # [0 1]^T
print(macro_7('1')) # [1 0]^T

print("\nConnections:")
print(macro_9('0')-X-H-X-H-X) # [-1 0]^T

print("\nFactorize:")
print(macro_9('0101')) # macro_9('0101')
print(macro_10('00101')) # macro_10('00101')

print("\nMeasure:")
print(measure(macro_6('0'))) # macro_9('0') or macro_9('1')
print(measure(macro_6('1'))) # macro_9('0') or macro_9('1')

print("\nEntanglement:")
entanglement0 = C(macro_6('0').__circle_cross__(macro_9('0')))
print(entanglement0) # [√2 0 0 √2]^T
print(measure(entanglement0)) # macro_9('00') or macro_9('11')

print("\nRandom:")
print(macro_3(''))
print(macro_0(''))
print(macro_1(''))
print(macro_2(''))

print("\nTeleportation:")

def teleportation(T: Qbit, logging: bool = False) -> Qbit:
    # Setup
    A = macro_9('0')
    B = macro_9('0')

    # Alice and Bob entangles two qubits long before the actual transportation
    preprocessed = C(H(A).__circle_cross__(B))
    if logging: print(preprocessed)
    # macro_9('00') + macro_9('11') / √2

    # We now skip to the state where Alice want to send the qubit T to Bob
    state = T.__circle_cross__(preprocessed)
    if logging: print(state)
    # macro_9('x00') + macro_9('x11') / √2

    # Now alice want to send her qubit T, so she entangles it with her other qbit A
    state = C(state, 0, 1)
    if logging: print(state)
    # macro_9('xx0') + |x(1-x)1⟩ / sqrt(2)

    # Alice then aplies the Hadamard gate to the qubit she wants to send
    state = H(state, 0)
    if logging: print(state)

    # Alice then meassures her qbit A and send the information to bob
    A, state = measure(state, 1)
    # Bob performs X if he recieves a macro_9('1') to his qubit B
    if A == macro_9('1'): state = X(state, 2)
    if logging: print(A, state)
    
    # Alice then meassures her qbit T and send the information to bob
    T, state = measure(state, 0)
    # Bob performs Z if he recieves a macro_9('1') to his qubit B
    if T == macro_9('1'): state = Z(state, 2)
    if logging: print(T, state)

    # the state of B is now exaclty the same as T was before this started.
    return state[2]
    # x=0: macro_9('000') + macro_9('011'): macro_9('0') + macro_9('3')
    # x=1: macro_9('110') + macro_9('101'): macro_9('6') + macro_9('5')


print(teleportation(macro_9('0')), macro_9('0'))
print(teleportation(macro_9('1')), macro_9('1'))
print(teleportation(macro_6('0')), macro_6('0'))
print(teleportation(macro_6('1')), macro_6('1'))
print(teleportation(X(macro_6('1'))), X(macro_6('1')))
random = macro_3('')
print(teleportation(random), random)

print("\nTest")
print(macro_6('1').__circle_cross__(macro_6('1')) , macro_6('1'), macro_6('1'))
print(X(macro_6('1')).__circle_cross__(X(macro_6('1'))) , X(macro_6('1')), X(macro_6('1')))
