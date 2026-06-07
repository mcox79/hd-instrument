# exp_dev hand-off -- research: sparse-KEY low-B regime reconciliation 2x

**Filed-by:** research sub-agent (2026-06-07)
**Trigger:** d:/AI/hd-instrument/notes/research_drill_sparse_key_low_B_regime_reconciliation_2x_2026-06-07.md
**Pause state:** check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file passes ANCHOR POINTERS and
CONTEXT POINTERS only. exp_dev reads the research note for the full theoretical background and
designs its own experiment code from first principles.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- SPARSE_KEY_B10_COHERENT_DISTRACTORS (tier: high, CPU, ~2 hr)
**Anchor pointer:** Section 4 of the research note (cheap decisive cell)
**Substrate-product reading:** Tests whether the 10x c_d reduction from sparse-KEY at
  alpha=0.005 actually translates to higher answer accuracy at K=8 and K=12 when B=10
  shards bundle with coherent distractors (c_d=0.28 injected). This is the primary test
  distinguishing Option A (sparse always) from Option B (sparse only at B=1).
**Tier hint:** CPU. N=4096, B=10, 5 seeds, K sweep 1..15, 3 configs (dense-only,
  sparse-only, dense-first-sparse-after-hop-3). Wall ~2 hr on remote CPU.
**Why now:** The reconciliation analysis shows that LVH #248's tie result was a synthetic
  artifact (random distractors). Before enabling sparse-KEY as the v1 default, confirm
  that coherent distractor c_d reduction works as predicted. This is the cheapest cell
  with maximum decision-gate value for the v1 config.
**Pre-reg bands:**
  HP: accuracy@K=8 sparse-only > dense-only by >= 20pp
  MID: sparse > dense by 5-20pp (helps but needs confidence threshold to reach K=12)
  HF: sparse-only accuracy indistinguishable from dense-only at B=10, coherent distractors

### Anchor 2 -- SPARSE_KEY_B10_PLUS_CONFIDENCE_THRESHOLD (tier: medium, CPU, ~3 hr)
**Anchor pointer:** Section 5 / HP-3 of research note; Mitigation 5 of K-hop drill
**Substrate-product reading:** Full production config: sparse-KEY at intermediate hops +
  T=0.85 confidence threshold at coordinator bundling. Tests whether combined mitigation
  gives K_max >= 12 at B=10 with coherent distractors (c_d=0.28). This is the complete
  v1 config validation.
**Tier hint:** CPU. Extension of Anchor 1 with Config 4 added.
**Why now:** Analytic prediction is K_max ~ 20-90 with combined mitigation. Production
  target is K=12. This confirms or refutes the "sparse + threshold = v1 production default"
  recommendation.
**Pre-reg bands:**
  HP: K_max >= 12 at B=10, c_d=0.28 with sparse + threshold (accuracy@12 > 0.50)
  MID: K_max in [6, 12) -- functional but below production target; increase N
  HF: K_max < 6 -- combined mitigation insufficient; semantic sharding needed in v1

### Anchor 3 -- DISTRACTOR_COHERENCE_MEASUREMENT (tier: critical, CPU, ~2 hr)
**Anchor pointer:** Cell A from K-hop noise drill (2026-06-07 notes)
**Substrate-product reading:** Measures c_d_empirical for real production facts using the
  Llama-1B BASE encoder. This single measurement determines whether the production
  architecture is in the coherent distractor regime (Option A justified) or the random
  distractor regime (LVH #248's tie generalizes; Option A less important).
**Tier hint:** CPU. 100-shard substrate, N=1024, Llama-1B embeddings. Wall ~2 hr.
**Why now:** Load-bearing cell for the entire v1/v2/v3 architecture. All Option A/B/C
  decisions flow from c_d_empirical. Run BEFORE enabling sparse as v1 default.
**Pre-reg bands:**
  HP: c_d_empirical < 0.20 (random distractor regime; averaging model holds)
  MID: c_d_empirical in [0.20, 0.40] (coherent; confidence threshold sufficient)
  HF: c_d_empirical > 0.40 (severe; semantic sharding needed in v1 spec)

---

## Context pointers (file paths)

- Research note (this hand-off's trigger):
  d:/AI/hd-instrument/notes/research_drill_sparse_key_low_B_regime_reconciliation_2x_2026-06-07.md

- K-hop noise model selection drill (source of distractor framework):
  d:/AI/hd-instrument/notes/research_drill_khop_noise_model_selection_2x_2026-06-07.md

- Sparse-KEY composition partners drill (composition context):
  d:/AI/hd-instrument/notes/research_drill_sparse_key_composition_partners_2x_2026-06-06.md

- LVH #248 verdict (cycle 151 empirical finding being reconciled):
  data/exp_SPARSE_KEY_B_REGIME/metrics.json (or equivalent cycle 151 verdict path)

---

## Contract section

These anchors are CONDITIONAL on Cell A (Anchor 3) results:
- If Anchor 3 shows c_d_empirical < 0.10: Anchors 1 and 2 have lower priority
  (production is random distractor regime; LVH #248 tie generalizes)
- If Anchor 3 shows c_d_empirical > 0.10: Anchors 1 and 2 are HIGH priority
  (production is coherent distractor regime; Option A / Option A+threshold needs empirical confirmation)
- Anchor 3 is the cheapest and most load-bearing. Run it first if parallelism is constrained.

## Autonomy declaration

exp_dev designs all experiment code from scratch using the anchor pointers and theoretical
context in the research note. This file passes structure and priority only. No inline design.
