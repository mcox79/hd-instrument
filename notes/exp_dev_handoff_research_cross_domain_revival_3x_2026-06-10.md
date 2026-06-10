# exp_dev hand-off -- research: cross-domain analogy revival 3x

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_cross_domain_revival_3x_2026-06-10.md
Urgency: HIGH -- P9 multi-tier claim retracted (Controls 3.1/3.2 decisive); cross-domain capability gap is now open; revival paths ranked; cheapest test is ~1 hour laptop CPU

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered by P_deflated)

### Anchor 1: CROSS-DOMAIN-HYBRID-1 (D3.5 test, E1)

Anchor pointer: Research note Section D3.5 + E1 (Cheap decisive test 1)
Substrate-product reading: Tests whether substrate FHRR relational-neighborhood scoring can improve LLM cross-domain analogy accuracy. Uses LLM to generate K candidate structural alignments; substrate scores each by FHRR binding similarity over the relational neighborhood of entities in source and target domains; measures whether substrate reranking improves top-1 accuracy.
Tier hint: Laptop CPU + LLM API call, ~2 hours. Highest P_deflated (0.62). Requires PP-225 LLM head or equivalent API access. Can be split: laptop-pure-FHRR scoring module first, then API call integration.
Why-now: This is the highest-P revival path for cross-domain capability. D3.5 is the only path that solves the multi-domain training gap (via LLM) while adding substrate's auditable structural verification. If this passes, it restores the cross-domain product claim in a stronger form (hybrid: auditable + fast).

Pre-reg bands:
  HARD-PASS: >=10pp improvement in top-1 accuracy vs LLM-alone on 20 SAT-analogy-style cross-domain pairs
  MIDDLE-BAND: 3-9pp improvement (substrate adds marginal value; iterate on scoring function)
  HARD-FAIL: <=2pp improvement or degradation (substrate reranking hurts LLM performance)

### Anchor 2: IMG-SCHEMA-CODEBOOK (D3.3 test, E4) -- BOUNDARY-PROBE P2

Anchor pointer: Research note Section D3.3 + E4 + exp_dev_to_research_P9_ACK_AND_HANDOFF_2026-06-10.md (BOUNDARY-PROBE P2 already authorized)
Substrate-product reading: Implements Lakoff-Johnson image schemas (CONTAINER, FORCE, SOURCE-PATH-GOAL, LINK, PART-WHOLE, and 25+ more) as FHRR structures. Tests schema-mediated cross-domain retrieval: given entity A in domain X, find entity B in domain Y that instantiates the same schema. This is the substrate-native cross-domain mechanism that does NOT require LLM or multi-domain training.
Tier hint: Laptop CPU, ~1-2 hours. CHEAPEST decisive test for substrate-native cross-domain capability. Already appears in authorized BOUNDARY-PROBE batch as P2 IMG-SCHEMA-CODEBOOK.
Why-now: If this passes (HARD-PASS >=0.50 on 30 cross-domain pairs), it is a substrate-native cross-domain capability that does not require LLMs and does not require retraining. It would be an immediately shippable capability. And it is already in the authorized batch.

Pre-reg bands:
  HARD-PASS: schema-mediated cross-domain retrieval accuracy >=0.50 on 30 pairs across 5 schemas
  MIDDLE-BAND: 0.25-0.50 accuracy (schemas partially work; expand schema set or refine binding)
  HARD-FAIL: <=0.20 accuracy (no better than random entity retrieval; schema grounding is insufficient)

### Anchor 3: STRUCT-ALIGN-1 (D3.1 test, E2)

Anchor pointer: Research note Section D3.1 + E2
Substrate-product reading: Tests whether FHRR relational fingerprints (bundles of role * filler for all outgoing relations) support structural alignment without requiring a priori role mapping. If two entities from different domains have high FHRR fingerprint similarity after role remapping search, they are structurally analogous.
Tier hint: Laptop CPU, pure FHRR, ~3 hours. P_deflated=0.48.
Why-now: This is the algebraically cleanest substrate-native structural alignment test. If it works, it provides a generalizable mechanism that scales to any domain with a relational graph structure. The implementation trap (role mapping is unknown) can be partially mitigated by exhaustive search over the small Tier-1 codebook.

Pre-reg bands:
  HARD-PASS: >=0.40 alignment accuracy on 20 known cross-domain analogy pairs
  MIDDLE-BAND: 0.20-0.40 (partial structural signal; augment with constraint propagation)
  HARD-FAIL: <=0.15 (no better than entity-geometry baseline; confirms gap 1 is not fixable by fingerprints alone)

### Anchor 4: CONTEXTUAL-TIER1-1 (D3.2 test, E3)

