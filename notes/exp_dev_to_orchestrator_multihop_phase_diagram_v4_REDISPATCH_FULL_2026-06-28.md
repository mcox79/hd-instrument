# exp_dev -> orchestrator: multihop_phase_diagram_v4 REDISPATCH AS FULL

**Filed-by:** exp_dev (hdi_exp_dev sub-agent) 2026-06-28T21:15Z
**Anchor (per seed):** `substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_{7,13,19}`
**Routing target:** overnight_queue (GPU; torch+CUDA mandatory per Fix #24)
**Push status:** harness-DENIED to exp_dev; ORCHESTRATOR REQUIRED to dispatch
**Trigger:** Skunkworks audit caught the existing 3 metrics.json as selftest-only (668 bytes; module-import gate pollution). Need actual FULL phase-grid runs.

---

## TL;DR

Three sibling cells (seed_7 / seed_13 / seed_19) READY for FULL dispatch to overnight_queue. Cell + prereg on origin/main (commits 487c3b0b + f2b50f8a). Selftest metrics-path pollution BUG ROOT-CAUSED + FIXED in f2b50f8a (write to sibling `_selftest` dir; FULL anchor dir reserved). Stale selftest dirs archived to `data/_archived_selftest_only_multihop_v4_2026-06-28/`.

**Dispatch ask (run sequentially or queue all 3 at once -- runner serialises):**

```bash
cd /d/AI/hd-instrument
for SEED in 7 13 19; do
  bash tools/orchestrator/queue_add.sh \
    overnight_queue \
    substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_${SEED} \
    experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_${SEED}.py \
    preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v4.md \
    7200
done
```

**Per-seed timeout = 7200s (2h).** Prereg estimated 10-30 min wall per seed FULL; 7200s = 4-12x margin. Stays BELOW PROT-021 14400s threshold so no `_seed_checkpoint` import needed (cell does not import it; refactor would be a separate cell).

---

## Bug root-caused this turn (Skunkworks "halt before completing" message)

**Symptom:** seed_7 metrics.json kept appearing as `run_mode=self_test`, 664 bytes, verdict_msg "SELFTEST_PASS module-import" -- even after archiving.

**Root cause:** queue_add.py's GATE (lines 702-709) runs the cell with `--self-test` AND `HDLAB_EXP_NAME=<full_anchor>` to verify the script is queueable. The cell's old code (line 842, pre-fix) wrote to `data/exp_{HDLAB_EXP_NAME}/metrics.json` regardless of mode, so the GATE'S selftest output landed in the FULL anchor's metrics path. Downstream auditors mistook this for "the cell ran and produced selftest results."

**Compounding factor:** The cells were NEVER actually queued to any of overnight_queue / remote_cpu_queue / local_cpu_queue (all three queue.json files contain ZERO multihop_phase_diagram entries). So the "landings" were 100% gate-side pollution, no real dispatches occurred.

**Fix (commit f2b50f8a, this turn):**
```python
if self_test:
    out_dir = REPO / "data" / ("exp_" + env_name + "_selftest")
else:
    out_dir = REPO / "data" / ("exp_" + env_name)
```
+ `anchor_name` field in selftest payload now suffixed `_selftest` so the path-mismatch can never recur as a misread.

**Verified:**
- self-test now writes to `data/exp_<full_anchor>_selftest/metrics.json` (sibling dir)
- FULL anchor dir (`data/exp_<full_anchor>/`) stays EMPTY until a real FULL run lands

This fix follows feedback_metrics_path_disambiguation_selftest_smoke_full_2026-06-27 (USER + Skunkworks) which called out the same pattern as a 4-day silent drift root cause across the fleet.

## What the cell does (pre-reg recap)

12-point phase diagram: `effective_V_C in {200, 800, 4000, 16000}` x `depth in {5, 10, 15}` x `N_chains=200 fixed` x `N_PARTITIONS=4 fixed` x `N_DIM=8192`. 3 arms per point:
1. **SUBSTRATE_BASELINE**: per-step cleanup over FULL V_C codebook (no oracle)
2. **PARTITION_ORACLE**: ground-truth target-partition; per-step cleanup over `effective_V_C` codewords (the load-bearing arm)
3. **RANDOM_PARTITION**: random partition assignment; sanity floor

Verdict tiers (on PART_ORACLE arm):
- CHAIN_GRADE_PHASE_MAP_COMPLETE: >= 50% (6/12) points HARD_PASS + cliffs identified
- PARTIAL_PHASE_MAP_SHALLOW: 30-49%
- REGIME_BOUNDS_NARROW: 10-29%
- PHASE_FRONTIER_COLLAPSED: <10%
- SANITY_BREACH: SAT_CORNER (5,200) PART_ORACLE<0.90 OR DISCRIM at any corner fails

## Pre-flight verification (all PASS local)

- [x] `--self-test` runs end-to-end: arms_distinct=True (sub=47f862d5cb82d514 part=c95db5c773146578 rand=44bf935c8afc9059); META_RULE_J ok (CPU NaN + reason captured); p_step model 0.99/0.98/0.95 matches v3-back-solved bands
- [x] Cell + prereg on origin/main: 487c3b0b (cell + prereg), f2b50f8a (selftest path fix)
- [x] PROT-018 N-suffix: anchor has `_seed_<N>` not `_n<N>`; not triggered
- [x] PROT-019 timeout floor: not triggered (no `_n<>=4096>` suffix)
- [x] PROT-020 GPU routing: cell imports torch (line 58); torch.cuda branch active; will use GPU
- [x] PROT-021 long-timeout checkpoint: timeout=7200s < 14400s; rule does not apply (cell does NOT import `_seed_checkpoint` -- if extending timeout above 4h in future, must add)
- [x] No PROT-022 KB_REFERENT declarations (cell is self-contained; no external KB ingest)
- [x] METRICS-PATH-DISAMBIGUATION verified: selftest now writes to `_selftest` sibling
- [x] CARDINALITY_OK: EXPECTED_N_FULL=12 hard-coded; HARD_FAIL on cardinality breach
- [x] ARMS-MUST-DIFFER (META_RULE_AF): SHA-256 per arm at every point; HARD_FAIL on collision
- [x] NO_SILENT_EXCEPT (META_RULE_AG): per-point try-log-reraise; gpu_util NaN-on-failure
- [x] Fix #24 GPU mandate guard: cell HARD_FAILs FULL on CPU (writes FIX24_GUARD sentinel)
- [x] Stale selftest metrics archived to `data/_archived_selftest_only_multihop_v4_2026-06-28/seed_{7,13,19}_metrics.json.selftest_archived_*`
- [x] FULL anchor dirs (`data/exp_<full_anchor>/`) confirmed EMPTY ready for real FULL landings

## Runtime estimate

Per-seed FULL = 12 points x 3 arms x N_chains=200 x N_DIM=8192:
- Hebbian ingest per eff_V_C: N_DIM x N_DIM matmul batched chunks of N_chains*max_depth=3000 triples
- Per-point per-arm: 200 chains x depth x (E @ state matmul; size eff_V_C x N_DIM)
- E codebook at eff_V_C=16000: V_C=64000; E=64000*8192*4 bytes = 2.1GB -> fits 6GB GPU budget
- W matrix: 8192*8192*4 = 256MB
- GPU estimate (per spec): 10-30 min/seed; safe budget 2h

3 seeds x ~30 min = ~1.5h total wall. Will fit comfortably overnight.

## Sequencing

**No smoke pre-dispatch this round.** Justification:
- Self-test (mechanism check) PASSES on laptop CPU; verified above
- Laptop CPU cannot run smoke at N=8192 V_C=64000 in any reasonable time
- The PROPER smoke would be on remote GPU, but smoke + full are SAME runtime envelope at this scale (4 corners vs 12 points = 33% of work)
- queue_add.sh on remote already passes `--skip-smoke` for overnight_queue (gate-time smoke would fail Fix #24 GPU gate anyway since gate runs on dispatch host)

If Orchestrator prefers smoke-first: dispatch seed_7 alone first; observe verdict; then dispatch 13/19. Otherwise queue all 3 in one shot.

## Independence check (no collision with in-flight)

- Lock-in v2 (hdi_exp_dev) -- DIFFERENT cell; no shared files
- 2026-06-27 HF backlog (hdi_skunkworks) -- audit-only; no dispatch overlap
- Capacity_multibank v2 (GPU last seed running) -- DIFFERENT anchor; overnight_queue runner will serialise per slot anyway

## Post-ship asks (back to me, exp_dev)

1. Confirm `queue_add.sh` post-ship VERIFIED line for each seed (entry in remote `data/overnight_queue/queue.json`)
2. When metrics land at `data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_{7,13,19}/metrics.json` with `run_mode=full` and 12-element phase_map, notify research-lead via SendMessage so Skunkworks can do landed-VET
3. If any seed sentinel-writes FIX24_GUARD (CPU detected on FULL): escalate -- runner routing broken

## Honest residual uncertainty

- p_step extrapolation to eff_V_C=4000 / 16000 is from v3 data at part_size in {10, 800} only. Eff_V_C in {4000, 16000} are PREDICTIONS, not back-solved. If smoke/full shows PART_ORACLE >> 0.95 at all 12 corners, the discriminator dimension is wrong and bands need re-derivation (v4 -> v5)
- SUBSTRATE_BASELINE arm at V_C=64000 may collapse below RANDOM_PARTITION; that's expected (no oracle benefit; V_C >> W's resolution at N=8192). META_AM check is PART_ORACLE >= RANDOM_PART, not SUB_BASELINE >= RANDOM_PART
- Promotion targets: CHAIN_GRADE phase map for stage-3 substrate-native composition; MIDDLE_BAND if cliffs not cleanly identified; HARD_FAIL paths well-defined per prereg

---

**State after this routing note:**
- Cell + prereg shipped (487c3b0b + f2b50f8a on origin/main)
- Stale selftest dirs archived; FULL anchor dirs empty
- Selftest metrics-path bug root-caused + fixed (the actual dispatch-wiring issue Skunkworks halted me on)
- Awaiting Orchestrator dispatch to overnight_queue (3 seeds x 7200s timeout each)

exp_dev (Opus 4.7 1M); commit f2b50f8a (selftest-path fix) on top of 487c3b0b (cell + prereg).
