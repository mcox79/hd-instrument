"""exp_meaning_asset_pretrained_positive_control_v1 -- the KNOWN-ANSWER ARM the battery was
missing, and an asset the enumeration missed.

WHY THIS EXISTS, and it is two separate reasons.

(1) THE ENUMERATION MISSED A WHOLE TIER. The prior enumeration walked hdlab/ for modules with a
    vector API and data/ for persisted checkpoints. Three pretrained distributional word tables
    sit in data/gensim_cache/ -- glove-wiki-gigaword-300 (394 MB), word2vec-google-news-300 and
    fasttext-wiki-news-subwords-300 -- and an experiment-resident encoder built on GloVe+WordNet
    (experiments/exp_semantic_hd_encoder_meaning_match_v1.py, verdict MEANING_MATCH_PASS,
    semantic separation 0.507 against a lexical floor of -0.400) uses them. None was scored,
    because the enumeration's SCOPE was hdlab modules and persisted checkpoints, and an
    experiment-resident encoder over an externally-supplied table is neither. I found it only by
    running the mandated substrate-KB prior-work query, which is exactly the check that is
    supposed to catch this. An absence claim is only as good as the enumeration behind it.

(2) A NULL NEEDS A POSITIVE CONTROL OR IT MEASURES THE RULER. Every asset so far lands
    NOT_SEPARATED on 322 SimLex pairs. Two very different worlds produce that: our assets carry
    little meaning, OR the population is too small for ANY asset to separate. Those are
    distinguished by one arm -- a source whose semantic content is not in doubt, run through the
    IDENTICAL scorer, pairs, floors and bootstrap. If GloVe clears comfortably, the instrument
    can detect meaning at n=322 and the nulls are about our assets. If GloVe ALSO lands
    NOT_SEPARATED, the nulls are about the ruler and no conclusion about any asset is available.

WHAT THIS IS NOT. It is NOT a recommendation to wire GloVe in, and no verdict here should be read
as one. GloVe is an EXTERNAL PRETRAINED TABLE. It is not an LLM and nothing is called at
inference -- the codes are a static lookup computed once, the same shape as the Lancaster norms,
which are also externally supplied. Whether an external distributional table is admissible under
the project's foundation policy is an OPERATOR DECISION and is deliberately not made here. It is
loaded from the LOCAL cache with the network never touched.

BRAIN FIDELITY. A co-occurrence table is NOT a claim about how the brain represents word meaning,
and it is not offered as one. It is a measuring instrument: a ceiling marker for what this
population and scorer can resolve. Labelling it otherwise would be the tool-reaching failure.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
os.environ.setdefault("GENSIM_DATA_DIR", str(REPO / "data" / "gensim_cache"))
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import load_units

ANCHOR_NAME = "meaning_asset_pretrained_positive_control_v1"
CACHE = REPO / "data" / "gensim_cache" / "glove-wiki-gigaword-300" / "glove-wiki-gigaword-300.gz"
D_NATIVE = 300
N_PERM = 2000
SEEDS = (7, 17, 23)


def load_glove():
    """Load the LOCAL cached table. No network: the file path is opened directly."""
    from gensim.models import KeyedVectors
    if not CACHE.exists():
        raise SystemExit(f"[fatal] local GloVe cache missing: {CACHE}")
    return KeyedVectors.load_word2vec_format(str(CACHE))


def main() -> int:
    t0 = time.time()
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(INS.SIMLEX) if a in w2i and b in w2i]
    gold = np.array([s for _, _, s in pairs], dtype=np.float64)
    assert len(pairs) == 322, len(pairs)

    print(f"[load] {CACHE.name} ...", flush=True)
    kv = load_glove()
    X = np.zeros((len(words), D_NATIVE), dtype=np.float32)
    miss = np.zeros(len(words), dtype=bool)
    for i, w in enumerate(words):
        if w in kv:
            X[i] = kv[w]
        else:
            miss[i] = True
    g = np.random.default_rng(0x611E)
    X[miss] = 1e-3 * g.standard_normal((int(miss.sum()), D_NATIVE)).astype(np.float32)
    codes = INS._l2n(X)                                   # same normalisation as every other arm
    pair_miss = sum(1 for a, b, _ in pairs if a not in kv or b not in kv)

    ia = np.array([w2i[a] for a, _, _ in pairs])
    ib = np.array([w2i[b] for _, b, _ in pairs])
    cos = np.einsum("ij,ij->i", codes[ia], codes[ib])
    rho = FT._spearman(cos, gold)

    # ---- self-test, BEFORE any verdict
    assert not np.allclose(codes[w2i["cat"]], codes[w2i["dog"]]), "degenerate codes"
    assert kv.vector_size == D_NATIVE, kv.vector_size
    # the table must be the meaning source it claims: a known synonym pair must out-score a
    # known unrelated pair, in the RAW table, before anything is projected or normalised.
    s_syn = float(kv.similarity("car", "automobile"))
    s_unrel = float(kv.similarity("car", "banana"))
    assert s_syn > s_unrel + 0.3, f"table is not a meaning source: {s_syn} vs {s_unrel}"
    # arms-must-differ against the orthographic floor at the same d
    ortho = INS._l2n(INS.build_codes("A_ORTHOGRAPHIC", D_NATIVE, 7, words, pairs, None)[0])
    assert not np.allclose(codes, ortho), "GloVe arm equals the orthographic arm"
    print(f"[selftest] OK  glove rho={rho:.4f}  syn {s_syn:.3f} vs unrel {s_unrel:.3f}  "
          f"vocab miss {int(miss.sum())}/{len(words)}  pairs affected {pair_miss}", flush=True)
    if "--self-test" in sys.argv:
        print("SELFTEST_ONLY_OK")
        return 0

    # ---- floors, all d-matched at 300 and rebuilt here, none reused across d
    lf = np.log(counts + 1.0)
    la, lb = lf[ia], lf[ib]
    freq = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
            "FREQ_MIN": np.minimum(la, lb),
            "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
    freq_rho = {k: FT._spearman(v, gold) for k, v in freq.items()}
    bfk = max(freq_rho, key=lambda k: freq_rho[k])

    ortho_cos, ortho_rho = {}, {}
    for s in SEEDS:
        oc = INS._l2n(INS.build_codes("A_ORTHOGRAPHIC", D_NATIVE, s, words, pairs, None)[0])
        ortho_cos[s] = np.einsum("ij,ij->i", oc[ia], oc[ib])
        ortho_rho[s] = FT._spearman(ortho_cos[s], gold)
    o_best = max(ortho_rho, key=lambda s: ortho_rho[s])

    # own scramble: the null measured properly, 2,000 ROW permutations of this very table
    rng = np.random.default_rng(20260816)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        p = rng.permutation(len(words))
        # codes[p][ia] == codes[p[ia]]; index the permutation, not the whole 4096 x 300 table
        null[i] = FT._spearman(np.einsum("ij,ij->i", codes[p[ia]], codes[p[ib]]), gold)
    p95 = float(np.percentile(null, 95))
    perm_p = float((np.sum(null >= rho) + 1) / (N_PERM + 1))
    # a real scramble draw near that percentile, so the paired bootstrap has per-pair data
    draws = {}
    for s in SEEDS:
        p = np.random.default_rng(s ^ 0xC0FFEE).permutation(len(words))
        draws[s] = np.einsum("ij,ij->i", codes[p[ia]], codes[p[ib]])
    near = min(draws, key=lambda s: abs(FT._spearman(draws[s], gold) - p95))

    cands = {"HARDENED_FREQUENCY_" + bfk: (freq[bfk], freq_rho[bfk]),
             "A_ORTHOGRAPHIC": (ortho_cos[o_best], ortho_rho[o_best]),
             "SCRAMBLE_NULL_P95": (draws[near], p95)}
    bf = max(cands, key=lambda k: cands[k][1])
    diff = FT.boot_rho_diff(cos, cands[bf][0], gold)
    band = FT.band(diff["ci95"])
    clears = bool(band == "ABOVE" and diff["point"] >= FT.T_MARGIN_MIN)

    # ---- head-to-head against our own best arms on the IDENTICAL pairs
    ours = {}
    for s in ("data/exp_meaning_asset_fair_test_v1",
              "data/exp_meaning_asset_fair_test_v1b_distributional"):
        for u in load_units(str(REPO / s)).values():
            if isinstance(u, dict) and "simlex_cos" in u and int(u["seed"]) == 7:
                ours[f"d{u['d']}|{u['arm']}"] = np.array(u["simlex_cos"], np.float64)
    head = {}
    for k in ("d12|ASSET_NORMS12", "d512|ASSET_RETRAIN_ISOL", "d512|ASSET_V2_CTX",
              "d512|ASSET_V2_ISOL", "d1024|ASSET_RI_SYMPAT", "d512|P_LIVE_WORD"):
        if k in ours:
            dd = FT.boot_rho_diff(cos, ours[k], gold)
            head[k] = {"our_rho": round(FT._spearman(ours[k], gold), 4), "glove_minus_ours": dd,
                       "band": FT.band(dd["ci95"])}

    verdict = ("RULER_CAN_DETECT_MEANING_AT_THIS_N" if clears
               else "RULER_CANNOT_SEPARATE_EVEN_A_KNOWN_MEANING_SOURCE")
    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": "full", "n_pairs": len(pairs),
        "role": ("POSITIVE CONTROL / known-answer arm. NOT a recommendation to wire, and NOT a "
                 "brain-fidelity claim -- a co-occurrence table is a measuring instrument here."),
        "asset": {"source": str(CACHE.relative_to(REPO)).replace("\\", "/"),
                  "kind": "external pretrained distributional word table (GloVe 6B, 300d)",
                  "loaded_from": "LOCAL cache, network never touched",
                  "native_d": D_NATIVE, "vector_size": int(kv.vector_size),
                  "vocab_words_missing": int(miss.sum()),
                  "simlex_pairs_with_a_missing_word": pair_miss,
                  "admissibility": ("NOT an LLM and nothing is called at inference; codes are a "
                                    "static offline lookup, the same shape as the Lancaster "
                                    "norms. Whether an external distributional table is "
                                    "admissible under the foundation policy is an OPERATOR "
                                    "decision, deliberately not made in this cell.")},
        "rho": FT.boot_rho(cos, gold),
        "floors": {k: round(v[1], 4) for k, v in cands.items()},
        "frequency_channels_rho": {k: round(v, 4) for k, v in freq_rho.items()},
        "orthographic_by_seed": {str(k): round(v, 4) for k, v in ortho_rho.items()},
        "scramble_null": {"n_permutations": N_PERM, "what_is_permuted": "rows of this table",
                          "mean": float(null.mean()), "sd": float(null.std(ddof=1)),
                          "p95": p95, "max": float(null.max()),
                          "permutation_p_value": perm_p},
        "strongest_floor": bf,
        "margin_over_strongest_floor": diff, "band": band, "clears_floor": clears,
        "head_to_head_vs_our_arms_same_322_pairs": head,
        "verdict": verdict,
        "reading_rule": ("If this arm clears and ours do not, the nulls are about OUR ASSETS and "
                         "not about the population. If this arm also fails to clear, no "
                         "conclusion about any asset is available from this population."),
    }
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["summary"] = verdict
    write_metrics(out_dir, out)
    print(f"GLOVE rho={rho:+.4f} [{out['rho']['ci95'][0]:+.4f},{out['rho']['ci95'][1]:+.4f}]")
    print(f"floors {json.dumps(out['floors'])} -> {bf}")
    print(f"null mean {null.mean():+.4f} sd {null.std(ddof=1):.4f} p95 {p95:+.4f} perm_p {perm_p:.5f}")
    print(f"margin {diff['point']:+.4f} [{diff['ci95'][0]:+.4f},{diff['ci95'][1]:+.4f}] {band}")
    for k, v in head.items():
        d = v["glove_minus_ours"]
        print(f"  vs {k:<26} ours={v['our_rho']:+.4f}  glove-ours={d['point']:+.4f} "
              f"[{d['ci95'][0]:+.4f},{d['ci95'][1]:+.4f}] {v['band']}")
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
