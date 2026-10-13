#!/usr/bin/env python3
"""
Analyze real_missing refs from cross_ref: for each ref determine
whether it is a format variant, present in the AT command index but
missing in dat_01, or entirely absent. Produces:
  reports/real_missing_analysis.csv
  reports/real_missing_analysis.md
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def normalize_at(s):
    """Aggressive canonicalization: strip AT prefix, leading +, mode suffix."""
    if not isinstance(s, str):
        return None
    s = s.strip().upper()
    s = re.sub(r'^AT\+?', '', s)
    s = re.sub(r'^\+', '', s)
    s = re.sub(r'[?=].*$', '', s)
    s = re.sub(r'\s+', '', s)
    return s or None


def load_yaml(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except Exception:
        return []


def build_ds_index(root, ds_id, field):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        raw, norm = set(), set()
        for r in load_yaml(p):
            if isinstance(r, dict):
                v = r.get(field)
                if isinstance(v, str) and v.strip():
                    raw.add(v.strip())
                    n = normalize_at(v)
                    if n:
                        norm.add(n)
        return raw, norm
    return set(), set()


def load_at_index(root):
    idx = root / "sources" / "extracted" / "_at_commands_index.json"
    if not idx.exists():
        return set(), set()
    try:
        with open(idx, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return set(), set()
    raw = set()

    def pull(x):
        if isinstance(x, str):
            raw.add(x)
        elif isinstance(x, dict):
            for k in ("command", "cmd", "name"):
                if isinstance(x.get(k), str):
                    raw.add(x[k]); return

    if isinstance(data, list):
        for x in data:
            pull(x)
    elif isinstance(data, dict):
        for k in ("commands", "items", "entries"):
            if isinstance(data.get(k), list):
                for x in data[k]:
                    pull(x)
    norm = set()
    for x in raw:
        n = normalize_at(x)
        if n:
            norm.add(n)
    return raw, norm


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    cross_json = root / "reports" / "_cross_ref_result.json"
    if not cross_json.exists():
        print(f"ERROR: {cross_json} not found. Run cross_ref.py first.", file=sys.stderr)
        sys.exit(1)
    with open(cross_json, "r", encoding="utf-8") as f:
        cross = json.load(f)

    real_missing = cross.get("buckets", {}).get("real_missing", [])
    if not real_missing:
        print("[analyze] No real_missing to analyze.")
        sys.exit(0)

    print(f"[analyze] Processing {len(real_missing)} real_missing refs ...")
    dat01_raw, dat01_norm = build_ds_index(root, "dat_01", "command")
    at_idx_raw, at_idx_norm = load_at_index(root)

    rows = []
    for entry in real_missing:
        src_ds = entry.get("dataset")
        ref = entry.get("ref")
        tgt = entry.get("target", "")
        manual_hint = entry.get("manual_hint")
        n = normalize_at(ref)

        in_dat01_raw  = ref in dat01_raw
        in_dat01_norm = bool(n and n in dat01_norm)
        in_idx_raw    = ref in at_idx_raw
        in_idx_norm   = bool(n and n in at_idx_norm)

        if in_dat01_norm and not in_dat01_raw:
            cls = "format_mismatch_deep"
        elif in_idx_raw or in_idx_norm:
            cls = "in_manual_missing_in_dat01"
        elif manual_hint:
            cls = "pending_blocked_manual"
        else:
            cls = "not_in_manual"

        rows.append({
            "source_dataset": src_ds,
            "ref": ref,
            "normalized": n or "",
            "target": tgt,
            "in_dat01_raw": in_dat01_raw,
            "in_dat01_norm": in_dat01_norm,
            "in_at_index_raw": in_idx_raw,
            "in_at_index_norm": in_idx_norm,
            "manual_hint": manual_hint or "",
            "classification": cls,
        })

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "real_missing_analysis.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    cls_counts = Counter(r["classification"] for r in rows)
    per_source = defaultdict(Counter)
    for r in rows:
        per_source[r["source_dataset"]][r["classification"]] += 1

    lines = [
        "# Real-Missing Analysis", "",
        f"Total refs analyzed: **{len(rows)}**", "",
        "## Classification Summary", "",
        "| Classification | Count |",
        "|---|---|",
    ]
    for cls, c in cls_counts.most_common():
        lines.append(f"| {cls} | {c} |")
    lines.append("")
    lines.append("## Per Source Dataset")
    lines.append("")
    lines.append("| Source | format_mismatch_deep | in_manual_missing_in_dat01 | not_in_manual | pending_blocked_manual |")
    lines.append("|---|---|---|---|---|")
    for ds in sorted(per_source):
        c = per_source[ds]
        lines.append(
            f"| {ds} | {c['format_mismatch_deep']} | {c['in_manual_missing_in_dat01']} "
            f"| {c['not_in_manual']} | {c['pending_blocked_manual']} |"
        )
    lines.append("")
    lines.append("## Samples per Class")
    lines.append("")
    by_cls = defaultdict(list)
    for r in rows:
        by_cls[r["classification"]].append(r)
    for cls in sorted(by_cls):
        lines.append(f"### {cls} ({len(by_cls[cls])})")
        lines.append("")
        for r in by_cls[cls][:30]:
            lines.append(f"- `{r['ref']}` (from {r['source_dataset']} -> {r['target']})")
        if len(by_cls[cls]) > 30:
            lines.append(f"- ... and {len(by_cls[cls]) - 30} more")
        lines.append("")

    (out_dir / "real_missing_analysis.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[analyze] CSV: {csv_path.name}")
    print(f"[analyze] MD : real_missing_analysis.md")
    for cls, c in cls_counts.most_common():
        print(f"  {cls}: {c}")
    sys.exit(0)


if __name__ == "__main__":
    main()