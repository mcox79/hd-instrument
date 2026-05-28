# Strategy decisions — 2026-05-28

## v258 -> v259 BATCHED 2-VERDICT @ 00:48 (saad_solla_v12_n8192_5seed TIMEOUT + pb3_extended_v2_n4096 SCRIPT_BUG_CUDA_GENERATOR_MISMATCH; both INFRASTRUCTURE — NO cap_map state move; 2 exp_dev routings filed)

**Trigger.** Two GPU verdicts landed in one runner cycle (00:44:51 and 00:44:54). Dispatch context framed these as candidate honest 5-seed/β-extension failures that would back off v252 Saad-Solla LIFT or v251 PB3 cap_map state. Per v256 audit lesson [[feedback-trust-queue.json-wall_s]] verdict_handler pulled queue.json wall_s + runner.log forensics directly via SSH to disambiguate.

### Verdict 1: saad_solla_v12_n8192_5seed FAILED — TIMEOUT (pattern d)

**Evidence (definitive from queue.json + runner.log):**
- queue.json: `status: failed`, `error: "timeout"`, `wall_s: 1800.0037`, `timeout_s: 1800`, `started: 00:14:51`, `ended: 00:44:51` — wall_s ≡ timeout_s to 4 decimal places = hard timeout kill.
- runner.log forensics: self-test PASSED at N=8192 (`OOM=5.37e+08, smoke ret=0.6277, replay=DISABLED`); production run completed seed=7 cells f=0.00 (495s), f=0.15 (1018s), f=0.50 (1540s); cut off mid-f=1.0 at 1800s before completing seed=7's last cell, let alone seeds {11,17,23,29} of the 5-seed envelope.
- r2=0.000 max_dev=0.000 reported per-cell are PRE-AGGREGATION sentinels (the actual computation runs at end-of-seed; values stamped at line emission, not real metrics). Not evidence of degenerate physics.

**Step 0 honest re-read:** dispatch context offered 4 candidate failure modes (a) honest 5-seed phase-prediction fail, (b) CUDA OOM 8GB-VRAM-binding, (c) script-output-path bug, (d) timeout. Evidence DEFINITIVE for (d). Reject (a) — no seed even completed all f-cells, so honest physics cannot be claimed either direction. Reject (b) — self-test confirmed OOM=5.37e+08 well under 8GB at N=8192 + seed=7's three completed cells executed cleanly without CUDA error. Reject (c) — runner-log header confirms correct exp_saad_solla_v12_n8192_5seed.py script path; cells emit per-cell lines under expected name; v10 path-bug class (78th catch) demonstrably resolved by 7d39e13 patch and v11/v12 inherit the fix.

**Honest reading:** Saad-Solla v12 envelope-extension probe (2→5 seed at N=8192) HIT TIMEOUT BUDGET. Per-cell wall scaling shows ~500s per (seed, f-cell); 5 seeds × 3 f-cells = 15 cells × 500s = 7500s required; 1800s allotted is ~24% of need. The TIMEOUT is an INSTRUMENTATION error (wrong timeout_s setting at queue-add time), not a substrate signal.

**Decision (1): v258 -> v259 ANNOTATION-ONLY on Saad-Solla row. NO REVERT.** Saad-Solla LEADING ✅ UNCHANGED. v252 N=8192 2-seed FULL HARD_PASS evidence STANDS. Annotation appended: "v259 envelope-extension v12 (2->5 seed) timed out at 1800s after completing seed=7 cells f∈{0.00, 0.15, 0.50} (per-cell wall ~500s; ~7500s budget required); INFRASTRUCTURE timeout NOT honest 5-seed physics failure; resheduled v13 with timeout_s=14400 OR N=4096 5-seed substitute pending exp_dev recommendation; envelope-extension gap remains OPEN as defense-in-depth (no urgency per v252 framing)".

**Decision (2): Rescue sketches cheapest-first (per [[feedback-rescue-sketch-first-sequencing]] + [[feedback-rehabilitation-after-rejection]] — sub-objective rescue chain, NOT row-closure rescues):**

(a) **PRIMARY / SUBSUMPTION 0-cost** — re-frame v12 timeout as "v252 2-seed HARD_PASS already constitutes Saad-Solla LARGE-N closure for substrate-product purposes; 5-seed envelope-extension is defense-in-depth not load-bearing"; no further work needed for cap_map state. Applied; 0-cost.

(b) **CHEAPEST INFRA ~5min exp_dev** — saad_solla_v13_n4096_5seed (reduce N from 8192 to 4096; ~4x wall savings → ~1875s fits in 1800s budget). Tests phase prediction at corroborating but lower-N regime; if HARD_PASS, multi-seed evidence at N=4096 + 2-seed evidence at N=8192 = scope-spanning corroboration. Trade-off: lower-N gives less direct v252 envelope-extension; mitigates by spanning.

(c) **MEDIUM INFRA ~10min exp_dev** — saad_solla_v13_n8192_5seed_extended_timeout (same N=8192 5-seed but timeout_s=14400 = 4hr ceiling, well above estimated 7500s). Pre-PROT-018-style: `--timeout` flag explicit per [[feedback-per-experiment-timeout-required]]; estimated wall_s formula `1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)` = 1.5 × 500s × 1 × (5/2) = 1875s per f-cell × 3 cells = ~5625s → budget 14400s = 2.5x headroom. Direct envelope-extension at N=8192.

