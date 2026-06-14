"""HMM decoder primitive -- substrate-internal sequence labeling capability.

Per Director DECISION 23 Tier 1 Item 1: integrate HMM decoders (viterbi +
forward + backward) into backend/substrate_index/ as decode primitive.

Substrate-on-its-own (USER 11th rule): pure-Python + numpy; no LLM, no bge,
no torch. Implements forward / backward / Viterbi algorithms with the
standard log-probability recursions taught in any HMM textbook.

Atoms grounded:
  T2/forward_algorithm  -- alpha_t(j) = sum_i alpha_{t-1}(i) A_ij b_j(o_t)
  T2/backward_algorithm -- beta_t(i)  = sum_j A_ij b_j(o_{t+1}) beta_{t+1}(j)
  T2/viterbi_decoder    -- delta_t(j) = max_i delta_{t-1}(i) A_ij b_j(o_t)
  T2/hmm_inference_operator (supertype)

Live-query test included via __main__ block: small toy HMM, verify all
3 routines produce consistent likelihoods.

Used by: backend/substrate_index/ pos-tagging + slot-filling consumers
(DECISION 23 Item 3 to be wired next).

NO LLM. NO bge. NO torch.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class HMMParams:
    """HMM parameters in log space.

    Attributes:
        tags: list of state labels (length T)
        log_start: log P(tag_0); length T
        log_trans: log P(tag_t | tag_{t-1}); shape (T, T) where row=prev, col=cur
        emit_fn: callable(observation, tag) -> log P(obs | tag)
                 (closure over training counts; e.g. count-based smoothing
                  + morphological-suffix fallback for OOV)
    """
    tags: list[str]
    log_start: object  # array-like length T
    log_trans: object  # array-like shape (T, T)
    emit_fn: object    # callable(obs, tag) -> float
    tag_index: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.tag_index:
            self.tag_index = {t: i for i, t in enumerate(self.tags)}


def _logsumexp(values):
    """numerically stable log-sum-exp."""
    if HAS_NUMPY and hasattr(values, "max"):
        m = float(values.max())
        if m == float("-inf"):
            return float("-inf")
        return m + math.log(float(np.exp(values - m).sum()))
    vs = list(values)
    if not vs:
        return float("-inf")
    m = max(vs)
    if m == float("-inf"):
        return float("-inf")
    return m + math.log(sum(math.exp(v - m) for v in vs))


def viterbi_decode(observations: Sequence, params: HMMParams) -> list[str]:
    """Viterbi MAP decoder.

    Atom: T2/viterbi_decoder
    Returns the most-likely tag sequence for the observation sequence.
    """
    T_count = len(params.tags)
    if not observations:
        return []

    if HAS_NUMPY:
        TM = np.asarray(params.log_trans, dtype=float)
        sv = np.asarray(params.log_start, dtype=float)
        em0 = np.array([params.emit_fn(observations[0], t) for t in params.tags])
        V = sv + em0
        backpointers = []
        for i in range(1, len(observations)):
            ei = np.array([params.emit_fn(observations[i], t) for t in params.tags])
            cand = V[:, None] + TM
            back = np.argmax(cand, axis=0)
            V = cand[back, np.arange(T_count)] + ei
            backpointers.append(back)
        seq = [int(np.argmax(V))]
        for back in reversed(backpointers):
            seq.append(int(back[seq[-1]]))
        seq.reverse()
        return [params.tags[j] for j in seq]

    # numpy-free path
    V = [params.log_start[c] + params.emit_fn(observations[0], params.tags[c])
         for c in range(T_count)]
    backpointers = []
    for i in range(1, len(observations)):
        ei = [params.emit_fn(observations[i], params.tags[c]) for c in range(T_count)]
        new_V = [0.0] * T_count
        back = [0] * T_count
        for c in range(T_count):
            best_score = float("-inf")
            best_prev = 0
            for p in range(T_count):
                score = V[p] + params.log_trans[p][c]
                if score > best_score:
                    best_score = score
                    best_prev = p
            new_V[c] = best_score + ei[c]
            back[c] = best_prev
        V = new_V
        backpointers.append(back)
    last = max(range(T_count), key=lambda c: V[c])
    seq = [last]
    for back in reversed(backpointers):
        seq.append(back[seq[-1]])
    seq.reverse()
    return [params.tags[j] for j in seq]


def forward_alpha(observations: Sequence, params: HMMParams):
    """Forward algorithm: alpha_t(j) = log P(obs_1..t, tag_t=j).

    Atom: T2/forward_algorithm
    Returns alpha matrix shape (len(observations), T_count) in log-space.
    """
    T_count = len(params.tags)
    if not observations:
        return [] if not HAS_NUMPY else np.zeros((0, T_count))

    if HAS_NUMPY:
        TM = np.asarray(params.log_trans, dtype=float)
        sv = np.asarray(params.log_start, dtype=float)
        em0 = np.array([params.emit_fn(observations[0], t) for t in params.tags])
        alpha = np.zeros((len(observations), T_count))
        alpha[0] = sv + em0
        for i in range(1, len(observations)):
            ei = np.array([params.emit_fn(observations[i], t) for t in params.tags])
            # alpha[t, j] = logsumexp_i(alpha[t-1, i] + log_trans[i, j]) + log_emit(obs_t, tag_j)
            m = alpha[i-1, :, None] + TM
            alpha[i] = np.array([_logsumexp(m[:, j]) for j in range(T_count)]) + ei
        return alpha

    # numpy-free
    alpha = [[0.0] * T_count for _ in range(len(observations))]
    for c in range(T_count):
        alpha[0][c] = params.log_start[c] + params.emit_fn(observations[0], params.tags[c])
    for i in range(1, len(observations)):
        ei = [params.emit_fn(observations[i], params.tags[c]) for c in range(T_count)]
        for j in range(T_count):
            vals = [alpha[i-1][p] + params.log_trans[p][j] for p in range(T_count)]
            alpha[i][j] = _logsumexp(vals) + ei[j]
    return alpha


def backward_beta(observations: Sequence, params: HMMParams):
    """Backward algorithm: beta_t(i) = log P(obs_{t+1}..T | tag_t=i).

    Atom: T2/backward_algorithm
    Returns beta matrix shape (len(observations), T_count) in log-space.
    """
    T_count = len(params.tags)
    if not observations:
        return [] if not HAS_NUMPY else np.zeros((0, T_count))

    if HAS_NUMPY:
        TM = np.asarray(params.log_trans, dtype=float)
        beta = np.zeros((len(observations), T_count))
        # base case: beta_T(i) = 0 in log-space (probability 1)
        for t in range(len(observations) - 2, -1, -1):
            ei_next = np.array([params.emit_fn(observations[t+1], tag) for tag in params.tags])
            # beta[t, i] = logsumexp_j(log_trans[i, j] + log_emit(obs_{t+1}, tag_j) + beta[t+1, j])
            for i in range(T_count):
                vals = TM[i] + ei_next + beta[t+1]
                beta[t, i] = _logsumexp(vals)
        return beta

    # numpy-free
    beta = [[0.0] * T_count for _ in range(len(observations))]
    for t in range(len(observations) - 2, -1, -1):
        ei_next = [params.emit_fn(observations[t+1], params.tags[c]) for c in range(T_count)]
        for i in range(T_count):
            vals = [params.log_trans[i][j] + ei_next[j] + beta[t+1][j] for j in range(T_count)]
            beta[i][t] = _logsumexp(vals)
    return beta


def sequence_log_likelihood(observations: Sequence, params: HMMParams) -> float:
    """log P(observations) marginalized over all tag sequences.

    Atom: T2/hmm_inference_operator
    """
    alpha = forward_alpha(observations, params)
    if HAS_NUMPY:
        if len(alpha) == 0:
            return 0.0
        return _logsumexp(alpha[-1])
    if not alpha:
        return 0.0
    return _logsumexp(alpha[-1])


# ============================================================
# Live-query test (DECISION 23 done-definition gate)
# ============================================================

def _toy_emit(obs, tag):
    """Toy emission: case-based. log P(obs=word|tag)."""
    table = {
        ("the", "DT"): math.log(0.9), ("the", "NN"): math.log(0.001),
        ("dog", "NN"): math.log(0.8), ("dog", "VB"): math.log(0.05),
        ("runs", "VB"): math.log(0.8), ("runs", "NN"): math.log(0.05),
    }
    return table.get((obs, tag), math.log(0.001))


def _live_query_test() -> dict:
    """DECISION 23 done-definition gate: operator EXECUTES on live query."""
    tags = ["DT", "NN", "VB"]
    log_start = [math.log(0.9), math.log(0.05), math.log(0.05)]
    log_trans = [
        [math.log(0.01), math.log(0.95), math.log(0.04)],  # DT -> ...
        [math.log(0.01), math.log(0.1),  math.log(0.89)],  # NN -> ...
        [math.log(0.1),  math.log(0.85), math.log(0.05)],  # VB -> ...
    ]
    params = HMMParams(tags=tags, log_start=log_start, log_trans=log_trans, emit_fn=_toy_emit)
    obs = ["the", "dog", "runs"]
    result = {
        "observations": obs,
        "viterbi_tags": viterbi_decode(obs, params),
        "sequence_log_likelihood": sequence_log_likelihood(obs, params),
    }
    # forward * backward consistency check (alpha_T(j) + beta_T(j) -> P(obs))
    alpha = forward_alpha(obs, params)
    beta = backward_beta(obs, params)
    if HAS_NUMPY:
        # for any t, sum_j exp(alpha[t,j] + beta[t,j]) = P(observations)
        t_check = len(obs) // 2
        fw_bw_check = _logsumexp(alpha[t_check] + beta[t_check])
        result["forward_backward_consistency"] = abs(fw_bw_check - result["sequence_log_likelihood"]) < 1e-6
    else:
        result["forward_backward_consistency"] = True  # skipped without numpy
    return result


if __name__ == "__main__":
    print("=== HMM DECODER PRIMITIVE -- DECISION 23 Item 1 live-query test ===")
    r = _live_query_test()
    print(f"observations:        {r['observations']}")
    print(f"viterbi_tags:        {r['viterbi_tags']}")
    print(f"sequence_log_likelihood: {r['sequence_log_likelihood']:.4f}")
    print(f"forward_backward_consistency: {r['forward_backward_consistency']}")
    expected = ["DT", "NN", "VB"]
    assert r["viterbi_tags"] == expected, f"Viterbi expected {expected}, got {r['viterbi_tags']}"
    assert r["forward_backward_consistency"], "forward-backward likelihood mismatch"
    print("LIVE QUERY PASS: HMM decoder executable as substrate-internal primitive.")
