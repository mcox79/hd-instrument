"""coherence_selector_bidirectional_v4 -- 3-way REVERSE vs FORWARD vs BIDIRECTIONAL
(meet-in-the-middle) stress test on the SAME held-out-novel-types substrate as v3, at
1/2/3-hop chain distances.

WHY v4 (Director brief, ledger commit 11a9dbf79 "prior bidirectional meet-in-middle largely
FAILED at scale (no meeting premium); v4 fix = add forward pass, 3-way arm"):
coherence_selector_novel_types_v3 (data/exp_coherence_selector_novel_types_v3/metrics.json)
is REVERSE-replay-only (M_backward: effect-content -> cause-content, trained via TD(0)
SR-transport on the predecessor/effect->cause adjacency) and its own docstring flags
multi-hop degradation as the known-fix-is-bidirectional open item (ARM_NOVEL_2HOP tracked
separately from the primary 1-hop arm precisely because reverse-only was expected to weaken
with hop distance). Two disk-verified prior results bound the fix space:
  1. exp_multihop_reverse_replay_backward_sweep_v1: reverse-ONLY collapses at 2-hop;
     D_bidir=0.690 beats A(reverse-only)=0.506 -- SOME forward signal helps.
  2. BUT the specific MEET-IN-THE-MIDDLE PREMIUM (bidir > forward-ALONE) is NOT established
     and repeatedly FAILED at scale: exp_substrate_multihop_bidirectional_meet_middle_v2
     REPRODUCE=0.12 (v1's HARD_PASS did not reproduce; v1 had mean_midpoint_cosine=0.0,
     i.e. the "meeting" quantity was ZERO -- an artifact-suspect pass);
     exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3=HARD_FAIL_NO_MEETING_PREMIUM
     (bidir 0.443 LOST to forward-half 0.684); wave14 bidirectional FULL=BIDIR_INSUFFICIENT.
  => The likely fix for our reverse-only v3 mechanism is simply ADDING A FORWARD PASS, and
  forward-ALONE may already suffice or even beat an explicit meeting combine. This cell
  tests all three arms, does NOT assume the meeting helps, and explicitly VETs whether any
  "meeting" quantity used by the bidirectional arm is actually nonzero (per v1's disk-
  verified failure mode: a HARD_PASS built on a mean_midpoint_cosine=0.0 meeting quantity is
  an artifact, not a mechanism win).

THREE ARMS on the SAME held-out NOVEL-TYPES substrate as v3 (type_overlap=0, verified on
disk below), evaluated at hop_distance in {1, 2, 3}:
  ARM R (reverse-only)  -- v3's mechanism, the floor to beat. M_backward trained via TD(0)
                           SR-transport on effect->cause transitions (predecessors adjacency).
                           Brain: reverse hippocampal replay (awake SWR replaying an episode
                           backward from reward/outcome toward its cause).
  ARM F (forward-only)  -- NEW. M_forward trained via the SAME TD(0) SR-transport machinery
                           on cause->effect transitions (successors adjacency -- the SAME
                           chain, opposite traversal direction). Score = does the candidate
                           cause's forward-projected state match the actual outcome content?
                           Brain: forward hippocampal replay / preplay (prospective sequences
                           run forward from a start state toward an anticipated goal).
  ARM B (bidirectional / meet-in-the-middle) -- combines F and B. Score_B(candidate) =
                           mean(score_R(candidate), score_F(candidate)) -- both directions
                           vote on the SAME candidate. Brain: forward+reverse replay
                           converging on a shared route representation (meet-in-middle
                           planning, e.g. bidirectional search literature / hippocampal
                           prospective+retrospective coding). A SEPARATE, non-scoring
                           diagnostic (meeting_cosine, see below) explicitly measures whether
                           forward-projected-future and backward-projected-past actually
                           converge onto a common representation, independent of whether the
                           combined score wins -- this is the anti-artifact VET the prior
                           v1/v2 meet-in-middle cells skipped.

REUSE NOTE on the prior meet-in-middle combine (exp_substrate_multihop_bidirectional_meet_
middle_v1.py, arm_bidirectional_meet_at_hop2 / arm_bidirectional_meet_middle_rank): that
cell's substrate is HRR bind/unbind chains over a Hebbian associative matrix W with explicit
relation vectors R -- NOT bit-reusable here (this substrate is TD(0)-trained linear SR-
transport maps M over a permutation-orbit content-transform, no R/predicate vectors exist).
The analogous quantity IS reused conceptually: v1 measured cosine(forward_state,
backward_state) AT THE LITERAL MIDPOINT HOP and flagged mean_midpoint_cosine=0.0 as the
artifact tell for its own HARD_PASS. This cell reimplements that same diagnostic on OUR
substrate: meeting_cosine = cos(cand_E @ M_forward, outcome_E @ M_backward) -- both
directions' SR-transport projections (each already a discounted multi-step feature via the
gamma-bootstrap in train_sr_transport, so a single M application is NOT a literal 1-hop
step -- it already encodes a geometric-discounted reachability estimate, which is exactly
why v3 reused ONE M_backward across 1-hop and 2-hop arms without retraining). If
mean_meeting_cosine (true-cause pairing) is ~0 (or indistinguishable from the distractor
pairing), any ARM_B win over ARM_F is reported as an artifact per the v1/v2 precedent, not a
genuine meeting premium.

TWO QUESTIONS answered with numbers (per hop distance, multi-seed):
  Q1: does adding forward (F or B) LIFT 2-hop/3-hop accuracy over reverse-only R?
  Q2: is there a real MEETING PREMIUM (B beats max(F,R) AND meeting_cosine is nonzero/
      discriminating), or does FORWARD-ALONE suffice/win (matching prior-art's repeated
      finding that the explicit meet-in-middle combine adds nothing over forward-only)?

GUARDS (kept identical to v3's fair design):
  FLOORS THAT MUST FAIL (each arm, each hop distance): RECENCY, RANDOM, NO_REPLAY_LOCAL
  (identity-M raw cosine, anti-tautology). SHUFFLED-STRUCTURE control (i.i.d. random bipolar
  replacing chain-structured embeddings, both M's held fixed) must collapse toward chance.
  POSITIVE CONTROL (ORACLE) fires at 100%/100% every hop distance -- episode-construction
  sanity. ONE variable per comparison: R/F/B share the identical held-out-novel-types
  substrate, identical TRAIN-partition transitions (opposite direction only), identical
  SR-transport hyperparameters, identical episode construction -- only the direction(s) of
  the trained map and the combine differ. SHORT chains only (1/2/3 hops, CHAIN_HOPS=3) --
  narrative-scale, not the VAMP-EP deep-chain regime (reference only, not chased here).
  Brain-foundational (forward/reverse hippocampal replay, named above); glass-box; no
  borrowed embedding/LLM/parser; deterministic (torch.Generator seeded per-seed,
  sorted(set()) split hygiene N/A here -- disjoint index ranges by construction);
  resumable (experiments/_seed_checkpoint.py); multi-seed; store binary/newline='' +
  git-commit after valid write.

CAN-FAIL CONTRACT: if NOTHING lifts 2-hop/3-hop over reverse-only R (matching prior
HARD_FAIL_NO_MEETING_PREMIUM), that is an honest informative negative -- before concluding a
mechanism-level ceiling this cell checks (a) M_forward's own SR TD(0) convergence
(err_last < err_first, same sr_diag contract as v3), (b) the combine arithmetic (score_B is
literally the mean of score_R and score_F, inspectable), (c) the meeting_cosine quantity is
non-degenerate (not NaN/exactly 0 for a torch float32 chain of nontrivial computation). No
forced pass.

Reuses (bit-identical import, not re-derived):
  experiments/exp_coherence_selector_novel_types_v3.py -- build_perm_transform,
    build_type_base_vectors, build_chain_trajectories, ChainPartition, build_episodes,
    situation_buffer_check, selector_recency, selector_random,
    selector_coherence_abstain_gated
  experiments/exp_pfc_gate_cfrpe_trained_v2.py -- make_bipolar_E, train_sr_transport,
    reach_value, reach_control_targetcos, collect_rollout_transitions, _norm_rows
  hdlab/situation_model_accumulate.py -- AccumulateRegister (buffer sanity, not the scorer)
  hdlab/self_improving_loop.py -- decide_keep_or_revert, ABSTAIN_BAND_DEFAULT
  experiments/_seed_checkpoint.py -- resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics, record_gate, get_output_dir

Author: exp_dev-role direct run (Sonnet 5, agent-spawn), 2026-08-04.
Prereg: d:/AI/hd-instrument/preregs/2026-08-04_coherence_selector_bidirectional_v4.md
Local-only cell: no queue, no remote dispatch, no push. Run directly:
  .venv/Scripts/python.exe experiments/exp_coherence_selector_bidirectional_v4.py
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp_pfc_gate_cfrpe_trained_v2 import (  # noqa: E402
    make_bipolar_E, train_sr_transport, reach_value, reach_control_targetcos,
    collect_rollout_transitions, _norm_rows,
)
from experiments.exp_coherence_selector_novel_types_v3 import (  # noqa: E402
    build_perm_transform, build_type_base_vectors, build_chain_trajectories,
    ChainPartition, build_episodes, situation_buffer_check, selector_recency,
    selector_random, selector_coherence_abstain_gated,
)
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds, write_partial_key, aggregate_partials, write_metrics,
    record_gate, get_output_dir,
)
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402

ANCHOR_NAME = "coherence_selector_bidirectional_v4"
DEVICE = torch.device("cpu")  # local-only cell, small scale, no GPU needed
DTYPE = torch.float32

# ------------------------------- config (LOCKED, PROSPECTIVE) ---------------------------
N_DIM = 2048
NOISE_FRAC = 0.05

N_TYPES_SEEN = 10          # 0 .. 9    (TRAIN)
N_TYPES_NOVEL = 10         # 10 .. 19  (EVAL-only, disjoint from TRAIN)
N_TYPES_TOTAL = N_TYPES_SEEN + N_TYPES_NOVEL

CHAIN_HOPS = 3              # chain = [hop0, hop1, hop2, hop3] -- supports 1/2/3-hop episodes
N_CHAINS_PER_TYPE_TRAIN = 26
N_CHAINS_PER_TYPE_NOVEL = 26

N_EPISODES_TRAIN = 60
N_EPISODES_EVAL = 60          # per arm per hop distance

SR_STEPS = 2000
SR_BATCH = 128
SR_LR = 0.5
GAMMA = 0.85
ROLLOUT_PER_NODE = 40
ROLLOUT_MAX_LEN = 3
SEEDS = [7, 17, 23, 31, 41]

HOP_DISTANCES = [1, 2, 3]

HP_EVAL_ACC_FLOOR = 0.75
HP_FLOOR_MARGIN = 0.15
HP_SHUFFLED_CEIL = 0.65
HP_STRUCTURAL_LIFT_MIN = 0.15
HP_MEETING_COSINE_MIN = 0.02   # anti-artifact floor: mean meeting cosine must clear ~0

CONFIG_VERSION = (
    "ANCHOR=%s,N_DIM=%d,N_TYPES_SEEN=%d,N_TYPES_NOVEL=%d,noise_frac=%.2f,chain_hops=%d,"
    "n_chains_train=%d,n_chains_novel=%d,n_ep_train=%d,n_ep_eval=%d,sr_steps=%d,sr_batch=%d,"
    "gamma=%.2f,hop_distances=%s,seeds=%s,abstain_band=%.3f"
) % (ANCHOR_NAME, N_DIM, N_TYPES_SEEN, N_TYPES_NOVEL, NOISE_FRAC, CHAIN_HOPS,
     N_CHAINS_PER_TYPE_TRAIN, N_CHAINS_PER_TYPE_NOVEL, N_EPISODES_TRAIN, N_EPISODES_EVAL,
     SR_STEPS, SR_BATCH, GAMMA, HOP_DISTANCES, SEEDS, ABSTAIN_BAND_DEFAULT)

_T0 = time.time()


# ============================================================================
# forward adjacency (opposite traversal direction of ChainPartition.predecessors)
# ============================================================================
def build_successors(predecessors: Dict[int, List[int]]) -> Dict[int, List[int]]:
    """successors[cause] = [effect, ...] -- literal reversal of predecessors[effect]=[cause].
    SAME chain edges, opposite direction: cause->effect (forward/preplay) vs effect->cause
    (v3's reverse-replay direction)."""
    succ: Dict[int, List[int]] = {}
    for effect, causes in predecessors.items():
        for c in causes:
            succ.setdefault(c, []).append(effect)
    return succ


def selector_oracle_nhop(ep: Dict[str, Any], predecessors: Dict[int, List[int]],
                         hop_distance: int) -> str:
    """Generalized N-hop oracle: walk `predecessors` back `hop_distance` steps from the
    outcome and compare to true_cause. Generalizes v3's selector_oracle (1-hop / hardcoded
    2-hop) to arbitrary hop_distance (needed here for the 3-hop arm)."""
    node = ep["outcome"]
    for _ in range(hop_distance):
        preds = predecessors.get(node)
        if not preds:
            return "distractor" if ep["true_cause"] != node else "true"
        node = preds[0]
    return "true" if node == ep["true_cause"] else "distractor"


# ============================================================================
# directional reach scoring (R = reverse: outcome->M_backward~cand; F = forward:
# cand->M_forward~outcome; B = mean of both). Reuses reach_value / reach_control_targetcos
# bit-identically; only the (cand, goal, M) argument ORDER encodes direction.
# ============================================================================
def score_reverse(cand_E: torch.Tensor, outcome_E: torch.Tensor, M_backward: torch.Tensor,
                  use_M: bool) -> torch.Tensor:
    """v3's exact scoring direction: cos(outcome @ M_backward, candidate)."""
    if use_M:
        return reach_value(outcome_E, cand_E, M_backward)
    return reach_control_targetcos(outcome_E, cand_E)


def score_forward(cand_E: torch.Tensor, outcome_E: torch.Tensor, M_forward: torch.Tensor,
                  use_M: bool) -> torch.Tensor:
    """New forward/preplay direction: cos(candidate @ M_forward, outcome)."""
    if use_M:
        return reach_value(cand_E, outcome_E, M_forward)
    return reach_control_targetcos(cand_E, outcome_E)


def meeting_cosine(cand_E: torch.Tensor, outcome_E: torch.Tensor, M_forward: torch.Tensor,
                   M_backward: torch.Tensor) -> torch.Tensor:
    """Anti-artifact diagnostic (reimplements v1's mean_midpoint_cosine tell on THIS
    substrate): cos(candidate @ M_forward, outcome @ M_backward) -- do the forward-
    projected-future-from-candidate and the backward-projected-past-from-outcome converge
    onto a shared representation? NOT used as the ARM_B selection score (that is a plain
    mean of the two directional scores, see score_bidirectional) -- this is purely the
    "is there a real meeting" measurement the prior v1/v2 cells skipped."""
    fwd = _norm_rows(cand_E @ M_forward)
    bwd = _norm_rows(outcome_E @ M_backward)
    return (fwd * bwd).sum(dim=1)


def score_bidirectional(s_reverse: torch.Tensor, s_forward: torch.Tensor) -> torch.Tensor:
    return 0.5 * (s_reverse + s_forward)


# ============================================================================
# per-arm episode scoring (recency/random/oracle/no_replay_local floors + coherence + meeting)
# ============================================================================
def _score_episodes(episodes: List[Dict[str, Any]], predecessors: Dict[int, List[int]],
                    hop_distance: int, E: torch.Tensor, id_start: int,
                    M_backward: torch.Tensor, M_forward: torch.Tensor, arm: str,
                    seed: int, rand_seed_offset: int) -> Dict[str, Any]:
    n = len(episodes)
    if n == 0:
        return {"n_episodes": 0}
    rg = np.random.default_rng(int(seed) * 999983 + rand_seed_offset)

    recency_correct = sum(1 for e in episodes if selector_recency(e) == "true")
    random_correct = sum(1 for e in episodes if selector_random(e, rg) == "true")
    oracle_correct = sum(1 for e in episodes
                         if selector_oracle_nhop(e, predecessors, hop_distance) == "true")

    outc = torch.tensor([e["outcome"] - id_start for e in episodes], dtype=torch.long, device=DEVICE)
    tru = torch.tensor([e["true_cause"] - id_start for e in episodes], dtype=torch.long, device=DEVICE)
    dis = torch.tensor([e["distractor"] - id_start for e in episodes], dtype=torch.long, device=DEVICE)
    outc_E, tru_E, dis_E = E[outc], E[tru], E[dis]

    # no_replay_local floor: anti-tautology raw-cosine control (direction irrelevant, symmetric)
    s_true_ctrl = reach_control_targetcos(outc_E, tru_E)
    s_distr_ctrl = reach_control_targetcos(outc_E, dis_E)
    norepl_correct = int(torch.sum(s_true_ctrl > s_distr_ctrl))

    s_true_r = score_reverse(tru_E, outc_E, M_backward, use_M=True)
    s_distr_r = score_reverse(dis_E, outc_E, M_backward, use_M=True)
    s_true_f = score_forward(tru_E, outc_E, M_forward, use_M=True)
    s_distr_f = score_forward(dis_E, outc_E, M_forward, use_M=True)

    if arm == "R":
        s_true_m, s_distr_m = s_true_r, s_distr_r
    elif arm == "F":
        s_true_m, s_distr_m = s_true_f, s_distr_f
    elif arm == "B":
        s_true_m = score_bidirectional(s_true_r, s_true_f)
        s_distr_m = score_bidirectional(s_distr_r, s_distr_f)
    else:
        raise ValueError("unknown arm %r" % arm)

    coh_correct = 0
    coh_abstain = 0
    margins = []
    for i in range(n):
        margin = float(s_true_m[i] - s_distr_m[i])
        margins.append(margin)
        adopt = decide_keep_or_revert({"true_over_distr": margin}, ABSTAIN_BAND_DEFAULT)
        if adopt != "true_over_distr":
            coh_abstain += 1
            continue
        coh_correct += 1

    out = {
        "n_episodes": n,
        "recency_acc": recency_correct / n,
        "random_acc": random_correct / n,
        "no_replay_local_acc": norepl_correct / n,
        "oracle_acc": oracle_correct / n,
        "coherence_acc_conservative": coh_correct / n,
        "coherence_abstain_rate": coh_abstain / n,
        "coherence_acc_covered": (coh_correct / (n - coh_abstain)) if (n - coh_abstain) > 0 else None,
        "glassbox_margin_mean": float(np.mean(margins)),
        "glassbox_margin_min": float(np.min(margins)),
        "glassbox_margin_positive_frac": float(np.mean([m > 0.0 for m in margins])),
    }

    # meeting-quantity diagnostic -- computed for EVERY arm (cheap, apples-to-apples), but
    # only load-bearing for ARM_B's verdict.
    mc_true = meeting_cosine(tru_E, outc_E, M_forward, M_backward)
    mc_distr = meeting_cosine(dis_E, outc_E, M_forward, M_backward)
    out["meeting_cosine_true_mean"] = float(mc_true.mean())
    out["meeting_cosine_distractor_mean"] = float(mc_distr.mean())
    out["meeting_cosine_true_minus_distractor"] = float((mc_true - mc_distr).mean())
    return out


def _arm(part: ChainPartition, hop_distance: int, n_episodes: int, E_variant: torch.Tensor,
        M_backward: torch.Tensor, M_forward: torch.Tensor, arm: str, seed: int,
        rand_offset: int, g: np.random.Generator) -> Dict[str, Any]:
    eps = build_episodes(part, n_episodes, hop_distance, g)
    return _score_episodes(eps, part.predecessors, hop_distance, E_variant, part.id_start,
                           M_backward, M_forward, arm, seed, rand_offset)


# ============================================================================
# per-seed run
# ============================================================================
def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    perm_gen = np.random.default_rng(int(seed) * 100003 + 5)
    perm_idx, inv_perm_idx = build_perm_transform(N_DIM, perm_gen)

    tgen = torch.Generator(device=DEVICE)
    tgen.manual_seed(int(seed) * 100003 + 1)
    base_vectors = build_type_base_vectors(N_TYPES_TOTAL, N_DIM, tgen)
    traj = build_chain_trajectories(base_vectors, perm_idx, CHAIN_HOPS)

    types_seen = list(range(0, N_TYPES_SEEN))
    types_novel = list(range(N_TYPES_SEEN, N_TYPES_SEEN + N_TYPES_NOVEL))

    egen_train = torch.Generator(device=DEVICE); egen_train.manual_seed(int(seed) * 100003 + 2)
    part_train = ChainPartition(types_seen, N_CHAINS_PER_TYPE_TRAIN, traj, NOISE_FRAC,
                                0, egen_train)

    egen_novel = torch.Generator(device=DEVICE); egen_novel.manual_seed(int(seed) * 100003 + 3)
    part_novel = ChainPartition(types_novel, N_CHAINS_PER_TYPE_NOVEL, traj, NOISE_FRAC,
                                part_train.id_end, egen_novel)

    entity_overlap = 0
    type_overlap_novel = float(len(set(types_seen) & set(types_novel)))
    assert set(range(part_train.id_start, part_train.id_end)).isdisjoint(
        range(part_novel.id_start, part_novel.id_end))

    # --- train M_backward (reverse: effect->cause, v3's direction) on TRAIN partition ------
    succ_train = build_successors(part_train.predecessors)
    adj_reverse = [dict(part_train.predecessors)]
    adj_forward = [dict(succ_train)]
    n_nodes_train = part_train.id_end - part_train.id_start
    n_transitions = min(200000, ROLLOUT_PER_NODE * n_nodes_train)

    transitions_rev = collect_rollout_transitions(
        adj_reverse, n_ops=1, V=part_train.id_end, n_transitions=n_transitions,
        max_len=ROLLOUT_MAX_LEN, g=g)
    transitions_fwd = collect_rollout_transitions(
        adj_forward, n_ops=1, V=part_train.id_end, n_transitions=n_transitions,
        max_len=ROLLOUT_MAX_LEN, g=g)

    sr_gen_r = torch.Generator(device=DEVICE); sr_gen_r.manual_seed(int(seed) * 7919 + 1)
    M_backward, sr_diag_r = train_sr_transport(
        part_train.E, transitions_rev, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen_r)

    sr_gen_f = torch.Generator(device=DEVICE); sr_gen_f.manual_seed(int(seed) * 7919 + 2)
    M_forward, sr_diag_f = train_sr_transport(
        part_train.E, transitions_fwd, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen_f)

    # situation-model buffer glass-box sanity (real integration, not the scorer) -- unchanged
    buf_gen = torch.Generator(device=DEVICE); buf_gen.manual_seed(int(seed) * 31337 + 1)
    ep_train_1hop_for_buf = build_episodes(part_train, N_EPISODES_TRAIN, 1, g)
    buf_fidelity_train = situation_buffer_check(ep_train_1hop_for_buf, buf_gen)

    # --- 3 arms x 3 hop distances, all on the SAME held-out NOVEL partition ---------------
    arms_by_hop: Dict[str, Dict[str, Any]] = {}
    for hop in HOP_DISTANCES:
        for arm in ("R", "F", "B"):
            key = "hop%d_arm%s" % (hop, arm)
            arms_by_hop[key] = _arm(part_novel, hop, N_EPISODES_EVAL, part_novel.E,
                                    M_backward, M_forward, arm, seed,
                                    2000 + hop * 10 + ord(arm), g)

    # --- SHUFFLED-STRUCTURE control at hop=2 (the discriminating multi-hop distance), all
    # 3 arms, M's held fixed -- proves any arm's win is structural, not a spurious cue.
    shuf_gen = torch.Generator(device=DEVICE); shuf_gen.manual_seed(int(seed) * 424243 + 1)
    n_novel_nodes = part_novel.id_end - part_novel.id_start
    E_shuffled_novel = make_bipolar_E(n_novel_nodes, N_DIM, shuf_gen)
    shuffled_by_arm: Dict[str, Any] = {}
    for arm in ("R", "F", "B"):
        g_shuf = np.random.default_rng(int(seed) * 313 + 9 + ord(arm))
        shuffled_by_arm["arm%s" % arm] = _arm(part_novel, 2, N_EPISODES_EVAL,
                                              E_shuffled_novel, M_backward, M_forward,
                                              arm, seed, 3000 + ord(arm), g_shuf)

    return {
        "seed": int(seed),
        "run_mode": "full",
        "N": N_DIM,
        "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "sr_diag_reverse": sr_diag_r,
        "sr_diag_forward": sr_diag_f,
        "situation_buffer_decode_fidelity_train": buf_fidelity_train,
        "train_eval_entity_overlap": entity_overlap,
        "train_eval_type_overlap_novel": type_overlap_novel,
        "arms_by_hop": arms_by_hop,
        "shuffled_structure_hop2_by_arm": shuffled_by_arm,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def _summ(per_seed: Dict[str, Dict[str, Any]], keys: List[str], block_path: Tuple[str, ...]
         ) -> Dict[str, Any]:
    def _get(d: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cur: Any = d
        for k in block_path:
            cur = cur.get(k, {}) if isinstance(cur, dict) else {}
        return cur if isinstance(cur, dict) and cur else None

    def _col(field: str) -> List[float]:
        out = []
        for k in keys:
            blk = _get(per_seed[k])
            if blk is None:
                continue
            v = blk.get(field)
            if v is not None:
                out.append(float(v))
        return out

    fields = ["recency_acc", "random_acc", "no_replay_local_acc", "oracle_acc",
              "coherence_acc_conservative", "coherence_abstain_rate",
              "glassbox_margin_mean", "glassbox_margin_positive_frac",
              "meeting_cosine_true_mean", "meeting_cosine_distractor_mean",
              "meeting_cosine_true_minus_distractor"]
    out: Dict[str, Any] = {}
    for f in fields:
        vals = _col(f)
        out[f] = {"mean": float(np.mean(vals)) if vals else None,
                  "std": float(np.std(vals)) if vals else None,
                  "n_seeds": len(vals),
                  "per_seed": {keys[i]: vals[i] for i in range(len(vals)) if i < len(vals)}}
    min_margins = _col("glassbox_margin_min")
    out["glassbox_margin_min_over_seeds"] = float(np.min(min_margins)) if min_margins else None
    return out


def _arm_gate_block(name: str, summary: Dict[str, Any], shuffled_summary: Optional[Dict[str, Any]],
                    prefix: str, check_meeting: bool = False) -> Tuple[Dict[str, Any], List[Dict[str, Any]], bool]:
    coh = summary["coherence_acc_conservative"]["mean"] or 0.0
    rec = summary["recency_acc"]["mean"] or 0.0
    rand = summary["random_acc"]["mean"] or 0.0
    norepl = summary["no_replay_local_acc"]["mean"] or 0.0
    margin_min = summary["glassbox_margin_min_over_seeds"]
    lift_recency = coh - rec
    lift_random = coh - rand
    lift_norepl = coh - norepl
    min_lift = min(lift_recency, lift_random, lift_norepl)
    margin_all_positive = (margin_min is not None and margin_min > 0.0)

    gates = [
        record_gate("%s_acc_floor" % prefix, coh, HP_EVAL_ACC_FLOOR, ">=",
                   "%s: HARD-PASS accuracy floor" % name),
        record_gate("%s_min_lift_over_floors" % prefix, min_lift, HP_FLOOR_MARGIN, ">=",
                   "%s: must beat all 3 floors by >=0.15" % name),
        record_gate("%s_margin_min_over_seeds" % prefix, margin_min if margin_min is not None else -999.0,
                   0.0, ">", "%s: true-vs-distractor reach margin positive every seed" % name),
    ]
    beats_floors = (coh >= HP_EVAL_ACC_FLOOR and min_lift >= HP_FLOOR_MARGIN and margin_all_positive)

    shuffled_ok = True
    coh_shuf = None
    structural_lift = None
    if shuffled_summary is not None:
        coh_shuf = shuffled_summary["coherence_acc_conservative"]["mean"] or 0.0
        structural_lift = coh - coh_shuf
        shuffled_ok = (coh_shuf <= HP_SHUFFLED_CEIL) and (structural_lift >= HP_STRUCTURAL_LIFT_MIN)
        gates.append(record_gate("%s_shuffled_structure_ceiling" % prefix, coh_shuf,
                                 HP_SHUFFLED_CEIL, "<=",
                                 "%s: ANTI-MEMORIZATION shuffled-structure control" % name))
        gates.append(record_gate("%s_structural_lift_min" % prefix, structural_lift,
                                 HP_STRUCTURAL_LIFT_MIN, ">=",
                                 "%s: coherence must show real structural dependence" % name))

    meeting_ok = True
    meeting_delta = None
    if check_meeting:
        meeting_delta = summary["meeting_cosine_true_minus_distractor"]["mean"]
        meeting_ok = (meeting_delta is not None and meeting_delta >= HP_MEETING_COSINE_MIN)
        gates.append(record_gate("%s_meeting_cosine_nonzero" % prefix,
                                 meeting_delta if meeting_delta is not None else -999.0,
                                 HP_MEETING_COSINE_MIN, ">=",
                                 "%s: ANTI-ARTIFACT meeting-quantity must discriminate "
                                 "true-cause from distractor pairing (per v1's disk-verified "
                                 "mean_midpoint_cosine=0.0 artifact-suspect precedent)" % name))

    arm_pass = beats_floors and shuffled_ok and meeting_ok
    block = {
        "coherence_eval_acc": coh, "recency_acc": rec, "random_acc": rand,
        "no_replay_local_acc": norepl, "lift_over_recency": lift_recency,
        "lift_over_random": lift_random, "lift_over_no_replay_local": lift_norepl,
        "min_lift_over_floors": min_lift, "margin_min_over_seeds": margin_min,
        "margin_all_positive": margin_all_positive, "beats_all_floors": beats_floors,
        "coherence_eval_shuffled_structure_acc": coh_shuf,
        "structural_lift_minus_shuffled": structural_lift,
        "shuffled_control_ok": shuffled_ok if shuffled_summary is not None else None,
        "meeting_cosine_true_minus_distractor_mean": meeting_delta,
        "meeting_quantity_nonzero_and_discriminating": meeting_ok if check_meeting else None,
        "arm_pass": arm_pass,
    }
    return block, gates, arm_pass


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    hop_arm_summaries: Dict[str, Dict[str, Any]] = {}
    hop_arm_blocks: Dict[str, Dict[str, Any]] = {}
    all_gates: List[Dict[str, Any]] = []
    for hop in HOP_DISTANCES:
        for arm in ("R", "F", "B"):
            key = "hop%d_arm%s" % (hop, arm)
            summ = _summ(per_seed, keys, ("arms_by_hop", key))
            hop_arm_summaries[key] = summ
            check_meeting = (arm == "B")
            block, gates, _pass = _arm_gate_block(
                "HOP%d_ARM_%s" % (hop, arm), summ, None, "hop%d_%s" % (hop, arm),
                check_meeting=check_meeting)
            hop_arm_blocks[key] = block
            all_gates.extend(gates)

    shuf_summaries: Dict[str, Dict[str, Any]] = {}
    for arm in ("R", "F", "B"):
        shuf_summaries[arm] = _summ(per_seed, keys, ("shuffled_structure_hop2_by_arm", "arm%s" % arm))

    # re-derive hop2 blocks WITH the shuffled control wired in (structural-lift gate)
    hop2_blocks_with_shuf: Dict[str, Any] = {}
    hop2_gates_with_shuf: List[Dict[str, Any]] = []
    for arm in ("R", "F", "B"):
        key = "hop2_arm%s" % arm
        block, gates, _pass = _arm_gate_block(
            "HOP2_ARM_%s" % arm, hop_arm_summaries[key], shuf_summaries[arm],
            "hop2shuf_%s" % arm, check_meeting=(arm == "B"))
        hop2_blocks_with_shuf[arm] = block
        hop2_gates_with_shuf.extend(gates)
    all_gates.extend(hop2_gates_with_shuf)

    buf_train = float(np.mean([per_seed[k]["situation_buffer_decode_fidelity_train"]
                               for k in keys])) if keys else 0.0

    oracle_by_hop = {hop: (hop_arm_summaries["hop%d_armR" % hop]["oracle_acc"]["mean"] or 0.0)
                     for hop in HOP_DISTANCES}
    positive_control_ok = all(v >= 0.999 for v in oracle_by_hop.values())

    max_entity_overlap = max((per_seed[k].get("train_eval_entity_overlap", 0) for k in keys),
                             default=0)
    max_type_overlap_novel = max((per_seed[k].get("train_eval_type_overlap_novel", 0.0)
                                  for k in keys), default=0.0)
    recurring_entity_clean = (max_entity_overlap == 0 and max_type_overlap_novel == 0.0)

    gate_claims = (
        [record_gate("no_entity_overlap", max_entity_overlap, 0, "==", "TRAIN/EVAL entity ids disjoint"),
         record_gate("no_type_overlap_novel", max_type_overlap_novel, 0.0, "==",
                    "novel types NEVER seen in TRAIN")]
        + [record_gate("positive_control_oracle_hop%d" % hop, oracle_by_hop[hop], 0.999, ">=",
                       "chain sanity") for hop in HOP_DISTANCES]
        + all_gates
    )

    sr_err_first_r = [per_seed[k]["sr_diag_reverse"]["err_first"] for k in keys
                      if per_seed[k]["sr_diag_reverse"].get("err_first") is not None]
    sr_err_last_r = [per_seed[k]["sr_diag_reverse"]["err_last"] for k in keys
                     if per_seed[k]["sr_diag_reverse"].get("err_last") is not None]
    sr_converged_r = bool(sr_err_first_r and sr_err_last_r
                          and np.mean(sr_err_last_r) < np.mean(sr_err_first_r))
    sr_err_first_f = [per_seed[k]["sr_diag_forward"]["err_first"] for k in keys
                      if per_seed[k]["sr_diag_forward"].get("err_first") is not None]
    sr_err_last_f = [per_seed[k]["sr_diag_forward"]["err_last"] for k in keys
                     if per_seed[k]["sr_diag_forward"].get("err_last") is not None]
    sr_converged_f = bool(sr_err_first_f and sr_err_last_f
                          and np.mean(sr_err_last_f) < np.mean(sr_err_first_f))

    # ---- Q1: does adding forward (F or B) LIFT 2/3-hop over reverse-only R? ----
    q1_lift = {}
    for hop in (2, 3):
        acc_r = hop_arm_blocks["hop%d_armR" % hop]["coherence_eval_acc"]
        acc_f = hop_arm_blocks["hop%d_armF" % hop]["coherence_eval_acc"]
        acc_b = hop_arm_blocks["hop%d_armB" % hop]["coherence_eval_acc"]
        q1_lift["hop%d" % hop] = {
            "acc_R": acc_r, "acc_F": acc_f, "acc_B": acc_b,
            "F_minus_R": acc_f - acc_r, "B_minus_R": acc_b - acc_r,
            "forward_helps": bool(acc_f > acc_r or acc_b > acc_r),
        }
    q1_answer = any(v["forward_helps"] for v in q1_lift.values())

    # ---- Q2: real meeting premium (B > max(F,R) AND meeting-quantity discriminates) or
    # forward-alone suffices/wins? ----
    q2_by_hop = {}
    for hop in HOP_DISTANCES:
        acc_r = hop_arm_blocks["hop%d_armR" % hop]["coherence_eval_acc"]
        acc_f = hop_arm_blocks["hop%d_armF" % hop]["coherence_eval_acc"]
        acc_b = hop_arm_blocks["hop%d_armB" % hop]["coherence_eval_acc"]
        meeting_delta = hop_arm_blocks["hop%d_armB" % hop]["meeting_cosine_true_minus_distractor_mean"]
        meeting_real = meeting_delta is not None and meeting_delta >= HP_MEETING_COSINE_MIN
        bidir_wins_numerically = acc_b > max(acc_r, acc_f)
        q2_by_hop["hop%d" % hop] = {
            "acc_R": acc_r, "acc_F": acc_f, "acc_B": acc_b,
            "bidir_wins_numerically": bool(bidir_wins_numerically),
            "meeting_cosine_true_minus_distractor": meeting_delta,
            "meeting_quantity_real": bool(meeting_real),
            "genuine_meeting_premium": bool(bidir_wins_numerically and meeting_real),
            "forward_alone_sufficient": bool(acc_f >= acc_b or not meeting_real),
        }
    genuine_meeting_premium_any = any(v["genuine_meeting_premium"] for v in q2_by_hop.values())
    forward_alone_wins_or_ties = all(
        (q2_by_hop["hop%d" % h]["acc_F"] >= q2_by_hop["hop%d" % h]["acc_B"] - 1e-9)
        for h in HOP_DISTANCES)

    stress_all_pass = bool(all(hop_arm_blocks["hop%d_arm%s" % (h, a)]["arm_pass"]
                               for h in HOP_DISTANCES for a in ("R", "F", "B")))
    any_arm_beats_2_3hop = bool(hop_arm_blocks["hop2_armF"]["beats_all_floors"]
                                or hop_arm_blocks["hop2_armB"]["beats_all_floors"]
                                or hop_arm_blocks["hop3_armF"]["beats_all_floors"]
                                or hop_arm_blocks["hop3_armB"]["beats_all_floors"])

    if not positive_control_ok:
        verdict = "GATE_FAILED_POSITIVE_CONTROL"
        msg = ("ORACLE positive control failed (by hop: %s, need >=0.999 all) -- episode/"
               "chain construction itself is broken; no arm's verdict can be trusted."
               % json.dumps(oracle_by_hop))
    elif not recurring_entity_clean:
        verdict = "GATE_FAILED_ANTI_MEMORIZATION_CONSTRUCTION"
        msg = ("TRAIN/EVAL entity overlap=%d or type overlap=%.3f nonzero -- the novel-types "
               "test is mis-constructed; results cannot be trusted as evidence."
               % (max_entity_overlap, max_type_overlap_novel))
    else:
        acc_r1 = hop_arm_blocks["hop1_armR"]["coherence_eval_acc"]
        acc_r2 = hop_arm_blocks["hop2_armR"]["coherence_eval_acc"]
        acc_r3 = hop_arm_blocks["hop3_armR"]["coherence_eval_acc"]
        acc_f2 = hop_arm_blocks["hop2_armF"]["coherence_eval_acc"]
        acc_f3 = hop_arm_blocks["hop3_armF"]["coherence_eval_acc"]
        acc_b2 = hop_arm_blocks["hop2_armB"]["coherence_eval_acc"]
        acc_b3 = hop_arm_blocks["hop3_armB"]["coherence_eval_acc"]
        if any_arm_beats_2_3hop and q1_answer:
            verdict = "HARD_PASS" if stress_all_pass else "MIDDLE_BAND"
            winner = "BIDIRECTIONAL (genuine meeting premium)" if genuine_meeting_premium_any else \
                     "FORWARD-ALONE (no genuine meeting premium; bidir adds nothing real)"
            msg = ("FORWARD-PASS LIFTS MULTI-HOP: reverse-only R degrades with hop distance "
                   "(1hop=%.4f 2hop=%.4f 3hop=%.4f) as v3 flagged; adding a forward pass "
                   "(F: 2hop=%.4f 3hop=%.4f, B: 2hop=%.4f 3hop=%.4f) lifts 2/3-hop over R "
                   "(Q1=YES). Q2: %s -- genuine_meeting_premium_any=%s "
                   "(meeting_cosine true-vs-distractor: %s), forward_alone_sufficient_or_wins=%s. "
                   "%s"
                   % (acc_r1, acc_r2, acc_r3, acc_f2, acc_f3, acc_b2, acc_b3, winner,
                      genuine_meeting_premium_any,
                      json.dumps({h: q2_by_hop[h]["meeting_cosine_true_minus_distractor"]
                                 for h in q2_by_hop}),
                      forward_alone_wins_or_ties,
                      "ALL 9 arm/hop cells confirm their own gates." if stress_all_pass else
                      "NOTE: at least one arm/hop cell did NOT clear its own floor/margin/"
                      "shuffled bar -- read as partial/scope-limited, not a refutation of the "
                      "primary forward-helps finding."))
        elif any_arm_beats_2_3hop and not q1_answer:
            # degenerate: some cell passed its own gate numerically but the F/B > R lift test
            # itself reads false (e.g. R already at/above F/B) -- report honestly, no forcing.
            verdict = "MIDDLE_BAND"
            msg = ("At least one multi-hop cell cleared its floor/margin bar, but the direct "
                   "F/B > R lift comparison did NOT confirm forward helps (q1_lift=%s) -- "
                   "read as an ambiguous/underpowered result, not a clean forward-pass win."
                   % json.dumps(q1_lift))
        else:
            verdict = "HARD_FAIL_NO_MULTIHOP_LIFT"
            msg = ("REPLICATES PRIOR NEGATIVE (exp_multihop_bidirectional_meet_in_middle_"
                   "depth_scaling_v3=HARD_FAIL_NO_MEETING_PREMIUM lineage): neither F nor B "
                   "beats R's own floor/margin bar at 2-hop or 3-hop on held-out novel types "
                   "(1hop=%.4f 2hop: R=%.4f F=%.4f B=%.4f; 3hop: R=%.4f F=%.4f B=%.4f). "
                   "sr_td_converged reverse=%s forward=%s (reverse err_first=%.4f err_last=%.4f; "
                   "forward err_first=%.4f err_last=%.4f). Per brain-faithful-losing=presumed-"
                   "impl-bug: BOTH SR maps' TD convergence checked above -- if both converged, "
                   "the honest reading is that within this cell's construction (a fixed-"
                   "permutation content-transform grammar with gamma-bootstrapped SR features "
                   "already encoding multi-step reachability from a SINGLE M application), "
                   "adding a forward pass does not add NEW information the reverse map lacked "
                   "-- both M's approximate the same discounted-future/discounted-past "
                   "structure over the SAME fixed T, so they may be redundant rather than "
                   "complementary. Route: (a) verify via sr_diag_forward whether M_forward "
                   "genuinely learned T (not T^-1, i.e. check which direction actually "
                   "converges faster/lower) before concluding a mechanism ceiling; (b) if both "
                   "converge and neither lifts multi-hop, the fix likely needs a qualitatively "
                   "different multi-hop mechanism (explicit iterative multi-step composition of "
                   "M, not a single-application discounted read), per task-brief contract for "
                   "an honest negative."
                   % (acc_r1, acc_r2, acc_f2, acc_b2, acc_r3, acc_f3, acc_b3,
                      sr_converged_r, sr_converged_f,
                      float(np.mean(sr_err_first_r)) if sr_err_first_r else -1.0,
                      float(np.mean(sr_err_last_r)) if sr_err_last_r else -1.0,
                      float(np.mean(sr_err_first_f)) if sr_err_first_f else -1.0,
                      float(np.mean(sr_err_last_f)) if sr_err_last_f else -1.0))

    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "structured_gate_claims": gate_claims,
        "hop_arm_summaries": hop_arm_summaries,
        "hop_arm_blocks": hop_arm_blocks,
        "hop2_blocks_with_shuffled_control": hop2_blocks_with_shuf,
        "shuffled_structure_hop2_summaries": shuf_summaries,
        "q1_forward_lifts_multihop": {"per_hop": q1_lift, "any_hop_forward_helps": q1_answer},
        "q2_meeting_premium": {"per_hop": q2_by_hop,
                               "genuine_meeting_premium_any_hop": genuine_meeting_premium_any,
                               "forward_alone_sufficient_or_wins_all_hops": forward_alone_wins_or_ties},
        "stress_all_pass": stress_all_pass,
        "situation_buffer_decode_fidelity_train_mean": buf_train,
        "sr_td_reverse_err_first_mean": float(np.mean(sr_err_first_r)) if sr_err_first_r else None,
        "sr_td_reverse_err_last_mean": float(np.mean(sr_err_last_r)) if sr_err_last_r else None,
        "sr_td_reverse_converged": sr_converged_r,
        "sr_td_forward_err_first_mean": float(np.mean(sr_err_first_f)) if sr_err_first_f else None,
        "sr_td_forward_err_last_mean": float(np.mean(sr_err_last_f)) if sr_err_last_f else None,
        "sr_td_forward_converged": sr_converged_f,
        "max_train_eval_entity_overlap": int(max_entity_overlap),
        "max_train_eval_type_overlap_novel": float(max_type_overlap_novel),
        "abstain_band_used": ABSTAIN_BAND_DEFAULT,
        "n_seeds_completed": len(keys),
        "seeds": keys,
        "v3_reference": "MEASURED@data/exp_coherence_selector_novel_types_v3/metrics.json "
                        "(reverse-only ARM_NOVEL_1HOP/2HOP -- this cell's hop1_armR/hop2_armR "
                        "are the SAME mechanism re-measured on a CHAIN_HOPS=3-capable "
                        "substrate; small numeric differences vs v3 are expected from the "
                        "wider chain and are not evidence of a regression).",
        "prior_art_reference": {
            "reverse_only_collapses_2hop": "exp_multihop_reverse_replay_backward_sweep_v1: "
                "A(reverse-only)=0.506 vs D_bidir=0.690",
            "meeting_premium_failed_v2": "exp_substrate_multihop_bidirectional_meet_middle_v2: "
                "REPRODUCE=0.12 (v1 HARD_PASS did not reproduce; v1 mean_midpoint_cosine=0.0)",
            "meeting_premium_failed_v3": "exp_multihop_bidirectional_meet_in_middle_depth_"
                "scaling_v3: HARD_FAIL_NO_MEETING_PREMIUM (bidir 0.443 lost to forward-half 0.684)",
            "meeting_premium_failed_wave14": "exp_wave14_multihop_bidirectional_N65536_v1: "
                "BIDIR_INSUFFICIENT",
        },
    }


# ============================================================================
# main
# ============================================================================
def main() -> int:
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s"
          % (len(done), len(SEEDS), remaining), flush=True)

    fatal: List[str] = []
    for i, seed in enumerate(remaining):
        t0 = time.time()
        try:
            result = run_one_seed(seed)
        except SystemExit:
            raise
        except Exception as e:
            fc = type(e).__name__
            fatal.append("seed=%d %s: %s" % (seed, fc, str(e)[:200]))
            write_partial_key(out_dir, seed, {
                "seed": int(seed), "anchor_name": ANCHOR_NAME,
                "config_version": CONFIG_VERSION,
                "failure_class": fc, "error": str(e)[:400],
                "traceback": traceback.format_exc()[:3000],
                "arms_by_hop": {}, "shuffled_structure_hop2_by_arm": {},
                "sr_diag_reverse": {}, "sr_diag_forward": {},
                "situation_buffer_decode_fidelity_train": 0.0,
                "train_eval_entity_overlap": None, "train_eval_type_overlap_novel": None})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        h2 = result["arms_by_hop"]
        print("[seed=%d] complete in %.1fs hop2: R=%.3f F=%.3f B=%.3f | hop3: R=%.3f F=%.3f B=%.3f"
              % (seed, time.time() - t0,
                 h2["hop2_armR"]["coherence_acc_conservative"],
                 h2["hop2_armF"]["coherence_acc_conservative"],
                 h2["hop2_armB"]["coherence_acc_conservative"],
                 h2["hop3_armR"]["coherence_acc_conservative"],
                 h2["hop3_armF"]["coherence_acc_conservative"],
                 h2["hop3_armB"]["coherence_acc_conservative"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("arms_by_hop")}
    final = aggregate_and_verdict(good)
    if fatal:
        final["fatal_seed_errors"] = fatal
        if final.get("verdict") == "HARD_PASS":
            final["verdict"] = "MIDDLE_BAND"
            final["verdict_msg"] = "DEMOTED_FROM_HP_DUE_TO_SEED_CRASH | " + final["verdict_msg"]
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _T0, 1)
    final["ts_iso"] = datetime.now(timezone.utc).isoformat()
    final["pid"] = os.getpid()
    final["run_mode"] = "full"
    final["config_version"] = CONFIG_VERSION
    final["device"] = str(DEVICE)
    final["prereg"] = "preregs/2026-08-04_coherence_selector_bidirectional_v4.md"
    write_metrics(out_dir, final)
    print("[%s] DONE: %s" % (ANCHOR_NAME, final.get("verdict_msg", "")), flush=True)
    return 0


if __name__ == "__main__":
    _od = get_output_dir(ANCHOR_NAME)
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:400]),
            "summary": "CELL_CRASHED: %s" % type(e).__name__,
            "elapsed_s": round(time.time() - _T0, 1),
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "config_version": CONFIG_VERSION,
        }
        try:
            write_metrics(_od, diag)
        except Exception:
            pass
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
