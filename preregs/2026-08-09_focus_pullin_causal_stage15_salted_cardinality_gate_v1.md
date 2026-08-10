# Pre-registration: exp_focus_pullin_causal_stage15_salted_cardinality_gate_v1

**Filed by:** exp_dev, 2026-08-09. **Task source:** Director spawn prompt, "Build STAGE 1.5 -- the
salted-cardinality gate test" per `notes/exp_dev_handoff_research_precise_highcardinality_retrieval_rescue_2026-08-09.md`
Anchor #1 (primary, self-contained spec).

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "salted cardinality high-M distractor pull-in false admission extreme
value cardinality gate context conditioned shortlist"` -> top hit `entity='cardinality'` cosine=0.373
(WordNet generic lexical entry), rank-2/3 hits are unrelated preregs (`prereg_coherence_role_conflict_
crosstalk_v1`, `research_drill_brain_multihop_M5_reverse_replay...`, K-extended task-vector sweeps,
time-decay-eviction Pareto cell, meta-learning cell) that merely contain the word "cardinality" in an
unrelated context (K-sweep axis size, not EVT-max-over-M salted-distractor pull-in). **Verdict:
genuinely novel, not a rediscovery** -- no prior cell tests salted-cardinality EVT inflation or a
context-conditioned pre-scoring gate against it. This is a direct, disclosed EXTENSION of Stage 1
(`exp_focus_pullin_causal_stage1_micro_world_v1`, itself authored+HARD-PASSed this same session).

## What / why
Stage 1 (HARD-PASS, 5/5 seeds, `data/exp_focus_pullin_causal_stage1_micro_world_v1/metrics.json`)
validated salience-gated `iterative_attractor` pull-in at a TRIVIAL cardinality (M=30, the micro-world
itself, no distractors). The anticipated failure mode at CSKG scale (M up to ~1.24M) is extreme-value
(EVT) inflation of the max-over-M null-similarity score: `E[max_i cos(probe, x_i)] ~ sigma * sqrt(2 ln
M)` for M unrelated candidates, so a FIXED admission threshold that is safe at M=30 will over-admit
(false pull-in) as M grows, purely from cardinality, with zero change in the mechanism's semantic
selectivity. This cell is the cheap, synthetic, CPU-only DIAGNOSIS+RESCUE gate: (1) prove the FLAT
(fixed-threshold, unmodified `pull_in()`) arm's false-pull-in rate actually grows with salted
distractor cardinality M as EVT predicts (the diagnosis), (2) prove a CONTEXT-CONDITIONED gate-before-
scoring arm (restrict candidates to a coarse context-matched shortlist BEFORE running the expensive
attractor settle + admission) keeps false-pull-in bounded as M grows (the rescue), and (3) an
independent NULL-SWEEP arm that measures the raw empirical max-cosine distribution directly against
the EVT `sqrt(2 ln M)` prediction -- this is what separates "real EVT/cardinality effect" from a
weak-signal misdiagnosis (a flat-result guard per the standing "flat=broken-experiment" discipline).

## Reuse contract (read-only import; NEW FILE; conflict-free with the concurrent Stage-2 sub-test)
Imports (read-only, unmodified) from `experiments/exp_focus_pullin_causal_stage1_micro_world_v1.py`:
`build_microworld`, `build_causal_facts`, `build_causal_register`, `BipolarCausalRegister`, `pull_in`,
`_sweep`, `_deterministic_perm`, `_cos`, `precheck_trivial_case`, `run_one_seed` (aliased
`stage1_run_one_seed`, used ONLY for the mandatory regression check), `seed_verdict` (aliased
`stage1_seed_verdict`), plus constants `N_DIM`, `N_CLUSTERS`, `STEPS`, `GATE_THRESH`, `IATTR_TEMP`,
`IATTR_MAX_STEPS`, `SEEDS_FULL` (all aliased `STAGE1_*`) -- avoids re-declaring values that could drift
from Stage-1's own calibrated constants. **Neither `hdlab/situation_focus.py` nor the Stage-1 script
itself is modified.** `hdlab.cleanup_family.iterative_attractor` (aliased `_iterative_attractor`, same
alias Stage-1 uses) and `hdlab.role_slot_summarizer._bipolar_bind/_bipolar_quantize/_bipolar_random`
and `hdlab.event_bundle.EventBundleCodec` are imported directly (same primitives Stage-1 already
depends on). This is a brand-new file (`experiments/exp_focus_pullin_causal_stage15_salted_cardinality_
gate_v1.py`); git add is targeted to this file + this pre-reg only (never `-A`), per the Director's
conflict-avoidance instruction (concurrent Stage-2 agent a7d5ce26 is independently using `pull_in`).

