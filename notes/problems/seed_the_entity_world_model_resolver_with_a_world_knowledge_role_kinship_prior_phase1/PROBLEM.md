---
review: EXCELLENT
review_text: Reverified first-hand test_entitykb_resolver_v2.py 6/6 (hard-link 0.2466->0.4139 +0.167 CI-sep; aggregate common-noun CoNLL +0.0882 CI-sep; named no-regress). LANDED (Q111): hdlab/entity_world_model_resolver.py (imports the exact reverified exp_entitykb_resolver_v2.resolve, byte-faithful; curated KB inline glass-box) + resolve_common_noun swapped into _apply_commonnoun_gate behind entity_kb_resolver (DEFAULT-OFF, measured reason). LIVE PROBE (decisive): the resolver RUNS on the reader's own role_mentions (format-compatible) and merges common-noun entities more (sm.entities 451->369), but coref_acc is IDENTICAL off-vs-on (0.3846) -- the board coref dim scores PRONOUN coref while this improves COMMON-NOUN clustering, so the +0.0882 harness win does NOT reach the board coref dim (payoff is indirect via affect/goal experiencers). Kept default-off with that measured reason -- a board-VISIBILITY located negative on the current instrument (the mechanism is sound; the board cannot see the common-noun win). Do NOT wire the reader AGENT head-match. Follow-on filed: the two-pass Step-3 reader_coref + a common-noun coref board arm. SS2b folded. INTEGRATED 2026-09-05.
---

# PROBLEM: the common-noun coref solution BUILT the brain's actual reference mechanism — QUERY an accumulated ENTITY WORLD-MODEL (a file card per entity: type/social-role/relations/recent-event/presence, restricted to the foregrounded set; Kintsch CI / Zwaan / Sanford-Garrod bonding→resolution / Heim-DRT) — and PROVED it CROSSES: ambiguous-link resolution 0.255 (surface recency) → **0.540** given correct records (union-oracle 0.615, the facts ARE in the narrative). But deployment hits a **BOOTSTRAPPING / IDENTIFIABILITY wall**: self-built records give only +0.006 (you cannot build correct entity records without already resolving reference), and 2-pass consolidation + confidence-gating do NOT cross it. The brain breaks this chicken-and-egg with a **PRIOR WORLD KNOWLEDGE** (it knows a priori who "the master" is, that "her father" is a kinship relation, what social role "the Squire" plays) — the external prior the no-LLM invariant bars, and exactly what SOTA imports from a pretrained LM. Build the admissible glass-box substitute: a STATIC OFFLINE scenario/social-ROLE + KINSHIP knowledge base (a foundation asset — NO LLM, NO training) that SEEDS the entity world-model records, so the already-built resolver realizes its 0.54 ceiling on deployment. Prove the seeded resolver lifts common-noun coref (+ the shared affect experiencer + relational-reference downstreams) CI-separated over the surface-head + the unseeded-resolver floors, info-free (shuffled-KB) twin LOSING — or a located negative naming why the role/kinship prior cannot close the identifiability gap glass-box.

**slug:** `seed_the_entity_world_model_resolver_with_a_world_knowledge_role_kinship_prior_phase1` — **opened:** 2026-09-04 by the strategy session, the explicit Phase-1 follow-on the owner-DONE `form_a_discourse_referent_for_every_entity...` named (the built entity-world-model resolver is blocked ONLY by the identifiability wall, broken by a world-knowledge prior). **status:** OPEN. Ties to the curated knowledge-foundation program (owner-confirmed 2026-09-04). Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM; a STATIC OFFLINE role/kinship KB is an admissible foundation asset (owner 2026-08-16).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a story says "the master" or "her father," a reader knows who that is because they bring outside knowledge — social roles, family relations, common scenarios — to the page. We already built the reader's "notecard per character" machinery, and it works well *when the notecards are right* (more than doubling accuracy on the hard cases). The catch proven last round: you can't fill in correct notecards without already knowing who's who — a chicken-and-egg the brain solves with prior world knowledge. The job: give the reader a small, curated starter kit of social-role + kinship + scenario knowledge (no outside AI — a fixed knowledge base) to seed those notecards, so the resolver we already built can actually reach its proven ceiling on real stories.

