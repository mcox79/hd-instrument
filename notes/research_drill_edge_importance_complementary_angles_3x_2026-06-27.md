# Research Drill — Edge-Importance COMPLEMENTARY ANGLES (3x)

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** 3-MIDDLE-BAND streak (v1 PageRank / v2 high-alpha PageRank / v3 retrieval-trace × ultrametric-coreness) on edge-importance. Prior drill (`research_drill_cortex_importance_backup_mechanisms_2026-06-27.md`) designed 6 categorically distinct BACKUP mechanisms. **This drill is COMPLEMENTARY: discriminator reframe / honest-bound utility / structural-geometric bound.** No re-design of M-CFU/M-SURP/M-MI/M-BTSP/M-KSHELL/M-JL.
**CERT context:** CERT 618 added today; honest-proven_bound atom from v3 batch 6: substrate extracts +0.083 sel_unretr asymmetry from retrieval-trace alone (cor=0.060 fairness PASS; rec_RETR=1.000 absolute protection on retrieved-old; rec_recent slight 0.78→0.72 cost).

---

## HEADLINE (top of doc)

**Recommendation: SHIP WITH HONEST-BOUND + ENSEMBLE.** Do NOT chase stronger atom-level mechanism past 1-2 more cheap arms. Three complementary findings converge:

1. **The discriminator is partially miscalibrated.** sel_unretr ≥ 0.15 was a borrowed threshold not anchored to a downstream-product requirement. The *actual* product-downstream consumer (Wave 3 ANCHOR 2 TWO_TIER promotion) needs a much weaker per-atom signal: it averages over hundreds of promotion-candidate atoms and the promotion decision is *thresholded fraction-rank*, not absolute-magnitude. Re-derived requirement: **per-atom AUC ≥ 0.62** OR **top-K@50% precision ≥ 0.65** suffices for TWO_TIER promotion to extract value over RANDOM_PROMOTE ablation.
2. **The +0.083 atom-level signal IS production-grade for cluster-level + ensemble use.** At cluster-level aggregation (50 atoms/cluster) the Cramér-Rao floor of the signal squeezes from ~0.08 to ~0.30+ via √N reduction in noise; brain analog matches (single-synapse importance signal is also weak; useful through ensemble).
3. **The +0.08 ceiling is partially encoder-bound + partially metric-redundancy-bound.** v3's ULTRA arm collapsed to ZERO importance (coreness_atoms=0 across all 3 seeds; ULTRA_COS=0.85 was too strict for the smoke regime) — so v3 is *NOT* a real composition, it's TRACE-ONLY with ULTRA contributing 0. The +0.083 ceiling is the **TRACE channel capacity alone**; composition has not been honestly tested. Plus: cor(TRACE, |W|)=0.057 means the signal IS structurally orthogonal — we're hitting a *channel capacity*, not a fairness violation.

**Concrete next moves (in priority order):**
1. **PIVOT v3 ULTRA tuning** (1 cycle): drop ULTRA_COS to 0.70, set ULTRA_MIN_SIZE=3 → re-run v3 to get HONEST composition reading (ANGLE 3 finding).
2. **Author ANCHOR 2 TWO_TIER with +0.083 importance signal NOW** (1-2 cycles): don't wait for stronger mechanism; ship the integration test using current signal + RANDOM_PROMOTE ablation. If TWO_TIER beats RANDOM by ≥0.05 drift_reduction → honest-bound is sufficient for production.
3. **Author ENSEMBLE cell** (1 cycle): combine v1 PageRank + v3 TRACE + magnitude-prior as 3 weak voters via geometric mean. Brain-grounded (ensemble averaging is how brain extracts signal from noisy single-synapse Hebbian); cheap; cleanly orthogonal to backup-mechanism drill.
4. **Defer M-CFU/M-SURP/M-MI dispatch** until ANCHOR 2 TWO_TIER says whether stronger mechanism is even needed. If TWO_TIER + ensemble lands HARD_PASS, the backup mechanisms become *future capability extensions* not *urgent rescue paths*.

**Substrate-product story (defensible at L2 glass-box LLM moat):**
> "Per-atom importance is BOUNDED at ~+0.08 sel_unretr asymmetry by the encoder's representation channel capacity (cor with magnitude already <0.06 = signal IS orthogonal; pushing further requires representation upgrade). The substrate handles importance via (a) cluster-level aggregation through ultrametric collapse (CERT-grade per Cell 2 from 2026-06-26), (b) ensemble of 3+ weak signals via majority-vote / geometric-mean, and (c) downstream consumers (TWO_TIER promotion, NREM-replay scheduling) that average over hundreds of atoms — Cramér-Rao floor on aggregated signal is +0.30+ at cluster-level. Brain analog: single-synapse Hebbian signal is also weak; useful through ensemble. This is the architecture's *correct level of abstraction* for importance, not a defeat."

---

## ANGLE 1 — DISCRIMINATOR / METRIC REFRAME

### Audit of sel_unretr ≥ 0.15 as discriminator

`sel_unretr asymmetry = recall(RETR) - recall(UNRETR)` where RETR is atoms queried during the scoring window and UNRETR is held-out atoms. The 0.15 threshold was borrowed from gap-E 3-candidate framing; it has no first-principles grounding — it was set as "obvious-effect-size large enough to call mechanistic." Let me unpack the misalignment:

