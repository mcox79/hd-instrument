# Pipeline Complete: g1_substrate_native_generation_v1

**Date:** 2026-06-22 (UTC)
**Disposition:** HARD_PASS (chain-grade candidate; honest-scope flag below)
**Cell commit:** 72558958
**Full metrics commit:** 72558958 (same commit; full run landed local)
**Cert_ledger row hash:** (Skunkworks fills after A5 write)
**Atom ID candidate:** `research::T1/EXP_g1_substrate_native_generation_v1`

## Headline (plain English first)

c3 (CERT 585->586, landed today) gave the substrate sequence STORAGE. g1
(this cell) extends to sequence GENERATION. Tested whether the substrate
can autoregressively generate a coherent sequence of states using ONLY
substrate primitives (c3's SequenceMatrix S + Langevin noise + codebook
NN-cleanup), with ZERO LLM forward calls anywhere. The 4-arm discriminator
(NONE / S_ONLY / S_LANGEVIN / S_LANGEVIN_CLEANUP) cleanly separates: raw
retrieval drifts (S_ONLY=0.375 at T=8), Langevin without cleanup is worst
(S_LANGEVIN=0.127), but the full mechanism with codebook attractor cleanup
hits perfect-by-construction (1.000) at this scale. **Cleanup is the
load-bearing complement to S + Langevin.** Substrate now does both
retrieval (U1, c3) AND generation (g1).

## Key Numbers (re-derived from per_unit -- not from verdict_msg)

All 3 seeds (7, 17, 23), N_DIM=4096, K_SEQ=20, N_SEQ=10, T_GENS=[1,4,8,16]:

| Metric | Arm 4 value | HARD_PASS bar | PASS? |
|---|---|---|---|
| trajectory_coherence(T=8) | 1.000 (cv=0.000) | >= 0.60 | YES |
| trajectory_coherence(T=1) anchor | 1.000 | sanity bracket | YES |
| trajectory_coherence(T=16) | 1.000 | super-pass bar 0.50 | YES (super-pass) |
| novelty_ratio | 401.0 | >= 1.5 | YES |
| refuse_OOD | 1.00 | >= 0.90 | YES |
| refuse_in_corpus | 0.00 | <= 0.10 (gate calibration) | YES |
| n_distinct_visited(T=8) | 154 (range 149-158) | NOT collapsed | YES (not fixed-point) |
| delta(Arm4 - Arm1) at T=8 | 0.995 | >= 0.40 | YES |
| cv across 3 seeds | 0.000 | <= 0.07 | YES |
| substrate_only_gate (n_llm) | 0 | == 0 | YES |
| W_unchanged_by_generation | True (all arms) | True | YES |

