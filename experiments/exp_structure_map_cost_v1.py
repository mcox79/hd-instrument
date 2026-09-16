"""exp_structure_map_cost_v1 -- THE READ-TIME COST TABLE for the structure map (pri 142).

WHAT THIS CELL MEASURES, IN PLAIN WORDS
---------------------------------------
One full read of the same six modern GUM documents, with the interpreter's own profiler switched on,
so that every part of the reader gets a number in seconds.  The point is not a benchmark: it is the
RANKING INPUT for the consolidation list.  Two parts that compute the same thing are worth merging in
proportion to what they cost, and a part that re-does upstream work (parsing the same sentence twice,
reading the same lexicon entry again) is worth a cache in proportion to what that repetition costs.

WHAT IT PRODUCES
----------------
  * per-MODULE self time (`tottime`, seconds, summed over the six documents) -- the cost table's rows.
  * the top functions by cumulative and by self time -- where inside a module the time goes.
  * CALL COUNTS for the named repetition suspects (sentence parsing, tagging, tree decoding, lemmas,
    lexicon reads), so "redundant work" is a counted claim, not an impression.
  * a CONTENTION CHECK: every document is read TWICE in the same process; the per-document ratio of
    the second pass to the first is reported.  A laptop shared with another run shows up as one
    document 3x slower on its repeat, and that document's row is reported as UNSTABLE rather than used.

BRAIN-FOUNDATIONAL NOTE: this cell measures; it decides nothing and changes no organ.  It reads the
live reader exactly as the product board calls it (`SituationReader(gaz).read(path)`), on the board's
own GUM test split (odd document index), evenly spaced across genres.

USAGE
  .venv/Scripts/python.exe experiments/exp_structure_map_cost_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_structure_map_cost_v1.py --run [--docs 6] [--mode annotated|textonly|both]
"""
from __future__ import annotations

import argparse
import cProfile
import collections
import json
import os
import pstats
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments._seed_checkpoint import get_output_dir          # noqa: E402  (Q115: canonical out dir)

ANCHOR = "exp_structure_map_cost_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260916
N_DOCS = 6

# The repetition suspects the map names.  (module-substring, function name) -> a plain-language label.
CALL_PROBES = [
    ("scene_segment", "parse_conll_sentences", "parse the document's sentences off disk"),
    ("coref", "parse_litbank_conll", "parse the document's mentions off disk"),
    ("pos_tagger", "tag", "tag a sentence with the perceptron tagger"),
    ("lexical_categories", "tag", "tag a sentence with the category organ"),
    ("lexical_categories", "posterior", "category posterior for a sentence"),
    ("lexical_categories", "feed_passage", "the one in-order passage feed"),
    ("attachment_arm", "arc_scores", "score every candidate arc of a sentence"),
    ("attachment_arm", "incremental_tree", "decode a sentence's tree in order"),
    ("attachment_arm", "map_tree_single_root", "decode a sentence's tree by search"),
    ("arc_parser", "parse", "parse a sentence with the arc-factored parser"),
    ("graded_parser", "parse", "parse a sentence with the graded parser"),
    ("arc_labeler", "predict", "label a sentence's arcs"),
    ("morphology", "lemma", "reduce a word to its dictionary form"),
    ("lexicon_foundation", "get", "read the frozen lexical foundation"),
    ("animacy_lexicon", "lookup", "look a word up in the animacy lexicon"),
    ("affect_lexicon", "lookup", "look a word up in the affect lexicon"),
    ("grounded_semantic_graph", "spread", "spread activation over the meaning graph"),
]


