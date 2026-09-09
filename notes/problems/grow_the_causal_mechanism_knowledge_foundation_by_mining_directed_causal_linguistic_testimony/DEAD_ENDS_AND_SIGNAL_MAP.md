# DEAD-END LEDGER + SIGNAL MAP — causal-testimony foundation

Consolidated from FULL reads of the three parent SOLVED.md's (2026-09-09, solver_opus48_causaltestimony).
Purpose: (1) never re-run a closed route; (2) state exactly how THIS lever differs from the graveyard;
(3) map the signal the final component needs and where it is lost. **THE DISK OUTRANKS THE BRIEF.**

## 0. THE ONE PLOT: what the final component needs, and where the signal dies
- **FINAL COMPONENT** = `hdlab.predictive_world_model.causal_antecedent` (owner-DONE, PARTIAL/north-star).
  Criterion (100% BF in FORM — Gerstenberg CSM / Trabasso): `cause(B) = argmax_A [surprisal(B|ctx) - surprisal(B|ctx\{A})]`.
  It needs, per candidate A and effect B, a **directed cause→effect production strength** P(B | A caused).
- **ITS INPUT** = the forward model `W`: `P(next event-concept | recent event-concepts)`, learned by delta-rule
  on **raw textual ADJACENCY** of verb-concepts on simplewiki (`fit_online` over `content_events`).
- **WHERE THE SIGNAL DIES**: `W` carries ASSOCIATION (topical/script co-occurrence), not causation. On the disk,
  on TellMeWhy-GOAL **answerable** items (`exp_genworldmodel_residual_decomposition_v1`): the gold cause has
  **mean lexical overlap 0.073** with the effect and **53.8% (SOLVED) / 59.0% (residual) share ZERO lexical
  content** with it (mean distance 2.5 sentences). So for a majority of items there is **no lexical/associative
  bridge at all** — an adjacency-learned `W` has ~0 transition weight cause→effect and picks a topical distractor.
  (BRIEF CORRECTION: the brief's "54% lexical / 73% forward-pred / 34% zero-overlap" is a garbled restatement of
  the on-disk zero-overlap 53.8%/59.0%; the "73%" is not located on disk — I will reproduce forward-pred
  orthogonality first-hand rather than requote it.)

## 1. THE GRAVEYARD — routes CLOSED (do NOT re-run)
### Knowledge SOURCE swaps — ALL tied the info-free twin / no integrator lift
- co-occurrence PPMI-SVD; WordNet-gloss conceptual; GEK-entropy; script-ORDER (454k pairs); VerbNet-telic;
  6M-edge CSKG (152k goal/intent) — six channels, all tie (generate_dont_retrieve finding 3).
- naive ATOMIC ingest / applied weighted-discriminative ATOMIC — floods, no lift, weight-shuffle twin matches
  (`exp_genworldmodel_atomic_commonsense_v1`, `_applied_commonsense_v1`).
- **directed causal-KB rollout** (`exp_genworldmodel_directed_kb_rollout_v1`): **0.283 vs random-directed twin 0.304,
  NOT CI-sep** — a generic directed verb-pair KB ties a random-directed twin. ⚠️ CLOSEST ANALOG — see §2.
- **forward-transition operator** (`exp_genworldmodel_forward_transition_v1`): role-binding STRUCTURE is load-bearing
  (+0.126 vs bind-shuffle), but the **ATOMIC transition KNOWLEDGE ties its atom-shuffle twin (0.341 vs 0.349)**.
- online-learned MINERVA-2/ECHO forward model (`_online_forward_model_v1`): FWD +0.000, **more data (12k→40k) did NOT help**.
- Story-Cloze native forward task (`_cloze_forward_v1`): **at chance 0.517**, ties shuffle-transition twin; diagnosis =
  ungrounded substrate ("milk ⊥ store").
- meaning-grounded bridge (curated 200-d meaning_foundation): ties KNOWLEDGE-SHUFFLE twin (+0.011); encodes
  associative similarity, not the directed causal relation.
- grounding-as-similarity (12-d generative sim; perceptual fillers): no integrator lift; too coarse / no effect.
- SR-TD trained forward form: FALSIFIED (margin +0.0025 vs 0.05 required).

