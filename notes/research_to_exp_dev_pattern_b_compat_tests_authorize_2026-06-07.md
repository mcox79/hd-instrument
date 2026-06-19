# Research -> Exp-Dev: Pattern B compatibility pre-tests (5 cells, <30 min total CPU)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Pattern B production stack compatibility 3x drill output.

The drill found 7 of 8 Pattern A elements transfer to Pattern B with minor or no adaptation.
Pattern B v1.1 integration is a 3-day overlay, not a rebuild. Five cheap CPU tests resolve
all remaining uncertainty.

Authorize all 5. Total budget < 30 min CPU. $0.

## 1. Bundle manifold dimensionality (TwoNN; PRIORITY 1)

The single highest-leverage test. The d=30 PCA truncation that worked for Pattern A KEYs
probably does NOT transfer to Pattern B bundles. This test measures Pattern B's bundle
manifold dim.

Method:
- Generate 1000 random bound bundles using 20 role vectors + bge-small fillers at N=4096
- Run TwoNN MLE intrinsic-dim estimator
- Also report PCA explained-variance 95% threshold

Decision rules:
- d_hat <= 50: d=30 transfers to Pattern B; engineering = minor (config change)
- d_hat in 50-200: moderate truncation possible; pick the right dim via empirical sweep
- d_hat >= 200: PCA truncation does NOT meaningfully compress Pattern B; storage cost
  recalculated higher

Wall: <5 min CPU.

## 2. Auto-associative pinv recovery on bundles

Confirms pinv transfers cleanly to Pattern B as auto-associative storage.

Method:
- Store 200 bound bundles in substrate via pinv
- Query with PARTIAL bundles (e.g., just the subject-role binding) and measure whether the
  full bundle is recovered

HARD-PASS: partial-query recovery acc >= 0.95.

Wall: 5 min CPU.

## 3. PCA whitening basis on bundles

Tests whether the whitening basis needs recomputation on Pattern B bundles.

Method:
- Pattern A whitening: uses basis from raw Llama embeddings
- Pattern B whitening: compute new basis from 1000 representative bound bundles
- Compare retrieval quality: Pattern B with Pattern A's whitening vs Pattern B's own
  whitening

HARD-PASS: Pattern B's own whitening basis gives lift >= +5% over Pattern A's whitening.
HARD-FAIL: no meaningful difference (whitening doesn't matter for Pattern B).

Wall: 5 min CPU.

## 4. H=2 multi-head BFT on bundles

Verifies H=2 BFT works for Pattern B bundles.

Method:
- Same H=2 BFT mechanism: write each bundle through 2 random orthogonal rotations of
  storage space
- Read-average consensus
- Measure noise robustness on Pattern B bundles at noise std 0.05, 0.20, 0.50 (matching
  the CELL-4 sweep)

HARD-PASS: recall@1 stays >= 0.95 at noise 0.50 (matching CELL-4).

Wall: 5-10 min CPU.

## 5. 4-bit quantization + modern Hopfield on Pattern B W

Verifies the storage stack continues to work with Pattern B's compositional load.

Method:
- Store 5000 Pattern B bundles at N=4096 with modern Hopfield exponential energy
- Apply 4-bit quantization on resulting W
- Measure retrieval quality vs bf16 baseline

HARD-PASS: recall@1 drop < 3% with 4x storage reduction.

Wall: 5 min CPU.

## Sequencing

Run Test 1 first (resolves the d=30 question; informs the others).

Tests 2-5 run in parallel after Test 1 informs the bundle dimensionality.

If Test 1 finds d_hat > 200, the storage cost recalculation matters more, and Tests 4-5
become the critical path for v1.1 storage projections.

## Decision tree after all 5 results

If all 5 HARD-PASS:
- Pattern B inherits the Pattern A production stack cleanly
- Pattern B v1.1 engineering = 3-5 days for the integration overlay
- v1.1 ships ~1-2 weeks after Pattern A v1

If Tests 2/3/4/5 HARD-PASS but Test 1 finds high bundle dim:
- Pattern B inherits the stack but storage cost projection adjusts
- Per-fact cost for Pattern B at v3 increases from ~500 bytes to ~1-2 KB
- Still in the 10-100x band acceptable for user

If any of Tests 2/4/5 HARD-FAIL:
- Specific element of Pattern A doesn't transfer cleanly
- File to me for design adaptation; may require additional engineering

## Cross-references

- Pattern B production stack compat 3x drill: notes/research_drill_pattern_b_production_stack_compat_3x_2026-06-07.md
- Pattern B handoff: notes/exp_dev_handoff_research_pattern_b_production_stack_compat_3x_2026-06-07.md
- Cycle 158 Pattern B HP results (unbind+substitute, K-hop compose acc=1.0): notes/orchestrator_to_research_results_summary_2026-06-07_cycle158.md
- Pattern B exploration program: notes/research_to_exp_dev_pattern_b_full_exploration_program_2026-06-07.md
- North-star result: notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all 5 pre-tests. Test 1 first; Tests 2-5 in parallel after.
Apply decision rules autonomously per case. Combined wall < 30 min CPU.

The two other Pattern B compatibility drills (manifold+storage cost; audit+distributed)
are still in flight and will inform additional integration design.
