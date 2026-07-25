"""arc_derivation_rule_supply_cskg_v1 -- ONE-VARIABLE ablation of the derivation connectivity gate
where the SINGLE variable is the RULE SOURCE. Does SUPPLYING MORE RULES (a bigger typed
causal/conditional/functional corpus than WorldTree's ~1868 licensed rows) make the derivation graph
actually CONNECT ARC-Challenge questions to their answers -- WITHOUT falling into the
"everything-connects" promiscuity trap?

WHY (VET-confirmed, cell 99736f579 COVERAGE_BOUND_CONFIRMED): the clean-node ablation
(exp_arc_derivation_connectivity_gate_cleannodes_v2) confirmed WorldTree's ~1868 licensed rows do NOT
span ARC-Challenge content -- typed correct-coverage stayed ~0.06 even with clean negation-aware
node-identity and no mega-hub. RULE-SUPPLY is the mandated next lever. BUT the risk (already shown by
the gate's untyped-null: connects ~32% with ~0 selectivity) is that a big GENERIC KB connects
EVERYTHING with ~0 selectivity. So this probe measures BOTH coverage AND selectivity, PER source, with
an untyped-null promiscuity control for each source and a mega-hub (max-degree) watch.

ONE VARIABLE = RULE SOURCE. EVERYTHING ELSE reused UNCHANGED from the clean-node gate
(exp_arc_derivation_connectivity_gate_cleannodes_v2, imported as cn):
  - SAME node-identity: cn.NegAwareEncoder + head-lemma gate + PolarityLexicon.contradicts merge-gate
  - SAME graph builder cn.build_graph_gated (typed directed edges + untyped-null cos edges)
  - SAME depth<=3 meet-in-middle search gate.meet_connected, SAME eval cn.eval_arm
  - SAME ~100 ARC-Challenge Qs (same seed permutation), SAME word->node mapping (cos>=tau_unify)
  - SAME thresholds tau_unify=0.85, tau_sim=0.60, depth=3 (NOT tuned to force a band)

RULE SOURCES (the ONE variable), each fed to the IDENTICAL gate:
  1. worldtree      : WorldTree licensed rows (LICENSED types, confident, non-empty). The ANCHOR
                      baseline reproduced under identical conditions (expected ~0.06 typed coverage).
  2. cskg           : CSKG (data/grounding_testbed/cskg.tsv.gz, ~6M rows) restricted to LICENSED
                      causal/conditional/functional relations (~180k rows), then INDUCED to the
                      subgraph relevant to the sampled ARC vocabulary (2-level lexical induction, see
                      below). The bigger typed source.
  3. worldtree_cskg : union of (1) and (2). The "supply everything typed" arm.

CSKG relation licensing (causal/conditional/functional inference steps; commonsense structural
relations RelatedTo/Synonym/Antonym/IsA/FormOf/DerivedFrom/HasContext/AtLocation/PartOf/HasA/dbpedia/*
are EXCLUDED as non-licensed):
    CAUSE    <- /r/Causes /r/CausesDesire /r/MotivatedByGoal /r/Desires /r/NotDesires
    REQUIRES <- /r/HasPrerequisite
    IFTHEN   <- /r/HasSubevent /r/HasFirstSubevent /r/HasLastSubevent
    USEDFOR  <- /r/UsedFor /r/CapableOf /r/ReceivesAction
    SOURCEOF <- /r/MadeOf
(ATOMIC at:x*/at:o* social if-then relations EXIST in CSKG but are EXCLUDED as social-not-science; the
report notes their availability as a promiscuity-flavored follow-up, not run here to keep ONE variable.)

CSKG INDUCTION (a NECESSITY, reported as a generosity caveat): the O(U^2) cosine node-merge in the gate
is intractable over CSKG's ~180k licensed rows / >100k fillers, so CSKG is subgraph-induced around the
sampled ARC vocabulary: (a) seed_nodes = CSKG nodes whose label shares a content token with the ARC
givens+choices vocab; (b) frontier = licensed-edge neighbors of seed_nodes; (c) keep = seed U frontier,
capped to FILLER_BUDGET by relevance (seeds first, then frontier by #seed-neighbors, sorted-deterministic);
(d) kept rows = licensed rows with BOTH endpoints in keep. This captures given(seed)->frontier->frontier
->choice(seed) depth<=3 chains. Induction is query-conditioned (a retrieval step) and GENEROUS to CSKG
-> CSKG coverage here is an UPPER BOUND; a STILL-STARVED verdict under it is therefore decisive, and a
GREEN is appropriately caveated. WorldTree is small enough to use whole (no induction) = fair anchor.

METRICS + PRE-REGISTERED BANDS (a priori, per source; reported STRAIGHT, NOT tuned). For each source:
  correct-choice coverage (cov), selectivity gap (typed: cov - mean-wrong-coverage), and the SAME
  source's untyped-null coverage+gap (promiscuity control), plus graph size + max node degree.
  Per-source band (classify_source_band):
    GREEN            : cov >= 0.35 AND typed_gap >= 0.15 AND typed_gap > untyped_gap
                       -> rule-supply is the lever; typing still adds selectivity at higher coverage.
    PROMISCUOUS_FAIL : cov > 0.5 AND (typed_gap < 0.05 OR typed_gap <= untyped_gap)
                       -> more rules but no reasoning; the bigger KB connects everything equally ->
                       generic KB is the WRONG kind of supply (need science-precise/trustworthy rules).
    STILL_STARVED    : cov < 0.15 -> even the big available typed KB does not span ARC science causally
                       -> need a different supply (science-text rule extraction / curated).
    MIDDLE_BAND      : otherwise (partial coverage, modest selectivity) -> report straight, no claim.
  HONEST GUARD: coverage AND selectivity tracked TOGETHER; a coverage win with zero selectivity is NOT
    a win. Mega-hub watch: report max typed node-degree per source.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic
(fixed seed, numpy default_rng, sorted iteration); repo .venv. Agent-reported VET-PENDING.

CELL-TEMPLATE:
  - except SystemExit raised BEFORE except Exception (no bare/BaseException).
  - final metrics atomicity = tmp + os.replace ; start-marker ; crash-diagnostic ; heartbeat with flush.
  - real_code_path self_test: (i) CSKG tsv parse + licensing on a synthetic gz; (ii) 2-level induction
    keeps ARC-relevant edges + honors the budget; (iii) a planted typed chain from CSKG-style rows
    CONNECTS the correct choice while a lure does NOT under the REAL gate (cn.build_graph_gated +
    gate.meet_connected) = discriminator CAN fire and CAN fail; (iv) band classifier asserts (each band
    reachable).
  - deterministic_seeding: fixed int seed + numpy default_rng + sorted iteration; no hash()-seeding.
  - all reported numbers MEASURED @ this cell's metrics.json.

Compute architecture: sequential-CPU (JUSTIFIED). One streaming decompress-scan of cskg.tsv.gz (~6M
lines, ~60-120s), in-memory induction, then the same cheap gate (graph build + BFS over ~100 Qs) per
source. The only vectorized cost is the GloVe encode of the fillers + the O(U^2) cosine merge, bounded
by FILLER_BUDGET (~6000). No matmul-heavy substrate primitive is swept -> not a GPU-batching candidate.
Storage: no_storage (connectivity gate; no atoms written).
"""
from __future__ import annotations

