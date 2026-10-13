#!/usr/bin/env python3
"""
Fix validation errors reported in reports/_validation_result.json:
  - R5  secondary/external with confidence > 0.7  -> clamp to 0.7
  - SIM800H-only (has SIM800H, no SIM800L)         -> add SIM800L
  - R12 complete record with low coverage          -> downgrade to partial
Idempotent.
"""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.", file=sys.stderr)
    sys.exit(2)


def load_yaml(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def dump_yaml(p, data):
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True,
                       sort_keys=False, default_flow_style=False)


def find_data(root, ds_id):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        return p
    return None


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    val_path = root / "reports" / "_validation_result.json"
    if not val_path.exists():
        print("ERROR: _validation_result.json missing")
        sys.exit(1)
    val = json.loads(val_path.read_text(encoding="utf-8"))

    # Collect error classes per dataset.
    r5_ds = set()
    sim800h_ds = set()
    r12_ds = set()

    for r in val.get("results", []):
        ds = r.get("dataset")
        for e in r.get("errors", []):
            if "R5:" in e:
                r5_ds.add(ds)
            if "SIM800H-only" in e:
                sim800h_ds.add(ds)
            if "R12:" in e:
                r12_ds.add(ds)

    print(f"[fix] R5 datasets        : {sorted(r5_ds)}")
    print(f"[fix] SIM800H-only       : {sorted(sim800h_ds)}")
    print(f"[fix] R12 datasets       : {sorted(r12_ds)}")

    changed_files = []

    # ---- R5: clamp confidence ----
    for ds in r5_ds:
        p = find_data(root, ds)
        if p is None:
            continue
        records = load_yaml(p)
        if not isinstance(records, list):
            continue
        changed = 0
        for rec in records:
            if not isinstance(rec, dict):
                continue
            st = rec.get("source_type")
            c = rec.get("confidence")
            if st in ("secondary", "external") and isinstance(c, (int, float)) and c > 0.7:
                rec["confidence"] = 0.7
                changed += 1
        if changed:
            dump_yaml(p, records)
            changed_files.append(f"{p.name} (R5, {changed} records)")
            print(f"[fix] {ds}: clamped confidence on {changed} records")

    # ---- SIM800H-only: add SIM800L ----
    for ds in sim800h_ds:
        p = find_data(root, ds)
        if p is None:
            continue
        records = load_yaml(p)
        if not isinstance(records, list):
            continue
        changed = 0
        for rec in records:
            if not isinstance(rec, dict):
                continue
            models = rec.get("applicable_models") or []
            if "SIM800H" in models and "SIM800L" not in models:
                models.append("SIM800L")
                rec["applicable_models"] = models
                changed += 1
        if changed:
            dump_yaml(p, records)
            changed_files.append(f"{p.name} (SIM800H, {changed} records)")
            print(f"[fix] {ds}: added SIM800L to {changed} records")

    # ---- R12: downgrade complete -> partial ----
    for ds in r12_ds:
        p = find_data(root, ds)
        if p is None:
            continue
        records = load_yaml(p)
        if not isinstance(records, list):
            continue
        changed = 0
        for rec in records:
            if not isinstance(rec, dict):
                continue
            if rec.get("status") == "complete":
                rec["status"] = "partial"
                changed += 1
        if changed:
            dump_yaml(p, records)
            changed_files.append(f"{p.name} (R12, {changed} records)")
            print(f"[fix] {ds}: downgraded {changed} records complete->partial")

    print(f"[fix] total files changed: {len(changed_files)}")
    for f in changed_files:
        print(f"      {f}")

    sys.exit(0)


if __name__ == "__main__":
    main()