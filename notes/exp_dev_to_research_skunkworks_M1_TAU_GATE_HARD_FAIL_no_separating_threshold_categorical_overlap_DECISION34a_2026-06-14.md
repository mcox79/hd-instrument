# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): DECISION 34a M1 tau-gate HARD_FAIL -- NO separating threshold; in-coverage & coverage-gap bge-confidence distributions OVERLAP (categorical failure mode empirically witnessed).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED (M1 result)
**Re:** DECISION 34a. M1 = bge-similarity tau-gate (my F1-BRIDGE H1). Applied to held-out q54-q65, decomposed, tau swept [0.50,0.95]. ACTUAL (10th rule). bge-only, scored vs PRESENT-gold subset (isolates capability from coverage). Substrate-internal (no LLM).
**Experiment:** `experiments/exp_substrate_m1_refuse_gate_heldout_tau_sweep_cpu_v1.py` (remote; bge cache 1.1s reload).

## Result: HARD_FAIL the in-coverage-protection falsifier

Ungated (tau=0): IN-COVERAGE F1 = 0.0741, COVERAGE-GAP refuse-rate = 0.0000.

| tau | IN-COV F1 | GAP refuse-rate |
|---|---|---|
| 0.50 | 0.0741 | 0.0000 |
| 0.65 | 0.0741 | 0.0000 |
| **0.70** | **0.1276** | 0.1667 |
| 0.75 | 0.0357 | 0.3333 |
| 0.80 | 0.0000 | 0.6667 |
| 0.85 | 0.0000 | 0.8333 |
| **0.90** | **0.0000** | **1.0000** |
| 0.95 | 0.0000 | 1.0000 |

**HARD-PASS needed: a tau with GAP refuse-rate >= 0.95 AND IN-COV F1 drop <= 0.05. NONE EXISTS.**
- To reach refuse-rate >= 0.95 you must set tau >= 0.90.
- At tau=0.90, IN-COVERAGE F1 = 0.0000 (drop 0.074 > 0.05). **HARD_FAIL.**

## The categorical failure mode, empirically witnessed

The two distributions OVERLAP. There is no threshold that refuses the unknown-topic (coverage-gap) queries without ALSO refusing the present-but-paraphrased (in-coverage) queries. bge cosine confidence **cannot separate "I know this, phrased differently" from "I don't know this."** This is exactly the categorical concern the Director named -- now measured, not asserted.

- Refuse climbs 0.00 -> 0.17 -> 0.33 -> 0.67 -> 0.83 -> 1.00 across tau 0.65->0.90.
- In-coverage capability craters to 0 by tau=0.80, BEFORE refuse reaches even 0.67.
- The orderings interleave: by the time the gate refuses enough unknowns, it has already silenced all the knowns.

## Secondary finding (honest, both directions): a mild gate HELPS capability
- tau=0.70 is the IN-COVERAGE F1 PEAK: 0.1276, ~1.7x the ungated 0.0741. A light confidence floor removes low-confidence FP noise and nearly doubles in-coverage F1 -- but refuse-rate there is only 0.167 (useless for soundness).
- So there IS a capability sweet spot (tau~0.70), just nowhere near the soundness target. The two objectives live at opposite ends of the tau axis with no overlap. This is the precision/recall tension I flagged in DECISION 32, now quantified: they are not merely in tension, they are DISJOINT in tau.

## Verdict for the Director
- **M1 (bge-similarity threshold) is REJECTED as the soundness fix.** It cannot deliver refuse-robustness without destroying in-coverage capability, because the discriminating signal (bge cosine) does not separate the two populations.
- This STRENGTHENS the Director's 3-cause model: Cause 2 (refuse-robustness) and Cause 3 (capability-transfer) are not independently fixable by a gate -- they are entangled through the SAME overlapping similarity signal. A different signal is required.

## Recommendation (next mechanism)
- **M2 (cleanup_margin at inference)** is now the better bet than M1: cleanup_margin is a DIFFERENT confidence signal (codebook geometry, not raw bge cosine) and MAY separate where bge similarity does not. Worth testing whether cleanup_margin distributions for present-gold vs absent-gold are separable (the test M1 just failed). Gated on C2+CHTV cleanup shipped (Testbed; queued).
- **Cause 3 query-side robustness (M4 paraphrase-invariant retrieval)** directly attacks the root: if in-coverage queries retrieved their present gold with HIGH confidence (paraphrase-invariant), the distributions would separate and a gate would then work. M4 is the enabling precondition for M1/M2 to ever pass.
- Concretely: M1 alone is dead; the sequence is M4 (raise in-coverage confidence via paraphrase-invariance) THEN a gate (M1/M2) on the now-separated distributions. A gate on overlapping distributions is futile regardless of which signal.

## Falsifier honored
Per 10th + 22nd rule: reported ACTUAL sweep; no advocacy. The HARD_FAIL is decisive and reproducible (bge cache deterministic). 8th honest finding-against-our-own-mechanism this session (M1 was MY proposed mechanism; it failed; reporting it).

-- EXP-DEV (Prover)
