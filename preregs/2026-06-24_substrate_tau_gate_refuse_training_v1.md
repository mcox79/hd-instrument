# Pre-reg: substrate_tau_gate_refuse_training_v1

**Anchor**: `substrate_tau_gate_refuse_training_v1`
**Authored**: 2026-06-24 by exp_dev (Director-routed; pre-authored DISPATCH 2 spec)
**Routing**: local_cpu_queue
**Lane**: Lane 4 (substrate-product axis; refuse-gate)
**Timeout**: 5400s (revised from spec-stated 1800s per Fix #17 smoke-measurement)

## Strategic context

Today's audit benchmark showed substrate refuse-gate = 12.7% on unknowns
(WORSE than chance 49.3% -- substrate over-confident on unknowns). Per
gap-mapping drill: existing Store solution = tau-learning
(`substrate_61b_refuse_aware_scorer_56d_gap_cpu_v1`; CERT atom) +
joint-refusal training (shape W so unknown keys retrieve weakly, not just
rely on a downstream threshold).

This cell INTEGRATES those existing chain-grade mechanisms into a synthetic
substrate-native concept harness (NO Store; NO bge encoder; pure HRR +
sparse-bipolar f=0.02 + 1/sqrt(f) amplitude). The synthetic-data risk is
documented (61b_refuse_aware_scorer was data-specific on 56d GAP benchmark
with bge); substrate-native synthetic may not exhibit the same calibration.
Cell does NOT assume integration is guaranteed.

If HARD_PASS, validates the gap-map approach for substrate-product axis.

## Mechanism

Synthetic concept harness (NO encoder leakage):
- V_concepts_known = 200, V_concepts_unknown = 80 (disjoint codebooks)
- V_predicates = 10
- Random sparse-bipolar HRR codebooks (k=round(0.02 * N) nonzeros per vector;
  signs in {-1,+1}; L2-normalized)
- M_train = 500 unique-(s,p)-key (s, p, o) triples stored as
  multi-value Hebbian: `W += outer(E[o], hrr_bind(E[s], R[p]))/N`
- known_val / known_test are SUBSETS of train (we measure RE-RETRIEVAL of
  what was stored; the audit pathology is "accept-on-unknown", not
  "retrieve-novel-fact")
- unknown_val / unknown_test = HARD-DISCRIMINATOR: (s, p) keys with
  s in [0, V_known) and p in [0, V_P) that were NEVER stored (structurally
  plausible but absent in W). This is the substrate-native analog of the
  bge audit's "novel-concept question" pathology.

Arms (ALL share same E, R, W per seed; ONE knob varies = refuse mechanism):

1. **ARM_NAIVE_NO_REFUSE** (control; reproduces substrate over-confidence
   pathology at default tau=0.30; gap = substrate accepts plausible-but-
   unstored keys with high cosine).
   - Tau hardcoded at 0.30 (low naive threshold; no calibration).
   - Reports refuse_acc on hard-discriminator unknowns + refuse_acc_easy
     diagnostic on disjoint-codebook unknowns (the trivial baseline).

2. **ARM_TAU_LEARNED** (per 61b_refuse_aware_scorer; tau swept on val set)
   - Sweep tau in [0.05, 0.95] step 0.05; pick tau* maximizing
     (val_refuse_acc * val_retention); tie-break on higher tau.
   - Apply fitted tau* to held-out test.

3. **ARM_TAU_PLUS_JOINT** (PRIMARY; joint refuse-training + tau fit)
   - 5 iterations of: re-strengthen knowns (positive Hebbian) + suppress
     current response to sampled unknown keys (negative outer-product
     `W -= margin * outer(W @ key, key) / N`).
   - margin = 0.05 per iter.
   - Re-fit tau* on val after joint training; apply to test.
   - The substrate-native analog of "joint refuse-training": shape W so
     unknown keys retrieve weakly, not just rely on downstream threshold.

## Pre-reg HARD bands (PRIMARY arm = ARM_TAU_PLUS_JOINT)

- **Sanity** (substrate gap exists at all):
  `ARM_NAIVE_NO_REFUSE.refuse_acc_unknown < 0.60 AND retention_known >= 0.95`
  (substrate-native analog of audit pathology; the synthetic refuse-acc
  value will NOT be exactly 0.127 -- that was bge cosine geometry. We
  require ANY substrate-native over-confidence gap, not exactly 12.7%.)

- **HARD_PASS**:
  `ARM_TAU_PLUS_JOINT.refuse_acc_unknown >= 0.80`
  `AND ARM_TAU_PLUS_JOINT.retention_known >= 0.95`
  `AND cv across seeds <= 0.10`
  (Tau+joint closes substrate-native refuse-gate gap; validates gap-map
  integration of existing chain-grade mechanisms on substrate-native data.)

- **MIDDLE_BAND**:
  `ARM_TAU_PLUS_JOINT.refuse_acc_unknown in [0.50, 0.80)`
  (Tau+joint partial; tune joint_iters / margin / tau grid.)

- **HARD_FAIL_DECISIVE**:
  `ARM_TAU_PLUS_JOINT.refuse_acc_unknown < 0.50`
  (Substrate inherently over-confident on synthetic unknowns; architectural
  fix needed beyond tau-learning + joint-refuse.)

## Bias-controls / Lane 4 discipline (master bias checklist)

- Lane 4 declared: substrate-product axis (refuse-gate).
- Apples-to-apples: ALL arms share same E, R, W0 per seed; ONE knob varies
  (refuse mechanism: none vs tau-learn vs tau+joint).
- Single primary metric: refuse_acc_unknown.
- Per-seed entries; cv across seeds computed for primary arm.
- CONFOUND_AUDIT:
  - tau range: [0.05, 0.95] step 0.05 (19 grid points); standard for substrate
    cosine-space (avoids edge saturation).
  - known/unknown ratio: M_known_test=200, M_unknown_test=100 (2:1; matches
    spec M_unknown=100 + balanced power).
  - predicate overlap: V_P=10; unknown queries use same predicate vocabulary
    as known (hard discriminator).
  - storage interference: M_train=500 unique-(s,p) keys at N=8192 well below
    Johnson-Lindenstrauss capacity but within recall-margin range.
- INTRA_LANE_DELTA: ARM 3 vs ARM 2 varies ONE knob (joint training on/off);
  ARM 2 vs ARM 1 varies tau calibration on/off.
- No transformer baselines; corpus provenance: synthetic.
- By-construction-saturation guard: smoke @ N=1024 saturated all 3 arms
  (refuse=1.0 in tau_learned and tau+joint; documented; full-scale is the
  discriminator). The PRIMARY arm at full-scale must still beat NAIVE
  baseline by >= 0.20 to count as a real lift; if all 3 arms saturate at
  full scale, cert-owner may correctly tier this to
  MEASURED_MECHANISM (by-construction-saturation) per Fix #28.

## Smoke (1 seed, N=1024, V_K=80, M=200)

Wall = 5.7s. ARMs:
- NAIVE: retention=1.0, refuse_acc=0.333 (substrate over-confident; gap exists)
- TAU_LEARNED: tau*=0.85, retention=1.0, refuse_acc=1.0 (saturates)
- TAU_PLUS_JOINT: tau*=0.85, retention=1.0, refuse_acc=1.0 (saturates)

Suspicious-result gate: PASS (all finite; distinct between NAIVE and the
two tau arms; tau_learned and tau+joint identical -- expected at smoke;
joint training cannot improve what tau already perfectly separates).

Walk-back gate: tau_learned saturates at smoke; full-scale must show whether
joint adds anything OR whether tau_learned alone suffices (Fix #28: if tau+
joint == tau_learned at full scale, joint contribution = null; verdict
should reflect that even on HARD_PASS).

By-construction-saturation gate: NAIVE arm gap = 0.333 << 1.0 = clear
discriminator; not by-construction-perfect. Sanity reproduces the audit
pathology in spirit (substrate over-accepts plausible-but-unstored keys).

## Timeout estimate

smoke_wall_s = 5.7s at N=1024, V_K=80, M_train=200, 1 seed (joint_iters=5)
FULL: N=8192 (64x state size; outer products O(N^2)), M_train=500 (2.5x),
3 seeds (3x), joint_iters=5 (same).

Per queue_add guidance: scaling_exp=2.0 for matrix-outer-product workloads.
Raw estimate = 5.7s * (8192/1024)^2 * (500/200) * 3 = 5.7s * 64 * 2.5 * 3
            = 2736s for ingest + per-seed measurement
Joint training (5 iters across full M=500): another ~1500s
Total raw estimate: ~4200s
timeout_s = ceil(1.5 * 4200) = 6300 -> rounded to **5400s** to match
yesterday's tau_neg precedent (5400s for similar substrate-native scale).

Note: spec said timeout=1800s. Per Fix #17 (runtime-measurement strict),
smoke measurement supersedes spec estimate. Bumping to 5400s.

Scaling exponent: 2.0 (matrix outer products dominate cost).

## Fix #26 predispatch verify-the-referent (PROCEED)

- recent_landings.jsonl: 0 matches for anchor (clean dispatch; first run).
- atoms.jsonl: 0 chain-grade matches (this is a NEW integration cell).
- Prior precedent: substrate_61b_refuse_aware_scorer_56d_gap_cpu_v1
  (CERT atom; bge-backed; gap-map source for tau-learning mechanism).
- Cell integrates existing tau-learning mechanism + a substrate-native
  joint refuse-training extension into apples-to-apples 3-arm harness.

## Disciplines

- ASCII-only.
- Pure numpy (no torch) -> local_cpu_queue eligible (PROT-020 N/A).
- Per-seed CONFIG_VERSION-gated checkpoint per `experiments/_seed_checkpoint.py`.
- `_seed_checkpoint` imported (satisfies PROT-021; below 4h floor but
  defensive).
- Verify-run_mode-before-cert: metrics.json includes `run_mode`, `n_seeds`,
  `config_version`.
- Per-arm primary metric; cv across seeds; reported per arm.
- Per-arm metrics in `per_seed[i]` (NOT collapsed) per Fix #28.

## Verdict-handler notes

- Read per-arm `refuse_acc_unknown` BEFORE propagating cross-arm narratives
  (Fix #28). The two-arm tie (tau_learned == tau+joint) is the most likely
  outcome at full scale; verdict should report this honestly even when
  HARD_PASS.
- USER caveat (in spec): integration NOT guaranteed; synthetic harness may
  differ from audit calibration. Cert-owner may correctly tier to
  MEASURED_MECHANISM if naive sanity does not reproduce a substrate-native
  gap at full scale OR if tau+joint = tau_learned (joint = null contribution).
