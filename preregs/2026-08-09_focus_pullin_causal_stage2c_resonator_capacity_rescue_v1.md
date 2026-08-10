# Pre-registration: exp_focus_pullin_causal_stage2c_resonator_capacity_rescue_v1

**Filed by:** exp_dev, 2026-08-09. **Task source:** Director spawn prompt, "test the CAPACITY
RESCUE for the re-diagnosed scale wall." Stage-2-B (`exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1`,
HARD_FAIL, commit 013f1481e) EMPIRICALLY found the wall is NOT EVT false-positive inflation
(`false_pull_in_rate=0.000` at every scale) but STORE-CAPACITY COLLAPSE: `KGStore`'s single
`[1024,1024]` Hebbian W hits a Hopfield/Tsodyks-Feigelman crosstalk cliff --
`relevant_recall`: 0.967(1K) -> 0.947(5K) -> 0.700(10K) -> 0.000(30K+); `relevant_in_shortlist_rate`
(the store-capacity attribution diagnostic): 1.000(1K-5K) -> 0.973(30K) -> 0.333(100K) ->
0.007(1.2M) -- the true answer drops out of even the coarse linear shortlist well before full
cardinality. This EMPIRICALLY CONTRADICTS `KGStore`'s docstring cert (`setrecall@100K=1.0`) for
this bipolar single-W config at THIS task shape (pull-in admission over the full 482,588-entity
codebook, not the KG-completion top-k task the cert was measured on) -- treated here as a
DIFFERENT task shape invalidating direct transfer, not as a fabrication.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "resonator factorization causal store capacity crosstalk KGStore
scale"` -> top hit `resonator_factorization_v1` at **cosine=0.4092** (above the 0.30 read
threshold) -- **VERDICT_OF: HARD_FAIL**. Read in full (`data/exp_resonator_factorization_v1/metrics.json`):
K-way multiplicative-bind resonator factorization success by K (N=2048, M=30 per factor, pure
synthetic composite, NO Hebbian store, NO crosstalk from other items): K2=1.000, K3=0.613 (HARD_FAIL
band, <0.70), K4=0.047. **This is prior work that must inform, not be rediscovered:** basin-convergence
of the alternating resonator ITSELF degrades sharply as K grows past 2, even in the ideal
noise-free case. Design response (see Mechanism below): this cell uses **K_ENT=2** (not K=3 or
higher) for entity-identity factorization specifically to sidestep the basin-convergence risk this
prior cell surfaced, banking the validated K2=1.000 regime rather than the shakier K3 regime. Second
hit `exp_resonator_dg_crosstalk_disentangler_v1` (cosine <0.30 on this exact query but read anyway
per its explicit reuse mandate from the Director) supplies the ORACLE-UNBIND-MARGIN methodology
reused directly below (isolating codebook crosstalk from basin dynamics by unbinding with the
TRUE other factor rather than an estimated one). **Verdict: genuinely novel wiring (resonator
factorization applied to the real CSKG causal store's capacity collapse) that explicitly reuses,
not rediscovers, two prior mechanisms (the K2-viable/K3-risky finding, and the oracle-unbind-margin
measurement technique).**

## What / why
Stage-2-B named the mechanism (Hopfield/Tsodyks-Feigelman crosstalk cliff in a single shared W) and
proposed two rescues: resonator factorization (this cell) or sharded-W. This cell tests whether
factorizing the causal-fact space so effective per-decode-step candidate counts shrink from
`n_ent=482,588` to `M_SUB~1,024` per factor raises the crosstalk-tolerance ceiling enough to hold
recall at the exact rungs (100K, 1.2M) where the flat single-entity-codebook readout collapsed to
`relevant_recall=0.000`.

**Theoretical grounding (THEORETICAL, Gaussian order-statistics / Gumbel 1958, same family cited in
`notes/research_precise_highcardinality_retrieval_rescue_2026-08-09.md`):** the standardized noise
margin a decode step must beat scales `~sqrt(2*ln(#competing candidates))`. `sqrt(2*ln(482588)) =
5.116` vs `sqrt(2*ln(1024)) = 3.723` -- a ~1.37x reduction in required per-step SNR margin from
factorizing the search space from flat-`n_ent` to two `M_SUB=1024` sub-decodes. This is the
mechanistic reason factorization can raise the crosstalk-tolerance ceiling even though the SAME
physical W matrix, ingesting the SAME triples, carries the SAME absolute crosstalk noise magnitude
regardless of how the O-role identity is encoded -- what changes is how much of that noise a given
decode step can tolerate before picking the wrong candidate.

## Mechanism design (exp_dev's exact factoring choice, disclosed)
**Entity-identity digit-factorization** (K_ENT=2, mixed-radix, deterministic, no `hash()`):
- `M_SUB = 1024` (chosen for `M_SUB^2 = 1,048,576 >= n_ent = 482,588`, ~2.17x headroom margin, and
  a clean power-of-2 codebook size).
- `digit0(id) = id // M_SUB`, `digit1(id) = id % M_SUB` for every entity id in `[0, n_ent)`.
- Two per-digit bipolar codebooks `D0, D1` of shape `[M_SUB, n_dim=1024]` (fixed-seed, deterministic
  `torch.Generator`), each **~2 orders of magnitude smaller** than the flat `n_ent x n_dim` entity
  codebook (`8MB` total for `D0+D1` vs `~2.0GB` for a flat `[482588,1024]` `E`).
- `entity_code(id) = D0[digit0(id)] * D1[digit1(id)]` (bipolar elementwise multiply -- exactly
  invertible since `x*x=1` elementwise for bipolar `{-1,+1}`).
- This `entity_code` REPLACES `KGStore.E` for BOTH the S-role and the O-role (entities appear in
  both positions across the real CSKG triples); `KGStore.R` (33 relations) stays a flat codebook,
  un-factored, since `n_rel=33` is already far smaller than any useful `M_SUB`.
- **The Hebbian store itself is UNCHANGED**: `key(s,p) = entity_code(s) * R[p] * sqrt(n_dim)`,
  `W += outer(entity_code(o), key) / n_dim`, accumulated via the SAME
  `KGStore.ingest_triples()` method, byte-identical code path, injected via the documented
  `init_entities=False` + explicit `store.E = <precomputed factored codebook>` pattern (per
  `experiments/_validity_preflight` gate F.3's "base kwargs only, overwrite fields explicitly"
  discipline -- the same safe injection pattern `director_kb.run_ingest` already uses). **Disclosed
  design choice:** this keeps the SINGLE shared `[1024,1024]` W matrix and its crosstalk physics
  exactly as-is; what is being tested is whether a smaller-per-decode-step, resonator-factored VALUE
  representation raises the crosstalk-tolerance ceiling of retrieval FROM that same matrix -- not a
  claim that the matrix itself was restructured. This is the mechanistically correct operationalization
  of "capacity ~M^K vs a single W's O(N)": the M^K argument is about how many DISTINCT VALUES a fixed
  noise budget can still discriminate, not about the storage matrix's own shape.

**Resonator decode** (2-way alternating unbind-cleanup, `RESONATOR_MAX_IT=8`, early-stop on
digit-pair stabilization -- directly analogous to `exp_resonator_factorization_v1.resonate()`,
banked at K=2 where that cell measured 1.000 success):
```
e1 = D1.mean(0)                      # init
loop (<=8 iters):
    r0 = probe * e1;  s0 = D0 @ r0;  i0 = argmax(s0);  e0 = D0[i0]
    r1 = probe * e0;  s1 = D1 @ r1;  i1 = argmax(s1);  e1 = D1[i1]
    stop if (i0,i1) unchanged
entity_id_hat = i0 * M_SUB + i1
confidence   = cosine(probe, D0[i0]*D1[i1])
admitted     = confidence >= GATE_THRESH   # SAME 0.28, reused unretuned (see Gate/threshold note)
```
**`relevant_in_shortlist_rate` analog (reuses the oracle-unbind-margin methodology from
`exp_resonator_dg_crosstalk_disentangler_v1` directly, per Director instruction "do NOT re-derive"):**
unbind with the TRUE OTHER digit (`r0_oracle = probe * D1[true_d1]`, `r1_oracle = probe *
D0[true_d0]`) and check whether `argmax(D0 @ r0_oracle) == true_d0` AND `argmax(D1 @ r1_oracle) ==
true_d1`. This isolates STORE crosstalk (is the true digit combination still the best explanation of
the noisy probe, given the other true digit) from RESONATOR BASIN-CONVERGENCE dynamics (whether the
iterative alternating search actually finds that combination starting from an uninformed init) --
exactly the same attribution split Stage-2-B's `relevant_in_shortlist_rate` (upstream store capacity)
vs `relevant_recall` (gate/argmax) draws, now decomposed one level further for the resonator arm.

**Gate/threshold note (disclosed caveat, not swept):** baseline's admission score is a cosine against
a CA3-settled probe (`pull_in`'s `_iterative_attractor` refines the raw probe before the final cosine
gate); the resonator arm's admission score is a cosine against the RAW, un-settled probe. Reusing the
identical numeric `GATE_THRESH=0.28` for both arms is the SAME un-retuned-number discipline
Stage-2-B used against Stage-1's calibration, but the two arms' confidence scores are not guaranteed
to live on an identical natural scale. Full confidence-score distributions (admitted vs rejected,
true vs false) are logged in metrics so this is auditable, not asserted away.

## Reuse (imported, not re-transcribed)
`from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import load_entity_vocab,
load_spine_edges, eval_gate, precheck_kgstore_and_loader, scale_point_verdict, _shuffle_objects,
GATE_THRESH, SHORTLIST_K, N_QUERY, QUERY_SEED, DATA_SEED, SCALES_SMOKE, SCALES_FULL, CSKG_DIR` --
the baseline (single-W) arm is this exact imported code, called with the exact same seeds, giving
BIT-IDENTICAL reproduction of Stage-2-B's landed numbers at matching scales (not merely
approximate) -- the strongest available form of the CONTRACT's "the single-W baseline arm ...
reproduce its collapse" precheck. `KGStore` from `hdlab.kg_traversal` (unchanged). `tools.exp_checkpoint`
(`unit_key`, `completed_units`, `record_unit`, `load_units`) for per-(arm,scale) resumability.

