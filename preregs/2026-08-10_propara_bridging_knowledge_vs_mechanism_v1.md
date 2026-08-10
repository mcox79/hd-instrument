# Pre-registration: exp_propara_bridging_knowledge_vs_mechanism_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator decisive-diagnostic follow-up to
ARM2 (which exhausted the localization thread + retro-corrected v3). Decides the NEXT direction:
is the UNMENTIONED-state wall the BRIDGING MECHANISM or the missing KNOWLEDGE?

## Prior-work check (SUBSTRATE-KB)
Same arc (top hit cosine 0.3096 FrameNet, no prior arc cell > 0.30). Direct follow-up on ARM2's
own landed result; novelty inherited.

## The question
The residual after the localization thread = cross-step inference for UNMENTIONED states =
persistence (priors cover it) + CAUSAL BRIDGING from world-knowledge. Diagnostic: supply the
minimal general bridging knowledge; does the retrieve-validate loop USE it to infer unmentioned
state-changes? (a) WITH > WITHOUT + > prior-lesion, WITH not ~1.0 -> loop uses knowledge -> wall
is SOURCING (build a bridging KB). (b) WITH ~= WITHOUT -> loop cannot bridge even given knowledge
-> MECHANISM wall (converges with the SIQa covered-knowledge-but-USE-fails finding).

## Design (isolate BRIDGING; grant event-COUNT budget to BOTH arms)
Both WITH and WITHOUT get the ORACLE event-count budget (counting is NOT the variable -- that
cost was measured in ARM2). The ONLY variable = bridge-location knowledge.
- WITHOUT_KNOWLEDGE: oracle budget + ARM2 participant-attributed firing (dep-parse+coref). Events
  land on ATTRIBUTED (mentioned) steps; an event whose participant is UNMENTIONED at its true step
  is not attributed -> random fallback (loop cannot LOCATE the unmentioned change).
- WITH_KNOWLEDGE: same loop + oracle BRIDGE FACTS. A bridge fact = minimal GENERAL causal rule
  `(effect_type, trigger_verb_class)` per participant (e.g. "p is DESTROYED by a DESTROY-class
  consumption process" / "p is DESTROYED as a precursor of a CREATE-class 'becomes' conversion").
  Sourced from gold: for each of p's UNMENTIONED gold changes, record (effect_type, the
  participant-AGNOSTIC verb-class present in the TEXT at that step). The loop RETRIEVES the fact,
  LOCATES a text step carrying the trigger verb-class (step from TEXT, not oracle), VALIDATES state
  feasibility, APPLIES the effect. Trigger absent/ambiguous -> can still fail (NOT a trivial copy).
- PRIOR_LESION: oracle budget + random-monotonic (content-free floor).

## Honest guards (the recurring oracle-leak trap)
1. Bridge fact = general (effect_type, trigger_class), NEVER (step, label). No step index, no
   per-step label.
2. KNOWLEDGE-ABLATION must COLLAPSE: WITHOUT unmentioned macro-F1 must be < WITHOUT_COLLAPSE_CEILING
   (0.60). If WITHOUT already scores high, the knowledge was not needed (no bridging happening) ->
   result VOID (HARD_FAIL_ABLATION_DID_NOT_COLLAPSE).
3. LEAK CHECK: if WITH unmentioned macro-F1 > LEAK_CEILING (0.95), the trigger uniquely located
   every step (answer leaked) -> MIDDLE_BAND_POSSIBLE_LEAK (inconclusive). Genuine bridging is
   PARTIAL (limited by trigger-verb readability -- reported as bridgeable_fraction -- + multi-step
   ambiguity).

## Metric
PRIMARY = per-step 4-way change-label macro-F1 on the UNMENTIONED subset (trap-check proxy
restricted to mentioned==False rows -- exactly the residual; dev n=770, test n=1119). Reported
alongside accuracy, the official metric (full), and the focus. Decisive quantities: with_minus_
without, with_minus_prior_lesion, with_minus_best_baseline. bridgeable_fraction = fraction of gold
unmentioned changes that HAVE a textual trigger (upper bound on what bridging can recover from
text). Scramble = secondary/optional (2 seeds; bridging is a knowledge test, not an order test).

## HARD-PASS / HARD-FAIL bands (DEV-calibrated; pinned before TEST)
- `WITH_MINUS_WITHOUT_HARD_PASS = 0.05`: WITH beats WITHOUT on unmentioned macro-F1 by >= this AND
  WITH > prior-lesion -> **HARD_PASS_KNOWLEDGE_IS_LOAD_BEARING (wall = SOURCING; mechanism works)**.
- `WITH_MINUS_WITHOUT_HARD_FAIL = 0.02`: WITH - WITHOUT < this -> **HARD_FAIL_MECHANISM_WALL (loop
  cannot use supplied knowledge)**.
- `WITHOUT_COLLAPSE_CEILING = 0.60`: WITHOUT >= this -> ablation did not collapse -> result VOID.
- `LEAK_CEILING = 0.95`: WITH > this -> possible answer-leak -> MIDDLE_BAND (inconclusive).
- MIDDLE_BAND otherwise (partial).
- Infra gates: arms_differ, decode >= 0.99 all three arms.

## HP_SCOPE
`{bridging: [with_beats_without_on_unmentioned, with_beats_prior_lesion, knowledge_is_load_bearing]}`.

