#!/usr/bin/env python3
# CELL-TEMPLATE MANDATORY (adapted for a KB-ENRICHMENT PROBE-RECOVERY DIAGNOSTIC, not a
# substrate-physics sweep -- see preregs/2026-08-11_causal_enrichment_probe_recovery_v1.md for the
# full SCHEMA-VET declaration table; summary of applicable items):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - start_marker + crash_diagnostic + heartbeat (single deterministic pass, <=4 min)
# - final_metrics_atomicity = tmp_replace (os.replace)
# - real_code_path: self-test constructs the REAL objects at tiny scale (real edges_shard_00.jsonl
#   sample, real parse_gene_ontology() against real go.obo capped max_terms=50, real regex-parse of
#   the first ~200 lines of the real causenet-precision.jsonl.bz2)
# - CAN-FAIL recovery test with pre-registered HARD_PASS / MIDDLE_BAND / HARD_FAIL bands + TWO
#   required controls (shuffled-relation-label; random-non-causal-edges)
# - deterministic seeding (fixed int seeds; sorted()/np.random.default_rng; no hash()-seeded RNG)
# - N/A META_RULEs declared in the pre-reg (cardinality / CRLB / baseline_in_band do not apply to a
#   KB-coverage recall diagnostic; same class of exemption exp_cskg_foundation_v1.py itself declares).
#
# WHAT: overlay CauseNet-Precision (general-domain web-extracted causal pairs) + GO regulates-family
# edges (from a go.obo full re-download, fixing the go-basic.obo omission) onto the already-landed
# CSKG foundation v1 graph (read-only input; this cell writes ONLY to its own data/exp_.../ dir, never
# mutates data/cskg_foundation_v1/). Measure recovery rate of a 40-probe held-out causal-fact set via
# a 1-2 hop, every-hop-causal-typed graph query, under BASELINE / ENRICHED / SHUFFLE-control /
# RANDOM-EDGES-control.
#
# ASCII-only. Determinism: fixed seeds; sorted() for any set/dict ordering; no hash()-seeded RNG.
# NO ORIGIN PUSH this cycle -> runs INLINE-LOCAL, not via queue_add / remote dispatch.
from __future__ import annotations

import argparse
import bz2
import hashlib
import json
import os
import platform
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------------------
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

CSKG_DIR = os.path.join(REPO, "data", "cskg_foundation_v1")
CAUSENET_BZ2 = os.path.join(REPO, "data", "bio_kb_cache", "causenet", "causenet-precision.jsonl.bz2")
GO_OBO = os.path.join(REPO, "data", "bio_kb_cache", "go", "go.obo")
ANCHOR_NAME = "causal_enrichment_probe_recovery_v1"
ART_DIR = os.path.join(REPO, "data", f"exp_{ANCHOR_NAME}")
PREREG_PATH = os.path.join(REPO, "preregs", "2026-08-11_causal_enrichment_probe_recovery_v1.md")

N_EDGE_SHARDS = 16

# ---- causal relation buckets (exact; reproduces the scout's disk-verified 14.83% generous bucket) --
CAUSAL_RELS_BASE = frozenset({
    "/r/Causes", "at:xEffect", "at:oEffect",
    "/r/HasSubevent", "/r/HasFirstSubevent", "/r/HasLastSubevent",
})
NEW_CAUSENET_REL = "cn:Causes"
GO_REGULATES_RELS = frozenset({"REGULATES", "POSITIVELY_REGULATES", "NEGATIVELY_REGULATES"})
NEW_RELS = frozenset({NEW_CAUSENET_REL}) | GO_REGULATES_RELS
ENRICHED_CAUSAL_RELS = CAUSAL_RELS_BASE | NEW_RELS
STRICT_CAUSAL_RELS = frozenset({"/r/Causes", NEW_CAUSENET_REL})

# ---- deterministic seeds (fixed ints; never hash()/list(set())) --------------------------------
SHUFFLE_SEED = 20260811
RANDOM_ENDPOINT_SEED = 20260812
RANDOM_REL_SEED = 20260813