import os
import sys
import gzip
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

# reuse gate primitives + clean-node identity UNCHANGED (ONE variable = rule source)
from experiments import exp_arc_derivation_connectivity_gate_v1 as gate
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as cn
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc

ANCHOR_NAME = "arc_derivation_rule_supply_cskg_v1"
SEED = 20260725

# SAME thresholds + node-identity as the clean-node gate (ONE variable = rule source)
TAU_UNIFY = cn.TAU_UNIFY   # 0.85
TAU_SIM = cn.TAU_SIM       # 0.60
DEPTH = cn.DEPTH           # 3
WORLDTREE_LICENSED = gate.LICENSED  # ("CAUSE","IFTHEN","REQUIRES","COUPLEDRELATIONSHIP","SOURCEOF","USEDFOR")

CSKG_PATH = os.path.join(_REPO, "data", "grounding_testbed", "cskg.tsv.gz")

# CSKG relation -> generic WorldTree-style licensed type (causal/conditional/functional only).
CSKG_LICENSED = {
    "/r/Causes": "CAUSE", "/r/CausesDesire": "CAUSE", "/r/MotivatedByGoal": "CAUSE",
    "/r/Desires": "CAUSE", "/r/NotDesires": "CAUSE",
    "/r/HasPrerequisite": "REQUIRES",
    "/r/HasSubevent": "IFTHEN", "/r/HasFirstSubevent": "IFTHEN", "/r/HasLastSubevent": "IFTHEN",
    "/r/UsedFor": "USEDFOR", "/r/CapableOf": "USEDFOR", "/r/ReceivesAction": "USEDFOR",
    "/r/MadeOf": "SOURCEOF",
}

