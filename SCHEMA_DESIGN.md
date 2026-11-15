# CyberShield AI Schema Design

## Status

This document records the approved data contracts for CyberShield AI before
Python implementation begins. They support defensive, rule-based analysis of
authorized CSV and JSON security-log data.

These contracts do not authorize automatic remediation. Findings are
investigation indicators, not proof of compromise. AI summarization is optional
and disabled by default.

## Shared Conventions

- Schema version: `1.0`.
- Timestamps use RFC 3339 / ISO 8601 and are stored in UTC with the `Z` suffix.
- Missing applicable data is represented by JSON `null`, not an empty string,
  `"N/A"`, or `"-"`.
- Rejected records are not silently discarded. The report retains their source
  references and validation errors, but never raw record values or sensitive
  values.
- Recommendations are defensive investigation steps only. They do not block
  IPs, disable accounts, change firewall settings, execute commands, or alter
  systems automatically.

## 1. Normalized Event Schema

A normalized event is a validated record accepted from an authorized CSV or
JSON source. It is the common input contract for the rule-based components.

| Field | Type | Required | Example | Validation and purpose |
| --- | --- | --- | --- | --- |
| `schema_version` | `string` | Yes | `"1.0"` | Version of this event contract. |
| `event_id` | `string` | Yes | `"evt-src-001-0007"` | Generated from `source_id` and `source_row_number` as `evt-{source_id}-{source_row_number}`. It must be unique among accepted events in an import. |
| `timestamp` | `string` | Yes | `"2026-01-01T10:00:00Z"` | RFC 3339 / ISO 8601 timestamp with an explicit timezone (`Z` or an offset such as `+02:00`). It is normalized and stored in UTC. A timestamp without a timezone is rejected; the system never guesses local time. |
| `event_type` | `string` | Yes | `"authentication"` | Allowed values: `authentication`, `network`, `other`. |
| `status` | `string` or `null` | No | `"failure"` | Allowed values: `success`, `failure`, `unknown`, or `null` where status does not apply. |
| `source_ip` | `string` or `null` | No | `"192.0.2.10"` | A valid IPv4 or IPv6 address, or `null`. Invalid values are never used for matching or analysis. |
| `destination_ip` | `string` or `null` | No | `"198.51.100.20"` | A valid IPv4 or IPv6 address, or `null`. |
| `destination_host` | `string` or `null` | No | `"demo-indicator.example"` | A non-empty host or domain name after trimming and normalizing to lowercase, or `null`. |
| `username` | `string` or `null` | No | `"demo-user"` | A non-empty username after trimming, or `null`. It is untrusted data and must never be executed or interpreted as a command. |
| `destination_port` | `integer` or `null` | No | `8443` | Integer from `1` to `65535`, or `null`. |
| `protocol` | `string` or `null` | No | `"tcp"` | Allowed values: `tcp`, `udp`, `icmp`, `other`, or `null`. |
| `source_id` | `string` | Yes | `"src-001"` | A new opaque identifier for every import operation, including repeat imports of the same file. It must not expose an absolute path or sensitive data. |
| `source_name` | `string` | Yes | `"demo_login_events.csv"` | Source filename or safe source label only; never an absolute local path. |
| `source_row_number` | `integer` | Yes | `7` | Original one-based data-record position in the imported source. |
| `source_record_id` | `string` or `null` | No | `"login-007"` | Original source-provided record identifier when available. It does not replace `event_id`. |

### IP validation policy

- An invalid IP is rejected when that IP is required for the event to be valid
  or for a rule that will analyze the event.
- When an IP is not required for the event's valid purpose, the event may be
  accepted with that field set to `null` and a recorded validation warning.
- Validation errors and warnings must never be ignored silently.
- An invalid IP must not reach any indicator matching, grouping, or detection
  logic.

### Rejected record policy

Rejected records do not become normalized events. Their source row reference
and validation errors appear in `input_summary.rejected_records`. Raw values,
raw rows, and sensitive values are not stored in the report.

### Valid example

```json
{
  "schema_version": "1.0",
  "event_id": "evt-src-001-0007",
  "timestamp": "2026-01-01T10:00:00Z",
  "event_type": "authentication",
  "status": "failure",
  "source_ip": "192.0.2.10",
  "destination_ip": null,
  "destination_host": null,
  "username": "demo-user",
  "destination_port": null,
  "protocol": null,
  "source_id": "src-001",
  "source_name": "demo_login_events.csv",
  "source_row_number": 7,
  "source_record_id": "login-007"
}
```

