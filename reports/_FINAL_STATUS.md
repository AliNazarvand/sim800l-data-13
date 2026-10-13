# SIM800L Data - Final Status



**Generated**: 2026-10-13T19:10:14Z



## Overall



| Metric | Value |

|---|---|

| Total records | 1369 |

| Validation errors | 0 |

| real_missing | 0 |

| pending_blocked | 35 |

| format_mismatch | 129 |

| basic AT added (Q1) | 5 |

| dat_06 nulled (Q3) | 6 |



## Per-dataset



| Dataset | Name | Records | Errors | Status | Coverage | Est |

|---|---|---|---|---|---|---|

| dat_01 | AT Command | 340 | 0 | complete | 101.5% | high |

| dat_02 | URC | 18 | 0 | partial | — | low |

| dat_03 | Error Code | 255 | 0 | partial | — | high |

| dat_04 | Timing & Timeout | 99 | 0 | partial | — | medium |

| dat_05 | State Machine | 31 | 0 | partial | — | medium |

| dat_06 | Init Sequence | 35 | 0 | partial | — | medium |

| dat_07 | Hardware Reference | 77 | 0 | partial | — | medium |

| dat_08 | Firmware Compatibility | 1 | 0 | blocked | — | low |

| dat_09 | SMS | 14 | 0 | partial | — | low |

| dat_10 | GPRS/Data | 24 | 0 | partial | — | medium |

| dat_11 | HTTP/FTP/SSL | 38 | 0 | partial | — | medium |

| dat_12 | Audio | 13 | 0 | partial | — | low |

| dat_13 | SIM Management | 10 | 0 | partial | — | low |

| dat_14 | Operator/APN | 52 | 0 | partial | — | medium |

| dat_15 | Power Management | 351 | 0 | partial | — | high |

| dat_16 | Board/EVB | 1 | 0 | blocked | — | low |

| dat_17 | Certificate/Key Store | 9 | 0 | partial | — | low |

| dat_18 | Certification | 1 | 0 | blocked | — | low |



## Outstanding (documented)



- 35 cross-refs are pending_blocked (missing manuals).

- dat_07 pin-table coverage audit deferred (Q4).

- dat_08, dat_16, dat_18 blocked (sources unavailable).



## Pipeline



- validate.py (R1-R24 + schema)

- cross_ref.py (3-bucket)

- classify_missing.py (4-way)

- coverage_report.py

- consistency_check.py (R20)

- apply_decisions.py (Q1/Q3)

- normalize_data.py

- dedup_dat07.py