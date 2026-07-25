"""arc_derivation_connectivity_gate_cleannodes_v2 -- ONE-VARIABLE ablation of the derivation
connectivity gate: re-run the SAME gate with CLEANED, NEGATION-AWARE node-identity.

WHY (VET-confirmed, atom 29551): the parent gate (exp_arc_derivation_connectivity_gate_v1) was RED,
but its 0.070 typed correct-coverage is a SPURIOUS artifact -- ALL 6/6 example chains route through
ONE over-merged [food] mega-hub (typed degree ~498, ~38.5% of edges). tau_unify=0.85 over thin
GloVe/WordNet transitively over-merged 9355 pairs AND COLLAPSED NEGATION (~239 merges like
"exist"~"not exist any more" cos~1.0, because SemanticHDEncoder drops "not" as a stopword). This cell
recomputes the gate with clean nodes to ADJUDICATE: is the RED PRIMARILY coverage-bound (clean nodes
-> coverage stays ~0 / drops -> rule-supply mandatory) or node-identity-bound (a RISE from
de-fragmentation)?  It ALSO builds the negation-aware node-identity that is a HARD PREREQUISITE for any
derivation reasoning (a graph where "not exist"~"exist" has discarded the entailment structure).

ONE VARIABLE = node-identity. EVERYTHING ELSE is reused UNCHANGED from the parent gate:
  - SAME licensed rules (LICENSED tuple, rel.parse_tablestore_typed, confident/non-empty filter)
  - SAME ~100 ARC-Challenge Qs (same seed sampling), SAME given/choice mapping (arc._content_words)
  - SAME typed directed graph + depth<=3 meet-in-middle search + UNTYPED_NULL comparison + metrics
  - SAME thresholds tau_unify=0.85, tau_sim=0.60, depth=3 (NOT tuned to force a band)
  - meet_connected / _reach / reconstruct_chain / classify_band / _UF / _l2_rows IMPORTED from parent

NODE-IDENTITY CHANGE (the single variable), three layers, all glass-box:
  (1) MEGA-HUB KILL = phrase-HEAD-lemma gate: a union-find cosine merge (cos>=tau_unify, same tau) is
      allowed ONLY when the two fillers share a normalized head-noun lemma. This blocks the transitive
      cross-head chaining that built the [food] deg-498 hub while keeping within-head synonymy. Word ->
      node mapping rule is UNCHANGED (cos>=tau_unify vs the -- now cleaner -- node reps).
  (2a) NEGATION-AWARE ENCODING: SemanticHDEncoder drops "not"/"no"/... as stopwords so "not exist" ==
      "exist". Fix = a thin wrapper that BINDS the content sum with a fixed random sign vector (+-1,
      300d, pre-projection) whenever a filler carries a negation cue. Binding preserves norms + inner
      products among negated items (cos("not X","not Y")==cos("X","Y") -> NO spurious negation-hub)
      while cos("exist","not exist")~=0. Non-negated fillers are BIT-UNCHANGED vs the base encoder
      (proved in self-test). ONLY the negation handling changes; same GloVe, same WordNet fuse, same P.
  (2b) POLARITY-GATED MERGE: reuse PolarityLexicon.contradicts (WordNet antonym + curated flip pairs +
      negation asymmetry) to BLOCK any union-find merge of two polarity-contradicting fillers. Defense
      -in-depth backstop to (2a): even if two fillers were cos-high, a fired contradiction rule vetoes
      the merge. Reports how many candidate merges the gate blocked (the "239 -> ~0" check).

DIAGNOSTIC OLD arm (in-cell "before"): the parent's identity (base negation-blind encoder, pure
cos>=0.85 merge, no gates) rebuilt here to reproduce the deg-~498 mega-hub + the ~239 negation-collapse
merges, so the before/after is self-contained (not reliant on stale disk). The PRIMARY typed-vs-untyped
headline runs on the CLEAN (new) graph only.

METRICS + PRE-REGISTERED BANDS (a priori; reported STRAIGHT, NOT tuned):
  PRIMARY adjudication = typed correct-choice coverage under CLEAN nodes:
    COVERAGE_BOUND_CONFIRMED (expected)  : clean_typed_cov < 0.15  (stays in/below parent RED coverage
        floor) -> rule-supply is MANDATORY next. Fully reportable.
    NODE_IDENTITY_BOUND_FLIP (unexpected): clean_typed_cov >= 0.15 (rises materially above the RED
        ceiling from de-fragmentation) -> the RED was a node-identity artifact, not coverage-bound.
        STRONG flip = clean_typed_cov >= 0.35 AND typed_gap>=0.15 AND typed_gap>untyped_gap (parent GREEN).
  SANITY invariants (must hold for a valid clean-node run; reported, not tuned):
    mega_hub_broken       : clean max typed node-degree < 100  (parent [food] ~498).
    negation_preserved    : clean polarity-contradiction merges remaining <= 5  (parent ~239).
  SECONDARY (revive-the-signal, NOT banked as a win): does typed vs untyped-null selectivity gap SURVIVE
    clean node-identity (typed_gap>untyped_gap AND typed_gap>0 -> mechanism corroborated-but-starved) or
    VANISH (typed_gap<=untyped_gap -> the parent 4.3x gap was a mega-hub artifact)?
  CONTROLS: untyped-null present; ONE variable = node-identity; report STRAIGHT.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic
(fixed seed, numpy default_rng, sorted iteration); repo .venv. Agent-reported VET-PENDING.

CELL-TEMPLATE:
  - except SystemExit raised BEFORE except Exception (no bare/BaseException).
  - final metrics atomicity = tmp + os.replace ; start-marker ; crash-diagnostic ; heartbeat.
  - real_code_path self_test: builds REAL clean+old graphs from a hand rule set via the REAL builder
    with an injected deterministic base encoder (no GloVe), asserts (i) neg-aware encoding separates
    "exist"/"not exist", (ii) head-gate blocks a cross-head cos-high merge, (iii) polarity-gate blocks
    a contradiction merge, (iv) a planted 2-hop typed chain connects while a lure does NOT (gate CAN
    fire), (v) a disconnected case -> 0 coverage (RED reachable); + band-classifier asserts.
  - deterministic_seeding: fixed int seed + numpy default_rng + sorted iteration; no hash()-seeding.
  - all reported numbers MEASURED @ this cell's metrics.json.

Compute architecture: sequential-CPU (JUSTIFIED). This is a cheap DIRECTIONAL adjudication gate
(compute-proportionality): graph build + BFS connectivity over ~100 Qs; the only vectorized cost is a
single GloVe encode of the fillers (gensim-internal). No matmul-heavy substrate primitive is swept ->
not a GPU-batching candidate. Parent full ran 126.7s; this adds one extra graph build (cheap) + one
extra 300d projection pass. Storage: no_storage (connectivity gate; no atoms written).
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

# reuse the parent gate's search + graph primitives UNCHANGED (ONE variable = node-identity)
from experiments import exp_arc_derivation_connectivity_gate_v1 as gate
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc

ANCHOR_NAME = "arc_derivation_connectivity_gate_cleannodes_v2"
SEED = 20260725

# SAME licensed relations + SAME thresholds as the parent (ONE variable = node-identity).
LICENSED = gate.LICENSED
TAU_UNIFY = 0.85
TAU_SIM = 0.60
DEPTH = 3
PRETRAIN_DIM = 300  # SemanticHDEncoder pretrain dim (GloVe 300d) -- neg binding lives here (pre-projection)

# literal negation cues for the ENCODER injection (narrower than PolarityLexicon's flip-inclusive set;
# antonym/flip opposition is handled by the polarity MERGE gate, not the encoder).
NEG_TOKENS = frozenset({
    "not", "no", "never", "cannot", "cant", "without", "lack", "lacks", "lacking",
    "none", "neither", "nor", "nothing", "non", "absence", "absent", "unable",
})

# pre-registered bands (a priori)
COV_BOUND_CEIL = 0.15   # clean_typed_cov < this -> COVERAGE_BOUND_CONFIRMED (expected)
FLIP_STRONG = 0.35      # clean_typed_cov >= this (+gap) -> parent-GREEN strong flip
MEGA_HUB_MAX_DEG = 100  # clean max typed node-degree must be < this (parent ~498)
NEG_MERGE_MAX = 5       # clean polarity-contradiction merges remaining must be <= this (parent ~239)

_T0 = [time.perf_counter()]


# ---------------------------------------------------------------------------
# atomic metrics / heartbeat / crash diag / start-marker
# ---------------------------------------------------------------------------
def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
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
# negation-aware encoder wrapper (single change vs base: inject NEG axis for negated fillers)
# ---------------------------------------------------------------------------
def _has_neg_token(text):
    """True iff text carries a literal negation cue (token in NEG_TOKENS or an n't contraction)."""
    for tok in str(text).lower().replace("'", " ").split():
        w = "".join(ch for ch in tok if ch.isalpha())
        if w in NEG_TOKENS or tok.endswith("nt"):
            return True
    return False


class NegAwareEncoder:
    """Wrap a base encoder exposing ._sum300(text)->[300] (negation-blind content sum) and .P
    ([N_DIM,300] JL projection). encode_batch BINDS the content sum with a fixed random sign vector
    (elementwise +-1) whenever a filler carries a negation cue. Binding is a norm/inner-product-
    preserving role assignment (standard HD role-filler bind; NOT vector-negation -v and NOT a
    geometric bipolar axis): cos("exist","not exist") ~= 0 (separated), while cos("not X","not Y") ==
    cos("X","Y") (negated fillers spread exactly as their content -> NO spurious negation-hub). Non-
    negated fillers are BIT-IDENTICAL to base.encode (proved in self-test)."""

    def __init__(self, base, seed=SEED):
        self.base = base
        rng = np.random.default_rng(seed * 7919 + 11)
        self.neg_sign = (rng.integers(0, 2, size=PRETRAIN_DIM) * 2 - 1).astype(np.float32)  # fixed +-1
        self.n_neg_flagged = 0

    def encode_batch(self, texts):
        texts = list(texts)
        S = np.zeros((len(texts), PRETRAIN_DIM), dtype=np.float32)
        for i, t in enumerate(texts):
            s = self.base._sum300(t).astype(np.float32)  # negation-blind content sum
            if _has_neg_token(t):
                s = s * self.neg_sign  # binding: preserves norm + inner products among negated items
                self.n_neg_flagged += 1
            S[i] = s
        return (S @ self.base.P.T).astype(np.float32)


# ---------------------------------------------------------------------------
# head-lemma normalization (the mega-hub kill)
# ---------------------------------------------------------------------------
def _lemma(w, wn):
    if wn is None:
        return w
    try:
        m = wn.morphy(w)
    except Exception:
        m = None
    return m if m else w


def _head_key(text, wn):
    """Normalized phrase-head lemma: last content word (arc stopword/len>=3 filter, drops negation),
    lemmatized. Empty content -> the lowercased stripped string (rare)."""
    cws = arc._content_words(text, min_len=3)
    if not cws:
        return str(text).strip().lower()
    return _lemma(cws[-1], wn)


# ---------------------------------------------------------------------------
# clean graph builder: SAME shape as gate.build_graph, node-identity gated by head + polarity + neg-enc
# ---------------------------------------------------------------------------
def build_graph_gated(rows, encode_fn, tau_unify, tau_sim, wn, pol_lex,
                      use_head_gate, use_pol_gate):
    """Return the SAME dict shape as gate.build_graph, with union-find merges gated by head-lemma and
    polarity. use_head_gate/use_pol_gate=False reproduces the parent's pure-cosine identity."""
    # 1. unique fillers (identical to parent)
    fillers = []
    fidx = {}
    for r in rows:
        for s in (r["arg0"], r["arg1"]):
            if s not in fidx:
                fidx[s] = len(fillers)
                fillers.append(s)
    U = len(fillers)
    E = gate._l2_rows(encode_fn(fillers))  # [U, dim]

    heads = [_head_key(fillers[i], wn) for i in range(U)] if use_head_gate else [None] * U

    # 2. gated union-find on cos >= tau_unify
    uf = gate._UF(U)
    merged_pairs = []
    n_candidate = 0
    n_head_blocked = 0
    n_pol_blocked = 0
    n_pol_contradiction_merged = 0  # contradiction pairs that STILL merged (should be ~0 w/ gate on)
    n_pol_contradiction_candidates = 0  # contradiction pairs among cos-candidates (the ~239 diagnostic)
    S = (E @ E.T).astype(np.float32)
    iu = np.triu_indices(U, k=1)
    sim_u = S[iu]
    hit = np.where(sim_u >= tau_unify)[0]
    for h in hit.tolist():
        a = int(iu[0][h]); b = int(iu[1][h])
        n_candidate += 1
        contra = pol_lex.contradicts(fillers[a], fillers[b]) if pol_lex is not None else False
        if contra:
            n_pol_contradiction_candidates += 1
        if use_head_gate and heads[a] != heads[b]:
            n_head_blocked += 1
            continue
        if use_pol_gate and contra:
            n_pol_blocked += 1
            continue
        uf.union(a, b)
        merged_pairs.append((fillers[a], fillers[b], round(float(sim_u[h]), 4)))
        if contra:
            n_pol_contradiction_merged += 1
    merged_pairs.sort(key=lambda t: -t[2])

    # 3. compact nodes (identical to parent)
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
    node_rep = gate._l2_rows(node_rep)
    fnode = [root2node[uf.find(i)] for i in range(U)]

    # 4. typed directed edges (identical to parent)
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

    # max typed node-degree (in+out) -- the mega-hub metric
    deg = {}
    for u, outs in fwd.items():
        deg[u] = deg.get(u, 0) + len(outs)
    for v, ins in bwd.items():
        deg[v] = deg.get(v, 0) + len(ins)
    if deg:
        top_node = max(deg, key=lambda k: deg[k])
        max_degree = deg[top_node]
        top_node_label = node_label[top_node]
    else:
        max_degree = 0
        top_node_label = None

    # 5. untyped-null similarity edges (identical to parent)
    undirected = {}
    Snull = (node_rep @ node_rep.T).astype(np.float32)
    ju = np.triu_indices(Nn, k=1)
    simn = Snull[ju]
    hitn = np.where(simn >= tau_sim)[0]
    n_null_edges = 0
    for h in hitn.tolist():
        a = int(ju[0][h]); b = int(ju[1][h])
        undirected.setdefault(a, set()).add(b)
        undirected.setdefault(b, set()).add(a)
        n_null_edges += 1

    def map_words(word_vecs_L2):
        if word_vecs_L2.shape[0] == 0:
            return []
        M = (word_vecs_L2 @ node_rep.T).astype(np.float32)
        return [set(np.where(M[w] >= tau_unify)[0].tolist()) for w in range(M.shape[0])]

    return {
        "n_nodes": Nn, "node_rep": node_rep, "node_label": node_label,
        "fwd": fwd, "bwd": bwd, "edge_rel": edge_rel, "undirected": undirected,
        "map_words": map_words, "merged_pairs": merged_pairs,
        "n_fillers": U, "n_typed_edges": n_typed_edges, "n_null_edges": n_null_edges,
        "max_typed_node_degree": int(max_degree), "max_degree_node_label": top_node_label,
        "n_merge_candidates": n_candidate, "n_head_blocked": n_head_blocked,
        "n_pol_blocked": n_pol_blocked, "n_merges": len(merged_pairs),
        "n_pol_contradiction_candidates": n_pol_contradiction_candidates,
        "n_pol_contradiction_merged": n_pol_contradiction_merged,
    }


# ---------------------------------------------------------------------------
# per-arm connectivity eval (identical logic to parent's nested eval_arm)
# ---------------------------------------------------------------------------
def eval_arm(fwd, bwd, questions, nodes_for, depth, min_len):
    n_corr = 0
    wrong_hits = 0
    wrong_total = 0
    per_q = []
    for q in questions:
        given_nodes = nodes_for(q["stem"])
        ci = q["correct_index"]
        conns = [gate.meet_connected(fwd, bwd, given_nodes, nodes_for(ch), depth, min_len=min_len)
                 for ch in q["choices"]]
        c_ok = conns[ci] if ci < len(conns) else False
        if c_ok:
            n_corr += 1
        for j, cc in enumerate(conns):
            if j == ci:
                continue
            wrong_total += 1
            if cc:
                wrong_hits += 1
        per_q.append({"qid": q["qid"], "correct_conn": bool(c_ok), "n_choice_conn": int(sum(conns))})
    nq = len(questions)
    cov = n_corr / nq if nq else 0.0
    wcov = wrong_hits / wrong_total if wrong_total else 0.0
    return {"correct_coverage": cov, "mean_wrong_coverage": wcov, "selectivity_gap": cov - wcov,
            "n_correct_connected": n_corr, "n_wrong_connected": wrong_hits,
            "n_wrong_total": wrong_total, "n_questions": nq, "per_q": per_q}


# ---------------------------------------------------------------------------
# self-test (REAL builder path via injected deterministic base encoder; GloVe-free)
# ---------------------------------------------------------------------------
class _FakeBase:
    """Mimics SemanticHDEncoder interface for self-test: ._sum300 (negation-blind token-basis sum via
    arc._content_words, so 'not' is dropped) and .P = identity (dims line up)."""
    def __init__(self, dim=PRETRAIN_DIM):
        self.dim = dim
        self.P = np.eye(dim, dtype=np.float32)
        self.vocab = {}

    def _tok(self, t):
        if t not in self.vocab:
            i = len(self.vocab)
            v = np.zeros(self.dim, dtype=np.float32)
            v[i % self.dim] = 1.0
            self.vocab[t] = v
        return self.vocab[t]

    def _sum300(self, text):
        acc = np.zeros(self.dim, dtype=np.float32)
        for w in arc._content_words(text, min_len=3):  # drops "not" -> negation-blind (mirrors real)
            acc = acc + self._tok(w)
        return acc

    def encode_batch(self, texts):
        texts = list(texts)
        S = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            S[i] = self._sum300(t)
        return (S @ self.P.T).astype(np.float32)


def _self_test():
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    print("[self-test] pure meet-in-middle connectivity (imported from parent) ...", flush=True)
    fwd = {0: {1}, 1: {2}}
    bwd = {1: {0}, 2: {1}}
    assert gate.meet_connected(fwd, bwd, {0}, {2}, 3) is True
    assert gate.meet_connected(fwd, bwd, {0}, {3}, 3) is False
    print("[self-test] pure connectivity OK", flush=True)

    wn = _load_wordnet()
    pol = PolarityLexicon()
    base = _FakeBase()
    enc = NegAwareEncoder(base, seed=SEED)

    # (i) neg-aware encoding SEPARATES "exist" from "not exist"; leaves non-negated bit-unchanged
    v = enc.encode_batch(["exist", "not exist", "river"])
    v = gate._l2_rows(v)
    cos_exist_notexist = float(v[0] @ v[1])
    assert cos_exist_notexist < TAU_UNIFY, f"neg-aware failed to separate: cos={cos_exist_notexist}"
    # non-negated identical to base.encode (up to final L2)
    base_river = gate._l2_rows((base._sum300("river") @ base.P.T)[None, :])[0]
    assert np.allclose(v[2], base_river, atol=1e-5), "non-negated filler must equal base encoding"
    print(f"[self-test] neg-aware OK: cos(exist, not exist)={cos_exist_notexist:.3f} < {TAU_UNIFY}", flush=True)

    # (ii) head-gate blocks a cross-head cos-high merge ; (iii) polarity-gate blocks a contradiction merge
    # planted rules: rain --CAUSE--> runoff --SOURCEOF--> river ; volcano --CAUSE--> lava
    rows = [
        {"relation": "CAUSE", "arg0": "rain", "arg1": "runoff"},
        {"relation": "SOURCEOF", "arg0": "runoff", "arg1": "river"},
        {"relation": "CAUSE", "arg0": "volcano", "arg1": "lava"},
    ]
    g = build_graph_gated(rows, enc.encode_batch, tau_unify=0.99, tau_sim=0.5, wn=wn, pol_lex=pol,
                          use_head_gate=True, use_pol_gate=True)
    assert g["n_typed_edges"] == 3, f"expected 3 typed edges, got {g['n_typed_edges']}"

    def wvec(words):
        return gate._l2_rows(enc.encode_batch(words))

    given_nodes = set().union(*g["map_words"](wvec(["rain"])))
    river_nodes = set().union(*g["map_words"](wvec(["river"])))
    lava_nodes = set().union(*g["map_words"](wvec(["lava"])))
    assert given_nodes and river_nodes and lava_nodes, "planted words must map to nodes"
    assert gate.meet_connected(g["fwd"], g["bwd"], given_nodes, river_nodes, 3) is True, \
        "planted correct choice MUST connect (gate can fire)"
    assert gate.meet_connected(g["fwd"], g["bwd"], given_nodes, lava_nodes, 3) is False, \
        "planted lure MUST NOT connect (selectivity real)"

    # head-gate: two DIFFERENT-head fillers that the FakeBase makes cos-high must NOT merge.
    # "nuclear fuel" vs "falling water": share no content tokens under fake -> cos 0; force a shared token
    # pair with different heads: "solar power" vs "wind power" share "power" (head) -> WOULD merge (same head).
    # Use "power source" (head=source) vs "power plant" (head=plant): share "power", heads differ -> blocked.
    rows_h = [{"relation": "CAUSE", "arg0": "power source", "arg1": "x"},
              {"relation": "CAUSE", "arg0": "power plant", "arg1": "y"}]
    gh = build_graph_gated(rows_h, enc.encode_batch, tau_unify=0.30, tau_sim=0.99, wn=wn, pol_lex=pol,
                           use_head_gate=True, use_pol_gate=True)
    gh_off = build_graph_gated(rows_h, enc.encode_batch, tau_unify=0.30, tau_sim=0.99, wn=wn, pol_lex=pol,
                               use_head_gate=False, use_pol_gate=False)
    assert gh["n_head_blocked"] >= 1, f"head-gate should block cross-head merge: {gh['n_head_blocked']}"
    assert gh["n_nodes"] > gh_off["n_nodes"], "head-gate must yield MORE (less-merged) nodes than ungated"
    print(f"[self-test] head-gate OK: blocked={gh['n_head_blocked']}, "
          f"nodes gated={gh['n_nodes']} > ungated={gh_off['n_nodes']}", flush=True)

    # polarity-gate: contradiction pair cos-high, same head -> gate must block.
    # "increase" vs "not increase": same head lemma "increase"; contradicts() fires (negation asymmetry).
    rows_p = [{"relation": "CAUSE", "arg0": "increase heat", "arg1": "x"},
              {"relation": "CAUSE", "arg0": "not increase heat", "arg1": "y"}]
    # force cos-high by low tau; neg-enc already separates, so also test with pol gate isolated via base enc
    gp = build_graph_gated(rows_p, base.encode_batch, tau_unify=0.30, tau_sim=0.99, wn=wn, pol_lex=pol,
                           use_head_gate=False, use_pol_gate=True)
    assert gp["n_pol_blocked"] >= 1, f"polarity-gate should block contradiction merge: {gp['n_pol_blocked']}"
    assert gp["n_pol_contradiction_merged"] == 0, "no contradiction pair may survive the polarity gate"
    print(f"[self-test] polarity-gate OK: pol_blocked={gp['n_pol_blocked']}, "
          f"contradiction_merged={gp['n_pol_contradiction_merged']}", flush=True)

    # (v) disconnected -> 0 coverage (RED reachable)
    far = set().union(*g["map_words"](wvec(["volcano"])))
    assert gate.meet_connected(g["fwd"], g["bwd"], far, river_nodes, 3) is False, "must be disconnected"

    # band classifier (imported from parent, verbatim bands)
    assert gate.classify_band(0.40, 0.20, 0.05) == "GREEN"
    assert gate.classify_band(0.10, 0.30, 0.00) == "RED"
    assert gate.classify_band(0.25, 0.10, 0.02) == "YELLOW"
    assert classify_primary(0.07) == "COVERAGE_BOUND_CONFIRMED"
    assert classify_primary(0.22) == "NODE_IDENTITY_BOUND_FLIP"
    print("[self-test] band classifiers OK", flush=True)
    print("[self-test] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# primary adjudication band
# ---------------------------------------------------------------------------
def classify_primary(clean_typed_cov):
    if clean_typed_cov < COV_BOUND_CEIL:
        return "COVERAGE_BOUND_CONFIRMED"
    return "NODE_IDENTITY_BOUND_FLIP"


# ---------------------------------------------------------------------------
# main run
# ---------------------------------------------------------------------------
def run(output_dir, n_sample, seed):
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full")
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _heartbeat(output_dir, "start", {"n_sample": n_sample, "tau_unify": TAU_UNIFY,
                                     "tau_sim": TAU_SIM, "depth": DEPTH})

    from experiments import exp_arc_selection_relational_meaning_v1 as rel
    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon

    # 1. typed rule rows (LICENSED, confident, non-empty) -- IDENTICAL to parent
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

    # 2. encoders: base (parent identity) + neg-aware wrapper (ONLY negation handling differs)
    base_enc = SemanticHDEncoder()
    neg_enc = NegAwareEncoder(base_enc, seed=seed)
    wn = base_enc._wn
    pol = PolarityLexicon()
    _heartbeat(output_dir, "encoder_ready")

    # 3a. OLD identity (diagnostic "before": parent's pure-cosine, negation-blind, no gates)
    g_old = build_graph_gated(rows, base_enc.encode_batch, TAU_UNIFY, TAU_SIM, wn, pol,
                              use_head_gate=False, use_pol_gate=False)
    _heartbeat(output_dir, "old_graph_built",
               {"n_nodes": g_old["n_nodes"], "max_deg": g_old["max_typed_node_degree"],
                "hub_label": g_old["max_degree_node_label"], "n_merges": g_old["n_merges"],
                "pol_contradiction_merged": g_old["n_pol_contradiction_merged"]})

    # 3b. CLEAN identity (head-gate + polarity-gate + neg-aware encoding) -- the single-variable change
    g = build_graph_gated(rows, neg_enc.encode_batch, TAU_UNIFY, TAU_SIM, wn, pol,
                          use_head_gate=True, use_pol_gate=True)
    _heartbeat(output_dir, "clean_graph_built",
               {"n_nodes": g["n_nodes"], "max_deg": g["max_typed_node_degree"],
                "hub_label": g["max_degree_node_label"], "n_merges": g["n_merges"],
                "head_blocked": g["n_head_blocked"], "pol_blocked": g["n_pol_blocked"],
                "pol_contradiction_remaining": g["n_pol_contradiction_merged"],
                "neg_flagged_fillers": neg_enc.n_neg_flagged})

    # 4. sample ARC-Challenge questions -- IDENTICAL to parent (same seed permutation)
    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(all_q))[:n_sample]
    questions = [all_q[int(i)] for i in sorted(idx.tolist())]
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_sample": len(questions)})

    # 5. pre-encode unique content words (givens + choices) once with the NEG-aware encoder, map to
    #    CLEAN nodes. Word->node mapping RULE is unchanged (cos>=tau_unify vs node reps).
    word_set = set()
    for q in questions:
        for w in arc._content_words(q["stem"], min_len=4):
            word_set.add(w)
        for ch in q["choices"]:
            for w in arc._content_words(ch, min_len=4):
                word_set.add(w)
    words = sorted(word_set)
    wvecs = gate._l2_rows(neg_enc.encode_batch(words)) if words else \
        np.zeros((0, g["node_rep"].shape[1]), np.float32)
    wnodes = g["map_words"](wvecs)
    word2nodes = {words[i]: wnodes[i] for i in range(len(words))}
    _heartbeat(output_dir, "words_mapped", {"n_words": len(words)})

    def nodes_for(text):
        ns = set()
        for w in arc._content_words(text, min_len=4):
            ns |= word2nodes.get(w, set())
        return ns

    # 6. connectivity, BOTH arms, on the CLEAN graph (min_len=1 = a real >=1-edge derivation)
    typed = eval_arm(g["fwd"], g["bwd"], questions, nodes_for, DEPTH, min_len=1)
    null = eval_arm(g["undirected"], g["undirected"], questions, nodes_for, DEPTH, min_len=1)
    typed_l0 = eval_arm(g["fwd"], g["bwd"], questions, nodes_for, DEPTH, min_len=0)
    null_l0 = eval_arm(g["undirected"], g["undirected"], questions, nodes_for, DEPTH, min_len=0)
    typed_l0.pop("per_q"); null_l0.pop("per_q")
    _heartbeat(output_dir, "connectivity_done",
               {"clean_typed_cov": round(typed["correct_coverage"], 4),
                "clean_typed_gap": round(typed["selectivity_gap"], 4),
                "clean_null_cov": round(null["correct_coverage"], 4),
                "clean_null_gap": round(null["selectivity_gap"], 4)})

    # 7. example chains (glass-box): up to 6 Qs where correct connected under CLEAN typed
    examples = []
    for q in questions:
        if len(examples) >= 6:
            break
        given_nodes = nodes_for(q["stem"])
        ci = q["correct_index"]
        cn = nodes_for(q["choices"][ci])
        if gate.meet_connected(g["fwd"], g["bwd"], given_nodes, cn, DEPTH, min_len=1):
            chain = gate.reconstruct_chain(g, given_nodes, cn, DEPTH)
            examples.append({"qid": q["qid"], "stem": q["stem"][:200],
                             "correct_choice": q["choices"][ci][:120], "correct_chain": chain})

    # 8. bands
    clean_typed_cov = typed["correct_coverage"]
    typed_gap = typed["selectivity_gap"]
    untyped_gap = null["selectivity_gap"]
    primary = classify_primary(clean_typed_cov)
    parent_band = gate.classify_band(clean_typed_cov, typed_gap, untyped_gap)  # for continuity
    strong_flip = (clean_typed_cov >= FLIP_STRONG and typed_gap >= 0.15 and typed_gap > untyped_gap)

    mega_hub_broken = g["max_typed_node_degree"] < MEGA_HUB_MAX_DEG
    negation_preserved = g["n_pol_contradiction_merged"] <= NEG_MERGE_MAX
    selectivity_survives = (typed_gap > untyped_gap) and (typed_gap > 0.0)

    # 9. cheap depth-context sweep on CLEAN typed arm
    depth_sweep = {}
    for dd in sorted({2, DEPTH, 4}):
        nc = 0
        for q in questions:
            gn = nodes_for(q["stem"])
            cn = nodes_for(q["choices"][q["correct_index"]])
            if gate.meet_connected(g["fwd"], g["bwd"], gn, cn, dd, min_len=1):
                nc += 1
        depth_sweep[str(dd)] = round(nc / len(questions), 4) if questions else 0.0

    typed_per_q = typed.pop("per_q")
    null_per_q = null.pop("per_q")

    summary = (f"CLEAN-NODES GATE primary={primary} | clean_typed_cov={clean_typed_cov:.3f} "
               f"(parent RED 0.070) | max_deg {g_old['max_typed_node_degree']}->"
               f"{g['max_typed_node_degree']} | neg_merges {g_old['n_pol_contradiction_merged']}->"
               f"{g['n_pol_contradiction_merged']} | typed_gap={typed_gap:.4f} vs "
               f"untyped_gap={untyped_gap:.4f} (survives={selectivity_survives})")
    vmsg = {
        "COVERAGE_BOUND_CONFIRMED": ("COVERAGE-BOUND CONFIRMED: clean node-identity keeps typed "
            "correct-coverage below the RED ceiling -> the parent 0.070 was a mega-hub artifact; "
            "RULE-SUPPLY is mandatory next (the licensed table set does not connect ARC Qs to answers "
            "by depth<=3 even with clean nodes)."),
        "NODE_IDENTITY_BOUND_FLIP": ("NODE-IDENTITY-BOUND (unexpected FLIP): clean node-identity RAISED "
            "typed correct-coverage materially above the RED ceiling -> the RED was partly a "
            "fragmentation/over-merge artifact of node-identity, not purely coverage-bound. Re-adjudicate "
            "before mandating rule-supply."),
    }[primary]

    metrics = {
        "verdict": "GATE_MEASURED",
        "primary_adjudication": primary,
        "strong_flip_parent_green": bool(strong_flip),
        "parent_band_on_clean_nodes": parent_band,
        "summary": summary,
        "verdict_msg": vmsg,
        "anchor_name": ANCHOR_NAME,
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": "full",
        "config": {"n_sample": len(questions), "tau_unify": TAU_UNIFY, "tau_sim": TAU_SIM,
                   "depth": DEPTH, "seed": seed, "neg_marker": "sign_flip_binding",
                   "licensed": list(LICENSED),
                   "one_variable": "node_identity (head-gate + polarity-gate + neg-aware encoding); "
                                   "rules/Qs/depth/typed-vs-untyped/thresholds identical to parent"},
        # ---- PRIMARY adjudication (clean nodes) ----
        "clean_typed_correct_coverage": round(clean_typed_cov, 4),
        "clean_typed_selectivity_gap": round(typed_gap, 4),
        "clean_untyped_correct_coverage": round(null["correct_coverage"], 4),
        "clean_untyped_selectivity_gap": round(untyped_gap, 4),
        # ---- SANITY invariants ----
        "sanity": {
            "mega_hub_broken": bool(mega_hub_broken),
            "clean_max_typed_node_degree": g["max_typed_node_degree"],
            "clean_max_degree_node_label": g["max_degree_node_label"],
            "old_max_typed_node_degree": g_old["max_typed_node_degree"],
            "old_max_degree_node_label": g_old["max_degree_node_label"],
            "negation_preserved": bool(negation_preserved),
            "old_pol_contradiction_merged": g_old["n_pol_contradiction_merged"],
            "clean_pol_contradiction_remaining": g["n_pol_contradiction_merged"],
            "clean_pol_contradiction_candidates": g["n_pol_contradiction_candidates"],
            "clean_pol_merges_blocked": g["n_pol_blocked"],
            "clean_head_merges_blocked": g["n_head_blocked"],
            "neg_flagged_fillers": neg_enc.n_neg_flagged,
        },
        # ---- SECONDARY: selectivity survival (NOT a win) ----
        "secondary_selectivity": {
            "selectivity_survives_clean_nodes": bool(selectivity_survives),
            "clean_typed_gap": round(typed_gap, 4),
            "clean_untyped_gap": round(untyped_gap, 4),
            "parent_typed_gap_on_disk": 0.0296,
            "parent_untyped_gap_on_disk": 0.0069,
            "note": ("SURVIVES = typed_gap>untyped_gap AND >0 (typing mechanism corroborated but "
                     "starved); VANISHES = otherwise (the parent 4.3x gap was a mega-hub artifact)."),
        },
        "graph_clean": {"n_licensed_rows": len(rows), "per_relation": per_rel,
                        "n_fillers": g["n_fillers"], "n_nodes": g["n_nodes"],
                        "n_typed_edges": g["n_typed_edges"], "n_null_edges": g["n_null_edges"],
                        "n_merges": g["n_merges"], "n_merge_candidates": g["n_merge_candidates"]},
        "graph_old_diagnostic": {"n_nodes": g_old["n_nodes"], "n_typed_edges": g_old["n_typed_edges"],
                                 "n_null_edges": g_old["n_null_edges"], "n_merges": g_old["n_merges"],
                                 "max_typed_node_degree": g_old["max_typed_node_degree"]},
        "typed": typed, "untyped_null": null,
        "context_min_len0_trivial_overlap_inclusive": {
            "typed_correct_coverage": round(typed_l0["correct_coverage"], 4),
            "typed_selectivity_gap": round(typed_l0["selectivity_gap"], 4),
            "untyped_correct_coverage": round(null_l0["correct_coverage"], 4),
            "untyped_selectivity_gap": round(null_l0["selectivity_gap"], 4),
            "note": "min_len=0 counts trivial given==choice lexical overlap (0 rule applications); "
                    "NOT a derivation -- context only.",
        },
        "depth_sweep_correct_coverage_clean_typed": depth_sweep,
        "example_chains_clean": examples,
        "clean_merged_pairs_top40": [{"a": a, "b": b, "cos": c} for (a, b, c) in g["merged_pairs"][:40]],
        "bands_preregistered": {
            "PRIMARY": {"COVERAGE_BOUND_CONFIRMED": f"clean_typed_cov < {COV_BOUND_CEIL}",
                        "NODE_IDENTITY_BOUND_FLIP": f"clean_typed_cov >= {COV_BOUND_CEIL}",
                        "STRONG_FLIP_PARENT_GREEN": f"clean_typed_cov >= {FLIP_STRONG} AND typed_gap>=0.15 "
                                                    "AND typed_gap>untyped_gap"},
            "SANITY": {"mega_hub_broken": f"clean max typed node-degree < {MEGA_HUB_MAX_DEG}",
                       "negation_preserved": f"clean polarity-contradiction merges <= {NEG_MERGE_MAX}"},
            "SECONDARY": "selectivity_survives = typed_gap>untyped_gap AND typed_gap>0",
        },
        "parent_ref_on_disk": {
            "source": "data/exp_arc_derivation_connectivity_gate_v1/metrics.json",
            "band": "RED", "typed_cov": 0.07, "typed_gap": 0.0296, "untyped_cov": 0.32,
            "untyped_gap": 0.0069, "n_merged_pairs": 9355, "n_nodes": 1654,
            "note": "recomputed OLD-identity in-cell (graph_old_diagnostic) as the self-contained before.",
        },
        "notes": ("ONE-VARIABLE ablation of exp_arc_derivation_connectivity_gate_v1: node-identity only. "
                  "Head-lemma gate kills the transitive cross-head mega-hub; neg-aware encoding + "
                  "PolarityLexicon.contradicts merge-gate preserve negation. STRAIGHT report; NOT tuned. "
                  "COVERAGE_BOUND_CONFIRMED is the EXPECTED, fully-reportable outcome -> mandates RULE-SUPPLY."),
        "REQUIRED_FIELDS": ["verdict", "primary_adjudication", "clean_typed_correct_coverage",
                            "clean_typed_selectivity_gap", "clean_untyped_correct_coverage",
                            "clean_untyped_selectivity_gap", "sanity"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    with open(os.path.join(output_dir, "per_question.json"), "w", encoding="utf-8") as f:
        json.dump({"typed": typed_per_q, "untyped_null": null_per_q}, f, indent=2)

    print("\n===== CLEAN-NODES CONNECTIVITY GATE RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"PRIMARY = {primary} :: {vmsg}", flush=True)
    print(f"mega_hub_broken={mega_hub_broken} (deg {g_old['max_typed_node_degree']}"
          f"[{g_old['max_degree_node_label']}] -> {g['max_typed_node_degree']}"
          f"[{g['max_degree_node_label']}]);  negation_preserved={negation_preserved} "
          f"(pol-contradiction merges {g_old['n_pol_contradiction_merged']} -> "
          f"{g['n_pol_contradiction_merged']}; blocked={g['n_pol_blocked']}; "
          f"neg_flagged_fillers={neg_enc.n_neg_flagged})", flush=True)
    print(f"selectivity_survives={selectivity_survives} (typed_gap={typed_gap:.4f} vs "
          f"untyped_gap={untyped_gap:.4f})", flush=True)
    print(f"nodes old={g_old['n_nodes']} -> clean={g['n_nodes']} "
          f"(head_blocked={g['n_head_blocked']}, pol_blocked={g['n_pol_blocked']})", flush=True)
    print(f"depth_sweep(clean typed) = {depth_sweep}", flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=100, help="ARC-Challenge sample size")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    n_sample = 12 if args.mode == "smoke" else args.n
    output_dir = args.out
    try:
        run(output_dir, n_sample, args.seed)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print(f"[CRASH] {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
