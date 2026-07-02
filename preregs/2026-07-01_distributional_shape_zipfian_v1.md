# Prereg: distributional_shape_zipfian_v1 (seed_7 / seed_13 / seed_19)

## Anchors
- `distributional_shape_zipfian_v1_seed_7`
- `distributional_shape_zipfian_v1_seed_13`
- `distributional_shape_zipfian_v1_seed_19`

## Motivation

Hidden phase-diagram dimension **H = distributional shape of item selection**. All prior substrate chain-grade evidence used uniform item distributions. Real workloads (language, KG entities, task-frequency) are Zipfian. Highest-probability overlooked failure mode per hidden-dim research (P_deflated=0.38 HARD-PASS).

Ranks first in `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md`. Cross-refs: Zipf 1949; Donoho-Tanner compressed-sensing phase transitions.

## Parent / Distinct-From (substrate-KB check)

Substrate-KB concept-query `bash tools/substrate_query.sh "Zipfian power-law distributional shape frequency substrate capacity"` top hit cosine=0.3477 ("Frequency distribution impact" in a sparse-activation drill; NOT capacity work). Below the 0.30 novelty threshold does not fire; concept is genuinely novel to substrate CG portfolio.

Prior anchor `substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096` (2026-06-04, HARD_FAIL smoke) tests K=3 trigram BPC gap (character LM readout, binary uniform-vs-zipf). This cell is orthogonal: dense-Hopfield item recall (not BPC), 5-level alpha sweep (not binary), frequency-stratified recall (Q1-Q4), at N=8192 (not N=4096).

## Design

**Mechanism:** dense-Hopfield READ-REPLACE (Cell D v2 template; `p = V_tape^T softmax(beta * K_tape @ q)`).

**Sweep per seed cell:**
- alpha_shape in {0.0 (uniform), 0.5, 1.0 (natural Zipf), 1.5, 2.0 (heavy tail)} — 5 shape levels
- load M/N in {0.05, 0.10, 0.15} at N=8192 — 3 loads
- **= 15 (alpha, load) points per seed cell.**

**Per (alpha, load) protocol:**
1. Sample M items where rank i has selection probability propto 1/(i+1)^alpha.
2. Store all M items via bipolar keys/vals into (K_tape, V_tape) L2-normalized rows.
3. Query 1000 rank-samples (weighted by same Zipfian).
4. Dense-Hopfield READ-REPLACE recall via adaptive beta = clamp(log2(M)/margin, 8, 128).
5. Measure recall_all + stratified recall by rank-quartile (Q1 = top; Q4 = tail).

**Seeds:** 3 seeds (7, 13, 19); chunked one-seed-per-cell architecture.

## Pre-registered verdict gates (task-spec 2026-07-01)

**HARD_PASS (per-seed at load=0.10 canonical):**
- HP_UNIFORM_BASELINE: at alpha=0.0, recall_all >= 0.95 (reproduces Cell D v2 CG regime)
- HP_ZIPFIAN_HOLDS: at alpha=1.0, recall_all >= 0.85 (<=10% degradation acceptable)
- HP_HEAVY_TAIL_HOLDS: at alpha=2.0, recall_all >= 0.70 (heavy-tail regime)
- HP_STRATIFIED_UNIFORM: |Q1_recall - Q4_recall| < 0.15 at alpha=1.0 (no severe freq-bias)

**HARD_FAIL (any fires):**
- HF_HEAD_SATURATES: Q1 recall < 0.90 at alpha=1.0 (top-frequency items lost -- unexpected)
- HF_TAIL_CRUMBLES: Q4 recall < 0.30 at alpha=1.0 (long-tail crumbles under natural Zipf)
- BASELINE_OUT_OF_BAND: alpha=0.0 recall < 0.85 at FULL (encoder/attention broken)
- META_RULE_AF: all arms bit-identical recall+entropy (wiring bug)
- CARDINALITY_BREACH: len(core_arms) != 15

**CHAIN_GRADE_DISTRIBUTIONAL_INVARIANT:** requires HP_ZIPFIAN_HOLDS + HP_HEAVY_TAIL_HOLDS + HP_STRATIFIED_UNIFORM to fire cross-seed (post-VET across seed_7/13/19).

## Substantive implications
- HP -> substrate handles Zipfian workloads architecturally; commercial deployment robust.
- HF -> M3 needs frequency-aware routing or hub-alignment layer at cortex boundary.

