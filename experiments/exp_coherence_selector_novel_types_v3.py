"""coherence_selector_novel_types_v3 -- discriminating stress-test of v2: does the
reverse-replay coherence selector learn an ABSTRACT structural TRANSFORMATION (generalizes
to types never seen in TRAIN) or a MEMORIZED per-type TABLE (works only for seen types)?

WHY v3 (Director brief, WHERE-banner commit history; data/exp_coherence_selector_insim_v2/
metrics.json = HARD_PASS): v2 fixed v1's entity-memorization collapse by giving entities a
shared TYPE vocabulary + a fixed grammar. It generalized to NOVEL ENTITIES (entity_overlap=0,
structural_lift 0.73 vs a shuffled-structure ablation) -- BUT v2's EVAL reused the SAME 10
types as TRAIN (train_eval_type_overlap_frac == 1.0). v2's "grammar" was `RULE: type_id ->
type_id`, a random BIJECTION over discrete type INDICES (a 10x10 lookup table). A lookup
table has NO content in the type embeddings that reveals RULE -- cause-type c's vector and
effect-type RULE[c]'s vector are UNRELATED i.i.d. random vectors. This means RULE[novel_type]
is UNDEFINED/unlearnable for a type index M_backward never saw: a discrete-ID lookup table is
UNSOLVABLE IN PRINCIPLE for novel types by ANY mechanism. Testing v2's mechanism against novel
types would therefore be an UNFAIR, rigged-to-fail test -- not evidence about the mechanism.

THE FIX (this is the whole point of v3): replace the arbitrary per-type-ID lookup with a
CONSISTENT STRUCTURAL TRANSFORM T that is a FIXED function of VECTOR CONTENT, the SAME T for
EVERY type, seen or novel. Concretely: T = a fixed random permutation of the N_DIM coordinate
axes (an orthogonal, invertible, bipolar-preserving linear operator -- generated once per
seed). Every type t (seen or novel) gets an independent i.i.d. random bipolar "identity"
vector b_t (same generative distribution for seen and novel types -- this is the fairness-
critical property: nothing distinguishes a novel type's DISTRIBUTION from a seen type's).
A causal chain of length K for type t is the literal iterated orbit of T:
    u_0 = b_t,  u_1 = T(u_0),  u_2 = T(u_1) = T(T(b_t))
Entities instantiating hop k of type t's chain get embedding = normalize(u_k + per-instance
noise). A cause->effect edge is hop_k -> hop_{k+1} WITHIN one chain. Because T is a SINGLE
fixed permutation applied identically regardless of which type produced the input vector, the
relation "effect content = T(cause content)" is SOLVABLE IN PRINCIPLE for a type never seen at
train time -- a mechanism that has learned T^-1 (not a per-type lookup) can invert it for ANY
content vector, novel or not. This is the "grammar-consistency" fairness property the task
brief demands: novel types are solvable in principle because the causal rule lives in VECTOR
GEOMETRY (content-addressable, hippocampal-relational-match style), not in a discrete type-ID
table. Contrast with v2's RULE: a novel type index has no entry in a 10x10 permutation matrix
-- unsolvable by ANY mechanism, an unfair test.

M_backward is trained via the SAME TD(0) SR-transport delta-rule as v1/v2 on TRAIN-partition
(types 0..N_TYPES_SEEN-1) chain transitions ONLY. If train_sr_transport's linear map M
actually converges toward T^-1 in the shared 2048-dim VECTOR SPACE (not toward a per-type
association keyed by discrete identity), it should recover the true cause of an EVAL episode
built from BRAND-NEW never-seen types (fresh i.i.d. b_t vectors, disjoint type-index range)
purely from vector content -- an ABSTRACT competence. If it instead only works for the TRAIN
types (memorized table despite content being technically available), that is the informative
negative the task brief asks to report honestly.

THREE STRESS ARMS (all scored against the SAME single M_backward per seed, trained ONCE on
TRAIN types only -- cheap, and directly tests whether the learned map is type-count-agnostic):
  ARM_NOVEL_1HOP (primary)  -- EVAL entities drawn from N_TYPES_NOVEL BRAND-NEW types
                               (disjoint index range from TRAIN types), 1-hop episodes
                               (outcome=hop1, true_cause=hop0, distractor=hop0 of a
                               different-type chain). THE primary novel-types discriminator.
  ARM_NOVEL_2HOP (multi-hop stress) -- SAME novel-type partition, but outcome=hop2,
                               true_cause=hop0 (grandparent, 2 hops back via the SAME chain),
                               distractor=hop0 of a different-type chain. Tests whether
                               coherence-selection (SR multi-step bootstrapping through gamma)
                               survives a longer causal chain on NOVEL types.
  ARM_NOVEL_SCALE (vocab-scale stress) -- a FOURTH, disjoint, larger type-index range
                               (N_TYPES_SCALE=40, 4x the seen vocabulary), 1-hop episodes,
                               using the SAME M_backward trained on only 10 seen types (no
                               retraining). Tests whether the learned map is type-COUNT
                               agnostic (a real content-transform competence should not care
                               how many novel types it is asked to invert).

FLOORS (each arm's EVAL, must fail): RECENCY, RANDOM, NO_REPLAY_LOCAL (identity-M raw cosine,
anti-tautology). SHUFFLED-STRUCTURE control (i.i.d. random bipolar replacing chain-structured
embeddings, M_backward held fixed) must collapse toward chance -- proves any win is
attributable to the learned content-transform, not a spurious cue. POSITIVE CONTROL (ORACLE,
reads the true chain edge) must be 100%/100% train/eval -- episode-construction sanity.

HONEST-RESULT CONTRACT (task brief): GENERALIZES on ARM_NOVEL_1HOP => the mechanism learned an
abstract transferable T^-1 = real competence. FAILS => it is table-limited despite the fair
content-addressable construction; report as an informative negative and route the direct
effect<->outcome content-MATCH reformulation (reach_control_targetcos-style, no learned M) as
next step. Per brain-faithful-losing=presumed-impl-bug: sr_diag err_first/err_last convergence
is inspected before concluding structural-features-don't-generalize.

Reuses (bit-identical import, not re-derived):
  experiments/exp_pfc_gate_cfrpe_trained_v2.py -- make_bipolar_E, train_sr_transport,
    reach_value, reach_control_targetcos, collect_rollout_transitions, _norm_rows
  hdlab/situation_model_accumulate.py -- AccumulateRegister (buffer sanity, not the scorer)
  hdlab/self_improving_loop.py -- decide_keep_or_revert, ABSTAIN_BAND_DEFAULT
  experiments/_seed_checkpoint.py -- resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics, record_gate, get_output_dir

Author: exp_dev-role direct run (Sonnet 5, agent-spawn), 2026-08-04.
Prereg: d:/AI/hd-instrument/preregs/2026-08-04_coherence_selector_novel_types_v3.md
Local-only cell: no queue, no remote dispatch, no push. Run directly:
  .venv/Scripts/python.exe experiments/exp_coherence_selector_novel_types_v3.py
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
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds, write_partial_key, aggregate_partials, write_metrics,
    record_gate, get_output_dir,
)
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402

ANCHOR_NAME = "coherence_selector_novel_types_v3"
DEVICE = torch.device("cpu")  # local-only cell, small scale, no GPU needed
DTYPE = torch.float32

# ------------------------------- config (LOCKED, PROSPECTIVE) ---------------------------
N_DIM = 2048
NOISE_FRAC = 0.05          # per-instance bit-flip fraction over its chain-hop vector

# Disjoint type-index ranges (fairness bookkeeping): TRAIN types are the ONLY types
# M_backward's SR training ever sees. NOVEL and SCALE types are drawn i.i.d. from the SAME
# generative distribution but occupy disjoint index ranges never touched during training.
N_TYPES_SEEN = 10          # 0 .. 9         (TRAIN)
N_TYPES_NOVEL = 10         # 10 .. 19       (ARM_NOVEL_1HOP / ARM_NOVEL_2HOP, EVAL-only)
N_TYPES_SCALE = 40         # 20 .. 59       (ARM_NOVEL_SCALE, EVAL-only, 4x vocab)
N_TYPES_TOTAL = N_TYPES_SEEN + N_TYPES_NOVEL + N_TYPES_SCALE

CHAIN_HOPS = 2              # chain = [hop0, hop1, hop2] (3 nodes, 2 edges) per (type, instance)
N_CHAINS_PER_TYPE_TRAIN = 26
N_CHAINS_PER_TYPE_NOVEL = 26
N_CHAINS_PER_TYPE_SCALE = 10   # smaller per-type count at 4x vocab keeps total node count sane

N_EPISODES_TRAIN = 60
N_EPISODES_EVAL = 60          # per arm

SR_STEPS = 2000
SR_BATCH = 128
SR_LR = 0.5
GAMMA = 0.85
ROLLOUT_PER_NODE = 40
ROLLOUT_MAX_LEN = 3
SEEDS = [7, 17, 23, 31, 41]

HP_EVAL_ACC_FLOOR = 0.75
HP_FLOOR_MARGIN = 0.15
HP_SHUFFLED_CEIL = 0.65
HP_STRUCTURAL_LIFT_MIN = 0.15

CONFIG_VERSION = (
    "ANCHOR=%s,N_DIM=%d,N_TYPES_SEEN=%d,N_TYPES_NOVEL=%d,N_TYPES_SCALE=%d,noise_frac=%.2f,"
    "chain_hops=%d,n_chains_train=%d,n_chains_novel=%d,n_chains_scale=%d,n_ep_train=%d,"
    "n_ep_eval=%d,sr_steps=%d,sr_batch=%d,gamma=%.2f,seeds=%s,abstain_band=%.3f"
) % (ANCHOR_NAME, N_DIM, N_TYPES_SEEN, N_TYPES_NOVEL, N_TYPES_SCALE, NOISE_FRAC,
     CHAIN_HOPS, N_CHAINS_PER_TYPE_TRAIN, N_CHAINS_PER_TYPE_NOVEL, N_CHAINS_PER_TYPE_SCALE,
     N_EPISODES_TRAIN, N_EPISODES_EVAL, SR_STEPS, SR_BATCH, GAMMA, SEEDS, ABSTAIN_BAND_DEFAULT)

_T0 = time.time()


# ============================================================================
# fixed structural transform T (permutation of coordinate axes) + chain construction
# ============================================================================
def build_perm_transform(n_dim: int, g: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """T = permutation of the n_dim coordinate axes (fixed once per seed, SAME for every
    type). Orthogonal, invertible, bipolar-value-preserving. Returns (perm, inv_perm) s.t.
    T(v) = v[..., perm] and T^-1(v) = v[..., inv_perm]."""
    perm = g.permutation(n_dim)
    inv = np.argsort(perm)
    return perm, inv


def apply_perm(v: torch.Tensor, perm_idx: np.ndarray) -> torch.Tensor:
    idx = torch.as_tensor(perm_idx, dtype=torch.long, device=v.device)
    return v.index_select(-1, idx)


def build_type_base_vectors(n_types_total: int, n_dim: int, gen: torch.Generator) -> torch.Tensor:
    """[n_types_total, n_dim] i.i.d. bipolar base vector per type index. SEEN, NOVEL, and
    SCALE type ranges are drawn from this SAME call / SAME distribution -- the fairness-
    critical property: nothing about a novel type's generative process differs from a seen
    type's, only its index range and whether TRAIN ever samples it."""
    return make_bipolar_E(n_types_total, n_dim, gen)


