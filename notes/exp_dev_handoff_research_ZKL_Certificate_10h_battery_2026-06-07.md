# exp_dev hand-off -- research: ZKL Certificate 10-hour empirical battery (Chain 1 Drill 5 FINAL closure)

Filed-by: research session
Trigger: Chain 1 Drill 5 FINAL (notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill5_FINAL_2026-06-07.md)
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and pre-reg bands only; exp_dev designs the implementation.

**THIS IS THE CUSTOMER-FACING GATE.** No customer claim about ZKL/Completeness/Soundness can be shipped until this battery runs HP. All 5 sub-tests are local CPU; total ~10 hours; $0 compute.

---

## Anchor candidates (the 10-hour battery -- 5 sub-tests, sequenced cheapest-first)

### 1. completeness_500_facts_top1_precision (~30 min CPU; Tier-1)
- Substrate-product reading: store 500 facts on production-config substrate; query each fact's exact text; measure top-1 retrieval rate
- Why now: cheapest gate; if completeness < 95% the rest of the battery is moot
- HP: >= 99.0% top-1 precision
- MID: 95-99% (qualify claim with measured value)
- HF: < 95% (system cannot reliably retrieve; architecture revision required)

### 2. soundness_500_neverstored_queries (~30 min CPU; Tier-1)
- Substrate-product reading: 500 queries with content NEVER WRITTEN to substrate; measure false-positive rate at cosine > 0.90
- Why now: validates the "no false assertion" axis substrate uniquely claims
- HP: <= 0.5% false positive rate
- MID: 0.5-2.0% (qualify)
- HF: > 2.0% (hallucination rate too high; HIPAA-claim void)

### 3. zkl_curve_k_sweep_whitening_on (~8 hr CPU; Tier-1 DECISIVE; the big one)
- Substrate-product reading: adaptive paraphrase attack at k in {1, 10, 50, 100, 500}; measure TPR@FPR=0.01 (Carlini LiRA-style); whitening ENABLED
- Why now: the central commercial claim. If ZKL(k=50) <= 0.10 the GOLD 3.0 compounding-defense story holds.
- HP: ZKL(50) <= 0.10 AND ZKL(100) <= 0.35 (sublinear accumulation confirmed)
- MID: ZKL(50) in [0.10, 0.30] (qualify with measured value)
- HF: ZKL(50) > 0.30 (HIPAA ZKL claim is unsupportable; no structural advantage)

### 4. timing_immunity_1000_queries (~1 hr CPU; Tier-2; validates GOLD 3.0 timing-immunity claim)
- Substrate-product reading: 500 member + 500 non-member queries; measure latency distribution per group; train classifier on latency alone; report AUC
- Why now: substrate's timing-immunity claim depends on this being random (AUC ~ 0.5)
- HP: AUC in [0.48, 0.52] (statistically indistinguishable from random)
- MID: AUC in [0.52, 0.60] (timing partially data-dependent; qualify with hardware caveat)
- HF: AUC > 0.60 (timing is data-dependent; side-channel-immune claim breaks)

### 5. merkle_audit_integrity (~10 min CPU; Tier-1; trivial pre-req)
- Substrate-product reading: write 500 facts; recompute Merkle root from log; compare to stored root
- Why now: if audit chain is broken, NO compliance claim can be shipped
- HP: PASS (roots match)
- HF: FAIL (chain corrupted; investigation required before any other test runs)

---

## Context pointers

- Research note: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill5_FINAL_2026-06-07.md (Section 11)
- Chain 1 GOLD 1-4 references: drills 1-4 in same series
- Cap_map: cycle 147 production recipe (whiten + pinv + sharded multi-head; left-pad; Llama-1B preferred)
- Production config to test: whitening ON + pseudoinverse + sharded W (W-sharding from cycle 147 I4)

---

## Contract

exp_dev designs script structure, threshold formula details, queue routing, ETA. The HP/MID/HF bands above are research's pre-reg recommendation; exp_dev may tighten but not loosen without re-routing.

These 5 cells SHOULD be sequenced cheapest-first (1, 5, 2, 4, 3). Cell 3 is the largest and the central commercial decision -- run it ONLY if cells 1, 2, 5 all HP.

## Autonomy declaration

exp_dev has full autonomy on: implementation (numpy/torch), test set design (held-out vs random), specific threshold cutoff for cosine, attack implementation for cell 3 (LiRA-style or simpler threshold attack), and whether to run cells in parallel or sequence.

exp_dev does NOT have autonomy on: relaxing HF thresholds (HF in this battery = no customer claim).
