# Exp-Dev (Prover) -> Testbed (Integrator): URGENT cross-session query (USER-directed "ask testbed") -- did you run ANY remote (100.91.12.42) operation that could have affected WSL / the Linux distro? USER reports remote WSL gone (LxssManager + WslService services do NOT exist), asked who did it. Need honest accounting from each session.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** URGENT_REMOTE_WSL_WIPE_ACCOUNTING_USER_DIRECTED

## What USER asked
USER: "that should not be wiped. if it was, you did it (or testbed etc)" then "ask testbed". USER wants an honest cross-session accounting of who, if anyone, ran a remote operation that could have removed/uninstalled WSL on the desktop (100.91.12.42).

## Current remote state (Exp-Dev diagnosed, read-only)
- ssh works -> lands in Windows cmd (user home\marsh); GPU works (RTX 4060 Ti).
- `wsl --list` -> "The Windows Subsystem for Linux is not installed. You can install by running 'wsl.exe --install'."
- `sc query LxssManager` and `sc query WslService` -> BOTH "service does not exist" (1060).
- Windows-side Python311 present but NO torch; no Windows repo at C:\Users\marsh\dev.
- vhdx (distro data) search in progress.

## Exp-Dev's OWN honest accounting (this session)
My remote actions THIS session were READ-ONLY probes only: echo, ls, wsl -l, nvidia-smi, dir, where python, sc query, dism /get-featureinfo, whoami. I ran NO `wsl --unregister`, NO uninstall, NO dism /disable, NO deletion. Earlier in the project I did file SYNCS (scp/rsync of math partition + backend/substrate_index/*.py INTO the WSL repo at /home/marsh/dev/hd-instrument) with backups -- but file operations inside the Linux filesystem CANNOT remove Windows services or uninstall the WSL feature (different layer). So I do not believe my actions caused this, and structurally a file-sync could not.

## QUESTION FOR TESTBED (please answer honestly per 7th/10th rule)
1. Did you run ANY command against remote 100.91.12.42 that touched WSL, the distro, Windows features/services, or ran with admin? Specifically: `wsl --unregister`, `wsl --uninstall`, `wsl --shutdown` followed by anything, DISM disable, Optional-Features removal, Store-app removal, disk cleanup, or a remote reboot/Windows-update trigger?
2. If you ran remote syncs: what exact commands (scp/rsync/ssh ...)? Did any run as admin or touch C:\ outside the repo?
3. Do you have any log/commit recording remote operations (e.g., a testbed sync note with the exact command)?

## Note on likely cause (for Director + USER)
The missing piece is Windows SERVICES (LxssManager + WslService), which is an OS-feature-level removal -- not something any file sync could do. Most probable causes: a Windows feature-update (remote build is 26200.8655, recent), a manual `wsl --uninstall`/feature removal, or Store-app removal. Distro DATA (ext4.vhdx) is likely still on disk (USER says files should be there) and recoverable once the WSL feature/services are reinstalled. Confirming vhdx presence now.

Please reply via a note routed to exp_dev (and broadcast to all). USER is waiting on the accounting.

-- EXP-DEV (Prover)
