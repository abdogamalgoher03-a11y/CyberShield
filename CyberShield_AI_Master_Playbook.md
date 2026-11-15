# CyberShield AI — Master Project Playbook for Claude and Codex
**Version:** 1.0  
**Purpose:** This is the single source of truth for planning, building, testing, documenting, and demonstrating CyberShield AI from a clean Windows computer. Give this file to Claude or Codex at the start of every new working session.

---

## 0. How to use this file

1. Create a project folder named `CyberShield_AI`.
2. Open that folder in your coding tool (Codex, Claude Code, or another coding assistant that can inspect/edit local files).
3. Give the assistant this file and tell it to follow the **Master instruction** below.
4. Work through the phases in order. Do not ask the assistant to build the entire system in one huge step.
5. Keep this file in the repository as `PROJECT_PLAYBOOK.md`. Update the progress checklist at the end after each completed phase.
6. Use Git commits so you can undo mistakes and review team contributions.

### Master instruction to paste into Claude or Codex

> Read `PROJECT_PLAYBOOK.md` completely before doing anything. We are beginners/intermediate students building CyberShield AI from zero on Windows. Start by inspecting the current folder and computer environment without modifying anything. Explain what you find in beginner-friendly Arabic (Egyptian Arabic is fine), including what each command does and why it is needed. Then propose the smallest safe next step. Do not overwrite files blindly, do not claim a command or test succeeded unless you actually ran it, and do not skip tests. Work one phase at a time. Before installing software, changing system settings, deleting files, downloading a large AI model, or using a paid API, explain the impact and ask for approval. Never expose or commit secrets. Use synthetic demo data unless the user explicitly authorizes other data. Keep all security behavior defensive: no scanning external systems, exploitation, credential attacks, stealth, persistence, automatic IP blocking, or automatic account disabling. Keep the core app working without an AI model, an API key, or an internet connection after dependencies/data have been installed. At the end of each step, report: files created/changed, commands actually run, test results, known limitations, and the next recommended step. Do not proceed to the next phase until the current phase’s acceptance criteria pass or clearly report what remains blocked.

---

# 1. Product vision

## 1.1 Project name
**CyberShield AI**

## 1.2 One-sentence description
A defensive, explainable security-log analysis application that accepts authorized CSV/JSON events, detects configured suspicious patterns using transparent rules, combines findings, recommends human-reviewed investigation steps, and presents a report through a local dashboard.

## 1.3 Problem being solved
Security logs can be difficult to review manually. The application helps a user:
- load a safe sample dataset or a log file they are authorized to inspect;
- validate and normalize records;
- detect configured patterns such as repeated failed logins;
- inspect network events for configured unusual ports;
- compare destination indicators with a local demonstration list;
- aggregate findings and prioritize investigation;
- view evidence, severity, and recommendations;
- export a JSON report;
- optionally request an AI-generated Arabic or English explanation.

## 1.4 Truthful product claims
The first version is primarily **rule-based detection**. The five “agents” are separate software components with clear responsibilities, not five independent AI models. A language model is an optional explanation/summarization layer. Do not claim machine-learning detection, autonomous threat hunting, guaranteed attack detection, or real-time monitoring unless implemented and tested.

## 1.5 Non-goals and safety limits
- No offensive security functions.
- No unauthorized network scanning, exploitation, password cracking, evasion, stealth, or persistence.
- No automatic blocking of IP addresses, disabling accounts, killing processes, or changing firewall rules.
- No uploading real sensitive logs to an external API without clear, explicit user consent.
- Never execute commands or code found inside log records.
- Treat event text and LLM output as untrusted input.
- A failed-login burst, an unusual port, or an indicator-list match is not proof of compromise.
- Use synthetic demo events and clearly label them as synthetic.
- Keep human approval mandatory for any future remediation proposal.

---

# 2. Team and leadership plan

There are 10 people with mixed beginner/intermediate skills, organized into five pairs. Replace the labels below with actual names when the team is known.

