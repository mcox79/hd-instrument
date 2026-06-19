# RESEARCH (Director) -> USER: substantive update -- 20h sprint progress + A2 v6 VERDICT LANDED (ALREADY_SEPARATES; untuned AUROC=0.9652 on 41330 PRE-INGEST scope per Skunkworks A-now ruling). 2 Items LANDED this window (mining-script layer-3 + Phase-portrait v1) + 1 cascading verdict (A2 v6) + Skunkworks verdict-VET imminent. The untuned substrate ALREADY separates gap vs in-coverage on the pre-ingest corpus -> LoRA Stage-2 has NO headroom; calibrated threshold suffices. 5-layer audit-lesson framing addendum + substrate-discipline self-applying pattern continuing visibly. Push-pipeline-DOWN remains priority-0 (your lane).

**From:** Research (Director)  **To:** USER  **Date:** 2026-06-18 ~19:25 PDT  **Re:** 20h sprint progress + A2 v6 verdict + 5-layer addendum. ASCII; fname_v2.

## Bottom line (one sentence)

The 20h sprint is delivering: 2 Items LANDED clean (Item 2 cert-integrity tooling encoding the 5-layer audit-lesson + Item 3 Phase-portrait v1 substantive Director piece both atomized with all structural guards held + sub-counts independently verified by Skunkworks) + a major substantive cascading verdict (A2 v6 = ALREADY_SEPARATES; untuned bge-confidence AUROC=0.9652 on the 41,330 pre-ingest corpus; the untuned substrate already separates gap vs in-coverage -> the planned LoRA Stage-2 has NO headroom; a calibrated threshold suffices) + the substrate-discipline self-applying pattern continuing (4 distinct lessons-applied-forward in real-time this cycle).

## Items LANDED this window

**Item 2 (cert-integrity maintenance) sub-component LANDED:**
- Mining-script layer-3 value-RESOLVES + layer-4 id-FORM check encoding Skunkworks's 5-layer AUDIT_LESSON into `tools/scour_capability_optimality.py`
- Surfaced EXACTLY 3 phantom current_bests (PP-371 + PP-395 + PP-396) -- matches Skunkworks's prediction (23 resolved-clean / 0 ambiguous)
- Substrate-autonomy at cert-integrity layer: audit-lesson -> deterministic check; future scours auto-flag phantoms without manual review
- 3/24 phantom cleanup queue concretized; Exp-Dev investigation chain clear (PP-371 Option 3 ruled; PP-395/396 investigate-first per evidence-tier)

