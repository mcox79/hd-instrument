# Skunkworks landed-VET batch: WM K-cliff (orchestrator HP framing OVERRIDDEN -> MM) + pattern_completion (concur MB)

**Date:** 2026-06-28T17:35Z
**Cert-owner:** skunkworks (Agent Teams sub-agent spawned by Research)
**Triggered by:** notes/orchestrator_to_skunkworks_WM_KCLIFF_3seed_HARDPASS_landed_VET_2026-06-28.md

## Headline

| cell | orchestrator framing | cert-owner ruling | CERT delta |
|---|---|---|---|
| WM multi-bank K-cliff phase diagram v1 (3-seed seeds 7/13/19) | HARD_PASS x3 chain-grade candidate | MEASURED_MECHANISM / mechanism_characterization | +0 |
| pattern_completion corruption-cliff phase diagram v1 | MIDDLE_BAND by-construction saturation | MIDDLE_BAND / mechanism_characterization | +0 |

**CERT delta this batch: 0** (both cert-neutral; neither chain-grade).

## Atom IDs + cert_ledger rows

Atomized via `tools/skunkworks_atomize_wm_kcliff_MM_pattern_completion_MB_2026-06-28.py --apply` (A5 PRE+2=POST clean; round-trip verify PASS; verify-off-data PASS).

- `math::T3/EXP_substrate_wm_multibank_K_cliff_phase_diagram_v1_3seed_MEASURED_MECHANISM_capacity_bound_by_construction_saturation_2026-06-28` (content-sha b1201d0909976c34)
- `math::T3/EXP_substrate_pattern_completion_corruption_cliff_phase_diagram_v1_MIDDLE_BAND_sharp_step_cliff_at_corruption_0p5_iters_falsified_2026-06-28` (content-sha 2303c5cd7c339d4f)
- 2 cert_ruling rows appended to `data/substrate_index/meta/cert_ledger.jsonl` (884 -> 886)

## WM K-cliff: why orchestrator HARD_PASS framing is OVERRIDDEN

Verified OFF DATA (per_unit recompute across all 3 seeds; NOT from verdict_msg):

1. **VRAM ceiling masquerading as substrate cliff.** Pre-reg promised 5 K-values {4096, 8192, 16384, 32768, 65536}. Only K in {4096, 8192, 16384} actually ran. K=32768 + K=65536 hit `HP_VRAM_PROBE_BREACH` (est_peak=5.51GB > budget=4.88GB on 8GB GPU). The cell's `cliff_per_ov_rn={'ov=0.00_rn=0.00': 16384, ...}` reports the highest measured K that passed — NOT the substrate's empirical phase boundary. The "cliff at K=16384" is a GPU memory ceiling.

2. **By-construction saturation at every measured point.** For all 27 paired (K, ov, rn) points per seed: SUBSTRATE recall = 1.0000 (n_saturate=27/27 of MEASURED points). The cell's HARD_FAIL_SATURATION_ONLY check at `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py:887` tests `n_saturate == len(phase_map)` — but `len(phase_map)` includes 18 probe-denied "CLIFF" markers, so `n_saturate=27 != 45` always and the gate cannot fire. SCHEMA BUG.

3. **Discriminator passes by construction.** SUBSTRATE - RANDOM > 0.20 trivially passes because RANDOM is mathematically pinned at 1/CB ~ 1.5e-5 (cell uses CB=65536). With SUBSTRATE = 1.0 and RANDOM ~ 0, the margin is always ~1.0. This is the canonical g1 pattern (atomized 2026-06-22, feedback_cert_owner_overrides_director_via_by_construction_saturation).

4. **Secondary axes also saturate.** overlap in {0, 0.1, 0.3} x routing_noise in {0, 0.05, 0.15} — at every (K, ov, rn) combination that ran, SUBSTRATE recall stayed at ~1.0. The pre-reg's F6 (phase-coherence: cliff K monotone in overlap+noise) has no empirical basis — no cliff observed in any direction within the measurement regime.

