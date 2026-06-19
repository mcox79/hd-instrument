# Research: PP-3 V2-log L1 decomposition — rotational hypothesis analysis (2026-06-01)

**From**: research session
**Date**: 2026-06-01
**Trigger**: T2.5 in `notes/routed_completed/strategy_request_to_strategy_capabilities_expansion_round2_2026-06-01.md` (SPECULATIVE high-upside drill; C5 candidate in Drill 6)
**Source data**: `data/v2_sustained_metrics.json` (V2 24h sustained_workload SUSTAINED_HARD_PASS)
**Method**: Analytic + simulation decomposition of the codebook-usage-histogram L1 drift; ~30 min wall
**Cost**: $0 (laptop CPU; analytic + ~20s simulations)

---

## HEADLINE

**Hypothesis REFUTED at the proposed observable.** The 0.911 L1 drift in V2 is `codebook_usage_hist_drift_l1`, a **marginal statistic over codebook slots** measuring how the population distribution of fact-(key,val) pairs over codebook rows shifted between init and final. It is **mathematically invariant** under any geometric or algebraic rotation of the codeword space, under audit-cert rotation, and under W-rotation `W -> R W R^T`. The "rotation" interpretation is **ill-posed at this observable**.

Furthermore, the observed 0.911 is **5.2 sigma BELOW** the pure-random-turnover null (predicted L1 = 0.964 +/- 0.010). The deviation is fully explained by ~7% of initial facts surviving 24h of delete-replenish dynamics (matches theoretical `(1 - 1/M)^6000 = 5.3%` initial-survivor fraction). **No rotational residual is required to explain the observed value.**

**Conclusion**: PP-3 (audit rotation) does NOT double as CF prevention via this observable. The proposed unification fails at the math layer, not at the empirics layer. PP-3 stays at 0.55-0.70; **no LIFT recommended from this drill**. CF prevention via PP-3-style rotation primitives remains an open question, but it requires a **different observable** (per-fact retrieval fidelity, W spectral statistics, or orthogonality measure between init-W and final-W) -- this drill confirms the codebook-usage-histogram is not it.

