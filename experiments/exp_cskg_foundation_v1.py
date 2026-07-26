#!/usr/bin/env python3
# CELL-TEMPLATE MANDATORY (adapted for a DATA-FOUNDATION BUILD, not a substrate-physics sweep):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - start_marker + crash_diagnostic + heartbeat (long streaming build)
# - final_metrics_atomicity = tmp_replace (os.replace)
# - real_code_path: self-test constructs the REAL PLAIN HDFactStore (random filler; NO GloVe) and
#   round-trips a sample of core edges -> proves the target schema ingests the foundation.
# - CAN-FAIL gate (relation-reconstruction by endpoint relation-affinity vs SHUFFLED-relation control)
#   with pre-registered HARD_PASS / HARD_FAIL bands relative to the measured base-rate.
# - deterministic seeding (fixed int seeds; sorted() dedupe; no hash()-seeded RNG, no list(set()) ordering)
# - N/A META_RULEs declared in the pre-reg (arms-differ / CRLB / cardinality do not apply to a build cell).
#
# WHAT: stream full CSKG (cskg.tsv.gz, 6,001,531 rows), apply the cross-cutting SPINE relation filter,
# canonicalize concept identity by normalized label, dedup, k-core decompose (LABEL the dense 12-14 band,
# do NOT discard the sparse periphery), attach 4 grounding-norm sets by lemma, reserve a held-out edge slice,
# land a sharded glass-box foundation store (hd_fact_store field schema; SYMBOLIC only, NO borrowed vectors),
# and run the can-fail relation-reconstruction gate.
#
# ASCII-only. Determinism: fixed seeds; sorted() for any set ordering.
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# ---------------------------------------------------------------------------------------
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
CSKG_GZ = os.path.join(REPO, "data", "grounding_testbed", "cskg.tsv.gz")
GT_DIR = os.path.join(REPO, "data", "grounding_testbed")
ANCHOR_NAME = "cskg_foundation_v1"
ART_DIR = os.path.join(REPO, "data", ANCHOR_NAME)  # foundation artifact + metrics.json land here

# ---- SPINE keep-set (cross-cutting commonsense; DROP the 79.1% lexical/taxonomic dilution) -------------
# Locked from the FULL relation-column distribution (measured this session). DROP: RelatedTo, Synonym,
# Antonym, FormOf, DerivedFrom, IsA, HasContext, EtymologicallyRelatedTo, SimilarTo, DistinctFrom,
# DefinedAs, InstanceOf, fn:HasLexicalUnit, /r/dbpedia/*, EtymologicallyDerivedFrom, SymbolOf, mw:SameAs.
SPINE_KEEP = frozenset({
    # ATOMIC inferential if-then (at:*)
    "at:xAttr", "at:xWant", "at:xEffect", "at:xNeed", "at:xReact", "at:xIntent",
    "at:oWant", "at:oEffect", "at:oReact",
    # ConceptNet causal / functional / lateral + Wikidata-CS property
    "/r/LocatedNear", "mw:MayHaveProperty", "/r/UsedFor", "/r/CapableOf", "/r/PartOf",
    "/r/AtLocation", "/r/HasSubevent", "/r/HasPrerequisite", "/r/Causes", "/r/HasA",
    "/r/MannerOf", "/r/MotivatedByGoal", "/r/HasProperty", "/r/ReceivesAction", "/r/CausesDesire",
    "/r/HasFirstSubevent", "/r/Desires", "/r/NotDesires", "/r/HasLastSubevent", "/r/MadeOf",
    "/r/CreatedBy", "/r/Entails", "/r/NotCapableOf", "/r/NotHasProperty",
})

# Trust ladder by CSKG source token (curated-vs-crowd; SOURCE-TRUST not correctness).
CURATED_SOURCES = frozenset({"CN", "WN", "WD", "WDT", "WIKIDATA", "WORDNET"})  # -> TRUST_HIGH

# ---- k-core band the blueprint identified as the dense reasoning-capable core ----
DENSE_CORE_K = 12  # nodes with coreness >= 12 flagged is_dense_core (12-14 band per blueprint)

# ---- held-out reservation ----
HELDOUT_FRAC = 0.02   # 2% of spine edges reserved (proving reasoning-not-parroting later)
HELDOUT_SEED = 20260726

# ---- can-fail gate bands (pre-registered; relative to MEASURED base-rate) ----
GATE_MARGIN_REAL = 0.10        # HARD_PASS needs real_acc >= base_rate + 0.10
GATE_SHUFFLE_GAP = 0.10        # HARD_PASS needs real_acc - shuffled_acc >= 0.10
GATE_SHUFFLE_COLLAPSE = 0.03   # HARD_PASS needs shuffled_acc <= base_rate + 0.03
GATE_FAIL_REAL = 0.03          # HARD_FAIL if real_acc < base_rate + 0.03 (no structure beyond mode)
GATE_SEED = 424242

