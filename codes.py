from __future__ import annotations
import typing

from dataclasses import dataclass

import math

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
        return self.over_under == +1

    def is_under(self) -> bool:
        return self.over_under == -1

    def is_left(self) -> bool:
        return self.sign == +1

    def is_right(self) -> bool:
        return self.sign == -1

    def opposite(self) -> SignedGaussCodeCrossing:
        return SignedGaussCodeCrossing(self.id, -self.over_under, self.handedness)

    def __repr__(self):
        return f"({self.id * self.over_under}, {self.handedness})"


@dataclass(frozen=True)
class SignedGaussCode:
    components: list[list[SignedGaussCodeCrossing]]

    def __repr__(self):
        return f"SignedGaussCode({self.components})"

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

    def reverse(self):
        """
        Reverse the signed Gauss code.
        :return: Reversed signed Gauss code
        """
        return SignedGaussCode([
            list(reversed(component))
            for component in self.components
        ])

    def mirror(self):
        """
        Mirror the signed Gauss code.
        :return: Mirrored signed Gauss code
        """
        return SignedGaussCode([
            [c.opposite() for c in reversed(component)]
            for component in self.components
        ])

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
                        new_component.append(crossing.opposite())
                        switched_crossings.add(crossing.id)
                    else:
                        new_component.append(crossing)
                    visited_crossings.add(crossing.id)
                else:
                    if crossing.id in switched_crossings:
                        new_component.append(crossing.opposite())
                    else:
                        new_component.append(crossing)
            new_components.append(new_component)

        return SignedGaussCode(new_components)

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
                crossing.opposite() if crossing.id in switching_sequence else crossing
                for crossing in component
            ]
            for component in self.components
        ])

    def splice_h(self, id: int):
        raise NotImplementedError("Splicing not implemented yet")

    def splice_v(self, id: int):
        raise NotImplementedError("Splicing not implemented yet")

    def switch_crossing(self, id: int):
        return SignedGaussCode([
            [
                crossing.opposite() if crossing.id == id else crossing
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

        components: list[list[SignedGaussCodeCrossing]] = [
            [
                (0, 0) for _ in range(len(component))
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

        return SignedGaussCode(components)


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
