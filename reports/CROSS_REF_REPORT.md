# Cross-Reference Report

- Rules evaluated: 16
- pending_blocked : 9
- format_mismatch : 129
- real_missing    : 26

- **URC.related_command -> AT.command** — pending_blocked
    - pending_blocked=0 format_mismatch=12 real_missing=0
        [format_mismatch] AT+CGREG, AT+CIPRXGET, AT+CIPSTATUS, AT+CLIP, AT+CNMI, AT+CPIN, AT+CREG, AT+CUSD, AT+FTPGET, AT+FTPPUT
- **URC.related_state -> State.state_name** — ok
- **ErrorCode.related_commands -> AT.command** — ok
- **Timing.related_command -> AT.command** — ok
- **Timing.related_state -> State.state_name** — ok
- **State.related_commands -> AT.command** — pending_blocked
    - pending_blocked=0 format_mismatch=25 real_missing=0
        [format_mismatch] AT+CCID, AT+CFUN=1, AT+CFUN=1,1, AT+CGACT, AT+CGATT, AT+CGATT=1, AT+CGDCONT, AT+CIMI, AT+CIPCLOSE, AT+CIPSEND
- **Init.command -> AT.command** — pending_blocked
    - pending_blocked=0 format_mismatch=19 real_missing=0
        [format_mismatch] AT+CFUN=1, AT+CGACT=1,<cid>, AT+CGATT=1, AT+CGREG?, AT+CIFSR, AT+CIICR, AT+CIPSTART="TCP","host",port, AT+CIPSTART=<mode>,<IP>,<port>, AT+CMGF=1, AT+CPIN=<pin>
- **Init.related_state -> State.state_name** — ok
- **SMS.command -> AT.command** — pending_blocked
    - pending_blocked=0 format_mismatch=14 real_missing=0
        [format_mismatch] AT+CMEE, AT+CMGD, AT+CMGF, AT+CMGL, AT+CMGR, AT+CMGS, AT+CMGW, AT+CNMI, AT+CPMS, AT+CSCA
- **GPRS.command -> AT.command** — unresolved
    - pending_blocked=0 format_mismatch=21 real_missing=3
        [format_mismatch] AT+CDNSGIP, AT+CGACT, AT+CGATT, AT+CGDCONT, AT+CGPADDR, AT+CGREG, AT+CIFSR, AT+CIICR, AT+CIPCCFG, AT+CIPCLOSE
        [real_missing] AT+CEREG, AT+CGCONTRDP, AT+CIPDDREM
- **HTTP/FTP/SSL.command -> AT.command** — unresolved
    - pending_blocked=0 format_mismatch=19 real_missing=19
        [format_mismatch] AT+FTPDELE, AT+FTPGET, AT+FTPGETPATH, AT+FTPLIST, AT+FTPMKD, AT+FTPMODE, AT+FTPPORT, AT+FTPPUT, AT+FTPPUTOPT, AT+FTPPUTPATH
        [real_missing] AT+FTPCLOSE, AT+FTPCWD, AT+FTPFLST, AT+FTPOPEN, AT+FTPPASS, AT+FTPPWD, AT+FTPUSER, AT+HTTPHEAD, AT+HTTPSSL, AT+HTTPURL
- **Audio.command -> AT.command** — unresolved
    - pending_blocked=0 format_mismatch=9 real_missing=4
        [format_mismatch] AT+CADC, AT+CHFA, AT+CLVL, AT+CMIC, AT+CMUT, AT+CRSL, AT+CRSM, AT+CSDT, AT+VTS
        [real_missing] AT+CADTONE, AT+CATONE, AT+CLDTONE, AT+CPCMREG
- **SIM.command -> AT.command** — pending_blocked
    - pending_blocked=0 format_mismatch=10 real_missing=0
        [format_mismatch] AT+CCID, AT+CIMI, AT+CLCK, AT+CPIN, AT+CPWD, AT+CRSM, AT+CSIM, AT+CSMINS, AT+CSPN, AT+CUSD
- **Power.command -> AT.command** — ok
- **Cert.command -> AT.command** — pending_blocked
    - pending_blocked=9 format_mismatch=0 real_missing=0
        [pending_blocked] AT+SSLCFG, AT+SSLCLOSE, AT+SSLCONF, AT+SSLOPEN, AT+SSLRECV, AT+SSLSEND, AT+SSLSETCA, AT+SSLSETCERT, AT+SSLSETKEY
- **Cert.related_commands -> AT.command** — ok