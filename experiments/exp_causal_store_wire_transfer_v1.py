"""exp_causal_store_wire_transfer_v1 -- DOES THE MINED-STORE +0.139/+0.150 TRANSFER TO THE READER'S OWN
EXTRACTED-FROM-PROSE CAUSAL READ? (the wire_the_mined_directed_causal_store... problem, the live-transfer measurement).

BACKGROUND (disk-established, exp_causal_necessity_bf_reader_v1 metrics + grow_the_causal_mechanism SOLVED):
  * The store's PROVEN prize is the KNOWLEDGE-TEST arm: a graph built from the MINED STORE ONLY (no given order),
    rung-2 do-sim necessity, beats the shuffled-store twin +0.150 CI[0.057,0.243] (bf 0.590 vs twin 0.440). On WIQA's
    GIVEN process order the twin ties (+0.013 n.s.) -- that given order is a position artifact both exploit.
  * The store is a rung-1.5 STRUCTURAL PRIOR / edge-HYPOTHESIS source (direction cap ~0.61 intrinsic), NOT a scorer.
  * THE LIVE CONSUMER: situation_reader `sm.causal_reasoner()` lazily builds a CausalGraph over `sm.causal_links` ONLY
    -- NO store edges. `sm.causal_links` is produced by hdlab.causal_network (6 connectives + a 36-word hard-coded
    force-dynamics BRIDGE lexicon + adjacency fallback), so on UNMARKED prose it is SPARSE (median chain depth 0 on
    ROCStories; only 3.2% of stories support a >=2-hop chain -- audit 2026-09-06). The reasoner has little to walk.

THE FULL-STACK-UPSTREAM THESIS (owner directive):
  END component = the rung-2 do-sim necessity read (BF_SPIRIT, verified Pearl do-surgery + Trabasso reachability).
  Its INPUT = the bound causal graph. Signal on that input is LOST upstream because the graph is built from a
  connective+36-word-hard-coded-bridge extraction that misses UNMARKED narrative causation -- the exact links the
  1.29M-edge mined causal-TESTIMONY store exists to supply (Harris & Koenig 2006: causal knowledge is acquired from
  testimony). The hard-coded bridge lexicon is the NON-BF cheap stand-in; the store is its brain-foundational
  replacement, fed as candidate BYPASS edges into the REASONER graph (NOT into sm.causal_links -- that keeps the
  connective causal QA byte-identical, avoiding the -0.2079 plausibility-selector regression the mental-bridge SOLVED
  already located).

WHAT THIS CELL MEASURES (the reader's OWN extracted-from-prose read, NOT the WIQA gift-wrapped order):
  BASE graph = the reader's OWN extraction (hdlab.causal_network.build_causal_edges on the step sentences = the exact
  sm.causal_links mechanism), nodes = event verb LEMMAS. Necessity axis (effect vs no_effect) = reachability(Xnode,
  Ynode) under the do-simulation. Arms:
    * extracted_base        = the current LIVE behaviour (no store edges) -- the graph the reasoner has today.
    * extracted_plus_store  = THE WIRE: base + store bypass edges (edge_condXasym > thr) between graph-node lemmas.
    * extracted_plus_twin   = base + SHUFFLED-store bypass edges (info-free; MUST lose if the store is load-bearing).
    * (reference) storeonly / storeonly_twin = the instrument's proven +0.150 regime, recomputed here for anchoring.
  DIAGNOSTICS (the signal-loss trace): extraction density (nodes/edges/frac-with-any-link), and store COVERAGE on the
  single-lemma node space vs the rich span_concepts space (isolates the lemma-vs-concept lookup loss).

Glass-box, NO external LLM. Reuses load_wiqa / span_concepts / load_store / shuffle_store / edge_condXasym +
hdlab.causal_network (the live extractor) + hdlab.causal_reasoner.CausalGraph (the live reasoner).
Run: .venv/Scripts/python.exe experiments/exp_causal_store_wire_transfer_v1.py --run [--smoke]
# KB_REFERENT: data/corpora/wiqa/raw_official/dev_with_expl.jsonl
# KB_REFERENT: data/exp_causal_testimony_mine_v1/store_v1.json
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("measures live transfer of the mined causal-testimony store (structural prior) into the reader's OWN "
               "extracted-from-prose rung-2 necessity read; the store replaces the non-BF 36-word hard-coded bridge "
               "lexicon as the candidate-bypass-edge source (Harris-Koenig testimony), fed into the reasoner graph.")

import argparse
import json
import os
import sys
import time
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")   # determinism: orient_scramble iterates a set of frozensets
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.causal_reasoner import CausalGraph
from hdlab import causal_network as CN
from experiments.exp_causal_testimony_mine_v1 import span_concepts
from experiments.exp_causal_testimony_eval_v1 import load_store, shuffle_store
from experiments.exp_causal_directional_score_v1 import edge_condXasym
from experiments.exp_causal_wiqa_dosim_v1 import load_wiqa, polarity

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT = str(get_output_dir("exp_causal_store_wire_transfer_v1"))
STORE = os.path.join(_REPO, "data", "exp_causal_testimony_mine_v1", "store_v1.json")

_CC: Dict[str, List[str]] = {}


def _c(s):
    h = _CC.get(s)
    if h is None:
        h = span_concepts(s); _CC[s] = h
    return h


# ---------------------------------------------------------------------------
# THE READER'S OWN EXTRACTION -> a base CausalGraph over event verb LEMMAS (the live sm.causal_links mechanism)
# ---------------------------------------------------------------------------
def extract_base_graph(step_sents: List[str]) -> Tuple[CausalGraph, List[str]]:
    """Build the base CausalGraph exactly as the live `sm.causal_reasoner._graph()` does: run the reader's OWN causal
    extractor (hdlab.causal_network) over the prose, edges = connective/bridge cause->effect links (lemma nodes)."""
    g = CausalGraph()
    node_lemmas: List[str] = []
    for sent in step_sents:
        events, toks = CN.extract(sent)          # the reader's OWN event detector (temporal_model.extract_events)
        for e in events:
            if e.lemma not in node_lemmas:
                node_lemmas.append(e.lemma)
        edges, _tags = CN.build_causal_edges(events, toks)   # connective + 36-word hard-coded bridge (the live rule)
        for (c, o) in edges:
            if c != o:
                g.add_edge(c, o)
    for lm in node_lemmas:
        g.add_node(lm)
    return g, node_lemmas


def add_store_edges(g: CausalGraph, store, thr: float, concept_of=None) -> int:
    """THE WIRE: add store-hypothesized directed bypass edges between graph nodes. concept_of(node)->[concepts] lets a
    node be looked up by its richer concept set (the OPTIMIZATION arm); default = the bare lemma (the LIVE node space)."""
    nodes = sorted(g.nodes)
    added = 0
    for i, a in enumerate(nodes):
        ca = concept_of(a) if concept_of else [a]
        for b in nodes:
            if a == b:
                continue
            cb = concept_of(b) if concept_of else [b]
            best = 0.0
            for x in ca:
                for y in cb:
                    v = edge_condXasym(store, x, y)
                    if v > best:
                        best = v
            if best > thr:
                if b not in g.fwd.get(a, {}):
                    added += 1
                g.add_edge(a, b, polarity=1, necessity=min(1.0, 0.5 + best))
    return added


def storeonly_graph(concepts: List[str], store, thr: float) -> CausalGraph:
    """The instrument's proven KNOWLEDGE-TEST regime: graph from the MINED STORE ONLY over the item's concepts."""
    g = CausalGraph()
    cs = list(set(concepts))
    for a in cs:
        for b in cs:
            if a == b:
                continue
            v = edge_condXasym(store, a, b)
            if v > thr:
                g.add_edge(a, b, polarity=1, necessity=min(1.0, 0.5 + v))
    return g


def _map_node(phrase_c: List[str], node_lemmas: List[str]) -> str:
    """Map an X/Y phrase to the best-overlapping extracted event lemma (else '')."""
    pcs = set(phrase_c)
    best, bo = "", 0
    for lm in node_lemmas:
        ov = 1 if lm in pcs else 0
        if ov > bo:
            bo, best = ov, lm
    return best


def reach_effect(g: CausalGraph, nodeX: str, nodeY: str, store, X, Y, thr: float, fallback_store=None) -> str:
    """do(X): is Y reachable from X under the simulated intervention? The store/twin arms fall back to a direct
    store/twin edge when a phrase is unmapped (exogenous perturbation) -- mirrors the instrument's bf_dosim_decision.
    The BASE arm passes fallback_store=None (no store at all) and abstains -> no_effect, so base-vs-store is a fair
    'graph with vs without store' contrast, not a hidden store fallback."""
    if nodeX and nodeY and nodeX in g.nodes and nodeY in g.nodes:
        return "effect" if g.reachable(nodeX, nodeY) else "no_effect"
    if fallback_store is None:
        return "no_effect"
    best = 0.0
    for x in X:
        for y in Y:
            v = edge_condXasym(fallback_store, x, y)
            if v > best:
                best = v
    return "effect" if best > thr else "no_effect"


def concept_bound_graph(SC: List[List[str]], store, thr: float, chain: bool = False) -> CausalGraph:
    """THE UPSTREAM BF FIX (phase-diagram move on node granularity): one event node PER step, BOUND to its concept set
    (verb + noun arguments = the situation-model instantiation the causal chain-trace named MISSING), store bypass edges
    (condXasym over the bound concept sets) between steps. `chain` optionally adds the reading-order s_k->s_{k+1} edges.
    This is the store-only KNOWLEDGE regime lifted onto concept-BOUND step nodes (vs the live bare-verb-lemma nodes)."""
    g = CausalGraph()
    n = len(SC)
    for k in range(n):
        g.add_node("s%d" % k)
    if chain:
        for k in range(n - 1):
            g.add_edge("s%d" % k, "s%d" % (k + 1), polarity=1, necessity=1.0)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            best = 0.0
            for x in SC[i]:
                for y in SC[j]:
                    v = edge_condXasym(store, x, y)
                    if v > best:
                        best = v
            if best > thr:
                g.add_edge("s%d" % i, "s%d" % j, polarity=1, necessity=min(1.0, 0.5 + best))
    return g


def _map_step(phrase_c: List[str], SC: List[List[str]]) -> str:
    pcs = set(phrase_c); best, bo = "", 0
    for i, sc in enumerate(SC):
        ov = len(pcs & set(sc))
        if ov > bo:
            bo, best = ov, "s%d" % i
    return best


def undirected_reachable(g: CausalGraph, a: str, b: str) -> bool:
    """Connectivity ignoring edge DIRECTION (fwd + bwd neighbours). If directed reachability == this, the graph's
    DIRECTION content is inert on the existence axis (research control A: existence axis is direction-insensitive)."""
    if a == b:
        return a in g.nodes
    from collections import deque
    seen = {a}; dq = deque([a])
    while dq:
        cur = dq.popleft()
        nbrs = set(g.fwd.get(cur, {})) | set(g.bwd.get(cur, {}))
        for nx in nbrs:
            if nx == b:
                return True
            if nx not in seen:
                seen.add(nx); dq.append(nx)
    return False


def orient_scramble(g: CausalGraph, seed: int) -> CausalGraph:
    """Direction-scramble that HOLDS THE UNDIRECTED SKELETON FIXED (research control B, the decisive direction null):
    for each undirected edge {a,b}, pick a random orientation. Same skeleton, same edge count -> if cbound ties this,
    the topology residual is UNDIRECTED connectivity, not the store's DIRECTION."""
    import numpy as np
    rng = np.random.default_rng(seed)
    und = set()
    for a in g.fwd:
        for b in g.fwd[a]:
            und.add(frozenset((a, b)) if a != b else None)
    und.discard(None)
    T = CausalGraph()
    for n in g.nodes:
        T.add_node(n)
    for e in und:
        a, b = tuple(e) if len(e) == 2 else (list(e)[0], list(e)[0])
        if rng.random() < 0.5:
            T.add_edge(a, b)
        else:
            T.add_edge(b, a)
    return T


