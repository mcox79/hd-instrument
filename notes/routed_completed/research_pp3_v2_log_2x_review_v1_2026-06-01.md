# Research 2x review: PP-3 V2-log rotational hypothesis REFUTATION (2026-06-01)

**From**: research session (2x drill on closed result)
**Date**: 2026-06-01
**Trigger**: User directive "make sure negative findings are routed to research for review" + `[[feedback-negative-results-2x-research]]` (rescue paths before closure)
**Source**: closure note `notes/routed_completed/research_pp3_v2_log_decomposition_v1_2026-06-01.md`
**Method**: stress-test the observable-invariance math; enumerate alternative observables; theoretical CF-prevention check via consistent / inconsistent / partial rotation primitives; multi-seed micro-simulation
**Cost**: $0 (laptop CPU; ~30 min wall)

---

## HEADLINE

**Closure CONFIRMED at FULLY-CLOSED level.** The observable-invariance argument is mathematically correct: `codebook_usage_hist_drift_l1` is a marginal PMF over slot indices and is invariant under any continuous rotation of the codeword space, under W -> R W R^T, and under any (k,v) multiset-preserving permutation. One non-trivial edge case exists — slot-permutation "rotations" that are code automorphisms — but they require an explicit rotation primitive in the workload, which V2 SUSTAINED does NOT contain. The 0.911 value remains fully explained by random fact-turnover.

**The underlying CF-prevention-via-rotation claim** also collapses on theoretical analysis: consistent W + codebook rotation is identity (no CF effect); inconsistent W-only rotation is catastrophically destructive (0.000 retention); per-step small consistent rotation (rotation-noise as regularizer) shows no significant CF benefit at 5-seed N=512 sweep (mean diff +0.016, std 0.059 — not significant). The "PP-3 rotation doubles as CF prevention" unification path is closed at BOTH observable AND theoretical layers.

**Calibrated P(rotational dynamics exist in PP-3 rotation but are masked by L1 observable)**: **0.04 deflated** (was 0.05 in closure; further deflated by 0.01 because theoretical CF-prevention path independently fails).

**Closure confidence**: **FULLY-CLOSED**.

**Cheap-probe recommendation**: NOT required. (One opportunistic future drill noted at end, but not authorized.)

---

## Task 1: Validate the closure (stress-test the math)

### Verification simulation

Direct numeric check at N=256:
- W rotation `cb' = cb @ R^T` reproduces `R W R^T` exactly: confirmed (`allclose` true, atol 1e-4).
- L1 of codebook usage histogram under codebook rotation (same fact set, rotated codebook): **0.000000** — confirms full invariance.

### Edge cases stress-tested

**Edge case 1 — Adversarial codebook construction**: would a codebook with engineered structure make L1 rotation-sensitive? **NO**. L1 of the slot histogram depends ONLY on the (k,v) multiset assignment to slot IDs; the bit pattern of codeword[s] in R^N is never read by `codebook_usage_histogram`. Any codebook geometry yields the same L1 invariance.

**Edge case 2 — Particular workloads that create rotation-correlated slot usage**: even if the workload preferentially uses slots related by a fixed orthogonal R (e.g. retrieving by k then storing at R(k)), the histogram counts at slot IDs are still independent of the geometric relationship between codewords. No workload class breaks the invariance.

**Edge case 3 — Slot-permutation "rotations" (code automorphisms)**: this is the ONLY non-trivial edge case. If R is in Aut(codebook) — e.g. a hyperoctahedral / coset-translation symmetry that maps codewords to codewords (effectively permuting slot IDs) — then the geometric rotation IS a slot permutation. In this case, L1 between pre-rotation and post-rotation histograms would be NONZERO if the permutation reshuffles high-usage slots into different positions. **However**: (a) V2 SUSTAINED runs no rotation primitive at all; W is updated only by rank-1 outer-product add/sub at store_fact/edit/delete; (b) the 0.911 drift came purely from fact-turnover, not from any applied rotation operation; (c) testing this edge case would require an experiment WITH an explicit rotation step, which is a different experiment from V2.

