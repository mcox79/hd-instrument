# exp_dev hand-off -- research: negation/factuality gate for the who-is-affected reader

**Filed-by:** research sub-agent, 2026-07-21
**Trigger:** USER-surfaced gap -- the reader assumes every parsed event happened; negation/modality breaks that ("he didn't break it" still marks the vase affected today). Full derivation: `notes/research_negation_factuality_gate_reader_2026-07-21.md`

**Pause state:** Check data/orchestrator_paused.flag before dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off WHAT and WHY.
exp_dev owns all anchor names, sweep grids, threshold formulas, queue routing, and timing.

---

## Anchor candidates (rank-ordered)

### Rank 1: negation-cue-and-scope gate -- highest P_deflated, cheapest test, reuses existing UD parse

**Anchor pointer:** Add a negation/factuality tag to the reader's Step-2 vote: detect the UD cue (`lemma=="not"` + `Feats` contains `Polarity=Neg`, or lexicon fallback never/no/nobody/nothing/neither/nor/without/cannot), resolve scope via the cue's `advmod` head (the governing verb, directly from dependency attachment -- NOT surface word-order distance), and propagate NEGATED status across `conj`-coordinated verbs sharing the same negated head. Output REALIZED (default) or NEGATED per event.

**Substrate-product reading:** Today the reader's crude cue-extractor (`experiments/exp_learned_argstruct_parser_lccp_independent_gold_v1.py` line 136) puts "not" and "never" in its `FUNCWORD` stopword set -- negation is discarded as noise, not merely unweighted. This is a genuinely unbuilt, orthogonal correctness dimension (confirmed by dedup: no prior work touches this; the one adjacent artifact, `exp_dev_handoff_research_negation_detection_2x_2026-06-06.md`, is a different subsystem -- KF-1 fact-verification, not the argument-structure reader, and proposes a non-glass-box DeBERTa cross-encoder that's off-limits under the runtime invariant). The dependency-attachment approach is directly precedented: DEEPEN (Mehrabi et al. 2015) and DepND replaced NegEx's crude token-window with exactly this dependency-tree scope logic and measurably reduced coordination/apposition errors; UiO1 (Read, Velldal, Oevrelid & Oepen 2012) reached scope-resolution F1=85.26 (predicted cues) on the *SEM-2012 CD-SCO benchmark using syntactic features.