(d) **MEDIUM ~15min** — saad_solla_v13_n8192_3seed (drop seed count to 3 = {7, 17, 23}; ~4500s fits 5400s timeout). Compromise between coverage and budget.

(e) **LAST RESORT ~20min** — split into 5 separate single-seed jobs each at 2000s timeout; ship as a batch; aggregate offline. Highest robustness but most queue traffic; deferred.

**Sequenced for filing:** (b) cheapest-fastest IF user prefers scope-span; (c) most-faithful-to-original-intent IF user prefers direct N=8192 envelope-extension. Filing both as alternatives in routing note; exp_dev picks based on current GPU queue depth.

### Verdict 2: pb3_extended_v2_n4096 FAILED — SCRIPT_BUG_CUDA_GENERATOR_MISMATCH (pattern c)

**Evidence (definitive from queue.json + runner.log):**
- queue.json: `status: failed`, `exit_code: 1`, `wall_s: 3.13`, `started: 00:44:51`, `ended: 00:44:54` — sub-4-second wall = pure script-launch crash, NOT a physics failure and NOT a timeout.
- runner.log full traceback:
  ```
  File "C:\dev\hd-instrument\experiments\exp_pb3_extended_v2_n4096.py", line 137, in run_one_seed
    byte_atoms = pa.make_bsc_atoms(VOCAB, N_use, gen).to(device)
  File "C:\dev\hd-instrument\experiments\exp_wave14b_cl_phase_a.py", line 78, in make_bsc_atoms
    raw = torch.rand((k, n), generator=gen)
  RuntimeError: Expected a 'cpu' device type for generator but found 'cuda'
  ```
- Root cause: `pa.make_bsc_atoms` from `exp_wave14b_cl_phase_a.py:78` calls `torch.rand((k, n), generator=gen)` WITHOUT a `device=` parameter — the generator's device must match the tensor's default device. Caller in v2 script created `gen = torch.Generator(device='cuda')` then passed it to a CPU-default `torch.rand` call.

**Step 0 honest re-read:** dispatch context offered (a) honest critical-slowing β-extension fail, (b) OOM at N=4096 on memory-intensive perturbation grid, (c)/(d) infra. Evidence DEFINITIVE for (c) script-bug. Reject (a) — no β-cell even ran to completion (crash on first call to `make_bsc_atoms` before any physics computation). Reject (b) — wall_s=3.13s and traceback is RuntimeError on generator-device mismatch, not torch.OutOfMemoryError.

**Honest reading:** pb3_extended_v2 has a SCRIPT BUG. The fix is mechanical — either (i) modify caller to use `gen = torch.Generator(device='cpu')` (since `make_bsc_atoms` operates on CPU then `.to(device)`s), or (ii) modify `make_bsc_atoms` signature to accept and respect a device-matched generator. PB3 v1 (v251 HARD_PASS) used the wave14b helper without this bug because v1 either used a CPU generator throughout or used a different code path; v2 inherited the bug when extending β-sweep grid.

**Decision (3): v259 ANNOTATION-ONLY on PB3 row. NO REVERT.** PB3 critical-slowing-down row UNCHANGED. v251 HARD_PASS evidence STANDS. Annotation appended: "v259 PB3 β-extension v2 SCRIPT_BUG_CUDA_GENERATOR_MISMATCH (RuntimeError at exp_wave14b_cl_phase_a.py:78 — `torch.rand` called without `device=` while generator is CUDA); pure infrastructure failure 3.13s wall NOT physics; fix is 1-line caller change (use `Generator(device='cpu')`) or 1-line helper signature update; pb3_extended_v3 reship after fix; β∈{4, 8} bug-free baseline UNCHANGED at v251".

**Decision (4): Rescue sketches cheapest-first:**

(a) **PRIMARY / SUBSUMPTION 0-cost** — re-frame v2 crash as "v251 PB3 critical-slowing-down β=4,8 HARD_PASS evidence stands; β-extension is incremental envelope-fill not load-bearing for cap_map state"; no urgency. Applied; 0-cost.

(b) **CHEAPEST FIX ~5min exp_dev** — edit exp_pb3_extended_v2_n4096.py: replace `gen = torch.Generator(device='cuda')` with `gen = torch.Generator(device='cpu')` (since `make_bsc_atoms` is CPU-bound then `.to(device)`s); rename to v3; reship. Avoids touching shared helper.

(c) **MEDIUM FIX ~10min exp_dev** — update `pa.make_bsc_atoms` in `exp_wave14b_cl_phase_a.py:78` to add `device=gen.device` parameter to `torch.rand` call. Cleaner: any future caller can pass either CPU or CUDA generator without mismatch. BUT touches a shared helper used by ≥5 other experiments; risk of regression — needs broader self-test sweep.