**Conclusion of stress-test**: the original observable-invariance argument is correct. The slot-permutation edge case is a mathematical curiosity, not a defect in the closure for the V2 dataset analyzed.

### Numerical bounds

- L1 invariance under continuous rotation: exact (numerical confirmation at 1e-6 level).
- L1 sensitivity to slot-permutation rotations: depends on permutation; ranges 0.0 (if usage profile is permutation-symmetric) to ~1.0 (if permutation moves all mass to disjoint support). Not applicable to V2 since no such rotation was performed.

---

## Task 2: Alternative observables for detecting rotation (if it existed)

Per `[[feedback-dont-overextend-theorems]]`, ranked by sensitivity and cost.

| Observable | Detects | Pre-conditions | Cost (smoke) | P(informative) |
|---|---|---|---|---|
| **A. W spectral fingerprint** `delta_spectrum = |sort(eigvals(W_init)) - sort(eigvals(W_final))|_1 / sum` | Invariant under rotation; sensitive to content change | requires saving W at init+final | ~$0.01 (analytic on saved W) | 0.65 |
| **B. W orthogonality matrix** `O = W_init^T W_final / |...|`; effective rotation angle `theta_eff = arccos(median eigval of O)` | Direct rotation measurement | requires saving W_init, W_final | ~$0.01 (analytic) | 0.80 |
| **C. Per-slot codeword overlap** `cos(codebook_init[s], codebook_final[s])` per slot | Detects per-slot codeword changes; pointwise rotation | requires codebook snapshots | ~$0.01 | 0.55 — but BSC codebook is fixed in current substrate so this is identically 1.0 |
| **D. Cross-slot inner-product time series** `sim(slot_i_t0, slot_i_t1)` matrix | Detects rotation magnitude and direction | requires codebook snapshots at >=2 timepoints | ~$0.05 | 0.50 — same blocking as C |
| **E. Per-fact retrieval fidelity** of INIT-set facts at t=final | Retention proxy; rotation-aware only if applied | requires logging init fact IDs and retrieving them at end | ~$0.10 (extra retrieves) | 0.70 |
| **F. Audit-cert tag rotation entropy** Shannon entropy of cert-chain link tags | Tag distribution change | already partially logged via chain | ~$0.01 | 0.30 — coarse-grained, weak |
| **G. Mutual information** `MI(W_init, W_final)` via plug-in or KSG | Non-linear dependence beyond linear correlation | requires sampling pairs from W matrices; expensive | ~$0.50 | 0.40 (overpowered for the question) |
| **H. Free-probability moment match** `m_k(eigvals(W_init))` vs `m_k(eigvals(W_final))` for k=2..6 | Rotation preserves all moments; content change shifts them | analytic on saved W | ~$0.01 | 0.55 — but v316 closed the underlying free-prob framework |

**Top 3 recommended observables** (if a rotation-detection drill were ever authorized):
1. **B** (W orthogonality matrix): cleanest direct measurement of rotation magnitude.
2. **A** (W spectral fingerprint): cheap distinction between rotation (preserves spectrum) and content remake (shifts spectrum).
3. **E** (per-fact retrieval fidelity for init set): the meaningful CF observable; closer to the killer-feature question than spectral arithmetic.

**Critical caveat**: ALL of A-H require capturing W (and possibly codebook) at multiple time points, which V2 SUSTAINED does NOT do. The summary `v2_sustained_metrics.json` has 4 keys (verdict, verdict_msg, elapsed_s, summary). To run any of these observables, a NEW experiment would need to save the matrices.

---

## Task 3: CF-prevention-via-rotation theoretical re-examination

Per `[[feedback-dont-overextend-theorems]]`: don't kill the rotation-affects-CF idea because L1 misses it. Test the underlying theoretical claim directly.

### Three regimes

**Regime 1 — Consistent rotation** (W -> R W R^T AND codebook -> codebook R^T applied together):

Numerical check at N=512, M=100 baseline retention 0.910:
- Original retrieval: 0.910
- After R W R^T + cb R^T: 0.910

