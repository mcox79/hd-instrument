# Wiring design: validated extraction -> overwrite-WM, real-text entity-tracking (updated 2026-08-02)

## Why (honest-lever + brain-foundational)
The extraction layer is VALIDATED + power-hardened on real text (atoms 29606/29608: interactive top-down
loop resolves quotative 0.895 + by-agent passive 0.739, clean dissociation). The WM layer's synthetic
SOR probe is REFUTED as an instrument (atom 29607: DG allocate HARD_FAIL + a permutation-symmetry
artifact + inert cleanup + recall walled ~0.32 + no positive control shows 0.75 reachable). Continuing to
tune the synthetic SOR = the instrument-perfectionism trap. The WM's ACTUAL value is discourse-level
entity-tracking; the honest test is on REAL text, not a synthetic score. This is also the comprehension
frontier: extraction answers "who-did-what THIS clause"; the situation-model/WM answers "who-did-what
ACROSS the passage" (Kintsch C-I; Zwaan situation model; Zacks event-segmentation update-at-boundary).

## Goal (one sentence)
Does feeding the validated extraction's per-clause (entity, role) sequence into the overwrite-brain-faithful
WM let us RECALL an entity's role from an EARLIER clause, across a real multi-clause McGuffey passage,
where a no-memory / last-clause-only baseline provably CANNOT?

## Architecture (assemble PROVEN organs; drop the refuted one)
real McGuffey passage (multi-clause)
  -> tagger (supplied structure, allowed) + VALIDATED interactive top-down extraction (learned mapping)
     => per-clause list of (entity_mention, role) [the 29606/29608 mechanism, reused verbatim]
  -> WM stream: PEGatedSlotWM (PE-driven overwrite gate = the ONE brain-faithful WM piece, atom-level
     proven). DROP the allocate mechanism (refuted, 29607). Content-route each (entity,role) to a slot;
     overwrite gate fires at role-change / new-info (Zacks boundary), holds otherwise.
  -> query: "what role did entity E have in clause k?" via HRR unbind of E's slot.

## Eval data (THE prerequisite -- new gold, director-hand-verified; supplying DATA is allowed)
Current gold is per-SENTENCE (quotative/passive), NOT cross-clause. Need NEW gold:
- ~12-20 short real McGuffey passages (2-4 clauses each), each with:
  - per-clause (entity_mention, role) [agent/patient/speaker]
  - cross-clause COREFERENCE (which mentions are the same entity, incl pronouns)
  - >=1 target entity that appears in >=2 clauses with a trackable role
- Source: McGuffey g1-g4 narrative (dialogue + action sequences are rich in this). Mine passages where a
  named entity recurs across clauses; hand-verify roles + coref.
- File: data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v1.jsonl (new; v1 gold files intact).

## Metric + FAIR-TEST controls (measurement-first; can-fail MUST fail)
- PRIMARY: cross-clause entity-role recall (query an entity's role from a NON-final clause).
- CAN-FAIL #1 (no-memory): last-clause-only readout MUST fail on earlier-clause queries (proves memory needed).
- CAN-FAIL #2 (shuffled-clause-order): degrades if order/segmentation matters.
- CAN-FAIL #3 (reservoir/random-WM): the non-vacuous floor (same one that floored SOR 0.04-0.09).
- BRAIN-METRIC (component-fidelity): the overwrite gate should SPIKE at role-change / new-entity and HOLD
  otherwise on REAL text (the spike_WR selectivity, but now measured on real discourse, not synthetic).
- ORACLE-vs-REAL extraction split (isolate WM from extraction error): run the WM given (a) GOLD per-clause
  roles [isolates the WM] and (b) the REAL extraction output [end-to-end]. (a) tells us if the WM works;
  the (a)->(b) drop tells us how much extraction error propagates. This is the key diagnostic.

## Honest risks / scope
- Extraction is imperfect (0.739 by-agent, 0.895 quot) -> errors propagate; the oracle-vs-real split
  quantifies this so we don't blame the WM for extraction misses.
- Coref across clauses (esp pronouns) is itself a competency (entity-identity, competency #1); the WM's
  content-routing must handle "he" -> the right slot. If coref is the wall, that's a DIFFERENT organ
  (competitive coref, atom 29592 has a piece) -- keep it separable in the metric.
- Small N (12-20 passages) = exploratory first; power later if the signal is real (same discipline as the
  by-agent gold N=5->23 power-up).
- This is EXTRACTION+MAINTENANCE, still NOT full comprehension (inference/discourse ahead).

## Sequence (cheap-first, one variable, no scale)
1. [director, lock-clean, no steer needed] Build gold_multiclause_entity_track_v1 (~12-20 passages, hand-verified).
2. [exp_dev, tightly scoped, ANTI-RACE: no nohup-detached, single clean run, no relaunch] Wire the probe:
   extraction-output -> PEGatedSlotWM(no-allocate) -> cross-clause recall; run oracle-arm first (isolate WM),
   then real-extraction arm; all 3 can-fail controls; brain-metric on real text.
3. VET (positives hardest); if the WM works on oracle roles but real-extraction drops it -> the wall is
   extraction/coref, not the WM (routes to the right next organ). If WM fails even on oracle roles ->
   the overwrite-WM doesn't scale to real discourse structure (a real, honest negative -> redesign).
All numpy/CPU, no GPU, no scale commitment. SCALE remains USER-steer-held.