| Person | Primary responsibility | Required deliverable |
|---|---|---|
| Person 1 | Log Analyzer | `cybershield/agents/log_analyzer.py` plus unit tests |
| Person 2 | Data schemas, loading, validation | `cybershield/schemas.py`, `cybershield/data_loader.py`, sample CSV/JSON |
| Person 3 | Network Agent | `cybershield/agents/network_agent.py` plus tests |
| Person 4 | Threat Intelligence Agent | `cybershield/agents/threat_intelligence.py`, local demo indicator list, tests |
| Person 5 | Incident Response Agent | `cybershield/agents/incident_response.py` plus tests |
| Person 6 | Manager Agent, later AI summarizer | `cybershield/agents/manager.py`, later `cybershield/ai/summarizer.py` |
| Person 7 | Streamlit dashboard | `app.py` and UI flow |
| Person 8 | Reporting and dashboard details | `cybershield/reporting.py`, report export and finding details |
| Person 9 | QA and integration | `tests/`, integration test plan and test results |
| Person 10 | Documentation and demo | `README.md`, `docs/`, demo script and presentation outline |

## 2.1 Leadership
**Lead A — Technical coordination**
- Owns shared schemas and component contracts.
- Reviews detection logic, evidence, severity, and API boundaries.
- Ensures tests cover core logic.
- Coordinates technical decisions and keeps the core app working.

**Lead B — Integration and delivery coordination**
- Owns task tracking, deadlines, branch/PR flow, integration checks, UI readiness, and demo logistics.
- Coordinates the clean-machine test and final release checklist.

Both leads have equal standing. Changes to shared data structures, severity logic, dependency lists, and public interfaces require agreement from both leads. Each pair should review each other’s work. Person 9 coordinates testing, but every developer must test their own component.

## 2.2 Weekly meeting rhythm
- One kickoff meeting each week: goals, owners, blockers, definition of done.
- Short check-ins during the week: completed, next, blocker.
- One integration/review meeting at the end of the week.
- Every task should have an owner, expected deliverable, and acceptance criteria.
- Never wait until the end to merge everything. Integrate small changes continuously.

---

# 3. Suggested architecture and repository structure

Start simple and add files only when they are needed. Target structure:

```text
CyberShield_AI/
├── PROJECT_PLAYBOOK.md
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── main.py
├── app.py
├── data/
│   ├── demo_login_events.csv
│   ├── demo_network_events.csv
│   └── demo_threat_indicators.json
├── cybershield/
│   ├── __init__.py
│   ├── schemas.py
│   ├── data_loader.py
│   ├── reporting.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── log_analyzer.py
│   │   ├── network_agent.py
│   │   ├── threat_intelligence.py
│   │   ├── incident_response.py
│   │   └── manager.py
│   └── ai/
│       ├── __init__.py
│       └── summarizer.py
├── tests/
│   ├── test_schemas.py
│   ├── test_data_loader.py
│   ├── test_log_analyzer.py
│   ├── test_network_agent.py
│   ├── test_threat_intelligence.py
│   ├── test_incident_response.py
│   ├── test_manager.py
│   └── test_reporting.py
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA_FORMAT.md
    ├── TEST_PLAN.md
    └── DEMO_SCRIPT.md
```

## 3.1 Component responsibilities

### `schemas.py`
Defines and documents a normalized event shape and finding shape. Prefer simple, typed Python structures or documented dictionaries. Avoid inventing confidence scores without a defensible definition.

### `data_loader.py`
Reads user-selected CSV/JSON files, validates required fields and data types, normalizes valid records, and returns clear row-level errors. It must not execute file contents or accept arbitrary filesystem paths without a deliberate user selection.

### Agent 1: Log Analyzer
Detect repeated failed authentication attempts from a source IP within a configurable interval. Use a configurable threshold. Evidence must identify the relevant event IDs/counts and configured time window.

### Agent 2: Network Agent
Inspect provided network-event records and flag connections to configured unusual ports. A port match is only an indicator; explain that context is needed.