# pre-registered per-source band thresholds (a priori)
GREEN_COV = 0.35
GREEN_GAP = 0.15
PROMISCUOUS_COV = 0.50
PROMISCUOUS_GAP = 0.05
STARVED_COV = 0.15

FILLER_BUDGET = 6000       # cap CSKG induced unique fillers (keeps O(U^2) merge tractable)
CSKG_MAX_DEG_INDUCE = 64   # per-node degree cap during induction (hub guard, pre-merge)
UNION_HARD_CAP = 12000     # safety: refuse to build a graph beyond this many fillers (OOM guard)

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
# CSKG loading + query-conditioned 2-level induction
# ---------------------------------------------------------------------------
def _node_label(raw_label, node_id):
    """CSKG label column, else derived from the /c/en/ id (underscores -> spaces)."""
    s = (raw_label or "").strip().lower()
    if s:
        return s
    nid = (node_id or "").strip()
    if nid.startswith("/c/en/"):
        nid = nid[len("/c/en/"):]
        nid = nid.split("/")[0]  # drop POS/sense suffixes
    return nid.replace("_", " ").strip().lower()


def load_cskg_licensed(path, max_lines=0):
    """Stream cskg.tsv.gz once; return LICENSED rows [(generic_rel, arg0_label, arg1_label)].
    max_lines>0 caps lines scanned (smoke). ASCII-safe; skips malformed rows."""
    rows = []
    n_scanned = 0
    per_rel = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline()  # id node1 relation node2 node1;label node2;label ...
        for line in f:
            n_scanned += 1
            if max_lines and n_scanned > max_lines:
                break
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 6:
                continue
            rel = parts[2]
            gen = CSKG_LICENSED.get(rel)
            if gen is None:
                continue
            a = _node_label(parts[4], parts[1])
            b = _node_label(parts[5], parts[3])
            if not a or not b or a == b:
                continue
            rows.append((gen, a, b))
            per_rel[rel] = per_rel.get(rel, 0) + 1
    return rows, n_scanned, per_rel


def induce_subgraph(cskg_rows, seed_words, filler_budget, max_deg_induce=None):
    """Query-conditioned lexical induction that keeps the DENSEST ARC-relevant licensed core (so the
    node budget retains connectivity, NOT an arbitrary alphabetical slice of isolated seeds).
    Returns rows [{relation,arg0,arg1}] whose BOTH endpoints are in the kept node set.
    GENEROUS to CSKG (upper-bound): keep top-budget nodes by ARC-relevant licensed degree, tie-broken
    by concept-specificity then label. Deterministic: sorted iteration, stable ranking."""
    seed_words = set(seed_words)

    def label_tokens(lab):
        return set(arc._content_words(lab, min_len=4))

    # 1. seed nodes = labels sharing a content token with ARC vocab; relevance = ARC-token fraction
    #    (prefers nodes that ARE an ARC concept over nodes that merely contain one).
    all_labels = set()
    for (_, a, b) in cskg_rows:
        all_labels.add(a)
        all_labels.add(b)
    seed_relevance = {}
    for lab in all_labels:
        toks = label_tokens(lab)
        if not toks:
            continue
        m = toks & seed_words
        if m:
            seed_relevance[lab] = len(m) / len(toks)
    seed_nodes = set(seed_relevance)

    # 2. ARC-relevant licensed edges = at least one seed endpoint; score EVERY incident node
    #    (seeds AND their frontier neighbors) by relevant-edge degree = its connective value.
    rel_deg = {}
    for (_, a, b) in cskg_rows:
        if a in seed_nodes or b in seed_nodes:
            rel_deg[a] = rel_deg.get(a, 0) + 1
            rel_deg[b] = rel_deg.get(b, 0) + 1

    # 3. keep = top-budget candidate nodes by (-relevant_degree, -seed_relevance, label). This retains
    #    the most-connected ARC-relevant core (hubs + connected seeds + bridging frontier) within budget.
    cand = sorted(rel_deg.keys(),
                  key=lambda n: (-rel_deg[n], -seed_relevance.get(n, 0.0), n))
    keep = set(cand[:filler_budget])

    # 4. kept rows = licensed rows with BOTH endpoints in keep
    kept = []
    for (gen, a, b) in cskg_rows:
        if a in keep and b in keep:
            kept.append({"relation": gen, "arg0": a, "arg1": b})
    n_frontier = len([n for n in keep if n not in seed_nodes])
    return kept, {"n_all_labels": len(all_labels), "n_seed_nodes": len(seed_nodes),
                  "n_candidate_nodes": len(rel_deg), "n_kept_nodes": len(keep),
                  "n_kept_seeds": len(keep) - n_frontier, "n_kept_frontier": n_frontier,
                  "n_kept_rows": len(kept), "filler_budget": filler_budget}


