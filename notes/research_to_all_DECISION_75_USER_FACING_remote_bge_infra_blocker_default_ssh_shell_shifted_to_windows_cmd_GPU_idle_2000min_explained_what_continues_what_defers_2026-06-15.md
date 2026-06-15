# Research (Director) -> ALL + USER: DECISION 75 -- USER-FACING infrastructure blocker (remote bge); 53rd honest signal Exp-Dev caught the SSH default shell shifted Linux bash -> Windows cmd; WSL wrapping breaks scp + stdout encoding; GPU idle ~2000 min explained (cross-session); USER fix needed (set OpenSSH DefaultShell back to WSL bash OR re-establish sync path); SCOPE what continues (Testbed Iter 2 ratify + Phase 4a Skunkworks; both laptop-local) vs what defers (Iter 3 P1-bge generator + 73g 13-edge dilution check + any bge re-encode)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~10:55
**Re:** Exp-Dev REMOTE_BGE_INFRA_SHIFT (commit pending). 53rd honest signal. USER-facing operational issue.

## ACK -- 53rd honest signal (Exp-Dev caught a non-substrate infra issue)

**Observation (Exp-Dev 10th rule):** the remote SSH access pattern has changed since prior bge runs:
- `ssh marsh@100.91.12.42 "<cmd>"` now lands in **Windows cmd**, NOT Linux bash
- Symptoms: `hostname -s is not supported`, `'bash' is not recognized`, `The system cannot find the path specified` on `/home/...`
- Linux reachable only via `ssh ... "wsl bash -lc '...'"` BUT wsl wraps stdout as UTF-16 (grep sees "Binary file matches"; iconv/strings roundtrip unreliable)
- WSL repo `/home/marsh/dev/hd-instrument` cannot be scp'd into from the cmd landing
- **This almost certainly explains GPU idle ~2000 min** (event-bus IDLE [GPU])

**Likely cause:** Remote rebooted with default OpenSSH shell reset to cmd.exe, OR WSL distro's default-shell registration was lost.

**Exp-Dev correctly DID NOT change remote config** (touching shared infrastructure without authorization; 7th-rule discipline maintained). This is a USER-only fix.

## DECISION 75a -- USER ASK (only USER can resolve)

**Required USER action (one of):**
1. SSH to remote 100.91.12.42 and reset OpenSSH `DefaultShell` to point to WSL bash (Registry edit on Windows side: `HKLM\SOFTWARE\OpenSSH\DefaultShell` -> WSL bash path)
2. OR re-establish prior sync path (Windows-side repo mirror OR WSL-default-shell login restoration)
3. OR confirm a different intended access pattern (Director can update sessions accordingly)

Until USER fix: all bge-dependent work is BLOCKED cross-session. Phase 3 + Phase 4 continue on laptop-local work.

## DECISION 75b -- What CONTINUES (laptop-local; not bge-dependent)

```
ACTIVE LAPTOP-LOCAL WORK (not blocked):

Testbed (Integrator):
  Iter 2 atomic ratify of 7 PLAUSIBLE edges (per DECISION 74a)
  ~15 min; substrate-state-mutation; no bge required
  Tag: PHASE3_ITER2_RATIFY iter2_confidence=PLAUSIBLE

Skunkworks (Auditor):
  Phase 4a self-model authoring BATCH 2+ toward 100+ HARD-PASS
  Laptop-local; description + textbook-derived; no bge
  ~3-4 hrs more to deliver

Exp-Dev (Prover):
  M4d on laptop-local adjacency (works with cached bge embeddings)
  Iter 3 generator design / candidate-target inventory (substrate-internal counting)
  Generator hygiene + future Iter 3 prep
```

Substrate progress is NOT halted. Most of the active workstreams are laptop-local.

## DECISION 75c -- What DEFERS (needs remote bge)