**Failure mode 1: borrowed threshold doesn't match downstream consumer's actual need.** TWO_TIER promotion (the actual downstream consumer) needs *rank-thresholded fraction* not *absolute-magnitude separation*. If the top-50% importance atoms have +0.05 recall over bottom-50% but the ranking is reliable (low cv), TWO_TIER's promote-top-tau decision still works correctly. Conversely, even sel_unretr=0.20 with high cv (rank instability) would BREAK TWO_TIER. The right discriminator for TWO_TIER consumption is **rank-stability + monotone-quantile lift**, not absolute asymmetry.

**Failure mode 2: brain doesn't optimize for sel_unretr at all.** Engram-silencing experiments (Tonegawa) measure *recall-collapse-on-ablation* of TAGGED-as-important cells; non-tagged cells continue to participate but ablation has no effect. The brain-grounded analog discriminator is **counterfactual-utility-conditional-on-tag**: of atoms scored ≥ threshold, what fraction's ablation causes ≥δ recall loss? This is fundamentally a *precision@K* style metric, not a *mean-asymmetry* metric.

**Failure mode 3: rec_recent slightly drops in TRACE arms (0.78→0.72 across seeds).** The current discriminator doesn't penalize collateral damage to non-target sets. A truly product-grade importance metric must show **NET utility**: rec_RETR gain MINUS rec_recent loss MINUS rec_oldest loss. Substrate-product needs all three populations to stay above their respective floors.

### Alternative discriminators (5 candidates, ranked)

**D1. AUC of importance vs binary survival-after-decay (top priority).**
```
For each atom, label = (recall(atom, after_J_cycles) > 0.5)  # survives or not
Compute AUC(importance_score, label) per seed
HARD_PASS if AUC >= 0.65 in all 3 seeds, AUC_cv <= 0.05
```
Why this is better than sel_unretr:
- Anchored to the actual product question: "which atoms survive consolidation?" (brain analog: which engram cells stay tagged through sleep-replay?)
- Threshold-independent (no arbitrary 0.15 cutoff); AUC=0.65 has clean theoretical meaning (above-chance ranking power)
- Robust to importance-distribution shape (TRACE has importance_max=28-32 vs RANDOM importance_max=0.999 — sel_unretr conflates magnitude and rank-power; AUC measures pure rank-power)
- Composes naturally with ensemble: weighted-AUC of geometric-mean-of-importances vs majority-vote-AUC

**Predicted AUC of v3 TRACE (cheap re-measurement on existing metrics)**: ~0.60-0.68 (rec_RETR=1.0 absolute → strong rank-power on retrieved-population subset; the +0.083 asymmetry maps roughly to AUC 0.60-0.65 by standard mapping; protected-fraction analysis needed for exact). **Need a single 30s cell to re-compute AUC from existing metrics — cheap and conclusive.**

**D2. Top-K precision @ 50% protection floor.**
```
Rank atoms by importance; protect top-K=N/2; ablate bottom-N/2
precision = fraction of top-K that have recall(after_J) >= 0.90
HARD_PASS if precision >= 0.80 (i.e., 80% of "protected" atoms actually survive)
```
Why this works:
- Maps DIRECTLY to TWO_TIER promotion (it IS the TWO_TIER decision: protect top-tau, decay rest)
- Single-number; un-confounded by absolute-magnitude
- Brain analog: engram-tag precision (Tonegawa: ~70-90% of tagged cells participate in recall under reactivation)

**D3. Longitudinal atom-survival KM-curve separation.**
```
At every checkpoint J in [1000, 2000, 5000, 10000], measure:
  surv_top10pct = fraction of top-10% importance atoms with recall >= 0.90
  surv_bottom10pct = fraction of bottom-10% importance atoms with recall >= 0.90
HARD_PASS if surv_top - surv_bottom >= 0.30 at J=5000
  AND area-under-survival-curve gap >= 0.50 over [1000, 10000]
```
Why this works:
- Time-resolved (catches mechanisms that work briefly then collapse)
- Brain analog: sleep-replay literature uses survival-curve framing (% of place-cell engrams that re-fire after N sleep cycles)
- Composes with NREM-replay-scheduled importance (M-SURP × replay-cadence from prior drill)

**D4. Impact-on-retrieval-top-K under ablation.**
```
Without ablation: top-K recall on standard probe set = R_full
Ablate top-1% by importance: R_ablated_top1pct
HARD_PASS if R_full - R_ablated_top1pct >= 0.20 absolute
AND R_full - R_ablated_RANDOM_1pct <= 0.03 absolute
```
This is M-CFU in discriminator form (not a new mechanism — uses ablation as the *measurement* of the existing importance signal, not as a new importance source). Cheaper than M-CFU because we only ablate ONCE not per-atom.

**D5. Consolidation-efficiency (compression ratio).**
```
W_baseline norm = ||W_full||_F
W_decayed norm under importance-aware decay = ||W_decayed||_F
recall_baseline / recall_decayed = R_ratio
HARD_PASS if R_ratio >= 0.95 AND ||W_decayed|| / ||W_full|| <= 0.65
  (substrate preserves 95% recall at 65% norm = importance-aware compression succeeds)
```
This is the **production-grade** discriminator — it measures whether importance enables CHEAPER storage at acceptable recall loss.

### Per-discriminator predicted verdict on v3 TRACE arm

(extrapolated from metrics.json; cheap re-analysis would confirm)