## Rung reuse (identical to Stage-2-B, for a clean head-to-head)
`SCALES_SMOKE = [1000, 10000]`, `SCALES_FULL = [1000, 5000, 10000, 30000, 100000, 1213912]` --
imported constants, not re-declared, so there is no risk of an accidental rung drift between the
two cells' sweeps.

## Bands
**Per-scale-point** (both arms): reuses Stage-2-B's `scale_point_verdict()` UNCHANGED (imported) --
same `HARD_PASS`/`HARD_FAIL`/`MIDDLE_BAND` formula applied to both arms' `(relevant_recall,
false_pull_in_rate)` pairs, so no per-arm threshold gerrymandering is possible.

**Cell-level RESCUE verdict** (compares resonator vs single-W head-to-head, per Director's
pre-registered bands, MEASURED at scale=100,000 and scale=1,213,912 -- the two rungs where
Stage-2-B's single-W arm measured `relevant_recall=0.000`):
- **HARD-PASS**: resonator `relevant_recall >= 0.50` at BOTH scale=100,000 AND scale=1,213,912
  (holds at BOTH collapsed rungs, not just delays to one) AND `false_pull_in_rate <= 0.20` at both
  (Stage-2-B's own HARD-PASS band) AND the SCRAMBLE_OBJECTS control at full scale collapses
  (`relevant_recall <= 0.10` AND `real_full_recall - scramble_recall >= 0.20`).
- **HARD-FAIL**: resonator `relevant_recall < 0.10` at BOTH scale=100,000 AND scale=1,213,912
  (factorization does not rescue the capacity cliff for this task; escalate to sharded-W).
- **MIDDLE_BAND**: everything else (partial rescue -- delays the collapse to a higher scale, or
  holds recall but fails the false-pull-in/scramble hygiene checks, or holds at one rung but not the
  other) -- motivates layering sharded-W on top rather than treating resonator alone as sufficient.

## Pre-check (CONTRACT-mandated, flat=broken-experiment discipline, BOTH required before any
result is trusted)
1. **Resonator trivial hand-case**: tiny synthetic setup, `n_ent=16, M_SUB=4, K_ENT=2` (exact
   cover: `4^2=16`), `n_dim=64`, real `KGStore` (via `init_entities=False` + injected factored `E`),
   16 hand-planted triples, `eval_gate_resonator` must show `relevant_recall >= 0.5` in this clean,
   near-zero-crosstalk regime.
2. **Single-W baseline reproduces its known collapse**: `self_test()` reads Stage-2-B's ALREADY-LANDED
   `data/exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1/metrics.json` off disk and asserts its
   `per_scale` shows the documented collapse shape (`recall > 0.9` at scale=1000, `recall < 0.05` at
   scale=1,213,912) -- guards against a stale/wrong reference file. Then, at smoke/full runtime,
   FRESH baseline numbers (computed via the bit-identically-reused code) are compared against this
   loaded reference at every overlapping scale, tolerance `0.02`; a mismatch sets
   `baseline_repro_ok=False` and the cell's overall verdict is downgraded to
   `BASELINE_REPRO_FAIL_DO_NOT_TRUST_COMPARISON` regardless of the resonator numbers.

## Cell-template mandates
- `arms_differ_verified`: baseline-vs-resonator per-scale digests must differ (different mechanism,
  expected); REAL-vs-SCRAMBLE_OBJECTS digests must differ per arm (reused `_shuffle_objects`).
- `final_metrics_atomicity`: `tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no bare `except:`, no `except BaseException`).
- `crlb_n/a`: empirical capacity-rescue diagnostic; no single closed-form noise floor to check
  against for the FULL pipeline (the oracle-unbind-margin THEORETICAL ratio above is the closest
  analytical anchor, logged as `THEORETICAL@` not `MEASURED@`).