# ---------------------------------------------------------------------------------------------------
# attribution
# ---------------------------------------------------------------------------------------------------
def _module_of(filename: str) -> str:
    """Map a profiled function's file to a substrate module name (or a coarse bucket)."""
    f = filename.replace("\\", "/")
    for marker, prefix in (("/hdlab/", "hdlab."), ("/experiments/", "experiments."),
                           ("/tools/", "tools.")):
        if marker in f:
            stem = f.split(marker, 1)[1]
            return prefix + stem[:-3].replace("/", ".") if stem.endswith(".py") else prefix + stem
    if f in ("~", "") or f.startswith("<"):
        return "<builtin>"
    low = f.lower()
    for third in ("numpy", "nltk", "scipy", "torch", "sklearn"):
        if "/" + third + "/" in low:
            return "<3rd-party:%s>" % third
    if "/lib/" in low or "/python3" in low or "/site-packages/" in low:
        return "<stdlib/other>"
    return "<other>"


def _attribute(stats: pstats.Stats):
    """Per-module SELF time (tottime) + per-function cumulative/self time + call counts."""
    per_mod = collections.Counter()
    per_mod_calls = collections.Counter()
    funcs = []
    for (fn, lineno, name), (cc, nc, tt, ct, _callers) in stats.stats.items():
        mod = _module_of(fn)
        per_mod[mod] += tt
        per_mod_calls[mod] += nc
        funcs.append({"module": mod, "func": name, "line": lineno,
                      "ncalls": nc, "tottime": tt, "cumtime": ct})
    return per_mod, per_mod_calls, funcs


def _probe_counts(funcs):
    out = {}
    for mod_sub, fname, label in CALL_PROBES:
        n = 0
        for f in funcs:
            if f["func"] == fname and mod_sub in f["module"]:
                n += f["ncalls"]
        if n:
            out["%s.%s" % (mod_sub, fname)] = {"calls": n, "plain": label}
    return out


# ---------------------------------------------------------------------------------------------------
# the documents + the read
# ---------------------------------------------------------------------------------------------------
def _gum_test_docs(n_docs=N_DOCS, prefix=False):
    """The board's own GUM split (TEST = odd document index), evenly spaced across genres."""
    import experiments.gum_coref as G
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, name_gazetteer=gaz, decision_source=G.DECISION_SOURCE,
                       limit=(2 * n_docs if (n_docs and prefix) else None))
    test = [d for i, d in enumerate(docs) if i % 2 == 1]
    if n_docs and n_docs < len(test):
        if prefix:
            test = test[:n_docs]
        else:
            step = len(test) / float(n_docs)
            test = [test[int(i * step)] for i in range(n_docs)]
    return test, gaz


def _write_two_conll(doc, dirpath):
    """(annotated_path, textonly_path) -- the board's own two input contracts."""
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    p_ann = os.path.join(dirpath, doc.docid + ".ann.conll")
    gum_to_conll(doc, p_ann)
    p_txt = os.path.join(dirpath, doc.docid + ".txt.conll")
    with open(p_ann, encoding="utf-8") as fh, open(p_txt, "w", encoding="utf-8") as out:
        for ln in fh:
            s = ln.rstrip("\n")
            if s.startswith("#") or not s.strip():
                out.write(s + "\n")
                continue
            c = s.split("\t")
            c[-1] = "_"
            out.write("\t".join(c) + "\n")
    return p_ann, p_txt


def _one_read(path, gaz):
    from hdlab.situation_reader import SituationReader
    rdr = SituationReader(gaz=gaz)
    return rdr.read(path)


def _timed_read(path, gaz):
    t0 = time.perf_counter()
    sm = _one_read(path, gaz)
    return time.perf_counter() - t0, sm


