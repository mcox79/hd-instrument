# Research -> Exp-Dev: LSH fanout pre-tests (normalization check + cone correction)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** LSH fanout 2x drill output.

Two immediate Tier-A pre-tests, both cheap. The first is a 30-minute sanity check that may
fix the issue at zero engineering cost. The second is the cone-correction mechanism that
also lands as the privacy Path F fix.

## 1. L2 normalization check (30 minutes, CPU)

Before any redesign, verify whether L2 normalization is actually applied to Llama-1B
embeddings before LSH bit generation. Random-hyperplane LSH assumes unit vectors; if
embeddings aren't normalized, hash bucket distribution skews and B_eff inflates.

Method: load the production LSH pipeline, log the embedding norms at the point of LSH
bucket assignment. If norms vary substantially, add L2 normalization before LSH and
re-measure B_eff at S=100.

HARD-PASS: B_eff < 30 from normalization alone. Root cause was an infrastructure gap;
no design change needed for v1.

HARD-FAIL: no change in B_eff (already normalized). Proceed to cone correction.

## 2. Cone correction B_eff measurement (2 hours, CPU)

Subtract the mean embedding direction from query and stored vectors before computing LSH
bits. Mechanism is identical to Path F from the privacy 3x drill, just applied to the
hashing stage rather than the cosine similarity stage.

Method: compute mean direction across a representative embedding sample, subtract from all
embeddings before LSH bucketing, measure B_eff at S=100 with the same query set used for
the current B_eff=40 baseline.

HARD-PASS: B_eff < 20 at S=100. v1 LSH design is ready; ship cone correction in the v1
pipeline.

HARD-FAIL: B_eff still >= 30. The anisotropic encoder isn't the dominant cause of fanout
inflation. Proceed to ensemble LSH or hierarchical routing analysis (deferred to a
follow-up drill).

## Shared engineering with privacy Path F

The cone correction mechanism is identical to the privacy Path F cell already routed and
in flight at Exp-Dev. If Path F's privacy test passes, the same code path likely passes
LSH fanout reduction. You can structure these as one engineering deliverable with two
acceptance metrics (ZKL and B_eff).

If Path F privacy hits HARD-PASS first, run LSH test 2 with the same cone-correction
implementation. If Path F fails on privacy, LSH test 2 still independently informs whether
the same mechanism works for fanout reduction.

## v2 design preview (NOT to queue now, just record)

If cone correction passes v1 acceptance, v2 design adds two-tier hierarchical LSH for
S=1000-3000. Coarse routing to a sub-cluster, fine routing within. Estimated 2 weeks
engineering. The drill provided cheap pre-test (Pre-test 4: two-tier B_eff at S=300, 2
hours CPU) for that design when v2 enters scope.

v3 design (S>=10000) requires three-tier hierarchical or learned hashing. Not in the v1
scope; revisit when v2 ships.

## Multi-dim acceptance criteria

Pre-test 1 reports B_eff only (it's a sanity check). Pre-test 2 reports the full multi-dim
set per the supplement note (retrieval F1, K-hop accuracy, KF-1 AUC, audit, ZKL,
performance). A B_eff reduction that comes with retrieval quality degradation is not a
clean win.

## Cross-references

- LSH 2x drill: notes/research_drill_lsh_fanout_reduction_2x_2026-06-07.md
- LSH handoff: notes/exp_dev_handoff_research_lsh_fanout_reduction_2026-06-07.md
- Privacy Path F routing: notes/research_to_exp_dev_privacy_three_fixes_authorize_2026-06-07.md
- Multi-dim criteria: notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md

---

**END.**

**Exp-Dev:** Authorize both pre-tests. Test 1 (normalization check) first; if HARD-PASS
the issue is solved without further work. Test 2 (cone correction) shares implementation
with privacy Path F. Decision rules above; apply autonomously.
