# What was wrong: we built the brain's BACKUP (heuristic) role route, not its MAIN (structural) one -- and measured it on a confounded ruler

Owner (2026-09-04): "drill and research this to fully understand, and evaluate for true brain fidelity. something
is wrong." It was. Two compounding errors, both now confirmed on disk + on a CLEAN instrument.

## ERROR 1 (FIDELITY): our who-did-what is the AGRAMMATIC/heuristic route, not the brain's structural route

Research verdict (hdi_research, cited): the brain assigns core roles by reading grammatical relations (subject/
object) off an incrementally-built PARSE, BINDING arguments into the verb's frame slots (Hagoort MUC: verb frames
in temporal cortex, unification in Broca's area), and applying linking rules (grammatical-relation -> thematic-role)
with a VOICE remapping (passive: subject->patient, by-phrase->agent). Cue-competition + thematic fit are the
SECONDARY route -- prediction + tie-breaking under ambiguity -- NOT the primary selector.

Our live reader does the opposite (confirmed on disk): `route_predicate_arguments` -> `hybrid_role_patient` ->
`resolve_patient`, which "takes NO arc heads, invariant to permuting arc heads" -- a flat cue/position selector.
The parse (`heads`) is used ONLY for oblique/spatial roles, never the core agent/patient. **This is exactly the
algorithm agrammatic Broca's aphasics fall back to** (first-noun=agent + plausibility) -- they fail on reversible/
non-canonical and ace semantically-constrained items -- OUR precise failure profile. We replicated the LESIONED
brain and left its main, accurate system unbuilt. Thematic fit (my iters 2-4) was MISUSED as a primary selector
(the research: it is a predictor/re-ranker, useless on reversible items) -- a red herring.

## ERROR 2 (INSTRUMENT): the role-balanced gold is confounded -- my iters 1-4 numbers are largely uninterpretable

The role-balanced gold (`aligned_gold.jsonl`) is built from crowd QA-SRL *question* annotations: its `voice` is the
QUESTION's voice (a passive question is routinely asked of an active clause), its patients are often COREFERENT
ANTECEDENTS not the surface argument (~29% of "errors"), its `heads`/`pos` are the READER'S OWN parser (two
provenances stapled -> "role vs parse" disagreements baked in -> my measured 45% patient-attaches-to-verb), its
distribution is ENGINEERED (post-pool down-sampled to force a 0.5 floor; 62% passive vs ~10% natural), and the live
reader's cue weights were TRAINED on it (circular). A signal-loss study here measures the reader's parse against
itself + crowd artifacts. **NOT a valid who-did-what instrument.**

## THE CLEAN TEST (UD-EWT gold dependencies -- non-circular; patient := obj [active] | nsubj:pass [passive] + voice)

`experiments/exp_whodidwhat_ud_structural_v1.py`, n_active=1147, n_passive=108 (UD-EWT test):

| route | active | passive | ALL |
|---|---|---|---|
| FLOOR (nearest post-verbal position) | 0.664 | 0.732 | 0.669 |
| **HEURISTIC (the live reader: cues+position+voice, NO structure)** | 0.667 | 0.732 | **0.673** |
| **STRUCT_ourparse (roles off OUR arc-parse dependents + voice remapping)** | 0.733 | 0.750 | **0.735** |
| **STRUCT_goldparse (roles off a PERFECT parse + voice -- the ceiling)** | 0.906 | 0.991 | **0.913** |

**Three load-bearing facts:**
1. **The STRUCTURAL route is the brain's mechanism and it WORKS: perfect-parse structure hits 0.913 overall / 0.991
   on passives -- human-level.** Structure + voice remapping nails who-did-what.
2. **The structure-first route BEATS the live heuristic EVEN WITH OUR CURRENT (weak) PARSER: 0.735 vs 0.673 (+0.062).**
   So the fix is buildable NOW -- read the patient off the verb's parse dependents + voice, instead of the flat
   cue/position selector.
3. **The live HEURISTIC barely beats plain position (0.673 vs 0.669)** -- the Competition Model adds ~nothing on
   clean gold, because its cues were tuned on the confounded gold (circular). Its apparent value was overfitting.

## WHAT THIS CORRECTS (be honest about my own earlier conclusions)

- My iters 1-4 "the residual is MEANING / thematic fit / a domain-matched foundation" was **an artifact of the
  confounded gold + misusing thematic fit as a selector.** On clean gold the residual is STRUCTURE (parse quality),
  not meaning. Thematic fit is a red herring for the primary who-did-what decision.
- "Stage 4 (Competition Model) is the clean +0.0247 win" was **inflated by circularity** (weights trained on the
  eval gold); on clean gold the Competition Model ~= position.
- The genuinely-load-bearing earlier finding SURVIVES: we match the brain on canonical, and the gap is on
  non-canonical -- but the FIX is the structural route (dorsal parser), exactly as the agrammatism parallel predicts.

## THE FIX (brain-faithful, buildable, measured)

Build the STRUCTURE-FIRST route and demote the current organ to the gated heuristic fallback (the brain's dual
route; structure wins, cues/thematic-fit only break genuine ties):
1. **Read core roles off the parse's grammatical relations** (the verb's subject/object dependents) + **voice
   remapping** (active: obj=patient, subj=agent; passive: subj=patient, by-phrase=agent). Handle coordination/
   control by SHARING one filler across verb slots (UD enhanced-dependency style). +0.062 over the live heuristic
   with our current parser, on clean gold -- a ready win.
2. **Improve the PARSER toward the 0.913 ceiling** -- the remaining +0.18 is parse quality (patient correctly
   attached to its verb), a STRUCTURAL problem, not a meaning one. This is the real who-did-what lever.
3. **Re-base all who-did-what evaluation on the clean UD-EWT structural gold** (or the repo's
   `eval_gold_mention_role_modern_ud_ewt_v1`, roles off gold UD deprels) -- never the confounded role-balanced gold.

**One-line answer to "what's wrong":** we assign who-did-what with the brain's damaged backup system (flat cues) on
a broken ruler; the brain reads it off sentence STRUCTURE, which -- even with our imperfect parser -- is already
better (+0.06) and, with a good parse, reaches human level (0.91). The lever is the PARSER/structure, not meaning.
