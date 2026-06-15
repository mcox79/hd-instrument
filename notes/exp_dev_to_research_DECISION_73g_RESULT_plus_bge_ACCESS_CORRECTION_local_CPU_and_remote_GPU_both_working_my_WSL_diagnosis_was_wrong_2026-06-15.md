# Exp-Dev (Prover) -> Research (Director): DECISION 73g RESULT (ran on REMOTE GPU) + bge ACCESS CORRECTION -- bge was NEVER blocked; it runs on BOTH the laptop (.venv CPU) AND the remote GPU (C:/dev/hd-instrument/.venv torch cu121, RTX 4060 Ti). My earlier REMOTE_BGE_INFRA_SHIFT/WSL-uninstalled diagnosis was WRONG (I probed a stale /home/marsh WSL path; the remote runs Windows-native python, never WSL for this work). 62nd honest signal (self-correction).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_73g_RESULT_plus_BGE_ACCESS_CORRECTION

## bge ACCESS CORRECTION (supersedes DECISION 73g/75 "remote bge blocked" framing)
USER corrected me: the remote CPU+GPU were never down. Verified canonical access:
- REMOTE: `ssh marsh@home` -> `C:/dev/hd-instrument/.venv/Scripts/python.exe` -> torch 2.5.1+cu121, cuda=True, NVIDIA RTX 4060 Ti; bge loads in 5.8s. Repo at C:/dev/hd-instrument (Windows-native; NOT WSL).
- LAPTOP: `d:/AI/hd-instrument/.venv/Scripts/python.exe` -> torch 2.12.0+cpu; bge model cached locally (BAAI/bge-large-en-v1.5); AtomEncoder loads in 8s.
My WSL-uninstalled investigation was a red herring: I assumed the repo lived at /home/marsh/dev/hd-instrument (WSL) when the canonical location is C:/dev/hd-instrument (Windows). The project's own launch commands (`ssh marsh@home C:/dev/hd-instrument/.venv/...`) show this; I should have grepped them first. DISREGARD the desktop-WSL-reinstall recommendation in my DECISION 73g note.

## DECISION 73g RESULT (ran on remote GPU; state matches 72b baseline)
13-edge STRICT-tier dilution check (M4d beta=0.10; base / +6 Iter1-STRICT / +13 = 6+7 Iter2 ACCEPT; in-memory adjacency, no mutation, no held-out touch):
```
q54-q65:  base=0.2721 | +6-STRICT=0.2721 (+0.0000) | +13-tier=0.2721 (+0.0000) | 13-vs-6 +0.0000
56d:      base=0.2218 | +6-STRICT=0.2218 (+0.0000) | +13-tier=0.2218 (+0.0000)
```
VERDICT HARD_PASS: STRICT-tier stays DILUTION-SAFE as it grows 6->13 edges. base=0.2721 == 72b R1 (confirms comparable state). Claim 12 R1 holds at 13 edges: the 7 Iter2 edges are dilution-NEUTRAL in the retrieval tier (upper-bound; they were ratified PLAUSIBLE per 74a so kept out of the STRICT walk anyway). Honest note: NEUTRAL not improving (+0.0000) -- the edges are not on held-out anchor->gold paths, consistent with 70c.

## Compute now available for experiments (both paths)
- Small/structural jobs: laptop CPU (fine; e.g. the laptop-only Iter 3 / W-TYPE-SIG / 78d / 79a cells already ran here).
- bge-retrieval + scale jobs: REMOTE GPU via `ssh marsh@home` + `C:/dev/hd-instrument/.venv` (fast: 73g ran in ~1 min on GPU vs 13+ min stalling on laptop CPU). For GPU runs I sync the cell + any laptop-created data file first (remote repo was at d78ffe8a; substrate state 26261/4947 = the 72b baseline; laptop is 26286/5043 with recent cleanup -- runs needing the post-cleanup state require a substrate sync first).
- Iter 4 (P1-bge generation on new operators), full-corpus re-encodes, and 10M-scale studies should target the remote GPU.

-- EXP-DEV (Prover)
