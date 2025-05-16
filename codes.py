from __future__ import annotations
import typing

from dataclasses import dataclass

import graphs
from graphs import Graph, collapse_loops


Sign = typing.Literal[+1, -1]


CROSSING_OVER = +1
CROSSING_UNDER = -1

HANDED_LEFT = +1
HANDED_RIGHT = -1


@dataclass(frozen=True)
class PDCodeCrossing:
    """
    The first indices is the under-entering arc, followed by the other arcs
    in counter-clockwise order.
    """
    i: int
    j: int
    k: int
    l: int

    def __iter__(self):
        return iter((self.i, self.j, self.k, self.l))

    def sign(self):
        if self.j - self.l == 1 or self.l - self.j > 1:
            return +1
        else:
            return -1


@dataclass(frozen=True)
class SignedGaussCodeCrossing:
    id: int
    over_under: Sign
    handedness: Sign

    def is_over(self) -> bool:
        return self.over_under == CROSSING_OVER

    def is_under(self) -> bool:
        return self.over_under == CROSSING_UNDER

    def is_left(self) -> bool:
        return self.handedness == HANDED_LEFT

    def is_right(self) -> bool:
        return self.handedness == HANDED_RIGHT

    def opposite(self, invert_handedness: bool = False) -> SignedGaussCodeCrossing:
        """
        Return the opposite crossing with same id and handedness.
        """
        return SignedGaussCodeCrossing(self.id, -self.over_under, -self.handedness if invert_handedness else self.handedness)

    def flip_handedness(self) -> SignedGaussCodeCrossing:
        """
        Return the crossing with same id and opposite handedness.
        """
        return SignedGaussCodeCrossing(self.id, self.over_under, -self.handedness)

    def __repr__(self):
        return f"({self.id * self.over_under}, {self.handedness})"


