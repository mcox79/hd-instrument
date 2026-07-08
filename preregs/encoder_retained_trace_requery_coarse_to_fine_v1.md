# Pre-reg: encoder_retained_trace_requery_coarse_to_fine_v1

Date: 2026-07-08
Cell: `experiments/exp_encoder_retained_trace_requery_coarse_to_fine_v1.py`
Anchor: `encoder_retained_trace_requery_coarse_to_fine_v1`
Trigger: brain-first 5x-revival drill (`notes/research_energy_scaled_selective_depth_nondestructive_refinement_brain_first_2026-07-08.md`)
on the CONFIRMED GENUINE negative -- the v1 phase-traversal condenser
(`exp_encoder_phase_traversal_spread_condense_v1`) hit an information wall (structural_gain = -0.348) because it
tried to recover pointwise semantics by condensing the HARD sign+top-k SPARSE code. Skunkworks confirmed the wall
is the quantization step, NOT the condenser: the same cell's `phase_traversal_dense` arm (condense off the
un-sparsified DENSE code) reached SC 0.9933. The drill's top pick (mechanism A) is the direct hippocampal-indexing
analog (Teyler & Rudy 2007): the brain never destroys-then-recovers -- it stores a sparse INDEX and re-queries a
RETAINED intact trace. This cell tests that fix. (Mechanism B = graded-soft-topk = the separate in-flight
`exp_encoder_phase_traversal_graded_sparse_rescue_v1` cell; NOT duplicated here.)

Prior-work check (MANDATORY substrate-KB concept-query, MEASURED): `bash tools/substrate_query.sh "retained dense
trace re-query coarse to fine selective depth shortlist condense"` -> top hits at cosine>0.30 are the two same-day
research notes + the v1 cell itself (all grounding FOR this cell, expected), plus generic concept-nodes
`condense`/`dense` (cosine 0.34). NO prior ARC cell implements the coarse-to-fine retained-trace-shortlist
mechanism. Genuinely novel; a DIFFERENT lever from the graded-sparse rescue (mechanism B).

## Question
Does refining from a RETAINED DENSE trace (mechanism A: index-dont-invert) recover fine fidelity where refining
from the SPARSE quantized code (the v1 negative) cannot -- at materially lower coarse-read cost than the full fine
read? I.e. can a CHEAP coarse condensation of the retained dense code produce a shortlist that PRESERVES the
information for a subsequent expensive fine read (on the retained trace) to recover full fidelity (energy-scaled:
low-cost coarse over all V + recoverable fine over the shortlist only)?

## Mechanism (mechanism A: index, don't invert)
- RETAINED DENSE TRACE: each concept's native expanded code z = bge @ W_up (Din=1024 -> N=4096, fixed random
  Gaussian; the encoder's native dense output). This is the intact trace; it is NEVER destroyed.
- COARSE read (cheap, all V): rank every dictionary item by a CHEAP low-dim CONDENSATION of z -- a fixed random
  projection z @ P to D_COARSE=128 dims, cosine (JL-preserves the semantic geometry since z ~ bge @ W_up). This is
  "condense the RETAINED DENSE code cheaply", NOT the sparse quantized code -> the coarse ranking shares the DENSE
  geometry the fine read uses (avoids the drill's decoupled-geometry risk that a SPARSE-code coarse ranking would
  incur). Take the top-k -> SHORTLIST.
- FINE read (expensive, shortlist only): re-rank the shortlist by the FULL trained DENSE condenser (the
  already-MEASURED-0.9933 operator: c = gelu(z @ W1) @ W2, N->H=1024->Din=1024, RKD-distilled, noise-augmented) on
  the RETAINED DENSE code z. Because the trace was never destroyed, the fine read recovers full fidelity.

