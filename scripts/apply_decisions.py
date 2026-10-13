#!/usr/bin/env python3
"""
Apply R14 owner decisions:
  Q1 - add basic AT commands to dat_01 (source: AT Manual V1.01).
  Q3 - null the 'command' field in dat_06 for not-a-command items.
Idempotent.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.", file=sys.stderr)
    sys.exit(2)


# The 5 basic AT commands to add to dat_01 (unique).
BASIC_AT_COMMANDS = [
    ("AT",   "Attention: checks module readiness. Response: OK."),
    ("ATA",  "Answer an incoming call."),
    ("ATD",  "Dial a voice call or data number (ATD<number>;)."),
    ("ATH",  "Hang up the current call."),
    ("ATE0", "Disable command echo."),
]

DEFAULT_SOURCE = {
    "name": "SIM800 Series AT Command Manual",
    "version": "V1.01",
    "date": "2014-01-01",
    "page": "",
    "section": "General AT Commands",
    "quote": "",
}


def load_yaml(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def dump_yaml(p, data):
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True,
                       sort_keys=False, default_flow_style=False)


def find_data_file(root, ds_id):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        return p
    return None


def next_id(records, ds_id):
    max_n = 0
    pat = re.compile(rf"^{ds_id}_(\d+)$")
    for r in records:
        if isinstance(r, dict):
            m = pat.match(str(r.get("id", "")))
            if m:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
    return max_n + 1


def apply_q1_add_basic_at(root, now_iso):
    """Add basic AT commands to dat_01 if not present."""
    p = find_data_file(root, "dat_01")
    if p is None:
        return {"added": 0, "skipped": 0, "reason": "dat_01 not found"}
    records = load_yaml(p)
    if not isinstance(records, list):
        return {"added": 0, "skipped": 0, "reason": "dat_01 not a list"}

    existing = set()
    for r in records:
        if isinstance(r, dict):
            c = r.get("command")
            if isinstance(c, str):
                existing.add(c.strip().upper())
                # also without AT prefix
                existing.add(c.strip().upper().replace("AT+", "+"))

    added, skipped = 0, 0
    nid = next_id(records, "dat_01")
    for cmd, desc in BASIC_AT_COMMANDS:
        key = cmd.strip().upper()
        if key in existing:
            skipped += 1
            continue
        rec = {
            "id": f"dat_01_{nid:04d}",
            "category": "General",
            "command": cmd,
            "mode": "exec",
            "syntax": cmd,
            "parameters": [],
            "response_success": "OK",
            "response_error": "ERROR",
            "examples": [cmd, f"{cmd} -> OK"],
            "related_urcs": [],
            "related_states": [],
            "related_commands": [],
            "firmware_min": None,
            "firmware_max": None,
            "source": dict(DEFAULT_SOURCE),
            "source_type": "primary",
            "confidence": 0.6,
            "status": "partial",
            "conflicts": [],
            "notes": f"Basic AT command added from AT Manual V1.01. {desc}",
            "tags": ["at", "general", "basic"],
            "applicable_models": ["SIM800L"],
            "created_at": now_iso,
            "updated_at": now_iso,
        }
        records.append(rec)
        nid += 1
        added += 1

    if added > 0:
        dump_yaml(p, records)
    return {"added": added, "skipped": skipped, "file": p.name}


def apply_q3_null_dat06_commands(root, classification, now_iso):
    """Null the 'command' field in dat_06 for not-a-command items."""
    p = find_data_file(root, "dat_06")
    if p is None:
        return {"nulled": 0, "reason": "dat_06 not found"}
    records = load_yaml(p)
    if not isinstance(records, list):
        return {"nulled": 0, "reason": "dat_06 not a list"}

    bad_values = set()
    for it in classification.get("not_a_command", []):
        if it.get("dataset") == "dat_06":
            bad_values.add(it.get("ref"))

    if not bad_values:
        return {"nulled": 0, "reason": "no dat_06 not-a-command items"}

    nulled = 0
    for r in records:
        if not isinstance(r, dict):
            continue
        c = r.get("command")
        if isinstance(c, str) and c in bad_values:
            r["notes"] = (r.get("notes") or "") + f" | Original command-field value: {c}"
            r["command"] = None
            r["updated_at"] = now_iso
            nulled += 1

    if nulled > 0:
        dump_yaml(p, records)
    return {"nulled": nulled, "file": p.name}


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Load classification
    cls_path = root / "reports" / "real_missing_classification.json"
    classification = {}
    if cls_path.exists():
        try:
            with open(cls_path, "r", encoding="utf-8") as f:
                classification = json.load(f)
        except Exception as e:
            print(f"WARN: classification load failed: {e}")

    q1 = apply_q1_add_basic_at(root, now_iso)
    print(f"[apply] Q1 dat_01: added={q1.get('added')} skipped={q1.get('skipped')}")

    q3 = apply_q3_null_dat06_commands(root, classification, now_iso)
    print(f"[apply] Q3 dat_06: nulled={q3.get('nulled')}")

    summary = {"timestamp": now_iso, "q1": q1, "q3": q3}
    (root / "reports" / "_apply_decisions.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    sys.exit(0)


if __name__ == "__main__":
    main()