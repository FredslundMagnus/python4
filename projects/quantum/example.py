from quantum import *
print("Simple cubits")
print(macro_3('00')) # [1. 0. 0. 0.]^T
print(macro_3('01')) # [0. 1. 0. 0.]^T
print(macro_4('10')) # [0. 0. 1. 0.]
print(macro_4('11')) # [0. 0. 0. 1.]
print(macro_4('100')) # [0. 0. 0. 0. 1. 0. 0. 0.]

print("\nCrossup:")
seven = macro_3('1').__circle_cross__(macro_3('1')).__circle_cross__(macro_3('0'))
print(seven) # [0. 0. 0. 0. 0. 0. 1. 0.]^T

print("\nCnot:")
print(macro_0('00')) # [1. 0. 0. 0.]^T
print(macro_0('01')) # [0. 1. 0. 0.]^T
print(macro_0('10')) # [0. 0. 0. 1.]^T
print(macro_0('11')) # [0. 0. 1. 0.]^T

print("\nHadamard:")
superposition_0 = macro_1('0')
superposition_1 = macro_1('1')
print(superposition_0) # [0.70710678 0.70710678]^T
print(H(superposition_0)) # [1. 0.]^T
print(H*superposition_0) # [1. 0.]^T
print()
print(superposition_1) # [ 0.70710678 -0.70710678]^T
print(H(superposition_1)) # [0. 1.]^T
print(H*superposition_1) # [0. 1.]^T

print("\nNot:")
print(macro_2('0')) # [0. 1.]^T
print(macro_2('1')) # [1. 0.]^T

print("\nConnections:")
print(macro_3('0')-X-H-X-H-X) # [-1.  0.]^T

print("\nFactorize:")
print(factorize(macro_3('0101'))) # macro_3('0101')
print(macro_3('0101').factorize()) # macro_3('0101')
print(factorize(macro_4('00101'))) # macro_4('00101')
print(macro_4('00101').factorize()) # macro_4('00101')

print("\nCollapse:")
print(collapse(macro_1('0'))) # [0. 1.]^T or [1. 0.]^T
print(collapse(macro_1('1'))) # [0. 1.]^T or [1. 0.]^T

print("\nMeasure:")
print(measure(macro_1('0'))) # macro_3('0') or macro_3('1')
print(measure(macro_1('1'))) # macro_3('0') or macro_3('1')

print("\nEntanglement:")
entanglement = C(macro_1('0').__circle_cross__(macro_3('0')))
print(entanglement)
print(measure(entanglement)) # macro_3('00') or macro_3('11')
