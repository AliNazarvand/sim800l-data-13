#!/usr/bin/env python3
"""Compute and report coverage for datasets with known source inventories.

Coverage is capped at 100%. A record_count above the AT index baseline is
treated as coverage=100% (the extra records are the ones added by Q1).
"""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.", file=sys.stderr)
    sys.exit(2)

COVERAGE_SOURCES = {
    "dat_01": "SIM800 Series AT Command Manual V1.01",
    "dat_02": "SIM800 Series AT Command Manual V1.01",
    "dat_03": "SIM800 Series AT Command Manual V1.01",
    "dat_04": "SIM800H&SIM800L Hardware Design V2.02",
    "dat_05": "SIM800 Series AT Command Manual V1.01",
    "dat_06": "SIM800 Series AT Command Manual V1.01",
    "dat_07": "SIM800H&SIM800L Hardware Design V2.02",
    "dat_08": "(source unavailable)",
    "dat_09": "SIM800 Series AT Command Manual V1.01",
    "dat_10": "SIM800 Series AT Command Manual V1.01",
    "dat_11": "SIM800 Series AT Command Manual V1.01",
    "dat_12": "SIM800 Series AT Command Manual V1.01",
    "dat_13": "SIM800 Series AT Command Manual V1.01",
    "dat_14": "mcc-mnc.com (external)",
    "dat_15": "SIM800H&SIM800L Hardware Design V2.02",
    "dat_16": "(source unavailable)",
    "dat_17": "SIM800 Series SSL AT Command Manual V1.01",
    "dat_18": "(source unavailable)",
}

BLOCK_REASONS = {
    "dat_08": "Firmware Release Notes not available in sources/",
    "dat_16": "Official EVB documentation not available in sources/",
    "dat_18": "Certification documents not available in sources/",
}


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def find_data(root, ds_id):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        return p
    return None


def count_commands_in_manual(root):
    idx = root / "sources" / "extracted" / "_at_commands_index.json"
    if not idx.exists():
        return None
    try:
        with open(idx, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            # flat dict {cmd: id}
            keys = [k for k in data.keys() if isinstance(k, str)]
            if keys and not any(k in ("commands", "items", "entries") for k in keys):
                return len(keys)
            for k in ("commands", "items", "entries"):
                if k in data and isinstance(data[k], list):
                    return len(data[k])
            return len(data)
    except Exception:
        return None
    return None


def record_status_counts(records):
    """Return (complete, partial, blocked, other) counts."""
    complete = partial = blocked = other = 0
    for r in records:
        if not isinstance(r, dict):
            continue
        st = r.get("status")
        if st == "complete":
            complete += 1
        elif st == "partial":
            partial += 1
        elif st == "blocked":
            blocked += 1
        else:
            other += 1
    return complete, partial, blocked, other


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    manual_at_count = count_commands_in_manual(root)
    DATASETS = [f"dat_{i:02d}" for i in range(1, 19)]

    rows = []
    for ds_id in DATASETS:
        p = find_data(root, ds_id)
        if p is None:
            rows.append({"dataset": ds_id, "records": 0, "status": "blocked",
                         "coverage": None, "coverage_estimate": "low",
                         "source": "—", "reason": "No data file",
                         "complete": 0, "partial": 0, "blocked": 0})
            continue
        try:
            records = load_yaml(p)
            if not isinstance(records, list):
                records = []
        except Exception:
            records = []

        n = len(records)
        cmp_cnt, prt_cnt, blk_cnt, _ = record_status_counts(records)

        status = "partial"
        coverage = None
        estimate = "medium"
        source = COVERAGE_SOURCES.get(ds_id, "—")
        reason = ""

        if ds_id in BLOCK_REASONS:
            status = "blocked"
            estimate = "low"
            source = "(source unavailable)"
            reason = BLOCK_REASONS[ds_id]
        elif n == 0:
            status = "blocked"
            estimate = "low"
            reason = "No records"
        elif ds_id == "dat_01" and manual_at_count:
            cov_raw = 100.0 * n / manual_at_count
            coverage = round(min(cov_raw, 100.0), 1)
            if coverage >= 95:
                status = "complete"
                estimate = "high"
            elif coverage >= 70:
                estimate = "medium"
            else:
                estimate = "low"
        elif n >= 100:
            status = "partial"
            estimate = "high"
        elif n >= 20:
            status = "partial"
            estimate = "medium"
        else:
            status = "partial"
            estimate = "low"

        rows.append({
            "dataset": ds_id,
            "records": n,
            "status": status,
            "coverage": coverage,
            "coverage_estimate": estimate,
            "source": source,
            "reason": reason,
            "complete": cmp_cnt,
            "partial": prt_cnt,
            "blocked": blk_cnt,
        })

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "_coverage_result.json").write_text(
        json.dumps({"rows": rows, "manual_at_count": manual_at_count},
                   indent=2, ensure_ascii=False),
        encoding="utf-8")

    # Markdown
    lines = [
        "# Coverage Matrix", "",
        "| Dataset | Records | Complete | Partial | Blocked | Status | Coverage | Estimate | Source | Reason |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        cov = f"{r['coverage']}%" if r['coverage'] is not None else "—"
        lines.append(
            f"| {r['dataset']} | {r['records']} | {r['complete']} | {r['partial']} | "
            f"{r['blocked']} | {r['status']} | {cov} | "
            f"{r['coverage_estimate']} | {r['source']} | {r['reason'] or '—'} |"
        )
    lines.append("")
    if manual_at_count:
        lines.append(f"_AT command index total: {manual_at_count}_")
    (out_dir / "COVERAGE_MATRIX.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[coverage] datasets={len(rows)} manual_at_count={manual_at_count}")
    sys.exit(0)


if __name__ == "__main__":
    main()