**P_deflated:** 0.45 (see full note's P-breakdown for cue-detection 0.55, scope-attachment 0.45, end-to-end lift 0.45 -- composite anchored to the scope-attachment number since that gates everything downstream)
**HP:** cue-detection recall >= 0.95 on negation-tagged items; scope-attachment accuracy >= 0.85 on the difficulty-on subset (coordination + intervening-adverb + relative-clause cases); end-to-end who-is-affected accuracy on the NEGATED subset improves >= 0.30 absolute over the ignore-negation baseline; affirmative-item accuracy regression <= 0.02 absolute
**MID:** scope-attachment 0.60-0.85, or end-to-end lift 0.15-0.30
**HF:** scope-attachment < 0.60 on the coordination/embedding difficulty-on subset (mechanism-level: dependency attachment + naive conj-propagation insufficient, needs a real CRF/classifier scope resolver per *SEM-2012's best-system pattern); OR affirmative-item accuracy regresses > 0.05 absolute (net-harmful)
**Tier hint:** CPU-eligible, cheap (feature check + graph walk over an already-computed UD parse; no training, no GPU)
**Why now:** direct code-level confirmation the gap exists (FUNCWORD list) + direct data-level confirmation of real incidence (see Rank 2 -- must run alongside/before this) + strong, credited, already-published precedent for the exact mechanism (DEEPEN/DepND/UDepLambda), not a speculative design.

---

### Rank 2: negation-balanced eval-slice extension -- DATA prerequisite, must run before or alongside Rank 1's full-scale measurement

**Anchor pointer:** Pull additional (verb, patient, negation-scope) items from the full UD-EWT source (`experiments/data/ud_english_ewt/en_ewt-ud-{train,dev,test}.conllu`) beyond the 136 currently sampled into `data/gold_construction_argstruct_ewt_v1/gold_construction_argstruct_ewt_v1.json`, using the same selection logic already used to build that gold (`tools/build_construction_gold.py`) but filtered for items where a `Polarity=Neg` cue's `advmod` head IS the labeled verb (or a `conj` sibling of it).

**Substrate-product reading:** This drill's own audit found 16/136 (11.8%) items with a negation-cue string hit, but after per-item scope inspection only ~13-14/136 (~10%) actually scope over the item's labeled verb (one hit is idiomatic "no matter what", one attaches to an adjective not the verb). Reaching a statistically meaningful n>=40 negation-subset for the Rank-1 HARD-FAIL/HARD-PASS measurement almost certainly requires this pull -- it is the single most likely near-term blocker (P_deflated 0.30 that n>=40 is reached WITHOUT this task), more likely to gate progress than any mechanism-level risk in Rank 1. Bounded, mechanical, no new annotation scheme (same parse-derived labeling philosophy as the existing gold's `label_derivation`).

**P_deflated:** 0.55 (mechanical extension of an existing, working pipeline -- main risk is whether UD-EWT train+dev+test contains enough additional clean negation-scoping items past the 136 already sampled, not whether the method works)
**HP:** n>=40 clean negation-subset items reached; n>=15 modal/hypothetical-subset items reached (for Rank 3)
**MID:** n in [25,40) negation items -- usable but underpowered
**HF:** n<25 even after exhausting train+dev+test -- would mean negation incidence in this register is genuinely too low for a standalone eval slice, requiring either a different corpus or pooling negation+modal together
**Tier hint:** CPU, near-zero cost (re-run of an existing script with a filter change)
**Why now:** this is the honest bottleneck flagged in the full research note's Data section -- run it FIRST or in parallel with Rank 1's cell-authoring so the full-scale measurement isn't blocked on it later.

---

### Rank 3: modal/factivity lookup (implicative-verb lexicon) -- phase 2, ships only after Rank 1 clears

**Anchor pointer:** Small closed lexicon of implicative/aspectual predicates (try, attempt, manage, fail, almost, nearly, supposed to) per Karttunen's implicative-verb classification, plus conditional/hypothetical clause markers (`mark`-relation "if"/"unless"), tagging the embedded event HYPOTHETICAL-MODAL rather than REALIZED/NEGATED. Routes to the existing abstain/confidence layer rather than a forced binary flip, consistent with the graded-not-categorical precedent from `research_verb_affectedness_type_gate_2026-07-20.md`.

**Substrate-product reading:** This is the lower-confidence, harder half -- de Marneffe, Manning & Potts (2012) show veridicality is not purely lexically determined (context/world knowledge matter), an honest ceiling on how far a closed-lexicon rule can go. The gold's modal-cue subset (11/136 items) is smaller and more ambiguous than the negation subset per this drill's own inspection (some "if"/"supposed to" hits are borderline epistemic hedges, not clean non-occurrence markers).

**P_deflated:** 0.35 (lowest-confidence anchor in this hand-off; the implicative-verb lexicon was added from the Director's own cross-check, NOT independently verified by either lit-scan sub-agent this cycle)
**HP:** modal/factivity lookup resolves >= 50% of the hypothetical-cue subset with correct HYPOTHETICAL-MODAL tagging
**MID:** 30-50% coverage
**HF:** < 30% coverage (Karttunen-class lexicon insufficient for this register; would need broader veridicality-prediction features, likely crossing into non-glass-box territory -- flag and stop rather than force it)
**Tier hint:** CPU, cheap (lexicon lookup + one deprel check for conditional markers)
**Why now:** explicitly gated -- do not dispatch until Rank 1 (negation-only) clears at least MID-band, per the phased-shipping design in the full research note.

---

## Context pointers

- Full research note (all derivations, brain-mechanism lit-scan, glass-box NLP prior-art lit-scan, data audit, full P-breakdown): `d:/AI/hd-instrument/notes/research_negation_factuality_gate_reader_2026-07-21.md`
- Current reader code confirming the gap: `experiments/exp_learned_argstruct_parser_lccp_independent_gold_v1.py` (FUNCWORD set, line 136)
- Construction gold + negation/modal incidence data: `data/gold_construction_argstruct_ewt_v1/gold_construction_argstruct_ewt_v1.json`
- UD-EWT source parses (for Rank 2's extension pull): `experiments/data/ud_english_ewt/en_ewt-ud-{train,dev,test}.conllu`
- Sibling gate (graded, not categorical, same wiring pattern into the Step-2 vote): `notes/research_verb_affectedness_type_gate_2026-07-20.md`
- McGuffey gold has NO raw text (`data/gold_mcguffey_lccp_argstruct_v1.json`) -- negation incidence there is unmeasurable without re-extraction from source; flagged, not a blocker for Rank 1/2 which run on the construction gold.
- Adjacent-but-different prior artifact (do not confuse): `notes/exp_dev_handoff_research_negation_detection_2x_2026-06-06.md` (KF-1 fact-verification subsystem, non-glass-box DeBERTa proposal, different subsystem entirely).

---

## Contract

exp_dev owns ALL of: anchor naming, sweep grid design, queue routing (CPU vs GPU),
timeout estimation, pre-reg HP/MID/HF numerical bounds, cap_map decision post-verdict.

This file is context + direction only. No experiment design is pre-committed here.

## Autonomy declaration

exp_dev may: reorder Rank 1 vs Rank 2 (they are near-parallel, not strictly sequential -- Rank 1's cell can be authored while Rank 2's data pull runs); combine Rank 1 and Rank 2 into a single cell if the data pull is cheap enough to inline; defer Rank 3 indefinitely if Rank 1 does not clear MID-band; adjust the coordination-propagation rule's exact `conj`-blocking conditions based on what the extended data (Rank 2) reveals about real-world exceptions.