# ---------------------------------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------------------------------
def run(n_docs=N_DOCS, mode="annotated"):
    os.makedirs(OUT_DIR, exist_ok=True)
    test, gaz = _gum_test_docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p142_cost_")
    paths = []
    for d in test:
        p_ann, p_txt = _write_two_conll(d, tmp)
        paths.append((d.docid, p_ann if mode == "annotated" else p_txt))

    # WARM the module imports + frozen assets OUTSIDE the profile, so the table is READ cost, not load cost.
    warm_t, warm_sm = _timed_read(paths[0][1], gaz)

    prof = cProfile.Profile()
    per_doc = []
    sm_shape = {}
    for docid, path in paths:
        prof.enable()
        t1, sm = _timed_read(path, gaz)
        prof.disable()
        # CONTENTION CHECK -- the same document again, in the same process, unprofiled.
        t2, _ = _timed_read(path, gaz)
        per_doc.append({"docid": docid, "n_sentences": sm.n_sentences,
                        "profiled_s": t1, "repeat_s": t2,
                        "repeat_ratio": (t2 / t1) if t1 > 0 else None})
        sm_shape[docid] = {"n_sentences": sm.n_sentences, "n_entities": len(sm.entities),
                           "n_events": len(sm.events),
                           "n_targets": getattr(sm, "n_targets", 0),
                           "n_pronouns_discovered": getattr(sm, "n_pronouns_discovered", 0)}

    stats = pstats.Stats(prof)
    per_mod, per_mod_calls, funcs = _attribute(stats)
    total_self = sum(per_mod.values())
    total_wall = sum(d["profiled_s"] for d in per_doc)
    n_sents = sum(d["n_sentences"] for d in per_doc)

    unstable = [d["docid"] for d in per_doc
                if d["repeat_ratio"] is not None and (d["repeat_ratio"] > 2.0 or d["repeat_ratio"] < 0.34)]

    rows = []
    for mod, tt in per_mod.most_common():
        rows.append({"module": mod, "self_s": round(tt, 4),
                     "share_of_self": round(tt / total_self, 4) if total_self else None,
                     "calls": int(per_mod_calls[mod]),
                     "s_per_doc": round(tt / max(len(per_doc), 1), 4)})

    by_cum = sorted(funcs, key=lambda f: -f["cumtime"])[:40]
    by_self = sorted(funcs, key=lambda f: -f["tottime"])[:40]
    probes = _probe_counts(funcs)

    metrics = {
        "anchor": ANCHOR, "seed": SEED, "mode": mode,
        "corpus": "GUM modern TEST split (odd document index), evenly spaced across genres",
        "n_documents": len(per_doc), "n_sentences": n_sents,
        "warm_read_s": round(warm_t, 4),
        "total_profiled_wall_s": round(total_wall, 4),
        "total_self_s": round(total_self, 4),
        "s_per_document": round(total_wall / max(len(per_doc), 1), 4),
        "s_per_sentence": round(total_wall / max(n_sents, 1), 5),
        "profiler_overhead_note": ("cProfile inflates absolute wall time; the SHARES and the RANKING are what "
                                   "the consolidation list uses, and the unprofiled repeat time is reported "
                                   "per document as the honest wall clock."),
        "contention_check": {"per_document": per_doc, "unstable_documents": unstable,
                             "plain": ("each document is read a second time in the same process; a ratio far "
                                       "from 1 means the laptop was busy and that row is not used")},
        "cost_table": rows[:60],
        "top_functions_by_cumulative": [dict(f, tottime=round(f["tottime"], 4),
                                             cumtime=round(f["cumtime"], 4)) for f in by_cum],
        "top_functions_by_self": [dict(f, tottime=round(f["tottime"], 4),
                                       cumtime=round(f["cumtime"], 4)) for f in by_self],
        "repetition_counts": probes,
        "situation_model_shape": sm_shape,
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    stats.dump_stats(os.path.join(OUT_DIR, "read_profile.prof"))

    print("documents %d  sentences %d  wall %.1fs (profiled)  %.2fs/doc  warm %.2fs"
          % (len(per_doc), n_sents, total_wall, total_wall / max(len(per_doc), 1), warm_t))
    print("unstable documents (contention): %s" % (unstable or "none"))
    print("\n  %-46s %9s %7s %10s" % ("module", "self_s", "share", "calls"))
    for r in rows[:25]:
        print("  %-46s %9.3f %6.1f%% %10d" % (r["module"], r["self_s"], 100 * (r["share_of_self"] or 0), r["calls"]))
    print("\n  REPETITION COUNTS (over %d documents, %d sentences):" % (len(per_doc), n_sents))
    for k, v in sorted(probes.items(), key=lambda kv: -kv[1]["calls"]):
        print("  %-46s %8d   %s" % (k, v["calls"], v["plain"]))
    print("\nwrote %s" % os.path.join(OUT_DIR, "metrics.json"))
    return metrics


# ---------------------------------------------------------------------------------------------------
# OPTIMIZATION LEAD -- is the dominant cost REPEATED work?
# ---------------------------------------------------------------------------------------------------
def coord_probe(n_docs=6, mode="annotated"):
    """THE COORDINATION LEAD, COUNTED: does the goal register have any way to read a result state?

    The owner's 2026-09-16 concern is that a goal closes without the state register's result state.  The
    binding constraint on that repair is not the rule -- it is whether the two registers can even name the
    same thing.  This counts, per document, on ONE live read: how many goals the goal register holds, how
    many entities the state register tracks, and HOW MANY GOAL AGENTS APPEAR AS STATE-REGISTER KEYS.  A
    coordination that cannot be keyed cannot be built, and the overlap is the number that bounds it.
    """
    test, gaz = _gum_test_docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p142_coord_")
    rows = []
    for d in test:
        p_ann, p_txt = _write_two_conll(d, tmp)
        _, sm = _timed_read(p_ann if mode == "annotated" else p_txt, gaz)
        gr = getattr(sm, "goal_register", None)
        sr = getattr(sm, "state_register", None)
        goals = list(getattr(gr, "goals", []) or [])
        tracks = dict(getattr(sr, "tracks", {}) or {})
        stated = {k for k, v in tracks.items() if getattr(v, "spans", None) or getattr(v, "occurrences", None)}
        def keys_of(g):
            return {str(x).lower() for x in (getattr(g, "agent_canonical", None), getattr(g, "agent", None)) if x}
        low_tracks = {str(k).lower() for k in tracks}
        low_stated = {str(k).lower() for k in stated}
        shared = sum(1 for g in goals if keys_of(g) & low_tracks)
        shared_stated = sum(1 for g in goals if keys_of(g) & low_stated)
        status = collections.Counter(getattr(g, "status", "?") for g in goals)
        rows.append({"docid": d.docid, "n_sentences": sm.n_sentences,
                     "n_goals": len(goals), "goal_status": dict(status),
                     "n_state_tracks": len(tracks), "n_state_tracks_with_a_state": len(stated),
                     "n_entity_states": len(getattr(sm, "entity_states", []) or []),
                     "goals_whose_agent_is_a_state_key": shared,
                     "goals_whose_agent_HAS_a_state": shared_stated,
                     "n_events": len(sm.events)})
        print("  %-28s sents=%-4d goals=%-4d state_tracks=%-4d (with a state %-4d)  "
              "goal agents that are state keys: %d   that HAVE a state: %d"
              % (d.docid, sm.n_sentences, len(goals), len(tracks), len(stated), shared, shared_stated))
    tot = {k: sum(r[k] for r in rows) for k in
           ("n_goals", "n_state_tracks", "n_state_tracks_with_a_state", "n_entity_states",
            "goals_whose_agent_is_a_state_key", "goals_whose_agent_HAS_a_state", "n_events", "n_sentences")}
    res = {"per_document": rows, "totals": tot, "n_documents": len(rows),
           "plain": ("how many goals could even be checked against the state register: a goal whose agent is "
                     "not a key in the state register cannot be closed by a result state, however good the "
                     "rule is")}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "coord_probe.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print("\nTOTALS over %d documents / %d sentences: goals %d | state tracks %d (with a state %d) | "
          "entity_states %d | goal agents that are state keys %d | that HAVE a state %d"
          % (len(rows), tot["n_sentences"], tot["n_goals"], tot["n_state_tracks"],
             tot["n_state_tracks_with_a_state"], tot["n_entity_states"],
             tot["goals_whose_agent_is_a_state_key"], tot["goals_whose_agent_HAS_a_state"]))
    return res


