#!/usr/bin/env python3
"""
Final data normalization: preserve IDs, mark blocked datasets honestly,
normalize base fields. Idempotent and safe.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


DATASETS = [f"dat_{i:02d}" for i in range(1, 19)]

# Datasets marked blocked (no official source available in project).
BLOCKED = {"dat_08", "dat_16", "dat_18"}

DEFAULT_CATEGORY = {
    "dat_01": "AT Command", "dat_02": "URC", "dat_03": "Error Code",
    "dat_04": "Timing",     "dat_05": "State", "dat_06": "Init Sequence",
    "dat_07": "Hardware",   "dat_08": "Firmware", "dat_09": "SMS",
    "dat_10": "GPRS",       "dat_11": "HTTP/FTP/SSL", "dat_12": "Audio",
    "dat_13": "SIM",        "dat_14": "Operator/APN", "dat_15": "Power",
    "dat_16": "Board/EVB",  "dat_17": "Certificate", "dat_18": "Certification",
}

DEFAULT_SOURCE = {
    "dat_01": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_02": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_03": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_04": ("SIM800H&SIM800L Hardware Design", "V2.02", "2015-07-27"),
    "dat_05": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_06": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_07": ("SIM800H&SIM800L Hardware Design", "V2.02", "2015-07-27"),
    "dat_08": ("(source unavailable)", "N/A", "1970-01-01"),
    "dat_09": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_10": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_11": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_12": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_13": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_14": ("mcc-mnc.com", "external", "2024-01-01"),
    "dat_15": ("SIM800H&SIM800L Hardware Design", "V2.02", "2015-07-27"),
    "dat_16": ("(source unavailable)", "N/A", "1970-01-01"),
    "dat_17": ("SIM800 Series SSL AT Command Manual", "V1.01", "2016-03-10"),
    "dat_18": ("(source unavailable)", "N/A", "1970-01-01"),
}


def stable_id_from_content(rec):
    """Deterministic 4-digit suffix based on record content."""
    h = hashlib.sha1(repr(sorted(rec.items(), key=lambda x: str(x))).encode()).hexdigest()
    return int(h[:8], 16) % 10000


def find_data_file(root, ds_id):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        return p
    return None


def normalize_record(ds_id, idx, rec, now_iso, existing_ids):
    if not isinstance(rec, dict):
        return None
    # id: preserve if present and unique; else deterministic
    rid = rec.get("id")
    if not rid or rid in existing_ids:
        suffix = stable_id_from_content({k: v for k, v in rec.items() if k != "id"})
        candidate = f"{ds_id}_{suffix:04d}"
        counter = 0
        while candidate in existing_ids:
            counter += 1
            candidate = f"{ds_id}_{(suffix + counter) % 10000:04d}"
        rid = candidate
    existing_ids.add(rid)
    rec["id"] = rid

    # category
    if not rec.get("category"):
        rec["category"] = DEFAULT_CATEGORY.get(ds_id, ds_id)

    # source
    src_name, src_ver, src_date = DEFAULT_SOURCE.get(ds_id, ("unknown", "unknown", "1970-01-01"))
    if not isinstance(rec.get("source"), dict) or not rec["source"].get("name"):
        rec["source"] = {"name": src_name, "version": src_ver, "date": src_date}
    else:
        s = rec["source"]
        if not s.get("name"):    s["name"] = src_name
        if not s.get("version"): s["version"] = src_ver
        if not s.get("date"):    s["date"] = src_date

    # source_type
    if rec.get("source_type") not in ("primary", "secondary", "external"):
        if ds_id == "dat_14":
            rec["source_type"] = "external"
        elif ds_id in BLOCKED:
            rec["source_type"] = "secondary"
        else:
            rec["source_type"] = "primary"

    # confidence
    if ds_id in BLOCKED:
        rec["confidence"] = 0.0
    else:
        c = rec.get("confidence")
        if not isinstance(c, (int, float)) or not (0.0 <= c <= 1.0):
            rec["confidence"] = 0.9 if rec["source_type"] == "primary" else 0.7
        # clamp by source_type per R5
        if rec["source_type"] == "secondary":
            rec["confidence"] = min(rec["confidence"], 0.7)
        elif rec["source_type"] == "external":
            rec["confidence"] = min(rec["confidence"], 0.7)

    # status
    if ds_id in BLOCKED:
        rec["status"] = "blocked"
    else:
        if rec.get("status") not in ("complete", "partial", "unknown", "inferred", "blocked", "deferred"):
            rec["status"] = "partial"

    # applicable_models
    m = rec.get("applicable_models")
    if not isinstance(m, list) or "SIM800L" not in m:
        rec["applicable_models"] = ["SIM800L"]

    # timestamps
    if not isinstance(rec.get("created_at"), str) or not rec["created_at"]:
        rec["created_at"] = now_iso
    if not isinstance(rec.get("updated_at"), str) or not rec["updated_at"]:
        rec["updated_at"] = now_iso

    return rec


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = {"timestamp": now_iso, "datasets": []}

    for ds_id in DATASETS:
        p = find_data_file(root, ds_id)
        if p is None:
            report["datasets"].append({"dataset": ds_id, "file": None, "records": 0})
            print(f"  {ds_id}: no file")
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                records = yaml.safe_load(f) or []
        except Exception as e:
            print(f"  {ds_id}: load failed: {e}")
            report["datasets"].append({"dataset": ds_id, "file": p.name, "records": 0,
                                       "error": str(e)})
            continue
        if not isinstance(records, list):
            records = []

        existing_ids = set()
        normalized = []
        for idx, r in enumerate(records):
            nr = normalize_record(ds_id, idx, r, now_iso, existing_ids)
            if nr is not None:
                normalized.append(nr)

        with open(p, "w", encoding="utf-8") as f:
            yaml.safe_dump(normalized, f, allow_unicode=True,
                           sort_keys=False, default_flow_style=False)

        report["datasets"].append({"dataset": ds_id, "file": p.name,
                                   "records": len(normalized),
                                   "blocked": ds_id in BLOCKED})
        print(f"  {ds_id}: {len(normalized)} records -> {p.name}")

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "_normalize_result.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[normalize] done. See reports/_normalize_result.json")
    sys.exit(0)


if __name__ == "__main__":
    main()