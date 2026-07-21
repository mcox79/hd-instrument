# Pre-registration: wordnet_noun_semantics_kb_who_affected_breadth_v2

Date: 2026-07-21
Author: exp_dev (cell author)
Status: PRE-REGISTERED BEFORE FULL RUN (bands + CG-vs-MM criterion fixed before measurement)

## Prior-work KB check (substrate_query.sh)
Query "entity semantics noun WordNet selectional affectedness verb breadth generalization who-is-affected":
top hit cosine=0.365 = 'affectedness' (WordNet lemma, not a prior cell); no genuine dup at cosine>0.30 for
a verb-breadth re-test of the entity-semantics selectional gate. This cell is the CHAIN-GRADE follow-up to
atom 29420 (wordnet_noun_semantics_kb_who_affected_v1, MEASURED_MECHANISM). NOT novel science -- it is the
decisive breadth test the 29420 VET explicitly left open. Rediscovery-vs-novel: this is a DELIBERATE re-run
of the frozen 29420 rules on new data, not a new mechanism.

## Decisive question (what the 29420 VET left open)
atom 29420 showed the KB lifts who-affected +0.033 pooled (Pareto-clean, scramble-collapses, deployable,
leak-clean) BUT all 3 rescues were the SAME verb `met`, N=90 -> narrow exercise -> MEASURED_MECHANISM not
chain-grade. The path to CG = verb-breadth. Does the WordNet-lookup entity-selectional lift hold across
MANY DISTINCT VERBS (= settled capability = CHAIN-GRADE), or is its envelope NARROW (met/encounter-class
only = stays MEASURED_MECHANISM)? Honest either way -- do NOT force a CG.

## Frozen rules (NO re-tuning; re-tuning on the test gold = p-hacking)
- KB build (dominant-sense lexname + hypernym-closure animacy + grass-animacy fix), selectional override
  (kb_selectional_override), gate composition (kb_gate), eval (eval_ud), must-fail scramble (permute_feats),
  bootstrap (_bootstrap_delta) = ALL IMPORTED UNCHANGED from
  experiments/exp_wordnet_noun_semantics_kb_who_affected_v1.py (commit 67956a587 = atom 29420).
- ONLY new thing = comprehensive KB coverage of the breadth-gold nouns (per the USER reframe: meaning =
  comprehensive ASSIGNMENT/lookup; every noun gets looked up -- COVERAGE, not generalization-across-words).
  Built over v1 vocab UNION breadth-gold tokens with the SAME frozen build_kb. Per-noun records are
  vocab-independent -> the v1-noun records are BYTE-IDENTICAL to the 29420 KB (self_test asserts this
  against data/wordnet_noun_semantics_kb_v1/kb.json; 325 records checked). New artifact written to a NEW
  path (data/wordnet_noun_semantics_kb_v2_breadth/kb.json); the v1 artifact is NEVER mutated.

## Test gold (fresh, independent, blind, verb-broad)
data/ud_ewt_semantic_affectedness_gold_v2_breadth/gold.json: 47 UD-EWT sentences, blind annotator (blind
to lexicon + KB), Director-verified; 43 primary rows after 4 ambiguous excluded; ~43 distinct verbs; NO
`met`. Binary affected-vs-not: AFFECTED = {patient, effected, transfer}; NOT-affected = {target_not_affected,
none, negated}. Object-type-dependent cases present (carry/leave/save type-flipping, chase-capture vs
hunt-pursuit, watch/visit beyond met).

## Design-gate (pre-registered bands)
- real_baseline: FROZEN v2 verb-affectedness gate (full_gate baseline), no noun KB; recomputed in-cell on
  the breadth gold.
- can_fail: D=0 (frozen override never fires on the verb-broad set = narrow envelope confirmed) OR delta<=0
  OR a spurious selectional match breaks an affected row OR the scramble control fails to collapse.
- one_variable: KB selectional override on/off (identical negation/phrasal/stative/modal prefix).
- difficulty_on: fresh verb-broad UD-EWT web-text, blind annotator, NO met; frozen rules; verb/noun
  disjoint from v1 tuning.

## Multi-seed + must-fail control
- SEEDS = [7, 13, 17, 23, 29].
- SCRAMBLE (must-fail): frozen positional permutation of the object feature-sets across instances (each
  seed) -> any lift MUST collapse (mean scramble delta near 0), proving the type/animacy SIGNAL is
  load-bearing, not a base-rate artifact.
- BOOTSTRAP: B (full 2000) resamples of the paired (base_correct, kb_correct) rows -> 5th/95th CI on delta.
- STORE fidelity across seeds (sharded additive-map partition; expect 1.0).