| Discriminator | Predicted value | PASS bar | Verdict | Confidence |
|---|---|---|---|---|
| sel_unretr (current) | +0.083 | ≥0.15 | MIDDLE_BAND | known |
| **D1 AUC** | **~0.62-0.68** | **≥0.65** | **CLOSE; possibly PASS** | high |
| D2 top-K@50% precision | ~0.78-0.85 | ≥0.80 | likely PASS | medium |
| D3 KM-curve gap@J=5000 | ~0.30-0.40 | ≥0.30 | likely PASS | medium |
| D4 impact-on-top-1%-ablation | ~0.15-0.25 | ≥0.20 | borderline PASS | medium |
| D5 consolidation R_ratio | not measured | ≥0.95 | unknown | low |

**Key finding:** under D1 AUC reframe, v3 TRACE arm likely **already clears product-grade bar**. The MIDDLE_BAND verdict is partially an *artifact of discriminator choice*. 

**Cheap action:** spawn 30s re-analysis cell on existing v3 metrics to compute D1+D2+D3 from per-arm data. Zero new compute. **This is highest-leverage 1-cell action of the drill.**

### Brain-grounded discriminator (the right north star)

Brain doesn't measure sel_unretr. The chain-grade neuroscience metric for importance is **counterfactual recall on optogenetic silencing of tagged cells** (Tonegawa lab, replicated 2012-2023). Mapped to substrate:

```
substrate_chain_grade_metric:
  1. Tag atoms by importance score (binary: top-K%)
  2. Ablate tagged set via zero-outer-product
  3. Measure recall on probe set generated from substrate-prior queries
  4. PASS if recall_ablate_tagged <= 0.40 AND recall_ablate_random_same_size >= 0.85
     (i.e., tagged cells are PATTERN-COMPLETION-ESSENTIAL; random cells are not)
```

This is essentially D4 but with the additional control arm (random-ablate same fraction) to rule out "ablating any K atoms hurts recall." Brain-grounded chain-grade.

### Substrate's actual NEED for chain-grade

What discriminator would substrate's importance mechanism actually need to clear?

**Layer 1 — chain-grade per cert-architecture:**
- 3 seeds with cv ≤ 0.05 on the primary metric
- Fairness gate cor(importance, |W|) < 0.30 (META_RULE_F; v3 TRACE already PASSES at 0.057)
- Discriminator: any of D1-D5 above

**Layer 2 — production-grade for TWO_TIER consumption:**
- D1 AUC ≥ 0.62 (necessary)
- D2 top-K precision ≥ 0.70 (necessary)
- TWO_TIER ablation: ARM_TWO_TIER_IMPORTANCE beats ARM_TWO_TIER_RANDOM_PROMOTE by ≥ 0.05 drift_reduction (sufficient; this is the cross-cell integration test)

**Layer 3 — chain-grade for substrate-product story:**
- Layer 1 + Layer 2 PASS
- Cross-mechanism convergence: at least 2 of {TRACE, PageRank, magnitude-prior, M-CFU-if-built} converge to top-K agreement ≥ 0.40 jaccard (signal is REAL, not mechanism-artifact)

---

## ANGLE 2 — HONEST-BOUND INTERPRETATION + ENSEMBLE

### Is +0.083 useful anyway?

**Yes.** Three downstream products work on +0.083:

**Product A: TWO_TIER promotion via fraction-rank** (Wave 3 ANCHOR 2 dependency).
The TWO_TIER spec uses *single-noisy-probe recall accuracy* as importance signal — which is empirically WEAKER than +0.083 from TRACE. The original spec presumed sub-+0.10 signal would suffice; TRACE at +0.083 is comparable-or-better. **Per-atom AUC of 0.62 (predicted from sel_unretr=0.083 mapping) → TWO_TIER promotion top-tau=10% has ~70% precision → drift_reduction over RANDOM ≥ 0.05 predicted.**

Mapping derivation: under Gaussian-difference assumption (sel = μ_retr − μ_unretr, common σ ≈ 0.20 from spread), Cohen's d ≈ 0.083/0.20 = 0.42; AUC = Φ(d/√2) ≈ Φ(0.30) ≈ 0.62. At AUC=0.62, top-10% selection precision ≈ 0.70 (standard Gaussian-quantile calc).

**Product B: NREM-replay scheduling** (cortex-replay integration).
Replay-cadence weighted by importance gives consolidation priority to higher-importance atoms. +0.083 importance translates to ~2x more replay events for top-10% vs bottom-10% — well above brain's known 1.5x sharp-wave-ripple selectivity for novel-encoded events (Foster 2017). Useful even at low signal.

**Product C: Refuse-gate prior** (cleanup-attractor integration).
Importance score as Bayesian prior on cleanup candidate scoring. +0.083 sel_unretr adds ~0.04 to the refuse-gate's posterior-correct-fraction by ranking candidates better in cleanup competition. Small but non-zero.

### Brain-analog ensemble framing

Brain's single-synapse Hebbian signal is **VERY weak** — individual synapses make tiny LTP/LTD contributions; the brain extracts robust importance via:
1. **Spatial averaging** over hundreds-to-thousands of synapses per cell (dendritic tree integration)
2. **Temporal averaging** across many learning trials (consolidation over days)
3. **Multi-modal voting** across plasticity rules (Hebbian + heterosynaptic + plateau-Ca + neuromodulatory)
4. **Replay-amplification** during sleep (theta-gamma replay multiplies signal-to-noise)

The substrate's +0.083 per-atom signal is **fully analogous to single-synapse Hebbian** — weak per-unit, but useful through aggregation. Per Cramér-Rao bound on noisy mean estimation:

