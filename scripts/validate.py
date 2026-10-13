#!/usr/bin/env python3
"""Validate all SIM800L datasets against their schemas and project rules."""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft7Validator
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False

DATASETS = [f"dat_{i:02d}" for i in range(1, 19)]
VALID_STATUS = {"complete","partial","unknown","inferred","blocked","deferred"}
VALID_SOURCE_TYPES = {"primary","secondary","external"}


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def find_data_file(root, ds_id):
    for p in sorted((root / "data").glob(f"{ds_id}_*.yaml")):
        return p
    return None


def validate_dataset(root, ds_id):
    errors = []
    warnings = []
    data_path = find_data_file(root, ds_id)
    if data_path is None:
        return {"dataset": ds_id, "file": None, "records": 0,
                "errors": [f"No data file for {ds_id}"],
                "warnings": warnings, "schema_ok": False}

    try:
        records = load_yaml(data_path)
    except Exception as e:
        return {"dataset": ds_id, "file": data_path.name, "records": 0,
                "errors": [f"YAML load failed: {e}"],
                "warnings": warnings, "schema_ok": False}
    if not isinstance(records, list):
        return {"dataset": ds_id, "file": data_path.name, "records": 0,
                "errors": ["Top-level YAML must be a list"],
                "warnings": warnings, "schema_ok": False}

    schema = None
    schema_path = root / "schemas" / f"{ds_id}.schema.yaml"
    if schema_path.exists():
        try:
            schema = load_yaml(schema_path)
        except Exception as e:
            warnings.append(f"Schema load failed: {e}")

    validator = None
    if HAVE_JSONSCHEMA and schema:
        try:
            Draft7Validator.check_schema(schema)
            validator = Draft7Validator(schema)
        except Exception as e:
            warnings.append(f"Schema invalid: {e}")

    seen_ids = set()
    complete_records = 0
    for idx, rec in enumerate(records):
        if not isinstance(rec, dict):
            errors.append(f"[#{idx}] not a mapping")
            continue
        rid = rec.get("id")
        if not rid:
            errors.append(f"[#{idx}] missing id")
            continue

        models = rec.get("applicable_models") or []
        # R1
        if "SIM800L" not in models:
            errors.append(f"[{rid}] R1: applicable_models must contain SIM800L")
        # SIM800H-only check (applicable_models has SIM800H but not SIM800L)
        if "SIM800H" in models and "SIM800L" not in models:
            errors.append(f"[{rid}] SIM800H-only record forbidden")

        # R2
        if not isinstance(rec.get("source"), dict) or not rec["source"].get("name"):
            errors.append(f"[{rid}] R2: missing or invalid source.name")
        # R6
        if rec.get("status") == "synthetic":
            errors.append(f"[{rid}] R6: synthetic forbidden")
        # R21
        if rec.get("status") == "example-only":
            errors.append(f"[{rid}] R21: example-only forbidden in data/")
        # R22
        if rec.get("status") == "in-progress":
            errors.append(f"[{rid}] R22: in-progress forbidden in data/")

        st = rec.get("status")
        if st not in VALID_STATUS:
            errors.append(f"[{rid}] invalid status: {st}")
        if st == "complete":
            complete_records += 1

        stype = rec.get("source_type")
        if stype not in VALID_SOURCE_TYPES:
            errors.append(f"[{rid}] invalid source_type: {stype}")
        # R5: secondary <= 0.7
        c = rec.get("confidence")
        if not isinstance(c, (int, float)) or not (0.0 <= c <= 1.0):
            errors.append(f"[{rid}] confidence out of [0,1]: {c!r}")
        elif stype in ("secondary", "external") and c > 0.7:
            errors.append(f"[{rid}] R5: {stype} confidence > 0.7")

        if rid in seen_ids:
            errors.append(f"[{rid}] duplicate id")
        seen_ids.add(rid)

        if validator is not None:
            for err in validator.iter_errors(rec):
                errors.append(f"[{rid}] schema: {err.message}")

    # R12: coverage for complete datasets
    cov_path = root / "reports" / "_coverage_result.json"
    if cov_path.exists() and complete_records > 0:
        try:
            cov = json.loads(cov_path.read_text(encoding="utf-8"))
            rows = cov.get("rows", [])
            for r in rows:
                if r.get("dataset") == ds_id:
                    cov_val = r.get("coverage")
                    est = r.get("coverage_estimate")
                    if cov_val is None and est != "high":
                        errors.append(
                            f"[dataset] R12: contains complete records "
                            f"but coverage is None and estimate != high")
                    elif cov_val is not None and cov_val < 95.0:
                        errors.append(
                            f"[dataset] R12: contains complete records "
                            f"but coverage {cov_val}% < 95%")
        except Exception as e:
            warnings.append(f"R12 coverage check failed: {e}")

    return {"dataset": ds_id, "file": data_path.name, "records": len(records),
            "errors": errors, "warnings": warnings,
            "complete_records": complete_records,
            "schema_ok": len(errors) == 0}


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    results = [validate_dataset(root, ds) for ds in DATASETS]
    total_errors = sum(len(r["errors"]) for r in results)
    total_records = sum(r["records"] for r in results)

    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "_validation_result.json").write_text(
        json.dumps({"results": results, "total_errors": total_errors,
                    "total_records": total_records, "jsonschema": HAVE_JSONSCHEMA},
                   indent=2, ensure_ascii=False),
        encoding="utf-8")

    lines = ["# Validation Report", "",
             f"- Datasets: {len(results)}",
             f"- Total records: {total_records}",
             f"- Total errors: {total_errors}",
             f"- jsonschema available: {HAVE_JSONSCHEMA}", ""]
    for r in results:
        flag = "OK" if r["schema_ok"] else "FAIL"
        lines.append(f"## {r['dataset']} [{flag}] records={r['records']}")
        if r["file"]:
            lines.append(f"File: `{r['file']}`")
        for w in r["warnings"]:
            lines.append(f"- WARN: {w}")
        if r["errors"]:
            for e in r["errors"][:30]:
                lines.append(f"- ERROR: {e}")
            if len(r["errors"]) > 30:
                lines.append(f"- ... and {len(r['errors'])-30} more")
        lines.append("")
    (out_dir / "VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[validate] datasets={len(results)} records={total_records} errors={total_errors}")
    sys.exit(3 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()