## Cell-template mandates
arms_differ (asserted self-test + recorded); final_metrics_atomicity tmp_replace; except SystemExit
before except Exception (grep-verified); crlb_n/a; calibration_check default_ok; deterministic_seeding
(hashlib-seeded rng, no Python hash()/list(set())); progress_logging print_flush_true.

## Compute architecture
Sequential-CPU, justified: reuses ARM2 precompute (spaCy parse + coref align, parsed once) + gold
bridge-fact extraction + discrete firing + FHRR decode. No batching. MEASURED self-test 1.7s. Expect
smoke ~30-60s, full ~40-90s. Run INLINE/LOCALLY foreground.

## Self-test findings (real code path)
**MEASURED@..._metrics.json (self_test, 1.7s):** synth with an UNMENTIONED destroy ("the fire
consumes everything" -> seed destroyed unmentioned): bridge fact = {DESTROY: {DESTROY}} (extracted,
general form), WITH placed DESTROY at the consume step (3), decode 1.0 all arms, 4 verdict-logic
unit checks correct (used HARD_PASS / wall HARD_FAIL / no_collapse HARD_FAIL / leak MIDDLE_BAND).

## Smoke findings (DEV)
**MEASURED@..._smoke/metrics.json (dev):** UNMENTIONED with_f1 0.399, without_f1 0.324 ->
with_minus_without +0.075, with_minus_prior_lesion +0.062; ablation_collapsed True (WITHOUT 0.324
< 0.60), leak False (WITH 0.399 < 0.95), bridgeable_frac 0.56. -> HARD_PASS on DEV; bands (v3-style
0.05/0.02) held, pinned before TEST.

## Full findings (TEST) -- the decisive read: KNOWLEDGE-SOURCING is the wall, the mechanism WORKS
**MEASURED@data/exp_propara_bridging_knowledge_vs_mechanism_v1/metrics.json (test, 54 paragraphs,
UNMENTIONED subset n=1119 per-step cells; run_mode=full, cardinality_ok, arms_differ True, decode
1.0 all three arms). Verdict: HARD_PASS_KNOWLEDGE_IS_LOAD_BEARING_wall_is_SOURCING.**

UNMENTIONED-subset per-step change-label macro-F1:
- baselines majority/bow 0.238, bagstates 0.246 (floor -- cannot do unmentioned)
- prior_lesion 0.318 (oracle budget + random-monotonic)
- **WITHOUT_knowledge 0.356** (attributed firing; cannot LOCATE unmentioned changes -> random fallback)
- **WITH_knowledge 0.463** (bridge facts locate unmentioned changes at their trigger steps)

**DECISIVE margins: with_minus_without = +0.106; with_minus_prior_lesion = +0.145;
with_minus_best_baseline = +0.217.** The retrieve-validate loop DEMONSTRABLY USES the supplied
bridging knowledge: +0.106 macro-F1 over the identical knowledge-ablated loop on the exact residual
subset.

**All three honest guards PASS (not a leak, not a no-op ablation):**
- Ablation COLLAPSED: WITHOUT 0.356 < 0.60 -> the loop genuinely CANNOT solve unmentioned changes
  without the bridging knowledge (the knowledge is load-bearing, not decorative).
- NO LEAK: WITH 0.463 < 0.95 -> partial, genuine bridging, NOT an answer-copy. Bounded by
  bridgeable_fraction = 0.728 (67/92 unmentioned gold changes have a textual trigger; the other
  27% are truly cueless -> unbridgeable from text alone even with the effect known = a real
  residual ceiling) + multi-step trigger ambiguity (the loop locates the FIRST feasible trigger
  step, so some go to the wrong step).
- Bridge fact is the general (effect_type, trigger_verb_class) rule, never (step, label).

**Secondary (scramble, 2 seeds):** WITH unmentioned-F1 0.415/0.420 scrambled vs 0.463 natural ->
retained ~0.68. Bridging is MILDLY order-sensitive (first-feasible-trigger locating depends on
order) but far less than localization -- as expected for a knowledge test, not an order test. Not
gated.

**Official metric (full set, context not claim):** WITH F1 0.677 vs WITHOUT 0.671 (+0.006 only) --
the bridging lift is CONCENTRATED in the unmentioned residual (a minority of all cells), so it
barely moves the participant-level full-set number; both are below the oracle-budget random-
monotonic prior_lesion (0.722) which does well on the majority mentioned/existence cells. This is
honest scoping: the claim is on the unmentioned subset where the wall is, not the full set.

**DECISIVE CONCLUSION (outcome (a) of the diagnostic):** given the minimal general bridging
knowledge, the retrieve-validate MECHANISM successfully infers unmentioned state-changes
(+0.106 over ablation, non-leaked, ablation-collapsed). Therefore the UNMENTIONED-state wall is
KNOWLEDGE-SOURCING, NOT the bridging mechanism. This CONVERGES with the charter's foundation
direction: build a real bridging KB (world-knowledge of process->effect-on-participant, e.g.
"conversion consumes its precursor", "combustion destroys fuel"). It does NOT converge with the
SIQa mechanism-wall (covered-knowledge-but-USE-fails) -- here the loop DOES use the knowledge.
Honest bound: even perfect sourcing caps at ~bridgeable_fraction (0.73 from text cues); the
cueless ~27% + multi-step ambiguity need either richer context modelling or are genuinely
underspecified. Next: source a real (non-oracle) causal bridging KB (ConceptNet/ATOMIC process
frames / a distilled process-physics KB) + feed it as typed facts, and re-run WITH-vs-WITHOUT with
the REAL KB to measure how much of this oracle-knowledge lift survives real sourcing.
