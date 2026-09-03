# Baseline Board

**The versioned baseline to diff future improvements against.** Each row is one existing, tracked eval; re-run this and compare snapshots to see what a change actually yields. Regenerated on every run (do not hand-edit).

- **generated (UTC):** 2026-09-03T15:29:08Z
- **docs (LitBank arms):** 16  |  **seed:** 20260902  |  **elapsed:** 700s
- **snapshot JSON:** `data/baseline_board/baseline_2026-09-03.json`
- **HOW TO RE-RUN:** `.venv/Scripts/python.exe tools/baseline_board.py --docs 16` (patient: ~10-15 min -- WSD graph build ~1-2 min + the D/E parser & world-state arms ~5 min). model/floor/twin are accuracies in [0,1]; higher model, and model separated above floor & twin, is the win.
- **Phase-2 (D/E) caps:** newarm_nboot=1000, coref_docs=25 (LitBank he/she densify), mcscript_stories=800 (MCScript2 end-to-end). n recorded per row.

| instrument | metric | corpus | domain | model | floor | twin | n | config |
|---|---|---|---|---|---|---|---|---|
| reader_qa | qa_coref | LitBank | 19c | 0.5688 | 0.3968 | 0.0000 | 436 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=mostfreq_ok |
| reader_qa | qa_events | LitBank | 19c | 0.2519 | 0.0361 | 0.0000 | 1830 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=overlap_ok |
| reader_qa | qa_temporal | LitBank | 19c | 0.8358 | 0.2761 | 0.0000 | 268 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=textorder_ok |
| reader_qa | qa_causal | LitBank | 19c | 0.1485 | 0.5248 | 0.0000 | 101 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=adjacency_ok |
| reader_qa | qa_location | LitBank | 19c | 1.0000 | 0.0000 | 0.0000 | 16 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=overlap_ok |
| reader_qa | qa_belief | LitBank | 19c | 1.0000 | 0.0000 | 0.0000 | 16 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=overlap_ok |
| reader_qa | qa_aggregate | LitBank | 19c | 0.3598 | 0.1624 | 0.0000 | 2635 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; temporal_readout=sm.timeline_order (whole-passage register) |
| who_did_what | who_did_what | LitBank | 19c | 0.2257 | — | — | 1830 | positional |
| who_did_what | who_did_what | LitBank | 19c | 0.2519 | — | — | 1830 | wired |
| who_did_what | who_did_what | LitBank | 19c | 0.2508 | — | — | 1830 | wired_arceager |
| wsd | wsd | WiC-dev | modern | 0.6661 | 0.5000 | 0.5815 | 638 | grounded_semantic_graph(relations_glosses+conceptnet+syntagnet) |
| who_did_what | who_did_what | QA-SRL | modern | 0.3743 | — | — | 2423 | positional |
| who_did_what | who_did_what | QA-SRL | modern | 0.5147 | 0.3743 | — | 2423 | richfeat (arc-factored, LIVE parser) |
| who_did_what | who_did_what | QA-SRL | modern | 0.5477 | 0.3743 | — | 2423 | arc_eager (promoted parser) |
| who_did_what | who_did_what | QA-SRL | modern | 0.5411 | 0.3743 | — | 2423 | organ_hybrid_role (LIVE wired organ) |
| who_has_what | who_has_what | LitBank | 19c | 0.5704 | — | — | 135 | blind (raw-string keys) |
| who_has_what | who_has_what | LitBank | 19c | 0.7185 | 0.5704 | 0.6519 | 135 | reader (coref-densified) = HONEST HEADLINE |
| who_has_what | who_has_what | LitBank | 19c | 0.5000 | 0.0000 | 0.1538 | 26 | reader he/she-holder SUBSET (where blindness bites) |
| who_has_what | who_has_what | MCScript2 | modern | 0.2849 | — | — | 667 | blind (raw-string keys) |
| who_has_what | who_has_what | MCScript2 | modern | 1.0000 | 0.2849 | 1.0000 | 667 | full_binder (EntityBinder) -- CIRCULAR/degenerate twin |

