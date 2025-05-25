# Kauffman Polynomial in Python

[![Test first 50 polynomials](https://github.com/aziis98/kauffman-polynomial/actions/workflows/test-polynomials.yml/badge.svg)](https://github.com/aziis98/kauffman-polynomial/actions/workflows/test-polynomials.yml)

This repository contains a Python implementation of the Kauffman polynomial, a
knot invariant that is used to distinguish knots and links in knot theory. It is
defined using skein relations and can be computed from a knot diagram given its
**P.D. (planar diagram) code** or its **S.G. (signed Gauss) code**.

## Features

-   **Kauffman Polynomial Implementation**: Two versions of the Kauffman
    polynomial calculation using different approaches

-   **HOMFLY Polynomial**: Implementation of the HOMFLY polynomial for knots and
    links

-   **Knot Representations**: Support for both Planar Diagram (PD) codes and
    Signed Gauss (SG) codes

-   **KnotInfo Integration**: Validation against the KnotInfo database for
    accuracy testing

-   **Comprehensive Testing**: Test suite covering many knot/link cases,
    including some not present in KnotInfo

-   **Command Line Interface**: Easy-to-use CLI for computing polynomials

-   **Automated Testing**: GitHub Actions workflow for continuous validation of
    the first knots and links from KnotInfo

## Polynomial Implementations

### Kauffman Polynomial (`F`)

-   **`f_polynomial`**: The normalized Kauffman polynomial
    $`F_K(a,z) = a^{-w(K)} * L_K(a,z)`$

-   **`kauffman_polynomial`**: The bracket polynomial $L(a,z)$ using skein
    relations

### HOMFLY Polynomial (`P`)

-   **`homfly_polynomial`**: Implementation using skein relations with variables
    $v$ and $z$ (using KnotInfo
    [conventions](https://knotinfo.math.indiana.edu/descriptions/jones_homfly_kauffman_description/polynomial_defn.html))

## Core Components

### Code Representations

-   **`PDCode`**: Planar Diagram code representation based on arc labels with
    crossing information

-   **`SGCode`**: Signed Gauss code representation for knot/link components

-   **Conversion utilities**: Convert from PD code to SG representation

### Graph Operations

-   ~~**Connected components**: Find unlinked components in knot diagrams~~

-   ~~**Loop detection**: Identify and collapse loops in graph structures~~

-   **Topology analysis**: Determine overlies relationships between components

### (WIP) Skein Equation DSL

-   **Expression evaluation**: Domain-specific language for mathematical
    expressions

-   **Derive algorithm from skein relation**: Compute new polynomial invariants
    different from the Kauffman and HOMFLY polynomials using their skein
    relations axiomatic definition.

## Usage

### Command Line Interface

```bash
# Calculate Kauffman polynomial for a specific knot
uv run python kauffman_cli.py --polynomial F 8_18

# Calculate HOMFLY polynomial
uv run python kauffman_cli.py --polynomial P 10_125

# Use custom PD notation
uv run python kauffman_cli.py --pd "[[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]]"
```

### Validation Against KnotInfo Database

```bash
# Test first 50 knots with Kauffman polynomial
uv run python check_knotinfo.py --polynomial F --knots -c 50

# Test links with specified polynomial
uv run python check_knotinfo.py --polynomial F --links -c 50

# Test with HOMFLY polynomial
uv run python check_knotinfo.py --polynomial P --knots -c 50
```

### Programmatic Usage

```python
from codes import PDCode, SGCode
from kauffman_v2 import f_polynomial, kauffman_polynomial
from homfly import homfly_polynomial

# Create a knot from PD code
pd = PDCode.from_tuples([(4, 2, 5, 1), (8, 6, 1, 5), (6, 3, 7, 4), (2, 7, 3, 8)])
sg = pd.to_signed_gauss_code()

# Calculate polynomials
f_poly = f_polynomial(sg)
kauffman_poly = kauffman_polynomial(sg)
homfly_poly = homfly_polynomial(sg)
```

## Testing

### Run All Tests

```bash
uv run pytest
```

### Continuous Testing During Development

```bash
fd -e py | entr -c uv run pytest
```

### Specific Test Categories

```bash
# Test specific polynomial implementations
uv run pytest kauffman_v2_test.py
uv run pytest homfly_test.py

# Test code representations
uv run pytest codes_test.py

# Test against KnotInfo database
uv run pytest kauffman_v2_knotinfo_test.py
```

## Project Structure

```
├── check_knotinfo.py       # Validation script against KnotInfo database
├── codes.py                # PD and SG code implementations
├── graphs.py               # Graph algorithms for topology analysis
├── homfly.py               # HOMFLY polynomial implementation
├── kauffman_v2.py          # Main Kauffman polynomial implementation
├── kauffman_closed.py      # Alternative Kauffman implementation
├── kauffman_cli.py         # Command line interface
├── utils.py                # Utility functions and parsing
├── equation_dsl/           # Domain-specific language for equations
│   ├── equation_dsl.py     # Expression evaluation framework
│   └── skein_dsl_test.py   # Skein relation validation tests
└── *_test.py               # Comprehensive test suites
```

## Dependencies

-   **sympy**: Symbolic mathematics for polynomial manipulation
-   **database-knotinfo**: Access to the KnotInfo database for validation
-   **pytest**: Testing framework
-   **tqdm**: Progress bars for long-running computations

## Development

This Python project uses [the uv tool](https://docs.astral.sh/uv)

```bash
# Install dependencies
uv sync

# Run tests with file watching
fd -e py | entr -c uv run pytest

# Run specific validation
uv run python check_knotinfo.py --polynomial F --knots -c 10
```

## Validation

The implementation is continuously validated against the KnotInfo database
through:

-   **GitHub Actions**: Automated testing of 50 knots/links for each polynomial
    type

-   **Test suite**: Many tests covering various knot/link cases even some not in
    KnotInfo

-   **(WIP) Cross-validation**: Multiple polynomial implementations tested
    against each other (both the HOMFLY and the Kauffman polynomials specialize
    to the Jones polynomial for the same knot/link)

## Mathematical Background

### Kauffman Polynomial

The Kauffman polynomial $`L(a, z)`$ is defined through skein relations:

-   $`L(O) = 1`$

-   $`L(W^+) = a L(W)`$, $`L(W^-) = a^{-1} L(W)`$

-   $`L(K) + L(K_-) = z (L(K_h) + L(K_v))`$

Where:

-   $`W^\pm, W`$ are the same know with a strands with a positive, negative or
    zero curl.

-   $`K`$ is the initial knot.

-   $`K_-`$ is the knot with the crossing switched.

-   $`K_h`$ is the horizontal splice of the crossing.

-   $`K_v`$ is the vertical splice of the crossing.

Then the normalized Kauffman polynomial is defined as:

```math
F_K(a, z) = a^{-w(K)} * L_K(a, z)
```

Where $`w(K)`$ is the writhe of the knot/link diagram.

### HOMFLY Polynomial

The HOMFLY polynomial uses similar skein relations with variables $`v`$ and
$`z`$...
