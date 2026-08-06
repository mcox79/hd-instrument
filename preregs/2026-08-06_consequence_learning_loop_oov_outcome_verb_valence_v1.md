# Pre-reg: continuous consequence-learning loop for OOV outcome-verb result-valence

Date: 2026-08-06. Status: **PRE-REGISTERED, NOT YET EXECUTED** (spec-only cycle, per FORMALIZE-drill
discipline; a cell-author builds and runs this later). Companion spec (read first -- full brain->organ
map, engine-reuse map, reward-wire verdict, credit-assignment design, bootstrap analysis, WordNet
verdict, corpus data-sufficiency scan): `notes/research_consequence_learning_loop_oov_outcome_verb_
valence_2026-08-06.md`. Supersedes `preregs/2026-08-06_anchor_propagate_oov_outcome_verb_valence_v1.md`
as the PRIMARY direction per explicit USER instruction (that pre-reg remains a standing, buildable
fallback, not deleted).

## What is being built

A multi-pass corpus LEARNING loop that grounds OOV outcome-verb result-valence from real-text
goal-outcome CONSEQUENCE, not from surface structure or a hand-authored propagation channel. Reuses
5 already-validated owned organs verbatim (`hdlab.goal_typing.find_desired_state`/`congruence_
decision`/`lexicon_predict`, `hdlab.verb_lexical_similarity.register_acquired_outcome`, `hdlab.self_
improving_loop.decide_keep_or_revert`'s abstain-band ARCHITECTURE) plus the self-extension loop
family's multi-pass read-mint-reread CONTROL STRUCTURE, plus 3 small new generalizations (window-
scoped Signal A/B, referent-linked credit-target scan, 3-way POS/NEG/NEUTRAL consolidation).

### 1. NEW: `credit_window(goal_sentence, window_sentences) -> Optional[dict]`

Given a `find_desired_state`-firing `goal_sentence` and its window (`goal_sentence` + next `W=3`
sentences, config below):

- `Signal_A = congruence_decision([goal_sentence], window_text)` -- **generalization**: `congruence_
  decision`'s existing `find_actual_state_candidates` call is applied to the CONCATENATED window text
  (not one sentence); logic inside (class-relation, referent-linking) is UNCHANGED.
- `Signal_B = lexicon_predict(window_text)` -- same generalization (window text, not one sentence);
  V2-lexicon membership logic UNCHANGED.
- `teacher_verdict`: `Signal_A` if `Signal_A in {"MET","UNMET"}` and (`Signal_B == Signal_A` OR
  `Signal_B in {"NONE"}`); `ABSTAIN_EPISODE` if `Signal_A not in {"MET","UNMET"}` OR `Signal_B` is the
  OPPOSITE polarity of `Signal_A` (hard disagreement).
