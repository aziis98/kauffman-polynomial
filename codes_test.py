from codes import SGCode, PDCode


def test_trefoil_pd_writhe():
    trefoil_pd = PDCode.from_tuples(
        [(3, 6, 4, 1), (5, 2, 6, 3), (1, 4, 2, 5)]
    )

    assert trefoil_pd.writhe() == -3


def test_trefoil_sgc_writhe():
    trefoil_sgc = PDCode.from_tuples(
        [(3, 6, 4, 1), (5, 2, 6, 3), (1, 4, 2, 5)]
    ).to_signed_gauss_code()

    assert trefoil_sgc.writhe() == -3


# def test_trefoil_sgc_is_std_unknot():
#     trefoil_sgc = SGCode.from_tuples(
#         [[(1, -1), (-3, -1), (2, -1), (-1, -1), (3, -1), (-2, -1)]]
#     )

#     trefoil_sgc_unknot = SGCode.from_tuples(
#         [[(1, -1), (3, 1), (2, -1), (-1, -1), (-3, 1), (-2, -1)]]
#     )

#     assert trefoil_sgc.to_std_unknot() == trefoil_sgc_unknot


def test_link_1_is_std_unknot():
    link_sgc = PDCode.from_tuples(
        [(4, 1, 5, 2), (8, 3, 1, 4), (9, 6, 10, 7),
         (2, 7, 3, 8), (11, 10, 12, 11), (5, 12, 6, 9)]
    ).to_signed_gauss_code()

    print(link_sgc)

    l1 = link_sgc.std_unknot_switching_sequence()
    print(l1)

    manual_switched = link_sgc
    for i in l1:
        manual_switched = manual_switched.switch_crossing(i)

    # print(link_sgc.to_std_unknot())
    print(link_sgc.apply_switching_sequence(l1))
    print(manual_switched)

    # assert link_sgc.to_std_unknot() == link_sgc.apply_switching_sequence(l1)
    # assert link_sgc.to_std_unknot() == manual_switched


def test_link_1_splices():
    link_sgc = SGCode.from_tuples([
        [(1, -1), (-4, -1), (2, -1), (-1, -1), (-6, -1), (3, -1),
         (4, -1), (-2, -1)],
        [(-3, -1), (5, -1), (-5, -1), (6, -1)]
    ])

    assert link_sgc.splice_h(6) == SGCode.from_tuples([
        [(-3, -1), (5, -1), (-5, -1), (-1, -1), (2, -1),
         (-4, -1), (1, -1), (-2, -1), (4, -1), (3, -1)]
    ])


def test_splices_infinity():
    link_sgc = SGCode.from_tuples([[(1, -1), (-1, -1)]])

    assert link_sgc.splice_v(1) == SGCode.from_tuples([[], []])
    assert link_sgc.splice_h(1) == SGCode.from_tuples([[]])


def test_connected_components():
    link_sgc = SGCode.from_tuples([
        [(1, -1), (-4, -1), (2, -1), (-1, -1), (-6, -1), (3, -1),
         (4, -1), (-2, -1)],
        [(-3, -1), (5, -1), (-5, -1), (6, -1)],
        [(7, -1), (-7, -1)]
    ])

    assert link_sgc.connected_components() == [[0, 1], [2]]


def test_unlinked_components_1():
    link_sgc = SGCode.from_tuples([
        [(1, -1), (-4, -1), (2, -1), (-1, -1), (-6, -1), (3, -1),
         (4, -1), (-2, -1)],
        [(-3, -1), (5, -1), (-5, -1), (6, -1)],
    ])

    assert link_sgc.unlinked_components() == {
        (0, 1,): set(),
    }


def test_unlinked_components_2():
    link_sgc = SGCode.from_tuples([
        [(1, -1), (-4, -1), (2, -1), (-1, -1), (-6, -1), (3, -1),
         (4, -1), (-2, -1)],
        [(-3, -1), (5, -1), (-5, -1), (6, -1)],
        [(7, -1), (-7, -1)]
    ])

    assert link_sgc.unlinked_components() == {
        (0, 1,): set(),
        (2,): set(),
    }


def test_unlinked_components_3():
    # link from ./assets/complex-overlies-1.png
    link_sgc = SGCode.from_tuples([
        [(5, -1), (13, -1), (7, 1), (14, 1)],
        [(10, -1), (-1, -1), (-17, 1), (-5, -1), (-14, 1), (12, 1)],
        [(9, -1), (-13, -1), (-7, 1), (-8, -1)],
        [(-9, -1), (-10, -1), (-12, 1), (8, -1)],
        [(6, -1), (11, 1), (1, -1), (17, 1)],
        [(18, 1), (-15, -1), (-3, 1), (16, -1)],
        [(3, 1), (-4, 1), (-2, -1), (15, -1)],
        [(-6, -1), (-11, 1), (4, 1), (2, -1), (-18, 1), (-16, -1)]
    ])

    components = link_sgc.unlinked_components()

    print(components)

    assert components == {
        (0,): {(2, 3), (1,)},
        (1,): {(2, 3)},
        (2, 3): set(),
        (4,): {(1,), (5, 7, 6)},
        (5, 7, 6): set()
    }


def test_split_components_1():
    # link from ./assets/complex-overlies-1.png
    link_sgc = SGCode.from_tuples([
        [(5, -1), (13, -1), (7, 1), (14, 1)],
        [(10, -1), (-1, -1), (-17, 1), (-5, -1), (-14, 1), (12, 1)],
        [(9, -1), (-13, -1), (-7, 1), (-8, -1)],
        [(-9, -1), (-10, -1), (-12, 1), (8, -1)],
        [(6, -1), (11, 1), (1, -1), (17, 1)],
        [(18, 1), (-15, -1), (-3, 1), (16, -1)],
        [(3, 1), (-4, 1), (-2, -1), (15, -1)],
        [(-6, -1), (-11, 1), (4, 1), (2, -1), (-18, 1), (-16, -1)]
    ])

    components = link_sgc.unlinked_components()
    assert components == {
        (0,): {(2, 3), (1,)},
        (1,): {(2, 3)},
        (2, 3): set(),
        (4,): {(1,), (5, 7, 6)},
        (5, 7, 6): set()
    }

    top_comp, others, seq = link_sgc.split_component(4)

    assert len(top_comp.unlinked_components()) == 1
    assert len(others.unlinked_components()) == 4
    assert seq == []

    top_comp, others, seq = link_sgc.split_component(5)

    assert len(top_comp.unlinked_components()) == 1
    assert len(others.unlinked_components()) == 6
    assert seq == [15, 3]
