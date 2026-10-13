# Changelog

## [0.9.0] - 2026-10-13T19:11:56Z

### Added
- Extended cross-reference rules: dat_15 -> dat_01, dat_14 -> dat_10, dat_17 -> dat_11.
- Hardened validate.py: R12 (complete requires coverage) and SIM800H-only rejection.
- Per-dataset reports include explicit `Why partial/blocked` section.

### Changed
- Classification rebuilt from cross_ref buckets.
- dat_01 extended with 5 basic AT commands (Q1).
- dat_06 command-fields nulled for 6 non-command items (Q3).

### Fixed
- Replaced legacy _validation_summary.json with _validation_result.json.
- ISO 8601 UTC timestamps enforced.

## [0.1.0] - project start

- Initial schemas, data files, and reports.