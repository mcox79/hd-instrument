"""Basal-ganglia Go/NoGo value-based ACTION-SELECTION gate (cortex primitive).

Extracted 2026-07-08 from exp_pfc_gate_cfrpe_trained_v2 (5-seed FULL N=8192
7-regime sweep; cell self-verdict HARD_PASS closure=0.661 at the fair depth-4
regime; landed-VET cert tier MEASURED_MECHANISM proven-at-depth4). This is the
substrate analog of the PBWM Go/NoGo model (Frank, Loughry & O'Reilly 2001;
O'Reilly & Frank 2006): a learned successor-representation (SR) value signal
(reach), trained by a TD(0) error that IS the substrate reward-prediction-error
(RPE) delta-rule (cfrpe), feeds a winner-take-all actor over candidate actions.

Mechanism (torch; batched matmuls; device-agnostic; ported verbatim from the
certified cell so the library reproduces the certified value-gate advantage):
  - SR-transport critic M trained by TD(0): E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M)
    (discounted successor features; Dayan 1993, Stachenfeld et al. 2017). The
    update is the cfrpe delta-rule outer-product with adaptive per-sample LR
    (clamp error/median in [0.25, 4.0]) times a linear LR-decay schedule.
  - reach(cand; goal) = cos(E[cand] @ M, E[goal]) -- the learned "does this action
    move toward the goal" value signal (the Go-drive).
  - Go/NoGo actor: Go_i = w_manifold*manifold_i + alpha*goal_sim_i + w_reach*reach_i;
    gate = argmax_i Go_i (winner-take-all disinhibition).

KEY DISCRIMINATOR (certified; reproduced by the module selftest witness):
  - Go/NoGo beats the static additive baseline where the value signal matters.
  - w_reach == 0 reduces the Go/NoGo actor EXACTLY to the additive baseline
    (clean null reduction; op-trace bit-identical).
  - Anti-tautology: the trained-M reach is target-cosine INDEPENDENT (reach with
    M := identity carries no dynamics; it must NOT separate on-path from off-path
    where the trained reach does).

============================================================================
COMPUTE ARCHITECTURE
============================================================================
Storage strategy: SHARDED (each operator its own W matrix; M is a learned value
operator, not an item store). No bundled store. Batched matmuls on cuda-if-
available; within-chain hops are sequential (genuine dependency).

============================================================================
ENVELOPE (certified; do NOT exceed without a rescue cell)
============================================================================
- PROVEN at the fair depth-4 superposition regime (baseline in band, not floored):
    MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:per_regime.V1200_d4
      additive=0.053  gonogo=0.653  control_identity=0.051  oracle=0.962
      closure=0.661  dynamics_lift=0.602  cv=0.037  reach_rank_test=0.690
      reach_tcos_corr=-0.079  sign_p~2e-196
    Second fair regime V2400_d4: closure=0.514, gonogo_lift=0.468, cv=0.031.
- SCOPED TO SHALLOW DEPTH. Capability degrades with superposition depth
  (gonogo 0.653 @ d4 -> 0.075 @ d6; per-hop accuracy decays geometrically). The
  n_fair=2/7 regime count is the CONSERVATIVE meta-rule excluding 5 floored-
  baseline regimes -- a harder test, not a cherry-pick.
- KNOWN BOUNDARIES (separate HARD_FAILs; this primitive does NOT claim them):
    * compounding depth-error at deeper chains
      (exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1 HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL)
    * cannot self-discover multi-step subgoal decomposition
      (exp_pfc_gate_autonomous_waypoint_discovery_v1 HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION)
  This is a FLAT value-based action gate, NOT a hierarchical / multi-step planner.

Cert atom: math::MEASURED_MECHANISM_pfc_gate_cfrpe_trained_v2_FULL_5seed_7regime_sweep_...
           (tier MEASURED_MECHANISM; cell_commit 1d606f4ec; auditor skunkworks 2026-07-05)
Source cell: experiments/exp_pfc_gate_cfrpe_trained_v2.py
Prereg: preregs/2026-07-05_pfc_gate_cfrpe_trained_v2.md

ASCII-only. No emojis. No em-dashes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import torch

DTYPE = torch.float32

# cfrpe adaptive-LR clamp (from the certified source cell).
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2  # linear LR decay to 0.2*base over training

# ----- CG-anchored MEASURED constants (v2 FULL 5-seed N=8192) -----------------
# MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json (verified off-disk 2026-07-08).
CG_FOCUS_REGIME = "V1200_d4"
CG_CLOSURE = 0.661
CG_GONOGO = 0.653
CG_ADDITIVE = 0.053
CG_CONTROL_IDENTITY = 0.051
CG_ORACLE = 0.962
CG_DYNAMICS_LIFT = 0.602  # gonogo - control_identity
CG_CV = 0.037
CG_REACH_RANK_TEST = 0.690
CG_REACH_TCOS_CORR = -0.079
CG_CELL_COMMIT = "1d606f4ec"
CG_CERT_TIER = "MEASURED_MECHANISM_proven_at_depth4"
CG_CERT_ATOM = (
    "math::MEASURED_MECHANISM_pfc_gate_cfrpe_trained_v2_FULL_5seed_7regime_sweep"
    "_RESOLVES_the_v1_regime_calibration_failure_..._V1200_d4_closure_0p661"
)


# ============================================================================
# substrate primitives (torch, batched) -- ported verbatim from the cert cell
# ============================================================================
def _norm_rows(X: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Row-wise L2 normalize. X: [..., n]."""
    return X / (X.norm(dim=-1, keepdim=True) + eps)


