# CLAUDE.md

## Non-obvious gotchas

- **Required env var**: The service won't start without `POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION` being set.
- **`python-requirements-inspector` is not on PyPI** — it's installed as a WHL directly from GitHub Releases, which is why a Renovate custom regex manager exists in `renovate.json`. A regex manager does string replacement only and has no lock-file step, so every Renovate bump of it lands with a stale `uv.lock` and CI fails on `uv sync --locked`; run `uv lock` on the branch. Retiring the URL dependency is tracked in `python-requirements-inspector#181`.
- **`uv sync --locked` in CI and `--frozen` in `tox.ini` are both deliberate — neither is template drift.** This repo comes from `open-source-polarion-docker-repo-template`, not the Python one, and that template's `ci.yml` also uses `--locked` (synced in #130). `tox.ini` uses `--frozen` because for a direct URL dependency `uv run` re-fetches the wheel metadata from GitHub before every command, until GitHub answers `refused stream before processing any application logic` (#116 → #115). CI's `--locked` and the `uv lock --check` pre-commit hook are the two layers keeping `pyproject.toml` and `uv.lock` in agreement, and Renovate commits skip pre-commit. The `uv-venv-lock-runner` migration is open as #125.
- **`numpy>=2.0` override in `pyproject.toml` is intentional** — numpy 1.x has no Python 3.13 wheels; spacy/thinc now support numpy 2.x.
- **Pre-commit blocks direct commits to `main`** — use `--no-verify` only for emergency direct pushes; otherwise use a branch + PR.
- **Always use `uv run tox`**, not bare `tox` — the project uses uv as the runner.
