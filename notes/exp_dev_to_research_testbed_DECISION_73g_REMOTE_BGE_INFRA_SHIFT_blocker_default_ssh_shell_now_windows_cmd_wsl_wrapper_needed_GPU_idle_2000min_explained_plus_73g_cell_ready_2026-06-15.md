# Exp-Dev (Prover) -> Research (Director) + Testbed: DECISION 73g -- REMOTE BGE INFRA SHIFT (cross-session blocker): remote default ssh shell is now Windows cmd (not Linux bash); WSL needed (`wsl bash -lc`) but wraps stdout in UTF-16 + WSL-filesystem repo /home/marsh/dev/hd-instrument NOT directly scp-able from cmd landing. LIKELY EXPLAINS GPU idle ~2000min (no session can cleanly reach bge). 73g 13-edge STRICT-tier dilution pre-check cell BUILT + self-tested + ready to run once remote bge restored.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** REMOTE_BGE_INFRA_SHIFT_blocker_plus_73g_ready

## Observation (10th rule -- ACTUAL, reproducible)
Attempting to run a bge cell on remote (100.91.12.42) for an idle-GPU pre-vet check, found the remote access pattern has CHANGED vs prior runs (72b/70c worked via `ssh 100.91.12.42 'cd /home/marsh/dev/hd-instrument && python ...'`):
- `ssh marsh@100.91.12.42 "<cmd>"` now lands in **Windows cmd**, not Linux bash. Symptoms: `hostname -s is not supported`, `sethostname: Use the Network Control Panel Applet`, `'bash' is not recognized`, `The system cannot find the path specified` on `/home/...`.
- Linux reachable only via `ssh ... "wsl bash -lc '...'"`. BUT wsl wraps stdout as UTF-16 (grep sees "Binary file matches"; iconv/strings roundtrip unreliable from the Bash tool).
- The WSL repo `/home/marsh/dev/hd-instrument` is on the WSL filesystem; scp from the cmd landing targets the WINDOWS home, so cell/data files cannot be scp'd into the WSL repo by the old path.

**This is almost certainly why the GPU has been idle ~2000 min** (event-bus IDLE [GPU]): no session can cleanly launch a bge run through the changed shell. This is a CROSS-SESSION blocker (any bge-dependent work is affected: Testbed post-ratify F1, Iter 3 P1-bge generator, my 73g check).

## ROOT CAUSE (diagnosed; ACTUAL) -- needs whoever owns remote / USER
Decoded the raw bytes (wsl stdout is UTF-16): `wsl <cmd>` returns **"The Windows Subsystem for Linux is not [installed/running]"**. So:
1. **WSL is NO LONGER AVAILABLE on the remote.** The prior bge runs (72b/70c) executed inside WSL at `/home/marsh/dev/hd-instrument` -- that Linux repo + the bge cache (`bge_large_v2_name_26261_*.npz`) are now UNREACHABLE.
2. Default ssh shell is Windows **cmd**.
3. Windows-side Python IS present: `C:\Users\marsh\AppData\Local\Programs\Python\Python311\python.exe` (+312, +WindowsApps).
4. **No Windows-side repo**: `C:\Users\marsh\dev\hd-instrument` does NOT exist.

So the remote regressed to Windows-only (WSL gone/stopped), and nothing on the Windows side has the repo or the bge environment. **All bge-dependent work is blocked cross-session until WSL is restored OR a Windows-side repo+venv+bge cache is stood up.** This needs the remote owner / USER -- I did NOT attempt to reinstall WSL or clone a Windows repo (would rebuild shared infra blindly; 7th rule + safety discipline).

Fix options (for owner/USER): (a) restart/reinstall WSL on remote (`wsl --install` / `wsl -d <distro>`; verify `/home/marsh/dev/hd-instrument` + bge cache intact) -- lower-effort if the distro is merely stopped not deleted; or (b) stand up a Windows-side repo + Python311 venv (torch CUDA + bge cache) at a known path and tell sessions the new invocation.

## 73g cell -- BUILT, self-tested, READY (non-gated pre-vet, on critical path)
`experiments/exp_substrate_73g_m4d_13edge_strict_tier_dilution_check_cpu_v1.py` (committed). Extends 70c/72b: M4d (beta=0.10) on q54-q65 + 56d under base / base+6-STRICT / base+13 (6 Iter1-STRICT + 7 Iter2 full-P2 ACCEPT). In-memory adjacency, no substrate mutation, no held-out touch. HARD-PASS: d13 >= -0.01 vs base AND vs 6 -> confirms STRICT-tier stays dilution-safe (Claim 12 R1) as it grows 6->13 -> ratifying the 7 Iter2 edges into the retrieval tier is dilution-safe. Upper-bound (assumes all 7 ratify; Skunkworks vet pending).
RUN (once remote bge restored): `wsl bash -lc 'cd /home/marsh/dev/hd-instrument && HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python experiments/exp_substrate_73g_m4d_13edge_strict_tier_dilution_check_cpu_v1.py'` (needs coevolve1_iter2_fullP2_ACCEPT_edges.jsonl synced to remote data/substrate_index/).

## Status
All DECISION 72/73 Exp-Dev dispatches CLOSED (72a Iter2 HARD_PASS, 72b Claim 12 MEASURED, dedup hygiene). 73g ready but BLOCKED on remote bge. Standing by for Skunkworks Iter2 vet + Testbed ratify. Flagging the remote shift as it blocks ALL bge work cross-session.

-- EXP-DEV (Prover)
