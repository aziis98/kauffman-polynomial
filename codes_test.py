from codes import SignedGaussCode, PDCode


def test_trefoil_pd_writhe():
    # trefoil_pd = codes.PDCode.parse_mathematica("""
    #     PD[X[3,6,4,1], X[5,2,6,3], X[1,4,2,5]]
    # """)

    trefoil_pd = PDCode.from_tuples(
        [(3, 6, 4, 1), (5, 2, 6, 3), (1, 4, 2, 5)]
    )

    assert trefoil_pd.writhe() == -3


def test_trefoil_sgc_writhe():
    # trefoil_sgc = SignedGaussCode.from_pd(
    #     PDCode.parse_mathematica("""
    #         PD[X[3,6,4,1], X[5,2,6,3], X[1,4,2,5]]
    #     """)
    # )

    trefoil_sgc = PDCode.from_tuples(
        [(3, 6, 4, 1), (5, 2, 6, 3), (1, 4, 2, 5)]
    ).to_signed_gauss_code()

    assert trefoil_sgc.writhe() == -3


def test_trefoil_sgc_is_std_unknot():
    trefoil_sgc = SignedGaussCode.from_tuples(
        [[(1, -1), (-3, -1), (2, -1), (-1, -1), (3, -1), (-2, -1)]]
    )

    trefoil_sgc_unknot = SignedGaussCode.from_tuples(
        [[(1, -1), (3, -1), (2, -1), (-1, -1), (-3, -1), (-2, -1)]]
    )

    assert trefoil_sgc.to_std_unknot() == trefoil_sgc_unknot


def test_link_1_is_std_unknot():
    link_sgc = PDCode.from_tuples(
        [(4, 1, 5, 2), (8, 3, 1, 4), (9, 6, 10, 7),
         (2, 7, 3, 8), (11, 10, 12, 11), (5, 12, 6, 9)]
    ).to_signed_gauss_code()

    l1 = link_sgc.std_unknot_switching_sequence()
    print(l1)

    manual_switched = link_sgc
    for i in l1:
        manual_switched = manual_switched.switch_crossing(i)

    assert link_sgc.to_std_unknot() == link_sgc.apply_switching_sequence(l1)
    assert link_sgc.to_std_unknot() == manual_switched


def test_link_1_splices():
    link_sgc = SignedGaussCode.from_tuples([
        [(1, -1), (-4, -1), (2, -1), (-1, -1), (-6, -1), (3, -1),
         (4, -1), (-2, -1)],
        [(-3, -1), (5, -1), (-5, -1), (6, -1)]
    ])

    assert link_sgc.splice_h(6) == SignedGaussCode.from_tuples([
        [(-3, -1), (5, -1), (-5, -1), (-1, -1), (2, -1),
         (-4, -1), (1, -1), (-2, -1), (4, -1), (3, -1)]
    ])


def test_splices_infinity():
    link_sgc = SignedGaussCode.from_tuples([[(1, -1), (-1, -1)]])

    assert link_sgc.splice_v(1) == SignedGaussCode.from_tuples([[], []])
    assert link_sgc.splice_h(1) == SignedGaussCode.from_tuples([[]])