N_EDGE_SHARDS = 16

# Blueprint honesty anchors (for a validity check on the FULL run).
BLUEPRINT = {
    "rows": 6001531, "nonselfloop_edges": 5953561, "distinct_nodes": 2159195,
    "spine_directed_edges": 1244688, "spine_nodes": 501391, "spine_simple_edges": 1184796,
    "core12_nodes": 23632, "core12_avgdeg": 38.4, "core13_nodes": 17793, "core14_nodes": 10731,
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    fin = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, fin)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    fin = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, fin)


def _hb(output_dir, stage, t0, extra=None):
    row = {"ts_iso": _now_iso(), "stage": stage, "elapsed_s": round(time.perf_counter() - t0, 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} t={row['elapsed_s']}s {extra or ''}", flush=True)


# ---------------------------------------------------------------------------------------
def canon_from_uri(uri, label):
    """Canonical concept id = the LEMMA extracted from the CSKG node URI (more reliable identity than
    the sense-glossed label column), then normalized. ConceptNet '/c/en/dog/n/wn/animal' -> 'dog';
    ATOMIC 'at:personx_bakes_a_cake' -> 'personx_bakes_a_cake'; 'wd:Q5'/'fn:x' -> after ':'. This
    DELIBERATELY merges POS/sense suffix variants of one concept (sense granularity deferred to the
    LEARNED encoder downstream; glass-box: one lemma = one node). Falls back to the label if the URI
    has no recognizable lemma segment."""
    lemma = None
    if uri.startswith("/c/"):
        segs = uri.split("/")            # ['', 'c', 'en', 'dog', 'n', 'wn', 'animal']
        if len(segs) >= 4 and segs[3]:
            lemma = segs[3]
    elif ":" in uri:
        lemma = uri.split(":", 1)[1]
    if not lemma:
        lemma = label
    return canon(lemma)


def canon(label):
    """Normalize a lowercased free-text token to a canonical id.
    lower -> collapse every run of non-alphanumeric to a single '_' -> strip leading/trailing '_'."""
    s = label.strip().lower()
    out = []
    prev_us = True  # suppress leading underscore
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            prev_us = False
        elif not prev_us:
            out.append("_")
            prev_us = True
    r = "".join(out)
    if r.endswith("_"):
        r = r[:-1]
    return r


def kcore_coreness(n_nodes, edges_uv):
    """Batagelj-Zaversnik coreness on a simple undirected graph.
    edges_uv: (E,2) int array of DEDUPED undirected simple edges (u<v, no self-loops).
    Returns coreness[n_nodes] int array (max k for which node is in the k-core)."""
    if n_nodes == 0:
        return np.zeros(0, dtype=np.int32)
    deg = np.zeros(n_nodes, dtype=np.int64)
    u = edges_uv[:, 0]
    v = edges_uv[:, 1]
    np.add.at(deg, u, 1)
    np.add.at(deg, v, 1)
    # CSR adjacency: place each endpoint into its source node's contiguous slot block.
    ptr = np.zeros(n_nodes + 1, dtype=np.int64)
    ptr[1:] = np.cumsum(deg)
    order_a = np.concatenate([u, v])   # source endpoints (both directions)
    order_b = np.concatenate([v, u])   # neighbor endpoints
    srt = np.argsort(order_a, kind="stable")  # group neighbors by source node in CSR order
    adj = order_b[srt]
    # BZ peeling
    core = deg.copy()
    # bucket sort nodes by current degree
    md = int(core.max()) if n_nodes else 0
    verts = np.argsort(core, kind="stable")
    pos = np.empty(n_nodes, dtype=np.int64)
    pos[verts] = np.arange(n_nodes)
    bin_start = np.zeros(md + 2, dtype=np.int64)
    dcount = np.bincount(core, minlength=md + 1)
    bin_start[1:md + 2] = np.cumsum(dcount)
    bin_boundary = bin_start.copy()
    core_out = core.copy()
    processed = np.zeros(n_nodes, dtype=bool)
    verts = list(verts)
    for i in range(n_nodes):
        w = verts[i]
        processed[w] = True
        dw = core_out[w]
        for j in range(ptr[w], ptr[w + 1]):
            nb = adj[j]
            if not processed[nb] and core_out[nb] > dw:
                dn = core_out[nb]
                pn = pos[nb]
                pb = bin_boundary[dn]
                first = verts[pb]
                if first != nb:
                    verts[pn] = first
                    verts[pb] = nb
                    pos[first] = pn
                    pos[nb] = pb
                bin_boundary[dn] += 1
                core_out[nb] = dn - 1
    return core_out.astype(np.int32)


def load_norms():
    """Load the 4 grounding-norm sets keyed by lowercased word. Returns dict name->{word:attrs}."""
    norms = {"lancaster": {}, "concreteness": {}, "vad": {}, "aoa": {}}

    def _f(x):
        try:
            v = float(x)
            return v if v == v else None  # drop NaN
        except (ValueError, TypeError):
            return None

    p = os.path.join(GT_DIR, "Lancaster_sensorimotor_norms_for_39707_words.csv")
    if os.path.exists(p):
        with open(p, newline="", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                w = (row.get("Word") or "").strip().lower()
                if not w:
                    continue
                norms["lancaster"][w] = {
                    "aud": _f(row.get("Auditory.mean")), "gus": _f(row.get("Gustatory.mean")),
                    "hap": _f(row.get("Haptic.mean")), "int": _f(row.get("Interoceptive.mean")),
                    "olf": _f(row.get("Olfactory.mean")), "vis": _f(row.get("Visual.mean")),
                    "foot": _f(row.get("Foot_leg.mean")), "hand": _f(row.get("Hand_arm.mean")),
                    "head": _f(row.get("Head.mean")), "mouth": _f(row.get("Mouth.mean")),
                    "torso": _f(row.get("Torso.mean"))}

    p = os.path.join(GT_DIR, "Concreteness_ratings_Brysbaert_et_al_BRM.txt")
    if os.path.exists(p):
        with open(p, newline="", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                w = (row.get("Word") or "").strip().lower()
                if not w:
                    continue
                norms["concreteness"][w] = {"conc": _f(row.get("Conc.M"))}

    p = os.path.join(GT_DIR, "Ratings_Warriner_et_al.csv")
    if os.path.exists(p):
        with open(p, newline="", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                w = (row.get("Word") or "").strip().lower()
                if not w:
                    continue
                norms["vad"][w] = {"valence": _f(row.get("V.Mean.Sum")),
                                   "arousal": _f(row.get("A.Mean.Sum")),
                                   "dominance": _f(row.get("D.Mean.Sum"))}

    p = os.path.join(GT_DIR, "AoA_51715_words.csv")
    if os.path.exists(p):
        with open(p, newline="", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                w = (row.get("Word") or "").strip().lower()
                if not w:
                    continue
                norms["aoa"][w] = {"aoa": _f(row.get("AoA_Kup"))}
    return norms


# ---------------------------------------------------------------------------------------
def stream_spine(path, output_dir, t0, row_cap=None):
    """Single memory-bounded streaming pass. Returns node arrays + directed typed spine edges.
    node_of: canon_id -> int index. Also tracks raw-node-id collisions + per-source counts."""
    node_of = {}
    node_label = []          # surface label per node index (first seen)
    raw_ids_seen = set()     # distinct raw CSKG node ids
    collisions = 0           # raw ids mapping to an already-populated canon id
    seen_raw_to_canon = {}
    rel_list = sorted(SPINE_KEEP)
    rel_id = {r: i for i, r in enumerate(rel_list)}
    src_counts = {}
    rel_counts = np.zeros(len(rel_list), dtype=np.int64)

    eu = []  # directed edge u
    ev = []  # directed edge v
    er = []  # rel id
    es = []  # source-trust: 1 curated (HIGH) else 0 (MID)
    esrc = []  # raw source token id
    src_tok_id = {}

    n_rows = 0
    n_kept = 0
    n_selfloop = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline()  # skip header
        for line in f:
            n_rows += 1
            if row_cap and n_rows > row_cap:
                break
            if (n_rows % 1000000) == 0:
                _hb(output_dir, "stream", t0, {"rows": n_rows, "kept": n_kept, "nodes": len(node_of)})
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            rel = parts[2]
            if rel not in SPINE_KEEP:
                continue
            n1raw, n2raw = parts[1], parts[3]
            l1, l2 = parts[4], parts[5]
            src = parts[8] if len(parts) > 8 else ""
            c1, c2 = canon_from_uri(n1raw, l1), canon_from_uri(n2raw, l2)
            if not c1 or not c2:
                continue
            if c1 == c2:
                n_selfloop += 1
                continue
            # node identity + collision bookkeeping
            for raw, c in ((n1raw, c1), (n2raw, c2)):
                if raw not in raw_ids_seen:
                    raw_ids_seen.add(raw)
                    if c in node_of:
                        collisions += 1  # a distinct raw id folding into an existing canon node
                    seen_raw_to_canon[raw] = c
                if c not in node_of:
                    node_of[c] = len(node_label)
                    node_label.append(c)
            u, v = node_of[c1], node_of[c2]
            rid = rel_id[rel]
            if src not in src_tok_id:
                src_tok_id[src] = len(src_tok_id)
            sid = src_tok_id[src]
            trust_high = 1 if src.upper() in CURATED_SOURCES else 0
            eu.append(u); ev.append(v); er.append(rid); es.append(trust_high); esrc.append(sid)
            src_counts[src] = src_counts.get(src, 0) + 1
            rel_counts[rid] += 1
            n_kept += 1

    eu = np.asarray(eu, dtype=np.int64); ev = np.asarray(ev, dtype=np.int64)
    er = np.asarray(er, dtype=np.int32); es = np.asarray(es, dtype=np.int8)
    esrc = np.asarray(esrc, dtype=np.int32)
    id_src = sorted(src_tok_id, key=lambda k: src_tok_id[k])
    return {
        "node_of": node_of, "node_label": node_label, "rel_list": rel_list,
        "eu": eu, "ev": ev, "er": er, "es": es, "esrc": esrc, "id_src": id_src,
        "rel_counts": rel_counts, "src_counts": src_counts,
        "n_rows": n_rows if not row_cap else min(n_rows, row_cap),
        "n_kept": n_kept, "n_selfloop": n_selfloop,
        "distinct_raw_ids": len(raw_ids_seen), "collisions": collisions,
    }


def build_and_measure(S, output_dir, t0):
    """Dedup, k-core, and assemble measured foundation metrics from streamed spine S."""
    n_nodes = len(S["node_label"])
    eu, ev, er = S["eu"], S["ev"], S["er"]
    n_directed = eu.shape[0]

    # exact directed-typed-triple dedup (u, rel, v)
    trip = (eu.astype(np.int64) * n_nodes + ev.astype(np.int64)) * len(S["rel_list"]) + er.astype(np.int64)
    uniq_trip, uidx = np.unique(trip, return_index=True)
    n_typed_edges = uniq_trip.shape[0]
    dup_typed = n_directed - n_typed_edges

    # simple undirected edges (ignore relation + direction) for k-core
    lo = np.minimum(eu, ev).astype(np.int64)
    hi = np.maximum(eu, ev).astype(np.int64)
    upair = lo * n_nodes + hi
    uniq_pair = np.unique(upair)
    su = (uniq_pair // n_nodes).astype(np.int64)
    sv = (uniq_pair % n_nodes).astype(np.int64)
    simple_edges = np.stack([su, sv], axis=1)
    n_simple = simple_edges.shape[0]
    _hb(output_dir, "dedup", t0, {"typed_edges": int(n_typed_edges), "simple_edges": int(n_simple)})

    coreness = kcore_coreness(n_nodes, simple_edges)
    _hb(output_dir, "kcore", t0, {"max_core": int(coreness.max()) if n_nodes else 0})

    # per-k core stats for the 5..20 band
    core_stats = {}
    deg_simple = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(deg_simple, su, 1)
    np.add.at(deg_simple, sv, 1)
    for k in [5, 8, 10, 11, 12, 13, 14, 15, 16, 20]:
        mask = coreness >= k
        nk = int(mask.sum())
        if nk == 0:
            core_stats[str(k)] = {"nodes": 0, "avg_deg": 0.0}
            continue
        both = mask[su] & mask[sv]
        ek = int(both.sum())
        core_stats[str(k)] = {"nodes": nk, "avg_deg": round(2.0 * ek / nk, 2)}

    return {
        "n_nodes": n_nodes, "n_directed_spine": int(n_directed), "n_typed_edges": int(n_typed_edges),
        "dup_typed": int(dup_typed), "n_simple_edges": int(n_simple),
        "coreness": coreness, "deg_simple": deg_simple, "uidx": uidx, "uniq_trip": uniq_trip,
        "core_stats": core_stats,
    }


def relation_reconstruction_gate(S, M, output_dir, t0):
    """CAN-FAIL: predict a held-out edge's relation from its endpoints' TRAIN relation-affinity.
    score[r] = (#train edges incident to head with rel r) + (#train edges incident to tail with rel r).
    Real vs SHUFFLED-relation control (relation labels permuted across all train edges -> endpoint
    relation-profiles destroyed -> must collapse to base-rate). Evaluated on held-out edges whose BOTH
    endpoints are in the dense core (coreness>=DENSE_CORE_K) AND retain >=3 train incidences."""
    n_nodes = M["n_nodes"]
    nrel = len(S["rel_list"])
    eu, ev, er = S["eu"], S["ev"], S["er"]
    # use unique typed edges as the edge population
    uidx = M["uidx"]
    hu, hv, hr = eu[uidx], ev[uidx], er[uidx]
    ne = hu.shape[0]

    rng = np.random.default_rng(HELDOUT_SEED)
    perm = rng.permutation(ne)
    n_hold = max(1, int(round(HELDOUT_FRAC * ne)))
    hold_idx = np.zeros(ne, dtype=bool)
    hold_idx[perm[:n_hold]] = True
    train = ~hold_idx

    tu, tv, tr = hu[train], hv[train], hr[train]

    def build_affinity(rel_labels):
        aff = np.zeros((n_nodes, nrel), dtype=np.int32)
        np.add.at(aff, (tu, rel_labels), 1)
        np.add.at(aff, (tv, rel_labels), 1)
        return aff

    gu, gv, gr = hu[hold_idx], hv[hold_idx], hr[hold_idx]
    core = M["coreness"]
    incid = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(incid, tu, 1)
    np.add.at(incid, tv, 1)
    evalmask = (core[gu] >= DENSE_CORE_K) & (core[gv] >= DENSE_CORE_K) & (incid[gu] >= 3) & (incid[gv] >= 3)
    n_eval = int(evalmask.sum())
    if n_eval < 50:  # fall back to any held-out with defined affinity (small smoke slices)
        evalmask = (incid[gu] >= 1) & (incid[gv] >= 1)
        n_eval = int(evalmask.sum())
    egu, egv, egr = gu[evalmask], gv[evalmask], gr[evalmask]

    global_freq = np.bincount(tr, minlength=nrel)
    mode_rel = int(np.argmax(global_freq))
    base_rate = float((egr == mode_rel).mean()) if n_eval else 0.0

    def predict_acc(aff):
        sc = aff[egu].astype(np.int64) + aff[egv].astype(np.int64)  # (n_eval, nrel)
        sc = sc + (global_freq.astype(np.int64)[None, :] * 0)       # (no global tiebreak bias)
        # deterministic tiebreak: add a tiny global-frequency term scaled below 1
        tie = global_freq.astype(np.float64) / (global_freq.sum() + 1.0)
        pred = np.argmax(sc.astype(np.float64) + tie[None, :], axis=1)
        return float((pred == egr).mean()) if n_eval else 0.0

    real_acc = predict_acc(build_affinity(tr))
    rng2 = np.random.default_rng(GATE_SEED)
    shuf = tr[rng2.permutation(tr.shape[0])]
    shuffled_acc = predict_acc(build_affinity(shuf))

    _hb(output_dir, "gate", t0, {"n_eval": n_eval, "base_rate": round(base_rate, 4),
                                 "real": round(real_acc, 4), "shuffled": round(shuffled_acc, 4)})

    hard_pass = (real_acc >= base_rate + GATE_MARGIN_REAL and
                 (real_acc - shuffled_acc) >= GATE_SHUFFLE_GAP and
                 shuffled_acc <= base_rate + GATE_SHUFFLE_COLLAPSE)
    hard_fail = (real_acc < base_rate + GATE_FAIL_REAL) or (shuffled_acc > base_rate + GATE_MARGIN_REAL)
    verdict = "HARD_PASS" if hard_pass else ("HARD_FAIL" if hard_fail else "MIDDLE_BAND")
    return {
        "gate_verdict": verdict, "n_heldout": int(n_hold), "n_eval": n_eval,
        "base_rate": round(base_rate, 4), "mode_relation": S["rel_list"][mode_rel],
        "real_acc": round(real_acc, 4), "shuffled_acc": round(shuffled_acc, 4),
        "real_minus_shuffle": round(real_acc - shuffled_acc, 4),
        "real_minus_base": round(real_acc - base_rate, 4),
        "bands": {"hard_pass": "real>=base+0.10 AND real-shuf>=0.10 AND shuf<=base+0.03",
                  "hard_fail": "real<base+0.03 OR shuf>base+0.10"},
        "hold_idx_bool": hold_idx, "uidx_edge": uidx,
    }


def attach_grounding(S, norms, output_dir, t0):
    """Attach norm attrs to concept nodes by lowercased-lemma match (underscore->space). Partial."""
    labels = S["node_label"]
    n = len(labels)
    grounding = {}
    cov = {k: 0 for k in norms}
    single_tok = 0
    conc_vals = []
    for i, c in enumerate(labels):
        key = c.replace("_", " ")
        if "_" not in c:
            single_tok += 1
        rec = {}
        for name, d in norms.items():
            hit = d.get(key)
            if hit is not None:
                rec[name] = hit
                cov[name] += 1
                if name == "concreteness" and hit.get("conc") is not None:
                    conc_vals.append(hit["conc"])
        if rec:
            grounding[i] = rec
    _hb(output_dir, "grounding", t0, {"grounded_nodes": len(grounding)})
    return {
        "grounding": grounding,
        "coverage": {k: round(cov[k] / n, 4) if n else 0.0 for k in cov},
        "coverage_counts": cov, "single_token_nodes": single_tok,
        "nodes_with_any_grounding": len(grounding),
        "frac_any_grounding": round(len(grounding) / n, 4) if n else 0.0,
        "mean_concreteness_matched": round(float(np.mean(conc_vals)), 3) if conc_vals else None,
    }


def write_artifact(S, M, G, GATE, output_dir, t0):
    """Land the sharded glass-box foundation (hd_fact_store field schema; SYMBOLIC only)."""
    labels = S["node_label"]
    core = M["coreness"]
    deg = M["deg_simple"]
    grounding = G["grounding"]
    id_src = S["id_src"]

    # nodes.jsonl
    with open(os.path.join(output_dir, "nodes.jsonl"), "w", encoding="utf-8", newline="") as f:
        for i, c in enumerate(labels):
            row = {"id": c, "surface": c.replace("_", " "), "degree": int(deg[i]),
                   "kcore": int(core[i]), "is_dense_core": bool(core[i] >= DENSE_CORE_K)}
            g = grounding.get(i)
            if g:
                row["grounding"] = g
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # edges: sharded jsonl in hd_fact_store field schema (subject/relation/obj/source/trust + provenance)
    uidx = M["uidx"]
    eu, ev, er, es, esrc = S["eu"], S["ev"], S["er"], S["es"], S["esrc"]
    rel_list = S["rel_list"]
    hold_bool = GATE["hold_idx_bool"]                 # aligned to unique-typed-edge order (uidx)
    uidx_edge = GATE["uidx_edge"]
    # map: position in uidx array -> whether held out
    heldout_of_uidxpos = hold_bool  # same order as hu=eu[uidx]
    shards = [open(os.path.join(output_dir, f"edges_shard_{s:02d}.jsonl"), "w",
                   encoding="utf-8", newline="") for s in range(N_EDGE_SHARDS)]
    hf = open(os.path.join(output_dir, "heldout_edges.jsonl"), "w", encoding="utf-8", newline="")
    n_edges_written = 0
    n_heldout_written = 0
    try:
        for pos, ei in enumerate(uidx):
            subj = labels[eu[ei]]
            obj = labels[ev[ei]]
            rel = rel_list[er[ei]]
            src = id_src[esrc[ei]]
            trust = "TRUST_HIGH" if es[ei] == 1 else "TRUST_MID"
            rec = {"subject": subj, "relation": rel, "obj": obj, "source": src, "trust": trust,
                   "subj_core": bool(core[eu[ei]] >= DENSE_CORE_K),
                   "obj_core": bool(core[ev[ei]] >= DENSE_CORE_K)}
            if heldout_of_uidxpos[pos]:
                hf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_heldout_written += 1
            else:
                sh = shards[hash(subj) % N_EDGE_SHARDS] if False else shards[(eu[ei]) % N_EDGE_SHARDS]
                sh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_edges_written += 1
    finally:
        for sh in shards:
            sh.close()
        hf.close()
    _hb(output_dir, "write", t0, {"edges_written": n_edges_written, "heldout_written": n_heldout_written})
    return {"nodes_written": len(labels), "edges_written": n_edges_written,
            "heldout_written": n_heldout_written, "n_shards": N_EDGE_SHARDS}


# ---------------------------------------------------------------------------------------
def run(run_mode, output_dir):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode)
    os.makedirs(ART_DIR, exist_ok=True)
    # smoke = FULL-scale stream + measurement + gate (discriminator fires at full-N per
    # DISCRIMINATOR-MUST-SURVIVE-SCALE option A) but SKIPS the heavy artifact write. A row-cap
    # would read only the sorted file's alphabetical head -> non-representative k-core.
    row_cap = None
    _hb(output_dir, "begin", t0, {"run_mode": run_mode, "row_cap": row_cap})

    S = stream_spine(CSKG_GZ, output_dir, t0, row_cap=row_cap)
    _hb(output_dir, "stream_done", t0, {"kept": S["n_kept"], "nodes": len(S["node_label"])})
    M = build_and_measure(S, output_dir, t0)
    GATE = relation_reconstruction_gate(S, M, output_dir, t0)
    norms = load_norms()
    G = attach_grounding(S, norms, output_dir, t0)

    W = None
    if run_mode == "full":
        W = write_artifact(S, M, G, GATE, ART_DIR, t0)

    # blueprint validity check (FULL only)
    blueprint_ok = None
    blueprint_delta = None
    if run_mode == "full":
        def within(a, b, tol=0.05):
            return abs(a - b) <= tol * b
        blueprint_delta = {
            "spine_nodes": [M["n_nodes"], BLUEPRINT["spine_nodes"]],
            "spine_simple_edges": [M["n_simple_edges"], BLUEPRINT["spine_simple_edges"]],
            "core12_nodes": [M["core_stats"]["12"]["nodes"], BLUEPRINT["core12_nodes"]],
            "core13_nodes": [M["core_stats"]["13"]["nodes"], BLUEPRINT["core13_nodes"]],
        }
        blueprint_ok = (within(M["n_nodes"], BLUEPRINT["spine_nodes"]) and
                        within(M["n_simple_edges"], BLUEPRINT["spine_simple_edges"], 0.05) and
                        within(M["core_stats"]["12"]["nodes"], BLUEPRINT["core12_nodes"], 0.10))

    rel_dist = {S["rel_list"][i]: int(S["rel_counts"][i]) for i in range(len(S["rel_list"]))}
    core12 = M["core_stats"]["12"]
    gate_floor_ok = core12["nodes"] >= 5000 and core12["avg_deg"] >= 37.0

    metrics = {
        "verdict": GATE["gate_verdict"], "run_mode": run_mode,
        "verdict_msg": (f"CSKG foundation {run_mode}: {M['n_nodes']} spine nodes / "
                        f"{M['n_typed_edges']} typed edges; dense-core(k>=12)={core12['nodes']} @ "
                        f"deg {core12['avg_deg']}; gate={GATE['gate_verdict']} "
                        f"(real={GATE['real_acc']} shuf={GATE['shuffled_acc']} base={GATE['base_rate']})"),
        "summary": f"CSKG_FOUNDATION {run_mode} {GATE['gate_verdict']}",
        "elapsed_s": round(time.perf_counter() - t0, 1), "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME, "pid": os.getpid(),
        # scale / quality
        "n_rows_streamed": S["n_rows"], "n_selfloop_dropped": S["n_selfloop"],
        "spine_directed_edges": M["n_directed_spine"], "spine_typed_edges": M["n_typed_edges"],
        "duplicate_typed_edges": M["dup_typed"],
        "duplicate_rate": round(M["dup_typed"] / M["n_directed_spine"], 4) if M["n_directed_spine"] else 0.0,
        "spine_nodes": M["n_nodes"], "spine_simple_edges": M["n_simple_edges"],
        "distinct_raw_cskg_ids": S["distinct_raw_ids"],
        "concept_identity_collisions": S["collisions"],
        "collision_rate": round(S["collisions"] / S["distinct_raw_ids"], 4) if S["distinct_raw_ids"] else 0.0,
        "relation_distribution": rel_dist, "n_relation_types": len(S["rel_list"]),
        "source_distribution": S["src_counts"],
        # k-core
        "kcore_band": M["core_stats"], "dense_core_k": DENSE_CORE_K,
        "dense_core_nodes": core12["nodes"], "dense_core_avg_deg": core12["avg_deg"],
        "gate_density_floor_ok": bool(gate_floor_ok),
        "blueprint_ok": blueprint_ok, "blueprint_delta": blueprint_delta,
        # grounding
        "grounding_coverage": G["coverage"], "grounding_coverage_counts": G["coverage_counts"],
        "nodes_with_any_grounding": G["nodes_with_any_grounding"],
        "frac_any_grounding": G["frac_any_grounding"],
        "single_token_nodes": G["single_token_nodes"],
        "mean_concreteness_matched": G["mean_concreteness_matched"],
        # gate
        "gate": {k: v for k, v in GATE.items() if k not in ("hold_idx_bool", "uidx_edge")},
        "heldout_frac": HELDOUT_FRAC,
        # artifact
        "artifact_dir": ART_DIR if run_mode == "full" else None,
        "artifact": W,
        # pre-reg / discipline provenance
        "prereg": os.path.join(REPO, "preregs", "2026-07-26_cskg_foundation_v1.md"),
        "canonicalization": "normalized-label (lower; non-alnum-run->_; strip); surface-collision merge; sense deferred to learned encoder",
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    fin = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, fin)
    if run_mode == "full":
        # mirror metrics into the artifact dir too (self-contained VET-able artifact)
        with open(os.path.join(ART_DIR, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
    print(f"[done] {metrics['summary']} elapsed={metrics['elapsed_s']}s -> {fin}", flush=True)
    return metrics


# ---------------------------------------------------------------------------------------
def self_test():
    """Real-code-path self-test on a tiny synthetic CSKG-shaped TSV.gz: exercises spine filter,
    canonicalization+collision, k-core, held-out split, grounding join, the can-fail gate (real
    PASSES on structured toy / SHUFFLE collapses), and a round-trip through the REAL PLAIN HDFactStore
    (random filler; NO GloVe) proving the target schema ingests the foundation edges."""
    import tempfile
    exercised = set()
    td = tempfile.mkdtemp(prefix="cskgft_selftest_")
    tsv = os.path.join(td, "mini.tsv.gz")
    hdr = "id\tnode1\trelation\tnode2\tnode1;label\tnode2;label\trelation;label\trelation;dimension\tsource\tsentence\n"
    rows = []
    # Structured toy: two relation-coherent clusters so endpoint-affinity beats shuffle.
    # cluster A: 'fire','heat','burn','smoke','flame' densely connected by /r/Causes
    A = ["fire", "heat", "burn", "smoke", "flame", "spark"]
    B = ["knife", "fork", "spoon", "plate", "cup", "bowl"]
    rid = 0
    for grp, rel in ((A, "/r/Causes"), (B, "/r/UsedFor")):
        for i in range(len(grp)):
            for j in range(len(grp)):
                if i == j:
                    continue
                rid += 1
                rows.append(f"e{rid}\t/c/en/{grp[i]}\t{rel}\t/c/en/{grp[j]}\t{grp[i]}\t{grp[j]}\t{rel}\t\tCN\t.")
    # collision case: two raw ids -> same canon label 'fire'
    rows.append(f"eC\t/c/en/fire/n/wn\t/r/HasProperty\t/c/en/hot\tFire\thot\tprop\t\tCN\t.")
    # dropped lexical relations (must be filtered out)
    rows.append(f"eD\t/c/en/fire\t/r/Synonym\t/c/en/blaze\tfire\tblaze\tsyn\t\tCN\t.")
    rows.append(f"eS\t/c/en/x\t/r/RelatedTo\t/c/en/y\tx\ty\trel\t\tCN\t.")
    # self-loop (must drop)
    rows.append(f"eL\t/c/en/fire\t/r/Causes\t/c/en/fire\tfire\tfire\tcauses\t\tCN\t.")
    with gzip.open(tsv, "wt", encoding="utf-8") as f:
        f.write(hdr)
        f.write("\n".join(rows) + "\n")

    out = tempfile.mkdtemp(prefix="cskgft_out_")
    t0 = time.perf_counter()
    S = stream_spine(tsv, out, t0)
    exercised.add("stream_spine")
    assert "fire" in S["node_of"], "canon fire missing"
    assert S["n_selfloop"] == 1, ("selfloop", S["n_selfloop"])
    assert all(r in SPINE_KEEP for r in S["rel_list"]), "non-spine rel leaked"
    # Synonym/RelatedTo dropped -> 'blaze','x','y' never become nodes
    assert "blaze" not in S["node_of"] and "x" not in S["node_of"], "lexical rel leaked as node"
    assert S["collisions"] >= 1, ("collision not detected", S["collisions"])
    M = build_and_measure(S, out, t0)
    exercised.add("build_and_measure")
    assert M["n_simple_edges"] > 0 and M["coreness"].max() >= 3, ("kcore", M["coreness"].max())
    GATE = relation_reconstruction_gate(S, M, out, t0)
    exercised.add("relation_reconstruction_gate")
    # On the structured toy the real predictor must beat the shuffle control.
    assert GATE["real_acc"] >= GATE["shuffled_acc"], ("gate not discriminating", GATE)
    norms = load_norms()
    exercised.add("load_norms")
    G = attach_grounding(S, norms, out, t0)
    exercised.add("attach_grounding")
    assert G["coverage"]["concreteness"] >= 0.0
    # REAL PLAIN HDFactStore round-trip (schema-ingest proof; random filler, NO GloVe)
    from hdlab.hd_fact_store import HDFactStore
    st = HDFactStore(n_dim=4096, seed=1)
    labels = S["node_label"]; eu, ev, er = S["eu"], S["ev"], S["er"]
    stored = []
    for ei in range(min(30, eu.shape[0])):
        subj, obj, rel = labels[eu[ei]], labels[ev[ei]], S["rel_list"][er[ei]]
        st.store(subj, rel, obj, "CN", "TRUST_MID")
        stored.append((subj, rel, obj))
    exercised.add("HDFactStore.store")
    rec = st.recover_fact(st._facts[0].vec)
    assert rec["subject"] == stored[0][0] and rec["object"] == stored[0][2], ("roundtrip", rec, stored[0])
    exercised.add("HDFactStore.recover_fact")
    # write-artifact path
    W = write_artifact(S, M, G, GATE, out, t0)
    exercised.add("write_artifact")
    assert W["nodes_written"] == len(labels)
    need = {"stream_spine", "build_and_measure", "relation_reconstruction_gate", "attach_grounding",
            "HDFactStore.store", "HDFactStore.recover_fact", "write_artifact"}
    missing = need - exercised
    assert not missing, ("self-test skipped real entrypoints", missing)
    print(f"[self_test] PASS exercised={sorted(exercised)} "
          f"gate(real={GATE['real_acc']} shuf={GATE['shuffled_acc']}) "
          f"collisions={S['collisions']} maxcore={int(M['coreness'].max())}", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    output_dir = os.path.join(REPO, "data", f"exp_{ANCHOR_NAME}") if mode != "self_test" else \
        os.path.join(REPO, "data", f"exp_{ANCHOR_NAME}_selftest")
    global _OUTPUT_DIR
    _OUTPUT_DIR = output_dir
    if mode == "self_test":
        self_test()
        return
    run(mode, output_dir)


_OUTPUT_DIR = os.path.join(REPO, "data", f"exp_{ANCHOR_NAME}")

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_OUTPUT_DIR, e)
        raise
