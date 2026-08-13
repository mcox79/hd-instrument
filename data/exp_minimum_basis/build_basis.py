"""ANALYSIS-ONLY (2026-08-13). Minimum grounded basis: derivation + brain-fidelity falsification.

Writes ONLY under data/exp_minimum_basis/. No hdlab/ or tools/ edit. No git add/commit.
Nothing written to any canonical foundation path. ASCII-only. OMP/OPENBLAS pinned to 1.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import csv
import json
import re
import sys
import time
from collections import defaultdict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

OUT = os.path.dirname(os.path.abspath(__file__))

from hdlab.closed_class_lexicon import is_eligible_meaning
from hdlab.thematic_role_labeler import lemma_word

TOK = re.compile(r"[A-Za-z][A-Za-z'\-]*")

_LEM_CACHE = {}


def lem(w):
    v = _LEM_CACHE.get(w)
    if v is None:
        v = lemma_word(w)
        _LEM_CACHE[w] = v
    return v


# ============================================================ 1. corpus vocabulary
CORPUS_CACHE = os.path.join(OUT, "corpus_vocab.json")


def corpus_vocab():
    if os.path.exists(CORPUS_CACHE):
        with open(CORPUS_CACHE, encoding="utf-8") as f:
            d = json.load(f)
        return d["freq"], d["n_sentences"]
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5
    t0 = time.time()
    stream = load_corpus_v5(None, lineaware=True)
    print("[corpus] %d sentences loaded %.0fs" % (len(stream), time.time() - t0), flush=True)
    freq = defaultdict(int)
    for _seg, s in stream:
        for t in TOK.findall(s):
            freq[lem(t)] += 1
    freq = {k: v for k, v in sorted(freq.items())}
    with open(CORPUS_CACHE, "w", encoding="utf-8") as f:
        json.dump({"freq": freq, "n_sentences": len(stream)}, f)
    print("[corpus] %d distinct lemmas %.0fs" % (len(freq), time.time() - t0), flush=True)
    return freq, len(stream)


# ============================================================ 2. relational graph
FACT_FILES = [
    ("v5", "data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl"),
    ("v62", "data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl"),
    ("v4", "data/foundation/reading_grounding_v4_parsefix/definitional_facts_v4.jsonl"),
    ("v3", "data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl"),
]


def subject_lemma(rec):
    """Definiendum -> single lemma identity. Prefer the extractor's own head lemma; else the
    lemma of the LAST token of the subject surface (English NPs are head-final)."""
    h = rec.get("subject_head_lemma")
    if h:
        return lem(h)
    toks = TOK.findall(rec.get("subject", ""))
    return lem(toks[-1]) if toks else ""


def build_graph(sets_used):
    """Edge semantics: a definitional fact (SUBJ, REL, OBJ) says SUBJ's meaning is expressed in
    terms of OBJ. For GROUNDING/bridging the useful direction is the REVERSE: if OBJ is grounded,
    SUBJ becomes reachable in one hop. So the graph edge is OBJ -> SUBJ (`enables`).
    Self-loops (SUBJ == OBJ, the tautology class) are dropped -- they carry no bridge."""
    edges = defaultdict(set)          # obj -> {subj}
    prov = defaultdict(set)           # (obj,subj) -> {source set}
    n_raw = n_self = n_kept = 0
    per_set = {}
    for tag, rel in FACT_FILES:
        if tag not in sets_used:
            continue
        c_raw = c_self = c_kept = 0
        path = os.path.join(REPO_ROOT, rel)
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                s = subject_lemma(rec)
                o = lem(str(rec.get("object", "")))
                c_raw += 1
                if not s or not o:
                    continue
                if s == o:
                    c_self += 1
                    continue
                edges[o].add(s)
                prov[(o, s)].add(tag)
                c_kept += 1
        per_set[tag] = {"rows": c_raw, "self_loops": c_self, "edges_kept": c_kept}
        n_raw += c_raw
        n_self += c_self
        n_kept += c_kept
    nodes = sorted(set(edges) | {s for v in edges.values() for s in v})
    stats = {"per_set": per_set, "rows": n_raw, "self_loops": n_self, "edge_instances": n_kept,
             "distinct_edges": len(prov), "nodes": len(nodes)}
    return edges, nodes, stats


def reach(edges, src, k):
    """Nodes reachable from src in <= k hops, inclusive of src."""
    seen = {src}
    frontier = {src}
    for _ in range(k):
        nxt = set()
        for u in frontier:
            for v in edges.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    nxt.add(v)
        if not nxt:
            break
        frontier = nxt
    return seen


# ============================================================ 3. greedy set cover
def greedy_cover(edges, candidates, target, k, max_picks):
    """Classic greedy max-coverage. APPROXIMATION (1 - 1/e guarantee for max-coverage,
    H(n)-approx for set-cover); NOT the true optimum, which is NP-hard."""
    R = {c: reach(edges, c, k) & target for c in candidates}
    covered = set()
    picks = []
    remaining = dict(R)
    while len(picks) < max_picks:
        best, best_gain = None, 0
        for c in sorted(remaining):
            g = len(remaining[c] - covered)
            if g > best_gain or (g == best_gain and best is None and g > 0):
                best, best_gain = c, g
        if best is None or best_gain == 0:
            break
        newly = remaining[best] - covered
        covered |= newly
        picks.append({"lemma": best, "gain": best_gain, "cum": len(covered),
                      "cum_frac_target": round(len(covered) / max(1, len(target)), 6)})
        del remaining[best]
    return picks, covered


# ============================================================ 4. norms
def load_concreteness():
    d = {}
    p = os.path.join(REPO_ROOT, "data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt")
    with open(p, encoding="utf-8", errors="ignore") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row.get("Bigram") != "0":
                continue
            try:
                d[row["Word"].strip().lower()] = float(row["Conc.M"])
            except (ValueError, KeyError, AttributeError):
                pass
    return d


def load_aoa():
    d = {}
    p = os.path.join(REPO_ROOT, "data/grounding_testbed/AoA_51715_words.csv")
    with open(p, encoding="utf-8", errors="ignore") as f:
        for row in csv.DictReader(f):
            v = (row.get("AoA_Kup_lem") or "").strip()
            if not v or v.upper() == "NA":
                continue
            try:
                d[row["Word"].strip().lower()] = float(v)
            except ValueError:
                pass
    return d


def load_lancaster():
    d = {}
    p = os.path.join(REPO_ROOT, "data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv")
    with open(p, encoding="utf-8", errors="ignore") as f:
        for row in csv.DictReader(f):
            try:
                d[row["Word"].strip().lower()] = float(row["Max_strength.sensorimotor"])
            except (ValueError, KeyError, AttributeError):
                pass
    return d


def desc(vals):
    import numpy as np
    a = np.asarray(sorted(vals), dtype=float)
    if a.size == 0:
        return {"n": 0}
    return {"n": int(a.size), "mean": round(float(a.mean()), 4), "sd": round(float(a.std(ddof=1)), 4) if a.size > 1 else None,
            "median": round(float(np.median(a)), 4),
            "p10": round(float(np.percentile(a, 10)), 4), "p90": round(float(np.percentile(a, 90)), 4)}


def mwu(a, b):
    """Mann-Whitney U, two-sided, + rank-biserial effect size (a vs b)."""
    from scipy.stats import mannwhitneyu
    import numpy as np
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    if a.size < 3 or b.size < 3:
        return {"n_a": int(a.size), "n_b": int(b.size), "note": "too few"}
    U, p = mannwhitneyu(a, b, alternative="two-sided")
    rbc = 2.0 * U / (a.size * b.size) - 1.0     # +1 = a stochastically larger
    return {"n_a": int(a.size), "n_b": int(b.size), "U": float(U), "p_two_sided": float(p),
            "rank_biserial_a_vs_b": round(float(rbc), 4)}


def compare(name, group, ref, norms):
    out = {}
    for nm, tbl in norms.items():
        ga = [tbl[w] for w in sorted(group) if w in tbl]
        rb = [tbl[w] for w in sorted(ref) if w in tbl]
        out[nm] = {"group": desc(ga), "reference": desc(rb),
                   "group_norm_coverage": round(len(ga) / max(1, len(group)), 4),
                   "ref_norm_coverage": round(len(rb) / max(1, len(ref)), 4),
                   "test": mwu(ga, rb)}
    return {"name": name, "n_group": len(group), "n_reference": len(ref), "by_norm": out}


# ============================================================ main
def main():
    freq, n_sent = corpus_vocab()
    vocab_all = sorted(freq)
    vocab_elig = sorted(w for w in vocab_all if is_eligible_meaning(w))
    print("[vocab] all=%d eligible=%d sentences=%d" % (len(vocab_all), len(vocab_elig), n_sent), flush=True)

    # seed / grounded anchors
    from experiments.exp_reading_grounding_loop_cycle1_v1 import load_base_vocab_seed
    seed_words = load_base_vocab_seed()
    seed_lemmas = sorted({lem(w) for w in sorted(set(seed_words))})
    with open(os.path.join(REPO_ROOT, "data/exp_structured_comparator_v1/arm_STRUCTURED_provenance.json"),
              encoding="utf-8") as f:
        prov_s = json.load(f)
    grounded = sorted({r["subject"] for r in prov_s})
    anchor_universe = sorted(set(seed_lemmas) | set(grounded))

    # full base vocabulary file size
    nbase = 0
    with open(os.path.join(REPO_ROOT, "data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv"),
              encoding="utf-8") as f:
        for _ in csv.DictReader(f):
            nbase += 1

    report = {"corpus": {"n_sentences": n_sent, "n_lemmas_all": len(vocab_all),
                         "n_lemmas_eligible": len(vocab_elig)},
              "anchors": {"seed_words": len(seed_words), "seed_lemmas": len(seed_lemmas),
                          "grounded_STRUCTURED": len(grounded),
                          "anchor_universe": len(anchor_universe),
                          "base_vocabulary_rows": nbase}}

    # ---- graph, two configurations
    ev5, nv5, sv5 = build_graph({"v5", "v62"})
    eall, nall, sall = build_graph({"v5", "v62", "v4", "v3"})
    report["graph_v5_v62"] = sv5
    report["graph_all"] = sall

    results = {}
    for gname, (edges, nodes) in (("v5_v62", (ev5, nv5)), ("all", (eall, nall))):
        elig = set(vocab_elig)
        node_set = set(nodes)
        # TARGET = corpus-eligible lemmas that exist in the graph at all (the only ones any
        # covering solution could ever reach). Report vs full corpus separately.
        target = node_set & elig
        cands = sorted(node_set)
        g = {"n_nodes": len(nodes), "n_nodes_in_corpus_eligible": len(target),
             "target_frac_of_corpus_eligible": round(len(target) / len(elig), 6),
             "k": {}}
        for k in (1, 2, 3):
            picks, covered = greedy_cover(edges, cands, target, k, max_picks=len(cands))
            curve = {}
            for thr in (0.50, 0.80, 0.95):
                need = None
                for i, p in enumerate(picks, 1):
                    if p["cum_frac_target"] >= thr:
                        need = i
                        break
                curve["%.2f" % thr] = need
            g["k"][str(k)] = {"picks_total": len(picks), "covered": len(covered),
                              "covered_frac_target": round(len(covered) / max(1, len(target)), 6),
                              "covered_frac_corpus_eligible": round(len(covered) / len(elig), 6),
                              "S_for": curve,
                              "top200": picks[:200]}
        results[gname] = g
    report["cover"] = results

    # ---- brain-fidelity gate on the primary basis: graph=all, k=2, top 200
    norms = {"concreteness_ConcM": load_concreteness(),
             "aoa_Kuperman_lem_years": load_aoa(),
             "lancaster_max_sensorimotor": load_lancaster()}
    report["norms_sizes"] = {k: len(v) for k, v in norms.items()}

    gates = {}
    for gname in ("v5_v62", "all"):
        for k in ("1", "2", "3"):
            picks = results[gname]["k"][k]["top200"]
            basis = sorted({p["lemma"] for p in picks})
            gates["%s_k%s_top200" % (gname, k)] = {
                "vs_corpus_eligible": compare("basis", basis, set(vocab_elig), norms),
                "vs_seed_lemmas": compare("basis", basis, set(seed_lemmas), norms),
                "n_in_seed": sum(1 for w in basis if w in set(seed_lemmas)),
                "n_in_grounded": sum(1 for w in basis if w in set(grounded)),
                "n_in_anchor_universe": sum(1 for w in basis if w in set(anchor_universe)),
                "n_new": sum(1 for w in basis if w not in set(anchor_universe)),
            }
    # reference: seed vs corpus (does the norms battery separate a KNOWN-early set?)
    gates["_reference_seed_vs_corpus"] = compare("seed_lemmas", set(seed_lemmas), set(vocab_elig), norms)
    # reference: pure out-degree hubs (topology-only control)
    hub = sorted(eall, key=lambda x: (-len(eall[x]), x))[:200]
    gates["_reference_outdegree_hubs_top200_vs_corpus"] = compare("hubs", set(hub), set(vocab_elig), norms)
    report["brain_fidelity_gate"] = gates
    report["hub_top30_by_outdegree"] = [[w, len(eall[w])] for w in hub[:30]]

    # ---- seed / basis overlap detail, primary basis
    primary = [p["lemma"] for p in results["all"]["k"]["2"]["top200"]]
    seed_set, gr_set = set(seed_lemmas), set(grounded)
    rows = []
    conc, aoa, lanc = norms["concreteness_ConcM"], norms["aoa_Kuperman_lem_years"], norms["lancaster_max_sensorimotor"]
    for p in results["all"]["k"]["2"]["top200"]:
        w = p["lemma"]
        rows.append({"lemma": w, "gain": p["gain"], "cum": p["cum"],
                     "cum_frac_target": p["cum_frac_target"],
                     "corpus_freq": freq.get(w, 0),
                     "outdeg": len(eall.get(w, ())),
                     "conc": conc.get(w), "aoa": aoa.get(w), "sensorimotor": lanc.get(w),
                     "in_seed": w in seed_set, "in_grounded": w in gr_set,
                     "is_new": (w not in seed_set) and (w not in gr_set)})
    report["primary_basis_note"] = "graph=all(v3+v4+v5+v62), k=2, greedy top-200"
    with open(os.path.join(OUT, "basis_top200.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)

    # ---- seed coverage of the whole graph target
    tgt_all = set(nall) & set(vocab_elig)
    report["seed_vs_target"] = {
        "target_size": len(tgt_all),
        "seed_lemmas_in_target": len(seed_set & tgt_all),
        "grounded_in_target": len(gr_set & tgt_all),
        "anchor_universe_in_target": len(set(anchor_universe) & tgt_all),
        "coverage_by_seed_k1": len(set().union(*[reach(eall, w, 1) for w in sorted(seed_set & set(nall))]) & tgt_all) if (seed_set & set(nall)) else 0,
        "coverage_by_seed_k2": len(set().union(*[reach(eall, w, 2) for w in sorted(seed_set & set(nall))]) & tgt_all) if (seed_set & set(nall)) else 0,
        "coverage_by_anchor_universe_k2": len(set().union(*[reach(eall, w, 2) for w in sorted(set(anchor_universe) & set(nall))]) & tgt_all) if (set(anchor_universe) & set(nall)) else 0,
        "seed_lemmas_present_in_graph": len(seed_set & set(nall)),
    }

    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("cover", "brain_fidelity_gate")}, indent=1))
    print("WROTE", os.path.join(OUT, "metrics.json"), flush=True)


if __name__ == "__main__":
    main()