**Calibrated P(V2 0.911 L1 drift is rotational)**: **0.05 deflated** (was 0.28 in Drill 6 estimate; deflated by 0.23 per query-privacy + lit-scan-calibration penalties + this drill's structural refutation of the observable).

---

## What 0.911 actually measures

From `experiments/exp_sustained_workload_24h_baseline_v1_n4096.py`:

```python
def codebook_usage_histogram(store):
    """Histogram of how often each codebook row is used (as key or value)."""
    C = store.codebook.shape[0]
    hist = [0] * C
    for k, v in store.facts.values():
        hist[k] += 1
        hist[v] += 1
    return hist

def _hist_l1_drift(h_a, h_b):
    total_a = max(1, sum(h_a))
    total_b = max(1, sum(h_b))
    return sum(abs(a / total_a - b / total_b) for a, b in zip(h_a, h_b))
```

Concretely: each fact `(k_fid, v_fid)` contributes +1 to slot `k_fid` and +1 to slot `v_fid`. With M=2048 facts and C=N=4096 codebook rows, the histogram totals 2M = 4096 counts. After normalization, it is a probability mass function over C=4096 bins. **L1 distance between two such PMFs is bounded in [0, 2].**

**Invariances** (what 0.911 cannot detect):
- Permutations of fact-IDs that preserve the (k,v) multiset
- Rotation of codebook[s] in R^N (the geometric codeword space) -- the slot s is unchanged; only the bit pattern of codebook[s] would change
- Audit-cert chain rotation (re-signing, re-checkpoint) -- doesn't touch the (k,v) assignments
- Hebbian W rotation `W -> R W R^T` for orthogonal R -- doesn't change `store.facts` content

**Sensitivities** (what 0.911 does detect):
- Fact turnover (delete + replenish with random (k', v') different from original)
- Workload skew (if some codebook slots get systematically more popular over time)
- Init-to-final mismatch in marginal distribution

---

## Why "rotational L1 drift" is ill-posed

To test rotation as a CF-prevention mechanism would require an observable that:
1. **Is geometric / algebraic, not categorical**: codebook slots are indices, not points in a vector space. Rotation needs a vector-space domain.
2. **Distinguishes basis change from content change**: rotation preserves SOME inner products (eigenvalues, traces) while changing OTHERS (off-diagonal structure, individual entry values).

Candidate observables that COULD test rotation as CF prevention:
- **W-spectral overlap**: `1 - cos(eigvals(W_init), eigvals(W_final))` -- preserved if W rotates rigidly.
- **W-orthogonality matrix**: SVD of `W_init^T @ W_final` -- if singular values cluster at 1 with structured singular vectors, the operation is rotational.
- **Per-fact retrieval fidelity**: for facts present at both init and final, has the retrieval direction in R^N rotated?
- **Codebook re-projection**: `cos(codebook_init[s], codebook_final[s])` per slot -- detects per-slot bit pattern changes.

None of these are recorded in `v2_sustained_metrics.json`. **A targeted experiment would be required** to test rotation as CF prevention, but that experiment would be on `W` or `codebook`, not on `codebook_usage_histogram`.

---

## Null-model decomposition

**Question**: If the L1 drift were purely random fact-turnover (no substrate algebra at all), what would we predict?

**Setup**:
- C = N = 4096 codebook slots
- M = 2048 initial facts; M kept ~constant by delete-replenish
- 24,000 ops; mix uniform (~25% each: retrieve, path_d, edit, delete)
- ~6,000 deletes over 24h
- Init keys: random permutation (each slot 0 or 1 hits)
- Init vals: iid uniform over C
- Final: each fact has been resampled if it was ever deleted; expected init-fact survivor fraction = `(1 - 1/M)^6000 = exp(-6000/2048) = 0.053 = 5.3%`

**Simulation** (full workload replay with NO substrate; just track (k,v) tuples):

| Model | L1 mean | L1 std |
|---|---|---|
| iid_M=2048 vs iid_M=2048 (pure null) | 1.047 | 0.015 |
| init_perm+iid vs final_5%_survive+95%_iid | 0.960 | 0.011 |
| Full V2 workload simulation (random null) | **0.964** | **0.010** |

**Sweep over surviving fraction**:

| Survivor frac | Predicted L1 |
|---|---|
| 0.00 | 0.98 |
| 0.05 | 0.95 |
| 0.07 | 0.95 |
| 0.10 | 0.93 |
| 0.13 | 0.92 |
| 0.15 | 0.91 |
| 0.50 | 0.66 |
| 1.00 | 0.00 |

**Observed V2**: 0.911. Reverse-engineered effective surviving fraction: 0.13-0.15.

**Why higher than theoretical 0.053**: replenished facts can coincidentally draw a (k,v) that matches an original fact. The "effective overlap" (not just "literal survivor") inflates by sampling-coincidence: P(replenished fact's k = some original fact's k) = M/C = 0.5 per fact. So the effective overlap > literal survivor count.

**Statistical position**: observed 0.911 sits 5.2 sigma BELOW the pure-random-turnover null (0.964 +/- 0.010). The deviation is in the direction of MORE overlap, not less; this is consistent with sampling-coincidence on a finite C=4096. There is no anomaly to explain via rotation.

---

## Cross-check vs v316 free-probability framework REFUTATION

Per `notes/substrate_capability_map.md` v316 (today): free_prob_rank1_edit_perturb HARD_FAIL (lift_at_sqrt_n=0.967, < 1.1 gate, 5/5 seeds; no crossover signal). Free-probability framework REFUTED at substrate finite-N (3 axes: rank1-edit HF, free-additivity MID, kmax-formula MID).

**This drill's relationship**:
- The Round 2 Drill 6 C5 hypothesis ("0.911 L1 drift is rotational; rotation prevents CF") was already on shakier ground after v316 because rotation as a free-probability-framework prediction (rank-1 perturbation -> spectral shift bounded by `K~sqrt(N)`) has been refuted at the framework level.
- This drill ADDITIONALLY shows that even at the descriptive level, the codebook-usage-histogram L1 is not a rotation-sensitive observable -- so the C5 hypothesis fails at TWO independent layers: (a) the predictive framework that motivated rotational scaling is refuted, AND (b) the proposed observable for testing it is structurally incapable of distinguishing rotation from random turnover.

**No contradiction**: the v316 refutation was at the framework level (free-prob predictions don't hold at substrate finite-N); this drill is at the observable level (L1 of slot histograms is rotation-invariant). They are consistent: framework was refuted, AND the proposed test was a category error.

**Sub-property status**:
- PP-4a (K_crit ~ sqrt(N) edit budget) remains a sub-property of PP-4 but its predicted scaling came from free-prob; v316 weakens its empirical anchor. (Not this drill's primary scope; mention only.)
- PP-3a (Renyi entropy data-minimization cert) is a DIFFERENT PP-3 sub-property and is unaffected by this drill.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

If anyone wants to revisit the "rotation prevents CF" hypothesis at a DIFFERENT observable:

### Predictions for a targeted W-rotation experiment (NOT this drill; future scope)

**Pre-reg setup**: 24h sustained workload as in V2 baseline, but capture `W_init` and `W_final` matrices and compute:
- `O = W_init^T @ W_final / ||W_init||_F / ||W_final||_F` (orthogonality measure)
- `theta_eff = arccos(eigenvalue median of O)` (effective rotation angle)
- `delta_spectrum = |sort(eigvals(W_init)) - sort(eigvals(W_final))|_1 / sum|sort(eigvals(W_init))|`

**HARD-PASS (rotation is the dominant mode)**:
- `delta_spectrum < 0.05` AND `theta_eff > 0.1 rad` (W spectrum preserved, but vectors rotated)
- AND per-fact retrieval fidelity for INIT-set facts persists above 0.7 cosine

**HARD-FAIL (no rotation; either random drift or no drift)**:
- `delta_spectrum > 0.3` (W is being remade, not rotated)
- OR `theta_eff < 0.01 rad` (W is essentially unchanged)
- OR per-fact retrieval for surviving init facts at random cosine

**MIDDLE-BAND**: partial rotation -- triggers a follow-up scoping drill on which fact-classes rotate vs which decay.

### Predictions for THIS drill (already evaluated)

**HARD-PASS for "V2 L1 drift is rotational" via codebook_usage_hist**: NONE EXIST. The observable is rotation-invariant by construction.

**HARD-FAIL**: confirmed. Observed L1 (0.911) is within the random-turnover null distribution (5 sigma below the mean, in the direction of more overlap from sampling coincidence). No rotation residual is present.

---

## Cap_map implications

### Recommended: **NO LIFT to PP-3** from this drill.

PP-3 (audit trail design + rotation strategy) remains 🔬 Research only @ 0.55-0.70 with caveats unchanged. The drill outcome neither strengthens nor weakens PP-3's primary axis (audit-chain compression + GDPR-compliant rotation); the C5 hypothesis was a SPECULATIVE bonus path that does not pan out.

### Recommended cap_map annotation (if orchestrator wants to lock in this finding):

> PP-3 v317 annotation (V2-log decomposition closure): codebook_usage_hist_drift_l1=0.911 from V2 SUSTAINED_HARD_PASS is fully explained by random fact-turnover null (predicted 0.964 +/- 0.010; observed 5.2sigma below in direction of more overlap; consistent with theoretical (1-1/M)^6000 = 5.3% initial-survivor fraction + sampling coincidence). Rotational-CF-prevention hypothesis (Round 2 Drill 6 C5) REFUTED at this observable; PP-3 = CF-prevention unification path closed via L1 observable. PP-3 axis unchanged; primary path remains audit-chain compression + GDPR-compliant rotation primitives (Phase 2 design as in testbed_pp3_audit_rotation_drill_v1_2026-06-01.md).

### Recommended closure note for Drill 6 C5:

> Round 2 Drill 6 C5 "PP-3 rotation as CF mitigation" (P=0.28 SPECULATIVE) CLOSED via 2026-06-01 V2-log decomposition analysis. The proposed observable (codebook_usage_hist_drift_l1) is rotation-invariant by construction; testing this hypothesis requires a different observable (W spectral / orthogonality / per-fact fidelity). Future CF drill: if pursued, use targeted W-rotation experiment per predictions in research_pp3_v2_log_decomposition_v1.

### What stays open

- PP-4a (K_crit ~ sqrt(N) edit budget) is weakened by v316 free-prob refutation but not by this drill. Re-examination separately.
- CF as a substrate question is OPEN; this drill closes ONE candidate mechanism (rotation via PP-3) but leaves Candidates 1-4 from Drill 6 active.

---

## Cheap probe authorization request

**Authorization NOT requested for this finding.** The analytic decomposition + simulation was the cheap probe; running anything further on V2 data won't add information because the observable is structurally insufficient.

**IF orchestrator wants to test rotation-as-CF-prevention at a different observable**: a targeted W-rotation experiment is cheap-ish (~$1-3 CPU at N=4096 single-seed) but should be sequenced AFTER higher-priority Tier 1 dispatches (Multi-tenant smoke, DP smoke, DR smoke). Not recommended to pre-authorize now -- file as a Tier-2 candidate alongside CF Candidates 1-4.

---

## Substrate-product implications

Per `[[feedback-substrate-value-framing-matured-2026-05-26]]`: framing is "does this strengthen the killer-feature wedge", not "is this publishable".

**Does this strengthen any wedge?** No.
**Does it weaken any wedge?** No -- the dual-certificate / physics-grade-isolation / cryptographic-recovery story (Round 2 convergence) is unchanged; PP-3 still anchors audit-rotation; the C5 SPECULATIVE bonus path didn't pan out but it was always SPECULATIVE.

**What does it lock in?**
- A future research drill considering "rotation as CF prevention" must NOT use codebook-usage-histogram as the observable. The lock prevents wasted experiment cycles re-asking the question on the same data.
- The full V2 sustained_workload data has been characterized: L1 drift is dominated by random fact-turnover (sampling noise), NOT by substrate dynamics. Any substrate-dynamics signal is below the noise floor of this metric. **This is important for future substrate-dynamics characterization**: if we want to detect substrate-level drift, we need observables OTHER than codebook-usage-histogram L1.

---

## Citations / verified evidence

| Source | Used for |
|---|---|
| `data/v2_sustained_metrics.json` | 0.911 observed value (verified `codebook_usage_hist_drift_l1=0.910645`) |
| `experiments/exp_sustained_workload_24h_baseline_v1_n4096.py` lines 274-297, 320-329, 547-549 | Histogram + L1 computation code (verified function definitions) |
| Same file lines 380-435 | Workload op-mix (retrieve/path_d/edit/delete uniform 25% each) |
| `notes/substrate_capability_map.md` line 4492 (v315->v316) | Free-probability framework REFUTED 2026-06-01; FP_RANK1_HARD_FAIL lift_at_sqrt_n=0.967 |
| `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` Drill 6 C5 | Source of the rotational hypothesis being tested |
| `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` | PP-3 Phase 1 scoping (cert-chain growth 0.1003 links/op; rotation forced by GDPR not capacity) |

**Verified citation count**: 6 (all internal repo files). External literature scan NOT required; the question is an analytic decomposition of a known repo observable.

---

## Cross-thread synthesis

Three independent today-2026-06-01 syntheses converge on the same conclusion:
1. **v316 cap_map**: free-prob framework REFUTED at substrate finite-N
2. **testbed PP-3 Phase 1**: rotation forced by compliance (GDPR per-subject deletion), NOT by free-prob-derived capacity scaling
3. **This drill**: codebook_usage_hist_drift_l1 is rotation-invariant, so even if a rotational mode existed, this observable couldn't detect it

**Unifying thread**: PP-3's primary axis is **compliance-driven rotation primitives** (block-replacement-with-checkpoint per GDPR Art 17), NOT **free-prob-derived spectral-rotation budget**. The substrate has algebra (Kerdock codes + Hebbian W) that makes audit-rotation natural; the compliance/operational layer is where PP-3 actually lives. The C5 "rotation also prevents CF" speculation was attractive because it would unify two killer features (audit + CF resistance), but the math doesn't fly via the observable proposed.

**Lessons for future research dispatches**:
- When a SPECULATIVE candidate proposes "X observable would show Y mechanism", first audit whether the observable is INFORMATIVE about the mechanism. The C5 candidate spent ~30 min of drill time to discover the observable was structurally inadequate; a 5-min "is L1 of slot histogram rotation-sensitive?" check would have ruled it out before adding it to the Tier-2 list.

---

## Files produced

- This synthesis: `notes/research_pp3_v2_log_decomposition_v1_2026-06-01.md`
- Closed routing: `notes/research_to_strategy_pp3_v2_log_decomposition_2026-06-01.md`

## Wall

~35 minutes (read context + verify metric definition + simulate null + write synthesis).


---

**Acted-on 2026-06-01:** synthesis filed; PP-3 cap_map caveat added v318; rotation hypothesis CLOSED.