## 2. Finding Schema

A finding is a transparent, rule-based investigation indicator produced by a
component. It is not proof of compromise.

| Field | Type | Required | Example | Validation and purpose |
| --- | --- | --- | --- | --- |
| `finding_id` | `string` | Yes | `"finding-001"` | Unique identifier within the report. |
| `agent` | `string` | Yes | `"log_analyzer"` | Allowed values: `log_analyzer`, `network_agent`, `threat_intelligence`, `incident_response`, `manager`. |
| `rule_id` | `string` | Yes | `"AUTH-REPEATED-FAILURES"` | Stable rule identifier in uppercase hyphenated form. |
| `title` | `string` | Yes | `"Repeated failed logins"` | Short factual title that does not assert a confirmed incident. |
| `description` | `string` | Yes | `"Five failed authentication events were observed from one source IP within the configured ten-minute window."` | Explainable description of the rule outcome. |
| `severity` | `string` | Yes | `"HIGH"` | Allowed values only: `LOW`, `MEDIUM`, `HIGH`. |
| `evidence` | `array<EvidenceItem>` | Yes | See example | A non-empty list of evidence items supporting the finding. |
| `event_ids` | `array<string>` | Yes | `["evt-src-001-0007"]` | Unique event IDs. Every ID must exist among accepted normalized events. |
| `recommendation` | `string` | Yes | `"Review the related authentication records and verify the activity with the system owner."` | Defensive investigation recommendation only. |
| `requires_human_approval` | `boolean` | Yes | `true` | Must be `true` in version `1.0`. |
| `limitations` | `array<string>` | Yes | `["This is an investigation indicator, not proof of compromise."]` | Explains uncertainty and interpretation limits. |

### EvidenceItem

| Field | Type | Required | Example | Validation and purpose |
| --- | --- | --- | --- | --- |
| `kind` | `string` | Yes | `"event_count"` | Allowed values: `event_count`, `time_window`, `port_match`, `indicator_match`. |
| `description` | `string` | Yes | `"Five failed authentication events were observed."` | Human-readable explanation of the evidence. |
| `value` | `integer` or `string` | Yes | `5` | Integer for counts or ports; string for a bounded explanatory value such as `"10 minutes"` or a local demo indicator. |
| `event_ids` | `array<string>` | No | `["evt-src-001-0007"]` | If present, each ID must also appear in the parent finding's `event_ids`. |

### Evidence consistency rules

- `Finding.event_ids` is the complete list of accepted events that support a
  finding.
- Every `event_id` in `Finding.event_ids` must reference an accepted normalized
  event from the same analysis run.
- `EvidenceItem.event_ids`, when present, must be a subset of
  `Finding.event_ids`.
- `event_count` and `time_window` evidence must describe the events listed by
  the finding.
- `port_match` must refer to event evidence with a matching valid
  `destination_port`.
- `indicator_match` must refer to a matching valid `destination_ip` or
  `destination_host` and a local list labelled demo/test data.
- No confidence score is included. The system is rule-based and has no
  calibrated probability model.

### Valid example

```json
{
  "finding_id": "finding-001",
  "agent": "log_analyzer",
  "rule_id": "AUTH-REPEATED-FAILURES",
  "title": "Repeated failed logins",
  "description": "Five failed authentication events were observed from one source IP within the configured ten-minute window.",
  "severity": "HIGH",
  "evidence": [
    {
      "kind": "event_count",
      "description": "Five failed authentication events were observed.",
      "value": 5,
      "event_ids": [
        "evt-src-001-0007",
        "evt-src-001-0008",
        "evt-src-001-0009",
        "evt-src-001-0010",
        "evt-src-001-0011"
      ]
    },
    {
      "kind": "time_window",
      "description": "All related events occurred within ten minutes.",
      "value": "10 minutes",
      "event_ids": [
        "evt-src-001-0007",
        "evt-src-001-0008",
        "evt-src-001-0009",
        "evt-src-001-0010",
        "evt-src-001-0011"
      ]
    }
  ],
  "event_ids": [
    "evt-src-001-0007",
    "evt-src-001-0008",
    "evt-src-001-0009",
    "evt-src-001-0010",
    "evt-src-001-0011"
  ],
  "recommendation": "Review the related authentication records and verify the activity with the system owner.",
  "requires_human_approval": true,
  "limitations": [
    "This is an investigation indicator, not proof of compromise."
  ]
}
```

