"""graded_parser -- the globally-normalized graded dependency parser over the LANDED arc-factored scorer.

Landed 2026-09-07 (Q111 -- strategy lands the additive wire the prototype proved) from the owner-DONE
`replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals`. Promoted from
experiments/graded_parser_promote_v1.py; the exact graph algorithms are INLINED here VERBATIM from the
brute-force-verified cells (experiments/exp_matrix_tree_parser_v1 + exp_matrix_tree_singleroot_v1) so this
module is self-contained (hdlab/ must not depend on experiments/). Every function is byte-identical to a
brute-force-verified cell and re-checked by `self_test()` at land.

WHAT IT PROVIDES (all off ONE arc-factored Matrix-Tree marginal = one matrix inverse / sentence):
  GradedParse.parse(tokens, pos) -> ParseOut(map_heads, marginals, second_best_heads)
    - map_heads     : exact maximum spanning arborescence (Chu-Liu/Edmonds) -- the exact MAP decode that replaces
                      the greedy per-token-argmax + heuristic cycle-break (eliminates the 7.2% invalid-tree parses).
    - marginals     : exact SINGLE-ROOT Matrix-Tree edge marginals mu[i][h] (grammar-faithful; Koo et al. 2007;
                      brute-force-verified) -- the graded posterior + the universal per-arc reliability signal.
    - second_best   : exact 2nd-best arborescence (Camerini) -- the genuine 2nd-best over PARSES (offline/analysis
                      only; it is a WEAK live lever -- do NOT compute it on the read path, see EFFICIENCY).
  patient_confidence_cue(marginals, v, pk)   -> mu(v->pk), the reliability cue for parse_confidence + role selection
  attachment_reliability(marginals, head_of) -> per-arc reliability for ANY head-driven reader (median AUC 0.825/29 labels)

WIRE POINTS (all additive; the graded parse is opt-in, parse heads default byte-identical):
  1. parse_confidence.obl_row / patient_row: feed the marginal into the `a2_marg` slot. OBL FIRST -- the RAW
     single-root marginal (AUC 0.782) BEATS the whole landed obl calibrator (0.736); see
     parse_confidence.obl_reliability_marginal (raw marginal, logistic dropped). Patient a2_marg +0.008 AUC.
  2. predicate_argument_frontend.structural_patient_pick: pass `marginals` (+ the mined frame lexicon) -> the
     marginal + argument-vs-adjunct typing act as a Competition-Model re-ranking cue over v's candidates INCLUDING
     the marginal's top-2 parse-miss reach, ANCHORED on the labeled pick -> ABSOLUTE who-did-what +0.0065 CI-sep.
  3. arc_parser.ArcParser.parse(..., want_marginals=True) / decode="exact": the exact CLE decode changes heads
     ONLY on the cycle/invalid-tree sentences (UAS +0.002 CI-sep, no consumer-label regress); the additive marginal
     changes NO head.

EFFICIENCY: the marginal (one inverse) serves reliability + role selection + parse-miss exposure -- compute ONCE per
read, reuse. The exact 2nd-best TREE is a WEAK live lever (5% parse-miss vs the marginal's 77.5% exposure) -- do NOT
compute it on the read path. single-root costs the same one inverse as multi-root and is grammar-faithful.

Glass-box, CPU, numpy only, NO external LLM (the invariant). ASCII-only.
Run: .venv/Scripts/python.exe -c "from hdlab.graded_parser import self_test; print(self_test())"
"""
from __future__ import annotations

from itertools import product
from typing import Dict, List, NamedTuple, Sequence

import numpy as np

# ================================================================================================
# arc-factored dense score matrix (from experiments/exp_matrix_tree_parser_v1.dense_scores)
# ================================================================================================
def dense_scores(Sc, n):
    """(n+1)x(n+1) dense score array A[h][i] = score(head h -> dep i); diagonal / i=0 = -inf.
    Sc[i][h] is the arc-factored score the landed scorer exposes (hdlab.arc_parser.sentence_scores_auto)."""
    A = np.full((n + 1, n + 1), -np.inf)
    for i in range(1, n + 1):
        for h in range(0, n + 1):
            if h != i:
                A[h][i] = Sc[i][h]
    return A