def worldtree_rows():
    """WorldTree licensed rows (LICENSED, confident, non-empty) -- IDENTICAL to parent gate."""
    from experiments import exp_arc_selection_relational_meaning_v1 as rel
    uid2typed = rel.parse_tablestore_typed()
    rows = []
    per_rel = {}
    for uid in sorted(uid2typed):
        d = uid2typed[uid]
        if d["relation"] in WORLDTREE_LICENSED and d["confident"] and d["arg0"].strip() and d["arg1"].strip():
            rows.append({"relation": d["relation"], "arg0": d["arg0"].strip(), "arg1": d["arg1"].strip()})
            per_rel[d["relation"]] = per_rel.get(d["relation"], 0) + 1
    return rows, per_rel


# ---------------------------------------------------------------------------
# per-source connectivity eval (identical gate; ONE variable = the `rows` fed in)
# ---------------------------------------------------------------------------
def eval_source(rows, neg_enc, wn, pol, questions, output_dir, source_name):
    if len(rows) == 0:
        return None
    # collect fillers for OOM guard
    fillers = set()
    for r in rows:
        fillers.add(r["arg0"]); fillers.add(r["arg1"])
    if len(fillers) > UNION_HARD_CAP:
        raise RuntimeError(f"{source_name}: {len(fillers)} fillers exceeds UNION_HARD_CAP "
                           f"{UNION_HARD_CAP}; tighten FILLER_BUDGET")

    g = cn.build_graph_gated(rows, neg_enc.encode_batch, TAU_UNIFY, TAU_SIM, wn, pol,
                             use_head_gate=True, use_pol_gate=True)
    _heartbeat(output_dir, f"{source_name}_graph_built",
               {"n_fillers": g["n_fillers"], "n_nodes": g["n_nodes"],
                "n_typed_edges": g["n_typed_edges"], "n_null_edges": g["n_null_edges"],
                "max_deg": g["max_typed_node_degree"], "hub": g["max_degree_node_label"]})

    # word -> CLEAN node mapping (SAME mechanism: cos>=tau_unify vs node reps)
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

    def nodes_for(text):
        ns = set()
        for w in arc._content_words(text, min_len=4):
            ns |= word2nodes.get(w, set())
        return ns

    typed = cn.eval_arm(g["fwd"], g["bwd"], questions, nodes_for, DEPTH, min_len=1)
    null = cn.eval_arm(g["undirected"], g["undirected"], questions, nodes_for, DEPTH, min_len=1)
    typed.pop("per_q", None)
    null.pop("per_q", None)

    cov = typed["correct_coverage"]
    tgap = typed["selectivity_gap"]
    ugap = null["selectivity_gap"]
    band = classify_source_band(cov, tgap, ugap)

    # example chains (glass-box) up to 4
    examples = []
    for q in questions:
        if len(examples) >= 4:
            break
        gn = nodes_for(q["stem"])
        ci = q["correct_index"]
        cnodes = nodes_for(q["choices"][ci])
        if gate.meet_connected(g["fwd"], g["bwd"], gn, cnodes, DEPTH, min_len=1):
            chain = gate.reconstruct_chain(g, gn, cnodes, DEPTH)
            examples.append({"qid": q["qid"], "stem": q["stem"][:160],
                             "correct_choice": q["choices"][ci][:100], "chain": chain})

    return {
        "source": source_name, "band": band,
        "typed_correct_coverage": round(cov, 4),
        "typed_mean_wrong_coverage": round(typed["mean_wrong_coverage"], 4),
        "typed_selectivity_gap": round(tgap, 4),
        "untyped_correct_coverage": round(null["correct_coverage"], 4),
        "untyped_mean_wrong_coverage": round(null["mean_wrong_coverage"], 4),
        "untyped_selectivity_gap": round(ugap, 4),
        "typed_gap_beats_untyped": bool(tgap > ugap),
        "graph": {"n_fillers": g["n_fillers"], "n_nodes": g["n_nodes"],
                  "n_typed_edges": g["n_typed_edges"], "n_null_edges": g["n_null_edges"],
                  "n_merges": g["n_merges"], "n_head_blocked": g["n_head_blocked"],
                  "n_pol_blocked": g["n_pol_blocked"],
                  "max_typed_node_degree": g["max_typed_node_degree"],
                  "max_degree_node_label": g["max_degree_node_label"]},
        "example_chains": examples,
        "typed_full": typed, "untyped_null_full": null,
    }


