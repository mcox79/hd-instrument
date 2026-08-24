"""witness for distributional_meaning_channel -- the acceptance gate.

Feeds the audited instrument counts THROUGH the live separable-store path
(ConceptSpace.observe_context_counts / all_context_counts), builds the organ from THAT, and scores
the licensed substitutability instrument through the organ's substitutability() read-out.

Checks:
  0. licensing gate reproduces (provenance).
  1. organ.phi reproduces the landed cell's phi (proves live-store roundtrip -> SOLVED space).
  2. FAITHFUL read-out AUC via substitutability_batch (the actual organ API) + bootstrap CI.
  2b. INDUCTIVE global-sign single-pair read-out (no reference batch) -- the documented FAILURE.
  3. EXACT landed reproduction: batch read-out with the fit pool disjoint from the instrument words.
  4. TRANSDUCTIVE reference: the landed cell's own scorer (X.score_arm) on the organ's phi+hub.
  5. INFO-FREE TWIN: random-hub distillation through the same batch-oriented read-out -> p50/p95/max.
  6. DEGENERACY: randomized counts -> AUC ~0.5.
  7. OOV -> None (single and batch).

Run: .venv/Scripts/python.exe verification/witness_distributional_meaning_channel.py
ASCII-only. CPU-only, single-threaded pins. NO LLM.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import time
from collections import Counter

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_crossmodal_distillation_substitutability_v1 as X
from experiments.exp_distributional_channel_store_representation_v1 import load_population
from hdlab.reading_grounding_loop import ConceptSpace
from hdlab import distributional_meaning_channel as ORG

GDIR = os.path.join(REPO, "data", "grounding_testbed")
NBOOT = 5000
NNULL = 200
SEED = ORG.MASTER_SEED


def auc_of(a, b):
    return X.auc_of(a, b)


def main():
    t0 = time.time()
    print("[witness] loading audited instrument counts (may be slow on USB)...", flush=True)
    matchedP, matchedS, cached, words_lp, counts, vocab_lp = load_population()
    print("[witness] load_population: words=%d vocab=%d P=%d S=%d"
          % (len(words_lp), len(vocab_lp), len(matchedP), len(matchedS)), flush=True)

    # ----- 0. licensing gate (provenance) -----
    gate = X.licensing_gate(cached, NBOOT)
    print("[0.gate] INSTRUMENT_LICENSED=%s" % gate["INSTRUMENT_LICENSED"], flush=True)

    # ----- live separable-store roundtrip: THE path the organ must consume -----
    cs = ConceptSpace()
    cs.track_context_counts = True
    for w in words_lp:
        cs.observe_context_counts(w, list(counts[w].elements()))
    live_counts = cs.all_context_counts()
    # confirm the roundtrip is exact
    rt_ok = all(live_counts.get(w, Counter()) == counts[w] for w in words_lp) and len(live_counts) == len(words_lp)
    print("[witness] live-store roundtrip exact=%s (%d lemmas)" % (rt_ok, len(live_counts)), flush=True)

    # ----- build the organ from the LIVE store -----
    print("[witness] building organ (PPMI+SVD consolidation, may be slow)...", flush=True)
    channel = ORG.build(live_counts, grounding_dir=GDIR, seed=SEED)
    print("[witness] organ: n_words=%d n_dim=%d fit_pool=%d global_sign=%+.0f"
          % (channel.n_words, channel.n_dim, channel.fit_pool_size, channel.global_sign), flush=True)

    # ----- 1. reproduce landed phi -----
    D_land = X.load_everything()
    same_order = (list(D_land["words_present"]) == channel.words)
    if D_land["phi"].shape == channel.phi.shape and same_order:
        repro = float(np.max(np.abs(np.abs(channel.phi) - np.abs(D_land["phi"]))))
    else:
        repro = 999.0
    print("[1.phi] reproduces_landed(absmax abs-diff of |phi|)=%.3e same_order=%s" % (repro, same_order), flush=True)

    # ----- instrument population (identical construction to the landed cell) -----
    row_idx = channel.row_idx
    present = [(w1, w2, p) for (w1, w2, p) in matchedP + matchedS
               if row_idx.get(w1) is not None and row_idx.get(w2) is not None]
    gold = {" ".join(t[:2]): 1 for t in matchedP}
    y = np.array([gold.get(" ".join(t[:2]), 0) for t in present])
    i1s = np.array([row_idx[w1] for (w1, w2, _) in present])
    i2s = np.array([row_idx[w2] for (w1, w2, _) in present])
    inst_words = set(w for w1, w2, _ in present for w in (w1, w2))
    print("[witness] instrument pairs=%d P=%d S=%d" % (len(present), int(y.sum()), int((y == 0).sum())), flush=True)

    phi = channel.phi

    # grounded hub, exactly the landed cell's, for an apples-to-apples teacher across arms
    hubs = X.build_hubs(channel.words, channel.freq)
    hub, cov = hubs["GROUNDED"]
    # confirm the organ's own hub construction matches the landed cell's
    hub_org, cov_org = ORG.build_grounded_hub(channel.words, GDIR)
    hub_match = float(np.max(np.abs(hub_org - hub))) if hub_org.shape == hub.shape else 999.0
    print("[witness] organ hub matches landed hub? absmax diff=%.3e cov_equal=%s"
          % (hub_match, bool(np.array_equal(cov_org, cov))), flush=True)

    inst_pairs = [(w1, w2) for (w1, w2, _) in present]

    # ----- 2. FAITHFUL read-out: the ACTUAL organ API substitutability_batch (batch-oriented) -----
    api_scores = np.array(channel.substitutability_batch(inst_pairs))
    auc_organ = auc_of(api_scores[y == 1], api_scores[y == 0])
    ci_organ = X.auc_bootstrap(api_scores[y == 1], api_scores[y == 0], NBOOT, SEED + 300)
    print("[2.organ_BATCH] AUC=%.4f CI95=%r halfwidth=%.4f" % (auc_organ, ci_organ["ci95"], ci_organ["ci_halfwidth"]), flush=True)

    # ----- 2b. INDUCTIVE global-sign read-out (single-pair, no reference batch) -- the FAILURE -----
    ind_scores = np.array([channel.substitutability(a, b) for (a, b) in inst_pairs])
    auc_ind = auc_of(ind_scores[y == 1], ind_scores[y == 0])
    print("[2b.inductive_GLOBAL_no_batch] AUC=%.4f global_sign=%+.0f (documents the transductivity trap)"
          % (auc_ind, channel.global_sign), flush=True)

    # ----- 3. EXACT landed reproduction: fit direction with instrument words excluded, batch-orient -----
    ch_disj = ORG.build(live_counts, grounding_dir=GDIR, seed=SEED, exclude_lemmas=inst_words)
    disj_scores = np.array(ch_disj.substitutability_batch(inst_pairs))
    auc_disj = auc_of(disj_scores[y == 1], disj_scores[y == 0])
    ci_disj = X.auc_bootstrap(disj_scores[y == 1], disj_scores[y == 0], NBOOT, SEED + 301)
    print("[3.organ_BATCH_eval_disjoint] AUC=%.4f CI95=%r fit_pool=%d"
          % (auc_disj, ci_disj["ci95"], ch_disj.fit_pool_size), flush=True)

    # ----- 4. TRANSDUCTIVE reference: the landed cell's own scorer on the organ's phi + hub -----
    Xg = phi[i1s] * phi[i2s]
    aucs_tr = []
    for s in range(8):
        r = X.score_arm(phi, Xg, i1s, i2s, hub, cov, inst_words, channel.words, SEED + 200 + s)
        aucs_tr.append(auc_of(r["oriented"][y == 1], r["oriented"][y == 0]))
    aucs_tr = np.array(aucs_tr)
    r0 = X.score_arm(phi, Xg, i1s, i2s, hub, cov, inst_words, channel.words, SEED + 200)
    ci_tr = X.auc_bootstrap(r0["oriented"][y == 1], r0["oriented"][y == 0], NBOOT, SEED + 302)
    print("[4.transductive_LANDED] AUC mean=%.4f sd=%.4f seed0=%.4f CI95=%r"
          % (aucs_tr.mean(), aucs_tr.std(), auc_of(r0["oriented"][y == 1], r0["oriented"][y == 0]),
             ci_tr["ci95"]), flush=True)

    # ----- 5. INFO-FREE TWIN: random hub through the SAME batch-oriented read-out -----
    null = []
    cov_idx_all = np.arange(channel.n_words)
    for s in range(NNULL):
        rh = ORG.l2n(np.random.default_rng(SEED + 10000 + s).standard_normal(
            (channel.n_words, len(ORG.SENS) + len(ORG.AFF))))
        w_n, _ = ORG.fit_direction(phi, rh, cov_idx_all, SEED + ORG._DISTILL_SEED_OFFSET)
        raw_n = (phi[i1s] * phi[i2s]) @ w_n
        href_n = ORG.hub_sim(rh, i1s, i2s)                      # batch orientation, random teacher
        sign_n = 1.0 if np.corrcoef(raw_n, href_n)[0, 1] >= 0 else -1.0
        sc_n = sign_n * raw_n
        null.append(auc_of(sc_n[y == 1], sc_n[y == 0]))
    null = np.array(null)
    twin = {"p50": float(np.percentile(null, 50)), "p95": float(np.percentile(null, 95)),
            "p99": float(np.percentile(null, 99)), "max": float(null.max()),
            "frac_ge_organ": float((null >= auc_organ).mean())}
    print("[5.info_free_twin] p50=%.4f p95=%.4f p99=%.4f max=%.4f frac>=organ=%.3f"
          % (twin["p50"], twin["p95"], twin["p99"], twin["max"], twin["frac_ge_organ"]), flush=True)

    # ----- 6. DEGENERACY: randomized counts -> AUC ~0.5 -----
    rng = np.random.default_rng(SEED + 777)
    vocab_list = list({c for w in channel.words for c in live_counts[w]})
    rand_counts = {}
    for w in channel.words:
        tot = int(sum(live_counts[w].values()))
        tot = max(tot, 1)
        draws = rng.choice(len(vocab_list), size=tot)
        rand_counts[w] = Counter(vocab_list[j] for j in draws)
    try:
        ch_rand = ORG.build(rand_counts, grounding_dir=GDIR, seed=SEED)
        rs = np.array(ch_rand.substitutability_batch([(w1, w2) for (w1, w2, _) in present]))
        auc_degen = auc_of(rs[y == 1], rs[y == 0])
    except Exception as exc:  # noqa: BLE001
        auc_degen = float("nan")
        print("[6.degeneracy] build on random counts raised: %r" % exc, flush=True)
    print("[6.degeneracy] randomized-counts AUC=%.4f (must be ~0.5)" % auc_degen, flush=True)

    # ----- 7. OOV -> None -----
    oov_a = channel.substitutability("qzxwvunknownlemma1", present[0][0])
    oov_b = channel.substitutability(present[0][0], "qzxwvunknownlemma2")
    oov_batch = channel.substitutability_batch([("qzxwvunknownlemma1", present[0][0]), present[0][:2]])
    print("[7.oov] single oov_a=%r oov_b=%r ; batch[oov,in]=%r" % (oov_a, oov_b, oov_batch), flush=True)

    # ----- verdict -----
    floor_p95 = max(X.EXPECTED_AUC["F_CONSTANT_PROTOTYPE"], twin["p95"])   # the brief's bar (p95)
    floor_max = max(X.EXPECTED_AUC["F_CONSTANT_PROTOTYPE"], twin["max"])   # stricter (null MAX)
    ci_lo = ci_organ["ci95"][0]
    clears_p95 = bool(ci_lo > floor_p95)
    clears_max = bool(ci_lo > floor_max)
    reproduces = bool(abs(auc_organ - aucs_tr.mean()) < 0.05 or abs(auc_disj - 0.8389) < 0.02)
    print("\n================ VERDICT ================", flush=True)
    print("organ FAITHFUL (batch)  AUC  = %.4f  CI95=%r" % (auc_organ, ci_organ["ci95"]), flush=True)
    print("organ batch, eval-disjoint   = %.4f  CI95=%r" % (auc_disj, ci_disj["ci95"]), flush=True)
    print("landed (transductive) AUC    = %.4f mean / %.4f seed0" % (aucs_tr.mean(), auc_of(r0["oriented"][y == 1], r0["oriented"][y == 0])), flush=True)
    print("inductive global-sign (fail) = %.4f  (sign-inverted image of the above)" % auc_ind, flush=True)
    print("info-free twin p95 / max     = %.4f / %.4f" % (twin["p95"], twin["max"]), flush=True)
    print("organ CI-lower               = %.4f" % ci_lo, flush=True)
    print("clears twin p95 (brief bar)? = %s (floor %.4f, margin %.4f)" % (clears_p95, floor_p95, ci_lo - floor_p95), flush=True)
    print("clears twin MAX (stricter)?  = %s (floor %.4f, margin %.4f)" % (clears_max, floor_max, ci_lo - floor_max), flush=True)
    print("reproduces landed number?    = %s" % reproduces, flush=True)
    print("phi reproduces landed?       = %s (%.2e)" % (repro < 1e-3, repro), flush=True)
    print("degeneracy ~0.5?             = %s (%.4f)" % (abs(auc_degen - 0.5) < 0.1, auc_degen), flush=True)
    print("OOV -> None?                 = %s" % (oov_a is None and oov_b is None and oov_batch[0] is None), flush=True)
    print("elapsed_s = %.1f" % (time.time() - t0), flush=True)
    print("=========================================", flush=True)


if __name__ == "__main__":
    main()