4-arm discriminator at T=8 (the Fix #16 CAN-fail regime):
- NONE = 0.005 (control; random codebook indices)
- S_ONLY = 0.375 (raw S retrieval, no Langevin, no cleanup; drifts)
- S_LANGEVIN = 0.127 (Langevin without cleanup; noise destroys coherence)
- S_LANGEVIN_CLEANUP = 1.000 (full mechanism)

Spread = 0.005 vs 1.000; mechanism is load-bearing.

## Inline Disposition

**HARD_PASS** by pre-reg bands (all 9 checks PASS; substrate-only gate +
W-invariant both clean; verify-off-DATA reproduces every cited number
exactly).

Pre-reg bands (deflated from brain-drill #4 L4): cell honors them.

**HONEST-SCOPE FLAG for Skunkworks landed-VET:** at N_DIM=4096 with only
190 pair-writes (N_SEQ * (K_SEQ - 1) = 10 * 19 = 190), the substrate is FAR
under its ~327-pattern capacity at this dim. This produces a result that's
operating near by-construction-saturation: coh=1.000 exactly, cv=0.000
exactly, novelty_ratio=401 (smoothing-prior driven because random-other-set
overlap is rare in small corpora). The 4-arm discriminator-regime still
shows real signal -- the per-step mechanism IS load-bearing (S_ONLY=0.375
vs S_LANGEVIN_CLEANUP=1.000 is a 0.6 spread that proves cleanup is the
complement) -- but the wide HARD_PASS margin warrants a capacity-saturation
follow-on probe (scale N_SEQ up until S_LANGEVIN_CLEANUP starts to fall
below 0.60; that's the discriminator-regime that proves the mechanism is
robust, not just saturated). This is the "by-construction-saturation
tiering" discipline (associative-memory-noise-scaling-bug META).

**Recommended landed-VET probe:** Skunkworks ratifies-or-tiers based on
whether the per-cell 4-arm spread (which IS the discriminator) is sufficient
chain-grade evidence at this corpus, OR whether the by-construction-saturation
pattern warrants a g1_capacity_sweep follow-on before A5-gated atomize.

## Per-Unit Reconciliation

Re-derived directly from `data/exp_g1_substrate_native_generation_v1/metrics.json`:

```
total per_unit entries: 12 (4 arms x 3 seeds)
seeds: [7, 17, 23]
arms:  ['NONE', 'S_ONLY', 'S_LANGEVIN', 'S_LANGEVIN_CLEANUP']

Arm 4 (S_LANGEVIN_CLEANUP) T=8 per-seed: [1.0, 1.0, 1.0]
  mean=1.0000  cv=0.0000

Arm 1 (NONE) T=8 per-seed: [0.00625, 0.00625, 0.003125]
  mean=0.0052

delta arm4-arm1: 0.9948

Arm 4 refuse_OOD per-seed: [1.0, 1.0, 1.0]
Arm 4 novelty(T=8) per-seed: [401.0, 401.0, 401.0]
Arm 4 distinct_visited(T=8) per-seed: [155, 158, 149]
W_unchanged all 12 per_unit: True
n_llm sum across all seeds: 0
```

Numbers reproduce exactly. No miscite.

## Honest Scope

- Phase 1 corpus: synthetic bipolar keys (matches c3 / c1 / a8 substrate-
  primitive-isolation pattern). Position-binding via the codebook itself
  (each state is a unique codebook entry; no explicit clock vector).
- N_DIM=4096, 190 pair-writes (FAR under substrate's ~327 capacity at this
  dim); 3 seeds, 40 probes per (arm, T), 40 OOD probes per arm.
- The HARD_PASS proves: (a) the harness works end-to-end with ZERO LLM, (b)
  the c3 SequenceMatrix S primitive is reusable for autoregressive
  generation, (c) the per-step composition (S + Langevin + codebook cleanup)
  works as advertised, (d) the 4-arm discriminator-regime resolves: cleanup
  is the load-bearing complement to S + Langevin.
- What this DOES imply: substrate can generate ON sequences it has stored.
  The structural moat over LLMs (refuse-gated, no context window, O(T*N_DIM)
  not O(T^2)) is mechanically demonstrated.
- What this does NOT imply yet: substrate generates novel COMPOSITIONS not
  in the training corpus. The "novelty" measure (401) is smoothed-prior
  driven by sparse codebook overlap; a stronger novelty test is a Phase 2
  cell with a held-out continuation graph + heldout-vs-OOD discriminator.
- Phase 2 (deferred, conditional on landed-VET ratify): explicit HVC clock-HV
  binding (Karuvally L2 ablation) + Pythia-encoded FB15k chains (brain-drill #4
  full corpus) + capacity sweep (the saturation discriminator).

## Corpus-Provenance

- Corpus: synthetic_bipolar_keys_sequences (in-cell-generated; mirrors c3 /
  c1 / a8)
- allow_synthetic=True (CORRECT for substrate-primitive isolation; same as c3)
- Data integrity: in-cell-generated from `np.random.RandomState(seed)`;
  deterministic + reproducible per seed.

## Discipline Compliance

- ASCII-only: YES (cell + prereg + this note all ASCII)
- Pre-reg per envelope-fail-bands: YES (HARD_PASS / MIDDLE_BAND / HARD_FAIL
  bands all locked in pre-reg before run)
- Smoke gate FIRST: YES (smoke ran in 0.5s; HARD_FAIL on T_GENS mismatch
  expected; harness PASS)
- REMOTE VERIFY post-ship: N/A (no remote dispatch -- cell landed locally;
  see "Dispatch decision" below)
- No padding experiments: YES (the local run IS the cell-land; not running
  a redundant remote-cpu cycle)
- Pause flag re-check pre-dispatch: PASSED (flag absent at session start
  AND before final commit)
- Commit before referencing in dispatch: N/A (no remote dispatch)
- No hard-coded paths: YES (cell uses REPO root)
- Pre-reg-direction-must-honor-intent (Fix #5): YES (Arm 4 > Arm 1, large
  positive delta, matches intent)
- Verify-the-referent on flattering result: APPLIED (honest-scope flag for
  by-construction-saturation; re-derived all cited numbers from per_unit;
  NOT substituting recomputed values for measured ones).

## Dispatch decision (HONEST: no remote dispatch needed)

The pre-reg routed g1 to remote_cpu_queue with a ~30-60min wall estimate
(per the task spec). The Fix #17 single-seed near-full wall measurement
discovered the actual full 3-seed wall is ~2 minutes on the laptop CPU
(np matmul on N_DIM=4096 keys is much faster than the task-spec estimate
which was built around c3's K=20 N_SEQ=10 wall). At this wall, running
the cell locally + landing HARD_PASS directly is the honest path; routing
to remote_cpu_queue would be busy-work (NO BUSY WORK rule). The Pipeline
Template's Section 1e empirical measurement caught this; the spec's
estimate was 15-30x too high.

This means: the cell IS dispatched and HAS landed. The "dispatch" in the
hd-instrument cert-trail sense was: cell author + smoke gate + Fix #17 wall
measurement + full-config local run + canonical metrics path + commit.
All steps complete.

## Cert Ledger Row (for Skunkworks A5 window)

Skunkworks: copy this into your atomize tool's A5 window.

```python
from tools.cert_ledger_writer import build_chain_grade_ruling_row, append_cert_ledger_row
row = build_chain_grade_ruling_row(
    atom_id='research::T1/EXP_g1_substrate_native_generation_v1',
    cell_commit='72558958',
    verdict='HARD_PASS',
    notes_path='notes/g1_substrate_native_generation_pipeline_complete_2026-06-22.md',
    metrics_path='data/exp_g1_substrate_native_generation_v1/metrics.json',
    cv=0.000,
    cert_class='pre_reg_pass',
    atomized_by='skunkworks',
    note='exp_dev_g1_substrate_native_generation_chain_grade_with_by_construction_saturation_flag',
)
hash = append_cert_ledger_row(row,
    expected_cert_n_pre=<CURRENT_CERT_N>,    # 586 per the substrate state? skunkworks verify
    expected_cert_n_post=<EXPECTED_CERT_N_POST>,  # 587 if ratified
)
print("row_hash:", hash)
```

**Note to Skunkworks (A5-gate decision):** the by-construction-saturation
flag means you may legitimately tier this as MEASURED_MECHANISM rather than
PRE_REG_PASS if the saturation concern is load-bearing in your judgment.
Either ruling is defensible. The cell + pre-reg + numbers stand
independently of the cert-class call; routing-to-Research for a
capacity-saturation follow-on probe is the right next step REGARDLESS of
the cert-class decision.

## 2x-Revival Angle (none needed -- HARD_PASS)

N/A: HARD_PASS by all bands. Routing for follow-on:

**Skunkworks landed-VET ratify-or-tier decision** (NOT a 2x-revival; a normal
cert-trail step):
- Option A: ratify as chain-grade (PRE_REG_PASS), atomize, CERT 586->587.
  The 4-arm discriminator-regime IS the C5/Fix #16 discriminator and it
  PASSED cleanly; saturation concern is for follow-on cells, not this one.
- Option B: tier as MEASURED_MECHANISM (delta=0 atom), route to Research
  for a g1_capacity_sweep / g1_pythia_corpus follow-on that operates in a
  CAN-fail regime; only ratify after a non-saturating discriminator
  reproduces the HARD_PASS bands.

**Research follow-on (regardless of A vs B):**
- g1_capacity_sweep_v1: vary N_SEQ in {10, 50, 100, 200, 500} at N_DIM=4096;
  find the regime where S_LANGEVIN_CLEANUP coh(T=8) drops below 0.60 (the
  capacity-saturation discriminator). This is the brain-drill #4 g1b cell
  that the pre-reg already flagged as the rescue route.
- g1_pythia_fb15k_corpus_v1: re-run g1 on Pythia-encoded FB15k entity chains
  (brain-drill #4 L4 corpus); harder test because real encodings have
  crosstalk; this is the "is it the substrate or the synthetic-bipolar
  perfection" discriminator.

## Asks

- **Skunkworks:** please run independent landed-VET (re-derive from per_unit;
  verify W_unchanged + n_llm == 0 invariants; ratify or tier inline
  disposition; do A5-gated Store write). Honest-scope flag is yours to weigh.
- **Research / Director:** please consider routing the capacity-saturation
  follow-on (g1_capacity_sweep_v1) as the next g-family cell. Brain-drill
  #4's g1b diagnostic + g2 hierarchical conditional cells already
  pre-registered as the natural next steps.
- **Orchestrator:** no dispatch action needed (cell landed locally).

## Artifacts

- Cell: `experiments/exp_g1_substrate_native_generation_v1.py` (commit 72558958)
- Pre-reg (deflated bands): `preregs/2026-06-22_g1_substrate_native_generation_v1.md` (commit 72558958)
- Pre-reg (full L1-L5 source-of-truth): `notes/research_brain_generation_cerebellar_forward_prediction_5x_drill_2026-06-22.md`
- Smoke metrics: `data/exp_g1_substrate_native_generation_v1_smoke/metrics.json`
- Full metrics: `data/exp_g1_substrate_native_generation_v1/metrics.json` (commit 72558958)
- Composes with: `hdlab/sequence_memory.py` (c3 SequenceMatrix; CERT 585->586)

---

*Cell-author / dispatcher: exp_dev pipeline (Opus 4.7 1M context), 2026-06-22.*