5. **3-seed convergence on SATURATION is not convergence on a discriminator.** All 3 seeds report identical aggregate (pass=27 sat=27 floor=0 probe_cliffs=36 arms_differ=27/9). When a metric is at 1.0 by construction, n-seed replication is uninformative; the discriminator is the cliff structure, and we don't have one. Seed independence is real (arm_sha distinct per seed: 48de93/686c87/6ceea1).

### WHAT THIS DOES PROVE (the proven robustness bound)

Substrate WM multi-bank mechanism is empirically robust to (overlap up to 0.30 + routing_noise up to 0.15) at K up to 16384. No degradation observed in any direction within the measurement regime. This is a useful characterization with a clear caveat: the cliff (if it exists below the VRAM ceiling) was not localized. This is MEASURED_MECHANISM in the strict sense — a proven bound, not nothing.

### Gates that DID pass (don't lose them)

- Fix #24 GPU util gate: PASS (77/77/88% across seeds 7/13/19; first phase-diagram cell with proper GPU usage).
- Substrate-only-decode gate: PASS (`_llm_forward_calls_at_inference=0` across all 54 units, all 3 seeds).
- Arms-distinct (META_RULE_AF): PASS (arms_differ=27/27 paired points per seed; SHA cleanly distinct per seed).
- No silent except (META_RULE_AN): PASS (real_failures=0; probe-denials are exc_type=HP_VRAM_PROBE_BREACH which the cell handles explicitly).
- Cardinality (META_RULE_H): PASS per cell convention (54 measured + 36 probe-denied = 90 = expected).

### Test-design recommendation for v2

1. **16GB+ GPU OR smaller K_per_bank** to localize the cliff beyond K=16384. The mechanism appears not to cliff in the K range we can measure; we need either more VRAM or a smaller-footprint configuration to push past.
2. **Pivot to discriminating regime.** Smaller N_DIM (e.g., 4096) or higher k_per_bank (e.g., 128) pushes alpha past 1.0, where the chain-grade multi-bank primitive previously cliffed in v3. THIS is the regime to map.
3. **Respec HARD_FAIL_SATURATION_ONLY** to fire on measured-points-only fraction: `n_saturate / n_measured`, not `n_saturate / len(phase_map)` where the denominator includes probe-denials.
4. **Consider k_per_bank as primary axis.** Crosstalk per bank is the direct phase control variable; K_total mixes capacity x crosstalk and may be the wrong knob to localize the mechanism transition.

## Pattern_completion: cert-owner concurs with orchestrator MIDDLE_BAND

Verified OFF DATA (phase_map recompute):

- 72/72 phase points ran (cardinality_ok=True).
- Tier distribution: 24 SATURATED + 48 FLOOR + 0 HARD_PASS + 0 per-point MIDDLE_BAND + 0 HARD_FAIL.
- Coarse corruption grid {0.10, 0.30, 0.50, 0.70, 0.85, 0.95} STEPS RIGHT OVER the bistable transition zone. Pre-reg's HARD_PASS band [0.80, 0.95) and per-point MIDDLE_BAND [0.50, 0.80) are EMPTY.
- corruption=0.10 + 0.30 -> top1_substrate = 1.0000 (24 points; SATURATED).
- corruption=0.50 -> top1_substrate = 0.0000 to 0.0020 (cliff already cliffed).
- corruption>=0.70 -> top1_substrate = 0.0000 (floor; 36 points).

### Cliff IS real and sharp

