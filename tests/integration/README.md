# `tests/integration/` - end-to-end behavior

Integration tests verify framework behavior across component boundaries
(`Engine`, registry, task execution, and adapters) using async flows.

## Current target

- `test_engine_e2e.py`: primary end-to-end suite for engine lifecycle,
  submission, concurrency, and shutdown semantics.

## Add tests here when

- A change touches the interaction between modules.
- You need to protect a user-visible workflow.
- A bug only appears when running real async sequencing.

## Test design rules

1. Assert external behavior, not private attributes.
2. Keep tests deterministic (no real network or hardware).
3. Prefer short mock delays for concurrency checks.
4. Cover both success and failure paths for lifecycle changes.