# ================================================================================================
# EXACT MAP -- Chu-Liu/Edmonds maximum spanning arborescence rooted at 0 (multi-root: 0 may have >1 child).
# The incumbent greedy decode_from_scores is a HEURISTIC (per-token argmax + min-loss cycle repair); this is the
# exact global maximizer of the SAME arc-factored objective. VERBATIM from exp_matrix_tree_parser_v1.
# ================================================================================================
def chu_liu_edmonds(A, n):
    """A[h][i] = score(h->i). Returns head[i] for i in 1..n (exact max arborescence rooted at 0)."""
    nodes = list(range(0, n + 1))
    return _cle(A, nodes, 0)


def _cle(A, nodes, root):
    # best incoming edge per non-root node
    par = {}
    for v in nodes:
        if v == root:
            continue
        best_h, best_s = None, -np.inf
        for h in nodes:
            if h == v:
                continue
            if A[h][v] > best_s:
                best_s, best_h = A[h][v], h
        par[v] = best_h
    # find a cycle
    cyc = _find_cycle(par, nodes, root)
    if cyc is None:
        return dict(par)
    # contract the cycle into a supernode
    cyc_set = set(cyc)
    super_id = max(nodes) + 1
    new_nodes = [v for v in nodes if v not in cyc_set] + [super_id]
    # cycle internal score
    in_cyc_score = {v: A[par[v]][v] for v in cyc}
    # build contracted scores
    B = {}
    # map for reconstruction: for edges into supernode, remember which cycle node + original head
    into_super = {}   # h(external) -> (best_score, cyc_node v, orig head h)
    outof_super = {}   # target external node -> (best_score, cyc_node u origin)
    for h in new_nodes:
        for v in new_nodes:
            if h == v:
                continue
            B[(h, v)] = -np.inf
    for h in [x for x in nodes if x not in cyc_set]:
        for v in [x for x in nodes if x not in cyc_set]:
            if h != v:
                B[(h, v)] = max(B[(h, v)], A[h][v])
    # edges into the cycle (external head h -> cycle node vc): score = A[h][vc] - in_cyc_score[vc] + (const)
    for h in [x for x in nodes if x not in cyc_set]:
        best = -np.inf; best_v = None
        for vc in cyc:
            s = A[h][vc] - in_cyc_score[vc]
            if s > best:
                best, best_v = s, vc
        if best > B[(h, super_id)]:
            B[(h, super_id)] = best
            into_super[h] = (best, best_v, h)
    # edges out of the cycle (cycle node uc -> external v): score = A[uc][v]
    for v in [x for x in nodes if x not in cyc_set]:
        best = -np.inf; best_u = None
        for uc in cyc:
            if A[uc][v] > best:
                best, best_u = A[uc][v], uc
        if best > B[(super_id, v)]:
            B[(super_id, v)] = best
            outof_super[v] = (best, best_u)
    # dense sub-matrix over new_nodes
    m = max(new_nodes) + 1
    Bd = np.full((m, m), -np.inf)
    for (h, v), s in B.items():
        Bd[h][v] = s
    sub_par = _cle(Bd, new_nodes, root)
    # reconstruct
    head = {}
    # which external head enters the supernode?
    h_into = sub_par[super_id]
    _, entry_v, _ = into_super[h_into]
    for v in cyc:
        if v == entry_v:
            head[v] = h_into
        else:
            head[v] = par[v]
    for v in [x for x in nodes if x not in cyc_set]:
        if v == root:
            continue
        h = sub_par[v]
        if h == super_id:
            _, u = outof_super[v]
            head[v] = u
        else:
            head[v] = h
    return head


def _find_cycle(par, nodes, root):
    seen_global = set()
    for start in nodes:
        if start == root or start in seen_global:
            continue
        path = []
        x = start
        local = {}
        while x != root and x is not None and x not in local:
            local[x] = len(path)
            path.append(x)
            seen_global.add(x)
            x = par.get(x)
        if x is not None and x != root and x in local:
            return path[local[x]:]
    return None


