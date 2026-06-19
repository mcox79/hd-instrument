# exp_dev hand-off -- research: image-schema polysemy rescue (2026-06-10)

**Filed:** 2026-06-10 by research sub-agent (Sonnet, 2x depth drill).

**Trigger:** PP-316 image-schema grounding HARD_FAIL on real polysemic ConceptNet abstract concepts (accuracy 0.342; synthetic was 1.000 via orthogonality artifact). Research drill delivered context-binding rescue paths. See: `notes/research_drill_image_schema_polysemy_negative_2x_2026-06-10.md`.

**Pause state:** Read `data/orchestrator_paused.flag` at dispatch time. If present, do NOT ship to queue. Annotate-only.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## What the research drill established (epistemic state)

PP-316 failure is a retrieval-protocol problem, not a representation problem. The stored atom for a polysemic abstract concept is a superposition of sense vectors; cleanup without context yields an averaged or glassy result. Three substrate-native rescue mechanisms are deployable on the current substrate with no new architecture:

1. **Hopfield-with-context-bias (D2.6):** Add a context-aligned quadratic term to the cleanup energy function. Single additional vector operation per retrieval call. Grounded in DMHN paper (arxiv 2506.01303, June 2026): 64% accuracy at 2N storage vs 13% standard modern Hopfield.

2. **Context-bound-embedding (D2.1):** Store senses as bound atoms (concept XOR context) using existing FHRR binding. Query as (concept XOR context_current). Highest P_deflated = 0.42. Requires preprocessing ConceptNet polysemic concepts to tag senses.

3. **Mixture-of-senses-gating (D2.5):** Cluster ConceptNet relations by relation type (IsA, HasA, CapableOf, etc.). Gate retrieval on active relation type. P_deflated = 0.35. Works if relation type is a reliable sense discriminator for abstract concepts.

The decisive test discriminates all three paths in one run: compare baseline PP-316 accuracy (0.342) against each mechanism on the 50 polysemic abstract ConceptNet concepts that originally failed.

---

## Anchor candidates (rank-ordered)

### 1. PP-316-CONTEXT-BIAS -- Hopfield context-bias rescue (cheapest, no re-storage)

- **Anchor pointer:** research note D2.6; DMHN paper arxiv 2506.01303 as theoretical precedent.
- **Substrate-product reading:** Modifies only the retrieval kernel (cleanup step). No re-storage of atoms, no preprocessing. Adds a single hyperparameter (alpha = context bias strength). Context vector constructed at query time from ConceptNet neighbor atoms of the relation type. If alpha > 0 raises accuracy from 0.342 to >= 0.60, the substrate has a deployable fix for abstract polysemy with zero data-structure cost.
- **Tier hint:** CPU. Pure vector arithmetic on existing infrastructure. Smoke run on 50-concept subset: fast.
- **Why now:** This is the lowest-cost rescue for a HARD_FAIL that blocks product claim for abstract knowledge retrieval. The DMHN paper provides direct empirical precedent. No prior art gap.
- **HARD-PASS / HARD-FAIL bands:** exp_dev to set. Research pre-registers: HP = accuracy >= 0.60 on polysemic abstract 50-concept set; HF = accuracy < 0.50 even with alpha tuned on held-out 10-concept validation set.

### 2. PP-316-CONTEXT-BIND -- context-bound-embedding rescue (cleanest algebraic path)

- **Anchor pointer:** research note D2.1; Plate (1995) HRR, Kanerva (2009) HDC survey.
- **Substrate-product reading:** Preprocess ConceptNet polysemic abstract concepts: for each concept, identify 2+ senses using relation type as discriminator. Store bound atoms: atom_sense_i = concept_atom XOR context_atom_i. At query time, construct probe = concept_query XOR context_current. Cleanup resolves to the matching sense. Requires a preprocessing pass over ConceptNet abstract concept subgraph to identify and tag polysemic concepts (those with >= 2 distinct relation type clusters).
- **Tier hint:** CPU. Preprocessing is a one-time pass. Retrieval cost is identical to current (XOR is elementwise).
- **Why now:** Algebraically cleanest fix; P_deflated = 0.42 (highest of all mechanisms). If context-bias (anchor 1) partially succeeds but does not reach 0.70, context-binding is the upgrade path.
- **HARD-PASS / HARD-FAIL bands:** exp_dev to set. Research pre-registers: HP = accuracy >= 0.70 on polysemic abstract 50-concept set with senses pre-tagged; HF = accuracy < 0.50 (implies context vectors from ConceptNet relation types are not sense-discriminating).

### 3. PP-316-SENSE-GATE -- mixture-of-senses gating by relation type

- **Anchor pointer:** research note D2.5; ConceptNet 5.5 paper (arxiv 1612.03975).
- **Substrate-product reading:** Use ConceptNet relation type (IsA, HasA, CapableOf, UsedFor, AtLocation) as a coarse-grained sense gate. At query time, caller specifies which relation type is relevant. Retrieval restricted to atoms in that relation-type cluster. Tests whether the PP-316 failure is driven by relation-type polysemy specifically (abstract concepts span multiple relation types that are being conflated into one representation).
- **Tier hint:** CPU. Requires indexing ConceptNet atoms by relation type (one-time preprocessing). Retrieval is a filtered nearest-neighbor search.
- **Why now:** Interpretable failure mode: if this works, it tells us exactly WHICH senses were being conflated. If this fails, it narrows the cause to within-relation-type ambiguity.
- **HARD-PASS / HARD-FAIL bands:** exp_dev to set. Research pre-registers: HP = accuracy >= 0.65 on polysemic abstract 50-concept set gated by relation type; HF = accuracy < 0.45 (implies polysemy is not relation-type-driven, need deeper sense inventory).

---

## Stretch candidate (if exp_dev has bandwidth)

4. **PP-316-SYMMETRY-BREAK -- epsilon-context injection before cleanup (D2.8):** Simplest possible test of whether any context signal helps. Apply probe = concept_query + epsilon * context_vector before cleanup, varying epsilon from 0 to 1. Measures the marginal value of context without any architectural change. Acts as a diagnostic for whether the context-vector direction correlates with sense discrimination at all. CPU, 1-2 hours. P_deflated = 0.32.

---

## Context pointers (pointers not summaries -- exp_dev reads what is needed)

- Research note (full analysis): `notes/research_drill_image_schema_polysemy_negative_2x_2026-06-10.md`
- DMHN paper: arxiv 2506.01303 (Dynamic Manifold Hopfield Networks, June 2026)
- HRR binding reference: Plate (1995), Kanerva (2009)
- ConceptNet data: `data/conceptnet/` (existing extraction from arXiv pipeline)
- PP-316 failure data: locate via `data/exp_PP-316/` or equivalent experiment output directory
- Image schema grounding post-compaction brief: `notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md`

---

## Contract

exp_dev owns: anchor naming, N/M/K/seed/threshold/queue assignment, smoke gate, dispatch, post-ship verify.
Research owns: mechanism specification, P_deflated estimates, HARD-PASS / HARD-FAIL pre-registration, context pointer list.
This hand-off is complete. No further research input is needed before dispatch unless HF1 fires (all three mechanisms fail), in which case escalate to RSB spin-glass drill.

## Autonomy declaration

exp_dev has full autonomy to: modify mechanism details for substrate compatibility, reorder anchors based on queue state, batch all three into one CPU run, or hold any anchor pending queue availability. Research does not gate exp_dev execution on research sign-off.