### Selection / binding / structure — closed
- coref binding (recency / ACT-R / optimized): FLAT on real coref though ORACLE excels — mechanism-task mismatch
  (why-Q is single-antecedent cause-ID; TMW object-anaphora rare).
- STRIPS `WorldState.do()` necessity: machinery WORKS + BF but predicate coverage on narrative causal types = **0/256**
  (starved, not broken); psychological ~52% vs physical ~9-12% — world_state is too physical an ontology.
- ECHO coherence-decision / generative candidate-candidate edges / entropy-gated integrator: not load-bearing on real prose.
- force dynamics as a live extractor: WITHIN-CLAUSE only; the cross-sentence cause→q LINK is not a clause → edge
  structurally absent (`exp_lever_signal_loss_diagnostic_v1`).

### Eval — closed / banned
- TellMeWhy / GLUCOSE / MAVEN as load-bearing gold = POSITION-ARTIFACT TRAPS: position floors (TMW nearest-non-adjacent
  0.679/0.713; GLUCOSE earliest 0.668-0.694) BEAT every mechanism. **Grade on the INTRINSIC surprisal/necessity frame.**
- 19c corpora BANNED. External LLM at inference = THE invariant, banned. spaCy/GLUCOSE/MAVEN not BF.

## 2. HOW THIS LEVER DIFFERS FROM THE GRAVEYARD (the "go deeper, don't stop" case)
The convergent negative is strong: decontextualized knowledge, in ANY form tested, ties. Two dead-ends are the
closest analogs and I must beat their design, not repeat it:
- **#directed-KB-rollout** tied a random-directed twin, but it was (a) a generic verb-pair KB, (b) used as a ROLLOUT
  SCORER, (c) measured on the BANNED position-trap crowd gold. 
- **#forward-transition ATOMIC** tied atom-shuffle, but used ATOMIC (generic social commonsense schema), not mined
  mechanism-level testimony, and structure — not knowledge — was the carrier.
THE DIFFERENCE I BET ON, made falsifiable:
1. **Change the necessity reader's OWN forward model `W`** (adjacency → directed causal testimony), do NOT bolt on a
   side-channel scorer. This attacks the association-orthogonality at its ROOT.
2. **Evaluate on the INTRINSIC necessity frame** (trap-proof), not the banned crowd golds.
3. **Testimony gives directed edges for the ZERO-OVERLAP pairs** that adjacency AND generic ATOMIC both miss
   (e.g. "the plant survived BECAUSE she watered it" testifies water→survive though they never co-occur adjacently).
4. **MECHANISM granularity from expository prose** (textbooks: "friction produces heat", "heat causes expansion")
   — a granularity generic social-commonsense KBs lack.

## 3. THE DECISIVE FIRST DIAGNOSTIC (ask "could it succeed?" BEFORE "why did it fail")
Before wiring anything: mine testimony → directed cause→effect store, then on the answerable items measure
**COVERAGE + DISCRIMINATION**: does mined testimony contain the gold cause→effect link, and does it weight
gold-cause→effect ABOVE distractor→effect? 
- If YES → wire into `W`, evaluate intrinsic, twin (shuffled causal edges) LOSING, show EXCEED.
- If NO → located negative WITH THE NUMBER: "only X% of gold causal links appear in any mined testimony; the
  narrative causal links are story-idiosyncratic, not corpus-general testimony" — quantifies the granularity ceiling.
Either outcome is a full pass per the bar.

## 4. REUSE (do not rebuild)
`hdlab.predictive_world_model` (the reader + W + intrinsic eval); `situation_reader._read_predictive_causal` →
`sm.causal_antecedent`/`sm.predictive_necessity` (default-on `track_predictive_causal`, witness
`test_predictive_causal_wire.py` 7/7); `hdlab.pos_tagger` (glass-box tagger); WordNet morphy; the intrinsic-necessity
eval cells (`exp_causal_antecedent_intrinsic_v1`, `_intrinsic_reader_v1`); `_sdrt_coherence.plausibility_components`;
the TMW loader for the answerable-item population; `hdlab.force_dynamics_lexicon` (CAUSE/ENABLE/PREVENT typing).
Corpus: simplewiki + the textbook corpora (dense causal testimony) + clean gutenberg — all offline/admissible.
