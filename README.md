# Kauffman Polynomial in Python

[![Test first 50 polynomials](https://github.com/aziis98/kauffman-polynomial/actions/workflows/test-polynomials.yml/badge.svg)](https://github.com/aziis98/kauffman-polynomial/actions/workflows/test-polynomials.yml)
[![PyTest](https://github.com/aziis98/kauffman-polynomial/actions/workflows/pytest.yml/badge.svg)](https://github.com/aziis98/kauffman-polynomial/actions/workflows/pytest.yml)

This repository contains a Python implementation of the Kauffman polynomial, a
knot invariant that is used to distinguish knots and links in knot theory. It is
defined using skein relations and can be computed from a knot diagram given its
**P.D. (planar diagram) code** or its **S.G. (signed Gauss) code**.

> Download the
> [latest version of the report](https://raw.githubusercontent.com/aziis98/kauffman-polynomial/refs/heads/main/report/kauffman-polynomial-report.pdf)
>
> **Abstract.** In this project we write implement from scratch the Kauffman
> polynomial in Python. We start with a brief detour in computational knot
> theory and describe various representations of knots and links and find a good
> one to use for the algorithm. We then describe two approaches for computing
> the Kauffman polynomial and how to implement it in Python. Finally we try the
> algorithm on various knots and links and compare the results with the ones
> from the KnotInfo Database, finding an error for the knot $10_{125}$.

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

-   **`kauffman_polynomial`**: The bracket polynomial $L(a,z)$ using skein
    relations

-   **`f_polynomial`**: The normalized Kauffman polynomial
    $`F_K(a,z) = a^{-w(K)} * L_K(a,z)`$

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

-   **Topology analysis**: Determine overlies relationships between components

### Skein Equation DSL

-   **Expression evaluation**: Domain-specific language for mathematical
    expressions

-   **Derive algorithm from skein relation**: Compute new polynomial invariants
    different from the Kauffman and HOMFLY polynomials using their skein
    relations axiomatic definition.

## Usage

### 1. Setup

To get started, you'll need to install [uv](https://docs.astral.sh/uv/), a tool
that simplifies running Python scripts and managing dependencies and virtual
environments.

#### macOS / Linux

Using `curl`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

Open PowerShell as Administrator and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Post Installation

After installation you may need to restart your terminal or run the following
command to make `uv` available:

```bash
source ~/.bashrc  # or ~/.zshrc, depending on your shell
```

### 2. Clone the Repo

To clone the repository, run the following command in your terminal:

```bash
git clone https://github.com/aziis98/kauffman-polynomial
cd kauffman-polynomial
```

### 3. Command Line Interface

#### Main Terminal Program

```bash
# Display help and options for the main cli program
uv run cli.py --help

# Calculate Kauffman polynomial for a specific knot
uv run cli.py --polynomial F 8_18

# Calculate HOMFLY polynomial
uv run cli.py --polynomial P 10_125

# Use custom PD notation
uv run cli.py --pd "[[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]]"
```

#### Raw Polynomial Output (for machine processing)

For machine processing and scripting, use `raw.py` which outputs raw SymPy
polynomial format without formatting:

```bash
# Display help and options for raw cli command
uv run raw.py --help

# Calculate polynomials for multiple inputs (preserves command-line order)
uv run raw.py -p F --knotinfo 3_1 --pd "[[1,3,2,4]]" --knotinfo 4_1

# Mix different input types in any order
uv run raw.py -p P --pd "[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]" --sg "[[(+1,-1),(-2,-1)],[(-1,-1),(+2,-1)]]"

# Use positional arguments for knot names
uv run raw.py -p F 3_1 4_1 5_1
```

Options, each input option produces one line of raw polynomial output

-   `--pd`: PD notation string

-   `--sg`: Signed Gauss code string

-   `--knotinfo`: KnotInfo knot/link name, or just use remaining positional
    arguments.

-   `-p`, `--polynomial`: Required. Polynomial type (P=HOMFLY, F=Kauffman F,
    L=Kauffman L)

### Validation Against KnotInfo Database

```bash
# Test first 50 knots with Kauffman polynomial
uv run check_knotinfo.py --polynomial kauffman --knots -c 50

# Test links with specified polynomial
uv run check_knotinfo.py --polynomial kauffman --links -c 50

# Test with HOMFLY polynomial
uv run check_knotinfo.py --polynomial homfly --knots -c 50
```

### Programmatic Usage

```python
from codes import PDCode, SGCode
from kauffman import f_polynomial, kauffman_polynomial
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
uv run pytest kauffman_test.py
uv run pytest homfly_test.py

# Test code representations
uv run pytest codes_test.py
```

## Project Structure

```
├── check_knotinfo.py       # Validation script against KnotInfo database
├── codes.py                # PD and SG code implementations
├── homfly.py               # HOMFLY polynomial implementation
├── kauffman.py             # Main Kauffman polynomial implementation
├── cli.py                  # Interactive command line interface
├── raw.py                  # Raw polynomial output for machine processing
├── utils.py                # Utility functions and parsing
└── *_test.py               # PyTest test suites
```

## Dependencies

-   **sympy**: Symbolic mathematics for polynomial manipulation

-   **database-knotinfo**: Access to the KnotInfo database for validation

-   **pytest**: Testing framework

-   **tqdm**: For nice progress bars for long-running computations

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
