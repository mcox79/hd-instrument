# Research -> Exp-Dev: cycle 162 follow-up test battery (11 cells)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** User authorization "yes on the rebuild, and I assume we have a battery of new tests
to queue" — cycle 162 confirmed Pattern B production stack + Art 12+17 co-compliance.

All apply multi-dim acceptance criteria. Decision rules autonomous unless flagged BORDER.

---

## TIER A: scale validation (CPU/local GPU, <=2 hr each)

### 1. Pattern B index-cache scale validation at 100K and 1M facts
ptb_reuse_index_cache HP'd at 16 bytes/fact at smoke scale. Validate at 100K + 1M facts
using the CELL-2 v3 Wikipedia cache.

Method: build Pattern B substrate at 100K facts with index-cache compression; measure
per-fact cost + retrieval F1. Then 1M facts.

HARD-PASS: per-fact cost stays <= 20 bytes AND retrieval F1 >= 0.95 at both scales.
HARD-FAIL: per-fact cost > 50 bytes OR F1 drop > 10% (the 16 bytes/fact result was
smoke-only).

Wall: 20-30 min local GPU.

### 2. Predicate routing at higher selectivities (30%, 40%, 50%)
predicate_audit_psweep HP'd at 1-20%. Test where the ceiling actually is.

Method: extend the sweep to 30%, 40%, 50% selectivity; measure recall@10.

HARD-PASS: recall@10 >= 0.90 at 50% selectivity (predicate routing fully general).
BORDER: recall@10 drops between 20% and 50% (find the actual selectivity ceiling).
HARD-FAIL: recall@10 < 0.80 at 30% selectivity.

Wall: 1-2 hours CPU.

### 3. Pattern B substrate-as-candidate-generator regime test
Composition regime drill identified substrate-as-candidate-generator as the win regime
(vs substrate-as-ranker which lost cycle 161). Direct test: substrate uses graph traversal
to generate candidates for compositional questions; compare to bge-small dense retrieval.

Method: 50 compositional HotpotQA questions; three retrievals:
- bge-small top-10 (baseline)
- Pattern B graph-traversal candidate set
- Hybrid (graph-traversal + bge re-rank)

HARD-PASS: graph-traversal beats bge by >= 0.10 F1 on compositional subset.
HARD-FAIL: graph-traversal does not beat bge by >= 0.05 F1.

Wall: 3-4 hours CPU.

### 4. EU AI Act Art 12 + GDPR Art 17 co-compliance live demo
The cycle 162 causal_gdpr_erasure_composition was smoke; package as a reproducible demo
scenario that regulators could run.

Method:
- Store 100 facts including 10 facts about person P
- Run a counterfactual query about person P; verify answer + audit chain
- Erase all 10 facts about person P via HMAC keystore deletion
- Re-run same counterfactual query; verify answer no longer leaks erased content;
  verify audit chain still verifies
- Run a separate counterfactual query NOT about person P; verify it still works correctly
- Document the entire flow as a reproducible script

HARD-PASS: zero erased content in counterfactual outputs; 100% audit integrity;
unrelated counterfactuals unaffected.

Wall: 2-3 hours CPU. (This becomes a demo asset.)

---

## TIER B: production validation (CPU/local GPU, 3-5 hr each)

### 5. Pattern B end-to-end on HotpotQA Tier-1
Substrate-augmented Qwen2.5-1.5B with Pattern B retrieval (not Pattern A) vs vanilla RAG
vs bare Qwen on HotpotQA n=200+.

Method: 200 HotpotQA questions; three baselines (bare, vanilla RAG, Pattern B + Qwen);
measure F1 + recall@2 + recall@10 per baseline.

HARD-PASS: Pattern B beats bare Qwen by >= +0.15 F1 AND beats vanilla RAG by >= +0.05 F1.

Wall: 30-60 min local GPU.

### 6. Pattern B on LongMemEval Tier-1 (persistence benchmark)
Pattern B's bitemporal as-of + role-binding decomposition should win on temporal queries.