# ---- pre-registered gate bands ------------------------------------------------------------------
GATE_HARD_PASS_GAIN = 0.30
GATE_HARD_FAIL_GAIN = 0.10
GATE_SHUFFLE_COLLAPSE_TOL = 0.05
GATE_RANDOM_STAYLOW_TOL = 0.10
GATE_RANDOM_MATCHES_ENRICHED_TOL = 0.05


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
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} t={row['elapsed_s']}s {extra or ''}", flush=True)


def canon(label):
    """IDENTICAL normalization to exp_cskg_foundation_v1.canon(): lower -> collapse every run of
    non-alnum to a single '_' -> strip leading/trailing '_'. Reused verbatim so probe/CauseNet/GO
    node ids match CSKG's own node ids without a separate re-mapping step."""
    s = str(label).strip().lower()
    out = []
    prev_us = True
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


# ---------------------------------------------------------------------------------------
# 40 hand-authored probes. Provenance: general world/science knowledge, authored this cycle by
# exp_dev, independent of CauseNet/GO/any ingested source. See prereg NO_LEAK_AUDIT note.
PROBES = [
    # combustion / fire (5)
    {"id": "p01", "subject": "combustion", "object": "oxygen", "domain": "combustion",
     "gloss": "combustion consumes oxygen"},
    {"id": "p02", "subject": "combustion", "object": "carbon dioxide", "domain": "combustion",
     "gloss": "combustion produces carbon dioxide"},
    {"id": "p03", "subject": "fire", "object": "heat", "domain": "combustion",
     "gloss": "fire produces heat"},
    {"id": "p04", "subject": "candle", "object": "wax", "domain": "combustion",
     "gloss": "a burning candle consumes wax"},
    {"id": "p05", "subject": "explosion", "object": "shockwave", "domain": "combustion",
     "gloss": "an explosion produces a shockwave"},
    # weather / water cycle (5)
    {"id": "p06", "subject": "evaporation", "object": "water vapor", "domain": "weather",
     "gloss": "evaporation produces water vapor"},
    {"id": "p07", "subject": "condensation", "object": "cloud", "domain": "weather",
     "gloss": "condensation produces clouds"},
    {"id": "p08", "subject": "rain", "object": "flood", "domain": "weather",
     "gloss": "heavy rain causes flooding"},
    {"id": "p09", "subject": "wind", "object": "erosion", "domain": "weather",
     "gloss": "wind causes erosion"},
    {"id": "p10", "subject": "sunlight", "object": "evaporation", "domain": "weather",
     "gloss": "sunlight causes evaporation"},
    # general plant biology, non-GO-jargon (5)
    {"id": "p11", "subject": "photosynthesis", "object": "glucose", "domain": "plant_biology",
     "gloss": "photosynthesis produces glucose"},
    {"id": "p12", "subject": "photosynthesis", "object": "oxygen", "domain": "plant_biology",
     "gloss": "photosynthesis produces oxygen"},
    {"id": "p13", "subject": "root", "object": "water", "domain": "plant_biology",
     "gloss": "roots absorb water"},
    {"id": "p14", "subject": "seed", "object": "sprout", "domain": "plant_biology",
     "gloss": "a germinating seed produces a sprout"},
    {"id": "p15", "subject": "pollination", "object": "fruit", "domain": "plant_biology",
     "gloss": "pollination leads to fruit"},
    # human physiology / everyday (8)
    {"id": "p16", "subject": "exercise", "object": "sweat", "domain": "physiology",
     "gloss": "exercise produces sweat"},
    {"id": "p17", "subject": "exercise", "object": "muscle", "domain": "physiology",
     "gloss": "exercise builds muscle"},
    {"id": "p18", "subject": "digestion", "object": "nutrients", "domain": "physiology",
     "gloss": "digestion produces nutrients"},
    {"id": "p19", "subject": "hunger", "object": "eating", "domain": "physiology",
     "gloss": "hunger causes eating"},
    {"id": "p20", "subject": "dehydration", "object": "thirst", "domain": "physiology",
     "gloss": "dehydration causes thirst"},
    {"id": "p21", "subject": "infection", "object": "fever", "domain": "physiology",
     "gloss": "infection causes fever"},
    {"id": "p22", "subject": "sunburn", "object": "skin peeling", "domain": "physiology",
     "gloss": "sunburn causes skin peeling"},
    {"id": "p23", "subject": "alcohol", "object": "intoxication", "domain": "physiology",
     "gloss": "alcohol causes intoxication"},
    # mechanical / physics (6)
    {"id": "p24", "subject": "friction", "object": "heat", "domain": "physics",
     "gloss": "friction produces heat"},
    {"id": "p25", "subject": "engine", "object": "exhaust", "domain": "physics",
     "gloss": "an engine produces exhaust"},
    {"id": "p26", "subject": "pressure", "object": "deformation", "domain": "physics",
     "gloss": "pressure causes deformation"},
    {"id": "p27", "subject": "magnet", "object": "attraction", "domain": "physics",
     "gloss": "a magnet causes attraction"},
    {"id": "p28", "subject": "battery", "object": "electric current", "domain": "physics",
     "gloss": "a battery produces electric current"},
    {"id": "p29", "subject": "lightning", "object": "thunder", "domain": "physics",
     "gloss": "lightning causes thunder"},
    # household chemistry / cooking (6)
    {"id": "p30", "subject": "yeast", "object": "carbon dioxide", "domain": "chemistry",
     "gloss": "yeast fermentation produces carbon dioxide"},
    {"id": "p31", "subject": "baking soda", "object": "bubbles", "domain": "chemistry",
     "gloss": "baking soda reacting with vinegar produces bubbles"},
    {"id": "p32", "subject": "oxidation", "object": "rust", "domain": "chemistry",
     "gloss": "oxidation of iron produces rust"},
    {"id": "p33", "subject": "fermentation", "object": "alcohol", "domain": "chemistry",
     "gloss": "fermentation produces alcohol"},
    {"id": "p34", "subject": "freezing", "object": "ice", "domain": "chemistry",
     "gloss": "freezing produces ice"},
    {"id": "p35", "subject": "boiling", "object": "steam", "domain": "chemistry",
     "gloss": "boiling water produces steam"},
    # astronomy / geology (5)
    {"id": "p36", "subject": "earthquake", "object": "tsunami", "domain": "geology",
     "gloss": "an undersea earthquake can cause a tsunami"},
    {"id": "p37", "subject": "volcano", "object": "lava", "domain": "geology",
     "gloss": "a volcanic eruption produces lava"},
    {"id": "p38", "subject": "erosion", "object": "canyon", "domain": "geology",
     "gloss": "erosion over time produces canyons"},
    {"id": "p39", "subject": "gravity", "object": "tide", "domain": "geology",
     "gloss": "gravity causes tides"},
    {"id": "p40", "subject": "sun", "object": "daylight", "domain": "geology",
     "gloss": "the sun produces daylight"},
]
assert len(PROBES) == 40, ("probe count drifted", len(PROBES))
assert len({p["id"] for p in PROBES}) == 40, "duplicate probe ids"


