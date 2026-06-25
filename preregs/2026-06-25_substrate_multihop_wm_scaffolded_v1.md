# Pre-registration: substrate_multihop_wm_scaffolded_v1

**Date:** 2026-06-25
**Anchor:** substrate_multihop_wm_scaffolded_v1
**Queue:** local_cpu_queue
**N:** 8192, **Seeds:** [7, 17, 23], **max_depth:** 10

## Why this cell exists

Research deep-dive (`notes/research_deep_dive_partial_and_open_capabilities_intuitive_2026-06-25.md`)
identified the substrate has all the parts for multi-hop reasoning but never
composed them via PFC + hippocampus:

- Hippocampus analog: Hebbian-bound W (chain-grade primitive; pointer_chain v2
  baseline reproduced beta-sweep regime rail 0.65).
- PFC analog: HRR-slot working memory (`exp_working_memory_hrr_slots_PRODUCTION_v1`
  HARD_PASS at K=32 sigma=1.0; recall 1.000 at sigma=0..2.0 for K<=64).

Pointer-chain v2 HARD_FAIL: 5hop=0.122, 10hop=0.035. Root cause: cleanup output
of step n is fed DIRECTLY into step n+1 query; error compounds geometrically.

This cell's mechanism: each hop reads a CLEAN scaffold-held intermediate.
Per hop, the cleaned codebook atom E[next_idx] is written through the WM slot;
the next hop's query uses the cleaned atom, not the noisy chain state. The
brain does this; substrate has never been asked to.

## Scientific question

Does WM-scaffolded multi-hop reasoning (PFC + hippocampus composition) close
the substrate's depth-5 and depth-10 retrieval ceiling that pointer-chain v2
HARD_FAILed?

## Pre-registered bands

**HARD_PASS_CHAIN_GRADE:**
- BASELINE in [0.62, 0.68] (sanity rail reproduces pointer_chain v2)
- ARM_WM_SCAFFOLDED_2HOP >= 0.80
- ARM_WM_SCAFFOLDED_5HOP >= 0.50 (vs pointer_chain v2: 0.122)
- ARM_WM_SCAFFOLDED_10HOP >= 0.20 (vs pointer_chain v2: 0.035)
- cv <= 0.07 across seeds (all WM arms)

**HARD_PASS_PARTIAL:**
- ARM_WM_SCAFFOLDED_5HOP >= 0.30 OR ARM_WM_SCAFFOLDED_10HOP >= 0.10
  (lift over pointer_chain v2 but not chain-grade-eligible)

**MIDDLE_BAND:**
- ARM_WM_SCAFFOLDED_5HOP in [0.15, 0.30]

**HARD_FAIL_WM_DOESNT_HELP:**
- ARM_WM_SCAFFOLDED_5HOP < 0.15 (same regime as pointer_chain v2;
  WM scaffold ineffective)

**RAIL_SANITY_BREACH:**
- BASELINE out of [0.62, 0.68] on majority of seeds
  (interpretation halted; not interpretable)

## Calibration rationale

- 0.80 / 0.50 / 0.20 targets reflect the brain's empirically-observed depth
  retention: human PFC + hippocampus multi-hop tasks (e.g., transitive
  inference) show ~80% accuracy at 2-hops, ~50% at 5-hops, ~20% at 10-hops
  before cleanup-fatigue / chunking dominates. Substrate with N=8192 has
  ~4x the WM capacity (32 vs 8 items) so should be at-least equal.
- cv <= 0.07 because the substrate is deterministic per-seed; cross-seed
  variability above 7% indicates seed-dependent W collisions, not mechanism.
- HF threshold 0.15 = same regime as pointer_chain v2 5hop=0.122 (within
  noise of the FAIL baseline). If WM-scaffold lands here, WM was not the
  missing piece.

## Q-discipline (BIAS-Q: suspect 1.000 results)

If any WM-scaffold arm scores >= 0.995, treat as suspect saturation; verify
queries are NOT in train W (i.e., the chain set + W ARE built from each
other intentionally but the held-out chains aren't being re-built into W).
Honest expectation: 0.50-0.95 range for 2-hop; 0.20-0.70 for 5-hop;
0.05-0.30 for 10-hop. The mechanism is real but error-budget per hop limits.

## Capacity-feasibility analysis

- W stores WM_N_CHAINS * max_depth = 200 * 10 = 2000 (s,p,o) bindings in
  W at N=8192. Per-(s,p) crosstalk floor is ~sqrt(2000/8192) = 0.49 (raw
  cosine to wrong atom).
- WM slot codebook is max(11, 20) = 20 slot-tags at N=8192; capacity headroom
  for slot writes is sqrt(8192/20) = 20.2 (very loose).
- E codebook is V_C = 200 atoms at N=8192; codebook crosstalk floor for
  argmax cleanup is sqrt(8192/200) = 6.4. Cleanup is the dominant signal.

Capacity is feasible at this regime.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix (deliberately; the cell tests
the WM-scaffolding mechanism at N=8192 only). PROT-018 does not apply.

## Timeout estimate

Smoke ~ 60-90s estimated at N=2048, 1 seed, max_depth=5, 50 chains.
FULL: N=8192, 3 seeds, max_depth=10, 200 chains.
Scaling: matmul-bound; scaling_exp = 2.0 (W is N x N).
formula: ceil(1.5 * 60 * (8192/2048)^2 * (3/1)) = ceil(1.5 * 60 * 16 * 3) = 4320s
With per-arm + per-depth runs (4 arms; baseline + 3 WM-scaffold depths):
budget timeout_s = 5400 (1.5 h).
Cell is well below PROT-021 4h floor; checkpoint imported anyway.
timeout_s = 5400

## Provenance rail

ARM_BASELINE_HRR_2HOP must reproduce pointer_chain v2 BASELINE within +/- 0.05
of 0.65 (sanity rail [0.62, 0.68]). If baseline breaches band, verdict is
RAIL_SANITY_BREACH (cell not interpretable).

## HF_top1 ceiling discipline

No arm should score >= 0.995; suspect Q-discipline saturation.
