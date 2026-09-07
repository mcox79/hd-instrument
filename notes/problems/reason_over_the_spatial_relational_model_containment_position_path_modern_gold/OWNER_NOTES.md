---
owner_verdict: DONE
---

SOLVED (pending your verdict) -- reason_over_the_spatial_relational_model_containment_position_path_modern_gold (opus 4.8 solver)

Write-up: notes/problems/reason_over_the_spatial_relational_model_containment_position_path_modern_gold/SOLVED.md
Reverify (scaffold-free witness; recomputes every headline from source; writes nothing; deterministic across processes):
  .venv/Scripts/python.exe verification/test_spatial_relational_reasoning.py     # 11/11

STATUS: SOLVED. Built the glass-box RELATIONAL SPATIAL REASONER the reader lacked (its only relational move was a
two-level INDOORS/OUTDOORS containment) -- transitive containment, spatial-framework relative position (converse +
nested-frame inheritance), and Goal-over-Source path/transfer with the vacate-Source "no longer" inference. Every
primitive maps to a PINNED brain competence (Johnson-Laird/Byrne model-based reasoning; Franklin-Tversky framework;
Dusek-Eichenbaum hippocampal transitive inference; Peer-Epstein nested frames; Lakusta-Landau Goal-over-Source).
NO learned QA model, NO external LLM. NO hdlab/ written (Q111 -- strategy lands the diff in Sec 7).

1. ALL THREE INFERENCE TYPES clear the bar CI-separated over BOTH controls on MODERN non-synthetic gold, reasoning
   ISOLATED from extraction (gold relations supplied):
   - CONTAINMENT (SpaceEval/ISO-Space gold, train n=1304): reasoner 1.000 vs last-mention 0.940, +0.060 CI[0.047,0.073],
     null p95 0.014; multi-fact subset (n=155) 1.000 vs 0.497 (floor AT CHANCE); shuffled-relation twin 0.508;
     two-level is_in_region ablation 0.896 (the existing register cannot do nested containment).
   - RELATIVE POSITION (SpartQA-HUMAN gold SPRL, test n=1300): reasoner 1.000 vs last-mention 0.734, +0.266
     CI[0.242,0.289]; multi-fact (n=828) 1.000 vs 0.582; twin 0.143.
   - PATH/TRANSFER (SpaceEval MOVELINK gold, train n=32): reasoner 1.000 vs last-mention 0.500, +0.500 CI[0.344,0.656];
     vacate-Source works; twin 0.469.
   Single-fact subsets: reasoner == last-mention (positive control -- they agree when one fact suffices).

2. RELATIVE POSITION ALSO clears the bar END-TO-END over the reader's OWN extraction (SpartQA, coverage 0.339):
   reasoner 0.276 vs last-mention 0.213 (+0.063 CI[0.024,0.110]) vs twin 0.095. So the composition win holds through
   the reader's own parse, not just on gold.

3. LOCATED NEGATIVE, named with counts (the bar treats this as a full pass too): SpaceEval containment/path END-TO-END
   is extraction-gated -- the reader's parse recovers 0.22 containment / 0.06 position / 0.02 move edges, multi-hop
   containment CHAIN survival 6/90; and ReSQ (implicit real-world captions) stays coverage 0.036. Reasoning is NOT the
   bottleneck: extraction is. Corroborated by the SpaceEval-2015 literature -- best system F1 ~0.845 from GOLD elements
   vs ~0.573 from raw text, MOVELINK hardest -- the exact reasoning-sound / extraction-weak split.

UPGRADES IMPLEMENTED + MEASURED this session (each kept only if net-positive; walls researched): extraction
constructions (part-whole "of" + locative predication: recall 0.13->0.22, chain 1/90->6/90); a canon_entity block-label
bug fix (a standalone block "A" was article-stripped to an empty node -- fixing it FLIPPED the end-to-end position
margin from un-separated to CI-separated); nested-frame position inheritance (cross-block transitivity); reasoner
completeness (principled abstention indeterminate-vs-unknown, consistency/contradiction detection, quantifier
capability); efficiency (memoized reachability + a set-order determinism fix so the reverify reproduces across
processes); a glass-box commonsense gap-filler (ConceptNet, NO LLM) that lifts ReSQ commonsense 0.019->0.126,
CI-separated over BOTH baseline and a shuffled-KB control. RESEARCHED and REVERTED with reasons: event-participant
grounding (unmeasurable) and quantifier-in-scorer (corrupts the composition margin + weakens the twin).

KEY REALIZATIONS: (a) isolate the reasoner from extraction and the picture inverts -- the reasoner is near-perfect,
extraction recall is the cap; (b) CHAIN SURVIVAL, not edge recall, is the wall metric (13% edge recall -> 1% chain
survival: multi-hop needs every edge); (c) real spatial transitivity is CROSS-FRAME (object-in-block + block-position),
so nested-frame inheritance was the "go deeper" fix; (d) a failing witness is a latent-bug detector -- drilling it
found the block-label bug that was capping the end-to-end; (e) a raw-accuracy upgrade can be a CONTROLS regression;
(f) orientation commonsense is VERIFIED KB-unreachable (ConceptNet has no vertical signal) -- it needs a
perceptual-simulation faculty, not a bigger KB.

AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT.md (SPACE): a NEW reasoning layer over the LOCATION REGISTER is demonstrated
brain-faithful + CI-separated on all three types; the SPACE cap is now doubly located (named-ground BINDING at
extraction + relation EXTRACTION RECALL for multi-fact reasoning), reasoning is not the bottleneck; and two SPACE
phrasings are OVERSTATED -- "metric coords ruled out" should read "categorical by default, metric on demand" (Rinck
Exp 3), and vacate-Source AUTOMATICITY is contested (the salience asymmetry is PINNED, automaticity is not).

ONE LABELLING CALL FOR YOU (QUESTIONS): I set SOLVED -- the reasoner clears the full positive bar on all three types
on modern gold, relative-position ALSO clears it end-to-end, AND a rigorous located negative is delivered for the
rest (the bar treats each as a pass). A stricter reading requiring CI-separation end-to-end for ALL three types
(containment/path are still extraction-gated on terse prose) would make it PARTIAL. Content is identical either way.

10 experiment files + a pinned reproducible gold fetch + an 11/11 scaffold-free witness; owner_verdict: (blank).

>>> PRIORITY NEXT STEPS:
    P1 (integrate now): land SpatialModel default-OFF over sm.locations (Sec 7.1) -- additive, no regression, makes
       the capability live; fold the AUDIT UPDATE at the same time.
    P2 (highest-value follow-on): joint text->spatial-relation EXTRACTION quality (parent SPACE line) -- the sole
       lever for end-to-end on real prose; prototype evidence + target curve ready; target is whole-sub-graph survival.
    P3 (new faculty): a glass-box PERCEPTUAL-SIMULATION / visual-spatial-statistics organ for orientation commonsense
       (KB-unreachable; grounded asset, NO LLM, preserve abstention).
    P4 (optional): land the commonsense gap-filler default-OFF behind the passage reasoner.
    DO NOT re-file: denser dataset, metric coordinates, a third bridging variant, event-grounding, quantifier-in-scorer.
