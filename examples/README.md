# Examples

Runnable scripts that exercise the framework end-to-end. They are **not**
installed with the package — they live in the repository so contributors can
run them directly against a checkout.

## Running

From the repo root, with the dev environment installed:

```bash
python examples/hello_mock.py
```

## Files

| File            | What it shows |
| ---             | --- |
| `hello_mock.py` | Minimum viable program — register a MockAdapter, submit a task, print the result. Mirrors the snippet in `docs/getting-started.md`. |

## Adding a new example

1. Create a new `*.py` file in this directory.
2. Keep it self-contained — one file, no extra config, runs with
   `python examples/<name>.py`.
3. Use only the public API (`from gemm import ...`, `from gemm.adapters import ...`).
   If you need to reach into a submodule, that is a sign the public surface is
   missing something — open a discussion first.
4. Every example should complete in under a few seconds against the mock
   adapter. Anything longer belongs in a benchmark, not an example.
5. Add a row to the table above so readers can find it.

## Do not put here

- Tests. Those live in `tests/`.
- Documentation prose. Those live in `docs/`.
- Hardware-specific demos. Those belong in the ecosystem adapter's own
  repository (for example, `gemm-unitree/examples/`).
