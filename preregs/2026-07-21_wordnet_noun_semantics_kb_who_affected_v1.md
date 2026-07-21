# Pre-registration: wordnet_noun_semantics_kb_who_affected_v1

Date: 2026-07-21
Author: exp_dev (cell author)
Status: PRE-REGISTERED BEFORE FULL RUN (bands fixed before measurement)

## Prior-work KB check (substrate_query.sh)
Query "wordnet noun semantics animacy entity type hypernym who-affected selectional":
top hit cosine=0.319 = 'selected' (WordNet antonym, not relevant); no genuine dup at cosine>0.30 for a
WordNet noun-semantics / animacy / entity-type KB wired into the affectedness gate. Genuinely novel
(the NOUN side of the selectional match; the VERB side = verbnet_affectedness_lexicon_v1 already exists).

## What this is
Build a VETTED WordNet noun-semantics KB (per-noun animacy + coarse semantic type via first-sense lexname
and hypernym-closure) and wire it into the who-is-affected gate's SELECTIONAL decision, GENERALIZING the
hardcoded-`met` object-animacy path (WSD cell commit 9f31de741) to a KB-backed, for-ANY-verb rule.

This is the ENTITY/NOUN-SEMANTICS lever the read-drives-knowledge loop predicted after word-sense, and
the VET-flagged direction (WSD VET confirmed object-ANIMACY, not frames, drove the `met` rescue). It is
ORTHOGONAL to the in-flight verb-affectedness correction loop (that is VERB affectedness; this is NOUN
semantics; they compose).

## Mechanism (glass-box, no external LLM)
KB (build-time WordNet ingest, materialized to data/wordnet_noun_semantics_kb_v1/kb.json):
- dominant (first) synset per noun lemma -> lexname -> coarse sem_type bucket + a VerbNet-compatible
  selrestr FEATURE set (animate/concrete/location/organization/communication/substance/abstract/...).
- animate = lexname in {noun.person, noun.animal} OR dominant-sense hypernym-closes to
  {person, animal, organism, causal_agent}. Dominant-sense discipline (WordNet over-splits -> first
  sense = most frequent; NOT any-of-top-3, which is the noisy path the v1 inline used).
- runtime = cache lookup with live-WordNet fallback for OOV (self-test asserts cache == live, no drift).

Selectional override (KB arm = BASE arm, Pareto in the force-none direction ONLY):
- BASE = the v2 verb-affectedness gate (full_gate baseline: negation -> phrasal -> stative/light ->
  VerbNet graded lemma-modal). This is the 0.769 real baseline (static, no noun KB).
- KB   = BASE, EXCEPT: when BASE would KEEP (affected) and the verb has 2+ frame-compatible VerbNet
  senses that differ in affectedness, and the parsed OBJECT's KB feature-set SATISFIES a NOT-affecting
  sense's non-subject-role +selrestr while satisfying NO affected sense's +selrestr, override to
  force-none. This can only turn KEEP->NONE (never NONE->KEEP) => Pareto; it CANNOT damage a row BASE
  already gets right on the affected classes except by a spurious selectional match (the risk the
  scramble control tests).
- ONE VARIABLE across arms = the KB selectional override (identical negation/phrasal/stative/modal prefix).

REPRESENTATION (substrate-native, secondary): the KB is also encoded as a sharded additive-map store
partition (noun (x) sem_type, FHRR unit-phasor codebook, N=1024). Retrieve-fidelity == dict KB is
asserted in self-test (sharded => exact) and reported per-seed. The accuracy measurement uses the dict
(identical to the store by the fidelity proof); routing accuracy through cleanup would be over-build with
no decision value (compute-proportionality). This block demonstrates the partition is a real substrate
object, not merely a dict.

## Eval (HELD-OUT, DEPLOYABLE regime = PREDICTED POS/parse, not gold-oracle)
- UD-EWT independent blind-annotator gold (data/ud_ewt_semantic_affectedness_gold_v1/gold.json),
  52 primary binary rows (4 ambiguous excluded). Base = 0.769 MEASURED@scoreboard metrics.
- McGuffey held-out (data/mcguffey_whoaffected_oracle_gold_v2_heldout/gold.json), 38 rows.
- KB never saw either gold (built from WordNet); front-end trained on UD-EWT TRAIN (disjoint from test).
- Pooled N ~ 90 instances. Report per-set + pooled deltas.

## Design-gate (real baseline / can-fail / difficulty-on / one-variable)
- real_baseline: BASE gate 0.769 (static, no noun KB), recomputed in-cell.
- can_fail: KB gives 0 lift (the narrow lever = only meet/reach-class polysemy with a discriminating
  object type; hunt/watch/look already force-none at BASE so no KB gain there) OR regresses (spurious
  selectional match on an affected row) OR the scramble control does NOT collapse (=> base-rate artifact).
