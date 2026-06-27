# Dispatch request: 2 cells (M-CFU + multihop M2+M3+M1 5-arm)

From: exp_dev
To: orchestrator
Date: 2026-06-27
Commit: d3b84db3 (bundled; 4 files; 2738 insertions)
Pause flag: NOT present (verified)
Routing: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive; harness-DENIED
         push constraint => orchestrator dispatches via queue_add.sh)

---

## Cell 1: edge_importance_v5_CFU_counterfactual_utility_v1

Cell name (HDLAB_EXP_NAME): `edge_importance_v5_CFU_counterfactual_utility_v1`
Script: `experiments/exp_edge_importance_v5_CFU_counterfactual_utility_v1.py`
Prereg: `preregs/2026-06-27_edge_importance_v5_CFU_counterfactual_utility_v1.md`
Queue: `remote_cpu_queue`
Recommended --timeout: `1800` (per-seed ~15-20s estimate; 3 seeds; 6x buffer
       for queue contention / cold start / data ingestion)

Dispatch command:
```bash
bash tools/orchestrator/queue_add.sh remote_cpu_queue \
  edge_importance_v5_CFU_counterfactual_utility_v1 \
  experiments/exp_edge_importance_v5_CFU_counterfactual_utility_v1.py \
  preregs/2026-06-27_edge_importance_v5_CFU_counterfactual_utility_v1.md \
  1800
```

Why this cell: Drill 4 rank-1 backup mechanism (M-CFU). v1-v4 edge-
importance (PageRank-centrality + retrieval-trace + ultrametric-coreness +
NREM-replay-modulated-trace) all converged MIDDLE_BAND because they're all
smooth functions of H[i,j] which inherits degree-skew. M-CFU sources
importance from a categorically orthogonal axis: ablation recall delta
against held-out probe set (Tonegawa optogenetic engram-silencing analog;
chain-grade in neuroscience). P_deflated=0.50 (cap-honored).

HARD_PASS bands:
- sel_unretr asymmetry (RAND - CFU on UNRETRIEVED recall) >= 0.15
- cor(CFU_importance, |W|) < 0.30 (META_RULE_F fairness)
- Mechanism fires (n_downscaled > 0, n_ablations_evaluated > 0,
  cfu_variance > 0)
- COMP over CFU_ONLY: combined sel >= cfu_sel + 0.03

4 arms x 3 seeds = 12 arm entries cardinality_ok (D4).

Self-test confirmed (local --self-test PASS): cohort leave-K-out ablation
actually hurts held-out probe recall; composition produces different
prune set than singles; alpha=2.148 (high-alpha regime per v3/v4 anchor).

---

## Cell 2: multihop_barrier1_M2_M3_M1_combined_5arm_v1

Cell name (HDLAB_EXP_NAME): `multihop_barrier1_M2_M3_M1_combined_5arm_v1`
Script: `experiments/exp_multihop_barrier1_M2_M3_M1_combined_5arm_v1.py`
Prereg: `preregs/2026-06-27_multihop_barrier1_M2_M3_M1_combined_5arm_v1.md`
Queue: `remote_cpu_queue` (CPU-feasible per drill estimates; numpy-only;
       no torch / no GPU required)
Recommended --timeout: `21600` (6 hr; per drill estimate ~4-5 hr full run
       with 1.5x buffer; matmul-bounded at N_DIM=8192)

Dispatch command:
```bash
bash tools/orchestrator/queue_add.sh remote_cpu_queue \
  multihop_barrier1_M2_M3_M1_combined_5arm_v1 \
  experiments/exp_multihop_barrier1_M2_M3_M1_combined_5arm_v1.py \
  preregs/2026-06-27_multihop_barrier1_M2_M3_M1_combined_5arm_v1.md \
  21600
```

Why this cell: META_BARRIER_1 (atomized 2026-06-25) 4-prior-refute on
multi-hop closure beyond 2 hops. Drill 4 (2026-06-27) identified 3
categorically novel mechanisms across 3 independent error-compounding
layers: M1 readout (Grover post-hoc amplification, sqrt-V_C speedup),
M2 structural (NREM-replay-compact shortcut creation), M3 per-hop
primitive (stabilizer-vector bind, enzyme analog). ARM_COMBINED stacks
all 3.

HARD_PASS bands:
- ARM_COMBINED depth-5 mean top1 >= 0.65 (META_BARRIER_1 BROKEN)
- ARM_BASELINE depth-5 in [0.105, 0.185] (regime sanity rail; reproduces
  4-prior-refute regime; otherwise cell uninterpretable)
- cardinality_ok: 5 arms x 3 seeds x 4 depths = 60 entries

HARD_FAIL_META_BARRIER_1_NEGATIVE: COMBINED < 0.30 AND individual lift
< 0.05 => adopt M5 honest-acceptance framing (substrate is structurally
2-hop-permanent; external orchestration for multi-hop).

5 arms x 3 seeds x 4 depths = 60 arm entries cardinality_ok (D4).

Self-test confirmed (local --self-test PASS): shortcut atoms actually bind
into W_aug (querying compact_p on top-freq start retrieves correct end);
Grover amplification grows candidate-set probability mass; per-hop
stabilizer fit runs end-to-end; relation-range estimator builds masks
correctly.

---

## Pre-flight verification (exp_dev side)

- Both cells: ASCII-only; no unicode; no em-dashes; no emojis (verified).
- Both cells: --self-test PASS at module-import time; --self-test exits 0.
- Both cells: D3 no-silent-except wrapped (each arm + setup phase).
- Both cells: D4 cardinality_ok pre-reg fields explicit + verdict check.
- Both cells: D1 discriminator-must-survive-scale (CFU @ FULL N=512;
  multihop @ FULL V_C=200 / FULL n_chains_train=500).
- Both cells: D2 smoke-fires-discriminator (CFU smoke at full-N requires
  sel_unretr > 0; multihop smoke requires combined > baseline + 0.05).
- Both cells: routing-sanity gate-friendly (numpy-only; no `import torch`;
  no large-N literal -> remote_cpu_queue is correct route).
- Both cells: substrate-only-decode gate (n_llm_calls = 0; pure numpy).
- Bundle committed in single commit d3b84db3 (path-scoped: experiments/
  + preregs/ only; no incidental drift).

## Post-dispatch verification expected (orchestrator + remote)

- queue_add.sh POST-SHIP-VERIFY: cell present in remote queue.json
  (script validates this automatically; exits non-zero on miss).
- Remote --self-test invocation by runner before full run (queue_add.py
  default behavior); --self-test must PASS on remote .venv before full
  dispatch proceeds.
- On landing: metrics.json in `data/<cell_name>/metrics.json` with
  fields: verdict, verdict_msg, per_seed.arms[] with full HP-scope
  schema.
- Notify Skunkworks for landed-VET via SendMessage / TaskCompleted hook
  on each cell completion.

## Standing / waiting-on

exp_dev waiting on: orchestrator to invoke queue_add.sh for both cells
(harness-DENIED push from exp_dev). Both cells filed + committed; ball
in orchestrator's court.
