---
owner_verdict: DONE
---

SUBMISSION — wire_the_context_gated_sense_read_into_the_live_meaning_path_and_measure   (status: PARTIAL; solver scope, WIP until owner DONE)

RESULT (both bar-options delivered; every claim floored + info-free-twin, all BF, NO external LLM, NO hdlab writes):
• POSITIVE — the wire fires live + reads meaning correctly. Instrumented that sm.select_sense is dormant (sm.senses==[]
  after a real read). The live wire lifts WiC over the SENSE-BLIND reader: 0.749 vs 0.500 majority (+0.2493 CI-sep,
  twin-losing). Validated a 2nd way on newly-acquired human data (SCWS): the graded settled context-modulated vector
  beats the context-free vector +0.0156 CI-sep, shuffled-context twin losing.
• LOCATED NEGATIVE (enumerated on the BOARD'S OWN metrics) — no live downstream consumer profits, understood to ONE
  root principle: sense-disambiguation helps only a DISCRIMINATIVE (graded) consumer, never an OR/LICENSING one.
  - coref type-license: board-native gated−blind +0.0056 (CI incl 0); gated below filter-off; twin above gated.
  - natural-logic is-a: committing a sense HURTS −0.48 where it acts; the SOFT posterior degenerates to the union
    (0.7222=0.7222) → licensing wants breadth, sense-narrowing can only shrink the OR.
  - bridge-writing: safer than sense-blind (precision +0.0257 CI-sep) but the gain is restrictiveness not context
    (twin matches), and writing never beats non-writing → the brain's Nref hold is correct.
  - readout params sweep +0.0000; grain: lexname near-optimal (WordNet is-a misses metonymic polysemy); SCWS local-
    context null; two-system fusion not CI-sep → the read is EXHAUSTED at every available lever; residual = the
    SIGNATURE/ENCODER quality (SCWS ~0.40 vs SOTA ~0.65).
  - graded consumer's own benefit is MAGNITUDE-bounded (+0.0294 where context moves the vector vs +0.0026 where it
    doesn't; ~half of natural pairs: no movement).

BF STATUS (finalized audit in SOLVED.md): wire/readout/signatures = BF_SPIRIT/FOUNDATION and WORK; the discrete
consumers (coref type-license, natural-logic is-a) = BF_SPIRIT but sense-IMMUNE by construction (OR/licensing); the
created SETTLED VECTOR = BF_SPIRIT (Kintsch CI/Rodd/Rabovsky), validated on human data; SCWS gold = FOUNDATION
(reproducible fetch, no LLM). ConceptSpace (live per-token meaning) is the standing sense-blind deviation.

HIGH-PRIORITY NEXT STEPS: (1) build the forward consumer as a DISCRIMINATIVE GRADED reader of the settled vector
(the world-model / mega-cluster) — the only consumer the principle permits to profit; (2) do NOT wire sense into any
OR/licensing consumer; (3) land two drop-ins (board WiC → live wire; add board_scws_graded_dimension); (4) the sole
remaining read ceiling is signature/encoder quality (grounding / contextual encoder / OntoNotes sense-groups) — all
foundation/mega-cluster, correctly behind the graded consumer.

KEY REALIZATION: sense-disambiguation is a small, ambiguity-confined DISCRIMINATIVE signal; it can only pay off in a
consumer that discriminates by the specific sense (graded vector-similarity), never in one that licenses by ANY sense.
This retires the "gate the discrete reasoners with sense" direction and points the whole meaning lever at the graded
world-model — with a validated input currency (the settled vector) and a newly-acquired human instrument (SCWS).

REVERIFY: verification/test_sense_wire_liveness_and_coref_negative.py (core: WiC-lift + enumerated negatives + board-
native coref + sweeps) ; verification/test_graded_consumer_scws.py (graded currency on human data) ;
experiments/exp_sense_override_diagnosis_v1.py + exp_soft_sense_natural_logic_v1.py (the root-cause mechanism).
FILES: experiments/exp_sense_* , exp_context_modulated_* , fetch_scws_v1.py (+ data/corpora/scws/) ; verification/test_* ;
notes/problems/wire_the_context_gated_sense_read_into_the_live_meaning_path_and_measure/SOLVED.md . NO hdlab writes (diffs proposed, Q111).
