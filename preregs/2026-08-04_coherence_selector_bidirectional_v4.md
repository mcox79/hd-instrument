# Pre-registration: coherence_selector_bidirectional_v4 (2026-08-04)

## Problem
`coherence_selector_novel_types_v3` (data/exp_coherence_selector_novel_types_v3/metrics.json,
MIDDLE_BAND) is REVERSE-replay-only: a single TD(0) SR-transport map `M_backward`
(effect-content -> cause-content) scores causal-coherence episodes on held-out NOVEL TYPES.
v3's own docstring and ledger (commit 08694d7b6) flag multi-hop degradation as the known open
item. Two disk-verified prior results bound the fix:
1. `exp_multihop_reverse_replay_backward_sweep_v1`: reverse-only collapses at 2-hop
   (A=0.506); bidirectional beats it (D_bidir=0.690) -- SOME forward signal helps.
2. BUT the MEET-IN-THE-MIDDLE PREMIUM specifically (bidir > forward-alone) is NOT
   established and has repeatedly FAILED at scale: `exp_substrate_multihop_bidirectional_
   meet_middle_v2` REPRODUCE=0.12 (v1's 0.86 HARD_PASS did not reproduce; v1's own
   `mean_midpoint_cosine=0.0` flags that HARD_PASS as artifact-suspect);
   `exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3`=HARD_FAIL_NO_MEETING_PREMIUM
   (bidir 0.443 lost to forward-half 0.684); wave14 bidirectional=BIDIR_INSUFFICIENT.

=> The likely fix for v3's reverse-only collapse is simply ADDING A FORWARD PASS -- and
forward-alone may already suffice or beat an explicit meet-in-middle combine. Ledger commit
11a9dbf79 directs: test all three (reverse / forward / bidirectional), do NOT assume the
meeting helps.

## Design (3-way arm on the SAME held-out-novel-types substrate as v3)
Substrate reused bit-identically from v3 (`experiments/exp_coherence_selector_novel_types_
v3.py`): a fixed permutation `T` of N_DIM=2048 coordinate axes (SAME `T` for every type,
seen or novel); each type gets an i.i.d. bipolar base vector; a causal chain for type `t` is
the iterated orbit `u_0=b_t, u_k=T(u_{k-1})`. TRAIN types (0-9) and NOVEL EVAL types (10-19)
are disjoint index ranges from the same generative distribution (fairness-critical: novel
types are solvable in principle, not an unfair table-lookup test). CHAIN_HOPS extended to 3
(v3 used 2) so 1/2/3-hop episodes are all available from the same chain.

Two SR-transport maps trained ONCE on TRAIN-partition transitions only (`train_sr_transport`,
TD(0) delta-rule, SR_STEPS=2000):
- `M_backward` -- trained on effect->cause transitions (`ChainPartition.predecessors`
  adjacency) -- v3's exact direction/mechanism.
- `M_forward` -- NEW. Trained on cause->effect transitions (the literal reversal of
  `predecessors`, built via `build_successors`) -- the SAME chain edges, opposite
  traversal direction, identical hyperparameters.

Three arms, scored on the SAME held-out novel-type episodes at hop_distance in {1,2,3}:
- **R** (reverse-only): `score(cand) = cos(outcome @ M_backward, cand)` -- v3's mechanism,
  the floor to beat. Brain: reverse hippocampal SWR replay (episode replayed backward from
  outcome toward cause).
- **F** (forward-only): `score(cand) = cos(cand @ M_forward, outcome)` -- NEW. Brain: forward
  hippocampal replay/preplay (prospective sequence run forward from a candidate cause toward
  an anticipated outcome).
- **B** (bidirectional): `score(cand) = mean(score_R(cand), score_F(cand))` -- both directions
  vote on the same candidate. Brain: forward+reverse replay converging on a shared route
  (meet-in-middle planning / bidirectional search).

## Reuse note on the prior meet-in-middle combine
`exp_substrate_multihop_bidirectional_meet_middle_v1.py`'s combine (`arm_bidirectional_
meet_at_hop2` / `_rank`) runs over HRR bind/unbind chains with a Hebbian W and explicit
relation vectors R -- not bit-reusable on this substrate (TD(0)-trained linear SR-transport
maps over a permutation-orbit content-transform, no R/predicate vectors). The reused IDEA is
v1's own anti-artifact diagnostic: it measured `cosine(forward_state, backward_state)` at the
literal midpoint hop and flagged `mean_midpoint_cosine=0.0` as the tell that its own
HARD_PASS was an artifact. This cell reimplements that diagnostic on the SR-transport
substrate: `meeting_cosine(cand) = cos(cand @ M_forward, outcome @ M_backward)`, reported
separately from the ARM_B selection score (which is a plain mean, not gated on meeting_cosine)
so a bidirectional win can be distinguished from a genuine meeting-driven win.

## Hypotheses / can-fail contract
- Q1: does adding forward (F or B) LIFT 2-hop/3-hop accuracy over reverse-only R?
- Q2: is there a REAL meeting premium (B beats max(F,R) AND `meeting_cosine_true_minus_
  distractor` clears a small nonzero floor, HP_MEETING_COSINE_MIN=0.02, discriminating true
  pairing from distractor pairing across all 5 seeds) -- or does forward-alone suffice/win,
  replicating the prior-art pattern?
- If NOTHING clears its own floor+margin+shuffled-control bar at 2/3-hop, that is an honest
  informative negative (matches `HARD_FAIL_NO_MEETING_PREMIUM` lineage) -- NOT forced to a
  pass. Before concluding a mechanism ceiling: check both M's SR TD(0) convergence
  (`err_last < err_first`), inspect whether the combine (plain mean) and meeting_cosine
  diagnostic are computing sane, non-degenerate quantities.

## Guards (kept identical to v3)
FLOORS that must fail every arm/hop: RECENCY, RANDOM, NO_REPLAY_LOCAL (anti-tautology
identity-M raw cosine). SHUFFLED-STRUCTURE control (hop=2, all 3 arms, M's held fixed) must
collapse toward chance. POSITIVE CONTROL (ORACLE) must hit 100%/100% every hop distance --
episode-construction sanity. ONE variable per comparison (R/F/B share identical substrate,
TRAIN transitions -- opposite direction only -- SR hyperparameters, episode construction).
SHORT chains only (1/2/3 hops, CHAIN_HOPS=3) -- narrative scale, not VAMP-EP deep-chain
territory. Brain-foundational (forward/reverse hippocampal replay, named above); glass-box;
no borrowed embedding/LLM/parser; deterministic seeded generators; resumable per-seed
checkpointing (`experiments/_seed_checkpoint.py`); 5 seeds [7,17,23,31,41].

## Hard-pass thresholds (per arm per hop, same bar as v3)
`HP_EVAL_ACC_FLOOR=0.75`, `HP_FLOOR_MARGIN=0.15` (min lift over all 3 floors),
`HP_SHUFFLED_CEIL=0.65`, `HP_STRUCTURAL_LIFT_MIN=0.15`, margin-positive every seed,
plus for ARM_B: `HP_MEETING_COSINE_MIN=0.02` on `meeting_cosine_true_minus_distractor`.

## Deliverable
`experiments/exp_coherence_selector_bidirectional_v4.py`, this prereg,
`data/exp_coherence_selector_bidirectional_v4/metrics.json`. Local-only cell: no queue, no
remote dispatch, no push. Run directly:
`.venv/Scripts/python.exe experiments/exp_coherence_selector_bidirectional_v4.py`
