---
owner_verdict: DONE
---

Problem: the_reader_cannot_answer_a_question_over_its_situation_model — SOLVED (self-graded STRONG,
excellent-grade rigor/brain-fidelity core), WIP until owner_verdict: DONE.

WHAT IT IS: the reader built a rich SituationModel (entities/coref/events/timeline/causal) but had NO way
to ASK IT A QUESTION. I built a UNIFIED, glass-box QA interface (SituationQA) that ROUTES a structure-
dependent question to the dimension holding the answer and READS THE ANSWER OFF THE ACCUMULATED MODEL (never
by re-reading), measured over a retrieval floor. GLASS-BOX, NO LLM (routing OR gold). No hdlab/ touched (Q111).

REVERIFY: .venv/Scripts/python.exe verification/test_situation_model_qa.py   # 8/8 scaffold-free

MEASURED (100 LitBank docs / 16,587 questions; scorer normalized match; doc-bootstrap 2000x CIs; disk OUTRANKS brief):
- WHICH-ENTITY (coref) 0.556 vs strongest floor 0.424 (most-frequent-entity) = +0.087 [0.053,0.208] CI-sep. WIN.
- WHEN (before/after) 0.926 vs 0.366 (text-order) = +0.55 CI-sep. WIN (honest caveat: model+gold share the tense signal).
- WHO-DID-WHAT 0.145 vs 0.017 (word-overlap) = +0.11 CI-sep. WIN (modest; the assembly's dimension).
- WHY (causal) 0.442 vs 0.652 (adjacency) = -0.31 LOSES = a RIGOROUS NEGATIVE: the live reader's causal dimension
  is a connective PLACEHOLDER; the real force_dynamics_typer (Talmy/Wolff, 0.929) is BUILT/owner-DONE but UNWIRED.
- WHERE / WHO-BELIEVES = correct HARD-ABSTAIN 1.00 / 0.96 (location_register / belief_partition are built-but-
  unwired ISLANDS = never-tracked, not guessing).
- Info-free TWIN = 0.000 on EVERY dimension (deranged router; loses CI-sep everywhere). POSITIVE CONTROL: the
  accumulated model resolves 1059 antecedents the recency re-reading floor MISSES vs 288 the other way (3.7:1).

BRAIN-FOUNDATIONAL (2 literature drills, PINNED):
- The FLOOR is the brain theory: Kintsch textbase-vs-situation-model dissociation -> bridging/causal/spatial/
  temporal/anaphor probes are UNANSWERABLE from surface memory. "Answer from the model, not by re-reading" = PINNED.
- The ROUTER is NOT a keyword switch: dimension->subsystem specialization is real (PPA/space, time-cells/order,
  pSTS/who, mPFC/cause, TPJ/belief) but the subsystems run in parallel and the match wins a graded cue-race
  (Lewis&Vasishth 2005). Built it SOFT + PARALLEL + THRESHOLD-GATED (abstain = FOK gate).
- GENERALIZATION (the key axis): a question means WHAT WOULD COUNT AS AN ANSWER (Roberts QUD; Cysouw wh->ontology
  universal). Upgraded the router to a wh-word ANSWER-TYPE + WordNet head-noun resolver (who->ENTITY, where->SPACE,
  "in what SPOT"->location) -- glass-box, no LLM. It generalizes to NOVEL cue words: routing 1.00 vs cue-table 0.40
  vs keyword 0.00 (all-paraphrase 1.00/0.78/0.39). And it MATTERS FOR ANSWERING end-to-end: under a natural
  paraphrase the cue-table's ANSWER accuracy COLLAPSES (coref 0.556->0.071, events 0.145->0.000) while the wh-
  ontology router PRESERVES it (0.556->0.556, 0.158->0.142). Reference architecture: SEM (Franklin 2020).

HONEST BOUNDS (withdraw-first order): temporal shares its tense signal with its gold (withdraw first). Coref is the
reader's existing coref reframed as QA (real +0.087, but not new capability). Corpus generalization UNTESTED (all
LitBank 19c; no 2nd narrative coref gold on the shelf). The capstone is as much a WIRING-DEBT DIAGNOSTIC as a broad
demonstration -- because most dimension organs are unwired (which it MEASURES). Ran the landed WIRED role path:
events QA only 0.120->0.142 (+0.022), residual is coref-bound (matches the assembly) -> who-did-what is at its
role-lever ceiling.

ADJACENT COMPONENTS (all built + owner-DONE + brain-PINNED, all UNWIRED islands -> the next-problem seeds):
force_dynamics_typer (WHY, 0.929), location_register (WHERE), belief_partition (WHO-BELIEVES), state_register
(WHAT-CONDITION), temporal_order_register (WHEN). The QA router ALREADY routes to all of them; only the readouts
lack the organ.

FILES: experiments/exp_situation_model_qa_v1.py; verification/test_situation_model_qa.py (8/8);
data/exp_situation_model_qa_v1/metrics.json; the problem folder SOLVED.md + 2 research notes
(research_situation_model_qa_{brain_mechanism,qud_paraphrase}_2026-08-30.md).

FOR STRATEGY (you own hdlab, Q111): (1) LAND the query API -- add SituationModel.answer(question) = the wh-ontology
router -> per-dimension readout off the accumulated fields (pure addition, gives the reader an "ask it" method).
(2) WIRE the built-but-idle dimension organs dimension-by-dimension, re-measuring with THIS instrument each time:
force_dynamics_typer->_read_causation (turns the causal NEGATIVE into a candidate win); location_register +
motion-event front-end (where); belief_partition + observation-cue front-end (who-believes); state_register (a 6th
dimension). (3) Swap the router's head-noun resolver from WordNet to the idle distributional_meaning_channel
(retires a standing wiring debt). AUDIT UPDATE + full detail in SOLVED.md.
