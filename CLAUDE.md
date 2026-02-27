# CLAUDE.md

## Non-obvious gotchas

- **Required env var**: The service won't start without `POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION` being set.
- **`python-requirements-inspector` is not on PyPI** — it's installed as a WHL directly from GitHub Releases. This is why a Renovate custom regex manager exists in `renovate.json`.
- **`numpy>=2.0` override in `pyproject.toml` is intentional** — numpy 1.x has no Python 3.13 wheels; spacy/thinc now support numpy 2.x.
- **Pre-commit blocks direct commits to `main`** — use `--no-verify` only for emergency direct pushes; otherwise use a branch + PR.
- **Always use `uv run tox`**, not bare `tox` — the project uses uv as the runner.
