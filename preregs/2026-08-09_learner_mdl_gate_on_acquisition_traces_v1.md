# Pre-reg: exp_learner_mdl_gate_on_acquisition_traces_v1

**Filed-by:** exp_dev, 2026-08-09.
**Hand-off:** notes/exp_dev_handoff_research_brain_script_acquisition_consolidation_2026-08-09.md,
anchor 1 (`exp_learner_mdl_gate_on_acquisition_traces_v1`). ANCHOR 1 ONLY -- anchors 2 and 3 are
strictly out of scope for this cell/prereg (research-fixed sequencing).

**Prior-work check (SUBSTRATE-KB, MANDATORY per exp_dev core discipline):**
`bash tools/substrate_query.sh "MDL compression gate schema commit consolidation learner ruleind
acquisition trace"` and a second phrasing `"MDL two-part code compression gate schema commit
acquisition consolidation"` both return top hits at cosine 0.36-0.43, but every hit is a generic
WordNet/concept-atom node (`compression`, `consolidation`, `election_commission` -- a same-string
false-positive) or one unrelated infra note (`consolidation_to_structure_implementable_algorithm_
2026-07-14.md`, a general note about consolidation-as-structure, not this specific MDL-gate wiring).
No prior EXPERIMENT CELL or pre-reg matches this design at cosine>0.30. Verdict: genuinely novel
wiring, not a rediscovery.

## What this tests

Whether `hdlab.learner`'s already-built MDL two-part-code compression gate (`per_cluster_gate` /
`mdl_select`, Perfors & Tenenbaum 2009) adds real discriminating power over
`hdlab.grounding_acquisition_loop.py`'s currently-wired `schema_consistency_split_half`-only
consolidation guard, when wired in as a CONJUNCTIVE (AND, never OR) second condition. Both organs
already exist, tested, independently wired to other cells -- this is a pure integration/measurement
question (zero new grain, zero new corpus per the hand-off).

Operationalizes Ghosh & Gilboa (2014)'s "non-specific/abstracted structure" schema-commit criterion:
the current guard only checks context CONGRUENCY (cosine coherence across trace halves); it never
checks whether a genuinely COMPRESSIBLE structural regularity exists across the item's evidence.
The MDL gate is a second, independent operationalization of that same underlying construct via a
different mechanism (discrete axis-aligned rule-induction compression vs. smooth cosine coherence).

## Design (exp_dev-owned specifics)

### 1. The adapter (`hdlab.learner.plugins.ruleind_plugin` over `LibraryItem.traces`)

`Trace` has exactly one label-bearing field (`pole: "POS"|"NEG"`) and one evidence field
(`context_vec`: 256-dim bipolar `np.ndarray`). The adapter:

- `episodes`: one dict per trace, `{"gold_class": trace.pole, "id": trace.episode_id, "vec":
  trace.context_vec}` -- `gold_class` is the ONLY label field `RULEIND.induce_rules` requires, and
  `pole` is the only label `Trace` carries; this is the direct, unforced mapping.
- `features` (feat_fn): `p{k}:{+|-}` for k in 0..7, the sign of the context vector's dot-product
  against 8 FIXED, deterministic (hashlib-seeded) random hyperplane projections (LSH-style coarse-
  graining of the 256-dim context vector). **This is NOT the first design tried** -- see the
  "Amendment" section below: a dense per-raw-dimension encoding (`d{i}:{+|-}` for all 256 dims) was
  tried first and FAILED the mandatory pre-check (section below) because it makes induce_rules' own
  rule-cost term (the bits needed to specify which of ~2000+ candidate rules was picked) exceed the
  achievable entropy savings for any realistically-sized item, including a perfectly-separable
  positive control. The 8-projection coarse-graining is the corrected design, used everywhere in
  the cell (pre-check, guard-invariant re-test, real-corpus measurement) -- one feature-space
  definition throughout, no per-context special-casing.
- `key_fn`: `lambda ep: ep["id"]` (residual-lookup key; not load-bearing for the gate decision
  itself, only for `build_residual_lookup`, which `ruleind_plugin.learn` always builds).
