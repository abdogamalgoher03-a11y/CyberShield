"""Demo: run the Incident Response Agent on sample findings (no auto-actions)."""

import json
from pathlib import Path

from cybershield.agents.incident_response import IncidentResponseAgent

ROOT = Path(__file__).resolve().parent
findings = json.loads((ROOT / "data" / "demo_findings.json").read_text(encoding="utf-8"))

plan = IncidentResponseAgent().plan(findings, include_details=True)

for item in plan:
    print(f"\n[{item['severity']}] {item['related_finding_id']}  ({item['agent']} / {item['rule_id']})")
    for i, step in enumerate(item["steps"], start=1):
        print(f"  {i}. {step}")
    print("  Requires human approval:", item["requires_human_approval"])

out = ROOT / "cybershield_response_plan.json"
out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nSaved response plan to {out.name}")