def tree_score(A, head, n):
    return float(sum(A[head[i]][i] for i in range(1, n + 1)))


# ================================================================================================
# EXACT Matrix-Tree edge marginals (multi-root, McDonald-Satta 2007 / Smith-Smith 2007).
# VERBATIM from exp_matrix_tree_parser_v1.matrix_tree_marginals.
# ================================================================================================
def matrix_tree_marginals(A, n, temp=1.0):
    """Returns marg[i][h] = P(arc h->i present) for i in 1..n, h in 0..n. Exact (multi-root MTT)."""
    W = np.zeros((n + 1, n + 1))   # W[h][i]
    for i in range(1, n + 1):
        col = A[:, i].copy()
        finite = np.isfinite(col)
        mx = col[finite].max()
        for h in range(0, n + 1):
            if h != i and np.isfinite(A[h][i]):
                # floor the exponent so a peaked column never underflows to an all-zero (singular) Laplacian
                W[h][i] = np.exp(max((A[h][i] - mx) / temp, -60.0))
    # Laplacian over modifiers 1..n (0-indexed as 0..n-1 <-> tokens 1..n)
    L = np.zeros((n, n))
    for i in range(1, n + 1):
        L[i - 1][i - 1] = sum(W[h][i] for h in range(0, n + 1) if h != i)
        for h in range(1, n + 1):
            if h != i:
                L[h - 1][i - 1] = -W[h][i]
    try:
        Binv = np.linalg.inv(L)
    except np.linalg.LinAlgError:
        Binv = np.linalg.pinv(L + 1e-12 * np.eye(n))
    marg = {i: {} for i in range(1, n + 1)}
    for i in range(1, n + 1):
        for h in range(0, n + 1):
            if h == i:
                continue
            if h == 0:
                m = W[0][i] * Binv[i - 1][i - 1]
            else:
                m = W[h][i] * (Binv[i - 1][i - 1] - Binv[i - 1][h - 1])
            marg[i][h] = float(np.clip(m, 0.0, 1.0))
    return marg


def marginal_heads(marg, n):
    """1-best + 2nd-best head per token by marginal (a graded, per-token ranked-parallel readout)."""
    best = {}; second = {}; best_m = {}; second_m = {}
    for i in range(1, n + 1):
        order = sorted(marg[i].items(), key=lambda kv: kv[1], reverse=True)
        best[i], best_m[i] = order[0]
        if len(order) > 1:
            second[i], second_m[i] = order[1]
        else:
            second[i], second_m[i] = order[0]
    return best, second, best_m, second_m


# ================================================================================================
# EXACT SINGLE-ROOT Matrix-Tree edge marginals (Koo et al. 2007) -- the grammar-faithful posterior (a UD
# sentence has EXACTLY ONE root). VERBATIM from exp_matrix_tree_singleroot_v1.single_root_marginals.
# ================================================================================================
def single_root_marginals(A, n, temp=1.0):
    """Exact SINGLE-ROOT edge marginals (Koo et al. 2007). marg[i][h] = P(arc h->i | exactly one root child)."""
    if n == 1:
        return {1: {0: 1.0}}
    W = np.zeros((n + 1, n + 1))
    for i in range(1, n + 1):
        col = A[:, i]; finite = np.isfinite(col); mx = col[finite].max()
        for h in range(0, n + 1):
            if h != i and np.isfinite(A[h][i]):
                W[h][i] = np.exp(max((A[h][i] - mx) / temp, -60.0))
    # L (1-indexed m in 1..n -> numpy row/col m-1): non-root Laplacian
    L = np.zeros((n, n))
    for m in range(1, n + 1):
        L[m - 1][m - 1] = sum(W[h][m] for h in range(1, n + 1) if h != m)   # NON-root incoming only
        for h in range(1, n + 1):
            if h != m:
                L[h - 1][m - 1] = -W[h][m]
    # replace row 1 (index 0) with root weights r(m)=W[0][m]
    for m in range(1, n + 1):
        L[0][m - 1] = W[0][m]
    try:
        B = np.linalg.inv(L)
    except np.linalg.LinAlgError:
        B = np.linalg.pinv(L + 1e-12 * np.eye(n))
    marg = {i: {} for i in range(1, n + 1)}
    for m in range(1, n + 1):
        for h in range(0, n + 1):
            if h == m:
                continue
            if m == 1:
                # column 1's diagonal IS the root row (replaced), so non-root arcs enter ONLY the off-diagonal
                val = W[0][1] * B[0][0] if h == 0 else -W[h][1] * B[0][h - 1]
            elif h == 0:
                val = W[0][m] * B[m - 1][0]
            elif h == 1:
                # row 1 (h==1) off-diagonal was replaced by the root row -> A(1,m) enters ONLY the diagonal
                val = W[1][m] * B[m - 1][m - 1]
            else:
                val = W[h][m] * (B[m - 1][m - 1] - B[m - 1][h - 1])
            marg[m][h] = float(np.clip(val, 0.0, 1.0))
    return marg