- difficulty_on: real UD-EWT web-text + blind annotator + archaic McGuffey; verb/noun DISJOINT from any
  tuning (the KB is WordNet-derived, uniform over all verbs; the rule is not met-specific).
- one_variable: noun-KB selectional override on/off.

## Multi-seed + must-fail control
- SEEDS = [7, 13, 17, 23, 29].
- SCRAMBLE (must-fail, MUST FIRE): permute the noun->feature-set mapping across the KB vocabulary
  (each seed). Re-run the KB arm with the scrambled KB. The improvement MUST collapse (mean scramble
  delta near 0), proving the animacy/type SIGNAL is load-bearing, not a base-rate artifact.
- BOOTSTRAP: B resamples (smoke 200 / full 2000) of the paired per-instance (base_correct, kb_correct)
  over the pooled eval -> 5th/95th percentile CI on the pooled delta.
- STORE fidelity across seeds (sharded additive-map partition; expect 1.0 each seed).

## Bands (declared BEFORE full)
Let pooled_delta = kb_pooled_acc - base_pooled_acc; ud_delta, mcg_delta = per-set deltas;
mean_scr_delta = mean over seeds of scramble pooled delta.
- scramble_collapses := (mean_scr_delta <= 0.01) AND (pooled_delta <= 0 OR mean_scr_delta < 0.5*pooled_delta).
- no_regression := (ud_delta >= -0.01) AND (mcg_delta >= -0.01).
- HARD_PASS_ENTITY_KB: pooled_delta >= 0.03 AND no_regression AND scramble_collapses AND arms_differ
  AND leak_clean.
- HARD_FAIL_ENTITY_KB: pooled_delta <= 0 OR ud_delta <= -0.03 OR mcg_delta <= -0.03 OR (NOT
  scramble_collapses) OR (NOT arms_differ).
- MIDDLE_BAND_ENTITY_KB: 0 < pooled_delta < 0.03 with no_regression AND scramble_collapses (real but
  small lift; N small => report bootstrap CI).

HYPOTHESIZED (pre-run, tagged): pooled_delta ~ +0.03..+0.05 HYPOTHESIZED (McGuffey met h17/h20 = +2 solid
[base KEEPs via contact-0.45; animate obj selects meet-36.3 encounter]; UD met u10 + reach u12/u14 =
+0..+3 parse-dependent); mean_scr_delta ~ 0 HYPOTHESIZED (random feature map cannot systematically select
the encounter/motion sense). CAN-FAIL is real: if reach does not rescue and one affected row regresses,
pooled_delta lands < +0.03 => MIDDLE_BAND.

## CELL-TEMPLATE MANDATORY (measurement + multi-seed control; no heavy fit)
- arms_differ_verified at smoke (base vs kb decision vectors differ)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: accuracy on labeled gold, no noise floor
- baseline_in_band: BASE pooled acc in (0.05, 0.95) verified at smoke
- discriminator survives scale: smoke runs the FULL eval sets (both gold complete; only bootstrap-B and
  scramble-seed count reduced) so the met-rescue discriminator FIRES at smoke (met cases are at
  indices > 14; a truncated smoke would miss them)
- calibration_check: default_ok_for_this_regime (VN_GRADED_THRESHOLD 0.35 inherited; selrestr features
  are exact VerbNet strings)
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
- cardinality_ok: EXPECTED_UNITS = len(SEEDS) scramble runs + 1 KB run + 1 base run per set
- selftest non-tautological: (a) leak-probe permutes gold labels -> KB decision vector byte-identical;
  (b) DEGRADE probe: scramble the KB feature map -> the met rescue reverts (must-fail fires);
  (c) animacy spot-sample matches WordNet ground truth; (d) store retrieve-fidelity == dict.

## Compute architecture
sequential-CPU, justified: pure-python glass-box pass over ~90 gold rows x (2 arms + 5 scramble seeds) +
a small FHRR store over ~120 nouns (numpy, N=1024, sharded exact); nltk VerbNet/WordNet cached lookups;
wall seconds. Not a GPU/batching candidate (no matmul inner loop; the FHRR store is ~120 length-1024
binds). Storage: sharded additive-map partition (representation demo) + no_composition for the metric.
Determinism: OMP/MKL/OPENBLAS=1; fixed RNG seeds; no hash()-seeded RNG. LOCAL foreground; NO queue, NO
push, NO remote-persist, NO git add of the canonical store, NO hdlab mutation, NO atom bank (skunkworks
VETs after land). ASCII-only, no em-dashes.

## Credit
WordNet (Fellbaum 1998); VerbNet (Kipper-Schuler 2005); Levin 1993; Dowty 1991 proto-patient;
Beavers 2011 affectedness; Paczynski-Kuperberg 2012 selectional pre-activation; v1 hand-lexicon +
v2 held-out gate + WSD frame_selectional_v1 (commit 9f31de741) + independent scoreboard_v1.