def _sig(sm):
    """A read's answer signature: the shape plus the event tuples, so a changed read is visible."""
    return (sm.n_sentences, len(sm.entities), len(sm.events),
            tuple(sorted((e.predicate, str(e.agent), str(e.patient)) for e in sm.events))[:50])


def cache_probe(n_docs=2, mode="annotated"):
    """MEASUREMENT ONLY -- wraps (does not edit) the spreading-activation call the cost table names as the
    dominant cost, and counts how many of its runs are EXACT REPEATS within one document's read.

    The wrapper is a counting shim installed in this process for the duration of the probe; it computes the
    same value and returns it (a memo is used only to answer 'would a cache have hit', and the memoized
    value is returned verbatim, so the read is byte-identical either way -- the assertion below checks the
    reader's own output is unchanged against an un-shimmed read of the same document).
    """
    import hdlab.grounded_semantic_graph as GSG
    test, gaz = _gum_test_docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p142_cache_")
    out = []
    for d in test:
        p_ann, p_txt = _write_two_conll(d, tmp)
        path = p_ann if mode == "annotated" else p_txt
        # PLASTICITY CONTROL FIRST.  The reader's count organs `observe` while they read, so two reads of
        # one document in one process need not agree.  Read it twice UN-SHIMMED and compare: that tells a
        # genuinely unsafe cache apart from the organ's own plasticity, which the memo cannot be blamed for.
        warm_t, warm_sm = _timed_read(path, gaz)
        warm_sig = _sig(warm_sm)
        base_t, base_sm = _timed_read(path, gaz)              # un-shimmed reference read (2nd)
        base_sig = _sig(base_sm)
        plastic = (warm_sig != base_sig)

        orig = GSG._ppr
        stats = {"calls": 0, "hits": 0, "distinct": 0, "seed_sizes": []}
        memo = {}

        def counting_ppr(seed_idx, Tt, n, d_=GSG.DAMPING, iters=GSG.PPR_ITERS, _orig=orig):
            stats["calls"] += 1
            key = (tuple(seed_idx), n, d_, iters)
            if key in memo:
                stats["hits"] += 1
                return memo[key]
            stats["distinct"] += 1
            stats["seed_sizes"].append(len(seed_idx))
            r = _orig(seed_idx, Tt, n, d_, iters)
            memo[key] = r
            return r

        GSG._ppr = counting_ppr
        try:
            cached_t, cached_sm = _timed_read(path, gaz)
        finally:
            GSG._ppr = orig
        cached_sig = _sig(cached_sm)
        out.append({"docid": d.docid, "n_sentences": base_sm.n_sentences,
                    "uncached_s": round(base_t, 3), "with_memo_s": round(cached_t, 3),
                    "saved_s": round(base_t - cached_t, 3),
                    "ppr_calls": stats["calls"], "ppr_distinct": stats["distinct"],
                    "ppr_repeat_calls": stats["hits"],
                    "repeat_share": round(stats["hits"] / max(stats["calls"], 1), 4),
                    "mean_seed_size": round(sum(stats["seed_sizes"]) / max(len(stats["seed_sizes"]), 1), 1),
                    "reader_is_plastic_read_to_read": plastic,
                    "memo_changed_the_read_beyond_plasticity": (cached_sig != base_sig) and not plastic,
                    "read_unchanged": cached_sig == base_sig})
        print("  %-28s sents=%-4d ppr calls=%-5d distinct=%-5d repeats=%-5d (%.0f%%)  %.1fs -> %.1fs "
              "(saved %.1fs)  plastic_read_to_read=%s  memo_identical=%s"
              % (d.docid, base_sm.n_sentences, stats["calls"], stats["distinct"], stats["hits"],
                 100 * stats["hits"] / max(stats["calls"], 1), base_t, cached_t, base_t - cached_t,
                 plastic, cached_sig == base_sig))
    tot_saved = sum(o["saved_s"] for o in out)
    res = {"per_document": out, "n_documents": len(out),
           "mean_saved_s_per_document": round(tot_saved / max(len(out), 1), 3),
           "plain": ("the meaning organ's spreading-activation run is the biggest single cost in a read; this "
                     "counts how many of its runs inside ONE document ask the identical question, and times "
                     "the read with those answered from a per-read memo instead of recomputed")}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "cache_probe.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print("\nmean saved %.1fs per document over %d documents -> %s"
          % (res["mean_saved_s_per_document"], len(out), os.path.join(OUT_DIR, "cache_probe.json")))
    return res