- `cardinality_ok`: `EXPECTED_N_UNITS = 2 arms x (len(scales) + (1 if full else 0))` = 14 (full) / 4
  (smoke); per-(arm,scale) checkpointed via `tools/exp_checkpoint.py`.
- `calibration_check`: `default_ok_for_this_regime` -- `GATE_THRESH=0.28` reused unretuned from
  Stage-1/Stage-2-B, `M_SUB=1024`/`K_ENT=2` chosen from the capacity-feasibility math above + the
  prior-work K2-viable/K3-risky finding, not tuned against this cell's own results.
- `deterministic_seeding`: True (`torch.Generator().manual_seed(...)` fixed seeds throughout;
  `np.random.default_rng` fixed seeds for query sampling, imported unchanged from Stage-2-B;
  `hashlib`-seeded `_shuffle_objects`, imported unchanged; no `hash()`, no `list(set(...))`).
- Real-code-path preflight: `self_test()` constructs a REAL tiny `KGStore` for BOTH arms (imported
  `precheck_kgstore_and_loader` for the flat/baseline path; the K_ENT=2 hand-case above for the
  resonator path) AND validates the REAL `cskg_foundation_v1` loader (imported, unchanged) against a
  real data slice.

## Compute architecture
(a) NOT batched-GPU; (b) sequential-CPU with justification. **MEASURED anchor**: Stage-2-B's
IDENTICAL data-loading + ingest + baseline-eval pipeline (which this cell's baseline arm literally
reuses) completed its full 6-scale sweep + scramble control in **243.6s (~4 min)**, foreground-local,
no GPU. This cell adds: (i) one extra `KGStore` allocation + `entity_code` precompute for the
resonator arm (`O(n_ent * n_dim)` vectorized elementwise-multiply, `~494M` flops, sub-second), (ii)
resonator decode overhead per query (`<=8` iterations x 2 matvecs of shape `[1024,1024]x[1024]` each
`~1.05M` mults, x `~300` queries/scale x `6` scales `~ 2.9e10` mults total across the full sweep --
cheap for BLAS, expected low-single-digit-minutes addition). **Total expected wall time: comfortably
under the 10-minute foreground-completion ceiling**; run directly in foreground (`timeout=600000`),
not queued, matching Stage-2-B's own dispatch precedent and the CONTRACT's "report compute needs if
it can't run local" instruction (expectation: it can). Per-rung checkpointing via
`tools/exp_checkpoint.py` is still wired (CONTRACT-mandated) so a killed/interrupted run resumes
cleanly rather than restarting, independent of whether the full run turns out to need more than one
foreground call.

