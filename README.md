# Kauffman Polynomial in Python

[![Test first 50 polynomials](https://github.com/aziis98/kauffman-polynomial/actions/workflows/test-polynomials.yml/badge.svg)](https://github.com/aziis98/kauffman-polynomial/actions/workflows/test-polynomials.yml)

This repository contains a Python implementation of the Kauffman polynomial,
which is a knot invariant. The Kauffman polynomial is defined using a recursive
formula based on the crossings of a knot diagram.

## Development

This Python project uses [the uv tool](https://docs.astral.sh/uv)

```bash
fd -e py | entr -c uv run pytest
```
