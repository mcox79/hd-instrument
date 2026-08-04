"""coherence_selector_insim_v2 -- STRUCTURAL/RELATIONAL causal-COHERENCE selector,
fixing v1's memorization collapse by construction.

WHY v2 (VET steer, WHERE-banner commit 711c61c24, notes/director_...): v1
(experiments/exp_coherence_selector_insim_v1.py, data/exp_coherence_selector_insim_v1/
metrics.json) landed HARD_FAIL: TRAIN coherence 1.000 but held-out EVAL 0.263 (BELOW the
0.50 RANDOM floor). Machinery was sound (SR TD converged, oracle 1.0/1.0). ROOT CAUSE
(Director-VET'd): v1's node embeddings were i.i.d. RANDOM BIPOLAR PER ENTITY, independent
of graph structure, and TRAIN/EVAL used DISJOINT node-id ranges -> M_backward learned an
ENTITY-SPECIFIC transition association matrix with ZERO shared structure between the TRAIN
and EVAL embedding spaces. There was nothing to generalize FROM -- pure memorization by
construction, not a mechanism failure.

THE FIX (the whole point of v2): make coherence a STRUCTURAL/RELATIONAL computation that
generalizes to NOVEL entities BY CONSTRUCTION. Entities are no longer atomic random symbols;
each entity carries a CONTENT TYPE drawn from a small SHARED vocabulary (N_TYPES, same
vocabulary instantiated independently in both TRAIN and EVAL partitions -- this is the
"recurring structural feature", per the task brief, analogous to action-type / effect-type
recurring across narrative episodes). A single fixed CAUSAL GRAMMAR (a random bijection
type->type, generated once per seed and used identically in both partitions) determines which
(cause_type, effect_type) pairs are causally connected: cause->effect edges are drawn ONLY
between entities respecting this grammar. Entity embeddings are TYPE_VECTOR[type(entity)]
perturbed by a small per-entity bit-flip (individuality without swamping the shared-type
signal). Because the SAME type vocabulary and grammar recur in EVAL, a backward SR-transport
map trained ONLY on TRAIN-partition reversed transitions is, in the type subspace, learning a
transferable type->type causal rule -- NOT an entity-identity lookup -- so it should
generalize to EVAL's disjoint (never-seen) entity IDs whose types recur from TRAIN.

Reuses (bit-identical import, not re-derived):
  experiments/exp_pfc_gate_cfrpe_trained_v2.py -- make_bipolar_E, train_sr_transport,
    reach_value, reach_control_targetcos, collect_rollout_transitions, _norm_rows
  hdlab/situation_model_accumulate.py -- AccumulateRegister (buffer sanity, not the scorer)
  hdlab/self_improving_loop.py -- decide_keep_or_revert, ABSTAIN_BAND_DEFAULT (control-flow
    architecture reuse over the reach-margin quantity)
  experiments/_seed_checkpoint.py -- resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics, record_gate

ARMS (paired, same episode set per seed/partition):
  RECENCY               -- picks the narratively-later candidate (the deliberate recency trap)
  RANDOM                -- coin flip
  NO_REPLAY_LOCAL        -- raw cosine cand-vs-outcome (M:=identity); anti-tautology guard
  COHERENCE_REVERSE_REPLAY (organ under test) -- reach_value via M_backward, abstain-gated
  ORACLE (positive control) -- reads the true graph edge directly

ANTI-MEMORIZATION CONTROLS (the mandatory can-fail battery, NOT gated by the primary bands
alone -- reported honestly regardless of outcome):
  1. NOVEL-ENTITY EVAL (primary): EVAL node IDs are DISJOINT from TRAIN by construction
     (asserted on disk); M_backward never sees an EVAL entity ID during SR training. A pass
     here cannot be entity-memorization.
  2. SHUFFLED-STRUCTURE control: re-score the SAME EVAL episodes (same true/distractor
     labels) but with EVAL entities' embeddings replaced by i.i.d. RANDOM bipolar vectors
     UNRELATED to type (i.e. v1's flawed construction, reproduced in-cell as the ablation).
     M_backward is held fixed (still the TRAIN-partition-trained map). This destroys the
     type-recurrence signal the mechanism is claimed to exploit; coherence accuracy under
     this control MUST collapse toward RANDOM (~0.50) for the v2 win to be attributed to
     structural recurrence rather than a spurious cue.
  3. RECURRING-ENTITY EXCLUSION: node-id sets for TRAIN/EVAL are asserted disjoint
     (train_eval_entity_overlap == 0) so a pass cannot be "it only works when the entity
     recurs" -- the SAME assertion also reports train_eval_type_overlap (== 1.0 by
     construction: the type VOCABULARY recurs even though no entity does), making explicit
     which axis is shared and which is not.

FLOORS (EVAL, must fail): RECENCY, RANDOM, NO_REPLAY_LOCAL.
POSITIVE CONTROL: ORACLE must be 100%/100% (train/eval) -- episode-construction pipeline
sanity, independent of the coherence mechanism.

Author: exp_dev-role direct run (Opus 4.8 1M, agent-spawn), 2026-08-04.
Prereg: d:/AI/hd-instrument/preregs/2026-08-04_coherence_selector_insim_v2.md
Local-only cell: no queue, no remote dispatch, no push. Run directly:
  .venv/Scripts/python.exe experiments/exp_coherence_selector_insim_v2.py
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
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp_pfc_gate_cfrpe_trained_v2 import (  # noqa: E402
    make_bipolar_E, train_sr_transport, reach_value, reach_control_targetcos,
    collect_rollout_transitions, _norm_rows,
)
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds, write_partial_key, aggregate_partials, write_metrics,
    record_gate, get_output_dir,
)
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402

ANCHOR_NAME = "coherence_selector_insim_v2"
DEVICE = torch.device("cpu")  # local-only cell, small scale, no GPU needed
DTYPE = torch.float32

# ------------------------------- config (LOCKED, PROSPECTIVE) ---------------------------
N_DIM = 2048
N_TYPES = 10             # shared content-type vocabulary (recurs across TRAIN/EVAL by construction)
NOISE_FRAC = 0.05         # per-entity bit-flip fraction over its TYPE_VECTOR (individuality, type-dominated)
V_TRAIN = 260             # TRAIN-partition node count (~26 nodes/type)
V_EVAL = 260              # EVAL-partition node count (disjoint index range, ~26 nodes/type)
V_TOTAL = V_TRAIN + V_EVAL
EDGE_DENSITY = 0.22       # expected out-edges per node within its own partition (RULE-respecting)
N_EPISODES_TRAIN = 60
N_EPISODES_EVAL = 60
SR_STEPS = 2000           # bumped from v1 (1500) -- structural task needs to learn a 10x10 type transform
SR_BATCH = 128
SR_LR = 0.5
GAMMA = 0.85
ROLLOUT_PER_V = 40
ROLLOUT_MAX_LEN = 3
SEEDS = [7, 17, 23, 31, 41]

HP_EVAL_ACC_FLOOR = 0.75
HP_FLOOR_MARGIN = 0.15    # coherence must beat every floor by >= this much on EVAL
HP_SHUFFLED_CEIL = 0.65   # anti-memorization: shuffled-structure control must land <= this on EVAL
HP_STRUCTURAL_LIFT_MIN = 0.15  # coherence_eval - shuffled_structure_eval must be >= this

CONFIG_VERSION = (
    "ANCHOR=%s,N_DIM=%d,N_TYPES=%d,noise_frac=%.2f,V_TRAIN=%d,V_EVAL=%d,density=%.2f,"
    "n_ep_train=%d,n_ep_eval=%d,sr_steps=%d,sr_batch=%d,gamma=%.2f,rollout_per_V=%d,"
    "seeds=%s,abstain_band=%.3f"
) % (ANCHOR_NAME, N_DIM, N_TYPES, NOISE_FRAC, V_TRAIN, V_EVAL, EDGE_DENSITY,
     N_EPISODES_TRAIN, N_EPISODES_EVAL, SR_STEPS, SR_BATCH, GAMMA, ROLLOUT_PER_V, SEEDS,
     ABSTAIN_BAND_DEFAULT)

_T0 = time.time()


# ============================================================================
# structural graph + episode construction
# ============================================================================
def build_partition_edges_structural(node_ids: List[int], types_arr: np.ndarray,
                                     inv_rule: np.ndarray, density: float,
                                     g: np.random.Generator) -> Dict[int, List[int]]:
    """Directed CAUSES edges within one partition, RULE-respecting: edge cause->effect
    exists only if types_arr[cause] == inv_rule[types_arr[effect]] (i.e. RULE[cause_type]
    == effect_type). Returns predecessors[effect] = [cause,...]."""
    n = len(node_ids)
    n_edges = max(4, int(round(density * n)))
    type_to_nodes: Dict[int, List[int]] = {}
    for nid in node_ids:
        type_to_nodes.setdefault(int(types_arr[nid]), []).append(nid)
    predecessors: Dict[int, List[int]] = {}
    made = 0
    guard = 0
    while made < n_edges and guard < n_edges * 60:
        guard += 1
        effect = int(node_ids[g.integers(0, n)])
        etype = int(types_arr[effect])
        ctype = int(inv_rule[etype])
        pool = type_to_nodes.get(ctype, [])
        if not pool:
            continue
        cause = int(pool[g.integers(0, len(pool))])
        if cause == effect:
            continue
        predecessors.setdefault(effect, [])
        if cause in predecessors[effect]:
            continue
        predecessors[effect].append(cause)
        made += 1
    return predecessors


def build_episodes_structural(node_ids: List[int], predecessors: Dict[int, List[int]],
                              types_arr: np.ndarray, inv_rule: np.ndarray,
                              n_episodes: int, g: np.random.Generator) -> List[Dict[str, Any]]:
    """Each episode: outcome (has >=1 real predecessor), true=a real predecessor (type-
    matching by construction), distractor=a same-partition node whose TYPE does NOT satisfy
    the grammar relation to the outcome (guaranteed non-causal, removes the ambiguity of a
    same-type-but-unsampled node), positioned MORE RECENT (closer to outcome) than true --
    the deliberate recency trap."""
    node_set = set(node_ids)
    candidates_outcomes = sorted([o for o, preds in predecessors.items() if preds])
    if not candidates_outcomes:
        return []
    episodes: List[Dict[str, Any]] = []
    tries = 0
    while len(episodes) < n_episodes and tries < n_episodes * 80:
        tries += 1
        outcome = int(candidates_outcomes[g.integers(0, len(candidates_outcomes))])
        preds = predecessors[outcome]
        preds_set = set(preds)
        true_cause = int(preds[g.integers(0, len(preds))])
        etype = int(types_arr[outcome])
        required_ctype = int(inv_rule[etype])
        distr = None
        for _try in range(60):
            cand = int(node_ids[g.integers(0, len(node_ids))])
            if cand == outcome or cand in preds_set:
                continue
            if int(types_arr[cand]) == required_ctype:
                continue  # type-matching but unsampled -- exclude to remove ambiguity
            distr = cand
            break
        if distr is None:
            continue
        pos_true = int(g.integers(0, 50))
        pos_distr = int(g.integers(60, 100))
        episodes.append({
            "outcome": outcome, "true_cause": true_cause, "distractor": distr,
            "pos_true": pos_true, "pos_distr": pos_distr, "pos_outcome": 100,
        })
    return episodes


def build_entity_embeddings(types_arr: np.ndarray, type_vectors: torch.Tensor,
                            noise_frac: float, gen: torch.Generator) -> torch.Tensor:
    """E[node] = TYPE_VECTOR[type(node)] with a small per-node bit-flip (individuality,
    type-dominated). types_arr: [V_TOTAL] int array. type_vectors: [N_TYPES, N_DIM] bipolar."""
    V = types_arr.shape[0]
    n = type_vectors.shape[1]
    idx = torch.tensor(types_arr.astype(np.int64), dtype=torch.long, device=DEVICE)
    base = type_vectors[idx]                                   # [V, n]
    flip_mask = (torch.rand((V, n), generator=gen, device=DEVICE) < noise_frac)
    E = torch.where(flip_mask, -base, base)
    return _norm_rows(E)


# ============================================================================
# situation-model buffer integration (glass-box sanity, NOT the scorer) -- unchanged from v1
# ============================================================================
def situation_buffer_check(episodes: List[Dict[str, Any]], gen: torch.Generator) -> float:
    if not episodes:
        return 0.0
    reg = AccumulateRegister(role_vocab=["MEMBER", "NON_MEMBER"], d=256, generator=gen,
                             max_event_slots=4)
    hits = 0
    total = 0
    for i, ep in enumerate(episodes):
        entity = "episode_%d" % i
        reg.add_event(entity, "MEMBER", 0)
        reg.add_event(entity, "MEMBER", 1)
        reg.add_event(entity, "MEMBER", 2)
        for slot in (0, 1, 2):
            role, _scores = reg.decode(entity, slot)
            total += 1
            if role == "MEMBER":
                hits += 1
    return float(hits) / float(max(1, total))


# ============================================================================
# selectors
# ============================================================================
def selector_recency(ep: Dict[str, Any]) -> str:
    return "true" if ep["pos_true"] > ep["pos_distr"] else "distractor"


def selector_random(ep: Dict[str, Any], g: np.random.Generator) -> str:
    return "true" if g.integers(0, 2) == 1 else "distractor"


def selector_oracle(ep: Dict[str, Any], predecessors: Dict[int, List[int]]) -> str:
    return "true" if ep["true_cause"] in predecessors.get(ep["outcome"], []) else "distractor"


def batched_reach_scores(episodes: List[Dict[str, Any]], E: torch.Tensor,
                         M: torch.Tensor, use_M: bool) -> Tuple[np.ndarray, np.ndarray]:
    if not episodes:
        return np.zeros(0), np.zeros(0)
    outc = torch.tensor([e["outcome"] for e in episodes], dtype=torch.long, device=DEVICE)
    tru = torch.tensor([e["true_cause"] for e in episodes], dtype=torch.long, device=DEVICE)
    dis = torch.tensor([e["distractor"] for e in episodes], dtype=torch.long, device=DEVICE)
    outc_E, tru_E, dis_E = E[outc], E[tru], E[dis]
    if use_M:
        s_true = reach_value(outc_E, tru_E, M)
        s_distr = reach_value(outc_E, dis_E, M)
    else:
        s_true = reach_control_targetcos(outc_E, tru_E)
        s_distr = reach_control_targetcos(outc_E, dis_E)
    return s_true.detach().cpu().numpy(), s_distr.detach().cpu().numpy()


def selector_coherence_abstain_gated(score_true: float, score_distr: float) -> Tuple[str, bool]:
    margin = score_true - score_distr
    adopt = decide_keep_or_revert({"true_over_distr": margin}, ABSTAIN_BAND_DEFAULT)
    if adopt == "true_over_distr":
        return "true", False
    return "distractor", True


def _score_partition(episodes: List[Dict[str, Any]], preds: Dict[int, List[int]],
                     E: torch.Tensor, M_backward: torch.Tensor, seed: int,
                     rand_seed_offset: int) -> Dict[str, Any]:
    """Scores one partition's episode set against embeddings E (may be the structural
    embedding table OR the shuffled-structure ablation table for the same episodes)."""
    n = len(episodes)
    if n == 0:
        return {"n_episodes": 0}
    rg = np.random.default_rng(int(seed) * 999983 + rand_seed_offset)

    recency_correct = sum(1 for e in episodes if selector_recency(e) == "true")
    random_correct = sum(1 for e in episodes if selector_random(e, rg) == "true")
    oracle_correct = sum(1 for e in episodes if selector_oracle(e, preds) == "true")

    s_true_ctrl, s_distr_ctrl = batched_reach_scores(episodes, E, M_backward, use_M=False)
    norepl_correct = int(np.sum(s_true_ctrl > s_distr_ctrl))

    s_true_m, s_distr_m = batched_reach_scores(episodes, E, M_backward, use_M=True)
    coh_correct = 0
    coh_abstain = 0
    margins = []
    for i in range(n):
        pick, abstained = selector_coherence_abstain_gated(float(s_true_m[i]), float(s_distr_m[i]))
        margins.append(float(s_true_m[i] - s_distr_m[i]))
        if abstained:
            coh_abstain += 1
            continue
        if pick == "true":
            coh_correct += 1

    return {
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


# ============================================================================
# per-seed run
# ============================================================================
def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    node_ids_train = list(range(0, V_TRAIN))
    node_ids_eval = list(range(V_TRAIN, V_TOTAL))

    # --- shared type vocabulary + causal grammar (recur across TRAIN/EVAL by construction) ---
    types_arr = g.integers(0, N_TYPES, size=V_TOTAL)
    rule_perm = g.permutation(N_TYPES)          # RULE[cause_type] = effect_type (bijection)
    inv_rule = np.argsort(rule_perm)             # inv_rule[effect_type] = cause_type

    tgen = torch.Generator(device=DEVICE)
    tgen.manual_seed(int(seed) * 100003 + 1)
    type_vectors = make_bipolar_E(N_TYPES, N_DIM, tgen)   # [N_TYPES, N_DIM]

    egen = torch.Generator(device=DEVICE)
    egen.manual_seed(int(seed) * 100003 + 2)
    E = build_entity_embeddings(types_arr, type_vectors, NOISE_FRAC, egen)  # [V_TOTAL, N_DIM]

    # anti-memorization guard #3: recurring-entity exclusion (structural check)
    entity_overlap = len(set(node_ids_train) & set(node_ids_eval))
    type_overlap_frac = float(len(set(types_arr[node_ids_train].tolist()) &
                                  set(types_arr[node_ids_eval].tolist())) / float(N_TYPES))

    pred_train = build_partition_edges_structural(node_ids_train, types_arr, inv_rule,
                                                  EDGE_DENSITY, g)
    pred_eval = build_partition_edges_structural(node_ids_eval, types_arr, inv_rule,
                                                 EDGE_DENSITY, g)
    predecessors: Dict[int, List[int]] = {}
    predecessors.update(pred_train)
    predecessors.update(pred_eval)

    ep_train = build_episodes_structural(node_ids_train, pred_train, types_arr, inv_rule,
                                         N_EPISODES_TRAIN, g)
    ep_eval = build_episodes_structural(node_ids_eval, pred_eval, types_arr, inv_rule,
                                        N_EPISODES_EVAL, g)

    # reversed rollout transitions: TRAIN-partition edges ONLY (M_backward never sees EVAL
    # entity IDs; it only sees TRAIN entities, whose TYPES recur in EVAL)
    adj_for_rollout = [dict()]
    for effect, causes in pred_train.items():
        adj_for_rollout[0].setdefault(effect, [])
        adj_for_rollout[0][effect].extend(causes)
    n_transitions = min(200000, ROLLOUT_PER_V * V_TRAIN)
    transitions = collect_rollout_transitions(
        adj_for_rollout, n_ops=1, V=V_TOTAL, n_transitions=n_transitions,
        max_len=ROLLOUT_MAX_LEN, g=g)

    sr_gen = torch.Generator(device=DEVICE)
    sr_gen.manual_seed(int(seed) * 7919 + 1)
    M_backward, sr_diag = train_sr_transport(
        E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)

    # situation-model buffer glass-box sanity (real integration, not the scorer)
    buf_gen = torch.Generator(device=DEVICE)
    buf_gen.manual_seed(int(seed) * 31337 + 1)
    buf_fidelity_train = situation_buffer_check(ep_train, buf_gen)
    buf_gen2 = torch.Generator(device=DEVICE)
    buf_gen2.manual_seed(int(seed) * 31337 + 2)
    buf_fidelity_eval = situation_buffer_check(ep_eval, buf_gen2)

    train_metrics = _score_partition(ep_train, pred_train, E, M_backward, seed, 1)
    eval_metrics = _score_partition(ep_eval, pred_eval, E, M_backward, seed, 2)

    # --- ANTI-MEMORIZATION CONTROL #2: SHUFFLED-STRUCTURE ablation on EVAL --------------
    # Replace EVAL entities' embeddings with i.i.d. random bipolar vectors UNRELATED to
    # type (v1's flawed construction, reproduced here as the ablation). M_backward is held
    # FIXED (still the TRAIN-structural-trained map). Same episodes/labels as ep_eval.
    shuf_gen = torch.Generator(device=DEVICE)
    shuf_gen.manual_seed(int(seed) * 424243 + 1)
    E_shuffled_eval_slice = make_bipolar_E(V_EVAL, N_DIM, shuf_gen)
    E_shuffled = E.clone()
    E_shuffled[V_TRAIN:V_TOTAL] = E_shuffled_eval_slice
    eval_metrics_shuffled = _score_partition(ep_eval, pred_eval, E_shuffled, M_backward, seed, 3)

    return {
        "seed": int(seed),
        "run_mode": "full",
        "N": N_DIM,
        "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "sr_diag": sr_diag,
        "situation_buffer_decode_fidelity_train": buf_fidelity_train,
        "situation_buffer_decode_fidelity_eval": buf_fidelity_eval,
        "train_eval_entity_overlap": entity_overlap,
        "train_eval_type_overlap_frac": type_overlap_frac,
        "train_partition": train_metrics,
        "eval_partition": eval_metrics,
        "eval_partition_shuffled_structure": eval_metrics_shuffled,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    def _col(partition: str, field: str) -> List[float]:
        out = []
        for k in keys:
            v = per_seed[k].get(partition, {}).get(field)
            if v is not None:
                out.append(float(v))
        return out

    def _summ(partition: str) -> Dict[str, Any]:
        fields = ["recency_acc", "random_acc", "no_replay_local_acc", "oracle_acc",
                  "coherence_acc_conservative", "coherence_abstain_rate",
                  "glassbox_margin_mean", "glassbox_margin_positive_frac"]
        out = {}
        for f in fields:
            vals = _col(partition, f)
            out[f] = {"mean": float(np.mean(vals)) if vals else None,
                      "std": float(np.std(vals)) if vals else None,
                      "n_seeds": len(vals),
                      "per_seed": {keys[i]: vals[i] for i in range(len(vals))} if vals else {}}
        min_margins = _col(partition, "glassbox_margin_min")
        out["glassbox_margin_min_over_seeds"] = float(np.min(min_margins)) if min_margins else None
        return out

    train_summary = _summ("train_partition")
    eval_summary = _summ("eval_partition")
    shuffled_summary = _summ("eval_partition_shuffled_structure")

    buf_train = float(np.mean([per_seed[k]["situation_buffer_decode_fidelity_train"]
                               for k in keys])) if keys else 0.0
    buf_eval = float(np.mean([per_seed[k]["situation_buffer_decode_fidelity_eval"]
                              for k in keys])) if keys else 0.0

    max_entity_overlap = max((per_seed[k].get("train_eval_entity_overlap", 0) for k in keys),
                             default=0)
    min_type_overlap = min((per_seed[k].get("train_eval_type_overlap_frac", 0.0) for k in keys),
                           default=0.0)

    coh_eval = eval_summary["coherence_acc_conservative"]["mean"] or 0.0
    rec_eval = eval_summary["recency_acc"]["mean"] or 0.0
    rand_eval = eval_summary["random_acc"]["mean"] or 0.0
    norepl_eval = eval_summary["no_replay_local_acc"]["mean"] or 0.0
    oracle_train = train_summary["oracle_acc"]["mean"] or 0.0
    oracle_eval = eval_summary["oracle_acc"]["mean"] or 0.0
    margin_min_over_seeds = eval_summary["glassbox_margin_min_over_seeds"]
    margin_pos_frac = eval_summary["glassbox_margin_positive_frac"]["mean"] or 0.0

    coh_shuffled = shuffled_summary["coherence_acc_conservative"]["mean"] or 0.0
    structural_lift = coh_eval - coh_shuffled

    lift_recency = coh_eval - rec_eval
    lift_random = coh_eval - rand_eval
    lift_norepl = coh_eval - norepl_eval
    min_lift = min(lift_recency, lift_random, lift_norepl)

    positive_control_ok = (oracle_train >= 0.999) and (oracle_eval >= 0.999)
    margin_all_positive = (margin_min_over_seeds is not None and margin_min_over_seeds > 0.0)
    recurring_entity_clean = (max_entity_overlap == 0) and (min_type_overlap >= 0.999)
    shuffled_control_fails = (coh_shuffled <= HP_SHUFFLED_CEIL) and (structural_lift >= HP_STRUCTURAL_LIFT_MIN)

    gate_claims = [
        record_gate("positive_control_oracle_train", oracle_train, 0.999, ">=",
                   "episode construction must be internally consistent"),
        record_gate("positive_control_oracle_eval", oracle_eval, 0.999, ">=",
                   "episode construction must be internally consistent"),
        record_gate("coherence_eval_acc_floor", coh_eval, HP_EVAL_ACC_FLOOR, ">=",
                   "HARD-PASS accuracy floor on held-out EVAL (novel entities)"),
        record_gate("min_lift_over_floors", min_lift, HP_FLOOR_MARGIN, ">=",
                   "coherence must beat ALL 3 floors by >=0.15 absolute on EVAL"),
        record_gate("glassbox_margin_min_over_seeds", margin_min_over_seeds or -999.0, 0.0, ">",
                   "true-vs-distractor reach margin must be positive in every seed"),
        record_gate("shuffled_structure_control_ceiling", coh_shuffled, HP_SHUFFLED_CEIL, "<=",
                   "ANTI-MEMORIZATION: destroying type-recurrence must collapse EVAL acc toward chance"),
        record_gate("structural_lift_min", structural_lift, HP_STRUCTURAL_LIFT_MIN, ">=",
                   "coherence_eval - shuffled_structure_eval must show real dependence on structure"),
        record_gate("recurring_entity_max_overlap", max_entity_overlap, 0, "==",
                   "TRAIN/EVAL entity id sets must be strictly disjoint (no memorization-by-recurrence path)"),
    ]

    if not positive_control_ok:
        verdict = "GATE_FAILED_POSITIVE_CONTROL"
        msg = ("ORACLE positive control failed (train=%.4f eval=%.4f, need >=0.999 both) -- "
               "episode-construction pipeline itself is broken; no other arm's verdict can be "
               "trusted." % (oracle_train, oracle_eval))
    elif not recurring_entity_clean:
        verdict = "GATE_FAILED_ANTI_MEMORIZATION_CONSTRUCTION"
        msg = ("TRAIN/EVAL entity overlap=%d (want 0) or type overlap frac=%.3f (want>=0.999) -- "
               "the compositional-generalization test itself is mis-constructed; results below "
               "cannot be trusted as evidence against memorization."
               % (max_entity_overlap, min_type_overlap))
    elif (coh_eval >= HP_EVAL_ACC_FLOOR and min_lift >= HP_FLOOR_MARGIN
          and margin_all_positive and shuffled_control_fails):
        verdict = "HARD_PASS"
        msg = ("COHERENCE_REVERSE_REPLAY EVAL(novel-entity) acc=%.4f beats RECENCY=%.4f "
               "(+%.4f) RANDOM=%.4f (+%.4f) NO_REPLAY_LOCAL=%.4f (+%.4f); glassbox margin "
               "positive in every seed (min=%.4f); ORACLE=%.4f/%.4f (train/eval); "
               "SHUFFLED-STRUCTURE control collapses to %.4f (<=%.2f ceiling, structural_lift="
               "%.4f>=%.2f) -- the win is attributable to STRUCTURAL type-recurrence, not "
               "entity memorization or a spurious cue."
               % (coh_eval, rec_eval, lift_recency, rand_eval, lift_random,
                  norepl_eval, lift_norepl, margin_min_over_seeds, oracle_train, oracle_eval,
                  coh_shuffled, HP_SHUFFLED_CEIL, structural_lift, HP_STRUCTURAL_LIFT_MIN))
    elif min_lift > 0.0 or margin_pos_frac >= 0.8:
        verdict = "MIDDLE_BAND"
        reason = []
        if coh_eval < HP_EVAL_ACC_FLOOR:
            reason.append("eval_acc %.4f<%.2f" % (coh_eval, HP_EVAL_ACC_FLOOR))
        if min_lift < HP_FLOOR_MARGIN:
            reason.append("min_lift %.4f<%.2f" % (min_lift, HP_FLOOR_MARGIN))
        if not shuffled_control_fails:
            reason.append("shuffled_control coh=%.4f structural_lift=%.4f DID NOT confirm "
                          "structural attribution (ceiling=%.2f, lift_min=%.2f)"
                          % (coh_shuffled, structural_lift, HP_SHUFFLED_CEIL,
                             HP_STRUCTURAL_LIFT_MIN))
        msg = ("COHERENCE beats floors on novel-entity EVAL but below the HARD-PASS bar (%s) -- "
               "read as right-mechanism-class/underpowered or partially-structural, not a "
               "refutation." % "; ".join(reason))
    else:
        verdict = "HARD_FAIL"
        msg = ("COHERENCE_REVERSE_REPLAY does NOT beat the RECENCY/RANDOM/NO_REPLAY_LOCAL "
               "floors on held-out novel-entity EVAL (eval_acc=%.4f, recency=%.4f random=%.4f "
               "no_replay_local=%.4f, min_lift=%.4f, margin_positive_frac=%.4f; shuffled_"
               "structure_control coh=%.4f). Per brain-faithful-losing=presumed-impl-bug: "
               "inspect sr_diag err_first/err_last for TD convergence before concluding "
               "structural-features-don't-generalize."
               % (coh_eval, rec_eval, rand_eval, norepl_eval, min_lift, margin_pos_frac,
                  coh_shuffled))

    sr_err_first = [per_seed[k]["sr_diag"]["err_first"] for k in keys
                    if per_seed[k]["sr_diag"].get("err_first") is not None]
    sr_err_last = [per_seed[k]["sr_diag"]["err_last"] for k in keys
                   if per_seed[k]["sr_diag"].get("err_last") is not None]

    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "structured_gate_claims": [c for c in gate_claims],
        "train_partition_summary": train_summary,
        "eval_partition_summary": eval_summary,
        "eval_partition_shuffled_structure_summary": shuffled_summary,
        "situation_buffer_decode_fidelity_train_mean": buf_train,
        "situation_buffer_decode_fidelity_eval_mean": buf_eval,
        "sr_td_err_first_mean": float(np.mean(sr_err_first)) if sr_err_first else None,
        "sr_td_err_last_mean": float(np.mean(sr_err_last)) if sr_err_last else None,
        "sr_td_converged": bool(sr_err_first and sr_err_last
                                and np.mean(sr_err_last) < np.mean(sr_err_first)),
        "lift_over_recency_eval": lift_recency,
        "lift_over_random_eval": lift_random,
        "lift_over_no_replay_local_eval": lift_norepl,
        "min_lift_over_floors_eval": min_lift,
        "coherence_eval_shuffled_structure_acc": coh_shuffled,
        "structural_lift_eval_minus_shuffled": structural_lift,
        "shuffled_control_fails_as_required": bool(shuffled_control_fails),
        "max_train_eval_entity_overlap": int(max_entity_overlap),
        "min_train_eval_type_overlap_frac": float(min_type_overlap),
        "abstain_band_used": ABSTAIN_BAND_DEFAULT,
        "n_seeds_completed": len(keys),
        "seeds": keys,
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
                "train_partition": {}, "eval_partition": {},
                "eval_partition_shuffled_structure": {},
                "sr_diag": {}, "situation_buffer_decode_fidelity_train": 0.0,
                "situation_buffer_decode_fidelity_eval": 0.0,
                "train_eval_entity_overlap": None, "train_eval_type_overlap_frac": None})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs eval_coh=%.3f eval_shuf=%.3f eval_recency=%.3f "
              "eval_random=%.3f eval_norepl=%.3f oracle_train=%.3f oracle_eval=%.3f"
              % (seed, time.time() - t0,
                 result["eval_partition"]["coherence_acc_conservative"],
                 result["eval_partition_shuffled_structure"]["coherence_acc_conservative"],
                 result["eval_partition"]["recency_acc"],
                 result["eval_partition"]["random_acc"],
                 result["eval_partition"]["no_replay_local_acc"],
                 result["train_partition"]["oracle_acc"],
                 result["eval_partition"]["oracle_acc"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("eval_partition")}
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
    final["prereg"] = "preregs/2026-08-04_coherence_selector_insim_v2.md"
    final["v1_eval_acc_for_comparison"] = "MEASURED@data/exp_coherence_selector_insim_v1/metrics.json"
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