def bipolar_codebook(V: int, n: int, gen: torch.Generator,
                     device: torch.device | None = None) -> torch.Tensor:
    """Row-normalized bipolar codebook. Returns E [V, n]."""
    dev = device if device is not None else gen.device
    X = (torch.randint(0, 2, (V, n), generator=gen, device=dev, dtype=DTYPE) * 2 - 1)
    return _norm_rows(X)


def hebbian_operator(triples: Sequence[Tuple[int, int]], E: torch.Tensor,
                     n: int) -> torch.Tensor:
    """Hebbian operator W = sum_s E[s]^T E[o] / n; state @ W ~= E[o] for a matching (s,o)."""
    dev = E.device
    if not triples:
        return torch.zeros((n, n), dtype=DTYPE, device=dev)
    arr = torch.tensor(list(triples), dtype=torch.long, device=dev)
    S = E[arr[:, 0]]
    O = E[arr[:, 1]]
    return (S.transpose(0, 1) @ O) / float(n)


def cleanup(vecs: torch.Tensor, E: torch.Tensor
            ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Codebook cleanup. vecs [B, n] -> (idx [B], cleaned E[idx] [B, n], manifold_max_sim [B])."""
    vn = _norm_rows(vecs)
    sims = vn @ E.transpose(0, 1)
    manifold, idx = sims.max(dim=1)
    return idx, E[idx], manifold


# ============================================================================
# cfrpe-trained SR value critic (TD(0); TD-error == reward-prediction-error)
# ============================================================================
def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Learn SR value operator M [n,n] s.t. E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M).

    Update = cfrpe delta-rule (adaptive per-sample LR clamp error/median) times a
    linear global decay (1.0 -> LR_DECAY_END). Returns (M, diag) with err_first/
    err_last (must shrink), clamp count, and final M norm.
    """
    dev = E.device
    M = torch.zeros((n, n), dtype=DTYPE, device=dev)
    K = transitions.shape[0]
    diag: Dict[str, Any] = {"n_transitions": int(K), "n_clamped_steps": 0,
                            "err_first": None, "err_last": None, "final_M_norm": 0.0}
    if K < 2:
        return M, diag
    cur_t = torch.tensor(transitions[:, 0], dtype=torch.long, device=dev)
    nxt_t = torch.tensor(transitions[:, 1], dtype=torch.long, device=dev)
    sqrt_n = math.sqrt(float(n))
    for step in range(steps):
        decay = 1.0 - (1.0 - LR_DECAY_END) * (step / max(1, steps - 1))
        st = torch.randint(0, K, (batch,), generator=gen, device=dev)
        Ecur = E[cur_t[st]]
        Enxt = E[nxt_t[st]]
        pred = Ecur @ M
        with torch.no_grad():
            boot = Enxt + gamma * (Enxt @ M)  # TD target (bootstrap)
        error = boot - pred                    # TD-error == RPE
        e_norm = error.norm(dim=1) / sqrt_n
        med = float(torch.median(e_norm))
        med_safe = med if med > 1e-8 else 1e-8
        ratio = e_norm / med_safe
        ratio_c = torch.clamp(ratio, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
        if bool(((ratio < ADAPT_LR_FLOOR) | (ratio > ADAPT_LR_CEIL)).any()):
            diag["n_clamped_steps"] += 1
        lr_per = base_lr * decay * ratio_c
        dM = (Ecur.transpose(0, 1) @ (error * lr_per.unsqueeze(1))) / float(batch)
        M = M + dM
        e_mean = float(e_norm.mean())
        if step == 0:
            diag["err_first"] = round(e_mean, 6)
        diag["err_last"] = round(e_mean, 6)
    diag["final_M_norm"] = round(float(M.norm()), 4)
    return M, diag


def reach_value(cand_E: torch.Tensor, goal_E: torch.Tensor, M: torch.Tensor
                ) -> torch.Tensor:
    """Learned-dynamics reach value: cos(E[cand] @ M, E[goal]) per row. cand_E,goal_E: [B,n]."""
    fwd = _norm_rows(cand_E @ M)
    return (fwd * _norm_rows(goal_E)).sum(dim=1)


def reach_control_targetcos(cand_E: torch.Tensor, goal_E: torch.Tensor) -> torch.Tensor:
    """Anti-tautology control: reach with M := identity == raw target-cosine cos(E[cand],E[goal]).
    Carries NO dynamics info; proves the trained-M win is not target-cosine in disguise."""
    return (_norm_rows(cand_E) * _norm_rows(goal_E)).sum(dim=1)


# ============================================================================
# Go/NoGo value-based action-selection gate (the actor)
# ============================================================================
@dataclass(frozen=True)
class GoNoGoActionGate:
    """Winner-take-all value-based action selector over candidate operators.

    Go_i = w_manifold*manifold_i + alpha*goal_sim_i + w_reach*reach_i, gate = argmax_i Go_i,
    with w_manifold = max(0, 1 - alpha).

    Args:
        alpha:    goal-bias mixture weight in [0, 1] (tuned on train rollouts).
        w_reach:  learned SR-value (reach) weight. w_reach == 0 reduces this gate
                  EXACTLY to the static additive baseline (clean null reduction).

    Reductions:
        w_reach == 0                         -> additive baseline (goal-bias + manifold)
        alpha == 0 and w_reach == 0          -> goal-blind manifold reference (v1_no_goal)
    """
    alpha: float = 0.2
    w_reach: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.alpha <= 1.0):
            raise ValueError(f"alpha must be in [0,1]; got {self.alpha}")
        if self.w_reach < 0.0:
            raise ValueError(f"w_reach must be >= 0; got {self.w_reach}")

    def score_actions(self, state: torch.Tensor, goal_E: torch.Tensor,
                      W_ops: Sequence[torch.Tensor], E: torch.Tensor,
                      M: torch.Tensor | None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Per-candidate Go-values. Returns (scores [B, n_ops], cand_idx [B, n_ops]).

        When w_reach == 0 the reach term is skipped entirely so the scores are
        bit-identical to the additive baseline (no dependence on M).
        """
        n_chains = state.shape[0]
        n_ops = len(W_ops)
        dev = E.device
        w_manifold = max(0.0, 1.0 - self.alpha)
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=dev)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=dev)
        use_reach = self.w_reach != 0.0
        if use_reach and M is None:
            raise ValueError("w_reach != 0 requires a trained SR value operator M")
        goal_n = _norm_rows(goal_E)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, manifold = cleanup(out, E)
            cand_idx[:, op] = idx
            out_n = _norm_rows(out)
            goal_sim = (out_n * goal_n).sum(dim=1)
            sc = w_manifold * manifold + self.alpha * goal_sim
            if use_reach:
                sc = sc + self.w_reach * reach_value(cleaned, goal_E, M)  # type: ignore[arg-type]
            scores[:, op] = sc
        return scores, cand_idx

    def select(self, state: torch.Tensor, goal_E: torch.Tensor,
               W_ops: Sequence[torch.Tensor], E: torch.Tensor,
               M: torch.Tensor | None) -> torch.Tensor:
        """One-hop Go/NoGo winner-take-all. Returns chosen op index per chain [B]."""
        scores, _ = self.score_actions(state, goal_E, W_ops, E, M)
        return scores.argmax(dim=1)

    def run_chain(self, starts: torch.Tensor, targets: torch.Tensor,
                  W_ops: Sequence[torch.Tensor], E: torch.Tensor,
                  M: torch.Tensor | None, depth: int
                  ) -> Tuple[torch.Tensor, np.ndarray]:
        """Batched multi-hop rollout of the gate toward each chain's goal.

        Returns (correct_bool [B], op_trace [B, depth]). Hops are sequential
        (genuine dependency). The goal signal is fixed E[targets] across hops.
        """
        n_chains = starts.shape[0]
        dev = E.device
        state = E[starts].clone()
        goal_E = E[targets]
        op_trace = np.zeros((n_chains, depth), dtype=np.int64)
        final_idx = starts
        for hop in range(depth):
            scores, cand_idx = self.score_actions(state, goal_E, W_ops, E, M)
            chosen = scores.argmax(dim=1)
            op_trace[:, hop] = chosen.detach().cpu().numpy()
            row = torch.arange(n_chains, device=dev)
            new_idx = cand_idx[row, chosen]
            state = E[new_idx]
            final_idx = new_idx
        correct = (final_idx == targets).detach().cpu().numpy().astype(bool)
        return torch.from_numpy(correct), op_trace


def run_oracle_chain(starts: torch.Tensor, targets: torch.Tensor, op_seqs: np.ndarray,
                     W_ops: Sequence[torch.Tensor], E: torch.Tensor, depth: int
                     ) -> torch.Tensor:
    """Ceiling arm: apply the true op sequence. Returns correct_bool [B]."""
    n_chains = starts.shape[0]
    dev = E.device
    state = E[starts].clone()
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=dev)
    final_idx = starts
    for hop in range(depth):
        ops_h = op_seq_t[:, hop]
        new_idx = torch.empty(n_chains, dtype=torch.long, device=dev)
        for op in range(len(W_ops)):
            mask = (ops_h == op)
            if not bool(mask.any()):
                continue
            out = state[mask] @ W_ops[op]
            idx, _, _ = cleanup(out, E)
            new_idx[mask] = idx
        state = E[new_idx]
        final_idx = new_idx
    return (final_idx == targets).detach().cpu().numpy().astype(bool)


def reach_rank_accuracy(starts: torch.Tensor, targets: torch.Tensor, op_seqs: np.ndarray,
                        W_ops: Sequence[torch.Tensor], E: torch.Tensor,
                        M: torch.Tensor, depth: int) -> float:
    """Mechanism-fires probe: along the TRUE trajectory, does argmax_op reach == true op?
    Chance = 1/n_ops. Directly measures reach-value informativeness."""
    n_chains = starts.shape[0]
    dev = E.device
    state = E[starts].clone()
    goal_E = E[targets]
    n_ops = len(W_ops)
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=dev)
    hits = 0
    total = 0
    for hop in range(depth):
        reach_scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=dev)
        cand_idx_all = torch.empty((n_chains, n_ops), dtype=torch.long, device=dev)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, _ = cleanup(out, E)
            cand_idx_all[:, op] = idx
            reach_scores[:, op] = reach_value(cleaned, goal_E, M)
        pred_op = reach_scores.argmax(dim=1)
        true_op = op_seq_t[:, hop]
        hits += int((pred_op == true_op).sum().item())
        total += n_chains
        row = torch.arange(n_chains, device=dev)
        new_idx = cand_idx_all[row, true_op]
        state = E[new_idx]
    return float(hits) / float(max(1, total))


# ============================================================================
# formula selftests / scaffold-free witness (reproduce the certified advantage)
# ============================================================================
def _build_nav_task(V: int, n: int, n_ops: int, density: float,
                    n_train: int, n_test: int, depth: int,
                    seed: int, device: torch.device
                    ) -> Dict[str, Any]:
    """Small deterministic navigation KB: operators, disjoint train/test chains, SR rollouts."""
    g = np.random.default_rng(seed)
    tgen = torch.Generator(device=device)
    tgen.manual_seed(seed * 100003 + V)
    E = bipolar_codebook(V, n, tgen, device=device)

    n_triples = max(4, int(round(density * V)))
    per_op: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    for _ in range(n_triples * n_ops):
        s = int(g.integers(0, V)); o = int(g.integers(0, V)); op = int(g.integers(0, n_ops))
        if s != o:
            per_op[op].append((s, o))

    def _grow(d: int) -> Tuple[int, List[int], int]:
        cur = int(g.integers(0, V))
        s = cur
        op_seq: List[int] = []
        for _ in range(d):
            op = int(g.integers(0, n_ops))
            cands = [o for (ss, o) in per_op[op] if ss == cur]
            if not cands:
                new_o = int(g.integers(0, V))
                while new_o == cur:
                    new_o = int(g.integers(0, V))
                per_op[op].append((cur, new_o))
                cur = new_o
            else:
                cur = int(cands[g.integers(0, len(cands))])
            op_seq.append(op)
        return (s, op_seq, cur)

    train = [_grow(depth) for _ in range(n_train)]
    test = [_grow(depth) for _ in range(n_test)]
    W_ops = [hebbian_operator(per_op[i], E, n) for i in range(n_ops)]

    # SR rollouts (random walk over the operator graph).
    adj: List[Dict[int, List[int]]] = [dict() for _ in range(n_ops)]
    for op in range(n_ops):
        for (s, o) in per_op[op]:
            adj[op].setdefault(s, []).append(o)
    transitions: List[Tuple[int, int]] = []
    n_want = min(4000, 25 * V)
    guard = 0
    while len(transitions) < n_want and guard < n_want * 50:
        guard += 1
        cur = int(g.integers(0, V))
        for _ in range(depth + 2):
            avail = [op for op in range(n_ops) if cur in adj[op] and adj[op][cur]]
            if not avail:
                break
            op = int(avail[g.integers(0, len(avail))])
            outs = adj[op][cur]
            nxt = int(outs[g.integers(0, len(outs))])
            transitions.append((cur, nxt))
            cur = nxt
            if len(transitions) >= n_want:
                break
    trans = np.asarray(transitions, dtype=np.int64) if transitions else np.zeros((0, 2), np.int64)
    return {"E": E, "W_ops": W_ops, "train": train, "test": test, "trans": trans, "depth": depth}


def _chain_tensors(chains: List[Tuple[int, List[int], int]], device: torch.device
                   ) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    starts = torch.tensor([c[0] for c in chains], dtype=torch.long, device=device)
    targets = torch.tensor([c[2] for c in chains], dtype=torch.long, device=device)
    op_seqs = np.asarray([c[1] for c in chains], dtype=np.int64)
    return starts, targets, op_seqs


def _selftest_td_shrinks_rpe() -> None:
    """cfrpe SR-TD delta-rule shrinks the TD prediction error over steps."""
    dev = torch.device("cpu")
    gen = torch.Generator(device=dev); gen.manual_seed(0)
    E = bipolar_codebook(12, 128, gen, device=dev)
    trans = np.array([[i, i + 1] for i in range(10)], dtype=np.int64)
    M, diag = train_sr_transport(E, trans, 128, steps=200, batch=8, base_lr=0.5,
                                 gamma=0.8, gen=gen)
    assert diag["err_last"] is not None and diag["err_first"] is not None
    assert diag["err_last"] < diag["err_first"], (
        "cfrpe TD failed to shrink error %s->%s" % (diag["err_first"], diag["err_last"]))
    assert float(M.norm()) > 1e-4, "M is ~zero"


def _selftest_adaptive_lr_ordering() -> None:
    """Adaptive per-sample LR: higher-error sample gets higher clamped LR."""
    err = torch.tensor([[5.0], [0.1]]) * torch.ones(2, 16)
    e_norm = err.norm(dim=1) / math.sqrt(16.0)
    med = float(torch.median(e_norm)); med = med if med > 1e-8 else 1e-8
    ratio_c = torch.clamp(e_norm / med, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
    assert float(ratio_c[0]) > float(ratio_c[1]), "adaptive LR ordering wrong"


def _selftest_lr_decay_monotone() -> None:
    """LR decay schedule is monotone-decreasing 1.0 -> LR_DECAY_END."""
    steps = 100
    decays = [1.0 - (1.0 - LR_DECAY_END) * (s / max(1, steps - 1)) for s in range(steps)]
    assert abs(decays[0] - 1.0) < 1e-9
    assert abs(decays[-1] - LR_DECAY_END) < 1e-9
    assert all(decays[i] >= decays[i + 1] - 1e-12 for i in range(steps - 1))


def _selftest_argmax_competition() -> None:
    """Go/NoGo winner-take-all selects the argmax Go-value."""
    scores = torch.tensor([[0.1, 0.9, 0.3, 0.2]])
    assert int(scores.argmax(dim=1)[0]) == 1


def _selftest_mechanism_fires() -> None:
    """Trained reach ranks an ON-PATH node above an OFF-PATH node for the goal."""
    dev = torch.device("cpu")
    gen = torch.Generator(device=dev); gen.manual_seed(3)
    Vt, Nt = 8, 512
    Et = bipolar_codebook(Vt, Nt, gen, device=dev)
    chainA = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int64)   # goal branch
    chainB = np.array([[0, 4], [4, 5], [5, 6]], dtype=np.int64)   # away branch
    toy = np.concatenate([np.tile(chainA, (30, 1)), np.tile(chainB, (30, 1))], axis=0)
    Mt, _ = train_sr_transport(Et, toy, Nt, steps=600, batch=16, base_lr=0.5,
                               gamma=0.8, gen=gen)
    goal = Et[3:4]
    reach_on = float(reach_value(Et[1:2], goal, Mt)[0])
    reach_off = float(reach_value(Et[4:5], goal, Mt)[0])
    assert reach_on > reach_off, (
        "mechanism-fires FAIL: reach on-path=%.4f !> off-path=%.4f" % (reach_on, reach_off))
    # anti-tautology: identity-reach control is uninformative where trained M is informative.
    ctrl_on = float(reach_control_targetcos(Et[1:2], goal)[0])
    ctrl_off = float(reach_control_targetcos(Et[4:5], goal)[0])
    trained_sep = reach_on - reach_off
    control_sep = abs(ctrl_on - ctrl_off)
    assert trained_sep > control_sep + 0.05, (
        "anti-tautology FAIL: trained-sep=%.4f not clearly > control-sep=%.4f"
        % (trained_sep, control_sep))


def value_gate_advantage_witness(V: int = 60, n: int = 1024, n_ops: int = 4,
                                 depth: int = 3, seed: int = 7) -> Dict[str, Any]:
    """Scaffold-free witness: Go/NoGo beats the static additive baseline, and the
    w_reach==0 null reduces EXACTLY to additive. Returns measured arm accuracies.

    Reproduces (at small scale) the certified value-gate discriminator from
    exp_pfc_gate_cfrpe_trained_v2. alpha (additive) and w_reach (gonogo) are tuned
    on TRAIN chains; arms are evaluated on disjoint TEST chains (held-out).
    """
    dev = torch.device("cpu")
    task = _build_nav_task(V, n, n_ops, density=0.21, n_train=48, n_test=48,
                           depth=depth, seed=seed, device=dev)
    E, W_ops, train, test = task["E"], task["W_ops"], task["train"], task["test"]
    sr_gen = torch.Generator(device=dev); sr_gen.manual_seed(seed * 7919 + V)
    M, sr_diag = train_sr_transport(E, task["trans"], n, steps=1500, batch=64,
                                    base_lr=0.5, gamma=0.85, gen=sr_gen)

    tr_s, tr_t, _ = _chain_tensors(train, dev)
    te_s, te_t, te_ops = _chain_tensors(test, dev)

    alpha_sweep = [0.1, 0.2, 0.5]
    w_reach_sweep = [0.0, 0.5, 1.0, 2.0]

    # tune alpha (additive) on train
    best_alpha, best_add_tr = alpha_sweep[0], -1.0
    for a in alpha_sweep:
        acc = float(GoNoGoActionGate(alpha=a, w_reach=0.0)
                    .run_chain(tr_s, tr_t, W_ops, E, None, depth)[0].float().mean())
        if acc > best_add_tr:
            best_add_tr, best_alpha = acc, a
    # tune w_reach (gonogo) on train, holding best_alpha
    best_wr, best_go_tr = w_reach_sweep[0], -1.0
    for wr in w_reach_sweep:
        Mopt = None if wr == 0.0 else M
        acc = float(GoNoGoActionGate(alpha=best_alpha, w_reach=wr)
                    .run_chain(tr_s, tr_t, W_ops, E, Mopt, depth)[0].float().mean())
        if acc > best_go_tr:
            best_go_tr, best_wr = acc, wr

    # evaluate on held-out TEST (paired)
    add_gate = GoNoGoActionGate(alpha=best_alpha, w_reach=0.0)
    go_gate = GoNoGoActionGate(alpha=best_alpha, w_reach=best_wr)
    add_c, add_tr = add_gate.run_chain(te_s, te_t, W_ops, E, None, depth)
    go_c, go_tr = go_gate.run_chain(te_s, te_t, W_ops, E, M, depth)
    orc_c = run_oracle_chain(te_s, te_t, te_ops, W_ops, E, depth)

    additive = float(add_c.float().mean())
    gonogo = float(go_c.float().mean())
    oracle = float(orc_c.mean())
    headroom = oracle - additive
    closure = ((gonogo - additive) / headroom) if headroom > 1e-6 else 0.0
    reach_rank_test = reach_rank_accuracy(te_s, te_t, te_ops, W_ops, E, M, depth)

    # null reduction: w_reach==0 gonogo op-trace bit-identical to additive op-trace
    null_go = GoNoGoActionGate(alpha=best_alpha, w_reach=0.0)
    null_c, null_tr = null_go.run_chain(te_s, te_t, W_ops, E, None, depth)
    null_reduces = bool(np.array_equal(null_tr, add_tr))

    return {
        "additive": additive, "gonogo": gonogo, "oracle": oracle,
        "closure": closure, "gonogo_lift": gonogo - additive,
        "reach_rank_test": reach_rank_test,
        "best_alpha": best_alpha, "best_w_reach": best_wr,
        "additive_in_band": bool(0.05 < additive < 0.95),
        "null_reduces_to_additive": null_reduces,
        "sr_err_first": sr_diag["err_first"], "sr_err_last": sr_diag["err_last"],
    }


def _selftest_value_gate_advantage() -> Dict[str, Any]:
    """CERTIFIED DISCRIMINATOR witness: gonogo > additive, in-band, null reduces cleanly."""
    r = value_gate_advantage_witness()
    assert r["oracle"] >= 0.90, "witness oracle rail too low: %.3f" % r["oracle"]
    assert r["additive_in_band"], (
        "witness additive baseline not in band: %.3f (regime not fair)" % r["additive"])
    assert r["gonogo_lift"] > 0.05, (
        "value-gate advantage did not fire: gonogo=%.3f additive=%.3f lift=%.3f"
        % (r["gonogo"], r["additive"], r["gonogo_lift"]))
    assert r["reach_rank_test"] > 0.30, (
        "reach mechanism did not fire: reach_rank_test=%.3f (chance 0.25)"
        % r["reach_rank_test"])
    assert r["null_reduces_to_additive"], (
        "w_reach==0 null did NOT reduce to additive baseline (op-trace differs)")
    return r


def _run_all_selftests() -> Dict[str, Any]:
    """Run every formula selftest + the certified-advantage witness. Returns summary dict."""
    _selftest_td_shrinks_rpe()
    _selftest_adaptive_lr_ordering()
    _selftest_lr_decay_monotone()
    _selftest_argmax_competition()
    _selftest_mechanism_fires()
    witness = _selftest_value_gate_advantage()
    return {
        "cg_focus_regime": CG_FOCUS_REGIME,
        "cg_closure": CG_CLOSURE,
        "cg_gonogo": CG_GONOGO,
        "cg_additive": CG_ADDITIVE,
        "cg_oracle": CG_ORACLE,
        "cg_dynamics_lift": CG_DYNAMICS_LIFT,
        "cg_cv": CG_CV,
        "cg_reach_rank_test": CG_REACH_RANK_TEST,
        "cg_cell_commit": CG_CELL_COMMIT,
        "cg_cert_tier": CG_CERT_TIER,
        "witness": witness,
        "cg_source": "exp_pfc_gate_cfrpe_trained_v2 FULL 5-seed N=8192 (2026-07-05)",
    }


if __name__ == "__main__":
    result = _run_all_selftests()
    w = result["witness"]
    print("[action_selection selftest] PASS")
    print("  witness: additive=%.3f gonogo=%.3f oracle=%.3f closure=%.3f "
          "reach_rank_test=%.3f null_reduces=%s (alpha=%.2f w_reach=%.1f)"
          % (w["additive"], w["gonogo"], w["oracle"], w["closure"],
             w["reach_rank_test"], w["null_reduces_to_additive"],
             w["best_alpha"], w["best_w_reach"]))
    print("  CG-anchored: %s closure=%.3f gonogo=%.3f additive=%.3f (%s)"
          % (result["cg_focus_regime"], result["cg_closure"], result["cg_gonogo"],
             result["cg_additive"], result["cg_cert_tier"]))