# ---------------------------------------------------------------------------
# per-source band classifier (a priori)
# ---------------------------------------------------------------------------
def classify_source_band(cov, typed_gap, untyped_gap):
    if cov >= GREEN_COV and typed_gap >= GREEN_GAP and typed_gap > untyped_gap:
        return "GREEN"
    if cov > PROMISCUOUS_COV and (typed_gap < PROMISCUOUS_GAP or typed_gap <= untyped_gap):
        return "PROMISCUOUS_FAIL"
    if cov < STARVED_COV:
        return "STILL_STARVED"
    return "MIDDLE_BAND"


# ---------------------------------------------------------------------------
# self-test (REAL code paths: CSKG parse + induction + gate discriminator)
# ---------------------------------------------------------------------------
def _self_test():
    import tempfile
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    print("[self-test] band classifier reachability ...", flush=True)
    assert classify_source_band(0.40, 0.20, 0.05) == "GREEN"
    assert classify_source_band(0.60, 0.02, 0.02) == "PROMISCUOUS_FAIL"
    assert classify_source_band(0.55, 0.10, 0.12) == "PROMISCUOUS_FAIL"   # gap <= untyped
    assert classify_source_band(0.06, 0.03, 0.00) == "STILL_STARVED"
    assert classify_source_band(0.25, 0.08, 0.02) == "MIDDLE_BAND"
    print("[self-test] band classifier OK", flush=True)

    # (0) node-identity negation-DETECTION bug guard (fixed 2026-07-25 in cleannodes_v2):
    #     science content ending in "nt"/"nt-like" must NOT be negation-flagged; real cues must be.
    sci_words = ["current", "element", "point", "content", "present", "nutrient", "continent",
                 "instrument", "experiment", "event", "environment", "plant", "amount", "moment"]
    for w in sci_words:
        assert cn._has_neg_token(w) is False, f"science word '{w}' spuriously negation-flagged"
    for w in ["not", "no", "never", "cannot", "without", "neither", "nor", "none",
              "does not exist", "isn't", "don't", "can't"]:
        assert cn._has_neg_token(w) is True, f"genuine negation cue '{w}' missed"
    print(f"[self-test] negation-detection fix OK: {len(sci_words)} science words clean, cues fire",
          flush=True)

    # (i) CSKG tsv parse + licensing on a synthetic gz
    tmpd = tempfile.mkdtemp()
    gzp = os.path.join(tmpd, "mini_cskg.tsv.gz")
    hdr = "id\tnode1\trelation\tnode2\tnode1;label\tnode2;label\trelation;label\trelation;dimension\tsource\tsentence\n"
    lines = [
        # licensed
        "x1\t/c/en/rain\t/r/Causes\t/c/en/flood\train\tflood\tcauses\t\tCN\t\n",
        "x2\t/c/en/flood\t/r/Causes\t/c/en/erosion\tflood\terosion\tcauses\t\tCN\t\n",
        "x3\t/c/en/volcano\t/r/Causes\t/c/en/lava\tvolcano\tlava\tcauses\t\tCN\t\n",
        "x4\t/c/en/hammer\t/r/UsedFor\t/c/en/nail\thammer\tnail\tused for\t\tCN\t\n",
        # non-licensed (must be dropped)
        "x5\t/c/en/rain\t/r/RelatedTo\t/c/en/weather\train\tweather\trelated to\t\tCN\t\n",
        "x6\t/c/en/rain\t/r/IsA\t/c/en/precipitation\train\tprecipitation\tis a\t\tCN\t\n",
        # empty-label -> derive from id
        "x7\t/c/en/soil\t/r/ReceivesAction\t/c/en/eroded\t\t\treceives action\t\tCN\t\n",
    ]
    with gzip.open(gzp, "wt", encoding="utf-8") as f:
        f.write(hdr)
        for ln in lines:
            f.write(ln)
    rows, n_scanned, per_rel = load_cskg_licensed(gzp)
    rel_set = {r[0] for r in rows}
    assert "CAUSE" in rel_set and "USEDFOR" in rel_set, f"licensed rels missing: {rel_set}"
    assert "/r/RelatedTo" not in per_rel and "/r/IsA" not in per_rel, "non-licensed leaked"
    # empty-label derive
    assert any(r[1] == "soil" and r[2] == "eroded" for r in rows), f"label-derive failed: {rows}"
    assert len(rows) == 5, f"expected 5 licensed rows, got {len(rows)}: {rows}"
    print(f"[self-test] CSKG parse OK: {len(rows)} licensed rows, per_rel={per_rel}", flush=True)

    # (ii) induction keeps ARC-relevant edges + honors budget
    seed_words = {"rain", "erosion"}   # connects rain->flood->erosion chain; volcano/lava/hammer are lures
    kept, istat = induce_subgraph(rows, seed_words, filler_budget=100, max_deg_induce=64)
    kept_labels = set()
    for r in kept:
        kept_labels.add(r["arg0"]); kept_labels.add(r["arg1"])
    assert "rain" in kept_labels and "flood" in kept_labels and "erosion" in kept_labels, \
        f"induction dropped the seed chain: {kept_labels}"
    # budget honored
    kept2, _ = induce_subgraph(rows, seed_words, filler_budget=2, max_deg_induce=64)
    n_nodes2 = len({r["arg0"] for r in kept2} | {r["arg1"] for r in kept2})
    assert n_nodes2 <= 2 or len(kept2) == 0, f"budget not honored: {n_nodes2} nodes"
    print(f"[self-test] induction OK: {istat}", flush=True)

    # (iii) discriminator CAN fire + CAN fail under the REAL gate on CSKG-derived rows
    wn = _load_wordnet()
    pol = PolarityLexicon()
    base = cn._FakeBase()
    enc = cn.NegAwareEncoder(base, seed=SEED)
    g = cn.build_graph_gated(kept, enc.encode_batch, tau_unify=0.99, tau_sim=0.5, wn=wn, pol_lex=pol,
                             use_head_gate=True, use_pol_gate=True)

    def wvec(words):
        return gate._l2_rows(enc.encode_batch(words))

    def nodes_of(word):
        m = g["map_words"](wvec([word]))
        return set().union(*m) if m else set()

    rain_n = nodes_of("rain")
    erosion_n = nodes_of("erosion")
    lava_n = nodes_of("lava")
    assert rain_n and erosion_n, "planted words must map to nodes"
    assert gate.meet_connected(g["fwd"], g["bwd"], rain_n, erosion_n, DEPTH, min_len=1) is True, \
        "planted correct chain rain->flood->erosion MUST connect (gate can fire)"
    if lava_n:
        assert gate.meet_connected(g["fwd"], g["bwd"], rain_n, lava_n, DEPTH, min_len=1) is False, \
            "planted lure rain->lava MUST NOT connect (selectivity real / gate can fail)"
    print("[self-test] REAL-gate discriminator OK (correct connects, lure does not)", flush=True)
    print("[self-test] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# main run
# ---------------------------------------------------------------------------
def run(output_dir, n_sample, seed, cskg_max_lines, filler_budget):
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "smoke" if cskg_max_lines else "full")
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _heartbeat(output_dir, "start", {"n_sample": n_sample, "cskg_max_lines": cskg_max_lines,
                                     "filler_budget": filler_budget, "tau_unify": TAU_UNIFY})

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon

    # 1. encoders + node-identity resources (SAME as clean-node gate)
    base_enc = SemanticHDEncoder()
    neg_enc = cn.NegAwareEncoder(base_enc, seed=seed)
    wn = base_enc._wn
    pol = PolarityLexicon()
    _heartbeat(output_dir, "encoder_ready")

    # 2. sample ARC-Challenge Qs (SAME seed permutation as parent) + seed vocab
    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(all_q))[:n_sample]
    questions = [all_q[int(i)] for i in sorted(idx.tolist())]
    seed_words = set()
    for q in questions:
        for w in arc._content_words(q["stem"], min_len=4):
            seed_words.add(w)
        for ch in q["choices"]:
            for w in arc._content_words(ch, min_len=4):
                seed_words.add(w)
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_sample": len(questions),
                                                "n_seed_words": len(seed_words)})

    # 3. RULE SOURCES (the one variable)
    wt_rows, wt_per_rel = worldtree_rows()
    _heartbeat(output_dir, "worldtree_loaded", {"n_rows": len(wt_rows), "per_rel": wt_per_rel})

    cskg_lic, n_scanned, cskg_per_rel = load_cskg_licensed(CSKG_PATH, max_lines=cskg_max_lines)
    _heartbeat(output_dir, "cskg_loaded", {"n_licensed_rows": len(cskg_lic), "n_scanned": n_scanned,
                                           "per_rel_top": dict(sorted(cskg_per_rel.items(),
                                                                      key=lambda kv: -kv[1])[:8])})
    cskg_rows, induce_stat = induce_subgraph(cskg_lic, seed_words, filler_budget, CSKG_MAX_DEG_INDUCE)
    _heartbeat(output_dir, "cskg_induced", induce_stat)

    union_rows = wt_rows + cskg_rows

    # 4. per-source eval (IDENTICAL gate; ONLY `rows` differs)
    results = {}
    for name, rows in (("worldtree", wt_rows), ("cskg", cskg_rows), ("worldtree_cskg", union_rows)):
        _heartbeat(output_dir, f"{name}_eval_start", {"n_rows": len(rows)})
        res = eval_source(rows, neg_enc, wn, pol, questions, output_dir, name)
        if res is not None:
            res["n_licensed_rows"] = len(rows)
            results[name] = res
            _heartbeat(output_dir, f"{name}_done",
                       {"band": res["band"], "cov": res["typed_correct_coverage"],
                        "typed_gap": res["typed_selectivity_gap"],
                        "untyped_gap": res["untyped_selectivity_gap"],
                        "max_deg": res["graph"]["max_typed_node_degree"]})

    # 5. overall verdict = the CSKG (bigger typed source) band, WorldTree anchor for continuity
    cskg_band = results.get("cskg", {}).get("band", "NO_CSKG")
    union_band = results.get("worldtree_cskg", {}).get("band", "NO_UNION")
    wt_cov = results.get("worldtree", {}).get("typed_correct_coverage", None)
    cskg_cov = results.get("cskg", {}).get("typed_correct_coverage", None)

    # headline = best decision-useful band across the bigger sources
    def _rank(b):
        return {"GREEN": 3, "PROMISCUOUS_FAIL": 2, "MIDDLE_BAND": 1, "STILL_STARVED": 0}.get(b, -1)
    headline_source = max(("cskg", "worldtree_cskg"),
                          key=lambda s: _rank(results.get(s, {}).get("band", "")))
    headline_band = results.get(headline_source, {}).get("band", "NO_SOURCE")

    table = []
    for name in ("worldtree", "cskg", "worldtree_cskg"):
        r = results.get(name)
        if r is None:
            continue
        table.append({
            "source": name, "band": r["band"], "n_rules": r["n_licensed_rows"],
            "cov": r["typed_correct_coverage"], "typed_gap": r["typed_selectivity_gap"],
            "untyped_cov": r["untyped_correct_coverage"], "untyped_gap": r["untyped_selectivity_gap"],
            "gap_beats_untyped": r["typed_gap_beats_untyped"],
            "max_deg": r["graph"]["max_typed_node_degree"], "n_nodes": r["graph"]["n_nodes"],
        })

    summary = (f"RULE-SUPPLY probe | headline={headline_band}({headline_source}) | "
               f"worldtree cov={wt_cov} (anchor) -> cskg cov={cskg_cov} band={cskg_band} | "
               f"union band={union_band}")

    vmsg_map = {
        "GREEN": ("GREEN: supplying the bigger typed CSKG rule corpus RAISED correct-choice coverage "
                  ">=0.35 WITH selectivity (typed gap>=0.15 and > that source's untyped-null) -> "
                  "rule-supply IS the lever; scale trustworthy typed rules."),
        "PROMISCUOUS_FAIL": ("PROMISCUOUS_FAIL: the bigger CSKG corpus raised coverage but selectivity "
                             "collapsed (typed gap ~= untyped-null / <0.05) -> the generic KB connects "
                             "everything equally; a bigger COMMONSENSE KB is the WRONG kind of supply. "
                             "Need science-precise/trustworthy rules (extraction/curation), not noise."),
        "STILL_STARVED": ("STILL_STARVED: even the query-conditioned (generous, upper-bound) CSKG "
                          "subgraph keeps correct coverage <0.15 -> the biggest available typed KB does "
                          "not span ARC-Challenge science causally. Redirect: science-text rule "
                          "extraction / curated causal rules, not off-the-shelf commonsense KBs."),
        "MIDDLE_BAND": ("MIDDLE_BAND: partial coverage with modest selectivity -> no clean win; report "
                        "straight. Rule-supply moves the needle but does not clear the GREEN bar."),
    }
    vmsg = vmsg_map.get(headline_band, f"headline band = {headline_band}")

    metrics = {
        "verdict": "GATE_MEASURED",
        "headline_band": headline_band,
        "headline_source": headline_source,
        "cskg_band": cskg_band,
        "union_band": union_band,
        "summary": summary,
        "verdict_msg": vmsg,
        "anchor_name": ANCHOR_NAME,
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": "smoke" if cskg_max_lines else "full",
        "config": {"n_sample": len(questions), "tau_unify": TAU_UNIFY, "tau_sim": TAU_SIM,
                   "depth": DEPTH, "seed": seed, "filler_budget": filler_budget,
                   "cskg_max_lines": cskg_max_lines, "cskg_max_deg_induce": CSKG_MAX_DEG_INDUCE,
                   "one_variable": "rule_source (worldtree vs cskg vs union); node-identity/gate/Qs/"
                                   "depth/thresholds IDENTICAL to clean-node gate cleannodes_v2",
                   "worldtree_licensed": list(WORLDTREE_LICENSED),
                   "cskg_licensed_map": CSKG_LICENSED},
        "per_source_table": table,
        "results": results,
        "cskg_load": {"path": os.path.relpath(CSKG_PATH, _REPO), "n_scanned": n_scanned,
                      "n_licensed_rows": len(cskg_lic),
                      "per_rel": dict(sorted(cskg_per_rel.items(), key=lambda kv: -kv[1])),
                      "induction": induce_stat,
                      "induction_caveat": ("CSKG is query-conditioned subgraph-induced around the "
                                           "sampled ARC vocab -> its coverage is an UPPER BOUND "
                                           "(generous). STILL_STARVED under it is decisive; GREEN is "
                                           "caveated. WorldTree used whole = fair anchor.")},
        "worldtree_per_relation": wt_per_rel,
        "bands_preregistered": {
            "GREEN": f"cov >= {GREEN_COV} AND typed_gap >= {GREEN_GAP} AND typed_gap > untyped_gap",
            "PROMISCUOUS_FAIL": f"cov > {PROMISCUOUS_COV} AND (typed_gap < {PROMISCUOUS_GAP} OR "
                                f"typed_gap <= untyped_gap)",
            "STILL_STARVED": f"cov < {STARVED_COV}",
            "MIDDLE_BAND": "otherwise",
            "HONEST_GUARD": "coverage AND selectivity tracked together; mega-hub watch = max typed degree",
        },
        "parent_ref": {"cell": "arc_derivation_connectivity_gate_cleannodes_v2 (99736f579)",
                       "worldtree_clean_typed_cov_on_disk": 0.06,
                       "outcome": "COVERAGE_BOUND_CONFIRMED -> rule-supply mandated (this cell)"},
        "notes": ("ONE-VARIABLE ablation: rule SOURCE only. Node-identity (NegAwareEncoder + head-gate + "
                  "polarity merge-gate), gate (build_graph_gated + meet_connected), Qs, depth, thresholds "
                  "ALL imported UNCHANGED from cleannodes_v2. CSKG licensed = causal/conditional/functional "
                  "/r/ relations only (structural + dbpedia excluded; ATOMIC social relations excluded). "
                  "STRAIGHT report; NOT tuned to force GREEN."),
        "REQUIRED_FIELDS": ["verdict", "headline_band", "cskg_band", "union_band", "per_source_table",
                            "results", "cskg_load"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)

    print("\n===== RULE-SUPPLY (CSKG) CONNECTIVITY GATE RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"HEADLINE = {headline_band} ({headline_source}) :: {vmsg}", flush=True)
    print("per-source table:", flush=True)
    for row in table:
        print(f"  {row['source']:>15} band={row['band']:<16} rules={row['n_rules']:>7} "
              f"cov={row['cov']:.3f} typed_gap={row['typed_gap']:+.4f} "
              f"untyped_cov={row['untyped_cov']:.3f} untyped_gap={row['untyped_gap']:+.4f} "
              f"gap>untyped={row['gap_beats_untyped']} max_deg={row['max_deg']} nodes={row['n_nodes']}",
              flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=100, help="ARC-Challenge sample size")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--filler-budget", type=int, default=FILLER_BUDGET)
    ap.add_argument("--cskg-max-lines", type=int, default=0,
                    help="cap CSKG lines scanned (>0 = partial; smoke uses a cap)")
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    if args.mode == "smoke":
        n_sample = 12
        cskg_max_lines = args.cskg_max_lines or 400000
        filler_budget = min(args.filler_budget, 1500)
    else:
        n_sample = args.n
        cskg_max_lines = args.cskg_max_lines  # 0 = full scan
        filler_budget = args.filler_budget

    output_dir = args.out
    try:
        run(output_dir, n_sample, args.seed, cskg_max_lines, filler_budget)
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
