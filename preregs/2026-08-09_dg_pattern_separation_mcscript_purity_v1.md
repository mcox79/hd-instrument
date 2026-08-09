# Pre-reg: dg_pattern_separation_mcscript_purity_v1 (ISOLATED CAN-FAIL diagnostic)

**Filed-by:** exp_dev, 2026-08-09.
**Task:** Director task -- isolate the diagnosed fix for the MCScript2.0
`exp_mcscript2_real_benchmark_validation_v1` HARD_FAIL (commit 5c1199f87)
BEFORE any full MC re-run. Diagnosis: the failure is CLUSTERING-CARDINALITY,
not extraction (extraction fires 100%). Greedy online match-or-spawn keying
(`hdlab.script_grain_acquisition_loop.ScriptLibrary.match_or_spawn`, via
`hdlab.cleanup_family.iterative_attractor`) OVER-MERGES at 195 scenario-types
-> only 33 items form, mean item_purity ~0.19-0.20 (catch-all buckets),
compounding DEGRADES with exposure (real_final=0.5538 < baseline=0.5859).
Root-cause hypothesis: the keying mechanism is CA3 pattern-COMPLETION
(`iterative_attractor`, brain-canonical via Treves-Rolls) with NO upstream
DG pattern-SEPARATION stage (orthogonalize/sparsify similar-but-distinct
inputs before matching) -- brain pairs DG-separation with CA3-completion
(Leutgeb 2007, Guzman 2016, McHugh 2007 causal evidence); this substrate only
completes.

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)

`bash tools/substrate_query.sh "DG pattern separation CA3 pattern completion
clustering cardinality over-merge purity"` -> top-5 hits: (1) `pattern_completion`
cosine=0.4619 (capability_registry, WIRED -- this IS the CA3-only mechanism
being diagnosed, not a DG-separation prior-art hit), (2)-(5) research-drill
notes on the DG/CA3 functional split (cosine 0.42-0.45, biology background,
not a prior built-and-tested DG-separation module). **Prior-work check: no
existing DG-separation MODULE at cosine>0.30 -- the biology is documented in
research notes (background/citation source, read + cited above) but no prior
cell/module implements DG-style expand+kWTA separation. Genuinely novel build,
not a rediscovery.**

## WHAT (isolation-first sequencing, FIXED per task contract)

Does adding a DG pattern-separation stage (`hdlab.dg_pattern_separation.
dg_separate` -- fixed random EXPANSION projection + k-winner-take-all
SPARSIFICATION, new module, self-tested standalone: determinism, exact
sparsity, self-similarity=1.0, and the decorrelation signature
raw_cos=0.8047 -> dg_cos=0.4409 on a controlled near-duplicate pair) BEFORE
the existing CA3/DG match-or-spawn keying raise item PURITY at 195-way
cardinality on MCScript2.0 TRAIN, without singleton-exploding into pure
memorization?

**This cell measures ONLY the isolated clustering/purity question.** No
consolidation passes (`script_consolidation_pass`), no MDL gate, no DEV
evaluation, no MC scoring -- those are irrelevant to cluster MEMBERSHIP, which
is determined entirely by the TRAIN spawn-loop (`ScriptLibrary.match_or_spawn`
called once per TRAIN instance, in `sorted(id)` order); the real-benchmark
cell's `item_purity` field is itself computed from exactly this same
spawn-loop's cluster membership (consolidation only flips item STATUS, never
re-keys traces) -- confirmed by reading `hdlab/script_grain_acquisition_loop.
py`'s `grow_and_track`/`script_consolidation_pass` (no `match_or_spawn` call
inside the passes loop). The MC re-run (Stage 2) is explicitly DEFERRED to a
follow-up cell, gated on this cell's purity result clearing HARD-PASS.

## Design

Two keying schemes, run through the IDENTICAL `ScriptLibrary().match_or_spawn`
loop over the full TRAIN split (2500 instances / 195 scenarios, `sorted(id)`
order, deterministic):

