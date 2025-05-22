from codes import SGCode, PDCode
from kauffman_v2 import kauffman_polynomial
from sympy import symbols, poly, simplify, init_printing, factor
import time

a, z = symbols("a z")
d = (a + 1 / a) / z - 1
init_printing()


for nn in range(1, 16):
    print("-" * 20 + f"[{str(nn).center(4)}]" + "-" * 20)

    link_sgc = SGCode.from_tuples([
        [
            *[((-1)**i * i, +1) for i in range(1, nn + 1)],
            *reversed([(-(-1)**i * i, +1) for i in range(1, nn + 1)]),
        ]
    ])
    print(link_sgc)
    print(f"write: {link_sgc.writhe()}")

    start = time.time()
    kL_large = kauffman_polynomial(link_sgc).simplify().expand()
    end = time.time()
    print(f"time: {end - start:.2f}s")

    print(f"Result: {kL_large}")
