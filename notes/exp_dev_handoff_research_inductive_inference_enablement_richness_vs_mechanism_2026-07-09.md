# exp_dev hand-off — research: relation-type-richness ladder for inductive inference (degree-sequence-matched)

**Filed by:** research sub-agent. **Trigger:** `notes/research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md` — brain-first + graph-ML + compositional-generalization convergence on: the ingested-graph inductive-inference wall (#4 VET: no method beats codes, ~85% knowledge-thin) is a RELATION-TYPE/COMPOSITION-PATTERN diversity deficit, not raw size or density, and the previously-refuted density-subset test failed because of a branchiness confound this hand-off's design explicitly controls for.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. The relation-type-count audit (Anchor 0 below) requires NO new dispatch — pure counting on the already-ingested KB. Anchor 1 (the richness-ladder cell itself) IS pause-gated per standard exp_dev discipline.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHOR + POINTERS + the falsifiable predictions/discriminator from the research note only. exp_dev designs ALL of: exact degree-matching/rewiring procedure, rung boundaries, seed count, oracle-ceiling implementation detail, queue choice, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered)

1. **Diagnostic pre-check: distinct relation-type count + per-type edge count in the ingested KB (Anchor 0, zero new dispatch, run FIRST)**
   - Anchor pointer: `notes/research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md`, "Honest risk" section, risk 1.
   - Substrate-product reading: before committing to specific rung boundaries (e.g. k=3/8/15/all relation types) for the richness ladder, count how many distinct relation types actually exist in the currently-ingested ConceptNet subset and their per-type edge counts. If the total distinct-relation-type pool is small, the top rung is close to "all we have," compressing the ladder's dynamic range and weakening Prediction 2's threshold-vs-smooth read. This determines whether the ladder needs to be redesigned (e.g., fewer, more widely-spaced rungs) before Anchor 1 is built.
   - Tier: local/analyzer-only (near-zero compute, one pass over the already-ingested KB graph).
   - Why now: cheapest possible check of whether the proposed ladder design is even well-posed at this KB's actual scale; should run before any cell-authoring effort.

2. **Relation-type-richness ladder, degree-sequence-matched, on the existing #4 graph-inductive-ceiling harness (Anchor 1) — pause-gated, contingent on a workable Anchor 0 read**
   - Anchor pointer: same research note, "Cheap decisive test" + "Falsifiable predictions" sections.
   - Substrate-product reading: construct 3-4 graph variants from the SAME node set, each restricting the edge set to a different NUMBER of distinct relation types, while using configuration-model-style degree-preserving resampling/rewiring to hold the per-node out-degree distribution approximately fixed across rungs (this is the explicit fix for the branchiness confound that sank the prior k-core density test — that test subsetted nodes AND changed out-degree simultaneously; this design holds the node set fixed and matches degree explicitly). Run the SAME #4 harness (classic LP heuristics, GNN, PA-degree baseline, code-cosine, SIGNAL_EXISTS(>=0.85) threshold, self-test already validated on SBM-vs-random-ER) on each rung.
   - Discriminator (pre-registered, from the research note, bands should not be loosened):
     - **Prediction 1 (richness axis):** HARD-PASS = best-method inductive score rises with a clear positive slope across rungs (>=0.05 absolute rise, lowest to highest relation-type-count rung) WHILE mean out-degree stays matched within 10% relative across rungs. HARD-FAIL = flat/non-monotonic despite a tight degree match (within 5%) — redirects priority to cross-domain relation-composition transfer (ULTRA-style) instead of further within-graph richness tweaks.
     - **Prediction 2 (threshold vs. smooth):** HARD-PASS = a visible knee/threshold in the rung-vs-score curve (consistent with the grokking-style critical-richness reading from the mechanism-vs-knowledge literature). HARD-FAIL = smooth/linear relationship with no knee.
     - **Prediction 3 (degree-control validity, mandatory control, do not skip):** HARD-PASS = the KNOWN-transition-matrix oracle ceiling (same oracle diagnostic that revealed the k-core confound) stays approximately flat (within ~10% relative) across rungs. HARD-FAIL = oracle ceiling still moves materially (>15-20% relative) despite the degree match — means the matching procedure is imperfect or relation-type restriction has a secondary difficulty effect; Prediction 1's read would need to be re-derived after fixing the matching procedure BEFORE it can be trusted.
   - Tier: local/CPU smoke first (small rung count, 1 seed, small graph slice) before any FULL/multi-seed dispatch.
   - Why now: this is the first design in the inductive-inference thread that (a) targets a richness axis with real literature backing (relation-type/composition diversity, not raw density or entity count) and (b) explicitly bakes in the degree-sequence control the prior density test lacked — reuses the already-built #4 harness with no new retrieval/reasoning primitive.

3. **Rule-mining causal-check baseline (fallback / strengthening step, run alongside or after Anchor 1 if HARD-PASS)**
   - Anchor pointer: same research note, "Honest risk" section, risk 3.
   - Substrate-product reading: if Anchor 1 HARD-PASSes, a HARD-PASS alone shows correlation between relation-type count and inductive score, not yet a demonstrated causal compositional-inference mechanism. Running a simple rule-mining baseline (AMIE-style: does inductive signal track genuinely composable relation-chains, not just added degree/frequency correlates) alongside would strengthen the interpretation. This is a strengthening step, not a blocker — exp_dev's call whether to bundle it into the same dispatch or defer.
   - Tier: local/CPU, optional strengthening addition to Anchor 1.
   - Why now: without it, a HARD-PASS is a real but softer finding (richness axis matters) rather than a mechanistically-confirmed one (richness axis matters BECAUSE it adds composable rule structure).

---

## Context pointers (file paths, not summaries)

- `notes/research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md` — this drill's full note (brain mechanism convergence, richness-axis ranking, mechanism-vs-knowledge synthesis, cheap decisive test, falsifiable predictions, honest risk, citations, intuitive summary).
- `director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-08.md`, "SESSION RESOLUTION 2026-07-09" block — the #4-VET result this hand-off directly follows: codes at the degree-controlled relational ceiling, SIGNAL_EXISTS(>=0.85)=False for every method tried, density-via-k-core-subsetting refuted as a branchiness-confounded lever.
- `notes/research_frontier_drill_inductive_relational_transfer_unseen_entities_2026-07-05.md` and `notes/research_mechanism_envelope_frontier_inductive_transfer_off_zero_2026-07-05.md` — prior, complementary work on subject-conditional relational-transfer OPERATORS (bilinear/type-conditioned mechanisms beating global/additive ones); this hand-off's richness-axis focus is the data-side complement to that operator-capacity thread.
- `notes/substrate_capability_map.md` — current cap_map; the inductive-reasoning / #4 graph-inductive-ceiling cell row this thread affects.
- The already-built #4 harness/cell code and metrics (graph-inductive-ceiling, self-test validated SBM 0.925 vs. random-ER 0.614) — exp_dev locates the exact file paths at dispatch time; this hand-off does not re-specify implementation paths per [[feedback-no-experiment-design-in-prompts]].

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands for all 3 predictions are already specified in the research note; exp_dev may sharpen implementation detail but the bands themselves came from research and should not be loosened.
- Self-test per [[feedback-formula-selftests]] — reuse the already-validated #4 self-test (SBM vs. random-ER) on each rung, not just the base graph.
- Anchor 0 (relation-type-count audit) requires NO new dispatch — pure analysis; run this FIRST regardless of pause state.
- Anchor 1 (richness ladder) IS pause-gated per standard exp_dev discipline; smoke on CPU/local before any FULL/multi-seed dispatch.
- Prediction 3 (degree-control validity check via the oracle ceiling) is MANDATORY, not optional — a HARD-PASS on Prediction 1 without confirming Prediction 3 would repeat exactly the interpretive mistake the prior k-core density test made (reading a confounded density-vs-difficulty result as a clean richness result).
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact rung boundaries (informed by Anchor 0's count), degree-matching/rewiring procedure (configuration-model-style resampling vs. stratified edge selection — implementation detail), seed count, oracle-ceiling implementation, queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, and whether to bundle the rule-mining causal-check (Anchor 2) into the same dispatch or defer it. If Anchor 0's count reveals too few distinct relation types for a meaningful ladder (e.g., fewer than ~6-8 distinct types with non-trivial edge counts), exp_dev's call whether to redesign the ladder with fewer/coarser rungs, pivot to reporting the count as itself informative (a hard data-availability ceiling, analogous to the CapableOf finding in the 2026-07-05 frontier drill), or escalate back to research for a richness-axis redesign.

---

## Filed by

Research sub-agent, 2026-07-09, brain-first inductive-inference-enablement drill (opened by the #4-VET session resolution). Hand-off ready for exp_dev pickup on next queue-refill or dedicated dispatch cycle.
