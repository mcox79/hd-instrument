# PRE-REG ADDENDUM: exp_structured_code_vs_flat_bag_c3_v1 (graded-comparator bug fix, RE-RUN)

**Filed:** 2026-08-15, BEFORE the re-run executes. **Author:** exp_dev (diagnostic-dispatch task).
**Supersedes, for this one point only:** section 8 of
`preregs/2026-08-14_exp_structured_code_vs_flat_bag_c3_v1.md` ("Does not modify
`hdlab/reading_grounding_loop.py`"). Everything else in that pre-reg (harness identity, arms, n,
seeds, bands, control battery) is UNCHANGED and re-applies verbatim to this re-run.

## 0. What happened

The 2026-08-14 run (`data/exp_structured_code_vs_flat_bag_c3_v1/metrics.json`, verdict
`VOID_PLUMBING_SELF_RETRIEVAL`) failed its own positive control: known-answer self-retrieval
`SR_STRUCT=0.6712 (n=292)` below the pre-registered `SELF_RETRIEVAL_FLOOR=0.70`, while
`SR_BASE=0.7860 (n=299)` cleared it. Per the pre-reg's own instrument-sanity band, that voids every
downstream floor comparison in that run -- no structure-vs-flat conclusion was or is drawn from it.

## 1. Diagnosis (verified on disk, not inferred)

`hdlab/reading_grounding_loop.py` has a module-wide switch, `GRADED_COMPARATOR` (line 103,
default `True` unless `HD_GRADED_COMPARATOR=0`), flipped live 2026-08-14. When ON, per-occurrence
context vectors and the ConceptSpace accumulator keep their full real-valued magnitude instead of
being sign-quantised to bipolar; `_selftest_graded_comparator_default` (line 2125) asserts this
holds coherently across "four sites": `context_vector`/`context_vector_masked` (graded kwarg),
`ConceptSpace.anchor_matrix`, `ConceptSpace.bundle`, and `ReadoutConfig().graded_query`.

`StructuralEncoder.vector()` (line 411, the STRUCTURED arm's per-occurrence encoder) was NOT one of
those four sites. It hardcoded `out = np.sign(acc); out[out==0]=1.0` unconditionally, built
2026-08-13 (one day before the graded default flip) and never updated. Net effect under the live
default: `A1_BASE` (`context_vector_masked`, graded=True) keeps full magnitude through every stage
of the pipeline (no `np.sign` anywhere in its path); `A2_STRUCTURED` had its per-occurrence vector
prematurely quantised to bipolar INSIDE `encoder.vector()`, before `ConceptSpace.observe()` ever
saw it -- discarding analog information before any cross-occurrence bundling could average it out,
at a measured mean of only 2.82 dependency features per encoding (a handful of near-orthogonal
bipolar terms sign'd per single occurrence is a lossy quantisation). This is the same
"ternary/bipolar zero-convention mismatch" class the `context_vector` docstring already documents
as having cost ~30% of a prior smoke-scale delta (`grounding_acquisition_loop.py:140-149`) -- not
applied to this encoder when the switch flipped.

This is a graded-vs-quantised confound, not evidence about structured-vs-flat coding: BASE and
STRUCT were never on the same normalisation convention in the voided run.

## 2. Fix (minimal, additive, scoped)

`StructuralEncoder.vector()` (`hdlab/reading_grounding_loop.py`) now returns the raw accumulated
`acc` when `GRADED_COMPARATOR` is True, matching `context_vector`'s contract exactly, and falls
back to the pre-existing sign-quantised behavior when the switch is off (`HD_GRADED_COMPARATOR=0`)
-- byte-identical to the prior run in that mode. `_encode_from_features` in
`experiments/exp_structured_code_vs_flat_bag_c3_v1.py` (the salted projection-draw helper) was
changed identically, to stay bit-consistent with `StructuralEncoder.vector()`.

No other code in `hdlab/reading_grounding_loop.py` changed. `StructuralEncoder` remains additive /
default-off (nothing on the live path calls it unless a caller explicitly builds one); this fix
only makes it consistent with the switch it was already documented as needing to follow.

## 3. Verification before re-run (done, evidence below)

- `--self-test` (local `_encode_from_features` reproduces `StructuralEncoder.vector()`
  byte-for-byte on the 32-d synthetic fixture): **PASS**.
- `hdlab/reading_grounding_loop.py` full self-test suite (`_run_all_selftests`, includes
  `_selftest_graded_comparator_default` and `_selftest_structural_unbound_matches_context_vector`):
  **ALL SELF-TESTS PASSED**, no regression from the fix.
- SMOKE run (`--smoke`, `data/exp_structured_code_vs_flat_bag_c3_v1_smoke/metrics.json`):
  `SR_BASE=0.8154 (n=298, ok=true)`, `SR_STRUCT=0.7875 (n=287, ok=true)` -- **both now clear the
  0.70 floor**, versus `SR_STRUCT=0.6712` before the fix. (Smoke's `HARNESS_MISMATCH_STOP` on the
  0.0480 exact-reproduction gate is EXPECTED and uninformative at smoke scale -- that gate is only
  meaningful at the full corpus/`MAX_ITEMS`, per the original pre-reg's own design; it is not a
  fix-quality signal.)

## 4. Re-run bands (verbatim from the 2026-08-14 pre-reg section 6, restated for clarity)

Unchanged. In order: (1) HARNESS-INTEGRITY GATE `A1_BASE.hit_at_1 == 0.0480` within `1e-9` --
A1_BASE is untouched by this fix (STRUCT-only change) so this is expected to reproduce exactly as
before; (2) INSTRUMENT SANITY `SR_BASE >= 0.70 AND SR_STRUCT >= 0.70` -- now the primary thing this
re-run tests at full scale; (3) if both gates pass, read `STRUCTURE WINS` /
`STRUCTURE DOES NOT HELP` / `STRUCTURE HURTS` off the pre-registered deltas exactly as written in
the 2026-08-14 pre-reg section 6, with the full control battery (scramble, frequency, orthographic,
between-projection-draw-spread, paired bootstrap CIs) already implemented in the cell, unchanged by
this fix.

## 5. What this addendum does NOT authorize

Still read-only on `data/foundation/*`. Still `CTX_D=256` (no d=256->1024 change). Still does not
wire anything -- a verdict here (even `STRUCTURE_WINS_CLEARS_FLOOR`) is a measurement, not a wiring
decision. If `A1_BASE` fails to reproduce 0.0480 exactly in the full re-run (it should not, since
only the STRUCT path changed), STOP per the original harness-integrity gate and report the
harness mismatch without drawing any structure-vs-flat conclusion.

## 6. Launch

Full run (`experiments/exp_structured_code_vs_flat_bag_c3_v1.py`, no `--smoke`) launched via
PowerShell `Start-Process` (detached, separate stdout/stderr, PID file), expected wall time
comparable to the voided run's `elapsed_s=2622.32` (~44 min) since the fix removes a `np.sign` call
per occurrence, not a algorithmic-complexity change. Per-unit checkpoint already implemented in the
cell (`tools/exp_checkpoint.py`, chunks of 500 items / 250 lemmas / per projection-draw), so a
killed run resumes rather than restarting.