## Arms (5; ONE lever varied = the fine-read TRACE SOURCE; coarse shortlist held IDENTICAL for B/A')
- `full_fine_read` [CEILING / Gate-D reproduce 0.9933]: dense condense over ALL V (no shortlist). Upper bound.
- `retained_trace_requery` [HEADLINE = B]: coarse dense-proj shortlist -> DENSE condense within shortlist (at k_OP).
- `sparse_condense_fullV` [MUST-FAIL / Gate-D reproduce 0.5383]: sparse condense over ALL V (the v1 negative).
- `sparse_condense_shortlist` [ISOLATOR = A']: SAME good dense shortlist -> SPARSE condense within shortlist. The
  load-bearing isolator: if A' fails while B recovers, the win is provably the DENSE fine-read TRACE, not the
  shortlist; if A' rises to meet B, the shortlist alone rescued sparse (a different, honest result).
- `coarse_only` [DIAGNOSTIC]: coarse-proj argmax over ALL V (top-1). Confirms the coarse read is genuinely COARSE
  (top-1 < full_fine), i.e. not secretly the oracle.

## Metrics
- `final_recall@alpha` = fraction of noisy queries whose argmax (over the arm's allowed index set: all V, or the
  coarse shortlist) is the true concept. THE decisive fidelity metric.
- `shortlist_hit_rate@k` = fraction of queries whose true concept is inside the coarse top-k (drill kill test).
- `cost_ratio@k` = analytical read-cost of B(k) vs full_fine (energy accounting; below).
- `SP@J` (native store) = superposition recall, reported for continuity (preserved by construction; not gated).
Swept axis: k_frac in {0.05, 0.10, 0.15, 0.25} (energy-scaled selective-depth curve). Operating point k_OP=0.10.
alpha_OP=1.2, J_OP=5, D_COARSE=128, sparsity k = N/32 (matches v1 / two-head).

## COST / ENERGY accounting (analytical flop model; the selective-depth win)
Fine-condense ONLY the shortlist, not all V. Per-query read cost:
- `full_fine` (ceiling)  ~ (V+1) * C_fine
- `retained_trace` B(k)  ~ V * C_coarse  +  (k+1) * C_fine
with `C_coarse = N * D_COARSE` (one linear projection) and `C_fine = N*H + H*Din` (2-layer condenser forward).
`cost_ratio(k) ~ C_coarse/C_fine + k/V`. At D_COARSE=128, N=4096, H=Din=1024:
`C_coarse = 4096*128 = 524288`, `C_fine = 4096*1024 + 1024*1024 = 5242880`, `C_coarse/C_fine = 0.10`.
- cost_ratio(k_OP=0.10) = 0.10 + 0.10 = **0.20** -> ~5.0x cheaper than the full fine read.
- cost_ratio(0.05)=0.15 (6.7x), (0.15)=0.25 (4x), (0.25)=0.35 (2.9x).
HARD_PASS requires cost_ratio_B(k_OP) <= COST_MAX=0.50 (>= 2x cheaper). Coarse scan overhead (V*C_coarse) is the
0.10 term; the dominant fine cost drops by the shortlist fraction k/V. (Amortization note: dict codes are
precomputed once in the harness for measurement; the cost model is the selective-depth flop count -- fine-condense
only the shortlist -- which is what a deployed reader would pay.)

## Pre-reg bands (envelope-fail; HEADLINE = retained_trace_requery = B at k_OP=0.10; strictly-above-floor META_RULE_L)
Anchored to MEASURED v1 (dense ceiling 0.9933, sparse wall 0.5383). RECOVER_HI=0.90 (headroom to 0.9933),
CEIL_TOL=0.05, DISCRIM_GAP=0.20 (below the MEASURED raw gap 0.9933-0.5383=0.455), SPARSE_FAIL_CEIL=0.70
(=RECOVER_HI-DISCRIM_GAP), COST_MAX=0.50, MIDDLE_TOL=0.05, HIT_FLOOR=0.65.
- `HARD_PASS_RETAINED_TRACE_RECOVERS` = B recovers (final_recall_B >= 0.90 AND within CEIL_TOL of the full_fine
  ceiling) AND sparse CANNOT (max(sparse_fullV, sparse_shortlist) <= 0.70) AND B beats sparse
  ((B - max_sparse) >= 0.20) AND cost_ok (cost_ratio_B(k_OP) <= 0.50). -> the brain-first index-dont-invert fix
  works: cheap coarse + recoverable fine; the v1 wall is the quantization step, not the retrieval.
- `MIDDLE_RETAINED_TRACE_NEAR_MISS` = B beats sparse by DISCRIM_GAP and is within MIDDLE_TOL of RECOVER_HI but does
  not clear at k_OP (needs a larger shortlist k or wider D_COARSE; see the CURVE).
- `HARD_FAIL_NO_RECOVERY` = (B - max_sparse) < 0.20 (retained-trace does NOT beat sparse-condense on recoverable
  fidelity -> the wall is deeper than the quantization step; escalate/5x-drill).
- `HARD_FAIL_DECOUPLED_GEOMETRY` = shortlist_hit_rate@k_OP < 0.65 (the coarse ranking cannot even CONTAIN the
  answer -> coarse and fine geometries decoupled; a genuinely NEW negative distinct from the quantization wall).
- Schema breaches (override): `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`, `HARD_FAIL_KCARDINALITY_BREACH_META_RULE_H`,
  `HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF`, `HARD_FAIL_BASELINE_SATURATED_NO_TRADEOFF_META_RULE_AG`,
  `HARD_FAIL_GATE_D_REGIME_OR_INVOCATION_MISMATCH` (smoke only; reproduce v1 dense 0.9933 + sparse 0.5383 at V=8000).

DISCRIMINATOR-FIRES (assert_discriminator_fires, MANDATORY at smoke): the SPARSE control must FAIL the recovery
gate at smoke scale (max(sparse_fullV, sparse_shortlist) <= SPARSE_FAIL_CEIL). If sparse rises above 0.70 at smoke
the smoke is SATURATION-VACUOUS -> raise V. sparse_condense_fullV reproduces the MEASURED v1 wall (~0.5383 at
V=8000), so the info-wall is present at smoke scale by MEASUREMENT, not by-construction.

## Compute architecture
Class (a) batched-GPU. Two condensers trained (dense + sparse), matmul-heavy (per-iter store-code forward
B x N @ N x H @ H x Din + B x B RKD pairwise). Storage: no_composition/no_store (encoder-geometry cell; per-concept
codes evaluated by argmax-cosine cleanup + coarse-to-fine shortlist, not a bundled store). Eval (argmax recall,
coarse ranking, shortlist masking) is vectorized numpy over precomputed codes -- no Python loop over V. FULL routes
to GPU (overnight_queue): N=4096, V=40000, iters=800, B=8192 (B > N -> full-rank RKD sample); cell auto-selects
cuda. SMOKE is CPU-local at production N=4096 AND V=8000 = the SAME V where v1 MEASURED the 0.9933/0.5383 gap, so
the discriminator provably fires at the smoke scale -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C.

## Functional Requirements
- FR1 cheap coarse shortlist that CONTAINS the answer -> low-dim linear condensation of the retained dense code
  (random projection z@P, JL-preserves the semantic geometry). Measured: shortlist_hit_rate@k. New composition (no
  prior primitive maps a coarse-to-fine dense-retained shortlist) -> flagged as this cell's new mechanism.
- FR2 fine read that recovers full pointwise fidelity FROM the retained trace -> the trained DENSE condenser (v1's
  phase_traversal_dense operator, MEASURED 0.9933). Measured: final_recall_B.
- FR3 do it at materially lower cost than the full fine read -> fine-condense only the shortlist. Measured:
  cost_ratio_B@k (analytical flop model).
- FR4 (contrast) a SPARSE-condensed fine read CANNOT recover -> the confirmed v1 info-wall, reproduced as
  sparse_condense_fullV (Gate-D) + the A' isolator that keeps the good shortlist.

## SCHEMA-VET / cell-template fields
```json
{
  "cardinality_ok": true,
  "expected_n_units_formula": "n_seeds (each seed = full multi-arm measurement); kcardinality: every seed carries all K_FRACS at every alpha",
  "arms_differ_verified": true,
  "arms_differ_note": "3 distinct READ-FAMILIES hashed (dense-fine / sparse-fine / coarse); k_frac variants are index-restrictions of the same family (shared by design, not a bug); no exemptions needed among the 3 families.",
  "baseline_in_band": "sparse_condense_fullV recall in (0.05, 0.95) (the ~0.5383 wall) AND sparse_condense_shortlist < 0.90 (not saturated by the shortlist). MEASURED at smoke V=8000 (below).",
  "final_metrics_atomicity": "tmp_replace",
  "crlb_n/a": "retrieval recall + shortlist hit rate; no closed-form noise floor. Feasibility calibrated by MEASURED v1 anchors (dense 0.9933, sparse 0.5383) at this exact N=4096/V=8000/alpha=1.2/k=N/32 regime.",
  "discriminator_reachability": true,
  "calibration_check": "default_ok_for_this_regime (real BGE cache; J_OP/alpha_OP/k=N/32 calibrated in v1 + two-head; Gate-D reproduce arms validate the harness at the matched regime).",
  "cell_chunked": false,
  "cell_chunked_justification": "few-seed single cell with per-seed partial checkpoint+resume (atomic tmp+os.replace); runner-death loses only the in-progress seed. Pausable/restartable.",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": "CellHeartbeat (interval_s=30) around the per-seed loop + print_flush cadence <60s (per-iter every iters//6, per-alpha line, per-seed [seed-done]).",
  "defensive_error_checking": "passed_all_4_patterns (start_marker, crash_metrics, no bare/BaseException except, per-seed partial atomic write)",
  "progress_logging": "print_flush_true",
  "progress_cadence_expected_s": 60,
  "sweep_alignment_verdict": "ALIGNED (swept axis = k_frac shortlist fraction; each k_frac is a genuine top-k slice of the SAME coarse ranking the arm experiences directly; no partition/effective-param indirection).",
  "discriminating_fraction": "the load-bearing discriminator is B(dense fine within shortlist) vs sparse-condense recall; MEASURED gap ~0.45 at smoke (below) -- well in-band.",
  "positive_control_arms": "Gate-D: full_fine reproduces v1 dense_condense 0.9933 (tol 0.12) AND sparse_condense_fullV reproduces v1 sparse wall 0.5383 (tol 0.12) AT THE MATCHED smoke V=8000. Hard-gated at smoke; report-only at FULL V=40000 (argmax over 5x more distractors drifts the absolute ceiling).",
  "telemetry_sensitivity": "self-test asserts the UNSATURATED discriminator (sparse recall) MOVES across seeds 7/13; at smoke V=8000 (un-saturated) final_recall_B, sparse recall, and shortlist hit rate all move seed-to-seed. MEASURED PASS.",
  "functional_requirements": "FR1 cheap coarse shortlist (random-proj condensation of retained dense code, new mechanism, flagged), FR2 fine recovery from retained trace (v1 dense condenser, MEASURED 0.9933), FR3 lower cost (shortlist-only fine, analytical flop model), FR4 sparse contrast (v1 wall reproduced + A' isolator)."
}
```

## Self-test (MEASURED)
`--self-test` PASS (7 witnesses) MEASURED (SELFTEST_REGIME N=2048 V=700, seeds 7/13): valid_enc (full_fine@op=1.000),
coarse_is_coarse (coarse_only 0.967 < full_fine 1.000), wall_present (sparse_fullv 0.494 < 0.90, A' 0.578 < 0.90 --
the v1 info-wall reproduces even at tiny V), recovers (dense B 1.000 > sparse), sp_moves (sparse recall 0.494 vs
0.500 across seeds -- the UNSATURATED discriminator is telemetry-sensitive), arms_differ (3 distinct read-families),
trains (finite RKD loss). NOTE the tiny-V=700 selftest SATURATES B/hit at ~1.0, so the non-saturated hit-rate/B
telemetry is a SMOKE-scale property (verified at V=8000 below) -- the identical tiny-V-saturation exemption v1's
selftest made.

## Smoke (MEASURED)
SMOKE N=4096, V=8000, iters=300, B=1536, seeds 7/13/19; CPU-local; elapsed 1137s (~19min). Verdict
`HARD_PASS_RETAINED_TRACE_RECOVERS`. All schema gates pass (arms_differ True 3 distinct read-families, cardinality
3/3 + kcardinality True, baseline_in_band True, Gate-D dense_ok+sparse_ok True). MEASURED@
data/exp_encoder_retained_trace_requery_coarse_to_fine_v1/metrics.json (aggregate over 3 seeds, alpha_OP=1.2):

| arm | final_recall@1.2 |
|---|---|
| full_fine_read [CEILING / Gate-D dense: reproduces v1 0.9933] | 0.994 |
| retained_trace_requery [HEADLINE B @k0.10] | 0.994 |
| sparse_condense_fullV [MUST-FAIL / Gate-D sparse: reproduces v1 0.5383] | 0.493 |
| sparse_condense_shortlist [ISOLATOR A' @k0.10] | 0.532 |
| coarse_only [DIAGNOSTIC top1] | 0.902 |

shortlist_hit_rate@k0.10 = 1.000 ; cost_ratio_B(k0.10) = 0.20 (~5x cheaper); GAP B-sparse = +0.462 (>= 0.20).
CURVE (B / hit / cost): k0.05=0.994/1.000/0.150, k0.10=0.994/1.000/0.200, k0.15=0.994/1.000/0.250,
k0.25=0.994/1.000/0.350. discriminator_fires: max_sparse=0.532 <= 0.70 (control FAILS the recovery gate; NOT
saturation-vacuous; sparse_fullV reproduces the v1 wall at the smoke scale). Per-seed B tight (cv 0.0024); per-seed
sparse recall moves seed-to-seed (0.5075/0.505/0.4675 -> telemetry-sensitive discriminator). SP@5=0.977 (native
store superposition preserved by construction).

DECISIVE ISOLATOR READ: the A' arm gives the SAME good dense shortlist (hit rate 1.000) to a SPARSE fine read and
it STILL fails (0.532), while the DENSE fine read (B) on the same shortlist recovers (0.994). This proves the win
is the RETAINED DENSE TRACE the fine read refines from, NOT the shortlist -- exactly the brain-first
index-dont-invert claim. The shortlist perfectly preserves the information (hit 1.0 at every k); the fine read
recovers it only when it reads the intact trace, not the destroyed sparse code.

## Disposition
SMOKE HARD_PASS (discriminator fired at the scale-honest V=8000 preview; sparse-condense FAILED fine-recovery
0.493/0.532, dense retained-trace RECOVERED 0.994 at 5x lower coarse-read cost). Clear FULL. Route to GPU
overnight_queue (2 trained condensers, N=4096, V=40000, iters=800, B=8192; cell auto-selects cuda). Timeout 10800s
(3h; tools/exp_guard.py trained_encoder floor; raw estimate 9333s floored, not blocked -- CPU-smoke->GPU-FULL
hardware change makes the multiplicative wall model inapplicable, so the class floor governs). exp_dev builds +
smokes + returns the command; ORCHESTRATOR ships remote (SCP/SSH) + owns post-ship REMOTE VERIFY. queue_add command:
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_retained_trace_requery_coarse_to_fine_v1 experiments/exp_encoder_retained_trace_requery_coarse_to_fine_v1.py preregs/encoder_retained_trace_requery_coarse_to_fine_v1.md 10800`

NOTE at FULL V=40000: the Gate-D dense ceiling may drift below 0.9933 (argmax over 5x more distractors) -- Gate-D is
hard-gated only at smoke V=8000 (matched regime) and report-only at FULL; the verdict keys on B recovering within
CEIL_TOL of the FULL full_fine ceiling AND beating sparse by DISCRIM_GAP (both regime-robust relative bands).

ASCII-only. No unicode. No emojis. No em dashes.
