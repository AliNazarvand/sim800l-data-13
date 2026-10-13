#!/usr/bin/env python3
"""
Cross-reference validation with classification into 3 buckets:
  - pending_blocked : target command owned by a manual missing from sources/
  - format_mismatch : normalized form matches a target entry
  - real_missing    : not present in target and not manual-owned
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.", file=sys.stderr)
    sys.exit(2)

DATASETS = [f"dat_{i:02d}" for i in range(1, 19)]

RULES = [
    ("dat_02", "related_command",  "dat_01", "command",    "URC.related_command -> AT.command", None),
    ("dat_02", "related_state",    "dat_05", "state_name", "URC.related_state -> State.state_name", None),
    ("dat_03", "related_commands", "dat_01", "command",    "ErrorCode.related_commands -> AT.command", None),
    ("dat_04", "related_command",  "dat_01", "command",    "Timing.related_command -> AT.command", None),
    ("dat_04", "related_state",    "dat_05", "state_name", "Timing.related_state -> State.state_name", None),
    ("dat_05", "related_commands", "dat_01", "command",    "State.related_commands -> AT.command", None),
    ("dat_06", "command",          "dat_01", "command",    "Init.command -> AT.command", None),
    ("dat_06", "related_state",    "dat_05", "state_name", "Init.related_state -> State.state_name", None),
    ("dat_09", "command",          "dat_01", "command",    "SMS.command -> AT.command", None),
    ("dat_10", "command",          "dat_01", "command",    "GPRS.command -> AT.command", None),
    ("dat_11", "command",          "dat_01", "command",    "HTTP/FTP/SSL.command -> AT.command", None),
    ("dat_12", "command",          "dat_01", "command",    "Audio.command -> AT.command", None),
    ("dat_13", "command",          "dat_01", "command",    "SIM.command -> AT.command", None),
    ("dat_15", "command",          "dat_01", "command",    "Power.command -> AT.command", None),
    ("dat_17", "command",          "dat_01", "command",    "Cert.command -> AT.command",
     "SIM800 Series SSL AT Command Manual"),
    ("dat_17", "related_commands", "dat_01", "command",    "Cert.related_commands -> AT.command",
     "SIM800 Series SSL AT Command Manual"),
]

# All manuals that are NOT present in sources/originals/, with their prefixes.
MANUAL_PREFIXES = {
    "SIM800 Series FTP AT Command Manual":      ("+FTP",),
    "SIM800 Series HTTP AT Command Manual":     ("+HTTP",),
    "SIM800 Series SSL AT Command Manual":      ("+SSL",),
    "SIM800 Series Audio AT Command Manual":    ("+CADTONE", "+CATONE", "+CLDTONE", "+CPCMREG"),
    "SIM800 Series TCP/IP AT Command Manual":   ("+CEREG", "+CGCONTRDP", "+CIPDDREM"),
}


def normalize_at(s):
    if not isinstance(s, str):
        return None
    s = s.strip().upper()
    s = re.sub(r'^AT\+?', '', s)
    s = re.sub(r'^\+', '', s)
    s = re.sub(r'[?=].*$', '', s)
    s = re.sub(r'\s+', '', s)
    return s or None


def load_ds(root, ds_id):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or []
        except Exception:
            return []
    return []


def build_index(records, field):
    raw, norm = set(), set()
    for r in records:
        if isinstance(r, dict):
            v = r.get(field)
            if isinstance(v, str) and v.strip():
                raw.add(v.strip())
                n = normalize_at(v)
                if n:
                    norm.add(n)
    return {"raw": raw, "norm": norm}


def is_manual_owned(ref):
    """Check if the ref starts with any manual-owned prefix."""
    s = ref.strip().upper()
    # strip leading AT
    if s.startswith("AT+"):
        s = "+" + s[3:]
    elif s.startswith("AT"):
        pass
    for manual, prefixes in MANUAL_PREFIXES.items():
        for p in prefixes:
            if s.startswith(p.upper()):
                return manual
    return None


def classify(missing_item, tgt_index, manual_hint):
    n = normalize_at(missing_item)
    if n and n in tgt_index["norm"]:
        return "format_mismatch", None
    # explicit manual_hint from rule
    if manual_hint:
        m = is_manual_owned(missing_item)
        return "pending_blocked", (m or manual_hint)
    # auto-detect manual-owned
    m = is_manual_owned(missing_item)
    if m:
        return "pending_blocked", m
    return "real_missing", None


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    cache = {ds: load_ds(root, ds) for ds in DATASETS}
    indexes = {}
    for ds in DATASETS:
        indexes[(ds, "command")]   = build_index(cache[ds], "command")
        indexes[(ds, "state_name")] = build_index(cache[ds], "state_name")

    findings = []
    buckets = {"pending_blocked": [], "format_mismatch": [], "real_missing": []}

    for src_ds, src_field, tgt_ds, tgt_field, desc, manual_hint in RULES:
        src_records = cache.get(src_ds, [])
        if not src_records:
            findings.append({"rule": desc, "status": "skipped", "reason": f"{src_ds} empty"})
            continue
        tgt_index = indexes.get((tgt_ds, tgt_field), {"raw": set(), "norm": set()})
        if not tgt_index["raw"]:
            findings.append({"rule": desc, "status": "pending_blocked",
                             "reason": f"{tgt_ds}.{tgt_field} empty"})
            continue

        total = 0
        missing = set()
        for r in src_records:
            if not isinstance(r, dict):
                continue
            v = r.get(src_field)
            if v is None:
                continue
            vals = v if isinstance(v, list) else [v]
            for item in vals:
                if not isinstance(item, str) or not item.strip():
                    continue
                total += 1
                if item.strip() not in tgt_index["raw"]:
                    missing.add(item.strip())

        if not missing:
            findings.append({"rule": desc, "status": "ok", "total": total})
            continue

        per_class = {"pending_blocked": [], "format_mismatch": [], "real_missing": []}
        for m in sorted(missing):
            c, manual = classify(m, tgt_index, manual_hint)
            per_class[c].append(m)
            entry = {"dataset": src_ds, "ref": m,
                     "target": f"{tgt_ds}.{tgt_field}"}
            if manual:
                entry["manual_hint"] = manual
            buckets[c].append(entry)

        status = "ok"
        if per_class["real_missing"]:
            status = "unresolved"
        elif per_class["pending_blocked"] or per_class["format_mismatch"]:
            status = "pending_blocked"

        findings.append({
            "rule": desc,
            "status": status,
            "total": total,
            "pending_blocked": len(per_class["pending_blocked"]),
            "format_mismatch": len(per_class["format_mismatch"]),
            "real_missing": len(per_class["real_missing"]),
            "samples": {
                "pending_blocked": per_class["pending_blocked"][:10],
                "format_mismatch":  per_class["format_mismatch"][:10],
                "real_missing":     per_class["real_missing"][:10],
            }
        })

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "_cross_ref_result.json").write_text(
        json.dumps({
            "findings": findings,
            "buckets": buckets,
            "counts": {k: len(v) for k, v in buckets.items()},
            "indexes": {f"{k[0]}.{k[1]}": len(v["raw"]) for k, v in indexes.items()},
        }, indent=2, ensure_ascii=False),
        encoding="utf-8")

    lines = [
        "# Cross-Reference Report", "",
        f"- Rules evaluated: {len(findings)}",
        f"- pending_blocked : {len(buckets['pending_blocked'])}",
        f"- format_mismatch : {len(buckets['format_mismatch'])}",
        f"- real_missing    : {len(buckets['real_missing'])}",
        ""
    ]
    for f in findings:
        lines.append(f"- **{f['rule']}** — {f['status']}")
        if f.get("reason"):
            lines.append(f"    - {f['reason']}")
        if "pending_blocked" in f:
            lines.append(f"    - pb={f['pending_blocked']} fm={f['format_mismatch']} rm={f['real_missing']}")
            for k, samples in f["samples"].items():
                if samples:
                    lines.append(f"        [{k}] {', '.join(samples)}")
    (out_dir / "CROSS_REF_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[cross_ref] rules={len(findings)} "
          f"pending_blocked={len(buckets['pending_blocked'])} "
          f"format_mismatch={len(buckets['format_mismatch'])} "
          f"real_missing={len(buckets['real_missing'])}")
    sys.exit(3 if buckets["real_missing"] else 0)


if __name__ == "__main__":
    main()