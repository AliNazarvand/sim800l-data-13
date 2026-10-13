#!/usr/bin/env python3
"""
Classify real_missing refs into 4 categories. Uses _at_commands_index.json
when available (list, nested-dict, or flat-dict {cmd: id}).
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

MANUAL_PREFIXES = {
    "SIM800 Series FTP AT Command Manual":   ["+FTP"],
    "SIM800 Series HTTP AT Command Manual":  ["+HTTP"],
    "SIM800 Series SSL AT Command Manual":   ["+SSL"],
    "SIM800 Series Audio AT Command Manual": ["+CADTONE", "+CATONE", "+CLDTONE", "+CPCMREG"],
    "SIM800 Series TCP/IP AT Command Manual": ["+CEREG", "+CGCONTRDP", "+CIPDDREM"],
}

AT_COMMAND_RE = re.compile(r'^(AT[A-Z0-9]*|AT\+[A-Z][A-Z0-9]*|\+[A-Z][A-Z0-9]*)$')

BASIC_AT_WHITELIST = {
    "AT", "ATA", "ATD", "ATH", "ATE0", "ATE1", "ATZ",
}


def normalize_for_manual(ref):
    s = ref.strip().upper()
    if s.startswith("AT+"):
        return "+" + s[3:]
    return s


def is_manual_owned(ref):
    upper = normalize_for_manual(ref)
    for manual, prefixes in MANUAL_PREFIXES.items():
        for p in prefixes:
            if upper.startswith(p.upper()):
                return manual
    return None


def is_not_a_command(ref):
    s = ref.strip()
    if re.search(r'\s', s): return True
    if "(" in s or ")" in s: return True
    if "_" in s: return True
    low = s.lower()
    if any(w in low for w in ("pull", "wait", "pwrkey", "signal")): return True
    return False


def looks_like_at(ref):
    return bool(AT_COMMAND_RE.match(ref.strip().upper()))


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

    def pull_scalar(x):
        if isinstance(x, str):
            raw.add(x)
        elif isinstance(x, dict):
            for k in ("command", "cmd", "name", "at_command"):
                if isinstance(x.get(k), str):
                    raw.add(x[k]); return

    if isinstance(data, list):
        for x in data: pull_scalar(x)
    elif isinstance(data, dict):
        found_nested = False
        for k in ("commands", "items", "entries"):
            if isinstance(data.get(k), list):
                for x in data[k]: pull_scalar(x)
                found_nested = True
        if not found_nested:
            for k in data.keys():
                if isinstance(k, str):
                    raw.add(k)

    norm = set()
    for x in raw:
        s = x.strip().upper()
        if not s: continue
        norm.add(s)
        if s.startswith("AT+"): norm.add("+" + s[3:])
        if s.startswith("+"):   norm.add("AT" + s)
        norm.add(re.sub(r'[?=].*$', '', s))
    return raw, norm


def in_index(ref, idx_raw, idx_norm):
    s = ref.strip().upper()
    variants = {s, re.sub(r'[?=].*$', '', s)}
    if s.startswith("AT+"): variants.add("+" + s[3:])
    if s.startswith("+"):   variants.add("AT" + s)
    for v in variants:
        if v in idx_raw or v in idx_norm:
            return True
    return False


def classify(ref, idx_raw, idx_norm):
    if is_not_a_command(ref):
        return "not_a_command", None
    manual = is_manual_owned(ref)
    if manual:
        return "manual_owned_pending", manual
    if looks_like_at(ref):
        upper = ref.strip().upper()
        if upper in BASIC_AT_WHITELIST:
            return "basic_at_missing", None
        if in_index(ref, idx_raw, idx_norm):
            return "basic_at_missing", None
        return "unknown", None
    return "unknown", None


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    cross_json = root / "reports" / "_cross_ref_result.json"
    if not cross_json.exists():
        print(f"ERROR: {cross_json} not found.", file=sys.stderr)
        sys.exit(1)
    with open(cross_json, "r", encoding="utf-8") as f:
        cross = json.load(f)
    real_missing = cross.get("buckets", {}).get("real_missing", [])
    idx_raw, idx_norm = load_at_index(root)
    print(f"[classify] AT index size: {len(idx_raw)} raw / {len(idx_norm)} norm")

    categories = defaultdict(list)
    for entry in real_missing:
        ref = entry.get("ref", "")
        cls, manual = classify(ref, idx_raw, idx_norm)
        categories[cls].append({
            "dataset": entry.get("dataset"),
            "ref": ref,
            "target": entry.get("target"),
            "manual": manual,
        })

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "real_missing_classification.json").write_text(
        json.dumps({k: v for k, v in categories.items()}, indent=2, ensure_ascii=False),
        encoding="utf-8")

    lines = ["# Real-Missing Classification", "",
             f"Total refs: **{len(real_missing)}**", "",
             f"AT index size: {len(idx_raw)}", ""]
    for cls in ("basic_at_missing", "manual_owned_pending", "not_a_command", "unknown"):
        items = categories.get(cls, [])
        lines.append(f"## {cls} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("_none_")
            lines.append("")
            continue
        for it in items:
            extra = f"   [manual: {it['manual']}]" if it.get("manual") else ""
            lines.append(f"- `{it['ref']}`  (from **{it['dataset']}** -> {it['target']}){extra}")
        lines.append("")
    (out_dir / "real_missing_classification.md").write_text("\n".join(lines), encoding="utf-8")

    counts = {k: len(v) for k, v in categories.items()}
    print(f"[classify] total={len(real_missing)}")
    for k in ("basic_at_missing", "manual_owned_pending", "not_a_command", "unknown"):
        print(f"  {k}: {counts.get(k, 0)}")
    sys.exit(0)


if __name__ == "__main__":
    main()