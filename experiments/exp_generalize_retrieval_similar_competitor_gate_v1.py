"""exp_generalize_retrieval_similar_competitor_gate_v1 -- the CHEAP DECISIVE GATE for the reframed
retrieval-interference test (research_retrieval_interference_load_and_dg_boundary_2026-08-30.md).

WHY. The event-count rerun (exp_generalize_retrieval_real_codes_v1) found the content-addressable
separated store's synthetic +0.94 win collapses to +0.06 on real LitBank -- but the research drill showed
this measured the WRONG interference axis. The PINNED cognitive-science axis is SIMILARITY-BASED
CUE-OVERLOAD (Van Dyke & McElree 2006; Radvansky & Zacks 1991 falsify event-count as the primitive), NOT
event-count-per-entity. The who-did-what per-entity register has near-zero competitor overlap (distinct
verbs), so it structurally cannot reveal the operation's value.

THE GATE (research, run BEFORE building the full reframed rerun). Does content genuinely UNDER-DETERMINE on
a real SIMILAR-COMPETITOR subset? Reframe the SAME corpus onto the right axis: retrieval query = "which
entity did verb V (near sentence s)?" Competitors = every entity who did V in the document. When a verb is
shared by >=2 entities, the CONTENT cue (the verb) cannot rank them -> the ambiguous subset. Measure:
  - CONTENT-ONLY floor: rank candidates by content/frequency affinity ONLY (cue-blind to temporal order):
    predict the entity that did V most often in the doc. This is the strongest content-only baseline.
  - CONTEXT (TCM/discourse recency, Howard & Kahana 2002): predict the candidate whose nearest mention is
    closest in sentences to the query -- temporal context reinstatement.
  - INFO-FREE TWIN: shuffle sentence positions -> context becomes uninformative -> must collapse to content.

DECISION GATE (pre-registered by the research): content-only floor on the ambiguous subset
  <= ~0.75  -> content under-determines; the separated-store + context-reinstatement operation has headroom
              -> BUILD the full reframed rerun (P1/P2/P3 in the research note).
  >= ~0.90  -> features already separate competitors; no room -> DO NOT build; report the floor as the answer.
And a PREVIEW of P1: does the temporal-context signal beat the content-only floor CI-separated (twin losing)?

This is the same discipline that produced the +0.06 correction (measure the operating point before crediting
the mechanism), applied one axis over. Pure counting + recency; NO CA3/store machinery (that is the full
rerun). Real LitBank who-did-what gold. NO external LLM. CPU. ASCII-only. Deterministic.

Run: .venv/Scripts/python.exe experiments/exp_generalize_retrieval_similar_competitor_gate_v1.py --self-test
     ... --full
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR = "generalize_retrieval_similar_competitor_gate_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
WDW_PATH = os.path.join(REPO, "data", "litbank", "who_did_what_events.json")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_doc_events():
    """Per-doc events: (entity_gold, verb, sent). Only mentions with a gov_verb (an action)."""
    docs = json.load(open(WDW_PATH, encoding="utf-8"))
    out = []
    for dd in docs:
        evs = []
        for m in dd["stream"]:
            v = m.get("gov_verb")
            if not v:
                continue
            evs.append({"e": int(m["gold"]), "v": str(v), "s": int(m["sent"])})
        if evs:
            out.append({"doc": dd["doc"], "events": evs})
    return out


def build_queries(doc_events, gen_np, shuffle_ctx=False):
    """For each doc, the AMBIGUOUS subset = events whose verb is done by >=2 DISTINCT entities in the doc.
    Each such event is a query; candidates = the distinct entities who did that verb.
    Returns per-query dicts with the content-floor and context predictions already resolvable.

    shuffle_ctx=True -> permute the sentence index of every mention within the doc (info-free twin: the
    temporal-context signal is destroyed while the candidate set / content stats are unchanged)."""
    queries = []
    for de in doc_events:
        evs = de["events"]
        # optional context shuffle: permute sentence labels across mentions (destroys recency signal)
        if shuffle_ctx:
            sents = np.array([e["s"] for e in evs])
            perm = gen_np.permutation(len(sents))
            evs = [dict(e, s=int(sents[perm[i]])) for i, e in enumerate(evs)]
        by_verb = collections.defaultdict(list)          # verb -> list of events
        ent_verb_ct = collections.Counter()              # (entity, verb) -> count (content affinity)
        ent_mentions = collections.defaultdict(list)     # entity -> [sent, ...] (for recency/context)
        for e in evs:
            by_verb[e["v"]].append(e)
            ent_verb_ct[(e["e"], e["v"])] += 1
            ent_mentions[e["e"]].append(e["s"])
        for v, elist in by_verb.items():
            cand = sorted(set(e["e"] for e in elist))
            if len(cand) < 2:
                continue  # not ambiguous: a single entity owns this verb
            # content-only prediction for verb v (cue-blind to the query sentence): the entity that did v
            # most in the doc; ties -> lowest id (deterministic).
            content_pred = max(cand, key=lambda c: (ent_verb_ct[(c, v)], -c))
            for qe in elist:
                s = qe["s"]
                # context prediction (LEAK-FREE): candidate most recently mentioned STRICTLY BEFORE the
                # query sentence -- genuine discourse recency / temporal-context reinstatement (Howard &
                # Kahana). The query mention itself (and any mention at/after s) is excluded so the signal
                # cannot see the answer's own position. A candidate with no prior mention gets a large
                # distance (dispreferred), which is itself part of the regime (a freshly-named actor).
                def prior_recency(c):
                    prev = [sm for sm in ent_mentions[c] if sm < s]
                    return (s - max(prev)) if prev else 10 ** 9
                ctx_pred = min(cand, key=lambda c: (prior_recency(c), c))
                queries.append({"gold": qe["e"], "v": v, "s": s, "n_cand": len(cand),
                                "content_pred": content_pred, "ctx_pred": ctx_pred})
    return queries


def acc(queries, key):
    if not queries:
        return float("nan")
    return float(np.mean([int(q[key] == q["gold"]) for q in queries]))


def boot_paired(queries, a, b, gen_np, n_boot=2000):
    if not queries:
        return {"delta": float("nan"), "band": "NA"}
    da = np.array([int(q[a] == q["gold"]) for q in queries], dtype=np.float64)
    db = np.array([int(q[b] == q["gold"]) for q in queries], dtype=np.float64)
    diff = da - db
    n = len(diff)
    idx = np.array([gen_np.integers(0, n, size=n) for _ in range(n_boot)])
    boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    null = np.array([np.abs((diff * gen_np.choice([-1.0, 1.0], size=n)).mean()) for _ in range(n_boot)])
    p95 = float(np.percentile(null, 95))
    band = "ABOVE" if lo > 0 and lo > p95 else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "half_width": (hi - lo) / 2.0,
            "null_p95": p95, "band": band, "n": n}


def run(n_boot=2000):
    t0 = time.perf_counter()
    doc_events = load_doc_events()
    gen = np.random.default_rng(20260830)
    q = build_queries(doc_events, gen, shuffle_ctx=False)
    q_shuf = build_queries(doc_events, np.random.default_rng(999), shuffle_ctx=True)

    content_floor = acc(q, "content_pred")
    ctx = acc(q, "ctx_pred")
    ctx_shuf = acc(q_shuf, "ctx_pred")
    chance = float(np.mean([1.0 / q_i["n_cand"] for q_i in q]))
    ctx_minus_content = boot_paired(q, "ctx_pred", "content_pred", gen, n_boot)
    # twin: real context vs shuffled context (paired is not aligned across different query sets; compare means)
    twin_gap = ctx - ctx_shuf

    # stratify by competitor count
    strata = {}
    for lo, hi, lbl in [(2, 2, "2"), (3, 4, "3-4"), (5, 100, "5+")]:
        qs = [x for x in q if lo <= x["n_cand"] <= hi]
        strata[lbl] = {"n": len(qs), "content_floor": acc(qs, "content_pred"),
                       "ctx": acc(qs, "ctx_pred"),
                       "ctx_minus_content": boot_paired(qs, "ctx_pred", "content_pred", gen, n_boot)}

    gate = "BUILD" if content_floor <= 0.75 else ("DO_NOT_BUILD" if content_floor >= 0.90 else "MARGINAL")
    p1_preview = "PASS" if (ctx_minus_content["band"] == "ABOVE" and ctx_minus_content["delta"] >= 0.10) else \
                 ("WEAK" if ctx_minus_content["band"] == "ABOVE" else "FAIL")

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_ambiguous_queries": len(q), "n_docs": len(doc_events),
           "chance_1_over_ncand": chance,
           "content_only_floor": content_floor, "context_recency": ctx, "context_shuffled_twin": ctx_shuf,
           "context_minus_content": ctx_minus_content, "context_minus_shuffled_twin": twin_gap,
           "strata_by_competitor_count": strata,
           "GATE": gate, "P1_context_preview": p1_preview}
    _log("ambiguous queries=%d (%.1f%% of docs have them) chance=%.3f" % (len(q), 100.0, chance))
    _log("CONTENT-ONLY floor=%.3f | CONTEXT(recency)=%.3f | CONTEXT shuffled-twin=%.3f"
         % (content_floor, ctx, ctx_shuf))
    _log("CONTEXT - CONTENT = %+.3f [%.3f,%.3f] %s | context beats shuffled twin by %+.3f"
         % (ctx_minus_content["delta"], ctx_minus_content["lo"], ctx_minus_content["hi"],
            ctx_minus_content["band"], twin_gap))
    for lbl, sv in strata.items():
        _log("  competitors=%s n=%d content=%.3f ctx=%.3f (ctx-content %+.3f[%s])"
             % (lbl, sv["n"], sv["content_floor"], sv["ctx"], sv["ctx_minus_content"]["delta"],
                sv["ctx_minus_content"]["band"]))
    _log("GATE=%s (content floor %.3f vs 0.75/0.90 thresholds) | P1 preview=%s" % (gate, content_floor, p1_preview))
    return res


def self_test():
    _log("SELF-TEST: cache loads, ambiguous subset is non-empty")
    de = load_doc_events()
    assert len(de) == 100, "expected 100 docs, got %d" % len(de)
    q = build_queries(de, np.random.default_rng(1))
    assert len(q) > 200, "ambiguous subset too small: %d" % len(q)
    for x in q[:50]:
        assert x["n_cand"] >= 2, "ambiguous query must have >=2 candidates"
    _log("  ambiguous queries=%d" % len(q))
    _log("SELF-TEST: two entities share a verb; LEAK-FREE prior-recency picks the recently-mentioned actor")
    # 'run' done by {0,1} -> ambiguous. Query = entity 1 runs at s=6; entity 1 was just mentioned (walk s=5),
    # entity 0 last mentioned at s=2. Prior-recency should pick entity 1 (recency 1 < 4), leak-free.
    toy = [{"doc": "t", "events": [{"e": 0, "v": "run", "s": 2}, {"e": 1, "v": "walk", "s": 5},
                                   {"e": 1, "v": "run", "s": 6}]}]
    tq = build_queries(toy, np.random.default_rng(0))
    q6 = [x for x in tq if x["v"] == "run" and x["s"] == 6][0]
    assert q6["ctx_pred"] == 1, "prior-recency should pick the recently-mentioned actor: got %d" % q6["ctx_pred"]
    # and it must NOT use the query's own position (leak-free): a freshly-introduced actor is NOT recoverable
    toy2 = [{"doc": "t", "events": [{"e": 0, "v": "run", "s": 2}, {"e": 0, "v": "run", "s": 3},
                                    {"e": 1, "v": "run", "s": 9}]}]
    tq2 = build_queries(toy2, np.random.default_rng(0))
    q9 = [x for x in tq2 if x["s"] == 9][0]
    assert q9["ctx_pred"] == 0, "a freshly-introduced actor (entity 1, no prior mention) must not be picked by recency"
    _log("SELF-TEST PASS")
    return {"n_docs": len(de), "n_ambiguous": len(q)}


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    if args.self_test or not args.full:
        st = self_test()
        _atomic_write(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now_iso()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return
    res = run()
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
