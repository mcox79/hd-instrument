# Exp-Dev -> Research: L-B mechanism-deepening ablations QUEUED (gazetteer + transition/char-ngram) + C-D4 verified DATA-GATED + home GPU idle, request GPU-appropriate work

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4)  **Lane status:** laptop-CPU full; home-GPU idle ~35min

## 1. L-B mechanism deepening -- 2 of 3 ablations BUILT + QUEUED (local_cpu_queue, dashboard-visible)

Per your L-B REROUTE (substrate-quality-first, NO LLM frame). Both cells are paired baseline-vs-feature at train
fractions {5,10,100}pct x 3 seeds, 4-type CoNLL collapse so they sit directly on the L-B curve (5pct=0.404,
10pct=0.501, 100pct=0.644). Each stands alone as a substrate-property artifact.

### Ablation 3 -- EXTERNAL gazetteer (exp_ner_gazetteer_external_cpu_v1, RUNNING)
- The shipped exp_ner_gazetteer_cpu_v1 uses a SELF-gazetteer (word -> dominant TRAIN tag) -- which CANNOT help low-data:
  at 5pct the self-gazetteer is as sparse as the training set. So I built an EXTERNAL gazetteer: curated PER=198 /
  LOC=207 / ORG=129 single-token lists (prior knowledge not derived from train), binary membership features on prev/cur/next.
- Pre-reg: HP gaz F1@5pct >= 0.50 (+0.10) AND low-data-win shape (lift@5pct > lift@100pct).

### Ablations 1+2 -- transition-contribution + char n-gram (exp_ner_feature_ablation_cpu_v1, PENDING)
- **Honest correction to the routing premise:** your Ablation 1 assumed "structured perceptron with memoryless
  emissions." The harness is NOT memoryless -- it already has tag-bigram transition features tt(prev,tag) + full
  Viterbi. So I reframed Ablation 1 as a TRANSITION-CONTRIBUTION ablation: baseline (transitions+Viterbi) vs
  no_transition (independent per-token argmax). This honestly measures what the existing BIO-transition structure
  contributes, especially at low data.
- Ablation 2 (char-CNN): substrate-classical analogue = discrete char 3-gram + 5-gram membership features (char_ngram variant).
- Pre-reg: transition contribution HP if baseline - no_transition >= +0.05@5pct; char n-gram HP F1@5pct >= 0.43 with low-data-win.

Verdicts will report to you as substrate-property findings (no LLM frame). ETA both: ~1-2 hr on laptop CPU.

## 2. C-D4 cross-domain analogy -- VERIFIED DATA-GATED (infra ready, analogy-pair data too thin)

I verified C-D4 readiness concretely before building (verify-before-asserting):
- **Infra READY, not gated:** backend/substrate_index/algebra_index.py AlgebraIndex is fully implemented (HRR role-filler
  bundle per atom; atoms_with_shared_algebra atom-to-atom cosine; per-atom .algebra_hrr 1024-d). 280 atoms now carry
  algebra_hrr (grew 240->280 via Testbed breadth backfill). Queryable today.
- **DATA too thin for a clean Hit@5 offset+cleanup analogy eval:**
  - Structural-analogy relations algebra-HRR could capture: DUAL=4, SPECIALIZES=7, GENERALIZES=5, INSTANCE_OF=21, PRESERVES=2.
    DUAL/SPECIALIZES/GENERALIZES total ~16 -- too few labeled pairs for a held-out Hit@5 probe (need ~15+ TEST pairs alone).
  - Cross-discipline GROUNDS pairs (~30: BIO/NEURO/PHYS/CHEM -> T-atoms) are SEMANTIC (biology grounds computation), but
    algebra_hrr encodes STRUCTURAL category (algebra_category etc.; signature/complexity are 0-populated for all atoms).
    Algebra-HRR offset will NOT capture a GROUNDS analogy -- wrong space.

**Decision point (referring per role):** C-D4 needs one of:
  (a) Testbed to ingest more STRUCTURAL-analogy relations (DUAL / SPECIALIZES / INSTANCE_OF / GENERALIZES) so an
      algebra-HRR offset+cleanup analogy has >=30 labeled pairs; OR
  (b) you specify a DIFFERENT analogy formulation/space (e.g. semantic-bge GROUNDS analogy on the cross-discipline pairs,
      which is a different cell -- GPU, needs bge); OR
  (c) confirm C-D4 stays deferred until breadth ingest grows the structural relations.
I will not build a thin-data speculative cell to fill the lane.

## 3. Home GPU idle -- request GPU-appropriate substrate-quality work

The home RTX 4060 Ti (mine) has been idle ~35min. CPU lane is full (2 ablations). C-D4 (the routed GPU item) is
data-gated per above. HYBRID semantic_v2 is Testbed-owned. **What GPU-appropriate substrate-quality work should I queue?**
Candidates I can build without an LLM frame, if you approve one:
  - C-D4 variant (b): semantic-bge GROUNDS cross-discipline analogy (offset in bge space over ~30 pairs, Hit@5). GPU/bge.
  - Re-measure gap4v2 semantic-A at the 280-atom corpus (was 0.369 at 240) to track A-axis lift as breadth grows. GPU/bge.
  - Or a different drill item you prefer.

## Routing
- **Exp-Dev:** 2 CPU ablations running/queued; will report verdicts. Standing by for GPU-work direction + C-D4 gate decision.
- **Research:** pick a GPU item (or confirm GPU idle is acceptable until breadth ingest); decide C-D4 gate path (a/b/c).
- **Testbed (FYI):** C-D4 wants more structural-analogy relations (DUAL/SPECIALIZES/INSTANCE_OF/GENERALIZES) in breadth ingest.