def run(smoke: bool = False, cap: int = 6000, thr: float = 0.0) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    store = load_store(STORE); twin = shuffle_store(store, seed=101)
    items = load_wiqa(300 if smoke else cap)
    prior = Counter(it["gold"] for it in items); majority = prior.most_common(1)[0][0]

    rows = []
    dens_nodes = []; dens_edges = []; n_any_link = 0
    n_store_crossedge = 0; n_lemma_pairs = 0; n_lemma_pairs_covered = 0
    n_concept_pairs = 0; n_concept_pairs_covered = 0; n_cb_graph = 0; n_same_step = 0
    cb_edges_real = []; cb_edges_gtwin = []; cb_pred_eff = 0; cb_tw_pred_eff = 0; cb_topotw_pred_eff = 0
    for it in items:
        X = _c(it["X"]); Y = _c(it["Y"]); steps = it["steps"]
        SC = [_c(s) for s in steps]
        # -- the reader's OWN extraction (base graph over lemma nodes) --
        base, node_lemmas = extract_base_graph(steps)
        dens_nodes.append(len(base.nodes)); dens_edges.append(base.n_edges())
        n_any_link += (1 if base.n_edges() > 0 else 0)
        nodeX = _map_node(X, node_lemmas); nodeY = _map_node(Y, node_lemmas)

        # -- arm graphs --
        g_store = CausalGraph(); g_twin = CausalGraph()
        for a in base.fwd:
            for b, pol in base.fwd[a].items():
                g_store.add_edge(a, b, pol); g_twin.add_edge(a, b, pol)
        for n in base.nodes:
            g_store.add_node(n); g_twin.add_node(n)
        added = add_store_edges(g_store, store, thr)
        add_store_edges(g_twin, twin, thr)
        n_store_crossedge += (1 if added > 0 else 0)

        # -- store COVERAGE trace: lemma-pair vs concept-pair (isolates the single-lemma lookup loss) --
        lset = sorted(base.nodes)
        for i in range(len(lset)):
            for j in range(len(lset)):
                if i == j:
                    continue
                n_lemma_pairs += 1
                if edge_condXasym(store, lset[i], lset[j]) > thr:
                    n_lemma_pairs_covered += 1
        allc = list(set(c for sc in SC for c in sc))
        for i in range(len(allc)):
            for j in range(len(allc)):
                if i == j:
                    continue
                n_concept_pairs += 1
                if edge_condXasym(store, allc[i], allc[j]) > thr:
                    n_concept_pairs_covered += 1

        # -- reference storeonly regime (the proven +0.150; flat concept bag) --
        allconcepts = list(set(X + Y + [c for sc in SC for c in sc]))
        gso = storeonly_graph(allconcepts, store, thr)
        gso_tw = storeonly_graph(allconcepts, twin, thr)
        # -- THE UPSTREAM BF FIX arm: concept-BOUND step nodes (the phase-diagram node-granularity move) --
        gcb = concept_bound_graph(SC, store, thr); gcb_tw = concept_bound_graph(SC, twin, thr)
        sX = _map_step(X, SC); sY = _map_step(Y, SC)

        eff_gold = "effect" if it["gold"] in ("more", "less") else "no_effect"
        # ALL arms are PURE rung-2 do-simulation reads: reachability over the graph, abstain->no_effect when a phrase
        # is unmapped (fallback_store=None). No direct store-edge lookup -> no store-as-scorer (rung-1.5) shortcut can
        # sneak the store in outside the reasoner graph. The store's contribution is ONLY the bypass edges it adds.
        e_base = reach_effect(base, nodeX, nodeY, store, X, Y, thr, fallback_store=None)   # NO store (current live)
        e_store = reach_effect(g_store, nodeX, nodeY, store, X, Y, thr, fallback_store=None)
        e_twin = reach_effect(g_twin, nodeX, nodeY, twin, X, Y, thr, fallback_store=None)
        # storeonly reads over concept nodes directly (X-concept reaches Y-concept)
        e_so = _storeonly_read(gso, X, Y)
        e_so_tw = _storeonly_read(gso_tw, X, Y)                       # GLOBAL-shuffle twin (density-DIFF)
        gso_topotw = gso.shuffled(seed=101) if gso.n_edges() > 0 else gso   # density-MATCHED topology twin
        e_so_topotw = _storeonly_read(gso_topotw, X, Y)
        # storeonly MAP_ONLY degenerate: effect iff some X-concept AND some Y-concept are BOTH store-graph nodes
        e_so_map = "effect" if (set(X) & gso.nodes) and (set(Y) & gso.nodes) else "no_effect"
        # concept-bound step-node necessity (map X/Y to the best-overlap step, then PURE graph reachability)
        e_cb = reach_effect(gcb, sX, sY, store, X, Y, thr, fallback_store=None)
        e_cb_tw = reach_effect(gcb_tw, sX, sY, twin, X, Y, thr, fallback_store=None)   # GLOBAL-shuffle twin (density-DIFF)
        # -- CONTROL BATTERY (understand the surprising +0.22) --
        # (a) DENSITY-MATCHED TOPOLOGY twin: the causal_reasoner's OWN shuffled() -- same nodes + SAME edge count,
        #     random acyclic rewire. Isolates TOPOLOGY/DIRECTION from per-item DENSITY (the global-shuffle twin under-
        #     connects small concept sets). THIS is the honest info-free twin for a per-item store-edged graph.
        gcb_topotw = gcb.shuffled(seed=101) if gcb.n_edges() > 0 else gcb
        e_cb_topotw = reach_effect(gcb_topotw, sX, sY, None, X, Y, thr, fallback_store=None)
        # (b) MAPPING-ONLY degenerate: predict effect iff BOTH endpoints map to a step (no edges consulted at all).
        #     If this already scores ~cbound, the win is the X/Y->step mapping, not store reachability.
        e_map = "effect" if (sX and sY) else "no_effect"
        # (c) UNDIRECTED-CONNECTIVITY ablation: same graph, ignore edge DIRECTION. cbound==this => direction inert.
        if sX and sY and sX in gcb.nodes and sY in gcb.nodes:
            e_cb_und = "effect" if undirected_reachable(gcb, sX, sY) else "no_effect"
        else:
            e_cb_und = "no_effect"
        # (d) DIRECTION-SCRAMBLE (skeleton fixed): random per-edge orientation. cbound==this => residual is UNDIRECTED
        #     topology, NOT the store's direction (the decisive direction null).
        gcb_dir = orient_scramble(gcb, seed=101) if gcb.n_edges() > 0 else gcb
        e_cb_dir = reach_effect(gcb_dir, sX, sY, None, X, Y, thr, fallback_store=None)
        n_cb_graph += 1 if (sX and sY) else 0
        n_same_step += 1 if (sX and sY and sX == sY) else 0
        cb_edges_real.append(gcb.n_edges()); cb_edges_gtwin.append(gcb_tw.n_edges())
        cb_pred_eff += 1 if e_cb == "effect" else 0; cb_tw_pred_eff += 1 if e_cb_tw == "effect" else 0
        cb_topotw_pred_eff += 1 if e_cb_topotw == "effect" else 0
        rows.append({
            "gold": eff_gold,
            "base": 1.0 if e_base == eff_gold else 0.0,
            "store": 1.0 if e_store == eff_gold else 0.0,
            "twin": 1.0 if e_twin == eff_gold else 0.0,
            "storeonly": 1.0 if e_so == eff_gold else 0.0,
            "storeonly_twin": 1.0 if e_so_tw == eff_gold else 0.0,
            "storeonly_topotwin": 1.0 if e_so_topotw == eff_gold else 0.0,
            "storeonly_maponly": 1.0 if e_so_map == eff_gold else 0.0,
            "cbound": 1.0 if e_cb == eff_gold else 0.0,
            "cbound_twin": 1.0 if e_cb_tw == eff_gold else 0.0,
            "cbound_topotwin": 1.0 if e_cb_topotw == eff_gold else 0.0,
            "cbound_undirected": 1.0 if e_cb_und == eff_gold else 0.0,
            "cbound_dirscramble": 1.0 if e_cb_dir == eff_gold else 0.0,
            "map_only": 1.0 if e_map == eff_gold else 0.0,
            "majority": 1.0 if (("effect" if majority in ("more", "less") else "no_effect") == eff_gold) else 0.0,
        })

    out = {
        "smoke": smoke, "n": len(rows), "thr": thr, "class_prior": dict(prior), "majority": majority,
        "extraction_density": {
            "avg_nodes": round(float(np.mean(dens_nodes)), 2), "avg_edges": round(float(np.mean(dens_edges)), 2),
            "median_edges": float(np.median(dens_edges)),
            "frac_items_with_any_causal_link": round(n_any_link / max(1, len(rows)), 3),
            "frac_items_with_store_crossedge": round(n_store_crossedge / max(1, len(rows)), 3),
            "frac_cbound_graph_read": round(n_cb_graph / max(1, len(rows)), 3)},
        "store_coverage_trace": {
            "lemma_pair_coverage": round(n_lemma_pairs_covered / max(1, n_lemma_pairs), 4),
            "concept_pair_coverage": round(n_concept_pairs_covered / max(1, n_concept_pairs), 4),
            "note": "lemma_pair = the LIVE node space (single verb lemmas); concept_pair = the instrument's rich "
                    "span_concepts space. A big gap => the single-lemma lookup is where the store signal leaks."},
        "necessity_effect_vs_noeffect": {
            "extracted_base": _boot([r["base"] for r in rows]),
            "extracted_plus_store": _boot([r["store"] for r in rows]),
            "extracted_plus_twin": _boot([r["twin"] for r in rows]),
            "majority": _boot([r["majority"] for r in rows]),
            "paired_store_minus_twin": _paired([r["store"] for r in rows], [r["twin"] for r in rows]),
            "paired_store_minus_base": _paired([r["store"] for r in rows], [r["base"] for r in rows])},
        "reference_storeonly_regime": {
            "storeonly": _boot([r["storeonly"] for r in rows]),
            "storeonly_globaltwin": _boot([r["storeonly_twin"] for r in rows]),
            "storeonly_topotwin": _boot([r["storeonly_topotwin"] for r in rows]),
            "storeonly_maponly": _boot([r["storeonly_maponly"] for r in rows]),
            "paired_storeonly_minus_globaltwin": _paired([r["storeonly"] for r in rows], [r["storeonly_twin"] for r in rows]),
            "paired_storeonly_minus_topotwin": _paired([r["storeonly"] for r in rows], [r["storeonly_topotwin"] for r in rows]),
            "paired_storeonly_minus_maponly": _paired([r["storeonly"] for r in rows], [r["storeonly_maponly"] for r in rows]),
            "note": "the brief's +0.139 headline regime, re-examined against the HONEST density-matched topotwin + the "
                    "map_only degenerate. If storeonly ties/loses topotwin or map_only, the +0.139 was itself a density/"
                    "topicality artifact of the global-shuffle twin (disk-outranks-brief on the store's own headline)."},
        "upstream_fix_concept_bound_step_nodes": {
            "cbound": _boot([r["cbound"] for r in rows]),
            "cbound_globaltwin": _boot([r["cbound_twin"] for r in rows]),
            "cbound_topotwin": _boot([r["cbound_topotwin"] for r in rows]),
            "cbound_undirected": _boot([r["cbound_undirected"] for r in rows]),
            "cbound_dirscramble": _boot([r["cbound_dirscramble"] for r in rows]),
            "map_only": _boot([r["map_only"] for r in rows]),
            "paired_cbound_minus_globaltwin": _paired([r["cbound"] for r in rows], [r["cbound_twin"] for r in rows]),
            "paired_cbound_minus_topotwin": _paired([r["cbound"] for r in rows], [r["cbound_topotwin"] for r in rows]),
            "paired_cbound_minus_undirected": _paired([r["cbound"] for r in rows], [r["cbound_undirected"] for r in rows]),
            "paired_cbound_minus_dirscramble": _paired([r["cbound"] for r in rows], [r["cbound_dirscramble"] for r in rows]),
            "paired_cbound_minus_maponly": _paired([r["cbound"] for r in rows], [r["map_only"] for r in rows]),
            "note": "THE UPSTREAM BF FIX + CONTROL BATTERY. cbound = concept-bound step nodes + real store bypass edges. "
                    "globaltwin = global shuffle_store (density-DIFFERENT, under-connects small sets). topotwin = the "
                    "causal_reasoner's OWN shuffled() (density-MATCHED, topology destroyed) = the HONEST twin. map_only "
                    "= predict effect iff both endpoints map (no edges). The store transfers ONLY if cbound beats "
                    "TOPOTWIN and MAP_ONLY CI-sep."},
        "control_diagnostics": {
            "frac_same_step": round(n_same_step / max(1, len(rows)), 3),
            "avg_edges_real": round(float(np.mean(cb_edges_real)), 2),
            "avg_edges_globaltwin": round(float(np.mean(cb_edges_gtwin)), 2),
            "pred_effect_rate_cbound": round(cb_pred_eff / max(1, len(rows)), 3),
            "pred_effect_rate_globaltwin": round(cb_tw_pred_eff / max(1, len(rows)), 3),
            "pred_effect_rate_topotwin": round(cb_topotw_pred_eff / max(1, len(rows)), 3),
            "gold_effect_rate": round(sum(1 for r in rows if r["gold"] == "effect") / max(1, len(rows)), 3),
            "note": "if avg_edges_globaltwin << avg_edges_real, the global twin's loss is a per-item DENSITY artifact "
                    "(why the density-matched topotwin is the honest control). pred_effect_rate vs gold_effect_rate "
                    "exposes base-rate gaming."},
    }
    ne = out["necessity_effect_vs_noeffect"]; rs = out["reference_storeonly_regime"]; ed = out["extraction_density"]
    ct = out["store_coverage_trace"]; cb = out["upstream_fix_concept_bound_step_nodes"]; cd = out["control_diagnostics"]
    out["headline"] = (
        "STORE-WIRE TRANSFER n=%d thr=%.2f | extraction avg_nodes %.1f avg_edges %.1f frac_any_link %.2f | coverage "
        "lemma %.4f vs concept %.4f || LIVE-LEMMA-NODE: base %.3f +store %.3f +twin %.3f paired(store-base) %+.4f%s || "
        "CONCEPT-BOUND: cbound %.3f%s | globaltwin %.3f (paired %+.4f%s) | TOPOtwin %.3f (paired %+.4f%s) | UNDIRECTED "
        "%.3f (paired %+.4f%s) | DIRSCRAMBLE %.3f (paired %+.4f%s) | map_only %.3f (paired %+.4f%s) || DENSITY "
        "real_edges %.1f vs gtwin_edges %.1f | pred_eff cb %.2f gold_eff %.2f same_step %.2f || REF storeonly %.3f vs "
        "topotwin %.3f (+%.4f%s)" % (
            out["n"], thr, ed["avg_nodes"], ed["avg_edges"], ed["frac_items_with_any_causal_link"],
            ct["lemma_pair_coverage"], ct["concept_pair_coverage"],
            ne["extracted_base"]["acc"], ne["extracted_plus_store"]["acc"], ne["extracted_plus_twin"]["acc"],
            ne["paired_store_minus_base"]["delta"], ne["paired_store_minus_base"]["ci"],
            cb["cbound"]["acc"], cb["cbound"]["ci"], cb["cbound_globaltwin"]["acc"],
            cb["paired_cbound_minus_globaltwin"]["delta"], cb["paired_cbound_minus_globaltwin"]["ci"],
            cb["cbound_topotwin"]["acc"], cb["paired_cbound_minus_topotwin"]["delta"], cb["paired_cbound_minus_topotwin"]["ci"],
            cb["cbound_undirected"]["acc"], cb["paired_cbound_minus_undirected"]["delta"], cb["paired_cbound_minus_undirected"]["ci"],
            cb["cbound_dirscramble"]["acc"], cb["paired_cbound_minus_dirscramble"]["delta"], cb["paired_cbound_minus_dirscramble"]["ci"],
            cb["map_only"]["acc"], cb["paired_cbound_minus_maponly"]["delta"], cb["paired_cbound_minus_maponly"]["ci"],
            cd["avg_edges_real"], cd["avg_edges_globaltwin"], cd["pred_effect_rate_cbound"],
            cd["gold_effect_rate"], cd["frac_same_step"],
            rs["storeonly"]["acc"], rs["storeonly_topotwin"]["acc"], rs["paired_storeonly_minus_topotwin"]["delta"],
            rs["paired_storeonly_minus_topotwin"]["ci"]))
    out["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(OUT, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT, "metrics.json"))
    print("[run] " + out["headline"], flush=True)
    return out


def _storeonly_read(g: CausalGraph, X, Y) -> str:
    for x in set(X):
        for y in set(Y):
            if x in g.nodes and y in g.nodes and g.reachable(x, y):
                return "effect"
    return "no_effect"


def _boot(hits, seed=17, n_boot=4000):
    a = np.array(hits, float)
    if len(a) < 3:
        return {"acc": float("nan"), "ci": [float("nan"), float("nan")], "n": int(len(a))}
    r = np.random.default_rng(seed)
    bs = [a[r.integers(0, len(a), len(a))].mean() for _ in range(n_boot)]
    return {"acc": round(float(a.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "n": int(len(a))}


def _paired(h1, h2, seed=23, n_boot=4000):
    d = np.array(h1, float) - np.array(h2, float)
    r = np.random.default_rng(seed)
    bs = [d[r.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    return {"delta": round(float(d.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--thr", type=float, default=0.0)
    a = ap.parse_args(argv)
    if a.self_test or a.smoke:
        run(smoke=True, thr=a.thr); print("SELFTEST PASS", flush=True); return 0
    run(thr=a.thr); return 0


if __name__ == "__main__":
    sys.exit(main())
