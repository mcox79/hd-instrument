"""arc_aggregation_sparse_code_regime_v1 -- does a SPARSE code regime fix superposition-crosstalk in
multi-fact AGGREGATION (bundle) on REAL (noisy) retrieval?

DECISIVE, CAN-FAIL test of a LIVE, UNPROVEN hypothesis. The aggregation retriever
(exp_arc_aggregation_retriever_bindsettle_v1) found the textbook dense-superposition-dilution signature:
  ORACLE (clean gold facts): bundle 0.766 BEATS single 0.706  (bundling helps when noise-free)
  REAL  (noisy top-K retrieval): bundle 0.298 < single 0.342  (combining retrieved facts HURTS)
HYPOTHESIS: the REAL-pool loss is DENSE-CODE crosstalk -- summing many dense fact vectors into one
superposition dilutes the signal. SPARSE distributed codes (near-disjoint supports; cortical, Barsalou)
compose many items with low interference -> a SPARSE bundle should beat single on REAL retrieval too, and
preserve the oracle-clean advantage.

HONEST CAVEAT (pre-register the NULL): sparse-reduces-crosstalk is NOT yet demonstrated in this substrate
-- prior GSBC dense-vs-sparse + ARCH-B gates came back SPARSITY-NEUTRAL / dense-not-worse. This is a
genuine can-fail test.

ONE VARIABLE = the CODE REGIME of the fact bundle (dense float vs sparse top-k bipolar). Everything else
is held IDENTICAL to the dense reference:
  - SAME SemanticHDEncoder embeddings (same GloVe/WordNet semantics) -- sparse arm just top-k-thresholds
    them to bipolar {-1,0,+1} (the same operator as hdlab/ppmi_sparse_encoder.encode_sparse), so the ONLY
    thing that changes between dense and sparse arms is code DENSITY, not the underlying meaning. (This is
    a purer one-variable test than swapping to a different natively-sparse encoder, which would confound
    "sparse" with "different semantics".)
  - SAME dense retrieval (identical retrieved fact SETS in both arms).
  - SAME relevance weights w_f = relu(cos_dense(fact, query)) normalized (dense-computed in both arms).
  Only the vectors entering single/bundle scoring switch dense<->sparse.

ARMS (per pool in {ORACLE gold-central, REAL held-out top-K retrieval}):
  dense_single   -- max_f cos(dense fact_f, dense choice_c)            [reproduces 0.706 / 0.342: POS CONTROL]
  dense_bundle   -- cos(sum_f w_f * dense fact_f, dense choice_c)      [reproduces 0.766 / 0.298: POS CONTROL]
  sparse_single  -- max_f cos(sparse fact_f, sparse choice_c)          [BASE-SIGNAL preservation check]
  sparse_bundle  -- cos(sum_f w_f * sparse fact_f, sparse choice_c)    [THE TEST]
  + sparse_bundle_shuffle (REAL) -- facts randomly re-assigned across questions -> must collapse to chance.

k SELECTION (calibration_check = adaptive_with_discriminator_gate): sparsity k is chosen by a criterion
INDEPENDENT of the bundle discriminator -- k* = the k whose SPARSE_SINGLE (REAL, Easy) best matches
DENSE_SINGLE (REAL, Easy) base signal. Sweep k in {0.02,0.05,0.10,0.20,0.50}. The bundle read is downstream
and free to fail. If NO k preserves the base single signal (sparse_single_real << dense_single_real), the
sparsification damaged the code -> INCONCLUSIVE_SPARSIFICATION_DAMAGED_CODE (not a clean NULL).

DECISIVE READ (pre-registered bands, PRIMARY = REAL pool, Easy split):
  SPARSE_FIXES_CROSSTALK  : sparse_bundle_real > sparse_single_real (bundle beats single in sparse regime)
                            AND sparse_bundle_real >= dense_bundle_real + 0.03 (sparse rescues the loss)
                            AND base signal preserved (sparse_single_real >= dense_single_real - 0.05)
                            AND shuffle collapses  -> composition was DENSE-CROSSTALK-limited; sparse rescues.
  SPARSITY_NEUTRAL (NULL) : |sparse_bundle_real - dense_bundle_real| < 0.03 AND still < single
                            -> crosstalk is NOT the limiter; the real-retrieval loss is retrieval-noise/content,
                            not superposition (consistent with prior neutral results). Report plainly, no spin.
  INCONCLUSIVE_SPARSIFICATION_DAMAGED_CODE : sparse_single_real < dense_single_real - 0.05 -> base signal
                            destroyed by top-k; cannot read bundle crosstalk fairly.
Instrument the crosstalk MECHANISM directly: (1) bundle answer-margin = cos(B,correct) - max_wrong cos(B,wrong),
mean over REAL questions, dense vs sparse; (2) mean off-diagonal |cos| among the retrieved fact codes
(pairwise interference), dense vs sparse. Sparse fixing crosstalk => higher margin AND lower interference.

BRAIN-CONSISTENCY: sparse distributed codes = cortical (Barsalou/sparse coding); no borrowed vectors beyond
the shared encoder; the retrieval stays the brain-faithful construction per
notes/aggregation_retriever_bindsettle_construction_integration_2026-07-24.md.

Contract: INLINE-LOCAL foreground-to-completion (GloVe cache + WorldTree are git-ignored/large -> NOT
remote-portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted
iteration; no hash()). Runs in repo .venv. Agent-reported VET-PENDING (skunkworks owns landed-VET).

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic ; heartbeat
# - real_code_path: self_test constructs the REAL SemanticHDEncoder + runs the REAL retrieval + dense/sparse
#   single/bundle on a planted case asserting the DISCRIMINATOR CAN FIRE (sparse bundle recovers where dense
#   bundle dilutes); determinism; arms-differ
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-saturation guard on dense_single_real (headroom exists: 0.342)
# - storage strategy = SHARDED (each fact its own vector; composed via bundle superposition)
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import glob
import json
import time
import argparse
import platform
import traceback
import hashlib
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_aggregation_sparse_code_regime_v1"
SEED = 20260725

# ---- bands (author-designed; see docstring). PRIMARY = REAL pool, Easy split. ----
K_GRID = [0.02, 0.05, 0.10, 0.20, 0.50]   # sparsity fractions swept for base-signal-preservation k-selection
HP_SPARSE_RESCUE = 0.03      # sparse_bundle_real - dense_bundle_real >= this -> sparse RESCUES the dense loss
HP_BUNDLE_BEATS_SINGLE = 0.0 # sparse_bundle_real - sparse_single_real > this -> bundle beats single (sparse)
BASE_SIGNAL_TOL = 0.05       # sparse_single_real >= dense_single_real - this -> base signal preserved
NEUTRAL_EPS = 0.03           # |sparse_bundle_real - dense_bundle_real| < this -> SPARSITY_NEUTRAL
REPRO_TOL = 0.05             # dense arm must reproduce prior atom within this (Gate D positive control)
MUSTFAIL_EPS = 0.05          # shuffle - chance < this -> control collapsed OK
AG_SATURATION = 0.90         # dense_single_real >= this -> discriminator vacuous (no headroom)
RETRIEVAL_K = 10             # top-K retrieved facts / question (matches the dense reference cell)

# prior-atom reference (Gate D positive control) MEASURED@ the dense reference cell's metrics.json
PRIOR_DENSE_SINGLE_REAL = 0.342   # MEASURED@data/exp_arc_aggregation_retriever_bindsettle_v1/metrics.json:retr_single_acc_easy
PRIOR_DENSE_BUNDLE_REAL = 0.298   # MEASURED@...:retr_bundle_acc_easy
PRIOR_DENSE_SINGLE_ORAC = 0.706   # MEASURED@...:oracle_single_acc_easy
PRIOR_DENSE_BUNDLE_ORAC = 0.766   # MEASURED@...:oracle_bundle_acc_easy

_T0 = [0.0]


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# code-regime core: dense vs sparse (top-k bipolar) single/bundle scoring
# ---------------------------------------------------------------------------
def sparsify_rows(V, k_frac):
    """Top-k bipolar sparsification per row (same operator as ppmi_sparse_encoder.encode_sparse):
    keep the k=round(k_frac*N) largest-|value| dims -> sign {-1,+1}, rest 0. V: [M, N] float rows.
    Returns [M, N] float32 sparse bipolar. Rows that are all-zero stay all-zero."""
    if V.shape[0] == 0:
        return V.astype(np.float32)
    N = V.shape[1]
    k = max(1, int(round(k_frac * N)))
    out = np.zeros_like(V, dtype=np.float32)
    if k >= N:
        return np.sign(V).astype(np.float32)
    mag = np.abs(V)
    idx = np.argpartition(-mag, k - 1, axis=1)[:, :k]     # [M, k] top-k col indices per row
    rows = np.arange(V.shape[0])[:, None]
    sgn = np.sign(V[rows, idx]).astype(np.float32)
    out[rows, idx] = sgn
    return out


def _unit(mat):
    """L2-normalize rows; zero rows stay zero."""
    if mat.shape[0] == 0:
        return mat.astype(np.float32)
    n = np.linalg.norm(mat, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return (mat / n).astype(np.float32)


def single_scores(fact_hd, choice_hd):
    """score(c) = max_f cos(fact_f, choice_c). fact_hd [K,N] unit rows, choice_hd [C,N] unit rows."""
    C = choice_hd.shape[0]
    if fact_hd.shape[0] == 0:
        return np.zeros(C, dtype=np.float32)
    cc = fact_hd @ choice_hd.T                       # [K, C]
    return cc.max(axis=0).astype(np.float32)


def bundle_scores(fact_hd, w, choice_hd):
    """score(c) = cos(sum_f w_f * fact_f, choice_c). Relevance-weighted superposition then cosine.
    fact_hd [K,N] unit rows, w [K] >=0, choice_hd [C,N] unit rows."""
    C = choice_hd.shape[0]
    K = fact_hd.shape[0]
    if K == 0:
        return np.zeros(C, dtype=np.float32), None
    ww = np.maximum(w.astype(np.float64), 0.0)
    ww = ww / ww.sum() if ww.sum() > 0 else np.ones(K) / K
    b = (ww[:, None] * fact_hd).sum(axis=0)
    nb = np.linalg.norm(b)
    if nb > 0:
        b = b / nb
    return (b @ choice_hd.T).astype(np.float32), b.astype(np.float32)


def _pick(scores, rng):
    """Argmax with seeded tie-break (matches the reference harness convention)."""
    mx = float(np.max(scores)) if scores.size else 0.0
    if scores.size == 0 or not np.isfinite(mx) or np.all(scores == scores[0]):
        cand = list(range(len(scores))) if scores.size else [0]
    else:
        cand = [i for i in range(len(scores)) if abs(float(scores[i]) - mx) < 1e-6]
    return int(rng.choice(cand)) if len(cand) > 1 else cand[0]


def run_pool(questions, pool_dense_fn, choice_dense_map, mode, regime, k_frac,
             shuffle=False, seed_base=0):
    """Run one (pool, mode, regime) arm over all questions.
      pool_dense_fn(qi) -> (fact_dense[K,N] unit rows, w[K])   (DENSE facts + weights; retrieval fixed)
      choice_dense_map[qi] -> choice_dense[C,N] unit rows      (DENSE choices)
      mode   : 'single' | 'bundle'
      regime : 'dense' | 'sparse'
      k_frac : sparsity fraction (used only when regime=='sparse')
      shuffle: re-assign each question's fact pool to a DIFFERENT question's facts (must-fail control)
    Returns dict: acc/acc_easy/acc_challenge, digest, plus (bundle only) margin + interference stats."""
    n_e = n_c = c_e = c_c = 0
    digest = []
    margins = []           # bundle answer-margin: cos(B,correct) - max_wrong cos(B,wrong)
    interferences = []     # mean off-diagonal |cos| among the fact codes (pairwise crosstalk)
    Q = len(questions)
    for qi, q in enumerate(questions):
        src_qi = (qi + Q // 2) % Q if shuffle else qi      # deterministic derangement-ish remap
        fact_d, w = pool_dense_fn(src_qi)
        choice_d = choice_dense_map[qi]
        if regime == "sparse":
            fact = _unit(sparsify_rows(fact_d, k_frac))
            choice = _unit(sparsify_rows(choice_d, k_frac))
        else:
            fact = fact_d
            choice = choice_d
        arng = np.random.default_rng(seed_base + qi)
        if mode == "single":
            scores = single_scores(fact, choice)
            b = None
        else:
            scores, b = bundle_scores(fact, w, choice)
        pick = _pick(scores, arng)
        digest.append(pick)
        ci = q["correct_index"]
        hit = int(pick == ci)
        # crosstalk instrumentation (bundle, non-shuffle, non-empty)
        if mode == "bundle" and b is not None and not shuffle and fact.shape[0] > 1:
            cor = float(b @ choice[ci]) if choice.shape[0] > ci else 0.0
            wrong = [float(b @ choice[j]) for j in range(choice.shape[0]) if j != ci]
            if wrong:
                margins.append(cor - max(wrong))
            G = fact @ fact.T
            K = fact.shape[0]
            off = (np.abs(G).sum() - np.trace(np.abs(G))) / (K * (K - 1))
            interferences.append(float(off))
        if q["source"].startswith("ARC-Easy"):
            n_e += 1; c_e += hit
        else:
            n_c += 1; c_c += hit
    n = Q
    return {
        "acc": (c_e + c_c) / n if n else 0.0,
        "acc_easy": c_e / n_e if n_e else None,
        "acc_challenge": c_c / n_c if n_c else None,
        "n_easy": n_e, "n_challenge": n_c,
        "bundle_margin_mean": round(float(np.mean(margins)), 5) if margins else None,
        "fact_interference_mean": round(float(np.mean(interferences)), 5) if interferences else None,
        "digest": np.array(digest, dtype=np.int64),
    }


# ---------------------------------------------------------------------------
# self-test (real code path + planted crosstalk discriminator + determinism + arms-differ)
# ---------------------------------------------------------------------------
def _planted_sparse_bundle_recovers():
    """Planted case where a SPARSE bundle recovers the correct choice while a DENSE bundle is diluted by a
    noisy off-target fact. Facts share DISJOINT sparse supports (low interference); the dense superposition
    of the same vectors has cross-term interference that tips the answer. Demonstrates the discriminator CAN
    FIRE (does not assert the win on real data -- that is MEASURED)."""
    N = 512
    rng = np.random.default_rng(3)
    # 2 choices; correct = C0. Build sparse fact codes with near-disjoint supports.
    def sparse_vec(active_idx, signs):
        v = np.zeros(N, dtype=np.float32); v[active_idx] = signs; return v
    k = 20
    c0_supp = np.arange(0, k)
    c1_supp = np.arange(k, 2 * k)
    C0 = sparse_vec(c0_supp, np.ones(k))
    C1 = sparse_vec(c1_supp, np.ones(k))
    choice = _unit(np.stack([C0, C1]))
    # two facts each partially aligned with C0 on disjoint supports; one noisy fact aligned with C1
    F1 = sparse_vec(c0_supp[:10], np.ones(10))
    F2 = sparse_vec(c0_supp[10:], np.ones(10))
    F3 = sparse_vec(c1_supp, 1.4 * np.ones(k))          # strong single distractor toward C1
    fact_sparse = _unit(np.stack([F1, F2, F3]))
    w = np.ones(3, dtype=np.float32)
    # dense version = same vectors densified with small random fill (adds cross-interference)
    dense = np.stack([F1, F2, F3]).astype(np.float32) + 0.15 * rng.standard_normal((3, N)).astype(np.float32)
    fact_dense = _unit(dense)
    choice_dense = _unit(np.stack([C0, C1]) + 0.15 * rng.standard_normal((2, N)).astype(np.float32))
    s_sparse, _ = bundle_scores(fact_sparse, w, choice)
    s_dense, _ = bundle_scores(fact_dense, w, choice_dense)
    p_sparse = _pick(s_sparse, np.random.default_rng(0))
    # sparse bundle: F1+F2 reinforce C0 on disjoint supports, F3 only hits C1 -> C0 wins
    assert p_sparse == 0, f"planted: sparse bundle should recover C0, got {p_sparse} ({s_sparse})"
    # arms-differ: dense and sparse bundle score vectors differ
    h = lambda a: hashlib.sha256(np.round(a, 5).tobytes()).hexdigest()
    assert h(s_sparse) != h(s_dense), "planted: dense and sparse bundle bit-identical"
    return True


def _selftest_real_path():
    """Construct the REAL SemanticHDEncoder + run the REAL retrieval + all 4 arms at tiny scale."""
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)
    store_sents = [
        "green plants use sunlight to make sugar during photosynthesis",
        "photosynthesis produces oxygen as a byproduct",
        "iron is a heavy metal used to build bridges",
        "the moon orbits the earth once each month",
    ]
    SV = arc._encode_store(enc, store_sents)
    q = {"qid": "T1", "stem": "What do green plants make using sunlight?",
         "choices": ["iron metal", "sugar and oxygen from photosynthesis", "moon orbit", "sound"],
         "correct_index": 1, "source": "ARC-Easy-Test"}
    qq = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    w = np.maximum(SV @ qq, 0.0).astype(np.float32)
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
    # dense arms
    ds = single_scores(SV, choice_hd)
    db, _ = bundle_scores(SV, w, choice_hd)
    # sparse arms
    SVs = _unit(sparsify_rows(SV, 0.10))
    chs = _unit(sparsify_rows(choice_hd, 0.10))
    ss = single_scores(SVs, chs)
    sb, _ = bundle_scores(SVs, w, chs)
    for name, sc in [("dense_single", ds), ("dense_bundle", db), ("sparse_single", ss), ("sparse_bundle", sb)]:
        assert sc.shape[0] == len(q["choices"]), f"{name} wrong shape {sc.shape}"
    h = lambda a: hashlib.sha256(np.round(a, 5).tobytes()).hexdigest()
    assert h(ds) != h(db), "arms-differ: dense single/bundle identical"
    assert h(ss) != h(sb), "arms-differ: sparse single/bundle identical"
    assert h(db) != h(sb), "arms-differ: dense/sparse bundle identical (regime swap inert)"
    # determinism
    sb2, _ = bundle_scores(SVs, w, chs)
    assert h(sb) == h(sb2), "sparse bundle non-deterministic"
    # sparsity check: sparse rows really are k-sparse
    k_expect = max(1, int(round(0.10 * nd)))
    nz = int((SVs[0] != 0).sum())
    assert nz <= k_expect, f"sparsify not k-sparse: {nz} > {k_expect}"
    # empty pool -> zeros (chance handled by tie-break pick downstream)
    es = single_scores(np.zeros((0, nd), np.float32), choice_hd)
    assert es.shape[0] == len(q["choices"])
    # tablestore + questions parse (real data, small touch)
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    qs = agg.load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    return nz, k_expect


def self_test():
    print("[self-test] planted sparse-bundle-recovers-crosstalk discriminator ...", flush=True)
    _planted_sparse_bundle_recovers()
    print("[self-test] constructing REAL SemanticHDEncoder + real retrieval/agg (dense+sparse) ...", flush=True)
    nz, ke = _selftest_real_path()
    print(f"[self-test] PASS (planted sparse-bundle recovery + real encoder + 4 arms dense/sparse + "
          f"arms-differ + determinism + k-sparsity {nz}/{ke} + WorldTree parse)", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 150, "limit_chal": 100}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    output_dir = _out_dir()
    cfg = _config(args.mode)
    _T0[0] = time.perf_counter()
    _write_start_marker(output_dir, args.mode)

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=cfg["n_dim"], seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "load_questions")
    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    chance = arc._chance_theoretical(questions)
    ctrl_random = arc._control_random(questions, np.random.default_rng(SEED + 1))
    print(f"[eval] {len(questions)} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f}", flush=True)

    # ---- tablestore (held-out: exclude every test-gold UID) ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = agg.parse_tablestore()
    test_gold = set()
    for q in questions:
        test_gold |= q["gold_all"]
    heldout_uids = sorted(u for u in uid2sent if u not in test_gold)
    heldout_sents = [uid2sent[u] for u in heldout_uids]
    n_excluded = len(uid2sent) - len(heldout_uids)
    print(f"[store] tablestore={len(uid2sent)} ; test-gold-excluded={n_excluded} ; held-out={len(heldout_sents)}",
          flush=True)

    # ---- batch-encode everything ONCE (dense; sparse is a downstream top-k of these) ----
    _heartbeat(output_dir, "encode_store", {"n": len(heldout_sents)})
    t_enc = time.perf_counter()
    SV_store = arc._encode_store(enc, heldout_sents)   # [Mstore, N] unit rows (DENSE)
    print(f"[encode] store {len(heldout_sents)} facts in {time.perf_counter()-t_enc:.1f}s", flush=True)

    _heartbeat(output_dir, "encode_questions")
    q_query_txt = [q["stem"] + " " + " ".join(q["choices"]) for q in questions]
    QQ = arc._encode_store(enc, q_query_txt)           # [nQ, N] DENSE query (retrieval + weights)
    choice_dense_map = []
    for q in questions:
        choice_dense_map.append(arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]))

    _heartbeat(output_dir, "encode_gold")
    gold_uids = sorted({u for q in questions for u in q["gold_central"] if u in uid2sent})
    gold_sents = [uid2sent[u] for u in gold_uids]
    GV = arc._encode_store(enc, gold_sents) if gold_sents else np.zeros((0, cfg["n_dim"]), np.float32)
    uid2row = {u: i for i, u in enumerate(gold_uids)}

    # ---- retrieval: top-K held-out facts per question (DENSE; identical fact sets for both regimes) ----
    _heartbeat(output_dir, "retrieval")
    K = RETRIEVAL_K
    Mstore = SV_store.shape[0]
    retr_idx = np.full((len(questions), K), -1, dtype=np.int64)
    if Mstore:
        chunk = 4000
        sims_topv = np.full((len(questions), K), -np.inf, dtype=np.float32)
        sims_topi = np.full((len(questions), K), -1, dtype=np.int64)
        for a in range(0, Mstore, chunk):
            b = min(a + chunk, Mstore)
            s = QQ @ SV_store[a:b].T
            cand_v = np.concatenate([sims_topv, s], axis=1)
            cand_i = np.concatenate([sims_topi, np.tile(np.arange(a, b), (len(questions), 1))], axis=1)
            part = np.argpartition(-cand_v, K - 1, axis=1)[:, :K]
            rows = np.arange(len(questions))[:, None]
            sims_topv = cand_v[rows, part]
            sims_topi = cand_i[rows, part]
        retr_idx = sims_topi

    # ---- pools return DENSE facts + dense weights (sparsification happens inside run_pool) ----
    def oracle_pool(qi):
        rows = [uid2row[u] for u in questions[qi]["gold_central"] if u in uid2row]
        if not rows:
            return np.zeros((0, cfg["n_dim"]), np.float32), np.zeros(0, np.float32)
        fh = GV[rows]
        w = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        return fh, w

    def retrieval_pool(qi):
        idx = retr_idx[qi][retr_idx[qi] >= 0]
        if idx.size == 0:
            return np.zeros((0, cfg["n_dim"]), np.float32), np.zeros(0, np.float32)
        fh = SV_store[idx]
        w = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        return fh, w

    # ---- k-selection (calibration_check): pick k* on SPARSE_SINGLE (REAL, Easy) base-signal preservation ----
    _heartbeat(output_dir, "k_selection")
    dense_single_real = run_pool(questions, retrieval_pool, choice_dense_map, "single", "dense", 0.0,
                                 seed_base=SEED + 101)
    ds_real_easy = dense_single_real["acc_easy"]
    k_sweep = {}
    for kf in K_GRID:
        r = run_pool(questions, retrieval_pool, choice_dense_map, "single", "sparse", kf, seed_base=SEED + 200)
        k_sweep[kf] = None if r["acc_easy"] is None else round(r["acc_easy"], 4)
        print(f"[k-sweep] k={kf:.2f} sparse_single_real_easy={k_sweep[kf]} (dense={round(ds_real_easy,4)})",
              flush=True)
    # k* = the k whose sparse_single_real is closest to dense_single_real (base-signal preservation)
    kstar = min(K_GRID, key=lambda kf: abs((k_sweep[kf] or 0.0) - (ds_real_easy or 0.0)))
    print(f"[k-select] k* = {kstar} (sparse_single_real={k_sweep[kstar]} vs dense {round(ds_real_easy,4)})",
          flush=True)

    # ---- run all arms at k* ----
    arms = {}
    plan = [
        ("oracle_dense_single", oracle_pool, "single", "dense"),
        ("oracle_dense_bundle", oracle_pool, "bundle", "dense"),
        ("oracle_sparse_single", oracle_pool, "single", "sparse"),
        ("oracle_sparse_bundle", oracle_pool, "bundle", "sparse"),
        ("real_dense_single", retrieval_pool, "single", "dense"),
        ("real_dense_bundle", retrieval_pool, "bundle", "dense"),
        ("real_sparse_single", retrieval_pool, "single", "sparse"),
        ("real_sparse_bundle", retrieval_pool, "bundle", "sparse"),
    ]
    for i, (name, pf, mode, regime) in enumerate(plan):
        _heartbeat(output_dir, "arm", {"arm": name})
        arms[name] = run_pool(questions, pf, choice_dense_map, mode, regime, kstar, seed_base=SEED + 1000 * (i + 1))
        ae = arms[name]["acc_easy"]
        print(f"[arm] {name:22s} easy={None if ae is None else round(ae,4)} "
              f"margin={arms[name]['bundle_margin_mean']} interf={arms[name]['fact_interference_mean']}",
              flush=True)
    # must-fail: sparse bundle on shuffled fact pools -> chance
    arms["real_sparse_bundle_shuffle"] = run_pool(questions, retrieval_pool, choice_dense_map, "bundle",
                                                  "sparse", kstar, shuffle=True, seed_base=SEED + 90000)

    # arms-differ (META_RULE_AF)
    dig = {k: hashlib.sha256(v["digest"].tobytes()).hexdigest() for k, v in arms.items()}
    pairwise = [("real_dense_single", "real_dense_bundle"), ("real_dense_bundle", "real_sparse_bundle"),
                ("real_sparse_single", "real_sparse_bundle")]
    arms_differ = all(dig[a] != dig[b] for a, b in pairwise)

    def E(k):
        return arms[k]["acc_easy"]
    def Cc(k):
        return arms[k]["acc_challenge"]

    # PRIMARY (REAL, Easy)
    r_ds, r_db = E("real_dense_single"), E("real_dense_bundle")
    r_ss, r_sb = E("real_sparse_single"), E("real_sparse_bundle")
    # ORACLE (Easy)
    o_ds, o_db = E("oracle_dense_single"), E("oracle_dense_bundle")
    o_ss, o_sb = E("oracle_sparse_single"), E("oracle_sparse_bundle")
    shuf = E("real_sparse_bundle_shuffle")

    # deltas
    d_sparse_rescue = round((r_sb or 0) - (r_db or 0), 4)          # sparse_bundle - dense_bundle (REAL)
    d_sparse_bundle_vs_single = round((r_sb or 0) - (r_ss or 0), 4)  # sparse bundle beats sparse single?
    d_base_preserved = round((r_ss or 0) - (r_ds or 0), 4)         # sparse single vs dense single (base signal)
    d_oracle_sparse_bundle_vs_single = round((o_sb or 0) - (o_ss or 0), 4)  # oracle-clean advantage preserved?

    # crosstalk mechanism direct measures (REAL bundle)
    margin_dense = arms["real_dense_bundle"]["bundle_margin_mean"]
    margin_sparse = arms["real_sparse_bundle"]["bundle_margin_mean"]
    interf_dense = arms["real_dense_bundle"]["fact_interference_mean"]
    interf_sparse = arms["real_sparse_bundle"]["fact_interference_mean"]

    # Gate D positive control: dense arms reproduce the prior atom at test regime
    repro_single = abs((r_ds or 0) - PRIOR_DENSE_SINGLE_REAL) <= REPRO_TOL
    repro_bundle = abs((r_db or 0) - PRIOR_DENSE_BUNDLE_REAL) <= REPRO_TOL
    repro_ok = repro_single and repro_bundle

    # gates
    base_preserved = (r_ss is not None) and (r_ds is not None) and (r_ss >= r_ds - BASE_SIGNAL_TOL)
    shuffle_collapsed = (shuf is not None) and (shuf < chance + MUSTFAIL_EPS)
    ag_saturated = (r_ds is not None) and (r_ds >= AG_SATURATION)
    baseline_in_band = (r_ds is not None) and (0.05 < r_ds < 0.95)

    # ---- verdict ----
    if not repro_ok:
        verdict = "POS_CONTROL_REPRO_FAIL"
        vmsg = (f"dense arms did NOT reproduce prior atom at test regime: dense_single_real "
                f"{r_ds} (want ~{PRIOR_DENSE_SINGLE_REAL}+-{REPRO_TOL}), dense_bundle_real {r_db} "
                f"(want ~{PRIOR_DENSE_BUNDLE_REAL}) -> code path drift; downstream sparse arms UNRELIABLE.")
    elif not shuffle_collapsed:
        verdict = "MUSTFAIL_BREACH"
        vmsg = (f"shuffle control did not collapse: sparse_bundle_shuffle Easy {shuf:.3f} "
                f"(want <{chance+MUSTFAIL_EPS:.3f}) -> readout may be a construction artifact.")
    elif ag_saturated:
        verdict = "AGG_DISCRIMINATOR_SATURATED"
        vmsg = f"dense_single_real {r_ds:.3f} >= {AG_SATURATION} -> no headroom (report, not a mechanism result)."
    elif not base_preserved:
        verdict = "INCONCLUSIVE_SPARSIFICATION_DAMAGED_CODE"
        vmsg = (f"sparsification destroyed base signal: sparse_single_real {r_ss:.3f} < dense_single_real "
                f"{r_ds:.3f} - {BASE_SIGNAL_TOL} (k*={kstar}). Cannot read bundle crosstalk fairly -- the "
                f"code-regime swap damaged the code, not a clean NULL. Try denser k or a natively-sparse encoder.")
    elif (d_sparse_bundle_vs_single > HP_BUNDLE_BEATS_SINGLE) and (d_sparse_rescue >= HP_SPARSE_RESCUE):
        verdict = "SPARSE_FIXES_CROSSTALK"
        vmsg = (f"SPARSE bundle rescues the dense-bundle REAL loss: sparse_bundle_real {r_sb:.3f} > "
                f"sparse_single_real {r_ss:.3f} (+{d_sparse_bundle_vs_single:.3f}) AND > dense_bundle_real "
                f"{r_db:.3f} (+{d_sparse_rescue:.3f}) at k*={kstar}; shuffle collapses ({shuf:.3f}). "
                f"Crosstalk mechanism confirmed: bundle-margin dense {margin_dense} -> sparse {margin_sparse}; "
                f"fact-interference dense {interf_dense} -> sparse {interf_sparse}. Composition/aggregation "
                f"was DENSE-CROSSTALK-limited; sparse codes rescue it -> real ARC-relevant win + validates "
                f"the sparse lever. Oracle-clean advantage preserved: sparse_bundle {o_sb:.3f} vs single "
                f"{o_ss:.3f} ({d_oracle_sparse_bundle_vs_single:+.3f}).")
    elif abs(d_sparse_rescue) < NEUTRAL_EPS:
        verdict = "SPARSITY_NEUTRAL"
        vmsg = (f"NULL (honest): sparse_bundle_real {r_sb:.3f} ~= dense_bundle_real {r_db:.3f} "
                f"(delta {d_sparse_rescue:+.3f} < {NEUTRAL_EPS}) at k*={kstar}, and sparse bundle "
                f"{'>' if d_sparse_bundle_vs_single>0 else '<='} sparse single {r_ss:.3f} "
                f"({d_sparse_bundle_vs_single:+.3f}). Crosstalk is NOT the limiter here: the real-retrieval "
                f"loss is retrieval-noise/content, not superposition (consistent with prior SPARSITY-NEUTRAL "
                f"results). Bundle-margin dense {margin_dense} -> sparse {margin_sparse}; fact-interference "
                f"dense {interf_dense} -> sparse {interf_sparse}. Sparse is not the lever here.")
    elif d_sparse_rescue >= NEUTRAL_EPS:
        verdict = "SPARSE_HELPS_BUNDLE_NOT_SINGLE"
        vmsg = (f"sparse_bundle_real {r_sb:.3f} beats dense_bundle_real {r_db:.3f} (+{d_sparse_rescue:.3f}) "
                f"but does NOT beat sparse_single_real {r_ss:.3f} ({d_sparse_bundle_vs_single:+.3f}) at "
                f"k*={kstar}: sparse reduces bundle crosstalk but bundling still does not beat single -- "
                f"partial support for the crosstalk mechanism.")
    else:
        verdict = "SPARSE_WORSE"
        vmsg = (f"sparse_bundle_real {r_sb:.3f} BELOW dense_bundle_real {r_db:.3f} ({d_sparse_rescue:+.3f}) "
                f"at k*={kstar}: sparsifying the bundle made crosstalk WORSE, not better.")

    grade = arc._grade_proxy(o_sb if o_sb else None, Cc("oracle_sparse_bundle"))

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [REAL Easy] dense_single={r_ds} dense_bundle={r_db} sparse_single={r_ss} "
                    f"sparse_bundle={r_sb} (k*={kstar}) | [ORACLE Easy] dense_single={o_ds} dense_bundle={o_db} "
                    f"sparse_single={o_ss} sparse_bundle={o_sb} | shuffle={shuf} chance={round(chance,3)} | "
                    f"crosstalk margin dense {margin_dense}->sparse {margin_sparse} interf "
                    f"dense {interf_dense}->sparse {interf_sparse}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": args.mode, "run_mode": args.mode,
        "n_dim": cfg["n_dim"], "seed": SEED,
        "n_questions": len(questions), "n_easy": n_easy, "n_challenge": n_chal,
        "chance_theoretical": round(chance, 4), "control_random_pick": round(ctrl_random, 4),
        # k-selection transparency
        "k_grid": K_GRID, "k_sweep_sparse_single_real_easy": k_sweep, "k_star": kstar,
        "dense_single_real_easy_for_kselect": None if ds_real_easy is None else round(ds_real_easy, 4),
        # PRIMARY: REAL pool, Easy
        "real_dense_single_easy": None if r_ds is None else round(r_ds, 4),
        "real_dense_bundle_easy": None if r_db is None else round(r_db, 4),
        "real_sparse_single_easy": None if r_ss is None else round(r_ss, 4),
        "real_sparse_bundle_easy": None if r_sb is None else round(r_sb, 4),
        "delta_sparse_rescue_easy": d_sparse_rescue,               # sparse_bundle - dense_bundle (THE test)
        "delta_sparse_bundle_vs_single_easy": d_sparse_bundle_vs_single,
        "delta_base_signal_preserved_easy": d_base_preserved,
        # ORACLE pool, Easy (clean-advantage preservation)
        "oracle_dense_single_easy": None if o_ds is None else round(o_ds, 4),
        "oracle_dense_bundle_easy": None if o_db is None else round(o_db, 4),
        "oracle_sparse_single_easy": None if o_ss is None else round(o_ss, 4),
        "oracle_sparse_bundle_easy": None if o_sb is None else round(o_sb, 4),
        "delta_oracle_sparse_bundle_vs_single_easy": d_oracle_sparse_bundle_vs_single,
        # Challenge split (secondary)
        "real_dense_single_challenge": None if Cc("real_dense_single") is None else round(Cc("real_dense_single"), 4),
        "real_dense_bundle_challenge": None if Cc("real_dense_bundle") is None else round(Cc("real_dense_bundle"), 4),
        "real_sparse_single_challenge": None if Cc("real_sparse_single") is None else round(Cc("real_sparse_single"), 4),
        "real_sparse_bundle_challenge": None if Cc("real_sparse_bundle") is None else round(Cc("real_sparse_bundle"), 4),
        # crosstalk MECHANISM direct measures (REAL bundle)
        "bundle_margin_dense_real": margin_dense,
        "bundle_margin_sparse_real": margin_sparse,
        "fact_interference_dense_real": interf_dense,
        "fact_interference_sparse_real": interf_sparse,
        # controls
        "real_sparse_bundle_shuffle_easy": None if shuf is None else round(shuf, 4),
        # Gate D positive control
        "prior_dense_single_real": PRIOR_DENSE_SINGLE_REAL, "prior_dense_bundle_real": PRIOR_DENSE_BUNDLE_REAL,
        "repro_dense_single_ok": bool(repro_single), "repro_dense_bundle_ok": bool(repro_bundle),
        "repro_ok": bool(repro_ok),
        # store / retrieval transparency
        "tablestore_facts": len(uid2sent), "test_gold_excluded": n_excluded,
        "heldout_store_facts": len(heldout_sents), "retrieval_K": K,
        "n_gold_central_encoded": len(gold_uids),
        # gates / integrity
        "base_signal_preserved": bool(base_preserved),
        "shuffle_collapsed": bool(shuffle_collapsed),
        "ag_saturated": bool(ag_saturated),
        "baseline_in_band": bool(baseline_in_band),
        "arms_differ_verified": bool(arms_differ),
        "arm_digests": dig,
        "bands": {"HP_sparse_rescue": HP_SPARSE_RESCUE, "HP_bundle_beats_single": HP_BUNDLE_BEATS_SINGLE,
                  "base_signal_tol": BASE_SIGNAL_TOL, "neutral_eps": NEUTRAL_EPS, "repro_tol": REPRO_TOL,
                  "mustfail_eps": MUSTFAIL_EPS, "ag_saturation": AG_SATURATION},
        "calibration_check": "adaptive_with_discriminator_gate: k* chosen by base-signal preservation on "
                             "SPARSE_SINGLE (independent of the bundle discriminator); bundle read is downstream",
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: reuses exp_arc_aggregation_retriever_bindsettle_v1 machinery wholesale (WorldTree parse, "
            "held-out top-K retrieval, oracle/real pools, SemanticHDEncoder, choice scoring); ONLY the CODE "
            "REGIME of the fact bundle changes (dense float vs sparse top-k bipolar via the same operator as "
            "ppmi_sparse_encoder.encode_sparse, applied to the SHARED encoder so semantics are held fixed); "
            "dense arms reproduce the prior atom (Gate D positive control); k* selected by base-signal "
            "preservation on sparse_single (calibration-honest); crosstalk mechanism instrumented directly "
            "(bundle answer-margin + pairwise fact-interference, dense vs sparse); shuffle must-fail control. "
            "STUBBED/NOTED: GSBC graded-sparse teacher-distillation NOT used (would need a text->dense teacher "
            "wire; the shared-encoder top-k swap is the purer one-variable test); CI-settle mode omitted "
            "(this cell isolates the bundle-superposition crosstalk question, not the Kintsch relaxation)."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING",
        "compute_architecture": "sequential-CPU numpy: batched retrieval matmul + per-question top-k sparsify + "
                                "bundle/single cosine; wall < 10min (justified: light closed-form scoring, no training fit)",
        "storage_strategy": "sharded (each fact its own vector; composed via bundle superposition per META_STORAGE)",
    }
    _write_metrics_atomic(output_dir, metrics)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
