"""MEASUREMENT ONLY (2026-08-13). Distance-to-grounded-frontier distribution over the whole
corpus vocabulary, using DEFINITIONAL edges (not co-occurrence).

Writes ONLY into data/exp_frontier_distance/. Modifies no hdlab/ or tools/ file. ASCII-only.
OMP/OPENBLAS pinned to 1. sorted(set(...)) everywhere.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import json
import re
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.reading_grounding_loop import normalize_lemma, content_lemmas, content_words
from hdlab.closed_class_lexicon import is_eligible_meaning
from experiments.exp_reading_grounding_loop_cycle1_v1 import load_base_vocab_seed
from experiments.exp_definitional_grounding_v5 import load_corpus_v5

OUT = os.path.dirname(os.path.abspath(__file__))
D = lambda *p: os.path.join(REPO_ROOT, *p)

_LEM_CACHE = {}


def lem(w):
    r = _LEM_CACHE.get(w)
    if r is None:
        r = normalize_lemma(w)
        _LEM_CACHE[w] = r
    return r


def jload(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def head_lemma(rec):
    """Subject -> single head lemma. v4/v5 carry subject_head_lemma; v3/v62 do not, so the
    LAST alphabetic token of the subject string is used (English NPs are right-headed)."""
    shl = rec.get("subject_head_lemma")
    if shl:
        return lem(str(shl))
    toks = re.findall(r"[A-Za-z][A-Za-z'-]*", str(rec.get("subject", "")))
    return lem(toks[-1]) if toks else ""


def main():
    t0 = time.time()
    report = {}

    # ---------------------------------------------------------------- 1. corpus vocabulary
    corpus = load_corpus_v5(None, lineaware=True)
    print("[1] corpus sentences", len(corpus), flush=True)
    freq = collections.Counter()          # lemma -> # sentences containing it
    tok_total = collections.Counter()     # lemma -> raw token occurrences
    cap_noninitial = collections.Counter()  # lemma -> capitalized, not sentence-initial
    tok_noninitial = collections.Counter()
    TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")
    for _seg, sent in corpus:
        for lm in content_lemmas(sent):
            freq[lm] += 1
        for i, m in enumerate(TOK.finditer(sent)):
            w = m.group(0)
            lm = lem(w)
            tok_total[lm] += 1
            if i > 0:
                tok_noninitial[lm] += 1
                if w[0].isupper():
                    cap_noninitial[lm] += 1
    corpus_vocab = sorted(set(freq))
    eligible = sorted(set(w for w in corpus_vocab if is_eligible_meaning(w)))
    print("[1] distinct content lemmas", len(corpus_vocab), "eligible", len(eligible),
          "%.0fs" % (time.time() - t0), flush=True)

    # ---------------------------------------------------------------- 2. the frontier
    seed_raw = load_base_vocab_seed()
    seed = sorted(set(lem(w) for w in seed_raw))
    prov_s = json.load(open(D("data/exp_structured_comparator_v1/arm_STRUCTURED_provenance.json"),
                            encoding="utf-8"))
    prov_c = json.load(open(D("data/exp_structured_comparator_v1/arm_CONTROL_provenance.json"),
                            encoding="utf-8"))
    grounded_s = sorted(set(lem(r["subject"]) for r in prov_s))
    grounded_c = sorted(set(lem(r["subject"]) for r in prov_c))
    frontier = sorted(set(seed) | set(grounded_s))
    frontier_control = sorted(set(seed) | set(grounded_c))
    report["frontier"] = {
        "seed_words_raw": len(seed_raw),
        "seed_distinct_lemmas": len(seed),
        "grounded_STRUCTURED_rows": len(prov_s),
        "grounded_STRUCTURED_distinct_lemmas": len(grounded_s),
        "grounded_CONTROL_rows": len(prov_c),
        "grounded_CONTROL_distinct_lemmas": len(grounded_c),
        "grounded_STRUCTURED_already_in_seed": len(set(grounded_s) & set(seed)),
        "frontier_size_STRUCTURED": len(frontier),
        "frontier_size_CONTROL": len(frontier_control),
        "seed_lemmas_occurring_in_corpus": len(set(seed) & set(corpus_vocab)),
        "frontier_lemmas_occurring_in_corpus": len(set(frontier) & set(corpus_vocab)),
    }
    print("[2] frontier", report["frontier"], flush=True)

    # ---------------------------------------------------------------- 3. relational graph
    SOURCES = [
        ("v5", "data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl"),
        ("v62", "data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl"),
        ("v4", "data/foundation/reading_grounding_v4_parsefix/definitional_facts_v4.jsonl"),
        ("v3", "data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl"),
    ]
    src_stats = {}
    edges = {}         # (subj, obj) -> list of provenance dicts
    edges_core = {}    # v5 + v62 only
    for tag, rel in SOURCES:
        rows = jload(D(rel))
        pairs, self_loops, empty = set(), 0, 0
        for r in rows:
            s, o = head_lemma(r), lem(str(r.get("object", "")))
            if not s or not o:
                empty += 1
                continue
            if s == o:
                self_loops += 1
                continue
            pairs.add((s, o))
            prov = {"src": tag, "fid": r.get("fid"), "relation": r.get("relation"),
                    "subject_surface": r.get("subject"), "pattern": r.get("pattern"),
                    "n_attestations": r.get("n_attestations"),
                    "subject_type": r.get("subject_type")}
            edges.setdefault((s, o), []).append(prov)
            if tag in ("v5", "v62"):
                edges_core.setdefault((s, o), []).append(prov)
        src_stats[tag] = {"rows": len(rows), "distinct_edges": len(pairs),
                          "self_loops_dropped": self_loops, "unparsable_dropped": empty}
    # incremental coverage in the order v5 -> v62 -> v4 -> v3
    seen, incr = set(), {}
    for tag, _ in SOURCES:
        new = sorted(set(k for k, v in edges.items()
                         if any(p["src"] == tag for p in v)) - seen)
        incr[tag] = len(new)
        seen |= set(new)
    src_stats["_incremental_new_edges_in_order_v5_v62_v4_v3"] = incr
    report["sources"] = src_stats

    def build(edgemap):
        fwd, rev = collections.defaultdict(set), collections.defaultdict(set)
        for (s, o) in edgemap:
            fwd[s].add(o)
            rev[o].add(s)
        return fwd, rev

    fwd_all, rev_all = build(edges)
    fwd_core, rev_core = build(edges_core)
    nodes_all = sorted(set(fwd_all) | set(rev_all))
    nodes_core = sorted(set(fwd_core) | set(rev_core))
    report["graph"] = {
        "ALL4_distinct_edges": len(edges), "ALL4_nodes": len(nodes_all),
        "CORE_v5_v62_distinct_edges": len(edges_core), "CORE_v5_v62_nodes": len(nodes_core),
        "CORE_nodes_in_corpus_vocab": len(set(nodes_core) & set(corpus_vocab)),
        "ALL4_nodes_in_corpus_vocab": len(set(nodes_all) & set(corpus_vocab)),
    }

    # ---------------------------------------------------------------- 4. BFS to frontier
    def bfs(rev, front):
        """dist[x] = min directed hops x->...->frontier along subject->object edges.
        Implemented as BFS from frontier over REVERSED edges."""
        dist = {f: 0 for f in front}
        q = collections.deque(sorted(set(front)))
        while q:
            u = q.popleft()
            for v in sorted(rev.get(u, ())):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    def bfs_undirected(fwd, rev, front):
        adj = collections.defaultdict(set)
        for k, vs in fwd.items():
            adj[k] |= vs
        for k, vs in rev.items():
            adj[k] |= vs
        return bfs(adj, front)

    variants = {
        "CORE_directed": bfs(rev_core, frontier),
        "CORE_undirected": bfs_undirected(fwd_core, rev_core, frontier),
        "ALL4_directed": bfs(rev_all, frontier),
        "ALL4_undirected": bfs_undirected(fwd_all, rev_all, frontier),
    }

    def histo(dist, vocab, fwdmap):
        h = collections.Counter()
        for w in vocab:
            d = dist.get(w)
            if d is None:
                h["UNREACHABLE"] += 1
            elif d >= 4:
                h["4+"] += 1
            else:
                h[str(d)] += 1
        no_out = sum(1 for w in vocab if w not in dist and not fwdmap.get(w))
        return {"hist": dict(h), "n_vocab": len(vocab),
                "unreachable_with_no_outgoing_edge": no_out,
                "unreachable_with_edges_but_no_path":
                    h["UNREACHABLE"] - no_out}

    report["histograms"] = {}
    for name, dist in variants.items():
        fm = fwd_core if name.startswith("CORE") else fwd_all
        if name.endswith("undirected"):
            fm = collections.defaultdict(set)
            base = fwd_core if name.startswith("CORE") else fwd_all
            rbase = rev_core if name.startswith("CORE") else rev_all
            for k, vs in base.items():
                fm[k] |= vs
            for k, vs in rbase.items():
                fm[k] |= vs
        report["histograms"][name] = {
            "all_corpus_lemmas": histo(dist, corpus_vocab, fm),
            "eligible_corpus_lemmas": histo(dist, eligible, fm),
        }

    PRIMARY = "CORE_directed"
    dist = variants[PRIMARY]
    report["primary_variant"] = PRIMARY

    # ---------------------------------------------------------------- 5. breakdowns
    def band(f):
        if f >= 100:
            return "f>=100"
        if f >= 30:
            return "30-99"
        if f >= 10:
            return "10-29"
        if f >= 4:
            return "4-9"
        if f >= 2:
            return "2-3"
        return "1"

    def dkey(w):
        d = dist.get(w)
        return "UNREACHABLE" if d is None else ("4+" if d >= 4 else str(d))

    by_band = collections.defaultdict(collections.Counter)
    for w in corpus_vocab:
        by_band[band(freq[w])][dkey(w)] += 1
    report["by_frequency_band"] = {k: dict(v) for k, v in sorted(by_band.items())}

    # proper-noun heuristic: >=50% of non-sentence-initial token occurrences capitalized,
    # min 2 such occurrences. Corpus-derived; approximate (see notes).
    proper = sorted(set(w for w in corpus_vocab
                        if tok_noninitial.get(w, 0) >= 2
                        and cap_noninitial.get(w, 0) / max(1, tok_noninitial.get(w, 0)) >= 0.5))
    proper_set = set(proper)
    by_proper = collections.defaultdict(collections.Counter)
    for w in corpus_vocab:
        by_proper["PROPER" if w in proper_set else "COMMON"][dkey(w)] += 1
    report["proper_noun_heuristic"] = {
        "rule": "non-sentence-initial capitalized share >= 0.5 with >= 2 such occurrences",
        "n_proper": len(proper), "n_common": len(corpus_vocab) - len(proper),
        "hist": {k: dict(v) for k, v in sorted(by_proper.items())},
    }

    # concreteness
    conc = {}
    with open(D("data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt"),
              encoding="utf-8", errors="ignore") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        ci, cc = hdr.index("Word"), hdr.index("Conc.M")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) <= cc:
                continue
            try:
                conc[p[ci].strip().lower()] = float(p[cc])
            except ValueError:
                pass
    cov = {w: conc[w] for w in corpus_vocab if w in conc}
    by_conc = collections.defaultdict(collections.Counter)
    mean_by_d = collections.defaultdict(list)
    for w in corpus_vocab:
        if w not in cov:
            by_conc["NOT_COVERED"][dkey(w)] += 1
            continue
        c = cov[w]
        b = "conc>=4.0" if c >= 4.0 else ("3.0-3.99" if c >= 3.0 else
                                          ("2.0-2.99" if c >= 2.0 else "conc<2.0"))
        by_conc[b][dkey(w)] += 1
        mean_by_d[dkey(w)].append(c)
    report["by_concreteness"] = {
        "source": "Brysbaert et al. BRM Conc.M",
        "corpus_lemmas_covered": len(cov), "corpus_lemmas_not_covered":
            len(corpus_vocab) - len(cov),
        "hist": {k: dict(v) for k, v in sorted(by_conc.items())},
        "mean_concreteness_by_distance": {
            k: round(sum(v) / len(v), 4) for k, v in sorted(mean_by_d.items()) if v},
        "n_rated_by_distance": {k: len(v) for k, v in sorted(mean_by_d.items())},
    }

    # ---------------------------------------------------------------- 6. distance-1 list
    d1 = sorted(set(w for w in corpus_vocab if dist.get(w) == 1))
    top = sorted(d1, key=lambda w: (-freq[w], w))[:100]
    bridging = []
    for w in top:
        tgts = sorted(set(o for o in fwd_core.get(w, ()) if dist.get(o) == 0))
        rows = []
        for o in tgts[:3]:
            for p in edges_core[(w, o)][:1]:
                rows.append({"object": o, "src": p["src"], "fid": p["fid"],
                             "relation": p["relation"], "pattern": p["pattern"],
                             "subject_surface": p["subject_surface"],
                             "n_attestations": p["n_attestations"],
                             "object_role": ("seed" if o in set(seed) else "grounded")})
        bridging.append({"lemma": w, "corpus_freq": freq[w],
                         "n_frontier_objects": len(tgts), "bridges": rows,
                         "proper": w in proper_set,
                         "concreteness": cov.get(w)})
    report["distance_1"] = {"count_all_corpus_lemmas": len(d1),
                            "count_eligible": sum(1 for w in eligible if dist.get(w) == 1)}
    report["distance_1_top100_by_corpus_freq"] = bridging

    # ---------------------------------------------------------------- 7. degree distribution
    outdeg = collections.Counter({k: len(v) for k, v in fwd_core.items()})
    indeg = collections.Counter({k: len(v) for k, v in rev_core.items()})
    # weighted in-degree = number of FACTS pointing at the object
    fact_in = collections.Counter()
    for (s, o), ps in edges_core.items():
        fact_in[o] += len(ps)
    n_edges = len(edges_core)
    top_in = indeg.most_common(30)
    cum = 0
    hub_curve = []
    for i, (w, dg) in enumerate(top_in, 1):
        cum += dg
        hub_curve.append({"rank": i, "node": w, "in_degree": dg,
                          "cum_share_of_edges": round(cum / n_edges, 4),
                          "is_frontier": w in set(frontier)})
    # how many distance-1 lemmas reach the frontier ONLY via a top-10 hub
    top10 = set(w for w, _ in top_in[:10])
    only_hub = sum(1 for w in d1
                   if set(o for o in fwd_core.get(w, ()) if dist.get(o) == 0) <= top10
                   and set(o for o in fwd_core.get(w, ()) if dist.get(o) == 0))
    report["degree"] = {
        "n_nodes": len(nodes_core), "n_edges": n_edges,
        "mean_out_degree": round(n_edges / max(1, len(set(fwd_core))), 4),
        "mean_in_degree": round(n_edges / max(1, len(set(rev_core))), 4),
        "max_in_degree": top_in[0][1] if top_in else 0,
        "top30_in_degree": hub_curve,
        "top10_in_degree_share_of_edges": round(sum(d for _, d in top_in[:10]) / n_edges, 4),
        "in_degree_histogram": dict(collections.Counter(
            (str(v) if v < 5 else ("5-9" if v < 10 else ("10-49" if v < 50 else "50+")))
            for v in indeg.values())),
        "out_degree_histogram": dict(collections.Counter(
            (str(v) if v < 5 else ("5-9" if v < 10 else ("10-49" if v < 50 else "50+")))
            for v in outdeg.values())),
        "distance1_lemmas_whose_ONLY_frontier_objects_are_top10_hubs": only_hub,
        "distance1_count": len(d1),
        "top_fact_weighted_objects": fact_in.most_common(15),
    }

    # counterfactual: frontier without hub objects
    for k in (1, 5, 10):
        hubs = set(w for w, _ in top_in[:k])
        fr2 = sorted(set(frontier) - hubs)
        d2 = bfs(rev_core, fr2)
        report["degree"]["distance1_count_if_top%d_hubs_removed_from_frontier" % k] = \
            sum(1 for w in corpus_vocab if d2.get(w) == 1)

    # ---------------------------------------------------------------- 7b. bridge concentration
    bridge_tgt = collections.Counter()
    seed_set, gs_set = set(seed), set(grounded_s)
    tgt_role = collections.Counter()
    for w in d1:
        tg = sorted(set(o for o in fwd_core.get(w, ()) if dist.get(o) == 0))
        for o in tg:
            bridge_tgt[o] += 1
        tgt_role["seed_only" if all(o in seed_set for o in tg) else
                 ("grounded_only" if all(o in gs_set for o in tg) else "mixed")] += 1
    cum, curve = 0, []
    for i, (o, c) in enumerate(bridge_tgt.most_common(20), 1):
        cum += c
        curve.append({"rank": i, "frontier_node": o, "n_distance1_lemmas_bridging_through": c,
                      "cum_share_of_all_bridge_links": round(cum / max(1, sum(bridge_tgt.values())), 4),
                      "role": "seed" if o in seed_set else "grounded"})
    report["bridge_concentration"] = {
        "n_distinct_frontier_nodes_used_as_bridge_target": len(bridge_tgt),
        "n_bridge_links_total": sum(bridge_tgt.values()),
        "top20": curve,
        "distance1_lemmas_by_target_role": dict(tgt_role),
    }

    # 7c. how much of distance-1 rests on which source file
    per_src = {}
    for tag in ("v5", "v62"):
        emap = {k: v for k, v in edges_core.items() if any(p["src"] == tag for p in v)}
        f2, r2 = build(emap)
        d2 = bfs(r2, frontier)
        per_src[tag] = {"edges": len(emap),
                        "distance1_corpus_lemmas": sum(1 for w in corpus_vocab if d2.get(w) == 1),
                        "reachable_corpus_lemmas_any_distance":
                            sum(1 for w in corpus_vocab if d2.get(w, 99) > 0 and w in d2)}
    d1_srcs = collections.Counter()
    for w in d1:
        tags = sorted(set(p["src"] for o in fwd_core.get(w, ())
                          if dist.get(o) == 0 for p in edges_core[(w, o)]))
        d1_srcs["+".join(tags)] += 1
    per_src["distance1_lemmas_by_bridging_source"] = dict(d1_srcs)
    report["source_dependence"] = per_src

    # ---------------------------------------------------------------- 8. named checks
    report["spot_checks"] = {}
    for w in ("fruit", "zone", "process", "thing", "people"):
        report["spot_checks"][w] = {
            "corpus_freq": freq.get(w, 0), "in_seed": w in set(seed),
            "grounded_STRUCTURED": w in set(grounded_s), "in_frontier": w in set(frontier),
            "distance": dist.get(w), "in_degree_core": indeg.get(w, 0),
            "out_degree_core": outdeg.get(w, 0),
        }

    report["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    # full per-lemma table for follow-up (not committed to any canonical path)
    with open(os.path.join(OUT, "lemma_distance.tsv"), "w", encoding="utf-8", newline="") as f:
        f.write("lemma\tfreq\tdistance\teligible\tproper\tconcreteness\tout_deg\tin_deg\n")
        for w in corpus_vocab:
            d = dist.get(w)
            f.write("%s\t%d\t%s\t%d\t%d\t%s\t%d\t%d\n" % (
                w, freq[w], "NA" if d is None else d, int(is_eligible_meaning(w)),
                int(w in proper_set), "" if w not in cov else ("%.2f" % cov[w]),
                len(fwd_core.get(w, ())), len(rev_core.get(w, ()))))
    print("DONE", report["elapsed_s"], "s", flush=True)
    print(json.dumps(report["histograms"][PRIMARY], indent=1))


if __name__ == "__main__":
    main()
