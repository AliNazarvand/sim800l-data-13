#!/usr/bin/env python3
"""Repair SIM800L data files: remove placeholder records (missing id),
ensure applicable_models contains SIM800L, save removed records for audit."""
import sys
import json
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    archive_dir = root / "reports" / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    total_removed = 0
    total_fixed = 0
    total_kept = 0
    report = {}

    for p in sorted((root / "data").glob("dat_*.yaml")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                records = yaml.safe_load(f) or []
        except Exception as e:
            print(f"  SKIP {p.name}: {e}")
            continue
        if not isinstance(records, list):
            continue

        new_records = []
        removed_records = []
        fixed = 0
        for r in records:
            if not isinstance(r, dict):
                removed_records.append(r)
                continue
            if not r.get("id"):
                removed_records.append(r)
                continue
            models = r.get("applicable_models")
            if not isinstance(models, list) or "SIM800L" not in models:
                r["applicable_models"] = ["SIM800L"]
                fixed += 1
            new_records.append(r)

        if removed_records or fixed:
            with open(p, "w", encoding="utf-8") as f:
                yaml.safe_dump(new_records, f, allow_unicode=True,
                               sort_keys=False, default_flow_style=False)
            if removed_records:
                archive_path = archive_dir / f"{p.stem}_removed_{stamp}.yaml"
                with open(archive_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(removed_records, f, allow_unicode=True,
                                   sort_keys=False, default_flow_style=False)
            print(f"  {p.name}: removed={len(removed_records)} fixed={fixed} kept={len(new_records)}")
            report[p.name] = {"removed": len(removed_records), "fixed": fixed,
                              "kept": len(new_records)}

        total_removed += len(removed_records)
        total_fixed += fixed
        total_kept += len(new_records)

    summary_path = archive_dir / f"_repair_summary_{stamp}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": stamp, "total_removed": total_removed,
                   "total_fixed": total_fixed, "total_kept": total_kept,
                   "per_file": report}, f, indent=2, ensure_ascii=False)

    print(f"[repair] removed={total_removed} fixed={total_fixed} kept={total_kept}")
    sys.exit(0)


if __name__ == "__main__":
    main()