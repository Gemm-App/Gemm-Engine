# `gemm/` — package internals

This is the installable package. The **public API** is whatever
`gemm/__init__.py` re-exports; everything else is private and may change
without a deprecation cycle.

## Layout

```
gemm/
├── __init__.py     ← public API (the only file users import from directly)
├── types.py        ← value types: Pose, RobotState, TaskResult, TaskStatus
├── errors.py       ← exception hierarchy rooted at GemmError
├── py.typed        ← PEP 561 marker — do not delete
├── adapters/       ← the Adapter Protocol + shipped adapters
├── core/           ← Engine + AdapterRegistry (the runtime)
├── tasks/          ← Task + TaskExecutor
└── testing/        ← reusable pytest harness for adapter authors
```

Each subpackage has its own `README.md`. Start there when editing the
corresponding area.

## The public surface

Anything importable as `from gemm import X` is part of the public contract.
Changing a signature, removing an export, or renaming a field is a breaking
change and needs a major version bump.

Adding new exports is fine. When you do:

1. Define the object in its natural module.
2. Re-export it in `gemm/__init__.py` and add it to `__all__`.
3. If it belongs in a subpackage's own `__init__.py` (e.g. `gemm.adapters`),
   add it there too.
4. Mention it in `docs/` where it fits.

## Adding a new module

- Put it in the subpackage where it conceptually belongs. Do not add a new
  top-level module unless you are introducing a genuinely new concept.
- Keep circular imports out: `types.py` and `errors.py` are leaves and must
  not import from other gemm modules.
- Use `from __future__ import annotations` at the top of every `.py` file
  that has type hints.

## What is and is not allowed

- **Allowed:** async APIs, dataclasses, Protocols, `match` statements,
  `asyncio.TaskGroup`, 3.11 union syntax.
- **Not allowed without a discussion:** third-party runtime dependencies
  (we have **zero** right now, on purpose — adding one is a design decision),
  sync-only public APIs, inheritance-based extension points.

## Invariants

- `__init__.py` must stay import-light. Importing `gemm` should not pull in
  an adapter SDK or connect to anything.
- No subpackage may import from a sibling it has no business depending on.
  Current allowed graph:
  - `types` / `errors` → nothing
  - `adapters` → `types`, `errors`
  - `tasks` → `types`, `errors`, `core` (registry only)
  - `core` → `adapters`, `tasks`, `errors`, `types`
  - `testing` → `adapters`, `errors`, `types`
- `py.typed` is an empty marker file. Its presence — not its contents —
  tells type-checkers that this package ships inline type hints.