- `credit_targets`: scan window tokens for `lemma` where `in_lexicon(lemma,"outcome") is False` for
  ALL of Tier-1/2/3 (i.e. genuinely OOV of the full lexicon including any words already grounded by an
  earlier pass), whose LOCAL CLAUSE referent (via `_np_last_content`, tried at both pre-verb-subject
  and post-verb-object token spans around the verb's own clause boundary, using the SAME `_CB_CLAUSE_
  BOUNDARY`/comma/coordinator splitting `_cb_analyze_outcome_clause` already uses) LINKS (via
  `_referent_links`) to `desired["referent"]` (`find_desired_state(goal_sentence)["referent"]`).
- Returns `None` if `teacher_verdict == ABSTAIN_EPISODE` or `credit_targets` is empty; else
  `{"teacher_verdict": ..., "credit_targets": [...]}`.

### 2. NEW: `consolidate(exposure_counter) -> Dict[str, str]`

Pure function of `{lemma: {"POS": n, "NEG": n}}` -> `{lemma: "POS"|"NEG"|"GROUNDED_NEUTRAL"|"PENDING"}`
per the companion spec Section 4.4's margin rule (`MIN_CONFIRM`, `NEUTRAL_BAND` below). Calls
`register_acquired_outcome(lemma, polarity)` (EXISTING, UNCHANGED API) for POS/NEG only.

### 3. NEW: `run_pass(corpus_sentences, exposure_counter) -> (updated_counter, n_windows_scored, n_newly_grounded)`

One corpus pass: for every `find_desired_state`-firing sentence, compute `credit_window`, accumulate
into `exposure_counter`, run `consolidate` at the END of the pass (not per-window -- consolidation is a
pass-boundary operation, matching the self-extension loop's own read-everything-then-consolidate
per-pass structure). Returns updated counts for the bootstrap-curve report.

### 4. Multi-pass driver (REUSED CONTROL STRUCTURE from `exp_self_extension_loop_v1`/`exp_self_
extension_grounded_realprose_v1`'s read -> gate -> mint -> consolidate -> re-read loop)

Run `run_pass` up to `N_PASSES=3` times over the SAME (excluded, see non-circularity) corpus; stop
early if a pass grounds zero new words (fixed point). Report per-pass: `n_windows_scored`,
`n_newly_grounded_pos`, `n_newly_grounded_neg`, `n_newly_grounded_neutral`, cumulative
`n_lemmas_pending`. This directly measures the bootstrap-outward claim (companion spec Section 5) --
expect `n_windows_scored` to rise pass-over-pass as Tier-3 words feed Signal A.

### 5. Consumer paths: UNCHANGED

`hdlab/goal_typing.py`'s `_verb_classes` Tier-3 sentinel and `congruence_with_lexicon_fallback` both
already consult `ACQUIRED_OUTCOME_VERB_FEATURES` (confirmed by direct code read this session) -- zero
new plumbing on the scoring side.

## Config (pre-registered BEFORE any run, not tuned post-hoc)

- `W = 3` (window = goal sentence + next 3 sentences) -- matches this session's own diagnostic corpus
  scan (companion spec Section 7), not chosen after seeing results.
- `MIN_CONFIRM = 3` (total pos+neg exposures before consolidation is even consulted) -- higher than
  `exp_self_extension_loop_v1`'s `MIN_CONFIRM=2`, given this payload's higher circularity/noise risk
  (a single-mechanism cross-situational tally, not a two-mechanism-per-episode AND-gate at the
  cross-episode level -- the AND-gate already operates WITHIN each episode via Signal A/B agreement, so
  `MIN_CONFIRM` here governs how many AGREED episodes are needed, a stricter requirement than it
  sounds).
- `NEUTRAL_BAND = 0.34` (vote margin `|pos-neg|/(pos+neg)`; below this magnitude -> `GROUNDED_NEUTRAL`
  once `total >= MIN_CONFIRM`; roughly requires a >2:1 skew to call POS/NEG).
- `N_PASSES = 3` (bootstrap cap; early-stop on a zero-new-growth pass).
- `LIGHT_VERB_CANARY` (26 lemmas, drawn directly from this session's corpus-scan top co-occurrences +
  the anchor_propagate note's own light-verb list, union, fixed before running): `be, have, do, say,
  try, look, feel, want, think, make, come, go, find, ask, seem, begin, mean, know, see, tell, get,
  put, take, give, carry, buy`.
- `NOISE_CANARY` (8 lemmas, semantically empty/manner-neutral, NOT drawn from the 36-item eval's own
  vocabulary and not expected to co-occur meaningfully with goal-outcome windows, same convention as
  the anchor_propagate pre-reg's own noise canary): `walk, sit, speak, stand, sigh, glance, nod,
  pause`. None should get confidently consolidated (POS or NEG) via this design.

## Corpora + non-circularity exclusion (CRITICAL, concrete)

**Learning corpus:** `data/corpora/{little_women,anne_of_green_gables,tom_sawyer,wizard_of_oz}/
cleaned/*.clean.txt` (~399K words combined, the SAME 4 novels this session's diagnostic scan measured
-- see companion spec Section 7 for baseline counts to reproduce at build time: 24,831 sentences,
1,641 goal-fire, 848 already-computable windows).

**MANDATORY exclusion (verified this session, not optional):** 34 of the 44 items in `experiments/
data/goal_bearing_modern_eval_v1.jsonl` are drawn from exactly these 4 novels (`little_women` 12,
`anne_of_green_gables` 12, `tom_sawyer` 5, `wizard_of_oz` 5 -- re-derived directly from the live file
this session, not assumed). Build an exclusion mask from every eval item's `line_citation` field
(e.g. `"little_women.clean.txt:~1945-1981"`), expanded `+/- 50` lines (safety margin for the `~`
approximation); drop any learning-corpus sentence whose originating line falls inside an excluded
range, for ALL 4 novels. Assert programmatically at build time that the exclusion mask is non-empty
for all 4 files (fail loud if the line-citation parse comes up empty, rather than silently training on
contaminated passages). This gate is LOAD-BEARING for every accuracy number below -- an unexcluded run
must be discarded, not reported.

**Held-out scoring set:** `experiments/data/goal_bearing_modern_eval_v1.jsonl`'s 36-item OOV subset
(`outcome_in_lexicon: false`; re-derived this session: 23 met / 13 unmet, majority floor `23/36 =
0.6389`, matching the anchor_propagate pre-reg's own count exactly). Scored via the EXISTING, unchanged
`congruence_with_lexicon_fallback` after the learning pass populates `ACQUIRED_OUTCOME_VERB_FEATURES`.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

**Primary metric:** `primary_accuracy` = fraction of the 36 OOV-outcome items where live
`congruence_with_lexicon_fallback` correctly types MET/UNMET vs gold (untyped/abstain = MISS,
coverage-inclusive, same convention as increment 1b and the anchor_propagate pre-reg).

**Learnable subset:** items whose `outcome_verb_lemma` reached `MIN_CONFIRM` AND consolidated to POS
or NEG (not NEUTRAL, not PENDING) by the end of the multi-pass run. Report its own size `N_learnable`
and `learnable_subset_accuracy` separately from the pooled 36-item number, exactly as the anchor_
propagate design reports its content-verb subset.

**HARD-PASS** (ALL of the following):
1. `learnable_subset_accuracy >= 0.75` AND `N_learnable >= 6` (a floor on subset size -- a
   high-accuracy result on 1-2 items is not evidence of a working mechanism; if fewer than 6 of the 33
   unique OOV lemmas ever clear `MIN_CONFIRM` and consolidate to POS/NEG, this gate cannot pass
   regardless of accuracy on however few did, and the honest verdict is `INSUFFICIENT_YIELD`, reported
   as such, not silently rounded up).
2. `primary_accuracy >= 0.60` (beats majority floor `0.6389`... **explicit honest note**: because
   roughly half the 36 items' outcome verbs are light/support verbs this design correctly predicts will
   land `GROUNDED_NEUTRAL` (companion spec Section 7), the pooled 36-item number is NOT expected to
   reach the anchor_propagate design's 0.75 target -- `0.60` is the calibrated bar for THIS design,
   chosen because it still decisively beats increment-1b's measured `0.4444` and represents genuine
   coverage gain over the `0.6389` no-mechanism floor once light-verb-correct-abstention is accounted
   for; report `content_verb_subset_accuracy` (light-verb-excluded, same 17-lemma exclusion list the
   anchor_propagate pre-reg uses) as the fairer secondary number).
3. `light_verb_canary_neutral_rate >= 0.70` (of the `LIGHT_VERB_CANARY` lemmas that reach
   `MIN_CONFIRM`, at least 70% land `GROUNDED_NEUTRAL`, not POS/NEG-locked -- the task's own named
   "crucial payoff").
4. **Non-circularity gates (must ALSO pass or HARD-PASS is void regardless of accuracy):**
   - (a) SCRAMBLE: permute `teacher_verdict` labels across all recorded `(lemma, window)` exposures
     (fixed seed, 5 seeds) BEFORE consolidation; re-run consolidation + scoring.
     `scrambled_primary_accuracy` must fall within `[0.40, 0.60]` (chance-centered band) while real
     `primary_accuracy` clears gate 2. Gap `(primary_accuracy - scrambled_primary_accuracy) >= 0.15`.
   - (b) RANDOM-CREDIT ablation: replace the referent-linked credit-target selection (step `credit_
     window`'s `credit_targets` scan) with a uniformly-random OOV-token choice from the same window
     (fixed seed). `random_credit_accuracy` must be `>= 0.15` BELOW real `primary_accuracy` on the
     learnable subset (using whatever subset the random-credit run itself produces) -- isolates that
     referent-linkage, not mere window co-occurrence, is load-bearing.
   - (c) SIGNAL-A-ONLY and SIGNAL-B-ONLY ablations: drop the AND-gate, consolidate off each signal
     alone. Report `noise_canary_consolidated_count` for each single-signal arm vs the AND-gated
     design's own noise-canary count -- the AND-gated design's canary count must be `<=` each
     single-signal arm's count (dual-signal agreement should never be LESS precise than either alone).
   - (d) EXCLUSION-INTEGRITY assert: programmatically verify zero training-window sentences fall
     inside the excluded line-ranges (re-check post-hoc, not just at construction time).
5. `noise_canary_consolidated_count == 0` (the 8-word `NOISE_CANARY` set, real run, no scrambling).

**HARD-FAIL** (ANY of the following):
- `primary_accuracy <= 0.6389` (does not beat blind majority-class guessing -- repeats increment-1b's
  literal failure mode).
- `scrambled_primary_accuracy` stays within `0.08` of real `primary_accuracy` (no genuine dependence
  on the teacher signal's actual content -- the mechanism would be learning something other than the
  consequence label, i.e. genuinely circular).
- `random_credit_accuracy` stays within `0.08` of real `primary_accuracy` (referent-linking is not
  actually doing the credit-assignment work the design claims).
- `light_verb_canary_neutral_rate < 0.30` (light verbs are getting spuriously POS/NEG-locked from
  noise rather than correctly washing out -- falsifies the design's central structural claim about
  cross-situational balance).
- `noise_canary_consolidated_count >= 2` (anti-drift leak, same severity threshold the anchor_
  propagate pre-reg uses).
- `N_learnable < 3` (`INSUFFICIENT_YIELD` -- the dual-signal AND-gate essentially never fires cleanly
  enough on real narrative windows to ground ANY meaningful number of genuinely novel content verbs;
  report this explicitly as the design's biggest pre-registered empirical risk, per the companion
  spec's own P_deflated discussion, not disguised as a different failure mode).

**MIDDLE-BAND:** `primary_accuracy` in `(0.6389, 0.75)` with `N_learnable` in `[3,6)`, OR gates 1-3
clear but one non-circularity gate is borderline (e.g. `scrambled_primary_accuracy` in `[0.55,0.65]`
-- partial but not full collapse), OR `light_verb_canary_neutral_rate` in `[0.30,0.70)`. Report
honestly, same discipline as increment 1b / the anchor_propagate pre-reg's own MIDDLE_BAND precedent.

## Bootstrap-curve reporting (informational, pre-registered, not a pass/fail gate)

Per-pass (1 through up to `N_PASSES=3`): `n_windows_scored`, `n_newly_grounded_pos/neg/neutral`,
cumulative `n_lemmas_pending`. Falsifiable sub-prediction: `n_windows_scored` should rise pass 1 -> 2
(newly-grounded Tier-3 words feed Signal A) and plateau by pass 3; a FLAT curve (no rise) would
falsify the bootstrap-outward claim in Section 5 of the companion spec and should be reported as such,
not silently omitted.

## Compute architecture

Sequential-CPU. No training, no GPU, no gradient step -- deterministic corpus scan + counting +
threshold consolidation, same complexity class as the anchor_propagate design's WordNet lookups (both
are O(corpus size) + O(vocabulary) glass-box operations). `crlb: n/a` (not a capacity/argmax-noise-
floor cell). `storage_strategy`: `ACQUIRED_OUTCOME_VERB_FEATURES` remains process-local/in-memory,
unchanged. Expected wall time: low minutes (three ~25K-sentence passes over four novels, `find_
desired_state`/`congruence_decision` per-sentence cost already measured cheap in this session's own
diagnostic scan, which completed in well under a minute for a single pass over all 4 novels).

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist)

- `cardinality_ok`: `EXPECTED_N_UNITS` = 3 passes (resumable per-pass via `tools/exp_checkpoint.py`,
  MANDATORY per this repo's multi-unit-cell convention) + 5 scramble seeds + 1 random-credit ablation +
  2 single-signal ablations + 1 noise-canary batch = 12 units minimum.
- `discriminator_reachability`: TRUE -- 36-item binary classification (as the anchor_propagate design
  established), majority floor 0.6389, ceiling 1.0, not saturated by construction.
- `baseline_in_band`: N/A for the primary arm (direct measurement against fixed gold); reference
  baselines (0.6389 majority, 0.4444 increment-1b) are REAL, re-derived from the live eval file and
  `data/exp_grounded_word_acquisition_increment1b_v1/metrics.json` this session, not assumed.
- `arms_differ_verified`: real vs scrambled `ACQUIRED_OUTCOME_VERB_FEATURES` entries must hash-differ;
  random-credit arm's credited-lemma set must differ from the real referent-linked arm's set (assert
  non-identical, same META_RULE_AF-style check this module family already uses).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: fixed integer seeds throughout (no `hash()`-derived seeding, PROT-023/F.5
  compliant); `sorted(set())` discipline for any corpus-sentence ordering that touches a set.
- `progress_logging`: `print_flush` per-pass (3 passes, low minutes -- heartbeat optional given the
  small pass count, but include for consistency with the mandatory cell template).
- `exclusion_integrity_assert`: programmatic, pre-scoring check that zero training-window sentences
  fall inside the eval-passage exclusion mask (Section above) -- fail loud, not silent contamination
  risk. This is the analog of the anchor_propagate pre-reg's `non_overlap_assert`, adapted for
  passage-range exclusion rather than vocabulary-set exclusion (this design's non-circularity risk is
  structurally different: passage overlap, not anchor-vocabulary overlap).

## Cert gate (MANDATORY -- touches production `hdlab/verb_lexical_similarity.py` write-back consumer path)

`python verification/run_certification.py` via `.venv/Scripts/python.exe` BEFORE and AFTER; baseline
to reproduce: 220 passed, 3 skipped (same baseline the anchor_propagate and increment-1b pre-regs both
cite). This design ONLY populates the ALREADY-EMPTY-AT-IMPORT `ACQUIRED_OUTCOME_VERB_FEATURES` overlay
via the EXISTING `register_acquired_outcome` API -- strict ADD; trace any collision with `verification/
test_outcome_valence_goal_congruence.py`'s decisive items before dispatch, same discipline as both
prior pre-regs in this lineage.

## Files to be touched

- `hdlab/goal_typing.py` (EDIT, strict-ADD) -- no changes to existing functions; new module-level
  helpers if the window-generalization is implemented as thin wrappers around `congruence_decision`/
  `lexicon_predict` rather than modifying their signatures (PREFERRED -- keeps the existing single-
  sentence call sites byte-identical, matches this module's own "Tier-N strict ADD" convention
  throughout).
- `hdlab/verb_lexical_similarity.py` -- NO CHANGE (consumes `register_acquired_outcome` as-is).
- `experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py` (NEW) -- the pre-reg'd
  cell: `credit_window`, `consolidate`, `run_pass`, the multi-pass driver, all ablations/controls
  above, resumable-per-pass via `tools/exp_checkpoint.py`, self-test per the mandatory cell template.
  `experiments/exp_grounded_word_acquisition_increment1_v1.py`/`_increment1b_v1.py`,
  `experiments/exp_self_extension_loop_v1.py`/`_grounded_realprose_v1.py`, and `experiments/data/
  goal_bearing_modern_eval_v1.jsonl` LEFT UNTOUCHED (source-of-truth convention, same as every prior
  pre-reg in this lineage).

## Prior-work check (per exp_dev standing discipline)

Direct prior-art, checked against `data/capability_registry.jsonl` and the live repo this session, not
paraphrased from memory: `grounded_word_acquisition_loop_increment1` (`gate_decision: SHELVE`, revival
criteria satisfied by increment 1b, itself HARD_FAILed -- this pre-reg is a FOURTH attempt at the same
revival criterion, now swapping BOTH the signal source (real-text goal-outcome consequence, not
surface structure or WordNet relatedness) AND the loop architecture (multi-pass bootstrap, not a
single deterministic per-lemma lookup) from every prior attempt); `preregs/2026-08-06_anchor_
propagate_oov_outcome_verb_valence_v1.md` (standing sibling design, WordNet-based, not superseded-by-
deletion, explicit fallback if this design's yield proves too sparse); `exp_self_extension_loop_v1`/
`_grounded_realprose_v1` (`REAL_PROSE_SELF_EXTENSION_WORKS`-family validated engine, source of the
multi-pass control-structure and anti-drift PRINCIPLE reused architecturally here, confirmed by direct
code read this session -- no existing `hdlab`-level promotion of the loop-driver itself, so this
increment's `run_pass`/multi-pass driver is genuinely new code, not a duplicate of an already-promoted
organ); `hdlab/self_improving_loop.decide_keep_or_revert` (WIRED, reused architecturally per the
companion spec's honest "pattern not literal call" distinction). No existing `experiments/exp_
consequence_learning_loop*`-equivalent module found (checked this session: no hit for `consequence`
combined with `learning`/`credit` anywhere under `hdlab/`/`experiments/`) -- confirmed genuinely new,
not a duplicate build.