- Called via `hdlab.learner.registry.learn(episodes, feat_fn, {"candidate_plugins": ["ruleind"],
  "key_fn": key_fn, "min_compression_ratio": 1.0})` -- literally the call shape the hand-off names.
  `min_compression_ratio=1.0` is the existing `per_cluster_gate` default (hand-off's suggestion);
  not tuned.
- Gate = `chosen_plugin_name == "ruleind"` (registry.learn returns `KEEP_EPISODIC` when
  `per_cluster_gate` rejects the only candidate plugin -- equivalent to calling `per_cluster_gate`
  directly, but exercises the real top-level integration surface named in the hand-off).

**Documented MDL edge case (not a bug):** when an item's traces are label-homogeneous (100% POS or
100% NEG pole), the null (no-model) code already costs 0 bits -- there is nothing left to compress,
so `per_cluster_gate` trivially returns True for ANY non-empty rule/default-clause output regardless
of context structure. This is mathematically correct MDL behavior (Perfors & Tenenbaum's null code
IS the entropy of the label multiset), not an adapter flaw. The gate is only NON-trivially exercised
on items with genuine label entropy (a minority-dissenting trace, or a GROUNDED_NEUTRAL-bound mixed-
vote item) -- the real corpus (see below) produces both. This is flagged explicitly because the
mandatory guard-invariant re-test below (adversarial/scrambled item, homogeneous POS pole in the
existing self_test fixture) will show `mdl_alone=True` for exactly this reason; the guard invariant
is nonetheless PROTECTED because AND-conjunction with the schema check (independently near-zero on
scrambled context) structurally cannot be weakened by a permissive MDL signal -- see "guard
invariant" section below.

### 2. Wire point (`hdlab/grounding_acquisition_loop.py::consolidation_pass`)

