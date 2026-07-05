"""
exp_cortex2_hard_unanswerables_nearmiss_transitivity_v1 -- the HARD follow-up to
cortex2_provenance_faithfulness_and_calibrated_refuse_v1 (CPU-local, NO re-encode).

v1 got refuse-precision=1.000 / conf-AUROC=1.000 -- but flagged that as by-construction-EASY: the
unanswerable queries had support FULLY ABSENT (trivially far). This cell replaces those with HARD
unanswerables and asks whether the glass-box audit is a GENUINE differentiator or an easy-test artifact.

Two HARD classes (per Director):
  1. NEAR-MISS: valid hop1 (intermediate is a REAL, present, often high-degree entity) but the FINAL
     edge is absent -- a plausible-wrong chain exists. Does per-hop confidence still refuse, or does a
     busy intermediate raise the noise floor enough to confabulate? (Tests confidence at a HARD op point.)
  2. TRANSITIVITY-VIOLATION (ATTACK-7 class): BOTH edges present (s-p1->mid-p2->tail all real) so the
     chain is mechanically composable, but the composition is arbitrary/non-materialized. Does the
     intrinsic per-hop confidence catch it where the black-box's top-K retrieval doesn't?
     KG-intrinsic label (NON-CIRCULAR vs the confidence detector): a chain is a VIOLATION iff NO direct
     edge (s, any_r, tail) corroborates the composition; LEGIT-CORROBORATED iff (s -> tail) is
     materialized in the KG. Detector under test = per-hop cleanup-cosine confidence (independent of
     that corroboration label).

Reasoning substrate: sharded FHRR KG over FB15k-237 (same as v1; random phasor codes seeded per run;
NO concept encoder touched). Cortex = per-hop unbind+cleanup; cited atoms = the two path edges;
confidence = min hop cleanup-cosine. Black-box = competent single-shot retrieve-about-query, no gate,
provenance = top-K retrieved facts.

PRE-REGISTERED verdict bands:
  GENUINE_DIFFERENTIATOR: faithfulness_answerable >= 0.70 (decisive metric still holds) AND near-miss
    confidence still separates (AUROC_nearmiss > 0.65 and refuse-precision_nearmiss > black-box's 0.0)
    AND cortex beats black-box on the transitivity class via chain-completeness (1.0 vs ~0.5).
  EASY_TEST_ARTIFACT: near-miss AUROC also collapses to chance (< 0.60) -> the v1 result was an artifact
    of trivially-far unanswerables; confidence is not a real capability.
  Honest transitivity finding reported regardless: if AUROC_transitivity ~0.5, state plainly that
    per-hop confidence does NOT catch transitivity violations (expected -- it measures hop-support, not
    composition-validity); the glass-box value on that class is auditability (faithful trace), not
    auto-refuse.

ASCII-only. write_metrics. Single-shot multi-seed. except SystemExit: raise BEFORE except Exception.
No re-encode, no substrate mutation.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "cortex2_hard_unanswerables_nearmiss_transitivity_v1"
N = 4096
FB = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

MAX_TRIPLES = 2000 if SMOKE else 6000
NQ = 20 if SMOKE else 120          # per class (answerable / near_miss / legit_corrob / transitivity)
SEEDS = [7, 13, 19]
K_CITED_BB = 3
N_NONCITED_ABLATE = 2
RETAIN_PCTILE = 10                 # refuse threshold = 10th pctile of answerable-correct conf (retain 90%)


# ------------------------------- FHRR primitives ----------------------------


def cphasor(m: int, d: int, g: np.random.Generator) -> np.ndarray:
    ang = (g.random((m, d)) * 2.0 - 1.0) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def _cosine_to_book(q: np.ndarray, book: np.ndarray) -> np.ndarray:
    qn = np.linalg.norm(q)
    if qn == 0.0:
        return np.zeros(book.shape[0], dtype=np.float64)
    return (book @ np.conj(q)).real / (qn * math.sqrt(book.shape[1]))


def _auroc(pos: np.ndarray, neg: np.ndarray) -> float:
    pos = np.asarray(pos, dtype=np.float64)
    neg = np.asarray(neg, dtype=np.float64)
    if pos.size == 0 or neg.size == 0:
        return 0.5
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, allv.size + 1, dtype=np.float64)
    sv = allv[order]
    i = 0
    while i < sv.size:
        j = i
        while j + 1 < sv.size and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            ranks[order[i:j + 1]] = avg
        i = j + 1
    u = ranks[:pos.size].sum() - pos.size * (pos.size + 1) / 2.0
    return float(u / (pos.size * neg.size))


# ------------------------------- selftests ----------------------------------


def _selftest() -> None:
    g = np.random.default_rng(0)
    a, r, o = cphasor(1, 64, g)[0], cphasor(1, 64, g)[0], cphasor(1, 64, g)[0]
    assert np.allclose(a * r * o * np.conj(a * r), o, atol=1e-3), "bind/unbind"
    bk = cphasor(6, 64, g)
    assert int(np.argmax(_cosine_to_book(bk[3], bk))) == 3, "cleanup self"
    # transitivity-violation is mechanically composable: both hops present -> both high confidence
    shard_mid = r * o
    assert _cosine_to_book(shard_mid * np.conj(r), bk[:1] if False else np.stack([o]))[0] > 0.9, "hop present -> high conf"
    assert abs(_auroc(np.array([0.9, 0.8]), np.array([0.1, 0.2])) - 1.0) < 1e-9, "auroc sep"
    assert abs(_auroc(np.array([0.5, 0.5]), np.array([0.5, 0.5])) - 0.5) < 1e-9, "auroc ties=0.5"
    print("[selftest] PASS: cortex2-hard-unanswerables-nearmiss-transitivity", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ------------------------------- KG build -----------------------------------


def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": expected_n_units, "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def load_triples(max_triples: int):
    ent: Dict[str, int] = {}
    rel: Dict[str, int] = {}
    triples: List[Tuple[int, int, int]] = []
    with open(FB, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            s, p, o = r["subject"], r["predicate"], r["object"]
            for e in (s, o):
                if e not in ent:
                    ent[e] = len(ent)
            if p not in rel:
                rel[p] = len(rel)
            triples.append((ent[s], rel[p], ent[o]))
            if len(triples) >= max_triples:
                break
    return triples, ent, rel


def build_shards(triples, ents, rels):
    out_edges: Dict[int, List[Tuple[int, int]]] = {}
    sp_objs: Dict[Tuple[int, int], set] = {}
    direct_targets: Dict[int, set] = {}
    shards: Dict[int, np.ndarray] = {}
    for s, p, o in triples:
        out_edges.setdefault(s, []).append((p, o))
        sp_objs.setdefault((s, p), set()).add(o)
        direct_targets.setdefault(s, set()).add(o)
        if s not in shards:
            shards[s] = np.zeros(N, dtype=np.complex64)
        shards[s] = shards[s] + rels[p] * ents[o]
    return shards, out_edges, sp_objs, direct_targets


# ------------------------------- cortex + black-box -------------------------


def _hop(shard, rel_vec, ents):
    c = _cosine_to_book(shard * np.conj(rel_vec), ents)
    top = int(np.argmax(c))
    return top, float(c[top])


def cortex_2hop(shards, ents, rels, s, p1, p2):
    if s not in shards:
        return {"answer": None, "mid": None, "conf": 0.0, "cited": [], "answered": False}
    mid, c1 = _hop(shards[s], rels[p1], ents)
    if mid not in shards:
        return {"answer": None, "mid": mid, "conf": min(c1, 0.0), "cited": [(s, p1, mid)], "answered": False}
    tail, c2 = _hop(shards[mid], rels[p2], ents)
    return {"answer": tail, "mid": mid, "conf": min(c1, c2),
            "cited": [(s, p1, mid), (mid, p2, tail)], "answered": True}


def _ablate(shards, ents, rels, edge):
    s, p, o = edge
    new = dict(shards)
    new[s] = shards[s] - rels[p] * ents[o]
    return new


def blackbox_2hop(shards, ents, rels, out_edges, s, p1, p2):
    res = cortex_2hop(shards, ents, rels, s, p1, p2)
    cands = out_edges.get(s, [])
    if cands:
        p1v = rels[p1]
        scores = [float((rels[p] * np.conj(p1v)).real.sum()) for (p, _o) in cands]
        order = np.argsort(scores)[::-1][:K_CITED_BB]
        cited = [(s, cands[int(i)][0], cands[int(i)][1]) for i in order]
    else:
        cited = []
    return {"answer": res["answer"], "cited": cited, "answered": res["answer"] is not None,
            "conf": res["conf"]}


# ------------------------------- query construction -------------------------


def build_sets(out_edges, sp_objs, direct_targets, g, nq):
    subs = [s for s in out_edges if len(out_edges[s]) > 0]
    all_rels = sorted({p for s in out_edges for (p, _o) in out_edges[s]})
    deg = {s: len(out_edges[s]) for s in out_edges}
    hi_deg = sorted(deg, key=lambda k: -deg[k])
    hi_deg_set = set(hi_deg[:max(1, len(hi_deg) // 3)])  # top third by out-degree = "busy" entities

    answerable, near_miss, legit_corrob, transitivity = [], [], [], []
    seen = {"a": set(), "n": set(), "l": set(), "t": set()}
    tries = 0
    budget = nq * 400
    while tries < budget and (len(answerable) < nq or len(near_miss) < nq or
                              len(legit_corrob) < nq or len(transitivity) < nq):
        tries += 1
        s = subs[int(g.integers(0, len(subs)))]
        p1, mid = out_edges[s][int(g.integers(0, len(out_edges[s])))]

        # ANSWERABLE (for the decisive faithfulness metric): real 2-hop chain
        if mid in out_edges and len(out_edges[mid]) > 0:
            p2, tail = out_edges[mid][int(g.integers(0, len(out_edges[mid])))]
            gold = set()
            for m in sp_objs.get((s, p1), set()):
                gold |= sp_objs.get((m, p2), set())
            if gold and (s, p1, p2) not in seen["a"] and len(answerable) < nq:
                seen["a"].add((s, p1, p2))
                answerable.append({"s": s, "p1": p1, "p2": p2, "gold": gold})

            # TRANSITIVITY split: both edges present (same mid distribution as answerable -> isolates
            # composition-validity from difficulty). corroborated iff tail in direct_targets[s].
            key = (s, p1, p2, mid, tail)
            if tail != s:
                corrob = tail in direct_targets.get(s, set())
                if corrob and key not in seen["l"] and len(legit_corrob) < nq:
                    seen["l"].add(key)
                    legit_corrob.append({"s": s, "p1": p1, "p2": p2, "gold_tail": tail})
                elif (not corrob) and key not in seen["t"] and len(transitivity) < nq:
                    seen["t"].add(key)
                    transitivity.append({"s": s, "p1": p1, "p2": p2, "path_tail": tail})

        # NEAR-MISS: valid hop1 to a BUSY (high-degree) mid, but mid has NO p2 edge (final edge absent)
        if mid in hi_deg_set and mid in out_edges and len(near_miss) < nq:
            mid_have = {p for (p, _o) in out_edges.get(mid, [])}
            cand = [p for p in all_rels if p not in mid_have]
            if cand:
                p2 = cand[int(g.integers(0, len(cand)))]
                if (s, p1, p2, mid) not in seen["n"]:
                    seen["n"].add((s, p1, p2, mid))
                    near_miss.append({"s": s, "p1": p1, "p2": p2, "mid_hint": mid})
    return answerable, near_miss, legit_corrob, transitivity


# ------------------------------- faithfulness helper ------------------------


def faithfulness_on(records, shards, ents, rels, out_edges, g):
    """Ablation faithfulness on a set of query records (each with s,p1,p2). Returns dict of rates."""
    cited_flips = cited_total = noncited_flips = noncited_total = 0
    chain_total = cortex_cov = bb_cov = 0
    for q in records:
        s, p1, p2 = q["s"], q["p1"], q["p2"]
        r = cortex_2hop(shards, ents, rels, s, p1, p2)
        if not r["answered"]:
            continue
        orig = r["answer"]
        cited_edges = set(r["cited"])
        for edge in r["cited"]:
            r2 = cortex_2hop(_ablate(shards, ents, rels, edge), ents, rels, s, p1, p2)
            cited_total += 1
            cited_flips += int(r2["answer"] != orig)
        noncited = []
        for (pp, oo) in out_edges.get(s, []):
            e = (s, pp, oo)
            if e not in cited_edges:
                noncited.append(e)
        mid = r["mid"]
        if mid is not None:
            for (pp, oo) in out_edges.get(mid, []):
                e = (mid, pp, oo)
                if e not in cited_edges:
                    noncited.append(e)
        g.shuffle(noncited)
        for edge in noncited[:N_NONCITED_ABLATE]:
            r2 = cortex_2hop(_ablate(shards, ents, rels, edge), ents, rels, s, p1, p2)
            noncited_total += 1
            noncited_flips += int(r2["answer"] != orig)
        # completeness vs black-box on this query
        rb = blackbox_2hop(shards, ents, rels, out_edges, s, p1, p2)
        bb_cited = set(rb["cited"])
        chain = r["cited"]
        chain_total += len(chain)
        cortex_cov += sum(1 for e in chain if e in cited_edges)
        bb_cov += sum(1 for e in chain if e in bb_cited)
    fc = cited_flips / max(1, cited_total)
    fn = noncited_flips / max(1, noncited_total)
    return {"faithfulness": fc - fn, "flip_cited": fc, "flip_noncited": fn,
            "completeness_cortex": cortex_cov / max(1, chain_total),
            "completeness_bb": bb_cov / max(1, chain_total),
            "n_ablated": cited_total}


# ------------------------------- per-seed run -------------------------------


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed)
    triples, ent, rel = load_triples(MAX_TRIPLES)
    VE, VR = len(ent), len(rel)
    ents = cphasor(VE, N, g)
    rels = cphasor(VR, N, g)
    shards, out_edges, sp_objs, direct_targets = build_shards(triples, ents, rels)
    answerable, near_miss, legit_corrob, transitivity = build_sets(
        out_edges, sp_objs, direct_targets, g, NQ)

    def conf_and_correct(records, gold_key=None):
        confs, correct = [], []
        answered_frac = 0
        for q in records:
            r = cortex_2hop(shards, ents, rels, q["s"], q["p1"], q["p2"])
            confs.append(r["conf"])
            answered_frac += int(r["answered"])
            if gold_key == "gold":
                correct.append(int(r["answered"] and r["answer"] in q["gold"]))
            elif gold_key == "gold_tail":
                correct.append(int(r["answered"] and r["answer"] == q["gold_tail"]))
            else:
                correct.append(0)
        return (np.array(confs, dtype=np.float64), np.array(correct, dtype=np.int64),
                answered_frac / max(1, len(records)))

    ans_conf, ans_correct, _ = conf_and_correct(answerable, "gold")
    near_conf, _, near_answered = conf_and_correct(near_miss)
    legit_conf, _, _ = conf_and_correct(legit_corrob, "gold_tail")
    trans_conf, _, trans_answered = conf_and_correct(transitivity)

    answerable_recall = float(np.mean(ans_correct)) if ans_correct.size else 0.0
    pos_conf = ans_conf[ans_correct == 1]

    # refuse threshold: retain ~90% of answerable-correct (principled, class-independent)
    thr = float(np.percentile(pos_conf, RETAIN_PCTILE)) if pos_conf.size else 0.15

    def refuse_prec(confs):
        return float(np.mean(confs < thr)) if confs.size else 0.0

    # metric: can confidence separate "should-answer" (answerable-correct) from each HARD class that
    # SHOULD be refused? AUROC ~0.5 => confidence CANNOT tell them apart (cannot refuse the class
    # without also refusing legit answers). Both sets are well-populated (NQ each).
    auroc_near = _auroc(pos_conf, near_conf)   # near-miss: hop2 UNSUPPORTED -> expect HIGH AUROC
    auroc_trans = _auroc(pos_conf, trans_conf)  # transitivity: BOTH hops present -> expect ~0.5 (fails)
    # (legit_corrob is rare in a subset; kept only as a reported count, not for AUROC)
    _ = legit_conf

    # v1-style EASY unanswerable (support fully absent) as an on-cell reference point
    easy_unans = []
    subs = [s for s in out_edges if out_edges[s]]
    all_rels = sorted({p for s in out_edges for (p, _o) in out_edges[s]})
    tries = 0
    while len(easy_unans) < NQ and tries < NQ * 200:
        tries += 1
        s = subs[int(g.integers(0, len(subs)))]
        have = {p for (p, _o) in out_edges[s]}
        cand = [p for p in all_rels if p not in have]
        if not cand:
            continue
        p1 = cand[int(g.integers(0, len(cand)))]
        p2 = all_rels[int(g.integers(0, len(all_rels)))]
        easy_unans.append({"s": s, "p1": p1, "p2": p2})
    easy_conf, _, _ = conf_and_correct(easy_unans)
    auroc_easy = _auroc(pos_conf, easy_conf)

    # decisive faithfulness on answerable + on transitivity-answered (audit honest even for fallacy)
    faith_ans = faithfulness_on(answerable, shards, ents, rels, out_edges, g)
    faith_trans = faithfulness_on(transitivity, shards, ents, rels, out_edges, g)

    # ARMS-MUST-DIFFER
    cp = json.dumps([cortex_2hop(shards, ents, rels, q["s"], q["p1"], q["p2"])["cited"]
                     for q in answerable], sort_keys=True).encode()
    bp = json.dumps([blackbox_2hop(shards, ents, rels, out_edges, q["s"], q["p1"], q["p2"])["cited"]
                     for q in answerable], sort_keys=True).encode()
    arms_differ = (hashlib.sha256(cp).hexdigest() != hashlib.sha256(bp).hexdigest()) or not answerable

    return {
        "seed": seed, "VE": VE, "VR": VR,
        "n_answerable": len(answerable), "n_near_miss": len(near_miss),
        "n_legit_corrob": len(legit_corrob), "n_transitivity": len(transitivity),
        "n_easy_unans": len(easy_unans),
        # decisive faithfulness
        "faithfulness_answerable": faith_ans["faithfulness"],
        "flip_cited_answerable": faith_ans["flip_cited"],
        "flip_noncited_answerable": faith_ans["flip_noncited"],
        "answerable_recall_at1": answerable_recall,
        # near-miss (HARD, hop2 unsupported)
        "auroc_nearmiss": auroc_near,
        "refuse_precision_nearmiss": refuse_prec(near_conf),
        "cortex_confabulate_rate_nearmiss": float(np.mean(near_conf >= thr)) if near_conf.size else 0.0,
        "completeness_cortex_nearmiss_n": near_answered,
        # transitivity (HARD, both edges present)
        "auroc_transitivity": auroc_trans,
        "refuse_precision_transitivity": refuse_prec(trans_conf),
        "faithfulness_transitivity": faith_trans["faithfulness"],
        "completeness_cortex_transitivity": faith_trans["completeness_cortex"],
        "completeness_bb_transitivity": faith_trans["completeness_bb"],
        # easy reference (v1 regime) on this cell
        "auroc_easy_unans": auroc_easy,
        "refuse_precision_easy": refuse_prec(easy_conf),
        # black-box refuse (control) + threshold
        "bb_refuse_precision": 0.0,
        "refuse_threshold": thr,
        "answerable_retention": float(np.mean(pos_conf >= thr)) if pos_conf.size else 0.0,
        "arms_differ_verified": bool(arms_differ),
    }


# ------------------------------- verdict ------------------------------------


def verdict(a: Dict) -> Tuple[str, str]:
    f = a["faithfulness_answerable_mean"]
    au_near = a["auroc_nearmiss_mean"]
    au_trans = a["auroc_transitivity_mean"]
    au_easy = a["auroc_easy_unans_mean"]
    rp_near = a["refuse_precision_nearmiss_mean"]
    comp_c_t = a["completeness_cortex_transitivity_mean"]
    comp_b_t = a["completeness_bb_transitivity_mean"]
    s = ("faith_answerable=%.3f | near-miss[AUROC=%.3f refuse_p=%.3f confab=%.3f] | "
         "transitivity[AUROC=%.3f refuse_p=%.3f faith=%.3f completeness cortex=%.3f vs bb=%.3f] | "
         "easy-ref[AUROC=%.3f refuse_p=%.3f] | thr=%.3f retention=%.3f" % (
             f, au_near, rp_near, a["cortex_confabulate_rate_nearmiss_mean"],
             au_trans, a["refuse_precision_transitivity_mean"], a["faithfulness_transitivity_mean"],
             comp_c_t, comp_b_t, au_easy, a["refuse_precision_easy_mean"],
             a["refuse_threshold_mean"], a["answerable_retention_mean"]))
    faith_holds = f >= 0.70
    nearmiss_holds = au_near > 0.65 and rp_near > 0.0
    trans_conf_catches = au_trans > 0.65
    trans_prov_holds = comp_c_t > comp_b_t
    if not faith_holds:
        return ("HARD_FAIL_DECORATIVE",
                "HARD_FAIL_DECORATIVE: decisive faithfulness collapsed (<0.70) on the hard cell. " + s)
    if au_near < 0.60:
        return ("EASY_TEST_ARTIFACT",
                "EASY_TEST_ARTIFACT: near-miss confidence AUROC collapsed to chance -> v1's 1.0 was an "
                "artifact of trivially-far unanswerables; confidence is not a real capability. " + s)
    if faith_holds and nearmiss_holds and trans_prov_holds:
        tnote = ("confidence CATCHES transitivity too" if trans_conf_catches else
                 "per-hop confidence does NOT catch transitivity (expected -- it measures hop-support "
                 "not composition-validity); glass-box value there is auditability (faithful trace)")
        return ("GENUINE_DIFFERENTIATOR",
                "GENUINE_DIFFERENTIATOR: decisive faithfulness holds; near-miss confidence still separates "
                "and refuses where black-box never does; transitivity -> " + tnote + ". " + s)
    return ("PARTIAL_HOLD",
            "PARTIAL_HOLD: some gates degrade on hard unanswerables (see per-class). " + s)


# ------------------------------- main ---------------------------------------


def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=len(SEEDS))
    print("[config] anchor=%s mode=%s N=%d max_triples=%d nq_per_class=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N, MAX_TRIPLES, NQ, SEEDS), flush=True)
    if not FB.exists():
        raise FileNotFoundError("FB15k-237 not found at %s" % FB)
    t0 = time.time()
    per_seed = []
    for seed in SEEDS:
        ts = time.time()
        r = run_seed(seed)
        r["elapsed_s"] = time.time() - ts
        per_seed.append(r)
        print("[seed %d] faith_ans=%.3f | near[auroc=%.3f refuse=%.3f] trans[auroc=%.3f refuse=%.3f "
              "comp c=%.3f/bb=%.3f] easy[auroc=%.3f] | n(a=%d n=%d l=%d t=%d) | %.1fs" % (
                  seed, r["faithfulness_answerable"], r["auroc_nearmiss"], r["refuse_precision_nearmiss"],
                  r["auroc_transitivity"], r["refuse_precision_transitivity"],
                  r["completeness_cortex_transitivity"], r["completeness_bb_transitivity"],
                  r["auroc_easy_unans"], r["n_answerable"], r["n_near_miss"], r["n_legit_corrob"],
                  r["n_transitivity"], r["elapsed_s"]), flush=True)

    cardinality_ok = len(per_seed) == len(SEEDS)

    def _mean(k):
        return float(np.mean([r[k] for r in per_seed]))

    def _std(k):
        return float(np.std([r[k] for r in per_seed]))

    keys = ["faithfulness_answerable", "flip_cited_answerable", "flip_noncited_answerable",
            "answerable_recall_at1", "auroc_nearmiss", "refuse_precision_nearmiss",
            "cortex_confabulate_rate_nearmiss", "auroc_transitivity", "refuse_precision_transitivity",
            "faithfulness_transitivity", "completeness_cortex_transitivity",
            "completeness_bb_transitivity", "auroc_easy_unans", "refuse_precision_easy",
            "bb_refuse_precision", "refuse_threshold", "answerable_retention"]
    agg = {k + "_mean": _mean(k) for k in keys}
    agg["faithfulness_answerable_std"] = _std("faithfulness_answerable")
    agg["auroc_nearmiss_std"] = _std("auroc_nearmiss")
    agg["auroc_transitivity_std"] = _std("auroc_transitivity")

    arms_ok = all(r["arms_differ_verified"] for r in per_seed)
    v, vmsg = verdict(agg)
    if not cardinality_ok:
        v, vmsg = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", "cardinality %d/%d" % (len(per_seed), len(SEEDS))
    elif not arms_ok:
        v, vmsg = "BLOCK_META_RULE_AF", "cortex vs black-box provenance bit-identical"

    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_seeds": len(SEEDS), "agg": agg, "per_seed": per_seed,
               "gates": {"cardinality_ok": cardinality_ok, "arms_differ_verified": arms_ok},
               "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, per_seed)
    print("[metrics] written -> %s" % (out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:500]),
                "summary": "CELL_CRASHED: %s" % type(e).__name__, "run_mode": RUN_MODE,
                "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
                "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid()}
        _out.mkdir(parents=True, exist_ok=True)
        _tmp = _out / "metrics.json.tmp"
        _tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(_tmp, _out / "metrics.json")
        raise
