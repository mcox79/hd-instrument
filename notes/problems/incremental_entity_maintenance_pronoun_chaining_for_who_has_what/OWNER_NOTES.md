---
owner_verdict: DONE
---

SUBMISSION -- incremental_entity_maintenance_pronoun_chaining_for_who_has_what
status: SOLVED (WIP until owner_verdict: DONE). NO hdlab/ written (Q111 -- strategy lands the wire). Witness 12/12; ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_entity_maintenance_chaining.py   # 12/12 FROM SOURCE

MECHANISM (brain-foundational): a RECURRENT incremental entity-maintenance loop -- each resolved he/she pronoun is
chained back into the PICKED entity's ACT-R activation history, so later pronouns retrieve it -- run over the PINNED,
near-optimal graded pick (local_graded_pick, self-tested BIT-EQUAL to hdlab.graded_coref_pick). This is the parent's
located ceiling lever (grouping decomp: ~91% of the he/she headroom is pronoun-chaining, not the pick). The reader
already HAS the primitive (event_centrality_coref chain_pronouns=True) but on its weaker centrality pick + surface
grouping; the contribution is running the loop over the graded pick with clean grouping.

MEASURED (LitBank gold coref, he/she who-has-what pick accuracy, gold-nominal grouping; pick HELD fixed; deterministic):
 * HELD-OUT (12 test docs, n=977): no-chaining floor 0.464 [0.433,0.495] -> CHAIN 0.521 [0.489,0.553], PAIRED
   +0.0573 [0.0328,0.0809] (hw 0.024). ALL 25 docs: 0.474 -> 0.538, +0.0647 [0.047,0.084] (unpaired-sep too).
   Fully-glass-box (aliaser grouping): ALL 0.451->0.549 +0.098; TEST 0.443->0.511 +0.068 CI-sep.
 * ATTRIBUTION surgical: nochain and chain use the IDENTICAL pick AND identical candidate entities -- only the histories
   differ -> the lift is 100% entity-maintenance, not the pick. Reproduces the parent decomposition (gold_anchored-
   nochain +0.24 ~ gold_nom->gold +0.26).
 * LONG-DISTANCE RE-INSTATEMENT (bar item 4, CONFIRMED): the entire gain is FAR-from-nominal -- far (nominal >=2 back,
   n=717) 0.261 -> 0.471 toward the per-bucket gold ceiling 0.750 = 43% of that bucket's gap recovered (long bucket,
   n=492: 0.185->0.423); NEAR (n=962) inert-to-slightly-negative (nochain already 0.642 vs gold 0.703).
 * TWIN loses: shuffled-chain (random gender-compat target, K=300) mean 0.270 p95 0.283, CHAIN 0.538 >> p95.

WALLS -- all drilled to a brain mechanism AND a number:
 * SOFT ("hold both") maintenance LOSES to HARD commit (-0.024 to -0.036 CI-sep) -> attractors SETTLE to one pattern
   (CA3/Hopfield), they don't hold a superposition; Nref "hold both" is a readout transient, not the stored state.
   (A self-correction: my a-priori "soft is more faithful" was wrong, and the data said so.)
 * PICK x MAINTENANCE are COUPLED: the loop over the graded pick +0.065, but over the incumbent rigid hard-tier pick it
   HURTS -0.025 CI-sep -- a rigid tier can't consume accrued activation. The wire MUST deliver graded pick + loop together.
 * DECAY robustness: gain CI-sep across the brain-plausible range d=2/3/4, flips negative at d=1 -- the lever exists
   BECAUSE memory decays (ACT-R d>0).
 * RESIDUAL = the missing coherence PRIOR (Kehler-Rohde), not a chaining defect: oracle-gated ceiling splits it into
   propagation (+0.091) + missed-reinforcement (+0.085), both the pick's structural ceiling; 29.4% of errors are
   structurally-dominated (0.481 acc vs 0.684) and 99.5% of wrong picks are confident (so the confidence gate is a null).
 * COLD re-instatement (entity gone 2+ sentences) is OUT of scope for WM maintenance -> needs episodic CA3 completion
   (a different system; n~21 here, underpowered).

GENERALIZATION: object-'it' chaining (same accrual, number not gender) reproduces the mechanism -- ALL +0.0226
[0.003,0.042] CI-sep, twin loses, same long-distance signature (long +0.115); underpowered held-out (honest: object
held-out effect NOT established).

CAUGHT + FIXED 2 of my own measurement bugs before trusting numbers: a paired-population key collapse (midx not unique
across docs -> composite (doc,midx) key) and a PYTHONHASHSEED tie-break nondeterminism (~0.013 drift -> Counter.most_common;
verified identical across seeds 0/1/42).

IS IT MAXED VS THE BRAIN? The maintenance MECHANISM is maxed (every internal lever a located negative/near-optimum), but
who-has-what is at ~0.52 vs a human-coref ceiling ~1.0. The gap is in ADJACENT systems, ranked by leverage:
  1. coherence next-mention PRIOR (owns 29.4% of errors; but HARD build, MODEST payoff on real prose per coref-cap).
  2. parser/role front-end (the dominant LIVE cap: recipient extraction 0.33; masked here by gold roles) -- my pick for
     highest-value next build.
  3. entity grouping / name-shatter (65.6% shatter; a CONCURRENT solver owns it).
  4. episodic cold re-instatement via ca3_completer.  5. reanalysis (forward-only now; modest, leak-risky).

TO REALIZE: STEP 1 wire a default-off graded-pick chaining loop into the reader (OFF byte-identical; ON beats no-chaining
CI-sep, gain far-from-nominal); STEP 2 carry it into densify_world_state; STEP 3 build the coherence prior; STEP 4
episodic cold re-instatement. AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT.md 2b included.

FILES: experiments/exp_entity_maintenance_chaining_v1.py, experiments/exp_entity_maintenance_object_chaining_v1.py,
verification/test_entity_maintenance_chaining.py (12/12), notes/problems/incremental_entity_maintenance_pronoun_chaining_for_who_has_what/SOLVED.md.
