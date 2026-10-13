#!/usr/bin/env python3
"""Rebuild real_missing_classification.json from the current cross_ref result:
   - pending_blocked  -> manual_owned_pending
   - format_mismatch  -> format_mismatch_bucket
   - real_missing     -> real_missing (should be 0)
   - basic_at_missing / not_a_command / unknown stay empty unless present.
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
cross_path = root / "reports" / "_cross_ref_result.json"
if not cross_path.exists():
    print("ERROR: _cross_ref_result.json missing")
    sys.exit(1)
cross = json.loads(cross_path.read_text(encoding="utf-8"))
buckets = cross.get("buckets", {})

manual_items = []
for entry in buckets.get("pending_blocked", []):
    manual_items.append({
        "dataset": entry.get("dataset"),
        "ref": entry.get("ref"),
        "target": entry.get("target"),
        "manual": entry.get("manual_hint"),
    })

fmt_items = []
for entry in buckets.get("format_mismatch", []):
    fmt_items.append({
        "dataset": entry.get("dataset"),
        "ref": entry.get("ref"),
        "target": entry.get("target"),
    })

real_items = []
for entry in buckets.get("real_missing", []):
    real_items.append({
        "dataset": entry.get("dataset"),
        "ref": entry.get("ref"),
        "target": entry.get("target"),
    })

payload = {
    "basic_at_missing": [],
    "manual_owned_pending": manual_items,
    "not_a_command": [],
    "unknown": [],
    "format_mismatch_bucket": fmt_items,
    "real_missing": real_items,
}
out = root / "reports" / "real_missing_classification.json"
out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

md = ["# Real-Missing Classification (rebuilt)", ""]
md.append(f"- manual_owned_pending : {len(manual_items)}")
md.append(f"- format_mismatch_bucket: {len(fmt_items)}")
md.append(f"- real_missing          : {len(real_items)}")
md.append("")
md.append("## manual_owned_pending")
for it in manual_items:
    md.append(f"- `{it['ref']}` (from {it['dataset']}) [{it.get('manual') or 'n/a'}]")
md.append("")
md.append("## format_mismatch_bucket")
for it in fmt_items[:50]:
    md.append(f"- `{it['ref']}` (from {it['dataset']})")
if len(fmt_items) > 50:
    md.append(f"- ... and {len(fmt_items)-50} more")
(root / "reports" / "real_missing_classification.md").write_text("\n".join(md), encoding="utf-8")
print(f"[rebuild] manual={len(manual_items)} fmt={len(fmt_items)} real={len(real_items)}")
sys.exit(0)