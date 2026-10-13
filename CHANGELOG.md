# Changelog

## [0.9.2] - 2026-10-13T19:15:43Z

### Fixed
- coverage_report.py: coverage capped at 100% (dat_01 ratio overflow).
- dat_14 source now correctly reported as "mcc-mnc.com (external)".
- Per-dataset reports now show record status breakdown (complete/partial/blocked).
- All stale dat_XX_REPORT.md regenerated after R12 downgrade.

### Changed
- Coverage matrix columns updated to include per-status counts.

## [0.9.1] - 2026-10-13T19:13:23Z

### Fixed
- R5: clamp confidence to 0.7 for secondary/external sources.
- SIM800H-only records: add SIM800L to applicable_models.
- R12: downgrade complete records when coverage is insufficient.

## [0.9.0] - 2026-10-13

### Added
- Extended cross-reference rules.
- Hardened validate.py (R12, SIM800H-only).
- Per-dataset reports with partial/blocked reasons.

## [0.1.0] - project start

- Initial schemas, data files, and reports.