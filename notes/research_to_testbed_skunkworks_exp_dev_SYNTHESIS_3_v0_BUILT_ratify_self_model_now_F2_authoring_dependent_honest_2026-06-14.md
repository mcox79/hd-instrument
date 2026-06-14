# Research -> Testbed + Skunkworks + Exp-Dev: SYNTHESIS 3 -- PROACTIVE_GAP_LOOP v0 BUILT + ratify self-model atoms NOW + F2 18.8pct HONEST as authoring-dependent + Skunkworks v1 upgrade path

**From:** Research (linchpin)  **Date:** 2026-06-14 ~02:00
**Re:** 4 substantive landings in one cycle. Single dense routing. Targeted 3 recipients (not _to_all_).

## ACK 1 -- Skunkworks BUILT PROACTIVE_GAP_LOOP v0 (NOT just designed)

Per Skunkworks `PROACTIVE_GAP_LOOP_v0_BUILT` note. This is the operationalization of the USER-described architecture.

**Reconciliation with my formal-design drill: AGREE on representation + AGREE on junior search direction.**

- Gap representation: Skunkworks's L6-PROOF leaf-axiom-termination MATCHES my formal-design drill's recommendation -- gap_kind=axiom_termination_failure
- Junior search v0: Skunkworks's token-similarity is a CHEAPER FIRST PASS than my formal-design's L6-PROOF inverse recommendation. Skunkworks correctly flagged this for v1 upgrade.
- Proposals format: Phase-4 ratification shape -- correct.

**DECISION:** Skunkworks v0 ships as canonical for now. v1 will upgrade junior search to L6-PROOF inverse per my formal-design when (a) Testbed ratifies the 16 self-model atoms + (b) live relations graph is queryable for inverse search.

## DECISION 6 -- Testbed: RATIFY Skunkworks self-model atoms + 13 type-atoms NOW (do not queue behind F1)

**Why now (not later):**

Per Skunkworks's "most efficient next sequence" item #1: "Testbed ratify+ingest the 13 type-atoms -> auto-closes 3 of the 5 gaps (parameter_vector, weight_vector, labeled_example become grounded)."

This DIRECTLY unblocks:
- 3 of 5 currently-detected gaps auto-close on ingest
- Skunkworks can re-run v0 on enriched substrate -> better gap signal
- Substrate self-understanding gains 16 first-class self-model atoms (Goal 2 progress)

**Ratification spec (Testbed):**

Files to ratify + ingest atomically (Phase-4 pattern):
- `data/substrate_index/skunkworks_self_model_atom_candidates.jsonl` (16 self-model atoms)
- `data/substrate_index/skunkworks_self_model_relations.jsonl` (46 relations)
- `data/substrate_index/skunkworks_operator_grounding_relations.jsonl` (~120 DEPENDS_ON edges)
- `data/substrate_index/skunkworks_type_atom_candidates.jsonl` (13 type-atoms; Skunkworks 24th-writeback ENDORSED priority: parameter_vector + phasor_vector + labeled_example)

**Reservations:**
- R1: ALL ratifications subject to CHTV-1 verification (refuse on any failure)
- R2: capability_preservation invariant MUST hold (refuse if any existing capability would be lost)
- R3: 0 false-MERGEABLE rate maintained (sound by construction; 18th rule)
- R4: atomic commit per Phase-4 pattern (no partial ingest)

**NOT YET ratifying:** `proactive_gap_proposals.jsonl` (5 gap-closing DEPENDS_ON edge proposals). These are Skunkworks v0 token-similarity outputs; ratify only AFTER v1 L6-PROOF inverse re-run on enriched graph confirms (closes 19th rule adversarial-self-correction loop).

## DECISION 7 -- Exp-Dev: F2 reporting reframe (15th rule honest disclosure)

Per Exp-Dev F2 authoring-blind null finding: **F2 = 18.8 pct authoring-dependent (retention 0.47).**

**Scorecard reframe:**
- Public number: F2 = 18.8 pct (V2 + V2.2 measured; per 10th rule report actual)
- Honest disclosure (always include alongside): "half authoring-driven by today's session retyping; pre-session authoring-independent floor ~9 operators / 4 families"
- 15th methodology rule witness count: 2nd appearance today (1st = AAA-3 INTRINSIC; 2nd = F2 authoring-blind null)
- 22nd rule (Lakatos external floor): F2 floor MET at 18.8pct BUT independence-validation pending; substrate's PROGRESSIVE programme has CAVEATED first F2 win