(d) **ALTERNATIVE ~5min** — wrap the offending line with explicit CPU generator local: `cpu_gen = torch.Generator(device='cpu'); cpu_gen.manual_seed(int(gen.initial_seed())); raw = torch.rand((k, n), generator=cpu_gen)`. Keeps deterministic RNG but isolates the CPU-side draw.

(e) **NOT-RECOMMENDED** — bypass `make_bsc_atoms` entirely and inline the BSC atom construction in pb3_extended_v3. Code duplication; rejected.

**Sequenced for filing:** (b) is cheapest, lowest-risk, and isolates the fix to the v2-specific script — that's the recommended path. (c) preferred if exp_dev intends a broader helper-cleanup follow-on. Both filed in routing note.

### Joint decisions

**Decision (5): Cap_map state — ANNOTATION-ONLY on both rows; NO portfolio/reliability move.**
- Saad-Solla LEADING ✅ row: annotation only (timeout, not honest fail).
- PB3 critical-slowing-down 🟢 row (per v251): annotation only (script bug, not honest fail).
- Portfolio count: UNCHANGED (14 + 23 per v258).
- Framework reliability: UNCHANGED (general 71-83% / specific 53-65% / product-feature 78-90% per v258).
- Non-eq stat-mech class: UNCHANGED (63-73% per v253; PB3 not in non-eq class anyway).
- Cumulative HONEST catches: 100 (v258) — UNCHANGED.
- Cumulative LABEL-VS-HONEST catches: 101 (v258) — UNCHANGED (these verdicts were truthfully labeled "failed"; the verdict_msg null/error fields ACCURATELY reflected infra-failure status; no label-vs-honest catch warranted).

**Decision (6): exp_dev routing files — TWO filed.**
- `notes/strategy_request_to_exp_dev_v259_saad_solla_v13_reship_2026-05-28.md` — sketches (b) and (c); exp_dev picks based on queue depth.
- `notes/strategy_request_to_exp_dev_v259_pb3_v3_genfix_2026-05-28.md` — sketches (b) and (c); recommend (b) for isolation, (c) flagged for future helper-cleanup.

**Decision (7): Queue-refill — PAUSE FLAG ABSENT; overnight_queue has 1 running (axis2_codebook_density_v1_n4096); no auto-refill needed.** Per [[feedback-no-padding-experiments]] — queue >= 1 satisfied; do NOT pad with marginal anchors just to backfill. The two exp_dev routings filed above are PROPER ANCHORED work (rescue follow-ons for v258 capabilities), not padding. exp_dev will pick them up on next dispatch cycle.

**Decision (8): NO exp_dev dispatch from this handler.** Routing files are the proper artifact; orchestrator's next routing_handler cycle will pick them up. No skill invocation needed here.

### PROT compliance (v259)

- PROT-004/006: 0 capability row closures; both anchored capabilities (Saad-Solla, PB3) retain prior FULL evidence; rescue sketches filed cheapest-first per [[feedback-rescue-sketch-first-sequencing]] but at SUB-OBJECTIVE level not row-level closure.
- PROT-007: history.md absent (consistent with v228+).
- PROT-008: No demotion; annotation-only on 2 rows.
- PROT-009: cap_map.md + strategy_decisions_2026-05-28.md + visibility_decisions_2026-05-28.md staged atomically (single commit, 3 files); 170th PROT-009 paired commit.
- PROT-018: anchor names contain `_n<N>` suffix (`_n8192_5seed` and `_n4096`) — BINDING contract honored; both v13/v3 reship anchor names will also include `_n<N>` suffix.
- [[feedback-verdict-msg-honest-reread]]: 102nd observation; BOTH labels HONEST (failed=true for both); no label-vs-honest catch (counter UNCHANGED at 101).
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-trust-queue.json-wall_s]]: v256 audit lesson APPLIED — queue.json wall_s + runner.log forensics dispositive in both cases (1800.0s ≡ timeout_s for v12; 3.13s wall + traceback for pb3 v2).
- [[feedback-dispatch-context-trust]]: dispatch context claimed v252 was the Saad-Solla precedent and v251 the PB3 precedent — VERIFIED against cap_map line 1869 and v251 PB3 entry; dispatch context accurate on those references.

**Per [[feedback-cap-map-update-protocol]]:** atomic commit of cap_map.md (v258 → v259 annotation line) + strategy_decisions_2026-05-28.md (this entry) + visibility_decisions_2026-05-28.md (one-line) + 2 strategy_request routing files. Commit message: `Cap map: v258 -> v259 (BATCHED 2-VERDICT INFRASTRUCTURE: saad_solla_v12 TIMEOUT 1800s + pb3_extended_v2 CUDA_GENERATOR_MISMATCH 3.13s; ANNOTATION-ONLY both rows; no honest physics signal; 2 exp_dev routings filed; portfolio 14+23 UNCHANGED; 170th PROT-009 paired commit)`.

Net effect v259: 0 CLOSURES + 0 LIFTS + 0 LABEL-VS-HONEST CATCH + 2 INFRASTRUCTURE-FAILURES correctly diagnosed via queue.json wall_s + runner.log; portfolio + reliability UNCHANGED; 2 exp_dev routings filed; rescue sketches sequenced cheapest-first; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch.