def build_chain_trajectories(base_vectors: torch.Tensor, perm_idx: np.ndarray,
                             chain_hops: int) -> torch.Tensor:
    """[n_types_total, chain_hops+1, n_dim]: u_0=b_t, u_k=T(u_{k-1}) -- the noise-free
    orbit of T starting at each type's base vector. Same T for every type (the grammar)."""
    n_types, n_dim = base_vectors.shape
    traj = torch.zeros((n_types, chain_hops + 1, n_dim), dtype=DTYPE, device=DEVICE)
    traj[:, 0, :] = base_vectors
    for k in range(1, chain_hops + 1):
        traj[:, k, :] = apply_perm(traj[:, k - 1, :], perm_idx)
    return traj


class ChainPartition:
    """A set of independently-instantiated causal chains over a fixed type-index range.
    node id -> (type, hop, chain_idx). Embedding[node] = normalize(traj[type,hop] + noise).
    predecessors[node_at_hop_k+1] = [node_at_hop_k] within the SAME chain (1 predecessor)."""

    def __init__(self, type_ids: List[int], n_chains_per_type: int, traj: torch.Tensor,
                noise_frac: float, id_start: int, gen: torch.Generator):
        self.type_ids = list(type_ids)
        self.n_chains_per_type = n_chains_per_type
        self.chain_hops = traj.shape[1] - 1
        n_chains = len(type_ids) * n_chains_per_type
        n_nodes = n_chains * (self.chain_hops + 1)
        node_type = np.zeros(n_nodes, dtype=np.int64)
        node_hop = np.zeros(n_nodes, dtype=np.int64)
        node_chain = np.zeros(n_nodes, dtype=np.int64)
        chain_nodes: List[List[int]] = []  # chain_idx -> [node_id at hop0, hop1, ...]
        nid = id_start
        cidx = 0
        for t in type_ids:
            for _c in range(n_chains_per_type):
                nodes_this_chain = []
                for k in range(self.chain_hops + 1):
                    node_type[nid - id_start] = t
                    node_hop[nid - id_start] = k
                    node_chain[nid - id_start] = cidx
                    nodes_this_chain.append(nid)
                    nid += 1
                chain_nodes.append(nodes_this_chain)
                cidx += 1
        self.node_ids = list(range(id_start, nid))
        self.node_type = node_type
        self.node_hop = node_hop
        self.node_chain = node_chain
        self.chain_nodes = chain_nodes  # [n_chains][chain_hops+1]
        self.id_start = id_start
        self.id_end = nid  # exclusive

        # embeddings: normalize(traj[type,hop] + individual bit-flip noise)
        idx_type = torch.as_tensor(node_type, dtype=torch.long, device=DEVICE)
        idx_hop = torch.as_tensor(node_hop, dtype=torch.long, device=DEVICE)
        base = traj[idx_type, idx_hop, :]  # [n_nodes, n_dim]
        flip_mask = (torch.rand(base.shape, generator=gen, device=DEVICE) < noise_frac)
        E = torch.where(flip_mask, -base, base)
        self.E = _norm_rows(E)

        # predecessors: node at hop k+1 <- node at hop k, within chain
        predecessors: Dict[int, List[int]] = {}
        for nodes in chain_nodes:
            for k in range(1, len(nodes)):
                predecessors[nodes[k]] = [nodes[k - 1]]
        self.predecessors = predecessors

    def grandparent(self, node_id: int) -> Optional[int]:
        """2-hop ancestor (hop k-2), or None if not available."""
        p = self.predecessors.get(node_id)
        if not p:
            return None
        return self.predecessors.get(p[0], [None])[0] if self.predecessors.get(p[0]) else None


