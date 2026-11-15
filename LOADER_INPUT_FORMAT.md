# CyberShield AI Loader Input Format

## Purpose

`cybershield.data_loader.load_events()` reads authorized UTF-8 CSV or JSON
files and delegates per-record validation to `normalize_event()`.

The loader does not execute file content, make network requests, or perform
automatic remediation.

## Supported Files

- File extensions: `.csv` and `.json`, case-insensitive.
- Text encoding: UTF-8, with an optional BOM tolerated (common in
  Excel-saved CSV files). Plain UTF-8 files without a BOM are read
  identically; validation stays strict.
- A zero-byte or whitespace-only file is rejected as `empty_file`.
- A CSV containing only valid headers and no data rows, and a JSON array `[]`,
  are valid imports with zero received records.

## Field Names

Both formats use the Normalized Event field names directly. Required input
fields are `timestamp` and `event_type`. All other fields are optional:

```text
timestamp, event_type, status, source_ip, destination_ip, destination_host,
username, destination_port, protocol, source_record_id
```

Extra input fields are ignored. The loader assigns `schema_version`,
`source_id`, `source_name`, `source_row_number`, and `event_id`; input files
must not supply them.

## CSV Format

- The first row is a header row.
- Headers must include `timestamp` and `event_type` exactly and must not be
  duplicated.
- Data records are counted from `1` after the header row. That number becomes
  `source_row_number`.
- A row containing more values than the header has is rejected safely. It does
  not stop other rows from being processed.

Example:

```csv
timestamp,event_type,status,source_ip,username
2026-01-01T10:00:00Z,authentication,failure,192.0.2.10,demo-user
```

## JSON Format

- The top-level JSON value must be an array.
- Each array element is treated as one source record; its one-based array index
  becomes `source_row_number`.
- An element that is not an object is rejected safely while other elements can
  still be processed.

Example:

```json
[
  {
    "timestamp": "2026-01-01T10:00:00Z",
    "event_type": "authentication",
    "status": "failure",
    "source_ip": "192.0.2.10",
    "username": "demo-user"
  }
]
```

## Import Results and Privacy

Each call creates a new `source_id`, including repeated imports of the same
file. Every accepted event ID is built by the approved schema rule from that
source ID and its original row number.

The result keeps these counts consistent:

```text
records_received = events_accepted + records_rejected
len(rejected_records) = records_rejected
```

Rejected-record references include only `source_row_number` and safe validation
issues. They never include raw rows, usernames, IPs, tokens, or other sensitive
values.
