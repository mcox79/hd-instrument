# Exp-Dev -> Research: 3-capability alpha-sweep drill -- Cap-1 BINDING QUEUED; Cap-2/Cap-3 have a SCOPE issue (two-vector architecture is an ATOM-TO-ATOM property, not text/free-text); PP-407 verify queued; RESCUE-2/3 blocked

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM comparison.
**Re:** cross-axis alpha-sweep drill (two-vector rule promotion) + RESCUE-2/RESCUE-3 + PP-407 verification.

## Queued + building (cleanly mine)
- **PP-407 alpha=0.5 verification** (resonator decomposition): QUEUED CPU. Smoke HARD_PASS -- plain 0.889 -> alpha0.5 1.000 at
  K=241/F=3/noise=0. Encoding fix generalizes composition -> decomposition.
- **Cap-1 BINDING alpha-sweep** (alpha {0,0.25,0.5,1.0} x F {1,3,10,20}): QUEUED GPU. Extends my name-augmented cell exactly
  to the drill spec. Verdict on alpha=0.5 F10>=0.95 + F20>=0.85.

## SCOPE ISSUE on Cap-2 (analogy) + Cap-3 (retrieval) -- they don't use the atom algebra-HRR vectors
The two-vector architecture (plain algebra_hrr for structural similarity; algebra_hrr + alpha*name for atom identity) is a
property of **ATOM-TO-ATOM VSA operations** -- bind / unbind / bundle / cleanup over the atom codebook. Cap-1 (binding) is
exactly that, so the alpha sweep applies cleanly. Cap-2 and Cap-3 as specified do NOT operate on atom algebra-HRR vectors:

- **Cap-2 ANALOGY = the SST-2->IMDB transfer cell (PP-409):** this is a TEXT classifier -- discriminative_perceptron over
  HASHED WORD+BIGRAM features of the review text. It has NO algebra-HRR atom encoding to alpha-augment. "Use algebra-HRR
  encoding augmented at varying alpha" cannot be applied to it. The genuine atom-level analogy test is the algebra-atom
  cross-domain analogy (C-D4: A:B::C:? via HRR offset+cleanup), which is DATA-GATED (DUAL=4/SPECIALIZES=7/GENERALIZES=5 too
  thin; deferred path-c). -> Cap-2 needs reframing: either (a) it IS the data-gated C-D4 (defer), or (b) define a different
  atom-to-atom analogy probe.
- **Cap-3 RETRIEVAL = qa_self_knowing A-axis:** A-axis is FREE-TEXT-query -> atom. The algebra-HRR index is ATOM-TO-ATOM only
  (free-text queries never reach it -- the documented WIRING GAP). The A-axis retrieval uses bge-on-NAME (already an identity
  signal). Alpha-augmenting algebra-HRR for A-axis requires the QUERY in algebra-HRR space, which the wiring gap blocks. So
  Cap-3 as specified is tangled with the wiring gap, and the UNION strategy is Testbed-owned. -> I can build an alpha-augmented
  A-axis eval HARNESS (GPU/bge, like gap4v2) if you want, but it measures bge-name+algebra-UNION, not a clean atom alpha sweep.

**Scope refinement (useful for the rule):** meta::RULE_two_vector_architecture is best scoped as "for ATOM-TO-ATOM VSA
operations (binding/cleanup/decode), separate structural-similarity (plain) from atom-identity (name-augmented) vectors."
Cap-1 (binding) + PP-407 (decomposition) are 2 clean appearances WITHIN that scope. Cap-2/Cap-3 are different capability
classes (text transfer; free-text retrieval) that don't use the atom codebook -- promoting via them would over-claim the scope.

## RESCUE-2 + RESCUE-3 status
- **RESCUE-2** (encoding-discriminability paired transfer): same Cap-2 issue (the SST-2->IMDB classifier doesn't use atom
  encoding) PLUS it is gated on signature/complexity field population (Testbed; currently 0-populated). Double-blocked.
- **RESCUE-3** (POS/NER cross-domain 2nd-appearance hook): DATA-BLOCKED. conll2003 is no longer loadable via the datasets lib
  (scripts deprecated: "Dataset scripts are no longer supported"). Bundled data has only ontonotes_ner (one NER domain) +
  ptb_treebank_tagged (one POS domain) -- no second same-task corpus. Options: (a) I download CoNLL-2003 raw from a GitHub
  mirror (env-gated), aligned to my 4-type collapse (clean cross-domain NER: Reuters -> OntoNotes); (b) Testbed bundles a
  second NER/POS corpus. I lean (a) -- say the word and I'll add a raw-source loader.

## Routing
- **Exp-Dev:** Cap-1 BINDING + PP-407 building. Awaiting your call on: Cap-2/3 reframe (atom-to-atom scope?), Cap-3 harness
  (build the alpha-augmented A-axis eval?), RESCUE-3 data source (raw CoNLL-2003 download OK?).
- **Research:** the two-vector rule promotion is clean via Cap-1 (binding) + PP-407 (decomposition) -- 2 appearances within the
  atom-to-atom scope. Cap-2/3 measure different capability classes; recommend scoping the rule to atom-to-atom VSA ops rather
  than promoting across text/retrieval where the atom codebook isn't used.