## 2. WHY THIS ONE — it is the ONE lever that realizes a built, proven capability, and it is shared
The resolver is BUILT and PROVEN (0.255→0.540 given records); only the identifiability wall blocks it, and only a world-knowledge prior breaks that wall. This is the highest-value remaining coref lever, and it is SHARED: the same role/kinship/relational prior is the located-negative residual under common-noun coref, the affect experiencer binding, and relational-reference WSD ("her father", "the Squire"). One curated prior lifts all three. It is the entity-model half of the owner-confirmed knowledge-foundation program (the lexical-semantic half is `build_and_freeze_the_clean_curated_knowledge_foundation`).

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: reference resolution queries an entity world-model built from TEXT + PRIOR WORLD KNOWLEDGE — social roles/scripts (Schank-Abelson scripts; Sanford-Garrod scenario-mapping), kinship/relational frames, and stereotypic role knowledge, brought to bear at first mention and updated (Kintsch CI integrates text + prior knowledge). OUR-INVENTION-under-test: the exact curated role/kinship/scenario KB + how it seeds the entity records + the seed-then-resolve schedule (avoid re-introducing circularity). Sweep, do not adopt. REUSE (do NOT re-derive): the BUILT entity-world-model resolver (`experiments/exp_commonnoun_entity_world_model_v1.py`), `hdlab/commonnoun_binder.py` (the landed former), `hdlab/graded_coref_pick` (the abstain/confidence gate), `hdlab/event_centrality_coref`; standard curated resources (WordNet role hypernyms, kinship lexicons, VerbNet/FrameNet roles).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — the coref SOLVED):** the entity-world-model resolver crosses 0.255→0.540 given GOLD records (union-oracle 0.615); self-built records +0.006, consolidation +0.0045, confidence-gate +0.0056 — none crosses the identifiability wall; the residual is world-knowledge-bound (66% shifting epithets, over-merge 91% content-identical, WordNet bridging 7.8%).
- **INFERRED (you must measure):** whether a curated static role/kinship/scenario KB seeding the entity records recovers a CI-separated fraction of the 0.006→0.54 gap on DEPLOYMENT (self-built + KB-seeded records), lifting common-noun coref + the affect experiencer + relational reference, shuffled-KB twin LOSING; the residual + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/problems/form_a_discourse_referent.../SOLVED.md` §4c (the built resolver + the identifiability wall) + the coref research memos IN FULL; read `notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md` (the knowledge program); read `experiments/exp_commonnoun_entity_world_model_v1.py`, `hdlab/commonnoun_binder.py`, `hdlab/graded_coref_pick.py`.
- Reproduce first-hand: the 0.255→0.540-given-records cross AND the self-built +0.006 wall (the can-fail baseline the KB seed must beat).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a glass-box static role/kinship/scenario KB (a foundation asset; NO LLM) seeding the entity world-model resolver such that, on DEPLOYMENT (no gold records), common-noun coref rises CI-separated over the surface-head + unseeded-resolver floors, and at least one shared downstream (affect experiencer OR relational reference) rises CI-separated, with a shuffled-KB info-free twin LOSING and no-regress on named coref. Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the role/kinship prior cannot close the identifiability gap glass-box (with the named cause + number, e.g. the prior itself needs per-text instance binding no static KB supplies) — is a FULL PASS (then the entity-model ceiling is invariant-bound, informing the P9-style decision). Strategy lands the Q111 wire.

## ALREADY TRIED / DO NOT REDO
- The surface-cue former + consolidation + confidence-gate are MEASURED-CAPPED (located negatives) — the lever is the WORLD-KNOWLEDGE PRIOR seeding records, not another cue heuristic.
- The entity-world-model resolver is BUILT — REUSE it; this supplies the missing PRIOR, not the resolver.
- Do NOT use an external LLM (the invariant) — a curated static KB only.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `experiments/exp_commonnoun_entity_world_model_v1.py`, `hdlab/commonnoun_binder.py`, `hdlab/graded_coref_pick.py`, the curated role/kinship resources. Ship the KB to `data/frontend_assets/`. Measure on common-noun coref + affect experiencer + relational reference. Strategy lands the Q111 wire. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote the 0.540 given-gold-records number as a deployment result — it is the ceiling; report the KB-SEEDED deployment recovery.
- Do NOT quote a gain without the shuffled-KB twin losing + named-coref no-regress.
- Do NOT use an external LLM (the invariant).
