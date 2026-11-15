"""CyberShield AI command-line entry point (no Streamlit, no AI service needed).

Usage:
    python main.py                              # run the built-in demo data
    python main.py --input events.csv           # analyze your own CSV/JSON file
    python main.py --input events.csv --output report.json

Pipeline: loader -> Log Analyzer / Network / Threat Intelligence
          -> Incident Response -> Manager -> validated JSON report.
Findings are investigation indicators, not proof of compromise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cybershield.agents.manager import build_manager
from cybershield.ai.summarizer import OllamaProvider, summarize
from cybershield.reporting import report_to_json
from cybershield.schemas import FindingValidationError, ReportValidationError

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "data" / "demo_full_pipeline.csv"
DEFAULT_OUTPUT = ROOT / "cybershield_report.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the CyberShield AI analysis pipeline.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV or JSON events file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="where to write the JSON report")
    parser.add_argument("--threshold", type=int, default=5, help="failed-login count that triggers a finding")
    parser.add_argument("--window", type=int, default=10, help="failed-login window in minutes")
    parser.add_argument("--ports", default=None, help="comma separated unusual ports (default: built-in list)")
    parser.add_argument(
        "--count-unknown-status",
        action="store_true",
        help="also count authentication events with unknown outcome (logs without success/failure)",
    )
    parser.add_argument("--ai-model", default=None, help="enable the optional AI summary with this local Ollama model")
    parser.add_argument("--ai-lang", choices=["en", "ar"], default="en", help="language of the AI summary")
    args = parser.parse_args(argv)

    try:
        ports = [int(p) for p in args.ports.split(",") if p.strip()] if args.ports else None
        run = build_manager(
            threshold=args.threshold,
            window_minutes=args.window,
            unusual_ports=ports,
            count_unknown_status=args.count_unknown_status,
        ).run_file(args.input)
    except (FindingValidationError, ReportValidationError) as exc:  # must precede ValueError
        print(f"Report validation failed: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:  # bad options and LoadError (a ValueError subclass)
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    report = run.report
    args.output.write_text(report_to_json(report), encoding="utf-8")

    print(f"Input: {report.input_summary.source_name} "
          f"({report.input_summary.events_accepted} accepted, "
          f"{report.input_summary.records_rejected} rejected)")
    print(f"Overall risk: {report.overall_risk} - {report.overall_risk_reason}")
    print(f"Findings per agent: {run.findings_per_agent}  (duplicates removed: {run.duplicates_removed})")
    for finding in report.findings:
        print(f"  [{finding.severity}] {finding.finding_id} {finding.agent}/{finding.rule_id}: {finding.title}")
    print(f"Response plan items: {len(report.response_plan)} (all require human approval)")
    print(f"Report saved to {args.output}")

    if args.ai_model:
        try:
            provider = OllamaProvider(args.ai_model)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        ai = summarize(report, provider, provider_name=provider.name, language=args.ai_lang)
        if ai.status == "ok":
            print(f"\n[{ai.label} - {ai.provider}]\n{ai.content}\n({ai.notice})")
        else:
            print(f"AI summary {ai.status}: {ai.reason}. The report above is unaffected.", file=sys.stderr)

    if run.agent_errors:
        for name, message in run.agent_errors.items():
            print(f"WARNING: agent '{name}' failed: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
