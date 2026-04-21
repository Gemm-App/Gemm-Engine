# `docs/` — documentation

The user-facing documentation site. Built with [MkDocs](https://www.mkdocs.org/)
and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.
Configuration lives in `mkdocs.yml` at the repo root.

## Local workflow

```bash
# Serve with live reload at http://127.0.0.1:8000
mkdocs serve

# Build the static site (output: site/) — same as CI
mkdocs build --strict
```

`--strict` turns warnings into errors. Always use it before opening a PR.

## Layout

```
docs/
├── index.md              ← landing page
├── getting-started.md    ← install + hello robot
├── concepts/
│   ├── adapters.md       ← Adapter protocol, lifecycle, ecosystem
│   └── tasks.md          ← Task lifecycle, fan-out, close semantics
└── guides/
    └── building-an-adapter.md  ← step-by-step for external adapter authors
```

`overrides/main.html` at the repo root extends the Material base template
(used for the apple-touch icons and any future head injections).

`docs/img/` holds static assets (favicon, apple-touch icons).

## Adding a page

1. Create a `.md` file in the right folder.
2. Register it in `mkdocs.yml` under `nav:`.
3. Run `mkdocs build --strict` locally — zero warnings allowed.
4. Link to it from at least one existing page so readers can find it.

## What belongs in docs vs. code READMEs

| Audience                | Write here |
| ---                     | --- |
| Framework **users** (app devs, adapter authors) | `docs/` |
| Framework **contributors** (engine maintainers) | `src/*/README.md`, `tests/README.md` |

If you are explaining how to *use* the framework, it goes in `docs/`.
If you are explaining how to *change* the framework, it goes in the
corresponding source `README.md`.

## Docs CI

`.github/workflows/ci.yml` runs `mkdocs build --strict` on every push and
PR. A failing docs build blocks merge, same as failing tests or lint.

## Writing style

- English only (consistent with code identifiers and the global open-source
  norm — localized versions are a future concern).
- Present tense, active voice.
- Every code block must be runnable as written. Test them.
- Avoid referencing internal implementation details that may change. Docs
  describe the public API.