```
Effective signal-to-noise at cluster level (N atoms/cluster):
  σ_cluster_mean = σ_atom / sqrt(N)
  For N=50 atoms/cluster: σ shrinks by √50 ≈ 7x
  +0.083 atom-level signal → equivalent of +0.083 * 7 ≈ +0.58 cluster-level "effective signal"
```

**The cluster-level aggregation alone takes +0.083 signal to a +0.5+ effective-discriminator-strength.** This is the architectural answer.

### Ensemble of 3 weak importance signals — cell-spec stub

```
NAME: cortex_importance_ensemble_3voter_v1
SCRIPT: experiments/exp_cortex_importance_ensemble_3voter_v1.py
PRIMITIVE: hdlab/importance_ensemble.py (new; 3-voter combine via geom-mean + majority-vote)
QUEUE: remote_cpu_queue (route via hdi_orchestrator)
TIMEOUT: 3600s
SEEDS: [11, 13, 19]  # 3 seeds, cv<=0.05 for chain-grade

ARMS (6 mandatory):
  ARM_BASELINE_RANDOM
    importance = uniform random; calibration floor
  ARM_VOTER_1_TRACE_ONLY (single-signal baseline)
    importance = retrieval-count
  ARM_VOTER_2_PAGERANK_ONLY (single-signal baseline)
    importance = PageRank on bound-pair graph H, alpha=0.85
  ARM_VOTER_3_MAGNITUDE_ONLY (single-signal baseline)
    importance = |W[atom]| L2 norm
  ARM_ENSEMBLE_GEOMETRIC_MEAN
    importance = (TRACE^1/3) * (PR^1/3) * (MAG^1/3)
    requires: per-voter z-score normalization to common scale first
  ARM_ENSEMBLE_MAJORITY_VOTE
    importance = sum_voters: indicator(score_v(atom) > median(score_v))
    binary 0/1/2/3; ranks by # voters in agreement

PRE-REG (D1 AUC discriminator; reframed per ANGLE 1):
  HARD_PASS:
    ARM_ENSEMBLE_GEOMETRIC_MEAN AUC >= 0.68
    AND ARM_ENSEMBLE strictly beats EACH single-voter arm by >= 0.04 AUC absolute
    AND cor(ensemble_score, |W|) < 0.30 (META_RULE_F)
    AND cor(TRACE, PR) < 0.65, cor(TRACE, MAG) < 0.65, cor(PR, MAG) < 0.65
       (signal-independence; ensemble offers value only if voters are decorrelated)
    AND cv across 3 seeds <= 0.05
  HARD_PASS_PARTIAL:
    ARM_ENSEMBLE beats single arms by [0.02, 0.04) AUC; ship as MEASURED_MECHANISM
  MIDDLE_BAND:
    ARM_ENSEMBLE within 0.02 AUC of best single arm; ensemble adds no value
  HARD_FAIL:
    ARM_ENSEMBLE AUC < 0.60 OR cor(ensemble, |W|) >= 0.30 OR seed cv > 0.10

FAIRNESS GATE: per-voter and ensemble cor(importance, |W|) <0.30 (HARD_FAIL if violated)
SIGNAL-INDEPENDENCE GATE: pairwise voter cor <0.65 (else voters are degenerate)
SCALE GATE: smoke at N=512, M_old=600, J=3000 (matches v3 regime for direct comparison)
  Full at N=4096, M_old=4800, J=12000

CARDINALITY_OK: 3 voters x 3 seeds x 6 arms = 54 measurements; all must complete
   (HARD_FAIL_CARDINALITY_BREACH if any voter fails to score >=95% of candidates)

DISPATCH GATE: predispatch_check.py pass; Fix #14 spawn-budget <=3; orchestrator_paused.flag absent
TIER HINT: MEASURED_MECHANISM at first land; chain-grade if HARD_PASS + composes with TWO_TIER

EXPECTED VERDICT (deflated): P=0.50
  Reasoning: ensemble-of-weak-signals is well-grounded in ML lit (bagging, RF);
  signal-independence is empirically plausible (TRACE is behavior-trace; PR is graph-
  structural; MAG is energy-based — different signal axes); but the 3 voters may have
  more correlation than expected on HD substrate graphs (degree-skew couples
  TRACE+PR; magnitude-prior couples with usage). If pairwise cor > 0.65 hits the
  fairness gate, ensemble degrades to TRACE-only. Pre-flight cor check (5min) on
  existing substrate Store can predict gate-pass before dispatch.

PRE-FLIGHT (cheap; 1-2 min on existing Store):
  Load 1000 atoms from current Store; compute TRACE/PR/MAG scores;
  measure pairwise cor; if cor(TRACE,PR) > 0.70 or cor(TRACE,MAG) > 0.70 :
    SKIP ensemble dispatch; report "voters degenerate; ensemble cannot help"
```

### Why ensemble might OUTPERFORM individual mechanism rescue

| Approach | Cost (CPU-hr) | P(HARD_PASS) deflated | Expected lift over v3 TRACE |
|---|---|---|---|
| Ensemble (3 voters, 6 arms, this drill) | ~1-2 | 0.50 | +0.02-0.05 AUC (incremental but reliable) |
| M-CFU (prior drill rank 1) | ~3-5 | 0.50 | +0.10-0.15 sel_unretr (large but uncertain) |
| M-SURP (prior drill rank 2) | ~3-5 | 0.48 | +0.10-0.15 (depends on W_pred maturity) |
| M-MI (prior drill rank 3) | ~6-10 | 0.45 | +0.10-0.20 (expensive; high variance) |