# ---------------------------------------------------------------------------------------------------
# self-test (formula + real code path, no corpus)
# ---------------------------------------------------------------------------------------------------
def _selftest_attribution() -> None:
    """_module_of maps hdlab / experiments / third-party / builtin files to the right bucket."""
    assert _module_of(r"C:\AI\hd-instrument\hdlab\coref.py") == "hdlab.coref"
    assert _module_of("/c/AI/hd-instrument/hdlab/learner/core.py") == "hdlab.learner.core"
    assert _module_of(r"C:\AI\hd-instrument\experiments\gum_coref.py") == "experiments.gum_coref"
    assert _module_of("~") == "<builtin>"
    assert _module_of("/usr/lib/python3.12/site-packages/numpy/core/x.py") == "<3rd-party:numpy>"


def _selftest_shares_sum_to_one() -> None:
    """The cost table is a PARTITION of self time: the shares sum to 1 and no row is negative."""
    per_mod = collections.Counter({"hdlab.a": 2.0, "hdlab.b": 1.0, "<builtin>": 1.0})
    tot = sum(per_mod.values())
    shares = [v / tot for v in per_mod.values()]
    assert abs(sum(shares) - 1.0) < 1e-12, shares
    assert min(shares) >= 0.0


def _selftest_profiled_read() -> dict:
    """REAL code path: profile ONE read of a tiny constructed document and assert the table is populated."""
    from hdlab.situation_reader import _write_temp_conll
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "saw", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "He", "(0)"), (1, 1, "left", "_"), (1, 2, "because", "_"),
        (1, 3, "she", "(1)"), (1, 4, "cried", "_"), (1, 5, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    gaz = {"john": "masc", "mary": "fem"}
    try:
        _one_read(path, gaz)                       # warm (imports + assets out of the profile)
        prof = cProfile.Profile()
        prof.enable()
        sm = _one_read(path, gaz)
        prof.disable()
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    per_mod, per_mod_calls, funcs = _attribute(pstats.Stats(prof))
    hd = [m for m in per_mod if m.startswith("hdlab.")]
    assert sm.n_sentences == 2, sm.n_sentences
    assert len(hd) >= 10, "too few hdlab modules attributed: %d" % len(hd)
    assert "hdlab.situation_reader" in per_mod, sorted(hd)[:20]
    assert sum(per_mod.values()) > 0.0
    probes = _probe_counts(funcs)
    assert probes, "no repetition probe fired on a real read"
    return {"n_modules_attributed": len(hd), "total_self_s": round(sum(per_mod.values()), 4),
            "probes_fired": len(probes)}


def self_test() -> int:
    _selftest_attribution(); print("PASS  attribution buckets")
    _selftest_shares_sum_to_one(); print("PASS  cost shares are a partition")
    out = _selftest_profiled_read()
    print("PASS  profiled real read: %s" % out)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--cache-probe", action="store_true")
    ap.add_argument("--coord-probe", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--docs", type=int, default=N_DOCS)
    ap.add_argument("--mode", default="annotated", choices=("annotated", "textonly"))
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.cache_probe:
        cache_probe(n_docs=a.docs, mode=a.mode)
        return 0
    if a.coord_probe:
        coord_probe(n_docs=a.docs, mode=a.mode)
        return 0
    if a.run:
        run(n_docs=a.docs, mode=a.mode)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