def build_episodes(part: ChainPartition, n_episodes: int, hop_distance: int,
                   g: np.random.Generator) -> List[Dict[str, Any]]:
    """Episode: outcome = a hop-`hop_distance` node of some chain; true_cause = the node
    `hop_distance` hops earlier in the SAME chain; distractor = the hop-0 node of a
    DIFFERENT-TYPE chain (guaranteed non-causal: different type -> different T-orbit ->
    genuinely unrelated content, removing same-type-but-unsampled ambiguity). Recency trap:
    distractor positioned narratively MORE RECENT than true_cause."""
    n_chains = len(part.chain_nodes)
    if n_chains == 0:
        return []
    episodes: List[Dict[str, Any]] = []
    tries = 0
    while len(episodes) < n_episodes and tries < n_episodes * 80:
        tries += 1
        cidx = int(g.integers(0, n_chains))
        nodes = part.chain_nodes[cidx]
        if hop_distance >= len(nodes):
            continue
        outcome = nodes[hop_distance]
        true_cause = nodes[0]
        outcome_type = int(part.node_type[outcome - part.id_start])
        # distractor: hop-0 node of a different-type chain
        distr = None
        for _try in range(60):
            dcidx = int(g.integers(0, n_chains))
            dnode = part.chain_nodes[dcidx][0]
            dtype = int(part.node_type[dnode - part.id_start])
            if dtype == outcome_type:
                continue
            distr = dnode
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