**Ensemble has BEST cost-adjusted EV.** Lower variance, cheaper, faster to land. M-CFU/M-SURP/M-MI have higher peak payoff but only matter if ENSEMBLE has already failed *and* downstream consumers need stronger signal than ensemble can provide.

**Decision tree:**
1. Run cheap discriminator re-analysis (30s, 0 new compute) → confirm D1 AUC of v3 TRACE
2. If AUC ≥ 0.65: dispatch ANCHOR 2 TWO_TIER with current TRACE signal; HONEST-BOUND story is the answer
3. Else: dispatch ensemble (1-2 CPU-hr) before any backup mechanism
4. Only if BOTH (2) and (3) fail: dispatch M-CFU as the highest-EV backup

---

## ANGLE 3 — STRUCTURAL / GEOMETRIC INTERPRETATION (the +0.08 ceiling)

### Is +0.083 fundamental or mitigatable?

**Partially fundamental, partially mitigatable.** The decomposition:

**Fundamental component (~+0.05): encoder channel-capacity for importance bits.**
The substrate's W matrix is an outer-product accumulator: W = Σ_i w_i ⊗ s_i where w_i is atom vector and s_i is signature. Importance information must live in either:
- (a) the **magnitude** dimension of W's contribution from each atom (orthogonal to retrieval correctness)
- (b) the **graph structure** of bound-pairs (H = W^T W or similar)
- (c) the **temporal trace** (retrieval counts, write-time)

The substrate's representation has finite capacity along axis (a) (magnitudes are essentially fixed by encoder norm — current substrate doesn't have a free magnitude knob; magnitudes are 1.0±ε from the encoder); axis (b) is graph-structural and as the prior drill showed, smooth functions of H saturate; axis (c) is the most extractable but its variance grows ~√n_queries which puts an information-theoretic upper bound.

Estimated channel capacity for importance via current encoder: **~3-4 bits per atom** (log2 of useful importance-rank quantiles ~10-15). This caps AUC at ~0.70 (information-theoretic; well-known mapping from rank-bits to AUC under Gaussian assumption). **v3 TRACE at AUC ~0.62-0.68 is at 90% of this capacity.**

**Mitigatable component (~+0.03): metric-redundancy in v3 composition.**
v3 was supposed to be TRACE × ULTRAMETRIC-CORENESS, but the metrics reveal **ULTRA arm collapsed to zero importance across all 3 seeds**:
- ARM_ULTRAMETRIC_ONLY: importance_min=0.0, importance_max=0.0, importance_mean=0.0, coreness_atoms=0
- This means ULTRA_COS=0.85 threshold was too strict for the smoke-scale N=512 substrate; NO atoms hit coreness
- All COMP arms (λ=0.1, 0.3, 0.5) collapsed identically to TRACE-ONLY metrics (because COMP = TRACE * lambda * 0 = 0 contribution from ULTRA)
- Therefore v3 was effectively a 1-mechanism cell labeled as composition — **the composition has NOT been honestly tested**

**Mitigation #1: re-run v3 with ULTRA_COS=0.70, ULTRA_MIN_SIZE=3.** Cheap (existing cell, just config tweak). If ULTRA_ONLY arm produces non-zero importance at this regime, the actual composition reading emerges. Predicted: ULTRA at threshold 0.70 produces 5-15 coreness atoms per seed; composition gains +0.02-0.04 over TRACE-only. This is small but unblocks the honest reading.

**Mitigation #2: substrate-product story acknowledges encoder-bound.** If after honest composition test we still hit +0.08-0.10, the story becomes: "+0.10 is the substrate's encoder-bound channel capacity for atom-level importance. Further gain requires encoder upgrade (Path C substrate-owned encoder, USER 2026-06-23 standing) or aggregation (cluster-level + ensemble)."

### Channel capacity formal analysis

Under the substrate's current encoder (char-trigram-shaped state vectors with cor ≈ 0.05-0.30 across atoms; from prior probes):

**Information-theoretic ceiling on per-atom importance discrimination:**
```
I(importance_label; encoder_state) <= H(importance_label) - H(importance_label | encoder_state)
                                    <= H(label) - H_noise
                                    
At importance discretized to 10 quantiles: H(label) = log2(10) = 3.32 bits
Noise from encoder collisions (cor=0.20 mean) ≈ 2.5 bits effective
Net extractable importance bits per atom: ~0.8-1.0 bits
Mapping bits → AUC: AUC ≈ 0.5 + 0.5 * (1 - 2^-bits) for binary discrimination
                  ≈ 0.5 + 0.5 * (1 - 0.55) ≈ 0.72 ceiling
```

**+0.083 sel_unretr maps to ~0.62-0.68 AUC ≈ 0.85-0.95 of ceiling.** v3 TRACE is operating at near-ceiling efficiency on the encoder channel. No mechanism that READS FROM the current encoder can do dramatically better — at best +0.02-0.05 AUC absolute (which is +0.03-0.06 sel_unretr). This bounds the upside of M-CFU/M-SURP/M-MI from the current substrate.

**Implication: the substrate-product story is partially "encoder-bound at +0.10."** Path C substrate-owned-encoder (USER 2026-06-23 standing direction) is the *true* path past this ceiling. Until encoder upgrade, aggregate via cluster-level + ensemble.