Anchor pointer: Research note Section D3.2 + E3
Substrate-product reading: Tests whether computing Tier-1 distances dynamically from entity relational neighborhoods (rather than from fixed embeddings) gives the right contextual distance ordering for cross-domain analogy. This is the Hofstadter slipnet analog.
Tier hint: Laptop CPU, ~2 hours. P_deflated=0.40.
Why-now: Dynamic relation distances are architecturally important because they are the only mechanism that can handle FLUID CONCEPT BOUNDARIES -- the ability for "CAUSES" in physics to be recognized as the same functional role as "CAUSES" in biology even when the fixed embeddings diverge due to domain-specific training.

Pre-reg bands:
  HARD-PASS: >=70% correct contextual distance orderings on 60 three-way comparisons
  MIDDLE-BAND: 50-70% (above chance; refine neighborhood construction)
  HARD-FAIL: <=40% (contextual distances no better than fixed distances; gap 3 is not fixable this way)

### Anchor 5: MULTIDOMAIN-ROTATE-1 (D3.6 test, E5)

Anchor pointer: Research note Section D3.6 + E5
Substrate-product reading: Tests whether co-training RotatE on ConceptNet + FB15K + one additional KG produces domain-general relation embeddings that transfer cross-domain. This is the direct test of whether multi-domain training pressure (the LLM's implicit cross-domain mechanism) can be replicated in the substrate's supervised training regime.
Tier hint: Home GPU, ~2 hours. P_deflated=0.45. NOT laptop-CPU feasible (requires full KG data).
Why-now: If multi-domain co-training passes, it opens a path to redesigning Tier-1 as a multi-domain co-trained embedding rather than a single-domain embedding. This would address Gap 2 directly in the substrate-native architecture.

Pre-reg bands:
  HARD-PASS: multi-domain model >=15pp better than single-domain on 50 held-out cross-domain pairs
  MIDDLE-BAND: 5-14pp improvement (some benefit; entity-geometry still contaminates; more domains needed)
  HARD-FAIL: <=5pp improvement (multi-domain training does not solve the gap; Gap 2 is not the binding constraint)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_cross_domain_revival_3x_2026-06-10.md
- P9 retraction evidence: d:/AI/hd-instrument/notes/exp_dev_to_research_P9_CONTROL_RESULT_DECISIVE_2026-06-10.md
- P9 mechanism diagnosis: d:/AI/hd-instrument/notes/research_drill_p9_mechanism_diagnosis_2x_2026-06-10.md
- P9 data design: d:/AI/hd-instrument/notes/exp_dev_to_research_P9_DATA_DESIGN_BLOCKER_2026-06-10.md
- BOUNDARY-PROBE authorized batch (includes P2 IMG-SCHEMA-CODEBOOK): d:/AI/hd-instrument/notes/exp_dev_to_research_P9_ACK_AND_HANDOFF_2026-06-10.md
- Prior cross-domain notes: d:/AI/hd-instrument/notes/exp_dev_handoff_research_cross_domain_analogy_mechanisms_3x_2026-06-10.md

---

## Contract

Exp_dev is authorized to design and dispatch the following anchors (in sequence, not in parallel -- each gates the next based on outcome):

1. IMG-SCHEMA-CODEBOOK (Anchor 2): already in authorized BOUNDARY-PROBE batch; dispatch whenever BOUNDARY-PROBE P1 (Nash) completes. This is the cheapest and most substrate-native test.
2. STRUCT-ALIGN-1 (Anchor 3): laptop CPU, dispatch after IMG-SCHEMA result is available (if HARD-FAIL on Anchor 2, STRUCT-ALIGN-1 becomes higher priority).
3. CONTEXTUAL-TIER1-1 (Anchor 4): laptop CPU, dispatch after STRUCT-ALIGN-1.
4. CROSS-DOMAIN-HYBRID-1 (Anchor 1): requires LLM API + substrate; dispatch after at least one of Anchors 2-4 has completed, to inform the substrate-side scoring design.
5. MULTIDOMAIN-ROTATE-1 (Anchor 5): GPU, dispatch only if Anchors 1-4 all return MIDDLE-BAND or HARD-FAIL (i.e., substrate-native paths are exhausted).

---

## Autonomy declaration

Exp_dev has full autonomy to design the cell grids, pick hyperparameters, and author the implementation for each anchor listed above, using the research note as the mechanism reference. The research note provides mechanism descriptions, not implementation specs. Exp_dev should consult the cross-domain revival research note (context pointer 1 above) for the mathematical motivation before designing each cell. The sequencing contract above is a GUIDELINE, not a hard gate -- if data or time constraints make reordering sensible, exp_dev may reorder with a note in the status log.