- **OFF (positive control, reproduces the landed HARD_FAIL's clustering):**
  `key_fn = bow_key` -- `hdlab.grounding_acquisition_loop.context_vector(text)`
  wrapped as a zero-imaginary complex64 tensor, IDENTICAL convention to the
  real-benchmark cell's `bow_register` (Amendment 1). This is the EXACT
  keying signal that produced the landed 0.19-0.20 purity -- reproducing it
  here (Gate D positive control, at the SAME test regime: full 2500-train/
  195-scenario TRAIN split) is the sanity check that this cell's spawn-loop
  is a faithful re-implementation before trusting the ON-arm comparison.
- **ON (treatment):** `key_fn = dg_key` -- `context_vector(text)` (same raw
  256-dim bag-of-words signal) run through `hdlab.dg_pattern_separation.
  dg_separate` (expand_dim=2048, sparsity=0.05, one fixed projection matrix
  per arm) before wrapping as the zero-imaginary complex64 register. Same
  `ScriptLibrary.match_or_spawn` / `iterative_attractor` CA3-completion step
  downstream, UNCHANGED (per task contract: DG-separation is a stage BEFORE
  CA3-completion, not a replacement for it).
- **Robustness variant (secondary, not gating):** ON @ sparsity=0.10 (same
  expand_dim), to show the primary result is not knife-edge-tuned to one
  sparsity value.

**Threshold calibration (per arm, mandatory -- fair-test discipline):** each
arm's `novelty_thresh` is calibrated SEPARATELY from a TRAIN-only stratified
sample (2 instances/scenario, all 195 scenarios, `sorted(id)`-deterministic --
identical sampling procedure to the real-benchmark cell's `precheck_a_keying_
discriminates`), via `hdlab.script_grain_acquisition_loop.
calibrate_novelty_threshold` (REUSED verbatim, not reimplemented -- it already
operates on arbitrary complex64 register tensors via `_real2d`+cosine, so it
works unmodified on DG-separated registers). Reusing the OFF arm's threshold
for the ON arm would be an unfair test: sparse k-WTA codes have a
fundamentally different cosine-similarity distribution than dense bag-of-words
codes, so each arm's threshold must reflect ITS OWN matched/wrong-pair
distribution. Gap (`matched_mean - wrong_mean`) and rank-AUC are also computed
per arm and reported for transparency (same realistic-not-strict criterion as
Amendment 3: gap>=0.05, auc>=0.60 -- if an arm's OWN keying fails this
precheck, its purity result is reported but flagged untrustworthy).

**DG-separation params (exp_dev autonomy, cited above):** `expand_dim=2048`
(~8x expansion of the 256-dim bow input; EC-II->DG mossy-fiber divergence
cited in the 5-10x range across species/estimates, 8x is a defensible
mid-range value), `sparsity=0.05` (5% active; biological DG population
sparsity is cited lower, ~1-4%, Jung & McNaughton 1993 / Chawla et al. 2005 --
5% is a deliberate, disclosed relaxation from the strict biological floor to
retain enough active units for 195-way discrimination against noisy
crowd-sourced language content, not a blind copy of the citation). Fixed
projection matrix per arm (`hdlab.dg_pattern_separation.projection_matrix`,
hashlib-seeded, PROT-023/F.5 compliant).

## PRE-REGISTERED BANDS (purity gate -- THE gate this cell answers; MC
re-run is a separate, deferred, follow-up cell gated on this HARD-PASSing)

Metrics (computed identically for OFF and ON arms):
- `n_items_total`: count of spawned `ScriptLibraryItem`s.
- `n_singletons` / `singleton_frac`: items with exactly 1 trace (trivially
  pure by construction -- excluded from the purity metrics below to avoid
  inflation; reported separately as the MEMORIZATION guard).
- `n_items_multi` (n_traces>=2): the population the purity gate applies to.
- `mean_purity_multi` (PRIMARY GATE METRIC): unweighted mean of per-item
  `majority_frac` (fraction of an item's traces sharing its most-common true
  scenario) over `n_items_multi` items.
- `trace_weighted_purity_multi`: same but weighted by each item's `n_traces`
  (fraction of ALL non-singleton traces sitting in their item's majority
  scenario) -- a data-coverage-weighted secondary view.
- `n_pure_items` / `pure_frac`: multi-trace items with `majority_frac >= 0.5`.
- `mean_purity_grounded_would_be` (n_traces>=MIN_CONFIRM=4, matching the
  real-benchmark cell's `item_purity` population for direct numeric
  comparability to its measured ~0.19-0.20).

**HARD-PASS:** ON-arm `mean_purity_multi` >= 0.50 (task's pre-registered
purity band) AND ON-arm `singleton_frac` <= 0.80 (at least 20% of items have
>=2 traces -- rules out the DG-separation degenerating into pure
memorization/near-1-to-1 mapping, the singleton-explosion failure mode) AND
the OFF-arm reproduction check (`mean_purity_grounded_would_be` on the OFF
arm) lands within 0.10 absolute of the landed cell's measured ~0.19-0.20
(sanity: this cell's spawn-loop is a faithful reproduction, not a different
code path masquerading as the same baseline -- Gate D).

**HARD-FAIL:** ON-arm `mean_purity_multi` < 0.35 (does not clear meaningfully
above the ~0.20 baseline) OR ON-arm `singleton_frac` >= 0.90 (DG-separation
is so aggressive nothing merges -- memorization, not generalization, a
failure mode by the task's own contract) OR the OFF-arm reproduction check
fails (>0.10 deviation from the landed ~0.19-0.20 -- this cell's baseline
arm is not trustworthy, so the ON-vs-OFF comparison cannot be trusted either).

**MIDDLE_BAND:** everything else (e.g. ON-arm purity improves materially
[0.35-0.50] but doesn't clear the pre-registered 0.50 band, or clears purity
but with a borderline singleton fraction).

**Contract note (explicit, per task):** clearing this gate does NOT itself
constitute a positive result on the downstream MC task -- it is the
NECESSARY-BUT-NOT-SUFFICIENT precondition the task instructs to check FIRST,
cheaply, before spending compute on a full MC re-run. A HARD-FAIL here is
reported as the honest capacity-ceiling finding (the substrate genuinely
cannot discriminate 195-way online with this keying signal, even with
DG-style separation), not hidden or reframed.

## SCHEMA-VET checklist

- `cardinality_ok`: `EXPECTED_N_UNITS = len(ARMS) = 3` (off, on_sparsity05,
  on_sparsity10); metrics field set from `len(per_arm) == 3`.
- `arms_differ_verified`: META_RULE_AF hash-test on each arm's
  `(n_items_total, sorted(item sizes))` -- all 3 arms must differ.
- `final_metrics_atomicity`: `tmp_replace`
  (`experiments._seed_checkpoint.write_metrics`), plus per-arm resumable
  checkpoints (`resumable_seeds`/`write_partial`/`aggregate_partials`, keys
  `"off"`/`"on_sparsity05"`/`"on_sparsity10"`).
- `except SystemExit / KeyboardInterrupt: raise` before `except Exception` --
  no bare `except:` / `except BaseException:` anywhere in the cell.
- `crlb_n_a`: keying/clustering cell; no argmax/top-k associative-recall
  capacity ceiling applies (this cell's own purity gate IS the
  capacity-feasibility question being measured, not assumed).
- `deterministic_seeding`: true -- `np.random.default_rng` + `hashlib`
  throughout; no built-in `hash()`, no `list(set())` ordering
  (`sorted(train_instances, key=lambda x: x["id"])` used for TRAIN iteration,
  `sorted(by_scenario)` for the stratified precheck sample).
- `calibration_check`: `adaptive_with_discriminator_gate` -- `novelty_thresh`
  calibrated fresh per arm every run from a TRAIN-only stratified sample,
  never hand-tuned to force a PASS.
- Resumable per-unit: 3 arms via `experiments._seed_checkpoint`.
- Progress logging: `print(..., flush=True)` per arm milestone (precheck,
  spawn-loop progress every 500 instances, final purity stats);
  `progress_logging: "print_flush_true"`. Estimated wall time well under
  1800s (see Compute architecture) so the heartbeat mandate does not
  strictly apply, but progress lines are emitted regardless.

## Compute architecture

Sequential-CPU, numpy/torch (complex64 CPU tensors for the FHRR register
wrapper convention; DG separation itself is a single (2048, 256) float32
matmul per instance, negligible). Per COMPUTE-PROPORTIONALITY /
INLINE-LOCAL-MANDATE: this is a DIRECTIONAL GATE question (does DG-separation
raise purity, yes/no), the cheapest decisive method is a structural clustering
measurement over the full TRAIN set with NO consolidation/DEV/MDL machinery
(all irrelevant to cluster membership, confirmed by code-reading above) -- NOT
a full pipeline re-run. Run FOREGROUND-TO-COMPLETION directly (not routed
through `queue_add.sh` / `local_cpu_queue`, per the same precedent as the
parent real-benchmark cell's own pre-reg: smoke-only-on-local-queue targets
FULL DISPATCH via queue infrastructure, not a direct light foreground
invocation). "Local if light" per task's explicit authorization.

**Wall-time estimate before dispatch:** worst-case per-arm cost is a Python
loop over 2500 instances, each doing an `iterative_attractor` matmul against a
codebook that grows up to (bounded by) n_items_total rows x (2*expand_dim)
columns for the ON arms (2*2048=4096) or (2*BOW_D)=512 for OFF. Summed
harmonic-like cost across the loop is estimated at low tens-of-seconds per
arm (BLAS-backed matmuls, no Python-level inner loop over dimensions) --
verified empirically before claiming FULL landed (see completion report).
Well under the 10-minute foreground cap even for all 3 arms sequentially.

**Smoke** (DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C hybrid): runs the
IDENTICAL 3-arm pipeline on a REDUCED scenario slice (first 20 scenarios,
sorted, deterministic -- around 250-300 train instances) to verify (a) no
crashes / clean precheck+spawn-loop completion for all 3 arms, (b) the OFF
arm's purity is LOW (over-merge directionally present even at reduced
cardinality -- discriminator-fires check for the baseline arm), (c) precheck
gap/AUC compute successfully for all 3 arms. FULL then runs the complete
195-scenario/2500-instance TRAIN split as the actual decisive gate (this is
cheap enough that FULL essentially IS a full-N smoke per DISCRIMINATOR-MUST-
SURVIVE-SCALE option A -- both run in the same session).

## MEASURED RESULT

See completion report / `data/exp_dg_pattern_separation_mcscript_purity_v1/
metrics.json` (FULL) and
`data/exp_dg_pattern_separation_mcscript_purity_v1_smoke/metrics.json`
(smoke) for full per-arm detail.