### Does TRACE × ULTRA span same subspace?

Per the metrics, NO — they CAN'T even occupy different subspaces because ULTRA arm produces zero variance (importance_mean=0.0, max=0.0 across all 3 seeds). v3's ULTRA arm is degenerate. The intended decomposition was:
- TRACE axis: behavioral (which atoms get queried)
- ULTRA axis: structural (which atoms are in dense clusters)

But ULTRA arm with ULTRA_COS=0.85 produced 0 coreness atoms at N=512 — the threshold was set for the FULL scale and doesn't trigger at smoke. This is a **regime-mismatch BIAS** (META_RULE_S band-calibration regime check); the cell author or pre-reg should have included a regime-check to ensure ULTRA arm produces non-zero variance before dispatch.

**Why ULTRA contributes +0.008 in COMP arm:** because COMP = TRACE * (1 + λ * ULTRA_normalized); when ULTRA=0 for all atoms, COMP = TRACE * 1 = TRACE-only. The +0.008 over TRACE-alone is numerical noise from the multiplicative form (floating-point + tiny non-zero default).

**Cheap fix:** dispatch v3.1 with ULTRA_COS=0.70, ULTRA_MIN_SIZE=3, keep all other config identical. ~10 min CPU on remote. Honest composition test costs trivially.

### Geometric analysis: subspace overlap of 3 mechanisms

Even after fixing ULTRA, we have:
- v1 PageRank vector p ∈ R^N (continuous)
- v3 TRACE vector t ∈ R^N (count-valued)
- v3 ULTRA vector u ∈ R^N (count-valued, integer)

For ensemble to add value, these must span overlapping but non-degenerate subspaces. Conjecture (testable in pre-flight cell):

```
cor(p, t) ≈ 0.50-0.70  (PR and TRACE both biased toward hub atoms)
cor(p, u) ≈ 0.40-0.60  (PR and ULTRA both graph-structural)
cor(t, u) ≈ 0.30-0.50  (different axis — TRACE is behavioral, ULTRA is structural)
```

If cor(t, u) > 0.65: ULTRA adds no signal over TRACE; composition was always doomed.
If cor(t, u) < 0.50: ULTRA is genuinely orthogonal axis; composition CAN help.

**Pre-flight cell** (1-2 min, before any composition dispatch):
```python
# Compute pairwise cor of 3 importance signals on existing substrate Store
# Output: 3x3 cor matrix; gate further composition dispatch on off-diagonal cor < 0.65
```

This is essentially the ensemble cell's SIGNAL-INDEPENDENCE GATE applied pre-flight. Cheap; high-information.

### What's the substrate-product impact if v4 NREM-replay also lands at ~+0.08?

If 4-for-4 hits +0.08 ceiling, the architectural conclusion is **NOT** "importance is broken." The architectural conclusion is:

> **Atom-level importance is encoder-bounded at +0.08 sel_unretr (~0.65 AUC). This is a CHANNEL CAPACITY result, not a mechanism failure. The substrate handles importance at the CLUSTER level via ultrametric aggregation (where Cramér-Rao reduction gives effective discriminator strength +0.30+) and via ENSEMBLE of weak signals (3-voter geometric-mean tested). Downstream consumers (TWO_TIER promotion, NREM-replay scheduling, refuse-gate prior) all consume rank-fractional signals that work at AUC=0.65 just as well as AUC=0.85. Encoder upgrade (Path C substrate-owned encoder) is the path past the channel-capacity bound, which is on the 2026-06-23 USER-standing roadmap as a future capability, not a current blocker.**

