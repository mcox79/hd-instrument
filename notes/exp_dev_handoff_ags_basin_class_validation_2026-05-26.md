# exp_dev handoff — AGS-RS-multi-FM basin-class validation

**Date.** 2026-05-26
**Owner.** Research → exp_dev.
**Parent research note.** `notes/research_ags_retrieval_phase_substrate_2026-05-26.md` (AGS-RS-MULTI-FERROMAGNET verdict at P=0.48, novel-synthesis cap binding).

## TASK

Two cheap decisive checks closing the substrate phase-classification gate (AGS-RS-multi-FM vs CLUSTER-GLASS vs 1-RSB-APPROXIMATE vs GEOMETRIC-FRUSTRATION sub-claim):

1. **Cluster-conditional P(q | cluster_k) signature analysis.** Confirm or extend the cluster-conditional P(q) re-analysis (in flight per dispatch context) to deliver, per cluster class (SAME / REPLAY / STAGE4 / DIFF) at N=8192 (or whatever N this analysis runs on):
   - peak count per conditional distribution (1 = AGS-RS-multi-FM; ≥2 = CLUSTER-GLASS)
   - primary peak position per conditional (predicted to match {0.94, 0.74, 0.60, m_4})
   - secondary peak weight if present (cluster-glass distinguishing signature)
   - within-cluster connected correlation function (Q-dependent decay = CLUSTER-GLASS; Q-independent = AGS-RS-multi-FM)

2. **Kerdock codebook distance-class audit.** Numerically verify the substrate's Kerdock variant has EXACTLY 4 distinct codeword-pairwise-distance classes (modulo coset structure):
   - extract pairwise Hamming distances between Kerdock codewords used as patterns
   - cluster the distance distribution into discrete classes
   - confirm exactly 4 classes (or report the actual count if different)
   - map each class to a substrate retention plateau height
   - cross-check predicted m_k = AGS-RS-metastable overlap at distance-class-k against substrate empirical {0.94, 0.74, 0.60, m_4}

If the cluster-conditional P(q) re-analysis already covers (1), the handoff reduces to (2) Kerdock distance-class audit + post-hoc cross-check.

## WHY

This drill calibrates substrate phase at P=0.48 (AGS-RS-MULTI-FERROMAGNET); the decisive falsifiers are cluster-conditional P(q) signature + Kerdock-class ↔ plateau mapping. Both are CHEAP (post-hoc on existing data or analytical on the known Kerdock codebook). Closing the phase classification:
- locks substrate's customer-facing tier spec to a theoretical anchor (AGS basin-class retention)
- replaces "1-RSB cluster structure" language with "multi-basin metastable-retrieval at 27% of structured-codebook capacity" — simpler product story
- simplifies cap_map row 405 ("Hierarchical retrieval index (RSB phase, ultrametric structure)") to a calibrated state (AGS-RS-multi-FM, not RSB)
- provides closed-form prediction for plateau heights from Kerdock distance lattice (vs ad-hoc empirical numbers)

## CONTRACT (pre-registered bands)

### Test 1 — Cluster-conditional P(q|cluster_k) signature

- **HARD-PASS AGS-RS-MULTI-FERROMAGNET:** all 4 cluster-conditional P(q|k) single-peaked (n_peaks=1, binder negative or near zero for unimodal); peak positions match retention plateau heights {0.94, 0.74, 0.60, m_4} within ±0.07; peak widths ~ 1/sqrt(N) within ±30%.
- **HARD-PASS CLUSTER-GLASS:** ≥ 2 of 4 cluster-conditional P(q|k) two-peaked with secondary peak weight > 0.10 AND gap between peaks > 0.20.
- **HARD-PASS 1-RSB-APPROXIMATE:** single-peaked at N=8192; if re-run at v211's N=1024 with same protocol, two-peaked structure emerges (secondary weight > 0.05).
- **MIDDLE / INCONCLUSIVE BAND:** one or two cluster-conditional distributions ambiguous; secondary peak weight in [0.05, 0.10] OR peak positions off plateau heights by 0.07-0.15.
- **INSTRUMENTATION-FAIL:** insufficient samples per cluster class to estimate P(q|k) (need n_samples_per_cluster > 50 for stable estimate); or cluster labels not available at sample level on existing data.

### Test 2 — Kerdock distance-class audit

