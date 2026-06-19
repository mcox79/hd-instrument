# Exp-Dev POST-COMPACTION BRIEF (2026-06-06 ~09:00) -- READ FIRST after context reset

Role: Exp-Dev (4-session arch). Build/derive experiment cells, smoke-gate, queue_add to remote runners, report verdicts.
Do NOT interpret verdicts beyond completion; metrics.json = completion only.

## THE PROCESS (changed 2026-06-06 -- this is how I operate now)
- **Research owns `notes/PRIORITY_QUEUE_LIVE.md`** = the SINGLE source of truth for experiment priority. I PULL FROM THE
  TOP, build (if needed) -> smoke-gate -> queue -> report verdict -> Research crosses off + adds follow-ons.
- **GENUINE-NEW-ONLY. NO PADDING.** Re-running completed fixed-seed cells = byte-identical metrics = BANNED (it caused
  the orchestrator's queue-republish-anomaly). Brief lane idle is CORRECT when the SSOT top is gated/multi-day.
- **Verdict reporting:** notes/exp_dev_to_research_<anchor>_<verdict>_2026-06-06.md (report HP AND FAIL -- honest
  negatives are valuable, e.g. norm-gate HARD_FAIL blocked a bad infra lever). Research auto-dispatches 2x rescue on
  genuine MIDDLE/HF.

## LANE BOUNDARIES (load-bearing -- user enforced)
- Exp-Dev: cell build, dispatch, queue.json MECHANICS (purge re-runs / reclaim stale entries via tools/orchestrator/
  purge_pending_reruns.py + reclaim2.py).
- Orchestrator: ALL runner_v2_prod lifecycle (start/stop/kill/restart/schtask). **I NEVER kill/restart runners.**
- exp-cell SUBPROCESS kills: ONLY with explicit per-instance user authorization.

## RUNNER POOL (do NOT re-misdiagnose)
4 python.exe = 2 runners in the standard Windows VENV LAUNCHER->CHILD pattern (venv launcher re-execs a system-python
child that inherits .venv site-packages -> deps WORK: gmpy2/sklearn/faiss/torch all import). This is NOT duplicate/broken
runners -- my earlier "duplicate runner" + "system shim broken" diagnoses were WRONG (orchestrator clarified). Healthy.

## METRIC HYGIENE (recurring trap -- 5x burned)
- Capacity/codebook/sparse cells: use AUTO-ASSOCIATIVE HOPFIELD (W=P^T P zero-diagonal; flip-corrupted cue ~0.05;
  exact-recovery). NON-saturating.
- For SPARSE-PATTERN coding (k-of-N active): SINGLE-step retrieval (sign(W@cue) once); iterating fills the sparse zeros
  with +/-1 -> dense divergence -> false 0. Exact-recovery on NON-ZERO positions.
- Do NOT use heteroassociative-to-small-value-codebook (N_VAL=64) + clean cue -- it SATURATES (signal always wins ->
  both arms hit grid-max -> false ratio 1.0). This killed early T1-6 / capacity / hadamard / norm attempts.
- W-free Hopfield (compute via P matmuls, no NxN W) for N>=16384.

## QUEUE GOTCHAS
- queue_add.sh: prereg file MUST EXIST first (preregs/2026-06-06_<name>.md) else "FAIL: prereg not found" (silently
  blocked a whole GPU lane once).
- PROT-018: anchor `_n<N>` binds a SINGLE fixed N (script must have matching N constant). N-SWEEP cells must NOT use
  _nN in the name (use descriptive e.g. _sweep_v1).
- PROT-019 timeout floor: _n>=8192 -> --timeout >= 21600s; _n>=4096 -> >= 14400s.
- queue_add CANNOT pass --args (forced-mode copy scripts if needed).
- ASCII-only, write_metrics(), --self-test early-exit, smoke-gate before queue, atomic commit+push.

## TODAY'S WINS (genuine; reported to Research)
- Matthiessen HP (codebook-collision = dominant noise; 24th flagship)
- K-hop reasoning HP (perfect to K=5; 25th)
- ETF/Hadamard codebook init HP (8.02x capacity vs random; 26th -- confirms Matthiessen; -> Phase-4a default codebook init)
- Slot 3 sparse-PATTERN-coding HP (~12x capacity; capacity rescue for two-regime alpha)
- Slot 6 embedding-norm-gate HARD_FAIL (genuine: norm correlates w/ concept -> drops 58% concepts; BLOCKED as speedup lever)
- Overnight: KF-1 hallucination AUC 0.999, real-encoder transfer 18/18, continual-KV 99.8% (21st/22nd/...)

## QUEUE STATE (at brief time)
- CPU: Slot 3 (sparse-alpha-sweep), Slot 6 (norm-gate, running), Slot 7 (k-hop N16384 K10), T2-9 (k4-XOR-sweep) queued/running.
- GPU: IDLE -> next genuine GPU cell = SSOT Slot 9 `substrate_etf_hadamard_phase4a_infra_eval_v1` (ETF Hadamard codebook
  on MiniLM/real-encoder substrate; HP >= 4x vs random init). GPU (MiniLM). BUILD THIS to get GPU going.

## NEXT SSOT CELLS (pull top-down; skip gated Llama-weights/vLLM/faiss + multi-day cubic-tensor Slot 1)
Slot 8 ETF+sparse compound (CPU; expect ~100x compound), Slot 9 ETF-on-MiniLM (GPU), Slot 10 ETF n-sweep capacity
(Phase-3 gate), Slot 11 u2-codebook stacked-defense, Slot 12 per-cluster-stratified-extraction (norm-gate rescue),
Slot 13 concept-uniform-random-extraction, Tier-2 T2-10/T2-11/T2-2/T2-8 etc. CLOUD-1 (7B vs 70B) = user-auth gated.
2 sanctioned varied-seed CI re-runs: capacity_scaling_sweep_xl seeds=10, hp12_v2_crypto seeds=10.

## AUTONOMY
- Monitor (persistent, task bi2simbjy): git fetch+diff every 75s -> event on any new note (near-real-time note detection).
- ScheduleWakeup keeper (20min): pull next SSOT cell, build, queue, report; check depth; NO padding.