## CG-vs-MM PRE-REGISTERED CRITERION (the explicit decision rule)
Let breadth_delta = kb_acc - base_acc on the 43 primary rows; D = number of DISTINCT VERB LEMMAS with net
rescue > 0 (rescued > broken for that lemma) = THE DECISIVE NUMBER; K = 3.
- scramble_collapses := mean_scr_delta <= 0.01 AND (breadth_delta <= 0 OR mean_scr_delta < 0.5*breadth_delta).
- no_regression := breadth_delta >= -0.01 AND total_broken <= total_rescued.
- ci_excludes_zero := boot_lo > 0.
- mechanism_reachable := the frozen override provably fires on its canonical met frame in-run (guards the
  arm-identity bug case: arm-identity is only a WIRING BUG if the mechanism is NOT reachable).
- CG_SUPPORTING_ENTITY_KB : D >= K AND breadth_delta > 0 AND ci_excludes_zero AND scramble_collapses AND
  no_regression AND arms_differ. => verb-broad generalization; SUPPORTS chain-grade.
- MIDDLE_BAND_ENTITY_KB   : D == 2 AND breadth_delta > 0 AND scramble_collapses AND no_regression AND
  arms_differ. => suggestive verb-breadth but below CG bar; stays MEASURED_MECHANISM.
- MM_NARROW_ENTITY_KB     : (D <= 1, incl. D=0 zero-intervention with mechanism_reachable) OR
  (breadth_delta <= 0 without net damage). => narrow envelope (met/contact-class only) CONFIRMED; stays
  MEASURED_MECHANISM (as 29420).
- HARD_FAIL_DESIGN        : (arm-identical AND NOT mechanism_reachable = wiring bug) OR (not
  scramble_collapses) OR breadth_delta <= -0.03 OR total_broken > total_rescued.

HYPOTHESIZED (pre-run, tagged): the frozen override fires only where BASE wrongly KEEPs on a not-affecting
row AND the object type selects a not-affecting frame-compatible sense while VIOLATING all affected senses.
Perception verbs (see/watch/hear/notice/read) may already BASE-force-none (then base is CORRECT on
target_not_affected -> no rescue possible, no opportunity). So D is genuinely uncertain in [0..~6];
breadth_delta ~ 0..+0.08 HYPOTHESIZED; mean_scr_delta ~ 0 HYPOTHESIZED. CAN-FAIL is real (D=0 -> MM narrow).

## CELL-TEMPLATE MANDATORY (measurement + multi-seed control; no heavy fit)
- arms_differ_verified recorded (arm-identity is SUBSTANTIVE here, guarded by mechanism_reachable +
  n_override_opportunities/n_override_fired instrumentation; not a blind AF hard-fail).
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: accuracy on labeled gold, no noise floor
- baseline_in_band: BASE breadth acc in (0.05, 0.95) verified in-run + self_test
- discriminator survives scale: run IS the full breadth eval (all 43 primary rows)
- cardinality_ok: EXPECTED = len(SEEDS) scramble runs + len(SEEDS) store runs; verdict counts them
- calibration_check: default_ok_for_this_regime (VN_GRADED_THRESHOLD 0.35 inherited; selrestr = exact VN strings)
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
- FROZEN-RULES self-test: KB records for v1 nouns BYTE-IDENTICAL to data/wordnet_noun_semantics_kb_v1/kb.json
- selftest non-tautological: leak-probe (permute breadth labels -> KB decision vector byte-identical);
  scramble-degrade behaves; frozen met-override still fires; coverage spot-sample; store fidelity == dict.

## Compute architecture
sequential-CPU, justified: glass-box pass over 43 rows x (2 arms + 5 scramble seeds) + a small FHRR store
over the KB nouns (numpy, N=1024, sharded exact); nltk cached WordNet/VerbNet lookups; wall ~14s. Not a
GPU/batching candidate (no matmul inner loop). Storage: sharded additive-map partition (repr demo) +
no_composition for the metric. Determinism: OMP/MKL/OPENBLAS=1; fixed RNG seeds; no hash()-seeded RNG.
LOCAL foreground; NO queue, NO push, NO remote-persist, NO git add of canonical store, NO hdlab mutation,
NO atom bank (skunkworks VETs after land). ASCII-only, no em-dashes.

## Credit
WordNet (Fellbaum 1998); VerbNet (Kipper-Schuler 2005); Levin 1993; Dowty 1991 proto-patient;
Beavers 2011 affectedness; Paczynski-Kuperberg 2012 selectional pre-activation; v1 entity-KB (atom 29420,
commit 67956a587) frozen; blind breadth gold v2 (Director-verified).
