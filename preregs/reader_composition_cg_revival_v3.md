# Pre-reg: Track A v3 -- reader composition CG-revival gate

Anchor: `learned_role_assigner_reader_composition_v3`
Cell: `experiments/exp_learned_role_assigner_reader_composition_v3.py`
Metrics: `data/exp_learned_role_assigner_reader_composition_v3/metrics.json`
Builds on: v2 `exp_learned_role_assigner_reader_heldout_v2` (VET ad3bb811 = MEASURED_MECHANISM).

## Question
Does reading GENUINELY COMPOSE relations into comprehension, on a FAIR, POWERED test?
(v1/v2 left composition CONFOUNDED + underpowered: N=2 CMP Qs, frequency trivially wins by
topic-frequency on 3-sentence passages -> UNTESTED not failed.)

## Three v3 fixes (VET + drill both endorse)
1. COREF = MAINTAINED-SALIENCE (`WorkingOverlay` strategy='maintained', freq-primary) threaded
   per-arm; v2 hardcoded 'recency'. Tested where recency is WRONG (topical subject != nearest).
2. INANIMATE-POSSESSOR extraction: possessive 'has/have/had' takes possessor = first pre-verb
   candidate STRUCTURALLY (any animacy) -> 'the nest has eggs' -> poss(nest,eggs). Also recovers a
   POS-tagger JJS mis-tag of grounded nouns in determiner position.
3. FAIR POWERED COMPOSITION: 16 CMP Qs (was 2) on longer CONSTRUCTED passages with FREQUENCY
   DECORRELATED by construction (a distractor entity of the answer type is more frequent than the
   answer; 2 owners/objects/locations so the 2-relation JOIN is load-bearing).

## Arms (one variable per contrast)
learned_full (learned + maintained coref) [CLAIM]; recency_coref (learned + recency) [must-beat CC];
learned_nocoref (coref off) [ablation]; positional (positional + maintained) [context];
frequency (no-relation grounded floor, DECORRELATED) [must-NOT-win CMP].

## Slices
NC single-hop | CO ordinary coref | CC competitive coref (recency wrong) | CMP composition (N=16).
RELATION-F1 scored on REAL held-out McGuffey PRIMER (extraction generalization).

## Pre-registered bands (envelope-fail)
- CRUX-1 composition: HARD_PASS learned_full CMP >= 0.60 AND (CMP - freq_CMP) >= 0.30 AND
  >= nocoref AND >= recency. HARD_FAIL CMP < 0.40 OR CMP <= freq_CMP.
- CRUX-2 maintained-vs-recency: HARD_PASS maintained CC >= 0.60 AND (maintained - recency) >= 0.25.
  HARD_FAIL maintained_CC <= recency_CC.
- SANITY extraction: HARD_PASS RELF1_heldout >= 0.65; HARD_FAIL < 0.45.
- SECONDARY (reported, contributes to HARD_PASS; validated in v2): role-reversal, passive-beats-positional.
- baseline_in_band: 0.05 < freq_all, pos_all < 0.95.

## Design-gate (USER 07-17) -- all four verified at the (deterministic full-N) run
1. REAL baselines (freq decorrelated, no-coref, recency-coref, positional; pos_all=0.865 not strawman).
2. CAN-FAIL: 2/16 CMP fail (T4c it->tree coref; C5b extraction miss) -> not saturated.
3. DIFFICULTY ON: freq genuinely cannot win (freq 0/14 on decorrelated subset); competitive coref;
   inanimate possessor; passives.
4. ONE variable per arm contrast.

## Result (MEASURED@metrics.json; CLAIM-VET-pending, NOT self-declared chain-grade)
verdict=HARD_PASS. composition learned_full=0.875 vs freq=0.125 (margin 0.750, p=0.000; on the
constructed decorrelated subset reader 13/14 vs freq 0/14); maintained CC=1.000 vs recency=0.000;
RELF1_heldout=0.727; reversal learned=1.00 freq=0.33; passive learned=1.00 pos=0.00.

## Honest deflation (report as hypothesis-pending-VET)
- CC 1.000/0.000 is CONSTRUCTION-DETERMINED (divergence passages + stipulated Centering gold): a
  WIRING/mechanism confirmation that maintained recovers the topical antecedent recency drops -- NOT
  independent empirical coref superiority (that = the prior LitBank VET a7ca3db1).
- Composition passages are AUTHORED (task-authorized) -> a CONTROLLED demonstration, not wild text.
  Support that it is not mere sentence-fitting: extraction is the SAME learned pipeline that
  generalizes on real held-out primer (RELF1 0.727).
- Real limit: it->tree (T4) = selectional-preference gap; maintained cannot break an equal-frequency
  tie (recency tie-break picks the recent 'tree').

## Compute / determinism
sequential-CPU, wall < 60s (directional gate; transparent classifier + symbolic overlay; no HD/torch/
GPU). OMP_NUM_THREADS=1; fixed seed 12345; fixed training order; sorted(set); no builtin-hash seeding.
Glass-box, learn-in-substrate, NO external LLM at runtime, NOT next-word prediction. Local/foreground.
NO push / NO remote-persist.