### Row notes
- **reader_qa / qa_coref (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** which-entity from accumulated coref_resolutions (LitBank coref gold).
- **reader_qa / qa_events (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** who-did-what agent off the event index (LitBank WDW gold); CAPABLE reader (tense-agnostic detector on).
- **reader_qa / qa_temporal (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** before/after off sm.timeline_order; HONEST CAVEAT: gold shares the tense signal (tests the QA claim, not independent temporal reasoning).
- **reader_qa / qa_causal (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** cause off causal_links vs grammar-direction gold; the reader's causal organ is connective-reducible (a connective detector, not force-dynamics).
- **reader_qa / qa_location (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** ISLAND dim -- organ not wired into the live reader; score = correct-ABSTAIN rate (faithful behavior is to abstain).
- **reader_qa / qa_belief (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** ISLAND dim -- ToM organ not wired into the live reader; score = correct-ABSTAIN rate.
- **reader_qa / qa_aggregate (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** Aggregate model accuracy over the 4 scored dimensions vs strongest per-dim floors + info-free (deranged-router) twin.
- **who_did_what / who_did_what (positional):** roles assigned POSITIONALLY (default reader; no parse). Scores the AGENT slot (subject head) via build_events_questions. [GOLD ~76% oblique-contaminated -- known-noisy; honest cleaned direct-object ~0.92; do not quote as clean.]
- **who_did_what / who_did_what (wired):** roles routed through a real parse -> route_predicate_arguments (+ quotative), positional fallback. Scores the AGENT slot (subject head) via build_events_questions. [GOLD ~76% oblique-contaminated -- known-noisy; honest cleaned direct-object ~0.92; do not quote as clean.]
- **who_did_what / who_did_what (wired_arceager):** wired parse routed through the promoted arc-eager parser. EXPECTED ~flat here: arceager is modern-trained; LitBank is 19c/OOD. The modern lift (+0.033) shows in Phase-2 QA-SRL (pending). Scores the AGENT slot (subject head) via build_events_questions. [GOLD ~76% oblique-contaminated -- known-noisy; honest cleaned direct-object ~0.92; do not quote as clean.]
- **wsd / wsd (grounded_semantic_graph(relations_glosses+conceptnet+syntagnet)):** select_sense (ppr_w2w spreading activation); graph=1025488 edges built in 20s. Predict SAME-sense iff the two independently-disambiguated synsets match. Floor=MFS (predict same always). Twin=context-shuffle (side-2 from a random sentence); model>twin = the context is used.
- **who_did_what / who_did_what (positional):** linear-position floor on the modern QA-SRL FULL population (non-reversible items).
- **who_did_what / who_did_what (richfeat (arc-factored, LIVE parser)):** the current LIVE frontend parser (arc_parser_richfeat) + labeler object-extraction -- the baseline arc-eager improves on. Floor = positional.
- **who_did_what / who_did_what (arc_eager (promoted parser)):** promoted arc-eager parser (heads + label-free patient rule). arc_eager vs richfeat delta=+0.0330 CI[+0.0198,+0.0462] frac<=0=0.000 -- THE modern lift the 19c board (Instrument B) cannot see. CAVEAT (strategy to confirm): this pair mixes TWO changes (parser richfeat->arc-eager AND extraction labeled->label-free); the pure one-variable head-swap through predicate_argument_frontend is +0.0152 matrix-verb / +0.0265 pp-arg F1 (exp_predarg_frontend_organ_v1).
- **who_did_what / who_did_what (organ_hybrid_role (LIVE wired organ)):** the actual wired who-did-what IDENTITY organ (graded_role_assigner: position+voice, head-INDEPENDENT -> a better parser does not move it directly; resolve_patient organ ties arc_eager at 0.5477). Position floor = the positional row.
- **who_has_what / who_has_what (blind (raw-string keys)):** the coref-BLIND world-state register wired today (holder key = raw surface head).
- **who_has_what / who_has_what (reader (coref-densified) = HONEST HEADLINE):** holder keyed through the reader's OWN he/she coref. reader vs blind delta=+0.1481 CI[+0.0963,+0.2148] (twin[shuffled-coref]=0.6519 loses: reader-twin +0.0667 CI[+0.0220,+0.1185]); gold-cluster oracle ceiling=1.0000. NON-CIRCULAR: object key held constant, scored in gold-cluster space, so the ONLY varying thing is he/she holder resolution.
- **who_has_what / who_has_what (reader he/she-holder SUBSET (where blindness bites)):** decisive subset: holder is a he/she pronoun -> blind=0.0000 by construction (a pronoun string maps to no entity); reader=coref recall, gold=1.0000; shuffled-coref null p95=0.1538 (reader beats p95=True).
- **who_has_what / who_has_what (blind (raw-string keys)):** coref-blind register on MCScript2 first-person narrative (deterministic gold).
- **who_has_what / who_has_what (full_binder (EntityBinder) -- CIRCULAR/degenerate twin):** END-TO-END through the full EntityBinder. full=gold=twin=1.0000 -> the object-anaphora twin does NOT lose (full_beats_twin_CIsep=False); the +0.7151 lift over blind is mostly the cheap indexical normalization (blind+idx=0.9820; object-anaphora-only full-blindidx=+0.0180 CI[+0.0090,+0.0285]). DEGENERATE-TWIN CAVEAT -> the LitBank row is the honest headline.

## PHASE 2 (LANDED 2026-09-02)

Both Phase-2 levers are now ON the board (their solver cells became tracked). Nothing else is pending. Each carries its own honesty caveat in the row notes above:
- **D. modern who-did-what (QA-SRL)** — LANDED 2026-09-02. On the board as instrument `who_did_what` / corpus QA-SRL: arc/richfeat (LIVE) vs arc-eager (PROMOTED) parser -- the +0.033 modern lift the 19c board (B) cannot see. Assembled from the now-tracked exp_parser_through_real_organs_v1.run_pop (+ exp_arceager_parser_operator_v1).
- **E. who-has-what (LitBank + MCScript2)** — LANDED 2026-09-02. On the board as instrument `who_has_what`: LitBank he/she coref-densify is the honest non-circular headline (blind->reader +0.148, twin loses); MCScript2 end-to-end is included but FLAGGED (full==gold==twin==1.0 -> degenerate twin). Assembled from the now-tracked exp_world_state_coref_densify_v1 + exp_world_state_endtoend_whohaswhat_v1.
