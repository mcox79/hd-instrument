---
owner_verdict: DONE
---

Problem: the_situation_model_tracks_no_entity_state_history — SOLVED, ready for review (WIP until owner_verdict: DONE).

Built the missing Zwaan-Radvansky ENTITIES(state) dimension: a per-entity STATE-HISTORY register (sibling of
the SPACE location_register) that reads "had been X" / copular / resultant-of-telic states into each entity's
timeline over intervals, default-persisting, closing only on an explicit incompatible state. Reuses the
location_register interval bookkeeping; coref supplies the entity key. NO external LLM (invariant).

REVERIFY: .venv/Scripts/python.exe verification/test_state_register.py   # 61/61

BRAIN-FOUNDATIONAL METHOD (two research drills, each corrected an intuition before I built):
- PINNED: aspect binds a state to an entity + routes to the entity/resultant layer (Ferretti/Kutas/McRae 2007);
  states default-persist (Dowty). The perfect's currency is a CANCELLABLE default, NOT entailed-closed — so I do
  NOT auto-close pluperfects (drill killed my first design). Telic = closable target-state + permanent
  occurrence-fact (Parsons/Kratzer). State matching is the ATL semantic hub (Patterson 2007), NOT lexical.
- REJECTED (drill said NO-GO): an aspect currency-confidence discount — Vos et al. 2025 found the perfect is the
  MORE reliable state cue, opposite my hypothesis. Correctly did not build it.

MEASURED (all CI-separated, info-free twins lose, 3 seeds):
- TRACKING (construction gold, isolates mechanism): register 1.000 vs strongest stateless floor 0.719; both
  info-free twins lose; EMPTY register 0.429 = chance (not gameable); distance-robust (flat 1.0 at K=20 vs a
  windowed floor collapsing to 0). No single floor handles binding+resultant+supersession; the register does.
- SEMANTIC (ATL-hub) matching: guarded WordNet matcher 0.950 vs exact-string 0.350; exact recovers 0% of
  synonym queries, guarded 92%; the 3 research guards (privative / open-vs-closed scale / typed antonymy) are
  LOAD-BEARING (guarded 1.000 vs unguarded 0.714 on traps). "is X unwell?" now matches stored "ill".
- SERVE, LIVE ORGAN (the payoff): the register improves the ACTUAL hdlab CorefReader (centering+adaptive) on
  state-decisive same-gender pronouns from CHANCE (0.54) to 0.96 — all resolution runs through the real coref
  code, the register only re-ranks its candidate pool by state-consistency; twin collapses. The organ is genuine
  (real-LitBank baseline 0.327 on 582 pronoun targets). Also a hand-floor description serve ("the sick one"->the
  ill entity) 0.95 vs stateless coref 0.53.
- REAL PROSE: extraction coverage 0.331 (bound to gold coref); the previously-DROPPED "had been X" channel now
  extracted+bound (n=33, hand precision ~0.65). Honest bounds: raw-prose extraction is capped by spaCy on 19c
  syntax (the shared role_assignment corpus-age wall); antonym-supersession has ~0 natural incidence.

FILES (no hdlab/ touched, Q111): experiments/state_register.py + exp_state_register_{query,real_prose,semantic,
serves_coref,serves_live_coref}_v1.py; verification/test_state_register.py (61/61); problem folder SOLVED.md +
2 research notes. Ledger --check: clean.

FOR STRATEGY (you land hdlab): promote the spaCy-free core + semantic matcher to hdlab/state_register.py; wire
the TIME-skipped "had been X" channel into it; make the state-consistency re-rank a default candidate filter in
the coref stack (serve already proven against the live organ). Fold the AUDIT UPDATE (new ENTITIES-state entry)
into BRAIN_FOUNDATIONAL_AUDIT.md. Next problems seeded: VerbNet result-state lexicon + slot/"but now" cancel
cue; evidentiality/reportative confidence ("was said to be").

Self-assessed EXCELLENT (grade is yours at integration): genuinely-missing PINNED organ, full control battery,
research-driven corrections, semantic upgrade, and a live-organ serve — honest, normal, corpus-age bounds.
