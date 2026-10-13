#!/usr/bin/env python3
"""R20: detect cross-dataset inconsistencies for shared keys."""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# For each dataset pair, the fields that should agree when the same key appears.
# key_field -> list of (ds_a, field_a, ds_b, field_b, description)
CHECKS = [
    # (key_a_ds, key_field_a, value_field_a, key_b_ds, key_field_b, value_field_b, desc)
    ("dat_01", "command", "syntax",        "dat_09", "command", "syntax",   "SMS syntax vs AT syntax"),
    ("dat_01", "command", "syntax",        "dat_10", "command", "syntax",   "GPRS syntax vs AT syntax"),
    ("dat_01", "command", "syntax",        "dat_11", "command", "syntax",   "HTTP/FTP/SSL syntax vs AT syntax"),
    ("dat_01", "command", "syntax",        "dat_12", "command", "syntax",   "Audio syntax vs AT syntax"),
    ("dat_01", "command", "syntax",        "dat_13", "command", "syntax",   "SIM syntax vs AT syntax"),
    ("dat_01", "command", "syntax",        "dat_17", "command", "syntax",   "Cert syntax vs AT syntax"),
]


def load_ds(root, ds_id):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or []
        except Exception:
            return []
    return []


def index_by(records, key_field, value_field):
    out = {}
    for r in records:
        if not isinstance(r, dict):
            continue
        k = r.get(key_field)
        v = r.get(value_field)
        if isinstance(k, str) and k.strip() and v is not None:
            out.setdefault(k.strip(), set()).add(str(v))
    return out


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    cache = {}
    for ds in {c[0] for c in CHECKS} | {c[3] for c in CHECKS}:
        cache[ds] = load_ds(root, ds)

    findings = []
    conflicts = []
    for a_ds, a_key, a_val, b_ds, b_key, b_val, desc in CHECKS:
        a_idx = index_by(cache.get(a_ds, []), a_key, a_val)
        b_idx = index_by(cache.get(b_ds, []), b_key, b_val)
        common = set(a_idx) & set(b_idx)
        mismatched = []
        for k in common:
            if a_idx[k] != b_idx[k]:
                mismatched.append({"key": k,
                                   f"{a_ds}.{a_val}": sorted(a_idx[k]),
                                   f"{b_ds}.{b_val}": sorted(b_idx[k])})
        if mismatched:
            findings.append({"check": desc, "status": "conflict",
                             "common": len(common), "mismatched": len(mismatched),
                             "samples": mismatched[:10]})
            for m in mismatched:
                conflicts.append({"check": desc, **m})
        else:
            findings.append({"check": desc, "status": "ok", "common": len(common)})

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "_consistency_result.json").write_text(
        json.dumps({"findings": findings, "conflicts": conflicts},
                   indent=2, ensure_ascii=False),
        encoding="utf-8")

    lines = ["# Consistency Report (R20)", "",
             f"- Checks: {len(findings)}",
             f"- Conflicts: {len(conflicts)}", ""]
    for f in findings:
        lines.append(f"- **{f['check']}** — {f['status']} (common={f['common']})")
        if f.get("samples"):
            for s in f["samples"]:
                lines.append(f"    - key={s['key']} differences: {s}")
    (out_dir / "CONSISTENCY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[consistency] checks={len(findings)} conflicts={len(conflicts)}")
    sys.exit(0)


if __name__ == "__main__":
    main()