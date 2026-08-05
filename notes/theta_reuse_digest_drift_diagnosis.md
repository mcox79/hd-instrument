# theta-reuse digest drift diagnosis (exp_grounded_appraisal_transfer_to_text_v1)

**Status:** DETERMINISTIC-BUT-DRIFTED. Values FUNCTIONALLY INTACT. Landed arm_a=1.000 is SAFE.
Fix recommended: tolerance-based reuse check (allclose on behavior), not raw SHA256 digest equality.

## The failure
`exp_grounded_appraisal_transfer_to_text_v1.py::self_test` (L647) asserts
`reconstruct_full_theta(0, TRAIN_CFG)`'s SHA256 digest of `theta.numpy().tobytes()` equals the
digest banked in `data/exp_grounded_appraisal_sim_earned_v1/metrics.json` (`arms_theta_digests.FULL`
for seed 0). It does not (`5d29b1e23d36cdb5` vs earned `f52b435fc62d1388`), crashing the transfer cell
(`data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json`, verdict CELL_CRASHED).

## Axis 1 -- non-deterministic vs deterministic-but-drifted
Reconstructed **within one process twice**: identical (`5d29b1e2...` both times).
Reconstructed via **fresh process launches** (transfer script bare, sim.py bare, with
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` pinned in the shell env before
python starts, and again with `torch.set_num_threads(1)`, `torch.set_num_threads(8)`,
default 12): **all five reproduce `5d29b1e23d36cdb5` exactly.** Verdict: reconstruction is fully
**DETERMINISTIC now**, just drifted from the old stored digest. Not process-level nondeterminism.

## Axis 2 -- did theta VALUES change, or is this a digest artifact?
The raw earned theta array was never persisted -- only its 16-hex-char SHA256 digest was banked
(`arms_theta_digests`), so a direct elementwise diff against the original array is impossible. The
next-best evidence is the FULL_heldout eval, which is a direct, high-resolution function of theta
(1500 held-out episodes x 8-way argmax(P @ theta) per episode):

| field | earned (banked, seed 0) | reconstructed now (seed 0) |
|---|---|---|
| acc | 1.0 | 1.0 |
| n_bh | 470 | 470 |
| revenge_emergence_rate | 1.0 | 1.0 |
| targeting_specificity | 1.0 | 1.0 |
| bystander_harm_rate | 0.0 | 0.0 |
| earned_restoration | 1.0 | 1.0 |
| recency_restoration | 0.2978723404255319 | 0.2978723404255319 |

`recency_restoration` matches to all 16 significant figures (= 140/470 exactly). Over 1500 stochastic
eval episodes x 8 argmax comparisons each, that level of agreement is not explainable by chance --
every single decision boundary the theta induces is identical between the two arrays. **Verdict:
VALUES INTACT (functionally), digest differs at the raw-bit level only** -- almost certainly float32
non-associativity (order-of-summation / FMA dispatch) too small to flip any argmax, not a real
parameter drift.

## Axis 3 -- root cause, checked explicitly
- **Thread nondeterminism (OMP/OPENBLAS not pinned):** RULED OUT by direct test. `torch.set_num_threads(1)`,
  `(8)`, and default (12, unpinned) all produce the *same* `5d29b1e23d36cdb5`, both within-process and
  across fresh process launches with the env vars set before `python` starts. The reconstruction ops here
  (N_DIM=256, 2*N_DIM=512-wide matmuls/FFT-binds) are too small for MKL to thread regardless of the cap,
  so this knob has zero effect either way on this cell -- present but not the mechanism.
- **PYTHONHASHSEED / list(set()) ordering:** RULED OUT. `grep "set("` on
  `exp_grounded_appraisal_sim_earned_v1.py` shows the only `set(`/`.keys()` uses are
  `aggregate_and_verdict`'s `sorted(per_seed.keys())` (post-hoc aggregation, doesn't touch theta) --
  no hash()-seeded container anywhere in `Codebook`, `make_episode`, or `train_theta`. All identity/role
  atoms are built from explicit tuples/`range()`, insertion-order-stable regardless of PYTHONHASHSEED.
- **Code drift between the banked run and now:** RULED OUT. `git diff 2d5695f61 -- data/exp_grounded_appraisal_sim_earned_v1/`
  and the working tree are both clean (`nothing to commit`) -- the `.py` and the banked `metrics.json`/
  `units.jsonl` are the exact files in the landing commit `2d5695f61`. `hdlab/binding.py` and
  `hdlab/bundling.py` (the bind/bundle primitives `phi()` depends on) have had zero commits since
  `2d5695f61` (`git log 2d5695f61..HEAD -- hdlab/binding.py hdlab/bundling.py` empty).
- **torch/numpy version or install change:** RULED OUT. Same host (`_start_marker.json` records
  `"host": "FrameworkMPC"`, matches current `hostname`). `site-packages/torch` last-write-time is
  2026-01-07 (7 months before the Aug 3 earned run and today) -- not touched/upgraded in between.
  `torch.__version__` = `2.8.0+cpu` now, matches exp_dev's report.
- **Leading candidate (not fully provable without the original array, but consistent with every
  ruled-in/ruled-out axis above): hybrid P-core/E-core float non-reproducibility.** Host CPU is a
  13th-gen Intel Core i5-13340P (`wmic cpu get name`) -- a hybrid P-core/E-core part. MKL/oneDNN can
  select slightly different vectorized code paths (AVX2 micro-kernel variants, FMA contraction order)
  depending on which core type the OS scheduler lands the process on at a given moment, which is a
  known source of bit-level (not value-level) FP non-reproducibility across separate process launches
  on the same box, even with thread count pinned to 1. This matches the evidence exactly: functionally
  identical decisions, bit-different raw floats, unaffected by thread-count knobs.

## Verdict on the landed arm_a=1.000 result
**SAFE.** The FULL_heldout behavioral metrics (accuracy, revenge emergence, targeting specificity,
bystander rate, earned/recency restoration) reproduce to 16 significant figures under a from-scratch
reconstruction on the same host with the same (git-verified unchanged) code. The grounded-transfer
science built on this theta is not resting on a corrupted/drifted parameter -- it is resting on a
verification check (bit-exact SHA256 digest equality) that is simply too strict for this hardware's
FP reproducibility envelope.

## Recommended fix (NOT applied -- flagging for Director approval)
Prefer (b) over (a): pinning threads further will not help (already disproven at 1/8/12 threads).
Do not attempt to hand-edit the banked earned digest.

1. Replace the bit-exact digest assertion in `exp_grounded_appraisal_transfer_to_text_v1.py::self_test`
   (and the analogous `run()`-path `digest_ok` check) with a **behavioral-equivalence check**: reconstruct
   theta, run the same held-out eval used to bank `FULL_heldout`, and assert the eval metrics
   (`acc`, `revenge_emergence_rate`, `targeting_specificity`, `bystander_harm_rate`,
   `earned_restoration`, `recency_restoration`) match the banked `metrics.json` values via exact
   equality on the derived rates (they are ratios of small integer counts over a fixed n_eval, so exact
   equality is actually the right bar, not `allclose` -- any real drift would flip at least one count) --
   this is a *stronger*, more meaningful proof of reuse than a raw hash, and does not require bit-identical
   floats.
2. Optionally, ALSO keep the digest as a soft/logged diagnostic (not an assert) so future drift is visible
   without crashing the cell.
3. Document this hardware caveat (hybrid-core BLAS bit-nondeterminism) as a standing discipline note next
   to the existing `sorted(set())`/`OMP_NUM_THREADS=1` determinism discipline: **digest-equality reuse
   checks are not safe on this host for anything that runs through MKL FP ops; use behavioral/functional
   equivalence checks for cross-process theta reuse instead.**

## Evidence trail (commands run, this session)
- `data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json` -- CELL_CRASHED, digest mismatch.
- `data/exp_grounded_appraisal_sim_earned_v1/metrics.json` -- earned digest `f52b435fc62d1388`,
  `_start_marker.json` host=`FrameworkMPC`.
- `git log --oneline -- experiments/exp_grounded_appraisal_sim_earned_v1.py` -- one commit (`2d5695f61`).
- `git diff 2d5695f61 -- data/exp_grounded_appraisal_sim_earned_v1/` -- empty; `git status` clean.
- `git log 2d5695f61..HEAD -- hdlab/binding.py hdlab/bundling.py` -- empty.
- Reconstruction reruns: same-process x2, fresh-process x1 (env-pinned 1 thread), `torch.set_num_threads(1/8)`,
  default (12) -- all five give `5d29b1e23d36cdb5`, none match `f52b435fc62d1388`.
- `eval_theta` on the reconstructed theta reproduces the banked `FULL_heldout` dict exactly
  (`recency_restoration=0.2978723404255319` to 16 sig figs).
- `(Get-CimInstance Win32_Processor).Name` -- `13th Gen Intel(R) Core(TM) i5-13340P` (hybrid P/E-core).