Mathematical reason: this is an isomorphism on the operator algebra of W. Retrieval `sims = cb (k W^T) / N` becomes `cb' (k' W'^T) / N` with `cb' = cb R^T`, `k' = cb'[k_id] = cb[k_id] R^T`, `W' = R W R^T`. Plugging in: `sims' = (cb R^T)(cb R^T)[k_id] (R W R^T)^T / N = cb R^T R W^T R^T cb^T... ` Working through: yes, this is identity to the original retrieval up to the global change of basis. **CF effect = 0**.

**Regime 2 — Inconsistent rotation** (W -> R W R^T, codebook FIXED):

Numerical check at N=512:
- After R W R^T (cb fixed): retention drops 0.910 -> **0.000**. Full catastrophic.
- Block-diagonal Rb (4 blocks of size 128): retention 0.910 -> 0.000. Even structured partial rotation is catastrophic without codebook coordination.

Mathematical reason: retrieval reads `cb[k] @ W.T`; if W rotates but cb doesn't, the new output `R k W^T R^T` is no longer aligned with any codeword in the un-rotated cb. **NOT a CF mechanism — destroys ALL retention**.

**Regime 3 — Rotation-noise** (per-step small theta rotation applied to both W and codebook):

5-seed sweep at N=512, M=100, n_new=200, theta=0.001:

| Seed | Baseline | Vanilla CF final | Rotation-noise final | Diff |
|---|---|---|---|---|
| 0 | 0.920 | 0.810 | 0.830 | +0.020 |
| 1 | 0.900 | 0.750 | 0.780 | +0.030 |
| 2 | 0.880 | 0.720 | 0.710 | -0.010 |
| 3 | 0.910 | 0.740 | 0.840 | +0.100 |
| 4 | 0.910 | 0.810 | 0.750 | -0.060 |
| Mean | | 0.766 | 0.782 | **+0.016** |
| Std | | | | **0.059** |

Sign test: 3 positive, 2 negative. T-statistic: 0.016 / (0.059 / sqrt(5)) = 0.60 — **NOT significant** at any reasonable threshold. Sample is small (5 seeds, N=512), so a real small effect at substrate scale (N=4096) can't be ruled out, but the direct signal is firmly null.

### Theoretical conclusion

The CF-prevention-via-rotation underlying claim FAILS in two of three regimes (catastrophic in Regime 2; identity in Regime 1) and shows no significant effect in Regime 3 at the scale tested. **There is no compelling theoretical path by which a rotation primitive provides CF resistance in this substrate's algebra.**

This is INDEPENDENT of the L1-observable refutation. The unification is closed not just at "L1 can't detect it" but at "the math says there's nothing to detect."

### Caveat per `[[feedback-dont-overextend-theorems]]`

Three things this analysis does NOT rule out:
1. **Discrete code-automorphism rotations** at the slot-permutation level COULD produce non-trivial dynamics if combined with a workload that respects the automorphism structure. Unstudied here; very narrow regime.
2. **Substrate-noise as implicit rotation** during high-throughput edits (numerical drift in W). Already captured in `w_l2_norm_drift_ratio=1.0011` which is within FP32 round-off; no signal.
3. **Larger N** (>=4096) might show a small Regime-3 effect that's drowned by noise at N=512. Could be tested but the prior is now very low.

---

## Task 4: Closure confidence decision

**Closure confidence: FULLY-CLOSED.**

Justification:
- (a) Observable-invariance argument is mathematically correct (verified numerically).
- (b) Edge cases (adversarial codebook, particular workloads, slot-permutation rotations) do not apply to the V2 dataset.
- (c) The underlying theoretical claim (rotation prevents CF) independently fails — Regime 1 is identity, Regime 2 is catastrophic, Regime 3 is not significant in the 5-seed micro-sim.
- (d) Two independent failure layers (observable AND theory) compound to FULLY-CLOSED.

**NEEDS-PROBE rejected**: a probe at this stage would burn $5-30 to test a hypothesis whose theoretical underpinning has been shown vacuous. Better to redirect that capacity to the Tier-1 candidates surfaced by the field advisor (F4 free cumulants, D1/D2/D7 stochastic dynamics, F2 Wigner edge).