### Agent 3: Threat Intelligence Agent
Compare destination indicators with a local list explicitly labelled demo/test data. Never present reserved documentation IPs or synthetic values as actual malicious infrastructure.

### Agent 4: Incident Response Agent
Turn findings into a safe investigation checklist. Recommendations only; no automatic remediation. State why the action is suggested and whether human approval is required.

### Agent 5: Manager Agent
Combine findings into one report, deduplicate only where justified, calculate an explainable overall risk using documented rules, and preserve evidence/provenance. Do not silently let AI change evidence or severity.

### Optional AI summarizer
Receives only the minimum sanitized report fields needed to explain results. AI is off by default. Validate outputs and fall back to the rule-based report if the model is unavailable or returns invalid output. Label generated text as AI-generated and communicate uncertainty.

### `reporting.py`
Builds a stable report object and exports JSON. CSV export is optional and must not delay the first working version.

### `app.py`
Streamlit dashboard: demo/upload controls, total findings, severity summary, searchable/filterable findings, evidence/recommendations, AI status, JSON download, and a clear limitations disclaimer.

### `main.py`
Simple command-line/demo entry point that works without Streamlit and without an AI service.

---

# 4. Shared data contracts

Agree on these contracts before the agents are developed in parallel. The coding assistant must explain the design and add tests.

## 4.1 Normalized event — illustrative shape
Adapt fields only after documenting the decision.

```json
{
  "event_id": "event-001",
  "timestamp": "2026-01-01T10:00:00Z",
  "event_type": "login",
  "source_ip": "192.0.2.10",
  "destination_ip": null,
  "username": "demo-user",
  "status": "failure",
  "destination_port": null,
  "protocol": null
}
```

Use reserved/documentation addresses and clearly synthetic usernames for demo data. Timestamps must have a documented timezone policy. Do not assume every field applies to every event type.

## 4.2 Finding — illustrative shape

```json
{
  "agent": "Log Analyzer",
  "rule_id": "AUTH-REPEATED-FAILURES",
  "title": "Repeated failed logins",
  "severity": "HIGH",
  "evidence": "5 failed login events from one source within the configured interval.",
  "recommendation": "Review the authentication logs and verify with the system owner.",
  "event_ids": ["event-001", "event-002"],
  "requires_human_approval": true
}
```

Severity should use a documented allowed set such as `LOW`, `MEDIUM`, `HIGH`. Include `confidence` only if its meaning is defensible and documented. Do not use an invented decimal as though it were a calibrated probability.

## 4.3 Manager report — illustrative shape

```json
{
  "schema_version": "1.0",
  "generated_at": "ISO-8601 timestamp",
  "input_summary": {
    "source_type": "demo",
    "events_processed": 0,
    "invalid_rows": 0
  },
  "overall_risk": "LOW",
  "findings": [],
  "response_plan": [],
  "limitations": [
    "Findings are indicators that require investigation, not proof of compromise."
  ],
  "ai_summary": null
}
```

The final field names may change during implementation, but once agreed they must be used consistently by all components and documented.

---

# 5. Software installation and device setup

## 5.1 Required tools

Install only from official sources. Check the current supported versions and system requirements at installation time; do not hard-code assumptions that may become stale.

1. **Python 3.12 or another currently supported Python version compatible with the dependencies.**  
   Official downloads: https://www.python.org/downloads/  
   During Windows installation, enable the option to add Python to PATH if offered.
2. **Visual Studio Code.**  
   https://code.visualstudio.com/  
   Install the Microsoft Python extension and Pylance extension.
3. **Git.**  
   https://git-scm.com/downloads
4. **GitHub account/repository access.**  
   https://github.com/  
   Git is the local version-control program; GitHub hosts the shared repository.
5. **A modern web browser** for viewing Streamlit locally.
6. **PowerShell or Windows Terminal** for commands; Windows PowerShell is sufficient.

## 5.2 Optional tools
- **Ollama** for a local AI model: https://ollama.com/  
  Install only on the designated AI/demo machine after checking its RAM, free storage, and the selected model’s requirements. Downloading a model can consume several gigabytes or more. The base project must not depend on it.
