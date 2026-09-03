"""SENSE-DISCRIMINATIVE W: the decisive headroom test -- how much of the oracle gap does a GOOD W recover?
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

This session proved: 100% of the loss is the context query; the cue is 85% in-context (oracle-context ceiling
0.853); the brain's mechanism is joint settling over a world-knowledge connection matrix W where relevance ==
connection strength; and over every TOPIC-relatedness W we can build (gloss/SyntagNet/ConceptNet) the mechanism
UNDERPERFORMS because topic reinforces the DOMINANT sense. The open positive-control: does a SENSE-DISCRIMINATIVE
W recover the oracle headroom? This cell answers it with a W-quality ladder, quantifying the target the
world-knowledge/consolidation problem must hit.

W = sense -> context-word DISCRIMINATIVE association (which words indicate THIS sense over its competitors),
scored as a relevance readout: score(sense s) = sum over context words w of Wsd[s][w]. Ladder:
  TOPIC     : the wired diagnostic biased-competition over gloss (topic relatedness) -- the current 0.31 floor.
  LEARNED   : Wsd learned from SemCor TRAIN gold sense tags, DOCUMENT-DISJOINT (a realistic learnable W -- the
              consolidation gate's product, from gold-tagged reading). PMI-style: how much more word w occurs
              in sense s's train contexts than at baseline. Coverage-limited (SemCor train is small).
  ORACLE    : Wsd from ALL data (train+test gold) -- the CEILING a perfect dense clean sense-discriminative W
              reaches with THIS mechanism. Clearly labeled ORACLE (upper bound), the headroom target.
Reported on COVERED senses (isolates the mechanism from coverage) AND overall; headroom recovered =
(a_s - 0.31)/(0.853 - 0.31). Strict document-disjoint eval, subordinate senses, subject a_s, same n~2676.
Info-free twin (shuffle the learned profiles onto wrong senses) must lose. Glass-box, NO LLM. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import json
import time
import math
import argparse
from collections import defaultdict, Counter

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_generative_situation_sense_selector_v1 as V1
import experiments.exp_sg_lite_sense_gestalt_v1 as SG
import experiments.exp_sg_lite_context2vec_encoder_wsd_v1 as C2V
from hdlab import diagnostic_context_wsd as DCW

ORACLE_CEIL = 0.853


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _build_Wsd(recs, mask, w_baseline):
    """Wsd[sense][word] = discriminative weight (PPMI of word given the sense's contexts vs baseline), learned
    from the recs selected by `mask` (their GOLD sense + context). w_baseline = global word frequency (Counter)."""
    sense_ctx = defaultdict(Counter)
    sense_tot = Counter()
    for i, r in enumerate(recs):
        if not mask[i]:
            continue
        for w in r["ctx"]:
            sense_ctx[r["gold"]][w] += 1
            sense_tot[r["gold"]] += 1
    tot_all = sum(w_baseline.values()) + 1e-9
    Wsd = {}
    for s, cc in sense_ctx.items():
        tot_s = sense_tot[s] + 1e-9
        d = {}
        for w, c in cc.items():
            p_w_given_s = c / tot_s
            p_w = w_baseline[w] / tot_all
            if p_w > 0:
                ppmi = max(math.log(p_w_given_s / p_w), 0.0)
                if ppmi > 0:
                    d[w] = ppmi
        Wsd[s] = d
    return Wsd


def run(max_files):
    t0 = time.time()
    emb = SG._build_embeddings(0, "full")
    w2i = emb["w2i"]; w2v = emb["mat"]
    recs = C2V._recs(emb, max_files)
    names = sorted({s for r in recs for s in r["tn"]})
    gsig = {s: C2V._sig(C2V._gloss_word_list(s), w2v, w2i) for s in names}
    doc = np.array([r["doc_id"] for r in recs]); tr = doc % 2 == 0; te = doc % 2 == 1
    sub = np.array([r["subordinate"] for r in recs], bool)
    tsub = te & sub
    print("[run] %d recs (%d subord test) (%.0fs)" % (len(recs), int(tsub.sum()), time.time() - t0), flush=True)

    w_baseline = Counter()
    for r in recs:
        for w in r["ctx"]:
            w_baseline[w] += 1

    Wsd_learned = _build_Wsd(recs, tr, w_baseline)                 # from TRAIN docs only (document-disjoint)
    Wsd_oracle = _build_Wsd(recs, np.ones(len(recs), bool), w_baseline)   # from ALL docs (upper bound)
    seen_learned = set(Wsd_learned.keys())

    def sd_scores(r, Wsd):
        return np.array([sum(Wsd.get(s, {}).get(w, 0.0) for w in r["ctx"]) for s in r["tn"]])

    def diag_scores(r):
        rows = [_unit(w2v[w2i[w]]) for w in r["ctx"] if w in w2i]
        if not rows:
            return np.zeros(len(r["tn"]))
        C = np.stack(rows).astype(np.float32)
        G = np.stack([gsig[s] if gsig[s] is not None else np.zeros(SG.EMB_DIM, np.float32) for s in r["tn"]]).astype(np.float32)
        return DCW.diagnostic_context_scores(C, G)

    idxs = [i for i in range(len(recs)) if tsub[i]]

    def a_s(scorefn, sub_idxs):
        ok = []
        for i in sub_idxs:
            sc = scorefn(recs[i])
            if sc.max() <= 0 and sc.min() >= 0:      # no signal -> abstain as wrong (conservative)
                ok.append(0); continue
            ok.append(int(recs[i]["tn"][int(np.argmax(sc))] == recs[i]["gold"]))
        return np.array(ok, float)

    def headroom(a):
        return round((a - 0.31) / (ORACLE_CEIL - 0.31), 4)

    ok_diag = a_s(diag_scores, idxs); a_diag = float(ok_diag.mean())
    ok_learn = a_s(lambda r: sd_scores(r, Wsd_learned), idxs); a_learn = float(ok_learn.mean())
    ok_orac = a_s(lambda r: sd_scores(r, Wsd_oracle), idxs); a_orac = float(ok_orac.mean())
    # fused: diagnostic + learned discriminative W (the realistic deployable arm)
    def fused(r):
        d = diag_scores(r); s = sd_scores(r, Wsd_learned)

        def z(a):
            a = np.asarray(a, float); sd = a.std(); return (a - a.mean()) / sd if sd > 1e-9 else np.zeros(len(a))
        return z(d) + z(s) if s.max() > 0 else d
    ok_fused = a_s(fused, idxs); a_fused = float(ok_fused.mean())

    # COVERED-only (gold sense seen in TRAIN): isolates the mechanism from coverage
    cov_idxs = [i for i in idxs if recs[i]["gold"] in seen_learned]
    a_learn_cov = float(a_s(lambda r: sd_scores(r, Wsd_learned), cov_idxs).mean()) if cov_idxs else float("nan")
    a_orac_cov = float(a_s(lambda r: sd_scores(r, Wsd_oracle), cov_idxs).mean()) if cov_idxs else float("nan")
    a_diag_cov = float(a_s(diag_scores, cov_idxs).mean()) if cov_idxs else float("nan")
    cov_frac = round(len(cov_idxs) / max(len(idxs), 1), 4)

    # info-free twin: permute the learned profiles onto WRONG senses
    keys = list(Wsd_learned.keys()); rng = np.random.default_rng(7); perm = rng.permutation(len(keys))
    Wsd_twin = {keys[i]: Wsd_learned[keys[perm[i]]] for i in range(len(keys))}
    ok_twin = a_s(lambda r: sd_scores(r, Wsd_twin), idxs)

    out = {"n_test_sub": len(idxs), "oracle_context_ceiling": ORACLE_CEIL, "covered_frac": cov_frac,
           "a_s": {"TOPIC_diagnostic": round(a_diag, 4),
                   "LEARNED_sense_discriminative_W_traindisjoint": round(a_learn, 4),
                   "FUSED_diag_plus_learnedW": round(a_fused, 4),
                   "ORACLE_sense_discriminative_W_upperbound": round(a_orac, 4)},
           "headroom_recovered": {"LEARNED": headroom(a_learn), "FUSED": headroom(a_fused), "ORACLE": headroom(a_orac)},
           "covered_only": {"n": len(cov_idxs), "TOPIC": round(a_diag_cov, 4),
                            "LEARNED": round(a_learn_cov, 4), "ORACLE": round(a_orac_cov, 4)},
           "paired_fused_vs_diag": V1._paired(ok_fused, ok_diag, 1001),
           "paired_learned_vs_twin": V1._paired(ok_learn, ok_twin, 1002),
           "elapsed_s": round(time.time() - t0, 2)}
    out["headline"] = (
        "SENSE-DISCRIMINATIVE W HEADROOM n=%d (cov=%.2f, oracle-ceiling=%.3f) | TOPIC-diag=%.3f | LEARNED-Wsd "
        "(train-disjoint)=%.3f (headroom %.2f) | FUSED=%.3f (vs diag %+.4f sep=%s) | ORACLE-Wsd=%.3f (headroom "
        "%.2f) | covered-only: TOPIC=%.3f LEARNED=%.3f ORACLE=%.3f | learned-vs-twin %+.4f sep=%s"
        % (out["n_test_sub"], cov_frac, ORACLE_CEIL, a_diag, a_learn, out["headroom_recovered"]["LEARNED"],
           a_fused, out["paired_fused_vs_diag"]["delta"], out["paired_fused_vs_diag"]["sep"], a_orac,
           out["headroom_recovered"]["ORACLE"], a_diag_cov, a_learn_cov, a_orac_cov,
           out["paired_learned_vs_twin"]["delta"], out["paired_learned_vs_twin"]["sep"]))
    odir = os.path.join(_REPO, "data", "exp_sg_lite_sense_discriminative_W_headroom_v1")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_sense_discriminative_W_headroom_v1", "verdict": "MEASURED", "result": out},
                  f, indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    print("SELFTEST PASS (sense-discriminative W headroom plumbing)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-files", type=int, default=30)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(args.max_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
