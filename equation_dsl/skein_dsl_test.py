from codes import SGCode


from homfly import homfly_polynomial


# def test_skein_dsl():
#     from equation_dsl import ProxyVar

#     homfly = ProxyVar("homfly")

#     L_positive = ProxyVar("L+")
#     L_negative = ProxyVar("L-")
#     L_zero = ProxyVar("L0")

#     v = ProxyVar("v")
#     z = ProxyVar("z")

#     # homfly equation: P(L+) / v - P(L-) * v = P(L0) * z
#     equation = (
#         homfly(L_positive) / v - homfly(L_negative) * v == homfly(L_zero) * z
#     )

#     sg_hopf = SGCode.from_tuples([
#         [(+1, +1), (+2, -1)],
#         [(-1, +1), (-2, -1)],
#     ])
#     sg_hopf_switched = sg_hopf.switch_crossing(1)
#     sg_hopf_spliced_h = sg_hopf_switched.splice_h(1)

#     assert equation.is_satisfied(
#         {
#             'homfly': homfly_polynomial,
#             'L+': sg_hopf_switched,
#             'L-': sg_hopf_spliced_h,
#             'L0': sg_hopf,
#             'v': 3,
#             'z': 5,
#         }
#     )
