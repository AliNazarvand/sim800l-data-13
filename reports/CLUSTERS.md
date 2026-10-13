# Cluster Status (A / B / C)

## Cluster A — Hardware
- dat_04 Timing — partial
- dat_05 State Machine — partial
- dat_06 Init Sequence — partial
- dat_07 Hardware Reference — partial
- dat_15 Power Management — partial
- dat_16 Board/EVB — blocked

## Cluster B — AT Command dependent
- dat_01 AT Command — partial
- dat_02 URC — partial
- dat_03 Error Code — partial
- dat_09 SMS — partial
- dat_10 GPRS — partial
- dat_11 HTTP/FTP/SSL — partial
- dat_12 Audio — partial
- dat_13 SIM Management — partial
- dat_17 Certificate/Key Store — partial

## Cluster C — External sources
- dat_08 Firmware — blocked
- dat_14 Operator/APN — partial (external source)
- dat_18 Certification — blocked

Closure rule (R24): a cluster closes when ALL members reach complete/blocked/deferred.
Because Cluster B contains partial members awaiting missing manuals, Cluster B is not yet closed.