# ---------------------------------------------------------------------------------------
def load_baseline_edges(cskg_dir, output_dir, t0, line_cap=None):
    """Read all spine typed edges from edges_shard_*.jsonl + heldout_edges.jsonl. Returns
    list[(subj_canon, relation, obj_canon)] (already canon'd on disk by exp_cskg_foundation_v1, but
    we re-canon defensively so this cell is correct even if fed a differently-normalized source)."""
    edges = []
    files = sorted(
        Path(cskg_dir).glob("edges_shard_*.jsonl")
    ) + [Path(cskg_dir) / "heldout_edges.jsonl"]
    n_lines = 0
    for fp in files:
        if not fp.exists():
            continue
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                if line_cap is not None and n_lines >= line_cap:
                    break
                line = line.strip()
                if not line:
                    continue
                n_lines += 1
                row = json.loads(line)
                s = canon(row["subject"])
                o = canon(row["obj"])
                r = row["relation"]
                if s and o and s != o:
                    edges.append((s, r, o))
        if line_cap is not None and n_lines >= line_cap:
            break
    _hb(output_dir, "baseline_loaded", t0, {"n_edges": len(edges), "n_lines_read": n_lines})
    return edges


_CAUSENET_PAT = re.compile(
    r'"cause":\s*\{"concept":\s*"((?:[^"\\]|\\.)*)"\}.*?"effect":\s*\{"concept":\s*"((?:[^"\\]|\\.)*)"\}'
)


