# SIM800L Data

Structured, source-documented, schema-validated dataset for the SIM800L module.

## Layout

- `data/`     - 18 datasets (dat_01 .. dat_18), YAML.
- `schemas/`  - 18 JSON-Schema files (draft-07) with nullable optionals.
- `reports/`  - coverage, validation, cross-ref, classification, consistency.
- `scripts/`  - validate, normalize, cross_ref, coverage, consistency, classify, apply.
- `sources/`  - original PDFs and extracted text.

## Current Status (2026-10-13T19:07:51Z)

- Total records          : 1369
- Validation errors      : 0
- Basic AT added (Q1)    : 5
- dat_06 command-nulled  : 6

## Cross-ref buckets

- pending_blocked   : 35
- format_mismatch   : 129
- real_missing      : 0

## Real-missing classes (should be 0 after fix)

- basic_at_missing     : 0
- manual_owned_pending : 0
- not_a_command        : 0
- unknown              : 0

## Blocked Datasets

- dat_08 (Firmware), dat_16 (EVB), dat_18 (Certification)