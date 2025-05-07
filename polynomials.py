from dataclasses import dataclass
from collections import defaultdict


@dataclass(frozen=True)
class Monomial:
    """
    Laurent polynomial monomial
    """
    variables: list[tuple[str, int]]

    def __mul__(self, other):
        if isinstance(other, Monomial):
            new_vars = defaultdict(int)
            for var, exp in self.variables:
                new_vars[var] += exp
            for var, exp in other.variables:
                new_vars[var] += exp
            return Monomial(sorted([(var, exp) for var, exp in new_vars.items()]))
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, int):
            return Term(self.variables, other)

    def __pow__(self, exponent):
        if isinstance(exponent, int):
            return Monomial(sorted([(var, exp * exponent) for var, exp in self.variables]))
        else:
            return NotImplemented

    def __str__(self):
        result = []
        for var, exp in self.variables:
            if exp == 1:
                result.append(var)
            else:
                result.append(f"{var}^{exp}")
        return " ".join(result) or "1"


@dataclass(frozen=True)
class Term:
    coef: int
    monomial: Monomial

    def __mul__(self, other):
        if isinstance(other, Term):
            return Term(self.coef * other.coef, self.monomial * other.monomial)
        elif isinstance(other, (int, float)):
            return Term(int(self.coef * other), self.monomial)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        if self.coef == 0:
            return "0"
        elif self.coef == 1:
            return str(self.monomial)
        elif self.coef == -1:
            return "-" + str(self.monomial)
        elif self.monomial == Monomial([]):
            return str(self.coef)
        else:
            return f"{self.coef} {self.monomial}"


@dataclass(frozen=True)
class Polynomial:
    terms: list[Term]

    def __add__(self, other):
        if isinstance(other, Polynomial):
            return Polynomial(self.terms + other.terms).simplify()
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Polynomial):
            new_terms = []
            for self_term in self.terms:
                for other_term in other.terms:
                    new_terms.append(self_term * other_term)
            return Polynomial(new_terms).simplify()
        else:
            return NotImplemented

    def __str__(self):
        return " + ".join(str(term) for term in self.terms)

    def simplify(self):
        """
        Simplifies the polynomial by combining like terms.
        """
        combined_terms = defaultdict(int)
        for term in self.terms:
            combined_terms[tuple(term.monomial.variables)] += term.coef

        return Polynomial(
            [
                Term(coef, Monomial(list(vars))) for vars, coef in combined_terms.items() if coef != 0
            ]
        )


def var(name):
    """
    Creates a Term with coefficient 1 and a single variable.
    """
    return Term(1, Monomial([(name, 1)]))


if __name__ == '__main__':
    x = var('x')
    y = var('y')

    # 2 + 3x
    p1 = Polynomial([
        Term(2, Monomial([])),
        Term(3, Monomial([('x', 1)]))
    ])

    # x + 4y
    p2 = Polynomial([
        Term(1, Monomial([('x', 1)])),
        Term(4, Monomial([('y', 1)]))
    ])

    print(f"p1: {p1!s}")
    print(f"p2: {p2!s}")
    print(f"p1 + p2: {p1 + p2!s}")
    print(f"p1 * p2: {p1 * p2!s}")