def _extract_causenet_pairs(bz2_path, output_dir, t0, line_cap=None):
    """Fast regex extraction of (cause, effect) concept pairs from CauseNet-Precision JSONL, without
    a full json.loads of each (megabyte-scale, provenance-heavy) row. Only the first 400 chars of each
    line are scanned -- the causal_relation block is always the first key, per the CauseNet schema
    (verified by inspection this cycle). Returns list[(cause_canon, "cn:Causes", effect_canon)],
    deduped + self-loop-dropped via sorted(set(...)) (deterministic)."""
    raw_pairs = []
    n_lines = 0
    with bz2.open(bz2_path, "rt", encoding="utf-8") as f:
        for line in f:
            if line_cap is not None and n_lines >= line_cap:
                break
            n_lines += 1
            m = _CAUSENET_PAT.search(line[:400])
            if m:
                c = canon(m.group(1))
                e = canon(m.group(2))
                if c and e and c != e:
                    raw_pairs.append((c, NEW_CAUSENET_REL, e))
    deduped = sorted(set(raw_pairs))
    _hb(output_dir, "causenet_parsed", t0,
        {"n_lines": n_lines, "n_raw_pairs": len(raw_pairs), "n_unique_pairs": len(deduped)})
    return deduped, n_lines


def _extract_go_regulates(obo_path, output_dir, t0, max_terms=None):
    """Parse go.obo via the EXISTING hdlab.director_kb_bio_sources.parse_gene_ontology() (already-
    owned schema-as-config extractor, obo_go mode; zero new parser engineering). Resolves REGULATES-
    family triples (term_id -> term_id) to canon'd term NAMES via the same parse's NAMED triples, so
    edges land in the same node-id space as the probe/CauseNet/CSKG graph. Returns list[(subj_canon,
    rel, obj_canon)], deduped + self-loop-dropped via sorted(set(...))."""
    from hdlab.director_kb_bio_sources import parse_gene_ontology  # noqa: PLC0415

    triples = parse_gene_ontology(Path(obo_path), max_terms=max_terms)
    name_of = {}
    for t in triples:
        if t["p"] == "NAMED":
            name_of[t["s"]] = t["o"]
    raw_edges = []
    n_regulates_raw = 0
    for t in triples:
        if t["p"] not in GO_REGULATES_RELS:
            continue
        n_regulates_raw += 1
        ns = name_of.get(t["s"])
        no = name_of.get(t["o"])
        if not ns or not no:
            continue
        cs, co = canon(ns), canon(no)
        if cs and co and cs != co:
            raw_edges.append((cs, t["p"], co))
    deduped = sorted(set(raw_edges))
    _hb(output_dir, "go_parsed", t0,
        {"n_triples": len(triples), "n_regulates_raw": n_regulates_raw,
         "n_regulates_resolved": len(deduped)})
    return deduped


def build_adjacency(edges):
    """edges: list[(s, r, o)]. Returns dict[node] -> list[(neighbor, relation)], both directions
    recorded so the recovery query is direction-agnostic (matches 'reconstructable via a graph query',
    not a strict-direction traversal)."""
    adj = defaultdict(list)
    for s, r, o in edges:
        adj[s].append((o, r))
        adj[o].append((s, r))
    return adj


def _recover(adj, causal_rels, subject, obj):
    """Returns hop count (1 or 2) if RECOVERED, else 0. 1-hop: a single causal-typed edge connects
    subject<->obj. 2-hop: a mid node exists with BOTH hops causal-typed (subject<->mid, mid<->obj).
    Every hop on the path must be causal_rels-typed (strict; see prereg RECOVERY-FUNCTION section)."""
    subj_edges = adj.get(subject, ())
    for n, r in subj_edges:
        if n == obj and r in causal_rels:
            return 1
    causal_mids = {n for n, r in subj_edges if r in causal_rels and n != obj}
    for mid in causal_mids:
        for n2, r2 in adj.get(mid, ()):
            if n2 == obj and r2 in causal_rels:
                return 2
    return 0


