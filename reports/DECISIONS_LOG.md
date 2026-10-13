

## 2026-10-13T18:11:10Z — v6-final decisions
- **PowerShell .Count bug**: ( | Where-Object).Count on a single-item result returns the number of keys in the hashtable (9), not 1. Wrapped with @() to force array semantics.
- **dat_01 dedup normalization**: extract_at_commands.py writes commands like +CMGS; _rebuild_B1_dat01.py writes AT+CMGS. Dedup now strips the AT prefix and =... parameter suffix so both collapse to +CMGS.
- **dat_15 dedup key**: 4-field key (category, mode, parameter, command) was too strict. Now uses 2-field key (category, parameter); mode and command serve as fallbacks.
- **Coverage > 100% rule**: coverage of 182% means 610 records against 335 source entries — data quality issue, not completion. Status rule now requires 95 <= coverage <= 100.
- **dat_15 oversize**: If real > 50, mark partial with reason 'oversize'.


## 2026-10-13T18:13:14Z — v7-final
- **dat_15 stays partial**: _rebuild_dat15.py generates 351 records with unique (category, parameter) pairs. This is over-extraction from the hardware PDF (expected ~13-28). Root cause: script extracts per-line rather than per-parameter. Marked partial with clear reason; _rebuild_dat15.py needs manual fix.
- **Root README.md / PHASE_1_REPORT.md / CHANGELOG.md regenerated**: prior versions were stale and reflected older counts.
- **Duplicate report filenames**: removed dat_XX_<name>_REPORT.md in favor of dat_XX_REPORT.md.
- **Status counts verified**: complete=8, partial=4, blocked=5, deferred=1, total=18.

## 1405-07-21T22-22-44

| Decision | Reason | Rejected Alternatives |
|---|---|---|
| Nullable optional fields in schema | Previous schema required strict types; repair fillled nulls causing 6008 errors | additionalProperties false / strict types (rejected) |
| Blocked datasets marked explicitly | R3/R11 require blocked status when source unavailable | Fake source injection (rejected) |
| Deterministic IDs from content hash | Non-idempotent index-based IDs caused repeated-run divergence | Index-based IDs (rejected) |
| Per-dataset default category | "dat_XX" as category is meaningless | Reuse dataset ID (rejected) |
| ISO 8601 backup folder names | Jalali date breaks ISO 8601 requirement (R19) | Jalali timestamp (rejected) |

## 2026-10-13T18:55:14Z — Report Finalization

| Decision | Reason | Rejected Alternatives |
|---|---|---|
| UTC timestamps via InvariantCulture | Local culture produced Jalali dates (R19 violation) | Locale-based formatting (rejected) |
| Classify cross-refs into 3 buckets | R14 requires pending_blocked vs real distinction | Single unresolved bucket (rejected) |
| Coverage estimate per dataset | R12 requires coverage or coverage_estimate | No coverage reporting (rejected) |
| Honest cluster status | R24: cluster closes only when members are closed | Mark all closed (rejected) |

## 2026-10-13T18:59:05Z — Fix Normalizer & Dedup dat_07

| Decision | Reason | Rejected Alternatives |
|---|---|---|
| Strong normalizer in cross_ref.py (align with analyze_missing.py) | 129/167 real_missing were false positives due to weak normalizer | Keep weak normalizer (rejected) |
| Dedup dat_07 by (name,pin_number) | 70/256 duplicates found by audit; violates R8/R10 | Keep duplicates (rejected) |
| Archive removed IDs instead of deleting silently | Traceability per R9/R10 | Delete outright (rejected) |

## 2026-10-13T19:00:52Z — Pending Owner Decisions (R14)

Classification of remaining real_missing refs:

| Category | Count | Proposed Action | Status |
|---|---|---|---|
| basic_at_missing | 6 | Add to dat_01 from AT Manual V1.01 | PENDING owner approval |
| manual_owned_pending | 0 | Mark as pending_blocked | PENDING owner approval |
| not_a_command | 6 | Set command field to null | PENDING owner approval |
| unknown | 26 | Review individually | PENDING |

No changes have been made to dat_01 (R14 compliance).

## 2026-10-13T19:02:17Z — Corrected R14 Classification

| Category | Count | Proposed Action | Status |
|---|---|---|---|
| basic_at_missing | 0 | Add to dat_01 from AT Manual V1.01 | PENDING owner approval |
| manual_owned_pending | 26 | Mark as pending_blocked | PENDING owner approval |
| not_a_command | 6 | Set command field to null | PENDING owner approval |
| unknown | 6 | Review individually | PENDING |

Corrected normalizer applied (AT-prefix stripped for manual matching, AT_COMMAND_RE accepts AT+XXX). No modification to dat_01 (R14).

## 2026-10-13T19:03:54Z — AT Index Loader Fix

| Decision | Reason | Rejected Alternatives |
|---|---|---|
| load_at_index supports flat dict (keys = commands) | Prior versions read only nested lists/values and found 0 commands | Only nested-list reading (rejected) |
| Whitelist fallback for basic AT commands | AT/ATA/ATD/ATH/ATE0 must always classify as basic if absent from dat_01 | Rely solely on index (rejected) |

Result: basic_at_missing=2, manual_owned_pending=26, not_a_command=6, unknown=4.
dat_01 untouched (R14).

## 2026-10-13T19:05:54Z — Final Closure (R14 owner decisions applied)

| Decision | Value | Reason |
|---|---|---|
| Q1: Add basic AT to dat_01 | 5 added | AT Manual V1.01 present |
| Q3: Null dat_06 command-field | 6 nulled | Items are descriptions/signals, not commands |
| Q2: Keep manual-owned as pending_blocked | 26 items | Awaiting FTP/HTTP/SSL/Audio/TCP-IP manuals |
| Q4: dat_07 remains partial | - | Pin table coverage requires manual audit |
| Q5: Git commit | see branch | feature/complete-datasets |

## 2026-10-13T19:07:51Z — True Final Closure

| Decision | Reason | Rejected Alternatives |
|---|---|---|
| cross_ref recognizes all manual prefixes (FTP/HTTP/SSL/Audio/TCP-IP) | 26 commands were mis-bucketed as real_missing | Keep only +SSL prefix (rejected) |
| classify_missing.py rewritten with correct AT_COMMAND_RE | Prior PowerShell -replace corrupted the file (SyntaxError) | In-place regex patch (rejected) |

Result after fix:
- pending_blocked : 35
- format_mismatch : 129
- real_missing    : 0
- basic_at_missing: 0
- manual_owned    : 0
- not_a_command   : 0
- unknown         : 0