- **HARD-PASS:** exactly 4 distinct distance classes in Kerdock codebook; each maps monotonically to a retention plateau; predicted m_k from AGS basin-class formula (see research note section c P3.2) matches empirical {0.94, 0.74, 0.60, m_4} for 3 of 4 plateaus within ±0.07.
- **HARD-FAIL:** ≠ 4 distance classes (3 or 5 or smooth distance distribution without discrete classes); OR predicted-vs-observed plateau heights off by > 0.15 systematically; OR non-monotone mapping (e.g., farther distance class has higher m_k than closer class).
- **MIDDLE BAND:** 4 classes confirmed, but plateau-height mapping has 2-of-4 mismatches between 0.07 and 0.15.
- **INSTRUMENTATION-FAIL:** Kerdock codebook construction internal to substrate cannot be enumerated for distance analysis (would require codebook re-derivation; falls back to qualitative bound).

## AUTONOMY

exp_dev decides:
- Test 1 anchor: extension of existing in-flight cluster-conditional P(q) re-analysis OR fresh anchor if needed.
- Test 2: post-hoc analytical on existing Kerdock codebook (NumPy/PyTorch script ~50 lines reading the codebook + computing pairwise distance histogram); ETA estimate ~30 min CPU.
- Queue choice (likely both fit laptop CPU quick-probe per [[feedback-laptop-cpu-quick-probes]] since post-hoc on existing data).
- Smoke gate decisions per [[feedback-envelope-expansion-fail-bands]].
- Self-test pairs per [[feedback-strategy-spec-formula-selftests]]: for AGS self-consistent fixed point m_k = erf(m_k / sqrt(2*r_k)), exp_dev verifies (m=0.95, r=0.05) → erf(0.95/sqrt(0.1)) ≈ erf(3.00) ≈ 0.99998 ≈ m; (m=0.6, r=0.5) → erf(0.6/sqrt(1.0)) = erf(0.6) ≈ 0.604 ≈ m.
- Ship-name-collision check per [[feedback-ship-name-collision]].
- Verdict envelope per standard.

## SUCCESS CRITERIA

If Test 1 + Test 2 BOTH HARD-PASS AGS-RS-MULTI-FERROMAGNET:
- P(AGS-RS-multi-FM) jumps from 0.48 to ~0.65 (above novel-synthesis cap after empirical anchoring)
- v215/v216 cap_map row 405 closes to ✅ Validated (AGS-RS-metastable-retrieval phase classification locked)
- 1-RSB framework retires; v211 hysteresis reinterpreted as AGS first-order spinodal
- Strategy can plan the next cycle around AGS basin geometry instead of RSB hierarchy
- Substrate-product narrative simplifies to single theoretical home (AGS retrieval-metastable with structured codebook)

If Test 1 HARD-PASS CLUSTER-GLASS:
- P(AGS-RS-multi-FM) drops to 0.18; CLUSTER-GLASS takes plurality
- Pursue Krzakala-Mezard cluster-glass framework; new research drill on cavity-method extensions
- Substrate-product positioning gains "condensation-class" anchor (different but still product-strong)

If Test 1 HARD-PASS 1-RSB-APPROXIMATE:
- Retain 1-RSB framework with finite-N correction calibration; reframe v216 stands as-is
- N-scaling test ON queue: gap_hysteresis vs N to distinguish AGS-RS-multi-FM finite-N from genuine 1-RSB
- Customer-facing spec unchanged

If MIDDLE / INSTRUMENTATION-FAIL:
- Escalate via routing to Research for a follow-up drill OR Strategy for capability-map status review

## DEPENDENCIES

- v215 cluster-conditional P(q) re-analysis (already in flight per dispatch context) — Test 1 reduces to extending its output schema to include peak count, position, secondary weight per cluster class
- Substrate's Kerdock codebook construction internal access — Test 2 needs codebook tensor or generator function
- Existing data dirs from v206 (4-corpus saddle-cascade), v211 (hysteresis), v212 (MoE SHIFT) for cluster-label cross-reference if needed

## NOTES

- This handoff is COMPATIBLE with the SVD-cascade unified-framework handoff (`exp_dev_handoff_unified_svd_cascade_falsifier_2026-05-26.md`); they test orthogonal aspects (this one: retrieval-phase static; that one: training-cascade dynamic).
- Failure of this drill DOES NOT close substrate-product viability — empirical retention numbers stand regardless of phase classification (per parent note section e point 6).
- Per [[feedback-no-experiment-design-in-prompts]]: this handoff hands TASK + WHY + CONTRACT (pre-registered bands) + AUTONOMY. NO anchor name; NO sweep grid; NO threshold formulas beyond what is necessary for pre-registration; NO queue choice or ETA pre-committed; NO cap_map row updates pre-decided.
- Per [[feedback-ship-before-dependency-verified]]: exp_dev MUST verify data + codebook dependencies BEFORE shipping; if v215 cluster-conditional re-analysis output schema doesn't include peak count / position per cluster, extend the analysis BEFORE re-ship.