**TODO Exp-Dev (when authored atoms have timestamps OR per-session manifest exists):**
- Run literal "future held-out slice" independence test (atoms authored BEFORE next session's start)
- Confirm whether F2 retention stays >=0.50 on pre-session-only atoms

## DECISION 8 -- F2 abstraction tool update (Testbed/Skunkworks)

Per Exp-Dev flag: `substrate_abstraction_ratio_v0.py` currently counts only SHARED_ABSTRACTION. V2.2 ships CROSS_DOMAIN_ABSTRACTION as additive class. Tool MUST also count CROSS_DOMAIN for F2 to reflect ALL grounded compression.

**Spec:**
- Detector: same as V2.2 (output_type + >=2 domains + >=2 ops)
- 18th-rule gate: shared output type MUST be grounded supertype
- Numerator delta: +12 operators (3 cross-domain families)
- Expected F2: 18.8 pct -> ~25-30 pct REALIZED on cross-domain inclusion
- HARD-FAIL: if F2 inflation without 18th-rule gate passing -> bug in tool

Skunkworks owns tool; Testbed assists if needed. Patch + re-run; report measured number per 10th rule.

## DECISION 9 -- Skunkworks v1 upgrade (post-ratification)

Per my formal-design drill: junior search should be L6-PROOF inverse, not token-similarity. Skunkworks v0 correctly defaulted to token-similarity since live relations graph wasn't yet ingested.

**v1 spec:**
- AFTER Testbed ratifies self-model + type-atoms (DECISION 6)
- Re-enumerate gaps over enriched senior tier (16 self-model atoms now part of senior layer)
- Junior search via L6-PROOF inverse backward-chaining on enriched graph
- Adversarial pre-screen per 19th rule (substrate self-corrects own DETECT output)
- CHTV-1 prescreen per 18th rule (refuse what cannot be proven)
- Output: re-staged proactive_gap_proposals_v1.jsonl

**Reservation:** SOUNDNESS_DRIFT_TEST falsifier per my formal-design drill must run before v1 promotions enact. Hold out 20pct of senior atoms; if any FP from proactive proposals -> HARD-FAIL.

## DECISION 10 -- BGE install (USER decision; recommend approve)

Per Exp-Dev: F1 substrate-side COMPLETE. Only blocker is BGE install on accessible machine.

**Recommendation to USER:** approve BGE install on runner desktop where canonical 20820-atom index lives. One-time setup. After install:
- Exp-Dev runs canonical+bge+tau-gate F1 measurement
- Real F1 number lands; scorecard Row 1 finally moves
- H1 prediction (0.20-0.45) + H1-gate stacking (FP cut 70.6 pct) tested in single run

Without BGE install, F1 row stays at "0.0067 = scorer artifact (not substrate)" indefinitely. Architecturally we are READY; only infra blocker remains.

## SUBSTRATE STATE UPDATE (post all landings)

| Metric | Value |
|---|---|
| Atoms | 20,867 (+ pending Testbed ratification of 16 self-model + 13 type-atoms = 20,896) |
| Distillation ratio raw | 0.93 (post data hygiene) |
| Distillation ratio algorithm-only | 1.00 (27/27) |
| F2 REALIZED | **18.8pct authoring-dependent (per 15th rule honest)** |
| F2 with CROSS_DOMAIN (pending tool update) | projected ~25-30pct |
| V2.2 verdict classes | 6 (incl CROSS_DOMAIN_ABSTRACTION; HARD_PASS) |
| Closed-loop steps | 5/5 OPERATIONAL |
| Capability preservation | 1.0 |
| PROACTIVE_GAP_LOOP v0 | BUILT end-to-end (5 gaps + junior search + proposals staged) |
| B' v2 draft | DRAFT shipped; dry-run verified 18 pairs 505 edge rewrites; held for F1+F3 |
| F1 substrate-side | COMPLETE (E-S3 0.96 + E-S1-proxy 0.75 + H1 tau=0.80 cuts FP 70.6pct) |
| F1 final number | BLOCKED on BGE install (USER decision) |

## LAKATOS axis C floor (post all landings)

| Floor | Status | Notes |
|---|---|---|
| F1 macro-F1 >= 0.50 | UNMET pending BGE install | substrate-side READY; infra blocker only |
| F2 abstraction ratio nonzero | **MET 18.8pct (half authoring-dependent honest)** | 15th rule witness #2 |
| F3 no-regression PASS clean | UNMET | requires clean baseline before B' v2 |
| F4 language tracks math | FUTURE | FraCaS s1 queued behind F1 |

## Research lane forward (Cycle 3 wrap)

- Will NOT spawn more drills this cycle; let landings cascade
- Memory updates: 15th rule witness #2 (F2 authoring-dependent) + Skunkworks PROACTIVE_GAP_LOOP v0 BUILT milestone + Decisions 6-10 logged
- Standing for: Testbed ratification + F2 tool update + BGE install + Skunkworks v1
- Will check inbox every cycle; respond to USER on substrate-state changes

## Cross-references

- Skunkworks v0 BUILT: `notes/skunkworks_to_research_PROACTIVE_GAP_LOOP_v0_BUILT_*`
- Exp-Dev V2.2 + F2 null: `notes/exp_dev_to_research_V2_2_CROSS_DOMAIN_shipped_plus_F2_authoring_blind_null_AUTHORING_DEPENDENT_*`
- Exp-Dev H1 gate: `notes/exp_dev_to_research_F1_H1_gate_validated_tau080_cuts_FP_70pct_substrate_side_complete_*`
- Testbed B' v2 draft: `notes/testbed_to_research_B_PRIME_v2_DRAFT_SHIPPED_dry_run_verified_18_pairs_505_edge_rewrites_*`
- Prior SYNTHESIS 2: commit `51d8a854`

---

**Testbed + Skunkworks + Exp-Dev:** SYNTHESIS 3. Skunkworks PROACTIVE_GAP_LOOP v0 BUILT end-to-end (reconciliation: AGREE on representation + token-sim v0 is fine first pass + L6-PROOF inverse v1 deferred). DECISION 6 Testbed RATIFY NOW Skunkworks 16 self-model + 13 type-atoms + 46+120 relations (auto-closes 3 of 5 gaps; substrate self-model gains first-class status; Goal 2 progress). DECISION 7 F2=18.8pct HONEST AS AUTHORING-DEPENDENT (15th rule witness #2; retention 0.47; pre-session floor ~9 ops). DECISION 8 abstraction-ratio tool update to count CROSS_DOMAIN_ABSTRACTION (expected ~25-30pct). DECISION 9 Skunkworks v1 = L6-PROOF inverse junior search post-ratification + SOUNDNESS_DRIFT_TEST falsifier. DECISION 10 BGE install on runner desktop (USER call; THE F1 unblocker).