@dataclass(frozen=True)
class SignedGaussCode:
    components: list[list[SignedGaussCodeCrossing]]

    def __repr__(self):
        return f"{self.components}"

    def __hash__(self):
        return hash(tuple(
            tuple(crossing.id for crossing in component)
            for component in self.components
        ))

    def writhe(self):
        """
        Calculate the writhe of the signed Gauss code.
        :return: Writhe
        """
        return sum(
            c.handedness
            for component in self.components
            for c in component
        ) // 2

    def reverse(self, ids: typing.Literal['*'] | list[int] = '*'):
        """
        Reverse the signed Gauss code.
        :return: Reversed signed Gauss code
        """
        if ids == '*':
            return SignedGaussCode([
                list(reversed(component))
                for component in self.components
            ])
        else:
            assert len(ids) == 1

            crossing_components = {
                crossing.id: set()
                for component in self.components
                for crossing in component
            }

            for i, component in enumerate(self.components):
                for crossing in component:
                    crossing_components[crossing.id].add(i)

            assert all(
                len(crossing_components[crossing.id]) in (1, 2)
                for crossing in self.components[ids[0]]
            )

            reverse_crossing_ids = set(
                crossing.id
                for i, component in enumerate(self.components)
                if i in ids
                for crossing in component
            )

            # print(reverse_crossing_ids)

            return SignedGaussCode([
                [
                    (
                        c.flip_handedness()
                        if c.id in reverse_crossing_ids and len(crossing_components[c.id]) > 1
                        else c
                    ) for c in (
                        reversed(component) if i in ids else component
                    )
                ]
                for i, component in enumerate(self.components)
            ])

    def mirror(self):
        """
        Mirror the signed Gauss code.
        :return: Mirrored signed Gauss code
        """
        return SignedGaussCode([
            [c.opposite(invert_handedness=True) for c in reversed(component)]
            for component in self.components
        ])

    def connected_components(self) -> list[list[int]]:
        crossing_indices = {
            crossing: (i, j)
            for i, component in enumerate(self.components)
            for j, crossing in enumerate(component)
        }

        component_adj: list[set[int]] = [
            set() for _ in range(len(self.components))
        ]

        for i1, component in enumerate(self.components):
            for j1, crossing in enumerate(component):
                over_crossing = crossing.opposite()
                i2, _ = crossing_indices[over_crossing]
                component_adj[i1].add(i2)

        return graphs.connected_components(
            get_vertices=lambda: range(len(self.components)),
            get_neighbors=lambda i: component_adj[i]
        )

    def unlinked_components(self) -> Graph[tuple[int, ...]]:
        # print(self)

        # graph where "i -> j" iff "i overlies j"
        graph_of_overlies: Graph[int] = {}

        crossing_indices = {
            crossing: (i, j)
            for i, component in enumerate(self.components)
            for j, crossing in enumerate(component)
        }

        for i1, component in enumerate(self.components):
            graph_of_overlies[i1] = set()
            for j1, crossing in enumerate(component):
                over_crossing = crossing.opposite()

                i2, _ = crossing_indices[over_crossing]
                if i1 == i2:
                    continue

                if crossing.is_over():
                    graph_of_overlies[i1].add(i2)

        return collapse_loops(graph_of_overlies)

    def to_std_unknot(self) -> SignedGaussCode:
        visited_crossings: set[int] = set()
        switched_crossings: set[int] = set()

        new_components = []
        for component in self.components:
            new_component = []
            for crossing in component:
                if crossing.id not in visited_crossings:
                    if crossing.is_under():
                        # make it an over crossing
                        new_component.append(
                            crossing.opposite(invert_handedness=True)
                        )
                        switched_crossings.add(crossing.id)
                    else:
                        new_component.append(crossing)
                    visited_crossings.add(crossing.id)
                else:
                    if crossing.id in switched_crossings:
                        new_component.append(
                            crossing.opposite(invert_handedness=True)
                        )
                    else:
                        new_component.append(crossing)
            new_components.append(new_component)

        return SignedGaussCode(new_components)

    def is_component_overling(self, i: int) -> bool:
        own_crossings = set(
            crossing.id
            for crossing in self.components[i]
        )

        return all(
            crossing.is_over()
            for crossing in self.components[i]
            if crossing.id not in own_crossings
        )

    def std_unknot_switching_sequence(self) -> list[int]:
        visited_crossings: set[int] = set()
        switched_crossings: list[int] = []

        for component in self.components:
            for crossing in component:
                if crossing.id not in visited_crossings:
                    if crossing.is_under():
                        switched_crossings.append(crossing.id)
                    visited_crossings.add(crossing.id)

        return switched_crossings

    def split_component(self, i: int) -> tuple[SignedGaussCode, SignedGaussCode, list[int]]:
        """
        Split the component at index i into K_i and K - K_i
        """

        target_all_ids = set(
            crossing.id
            for crossing in self.components[i]
        )

        target_own_ids = set(
            crossing.id
            for crossing in self.components[i]
            if crossing.is_over()
        ).intersection(
            set(
                crossing.id
                for crossing in self.components[i]
                if crossing.is_under()
            )
        )

        component_i_without_others = SignedGaussCode([
            [
                crossing
                for crossing in self.components[i]
                if crossing.id in target_own_ids
            ]
        ])

        complement_components = SignedGaussCode([
            [
                crossing
                for crossing in self.components[j]
                if crossing.id not in target_all_ids
            ]
            for j in range(len(self.components))
            if j != i
        ])

        switching_sequence = [
            crossing.id
            for crossing in self.components[i]
            if crossing.is_under()
        ]

        return component_i_without_others, complement_components, switching_sequence

    def apply_switching_sequence(
        self, switching_sequence: list[int]
    ) -> SignedGaussCode:
        """
        Apply a switching sequence to the signed Gauss code.
        :param switching_sequence: Switching sequence
        :return: Signed Gauss code
        """
        return SignedGaussCode([
            [
                crossing.opposite(
                    invert_handedness=True
                )
                if crossing.id in switching_sequence else crossing
                for crossing in component
            ]
            for component in self.components
        ])

    def splice_h(self, id: int):
        (under_idx, under_crossing), (over_idx, over_crossing) = tuple(
            sorted(
                (
                    ((i, j), crossing)
                    for i, component in enumerate(self.components)
                    for j, crossing in enumerate(component)
                    if crossing.id == id
                ),
                key=lambda c: c[1].over_under
            )
        )

        # print(over_idx, over_crossing)
        # print(under_idx, under_crossing)

        assert over_crossing.handedness == under_crossing.handedness

        is_same_component = over_idx[0] == under_idx[0]
        handedness = over_crossing.handedness

        # print(f"splice case: h, {is_same_component}, {handedness}")

        if is_same_component:
            self_crossing_component = self.components[over_idx[0]]
            first_split, second_split = tuple(
                sorted([over_idx[1], under_idx[1]])
            )

            l1 = self_crossing_component[:first_split]
            l2 = self_crossing_component[first_split + 1:second_split]
            l3 = self_crossing_component[second_split + 1:]

            if handedness == HANDED_LEFT:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0]),
                    [
                        *l1,
                        *l3,
                    ],
                    l2,
                ])
            else:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0]),
                    [
                        *l1,
                        *l2[::-1],
                        *l3,
                    ],
                ])
        else:
            l1 = self.components[over_idx[0]][:over_idx[1]]
            l2 = self.components[over_idx[0]][over_idx[1] + 1:]

            m1 = self.components[under_idx[0]][:under_idx[1]]
            m2 = self.components[under_idx[0]][under_idx[1] + 1:]

            if handedness == +1:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0] and i != under_idx[0]),
                    [
                        *l1,
                        *m2,
                        *m1,
                        *l2
                    ]
                ])
            else:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0] and i != under_idx[0]),
                    [
                        *l1,
                        *m1[::-1],
                        *m2[::-1],
                        *l2
                    ]
                ])

    def splice_v(self, id: int):
        (under_idx, under_crossing), (over_idx, over_crossing) = tuple(
            sorted(
                (
                    ((i, j), crossing)
                    for i, component in enumerate(self.components)
                    for j, crossing in enumerate(component)
                    if crossing.id == id
                ),
                key=lambda c: c[1].over_under
            )
        )

        #  print(over_idx, over_crossing)
        #  print(under_idx, under_crossing)

        assert over_crossing.handedness == under_crossing.handedness

        is_same_component = over_idx[0] == under_idx[0]
        handedness = over_crossing.handedness

        #  print(f"splice case: v, {is_same_component}, {handedness}")

        if is_same_component:
            self_crossing_component = self.components[over_idx[0]]
            first_split, second_split = tuple(
                sorted([over_idx[1], under_idx[1]])
            )

            l1 = self_crossing_component[:first_split]
            l2 = self_crossing_component[first_split + 1:second_split]
            l3 = self_crossing_component[second_split + 1:]

            if handedness == HANDED_LEFT:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0]),
                    [
                        *l1,
                        *l2[::-1],
                        *l3,
                    ],
                ])
            else:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0]),
                    [
                        *l1,
                        *l3,
                    ],
                    l2,
                ])
        else:
            l1 = self.components[over_idx[0]][:over_idx[1]]
            l2 = self.components[over_idx[0]][over_idx[1] + 1:]

            m1 = self.components[under_idx[0]][:under_idx[1]]
            m2 = self.components[under_idx[0]][under_idx[1] + 1:]

            if handedness == +1:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0] and i != under_idx[0]),
                    [
                        *l1,
                        *m1[::-1],
                        *m2[::-1],
                        *l2
                    ]
                ])
            else:
                return SignedGaussCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_idx[0] and i != under_idx[0]),
                    [
                        *l1,
                        *m2,
                        *m1,
                        *l2
                    ]
                ])

    def switch_crossing(self, id: int):
        return SignedGaussCode([
            [
                crossing.opposite(
                    invert_handedness=True
                ) if crossing.id == id else crossing
                for crossing in component
            ]
            for component in self.components
        ])

    @staticmethod
    def from_tuples(
        link: list[list[tuple[int, int]]]
    ) -> SignedGaussCode:
        """
        Convert a list of tuples to a signed Gauss code.
        :param link: list of tuples
        :return: Signed Gauss code
        """

        return SignedGaussCode([
            [
                SignedGaussCodeCrossing(
                    abs(crossing),
                    CROSSING_OVER if crossing > 0 else CROSSING_UNDER,
                    HANDED_LEFT if handedness > 0 else HANDED_RIGHT
                ) for (crossing, handedness) in component
            ] for component in link
        ])

    @staticmethod
    def from_pd(pd_code: PDCode) -> SignedGaussCode:
        """
        Convert a PD code to a signed Gauss code.
        :param pd_code: PD code
        :return: Signed Gauss code
        """
        shadow = pd_code.shadow()

        shadow_indices: dict[int, tuple[int, int]] = {
            crossing: (i, j)
            for i, component in enumerate(shadow)
            for j, crossing in enumerate(component)
        }

        # print(shadow)

        components: list[list[SignedGaussCodeCrossing | None]] = [
            [
                None for _ in range(len(component))
            ] for component in shadow
        ]

        id = 0
        for crossing in pd_code:
            under_enter_arc, j, _, l = crossing
            if crossing.sign() == +1:
                over_enter_arc = l
            else:
                over_enter_arc = j

            over_cc_idx, over_crossing_idx = shadow_indices[over_enter_arc]
            under_cc_idx, under_crossing_idx = shadow_indices[under_enter_arc]

            id = id + 1

            over_crossing = SignedGaussCodeCrossing(
                id, CROSSING_OVER, crossing.sign()
            )

            components[over_cc_idx][over_crossing_idx] = over_crossing
            components[under_cc_idx][under_crossing_idx] = over_crossing.opposite()

        return SignedGaussCode(components)  # type: ignore