- **OpenAI API**: https://platform.openai.com/  
  Optional, may incur charges, and is separate from a ChatGPT subscription. Do not enable it without explicit approval, a clear cost/privacy explanation, and secure key handling.
- **Postman** only if a real HTTP API is added and the team needs to test it. Not required for the initial local prototype.

## 5.3 Which team members need what?
- All 10: Python, VS Code, Python/Pylance extensions, Git, repository access, browser.
- All developers: the project’s `requirements.txt` in a virtual environment when they begin coding/testing.
- People working on UI (7–8) and anyone running the UI: Streamlit dependency.
- Person 9 and developers writing tests: pytest dependency. Prefer that the team install the complete approved development requirements so results are consistent.
- One designated machine only: Ollama and a suitable model, if the team chooses local AI.
- No one needs a database, Docker, Kubernetes, a paid API, or a security scanner for the initial version unless a documented requirement emerges.

## 5.4 Windows setup commands

The assistant must first check whether tools are already installed. Explain every command before running it, and ask for approval before installing software or changing system settings.

Check tools:

```powershell
python --version
py --version
git --version
code --version
```

Create/activate a virtual environment from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks activation, do not tell the user to weaken system-wide execution policy. Explain the issue and offer Command Prompt activation instead:

```bat
.venv\Scripts\activate.bat
```

Once `requirements.txt` has been reviewed and approved:

```powershell
python -m pip install -r requirements.txt
```

Run tests and the core app:

```powershell
python -m pytest
python main.py
```

After the UI phase:

```powershell
streamlit run app.py
```

Do not run a command that depends on a file before the file exists. Do not claim a command passed unless its actual output was observed.

## 5.5 Dependency policy
- Start with Python standard library for core analysis where practical.
- Add `pytest` for tests and `streamlit` for the dashboard when those phases begin.
- Add `pandas` only if it simplifies real data-handling needs.
- Add an HTTP client only if an actual integration needs it.
- Keep `requirements.txt` accurate and avoid unnecessary packages.
- Pin versions if repeatable installs require it, after testing a compatible set.
- Do not install a `.env` package unless needed. If a `.env` file is introduced, provide `.env.example`, ignore the real `.env` in Git, and never commit secrets.

