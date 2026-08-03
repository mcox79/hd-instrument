# Pre-reg: grounded_appraisal_richer_eval_v1 (THE PROPER VALIDATION)

Cell: `experiments/exp_grounded_appraisal_richer_eval_v1.py`
Eval: `data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1.jsonl` (15 items,
Director-VERIFIED, defeats trivial baselines).

## Question
Re-run the EXISTING grounded-appraisal mechanisms (REUSE, do not rebuild) on the richer eval that
finally has multi-candidate + genuine irony/sincere cases. Does the coherence-RANKING half of the
coref-as-bridging circuit (untested per the trustworthy gate,
`notes/audit_causal_attribution_bridging_TRUSTWORTHY_GATE_2026-08-03.md`) work when it has >=2
competitors? Does intent-valence-via-ToM beat surface on irony?

## Mechanisms reused verbatim (imported, not reimplemented)
- `bridge_causal_antecedent` / `recency_baseline` / `_corefers` from
  `exp_causal_attribution_bridging_v1.py` (themselves reuse `hdlab.coreference_resolver._pick_strict_cb`).
- `MentalStateAffectRegister` from `exp_intent_valence_via_mentalizing_v1.py` (FHRR ToM register).
- `resolve_valence_blind` from `exp_grounded_structure_phase0_probe_v1.py` (blind valence lexicon).

## Arms
- MULTI (4 items): BLIND_FAITHFUL (valence from each candidate's own span via blind lexicon;
  patient=victim symmetric; true earlier / distractor more-recent per gold recency structure);
  STEELMAN_FORCED (both candidates forced HARM so >=2 pass the filter and `_pick_strict_cb` is GENUINELY
  exercised); RECENCY baseline.
- IRONY/SINCERE (6): SURFACE (surface_valence reading) vs INTENT (ToM retaliation register query_affect).
- BENEFICIARY (5): reported honestly (no auto beneficiary resolver exists; mechanism is oracle-only).

## FAIR / contamination
No arm reads gold answer fields (true_blocker_agent / true_intent_valence / true_beneficiary). GIVEN =
factual-identity tier only (candidate NAMES, victim identity, real positions, the "distractor is
recency-favored" SETUP structure). Per-item `used_contamination` logs it.

## Pre-registered verdict bands
- RANKING_VALIDATED: >=1 item where ranking runs (>=2 gate candidates) AND steelman_acc > recency_acc AND
  steelman_acc >= 0.75.
- STILL_FILTER_ONLY: ranking never runs (0 items reach >=2 candidates in either faithful or steelman).
- RANKING_RUNS_BUT_EQUALS_RECENCY_FALSIFIED: ranking runs but steelman_acc <= recency_acc (ranking IS
  recency, not a distinct capability).
- VALENCE_VALIDATED: genuine intent (spurious fires discarded) beats surface on irony AND >=0.667 AND
  sincere preserved. VALENCE_PARTIAL_SINGLE_RETALIATION_FLIP: sub-majority genuine lift. NO_LIFT / REGRESSED
  otherwise.

## Honest disclosure (post-run tightening, MORE conservative not less)
The `tom_fire_legitimate` / GENUINE-intent guard was added AFTER the first run, when vetting revealed
irony_003 "fired" the ToM register on a WRONG key (Jo/Meg, no supplied prior-affect event) with near-zero
noise scores (HARM=0.032 vs HELP=-0.018) barely clearing the 0.02 refuse margin -- a SPURIOUS fire that
landed on the correct answer by luck. The guard discards such fires (falls back to surface) so lucky noise
is never credited. This tightened the raw irony intent from 2/3 to a genuine 1/3 -- a discipline catch that
made the verdict more conservative (VALIDATED -> PARTIAL), disclosed rather than hidden.

## Compute architecture
sequential-CPU, <0.02s total, n=15 (wall time << 10s). No GPU batching candidate. Foreground-to-completion
in .venv. Deterministic seeded (FIXED_SEED=990103, torch.Generator).