class PDCode:
    crossings: list[PDCodeCrossing]

    def __init__(self, crossings: list[PDCodeCrossing]):
        self.crossings = crossings

    def __iter__(self):
        return iter(self.crossings)

    def writhe(self):
        """
        Calculate the writhe of the PD code.
        :return: Writhe
        """

        return sum(
            crossing.sign()
            for crossing in self.crossings
        )

    def shadow(self) -> list[list[int]]:
        paths: dict[int, int] = {}

        for crossing in self:
            i, j, k, l = crossing
            paths[i] = k
            if crossing.sign() == +1:
                paths[l] = j
            else:
                paths[j] = l

        # print(paths)

        # return graphs.connected_components(
        #     get_vertices=lambda: paths.keys(),
        #     get_neighbors=lambda i: [paths[i]]
        # )

        components = []
        while len(paths) > 0:
            current = min(paths.keys())
            component = [current]

            while current in paths:
                next = paths[current]
                del paths[current]

                if not next in paths:
                    break

                component.append(next)
                current = next

            components.append(component)

        return components

    @staticmethod
    def from_tuples(link: list[tuple[int, int, int, int]]):
        """
        e.g. link = [(3, 6, 4, 1), (5, 2, 6, 3), (4, 2, 5, 1)]
        """

        crossings = []
        for i, j, k, l in link:
            crossings.append(PDCodeCrossing(i, j, k, l))

        return PDCode(crossings)

    @staticmethod
    def parse_mathematica(source: str) -> PDCode:
        """
        Parses the notation like "PD[X[6, 1, 7, 2], X[12, 7, 13, 8], X[4, 13, 1, 14], X[10, 6, 11, 5], X[8, 4, 9, 3], X[14, 10, 5, 9], X[2, 12, 3, 11]]"
        """

        def expect_literal(literal: str):
            nonlocal source

            if not source.startswith(literal):
                raise ValueError(f"Expected {literal} but got {source}")
            source = source[len(literal):]

        def maybe_literal(literal: str):
            nonlocal source

            if source.startswith(literal):
                source = source[len(literal):]
                return True
            return False

        def parse_number():
            nonlocal source

            raw = ""
            while source and source[0].isdigit():
                raw += source[0]
                source = source[1:]

            if not raw:
                raise ValueError(f"Expected number but got {source}")
            return int(raw)

        # remove all spaces
        source = source.replace("\n", "").replace(" ", "")

        expect_literal("PD[")
        crossings: PDCodeCrossing = []

        while source:
            expect_literal("X[")

            i = parse_number()
            expect_literal(",")
            j = parse_number()
            expect_literal(",")
            k = parse_number()
            expect_literal(",")
            l = parse_number()

            expect_literal("]")

            crossings.append(PDCodeCrossing(i, j, k, l))

            maybe_literal(",")

            if maybe_literal("]"):
                break

        return PDCode(crossings)

    def to_signed_gauss_code(self):
        """
        Convert the PD code to a signed Gauss code.
        :return: Signed Gauss code
        """
        return SignedGaussCode.from_pd(self)


# {{1, -7, 5, -3}, {4, -1, 2, -5, 6, -4, 7, -2, 3, -6}}

# L7a1_0_pd = PDCode.parse_mathematica(
#     """
#     PD[
#         X[ 6,  1,  7,  2],
#         X[12,  7, 13,  8],
#         X[ 4, 13,  1, 14],
#         X[10,  6, 11,  5],
#         X[ 8,  4,  9,  3],
#         X[14, 10,  5,  9],
#         X[ 2, 12,  3, 11]
#     ]
#     """
# )
# print(L7a1_0_pd)

# L7a1_0_sgc = SignedGaussCode.from_pd(L7a1_0_pd)
# print(L7a1_0_sgc)

# print(L7a1_0_pd.writhe())
# print(L7a1_0_sgc.writhe())