Example `.gitignore` entries:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.env
*.py[cod]
cybershield_report.json
.DS_Store
```

Do not ignore demo datasets, test files, README, or `.env.example`.

---

# 6. Six-week roadmap and acceptance criteria

The schedule is a planning estimate. Adjust it to the team’s availability and the actual state of the repository.

## Week 1 — Foundation and design
**Goal:** Agree on contracts before parallel development.

Tasks:
- Create Git repository and initial folder structure.
- Write `README.md`, `PROJECT_PLAYBOOK.md`, and `.gitignore`.
- Define normalized event, finding, and report schemas.
- Decide on timestamp/timezone handling and severity logic.
- Create small, clearly labelled synthetic test fixtures.
- Write a test plan and assign owners.

Acceptance criteria:
- Every person can clone/open the repository.
- The shared contracts are documented and accepted by both leads.
- No secrets or real sensitive logs are present.
- Initial structure and run instructions are committed.

## Week 2 — Core agents
**Goal:** Implement the five software components in small steps.

Tasks:
- Implement schema structures and basic validation.
- Implement repeated-failed-login rule.
- Implement unusual-port rule with configuration.
- Implement local demo-indicator matching.
- Implement human-reviewed response recommendations.
- Implement manager aggregation and explainable severity.
- Add unit tests as each component is written.

Acceptance criteria:
- Each agent has clear input/output and tests.
- Empty inputs behave predictably.
- Every finding contains a reason/evidence and a safe recommendation.
- Demo indicators are labelled as test-only.
- The app can run without any AI package or API.

## Week 3 — CSV/JSON loading and integration
**Goal:** Accept user-selected files safely and run the full engine.

Tasks:
- Support documented CSV/JSON formats.
- Validate required columns/keys and field types.
- Return row-level validation errors.
- Normalize valid rows.
- Connect loader → agents → manager → JSON report.
- Add integration tests and a safe demo dataset.

Acceptance criteria:
- Valid sample CSV/JSON can be analyzed.
- Malformed/empty input yields understandable messages rather than an unhandled traceback.
- Uploaded file content is never executed.
- JSON report structure is stable and documented.

## Week 4 — Streamlit dashboard
**Goal:** Make the system usable without editing Python code.

Tasks:
- Add demo mode and file-upload controls.
- Show total findings and severity counts.
- Add filters/search by severity and agent.
- Show evidence, event IDs, and recommendations.
- Add JSON download.
- Clearly label demo data and include limitations disclaimer.
- Test the app on another team member’s computer.

Acceptance criteria:
- `streamlit run app.py` works.
- Dashboard results come from the actual analysis engine, not hard-coded display data.
- Loading, success, and error states are understandable.
- JSON download contains the same findings shown in the report.

## Week 5 — Optional AI summarization
**Goal:** Add a safe explanation layer without making the app depend on it.

Tasks:
- Keep AI mode off by default.
- Add a status/configuration section.
- Test Ollama/model availability on the designated machine if chosen.
- Send only necessary sanitized report fields to the model.
- Validate model output and fall back if it fails.
- Label the summary as AI-generated.
- Keep evidence and severity controlled by deterministic logic.
- Consider external API only after privacy and cost review.

Acceptance criteria:
- The base application works when Ollama/API is unavailable.
- AI failure never crashes the core app.
- Secrets are not logged, displayed, or committed.
- No external upload happens silently.
- AI text communicates uncertainty and does not claim an attack is confirmed without evidence.

## Week 6 — Evaluation, documentation, and demo
**Goal:** Deliver a reproducible student prototype.

Tasks:
- Prepare labelled benign and suspicious synthetic cases.
- Measure precision/recall/false-positive rate only if labels and counts support valid calculations.
- Measure processing time on the test data and record the environment.
- Run all tests.
- Test from a clean environment.
- Complete README, architecture notes, data format, limitations, and demo script.
- Rehearse the demo and assign speaking roles.

Acceptance criteria:
- A new team member can set up and run the project from documentation.
- Core analysis works without AI/API.
- Five components have documented responsibilities.
- CSV/JSON validation, report export, and dashboard work.
- Tests and limitations are documented.
- The demo clearly states that synthetic events are not real attacks.

---

# 7. Git and integration workflow

## 7.1 Initial repository setup
The assistant should explain and ask before executing repository-changing commands. Once the project directory is ready, typical commands are:

```powershell
git init
git add .
git commit -m "chore: initialize CyberShield AI project"
```

Create a GitHub repository through the website or approved tooling, then connect it using the exact URL supplied by the user. Do not invent repository URLs or expose private credentials.

## 7.2 Branch naming
Examples:
- `feature/event-schema`
- `feature/log-analyzer`
- `feature/network-agent`
- `feature/threat-intelligence`
- `feature/incident-response`
- `feature/manager`
- `feature/dashboard`
- `feature/json-report`
- `test/integration-suite`
- `docs/demo-guide`

## 7.3 Pull request checklist
Before merging:
- [ ] Task matches the agreed scope.
- [ ] Shared contracts were not changed without approval.
- [ ] Tests were added/updated and actually run.
- [ ] No secrets, personal data, or unnecessary generated files are included.
- [ ] Error paths and empty input are handled.
- [ ] Documentation is updated where needed.
- [ ] A reviewer has checked the diff.
- [ ] Integration tests pass after merge.

## 7.4 Definition of a finished task
A task is not finished merely because code exists. It is finished when:
1. the implementation matches the agreed responsibility;
2. tests cover normal and relevant failure cases;
3. the owner explains how it works;
4. another person reviews it;
5. it is integrated and tested with the main branch;
6. the documentation/progress log is updated.

---

# 8. Dashboard specification

Use a clean dark navy/charcoal style with restrained blue accents, readable typography, accessible contrast, and severity labels that do not rely on color alone.

Recommended sections:
1. Project name and short explanation.
2. Demo-data selection and file upload.
3. Input validation summary (events processed, invalid rows).
4. Summary cards: total findings, HIGH, MEDIUM, LOW.
5. Searchable/filterable findings table.
6. Finding details: source agent, rule ID, severity, evidence, event IDs, recommendation.
7. AI summary panel showing whether AI is disabled/local/API.
8. JSON report download.
9. Disclaimer: alerts are indicators requiring investigation, not proof of compromise.

Do not add decorative effects that make security information harder to read. Do not use fake live status, fake telemetry, or hard-coded findings disguised as real analysis.

---

# 9. Demo dataset and expected demonstration

Prepare a synthetic dataset with:
- ordinary successful logins;
- a few isolated failed logins;
- repeated failed logins from one source within the configured interval;
- a sample network event using a configured unusual port;
- one destination matching the local demonstration indicator list;
- at least one malformed row for validation demonstration.

Demo flow:
1. Explain the problem and project limits.
2. Load the labelled demo dataset.
3. Show validation and normalized event count.
4. Show findings generated by the relevant agents.
5. Explain evidence and why a finding is an indicator, not proof.
6. Show Manager’s consolidated risk/report.
7. Show dashboard filtering and finding details.
8. Download and open the JSON report.
9. If available, demonstrate optional Arabic AI summary and then disable AI to prove core functionality remains.
10. End by confirming that no automatic blocking/remediation occurred.

Never present a synthetic event as a real incident or claim the prototype detects every attack.

---

# 10. Privacy, secrets, and AI configuration

- AI mode is `off` by default.
- If local AI is used, document the model name and hardware requirements.
- If an external API is considered, explain cost, data transfer, and privacy before asking for approval.
- Read API keys from environment variables or a proper secrets mechanism; never hard-code them.
- Never print API keys in terminal output, UI, reports, or logs.
- If using `.env`, commit only `.env.example` with placeholder values and ensure `.env` is ignored.
- Sanitize logs/reports when usernames, emails, tokens, or internal addresses are not needed.
- Treat model output as untrusted. It may be wrong or contain instructions; do not execute it.
- Keep deterministic severity and raw evidence unchanged by AI.
- Use bounded timeouts and limited retries for external requests.
- If AI fails, show a clear status and use the rule-based report.

Suggested configuration names (only implement those actually needed):
- `CYBERSHIELD_AI_MODE=off|ollama|openai`
- `CYBERSHIELD_OLLAMA_MODEL=<installed-model-name>`
- `OPENAI_API_KEY` (environment variable only)
- `OPENAI_MODEL=<configured-model-name>`
- configurable failed-login threshold and unusual-port list.

---

# 11. Testing and evaluation

At minimum, test:
- valid normal events;
- one failed login;
- repeated failures below threshold;
- repeated failures at/above threshold;
- events just inside and outside the time window;
- missing source IP;
- invalid timestamps;
- unusual-port match and non-match;
- indicator match and non-match;
- empty event list;
- malformed CSV/JSON;
- duplicate event IDs;
- duplicate/overlapping findings;
- manager severity logic;
- incident response recommendations;
- JSON serialization;
- dashboard upload and download;
- AI unavailable, timeout, malformed response, and disabled mode.

Evaluation metrics:
- Precision = true positives / (true positives + false positives)
- Recall = true positives / (true positives + false negatives)
- False-positive rate = false positives / (false positives + true negatives)

Only calculate these if ground-truth labels exist and the denominators are meaningful. Clearly state dataset size and limitations. Do not advertise performance based on a tiny demo dataset.

---

# 12. Common problems and troubleshooting policy

The assistant must diagnose from the actual error text and environment, not guess.

- **`python` not found:** check Python installation, try `py --version`, and explain PATH carefully.
- **`git` not found:** check installation and terminal restart.
- **PowerShell activation blocked:** offer Command Prompt activation; do not weaken system-wide policy casually.
- **Package install fails:** capture the exact error, check Python version/network, and adjust only what is necessary.
- **`ModuleNotFoundError`:** check the active virtual environment and install the approved requirements there.
- **Streamlit command not found:** run `python -m streamlit run app.py` after confirming Streamlit is installed in the active environment.
- **Port already in use:** explain the cause and offer a safe alternate port.
- **Ollama/model unavailable:** disable AI gracefully; do not block core work.
- **Git merge conflict:** explain both versions and resolve deliberately; do not overwrite one side without review.
- **Test failure:** reproduce, inspect the failing assertion, fix the cause, rerun the relevant test and full suite.
- **Missing files:** inspect the repository before creating or overwriting anything.

---

# 13. Rules for Claude and Codex

1. Start each session by reading this playbook and inspecting the actual repository.
2. Never assume a file exists just because it is listed in this plan.
3. Before editing, list the files you plan to change and why.
4. Preserve working behavior; make small, reversible changes.
5. Explain technical terms in beginner-friendly Arabic, and include English terms/code names so the team learns them.
6. Explain every terminal command before asking the user to run it.
7. Do not claim a program has been installed, a file created, or a test passed unless the action actually occurred and the result was checked.
8. Do not automatically download large models or install system-wide tools without asking.
9. Do not overwrite the project with a generated scaffold if working files already exist.
10. Use tests after every meaningful change.
11. Do not introduce paid services, telemetry, cloud hosting, databases, Docker, or extra frameworks without explaining why and getting approval.
12. Keep AI optional and security behavior defensive.
13. End each work session with:
    - Summary in plain Arabic.
    - Files created/changed.
    - Commands actually run.
    - Tests run and their actual results.
    - Remaining issues/risks.
    - Exact next step.
14. Update the progress checklist below. If blocked, explain the blocker and do not mark the task complete.

---

# 14. Progress checklist

Mark a checkbox only after the result is verified.

## Setup
- [ ] Read this playbook and inspected the current folder.
- [ ] Confirmed installed versions of Python, Git, and VS Code.
- [ ] Created the project virtual environment.
- [ ] Created Git repository and `.gitignore`.
- [ ] Confirmed team access to the repository.
- [ ] Approved and documented shared event/finding/report schemas.

## Core engine
- [ ] Schema structures and validation implemented.
- [ ] Log Analyzer implemented and tested.
- [ ] Network Agent implemented and tested.
- [ ] Threat Intelligence Agent implemented and tested.
- [ ] Incident Response Agent implemented and tested.
- [ ] Manager Agent implemented and tested.
- [ ] Demo datasets clearly labelled synthetic.
- [ ] CSV/JSON loading and validation implemented.
- [ ] CLI demo and JSON report work.

## Interface and optional AI
- [ ] Streamlit dashboard implemented and tested.
- [ ] Search/filter/detail views work.
- [ ] JSON download works.
- [ ] AI disabled mode works.
- [ ] Local AI, if chosen, fails gracefully when unavailable.
- [ ] External API, if chosen, passed cost/privacy approval and secure key review.

## Final delivery
- [ ] Unit and integration tests pass.
- [ ] Clean-environment setup verified.
- [ ] README and data format documentation complete.
- [ ] Limitations and privacy practices documented.
- [ ] Demo scenario rehearsed.
- [ ] All ten members can explain their own part and the full data flow.

---

# 15. First action — do this now

Do **not** start by generating every source file.

The first assistant session should:
1. Read this playbook.
2. Inspect the current folder and list existing files.
3. Check whether Python, Git, and VS Code are installed, without changing the system.
4. Explain the results in Arabic.
5. Identify the smallest safe first step.
6. Ask before installing anything or changing settings.
7. After approval, set up the minimal project structure and Git workflow.
8. Define and test the shared data contracts before parallelizing agent work.

**The first milestone is a small, tested core—not a large unverified code dump.**
