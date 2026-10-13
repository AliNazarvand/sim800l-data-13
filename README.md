# SIM800L Data

Structured, source-documented, schema-validated dataset for the SIM800L module.

## Layout

- `data/`     - 18 datasets (dat_01 .. dat_18), YAML.
- `schemas/`  - 18 JSON-Schema files (draft-07) with nullable optionals.
- `reports/`  - coverage, validation, cross-ref, consistency, classification.
- `scripts/`  - validate, normalize, cross_ref, coverage, consistency, classify, apply_decisions.
- `sources/`  - original PDFs and extracted text.

## Current Status (as of 2026-10-13T19:05:54Z)

- Total records        : 1369
- Validation errors    : 0
- Basic AT added       : 5
- dat_06 command-nulls : 6

## Cross-ref buckets

- pending_blocked   : 9
- format_mismatch   : 129
- real_missing      : 26

## Real-missing classes

- basic_at_missing     : 2
- manual_owned_pending : 26
- not_a_command        : 6
- unknown              : 4

## Blocked Datasets

- dat_08 (Firmware), dat_16 (EVB), dat_18 (Certification)