## Bipolar / glass-box / no-borrowed-embeddings constraint
Every distractor (event-content AND context-tag) is generated via `EventBundleCodec`'s bipolar
bind(elementwise-mul)+quantize(sign) construction, using role keys and a codec-primed reused
vocabulary drawn from a NAMESPACE DISJOINT from the real micro-world's symbols (`distr_ev_<ROLE>_<k>_
s<seed>` / `distr_ctx_<ROLE>_<k>_s<seed>` vs Stage-1's `agent_<c>_s<seed>` / `pred_<c>_<i>_s<seed>` /
etc). `KGStore` (and its `init_entities=False` / director_kb encoder-overwrite path) is NOT imported
or used anywhere in this cell -- the context-conditioned arm PORTS the `E[context]*R[relation]` key-
bind PATTERN and the `refuse_gate_calibrate` calibration PATTERN as cell-local functions operating on
raw bipolar-derived cosine scores (see "Context-conditioned arm" below), avoiding KGStore's W-matrix /
entity-codebook machinery entirely (not needed for this task shape, and keeps the forbidden path
untouched by construction, not by discipline alone).

**Performance note (disclosed, not silent):** literal per-item `codec.encode_event()` calls for
100,000+ distractors would be slow in a Python loop. The distractor-pool builder therefore VECTORIZES
the identical computation (gather reused-vocab filler rows via `codec.codebook()` + advanced indexing,
elementwise-multiply by `codec.role_key(role)`, sum over roles, `sign()`-quantize) -- mathematically
IDENTICAL to N calls to `encode_event()`, using the SAME codec-registered role keys, vocabulary, and
bind/quantize primitives, just batched. A self-test (`_selftest_vectorized_matches_literal_encode_
event`) cross-checks a sample of vectorized rows against literal `encode_event()` output for
bit-identity before any FLAT/CONTEXT/NULL-SWEEP measurement is trusted.

## Design
1. Reuse Stage-1's exact 5-cluster x 6-event micro-world (`build_microworld`, `N_CLUSTERS=5`,
   `STEPS=6`, `N_DIM=1024`, `GATE_THRESH=0.28`) unmodified, per seed.
2. Generate a NESTED distractor pool per seed: `M_MAX=100000` salt-content vectors + `N_NULL_
   QUERIES=200` held-out query vectors (never included in any rung's codebook, used only by the
   NULL-SWEEP arm) + `M_MAX` per-distractor context tags (2-role AGENT/TENSE-style partial-event
   binds, disjoint namespace, no relation to real clusters or each other). Three cardinality rungs
   `M_RUNGS = [1000, 10000, 100000]` take `pool[:M_rung]` (nested, so the EVT growth curve is measured
   on genuinely nested samples).
3. **Arm FLAT:** Stage-1's `pull_in()` UNMODIFIED, fixed `GATE_THRESH=0.28`, `iterative_attractor`
   (`hdlab.cleanup_family.iterative_attractor`, Stage-1's exact call convention) over the FULL salted
   codebook (30 real + M_rung distractors) for each of the 30 real probes (excluding self). Outcome
   per probe: `correct_incluster` / `false_offtopic` (admitted, real event, wrong cluster) /
   `false_distractor` (admitted, a distractor) / `not_admitted`. `false_pull_in_rate = (false_offtopic
   + false_distractor) / 30`.
4. **Arm CONTEXT-CONDITIONED:** per-cluster context vector `context_vecs[c] = bind(AGENT_filler_vec[c],
   TENSE_filler_vec[c])` (decoded from a real cluster event via `codec.query_role_vec` -- both fillers
   constant within a cluster by Stage-1's own construction). A single fixed `relation_vec` (bipolar,
   seed-derived) marks "focus-shortlist query" (`KGStore.key(s,p) = E[s]*R[p]`-style convention, ported
   as `ctx_key = bind(base_vec, relation_vec)` -- no KGStore object constructed). Each item (real event
   or distractor) carries an `item_context_tag`: real events get their cluster's `ctx_key`; distractors
   get their OWN independently-drawn context tag (no relation to any real cluster or each other). Per
   probe: rank ALL other items by raw dot-product against the probe's own `ctx_key` (bipolar bind
   vectors have constant norm sqrt(N_DIM), so raw dot ranks identically to cosine); take the top
   `K_SHORTLIST=20` (~4x the 5 in-cluster same-cluster-other candidates, leaving genuine room for
   false candidates to also compete at the final gate -- not a trivially-safe design). Run
   `iterative_attractor` over JUST the shortlist. Admission threshold is CALIBRATED per (seed, rung)
   via a cell-local `refuse_gate_calibrate_from_scores()` -- a direct algorithmic PORT of
   `hdlab.kg_traversal.KGStore.refuse_gate_calibrate`'s 50/50-split + tau-sweep + balanced-accuracy
   selection, applied to raw bipolar pull-in cosine scores instead of KGStore (s,p) key lookups.
   In-set calibration scores = probe-vs-same-cluster-other raw cosines (~5/probe); out-set = probe-
   vs-off-cluster-real raw cosines (~24/probe, M-independent) UNION probe-vs-shortlisted-distractor raw
   cosines (up to 20/probe, the ACTUAL rung-specific adversarial competitors) -- `calibration_check:
   adaptive_with_discriminator_gate` (tau recalculated per rung, since the OOD score distribution is
   M-dependent by design; this is the whole point of the test).
5. **Arm NULL-SWEEP (mandatory):** the 200 held-out distractor query vectors (never salted into any
   rung's codebook) are scored (single L2-normalized dot product, no `iterative_attractor`) against
   the FULL salted codebook at each rung; `mean_max_cosine` per rung is the empirical EVT statistic.
   Compared against the theoretical growth ratio `sqrt(ln(M_max)/ln(M_min))` between the smallest and
   largest rungs.
6. **Mandatory regression:** `stage1_run_one_seed(seed)` + `stage1_seed_verdict(...)` (Stage-1's OWN
   functions, unmodified) are re-run fresh for every seed used here, asserting Stage-1's M=30
   unsalted result is STILL `HARD_PASS` under the current code state -- catches any silent dependency
   drift from touching shared `hdlab/` primitives (none are touched by this cell, but the check is
   cheap (<10s) and mandatory per the hand-off).

## Pre-registered bands (research-fixed, verbatim; NOT exp_dev's to loosen)
- **HARD-PASS:** FLAT arm `false_pull_in_rate` at M=100,000 >= 2x its M=1,000 value AND
  CONTEXT-CONDITIONED arm `false_pull_in_rate` at M=100,000 <= 1.5x the Stage-1 M=30 baseline AND
  null-sweep max-cosine growth (M=1,000 -> M=100,000) is within +/-30% of the EVT `sqrt(2 ln M)`
  prediction.
- **HARD-FAIL:** CONTEXT-CONDITIONED arm ALSO rises >=2x by M=100,000 (context-conditioning
  insufficient -> escalate to resonator Rank-2) OR FLAT arm does NOT show the predicted rise (wall is
  not EVT/cardinality -> re-diagnose) OR the Stage-1 M=30 regression check fails.
- **MIDDLE_BAND:** everything else (e.g. context-conditioning slows but does not fully bound the rise).

### Edge-case declarations (disclosed BEFORE running, not decided post-hoc)
- **Stage-1's measured M=30 baseline `false_pull_in_rate` is EXACTLY 0.000 across all 5 seeds**
  (MEASURED@`data/exp_focus_pullin_causal_stage1_micro_world_v1/metrics.json:per_seed_summary.*.
  false_pull_rate` = 0.0 for seeds 7/17/29/41/53). Applied LITERALLY, `1.5x baseline = 0`, so the
  CONTEXT-CONDITIONED HARD-PASS leg requires EXACTLY ZERO false pull-ins across all 30 probes at
  M=100,000 for that seed. This is a strict, honest consequence of a verbatim band applied to a
  genuinely-zero empirical baseline -- NOT loosened (no epsilon-floor substituted). Reported plainly
  in the verdict message and metrics (`context_bound_check.cap = 0.0`).
- **FLAT-arm "shows the predicted rise" ratio check divides by the M=1,000 rate**, which could itself
  be exactly 0 (a legitimate possible outcome, not assumed). If `rate(M=1000) > 0`: literal ratio
  check (`rate(M=100000) >= 2 * rate(M=1000)`). If `rate(M=1000) == 0`: fallback interpretation
  `rate(M=100000) > 0` (any nonzero rise counts as "shows the predicted rise" when the ratio is
  undefined/infinite) -- `flat_growth_check.mode` field records which branch fired. Same fallback
  logic is reused for the symmetric HARD-FAIL leg ("CONTEXT-CONDITIONED arm ALSO rises >=2x").

## Compute architecture
(a) NOT batched-GPU; (b) sequential-CPU with justification: every scoring operation is a dense
`(M, N_DIM) @ (N_DIM,)` or `(M, N_DIM) @ (N_DIM, K)` numpy matmul (cosine/dot scoring, no training, no
backprop). At the heaviest rung (M=100,030, N_DIM=1024) the FLAT arm's 30-probe sweep is the dominant
cost (~30 probes x <=8 `iterative_attractor` iterations x ~205M-flop matmul/iter ~ 1e11 flops total);
NULL-SWEEP is a single batched (M, N_DIM)@(N_DIM, 200) matmul (~4e10 flops); CONTEXT-CONDITIONED is
CHEAPER than FLAT by construction (its `iterative_attractor` calls run over the K_SHORTLIST=20-row
shortlist, not the full M-row codebook -- the context-scoring pass itself is one more (M,N_DIM)@(N_DIM,)
matmul per probe, same order as NULL-SWEEP). THEORETICAL@estimate: ~1e11-2e11 total flops per (seed,
rung=100000) at plain single-thread numpy throughput (~5-15 GFLOP/s, `OMP_NUM_THREADS=1` per repo
convention) -> ~10-40s per seed at the top rung; M=10,000 and M=1,000 rungs are 10x/100x cheaper. 5
seeds x 3 rungs -> low-single-digit minutes total (MEASURED at smoke time, see completion report).
This is squarely CPU-cheap-by-construction (the entire point of Stage 1.5 per the hand-off) -- no GPU
speedup opportunity at this scale, and GPU dispatch overhead would exceed the compute itself. Storage
strategy: no_storage / no_composition (single-shot per-rung retrieval measurement, no chained
composition).

## Cell-template mandates
- `arms_differ_verified`: True -- FLAT vs CONTEXT-CONDITIONED per-probe outputs (at the top rung)
  hash-differ (`_arms_must_differ_stage15`, same SHA256-digest pattern as Stage-1's `_arms_must_differ`).
- `final_metrics_atomicity`: `tmp_replace` (top-level metrics.json) + `per_iter_paths`-equivalent via
  `experiments/_seed_checkpoint.write_partial_key`/`load_partial_key` at (seed, M_rung) compound-key
  granularity for per-rung resumability (M=100,000 is the heavy unit; a crash mid-run loses at most
  the in-flight rung, not the whole seed).
- `except SystemExit: raise` before `except Exception` (no bare `except:` / `except BaseException:`).
- `crlb_n/a`: accuracy/rate-comparison ablation over a fixed synthetic salted micro-world; no
  closed-form capacity/SNR discriminator threshold to CRLB-check (bands are rate-growth-ratio and
  EVT-curve-fit comparisons, not a noise floor).
- `cardinality_ok`: `EXPECTED_N_UNITS = len(SEEDS_FULL) * len(M_RUNGS) = 5 * 3 = 15` for `--full`,
  `1 * 3 = 3` for `--smoke` (smoke uses the SAME 3 rungs, including the M=100,000 discriminator-preview
  point, per DISCRIMINATOR-MUST-SURVIVE-SCALE option (A) -- smoke IS full-N, just 1 seed).
- `calibration_check`: FLAT arm = `default_ok_for_this_regime` (Stage-1's fixed `GATE_THRESH=0.28`,
  unmodified, imported not re-derived). CONTEXT-CONDITIONED arm = `adaptive_with_discriminator_gate`
  (tau recalibrated per (seed, rung) via `refuse_gate_calibrate_from_scores`, logged in metrics
  per-rung; the discriminator-still-fires check is the HARD-PASS/HARD-FAIL band comparison itself).
- `deterministic_seeding`: True -- all distractor generation uses `numpy.random.default_rng(<explicit
  int seed>)` or `torch.Generator().manual_seed(<explicit int>)`; scramble/permutation reuses Stage-1's
  `_deterministic_perm` (hashlib-seeded) where applicable; no built-in `hash()`, no `list(set())`
  ordering anywhere in this file.
- `cell_chunked`: False (single script; per-(seed,rung) checkpointing via `_seed_checkpoint.write_
  partial_key`/`load_partial_key`, not separate sibling files -- estimated total FULL runtime is
  low-single-digit minutes, well under the threshold that would warrant chunked-per-seed-file
  architecture).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: True.
- `progress_logging`: `print_flush_true` (declared defensively; per-rung `print(..., flush=True)`
  progress lines even though estimated `timeout_s` is well under the 1800s mandatory threshold).
- Real-code-path preflight: `self_test()` constructs the REAL `EventBundleCodec`,
  `hdlab.cleanup_family.iterative_attractor`, Stage-1's real `build_microworld`/`pull_in`/
  `precheck_trivial_case`/`run_one_seed`/`seed_verdict`, and this cell's own
  `refuse_gate_calibrate_from_scores` / context-conditioned pipeline, all at a REDUCED but still-real
  scale (`n_dim=256`, `M_RUNGS=[10,50,200]`) -- no synthetic-only branch.

## Dispatch
Local CPU, per Director's spawn prompt and the design's own CPU-cheap-by-construction premise.
`--self-test` and `--smoke` run foreground-local. Given the compute-architecture estimate
(low-single-digit minutes total for `--full`), `--full` is ALSO run foreground-local-to-completion
(per exp_dev's INLINE-LOCAL / COMPUTE-PROPORTIONALITY discipline: light compute runs fast-to-completion
in the foreground rather than round-tripping through a queue) -- NOT dispatched to `local_cpu_queue`
(smoke-only per the 2026-07-01 USER-lock) and NOT routed remote (no justification for remote-queue
round-trip latency on a sub-10-minute job). If actual measured smoke wall-time contradicts this
estimate (cell runs far slower than predicted on this box), exp_dev falls back to filing a
`remote_cpu_queue` hand-off for the Orchestrator per standard practice -- disclosed in the completion
report either way, not silently substituted.