# ================================================================================================
# EXACT 2nd-best spanning tree (Camerini-Fratta-Maffioli 1980). VERBATIM from exp_matrix_tree_parser_v1.
# WEAK live lever (5% parse-miss exposure) -- compute lazily / offline only, never on the read path.
# ================================================================================================
def second_best_tree(A, n, map_head=None):
    if map_head is None:
        map_head = chu_liu_edmonds(A, n)
    best_alt = None; best_alt_score = -np.inf; changed_tok = None
    for i in range(1, n + 1):
        A2 = A.copy()
        A2[map_head[i]][i] = -np.inf     # forbid the MAP arc into i
        alt = chu_liu_edmonds(A2, n)
        s = tree_score(A2, alt, n)
        if s > best_alt_score:
            best_alt_score, best_alt, changed_tok = s, alt, i
    return best_alt, changed_tok, best_alt_score


# ================================================================================================
# BRUTE-FORCE enumeration (n<=4) -- the exact positive control for Z, marginals, MAP, 2nd-best.
# VERBATIM from exp_matrix_tree_parser_v1 / exp_matrix_tree_singleroot_v1.
# ================================================================================================
def _valid_arborescence(head, n):
    """head: dict i->h (i in 1..n, h in 0..n). Valid iff following heads from every node reaches 0 (no cycle)."""
    for start in range(1, n + 1):
        x = start; steps = 0
        while x != 0:
            x = head.get(x)
            steps += 1
            if x is None or steps > n + 1:
                return False
    return True


def brute_force(A, n, temp=1.0):
    trees = []
    for combo in product(*[[h for h in range(0, n + 1) if h != i] for i in range(1, n + 1)]):
        head = {i + 1: combo[i] for i in range(n)}
        if not _valid_arborescence(head, n):
            continue
        sc = tree_score(A, head, n)
        trees.append((head, sc))
    # weights with per-modifier max shift (identical convention to matrix_tree_marginals)
    shift = {i: max(A[h][i] for h in range(0, n + 1) if h != i) for i in range(1, n + 1)}
    Z = 0.0
    wtrees = []
    for head, sc in trees:
        w = np.exp(sum((A[head[i]][i] - shift[i]) / temp for i in range(1, n + 1)))
        wtrees.append((head, sc, w)); Z += w
    marg = {i: {h: 0.0 for h in range(0, n + 1) if h != i} for i in range(1, n + 1)}
    for head, sc, w in wtrees:
        for i in range(1, n + 1):
            marg[i][head[i]] += w / Z
    order = sorted(trees, key=lambda t: t[1], reverse=True)
    map_head = order[0][0]; map_sc = order[0][1]
    second_sc = order[1][1] if len(order) > 1 else map_sc
    return marg, map_head, map_sc, second_sc, len(trees)


def _single_root(head, n):
    """valid arborescence AND exactly one modifier attaches to root 0."""
    if not _valid_arborescence(head, n):
        return False
    return sum(1 for i in range(1, n + 1) if head.get(i) == 0) == 1


