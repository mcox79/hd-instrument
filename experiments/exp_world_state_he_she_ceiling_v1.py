"""exp_world_state_he_she_ceiling_v1 -- the CEILING-LIFT for the register's he/she densification route.

The primary result capped the he/she who-has-what recovery at 0.500 -- the recall of the reader's CURRENT coref
(hdlab.event_centrality_coref.EventCentralityReader) on same-gender transfer pronouns. This cell asks the cron's
question directly: the BRAIN resolves these better than 0.5 -- can WE, with an organ already on disk? It measures
whether the landed-but-unwired brain-faithful graded cue-based retrieval (hdlab.graded_coref_pick, ACT-R
base-level activation; Lewis & Vasishth 2005) + its landed pool-cleanup RAISES the resolution accuracy that bounds
the register, over the reader's incumbent resolver -- quantifying the ceiling-lift the filed next-problem would buy.

ARMS (same he/she pronoun targets, gold clusters; correct = resolved cluster == gold cluster):
  reader_ec      : the reader's OWN resolver (EventCentralityReader.resolve_stream) -- the register's CURRENT input.
  graded         : hdlab.graded_coref_pick.graded_antecedent_pick over the gn-compatible candidate pool (+ the
                   landed keep_after_pool_cleanup). The brain-faithful ACT-R retrieval.
  hard_tier      : the incumbent rigid subject-first pick (graded_coref_pick.hard_tier_pick) -- reference floor.
  recency        : most-recent gn-compatible antecedent (locality floor).
  twin (NULL)    : a random gn-compatible candidate (K-perm -> mean + p95; info-free control).
Reported on (A) ALL he/she pronoun targets (powered, resolver-level) and (B) the TRANSFER-HOLDER subset (the
register-relevant, harder same-gender-competition population). PINNED reuse; NO spaCy/LLM. ASCII only.
# KB_REFERENT: data/corpora/litbank_coref_conll
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_world_state_coref_densify_v1 import extract_ops_idx, _sentences_from_conll, _mention_pos_map

ANCHOR = "world_state_he_she_ceiling_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
LITBANK_DIR = os.path.join(REPO, "data", "corpora", "litbank_coref_conll")
MASC = {"he", "him", "his"}
FEM = {"she", "her", "hers"}


def role_of(m):
    r = m.get("sent_role_rank", 9)
    return "SUBJECT" if r == 0 else ("OBJECT" if r == 1 else "OTHER")


def run_doc(path, reader_ec, sup_kw, gen, lex, lemma_word):
    from hdlab.coref import parse_litbank_conll, build_pronoun_targets, load_name_gender
    from hdlab.graded_coref_pick import graded_antecedent_pick, hard_tier_pick, keep_after_pool_cleanup
    gaz = load_name_gender()
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    if not mentions:
        return []
    targets = build_pronoun_targets(mentions)
    # reader's OWN resolver
    sid = [i // 5 for i in range(n_sents)]
    recs = reader_ec.resolve_stream(mentions, targets, scene_ids=sid, topical_mode="rolemass",
                                    query_memory=True, centrality_mode="event_role", **sup_kw)
    reader_by_midx = {r["target_midx"]: (r.get("resolved_cluster"), bool(r.get("correct"))) for r in recs}

    # cluster -> ordered mentions; cluster gender; cluster head list (for pool cleanup)
    cl_mentions = defaultdict(list)
    for m in mentions:
        cl_mentions[m["cluster"]].append(m)
    cl_gender = {}
    cl_heads = {}
    for c, ms in cl_mentions.items():
        gs = [ (mm.get("gender") or mm.get("name_gender")) for mm in ms ]
        gs = [g for g in gs if g in ("masc", "fem")]
        cl_gender[c] = (max(set(gs), key=gs.count) if gs else None)
        cl_heads[c] = [mm["head"] for mm in ms]

    # which he/she targets are TRANSFER HOLDERS (align to the register's population via the parse)
    toks_by_sent = _sentences_from_conll(path)
    holder_midx = set()
    if len(toks_by_sent) == n_sents:
        posmap = _mention_pos_map(mentions)
        for si, toks in enumerate(toks_by_sent):
            if not toks:
                continue
            try:
                cr = gen.generate(" ".join(toks))
            except Exception:
                continue
            if len(cr.tokens) != len(toks):
                continue
            for inst in extract_ops_idx(cr, lex, lemma_word):
                htok = inst["ARG2"] if (inst["op"] == "GIVE" and inst["ARG2"]) else inst["AGENT"]
                if htok is not None:
                    m = posmap.get((si, htok["wtok"]))
                    if m is not None and m["is_pronoun"] and (m["head"] in MASC or m["head"] in FEM):
                        holder_midx.add(m["midx"])

    rows = []
    for tgt in targets:
        P = tgt["target"]
        g_p = "masc" if P["head"] in MASC else ("fem" if P["head"] in FEM else None)
        if g_p is None:
            continue
        m_p, s_p = P["midx"], P["sent_idx"]
        # gn-compatible candidate clusters with a prior mention
        cand_clusters = []
        cand_priors = []
        cand_headlists = []
        for c, ms in cl_mentions.items():
            priors = [(mm["sent_idx"], role_of(mm)) for mm in ms if mm["midx"] < m_p]
            if not priors:
                continue
            if cl_gender[c] not in (g_p, None):
                continue
            cand_clusters.append(c)
            cand_priors.append(priors)
            cand_headlists.append([mm["head"] for mm in ms if mm["midx"] < m_p])
        if not cand_clusters:
            continue
        gold = P["cluster"]
        # pool cleanup (landed +0.022): drop 1st/2nd-person-artifact clusters
        keep = keep_after_pool_cleanup(cand_headlists)
        kc = [cand_clusters[i] for i in keep] or cand_clusters
        kp = [cand_priors[i] for i in keep] or cand_priors
        # graded (records the calibrated ENTROPY -- the brain's defer/abstain signal, Nieuwland & Van Berkum 2008)
        gp = graded_antecedent_pick(kp, p_sent=s_p, pron_role=role_of(P))
        graded_c = kc[gp["pick"]] if gp["pick"] >= 0 else None
        # hard tier (on the same cleaned pool)
        ht = hard_tier_pick(kp, s_p)
        hard_c = kc[ht] if ht >= 0 else None
        # recency: most-recent-mention gn-compatible candidate
        rec_i = max(range(len(cand_priors)), key=lambda i: max(s for s, _ in cand_priors[i]))
        rec_c = cand_clusters[rec_i]
        rd_c, rd_ok = reader_by_midx.get(m_p, (None, False))
        rows.append({
            "is_holder": int(m_p in holder_midx),
            "reader": int(rd_c == gold) if rd_c is not None else 0,
            "graded": int(graded_c == gold),
            "hard_tier": int(hard_c == gold),
            "recency": int(rec_c == gold),
            "gold": gold,
            "cand_clusters": kc,
            "graded_entropy": float(gp["entropy"]),      # abstain signal (#4)
            "pool_size": len(kc),                        # same-gender competition (#3 residual drill)
            "sent_dist": tgt["sent_dist"],               # antecedent distance (#3)
        })
    return rows


def boot(vals, n_boot, seed):
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return {"acc": None, "ci": [None, None], "n": 0, "half": None}
    rng = np.random.default_rng(seed)
    bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    return {"acc": round(float(vals.mean()), 4), "ci": [round(lo, 4), round(hi, 4)], "n": len(vals),
            "half": round((hi - lo) / 2, 4)}


def paired(rows, a, b, n_boot, seed):
    d = np.asarray([r[a] - r[b] for r in rows], float)
    rng = np.random.default_rng(seed)
    bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    return {"delta": round(float(d.mean()), 4), "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}


def twin_null(rows, n_boot, seed):
    rng = np.random.default_rng(seed)
    accs = []
    for _ in range(n_boot):
        hits = 0
        for r in rows:
            cc = r["cand_clusters"]
            hits += int(cc[rng.integers(0, len(cc))] == r["gold"])
        accs.append(hits / len(rows))
    accs = np.asarray(accs, float)
    return {"mean": round(float(accs.mean()), 4), "p95": round(float(np.percentile(accs, 95)), 4)}


def summarize(rows, tag, n_boot, seed):
    if not rows:
        return {"tag": tag, "n": 0}
    out = {"tag": tag, "n": len(rows)}
    for a in ("reader", "graded", "hard_tier", "recency"):
        out[a] = boot([r[a] for r in rows], n_boot, seed + hash(a) % 500)
    out["twin_null"] = twin_null(rows, n_boot, seed + 7)
    # FAIR pick-only comparison (all three arms use the IDENTICAL gold-clustered candidate pool -> isolates the
    # PICK RULE from entity grouping): graded vs recency vs hard_tier.
    out["graded_minus_recency"] = paired(rows, "graded", "recency", n_boot, seed + 10)
    out["graded_minus_hard"] = paired(rows, "graded", "hard_tier", n_boot, seed + 12)
    out["graded_beats_recency_CIsep"] = bool(out["graded_minus_recency"]["ci"][0] > 0)
    # register-input context (CONFLATES grouping+pick: reader uses its own surface-head overlay, graded uses gold
    # clusters -- so this gap is an UPPER BOUND on the total lift, not the pick-only lift).
    out["graded_minus_reader_UPPERBOUND"] = paired(rows, "graded", "reader", n_boot, seed + 11)
    return out


def run(mode="full", n_docs=100, n_boot=2000, seed=20260901):
    from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.thematic_role_labeler import lemma_word
    from experiments.possession_operators import build_lexicon
    gen = CandidateGenerator.load(os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"),
                                  os.path.join(REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz"))
    lex = build_lexicon(use_cache=True)
    SUP_KW = dict(suppress_generic=True, use_nonref=True, use_struct=True, chain_pronouns=True, use_gazetteer=True)
    reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=7)
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    files = files[:5] if mode == "smoke" else files[:n_docs]
    allrows = []
    for f in files:
        try:
            allrows.extend(run_doc(f, reader_ec, SUP_KW, gen, lex, lemma_word))
        except Exception as e:
            print("  [warn] %s: %s" % (os.path.basename(f), str(e)[:100]), flush=True)
    res = {"anchor": ANCHOR, "mode": mode, "n_docs": len(files)}
    res["ALL_he_she_targets"] = summarize(allrows, "all", n_boot, seed)
    res["TRANSFER_HOLDER_subset"] = summarize([r for r in allrows if r["is_holder"]], "holders", n_boot, seed + 100)

    # #4 CONFIDENCE-ABSTAIN (brain-faithful defer): commit graded picks only below an entropy threshold; report the
    # accuracy-when-committed vs coverage curve. A register that ABSTAINS on uncertain coref is never-confidently-
    # wrong (a wrong holder is worse than "unknown" for downstream state tracking).
    if allrows:
        ent = np.array([r["graded_entropy"] for r in allrows])
        cor = np.array([r["graded"] for r in allrows], float)
        curve = []
        for q in (1.0, 0.8, 0.6, 0.4, 0.2):
            thr = float(np.quantile(ent, q)) if q < 1.0 else float(ent.max() + 1e-9)
            keep = ent <= thr
            if keep.sum() > 0:
                curve.append({"coverage": round(float(keep.mean()), 3),
                              "acc_committed": round(float(cor[keep].mean()), 3), "n": int(keep.sum())})
        res["confidence_abstain_curve"] = curve
        res["abstain_lifts_precision"] = bool(len(curve) >= 2 and curve[-1]["acc_committed"] > curve[0]["acc_committed"])
        # #3 RESIDUAL DRILL: WHY does graded still miss? categorize wrong picks by same-gender pool size + distance.
        wrong = [r for r in allrows if not r["graded"]]
        right = [r for r in allrows if r["graded"]]
        res["graded_residual_drill"] = {
            "n_wrong": len(wrong), "n_right": len(right),
            "mean_pool_when_wrong": round(float(np.mean([r["pool_size"] for r in wrong])), 2) if wrong else None,
            "mean_pool_when_right": round(float(np.mean([r["pool_size"] for r in right])), 2) if right else None,
            "mean_dist_when_wrong": round(float(np.mean([r["sent_dist"] for r in wrong])), 2) if wrong else None,
            "mean_dist_when_right": round(float(np.mean([r["sent_dist"] for r in right])), 2) if right else None,
            "mean_entropy_when_wrong": round(float(np.mean([r["graded_entropy"] for r in wrong])), 3) if wrong else None,
            "mean_entropy_when_right": round(float(np.mean([r["graded_entropy"] for r in right])), 3) if right else None,
        }
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def _show(s):
    if not s.get("n"):
        print("  (%s: no items)" % s["tag"], flush=True)
        return
    print("  [%s] n=%d  reader=%.3f %s  graded=%.3f %s  hard_tier=%.3f  recency=%.3f  twin_p95=%.3f"
          % (s["tag"], s["n"], s["reader"]["acc"], s["reader"]["ci"], s["graded"]["acc"], s["graded"]["ci"],
             s["hard_tier"]["acc"], s["recency"]["acc"], s["twin_null"]["p95"]), flush=True)
    print("       FAIR pick-only (same gold pool): graded-recency %.3f %s (CI-sep %s) ; graded-hard %.3f %s"
          % (s["graded_minus_recency"]["delta"], s["graded_minus_recency"]["ci"], s["graded_beats_recency_CIsep"],
             s["graded_minus_hard"]["delta"], s["graded_minus_hard"]["ci"]), flush=True)
    print("       register-input UPPER BOUND (grouping+pick): graded-reader %.3f %s"
          % (s["graded_minus_reader_UPPERBOUND"]["delta"], s["graded_minus_reader_UPPERBOUND"]["ci"]), flush=True)


def self_test():
    from hdlab.graded_coref_pick import graded_antecedent_pick
    # two candidates: a topical subject (cluster 1, subject in sents 0,1) vs a fleeting object (cluster 2, sent 1).
    cp = [[(0, "SUBJECT"), (1, "SUBJECT")], [(1, "OBJECT")]]
    g = graded_antecedent_pick(cp, p_sent=2, pron_role="SUBJECT")
    print("[self-test] graded picks topical subject (idx0): %s (pick=%d)" % (g["pick"] == 0, g["pick"]), flush=True)
    return 0 if g["pick"] == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_boot=(400 if mode == "smoke" else args.n_boot))
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    print("\n  CEILING-LIFT for the register's he/she route (LitBank, %d docs):" % res["n_docs"], flush=True)
    _show(res["ALL_he_she_targets"])
    _show(res["TRANSFER_HOLDER_subset"])
    if res.get("confidence_abstain_curve"):
        print("  #4 CONFIDENCE-ABSTAIN (graded entropy) accuracy-when-committed vs coverage:", flush=True)
        for c in res["confidence_abstain_curve"]:
            print("     coverage=%.2f  acc_committed=%.3f (n=%d)" % (c["coverage"], c["acc_committed"], c["n"]), flush=True)
        d = res["graded_residual_drill"]
        print("  #3 RESIDUAL DRILL: pool when wrong=%s vs right=%s ; dist wrong=%s vs right=%s ; entropy wrong=%s vs right=%s"
              % (d["mean_pool_when_wrong"], d["mean_pool_when_right"], d["mean_dist_when_wrong"],
                 d["mean_dist_when_right"], d["mean_entropy_when_wrong"], d["mean_entropy_when_right"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
