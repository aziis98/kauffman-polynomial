from __future__ import annotations

from typing import Literal, Iterable

from dataclasses import dataclass

import graphs
from graphs import Graph, collapse_loops, find_roots

from utils import sorted_tuple, rotate_to_minimal, sign_str, depth_print


Sign = Literal[+1, -1]


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

    def __str__(self):
        return f"[{self.i}, {self.j}, {self.k}, {self.l}]"

    def __repr__(self):
        return f"PDCodeCrossing({self.i}, {self.j}, {self.k}, {self.l})"

    def sign(self):
        if self.j - self.l == 1 or self.l - self.j > 1:
            return +1
        else:
            return -1


@dataclass(frozen=True)
class SGCodeCrossing:
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

    def opposite(self) -> SGCodeCrossing:
        """
        Return the opposite crossing with same id and handedness.
        """
        return SGCodeCrossing(self.id, -self.over_under, self.handedness)

    def switch(self) -> SGCodeCrossing:
        """
        Return the crossing with same id and opposite over/under, this also flips the handedness.
        """
        return SGCodeCrossing(self.id, -self.over_under, -self.handedness)

    def flip_handedness(self) -> SGCodeCrossing:
        """
        Return the crossing with same id and opposite handedness.
        """
        return SGCodeCrossing(self.id, self.over_under, -self.handedness)

    def __str__(self):
        return f"{sign_str(self.over_under)}{self.id}{sign_str(self.handedness, mode='sup')}"

    def __repr__(self):
        return f"({sign_str(self.over_under)}{self.id}, {sign_str(self.handedness)}1)"

    def __lt__(self, other: SGCodeCrossing):
        # return self.id < other.id
        # return (-self.over_under, self.id) < (-other.over_under, other.id)
        return (self.id, -self.handedness) < (other.id, -other.handedness)


