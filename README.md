# CyberShield AI

CyberShield AI is a defensive, educational cybersecurity project for analyzing authorized security-log data.

The project will be developed incrementally by two human developers with Codex support. The initial goal is a small, tested, rule-based core that can validate CSV/JSON events, normalize them, run clearly defined analysis components, and export a JSON report. A Streamlit dashboard will be added later. Optional AI summarization remains disabled by default and will not be added until the core system is stable.

## Current Status

The five agents, the Manager pipeline, the CLI and the Streamlit dashboard (`streamlit run app.py`) are implemented. Optional AI summarization (local Ollama only, off by default) is implemented.

The original project plan is kept unchanged in:

```text
CyberShield_AI_Master_Playbook.md
```

## Planned Core Components

- Log Analyzer Agent
- Network Agent
- Threat Intelligence Agent
- Incident Response Agent
- Manager Agent

These are software components using transparent rules. They must not be described as independent AI models.

## Safety Rules

- Defensive educational use only.
- Use synthetic demo data or logs you are authorized to inspect.
- No unauthorized scanning, exploitation, password attacks, stealth, persistence, or destructive actions.
- No automatic IP blocking, account disabling, firewall changes, or remediation.
- Findings are investigation indicators, not proof of compromise.
- Do not commit secrets or upload sensitive logs to external AI services.

## Local Setup Plan

The proposed local Python version is Python 3.14. A local virtual environment will be used:

```powershell
py -3.14 -m venv .venv
```

Activate in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies after reviewing `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Run tests:

```powershell
python -m pytest
```

Install first: `python -m pip install -r requirements.txt`.

## Running the full pipeline

```text
python main.py                                   # built-in demo (data/demo_full_pipeline.csv)
python main.py --input my_events.csv --output report.json
python main.py --threshold 3 --window 5 --ports 4444,9001 --count-unknown-status
python main.py --ai-model llama3.2 --ai-lang ar     # optional, needs a local Ollama server
python tools/convert_ssh_log.py prototypes/real_login_sample.csv data/ssh_login_sample.csv
python -m pytest
```

Data flow (all agents connected through `cybershield/agents/manager.py`):

```text
load_events -> Log Analyzer + Network Agent + Threat Intelligence   (findings)
            -> Manager: dedupe exact duplicates, order by severity, assign finding-001...
            -> Incident Response (response plan linked to the same finding ids)
            -> build_report -> validated JSON report
```

Agent names in findings follow the schema: `log_analyzer`, `network_agent`, `threat_intelligence`.
`main.py` exits 0 on success, 1 if a detection agent failed, 2 if the input could not be loaded.
`prototypes/` holds the original standalone scripts, superseded by the agents above.


## Machine Learning (added)

The optional offline ML lab now trains and evaluates:
- Random Forest (supervised multi-class classification)
- XGBoost (supervised model comparison; gracefully reported if unavailable)
- Isolation Forest (unsupervised anomaly detection)

The label column is isolated to training/evaluation and is excluded from feature matrices. Numeric
identifier/time columns and constant/all-null columns are filtered. The default maximum is 250,000
CSV rows to avoid unexpectedly exhausting RAM. Metrics are held-out split results, not a guarantee
of production performance. See `ML_GUIDE_AR.md` for Windows commands and evaluation caveats.

Train from CLI:
```powershell
python -m cybershield.ml train --csv "C:\datasets\flows.csv" --label-column Label
python -m cybershield.ml status
python -m cybershield.ml predict --csv "C:\datasets\unlabeled_flows.csv" --output predictions.json
```

The Streamlit SOC dashboard includes a dark SOC-style traffic timeline and severity chart derived
from the loaded events, an ML training workspace, model metrics, feature importance, and optional
CSV inference. Start with `RUN_CYBERSHIELD_WINDOWS.bat` on Windows 11 or use the manual setup below.

### Optional AI providers

AI summaries remain off by default. Local Ollama remains supported. An optional hosted OpenAI
provider is also available from the dashboard; it requires `CYBERSHIELD_OPENAI_API_KEY` (or
`OPENAI_API_KEY`) and optionally `CYBERSHIELD_OPENAI_MODEL`. The summarizer sends only aggregate
counts, severities, agent names and rule IDs; it deliberately omits raw IPs, hostnames, usernames,
event IDs and event records. Hosted use still requires the team's explicit privacy approval.

## Research datasets and reproducible multi-source experiments
See `RESEARCH_DATASETS_AR.md` for official CIC-IDS2017, CSE-CIC-IDS2018, UNSW-NB15 and CICIoT2023 sources, usage notes, citation requirements and the safe multi-dataset workflow. Use `tools/benchmark_datasets.py` to train separate artifacts and record SHA-256 hashes; do not blindly concatenate incompatible feature schemas. See `DISCUSSION_PREP_AR.md` for the competition defense and likely jury questions.