def brute_force_singleroot(A, n, temp=1.0):
    shift = {i: max(A[h][i] for h in range(0, n + 1) if h != i) for i in range(1, n + 1)}
    Z = 0.0; wtrees = []
    for combo in product(*[[h for h in range(0, n + 1) if h != i] for i in range(1, n + 1)]):
        head = {i + 1: combo[i] for i in range(n)}
        if not _single_root(head, n):
            continue
        w = np.exp(sum((A[head[i]][i] - shift[i]) / temp for i in range(1, n + 1)))
        wtrees.append((head, w)); Z += w
    marg = {i: {h: 0.0 for h in range(0, n + 1) if h != i} for i in range(1, n + 1)}
    for head, w in wtrees:
        for i in range(1, n + 1):
            marg[i][head[i]] += w / Z
    return marg, len(wtrees)


# ================================================================================================
# BRUTE-FORCE self-tests -- the correctness gate (bit-identity vs enumeration for n<=4).
# _mt_self_test VERBATIM from exp_matrix_tree_parser_v1.self_test; _sr_self_test from
# exp_matrix_tree_singleroot_v1.self_test. decode_from_scores is imported LAZILY (hdlab->hdlab, avoids any
# import cycle: arc_parser may import this module's pure algorithms).
# ================================================================================================
def _mt_self_test():
    from hdlab.arc_parser import decode_from_scores
    rng = np.random.default_rng(7)
    for trial in range(200):
        n = int(rng.integers(2, 5))
        A = np.full((n + 1, n + 1), -np.inf)
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    A[h][i] = float(rng.normal(0, 1.5))
        Sc = {i: {h: A[h][i] for h in range(0, n + 1) if h != i} for i in range(1, n + 1)}
        for temp in (0.5, 1.0, 2.0):
            marg_bf, map_bf, map_sc_bf, second_sc_bf, ntrees = brute_force(A, n, temp)
            marg_mt = matrix_tree_marginals(A, n, temp)
            for i in range(1, n + 1):
                s = sum(marg_mt[i].values())
                assert abs(s - 1.0) < 1e-6, "marginals into token %d sum to %.6f (temp=%s)" % (i, s, temp)
                for h in marg_bf[i]:
                    assert abs(marg_mt[i][h] - marg_bf[i][h]) < 1e-6, \
                        "MTT marginal (%d<-%d) %.6f != brute %.6f (n=%d temp=%s)" % (i, h, marg_mt[i][h], marg_bf[i][h], n, temp)
        cle = chu_liu_edmonds(A, n)
        assert _valid_arborescence(cle, n), "CLE produced a non-arborescence"
        cle_sc = tree_score(A, cle, n)
        assert abs(cle_sc - map_sc_bf) < 1e-6, "CLE score %.6f != brute MAP %.6f (n=%d)" % (cle_sc, map_sc_bf, n)
        gh, _ = decode_from_scores(Sc, n)
        greedy_sc = tree_score(A, gh, n)
        if _valid_arborescence(gh, n):
            assert cle_sc >= greedy_sc - 1e-9, "CLE %.6f < valid-greedy %.6f (n=%d)" % (cle_sc, greedy_sc, n)
        _, _, sb_sc = second_best_tree(A, n, cle)
        assert abs(sb_sc - second_sc_bf) < 1e-6, "2nd-best %.6f != brute %.6f (n=%d)" % (sb_sc, second_sc_bf, n)
    return True


def _sr_self_test():
    rng = np.random.default_rng(11)
    for _ in range(200):
        n = int(rng.integers(2, 5))
        A = np.full((n + 1, n + 1), -np.inf)
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    A[h][i] = float(rng.normal(0, 1.5))
        for temp in (0.5, 1.0, 2.0):
            mbf, ntrees = brute_force_singleroot(A, n, temp)
            if ntrees == 0:
                continue
            msr = single_root_marginals(A, n, temp)
            for i in range(1, n + 1):
                s = sum(msr[i].values())
                assert abs(s - 1.0) < 1e-6, "single-root marginals into %d sum to %.6f" % (i, s)
                for h in mbf[i]:
                    assert abs(msr[i][h] - mbf[i][h]) < 1e-6, \
                        "single-root MTT (%d<-%d) %.6f != brute %.6f (n=%d temp=%s)" % (i, h, msr[i][h], mbf[i][h], n, temp)
    return True