## 3. Report Schema

The report combines ingestion results, findings, risk calculation, and a
human-reviewed response plan. It must be generated without AI, external APIs,
or an internet connection.

| Field | Type | Required | Example | Validation and purpose |
| --- | --- | --- | --- | --- |
| `schema_version` | `string` | Yes | `"1.0"` | Version of this report contract. |
| `report_id` | `string` | Yes | `"report-20260101-001"` | Traceable report identifier. |
| `generated_at` | `string` | Yes | `"2026-01-01T10:15:00Z"` | RFC 3339 / ISO 8601 UTC timestamp. |
| `input_summary` | `object` | Yes | See below | Summary of input source and validation results. |
| `findings` | `array<Finding>` | Yes | `[]` | Findings that satisfy the Finding Schema; the list may be empty. |
| `overall_risk` | `string` | Yes | `"HIGH"` | Allowed values: `LOW`, `MEDIUM`, `HIGH`. Calculated from the highest finding severity. |
| `overall_risk_reason` | `string` | Yes | `"At least one HIGH-severity finding is present."` | Plain-language explanation of the risk result. |
| `response_plan` | `array<ResponsePlanItem>` | Yes | See below | Defensive, human-reviewed investigation steps. |
| `analysis_warnings` | `array<string>` | Yes | `["One input record was rejected during validation."]` | Warnings that affect interpretation or completeness. |
| `limitations` | `array<string>` | Yes | `["Findings are indicators requiring investigation, not proof of compromise."]` | Report-level limitations. |
| `ai_summary` | `object` | Yes | `{ "status": "disabled", "content": null }` | Optional AI explanation state. The base report always provides it in disabled form. |

### input_summary

| Field | Type | Required | Example | Validation and purpose |
| --- | --- | --- | --- | --- |
| `source_type` | `string` | Yes | `"csv"` | Allowed values: `csv`, `json`, `demo`. |
| `source_name` | `string` | Yes | `"demo_login_events.csv"` | Safe filename or source label only; no absolute local path. |
| `records_received` | `integer` | Yes | `11` | Number of input records before validation; greater than or equal to zero. |
| `events_accepted` | `integer` | Yes | `10` | Number of accepted normalized events; greater than or equal to zero. |
| `records_rejected` | `integer` | Yes | `1` | Number of rejected records; greater than or equal to zero. |
| `rejected_records` | `array<object>` | Yes | See below | One safe reference object for every rejected record. |

The following rules are mandatory:

```text
records_received = events_accepted + records_rejected
len(rejected_records) = records_rejected
```

Every rejected record reference has this shape:

```json
{
  "source_row_number": 6,
  "errors": [
    "timestamp must include an explicit timezone"
  ]
}
```

It does not include raw event values, raw rows, credentials, tokens, or other
sensitive data.

### ResponsePlanItem

| Field | Type | Required | Example | Validation and purpose |
| --- | --- | --- | --- | --- |
| `related_finding_id` | `string` or `null` | No | `"finding-001"` | When present, it must refer to a finding in this report. |
| `action` | `string` | Yes | `"Review the related authentication records with the system owner."` | Defensive investigation step only. |
| `rationale` | `string` | Yes | `"The rule detected repeated failures from one source within the configured time window."` | Explains why the action is recommended. |
| `requires_human_approval` | `boolean` | Yes | `true` | Must be `true` in version `1.0`. |

### Risk calculation

- No findings: `LOW`.
- At least one `HIGH` finding: `HIGH`.
- No `HIGH` findings and at least one `MEDIUM` finding: `MEDIUM`.
- Only `LOW` findings: `LOW`.

### AI Summary

AI is disabled by default. A report generated by the core system uses:

```json
{
  "status": "disabled",
  "content": null
}
```

Future values for `status` may be `unavailable`, `generated`, or `failed`, but
they are not part of the current implementation. AI output must never change
deterministic findings, evidence, severity, or the response plan.

### Valid report example