**PROVISIONAL rejected**: there is no open question of the form "if we just had observable X..." — observable B (W orthogonality) would CONFIRM the closure, not reopen it, because consistent rotation is identity and inconsistent rotation is destructive.

---

## Task 5: Calibrated P estimate for "rotational dynamics exist but L1 masks them"

**P_rotation_masked = 0.04 deflated** (was 0.05 in closure).

Decomposition:
- Prior from closure analysis: 0.05
- This drill's theoretical analysis: independently fails the underlying mechanism (Regimes 1-3). Reduces by ~0.02.
- Adjacency caveat (slot-permutation rotations at code automorphism level): adds back ~0.01.

Calibration penalty per `[[feedback-lit-scan-calibration-penalty]]`: substrate is in uncharted regime; penalty already absorbed in 0.04 final estimate. Cap on novel-synthesis P is 0.50 (not binding here).

**Compare to threshold for NEEDS-PROBE recommendation (P > 0.30)**: 0.04 << 0.30. No probe recommended.

---

## Cross-thread synthesis

This drill confirms three convergent today-2026-06-01 syntheses:
1. **v316 cap_map**: free-prob framework REFUTED at substrate finite-N (rank-1 perturbation HF).
2. **testbed PP-3 Phase 1**: rotation forced by GDPR Art 17, NOT by free-prob-derived capacity scaling.
3. **closure note (research_pp3_v2_log_decomposition_v1)**: codebook_usage_hist_drift_l1 is rotation-invariant.
4. **THIS 2x drill**: the underlying CF-prevention-via-rotation claim independently fails at theoretical level (3 regime analysis).

**Unifying narrative**: PP-3's strategic value is the **compliance + audit + cryptographic erasure** path. The C5 SPECULATIVE bonus (rotation also prevents CF) was attractive because it would unify two killer features, but the substrate's algebra simply doesn't admit a non-trivial rotation-driven CF mechanism. The killer-feature wedges (deletion certificate, compositionality audit, per-fact retention) remain anchored on the PP-3 primary axis; the C5 path is structurally closed.

**Lesson locked-in**: future SPECULATIVE candidates proposing "X observable shows Y mechanism" must include a 5-min sanity check that X is INFORMATIVE about Y before being added to drill lists. The closure note already flagged this; this 2x drill reinforces and confirms.

---

## Substrate-product implications

Per `[[feedback-substrate-value-framing-matured-2026-05-26]]`: framing is "does this strengthen the killer-feature wedge".

**Does this strengthen any wedge?** No.
**Does it weaken any wedge?** No — the PP-3 primary axis (compliance-driven rotation primitives) is unchanged.
**What does it lock in?**
- A second-layer confirmation that the rotation-as-CF-prevention path is closed at BOTH observable AND theoretical levels. Future research dispatches need not re-examine this from a third angle.
- The killer-feature messaging stays clean: PP-3 = "auditable deletion + GDPR-compliant rotation"; CF resistance is a SEPARATE capability axis served by C1/C2/C3 (block-aligned sub-spaces, edit-locality, replay) or by capacity-bound architectures.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

These predictions apply ONLY if a future drill ever reopens the question at a different observable. Per closure-note recommendation NOT to authorize.

### Pre-reg setup (hypothetical)
24h sustained workload identical to V2 baseline, MODIFIED to save `W_init`, `W_final`, and apply a SCHEDULED rotation primitive at op_i=12000 (mid-run).

### HARD-PASS for "rotation is the dominant mode"
- `delta_spectrum < 0.05` AND
- `theta_eff > 0.1 rad` AND
- per-fact retrieval for INIT-set facts (rotated forward) >= 0.7 cosine to original cb-encoded target

### HARD-FAIL (any of):
- `delta_spectrum > 0.3` (W remade, not rotated)
- `theta_eff < 0.01 rad` (rotation negligible)
- per-fact retrieval for INIT-set < 0.3 (consistent with Regime 2 catastrophic)

### MIDDLE-BAND
- partial rotation with per-fact retrieval 0.3 - 0.7: triggers follow-up on which fact-classes rotate (cross-block vs within-block).

