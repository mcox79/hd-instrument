# Pre-registration: event-outcome-density patient-signal probe v2 -- POWER FIX (design-gate + smoke, n=1)

Cell: `experiments/exp_event_outcome_density_patient_signal_probe_v2.py`
Author: hdi_exp_dev. Date: 2026-07-20. DESIGN + SMOKE ONLY -- no full run, no queue_add, no push.
Spec sources:
- Director spawn prompt (2026-07-20): "properly-powered, capacity-controlled EVENT-OUTCOME-DENSITY probe";
  explicit fairness gate ("do NOT recommend a full run unless the fairness guards demonstrably hold at
  smoke").
- `notes/research_brain_building_event_plausibility_web_2026-07-20.md` (sections b/c: the cheap decisive
  test recipe + falsifiable HARD-PASS/HARD-FAIL predictions).
- `notes/research_plausibility_web_engineering_resources_adoptable_foundation_2026-07-20.md` (section 3:
  the fair high-powered recipe; ROCStories/BabyLM-gap framing; Chambers-Jurafsky as a label-free method).
- `preregs/event_outcome_density_patient_signal_probe_v1.md` + `data/exp_event_outcome_density_patient_
  signal_probe_v1/metrics.json` (the prior FAIR-but-power-starved probe: n_multi=21, SE~0.108-0.109, gap
  exactly 0.0000 -- uninformative, not a refutation).

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `bash tools/substrate_query.sh "event
outcome density patient signal corpus reporting bias affectedness pseudo-disambiguation power"` ->
confidence=0.2881, top hit cosine=0.2881 (generic WordNet/VerbNet "patient" entity + an unrelated
P3-v2-hybrid-criterion note). NONE at cosine>0.30 -- no prior arc cells on this exact concept; genuinely
novel, not a rediscovery.

## ROOT-CAUSE DIAGNOSIS (measured this cycle, not assumed)
Growing the BACKGROUND corpus does NOT fix v1's power problem. v1's own TEXT8_XGENRE reference arm
already used 74,000 background tokens (8x the primary tiers) and produced the IDENTICAL 0.3810 pick_gold
rate, bit-for-bit tied with the 9K-token arms. The bottleneck is the EVAL side: pick_gold is a Bernoulli
rate over n=21 independent trials; SE ~ 1/sqrt(n) regardless of background size. Confirmed by reading
`data/gold_mcguffey_lccp_argstruct_v1.json` this cycle: only 7 of the McGuffey Third Reader's 79 lessons
are hand-annotated (100 pos instances, 57 reader-scoreable, 21 multi-candidate). Expanding that is a NEW
hand-annotation labor task (not attempted this cycle), not a corpus fetch.

## THE FIX: label-free Chambers & Jurafsky-style pseudo-disambiguation (PRIMARY discriminator)
For every occurrence of a Levin causative-inchoative verb in the 72-of-79 Third Reader lessons NEVER used
in the hand-gold set, the OBSERVED adjacent noun IS the "true" patient (no semantic judgment needed --
classic label-free pseudo-disambiguation: corpus occurrence itself defines ground truth). MEASURED this
cycle: n=110 credited (verb, true-patient) instances (~5x the n=21 hand-gold multi-candidate trials),
achieved with ZERO new data fetch and ZERO new annotation. Corrupted competitor = another instance's true
patient (fixed-seed near-derangement, no self-pairing). Score = argmax(true, corrupt) under the arm's
density-informed prior; accuracy vs chance=50%.

The original n=21 LCCP hand-gold pick_gold rate is RETAINED as a SECONDARY / legacy continuity check
(reproduced verbatim via `V1.build_eval_instances`/`V1.score_arm` -- Gate D positive-control reproduction:
MEASURED@data/exp_event_outcome_density_patient_signal_probe_v2_smoke/metrics.json:v1_replication_block
reproduces v1's exact LOW=MED=HIGH rate_multi=0.3810, n_multi=21, bit-identical to v1's own metrics.json).

## ARMS / GENRE-CONFOUND CONTROL
PRIMARY comparison stays WITHIN the McGuffey graded-reader series (Primer/First/Second/Fourth Reader
non-eval background; Third Reader excluded, it is the eval corpus for both discriminators) -- option (a)
of the fairness-guard menu (within-source density stratification), the only option achievable with ZERO
new data this cycle. TEXT8_XGENRE / LITBANK_XGENRE cross-genre reference arms from v1 are NOT re-run in
v2 (the in-genre CJ probe is the power fix; cross-genre framing already showed a null in v1 at 74K tokens).

**Residual confound found + reported honestly (not hidden):** density is NOT independent of lesson
length/register even WITHIN the McGuffey series. MEASURED this cycle: the bottom density-ranked 83 lessons
(all density=0.0 exactly, a real floor not "low-but-nonzero") average only ~110 tokens/lesson (Primer/
First-Reader-style short simple sentences), while high-density lessons average 250-450 tokens/lesson
(longer Second/Fourth-Reader narrative prose). The bigram-perplexity diagnostic (see below) confirms HIGH
backgrounds are measurably more perplexing than LOW at every capacity tier (ratio ~1.3-1.9x). So "within-
genre" bounds the confound (same author/era/series) but does NOT eliminate a residual reading-level/
complexity coupling. This is exactly the risk the patient-specific diff-in-diff control below is designed
to catch.

## CAPACITY TIERS (BabyLM-style fixed-budget; MEASURED corpus-availability ceiling, not guessed)
Direct cumulative-token measurement this cycle over the full non-eval pool (73,451 scoreable tokens / 248
lessons): the bottom 83 lessons by density rank are ALL density=0.0 (9,103 raw tokens -- the ceiling for a
"pure zero-density LOW arm" at ANY budget without diluting LOW's density upward). HIGH has abundant
headroom (top 41 lessons alone = 10,112 tokens at density>=16.5). Capacity tiers = FIXED TOKEN BUDGETS
{3000, 6000, 9000}: LOW_B = bottom-ranked lessons (rank order, NOT the full pool shuffled-then-truncated --
a bug caught and fixed during authoring, see BUGS FOUND below) prefix-selected to budget B; HIGH_B =
top-ranked lessons, same procedure. The v1 tercile LOW/MED/HIGH design (~9.1-9.5K tok/arm) is retained
verbatim as a flagship replication-continuity block.

## DENSER-!=-EASIER CONTROL (general-syntax analog; no BLiMP fetch needed)
The SAME mechanism is run on the AGENT slot of the same held-out transitive-use instances (true preceding
subject vs corrupted swap; n=48 trials), scored under the AFF-ONLY component (patient_affinity alone, no
animacy term -- isolates exactly the density-dependent piece). `patient_affinity` is a theory of "seen as
an affected argument", not of agency; HARD-PASS requires density to help PATIENT discrimination
specifically and not (or much less) AGENT discrimination. `patient_specific_gap` = (patient_aff_HIGH -
patient_aff_LOW) - (agent_aff_HIGH - agent_aff_LOW); must be >= 0.05 at every tier for HARD-PASS, and a
value <= 0 at ANY tier is an independent HARD-FAIL trigger (agent-slot benefiting as much or more =
"denser text = generically easier to guess any salient noun", not "more event content").

## PERPLEXITY NUISANCE-COVARIATE DIAGNOSTIC
A closed-form add-1 bigram LM fit per background arm (LOW_B/HIGH_B), evaluated on the same held-out eval
sentences. Reported as a DIAGNOSTIC (not a full regression -- too few arms/tiers for a real slope fit at
this compute-proportional scale); the patient-vs-agent diff-in-diff above is the actual mechanism doing
the "controls for generic difficulty" work.

## MUST-FAIL CONTROL: BUG FOUND + FIXED (load-bearing, report this prominently)
v1's `compute_patient_prior(text, scramble_seed=X)` permutes the ORDER of a flat list of credited noun-
tokens BEFORE tallying (`credited = [credited[j] for j in perm]`, then `counts[n] += 1` for n in
credited). Tallying occurrence counts is order-invariant, so this permutation is a **mathematical NO-OP**:
the resulting counts dict is IDENTICAL to the unscrambled one at every corpus scale, by construction.
CONFIRMED empirically this cycle: with v1's original mechanism, HIGH vs HIGH_SCRAMBLED choice-hashes were
BIT-IDENTICAL (0/110 trials differing) at all 3 capacity tiers. v1's own pre-reg observed this same tie
("HIGH_vs_HIGH_SCRAMBLED: False ... at this small n") and attributed it to sample size -- **that
attribution was wrong; it is structural, not a small-n coincidence.** Because the must-fail gate as coded
could never fire differently from real HIGH at ANY scale, it was a VACUOUS control (a can't-fail
discriminator on the control axis specifically) -- exactly the design-gate failure mode this project's
own discipline says is "worse than idle."

**Fix (implemented in v2, `scramble_prior_table`):** draws a fixed-seed derangement over the SET of
DISTINCT credited noun-TYPES and reassigns each type's count to a different type (preserves total hit
count + the corpus-wide count DISTRIBUTION/multiset + vocabulary size; destroys which SPECIFIC noun owns
which count). Verified in `self_test()`: at budget=9000, the fixed control changes 33/110 trial choice
outcomes (vs 0/110 for v1's original mechanism) -- the control genuinely functions now. This does NOT
overturn v1's own HARD_FAIL verdict (v1's gap was independently already 0.0000, below its 0.03 floor
regardless of the control bug) but the gate itself was broken and is now fixed for v2 and flagged for any
future reuse of `V1.compute_patient_prior`'s `scramble_seed` parameter elsewhere.

## PRE-REG BANDS (envelope-fail-bands; PRIMARY = CJ patient-slot full-score, gate applies at EVERY tier)
- HARD_PASS_DENSITY_IS_THE_LEVER_V2: at ALL 3 capacity tiers, acc(HIGH_B)-acc(LOW_B) >= 0.08 AND
  acc(HIGH_B)-acc(HIGH_SCRAMBLED_B) >= 0.05 AND patient_specific_gap >= 0.05 AND baseline_in_band
  (0.05 < acc(LOW_B) < 0.95).
- HARD_FAIL_DENSITY_NOT_THE_LEVER_V2: gap < 0.03 at ANY tier, OR HIGH_SCRAMBLED within 0.03 of real HIGH
  at ANY tier, OR patient_specific_gap <= 0 at ANY tier.
- MIDDLE_BAND_V2: partial (between the bars).

## SCHEMA-VET fields
- cardinality_ok: N/A (fixed arm set per tier, no continuous sweep-cardinality risk).
- arms_differ_verified: choice-hash diffs MEASURED -- LOW vs HIGH differ at 69-71/110 positions (mechanism
  fires strongly on individual trials even though aggregate rate barely moves); HIGH vs HIGH_SCRAMBLED
  (post-fix) differ at 25-33/110 positions depending on tier (control genuinely exercises now).
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (grep-verified: no bare except / no except BaseException).
- crlb_n/a: corpus-count + pairwise-comparison measurement, no matmul noise floor.
- baseline_in_band: TRUE at every tier (acc(LOW_B) = 0.409, in (0.05,0.95); chance=0.50 so this also
  sanity-confirms the task is a real (not saturated) binary discrimination).
- calibration_check: default_ok_for_this_regime (score formula / animate_discount / MIN_COUNT fixed before
  looking at eval accuracy, reused verbatim from v1; not tuned to the result).
- deterministic seeding: fixed int seeds only (`np.random.default_rng(int)`), no builtin hash(), no
  `list(set(...))` ordering dependence; grep-verified.
- Compute architecture: class (b) sequential-CPU, JUSTIFIED (corpus counting + pairwise comparison over
  <=200 trials x 3 tiers; wall MEASURED ~17-19s smoke). No queue dispatch (local foreground measurement).
- run_mode: explicit flag required (self_test|smoke|full); no silent default.

## SMOKE RESULT (MEASURED@data/exp_event_outcome_density_patient_signal_probe_v2_smoke/metrics.json)
Held-out CJ pool: 72 lessons / 21,988 tokens / 110 patient trials / 48 agent trials.
Density confirmed ON at every tier: LOW=0.0 vs HIGH in {27.64, 23.98, 21.84} hits/1000tok (budgets
3000/6000/9000).
CJ patient-slot full-score accuracy: LOW=0.409 (all 3 tiers); HIGH={0.418, 0.436, 0.436}.
gap(HIGH-LOW) = {0.0091, 0.0273, 0.0273} -- well below the 0.08 HARD_PASS bar at every tier; analytic
binomial SE at n=110, p~0.42 is ~0.047, so even the largest gap (0.027) is well under 1 SE.
gap(HIGH-HIGH_SCRAMBLED, post-fix) = {0.0, 0.0091, -0.0091} -- noise-scale, sign-flipping across tiers;
real HIGH is statistically indistinguishable from the (now genuinely randomized) scrambled control.
patient_specific_gap (patient diff-in-diff minus agent diff-in-diff) = {-0.0182, -0.0117, -0.0117} at
every tier -- NEGATIVE throughout: the agent-slot control benefits AS MUCH OR MORE from density than the
patient slot does, the exact "denser text = generically easier to guess any salient noun" signature, not
"denser text = more event/outcome content."
gap_ok_all_tiers=False, scr_ok_all_tiers=False, baseline_ok_all_tiers=True, specificity_ok_all_tiers=False.
VERDICT: HARD_FAIL_DENSITY_NOT_THE_LEVER_V2 (both the primary-gap criterion AND the specificity criterion
independently trigger fail).
v1 legacy/secondary block reproduces exactly: LOW=MED=HIGH rate_multi=0.3810, n_multi=21 (Gate D pass).

## HONEST BOUND + DATA-DEPENDENCY STATUS (stated plainly, per the design-gate discipline)
n=110 (SE~0.047) is a genuine, ~5x, ZERO-NEW-DATA power improvement over v1's n=21 (SE~0.108) -- enough to
rule out LARGE effects (>~0.10) with reasonable confidence, but NOT enough to fully resolve the 0.03-0.08
MIDDLE_BAND range. The measured gaps (0.009-0.027) sit inside that still-ambiguous-if-taken-alone zone --
but the INDEPENDENT patient_specific_gap check (negative at every tier) and the must-fail control (noise-
scale, sign-flipping) both point the SAME direction (no affectedness-specific signal), which is why this
reads as a clean, multi-tier-corroborated HARD_FAIL rather than an inconclusive MIDDLE_BAND.
Residual, non-eliminated fairness risk: density and reading-level/lesson-length are coupled even WITHIN
the McGuffey series locally (confirmed via bigram perplexity: HIGH backgrounds are 1.3-1.9x more
perplexing than LOW at every tier). ROCStories (or another purpose-built, register-controlled dense-vs-
sparse pair) is the clean way to fully decouple density from register/complexity -- NOT stageable locally
this cycle (no fetch attempted; explicitly flagged as the full-run data dependency, per task instructions).
Expanding the hand-annotated gold set (more Third-Reader lessons, or a new corpus) would further shrink SE
on the LEGACY discriminator specifically -- a labor task, not attempted this cycle.