**Item 3 (Phase-portrait v1) LANDED:**
- PORTRAIT_v1_2026-06-18 atomized; PHASE_PORTRAIT AtomKind added (sibling to capability_map)
- atoms 43,895 -> 43,896 (+1); axiom_term 206 unchanged; cap_pres 6/6; CERT 570 unchanged (INVENTORY_NON_CERT correctly excluded)
- 574 cert atoms inventoried; honest 148 UNCLASSIFIED + 517 UNTAGGED_REGIME (v1-honest-scope caveat present: "SPARSE-MEASURED INVENTORY, NOT a coverage-map")
- Skunkworks landed-verify PASS (independent re-derivation; all sub-counts match)
- The optimal-OPERATING-POINT face of the mining unification is now Store-resident (composes with capability-mining's optimal-APPROACH face)

## A2 v6 VERDICT LANDED -- the substantive cert-event of the sprint

**Verdict:** ALREADY_SEPARATES; branch_path=untuned_refuse_gate_auroc
**Metrics:**
- untuned_auroc = 0.9652 (band: already_separates >= 0.7; near_chance [0.45,0.6])
- near_gap_auroc = 0.9338
- far_gap_auroc = 1.0
- n_gap = 38; n_in_cov = 34; n_cells = 72
- run_mode = full; metrics_source = measured_bge; gate0_self_check PASS (72/72); discrimination_self_check discriminates=true (0.965, both classes + spread)
- cell_commit d78ffe8a; anchor substrate_a2_decisive_test_untuned_auroc_gpu_v1

**Interpretation (Orchestrator's verdict_msg):**
"The untuned substrate ALREADY separates gap vs in-coverage by raw bge-confidence -> LoRA Stage-2 has NO headroom; a calibrated threshold suffices."

**SCOPE (load-bearing):** measured on the 41,330 PRE-INGEST corpus (remote frozen at a95b47b4; FrameNet/WordNet ingests in unpushed backlog per the push-pipeline-DOWN). Per Skunkworks's A-now ruling: this is a valid + useful pre-ingest measurement (the gap-set is valid on 41,330; pipeline-validation milestone after 7 dispatch causes; +2,562 ingests semantically orthogonal so 41,330 is a likely-close proxy for 43,892). The C-deferred grown-corpus measurement remains post-push-fix.

**Honest CAVEATS baked into the metrics (don't oversell):**
- Tarjan-SCC + Hopcroft-Karp scored AS GAPS but get high confidence -- a refuse-gate precision limitation the eval EXPOSES (not papers-over)
- Or residual leakage despite TF-IDF 0.510 -- inspect top gap confidences (recommended follow-up)
- coincidental_mention_caveat preserved

**Skunkworks verdict-VET imminent** (per their note): SCOPED PRE-INGEST + band-meaning + confidence-spread + per-item independent recompute sample + cert-grade-IF-bands-met + pre-ingest scope-caveat verbatim in the atom. The B-beta gate decision uses the result WITH that scope.

## What this means in plain English

You ratified the depth-cliff sprint as the centerpiece-cycle and the next-20h sprint as CONSOLIDATE-HARDEN-BROADEN. Within ~30 minutes of GO, both sub-character claims are paying off:

1. **HARDEN:** the mining-script layer-3 enhancement encoded the 5-layer audit-lesson as a deterministic check -> future phantom-current_bests auto-flag without manual review. This isn't a one-time fix; it's a discipline-machine.

2. **BROADEN:** the Phase-portrait v1 atom is the substrate's first INVENTORY of measured operating regimes -- honest-sparse (acknowledges 517 atoms aren't operating-point-tagged) but Store-resident + queryable. v2 will deepen the heuristics + structured key_metrics axes.

3. **CERT-EVENT (was lower-promised; over-delivered):** A2 v6 ALREADY_SEPARATES on pre-ingest is a major positive finding even with the corpus-mismatch caveat. The substrate's refuse-gate doesn't need the LoRA Stage-2 work we'd queued -- the untuned mechanism already discriminates at AUROC 0.965. This is the kind of "we don't need more architecture; we need calibration" insight that saves engineering time + corresponds with the "substrate is more capable than first-pass implies" pattern you've been calling out symmetrically.

## Substrate-discipline self-applying pattern (4 layers this cycle)

The lesson-applied-forward pattern visible 4 times in real-time:

1. **B1 layer-4 id-FORM check** -- Exp-Dev verified atom-id EXISTS before setting RETRIEVAL_multi_hop current_best (the value-RESOLVES check from the 5-layer audit-lesson; the very next mutation after the lesson framed it)
2. **Field-LOCATION metadata-vs-top-level** -- Exp-Dev placed phase-portrait provenance_quality INTO metadata per cap_map precedent (B1 layer-4 generalized; from_dict doesn't lift top-level fields)
3. **Investigate-first generalization** -- Skunkworks's PP-371 lesson (evidence-tier governs resolution) generalized to PP-395/396 cert-call (not blanket-B; investigate each)
4. **Audit-lesson -> deterministic check** -- the mining-script encoding the 5-layer AUDIT_LESSON as automatic phantom-detection -> substrate-autonomy at cert-integrity layer

This is the cert-discipline functioning as a discipline-MACHINE: each lesson generates a check; each check catches the next class of similar defect; each catch yields a sharper lesson; the loop closes itself. The depth-cliff sprint produced these as concepts; the 20h sprint is encoding them as MECHANISMS.

## 5-layer audit-lesson framing addendum (per my earlier note)

I'd filed an earlier USER-visibility note describing the cert-discipline catches as 4-layer. Skunkworks's deeper investigation showed it's actually 5-layer:

1. field-value-EXISTS (Director mining correct)
2. field-LOCATION metadata-vs-top-level (Exp-Dev wrong-field caught)
3. value-RESOLVES-to-an-atom (Skunkworks's deeper catch -- PHANTOM)
4. id-FORM bare-vs-qualified (Skunkworks's self-catch -- must use a.qualified_id not a.id)
5. disagreement-as-information (the disagreement didn't vanish after both verified -> the catch)

Skunkworks atomized this as a durable AUDIT_LESSON earlier (now landed); the mining-script enhancement encodes layers 3+4 as automatic. The framing carries forward.

## Substrate state right now

- **LOCAL atoms 43,896** (+1 PORTRAIT_v1_2026-06-18 this cycle)
- **REMOTE atoms 41,330 FROZEN** at a95b47b4 (origin/main); 17+ commits unpushed (push-pipeline-DOWN persists)
- **CERT 570** unchanged this cycle (Phase-portrait is INVENTORY_NON_CERT; A2 v6 atomize pending Skunkworks verdict-VET)
- **MEASURED_MECHANISM 4** (depth-cliff Phase A2 + 3 earlier)
- **METHODOLOGY_RULE 48** + **AUDIT_LESSON 50** (Skunkworks at-bandwidth queue complete)
- **capability_map 1** + **phase_portrait 1** (today's NEW AtomKind)
- **self-cert engine 7 gates LIVE**
- **Testbed 2nd-witness 38/38 cumulative this arc**

## What's still in flight

- Skunkworks: A2 v6 verdict-VET imminent + PART_OF cell SCHEMA-VET + ConceptNet cell SCHEMA-VET + 3-phantom landed-verifies
- Exp-Dev: vet_a2_v3_verdict run + PART_OF cell build (Item 1 -- the ONE discriminating cert-experiment of the sprint) + ConceptNet cell build (Item 4; apply deferred) + 3 phantom investigations
- Orchestrator REPLACEMENT: A2 v6 dispatch chain complete; reactive on push-fix
- USER: push-fix bandwidth (priority-0; unlocks C-grown-corpus + HYP-5 + ConceptNet apply + cert-durability of 17+ unpushed commits)

## What I'm waiting on / who's blocking

- **USER (you):** push-fix bandwidth (architectural; gates the C-deferred chain + protects cert-durability)
- **Skunkworks:** A2 v6 verdict-VET (imminent) + Items 1/4 cell SCHEMA-VETs + 3-phantom landed-verifies
- **Exp-Dev:** Items 1/4 cell builds + 3 phantom investigations + vet_a2_v3_verdict run
- **Orchestrator REPLACEMENT:** reactive on push-fix; no other gates

The sprint is delivering ahead of pace. Next substantive event likely the Skunkworks A2 v6 verdict-VET (cert-grade or scoped-MEASURED_MECHANISM call) or Exp-Dev's PART_OF cell SCHEMA-VET completion.

-- Research (Director)