```json
{
  "schema_version": "1.0",
  "report_id": "report-20260101-001",
  "generated_at": "2026-01-01T10:15:00Z",
  "input_summary": {
    "source_type": "csv",
    "source_name": "demo_login_events.csv",
    "records_received": 11,
    "events_accepted": 10,
    "records_rejected": 1,
    "rejected_records": [
      {
        "source_row_number": 6,
        "errors": [
          "timestamp must include an explicit timezone"
        ]
      }
    ]
  },
  "findings": [
    {
      "finding_id": "finding-001",
      "agent": "log_analyzer",
      "rule_id": "AUTH-REPEATED-FAILURES",
      "title": "Repeated failed logins",
      "description": "Five failed authentication events were observed from one source IP within the configured ten-minute window.",
      "severity": "HIGH",
      "evidence": [
        {
          "kind": "event_count",
          "description": "Five failed authentication events were observed.",
          "value": 5,
          "event_ids": [
            "evt-src-001-0007",
            "evt-src-001-0008",
            "evt-src-001-0009",
            "evt-src-001-0010",
            "evt-src-001-0011"
          ]
        },
        {
          "kind": "time_window",
          "description": "All related events occurred within ten minutes.",
          "value": "10 minutes",
          "event_ids": [
            "evt-src-001-0007",
            "evt-src-001-0008",
            "evt-src-001-0009",
            "evt-src-001-0010",
            "evt-src-001-0011"
          ]
        }
      ],
      "event_ids": [
        "evt-src-001-0007",
        "evt-src-001-0008",
        "evt-src-001-0009",
        "evt-src-001-0010",
        "evt-src-001-0011"
      ],
      "recommendation": "Review the related authentication records and verify the activity with the system owner.",
      "requires_human_approval": true,
      "limitations": [
        "This is an investigation indicator, not proof of compromise."
      ]
    }
  ],
  "overall_risk": "HIGH",
  "overall_risk_reason": "At least one HIGH-severity finding is present.",
  "response_plan": [
    {
      "related_finding_id": "finding-001",
      "action": "Review the related authentication records with the system owner.",
      "rationale": "The rule detected repeated failures from one source within the configured time window.",
      "requires_human_approval": true
    }
  ],
  "analysis_warnings": [
    "One input record was rejected during validation."
  ],
  "limitations": [
    "Findings are indicators requiring investigation, not proof of compromise.",
    "The analysis is rule-based and limited to the supplied records.",
    "No automatic remediation is performed."
  ],
  "ai_summary": {
    "status": "disabled",
    "content": null
  }
}
```

## Component Data Flow

```text
Authorized CSV/JSON input
  -> validation and normalization
  -> accepted normalized events and recorded rejected-record references
  -> rule-based detection components
  -> findings with evidence and event references
  -> human-reviewed response plan and manager aggregation
  -> stable JSON report
```

- The Log Analyzer uses authentication events and safe, configurable rules.
- The Network Agent uses network events and valid ports/protocols.
- The Threat Intelligence Agent compares valid destination indicators with a
  local demonstration/test list only.
- The Incident Response Agent produces safe investigation recommendations.
- The Manager Agent validates cross-object references, calculates overall risk,
  and builds the report.

## 4. Implementation Decisions (v1.0 code)

This section records decisions approved before Finding and Report code was
written. It does not change sections 1–3; it settles points those sections
left open. Anything marked NEW below is new wording, not a quote.

### D1. Finding identifiers

`finding_id` values are generated centrally by the report builder as
`finding-001`, `finding-002`, and so on, in the builder's input order
(zero-padded to three digits; longer numbers grow naturally).
A validator requires every `finding_id` to be non-empty, unique within the
report, and to match `^finding-\d{3,}$`.

The earlier examples used `finding-auth-001`; they were updated to
`finding-001` when this decision was recorded. The rule identifier
(`rule_id`, for example `AUTH-REPEATED-FAILURES`) is unchanged: it names the
rule, while `finding_id` names the finding instance.

### D2. Report identifiers

`report_id` has the form `report-YYYYMMDD-HHMMSS-NNN` in UTC, where `NNN`
is an in-memory per-process counter starting at `001` (zero-padded to
three digits; longer numbers grow naturally). Uniqueness is
guaranteed within a single run only, including several reports created in
the same second. Uniqueness across separate runs is not claimed, and no
persistent storage is added for it. A validator checks the shape
(`^report-\d{8}-\d{6}-\d{3,}$`) and that the value is non-empty.

### D3. Finding event references

`Finding.event_ids` must be a non-empty list of unique non-empty strings
(NEW sentence). Every ID must reference an accepted normalized event from
the same analysis run.

