---
owner_verdict: DONE
---

SUBMISSION — build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner  (SOLVER, opus 4.8)

STATUS: PARTIAL — the consolidation gate WORKS + a clear path; the reading-derived sub-question is a located
negative. WIP until owner_verdict: DONE. Witness verification/test_consolidation_gate.py = 14/14 from source.
Ledger malformed/incomplete: 0. NO hdlab writes. Glass-box, NO external LLM, NO training runs.
REVERIFY: .venv/Scripts/python.exe verification/test_consolidation_gate.py

HEADLINE (strict doc-disjoint SemCor subordinate, n=2676; gloss 0.251; curated ceiling 0.302):
- THE GATE PASSES with clean knowledge: admitting a CONSOLIDATED clean foundation (WordNet relations + SyntagNet +
  ConceptNet — admissible offline asset) through the brain-faithful SELECTION reader raises a_s 0.251 -> 0.318,
  +0.067 CI-sep [0.048,0.087], RAW reading twin LOSES (-0.033), no MFS regression. = "the clean foundation," delivered.
- NARROW LOCATED NEGATIVE: the reader can't grow that clean knowledge from its OWN reading glass-box —
  mechanism-complete (top-down 0.251; grounded norms+brain-faithful inheritance 0.251; bottom-up online
  competitive-Hebbian induction 0.183), all online/no-training, none crosses gloss.

>>> THE NEXT FOCUS — THE 100% BRAIN-FOUNDATIONAL PATHWAY (the ceiling-breaker, glass-box, no training) <<<
The ~0.35 ceiling is the FROZEN DISTRIBUTIONAL substrate: senses are SUPERPOSED in w2v (Arora 2018), so no reader
separates a rare sense from its dominant twin (PROVEN: supervised distributional keys cap at 0.35). Two ways
through, only ONE brain-foundational:
  ✗ contextual encoder / TRANSFORMER (~0.53) = ungrounded + BATCH-TRAINED = the invariant boundary. NOT pursued.
  ✓ THE ATL HUB-AND-SPOKE + ONLINE PREDICTIVE READER — word meaning = a transmodal hub bound to GROUNDED SPOKES
    (visual/motor/affective/relational) whose dimensions are ORTHOGONAL to distribution and SEPARATE the superposed
    senses (grounding separated the clear case 0.813 vs -0.096), RE-COMPUTED per context by the online predictive
    reader (one pass, no training — the reading loop). BUILD: (1) grounded sense atoms via hub_spoke_word/
    grounded_similarity/ATL hub bound with distributional; (2) ENRICH THE SPOKES — the 12-dim norms are too coarse
    (tested, ruled out); needs Binder-class ~65-dim + affect + relational, propagated to coverage by SEMANTIC
    INHERITANCE (brain-faithful, NOT a regressor); (3) online predictive reader settles the grounded atoms per
    context. This is the meaning-channel NORTH STAR — the next build this problem earns.

CLEAR PATH (ordered): (1) LAND THE CLEAN FOUNDATION NOW — wire relations+SyntagNet+ConceptNet as sense atoms through
hdlab/diagnostic_context_wsd (=+0.067, default-off/witnessed/Q111). (2) GATE + hdlab/cls_growth = SAFE wrapper for
reading-growth (prevents raw regression; +0.110/6 rounds, drift-free) — learner-on safe by construction. (3) OPEN
THE 100% BRAIN-FOUNDATIONAL PATHWAY (above) as its own problem — the next focus.

WHERE SIGNAL IS LOST (0.318 -> human ~0.65): DOMINANT loss = sense atoms are frozen-w2v CENTROIDS in a
sense-SUPERPOSED space, so rare/dominant atoms overlap and selection can't split them (supervised keys cap 0.35 ->
the SUBSTRATE is the cap, not the knowledge, not the reader; recurrent settling only worsens it, 0.202). Deepest
divergence: our substrate is frozen+distributional (senses merged); the brain's is GROUNDED + CONTEXTUALLY-RECOMPUTED
(senses distinct) — exactly the hub-and-spoke pathway above. 0.35->0.53 = this wall; 0.53->0.65 = world-knowledge
inference.

CORRECTIONS I OWN (owner-caught): overstated grounding as "the wall" (the 12-dim norm FUSION was ruled out — but the
richer GROUNDED HUB-AND-SPOKE is precisely the brain-foundational pathway); drifted to BATCH ML twice (ridge; a
contextual-encoder training run) — both KILLED. The brain does not do long training runs; we do glass-box, period.

FILES: experiments/exp_consolidation_gate_v1, _gate_readbind_v1(+window), _signal_loss_trace_v1,
_discriminative_rescore_v1, _gate_syntactic_v1, _grounded_v1, _grounding_inherit_v1, _online_sense_induction_v1,
_brain_faithful_reader_v1; verification/test_consolidation_gate.py (14/14). AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT.

TLDR (plain): the clean-up gate works and feeding in CLEAN curated knowledge beats the dictionary (+0.067, the
glass-box ceiling). It can't grow that knowledge from reading alone (proven every way). The one wall above is that
our word representations are frozen averages that merge a word's meanings, where the brain keeps them apart with
grounded senses/feelings and recomputes them as it reads. THE NEXT FOCUS is building exactly that — the brain's
hub-and-spoke grounded meaning + an online reader — the only ceiling-breaker that stays glass-box and needs no
training.

QUESTIONS: one — open the 100% brain-foundational pathway (ATL hub-and-spoke grounded atoms + online predictive
reader) as its own problem, the next focus? NEXT STEPS: land the clean foundation + safe learner-on now (Q111); then
that pathway.
