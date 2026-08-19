"""hdlab/successor_representation.py -- D7. THE ONE SLOT WHERE THE BRAIN HANDS US A CLOSED FORM.

    M = (I - gamma * P)^-1

WHY THIS ORGAN AND WHY NOW. `notes/COMPLETE_SUBSTRATE_DESIGN_2026-08-18.md` names D7 as the only
slot in the whole substrate where the brain's equation is FULLY PINNED and we had written none of
it. Phase 2 then measured the assembled substrate memorising almost perfectly (hit@1 0.9333 at
exact key) and transferring nothing to a new context (0.0044, tied with its own scramble, beaten
5x by a 1-step co-occurrence counter). The diagnosis that converges with ORGAN A is that the
missing ingredient is a LEARNING SIGNAL -- and the successor representation is one we can actually
have: self-supervised from the corpus's own transitions, derived from NO gold, NO WordNet and NO
LLM, so it is admissible where almost every other supervision candidate was circular.

WHAT IS PINNED AND WHAT IS OURS -- stated because presenting an invention as pinned is barred:
  PINNED   the COMPUTATION. Discounted expected future occupancy, M = sum_k (gamma^k P^k). The
           hippocampus is argued to encode exactly this (place fields as predictive maps; grid
           cells as its eigenvectors). We copy the operation.
  OURS     what a "state" is. The brain's SR runs over places an animal occupies; we run it over
           LEMMAS in a text stream. THAT SUBSTITUTION IS OUR INVENTION AND IT IS UNDER TEST.
  SWEEP    gamma. It is a PARAMETER derived from a constraint we do not share, so it is swept and
           never adopted as a value -- this project's worst result copied a pinned NUMBER (the
           0.2% MTL sparsity band, the worst point in its own sweep) and its best copied an
           OPERATION.

*** THE HONEST PREDICTION, PRE-REGISTERED BEFORE ANY NUMBER EXISTS, AND IT IS UNFLATTERING. ***
M is a DISCOUNTED MULTI-STEP CO-OCCURRENCE STATISTIC. Our floor is 1-step co-occurrence. So the
live possibility is that SR is simply a better counter, not a different kind of thing. Both
outcomes are informative and neither may be softened afterwards:
  (i)  SR beats the 1-step COOC floor CI-separated on held-out cues -> the missing thing included
       a PREDICTIVE HORIZON, and we now have a pinned mechanism that supplies it.
  (ii) SR ties or loses to the 1-step floor -> the horizon is NOT what was missing, and no amount
       of lookahead over word transitions produces generalisation. That closes a route with an
       equation rather than with an opinion, which is worth as much as (i).
  (iii) SR beats the floor ONLY at gamma ~ 0 -> it is the 1-step counter wearing a matrix, and
       must be reported as such.

USAGE
  python -m hdlab.successor_representation      # self-test, including the closed-form identity
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


def build_transition_matrix(sequences: Sequence[Sequence[str]],
                            vocab: Optional[Sequence[str]] = None,
                            *, window: int = 1,
                            ) -> Tuple[List[str], np.ndarray]:
    """Row-stochastic P over lemma states, estimated from observed transitions.

    `window` = 1 is the literal next-state transition. A wider window counts every successor
    within that many steps, which is still a TRANSITION estimate and not a co-occurrence bag --
    order is preserved and the matrix stays directed.
    """
    if vocab is None:
        seen = sorted({w for s in sequences for w in s})
    else:
        seen = sorted(set(vocab))
    idx = {w: i for i, w in enumerate(seen)}
    n = len(seen)
    C = np.zeros((n, n), dtype=np.float64)
    for seq in sequences:
        ids = [idx[w] for w in seq if w in idx]
        for t, a in enumerate(ids):
            for d in range(1, window + 1):
                if t + d < len(ids):
                    C[a, ids[t + d]] += 1.0
    row = C.sum(axis=1, keepdims=True)
    # A state never observed as a source gets a UNIFORM row rather than a zero row. A zero row
    # makes (I - gamma*P) closer to singular and silently turns "no data" into "absorbing state",
    # which is a modelling claim we did not make.
    dead = (row.squeeze(-1) == 0.0)
    P = np.where(row > 0, C / np.maximum(row, 1e-12), 0.0)
    if dead.any():
        P[dead, :] = 1.0 / max(n, 1)
    return seen, P


def successor_matrix(P: np.ndarray, gamma: float) -> np.ndarray:
    """M = (I - gamma*P)^-1. Closed form, solved rather than inverted where possible."""
    if not (0.0 <= gamma < 1.0):
        raise ValueError(f"gamma must be in [0, 1); got {gamma}")
    n = P.shape[0]
    A = np.eye(n) - gamma * P
    try:
        return np.linalg.solve(A, np.eye(n))
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A)


def successor_matrix_td(P_sequences: Sequence[Sequence[int]], n_states: int, gamma: float,
                        *, lr: float = 0.1, passes: int = 1,
                        seed: int = 0) -> np.ndarray:
    """The SAME quantity learned ONLINE by a TD error, which is the brain-plausible route.

    Kept beside the closed form on purpose: the closed form is the TARGET, the TD rule is the
    MECHANISM, and having both means a claim about the mechanism can be checked against the thing
    it is supposed to converge to instead of against a hope.
    """
    M = np.eye(n_states, dtype=np.float64)
    rng = np.random.default_rng(seed)
    order = list(range(len(P_sequences)))
    for _ in range(passes):
        rng.shuffle(order)
        for si in order:
            seq = P_sequences[si]
            for t in range(len(seq) - 1):
                s, s2 = seq[t], seq[t + 1]
                onehot = np.zeros(n_states)
                onehot[s] = 1.0
                td = onehot + gamma * M[s2] - M[s]
                M[s] += lr * td
    return M


class SparseSuccessorRepresentation:
    """D7 AT SCALE. The SAME quantity, never forming M, so vocabulary is not cubically capped.

    WHY THIS EXISTS. The dense form inverts a V x V matrix, which is O(V^3) and made the named
    re-test -- "rebuild SR on 10-50x the transitions" -- impossible: 2,114 states was already most
    of a 26-minute run, and 50,000 states would be ~1e14 flops. The first D7 result was filed
    UNTESTABLE-AT-THIS-SCALE (median ONE observed successor per word), so the ONLY way to convert
    that into a real verdict is to run it on far more text. A method that cannot reach the scale
    its own re-test requires is not a method.

    THE IDENTITY, and no approximation is hidden in it:
        M = (I - gamma*P)^-1 = SUM_k gamma^k P^k     (Neumann series, converges for gamma < 1)
    so `M[i, :] = e_i^T M` is K sparse matrix-vector products and never touches a dense matrix.
    The truncation error after K terms is bounded by gamma^(K+1) / (1 - gamma) in the row sum,
    which `n_terms_for` inverts to pick K from a tolerance rather than from a guess.

    AND IT IS ARGUABLY THE MORE FAITHFUL FORM: nothing in the brain inverts a matrix. Discounted
    future occupancy accumulates through repeated transitions, which is what this computes.
    """

    def __init__(self, states: Sequence[str], P_sparse, gamma: float = 0.9,
                 n_terms: Optional[int] = None, tol: float = 1e-3) -> None:
        self.states = list(states)
        self.index = {w: i for i, w in enumerate(self.states)}
        self.P = P_sparse.tocsr()
        self.Pt = self.P.T.tocsr()
        self.gamma = float(gamma)
        self.n_terms = int(n_terms) if n_terms is not None else self.n_terms_for(gamma, tol)

    @staticmethod
    def n_terms_for(gamma: float, tol: float = 1e-3) -> int:
        """Smallest K with gamma^(K+1)/(1-gamma) <= tol. Chosen from the bound, not by taste."""
        if gamma <= 0.0:
            return 1
        k = 1
        while (gamma ** (k + 1)) / (1.0 - gamma) > tol and k < 2000:
            k += 1
        return k

    @classmethod
    def from_sequences(cls, sequences: Sequence[Sequence[str]], *, gamma: float = 0.9,
                       window: int = 1, vocab: Optional[Sequence[str]] = None,
                       tol: float = 1e-3) -> "SparseSuccessorRepresentation":
        states, P = build_transition_matrix_sparse(sequences, vocab=vocab, window=window)
        return cls(states, P, gamma=gamma, tol=tol)

    def _series(self, v0: np.ndarray, mat) -> np.ndarray:
        """SUM_k gamma^k (mat^k) v0, accumulated by repeated matvec."""
        acc = v0.astype(np.float64).copy()
        cur = acc.copy()
        g = self.gamma
        for _ in range(self.n_terms):
            cur = g * (mat @ cur)
            acc += cur
        return acc

    def rank_from_cue(self, cue_words: Sequence[str], *, top_k: int = 5,
                      exclude: Sequence[str] = ()) -> List[str]:
        """Identical semantics to the dense class: both directions summed, cue words excludable."""
        ids = [self.index[w] for w in cue_words if w in self.index]
        if not ids:
            return []
        n = len(self.states)
        e = np.zeros(n, dtype=np.float64)
        e[ids] = 1.0
        # forward: rows of M for the cue -> e^T M  == series over P^T applied to e
        fwd = self._series(e, self.Pt)
        # backward: columns of M for the cue -> M e == series over P applied to e
        bwd = self._series(e, self.P)
        score = fwd + bwd
        for w in exclude:
            i = self.index.get(w)
            if i is not None:
                score[i] = -np.inf
        k = min(top_k, n)
        idx = np.argpartition(-score, k - 1)[:k] if k < n else np.arange(n)
        return [self.states[i] for i in idx[np.argsort(-score[idx])]]


def build_transition_matrix_sparse(sequences: Sequence[Sequence[str]],
                                   vocab: Optional[Sequence[str]] = None,
                                   *, window: int = 1):
    """Row-stochastic P as a scipy CSR matrix. Dead rows are LEFT EMPTY, deliberately.

    The dense builder fills a never-observed source with a UNIFORM row so the inverse stays well
    conditioned. At scale that is catastrophic and also dishonest: it would turn a vocabulary of
    50,000 unseen sources into 2.5e9 fabricated nonzeros. The Neumann series needs no
    conditioning, so an unobserved state simply contributes nothing -- which is what "no data"
    should mean.
    """
    from scipy import sparse

    seen = sorted({w for s in sequences for w in s}) if vocab is None else sorted(set(vocab))
    idx = {w: i for i, w in enumerate(seen)}
    n = len(seen)
    rows: List[int] = []
    cols: List[int] = []
    for seq in sequences:
        ids = [idx[w] for w in seq if w in idx]
        for t, a in enumerate(ids):
            for d in range(1, window + 1):
                if t + d < len(ids):
                    rows.append(a)
                    cols.append(ids[t + d])
    C = sparse.coo_matrix((np.ones(len(rows), dtype=np.float64), (rows, cols)),
                          shape=(n, n)).tocsr()
    rs = np.asarray(C.sum(axis=1)).ravel()
    inv = np.zeros_like(rs)
    nz = rs > 0
    inv[nz] = 1.0 / rs[nz]
    P = sparse.diags(inv) @ C
    return seen, P.tocsr()


class SuccessorRepresentation:
    """D7. Holds P and M, and scores candidates from a cue by discounted expected occupancy."""

    def __init__(self, states: Sequence[str], P: np.ndarray, gamma: float = 0.9) -> None:
        self.states = list(states)
        self.index = {w: i for i, w in enumerate(self.states)}
        self.P = P
        self.gamma = float(gamma)
        self.M = successor_matrix(P, self.gamma)

    @classmethod
    def from_sequences(cls, sequences: Sequence[Sequence[str]], *, gamma: float = 0.9,
                       window: int = 1, vocab: Optional[Sequence[str]] = None
                       ) -> "SuccessorRepresentation":
        states, P = build_transition_matrix(sequences, vocab=vocab, window=window)
        return cls(states, P, gamma=gamma)

    def rank_from_cue(self, cue_words: Sequence[str], *, top_k: int = 5,
                      exclude: Sequence[str] = ()) -> List[str]:
        """Rank candidates by total discounted occupancy reachable from the cue's words.

        Both directions are summed -- M[c, w] is "starting at the cue word, how much time do we
        expect to spend at w", and M[w, c] is the converse. A cloze target sits BEFORE and AFTER
        its neighbours, so using one direction only would be a modelling choice dressed as a
        detail.
        """
        ids = [self.index[w] for w in cue_words if w in self.index]
        if not ids:
            return []
        score = self.M[ids, :].sum(axis=0) + self.M[:, ids].sum(axis=1)
        drop = {self.index[w] for w in exclude if w in self.index}
        for d in drop:
            score[d] = -np.inf
        return [self.states[i] for i in np.argsort(-score)[:top_k]]


# ---------------------------------------------------------------------------------------------

def _selftest_closed_form_identity() -> dict:
    """M must satisfy its own defining recursion M = I + gamma*P*M. Mechanism PINS this answer,
    so it is asserted exactly rather than to a tolerance chosen to pass."""
    rng = np.random.default_rng(0)
    n = 40
    C = rng.random((n, n))
    P = C / C.sum(axis=1, keepdims=True)
    for gamma in (0.0, 0.5, 0.9, 0.99):
        M = successor_matrix(P, gamma)
        resid = np.abs(M - (np.eye(n) + gamma * P @ M)).max()
        assert resid < 1e-8, f"gamma={gamma} residual {resid:.3e}"
    return {"max_residual_ok": True, "gammas": [0.0, 0.5, 0.9, 0.99]}


def _selftest_gamma_zero_is_the_identity() -> dict:
    """gamma=0 must reduce M to I -- the degenerate case that proves the discount is doing the
    work. If a downstream arm only wins at gamma~0 it is a 1-step counter wearing a matrix."""
    rng = np.random.default_rng(1)
    C = rng.random((15, 15))
    P = C / C.sum(axis=1, keepdims=True)
    M = successor_matrix(P, 0.0)
    assert np.allclose(M, np.eye(15)), "gamma=0 did not reduce to the identity"
    return {"gamma0_is_identity": True}


def _selftest_td_converges_to_the_closed_form() -> dict:
    """The ONLINE rule must approach the CLOSED FORM it is supposed to compute. This is a
    can-fail check with a known answer, not a plausibility check."""
    rng = np.random.default_rng(2)
    n = 6
    C = rng.random((n, n))
    P = C / C.sum(axis=1, keepdims=True)
    seqs = []
    for _ in range(400):
        s = int(rng.integers(n))
        seq = [s]
        for _ in range(30):
            s = int(rng.choice(n, p=P[s]))
            seq.append(s)
        seqs.append(seq)
    gamma = 0.8
    M_closed = successor_matrix(P, gamma)
    M_td = successor_matrix_td(seqs, n, gamma, lr=0.05, passes=6, seed=3)
    err = float(np.abs(M_td - M_closed).mean())
    scale = float(np.abs(M_closed).mean())
    assert err / scale < 0.25, f"TD did not approach the closed form: rel err {err / scale:.3f}"
    return {"mean_abs_err": round(err, 4), "closed_form_scale": round(scale, 4),
            "relative": round(err / scale, 4)}


def _selftest_planted_structure_is_recovered() -> dict:
    """A PLANTED POSITIVE. In a corpus where 'alpha' is reliably followed two steps later by
    'omega', SR must rank omega above a frequency-matched distractor that never follows it. If
    this fails the organ cannot detect structure it was handed, and nothing downstream is worth
    running."""
    rng = np.random.default_rng(4)
    filler = [f"f{i}" for i in range(12)]
    seqs = []
    for _ in range(300):
        mid = filler[int(rng.integers(len(filler)))]
        seqs.append(["alpha", mid, "omega"])
        # the distractor appears exactly as often, but NEVER after alpha
        seqs.append([filler[int(rng.integers(len(filler)))], "decoy", "omega"])
    sr = SuccessorRepresentation.from_sequences(seqs, gamma=0.9, window=1)
    ranked = sr.rank_from_cue(["alpha"], top_k=4, exclude=["alpha"])
    assert "omega" in ranked, f"planted successor not recovered: {ranked}"
    assert ranked.index("omega") < ranked.index("decoy") if "decoy" in ranked else True, (
        f"decoy outranked the planted successor: {ranked}")
    return {"ranked": ranked}


def _selftest_dead_rows_do_not_break_the_solve() -> dict:
    """A state never seen as a source must not produce a singular matrix or a silent absorbing
    state. Real corpora have these in quantity."""
    seqs = [["a", "b"], ["b", "c"]]
    states, P = build_transition_matrix(seqs, vocab=["a", "b", "c", "z_never_a_source"])
    assert np.allclose(P.sum(axis=1), 1.0), "rows are not stochastic"
    M = successor_matrix(P, 0.9)
    assert np.isfinite(M).all(), "non-finite entries in M"
    return {"n_states": len(states), "rows_stochastic": True}


def _selftest_sparse_matches_the_closed_form() -> dict:
    """THE SCALABLE PATH MUST AGREE WITH THE EXACT ONE. If the Neumann series and the inverse
    disagree, the scale re-test would be measuring a different quantity and its verdict would be
    about my truncation rather than about the successor representation."""
    rng = np.random.default_rng(11)
    words = [f"w{i}" for i in range(60)]
    seqs = []
    for _ in range(500):
        L = int(rng.integers(3, 9))
        seqs.append([words[int(rng.integers(len(words)))] for _ in range(L)])
    worst = 0.0
    for gamma in (0.1, 0.5, 0.9):
        dense = SuccessorRepresentation.from_sequences(seqs, gamma=gamma, vocab=words)
        sp = SparseSuccessorRepresentation.from_sequences(seqs, gamma=gamma, vocab=words,
                                                          tol=1e-6)
        # Compare RANKINGS, which is what the experiment consumes, on many cues.
        agree = 0
        trials = 40
        for _ in range(trials):
            cue = [words[int(rng.integers(len(words)))] for _ in range(3)]
            a = dense.rank_from_cue(cue, top_k=5, exclude=cue)
            b = sp.rank_from_cue(cue, top_k=5, exclude=cue)
            agree += int(a[:1] == b[:1])
        frac = agree / trials
        worst = max(worst, 1.0 - frac)
        assert frac >= 0.95, f"gamma={gamma}: top-1 agreement only {frac:.2f}"
    return {"worst_top1_disagreement": round(worst, 4)}


def _selftest_sparse_leaves_dead_rows_empty() -> dict:
    """The sparse builder must NOT fabricate uniform rows. At 50k states that would invent 2.5e9
    nonzeros and quietly turn 'no data' into 'transitions to everything'."""
    from scipy import sparse
    states, P = build_transition_matrix_sparse([["a", "b"], ["b", "c"]],
                                               vocab=["a", "b", "c", "z_never_a_source"])
    assert sparse.issparse(P)
    z = states.index("z_never_a_source")
    assert P[z].nnz == 0, "a never-observed source was given fabricated transitions"
    rs = np.asarray(P.sum(axis=1)).ravel()
    assert abs(rs[states.index("a")] - 1.0) < 1e-12, "observed rows must be stochastic"
    return {"n_states": len(states), "dead_row_nnz": 0}


def run_all_selftests() -> dict:
    tests = [
        ("closed_form_identity", _selftest_closed_form_identity),
        ("sparse_leaves_dead_rows_empty", _selftest_sparse_leaves_dead_rows_empty),
        ("sparse_matches_the_closed_form", _selftest_sparse_matches_the_closed_form),
        ("gamma_zero_is_the_identity", _selftest_gamma_zero_is_the_identity),
        ("dead_rows_do_not_break_the_solve", _selftest_dead_rows_do_not_break_the_solve),
        ("planted_structure_is_recovered", _selftest_planted_structure_is_recovered),
        ("td_converges_to_the_closed_form", _selftest_td_converges_to_the_closed_form),
    ]
    out: Dict[str, object] = {}
    failed = []
    for name, fn in tests:
        try:
            r = fn()
            r["_ok"] = True
            out[name] = r
        except AssertionError as e:
            out[name] = {"_ok": False, "error": str(e)[:300]}
            failed.append(name)
        except Exception as e:
            out[name] = {"_ok": False, "error": f"{type(e).__name__}: {str(e)[:300]}"}
            failed.append(name)
    out["_failed"] = failed
    out["_overall"] = "PASS" if not failed else "FAIL"
    return out


if __name__ == "__main__":
    r = run_all_selftests()
    print(json.dumps(r, indent=2, default=str))
    print("ALL SELF-TESTS PASSED" if r["_overall"] == "PASS" else f"FAILURES: {r['_failed']}")
    sys.exit(0 if r["_overall"] == "PASS" else 1)
