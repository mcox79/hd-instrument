# Research drill: the brain mechanism of COMPOSING entity binding with the situation-model prediction channel

Solver problem: `wire_entity_tracking_end_to_end_on_running_narrative`. Drill dispatched via the `research`
agent (4 parallel lit-scans). This file persists the findings verbatim (per the "persist a scan's FULL
report" discipline). ASCII only.

## RECONCILED SYNTHESIS (parent)

The seam is real but asymmetric.
- **PINNED**: resolving a pronoun genuinely REACTIVATES the referent's neural representation -- two
  independent, convergent 2023-2024 studies (Dijksterhuis et al. 2024, *Science*, single-unit hippocampal
  recording; Ding, ten Oever & Martin 2023, MEG delta-band population coding). Strongest single result.
- **NOT pinned**: that the reinstated state then CAUSALLY conditions downstream prediction -- no study closes
  that loop. Reasonable inference, not demonstrated fact. => our composition is a COMPUTATIONAL TEST of the
  untested Step 3.
- **Our accumulate-and-decode register is a SHORTCUT, not faithful.** The literature supports a hybrid: keep
  the growing bundle as a GIST layer (fine), but add a separate, PATTERN-SEPARATED store of individual event
  traces per entity, index/pointer-keyed, retrieved by pattern completion -- not by algebraic unbind of one
  merged vector. Diagnostic: a FAN-EFFECT signature (item-selective interference growing with event count)
  that a pure bundle cannot produce but separate competing traces can. MEASURE the degradation-with-N profile
  before building the fix.
- **Most brain-faithful readout**: ANTICIPATORY next-argument prediction (Altmann & Kamide-style, scored
  BEFORE the continuation), not post-hoc "which verb did entity X govern." Implementable now with a
  string-identity floor + shuffled-link info-free twin.
- **PROHIBITION**: don't claim "resolution fully completes, THEN prediction begins" as brain-confirmed --
  Kehler & Rohde (2013), ACT-R additive activation, and McKoon & Ratcliff resonance all argue JOINT scoring of
  salience+content, not strict serial staging. Frame as a computational-level decomposition.
- **PIN**: mis-binding cost should be case-typed by ERP signature -- ambiguity -> graded/competitive
  multi-entity update (Nref); feature-mismatch -> explicit conflict/abstain (P600); poor-fit -> silent
  miss+corruption (N400-faithful, keep as-is).

## SUB-SCAN 1 (hippocampal reactivation) -- verbatim highlights

- Dijksterhuis, D.E. et al. (2024). "Pronouns reactivate conceptual representations in human hippocampal
  neurons." *Science* 385(6716):1478-1484. DOI 10.1126/science.adr2813. 22 epilepsy patients, hippocampal
  depth electrodes, 307 units. Concept cells selective to a named character re-fire when a later pronoun
  refers to that character. In ambiguous same-gender trials, stronger hippocampal activity at a name's first
  mention predicts which referent the patient behaviorally selects (a SELECTION/salience signature too).
- Ding, N., ten Oever, S., & Martin, A.E. (2023). "Pronoun resolution via reinstatement of referent-related
  activity in the delta band." bioRxiv 2023.04.16.537082 -- convergent population/oscillatory evidence for
  reactivation at the pronoun.
- Teyler & Rudy (2007) hippocampal indexing theory (sparse index over neocortical patterns; partial cue ->
  pattern completion) is the scaffold for pronoun-as-partial-cue reinstatement. Baldassano et al. 2017
  (*Neuron*) event-boundary reinstatement generalizes the logic to narrative events.
- VERDICT on the 3-step chain: Step 1 (salience selects) PARTIALLY PINNED; Step 2 (resolve -> reactivate)
  PINNED (best-supported); Step 3 (reinstated state conditions prediction) NOT DIRECTLY TESTED --
  PLAUSIBLE-BUT-UNTESTED.

## SUB-SCAN 3 (ERP cost of misresolved reference) -- verbatim highlights

- Human data do NOT support "silent corruption with no detection." Three failure types:
  - Ambiguity -> Nref (sustained anterior negativity, ~300-400ms onset, 1000-2000ms): the system HOLDS
    MULTIPLE candidates active under working-memory load (Nieuwland/Otten/Van Berkum 2007; Van Berkum et al.
    2003). Closer to a graded/competitive multi-entity update than a hard miss+corruption.
  - Feature-mismatch wrong-antecedent -> P600 (Osterhout & Mobley 1995): DETECTED conflict + reanalysis, not
    silent corruption.
  - No-unique-referent / poor-fit -> N400-family (Van Berkum/Brown/Hagoort 1999): retrieval/integration
    difficulty -- the case closest to a "miss."
- RECOMMENDATION: (i) ambiguous cases -> graded/competitive update across BOTH candidate registers (Nref-like)
  rather than a forced single wrong-commit; (ii) feature-mismatch -> explicit conflict/error signal (P600);
  (iii) reserve silent "miss + corrupt wrong entity" for the poor-fit (N400) case. Our "miss" is well
  supported; "corruption" (confident wrong-commit) is the weakest-supported piece.

## HOW THIS DRILL CHANGED THE BUILD

- Added the ANTICIPATORY next-argument prediction readout (the more-faithful readout) -> found the NULL
  (dissociation): correct linking does not improve prediction.
- MEASURED the fan effect (oracle decode 0.695 -> 0.608 with entity event-count) -> the dense bundle IS the
  shortcut; pattern-separated store is now evidence-backed.
- Implemented the Nref PIN as GRADED activation-weighted binding -> it BEATS hard argmax downstream (+0.027
  CI-sep; uniform-weight control WORSE, so the activation weighting is essential).
- Framed the composition as a computational-level decomposition, not strict serial staging (PROHIBITION).