**Recommendation**: do NOT pre-authorize. File as opportunistic-only candidate AFTER higher-priority Tier-1 dispatches (Multi-tenant smoke, DP smoke, DR smoke).

---

## Cap_map implications

### Recommended: NO ADDITIONAL CAP_MAP CHANGES from this 2x drill.

PP-3 caveat from v318 (already recorded by closure note) is sufficient. This 2x drill confirms but does not extend it.

### Recommended annotation (if orchestrator wants to lock in the theoretical-layer closure):

> PP-3 v319 annotation (2x review confirmation): rotation-as-CF-prevention path closed at BOTH observable layer (codebook_usage_hist_drift_l1 is rotation-invariant) AND theoretical layer (consistent rotation = identity; inconsistent rotation = catastrophic; rotation-noise CF benefit not significant at 5-seed N=512 sweep, mean diff +0.016 std 0.059). C5 SPECULATIVE bonus path FULLY-CLOSED with P_rotation_masked=0.04. No targeted probe authorized. PP-3 primary axis unchanged.

### What stays open

- PP-3 primary path: compliance-driven audit-rotation primitives (Phase 2 design, separate testbed track).
- CF as a substrate question: OPEN; C1-C4 candidates from Round 2 Drill 6 remain active. This 2x drill closes C5 only.
- Targeted W-rotation experiment design: filed as opportunistic-only; NOT recommended to authorize now.

---

## Cheap probe authorization request

**NOT REQUESTED.** Both layers (observable + theory) close the path. Capacity should be redirected to higher-priority candidates.

**IF an opportunistic future drill is desired**: cheapest path is to modify `exp_sustained_workload_24h_baseline` to save `W_init` and `W_final` (adds ~256 MB to the artifact). Then compute observables B (orthogonality) and E (per-fact retention) post-hoc analytically. Cost: ~$0.10 for the modified run + $0.01 analytic. But the prior (P=0.04) does not motivate spending this capacity.

---

## Citations / verified evidence

| Source | Used for |
|---|---|
| `notes/routed_completed/research_pp3_v2_log_decomposition_v1_2026-06-01.md` | Closure note being 2x-reviewed |
| `data/v2_sustained_metrics.json` | 0.911 observed value; 4-key summary (no W matrix saved) |
| `experiments/_workload_harness.py` lines 72-130 | DenseStore class; W = sum outer(v_i, k_i) / N; rank-1 add/sub updates |
| `experiments/exp_sustained_workload_24h_baseline_v1_n4096.py` lines 279-297 | codebook_usage_histogram + _hist_l1_drift definitions |
| `experiments/exp_sustained_workload_24h_baseline_v1_n4096.py` lines 380-435 | Op-loop (no rotation primitive applied) |
| `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` Drill 6 C5 line 129 | Source of original P=0.28 SPECULATIVE estimate |
| `notes/substrate_capability_map.md` v316 | Free-probability framework REFUTED at substrate finite-N |
| In-line micro-simulation (this drill) | Regime 1/2/3 retention numerics; 5-seed N=512 sweep |

**Verified citation count**: 7 internal + 1 in-line numerical.

---

## Final closure

- Observable-invariance argument: VALIDATED.
- Alternative-observable inventory: 8 candidates ranked; top 3 (B, A, E).
- CF-prevention-via-rotation theoretical claim: INDEPENDENTLY REFUTED in 3-regime analysis.
- Closure confidence: **FULLY-CLOSED**.
- P_rotation_masked: **0.04 deflated**.
- Probe recommendation: **NONE** (capacity to higher-priority Tier-1).
- Cap_map: optional v319 annotation; not required.

---

## Files produced

- This synthesis: `notes/research_pp3_v2_log_2x_review_v1_2026-06-01.md`
- Closed routing: `notes/research_to_strategy_pp3_v2_log_2x_review_2026-06-01.md`

## Wall

~40 minutes (read closure + verify math + 3-regime CF check + multi-seed sweep + write).


---

Acted-on 2026-06-01: 2x review FULLY-CLOSED at both observable + theoretical layers; PP-3 closure annotation added v320


Acted-on 2026-06-01: 2x review FULLY-CLOSED at both observable + theoretical layers
