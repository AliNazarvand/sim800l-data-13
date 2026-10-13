#!/usr/bin/env python3
"""Audit dat_07 for duplicates and quality issues."""
import json
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.", file=sys.stderr)
    sys.exit(2)


def load_yaml(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    ds_id = "dat_07"
    p = None
    for f in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        p = f
        break
    if p is None:
        print(f"ERROR: no data file for {ds_id}")
        sys.exit(1)

    records = load_yaml(p)
    if not isinstance(records, list):
        print("ERROR: top-level not a list")
        sys.exit(1)

    k1, k2, k3 = Counter(), Counter(), Counter()
    empty_name = empty_pin = 0
    for r in records:
        if not isinstance(r, dict):
            continue
        n = r.get("name")
        pin = r.get("pin_number")
        rid = r.get("id")
        k1[(str(n), str(pin))] += 1
        if pin: k2[str(pin)] += 1
        if rid: k3[rid] += 1
        if not n: empty_name += 1
        if not pin: empty_pin += 1

    out = {
        "dataset": ds_id,
        "file": p.name,
        "total": len(records),
        "empty_name": empty_name,
        "empty_pin_number": empty_pin,
        "duplicate_name_pin_pairs": sum(1 for v in k1.values() if v > 1),
        "duplicate_pin_number_only": sum(1 for v in k2.values() if v > 1),
        "duplicate_id": sum(1 for v in k3.values() if v > 1),
    }

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "_dat07_audit.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"[audit_dat07] total={len(records)} dup_name_pin={out['duplicate_name_pin_pairs']} "
          f"dup_pin={out['duplicate_pin_number_only']} dup_id={out['duplicate_id']} "
          f"empty_name={empty_name} empty_pin={empty_pin}")
    sys.exit(0)


if __name__ == "__main__":
    main()