@dataclass(frozen=True)
class SGCode:
    components: list[list[SGCodeCrossing]]

    def __str__(self):
        return f"{self.components}"

    def __repr__(self):
        return f"{self.components}"

    def __hash__(self):
        return hash(tuple(
            tuple(crossing.id for crossing in component)
            for component in self.components
        ))

    def relabel(self):
        """
        Relabel the crossings to use ids in the range [1, n].
        """

        crossing_ids = {
            crossing.id
            for component in self.components
            for crossing in component
        }

        id_mapping = {old_id: new_id for new_id,
                      old_id in enumerate(crossing_ids, start=1)}

        return SGCode([
            [
                SGCodeCrossing(
                    id_mapping[crossing.id],
                    crossing.over_under,
                    crossing.handedness
                ) for crossing in component
            ] for component in self.components
        ])

    def to_minimal(self):
        """
        Rotate the components to their minimal representation.
        """
        return SGCode([
            rotate_to_minimal(component)
            for component in self.components
        ])

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

    def reverse(self, ids: Literal['*'] | list[int] = '*'):
        """
        Reverse the signed Gauss code.
        :return: Reversed signed Gauss code
        """
        if ids == '*':
            return SGCode([
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

            return SGCode([
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
        return SGCode([
            [c.switch() for c in reversed(component)]
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

    def overlies_decomposition(self) -> list[list[int]]:
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

        roots = find_roots(graph_of_overlies)

        result = [[i] for i in roots]

        if len(roots) < len(self.components):
            result += [
                [
                    i for i in range(len(self.components))
                    if i not in roots
                ]
            ]

        # check result is a partition of 0...len(self.components)
        assert sum(len(component)
                   for component in result) == len(self.components)
        # assert len(result) < 3

        depth_print(f"ℹ️  {result}")
        return result

    # def unlinked_components(self) -> list[list[int]]:
    #     # print(self)

    #     # graph where "i -> j" iff "i overlies j"
    #     graph_of_overlies: Graph[int] = {}

    #     crossing_indices = {
    #         crossing: (i, j)
    #         for i, component in enumerate(self.components)
    #         for j, crossing in enumerate(component)
    #     }

    #     for i1, component in enumerate(self.components):
    #         graph_of_overlies[i1] = set()
    #         for j1, crossing in enumerate(component):
    #             over_crossing = crossing.opposite()

    #             i2, _ = crossing_indices[over_crossing]
    #             if i1 == i2:
    #                 continue

    #             if crossing.is_over():
    #                 graph_of_overlies[i1].add(i2)

    #     depth_print(f"ℹ️  {graph_of_overlies!r}")

    #     components = find_disjoint_loops(graph_of_overlies)
    #     present_ids = set(id for component in components for id in component)

    #     # add remaining singletons
    #     for i in range(len(self.components)):
    #         if i not in present_ids:
    #             components.append([i])

    #     return components

    # def to_std_unknot(self) -> SGCode:
    #     visited_crossings: set[int] = set()
    #     switched_crossings: set[int] = set()

    #     new_components = []
    #     for component in self.components:
    #         new_component = []
    #         for crossing in component:
    #             if crossing.id not in visited_crossings:
    #                 if crossing.is_under():
    #                     # make it an over crossing
    #                     new_component.append(crossing.switch())
    #                     switched_crossings.add(crossing.id)
    #                 else:
    #                     new_component.append(crossing)
    #                 visited_crossings.add(crossing.id)
    #             else:
    #                 if crossing.id in switched_crossings:
    #                     new_component.append(crossing.switch())
    #                 else:
    #                     new_component.append(crossing)
    #         new_components.append(new_component)

    #     return SGCode(new_components)

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

    def split_component(self, i: int) -> tuple[SGCode, SGCode, list[int]]:
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

        component_i_without_others = SGCode([
            [
                crossing
                for crossing in self.components[i]
                if crossing.id in target_own_ids
            ]
        ])

        complement_components = SGCode([
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
    ) -> SGCode:
        """
        Apply a switching sequence to the signed Gauss code.
        :param switching_sequence: Switching sequence
        :return: Signed Gauss code
        """
        return SGCode([
            [
                crossing.switch()
                if crossing.id in switching_sequence else crossing
                for crossing in component
            ]
            for component in self.components
        ])

    def get_crossing_handedness(self, id: int) -> Sign:
        crossing_indices = [
            (i, j, crossing)
            for i, component in enumerate(self.components)
            for j, crossing in enumerate(component)
            if crossing.id == id
        ]

        assert len(crossing_indices) == 2
        assert len(set(c.handedness for _, _, c in crossing_indices)) == 1

        _, _, c = crossing_indices[0]
        return c.handedness

    def get_crossing_indices(self, id: int) -> list[tuple[int, int, SGCodeCrossing]]:
        crossing_indices = [
            (i, j, crossing)
            for i, component in enumerate(self.components)
            for j, crossing in enumerate(component)
            if crossing.id == id
        ]

        assert len(crossing_indices) == 2
        assert len(set(c.handedness for _, _, c in crossing_indices)) == 1

        return crossing_indices

    def splice_h(self, id: int, orthogonal: Sign = +1):
        # under_idx and over_idx have the following shape
        #
        #   (component_index, crossing_index)
        #
        # where component_index is the index of the component in the components
        # list and crossing index is the index in the single component list. So
        # to access the original crossing we can do self.components[idx[0]][idx[1]]
        (under_index, under_crossing), (over_index, over_crossing) = sorted_tuple(
            (
                ((i, j), crossing)
                for i, component in enumerate(self.components)
                for j, crossing in enumerate(component)
                if crossing.id == id
            ),
            key=lambda c: c[1].over_under
        )

        assert over_crossing.handedness == under_crossing.handedness

        handedness = over_crossing.handedness
        over_index_component, _ = over_index
        under_index_component, _ = under_index

        if over_index_component == under_index_component:
            component_index = over_index[0]
            self_crossing_component = self.components[component_index]

            _, over_crossing_index = over_index
            _, under_crossing_index = under_index

            first_split, second_split = sorted_tuple(
                [over_crossing_index, under_crossing_index]
            )

            l1 = self_crossing_component[:first_split]
            l2 = self_crossing_component[first_split + 1:second_split]
            l3 = self_crossing_component[second_split + 1:]

            if handedness * orthogonal == HANDED_LEFT:
                return SGCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != component_index),
                    [
                        *l1,
                        *l3,
                    ],
                    l2,
                ])
            else:
                over_crossing_ids = set(c.id for c in l2 if c.is_over())
                under_crossing_ids = set(c.id for c in l2 if c.is_under())
                non_self_crossing_ids = over_crossing_ids ^ under_crossing_ids

                def update_signs(strand: Iterable[SGCodeCrossing]):
                    return [
                        c.flip_handedness() if c.id in non_self_crossing_ids else c
                        for c in strand
                    ]

                return SGCode([
                    *(
                        update_signs(component)
                        for i, component in enumerate(self.components)
                        if i != component_index
                    ),
                    [
                        *update_signs(l1),
                        *update_signs(reversed(l2)),
                        *update_signs(l3),
                    ],
                ])
        else:
            l1 = self.components[over_index[0]][:over_index[1]]
            l2 = self.components[over_index[0]][over_index[1] + 1:]

            m1 = self.components[under_index[0]][:under_index[1]]
            m2 = self.components[under_index[0]][under_index[1] + 1:]

            if handedness * orthogonal == HANDED_LEFT:
                # print("splice type +1", (id, handedness, orthogonal))

                return SGCode([
                    *(component[:]
                      for i, component in enumerate(self.components)
                      if i != over_index[0] and i != under_index[0]),
                    [
                        *l1,
                        *m2,
                        *m1,
                        *l2
                    ]
                ])
            else:
                # print("splice type -1", (id, handedness, orthogonal))

                non_self_crossing_ids = (
                    set(c.id for c in m1 if c.is_over())
                    |
                    set(c.id for c in m2 if c.is_over())
                ) ^ (
                    set(c.id for c in m1 if c.is_under())
                    |
                    set(c.id for c in m2 if c.is_under())
                )

                # non_self_crossing_ids = (
                #     set(c.id for c in m1) | set(c.id for c in m2)
                # ) - (
                #     (
                #         set(c.id for c in m1 if c.is_over())
                #         | set(c.id for c in m2 if c.is_over())
                #     )
                #     &
                #     (
                #         set(c.id for c in m1 if c.is_under())
                #         | set(c.id for c in m2 if c.is_under())
                #     )
                # )

                # if len(non_self_crossing_ids_old) != len(non_self_crossing_ids):
                #     print(self, id, orthogonal)
                #     print(non_self_crossing_ids_old)
                #     print(non_self_crossing_ids)
                #     raise ValueError("illegal state")

                def update_signs(strand: Iterable[SGCodeCrossing]):
                    return [
                        c.flip_handedness() if c.id in non_self_crossing_ids else c
                        for c in strand
                    ]

                return SGCode([
                    *(
                        update_signs(component)
                        for i, component in enumerate(self.components)
                        if i != over_index_component and i != under_index_component
                    ),
                    [
                        *update_signs(l1),
                        *update_signs(reversed(m1)),
                        *update_signs(reversed(m2)),
                        *update_signs(l2)
                    ],
                ])

    def splice_v(self, id: int):
        return self.splice_h(id, orthogonal=-1)

    def switch_crossing(self, id: int):
        """
        Switches the crossing with the given id.
        """
        return SGCode([
            [
                crossing.switch()
                if crossing.id == id else crossing
                for crossing in component
            ]
            for component in self.components
        ])

    @staticmethod
    def from_tuples(
        link: list[list[tuple[int, int]]]
    ) -> SGCode:
        """
        Convert a list of tuples to a signed Gauss code.
        :param link: list of tuples
        :return: Signed Gauss code
        """

        return SGCode([
            [
                SGCodeCrossing(
                    abs(crossing),
                    CROSSING_OVER if crossing > 0 else CROSSING_UNDER,
                    HANDED_LEFT if handedness > 0 else HANDED_RIGHT
                ) for (crossing, handedness) in component
            ] for component in link
        ])

    @staticmethod
    def from_pd(pd_code: PDCode) -> SGCode:
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

        components: list[list[SGCodeCrossing | None]] = [
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

            over_crossing = SGCodeCrossing(
                id, CROSSING_OVER, crossing.sign()
            )

            components[over_cc_idx][over_crossing_idx] = over_crossing
            components[under_cc_idx][under_crossing_idx] = over_crossing.opposite()

        return SGCode(components)  # type: ignore


class PDCode:
    crossings: list[PDCodeCrossing]

    def __str__(self):
        return f"[{", ".join(str(c) for c in self.crossings)}]"

    def __repr__(self):
        return f"PDCode({self.crossings})"

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
    def from_tuples(link: list[list[int]] | list[tuple[int, int, int, int]]):
        """
        e.g. link = [(3, 6, 4, 1), (5, 2, 6, 3), (4, 2, 5, 1)]
        """

        crossings = []
        for crossing_spec in link:
            i, j, k, l = tuple(crossing_spec)
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
        crossings: list[PDCodeCrossing] = []

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
        return SGCode.from_pd(self)


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