Method: 200 LongMemEval temporal questions; Pattern B vs vanilla RAG vs bare LLM.

HARD-PASS: Pattern B accuracy >= 60% AND beats vanilla RAG by >= +0.10 absolute.
HARD-FAIL: Pattern B < 50% accuracy OR LLM ignores retrieved context.

Wall: 4-6 hours CPU.

### 7. Pattern B on FActScore (attribution benchmark)
Pattern B's selective-disclosure Merkle proof gives provable attribution per fact.

Method: 20 biographical entities; Pattern B retrieval + Qwen generation; FActScore the
output (attribution-weighted accuracy).

HARD-PASS: FActScore >= 65% AND attribution coverage >= 90%.

Wall: 4-6 hours CPU.

### 8. Substrate vs vanilla RAG on HybridQA-style structured aggregates
substrate_structured_aggregates HP'd at COUNT/SUM=1.000 vs vanilla LLMs <0.50. Validate
on a published structured-aggregate benchmark.

Method: HybridQA or similar; 200 queries; substrate vs vanilla.

HARD-PASS: substrate accuracy >= 0.90 AND beats vanilla by >= +0.40 absolute.

Wall: 3-5 hours CPU.

---

## TIER C: storage compression follow-ups (CPU/local GPU)

### 9. 8-16x codebook-aware PQ on Pattern A W
PQ-on-W at 256x collapsed recall (cycle 162 LVH #260). Try the recommended 8-16x target
with codebook-aware encoding.

Method: PQ at 8x and 16x compression; codebook-aware (cluster W rows by similarity first;
quantize within clusters); measure retrieval F1.

HARD-PASS: 16x compression with F1 drop <= 3%.

Wall: 2-3 hours GPU.

### 10. Composite indexing on Pattern A
Already authorized in the 4-drill consolidated routing but pending; flagging for explicit
queue position.

### 11. SQL AVG formula fix verification
Highest priority from 4-drill consolidated; 30 min CPU; may retroactively upgrade cycle
155 MID to HP.

Already authorized in the 4-drill consolidated routing but pending; flagging for explicit
queue position.

---

## Sequencing

Tier A in parallel as capacity allows; ~6-8 hours CPU + 30 min local GPU.
Tier B sequential after Tier A informs (per-benchmark integration overhead).
Tier C in parallel with Tier A or B.

Total wall if parallelized: ~1 day to clear most of the battery; ~2 days for benchmark
runs.

## What this battery enables

- Pattern B production-scale validation across 100K and 1M facts (currently smoke only)
- Predicate routing ceiling identified (currently known viable at 1-20%, ceiling unknown)
- Substrate-as-candidate-generator empirically validated as Pattern B's retrieval value-add
- Co-compliance demo asset for regulators (Art 12 + Art 17)
- Pattern B competitive on benchmark suite (HotpotQA, LongMemEval, FActScore, HybridQA)
- Storage compression ceiling tested via PQ + composite indexing
- AVG aggregation may upgrade from MID to HP via formula fix

## Cross-references

- Cycle 162: notes/orchestrator_to_research_results_summary_2026-06-07_cycle162.md
- Top 20 unrouted: notes/research_to_exp_dev_top20_unrouted_experiments_2026-06-07.md
- 4-drill consolidated: notes/research_to_exp_dev_four_drills_consolidated_authorize_2026-06-07.md
- Composition regime pre-tests: notes/research_to_exp_dev_substrate_composition_regime_pretests_2026-06-07.md
- Testbed follow-ons (1M + Tier-1 HotpotQA): notes/research_to_exp_dev_two_testbed_followon_fast_2026-06-07.md
- ZKL alternatives crazy ideas 3x (in flight): notes/research_drill_zkl_alternatives_crazy_ideas_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all 11 cells per Tier A/B/C sequencing. Tier A is highest priority
(production scale validation of cycle 162's smoke wins). Apply decision rules autonomously
per cell. File synthesis on batches.
