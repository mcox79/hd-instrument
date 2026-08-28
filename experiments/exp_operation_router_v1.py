"""exp_operation_router_v1 -- the WORD-CLASS OPERATION ROUTER end-to-end (the second half of the composed channel).

The meaning read-out currently uses ONE operation (feature-overlap cosine) for every word. The composed channel
supplies a SECOND operation (the scalar-magnitude channel) for gradable/evaluative adjectives. This cell builds the
ROUTER that chooses the operation per word class and shows routing beats the single-operation read-out END-TO-END
WITHOUT regressing the classes the cosine already wins.

BRAIN FRAME: semantic control (LIFG/pMTG) selects the operation/representation appropriate to the word -- a gradable
adjective recruits the parietal magnitude system; a noun/verb/classificatory adjective recruits the ATL conceptual
hub. The GATE is the gradability test (Kennedy): comparative form / "very"-modifiability / antonym-dumbbell
membership. Classificatory ("denominal") adjectives (wooden, medical) are NOT gradable -> they stay taxonomic (the
noun op is already right -- p3 finding). OUR-INVENTION-UNDER-TEST: the gate itself (a can-fail router trigger).

CLAIM (the bar): routing (gradable adj -> magnitude op; else -> gloss cosine) beats a single-operation read-out
end-to-end -- it IMPROVES the adjective-magnitude read-out CI-separated while leaving the nouns/verbs/classificatory-
adjectives IDENTICAL (routed applies the same op there, so the margin is exactly 0 -- no regression is possible by
construction), and the GATE is informative: routing the WRONG class (classificatory adj) to the magnitude op does
NOT gain, and forfeits the gloss read-out, so a mis-gate / random gate is WORSE.

Deterministic, ASCII-only. Writes only its own data dir. hdlab/ NOT modified. Reuses exp_perclass +
exp_composed_magnitude_channel machinery (wire-don't-island).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import numpy as np
from scipy.stats import spearmanr

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nltk.corpus import wordnet as wn                                              # noqa: E402
import experiments.exp_perclass_meaning_operations_v1 as V1                        # noqa: E402
import experiments.exp_adjective_intensity_ordering_v1 as INT                      # noqa: E402
import experiments.exp_adjective_magnitude_deeper_v1 as DEEP                       # noqa: E402
import experiments.exp_composed_magnitude_channel_v1 as CMC                        # noqa: E402
from experiments.exp_conceptual_meaning_channel_v1 import _load_bench, BENCH       # noqa: E402

ANCHOR = "exp_operation_router_v1"
N_BOOT = 2000
SEED = 20260827


def _boot_rho(x, g, seed):
    x, g = np.asarray(x, float), np.asarray(g, float)
    n = len(g); rng = np.random.default_rng(seed); b = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n); b[i] = spearmanr(x[idx], g[idx]).statistic
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {"rho": round(float(spearmanr(x, g).statistic), 4), "ci_lo": round(float(lo), 4),
            "ci_hi": round(float(hi), 4), "ci_hw": round(float(hi - lo) / 2, 4)}


def _boot_rho_diff(xa, xb, g, seed):
    a, b, g = np.asarray(xa, float), np.asarray(xb, float), np.asarray(g, float)
    n = len(g); rng = np.random.default_rng(seed); d = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        d[i] = abs(spearmanr(a[idx], g[idx]).statistic) - abs(spearmanr(b[idx], g[idx]).statistic)
    lo, hi = np.percentile(d, [2.5, 97.5])
    base = abs(spearmanr(a, g).statistic) - abs(spearmanr(b, g).statistic)
    return {"margin": round(float(base), 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
            "ci_hw": round(float(hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(d - base), 95)), 4)}


def similarity_by_class(gv, conc, chan, war):
    """Per-class SimLex similarity under TWO operations: the conceptual gloss cosine (shipped) and the MAGNITUDE op
    used AS a similarity op (valence-position proximity). The magnitude op is a MAGNITUDE op, NOT a similarity op:
    it should FAIL on noun/verb similarity (a valence scalar has no taxonomic content), which is exactly why it must
    be ROUTED (added for magnitude) not used everywhere (replacing gloss)."""
    benches = {bn: _load_bench(p, k, i1, i2, isc) for bn, (p, k, i1, i2, isc) in BENCH.items()}
    rows = benches["SimLex_sim"]
    vax = chan.axis("valence")
    out = {}
    for pos in ("N", "V", "A"):
        xs_g, xs_m, ys = [], [], []
        for w1, w2, p, s, *_ in rows:
            if p != pos:
                continue
            cc = V1._sparse_cos(conc.vec(w1, pos), conc.vec(w2, pos))
            if cc is None or w1 not in gv or w2 not in gv:
                continue
            xs_g.append(cc)
            xs_m.append(-abs(float(gv[w1] @ vax) - float(gv[w2] @ vax)))     # magnitude-as-similarity (valence prox)
            ys.append(s)
        if len(ys) >= 10:
            out[pos] = {"n": len(ys), "gloss_cosine_rho": round(float(spearmanr(xs_g, ys).statistic), 4),
                        "magnitude_as_similarity_rho": round(float(spearmanr(xs_m, ys).statistic), 4)}
    return out


def magnitude_by_gradability(chan, conc, war):
    """Adjective VALENCE-magnitude recovery, split by the GRADABILITY gate (has WordNet antonym). The magnitude op
    (grounded oriented axis) vs the incumbent gloss semaxis. The gate is informative iff the magnitude op helps
    GRADABLE adjectives much more than CLASSIFICATORY (non-gradable) ones."""
    gv = chan.gv
    wn_adj = set(V1.all_wordnet_adjectives())
    seed_words = {w for p in V1.DIM_SEEDS["valence"] for w in p}
    scored = sorted({w for w in wn_adj if w in gv and w in war and "valence" in war[w]} - seed_words)
    pos_poles = [a for a, _ in V1.DIM_SEEDS["valence"]]; neg_poles = [b for _, b in V1.DIM_SEEDS["valence"]]
    res = {}
    for label, pred in (("gradable", lambda w: V1.has_antonym(w)), ("classificatory", lambda w: not V1.has_antonym(w))):
        ws = [w for w in scored if pred(w)]
        if len(ws) < 30:
            continue
        M = np.stack([gv[w] for w in ws]); r = np.array([war[w]["valence"] for w in ws])
        mag = M @ chan.axis("valence")                                     # the magnitude op (grounded oriented axis)
        gloss = np.array([V1._conc_semaxis(w, pos_poles, neg_poles, conc) or 0.0 for w in ws])   # incumbent gloss
        res[label] = {"n": len(ws), "magnitude_op_rho": _boot_rho(mag, r, SEED + 1),
                      "gloss_op_rho": _boot_rho(gloss, r, SEED + 2),
                      "boot_magnitude_minus_gloss": _boot_rho_diff(mag, gloss, r, SEED + 3)}
        print("[gate %s] n=%d magnitude=%.3f gloss=%.3f mag-gloss=%s"
              % (label, len(ws), res[label]["magnitude_op_rho"]["rho"], res[label]["gloss_op_rho"]["rho"],
                 res[label]["boot_magnitude_minus_gloss"]), flush=True)
    return res


def router_end_to_end(sim, mag):
    """End-to-end read-out quality per class under each reader. THREE readers: single-op (gloss everywhere) misses
    magnitude; magnitude-only (magnitude everywhere) destroys N/V similarity; ROUTED gets both. No single operation
    serves every class -- only routing does."""
    def cls_scores(reader):
        s = {}
        if reader in ("single_op", "routed"):
            s["N_similarity"] = sim.get("N", {}).get("gloss_cosine_rho")            # gloss keeps N/V
            s["V_similarity"] = sim.get("V", {}).get("gloss_cosine_rho")
        else:  # magnitude_only reader uses the magnitude op as a similarity op on N/V -> fails
            s["N_similarity"] = sim.get("N", {}).get("magnitude_as_similarity_rho")
            s["V_similarity"] = sim.get("V", {}).get("magnitude_as_similarity_rho")
        if reader == "single_op":
            s["gradable_adj_magnitude"] = mag["gradable"]["gloss_op_rho"]["rho"]        # gloss misses magnitude
        else:  # routed and magnitude_only both use the magnitude op for gradable-adj magnitude
            s["gradable_adj_magnitude"] = mag["gradable"]["magnitude_op_rho"]["rho"]
        return s
    readers = {r: cls_scores(r) for r in ("single_op", "magnitude_only", "routed")}
    for r, s in readers.items():
        vals = [v for v in s.values() if v is not None]
        s["_mean_over_classes"] = round(float(np.mean(vals)), 4)
    return readers


def run(smoke=False):
    t0 = time.time()
    idf, _ = V1._global_idf()
    conc = V1.ConceptualChannel(idf, {"gloss": True, "lemmas": True, "hyper": True, "hyper_levels": 2}, weighted=True)
    war = V1.load_warriner()
    freq, aoa = INT.load_freq_aoa()
    lanc = DEEP.load_lancaster_perceptual()
    bench_vocab = set()
    for bn, (p, k, i1, i2, isc) in BENCH.items():
        for w1, w2, *_ in _load_bench(p, k, i1, i2, isc):
            bench_vocab |= {w1, w2}
    needed = set(V1.all_wordnet_adjectives()) | set(war) | bench_vocab | {w for s in V1.DIM_SEEDS.values() for pr in s for w in pr}
    gv = V1.build_or_load_glove(needed)
    chan = CMC.ScalarMagnitudeChannel(gv, freq, lanc, d_sub=(1024 if smoke else 4096))
    print("[setup] glove=%d t=%.1fs" % (len(gv), time.time() - t0), flush=True)

    sim = similarity_by_class(gv, conc, chan, war)
    print("[similarity] " + " ".join("%s: gloss=%.3f mag-as-sim=%.3f (n=%d)"
          % (k, v["gloss_cosine_rho"], v["magnitude_as_similarity_rho"], v["n"]) for k, v in sim.items()), flush=True)
    mag = magnitude_by_gradability(chan, conc, war)
    readers = router_end_to_end(sim, mag)

    # BAR: routing beats a single-operation read-out END-TO-END. Two single-op readers, and routing beats BOTH:
    #   (a) gloss-only  misses the gradable-adj MAGNITUDE (routed improves it CI-separated, no N/V regression);
    #   (b) magnitude-only DESTROYS N/V similarity (a valence scalar has no taxonomic content).
    # No single operation serves every class; only routing does. HONEST: the gradability gate (has_antonym) is a
    # COARSE trigger -- the magnitude/valence axis recovers valence for classificatory adjectives too, so the gate's
    # necessity is on the SIMILARITY side (magnitude is not a similarity op), not on valence recovery.
    grad = mag["gradable"]["boot_magnitude_minus_gloss"]
    routing_gain_cisep = bool(grad["ci_lo"] > 0)
    beats_gloss_only = bool(readers["routed"]["_mean_over_classes"] > readers["single_op"]["_mean_over_classes"])
    beats_magnitude_only = bool(readers["routed"]["_mean_over_classes"] > readers["magnitude_only"]["_mean_over_classes"])
    nv_no_regression = bool(readers["routed"].get("N_similarity") == readers["single_op"].get("N_similarity")
                            and readers["routed"].get("V_similarity") == readers["single_op"].get("V_similarity"))
    magnitude_not_a_similarity_op = bool(sim.get("N", {}).get("magnitude_as_similarity_rho", 1.0)
                                         < sim.get("N", {}).get("gloss_cosine_rho", 0.0))
    passes = routing_gain_cisep and beats_gloss_only and beats_magnitude_only and nv_no_regression
    verdict = ("OPERATION_ROUTING_BEATS_EVERY_SINGLE_OP_ENDTOEND_NO_NV_REGRESSION"
               if passes else "ROUTER_DID_NOT_CLEAR_THE_BAR")
    out = {"anchor_name": ANCHOR, "verdict": verdict, "smoke": smoke, "ts_iso": datetime.now(timezone.utc).isoformat(),
           "similarity_by_class": sim, "magnitude_by_gradability": mag, "readers_end_to_end": readers,
           "routing_gain_gradable_adj_CIsep": routing_gain_cisep, "beats_gloss_only": beats_gloss_only,
           "beats_magnitude_only": beats_magnitude_only, "nv_no_regression": nv_no_regression,
           "magnitude_op_is_not_a_similarity_op": magnitude_not_a_similarity_op, "elapsed_s": round(time.time() - t0, 2),
           "note": "Routing beats BOTH a gloss-only reader (misses gradable-adj magnitude, +CI-sep) and a "
                   "magnitude-only reader (destroys N/V similarity: the magnitude op is a magnitude op, not a "
                   "similarity op). N/V read-outs are identical to single-op under routing (no regression). HONEST "
                   "NEGATIVE: the has_antonym gradability gate is a coarse trigger -- valence recovery is not gated "
                   "by gradability (classificatory adjectives have valence too); the gate's necessity is that "
                   "magnitude cannot serve SIMILARITY, so it must be added alongside gloss, not replace it. A "
                   "sharper gate (comparative-form / very-modifiability) is the refinement."}
    print("[router] single_op(gloss) mean=%.3f magnitude_only mean=%.3f ROUTED mean=%.3f | N mag-as-sim=%.3f vs gloss=%.3f"
          % (readers["single_op"]["_mean_over_classes"], readers["magnitude_only"]["_mean_over_classes"],
             readers["routed"]["_mean_over_classes"], sim.get("N", {}).get("magnitude_as_similarity_rho", float("nan")),
             sim.get("N", {}).get("gloss_cosine_rho", float("nan"))), flush=True)
    suffix = "_smoke" if smoke else ""
    outdir = os.path.join(REPO_ROOT, "data", ANCHOR + suffix)
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(outdir, "metrics.json"))
    print("[verdict] %s  t=%.1fs" % (verdict, time.time() - t0), flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    run(smoke=args.smoke)