# ============================================================================
# situation-model buffer integration (glass-box sanity, NOT the scorer) -- unchanged from v2
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


def selector_oracle(ep: Dict[str, Any], predecessors: Dict[int, List[int]],
                    hop_distance: int) -> str:
    if hop_distance == 1:
        ok = ep["true_cause"] in predecessors.get(ep["outcome"], [])
    else:
        p1 = predecessors.get(ep["outcome"], [])
        p0 = predecessors.get(p1[0], []) if p1 else []
        ok = bool(p0) and ep["true_cause"] == p0[0]
    return "true" if ok else "distractor"


def batched_reach_scores(episodes: List[Dict[str, Any]], E: torch.Tensor, id_start: int,
                         M: torch.Tensor, use_M: bool) -> Tuple[np.ndarray, np.ndarray]:
    if not episodes:
        return np.zeros(0), np.zeros(0)
    outc = torch.tensor([e["outcome"] - id_start for e in episodes], dtype=torch.long, device=DEVICE)
    tru = torch.tensor([e["true_cause"] - id_start for e in episodes], dtype=torch.long, device=DEVICE)
    dis = torch.tensor([e["distractor"] - id_start for e in episodes], dtype=torch.long, device=DEVICE)
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


def _score_episodes(episodes: List[Dict[str, Any]], predecessors: Dict[int, List[int]],
                    hop_distance: int, E: torch.Tensor, id_start: int, M_backward: torch.Tensor,
                    seed: int, rand_seed_offset: int) -> Dict[str, Any]:
    n = len(episodes)
    if n == 0:
        return {"n_episodes": 0}
    rg = np.random.default_rng(int(seed) * 999983 + rand_seed_offset)

    recency_correct = sum(1 for e in episodes if selector_recency(e) == "true")
    random_correct = sum(1 for e in episodes if selector_random(e, rg) == "true")
    oracle_correct = sum(1 for e in episodes if selector_oracle(e, predecessors, hop_distance) == "true")

    s_true_ctrl, s_distr_ctrl = batched_reach_scores(episodes, E, id_start, M_backward, use_M=False)
    norepl_correct = int(np.sum(s_true_ctrl > s_distr_ctrl))

    s_true_m, s_distr_m = batched_reach_scores(episodes, E, id_start, M_backward, use_M=True)
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


def _arm(part: ChainPartition, hop_distance: int, n_episodes: int, E_variant: torch.Tensor,
        M_backward: torch.Tensor, seed: int, rand_offset: int, g: np.random.Generator
        ) -> Dict[str, Any]:
    eps = build_episodes(part, n_episodes, hop_distance, g)
    real = _score_episodes(eps, part.predecessors, hop_distance, E_variant, part.id_start,
                           M_backward, seed, rand_offset)
    return real