Cliff at corruption_frac ~ 0.5 cleanly matches CRLB 1-step prediction (0.46-0.49 per overlap-floor analysis). Mechanism transitions within a band narrower than the test grid resolution. This is MEASUREMENT (we know cliff is sharp), just not a CHARACTERIZATION (we don't know the edge shape).

### Proven negatives (CERT-neutral but useful)

- **H1 (cliff shifts right with N): FALSIFIED.** Cliff at corruption_frac=0.5 for ALL N in {2048, 4096, 8192, 16384}. 4x variation in N produced ZERO shift. The cliff is N-independent in the measured grid (subject to N >> log(P)/(1-2c)^2 being satisfied everywhere; at M=500 this is OK for all 4 N values).
- **H2 (iterative cleanup T extends cliff): FALSIFIED.** cleanup_iters in {1, 5, 20} produce IDENTICAL top1_substrate at every (N, corruption_frac). T=20 doesn't beat T=1 anywhere. The iterative-attractor-basin-grows hypothesis does NOT hold in the measured regime.

### Test-design recommendation for v2

Per META_RULE_AG band-calibration: respec the corruption grid to the [0.30, 0.70] band where the mechanism is neither saturated nor floored. Suggested finer sweep: {0.40, 0.42, 0.44, 0.46, 0.48, 0.50, 0.52, 0.54, 0.56, 0.60}. THIS is where iterative cleanup (T=20 vs T=1) might differentiate — the basin-of-attraction question is meaningless at saturation OR at floor; it only matters at the edge. The v2 also offers a clean re-test of H2 falsification: if iters STILL doesn't help near the edge, that's a STRONGER negative on the iterative-attractor hypothesis (lift it to a chain-grade negative).

Also consider sweeping M_items: alpha = M/N might modulate cliff sharpness. At M=500/N=2048 alpha=0.244; at M=500/N=16384 alpha=0.031. The cliff sharpness could vary across this 8x range and v1 didn't test it.

## Schema/SCHEMA-VET observations for future pre-regs

Both cells passed pre-dispatch SCHEMA-VET by passing the explicit pre-reg checks. BUT:

1. **WM cell:** the pre-reg's HARD_FAIL_SATURATION_ONLY band ("every point at SUBSTRATE >= 0.995") was not paired with a "measured-points-only" caveat. With VRAM-probe-denial as an expected outcome, the saturation gate should EXCLUDE probe-denied points from both numerator and denominator. The pre-reg author and SCHEMA-VET (would have been me) missed this — flagged for next-cycle SCHEMA-VET discipline.

2. **Pattern_completion cell:** the pre-reg's corruption grid was authored before substrate-as-canonical query-first directive (USER 2026-06-27); the prior chain-grade `exp_iterative_cleanup_gpu_v1` HARD_PASS at corruption=0.50 N=2048 single-step already showed saturation at this exact frac. The pre-reg should have queried the substrate for the prior cliff-frac evidence and centered the new grid on the bistable region, not re-traversed it coarsely. SCHEMA-VET v2 must include "what corruption_frac did the prior chain-grade saturate at; does the new grid bracket it finely or coarsely?"

## Intuition (brief)

- **WM K-cliff:** valuable robustness data (substrate doesn't break under overlap+noise up to K=16384), but the "phase diagram" is incomplete on the primary axis. The cliff might be at K=32768 (just above VRAM) or might be at K=1M (well past current hardware). Without measurement, we can't say. The chain-grade WM K=8192 result already in CERT (586) covered the qualitatively-similar question; this run extends robustness to overlap+noise but doesn't materially advance the phase-diagram localization.
- **Pattern_completion:** the cliff is REAL and SHARP at corruption=0.5, matches theory cleanly, and the proven-negative on iters is genuinely informative (iterative softmax-Hopfield cleanup in this regime is wasted work; ship T=1 in production). The v2 finer-grid sweep is cheap (13s total runtime for this v1; same compute envelope at 10x finer) and should land quickly.

## Cross-references

- Pre-regs: `preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md`, `preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md`
- Cells: `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_{7,13,19}_v1.py`, `experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py`
- Metrics: `data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_{7,13,19}_v1/metrics.json`, `data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1/metrics.json`
- Orchestrator routing: `notes/orchestrator_to_skunkworks_WM_KCLIFF_3seed_HARDPASS_landed_VET_2026-06-28.md`
- Atomize tool: `tools/skunkworks_atomize_wm_kcliff_MM_pattern_completion_MB_2026-06-28.py`
- Cert ledger: `data/substrate_index/meta/cert_ledger.jsonl` (lines 885-886)
- Math atoms: `data/substrate_index/math/atoms.jsonl` (lines 28653-28654)
- Related prior: g1 pattern (2026-06-22) `feedback_cert_owner_overrides_director_via_by_construction_saturation_2026-06-22.md`

— skunkworks (cert-owner / auditor; spawned via Agent Teams)
