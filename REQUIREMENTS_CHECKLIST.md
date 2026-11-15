# CyberShield AI Requirements Checklist

Statuses:

- Not started
- In progress
- Implemented
- Tested
- Verified
- Blocked

Do not mark an item as complete unless there is evidence from code, tests, or documentation.

## Foundation

| Requirement | Status | Evidence |
|---|---|---|
| Keep the project inside `E:\agent` | In progress | Confirmed working folder before Milestone 0 setup. |
| Preserve `CyberShield_AI_Master_Playbook.md` unchanged | In progress | Existing plan file kept with original name. |
| Use Python 3.14 provisionally | Verified | `py -3.14 --version` reported Python 3.14.4; `.venv` uses Python 3.14.4. |
| Use pytest for tests | Verified | Added to `requirements.txt`; `pytest==9.0.2` installed inside `.venv`. |
| Use Git from the beginning | In progress | Two commits exist (`c014bda`, `a14a211`); current work modifies `SCHEMA_DESIGN.md`, `cybershield/schemas.py`, and the status docs, and adds `cybershield/reporting.py` plus `test_findings.py`, `test_report.py`, and `test_integration.py`; no `add`/`commit` executed in this phase. Git state may change later. |
| Maintain simple project documentation | In progress | `README.md`, `REQUIREMENTS_CHECKLIST.md`, and `PROJECT_STATUS.md` maintained; status and checklist updated to match the implemented finding/report work. |

## Core Functional Requirements

| Requirement | Status | Evidence |
|---|---|---|
| Define shared normalized event schema | Tested | Implemented in `cybershield/schemas.py`; defined in `SCHEMA_DESIGN.md` sec 1; covered by last documented run 2026-10-14 with 62 passed (not re-run here). |
| Define shared finding schema | Tested | Implemented in `cybershield/schemas.py` (`Finding`, `EvidenceItem`, validators); decisions D1/D3/D6–D9 in `SCHEMA_DESIGN.md` sec 4; covered by `tests/test_findings.py` (94 cases in the last full run). |
| Define shared report schema | Tested | Implemented in `cybershield/schemas.py` (`Report`, validators, risk calculation) with the builder in `cybershield/reporting.py`; decisions D2/D4/D5/D10–D13 in `SCHEMA_DESIGN.md` sec 4; covered by `tests/test_report.py` (50 cases in the last full run). |
| Validate and normalize CSV input | Tested | Implemented in `cybershield/data_loader.py` CSV path per `LOADER_INPUT_FORMAT.md`; covered by last documented run 2026-10-14 (not re-run here). |
| Validate and normalize JSON input | Tested | Implemented in `cybershield/data_loader.py` JSON path per `LOADER_INPUT_FORMAT.md`; covered by last documented run 2026-10-14 (not re-run here). |
| Implement Log Analyzer Agent | Tested | `cybershield/agents/log_analyzer.py` (rule `AUTH-REPEATED-FAILURES`, configurable threshold/window); `tests/test_log_analyzer.py`. |
| Implement Network Agent | Tested | `cybershield/agents/network_agent.py` (rule `NET-UNUSUAL-PORT`, configurable port list); `tests/test_network_agent.py`. |
| Implement Threat Intelligence Agent | Tested | `cybershield/agents/threat_intelligence.py` with synthetic feed `cybershield/data/demo_threat_intel.json`; `tests/test_threat_intelligence.py` (19 cases). |
| Implement Incident Response Agent | Tested | `cybershield/agents/incident_response.py`; `tests/test_incident_response.py` (25 cases); accepts both `network` and `network_agent`. |
| Implement Manager Agent | Tested | `cybershield/agents/manager.py` connects all agents (dedupe exact duplicates, order by severity, assign ids, build plan and report); `main.py` CLI; `tests/test_manager_pipeline.py`. |
| Export structured JSON report | Tested | `report_to_json` in `cybershield/reporting.py` with round-trip tests; CLI writes the file and the dashboard offers a download. |
| Add automated tests | Tested | 356 passed in the latest full run (`python -m pytest`, Python 3.14.6 and 3.13) covering loader, schemas, findings, report, all agents, the Manager pipeline, CLI and dashboard. |
| Build Streamlit dashboard | Tested | `app.py` (demo/upload, rule settings, severity summary, filters, evidence, plan, JSON download); `tests/test_dashboard.py` via Streamlit AppTest; server boot returned HTTP 200. |
| Optional AI summarization disabled by default | Tested | `cybershield/ai/summarizer.py`: off by default, sends only sanitized counts/rule IDs, validates output, falls back safely, labelled AI-generated; local Ollama only (loopback). Tested with fake providers and a local stub server; **not tested against a real Ollama model**. The Report schema keeps `ai_summary` disabled (v1.0), so the summary lives beside the report, not inside it. |

## Safety Requirements

| Requirement | Status | Evidence |
|---|---|---|
| Defensive educational project only | In progress | Documented in `README.md`; only foundation, schemas, and loader files exist so far; no comprehensive security audit performed. |
| No offensive security features | In progress | Original state kept; file presence check shows only `schemas.py`/`data_loader.py` plus tests; no comprehensive security audit performed. |
| No automatic remediation | In progress | Documented in `README.md`; loader is documented as performing no remediation per `LOADER_INPUT_FORMAT.md`. |
| Do not commit secrets | In progress | `.env` included in `.gitignore`. |
| Do not upload sensitive logs to external AI services | In progress | Documented in `README.md`; AI deferred. |
| Findings must not be presented as proof of compromise | In progress | Documented in `README.md` and enforced by required limitations plus `requires_human_approval`; finding/report code validates these fields. |
