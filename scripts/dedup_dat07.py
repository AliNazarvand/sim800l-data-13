#!/usr/bin/env python3
"""Dedup dat_07 by (name, pin_number); merge missing fields from duplicates."""
import json
import sys
from collections import OrderedDict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.", file=sys.stderr)
    sys.exit(2)


def merge(base, other):
    """Fill empty fields of base from other; keep base non-empty."""
    for k, v in other.items():
        if k in ("id", "created_at", "updated_at"):
            continue
        if k not in base or base[k] in (None, "", [], {}):
            base[k] = v
    return base


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    p = None
    for f in sorted((root / "data").glob("dat_07_*.yaml")):
        p = f
        break
    if p is None:
        print("ERROR: dat_07 file not found")
        sys.exit(1)

    with open(p, "r", encoding="utf-8") as f:
        records = yaml.safe_load(f) or []
    if not isinstance(records, list):
        print("ERROR: dat_07 top-level not a list")
        sys.exit(1)

    kept = OrderedDict()
    removed_ids = []
    for r in records:
        if not isinstance(r, dict):
            continue
        key = (str(r.get("name") or ""), str(r.get("pin_number") or ""))
        if key in kept:
            kept[key] = merge(kept[key], r)
            removed_ids.append(r.get("id"))
        else:
            kept[key] = r

    new_records = list(kept.values())
    archive_dir = root / "reports" / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    # Archive removed ids only
    (archive_dir / "_dat07_removed_ids.json").write_text(
        json.dumps({"removed_ids": removed_ids,
                    "kept": len(new_records),
                    "original": len(records)}, indent=2),
        encoding="utf-8")

    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(new_records, f, allow_unicode=True,
                       sort_keys=False, default_flow_style=False)

    print(f"[dedup_dat07] original={len(records)} kept={len(new_records)} removed={len(removed_ids)}")
    sys.exit(0)


if __name__ == "__main__":
    main()