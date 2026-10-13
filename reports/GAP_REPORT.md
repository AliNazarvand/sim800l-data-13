# Gap Report

Generated: 2026-10-13T19:10:14Z

## Missing Sources

| Missing Document | Affected Datasets | Status |
|---|---|---|
| SIM800 Series TCP/IP AT Command Manual | dat_10 | pending_blocked |
| SIM800 Series HTTP AT Command Manual | dat_11 | pending_blocked |
| SIM800 Series FTP AT Command Manual | dat_11 | pending_blocked |
| SIM800 Series SSL AT Command Manual | dat_11, dat_17 | pending_blocked |
| SIM800 Series Audio AT Command Manual | dat_12 | pending_blocked |
| SIM800 Series SIM AT Command Manual | dat_13 | pending_blocked |
| SIM800L Datasheet | supplementary | missing |
| SIM800 Series Sleep Mode Application Note | dat_15 | missing |
| SIM800 Series URC Application Note | dat_02 | missing |
| SIM800 Series Firmware Release Notes | dat_08 | blocked |
| SIM800 Series Certification Documents (CE/FCC/GCF/PTCRB/RoHS/IC/TA/RCM/Anatel/NCC) | dat_18 | blocked |
| Official EVB documentation | dat_16 | blocked |

## Impact

- pending_blocked cross-refs: 35
- format_mismatch cross-refs: 129 (safe; normalized form matches existing entries)
- real_missing cross-refs: 0

## Resolution Plan

Each missing manual, once provided in `sources/originals/`, will be re-extracted and the corresponding dataset re-audited.