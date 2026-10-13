# Changelog (reports)

## [Unreleased] - 2026-10-13T18:55:14Z

### Added
- Classified cross-reference report (pending_blocked / format_mismatch / real_missing).
- Coverage matrix with per-dataset coverage, estimate, source, reason.
- Consistency report (R20) across shared command keys.
- SOURCE_INVENTORY.md with full inventory of available and missing sources.

### Fixed
- ISO 8601 UTC timestamp for backup folder names (previous Jalali format).
- Nullable optional fields in schema (validated 0 errors).
- Deterministic IDs (SHA-1 of record content).

### Changed
- Blocked datasets (dat_08, dat_16, dat_18) marked explicitly.
- Per-dataset category (semantic, not "dat_XX").