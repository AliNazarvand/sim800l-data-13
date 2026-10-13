# SIM800L Data - Final Status



**Generated**: 2026-10-13T19:08:52Z



## Overall



| Metric | Value |

|---|---|

| Total records (18 datasets) | 1369 |

| Validation errors | 0 |

| Cross-ref real_missing | 0 |

| Cross-ref pending_blocked | 35 |

| Cross-ref format_mismatch | 129 |



## Real-missing classification



| Category | Count |

|---|---|

| basic_at_missing | 0 |

| manual_owned_pending | 0 |

| not_a_command | 0 |

| unknown | 0 |



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



## Documented outstanding items (not blocking)



- Q2: 0 manual-owned commands stay pending_blocked

      until FTP/HTTP/SSL/Audio/TCP-IP manuals are provided.

- Q4: dat_07 pin-table coverage vs V2.02 manual needs an audit.

- Blocked datasets: dat_08 (Firmware), dat_16 (EVB), dat_18 (Certification).



## Blocked datasets rationale



- **dat_08** - Firmware Release Notes not available in sources/.

- **dat_16** - Official EVB documentation not available in sources/.

- **dat_18** - Certification documents not available in sources/.



## Pipeline scripts



- alidate.py - schema + business logic validation

- cross_ref.py - 3-bucket cross-reference

- classify_missing.py - 4-way classification of real_missing

- coverage_report.py - coverage estimate per dataset

- consistency_check.py - R20 cross-dataset consistency

- pply_decisions.py - Q1/Q3 owner decisions

- 
ormalize_data.py - ID stabilization + blocked datasets

- dedup_dat07.py - dat_07 deduplication