# Kauffman Polynomial in Python

This repository contains a Python implementation of the Kauffman polynomial,
which is a knot invariant. The Kauffman polynomial is defined using a recursive
formula based on the crossings of a knot diagram.

## Development

This Python project uses [the uv tool](https://docs.astral.sh/uv)

```bash
fd -e py | entr -c uv run pytest
```