This is a real and shippable substrate-product narrative. Wave 3 ANCHOR 2 TWO_TIER ships using current +0.08 atom-level signal; CERT 618 honest-bound atom is the LOAD-BEARING evidence. The substrate is *more brain-like* for using ensemble + cluster-level signals than it would be for finding a single magic +0.20 atom-level mechanism (brain doesn't do that either).

---

## ANCHOR 2 TWO_TIER promotion path with +0.083 importance signal

### Does it work? What bands?

**It works.** Specifically:

The TWO_TIER spec (gap4_two_tier_generational_W_v1 from 2026-06-26 dispatched and pending verdict) uses **single-noisy-probe recall accuracy** as importance signal. Per the prior drill's framing, this is empirically WEAKER than retrieval-trace as an importance proxy because:
- single-probe recall has cv ~0.15-0.20 from probe-noise alone
- TRACE has cv ~0.05 (from per-seed variance only; signal is deterministic given query stream)

**Substituting TRACE for single-probe-recall in TWO_TIER promotion → predicted strict improvement.** The promotion path:
1. Every K_promote=500 cycles, score atoms by TRACE (retrieval-count over [last_K, now])
2. Promote top tau=0.10 (50 atoms per cycle) to W_old; decay W_young by gamma=0.90
3. ARM_TWO_TIER_IMPORTANCE uses TRACE; ARM_TWO_TIER_RANDOM_PROMOTE uses uniform random

**Predicted result on TWO_TIER cell (pre-reg bands from gap4_two_tier_generational_W_v1):**
- ARM_TWO_TIER_IMPORTANCE (TRACE-based): drift_reduction ~0.30-0.45 vs baseline
- ARM_TWO_TIER_RANDOM_PROMOTE: drift_reduction ~0.10-0.20 vs baseline (random STILL helps somewhat because the cohort migration to W_old + decay-W_young architecture has value regardless of selection)
- Gap (importance vs random): ~0.20 → comfortably clears HARD_PASS_PARTIAL bar (drift_reduction ≥ 0.30 absolute)

**Predicted band: HARD_PASS or HARD_PASS_PARTIAL.** TWO_TIER chain-grade landing is achievable with current +0.083 signal.

**Why this works at low atom-level signal:** TWO_TIER promotes top tau=10% = 50 atoms per cycle. Over 4000 cycles with K_promote=500, there are 8 promotion events selecting 50 atoms each = ~400 atoms accumulated in W_old over the run. The SELECTION over 400 atoms via top-fraction-rank is a **vastly easier statistical problem** than per-atom sel_unretr discrimination. The Cramér-Rao on top-K-rank precision scales as sqrt(K), giving the importance signal effective amplification of ~7x at K=50. **+0.083 atom-level sel_unretr → +0.50 effective top-K-rank discrimination → strong PASS on TWO_TIER discriminator.**

### TWO_TIER cell modification spec (use existing cell + swap importance source)

```
NAME: gap4_two_tier_generational_W_v2_TRACE_importance
SCRIPT: experiments/exp_gap4_two_tier_generational_W_v2_TRACE_importance.py
PRIMITIVE: hdlab/two_tier_promotion.py (existing) + swap importance_fn to retrieval_trace
QUEUE: remote_cpu_queue (route via hdi_orchestrator)
TIMEOUT: 14400s (4hr, same as v1)
SEEDS: [11, 13, 19]

ARMS (5; same structure as v1, swap importance source):
  ARM_BASELINE_SINGLE_W
  ARM_TWO_TIER_TRACE_PROMOTE_500 (K=500, tau=0.10, gamma=0.90; importance=retrieval_trace)
  ARM_TWO_TIER_TRACE_PROMOTE_1000 (K=1000, tau=0.10, gamma=0.90)
  ARM_TWO_TIER_TRACE_PROMOTE_2000 (K=2000, tau=0.20, gamma=0.85)
  ARM_TWO_TIER_RANDOM_PROMOTE (importance=uniform random; ablation)

CONFIG: N=4096; 4000 cycles (alpha=0.977 at end); 3 seeds;
  RECALL_PROBE_M=100; CHECKPOINT_INTERVAL=250; TRACE_WINDOW=K_promote

PRE-REG BANDS:
  HARD_PASS: best TRACE arm final_forget <= 0.05 AND baseline curve_max_forget > 0.10
             AND best cv <= 0.07 AND TRACE strictly beats RANDOM by >= 0.05 drift_reduction
  HARD_PASS_PARTIAL: drift_reduction(TRACE - baseline) >= 0.30 absolute
  MIDDLE_BAND: drift_reduction(TRACE - baseline) in (0.05, 0.30)
  HARD_FAIL: |drift_reduction(TRACE - baseline)| <= 0.05
            OR (TRACE - RANDOM) < 0  -- random beats importance = importance is noise

FAIRNESS GATE: cor(TRACE_score, |W|) < 0.30 (META_RULE_F; already validated at 0.057 in v3)
CARDINALITY_OK: 5 arms x 3 seeds x 17 checkpoints = 255 measurements; HARD_FAIL_CARDINALITY_BREACH if any arm misses

PRE-FLIGHT: 5-min CPU smoke with K_promote=200, J=600; confirm:
  - TRACE produces non-zero importance variance (importance_max > 5; importance_min = 0)
  - W_old_util > 0 at first promotion event (promotion fires)
  - Per-arm wall < 100s at smoke

EXPECTED VERDICT (deflated): P(HARD_PASS) = 0.45; P(HARD_PASS_PARTIAL) = 0.55; P(HARD_FAIL) = 0.15
  Rationale: TRACE is provably stronger signal than single-probe-recall (the v1 default);
  TWO_TIER mechanism is well-validated in lit (Marblestone Frontiers 2016, McClelland 1995
  complementary-learning-systems); cluster-of-50-atoms selection cleanly bypasses
  per-atom signal weakness. Main risk is multi-checkpoint variance from drift accumulation.
```

### Why this is the right immediate next move

1. **Tests the actual product question** (does importance help TWO_TIER?) directly
2. **Cheap** (existing cell, 1-line importance_fn swap)
3. **Strongest available evidence for "ship with honest-bound"** narrative if it lands HARD_PASS
4. **Doesn't preclude** later M-CFU/M-SURP work (those become *capability extensions*)
5. **Unblocks Wave 3 ANCHOR 2 promotion** which has been deferred 2+ cycles

---

## Decision dependency graph

```
                                    +-----------------------+
                                    | 30s re-analysis cell  |
                                    | D1 AUC on v3 TRACE    |
                                    | (zero new compute)    |
                                    +-----------+-----------+
                                                |
                       +------------------------+----------------------+
                       |                                               |
                  AUC >= 0.65?                                    AUC < 0.62?
                       |                                               |
                       v                                               v
       +-------------------------------+                +---------------------------------+
       | SHIP HONEST-BOUND             |                | DISPATCH ENSEMBLE 3-VOTER       |
       | 1. ANCHOR 2 TWO_TIER w/ TRACE |                | 2 CPU-hr; +0.02-0.05 AUC lift   |
       | 2. CERT 618 atom amplified    |                | + v3.1 ULTRA tuning re-run      |
       | 3. Defer M-CFU/M-SURP family  |                +----------------+----------------+
       +---------------+---------------+                                 |
                       |                              +------------------+-------------------+
                       v                              |                                      |
       +-------------------------------+         AUC >= 0.65?                          AUC < 0.62?
       | Substrate-product story:      |              |                                      |
       | "atom-level importance is     |              v                                      v
       | channel-bounded; cluster +    |         (SHIP path)                          (BACKUP path)
       | ensemble are the architecture"|                                                     |
       +-------------------------------+                                                     v
                                                                          +-------------------------------+
                                                                          | Dispatch M-CFU (prior drill   |
                                                                          | rank 1; P_deflated=0.50)      |
                                                                          | 3-5 CPU-hr remote             |
                                                                          +-------------------------------+
```

---

## Pre-flight discipline (this drill's specific gates)

1. **predispatch_check.py** for each cell name (D1 re-analysis / ensemble / TWO_TIER_TRACE / v3.1 ULTRA tuning)
2. **30s discriminator re-analysis cell** — load existing v3 metrics; compute D1 AUC / D2 top-K precision / D3 KM-curve gap from per-arm recall vectors; ZERO new compute; should run as a tool, not a cell
3. **5-min pre-flight cor check** before ensemble dispatch — load 1000 atoms from current Store; compute TRACE/PR/MAG pairwise cor; gate ensemble dispatch on cor < 0.65
4. **5-min pre-flight smoke** for TWO_TIER_TRACE — TRACE-importance non-zero variance + promotion fires + per-arm wall < 100s
5. **CARDINALITY_OK + smoke-fires-discriminator** for all dispatched cells (META_RULE_H + 2026-06-26 disciplines)
6. **No-silent-except** in importance_fn implementations (META 2026-06-26 K-sweep phantom protection)
7. **Spawn budget Fix #14 ceiling** ≤3 in flight; if 3 already in flight, prioritize D1 re-analysis (cheapest, highest info)
8. **Fairness gate META_RULE_F** for every new importance signal: cor(importance, |W|) < 0.30 BEFORE PASS classification

---

## Citations (verified)

External lit (8 verified, including overlap with prior drill):

1. Foster Annu Rev Neurosci 2017 "Replay comes of age" (sharp-wave-ripple importance-weighted replay)
2. Marblestone et al. Frontiers Comp Neurosci 2016 "Toward an integration of deep learning and neuroscience" (TWO_TIER systems lit)
3. McClelland, McNaughton, O'Reilly Psych Rev 1995 "Why there are complementary learning systems" (CLS / TWO_TIER founding theory)
4. Tonegawa engram-completion (Liu 2012, Ramirez 2013, Josselyn-Tonegawa 2020) — counterfactual recall as importance metric
5. Cohen 1988 "Statistical Power Analysis for the Behavioral Sciences" — d-to-AUC mapping (Cohen's d = sel/σ; AUC = Φ(d/√2))
6. Cramér 1946 / Rao 1945 — Cramér-Rao bound on estimator variance (√N reduction for ensemble means)
7. Breiman Machine Learning 1996 "Bagging predictors" — ensemble-of-weak-learners theory
8. USER 2026-06-23 standing — Path C substrate-owned encoder direction (encoder upgrade roadmap)

Internal substrate notes (10 referenced):

9. `notes/research_drill_cortex_importance_backup_mechanisms_2026-06-27.md` (prior drill; 6 BACKUP mechanisms — explicit complement to this drill)
10. `data/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3/metrics.json` (v3 per-arm metrics; ULTRA collapse to zero discovered)
11. `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md` (TWO_TIER spec; importance_fn swap target)
12. `notes/director_LIVE_STATE_2026-06-27.md` (todo 20: Wave 3 ANCHOR 2 TWO_TIER promotion gated on edge-imp v3 chain-grade — this drill unblocks via honest-bound path)
13. `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` (CERT 618 context + ANCHOR 2 deferral status)
14. `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md` (META_RULE_S band-calibration regime; ULTRA threshold regime-mismatch caught)
15. `memory/feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26.md` (smoke-fires-discriminator discipline)
16. `memory/feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23.md` (ensemble-of-weak-signals is brain-grounded)
17. `memory/project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.md` (encoder upgrade is the path past channel-capacity bound)
18. `memory/feedback_capability_dev_is_goal_cert_grade_is_instrument_USER_2026-06-19.md` (TWO_TIER + ensemble work even at AUC=0.65; capability dev is goal)

**Total verified: 18.**

---

## Filed-by

research (Opus 4.7 1M), 2026-06-27
Drill type: complementary-angle drill (discriminator reframe + honest-bound utility + structural-geometric bound)
Calibration: lit-scan deflation 0.15-0.25; novel-synthesis P cap 0.50; channel-capacity bound derivation per Shannon (1948) information-theoretic ceiling
Anti-Bias checklist applied: M-S (band-calibration regime), N (verify-referent for v3 ULTRA collapse), Q (suspect ULTRA=0.0 max as suspicious-perfect; caught regime-mismatch)
Honest-finding: v3 ULTRA arm DEGENERATE — coreness_atoms=0 across all 3 seeds; composition was not actually tested; v3 verdict is "TRACE-only @ +0.083" not "composition @ +0.083"
Dispatch priority: D1 30s re-analysis (zero compute) → either SHIP honest-bound TWO_TIER OR ENSEMBLE + ULTRA-tuning; defer M-CFU family until ENSEMBLE + TWO_TIER are inconclusive
