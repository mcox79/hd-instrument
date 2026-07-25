"""arc_derivation_connectivity_gate_v1 -- CHEAP DECISIVE GATE before the derivation-reasoner build.

Implements Section 4 of notes/research_verification_by_derivation_reasoning_pivot_2026-07-25.md
EXACTLY: a CONNECTIVITY-ONLY test (NO scoring function, NO learned weights, NO backtracking, NO
search-quality tuning). It answers the single highest-risk question of the reasoning pivot before
any expensive build: does the TYPED directed rule-graph even CONNECT ARC questions to their answers
by a depth<=3 derivation, and does TYPING add selectivity over untyped similarity connectivity?

ONE VARIABLE = the graph edge set (TYPED-DIRECTED vs UNTYPED-SIMILARITY). Node set, node-unification,
given/choice->node mapping, BFS meet-in-middle search, and depth budget are IDENTICAL across the two
arms. Only the edges differ. This isolates whether observed connectivity comes from the typed/licensed
structure or from "any 3-hop connectivity" over a similarity-symmetrized graph.

REUSE (UNCHANGED):
  - rel.parse_tablestore_typed()  -- typed relation/arg0/arg1/confident extraction (relational-meaning cell)
  - SemanticHDEncoder (GloVe+WordNet) -- ONLY for node unification (fuzzy filler-string identity), NOT
    for scoring any chain.
  - arc._content_words / arc._load_questions / arc._CHAL_TEST -- crude given/choice extraction + ARC load.
  - The M3 bidirectional meet-in-middle SEARCH SHAPE (forward-from-givens, backward-from-choice, meet).

METRICS (per graph arm, verbatim from Section 4):
  (a) correct-choice coverage = frac of Qs where the CORRECT choice has a depth<=3 chain.
  (b) selectivity gap        = correct-choice coverage - mean WRONG-choice coverage.
  (c) same (a)+(b) for the UNTYPED_SIMILARITY_NULL graph.

PRE-REGISTERED BANDS (Section 4, verbatim -- reported with measured numbers, NOT tuned to force a band):
  GREEN  (build full reasoner): correct_cov >= 0.35 AND typed_gap >= 0.15 AND typed_gap > untyped_gap.
  RED    (redesign/supply rules first): correct_cov < 0.15  OR (typed_gap < 0.05 AND untyped_gap < 0.05).
  YELLOW (scoped subset build): coverage ok but typed gap not clearly > untyped null.

HONEST FLAGS (mandatory, Section 5):
  - report STRICT tau_unify first; do NOT tune tau_unify to force GREEN.
  - LOG merged-node pairs above tau_unify for spot-check (loose unify can spuriously merge e.g.
    'nuclear fuel'/'falling water' via thin GloVe/WordNet meaning); report obviously-wrong merges.
  - RED (coverage-bound) is a fully-reportable EXPECTED outcome -> redirect to SUPPLYING rules
    (expand the LICENSED table set / deeper hops), NOT abandoning reasoning.

CONTRACT: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic
(fixed seed, numpy default_rng, sorted iteration); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE:
  - except SystemExit raised BEFORE except Exception (no bare/BaseException).
  - final metrics atomicity = tmp + os.replace ; start-marker ; crash-diagnostic ; heartbeat.
  - real_code_path self_test: builds a REAL typed+null graph from a hand-built rule set via the REAL
    builder with an injected deterministic encoder (no GloVe needed), asserts (i) a PLANTED correct
    choice connects by a 2-hop typed chain while a LURE does NOT -> gate CAN fire GREEN (not can't-fail),
    and (ii) a DISCONNECTED case yields 0 coverage -> RED reachable; plus band-classifier asserts.
  - all reported numbers MEASURED @ this cell's metrics.json.
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

ANCHOR_NAME = "arc_derivation_connectivity_gate_v1"
SEED = 20260725

# LICENSED causal/conditional/functional relations (relation name == tablestore TSV basename).
LICENSED = ("CAUSE", "IFTHEN", "REQUIRES", "COUPLEDRELATIONSHIP", "SOURCEOF", "USEDFOR")

_T0 = [time.perf_counter()]


# ---------------------------------------------------------------------------
# atomic metrics / heartbeat / crash diag
# ---------------------------------------------------------------------------
def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# small linear-algebra helpers
# ---------------------------------------------------------------------------
def _l2_rows(M):
    M = np.asarray(M, dtype=np.float32)
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return M / n


class _UF:
    """Union-find for node unification."""
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


# ---------------------------------------------------------------------------
# graph construction (typed-directed + untyped-similarity-null share the SAME nodes)
# ---------------------------------------------------------------------------
def build_graph(rows, encode_fn, tau_unify, tau_sim):
    """Build BOTH the typed-directed graph and the untyped-similarity-null graph over ONE shared node set.

    rows: list of {relation, arg0, arg1} LICENSED confident rows (arg0/arg1 non-empty strings).
    encode_fn(list[str]) -> [n, dim] matrix (rows will be L2-normalized here).

    Returns a dict with:
      n_nodes, node_rep (L2 [Nn,dim]), node_label (list[str]) ;
      fwd/bwd (typed directed adjacency: dict node->set) ; edge_rel ((u,v)->relation) ;
      undirected (null similarity adjacency: dict node->set) ;
      map_word(word_vecs_L2 [W,dim]) -> per-word set(node_ids) via cos>=tau_unify ;
      merged_pairs (list of (str_a,str_b,cos) unified across DISTINCT strings, for spot-check) ;
      counts.
    """
    # 1. unique fillers
    fillers = []
    fidx = {}
    for r in rows:
        for s in (r["arg0"], r["arg1"]):
            if s not in fidx:
                fidx[s] = len(fillers)
                fillers.append(s)
    U = len(fillers)
    E = _l2_rows(encode_fn(fillers))  # [U, dim]

    # 2. node unification via cos >= tau_unify (union-find); LOG cross-string merges
    uf = _UF(U)
    merged_pairs = []
    S = (E @ E.T).astype(np.float32)
    iu = np.triu_indices(U, k=1)
    sim_u = S[iu]
    hit = np.where(sim_u >= tau_unify)[0]
    for h in hit.tolist():
        a = int(iu[0][h])
        b = int(iu[1][h])
        uf.union(a, b)
        merged_pairs.append((fillers[a], fillers[b], round(float(sim_u[h]), 4)))
    merged_pairs.sort(key=lambda t: -t[2])

    # 3. compact node ids; node representative = L2(mean of member filler vecs); label = shortest member
    root2node = {}
    members = {}
    for i in range(U):
        r = uf.find(i)
        if r not in root2node:
            root2node[r] = len(root2node)
        members.setdefault(root2node[r], []).append(i)
    Nn = len(root2node)
    dim = E.shape[1]
    node_rep = np.zeros((Nn, dim), dtype=np.float32)
    node_label = [""] * Nn
    for nid, mem in members.items():
        node_rep[nid] = E[mem].mean(axis=0)
        node_label[nid] = sorted((fillers[m] for m in mem), key=lambda s: (len(s), s))[0]
    node_rep = _l2_rows(node_rep)
    fnode = [root2node[uf.find(i)] for i in range(U)]  # filler idx -> node id

    # 4. TYPED directed edges: arg0_node --relation--> arg1_node
    fwd = {}
    bwd = {}
    edge_rel = {}
    n_typed_edges = 0
    for r in rows:
        u = fnode[fidx[r["arg0"]]]
        v = fnode[fidx[r["arg1"]]]
        if u == v:
            continue
        if v not in fwd.setdefault(u, set()):
            fwd[u].add(v)
            bwd.setdefault(v, set()).add(u)
            edge_rel[(u, v)] = r["relation"]
            n_typed_edges += 1

    # 5. UNTYPED similarity null: undirected edge between nodes with cos >= tau_sim (ignore type+direction)
    undirected = {}
    Snull = (node_rep @ node_rep.T).astype(np.float32)
    ju = np.triu_indices(Nn, k=1)
    simn = Snull[ju]
    hitn = np.where(simn >= tau_sim)[0]
    n_null_edges = 0
    for h in hitn.tolist():
        a = int(ju[0][h])
        b = int(ju[1][h])
        undirected.setdefault(a, set()).add(b)
        undirected.setdefault(b, set()).add(a)
        n_null_edges += 1

    def map_words(word_vecs_L2):
        """[W,dim] L2 -> list of set(node_ids) per word via cos>=tau_unify against node reps."""
        if word_vecs_L2.shape[0] == 0:
            return []
        M = (word_vecs_L2 @ node_rep.T).astype(np.float32)  # [W, Nn]
        out = []
        for w in range(M.shape[0]):
            out.append(set(np.where(M[w] >= tau_unify)[0].tolist()))
        return out

    return {
        "n_nodes": Nn, "node_rep": node_rep, "node_label": node_label,
        "fwd": fwd, "bwd": bwd, "edge_rel": edge_rel, "undirected": undirected,
        "map_words": map_words, "merged_pairs": merged_pairs,
        "n_fillers": U, "n_typed_edges": n_typed_edges, "n_null_edges": n_null_edges,
    }


# ---------------------------------------------------------------------------
# meet-in-middle connectivity (M3 search SHAPE; connectivity boolean only, NO scoring)
# ---------------------------------------------------------------------------
def _reach(adj, sources, depth):
    """BFS up to `depth` hops; return dict node -> min hop-distance (sources at 0)."""
    dist = {s: 0 for s in sources}
    frontier = set(sources)
    for d in range(depth):
        nxt = set()
        for u in frontier:
            nxt.update(adj.get(u, ()))
        nxt -= set(dist)
        if not nxt:
            break
        for v in nxt:
            dist[v] = d + 1
        frontier = nxt
    return dist


def meet_connected(fwd, bwd, given_nodes, choice_nodes, depth, min_len=1):
    """True if a chain of length in [min_len, depth] connects any given to the choice (meet-in-middle).
    d_fwd = ceil(depth/2), d_bwd = floor(depth/2). min_len=1 => a DERIVATION (>=1 licensed edge
    traversed); min_len=0 also counts trivial given==choice lexical overlap (reported as context)."""
    if not given_nodes or not choice_nodes:
        return False
    d_fwd = (depth + 1) // 2
    d_bwd = depth // 2
    fr = _reach(fwd, given_nodes, d_fwd)
    br = _reach(bwd, choice_nodes, d_bwd)
    for m in (set(fr) & set(br)):
        if fr[m] + br[m] >= min_len:
            return True
    return False


def _bfs_parents(adj, sources, depth):
    parent = {s: None for s in sources}
    frontier = list(sources)
    for _ in range(depth):
        nxt = []
        for u in frontier:
            for v in adj.get(u, ()):
                if v not in parent:
                    parent[v] = u
                    nxt.append(v)
        frontier = nxt
        if not frontier:
            break
    return parent


def reconstruct_chain(g, given_nodes, choice_nodes, depth):
    """Return a human-readable typed chain given->...->choice, or None."""
    d_fwd = (depth + 1) // 2
    d_bwd = depth // 2
    pf = _bfs_parents(g["fwd"], given_nodes, d_fwd)
    pb = _bfs_parents(g["bwd"], choice_nodes, d_bwd)
    lab = g["node_label"]
    er = g["edge_rel"]
    # prefer a meet node yielding a chain with >=1 typed edge (a real derivation)
    best = None
    for m in sorted(set(pf) & set(pb)):
        fpath = []
        x = m
        while x is not None:
            fpath.append(x)
            x = pf[x]
        fpath.reverse()
        bpath = []
        x = pb[m]
        while x is not None:
            bpath.append(x)
            x = pb[x]
        full = fpath + bpath
        steps = []
        for i in range(len(full) - 1):
            u, v = full[i], full[i + 1]
            steps.append(f"[{lab[u]}] --{er.get((u, v), '?')}--> [{lab[v]}]")
        if steps:
            return " ; ".join(steps)
        if best is None:
            best = f"[{lab[full[0]]}] (given==choice node, len0)"
    return best


# ---------------------------------------------------------------------------
# band classifier (Section 4 verbatim)
# ---------------------------------------------------------------------------
def classify_band(correct_cov_typed, typed_gap, untyped_gap):
    if correct_cov_typed < 0.15 or (typed_gap < 0.05 and untyped_gap < 0.05):
        return "RED"
    if correct_cov_typed >= 0.35 and typed_gap >= 0.15 and typed_gap > untyped_gap:
        return "GREEN"
    return "YELLOW"


# ---------------------------------------------------------------------------
# self-test (REAL builder path via injected deterministic encoder; no GloVe needed)
# ---------------------------------------------------------------------------
class _FakeEncoder:
    """Deterministic encoder: maps each distinct whitespace token to an orthonormal basis vector;
    a text encodes to the L2-mean of its token vectors. Strings sharing all tokens -> cos 1.0."""
    def __init__(self, dim=64):
        self.dim = dim
        self.vocab = {}

    def _tok_vec(self, tok):
        if tok not in self.vocab:
            i = len(self.vocab)
            v = np.zeros(self.dim, dtype=np.float32)
            v[i % self.dim] = 1.0
            self.vocab[tok] = v
        return self.vocab[tok]

    def encode_batch(self, texts):
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            toks = [w for w in str(t).lower().split() if w]
            if toks:
                out[i] = np.mean([self._tok_vec(w) for w in toks], axis=0)
        return out


def _self_test():
    print("[self-test] pure meet-in-middle connectivity ...", flush=True)
    # synthetic typed adjacency: 0(given) ->1 ->2(correct choice) ; 3(lure) isolated
    fwd = {0: {1}, 1: {2}}
    bwd = {1: {0}, 2: {1}}
    assert meet_connected(fwd, bwd, {0}, {2}, 3) is True, "planted 2-hop chain must connect at depth3"
    assert meet_connected(fwd, bwd, {0}, {3}, 3) is False, "lure must NOT connect"
    assert meet_connected(fwd, bwd, {0}, {2}, 1) is False, "2-hop must NOT connect at depth1 (d_fwd1,d_bwd0)"
    assert meet_connected(fwd, bwd, set(), {2}, 3) is False, "empty givens -> not connected"
    # min_len: a given node that IS a choice node (length-0 lexical overlap) counts only at min_len=0
    assert meet_connected({}, {}, {7}, {7}, 3, min_len=0) is True, "len0 overlap counts at min_len=0"
    assert meet_connected({}, {}, {7}, {7}, 3, min_len=1) is False, "len0 overlap EXCLUDED at min_len=1"
    print("[self-test] pure connectivity OK", flush=True)

    print("[self-test] REAL builder path (injected encoder) ...", flush=True)
    enc = _FakeEncoder(dim=64)
    # planted rule set: rain --CAUSE--> runoff --SOURCEOF--> river ; distractor volcano --CAUSE--> lava
    rows = [
        {"relation": "CAUSE", "arg0": "rain", "arg1": "runoff"},
        {"relation": "SOURCEOF", "arg0": "runoff", "arg1": "river"},
        {"relation": "CAUSE", "arg0": "volcano", "arg1": "lava"},
    ]
    g = build_graph(rows, enc.encode_batch, tau_unify=0.99, tau_sim=0.5)
    assert g["n_typed_edges"] == 3, f"expected 3 typed edges, got {g['n_typed_edges']}"

    def wvec(words):
        return _l2_rows(enc.encode_batch(words))

    # given = 'rain' ; correct choice = 'river' (connects rain->runoff->river, 2 hops) ; lure = 'lava'
    given_nodes = set().union(*g["map_words"](wvec(["rain"])))
    river_nodes = set().union(*g["map_words"](wvec(["river"])))
    lava_nodes = set().union(*g["map_words"](wvec(["lava"])))
    assert given_nodes and river_nodes and lava_nodes, "planted words must map to nodes"
    correct_conn = meet_connected(g["fwd"], g["bwd"], given_nodes, river_nodes, 3)
    lure_conn = meet_connected(g["fwd"], g["bwd"], given_nodes, lava_nodes, 3)
    assert correct_conn is True, "planted correct choice MUST connect (gate can fire GREEN)"
    assert lure_conn is False, "planted lure MUST NOT connect (selectivity real)"
    chain = reconstruct_chain(g, given_nodes, river_nodes, 3)
    assert chain and "CAUSE" in chain and "SOURCEOF" in chain, f"chain reconstruct failed: {chain}"
    print(f"[self-test] planted chain = {chain}", flush=True)

    # DISCONNECTED case -> 0 coverage -> RED reachable
    given_far = set().union(*g["map_words"](wvec(["volcano"])))  # volcano->lava only; river unreachable
    assert meet_connected(g["fwd"], g["bwd"], given_far, river_nodes, 3) is False, "must be disconnected"
    print("[self-test] REAL builder path OK", flush=True)

    # band classifier asserts (Section 4 verbatim)
    assert classify_band(0.40, 0.20, 0.05) == "GREEN"
    assert classify_band(0.10, 0.30, 0.00) == "RED"          # coverage too sparse
    assert classify_band(0.50, 0.03, 0.02) == "RED"          # both gaps flat
    assert classify_band(0.25, 0.10, 0.02) == "YELLOW"       # coverage mid
    assert classify_band(0.40, 0.16, 0.16) == "YELLOW"       # typed gap NOT > untyped
    print("[self-test] band classifier OK", flush=True)
    print("[self-test] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# main run
# ---------------------------------------------------------------------------
def run(output_dir, n_sample, tau_unify, tau_sim, depth, seed):
    os.makedirs(output_dir, exist_ok=True)
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _heartbeat(output_dir, "start", {"n_sample": n_sample, "tau_unify": tau_unify,
                                     "tau_sim": tau_sim, "depth": depth})

    # heavy imports deferred to run (self-test path stays GloVe-free)
    from experiments import exp_arc_selection_relational_meaning_v1 as rel
    from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder

    # 1. typed rule rows (LICENSED, confident, non-empty args)
    uid2typed = rel.parse_tablestore_typed()
    rows = []
    per_rel = {}
    for uid in sorted(uid2typed):
        d = uid2typed[uid]
        if d["relation"] in LICENSED and d["confident"] and d["arg0"].strip() and d["arg1"].strip():
            rows.append({"relation": d["relation"], "arg0": d["arg0"].strip(),
                         "arg1": d["arg1"].strip()})
            per_rel[d["relation"]] = per_rel.get(d["relation"], 0) + 1
    _heartbeat(output_dir, "rules_parsed", {"n_licensed_rows": len(rows), "per_relation": per_rel})

    # 2. encoder (GloVe+WordNet) -- node unification only
    encoder = SemanticHDEncoder()
    encode_fn = encoder.encode_batch
    _heartbeat(output_dir, "encoder_ready")

    # 3. build shared-node graph (typed edges + untyped-null edges)
    g = build_graph(rows, encode_fn, tau_unify, tau_sim)
    _heartbeat(output_dir, "graph_built", {"n_nodes": g["n_nodes"], "n_fillers": g["n_fillers"],
                                           "n_typed_edges": g["n_typed_edges"],
                                           "n_null_edges": g["n_null_edges"],
                                           "n_merged_pairs": len(g["merged_pairs"])})

    # 4. sample ARC-Challenge questions (deterministic)
    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(all_q))[:n_sample]
    questions = [all_q[int(i)] for i in sorted(idx.tolist())]
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_sample": len(questions)})

    # 5. pre-encode all unique content words in the sample (givens + choices) once
    word_set = set()
    for q in questions:
        for w in arc._content_words(q["stem"], min_len=4):
            word_set.add(w)
        for ch in q["choices"]:
            for w in arc._content_words(ch, min_len=4):
                word_set.add(w)
    words = sorted(word_set)
    wvecs = _l2_rows(encode_fn(words)) if words else np.zeros((0, g["node_rep"].shape[1]), np.float32)
    wnodes_list = g["map_words"](wvecs)
    word2nodes = {words[i]: wnodes_list[i] for i in range(len(words))}
    _heartbeat(output_dir, "words_mapped", {"n_words": len(words)})

    def nodes_for(text):
        ns = set()
        for w in arc._content_words(text, min_len=4):
            ns |= word2nodes.get(w, set())
        return ns

    # 6. connectivity over the sample, BOTH arms.
    #    HEADLINE = min_len=1 (a DERIVATION: >=1 licensed edge traversed). min_len=0 (counts trivial
    #    given==choice lexical overlap) is reported as CONTEXT only -- it conflates similarity with
    #    derivation and is not the pivot's question.
    def eval_arm(fwd, bwd, min_len):
        n_corr = 0
        wrong_hits = 0
        wrong_total = 0
        per_q = []
        for q in questions:
            given_nodes = nodes_for(q["stem"])
            ci = q["correct_index"]
            conns = []
            for j, ch in enumerate(q["choices"]):
                cn = nodes_for(ch)
                conns.append(meet_connected(fwd, bwd, given_nodes, cn, depth, min_len=min_len))
            c_ok = conns[ci] if ci < len(conns) else False
            if c_ok:
                n_corr += 1
            for j, cc in enumerate(conns):
                if j == ci:
                    continue
                wrong_total += 1
                if cc:
                    wrong_hits += 1
            per_q.append({"qid": q["qid"], "correct_conn": bool(c_ok),
                          "n_choice_conn": int(sum(conns))})
        nq = len(questions)
        cov = n_corr / nq if nq else 0.0
        wcov = wrong_hits / wrong_total if wrong_total else 0.0
        return {"correct_coverage": cov, "mean_wrong_coverage": wcov,
                "selectivity_gap": cov - wcov, "n_correct_connected": n_corr,
                "n_wrong_connected": wrong_hits, "n_wrong_total": wrong_total,
                "n_questions": nq, "per_q": per_q}

    typed = eval_arm(g["fwd"], g["bwd"], min_len=1)
    # untyped null: undirected adjacency used for BOTH forward and backward reach
    null = eval_arm(g["undirected"], g["undirected"], min_len=1)
    # context (min_len=0, trivial-overlap-inclusive) -- NOT the headline
    typed_l0 = eval_arm(g["fwd"], g["bwd"], min_len=0)
    null_l0 = eval_arm(g["undirected"], g["undirected"], min_len=0)
    typed_l0.pop("per_q")
    null_l0.pop("per_q")
    _heartbeat(output_dir, "connectivity_done",
               {"typed_cov": round(typed["correct_coverage"], 4),
                "typed_gap": round(typed["selectivity_gap"], 4),
                "null_cov": round(null["correct_coverage"], 4),
                "null_gap": round(null["selectivity_gap"], 4)})

    # 7. example chains (glass-box): up to 6 Qs where correct connected under typed
    examples = []
    for q in questions:
        if len(examples) >= 6:
            break
        given_nodes = nodes_for(q["stem"])
        ci = q["correct_index"]
        cn = nodes_for(q["choices"][ci])
        if meet_connected(g["fwd"], g["bwd"], given_nodes, cn, depth, min_len=1):
            chain = reconstruct_chain(g, given_nodes, cn, depth)
            lure_hit = None
            for j, ch in enumerate(q["choices"]):
                if j == ci:
                    continue
                if meet_connected(g["fwd"], g["bwd"], given_nodes, nodes_for(ch), depth, min_len=1):
                    lure_hit = ch
                    break
            examples.append({"qid": q["qid"], "stem": q["stem"][:200],
                             "correct_choice": q["choices"][ci][:120],
                             "correct_chain": chain,
                             "a_lure_also_connected": lure_hit[:120] if lure_hit else None})

    # 8. band (Section 4 verbatim)
    band = classify_band(typed["correct_coverage"], typed["selectivity_gap"], null["selectivity_gap"])

    # 9. depth-context sweep (cheap; grounds RED 'deeper hops' recommendation) -- typed arm only
    depth_sweep = {}
    for dd in sorted({2, depth, 4}):
        n_corr = 0
        for q in questions:
            gn = nodes_for(q["stem"])
            cn = nodes_for(q["choices"][q["correct_index"]])
            if meet_connected(g["fwd"], g["bwd"], gn, cn, dd, min_len=1):
                n_corr += 1
        depth_sweep[str(dd)] = round(n_corr / len(questions), 4) if questions else 0.0

    # strip heavy per_q from top-level metrics; keep summary + write full to sidecar
    typed_per_q = typed.pop("per_q")
    null_per_q = null.pop("per_q")

    band_msg = {
        "GREEN": "GREEN: build the full derivation reasoner (typed graph connects + typing adds selectivity).",
        "RED": "RED: redesign/SUPPLY rules first (coverage too sparse OR everything-connects). Fix = expand "
               "LICENSED table set / deeper hops -- NOT abandon reasoning.",
        "YELLOW": "YELLOW: scoped-subset build; typing/METRIC claim still open (typed gap not clearly > null).",
    }[band]

    metrics = {
        "verdict": "GATE_MEASURED",
        "band": band,
        "summary": f"CONNECTIVITY GATE = {band} | typed_cov={typed['correct_coverage']:.3f} "
                   f"typed_gap={typed['selectivity_gap']:.3f} null_gap={null['selectivity_gap']:.3f}",
        "verdict_msg": band_msg,
        "anchor_name": ANCHOR_NAME,
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "config": {"n_sample": len(questions), "tau_unify": tau_unify, "tau_sim": tau_sim,
                   "depth": depth, "seed": seed, "licensed": list(LICENSED)},
        "graph": {"n_licensed_rows": len(rows), "per_relation": per_rel,
                  "n_fillers": g["n_fillers"], "n_nodes": g["n_nodes"],
                  "n_typed_edges": g["n_typed_edges"], "n_null_edges": g["n_null_edges"],
                  "n_merged_pairs": len(g["merged_pairs"])},
        "metric_a_correct_coverage_typed": round(typed["correct_coverage"], 4),
        "metric_b_selectivity_gap_typed": round(typed["selectivity_gap"], 4),
        "metric_c_correct_coverage_untyped": round(null["correct_coverage"], 4),
        "metric_c_selectivity_gap_untyped": round(null["selectivity_gap"], 4),
        "typed": typed,
        "untyped_null": null,
        "context_min_len0_trivial_overlap_inclusive": {
            "typed_correct_coverage": round(typed_l0["correct_coverage"], 4),
            "typed_selectivity_gap": round(typed_l0["selectivity_gap"], 4),
            "untyped_correct_coverage": round(null_l0["correct_coverage"], 4),
            "untyped_selectivity_gap": round(null_l0["selectivity_gap"], 4),
            "note": "min_len=0 counts trivial given==choice lexical overlap (0 rule applications); "
                    "NOT a derivation -- reported only to show how much apparent connectivity is pure "
                    "lexical overlap vs real >=1-edge derivation (the headline min_len=1 numbers).",
        },
        "depth_sweep_correct_coverage_typed": depth_sweep,
        "example_chains": examples,
        "merged_pairs_top40": [{"a": a, "b": b, "cos": c} for (a, b, c) in g["merged_pairs"][:40]],
        "bands_preregistered": {
            "GREEN": "correct_cov>=0.35 AND typed_gap>=0.15 AND typed_gap>untyped_gap",
            "RED": "correct_cov<0.15 OR (typed_gap<0.05 AND untyped_gap<0.05)",
            "YELLOW": "coverage ok but typed gap not clearly > untyped null",
        },
        "min_len_policy": "HEADLINE metrics require min_len=1 (a DERIVATION: >=1 licensed edge traversed). "
                          "min_len=0 (trivial given==choice lexical overlap, 0 rule applications) is "
                          "reported only under context_min_len0_* -- it is NOT the pivot's derivation question.",
        "notes": "CONNECTIVITY-ONLY gate (no scoring/weights/backtracking). ONE variable = typed-directed "
                 "vs untyped-similarity edges (shared nodes/mapping/search/depth). STRICT tau_unify "
                 "reported; NOT tuned to force a band. merged_pairs_top40 = spot-check for spurious merges.",
        "REQUIRED_FIELDS": ["verdict", "band", "metric_a_correct_coverage_typed",
                            "metric_b_selectivity_gap_typed", "metric_c_correct_coverage_untyped",
                            "metric_c_selectivity_gap_untyped"],
    }
    _write_metrics_atomic(output_dir, metrics)
    # sidecar with per-question detail (keeps metrics.json lean)
    with open(os.path.join(output_dir, "per_question.json"), "w", encoding="utf-8") as f:
        json.dump({"typed": typed_per_q, "untyped_null": null_per_q}, f, indent=2)

    print("\n===== CONNECTIVITY GATE RESULT =====", flush=True)
    print(metrics["summary"], flush=True)
    print(f"(a) correct-coverage  typed={typed['correct_coverage']:.3f}  untyped={null['correct_coverage']:.3f}",
          flush=True)
    print(f"(b/c) selectivity gap typed={typed['selectivity_gap']:.3f}  untyped={null['selectivity_gap']:.3f}",
          flush=True)
    print(f"BAND = {band} :: {band_msg}", flush=True)
    print(f"depth_sweep(correct_cov typed) = {depth_sweep}", flush=True)
    print(f"graph: {len(rows)} licensed rows -> {g['n_nodes']} nodes, {g['n_typed_edges']} typed edges, "
          f"{g['n_null_edges']} null edges, {len(g['merged_pairs'])} merged pairs", flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--n", type=int, default=100, help="ARC-Challenge sample size")
    ap.add_argument("--tau-unify", type=float, default=0.85, help="STRICT node-identity threshold")
    ap.add_argument("--tau-sim", type=float, default=0.60, help="untyped-null similarity-edge threshold")
    ap.add_argument("--depth", type=int, default=3, help="max total meet-in-middle chain depth")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str,
                    default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    output_dir = args.out
    try:
        run(output_dir, args.n, args.tau_unify, args.tau_sim, args.depth, args.seed)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        _write_crash_metrics(output_dir, exc)
        print(f"[CRASH] {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