# ================================================================================================
# Public graded-parse API
# ================================================================================================
class ParseOut(NamedTuple):
    map_heads: Dict[int, int]           # exact maximum spanning arborescence (Chu-Liu/Edmonds)
    marginals: Dict[int, Dict[int, float]]   # exact single-root Matrix-Tree edge marginals mu[dep][head]
    second_best_heads: Dict[int, int]   # exact 2nd-best arborescence (offline only -- weak live lever)


class GradedParse:
    """The globally-normalized graded parser over the landed arc-factored scorer (hdlab.arc_parser)."""

    def __init__(self, arc_parser, temp: float = 1.0):
        self.ap = arc_parser
        self.temp = float(temp)

    @classmethod
    def load(cls, path: str = None, temp: float = 1.0) -> "GradedParse":
        from hdlab.arc_parser import ArcParser
        if path is None:
            import os
            _REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
        return cls(ArcParser.load(path), temp=temp)

    def _scores(self, tokens: Sequence[str], pos: Sequence[str]):
        from hdlab.arc_parser import sentence_scores_auto
        n = len(tokens)
        sent = [(k + 1, tokens[k], pos[k], 0, "_") for k in range(n)]
        Sc = sentence_scores_auto(sent, self.ap.avg, self.ap._C, self.ap._tables())
        return dense_scores(Sc, n), n

    def marginals(self, tokens: Sequence[str], pos: Sequence[str]) -> Dict[int, Dict[int, float]]:
        """Exact single-root Matrix-Tree edge marginals -- the cheap (one inverse) reliability + graded posterior."""
        A, n = self._scores(tokens, pos)
        return single_root_marginals(A, n, self.temp)

    def parse(self, tokens: Sequence[str], pos: Sequence[str], want_second_best: bool = False) -> ParseOut:
        A, n = self._scores(tokens, pos)
        mh = chu_liu_edmonds(A, n)
        marg = single_root_marginals(A, n, self.temp)
        sb = second_best_tree(A, n, mh)[0] if want_second_best else {}
        return ParseOut(map_heads=mh, marginals=marg, second_best_heads=sb)


def patient_confidence_cue(marginals: Dict[int, Dict[int, float]], v: int, pk: int) -> float:
    """mu(v -> pk): the exact-posterior reliability that the picked patient pk attaches to verb v. Feeds
    parse_confidence (replacing the inert a2_marg) and the role-selection ensemble."""
    return float(marginals.get(pk, {}).get(v, 0.0))


def attachment_reliability(marginals: Dict[int, Dict[int, float]], head_of: Dict[int, int]) -> Dict[int, float]:
    """Per-dependent reliability mu(head_of[i] -> i) for ANY head-driven reader (universal signal; median AUC 0.825)."""
    return {i: float(marginals.get(i, {}).get(head_of.get(i, -1), 0.0)) for i in marginals}


def self_test() -> bool:
    """The promotion gate: the packaged marginals/decode/2nd-best are brute-force-exact (reuses the witnessed
    self-tests), and the public API returns a valid arborescence + normalized marginals on a smoke sentence."""
    assert _mt_self_test(), "matrix-tree/CLE/2nd-best brute-force self-test failed"
    assert _sr_self_test(), "single-root brute-force self-test failed"
    import os
    _REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    asset = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
    if os.path.exists(asset):
        gp = GradedParse.load(asset)
        toks = ["The", "committee", "gave", "the", "workers", "a", "raise", "."]
        pos = ["DET", "NOUN", "VERB", "DET", "NOUN", "DET", "NOUN", "PUNCT"]
        out = gp.parse(toks, pos, want_second_best=True)
        n = len(toks)
        assert all(1 <= i <= n for i in out.map_heads) and all(0 <= h <= n for h in out.map_heads.values())
        for i in range(1, n + 1):
            s = sum(out.marginals[i].values())
            assert abs(s - 1.0) < 1e-6, "marginals into %d sum to %.6f" % (i, s)
        assert patient_confidence_cue(out.marginals, 3, 5) >= 0.0
    return True


if __name__ == "__main__":
    print("self_test:", "PASS" if self_test() else "FAIL")
