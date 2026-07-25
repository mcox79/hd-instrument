# Pre-registration: intrinsic_foundation_loop_tie_gaps_v1

Cell: `experiments/exp_intrinsic_foundation_loop_tie_gaps_v1.py`
Design-of-record: `notes/intrinsic_foundation_loop_tie_gaps_2026-07-25.md`
Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic; VET-PENDING; no atom banking.

## Question
Does the intrinsic foundation loop -- DETECT own gap (reasoner tie) -> ACQUIRE discriminating definitional facts answer-agnostically -> CONSOLIDATE (trust-gate + sleep) -> RE-DECIDE -- actually RESOLVE the reasoner's own ties end-to-end (not just "it ran")?

## Gap set (intrinsic, answer-agnostic)
44 GENUINE lemma ties = questions where the composed DerivationReasoner co-derives gold AND >=1 distractor at BOTH link_mode=lemma_syn and the tighter lemma (the substrate's own "can't decide" flag). Exactly reproduced by reusing `exp_arc_reasoner_link_precision_tie_prune_v1.eval_config` + `classify_tie_transitions` (no re-derivation drift).

## Arms (one variable at a time)
- ARM0 = reasoner legacy node-combiner tie-break (POSITIVE CONTROL).
- FLOOR = text meaning-match (SemanticHDEncoder cosine), NO facts (isolates scorer swap).
- ARM1 = ORACLE-acquisition ceiling: widest answer-agnostic retrieval (choice content-words + lemmas + WordNet single-token synonyms) from the WorldTree tablestore (parse_tablestore_typed, ALL relations). FLOOR->ARM1 one variable = fact augmentation.
- ARM2 = AUTONOMOUS loop: detect tie -> retrieve own way (content+lemma, no synonym oracle) -> INGEST each fact through hd_fact_store.HDFactStore trust-gate (WorldTree=TRUST_HIGH) -> sleep-consolidate KEEP_EPISODIC -> query facts back by glass-box unbind -> re-decide. ARM1->ARM2 one variable = retrieval reach.
- ARM3-within = must-fail: oracle facts shuffled ACROSS the tied choices (design-note spec; clean control only on 2-way ties).
- ARM3-global = robust must-fail: concept->fact binding fully broken across ALL questions (challenges gold even for multi-way ties).

## Anti-leak (hard)
Acquisition keyed on choice/stem content-words, NEVER correct_index. Tie-break is a GENERAL meaning-match (augmented-choice vs stem cosine), not a hand-wired fact->choice map. Single-valid gold_only decisions returned UNCHANGED in every arm (preserved @1.00 by construction + asserted). Held-out ARC-Challenge test; science rules NOT from test labels. Deterministic seeding (numpy default_rng; no hash()-seed, no list(set())).

## POSITIVE CONTROL (Gate D, reproduce-prior)
`n_gap == 44` AND `arm0_correct == 15` (== 15/44 = 0.3409, reproduces 29570 EXACT). MISMATCH on full-set => POSITIVE_CONTROL_FAIL regardless of arm metrics.

## HARD-PASS bands (all four required)
1. `d(ARM1 - ARM0) >= 0.15` (oracle ceiling beats deployed baseline).
2. `d(ARM1 - FLOOR) >= 0.10` (lift attributable to FACTS, not the scorer swap).
3. `d(ARM3-global - FLOOR) <= 0.05` (concept-SPECIFIC: the right concept's facts drove it; robust across arity).
4. `gold_only_preserved >= 1.0`.

## HARD-FAIL / HONEST-KILL band
`d(ARM1 - ARM0) <= 0.05` -> the oracle fact cannot break ties over thin-GloVe meaning-match -> honest kill routing to deeper grounding. (This was the design note's deflated expectation.)

## MIDDLE_BAND
Between the bands (ARM1 clearly beats ARM0 but a generic-text component survives global scramble).

## Discriminator-fires + can-fail (smoke/self-test)
`--self-test` (GloVe-free bow encoder) plants a 2-choice tie: right discriminating fact -> picks gold; scrambled fact -> does NOT pick gold. Also asserts: HDFactStore ingest->glass-box-recover round-trip; autonomous loop ingest+recover; single-valid gold_only unchanged; real acquisition index builds + retrieves a known concept.

## Compute architecture
Sequential-CPU justified: wall < 3 min (135.5s MEASURED); the discriminator IS the full 44-tie gap set (full-scale, no smoke-subset saturation); HD store ops are tiny per-tie. No GPU batching candidate.

## MEASURED RESULT (this run; VET-PENDING)
`MEASURED@data/exp_intrinsic_foundation_loop_tie_gaps_v1/metrics.json`
- ARM0 = 0.3409 (repro_29570 = True), FLOOR = 0.250, ARM1 = 0.5455, ARM2 = 0.500, ARM3-within = 0.4545, ARM3-global = 0.3636.
- d(ARM1-ARM0) = +0.205; d(ARM1-FLOOR) = +0.295; d(ARM2-ARM0) = +0.159 (ARM2 captures 77.8% of the ARM1-ARM0 ceiling); d(ARM3-global-FLOOR) = +0.114.
- Concept-SPECIFIC lift (ARM1 - ARM3-global) = +0.181 (majority of the +0.295 over FLOOR); generic science-text relevance (ARM3-global - FLOOR) = +0.114.
- 2-way ties (n=21): FLOOR 0.429, ARM0 0.524, ARM1 0.714, ARM2 0.714 (autonomous == oracle, full ceiling), ARM3-within 0.524, ARM3-global 0.476 (collapses to ~floor).
- gold_only preserved = 1.00.
- tier = MIDDLE_BAND (3/4 bands; global-scramble-collapse fails: a generic-relevance component survives).

## Verdict read (VET-PENDING, exp_dev CLAIM)
NOT the deflated honest-kill: ARM1 decisively beats ARM0 and the concept-specific effect DOMINATES the generic-text effect. The bottleneck is acquisition-precision (tractable), NOT "the rep cannot break ties." Autonomous loop captures ~78% of the oracle ceiling (100% on clean 2-way ties). MIDDLE_BAND is earned (the meaning-match is still thin GloVe and a generic-relevance component survives global scramble). Routes to: deeper/grounded meaning-match + stronger acquisition precision on multi-way ties. Skunkworks owns landed-VET before this drives anything.