# ============================================================================
# per-seed run
# ============================================================================
def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    perm_gen = np.random.default_rng(int(seed) * 100003 + 5)
    perm_idx, inv_perm_idx = build_perm_transform(N_DIM, perm_gen)  # fixed grammar T

    tgen = torch.Generator(device=DEVICE)
    tgen.manual_seed(int(seed) * 100003 + 1)
    base_vectors = build_type_base_vectors(N_TYPES_TOTAL, N_DIM, tgen)  # [N_TYPES_TOTAL, N_DIM]
    traj = build_chain_trajectories(base_vectors, perm_idx, CHAIN_HOPS)  # [N_TYPES_TOTAL, hops+1, N_DIM]

    types_seen = list(range(0, N_TYPES_SEEN))
    types_novel = list(range(N_TYPES_SEEN, N_TYPES_SEEN + N_TYPES_NOVEL))
    types_scale = list(range(N_TYPES_SEEN + N_TYPES_NOVEL, N_TYPES_TOTAL))

    egen_train = torch.Generator(device=DEVICE); egen_train.manual_seed(int(seed) * 100003 + 2)
    part_train = ChainPartition(types_seen, N_CHAINS_PER_TYPE_TRAIN, traj, NOISE_FRAC,
                                0, egen_train)

    egen_novel = torch.Generator(device=DEVICE); egen_novel.manual_seed(int(seed) * 100003 + 3)
    part_novel = ChainPartition(types_novel, N_CHAINS_PER_TYPE_NOVEL, traj, NOISE_FRAC,
                                part_train.id_end, egen_novel)

    egen_scale = torch.Generator(device=DEVICE); egen_scale.manual_seed(int(seed) * 100003 + 4)
    part_scale = ChainPartition(types_scale, N_CHAINS_PER_TYPE_SCALE, traj, NOISE_FRAC,
                                part_novel.id_end, egen_scale)

    # anti-memorization bookkeeping: entity id ranges are strictly disjoint by construction;
    # type index ranges are strictly disjoint too (novel/scale types NEVER used in TRAIN).
    entity_overlap = 0  # disjoint id ranges by construction (assert below)
    type_overlap_novel = float(len(set(types_seen) & set(types_novel)))
    type_overlap_scale = float(len(set(types_seen) & set(types_scale)))
    assert set(range(part_train.id_start, part_train.id_end)).isdisjoint(
        range(part_novel.id_start, part_novel.id_end))
    assert set(range(part_train.id_start, part_train.id_end)).isdisjoint(
        range(part_scale.id_start, part_scale.id_end))

    # --- train M_backward ONCE on TRAIN-partition (seen types) chain transitions only ---
    adj_for_rollout = [dict(part_train.predecessors)]
    n_nodes_train = part_train.id_end - part_train.id_start
    n_transitions = min(200000, ROLLOUT_PER_NODE * n_nodes_train)
    transitions = collect_rollout_transitions(
        adj_for_rollout, n_ops=1, V=part_train.id_end, n_transitions=n_transitions,
        max_len=ROLLOUT_MAX_LEN, g=g)

    sr_gen = torch.Generator(device=DEVICE)
    sr_gen.manual_seed(int(seed) * 7919 + 1)
    M_backward, sr_diag = train_sr_transport(
        part_train.E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)

    # situation-model buffer glass-box sanity (real integration, not the scorer)
    buf_gen = torch.Generator(device=DEVICE); buf_gen.manual_seed(int(seed) * 31337 + 1)
    ep_train_1hop_for_buf = build_episodes(part_train, N_EPISODES_TRAIN, 1, g)
    buf_fidelity_train = situation_buffer_check(ep_train_1hop_for_buf, buf_gen)

    # --- TRAIN partition self-check (1-hop, known types -- sanity, not the discriminator) ---
    train_metrics = _arm(part_train, 1, N_EPISODES_TRAIN, part_train.E, M_backward,
                        seed, 1, g)

    # --- ARM_NOVEL_1HOP (primary discriminator) --------------------------------------------
    novel_1hop = _arm(part_novel, 1, N_EPISODES_EVAL, part_novel.E, M_backward, seed, 2, g)

    # --- ARM_NOVEL_2HOP (multi-hop stress, same novel-type partition) ----------------------
    novel_2hop = _arm(part_novel, 2, N_EPISODES_EVAL, part_novel.E, M_backward, seed, 3, g)

    # --- ARM_NOVEL_SCALE (vocab-scale stress: 4x novel types, same M_backward, no retrain) --
    scale_1hop = _arm(part_scale, 1, N_EPISODES_EVAL, part_scale.E, M_backward, seed, 4, g)

    # --- SHUFFLED-STRUCTURE control on ARM_NOVEL_1HOP's episodes ---------------------------
    # Replace the NOVEL partition's embeddings with i.i.d. random bipolar UNRELATED to the
    # T-orbit structure (destroys the content-transform signal). M_backward held FIXED.
    shuf_gen = torch.Generator(device=DEVICE); shuf_gen.manual_seed(int(seed) * 424243 + 1)
    n_novel_nodes = part_novel.id_end - part_novel.id_start
    E_shuffled_novel = make_bipolar_E(n_novel_nodes, N_DIM, shuf_gen)
    g_shuf = np.random.default_rng(int(seed) * 313 + 9)
    novel_1hop_shuffled = _arm(part_novel, 1, N_EPISODES_EVAL, E_shuffled_novel, M_backward,
                               seed, 5, g_shuf)

    return {
        "seed": int(seed),
        "run_mode": "full",
        "N": N_DIM,
        "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "sr_diag": sr_diag,
        "situation_buffer_decode_fidelity_train": buf_fidelity_train,
        "train_eval_entity_overlap": entity_overlap,
        "train_eval_type_overlap_novel": type_overlap_novel,
        "train_eval_type_overlap_scale": type_overlap_scale,
        "train_partition": train_metrics,
        "arm_novel_1hop": novel_1hop,
        "arm_novel_2hop": novel_2hop,
        "arm_novel_scale": scale_1hop,
        "arm_novel_1hop_shuffled_structure": novel_1hop_shuffled,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def _summ(per_seed: Dict[str, Dict[str, Any]], keys: List[str], partition: str) -> Dict[str, Any]:
    def _col(field: str) -> List[float]:
        out = []
        for k in keys:
            v = per_seed[k].get(partition, {}).get(field)
            if v is not None:
                out.append(float(v))
        return out

    fields = ["recency_acc", "random_acc", "no_replay_local_acc", "oracle_acc",
              "coherence_acc_conservative", "coherence_abstain_rate",
              "glassbox_margin_mean", "glassbox_margin_positive_frac"]
    out: Dict[str, Any] = {}
    for f in fields:
        vals = _col(f)
        out[f] = {"mean": float(np.mean(vals)) if vals else None,
                  "std": float(np.std(vals)) if vals else None,
                  "n_seeds": len(vals),
                  "per_seed": {keys[i]: vals[i] for i in range(len(vals))} if vals else {}}
    min_margins = _col("glassbox_margin_min")
    out["glassbox_margin_min_over_seeds"] = float(np.min(min_margins)) if min_margins else None
    return out


def _arm_gate_block(name: str, summary: Dict[str, Any], shuffled_summary: Optional[Dict[str, Any]],
                    prefix: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], bool]:
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
        record_gate("%s_margin_min_over_seeds" % prefix, margin_min or -999.0, 0.0, ">",
                   "%s: true-vs-distractor reach margin positive every seed" % name),
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

    arm_pass = beats_floors and shuffled_ok
    block = {
        "coherence_eval_acc": coh, "recency_acc": rec, "random_acc": rand,
        "no_replay_local_acc": norepl, "lift_over_recency": lift_recency,
        "lift_over_random": lift_random, "lift_over_no_replay_local": lift_norepl,
        "min_lift_over_floors": min_lift, "margin_min_over_seeds": margin_min,
        "margin_all_positive": margin_all_positive, "beats_all_floors": beats_floors,
        "coherence_eval_shuffled_structure_acc": coh_shuf,
        "structural_lift_minus_shuffled": structural_lift,
        "shuffled_control_ok": shuffled_ok if shuffled_summary is not None else None,
        "arm_pass": arm_pass,
    }
    return block, gates, arm_pass


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    train_summary = _summ(per_seed, keys, "train_partition")
    novel1_summary = _summ(per_seed, keys, "arm_novel_1hop")
    novel2_summary = _summ(per_seed, keys, "arm_novel_2hop")
    scale_summary = _summ(per_seed, keys, "arm_novel_scale")
    novel1_shuf_summary = _summ(per_seed, keys, "arm_novel_1hop_shuffled_structure")

    buf_train = float(np.mean([per_seed[k]["situation_buffer_decode_fidelity_train"]
                               for k in keys])) if keys else 0.0
    oracle_train = train_summary["oracle_acc"]["mean"] or 0.0
    oracle_novel1 = novel1_summary["oracle_acc"]["mean"] or 0.0
    oracle_novel2 = novel2_summary["oracle_acc"]["mean"] or 0.0
    oracle_scale = scale_summary["oracle_acc"]["mean"] or 0.0

    max_entity_overlap = max((per_seed[k].get("train_eval_entity_overlap", 0) for k in keys),
                             default=0)
    max_type_overlap_novel = max((per_seed[k].get("train_eval_type_overlap_novel", 0.0)
                                  for k in keys), default=0.0)
    max_type_overlap_scale = max((per_seed[k].get("train_eval_type_overlap_scale", 0.0)
                                  for k in keys), default=0.0)

    block_1hop, gates_1hop, pass_1hop = _arm_gate_block(
        "ARM_NOVEL_1HOP", novel1_summary, novel1_shuf_summary, "novel1hop")
    block_2hop, gates_2hop, pass_2hop = _arm_gate_block(
        "ARM_NOVEL_2HOP", novel2_summary, None, "novel2hop")
    block_scale, gates_scale, pass_scale = _arm_gate_block(
        "ARM_NOVEL_SCALE", scale_summary, None, "novelscale")

    positive_control_ok = (oracle_train >= 0.999 and oracle_novel1 >= 0.999
                           and oracle_novel2 >= 0.999 and oracle_scale >= 0.999)
    recurring_entity_clean = (max_entity_overlap == 0 and max_type_overlap_novel == 0.0
                              and max_type_overlap_scale == 0.0)

    gate_claims = (
        [record_gate("positive_control_oracle_train", oracle_train, 0.999, ">=", "chain sanity"),
         record_gate("positive_control_oracle_novel1hop", oracle_novel1, 0.999, ">=", "chain sanity"),
         record_gate("positive_control_oracle_novel2hop", oracle_novel2, 0.999, ">=", "chain sanity"),
         record_gate("positive_control_oracle_scale", oracle_scale, 0.999, ">=", "chain sanity"),
         record_gate("no_entity_overlap", max_entity_overlap, 0, "==", "TRAIN/EVAL entity ids disjoint"),
         record_gate("no_type_overlap_novel", max_type_overlap_novel, 0.0, "==",
                    "novel types NEVER seen in TRAIN"),
         record_gate("no_type_overlap_scale", max_type_overlap_scale, 0.0, "==",
                    "scale types NEVER seen in TRAIN")]
        + gates_1hop + gates_2hop + gates_scale
    )

    sr_err_first = [per_seed[k]["sr_diag"]["err_first"] for k in keys
                    if per_seed[k]["sr_diag"].get("err_first") is not None]
    sr_err_last = [per_seed[k]["sr_diag"]["err_last"] for k in keys
                   if per_seed[k]["sr_diag"].get("err_last") is not None]
    sr_converged = bool(sr_err_first and sr_err_last and np.mean(sr_err_last) < np.mean(sr_err_first))

    stress_all_pass = bool(pass_1hop and pass_2hop and pass_scale)

    if not positive_control_ok:
        verdict = "GATE_FAILED_POSITIVE_CONTROL"
        msg = ("ORACLE positive control failed (train=%.4f novel1hop=%.4f novel2hop=%.4f "
               "scale=%.4f, need >=0.999 all) -- episode/chain construction itself is broken; "
               "no arm's verdict can be trusted." % (oracle_train, oracle_novel1, oracle_novel2,
                                                      oracle_scale))
    elif not recurring_entity_clean:
        verdict = "GATE_FAILED_ANTI_MEMORIZATION_CONSTRUCTION"
        msg = ("TRAIN/EVAL entity overlap=%d or type overlap (novel=%.3f, scale=%.3f) nonzero -- "
               "the novel-types test is mis-constructed; results cannot be trusted as evidence."
               % (max_entity_overlap, max_type_overlap_novel, max_type_overlap_scale))
    elif pass_1hop:
        verdict = "HARD_PASS" if stress_all_pass else "MIDDLE_BAND"
        msg = ("ABSTRACT-RULE VERDICT: ARM_NOVEL_1HOP (primary) GENERALIZES -- "
               "coherence_acc=%.4f beats RECENCY=%.4f RANDOM=%.4f NO_REPLAY_LOCAL=%.4f on "
               "BRAND-NEW never-seen types (type_overlap=0), margin positive every seed "
               "(min=%.4f); shuffled-structure control collapses to %.4f (structural_lift=%.4f) "
               "-- the win is attributable to a learned CONTENT-TRANSFORM (approx T^-1), not "
               "per-type memorization. Stress arms: 2HOP pass=%s (acc=%.4f), SCALE(4x vocab, "
               "no retrain) pass=%s (acc=%.4f). %s"
               % (block_1hop["coherence_eval_acc"], block_1hop["recency_acc"],
                  block_1hop["random_acc"], block_1hop["no_replay_local_acc"],
                  block_1hop["margin_min_over_seeds"] or -1.0,
                  block_1hop["coherence_eval_shuffled_structure_acc"],
                  block_1hop["structural_lift_minus_shuffled"],
                  pass_2hop, block_2hop["coherence_eval_acc"],
                  pass_scale, block_scale["coherence_eval_acc"],
                  "ALL stress arms confirm the abstract rule." if stress_all_pass else
                  "NOTE: at least one stress arm (2hop and/or scale) did NOT clear its own "
                  "floor/margin/positive-control bar -- read as a partial/scope-limited "
                  "competence, not a refutation of the primary novel-types result."))
    elif block_1hop["min_lift_over_floors"] > 0.0 or (
            novel1_summary["glassbox_margin_positive_frac"]["mean"] or 0.0) >= 0.8:
        verdict = "MIDDLE_BAND"
        msg = ("ARM_NOVEL_1HOP beats floors partially but below HARD-PASS bar "
               "(acc=%.4f, min_lift=%.4f, shuffled_ok=%s) -- right-mechanism-class/underpowered, "
               "not a refutation. sr_td_converged=%s (err_first=%.4f err_last=%.4f)."
               % (block_1hop["coherence_eval_acc"], block_1hop["min_lift_over_floors"],
                  block_1hop["shuffled_control_ok"], sr_converged,
                  float(np.mean(sr_err_first)) if sr_err_first else -1.0,
                  float(np.mean(sr_err_last)) if sr_err_last else -1.0))
    else:
        verdict = "HARD_FAIL"
        msg = ("MEMORIZED-TABLE VERDICT: ARM_NOVEL_1HOP does NOT beat RECENCY/RANDOM/"
               "NO_REPLAY_LOCAL floors on BRAND-NEW never-seen types despite the FAIR, "
               "content-addressable grammar (same fixed permutation T for every type, novel "
               "types drawn i.i.d. from the identical distribution as seen types) -- "
               "coherence_acc=%.4f recency=%.4f random=%.4f no_replay_local=%.4f min_lift=%.4f. "
               "sr_td_converged=%s (err_first=%.4f err_last=%.4f). Per brain-faithful-losing="
               "presumed-impl-bug: SR TD convergence %s -- if converged, the mechanism did NOT "
               "learn a transferable content-transform even when one was fair and available; "
               "route to the direct effect<->outcome content-MATCH reformulation "
               "(reach_control_targetcos-style raw geometric match within the episode, no "
               "learned type-table, hippocampal relational-match without an intervening SR map) "
               "as the next redesign step, per task-brief contract for an honest negative."
               % (block_1hop["coherence_eval_acc"], block_1hop["recency_acc"],
                  block_1hop["random_acc"], block_1hop["no_replay_local_acc"],
                  block_1hop["min_lift_over_floors"], sr_converged,
                  float(np.mean(sr_err_first)) if sr_err_first else -1.0,
                  float(np.mean(sr_err_last)) if sr_err_last else -1.0,
                  "CONFIRMED (err_last<err_first)" if sr_converged else "DID NOT CONFIRM -- "
                  "inspect SR training before concluding a mechanism-level failure"))

    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "structured_gate_claims": gate_claims,
        "train_partition_summary": train_summary,
        "arm_novel_1hop_summary": novel1_summary,
        "arm_novel_2hop_summary": novel2_summary,
        "arm_novel_scale_summary": scale_summary,
        "arm_novel_1hop_shuffled_structure_summary": novel1_shuf_summary,
        "arm_novel_1hop_block": block_1hop,
        "arm_novel_2hop_block": block_2hop,
        "arm_novel_scale_block": block_scale,
        "stress_all_pass": stress_all_pass,
        "situation_buffer_decode_fidelity_train_mean": buf_train,
        "sr_td_err_first_mean": float(np.mean(sr_err_first)) if sr_err_first else None,
        "sr_td_err_last_mean": float(np.mean(sr_err_last)) if sr_err_last else None,
        "sr_td_converged": sr_converged,
        "max_train_eval_entity_overlap": int(max_entity_overlap),
        "max_train_eval_type_overlap_novel": float(max_type_overlap_novel),
        "max_train_eval_type_overlap_scale": float(max_type_overlap_scale),
        "abstain_band_used": ABSTAIN_BAND_DEFAULT,
        "n_seeds_completed": len(keys),
        "seeds": keys,
        "v2_known_types_reference": "MEASURED@data/exp_coherence_selector_insim_v2/metrics.json "
                                    "(HARD_PASS, eval_acc for the SAME-types/novel-entity regime; "
                                    "compare against this cell's arm_novel_1hop for the "
                                    "known-vs-novel-types gap)",
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
                "train_partition": {}, "arm_novel_1hop": {}, "arm_novel_2hop": {},
                "arm_novel_scale": {}, "arm_novel_1hop_shuffled_structure": {},
                "sr_diag": {}, "situation_buffer_decode_fidelity_train": 0.0,
                "train_eval_entity_overlap": None, "train_eval_type_overlap_novel": None,
                "train_eval_type_overlap_scale": None})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs novel1hop=%.3f novel2hop=%.3f scale=%.3f "
              "shuffled=%.3f oracle_train=%.3f"
              % (seed, time.time() - t0,
                 result["arm_novel_1hop"]["coherence_acc_conservative"],
                 result["arm_novel_2hop"]["coherence_acc_conservative"],
                 result["arm_novel_scale"]["coherence_acc_conservative"],
                 result["arm_novel_1hop_shuffled_structure"]["coherence_acc_conservative"],
                 result["train_partition"]["oracle_acc"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("arm_novel_1hop")}
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
    final["prereg"] = "preregs/2026-08-04_coherence_selector_novel_types_v3.md"
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
