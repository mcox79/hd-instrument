# Baseline Board

**The versioned baseline to diff future improvements against.** Each row is one existing, tracked eval; re-run this and compare snapshots to see what a change actually yields. Regenerated on every run (do not hand-edit).

- **generated (UTC):** 2026-09-02T14:57:48Z
- **docs (LitBank arms):** 16  |  **seed:** 20260902  |  **elapsed:** 421s
- **snapshot JSON:** `data/baseline_board/baseline_2026-09-02.json`
- **HOW TO RE-RUN:** `.venv/Scripts/python.exe tools/baseline_board.py --docs 16` (patient: WSD graph build ~1-2 min). model/floor/twin are accuracies in [0,1]; higher model, and model separated above floor & twin, is the win.

| instrument | metric | corpus | domain | model | floor | twin | n | config |
|---|---|---|---|---|---|---|---|---|
| reader_qa | qa_coref | LitBank | 19c | 0.5688 | 0.3968 | 0.0000 | 436 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=mostfreq_ok |
| reader_qa | qa_events | LitBank | 19c | 0.2257 | 0.0361 | 0.0000 | 1830 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=overlap_ok |
| reader_qa | qa_temporal | LitBank | 19c | 0.8358 | 0.2761 | 0.0000 | 268 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=textorder_ok |
| reader_qa | qa_causal | LitBank | 19c | 0.1485 | 0.5446 | 0.0000 | 101 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=adjacency_ok |
| reader_qa | qa_location | LitBank | 19c | 1.0000 | 0.0000 | 0.0000 | 16 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=overlap_ok |
| reader_qa | qa_belief | LitBank | 19c | 1.0000 | 0.0000 | 0.0000 | 16 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; floor=overlap_ok |
| reader_qa | qa_aggregate | LitBank | 19c | 0.3416 | 0.1632 | 0.0000 | 2635 | capable_reader[tense_agnostic_events+preserve_tense+timeline_register]; temporal_readout=sm.timeline_order (whole-passage register) |
| who_did_what | who_did_what | LitBank | 19c | 0.1202 | — | — | 1830 | positional |
| who_did_what | who_did_what | LitBank | 19c | 0.1426 | — | — | 1830 | wired |
| who_did_what | who_did_what | LitBank | 19c | 0.1404 | — | — | 1830 | wired_arceager |
| wsd | wsd | WiC-dev | modern | 0.6661 | 0.5000 | 0.5815 | 638 | grounded_semantic_graph(relations_glosses+conceptnet+syntagnet) |

### Row notes
- **reader_qa / qa_coref (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** which-entity from accumulated coref_resolutions (LitBank coref gold).
- **reader_qa / qa_events (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** who-did-what agent off the event index (LitBank WDW gold); CAPABLE reader (tense-agnostic detector on).
- **reader_qa / qa_temporal (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** before/after off sm.timeline_order; HONEST CAVEAT: gold shares the tense signal (tests the QA claim, not independent temporal reasoning).
- **reader_qa / qa_causal (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** cause off causal_links vs grammar-direction gold; the reader's causal organ is connective-reducible (a connective detector, not force-dynamics).
- **reader_qa / qa_location (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** ISLAND dim -- organ not wired into the live reader; score = correct-ABSTAIN rate (faithful behavior is to abstain).
- **reader_qa / qa_belief (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** ISLAND dim -- ToM organ not wired into the live reader; score = correct-ABSTAIN rate.
- **reader_qa / qa_aggregate (capable_reader[tense_agnostic_events+preserve_tense+timeline_register]):** Aggregate model accuracy over the 4 scored dimensions vs strongest per-dim floors + info-free (deranged-router) twin.
- **who_did_what / who_did_what (positional):** roles assigned POSITIONALLY (default reader; no parse). Scores the AGENT slot (subject head) via build_events_questions.
- **who_did_what / who_did_what (wired):** roles routed through a real parse -> route_predicate_arguments (+ quotative), positional fallback. Scores the AGENT slot (subject head) via build_events_questions.
- **who_did_what / who_did_what (wired_arceager):** wired parse routed through the promoted arc-eager parser. EXPECTED ~flat here: arceager is modern-trained; LitBank is 19c/OOD. The modern lift (+0.033) shows in Phase-2 QA-SRL (pending). Scores the AGENT slot (subject head) via build_events_questions.
- **wsd / wsd (grounded_semantic_graph(relations_glosses+conceptnet+syntagnet)):** select_sense (ppr_w2w spreading activation); graph=1025488 edges built in 22s. Predict SAME-sense iff the two independently-disambiguated synsets match. Floor=MFS (predict same always). Twin=context-shuffle (side-2 from a random sentence); model>twin = the context is used.

## PHASE 2 (pending cell persistence)

These levers are NOT on the board yet -- honest about what it does not cover. Both are blocked on persisting untracked solver cells (they HARD-FAIL the Q115 repro hook), not on the science:
- **modern who-did-what (QA-SRL)** — The arm that shows the parser's measured +0.033 lift. Its gold/scorer live in the parser solver's UNTRACKED cells (exp_arceager_parser_operator_v1 / exp_predarg_frontend_organ_v1 / QA-SRL pop) which HARD-FAIL the Q115 repro hook -> blocked on persisting those cells.
- **who-has-what (MCScript2)** — The coref-densifier's arm. Its gold/scorer live in the untracked exp_world_state_* cells -> blocked on persisting those cells.
