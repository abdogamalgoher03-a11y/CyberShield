# CyberShield AI Project Status

## Current Milestone

Milestone 2: Agents, Manager pipeline and dashboard implemented (optional local AI summary implemented, off by default)

## Current Folder

```text
E:\agent
```

## Existing Source of Truth

```text
CyberShield_AI_Master_Playbook.md
```

This file is the original project plan and must not be renamed, overwritten, or replaced.

## Team Model

- Developer 1: Python fundamentals, technical review, schemas, integration, and test verification.
- Developer 2: beginner, starts with testing, documentation, and small guided code changes.
- Coding assistant: writes most code, explains in Arabic, helps test, and keeps the project organized.

Major architecture, schema, dependency, and scope decisions require approval from the two human developers.

## Decisions So Far

| Decision | Status | Notes |
|---|---|---|
| Work inside `E:\agent` | Approved | Do not move unless explicitly approved. |
| Keep `CyberShield_AI_Master_Playbook.md` name | Approved | Do not rename. |
| Python 3.14 | Provisionally approved | Local `.venv` uses Python 3.14.4; latest full run (356 passed) was executed on Python 3.14.6 and Python 3.13. |
| pytest | Approved for testing | `pytest==9.0.2` installed inside `.venv`; last full run reported 244 passed (32 loader + 57 schemas + 94 findings + 50 report + 11 integration). |
| Streamlit | Approved | `streamlit==1.66.1` added; `app.py` implemented; usage telemetry disabled in `.streamlit/config.toml`. |
| AI summarization | Deferred | Optional and disabled by default. |
| Shared schemas | Implemented | Normalized event, finding, and report implemented in `cybershield/schemas.py` with the report builder in `cybershield/reporting.py`, covered by documented tests; agents not started. |

## Completed Work So Far

- Foundation, schemas, loader, finding/report schemas and report builder (see `SCHEMA_DESIGN.md`).
- Agents: Log Analyzer, Network Agent, Threat Intelligence (synthetic demo feed), Incident Response, and the Manager that connects them (`cybershield/agents/`).
- `main.py` CLI and `app.py` Streamlit dashboard share the same Manager pipeline.
- Latest full run: 332 passed (`python -m pytest`) on Python 3.14.6 and 3.13.
- Integration found and fixed a naming mismatch: the schema agent name is `network_agent`; Incident Response now accepts it.

## Setup Notes

- Creating `.venv` initially failed while `ensurepip` tried to write to the default temporary directory.
- The same issue appeared with a local temp folder inside the sandbox.
- Running `ensurepip` outside the sandbox succeeded and installed pip inside `.venv`.
- Installing `pytest` inside the sandbox failed because pip could not reach the package index.
- Running pip outside the sandbox succeeded and installed the approved dependency from `requirements.txt`.
- Running `python -m pytest` inside `.venv` worked, but collected 0 tests because project tests have not been created yet.
- Later documented run on 2026-10-14 reported 62 passed. This documentation review did not re-run tests.

## Next Required Review

- Optional AI summary (`cybershield/ai/summarizer.py`) is verified only with fake providers and a local stub server; try it with a real local Ollama model before the demo. The Report schema still requires `ai_summary` to be disabled (v1.0); putting the summary inside the report would be a schema decision for both developers.
- A clean-machine setup test (fresh venv, `pip install -r requirements.txt`, `pytest`) passed on Python 3.14.6 in the cloud workspace; it has not been repeated on the team's Windows machines.
- Thresholds, window and unusual ports are configurable in code, `main.py` options and the dashboard.
- `tools/convert_ssh_log.py` converts the original SSH sample (no timezone, no outcome) to loader format; use `--count-unknown-status`.
- `prototypes/` holds the original standalone scripts, superseded by the agents.
- Report IDs are unique within a single run only; cross-run uniqueness is not claimed.

## 2026-11-15 Competition Edition Update

- Preserved the existing schema, Manager pipeline, rule agents, CLI, bilingual Streamlit dashboard, CIC-IDS2017 interop/evaluation, and original Master Playbook.
- Added `cybershield/ml/pipeline.py`: offline Random Forest, optional XGBoost, and Isolation Forest training; held-out metrics; model artifact persistence; feature importance; and inference for an unlabeled feature CSV.
- Added `python -m cybershield.ml train|predict|status` commands and `ML_GUIDE_AR.md`.
- Added an ML workspace to the dashboard with labeled-CSV upload, training, metrics, feature importance, inference, and JSON prediction export.
- Added SOC-style dark header, event timeline and severity-mix visualization based on the actual uploaded/demo events (no fabricated traffic metrics).
- Added optional OpenAI Responses API provider; it receives only the existing sanitized aggregate prompt. Hosted AI remains opt-in and requires an environment API key. Ollama remains supported.
- Added Windows setup/run script `RUN_CYBERSHIELD_WINDOWS.bat`.
- Verification on Python 3.13 environment: `python -m compileall -q app.py main.py cybershield tests` passed; `python -m pytest -q` -> **412 passed, 1 skipped**.
- Important: no real ML artifact is shipped because the repository does not contain a verified labeled flow dataset appropriate for competition claims. Train on a licensed/authorized labeled dataset and report the held-out metrics with dataset provenance and limitations.
- UI implementation remains Streamlit to preserve the original tested application; it has not been migrated to React/FastAPI. The dashboard charts are derived from actual loaded event data, but it is not a live packet/network monitor.