### D4. Overall risk reasons (fixed templates)

The risk calculation in section 3 is unchanged. The reason strings are:

- No findings: `"No findings were present."` (NEW).
- Only `LOW` findings: `"Only LOW-severity findings are present."` (NEW).
- No `HIGH` findings with at least one `MEDIUM` finding:
  `"At least one MEDIUM-severity finding is present and no HIGH-severity finding is present."`
  (NEW).
- At least one `HIGH` finding:
  `"At least one HIGH-severity finding is present."` (original example text).

### D5. Where event references are verified

Existence of referenced events is verified at build time, when the accepted
event IDs are available; raw events are then dropped for privacy and never
stored in the report. A validator for a finished report checks internal
consistency only (subset rules, uniqueness, reason and count rules). A
finished-report validator alone cannot prove referenced events exist,
because the report carries no accepted-event list; this is documented here
instead of assumed.

### D6. Confidence and unknown fields

A numeric `confidence` field is rejected explicitly (NEW): findings carry no
calibrated probability model. Other unknown fields are ignored, consistent
with the loader ignoring extra input fields.

### D7. Evidence value rules

- `event_count`: integer `value`, at least `1`.
- `time_window`: non-empty string, at most 100 characters.
- `port_match`: integer `value` from `1` to `65535`.
- `indicator_match`: non-empty string, at most 200 characters. It MAY be an
  IP address or hostname from the local demo/test data or matching an
  accepted event's destination; technical indicators are allowed because
  matching them is this kind's purpose.
- No `value` may carry credentials, tokens, or passwords. Type, range,
  length, and shape checks are enforced; they do not guarantee detection of
  arbitrary secrets hidden in free text.

### D8. What an event count counts

An `event_count` value counts exactly the events in that evidence item's
own `event_ids` list when present, otherwise the parent finding's full
`event_ids` list. The value must equal that list's length. A `time_window`
value is a non-empty string (at most 100 characters); its wording is not
checked semantically.

### D9. Strict string matching

`severity`, `agent`, `kind`, and other closed sets match exactly
(`"high"` is rejected; only `"HIGH"` is accepted). The contract lists
allowed values without any normalization rule, so no case folding is
applied. This documents the existing "allowed values only" reading.

### D10. Analysis warnings

Warnings are built from internal codes, known field names, and computed
counts only — never from record values. Before use, a code must match
`^[a-z0-9_]+$` with at most 50 characters, and a field name must be a known
schema field. Emission rules with fixed templates:

- When `records_rejected > 0`:
  `"N input record(s) were rejected during validation."`
- For loader warnings grouped by code (and field where known):
  `"N warning(s) of type {code}."` or
  `"N warning(s) of type {code} on field {field}."`
- An unknown code passing the safety pattern uses the generic template
  without assuming the code's meaning; a malformed code falls back to a
  count-only message.
- The list is empty for a clean run. No warning is invented for events
  that did not occur.

### D11. Default limitations (verified original texts)

The finding example uses exactly:

```text
This is an investigation indicator, not proof of compromise.
```

The report example uses exactly:

```text
Findings are indicators requiring investigation, not proof of compromise.
The analysis is rule-based and limited to the supplied records.
No automatic remediation is performed.
```

Builders seed these original texts by default (the single text for a
finding's `limitations` when the producer omits it; the three texts for a
report). Validators require non-empty limitation lists; extra custom
entries are allowed. No new limitation claim is introduced here.

### D12. Accepted source types

`input_summary.source_type` accepts `csv`, `json`, and `demo`, as already
listed. The `demo` producer arrives later; validation accepts all three
today.

### D13. Shared validation details

- `generated_at` follows the same timestamp policy as normalized events:
  an explicit timezone is required and values are stored in UTC with the
  `Z` suffix.
- Counters (`records_received`, `events_accepted`, `records_rejected`,
  `source_row_number` in rejected references) are integers at or above
  zero as specified; boolean values are never accepted as integers.
- `related_finding_id` may be `null` for general steps; a non-null value
  must reference a finding in the same report. An empty string is
  rejected.
- `ai_summary` in version `1.0` must be exactly
  `{ "status": "disabled", "content": null }`.
- `ResponsePlanItem` entries require non-empty `action` and `rationale`
  plus `requires_human_approval` set to `true`.
