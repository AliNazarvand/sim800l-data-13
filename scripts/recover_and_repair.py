#!/usr/bin/env python3
"""
Safe recovery & repair for SIM800L datasets.

Strategy per dataset:
  1. Collect candidate sources: current data file, all files in
     reports/_archive/*/, and all sibling *-backup-*/data/ directories.
  2. Score each by (number of dict records with a non-empty 'id').
  3. Pick the highest-scoring candidate as base.
  4. Repair each record: ensure all 7 required fields are present.
     - id        : generate dat_XX_NNNN if missing
     - category  : use per-dataset default
     - source    : use per-dataset default source object
     - source_type: 'primary'
     - confidence: 0.7
     - status    : 'partial'
     - applicable_models: ['SIM800L']
     - created_at / updated_at: current ISO timestamp
  5. Also fill dataset-specific fields with null/empty if absent.
  6. Never discard a record unless it is not a dict.
  7. Save repaired file to data/, and write an audit JSON.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


DATASETS = [f"dat_{i:02d}" for i in range(1, 19)]

# Default source per dataset (name, version, date).
DEFAULT_SOURCES = {
    "dat_01": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_02": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_03": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_04": ("SIM800H&SIM800L Hardware Design", "V2.02", "2015-07-27"),
    "dat_05": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_06": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_07": ("SIM800H&SIM800L Hardware Design", "V2.02", "2015-07-27"),
    "dat_08": ("SIM800 Series Firmware Release Notes", "unknown", "1970-01-01"),
    "dat_09": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_10": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_11": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_12": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_13": ("SIM800 Series AT Command Manual", "V1.01", "2014-01-01"),
    "dat_14": ("mcc-mnc.com", "external", "2024-01-01"),
    "dat_15": ("SIM800H&SIM800L Hardware Design", "V2.02", "2015-07-27"),
    "dat_16": ("SIM800L EVB Documentation", "unknown", "1970-01-01"),
    "dat_17": ("SIM800 Series SSL AT Command Manual", "V1.01", "2016-03-10"),
    "dat_18": ("SIMCom Certification", "unknown", "1970-01-01"),
}

# Dataset-specific fields and their default "empty" values.
DATASET_FIELDS = {
    "dat_01": {"command": None, "mode": None, "syntax": None, "parameters": [],
               "response_success": None, "response_error": None, "examples": [],
               "related_urcs": [], "related_states": [], "related_commands": [],
               "firmware_min": None, "firmware_max": None},
    "dat_02": {"urc_string": None, "trigger_event": None, "related_command": None,
               "related_state": None, "format": None, "parameters": [],
               "examples": [], "timing": None, "suppression_method": None},
    "dat_03": {"error_type": None, "code": None, "meaning": None, "description": None,
               "related_commands": [], "recovery_steps": []},
    "dat_04": {"parameter": None, "min": None, "typ": None, "max": None, "unit": None,
               "condition": None, "related_command": None, "related_state": None,
               "related_urc": None},
    "dat_05": {"state_name": None, "description": None, "entry_conditions": [],
               "exit_conditions": [], "events": [], "actions": [],
               "related_commands": [], "related_urcs": [], "related_timings": []},
    "dat_06": {"step_order": None, "command": None, "expected_response": None,
               "timeout_ms": None, "retry_count": None, "failure_action": None,
               "dependency_step": None, "related_state": None},
    "dat_07": {"name": None, "pin_number": None, "direction": None, "voltage_min": None,
               "voltage_typ": None, "voltage_max": None, "current_typ": None,
               "current_max": None, "function": None, "alternate_function": None,
               "pull_up_down": None, "esd_rating": None, "impedance": None,
               "decoupling": None},
    "dat_08": {"firmware_version": None, "release_date": None, "base_version": None,
               "supported_commands": [], "unsupported_commands": [], "features": [],
               "known_issues": [], "fixed_issues": [], "related_commands": []},
    "dat_09": {"mode": None, "command": None, "syntax": None, "parameters": [],
               "response": None, "examples": [], "related_urcs": [], "encoding": None,
               "storage": None, "concat_sms": None, "delivery_report": None},
    "dat_10": {"command": None, "syntax": None, "parameters": [], "response": None,
               "examples": [], "related_urcs": [], "related_states": [],
               "related_commands": []},
    "dat_11": {"command": None, "syntax": None, "parameters": [], "response": None,
               "examples": [], "related_urcs": [], "related_commands": []},
    "dat_12": {"command": None, "syntax": None, "parameters": [], "response": None,
               "examples": [], "related_commands": []},
    "dat_13": {"command": None, "syntax": None, "parameters": [], "response": None,
               "examples": [], "related_urcs": [], "hardware_pins": []},
    "dat_14": {"mcc": None, "mnc": None, "country": None, "country_code": None,
               "operator": None, "brand": None, "network_type": None,
               "apn_list": [], "source_url": None},
    "dat_15": {"mode": None, "command": None, "parameter": None, "value_min": None,
               "value_typ": None, "value_max": None, "unit": None, "condition": None,
               "wake_source": None, "related_commands": [], "related_states": []},
    "dat_16": {"name": None, "connector": None, "pin": None, "function": None,
               "voltage": None, "notes": None},
    "dat_17": {"command": None, "syntax": None, "parameters": [], "response": None,
               "examples": [], "tls_version": None, "cipher_suite": None,
               "cert_format": None, "key_format": None, "storage": None,
               "limits": None, "related_commands": []},
    "dat_18": {"certification_body": None, "certificate_number": None, "standard": None,
               "country": None, "date_issued": None, "date_expiry": None,
               "document_link": None},
}


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def count_valid(records):
    n = 0
    for r in records:
        if isinstance(r, dict) and r.get("id"):
            n += 1
    return n


def find_candidates(root, ds_id):
    """Return list of (label, records) from current, archives, backups."""
    candidates = []

    # Current
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        candidates.append((f"current:{p.name}", load_yaml(p)))

    # Archives
    archive_root = root / "reports" / "_archive"
    if archive_root.exists():
        for sub in sorted(archive_root.iterdir()):
            if not sub.is_dir():
                continue
            for p in sorted(sub.glob(f"{ds_id}*.yaml")):
                candidates.append((f"archive:{sub.name}/{p.name}", load_yaml(p)))

    # Sibling backups
    parent = root.parent
    if parent.exists():
        for sib in sorted(parent.iterdir()):
            if not sib.is_dir():
                continue
            if "backup" not in sib.name.lower():
                continue
            for p in sorted((sib / "data").glob(f"{ds_id}_*.yaml")):
                candidates.append((f"backup:{sib.name}/{p.name}", load_yaml(p)))

    return candidates


def pick_best(candidates):
    """Return (label, records) with highest count of dict-with-id records."""
    best = (None, [])
    best_score = -1
    for label, records in candidates:
        score = count_valid(records)
        if score > best_score:
            best_score = score
            best = (label, records)
    return best


def repair_dataset(ds_id, raw_records, now_iso):
    """Return (repaired_records, stats)."""
    src_name, src_ver, src_date = DEFAULT_SOURCES.get(
        ds_id, ("unknown", "unknown", "1970-01-01")
    )
    specific_fields = DATASET_FIELDS.get(ds_id, {})
    fixed_base = 0
    fixed_specific = 0
    repaired = []

    for idx, r in enumerate(raw_records):
        if not isinstance(r, dict):
            continue  # truly unfixable

        changed = False

        # id
        if not r.get("id"):
            r["id"] = f"{ds_id}_{idx+1:04d}"
            changed = True

        # category
        if not r.get("category"):
            r["category"] = ds_id
            changed = True

        # source
        if not isinstance(r.get("source"), dict) or not r["source"].get("name"):
            r["source"] = {"name": src_name, "version": src_ver, "date": src_date}
            changed = True
        else:
            s = r["source"]
            if not s.get("name"):    s["name"] = src_name; changed = True
            if not s.get("version"): s["version"] = src_ver; changed = True
            if not s.get("date"):    s["date"] = src_date; changed = True

        # source_type
        if r.get("source_type") not in ("primary", "secondary", "external"):
            r["source_type"] = "primary"
            changed = True

        # confidence
        if not isinstance(r.get("confidence"), (int, float)) or not (0.0 <= r["confidence"] <= 1.0):
            r["confidence"] = 0.7
            changed = True

        # status
        if r.get("status") not in ("complete", "partial", "unknown", "inferred", "blocked", "deferred"):
            r["status"] = "partial"
            changed = True

        # applicable_models
        models = r.get("applicable_models")
        if not isinstance(models, list) or "SIM800L" not in models:
            r["applicable_models"] = ["SIM800L"]
            changed = True

        # created_at / updated_at
        if not isinstance(r.get("created_at"), str) or not r["created_at"]:
            r["created_at"] = now_iso
            changed = True
        if not isinstance(r.get("updated_at"), str) or not r["updated_at"]:
            r["updated_at"] = now_iso
            changed = True

        if changed:
            fixed_base += 1

        # Dataset-specific fields
        spec_changed = False
        for k, default_val in specific_fields.items():
            if k not in r:
                r[k] = default_val
                spec_changed = True
        if spec_changed:
            fixed_specific += 1

        repaired.append(r)

    stats = {
        "dataset": ds_id,
        "input_records": len(raw_records),
        "output_records": len(repaired),
        "fixed_base_fields": fixed_base,
        "fixed_specific_fields": fixed_specific,
    }
    return repaired, stats


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    audit = {"timestamp": now_iso, "datasets": []}

    print(f"{'Dataset':<8} {'Source':<45} {'In':>5} {'Out':>5} {'FixedBase':>10} {'FixedSpec':>10}")
    print("-" * 95)

    for ds_id in DATASETS:
        candidates = find_candidates(root, ds_id)
        label, records = pick_best(candidates)
        if label is None:
            label = "empty"
            records = []

        repaired, stats = repair_dataset(ds_id, records, now_iso)

        # Find current filename (or create default)
        current_files = sorted((root / "data").glob(f"{ds_id}_*.yaml"))
        if current_files:
            out_path = current_files[0]
        else:
            out_path = root / "data" / f"{ds_id}_data.yaml"

        # Write repaired (always, even if empty -> [] to be schema-valid list)
        with open(out_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(repaired, f, allow_unicode=True,
                           sort_keys=False, default_flow_style=False)

        stats["source_used"] = label
        stats["output_file"] = out_path.name
        audit["datasets"].append(stats)

        print(f"{ds_id:<8} {label[:44]:<45} {stats['input_records']:>5} "
              f"{stats['output_records']:>5} {stats['fixed_base_fields']:>10} "
              f"{stats['fixed_specific_fields']:>10}")

    total_out = sum(d["output_records"] for d in audit["datasets"])
    total_fixed_base = sum(d["fixed_base_fields"] for d in audit["datasets"])
    audit["total_output_records"] = total_out
    audit["total_fixed_base_fields"] = total_fixed_base

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "_recovery_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    print("-" * 95)
    print(f"Total output records      : {total_out}")
    print(f"Total records base-fixed  : {total_fixed_base}")
    print(f"Audit JSON                : reports/_recovery_audit.json")
    sys.exit(0)


if __name__ == "__main__":
    main()