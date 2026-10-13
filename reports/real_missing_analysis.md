# Real-Missing Analysis

Total refs analyzed: **167**

## Classification Summary

| Classification | Count |
|---|---|
| format_mismatch_deep | 129 |
| not_in_manual | 38 |

## Per Source Dataset

| Source | format_mismatch_deep | in_manual_missing_in_dat01 | not_in_manual | pending_blocked_manual |
|---|---|---|---|---|
| dat_02 | 12 | 0 | 0 | 0 |
| dat_05 | 25 | 0 | 4 | 0 |
| dat_06 | 19 | 0 | 8 | 0 |
| dat_09 | 14 | 0 | 0 | 0 |
| dat_10 | 21 | 0 | 3 | 0 |
| dat_11 | 19 | 0 | 19 | 0 |
| dat_12 | 9 | 0 | 4 | 0 |
| dat_13 | 10 | 0 | 0 | 0 |

## Samples per Class

### format_mismatch_deep (129)

- `AT+CGREG` (from dat_02 -> dat_01.command)
- `AT+CIPRXGET` (from dat_02 -> dat_01.command)
- `AT+CIPSTATUS` (from dat_02 -> dat_01.command)
- `AT+CLIP` (from dat_02 -> dat_01.command)
- `AT+CNMI` (from dat_02 -> dat_01.command)
- `AT+CPIN` (from dat_02 -> dat_01.command)
- `AT+CREG` (from dat_02 -> dat_01.command)
- `AT+CUSD` (from dat_02 -> dat_01.command)
- `AT+FTPGET` (from dat_02 -> dat_01.command)
- `AT+FTPPUT` (from dat_02 -> dat_01.command)
- `AT+HTTPACTION` (from dat_02 -> dat_01.command)
- `AT+HTTPREAD` (from dat_02 -> dat_01.command)
- `AT+CCID` (from dat_05 -> dat_01.command)
- `AT+CFUN=1` (from dat_05 -> dat_01.command)
- `AT+CFUN=1,1` (from dat_05 -> dat_01.command)
- `AT+CGACT` (from dat_05 -> dat_01.command)
- `AT+CGATT` (from dat_05 -> dat_01.command)
- `AT+CGATT=1` (from dat_05 -> dat_01.command)
- `AT+CGDCONT` (from dat_05 -> dat_01.command)
- `AT+CIMI` (from dat_05 -> dat_01.command)
- `AT+CIPCLOSE` (from dat_05 -> dat_01.command)
- `AT+CIPSEND` (from dat_05 -> dat_01.command)
- `AT+CIPSTART` (from dat_05 -> dat_01.command)
- `AT+CMGF` (from dat_05 -> dat_01.command)
- `AT+CMGF=1` (from dat_05 -> dat_01.command)
- `AT+CMGR` (from dat_05 -> dat_01.command)
- `AT+CMGS` (from dat_05 -> dat_01.command)
- `AT+CMTE` (from dat_05 -> dat_01.command)
- `AT+COPS?` (from dat_05 -> dat_01.command)
- `AT+CPIN?` (from dat_05 -> dat_01.command)
- ... and 99 more

### not_in_manual (38)

- `AT` (from dat_05 -> dat_01.command)
- `ATA` (from dat_05 -> dat_01.command)
- `ATD` (from dat_05 -> dat_01.command)
- `ATH` (from dat_05 -> dat_01.command)
- `(PWRKEY pulled low for >=1s)` (from dat_06 -> dat_01.command)
- `(wait for +CFUN: 1)` (from dat_06 -> dat_01.command)
- `(wait for +CPIN: READY)` (from dat_06 -> dat_01.command)
- `AT` (from dat_06 -> dat_01.command)
- `ATE0` (from dat_06 -> dat_01.command)
- `PWRKEY pull-down (hardware)` (from dat_06 -> dat_01.command)
- `PWRKEY_LOW` (from dat_06 -> dat_01.command)
- `PWRKEY_RELEASE` (from dat_06 -> dat_01.command)
- `AT+CEREG` (from dat_10 -> dat_01.command)
- `AT+CGCONTRDP` (from dat_10 -> dat_01.command)
- `AT+CIPDDREM` (from dat_10 -> dat_01.command)
- `AT+FTPCLOSE` (from dat_11 -> dat_01.command)
- `AT+FTPCWD` (from dat_11 -> dat_01.command)
- `AT+FTPFLST` (from dat_11 -> dat_01.command)
- `AT+FTPOPEN` (from dat_11 -> dat_01.command)
- `AT+FTPPASS` (from dat_11 -> dat_01.command)
- `AT+FTPPWD` (from dat_11 -> dat_01.command)
- `AT+FTPUSER` (from dat_11 -> dat_01.command)
- `AT+HTTPHEAD` (from dat_11 -> dat_01.command)
- `AT+HTTPSSL` (from dat_11 -> dat_01.command)
- `AT+HTTPURL` (from dat_11 -> dat_01.command)
- `AT+SSLCFG` (from dat_11 -> dat_01.command)
- `AT+SSLCLOSE` (from dat_11 -> dat_01.command)
- `AT+SSLCONF` (from dat_11 -> dat_01.command)
- `AT+SSLOPEN` (from dat_11 -> dat_01.command)
- `AT+SSLRECV` (from dat_11 -> dat_01.command)
- ... and 8 more