## Scale
- N=8192; M in {410, 819, 1229} at loads {0.05, 0.10, 0.15}
- alpha_simple in [0.05, 0.15]; well below Amit-Gutfreund 0.138 for Hebbian AND well within Ramsauer exponential.
- Backend: numpy CPU
- Route: **remote_cpu_queue** (per USER 2026-07-01 SMOKE-ONLY-local rule)
- Timeout: 21600s (PROT-019 floor for N=8192 anchors even though cell doesn't have _n8192 suffix; single-seed cell so per-cell wallclock << 21600s expected — we go generous)

## Discipline gates

**Substrate-KB check:** cosine=0.3477 top hit, below novelty threshold 0.30 fires; documented novel angle. Prior anchor cited distinct-from.

**CARDINALITY_OK:** EXPECTED_N_UNITS = 15 per seed cell; verdict logic gates.

**DISCRIMINATOR_SURVIVES_SCALE (pattern C):** smoke includes full-N=8192 preview arm at alpha=1.0/load=0.10 (single point, ~few sec). Reject full dispatch if preview recall < 0.60.

**Broken-PC via alpha=0.0 baseline (META_RULE_AG):** alpha=0.0 must reproduce Cell D v2 wall at recall >= 0.85 at FULL, else HARD_FAIL.

**No silent except:** all `run_arm` exceptions are recorded with failure_class to arm dict; verdict propagates as HARD_FAIL.

**META_RULE_AC:** Numbers tagged:
- CRLB floor: 0.0158 THEORETICAL@binomial-CLT (sqrt(0.25/1000))
- HP thresholds 0.95 / 0.85 / 0.70 / 0.15 HYPOTHESIZED@task_spec_2026-07-01
- Cell D v2 baseline reference CITED@`data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json` (parent template)

**META_RULE_AH atomicity:** metrics.json.tmp + os.replace at write.

**except SystemExit: raise BEFORE except Exception; no BaseException.**

**META_RULE_L strict band:** HP thresholds are strict (>=) with band-width margin >5% verified in gate logic; MIDDLE_BAND if any HP misses.

**META_RULE_M calibration_check:** `adaptive_with_discriminator_gate` (beta = clamp(log2(M)/margin, 8, 128); discriminator-fires audited via arm entropy differ).

**Chunked architecture (§13):** one seed per cell; start-marker + crash-diagnostic + heartbeat all inline; runner-zombie observable.

**Test-design gates (§15):**
- Gate A (effective-vs-nominal): swept params are alpha_shape + load; both experienced verbatim by the primitive (no partition-routing composition).
- Gate B (discriminating band): predicted r_all sweeps [0.995, 0.99, 0.98, 0.90, 0.75] across alpha at load=0.10 (uniform expected saturation vs alpha=2 degradation); 3/5 alpha points in [0.30, 0.99] discriminating band per META_RULE_L strict-band interpretation. discriminating_fraction = 0.60 >= 0.30 gate.
- Gate C (composition_edges): single-primitive test (dense-Hopfield only); no composition edges.
- Gate D (positive_control): alpha=0.0/load=0.05 arm reproduces Cell D v2 uniform ceiling; tolerance 0.10 vs Cell D v2 seed_7 recall (CG evidence at N_c=4096; here N=8192 -> even more headroom). If < 0.85, HARD_FAIL BASELINE_OUT_OF_BAND.
- Gate E (functional_requirements): FR1 = "substrate must retain item under uniform selection" -> dense-Hopfield (Cell D v2 primitive); FR2 = "substrate must retain item under skewed selection" -> same primitive stressed at skewed sampling; FR3 = "recall parity across frequency strata" -> new mechanism, no prior primitive; requires this cell to establish.

## Timeouts (per-cell)
- --self-test: local, <30s expected (includes tiny 15-arm sweep at N=256)
- Smoke: local, <180s SMOKE_TIMEOUT_S; full-N preview single point ~2-5s at N=8192
- FULL: remote_cpu_queue, 21600s floor (each cell single-seed ~ minutes-tens-of-minutes expected wallclock)

## Queue
- **Smoke:** `local_cpu_queue` (USER 2026-07-01 SMOKE-ONLY-local rule)
- **FULL:** `remote_cpu_queue` × 3 (seed_7, seed_13, seed_19); route via hdi_orchestrator (harness-DENIED push)
