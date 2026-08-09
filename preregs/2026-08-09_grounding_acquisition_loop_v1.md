# Pre-reg: the closed self-growing grounding loop (`exp_grounding_acquisition_loop_v1`)

Date: 2026-08-09. Status: **BUILT, SELF-TESTED, SMOKE-RUN, FULL-RUN** (this pre-reg is filed alongside
the implementation per the exp_dev "cell + prereg + self-test" contract; the HARD_PASS/HARD_FAIL bands
below were fixed by the closed-loop DESIGN in `notes/research_psych_acquisition_consolidation_loop_
2026-08-09.md` BEFORE the FULL run -- the one genuinely data-derived quantity, `schema_thresh`, is
computed by an explicit calibration formula off the corpus itself, never hand-tuned against the FULL
run's own outcome; see "Adaptive calibration honesty" below for the audit trail).

Director task: "Direction-B build #4" -- wire the already-built-but-never-joined halves (FLAG/credit +
periodic replay/consolidation) into one closed FLAG -> LIBRARY -> CONSOLIDATE -> GUARD -> BANK loop,
per `notes/research_psych_acquisition_consolidation_loop_2026-08-09.md`.

## Prior-work check (per exp_dev standing discipline)

`bash tools/substrate_query.sh "closed self-growing grounding acquisition loop sleep consolidation
false-memory guard"` (run before authoring): top hit cosine=0.333 (`preregs/2026-07-10_grounding_
consolidation_loop_degree_invariant_v1.md`, a DIFFERENT mechanism -- degree-invariant graph
consolidation, not word/construction acquisition), next hits are the 07-28 consolidation-audit and
08-03 grounded-foundation notes already cited by the design drill. **Verdict: no prior cell at
cosine>0.30 builds this specific FLAG->LIBRARY->CONSOLIDATE->GUARD->BANK wiring; genuinely novel
synthesis of two previously-separate, previously-measured halves** (word_acquisition_loop /
consequence_learning_loop's FLAG half; hippocampal_encoder / confidence_gated_codebook's consolidation
SHAPE), exactly as the design drill itself found.

## What is being built

`hdlab/grounding_acquisition_loop.py` (NEW module) + `experiments/exp_grounding_acquisition_loop_v1.py`
(NEW cell). Zero edits to any existing production file (`hdlab/consequence_learning_loop.py`,
`hdlab/goal_typing.py`, `hdlab/verb_lexical_similarity.py`, `hdlab/self_improving_loop.py` are all
imported read-only, called verbatim). No cert gate required (no production file touched).

### FLAG (reused verbatim)
`hdlab.consequence_learning_loop.credit_window` / `teacher_verdict`: an OOV outcome-verb lemma whose
local-clause referent links to the goal's referent, in a window whose structural congruence signal
fires MET/UNMET, is a flag (episode_id=window id, pole=POS-if-MET/NEG-if-UNMET, context=the window
text). `signal_mode="signal_a_only"` (the AND-gate co-fires on ~3 windows total per the parent cell's
own diagnosis -- too sparse to exercise a multi-pass loop; `signal_a_only` is the config the arc's own
prior cell already isolated as the one worth re-testing).

### LIBRARY (new; trace-level, not counter-level)
`Library` / `LibraryItem` / `Trace`: keyed by lemma. Each flagged episode is kept as a SEPARATE
`Trace(episode_id, pole, context_vec, pass_idx)` -- never folded/averaged at intake (Trueswell
propose-verify / the 07-28 audit's core finding). `context_vec` = a deterministic bag-of-content-words
bipolar bundle (`context_vector`, `D=256`, hashlib-seeded per-word draw, PROT-023/F.5-compliant -- no
built-in `hash()`). A terminal item (GROUNDED_*/ESCALATED) accepts no further traces.

### CONSOLIDATE -- the periodic "sleep" pass (new)
`consolidation_pass`, one call per exposure batch, over the WHOLE library (offline, matching
Diekelmann & Born's active-systems-consolidation framing -- separate from the FLAG/reading pass).
For each PENDING item with `>= MIN_CONFIRM` traces:
1. Record `first_min_confirm_pass` the first time the threshold is reached.
2. **Dumay & Gaskell intervening-pass rule**: the item may NOT integrate on the very pass it first
   becomes eligible (`pass_idx <= first_min_confirm_pass` -> skip, no patience cost). Sleep-dependent
   word integration is decoupled from time/repetition-count alone in the human literature; this is
   the literal design requirement, not decoration.
3. On any later pass: compute `schema_consistency_split_half(traces)` (below). If `None` (not enough
   evidence for a split), defer -- no patience cost (insufficient-evidence is not a guard FAILURE).
4. If the score is `>= schema_thresh`: BANK. Vote label = `decide_keep_or_revert({"POS": margin,
   "NEG": -margin}, abstain_band=NEUTRAL_BAND-1e-9)` (byte-identical idiom to
   `consequence_learning_loop.consolidate`); `None` vote -> `GROUNDED_NEUTRAL` (the light-verb
   payoff, not a failure). `GROUNDED_POS`/`GROUNDED_NEG` calls `register_acquired_outcome` (the
   REUSED Tier-3 write-back, unchanged).
5. Else: `patience += 1`; at `patience >= PATIENCE_MAX` (3) -> `ESCALATED` (terminal, logged, NEVER
   written to the overlay). **This REPLACES the un-run v6 design's "forced-commit-after-patience"
   with escalation, per the drill's Warren-et-al-2014-motivated correction** -- an item that cannot
   clear the schema gate is never force-banked under any patience budget.

### GUARD -- `schema_consistency_split_half` (new; the false-consolidation defense)
Split the item's traces into two halves by accumulation order (first half / second half, NOT
shuffled); cosine between the RAW (non-sign-cleaned) sum of each half's context vectors. Returns
`None` if fewer than 2 traces exist per half (`n < 4`).

**Deviation from the drill's literal spec, disclosed:** the drill's design (section 3c) named
`hdlab.hippocampal_encoder.cls_discrete_budget_consolidate` (a full FHRR fast-store/CA3-complete/
concept-codebook consolidation primitive) as the reuse target. That primitive needs a pre-existing
FHRR concept codebook for the CONTEXT space (entities/situations), which does not exist for this
domain (goal-bearing narrative windows) without a substantial separate build. Given the compute-
proportionality discipline (this is a DIRECTIONAL GATE on whether the wiring/loop mechanics work, not
a magnitude-of-mechanism claim) and the Autonomy grant ("the library store format... the confidence/
consistency threshold for the guard" are the cell-author's to set), I substituted a lighter, still
genuinely HD-native (bipolar bind/bundle, deterministic, glass-box) split-half context-coherence
metric that **reuses the SHAPE, not the code,** of `exp_confidence_gated_codebook_consolidation_v1`'s
already-validated split-half reliability signal (there: two independent PPMI builds over disjoint
TOKEN halves; here: two independent context bundles over disjoint TRACE halves). This is flagged
honestly as a scope reduction, not a silent substitution -- `cls_discrete_budget_consolidate`'s
discrete-budget/CA3-complete wiring remains the correct next-scope target if this lighter guard needs
to be hardened.

**Implementation note found during build (not a design change, a bug fix):** the naive bipolar
sign-cleanup convention (zero-tie broken to +1, matching `predictive_coding.py`) injects a
systematic POSITIVE bias into the cosine between two INDEPENDENTLY RANDOM small (2-item) bundles
(~50% of coordinates tie at 0 under only 2 summands, and both sides break the same direction) --
caught by the module self-test (a spurious 0.36 cosine between two independent noise bundles under
sign-cleanup, vs 0.11 under the raw-sum fix). Fixed by using the RAW (uncleaned) sum for this
specific cosine, not `predictive_coding`'s bipolar-cleanup convention (which is correct for producing
a canonical concept symbol, not a smooth reliability score).

**Adaptive calibration honesty (META_RULE_M):** `schema_thresh` is computed by
`calibrate_schema_threshold`: for every corpus lemma with `>=4` credited occurrences (up to 40,
sorted-deterministic), compute its OWN matched split-half cosine and a WRONG-CONTEXT cosine (its
first-half sum against a different, fixed-seed-paired lemma's second-half sum); `schema_thresh =
max(0.03, (matched_mean + wrong_mean) / 2)`. `discriminates: bool = (matched_mean - wrong_mean) >=
0.02` is logged; if `False`, the verdict is forced `MIDDLE_BAND` regardless of downstream gates
("CALIBRATION_DEGENERATE" -- growth/guard results below a degenerate calibration are uninterpretable,
not evidence). MEASURED (FULL, this run): `matched_mean=0.1912, wrong_mean=0.1290,
schema_thresh=0.1601, discriminates=True`.

### CORRECTNESS-WHEN-CHECKED (new gate, added per the Director task's explicit HARD-PASS clause)
Final banked POS/NEG groundings scored via the ALREADY-BUILT, REUSED
`exp_consequence_learning_loop_signal_a_primary_v1._per_verb_grounded_correctness` (byte-identical
import) against `experiments/data/goal_bearing_modern_eval_v1.jsonl`'s 36-item OOV subset (the SAME
eval every prior cell in this arc scores against). `polarity_match_rate > 0.5` (better than a coin
flip) is a SEPARATE, honestly-reported gate -- a MIDDLE_BAND on correctness alone (loop mechanics
sound, correctness inconclusive) is explicitly distinguished from a HARD_FAIL on loop mechanics, per
the flat-result-means-diagnose discipline.

## Corpus / stream

The 4 real, McGuffey-free novels `exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py`
already validated as the corpus (`little_women`, `anne_of_green_gables`, `tom_sawyer`, `wizard_of_oz`,
eval-passage-excluded), split into `N_PASSES=5` sequential, deterministic, corpus-order-preserving
batches (`_split_batches`) -- read one batch, then one offline consolidation ("sleep") pass, repeated,
matching the "read -> sleep -> read -> sleep" design the drill specifies (not 5 independent full
re-reads of the whole corpus).

## Config (mine to set per exp_dev Autonomy grant)

`D=256` (context dim), `MIN_CONFIRM=4` (raised from `consequence_learning_loop`'s 3 -- the
split-half guard structurally needs `>=2` traces per half, so 4 keeps "reached min_confirm" and
"schema-scoreable" coincident; a smaller value would waste patience on merely-under-evidenced items
before the None-defer fix, see build note above), `NEUTRAL_BAND=0.34` (matches
`consequence_learning_loop`), `PATIENCE_MAX=3` (drill's own "start at 3, matching the smallest tested
budget"), `N_PASSES=5` (drill's own K=5), `signal_mode="signal_a_only"`.

## Falsifiable predictions (as implemented; matches the Director task's section verbatim, +1 gate)

**HARD-PASS** (ALL required):
1. Growth: `net_growth >= 3` GROUNDED_* items across the 5-pass run, monotonic non-decreasing,
   zero regression of any prior-grounded lemma's status.
2. Guard: the adversarial wrong-context probe (3 synthetic items, consistent POS vote, genuinely
   mismatched REAL window contexts, fixed-seed-sampled without replacement) must ESCALATE 3/3, ground
   0/3.
3. Escalation sanity: the pure-noise nonsense-token probe (3 synthetic items, random context AND
   random vote) must ESCALATE 3/3, ground 0/3.
4. Correctness: banked POS/NEG `polarity_match_rate > 0.5` against the 36-item eval's grounded-verb
   subset.
5. Calibration must discriminate (`matched_mean - wrong_mean >= 0.02`) -- else forced `MIDDLE_BAND`
   regardless of 1-4 (a degenerate metric makes 1-4 uninterpretable, not evidence).

**HARD-FAIL** (per-gate, diagnosed not lumped -- matches the "diagnose flat, don't conclude ceiling"
discipline): growth flat/non-monotonic/regressing; OR guard grounds >=1/3 adversarial items; OR
escalation-sanity grounds >=1/3 nonsense items; OR calibration is degenerate. **Correctness (gate 4)
failing ALONE, with gates 1/2/3/5 all clearing, is scored `MIDDLE_BAND` not `HARD_FAIL`** -- it
diagnoses the underlying vote/FLAG signal's precision (already known-weak from 4 prior standalone
measurements on this exact eval), not the NEW library/consolidation/guard machinery this cell exists
to test; conflating the two would mis-attribute a base-ingredient limitation to a loop-mechanics
failure.

## Honest prior context (read before interpreting any correctness number)

The vote/FLAG signal this loop's guard sits on top of has HARD_FAILED on the SAME 36-item eval in
every standalone prior attempt: `grounded_word_acquisition_loop_increment1` (SHELVE),
`exp_grounded_word_acquisition_increment1b_v1` (0.4444 vs 0.6389 floor, HARD_FAIL),
`exp_consequence_learning_loop_oov_outcome_verb_valence_v1` (0.1667, HARD_FAIL),
`exp_consequence_learning_loop_signal_a_primary_v1` (0.1944 primary; per-verb
`polarity_match_rate=0.3333` at n=3, BELOW CHANCE). This cell's job is to determine whether the NEW
library/consolidation/schema-guard machinery grows coverage and rejects false consolidation --
cleanly separable from base-ingredient precision, which gate 4 measures honestly and separately.

## Compute architecture

Sequential-CPU. FHRR-adjacent bipolar bind/bundle context encoding (D=256) + the REUSED referent-
linking/congruence machinery (already-wired, zero new cost). MEASURED wall time: self-test ~3s,
smoke (1 novel, 958 windows) 3.6s, FULL (4 novels, 1655 windows, 5 passes + calibration + 2 adversarial
probes) 6.8s -- light compute, run FOREGROUND-TO-COMPLETION per the INLINE-LOCAL-for-light-compute
discipline (not dispatched via any queue). `crlb_n/a`: closed-loop growth/guard-discrimination test,
not an argmax/capacity-noise-floor cell. `storage_strategy`: `Library` is process-local/in-memory
(cross-session persistence out of scope, matching `consequence_learning_loop`'s own scope bound); the
production Tier-3 overlay (`ACQUIRED_OUTCOME_VERB_FEATURES`) is cleared at the end of every run
(hygiene, matches every prior cell in this family).

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist)

- `cardinality_ok`: `EXPECTED_N_UNITS = N_PASSES(5) + 2 adversarial probes = 7`; MEASURED 7/7.
- `discriminator_reachability`: TRUE -- calibration itself is the pre-dispatch discriminator-fires
  check (matched vs wrong-context split-half cosine on real corpus data); MEASURED discriminates=True
  at both smoke (margin=0.062) and FULL (margin=0.062).
- `baseline_in_band`: N/A (this is a mechanism-presence test, not an arm-vs-baseline accuracy cell);
  the closest analogue, correctness gate 4, uses the REAL majority-floor (0.6389) and prior
  signal_a_only pol_match (0.3333) as reported reference baselines, never gated on directly.
- `arms_differ_verified`: the main-run / adversarial-probe / nonsense-probe libraries are 3 distinct
  `Library()` instances with observably different final `final_statuses` content (verified by
  inspection of the printed per-probe status dicts in both smoke and FULL runs, not a formal
  hash-diff -- this cell has no literal "arm comparison," so META_RULE_AF's hash-check is adapted
  rather than applied verbatim; flagged honestly).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: fixed integer seeds throughout (`context_vector` hashlib-seeded per word;
  `calibrate_schema_threshold` / adversarial / nonsense probes use `np.random.default_rng(fixed)`); no
  `hash()` or `list(set())` ordering anywhere (batches are index-sliced from a stable corpus-order
  list).
- `progress_logging`: `print_flush_true` (every pass + probe prints; wall time under 10s regardless,
  well under the `timeout_s >= 1800` threshold that makes this mandatory, included anyway).
- `real_code_path_exercised`: self-test constructs REAL `Library` / `consolidation_pass` /
  `credit_window` / `calibrate_schema_threshold` objects against a REAL corpus slice (250 real
  windows from `little_women`), not a synthetic-only branch; MEASURED PASS.

## Cert gate

N/A -- no production file edited (see "What is being built" above). No `verification/
run_certification.py` re-run required.

## Files touched

- `hdlab/grounding_acquisition_loop.py` (NEW).
- `experiments/exp_grounding_acquisition_loop_v1.py` (NEW).
- `preregs/2026-08-09_grounding_acquisition_loop_v1.md` (this file, NEW).
- No existing file edited.

## Director land-decision (deferred, per task contract)

This cell is NOT wired into any default/production path. Director/Skunkworks VET decides WIRE vs
SHELVE vs iterate; this pre-reg + the metrics at `data/exp_grounding_acquisition_loop_v1/metrics.json`
and `data/grounding_acquisition_loop_v1_smoke/metrics.json` are the record to VET against.