Added an optional `mdl_gate_fn: Optional[Callable[[LibraryItem], bool]] = None` parameter. When
provided, consulted ONLY on passes where `schema_score >= schema_thresh` already holds (mirrors the
hand-off's literal instruction: "at the point schema_score >= schema_thresh is currently checked,
ALSO fit ruleind_plugin ... BANK only if BOTH"). A False `mdl_gate_fn` verdict is treated identically
to a schema failure (patience increments, no forced commit -- consistent with the module's existing
"escalate-don't-force-commit" design). Default `None` reproduces the exact prior code path
byte-for-byte (verified: `hdlab/grounding_acquisition_loop.py`'s own `self_test()` and
`experiments/exp_grounding_acquisition_loop_v1.py --self-test` both re-run clean, unchanged, after
this edit -- zero regression).

### 3. Dataset (exp_dev choice, justified)

The hand-off names either `data/exp_unified_self_learning_loop_v6_replay_consolidation_smoke` (a
DIFFERENT, unrelated `unified_self_learning_loop_v6` cell -- checked: it operates on a different
Library/consolidation shape entirely, not `grounding_acquisition_loop.LibraryItem`, so it cannot
supply the `Trace`-shaped input this adapter needs) OR "the loop's own self_test items" (only 2
informative fixtures: `mendtest` coherent, `adversarialtest` scrambled -- correct for the mandatory
guard-invariant re-test, but too thin for a meaningful 2x2 confusion table).

**Choice:** the ALREADY-LANDED `experiments/exp_grounding_acquisition_loop_v1.py` smoke corpus
(`SMOKE_NOVELS = little_women.clean.txt` only, `n_passes=5, min_confirm=4, patience_max=3,
neutral_band=0.34, signal_mode="signal_a_only", seed=0` -- identical config to the cell already
landed today at `data/grounding_acquisition_loop_v1_smoke/metrics.json`, verdict=MIDDLE_BAND,
338 library items, terminal breakdown `{PENDING:308, GROUNDED_NEUTRAL:20, GROUNDED_POS:4,
GROUNDED_NEG:3, ESCALATED:3}` -- MEASURED@d:/AI/hd-instrument/data/grounding_acquisition_loop_v1_smoke/metrics.json).
This IS "the existing dataset" in every meaningful sense: it is the real, already-run,
already-validated corpus that produced the CURRENT (schema-only) system's actual behavior, it
reproduces via the exact same verbatim-reused `flag_batch` + `calibrate_schema_threshold` helpers
(wire-don't-island, no reimplementation), and unlike the hand-picked self_test fixtures it contains
genuine label diversity (`GROUNDED_NEUTRAL` items are, by construction, mixed-vote -- non-degenerate
MDL-test cases; a minority-dissenting-trace item inside a POS/NEG bucket is also non-degenerate).
Compute-proportionality: this is the SAME scope the reference cell already validated as fast
(elapsed_s=3.57 measured) -- no new corpus scale manufactured for this diagnostic question.

### 4. Report shape

Per the hand-off's mandatory contract: for each (lemma, pass) at which the item first becomes
schema-eligible (mirrors `consolidation_pass`'s own `n>=min_confirm AND pass_idx>first_min_confirm_
pass` eligibility, computed read-only, cross-validated against the REAL `consolidation_pass` call's
`newly_grounded_*` lists every pass as a self-consistency assertion) -- record `schema_alone`,
`mdl_alone`, `conjunctive_would_bank`, whether the conjunction changes the verdict relative to
CURRENT (split-half-only) behavior. Aggregated into a full 2x2 confusion count, not just a pass/fail
tally. A second, independent full end-to-end trajectory (`mdl_gate_fn` actually wired in) is also
run to observe the real, fully-wired conjunctive system's own growth curve / final status, as a
second angle beyond the shadow-scored table.

## MANDATORY pre-check (flat-result-means-diagnose discipline)

Before accepting any "MDL never changes a verdict" result as a real MIDDLE_BAND: hand-construct a
maximally-compressible synthetic trace set (n_per_class POS traces with `context_vec = np.ones(D)`,
n_per_class NEG traces with `context_vec = -np.ones(D)` -- perfectly separable, non-degenerate
entropy since labels are NOT homogeneous) and assert `per_cluster_gate` fires True. This proves the
adapter plumbing (episodes/features/registry.learn/per_cluster_gate) genuinely CAN detect real
compressible structure, not merely pass vacuously on the zero-entropy edge case described above. A
complementary informative-only (non-asserted) control -- same trace count, independent random-noise
context vectors with mixed labels -- is also run and reported. **See the Amendment section below:**
this pre-check FAILED on its first implementation (dense 256-raw-dim features, n_per_class=4) and
the fix it forced (coarse 8-projection feature space, n_per_class=8) is exactly this discipline
doing its job -- caught before any real-corpus result was trusted.

## MANDATORY guard invariant

Re-run `hdlab/grounding_acquisition_loop.py::self_test`'s own coherent (`mendtest`) and adversarial
(`adversarialtest`) fixtures, byte-identical construction (same seeds, same `min_confirm=3,
schema_thresh=0.10, patience_max=3`), with `mdl_gate_fn` wired to the adapter. HARD-FAIL condition:
`adversarialtest` (scrambled, wrong-context, but vote-consistent) reaches any `GROUNDED_*` status
under the conjunctive gate. Structural argument for why this is expected to hold regardless of the
MDL signal's own behavior on this fixture: AND-conjunction means the schema-consistency check
(already independently near-zero for scrambled/adversarial context in this fixture, per the
module's own self_test assertion `abs(scrambled_score) < 0.35`) remains a NECESSARY condition that
cannot be relaxed by a permissive (or even trivially-True) MDL signal -- see the documented MDL edge
case above.

## Pre-registered bands (verbatim from the hand-off, exp_dev may not loosen)

- **HARD-PASS**: the conjunctive gate changes at least one verdict relative to split-half-only on
  the existing item set AND all of `self_test`'s existing coherent/scrambled/adversarial invariants
  still hold under the new gate (zero regressions on the guard's hard invariants).
- **MIDDLE_BAND**: the conjunctive gate never changes a verdict on the CURRENT item set (may be
  underpowered, not necessarily a negative on the mechanism -- proceed to anchor 3's richer corpus
  before concluding the two signals are redundant) but all guard invariants still hold.
- **HARD-FAIL**: any coherent/scrambled/adversarial self-test invariant breaks under the new gate
  (the MDL gate creates a NEW false-consolidation path) -- the guard's one hard invariant, never
  excused by "the gate is more principled in theory."

## SCHEMA-VET / cell-template fields

```yaml
cell_chunked: false   # single-shot cell, not multi-seed; 2 "arms" (schema_only, conjunctive)
                       # checkpointed via tools/exp_checkpoint.py per CLAUDE.md multi-unit rule
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: "n_a_under_15min_runtime"   # expected wall time ~10-30s; well under the
                                                 # >=15min heartbeat-mandate threshold (SCHEMA-VET #13-D)
progress_logging: "print_flush_true"
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
deterministic_seeding: true   # fixed int seeds only (0, 1, 777); np.random.default_rng; no hash()
arms_differ_verified: true    # schema_only vs conjunctive trajectories are independent Library()
                               # instances with independently-driven consolidation_pass calls
crlb_n_a: "diagnostic gate-comparison cell, not an argmax/capacity-noise-floor cell"
baseline_in_band: n_a         # not a baseline-vs-mechanism accuracy sweep; paired-signal comparison
discriminating_fraction: n_a  # not a swept-parameter cell (gate B does not apply)
composition_edges:
  - from: schema_consistency_split_half
    to: hdlab.learner.registry.learn (ruleind plugin)
    A_natural_output_shape: "Optional[float] cosine in [-1,1] or None (under-evidenced)"
    B_natural_input_shape: "episodes: list[{gold_class,...}], feat_fn: ep->list[str]"
    verdict: SHAPE_MISMATCH_adapter_traces_to_episodes   # the adapter documented in section 1 above
positive_control_arms:
  - arm: MDL_GATE_MAXIMALLY_COMPRESSIBLE_PRECHECK
    primitive: per_cluster_gate / mdl_select
    cited_prior_atom: "hdlab/learner/core.py per_cluster_gate (banked, exp_learner_module_refactor_proof_v1)"
    test_regime: "hand-constructed 8-trace perfectly-separable synthetic item, this cell's own construction"
    tolerance: "boolean must be True (not a numeric-tolerance check)"
    if_outside_tolerance: HARD_FAIL_PLUMBING_BROKEN_BEFORE_ANY_MIDDLE_BAND_ACCEPTED
    regime_extension_audit: SHAPE_MATCH   # ruleind_plugin's own (episodes,feat_fn) contract, unchanged
real_code_path_exercised: [Library, consolidation_pass, "registry.learn(ruleind)", credit_window,
                           schema_consistency_split_half]
substrate_signature_checked: [consolidation_pass, "registry.learn"]
guard_baseline_validated: n_a   # not a control-beats-baseline break-guard cell (gate F.4 does not apply)
functional_requirements:
  - requirement: "does a genuinely compressible structural regularity exist across an item's evidence"
    primitive: "hdlab.learner.core.per_cluster_gate (MDL two-part code, Perfors & Tenenbaum 2009)"
  - requirement: "does the item's context congruency alone already suffice (current behavior)"
    primitive: "hdlab.grounding_acquisition_loop.schema_consistency_split_half (unchanged)"
```

## Compute architecture

Class (b) sequential-CPU. Per-item `registry.learn` fits are tiny (<=~30 traces, 256 dense features,
`MAX_CONJUNCT=2` pairwise search capped at `MAX_SINGLES_FOR_PAIRING=60`) -- not a matmul-batchable
primitive; this cell IS validating a diagnostic gate composition, not a substrate compute primitive.
Storage strategy: `no_storage` (in-memory `Library`/`LibraryItem` objects only, matching the wire-
point module's own convention). Expected wall time: seconds to low tens-of-seconds (reference smoke
cell measured 3.57s for the underlying corpus pass alone; the added per-item MDL fits are the only
new cost, each a small closed-form search).

## Amendment (post-implementation, found by the mandatory pre-check itself)

The pre-check described above was FIRST implemented with the dense per-raw-dimension feature
encoding described in section 1 (`d{i}:+/-` for all 256 dims) at `n_per_class=4` (MIN_CONFIRM
scale). It FAILED: `per_cluster_gate` returned False (`chosen=KEEP_EPISODIC, n_rules=0`) even on a
perfectly-separable 8-trace synthetic set. Diagnosis: with ~512 raw singles (+ pairs, ~2000+ total
candidates), `induce_rules`' own MDL rule-cost term (`l_rule_bits = log2(n_candidates_considered)`,
the bits needed to specify WHICH candidate rule was picked -- a correct multiple-comparisons
penalty) is ~11 bits, exceeding the ~4-8 bits of achievable entropy savings for any item under
several dozen traces -- INCLUDING a maximally-compressible positive control. This is exactly the
flat-result-means-diagnose discipline firing as designed: the pre-check caught a broken adapter
BEFORE any real-corpus MIDDLE_BAND/negative would have been (wrongly) accepted at face value.

**Fix (implemented, not just proposed):** coarse-grained the feature space to
`N_MDL_PROJECTIONS=8` fixed, deterministic (hashlib-seeded) random hyperplane projections of the
256-dim context vector (LSH-style bucketing), shrinking the candidate space to <=16 singles / <=136
total. Re-ran the pre-check at `n_per_class=8` (16 traces, still perfectly separable, still
non-degenerate entropy) -- MEASURED@d:/AI/hd-instrument/data/exp_learner_mdl_gate_on_acquisition_
traces_v1/metrics.json:precheck_maximally_compressible = `{"chosen": "ruleind",
"compression_ratio": 2.6016, "null_bits": 16.0, "description_bits": 6.15, "is_episodic": false,
"n_rules": 2}` -- PASSES with margin. The noise-mixed-labels control (same trace count, independent
random-noise context) correctly gate=False. This coarse-projection encoding is used identically
everywhere in the cell (pre-check, guard-invariant re-test, real-corpus shadow scoring) -- one
feature-space definition, no per-context special-casing.

## Dispatch

Given the measured wall time (tens of seconds), this is run FOREGROUND-TO-COMPLETION locally, not
queued (per compute-proportionality + "light compute -> run fast to completion in foreground" -- see
`exp_learner_module_refactor_proof_v1.py` for the precedent of a same-class refactor/measurement
cell explicitly marked LOCAL-ONLY). `--self-test` and a real invocation are both run and reported
directly with numbers, per the COMPLETE-OR-HANDOFF discipline (prefer an actual verdict over a
queue handoff when the cell completes fast enough to make a handoff pure overhead).
