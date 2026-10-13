# SIM800L Data - Final Status



**Generated**: 2026-10-13T19:15:43Z



## Overall



| Metric | Value |

|---|---|

| Total records | 1369 |

| Validation errors | 0 |

| real_missing | 0 |

| pending_blocked | 35 |

| format_mismatch | 129 |



## Per-dataset



| Dataset | Name | Records | Complete | Partial | Blocked | Errors | Status | Coverage | Est |

|---|---|---|---|---|---|---|---|---|---|

| dat_01 | AT Command | 340 | 0 | 340 | 0 | 0 | complete | 100.0% | high |

| dat_02 | URC | 18 | 0 | 18 | 0 | 0 | partial | — | low |

| dat_03 | Error Code | 255 | 237 | 12 | 0 | 0 | partial | — | high |

| dat_04 | Timing & Timeout | 99 | 0 | 87 | 0 | 0 | partial | — | medium |

| dat_05 | State Machine | 31 | 0 | 16 | 0 | 0 | partial | — | medium |

| dat_06 | Init Sequence | 35 | 0 | 25 | 0 | 0 | partial | — | medium |

| dat_07 | Hardware Reference | 77 | 0 | 77 | 0 | 0 | partial | — | medium |

| dat_08 | Firmware Compatibility | 1 | 0 | 0 | 1 | 0 | blocked | — | low |

| dat_09 | SMS | 14 | 0 | 14 | 0 | 0 | partial | — | low |

| dat_10 | GPRS/Data | 24 | 0 | 21 | 3 | 0 | partial | — | medium |

| dat_11 | HTTP/FTP/SSL | 38 | 0 | 19 | 19 | 0 | partial | — | medium |

| dat_12 | Audio | 13 | 0 | 9 | 4 | 0 | partial | — | low |

| dat_13 | SIM Management | 10 | 0 | 10 | 0 | 0 | partial | — | low |

| dat_14 | Operator/APN | 52 | 0 | 52 | 0 | 0 | partial | — | medium |

| dat_15 | Power Management | 351 | 1 | 350 | 0 | 0 | partial | — | high |

| dat_16 | Board/EVB | 1 | 0 | 0 | 1 | 0 | blocked | — | low |

| dat_17 | Certificate/Key Store | 9 | 0 | 0 | 9 | 0 | partial | — | low |

| dat_18 | Certification | 1 | 0 | 0 | 1 | 0 | blocked | — | low |



## Outstanding (documented, not blocking)



- 35 cross-refs are pending_blocked (missing manuals: TCP-IP, HTTP, FTP, SSL, Audio).

- dat_08, dat_16, dat_18 blocked (sources unavailable in sources/originals/).

- Q4: dat_07 pin-table coverage audit vs V2.02 deferred.



## Pipeline



- scripts/validate.py (R1-R24 + schema)

- scripts/cross_ref.py (3-bucket cross-ref)

- scripts/classify_missing.py (4-way real_missing classifier)

- scripts/coverage_report.py (coverage + record status counts)

- scripts/consistency_check.py (R20)

- scripts/apply_decisions.py (Q1/Q3 owner decisions)

- scripts/normalize_data.py (ID stabilization + blocked marking)

- scripts/dedup_dat07.py (dat_07 deduplication)

- scripts/fix_validate_errors.py (R5/SIM800H/R12 fixes)