## Dispatch
Local (light-to-moderate) -- expected total wall time a few minutes over Stage-2-B's own MEASURED
243.6s baseline; run in foreground, resumable per (arm, scale) unit via `tools/exp_checkpoint.py` if
interrupted. `--self-test` and `--smoke` run first and gate the `--full` dispatch.

## ADDENDUM -- basin-convergence bug found + fixed before trusting any CSKG result (per
flat=broken-experiment discipline; disclosed as this changed the shipped mechanism mid-authoring)
The first smoke run (HARD-commit alternating readout: each iteration fully commits to the argmax
codeword before the next unbind) showed `relevant_recall` COLLAPSING at scale=1000/10000
(0.007/0.000) even though the oracle-unbind `relevant_in_shortlist_rate` stayed high (1.000/0.960)
-- i.e. the store still clearly contains the answer, but the end-to-end decode could not find it.
A standalone diagnostic (no CSKG needed, pure synthetic clean composites, zero crosstalk) isolated
the cause: **basin-proliferation in the alternating search itself**, not a crosstalk artifact --
hard-commit readout success collapses from ~93% (M_SUB=16, 30 restarts) to ~2% (M_SUB=1024, single
restart) even with NO noise at all. This generalizes the "K5/K6 basin/capacity wall" already on
file in `exp_resonator_dg_crosstalk_disentangler_v1`'s docstring: basin proliferation is severe not
only at K>=5, but at K=2 once the per-factor codebook M grows from resonator_factorization_v1's
M=30 to CSKG's required M_SUB~1024. A SOFT/linear readout (weighted-superposition estimate kept
REAL-VALUED and continuous between iterations, whole-vector normalized -- more faithfully mirroring
`exp_resonator_factorization_v1`'s actual FHRR structure than the hard-commit port originally
shipped) measured substantially better: 100% at M_SUB<=128, 85% at M_SUB=256, 57.5% at M_SUB=512,
~12-27% at M_SUB=1024 (clean, single-shot, 40 trials each). K_ENT=3 (M_SUB~79, needed for full
n_ent coverage at K=3) measured WORSE (6.7% at M_SUB=79) than K_ENT=2 at the equivalent coverage
requirement -- confirms higher K makes convergence harder per-M, consistent with
`resonator_factorization_v1`'s own K3=0.613/K4=0.047 at M=30. Multi-restart (soft-readout, up to 20
restarts, best-confidence selection) did NOT reliably improve M_SUB=1024 success (non-monotonic
15-30%) -- confidence is not a reliable discriminator of a correct vs spuriously-converged restart
at this scale, so multi-restart is NOT used in the shipped cell (would add cost without a
defensible reliability gain).

**Decision**: keep K_ENT=2/M_SUB=1024 (required for full n_ent=482,588 coverage, the real CSKG
entity space, not a subset) and ship the soft/linear readout (the measurably better,
literature-consistent fix) -- this is a genuine implementation-defect fix (matching the
already-validated FHRR resonator's actual structure), not a parameter retuned toward a favorable
outcome. **Consequence for interpretation**: even after the fix, `relevant_recall` (the full
decode pipeline) is expected to remain basin-convergence-limited at M_SUB=1024 REGARDLESS of store
crosstalk -- this is now a SEPARATE, already-characterized bottleneck from the crosstalk-capacity
question the cell was designed to answer. The oracle-unbind `relevant_in_shortlist_rate` (isolates
store crosstalk from search dynamics by construction, unaffected by this basin-convergence
limitation) is therefore promoted to the PRIMARY signal for the crosstalk-tolerance claim in the
final report, reported alongside (not instead of) the literal pre-registered `relevant_recall`
bands -- an honest mechanism decomposition, not a band substitution: the HARD-PASS/HARD-FAIL/
MIDDLE_BAND verdict in this pre-reg's Bands section still gates on `relevant_recall` as originally
specified.
