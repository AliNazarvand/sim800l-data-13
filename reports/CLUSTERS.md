# Cluster Status

Generated: 2026-10-13T19:10:14Z

## Cluster A - Hardware

- dat_04 Timing - partial
- dat_05 State Machine - partial
- dat_06 Init Sequence - partial
- dat_07 Hardware Reference - partial
- dat_15 Power Management - partial
- dat_16 Board/EVB - blocked (no official EVB doc)

## Cluster B - AT Command dependent

- dat_01 AT Command - partial
- dat_02 URC - partial
- dat_03 Error Code - partial
- dat_09 SMS - partial
- dat_10 GPRS - partial
- dat_11 HTTP/FTP/SSL - partial
- dat_12 Audio - partial
- dat_13 SIM Management - partial
- dat_17 Certificate/Key Store - partial

## Cluster C - External sources

- dat_08 Firmware - blocked
- dat_14 Operator/APN - partial (external)
- dat_18 Certification - blocked

Closure rule (R24): a cluster closes when ALL members reach complete/blocked/deferred.

- Cluster A: not closed (dat_04/05/06/07/15 partial awaiting pin-table audit)
- Cluster B: not closed (waiting for FTP/HTTP/SSL/Audio/TCP-IP manuals)
- Cluster C: closed (all members are blocked or partial with external source)