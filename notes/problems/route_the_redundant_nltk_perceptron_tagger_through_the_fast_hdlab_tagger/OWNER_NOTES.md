---
owner_verdict: DONE
---

SUBMISSION — problem: route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger
status: SOLVED (WIP until owner_verdict: DONE)

BAR (verbatim): "PASS = the affect/valence path tags via the hdlab fast tagger + the shared cache,
with BYTE-IDENTICAL affect output (feel-category + valence) on a held-out doc set and the NLTK tagger
no longer called, with the measured read-time cut. A located NEGATIVE — the hdlab tagger cannot
reproduce the NLTK tags the affect path relies on (a named tagset/behaviour difference) — is a FULL PASS."

RESULT. The single production NLTK perceptron-tagger call in the affect path
(context_grounded_valence._tokenize_and_tag, reached from situation_reader._assign_affect) is rerouted
through the reader's own hdlab UD tagger + shared _cached_tag. Across 40 held-out LitBank docs / 8947
affect calls: the VALENCED affect output (HARM/HELP — the only signal the situation model consumes) is
BYTE-IDENTICAL (0 flips; the single HARM instance preserved; reader HARM self-test preserved). NLTK
tagger calls/read drop 195 -> 12; affect NLTK time ~0.25–0.28s/read removed. Witness 6/6.

Two independent, byte-identical optimizations to the affect path:
  (1) DROP THE REDUNDANT NLTK TAGGER — one lexical-category system, not two (the hdlab UD tagger is
      more correct: contextual AUX, native PROPN). Tokenizer is inert (3/8947); reconcile unnecessary.
  (2) SKIP THE DISCARDED VALENCE — _assign_affect returns to_ternary(predicted_type) and never reads
      result['valence'], yet score_item runs valence_for_type (2 torch matmuls/event). Skipping it
      removes ~0.12s/read, byte-identical. (add need_valence=False)

NAMED RESIDUAL (located-negative sub-finding, itself a full pass per the bar): the affect FIELD's
None<->NA firing-provenance bit differs on 7.5–9% of events (hdlab vs NLTK are different statistical
taggers). INERT — no production consumer branches on None vs NA (enumerated repo-wide). Strict FIELD
byte-identity is unachievable without keeping NLTK, and shouldn't be pursued.

ADDITIONAL INEFFICIENCIES (owner asked "resolve those fully"):
  I. RESOLVED — arc-labeler naive scoring (the biggest lever, ~10x the affect tagger). _predict_label
     did 36 labels x 25 feats = 900 string-concat dict lookups/arc (~75k/read). Built the byte-identical
     _FastLabelPlan (same template as the landed POS-tagger fast path): 0 mismatches/5975 arcs,
     sm.entity_states byte-identical, 9.81x micro, ~0.87s/read median cut (up to +2.10s). Witness 3/3,
     hdlab diff ready. Wants its OWN filed problem (different organ).
  II. NOT fully resolved — tag_punct (temporal) is a LOCATED NEGATIVE: the timeline subsystem needs Penn
     VBD/VBN (finite-past vs participle), which UD UPOS structurally can't represent, and there is no
     substrate Penn tagger asset. Resolution path (separate problem): build a substrate XPOS tagger from
     the on-disk UD-EWT XPOS column, or route the timeline through the reader's own EventRecord.tense.

FLOOR / CONTROLS: info-free shuffled-tag twin loses (228 vs 85 divergences /784) — output is tag-sensitive,
so the agreement is non-vacuous; tokenizer control (3/8947); valenced-flip counter over all 8947; reader
self-test preserved; nltk.pos_tag/word_tokenize disabled -> readout still completes (NLTK dropped);
arc-labeler info-free shuffled-weights plan diverges.

NO hdlab/ writes (proposed diffs in SOLVED.md; strategy lands per Q111). NO external LLM at inference.
FILES: experiments/exp_affect_{nltk_profile,reroute_byteident,reroute_speedup_v1,reroute_speedup_v2,
optimized_full}_v1.py, experiments/exp_arc_labeler_fastpath_v1.py; verification/
test_affect_reroute_hdlab_tagger.py (6/6), verification/test_arc_labeler_fastpath.py (3/3); SOLVED.md.
REVERIFY: .venv/Scripts/python.exe verification/test_affect_reroute_hdlab_tagger.py