def _edge_set_hash(edges):
    """Deterministic hash of a sorted edge list, for the arms-must-differ check (META_RULE_AF)."""
    payload = "\n".join(f"{s}|{r}|{o}" for s, r, o in sorted(set(edges)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_random_control_edges(baseline_edges, new_source_edges, n_random, output_dir, t0):
    """BASELINE-node-pool UNION new-source-entity-pool endpoints, non-causal relation type sampled
    from BASELINE's own non-causal relation-frequency distribution (not a synthetic sentinel -- a
    more realistic 'same kind of graph noise' control). Deterministic seeds (RANDOM_ENDPOINT_SEED /
    RANDOM_REL_SEED), np.random.default_rng only."""
    baseline_nodes = set()
    rel_counts = Counter()
    for s, r, o in baseline_edges:
        baseline_nodes.add(s)
        baseline_nodes.add(o)
        rel_counts[r] += 1
    new_entity_names = set()
    for s, _r, o in new_source_edges:
        new_entity_names.add(s)
        new_entity_names.add(o)
    pool = sorted(baseline_nodes | new_entity_names)
    pool_arr = np.array(pool, dtype=object)

    noncausal_rels = sorted(r for r in rel_counts if r not in ENRICHED_CAUSAL_RELS)
    noncausal_weights = np.array([rel_counts[r] for r in noncausal_rels], dtype=np.float64)
    noncausal_weights = noncausal_weights / noncausal_weights.sum()

    rng_ep = np.random.default_rng(RANDOM_ENDPOINT_SEED)
    rng_rel = np.random.default_rng(RANDOM_REL_SEED)

    # oversample slightly to absorb self-loop drops, then truncate to exactly n_random
    oversample = int(n_random * 1.02) + 10
    idx_u = rng_ep.integers(0, len(pool_arr), size=oversample)
    idx_v = rng_ep.integers(0, len(pool_arr), size=oversample)
    rel_choices = rng_rel.choice(noncausal_rels, size=oversample, p=noncausal_weights)

    out = []
    for i in range(oversample):
        if len(out) >= n_random:
            break
        u, v = pool_arr[idx_u[i]], pool_arr[idx_v[i]]
        if u == v:
            continue
        out.append((str(u), str(rel_choices[i]), str(v)))
    assert len(out) == n_random, ("random-control oversample exhausted", len(out), n_random)
    _hb(output_dir, "random_control_built", t0,
        {"n_random_edges": len(out), "pool_size": len(pool_arr), "n_noncausal_rel_types": len(noncausal_rels)})
    return out


def compute_recovery(adj, causal_rels, probes):
    results = []
    for p in probes:
        s, o = canon(p["subject"]), canon(p["object"])
        hop = _recover(adj, causal_rels, s, o)
        results.append({"id": p["id"], "domain": p["domain"], "gloss": p["gloss"],
                         "subject": s, "object": o, "hop": hop, "recovered": hop > 0})
    rate = sum(1 for r in results if r["recovered"]) / len(results)
    hop1 = sum(1 for r in results if r["hop"] == 1) / len(results)
    hop2 = sum(1 for r in results if r["hop"] == 2) / len(results)
    return {"recovery_rate": round(rate, 4), "hop1_rate": round(hop1, 4), "hop2_rate": round(hop2, 4),
            "per_probe": results}


# ---------------------------------------------------------------------------------------
def gate_verdict(baseline_rate, enriched_rate, shuffle_rate, random_rate):
    gain = enriched_rate - baseline_rate
    shuffle_delta = abs(shuffle_rate - baseline_rate)
    random_delta_baseline = abs(random_rate - baseline_rate)
    random_delta_enriched = abs(random_rate - enriched_rate)
    shuffle_collapse_ok = shuffle_delta <= GATE_SHUFFLE_COLLAPSE_TOL
    random_stays_low_ok = random_delta_baseline <= GATE_RANDOM_STAYLOW_TOL
    random_matches_enriched = random_delta_enriched <= GATE_RANDOM_MATCHES_ENRICHED_TOL

    if gain < GATE_HARD_FAIL_GAIN or (not shuffle_collapse_ok) or random_matches_enriched:
        verdict = "HARD_FAIL"
    elif gain >= GATE_HARD_PASS_GAIN and shuffle_collapse_ok and random_stays_low_ok:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"
    return {
        "verdict": verdict, "gain": round(gain, 4),
        "shuffle_delta_from_baseline": round(shuffle_delta, 4),
        "random_delta_from_baseline": round(random_delta_baseline, 4),
        "random_delta_from_enriched": round(random_delta_enriched, 4),
        "shuffle_collapse_ok": bool(shuffle_collapse_ok),
        "random_stays_low_ok": bool(random_stays_low_ok),
        "random_matches_enriched": bool(random_matches_enriched),
        "bands": {
            "hard_pass": f"gain>={GATE_HARD_PASS_GAIN} AND shuffle_delta<={GATE_SHUFFLE_COLLAPSE_TOL} AND random_delta<={GATE_RANDOM_STAYLOW_TOL}",
            "hard_fail": f"gain<{GATE_HARD_FAIL_GAIN} OR shuffle_delta>{GATE_SHUFFLE_COLLAPSE_TOL} OR random_matches_enriched(<=  {GATE_RANDOM_MATCHES_ENRICHED_TOL})",
        },
    }


def causal_edge_fraction(edges, rel_set):
    if not edges:
        return 0.0
    n = sum(1 for _s, r, _o in edges if r in rel_set)
    return round(n / len(edges), 6)


# ---------------------------------------------------------------------------------------
def run(run_mode, output_dir, causenet_line_cap=None, go_max_terms=None, baseline_line_cap=None,
        n_probes_override=None):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode)
    _hb(output_dir, "begin", t0, {"run_mode": run_mode})

    probes = PROBES if n_probes_override is None else PROBES[:n_probes_override]

    baseline_edges = load_baseline_edges(CSKG_DIR, output_dir, t0, line_cap=baseline_line_cap)

    # ---- positive-control reproduction of the scout's disk-verified 14.83% generous-bucket figure --
    rel_counts_baseline = Counter(r for _s, r, _o in baseline_edges)
    generous_sum = sum(rel_counts_baseline.get(r, 0) for r in CAUSAL_RELS_BASE)
    generous_frac_baseline_reproduction = (generous_sum / len(baseline_edges)) if baseline_edges else 0.0

    causenet_edges, n_causenet_lines = _extract_causenet_pairs(
        CAUSENET_BZ2, output_dir, t0, line_cap=causenet_line_cap)
    go_edges = _extract_go_regulates(GO_OBO, output_dir, t0, max_terms=go_max_terms)
    new_source_edges = causenet_edges + go_edges

    enriched_edges = baseline_edges + new_source_edges

    # ---- SHUFFLE control: permute relation labels across the FULL enriched edge list -------------
    rng_shuf = np.random.default_rng(SHUFFLE_SEED)
    n_enriched = len(enriched_edges)
    perm = rng_shuf.permutation(n_enriched)
    subs = [e[0] for e in enriched_edges]
    objs = [e[2] for e in enriched_edges]
    rels = [e[1] for e in enriched_edges]
    shuffled_rels = [rels[i] for i in perm]
    shuffle_edges = list(zip(subs, shuffled_rels, objs))

    # ---- RANDOM-EDGES control: baseline + equal-count random non-causal edges ---------------------
    random_new_edges = build_random_control_edges(
        baseline_edges, new_source_edges, len(new_source_edges), output_dir, t0)
    random_control_edges = baseline_edges + random_new_edges

    # ---- arms-must-differ (META_RULE_AF) ------------------------------------------------------------
    hashes = {
        "baseline": _edge_set_hash(baseline_edges),
        "enriched": _edge_set_hash(enriched_edges),
        "shuffle": _edge_set_hash(shuffle_edges),
        "random": _edge_set_hash(random_control_edges),
    }
    pairs = sorted(hashes.keys())
    arm_collisions = []
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            a, b = pairs[i], pairs[j]
            if hashes[a] == hashes[b]:
                arm_collisions.append((a, b))
    arms_differ_verified = len(arm_collisions) == 0

    # ---- build adjacency + recovery per condition ---------------------------------------------------
    conditions = {}
    for name, edges in (("baseline", baseline_edges), ("enriched", enriched_edges),
                         ("shuffle", shuffle_edges), ("random", random_control_edges)):
        adj = build_adjacency(edges)
        rec = compute_recovery(adj, ENRICHED_CAUSAL_RELS, probes)
        conditions[name] = {"n_edges": len(edges), **rec}
        _hb(output_dir, f"recovery_{name}", t0,
            {"n_edges": len(edges), "recovery_rate": rec["recovery_rate"]})
        del adj  # free memory before next condition

    GATE = gate_verdict(
        conditions["baseline"]["recovery_rate"], conditions["enriched"]["recovery_rate"],
        conditions["shuffle"]["recovery_rate"], conditions["random"]["recovery_rate"])

    # ---- causal-edge-fraction gap-closure metric (strict + generous buckets) ------------------------
    frac_strict_baseline = causal_edge_fraction(baseline_edges, STRICT_CAUSAL_RELS)
    frac_strict_enriched = causal_edge_fraction(enriched_edges, STRICT_CAUSAL_RELS)
    frac_generous_baseline = causal_edge_fraction(baseline_edges, ENRICHED_CAUSAL_RELS)
    frac_generous_enriched = causal_edge_fraction(enriched_edges, ENRICHED_CAUSAL_RELS)

    elapsed_s = round(time.perf_counter() - t0, 1)
    metrics = {
        "verdict": GATE["verdict"], "run_mode": run_mode,
        "verdict_msg": (
            f"causal enrichment probe recovery {run_mode}: baseline={conditions['baseline']['recovery_rate']} "
            f"enriched={conditions['enriched']['recovery_rate']} shuffle={conditions['shuffle']['recovery_rate']} "
            f"random={conditions['random']['recovery_rate']} gain={GATE['gain']} "
            f"gate={GATE['verdict']} (shuffle_ok={GATE['shuffle_collapse_ok']} random_ok={GATE['random_stays_low_ok']})"
        ),
        "summary": f"CAUSAL_ENRICHMENT_PROBE_RECOVERY {run_mode} {GATE['verdict']}",
        "elapsed_s": elapsed_s, "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME, "pid": os.getpid(),
        "n_probes": len(probes),
        "conditions": conditions,
        "gate": GATE,
        "arms_differ_verified": arms_differ_verified,
        "arm_edge_hashes": hashes,
        "arm_hash_collisions": arm_collisions,
        "causenet_n_lines": n_causenet_lines, "causenet_n_unique_pairs": len(causenet_edges),
        "go_n_regulates_resolved": len(go_edges),
        "n_new_source_edges": len(new_source_edges),
        "generous_bucket_reproduction": {
            "sum_edges": generous_sum, "baseline_n_edges": len(baseline_edges),
            "frac": round(generous_frac_baseline_reproduction, 4),
            "scout_disk_verified_ref": 0.1483,
            "reproduction_ok": abs(generous_frac_baseline_reproduction - 0.1483) <= 0.001,
        },
        "causal_edge_fraction": {
            "strict_bucket_rels": sorted(STRICT_CAUSAL_RELS),
            "generous_bucket_rels": sorted(ENRICHED_CAUSAL_RELS),
            "strict_baseline": frac_strict_baseline, "strict_enriched": frac_strict_enriched,
            "generous_baseline": frac_generous_baseline, "generous_enriched": frac_generous_enriched,
        },
        "prereg": PREREG_PATH,
        "sources": {
            "causenet_precision_bz2": CAUSENET_BZ2, "causenet_license": "CC BY 4.0",
            "go_obo_full": GO_OBO, "go_license": "CC BY 4.0",
        },
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    fin = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, fin)
    print(f"[done] {metrics['summary']} elapsed={metrics['elapsed_s']}s -> {fin}", flush=True)
    return metrics


# ---------------------------------------------------------------------------------------
def self_test():
    """Real-code-path self-test at tiny scale: reads a real sample of edges_shard_00.jsonl, calls the
    REAL parse_gene_ontology() against the REAL go.obo (capped max_terms=50), regex-parses the first
    ~200 real lines of the REAL causenet-precision.jsonl.bz2, and exercises the full run() pipeline
    end-to-end on a reduced probe subset. Includes a known-positive and known-negative sanity check on
    the recovery function itself (guards against a vacuously-always-true/false implementation)."""
    import tempfile
    exercised = set()

    out = tempfile.mkdtemp(prefix="causal_enrich_selftest_")
    t0 = time.perf_counter()

    baseline_edges = load_baseline_edges(CSKG_DIR, out, t0, line_cap=5000)
    exercised.add("load_baseline_edges")
    assert len(baseline_edges) > 100, ("too few baseline edges in sample", len(baseline_edges))

    causenet_edges, n_lines = _extract_causenet_pairs(CAUSENET_BZ2, out, t0, line_cap=200)
    exercised.add("_extract_causenet_pairs")
    assert n_lines == 200, ("causenet line cap not honored", n_lines)
    assert len(causenet_edges) > 50, ("too few causenet pairs extracted from first 200 lines", len(causenet_edges))
    assert all(r == NEW_CAUSENET_REL for _s, r, _o in causenet_edges), "causenet edges mis-typed"

    go_edges = _extract_go_regulates(GO_OBO, out, t0, max_terms=None)
    exercised.add("_extract_go_regulates")
    # max_terms caps [Term] STANZAS processed by parse_gene_ontology, not regulates-edge count
    # directly (a term's regulates lines only land if the TARGET term also got a NAMED triple within
    # the cap); use the full parse here (fast, 1.2s measured) and just assert regulates edges exist.
    assert len(go_edges) > 100, ("too few GO regulates edges resolved", len(go_edges))
    assert all(r in GO_REGULATES_RELS for _s, r, _o in go_edges), "GO edges mis-typed"

    # ---- recovery-function positive/negative sanity (real code path, real data) -------------------
    adj = build_adjacency(baseline_edges)
    exercised.add("build_adjacency")
    # positive control: pick a real 1-hop causal edge from the loaded sample
    known_causal = next(((s, o) for s, r, o in baseline_edges if r in CAUSAL_RELS_BASE), None)
    assert known_causal is not None, "no causal-typed edge in the 5000-line baseline sample (unlucky shard?)"
    hop = _recover(adj, ENRICHED_CAUSAL_RELS, known_causal[0], known_causal[1])
    assert hop == 1, ("known-present causal edge failed to recover", known_causal, hop)
    exercised.add("_recover_positive")
    # negative control: two synthetic tokens guaranteed absent from the sample
    hop0 = _recover(adj, ENRICHED_CAUSAL_RELS, "zzz_selftest_nonexistent_a", "zzz_selftest_nonexistent_b")
    assert hop0 == 0, ("recovery function is vacuously true", hop0)
    exercised.add("_recover_negative")

    # ---- canon() sanity ------------------------------------------------------------------------------
    assert canon("Carbon Dioxide!!") == "carbon_dioxide", canon("Carbon Dioxide!!")
    exercised.add("canon")

    # ---- end-to-end pipeline on a reduced probe subset (5 probes, small caps) ----------------------
    m = run("self_test", os.path.join(out, "run"), causenet_line_cap=2000, go_max_terms=None,
            baseline_line_cap=5000, n_probes_override=5)
    exercised.add("run")
    assert m["n_probes"] == 5
    assert m["arms_differ_verified"], ("self-test arms collided", m["arm_hash_collisions"])
    assert m["gate"]["verdict"] in ("HARD_PASS", "MIDDLE_BAND", "HARD_FAIL")
    exercised.add("gate_verdict")

    need = {"load_baseline_edges", "_extract_causenet_pairs", "_extract_go_regulates",
            "build_adjacency", "_recover_positive", "_recover_negative", "canon", "run", "gate_verdict"}
    missing = need - exercised
    assert not missing, ("self-test skipped real entrypoints", missing)
    print(f"[self_test] PASS exercised={sorted(exercised)} "
          f"baseline_causal_edge_example={known_causal} "
          f"causenet_pairs={len(causenet_edges)} go_regulates={len(go_edges)}", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    output_dir = ART_DIR if mode == "full" else os.path.join(REPO, "data", f"exp_{ANCHOR_NAME}_{mode}")
    global _OUTPUT_DIR
    _OUTPUT_DIR = output_dir
    if mode == "self_test":
        self_test()
        return
    run(mode, output_dir)


_OUTPUT_DIR = ART_DIR

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