```
DEFERRED until USER fix:

73g 13-edge STRICT-tier dilution pre-check (cell BUILT + self-tested + ready)
  - extends 70c/72b R1; M4d on base+6+7 STRICT-tier
  - HARD-PASS d13 >= -0.01 vs base AND vs 6 -> confirms STRICT-tier dilution-safe at 13
  - Needs remote bge for the M4d candidate retrieval
  - Cell: `experiments/exp_substrate_73g_m4d_13edge_strict_tier_dilution_check_cpu_v1.py`
  - Ready to run when remote restored: 
    `wsl bash -lc 'cd /home/marsh/dev/hd-instrument && HF_HUB_OFFLINE=1 ... python ...'`
  
Iter 3 P1-bge generator (needs remote bge for top-K candidate generation)
  - Postpone Iter 3 dispatch until bge re-accessible
  - OR Iter 3 design: try LAPTOP-ONLY generator using cached embeddings only (no fresh bge encode)
  - The cached bge embeddings cover existing 26286 atoms; Iter 1 generator used these
  - Exp-Dev confirm whether laptop-only P1-bge works without remote bge re-encode
  
Iter 2 post-ratify M4d F1 measurement on full benchmark
  - Currently: laptop-local M4d on q54-q65 + 56d works (cached embeddings)
  - But: if Iter 2 ratify ADDS new atoms (it doesn't; only edges), no re-encode needed
  - 7 PLAUSIBLE Iter 2 edges connect EXISTING atoms; no new bge encode required
  - So Iter 2 post-ratify F1 likely CAN run on laptop (Exp-Dev confirm)
  
49b real-groups re-run (per DECISION 65c; depends on remote bge re-encode of 5510 relabeled atoms)
  DEFER until USER fix
```

## DECISION 75d -- Test whether laptop-only P1-bge can support Iter 3

Open question (Exp-Dev confirm with Director when ready):
- Iter 1 P1-bge generator: did it use remote bge OR laptop-cached embeddings?
- If laptop-cached: Iter 3 can proceed without remote (test on NEW isolated targets per DECISION 74c)
- If remote: Iter 3 dispatch deferred until USER fix

**If laptop-only works:** Iter 3 dispatches normally; the 1 NEW STRICT decisive test (DECISION 74c) proceeds.

**If remote-only:** Iter 3 deferred; Phase 4a (Skunkworks self-model authoring) becomes the primary work until USER fix.

## DECISION 75e -- Substrate-product positioning (no impact)

The infrastructure issue does NOT impact the 12-claim positioning. All measured claims (1-4, 6-12 except 5) are based on completed measurements; no new claim hinges on Iter 3 specifically (Iter 3 would mature Claim 10's STRICT-discovery question, which is currently scoped as OPEN).

**Substrate state UNCHANGED:** 26286 atoms / 5266 relations / 7 pending Iter 2 PLAUSIBLE (ratify in flight; laptop-local) / 20 pending operator signatures (Phase 4a BATCH 1).

## DECISION 75f -- Operational risk acknowledgment

**Substrate-product positioning operational addition (lower-priority; for cycle close):**
"The substrate's autonomous loop (Phase 3 CO-EVOLVE-1) depends on a learned bge embedding service for the P1-bge generator (the broad-heuristic proposer in the generate-verify pipeline). bge service is REMOTE; remote-access requires stable SSH shell configuration. Operational risk: remote shell config drift can block bge-dependent work for unbounded time. Substrate's laptop-local work (Skunkworks self-model authoring; Testbed ratify; M4d on cached embeddings) continues independently. Mitigation: maintain SSH access redundancy (document the expected shell config; alert on default-shell drift)."

This is an operational risk; not a substrate-product flaw. Logged.

## Session tally

74 cumulative decisions. **53 honest signals.** Most of the program continues laptop-local; bge-dependent work defers pending USER fix. Substrate-product positioning unimpacted.

## Cross-references

- Exp-Dev infra blocker: this commit responds
- DECISION 74 (Iter 2 vet HARD-PASS but 0 STRICT): commit `3c07b1a6`
- DECISION 72 + 73 (Iter 2 dispatch + COMPOUNDING): commits `49778cc8` + `e2e25e62`

## Safety / invariants

- ASCII only
- 7th-rule discipline: Exp-Dev did NOT modify shared remote config
- 11th rule preserved: laptop-local work is substrate-internal; no LLM
- 18th rule: substrate refuses to claim what it cannot measure (Iter 3 deferred IF remote-dependent)
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 preserved (no substrate state mutation in this DECISION)

---

**USER:** USER ASK present at DECISION 75a -- reset remote SSH DefaultShell to WSL bash OR equivalent fix. Until then, bge-dependent work is blocked. Most active work continues laptop-local.

**Testbed (Integrator):** proceed Iter 2 atomic ratify per DECISION 74a (laptop-local; not blocked).

**Skunkworks (Auditor):** continue Phase 4a self-model authoring (laptop-local; not blocked).

**Exp-Dev (Prover):** confirm whether Iter 3 P1-bge can run laptop-only (DECISION 75d open question). If yes, dispatch Iter 3 per DECISION 74c. If no, defer + flag for USER post-fix. Also: 73g cell stays built + ready; runs immediately on remote restore.

Tag: USER_FACING_REMOTE_BGE_INFRA_BLOCKER_GPU_IDLE_2000MIN_LAPTOP_WORK_CONTINUES_BGE_WORK_DEFERS -- Research (Director)
