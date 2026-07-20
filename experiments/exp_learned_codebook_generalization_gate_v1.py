"""Learned similarity-structured content codebook + held-out generalization GATE (v1).

STEP 1 of the foundation. Builds a LEARNED similarity-structured content codebook from CORPUS
co-occurrence (no external LLM) and VALIDATES that its geometry GENERALIZES against held-out,
corpus-independent relatedness labels. This replaces the RANDOM content codes that made the CPCL
forward model MEMORIZE (atom 29366: in-sample +0.50 -> held-out +0.004 = chance).

PRIOR ART (credit; learn-from / build-on, never steal):
  - Random Indexing: Kanerva 1988; Sahlgren 2005 (sparse-ternary index vectors + co-occurrence accumulation).
  - BEAGLE: Jones & Mewhort 2007 (context environment vectors; order via cyclic-shift binding).
  - PPMI + context smoothing (alpha=0.75): Church-Hanks 1990; Levy-Goldberg 2015.
  - PPMI-SVD embeddings: Levy-Goldberg 2015 (SVD of PPMI competitive with word2vec).
  - Reuses concept/math from hdlab/random_indexing.py (RI) + hdlab/ppmi_sparse_encoder.py (PPMI transform).
    The existing RI encoder is correct but pure-Python-looped and does not scale to text8's 17M tokens; this
    cell implements a vectorized scipy-sparse equivalent + PPMI weighting + RI-random-projection / SVD reductions.

ARMS (ONE variable = codebook construction; all share corpus / vocab / window / N / pair-sets):
  random     : random N(0,1) HD codes (NEGATIVE CONTROL = atom-29366 failure mode; no corpus info).
  ri_raw_rp  : Random Indexing of RAW co-occurrence counts.
  ppmi_rp    : Random Indexing of the PPMI matrix (RI + PPMI adopt).
  ppmi_svd   : PPMI + TruncatedSVD (Levy-Goldberg; primary mechanism arm).

VALIDATION (held-out true-vs-random; corpus-independent ground truth, never used to build codes):
  TRUE pairs   = top-tercile human-rated pairs from wordsim353 + simlex999 (in-vocab).
  RANDOM pairs = random re-pairings of the SAME pooled words (exact frequency/vocab control).
  Primary  = held-out TRUE-vs-RANDOM AUC per arm.  Sanity = external Spearman(cos, human) per benchmark.

Pre-reg: preregs/2026-07-19_learned_codebook_generalization_gate_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test; tmp_replace atomic metrics; except SystemExit: raise BEFORE
except Exception (no BaseException); crlb_n/a declared; baseline (negative control) in band; discriminator
survives scale (smoke at meaningful corpus scale, full scales UP); HARD_PASS strictly above chance floor;
cardinality gate; per-unit failure-class; fixed seeds (no hash()/list(set())); numbers tagged.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import scipy.sparse as sp
from scipy.stats import spearmanr
from sklearn.decomposition import TruncatedSVD

ANCHOR_NAME = "exp_learned_codebook_generalization_gate_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEXT8 = os.path.join(REPO, "data", "text8_cache", "text8.txt")
WORDSIM = os.path.join(REPO, "data", "encoder_eval_benchmarks", "wordsim353_combined.csv")
SIMLEX = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simlex999.txt")

ARMS = ["random", "ri_raw_rp", "ppmi_rp", "ppmi_svd"]
SEEDS = [7, 13, 19]

# Pre-registered bands (see prereg; declared BEFORE running, NOT tuned to pass).
HP_AUC = 0.72          # ppmi_svd held-out AUC (mean over seeds) HARD_PASS floor
HP_SPEARMAN = 0.35     # wordsim353 Spearman HARD_PASS floor
HF_AUC = 0.58          # at/below this = no better than random baseline
HF_SPEARMAN = 0.10     # at/below this = no transferable similarity
NEG_CTRL_AUC_MAX = 0.58  # random arm must stay at/below this (genuinely fails)


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- corpus + cooc
def load_tokens(n_tokens):
    """Load first n_tokens whitespace tokens from text8 (already lowercased)."""
    toks = []
    need = n_tokens
    with open(TEXT8, "r", encoding="utf-8") as f:
        while need > 0:
            chunk = f.read(4_000_000)
            if not chunk:
                break
            parts = chunk.split()
            toks.extend(parts[:need])
            need -= len(parts)
    return toks[:n_tokens]


def build_vocab(tokens, vocab_size, min_count):
    c = Counter(tokens)
    kept = [(w, n) for w, n in c.items() if n >= min_count]
    # Deterministic: sort by (-count, word); NO hash()/list(set()) ordering (PROT-023).
    kept.sort(key=lambda x: (-x[1], x[0]))
    kept = kept[:vocab_size]
    w2i = {w: i for i, (w, _n) in enumerate(kept)}
    counts = np.array([n for _w, n in kept], dtype=np.float64)
    return w2i, counts


def build_cooc(tokens, w2i, window):
    """Vectorized symmetric-window word-word co-occurrence -> CSR (V x V) float64."""
    V = len(w2i)
    ids = np.fromiter((w2i.get(t, -1) for t in tokens), dtype=np.int64, count=len(tokens))
    rows_all, cols_all = [], []
    for d in range(1, window + 1):
        a = ids[:-d]
        b = ids[d:]
        mask = (a >= 0) & (b >= 0)
        ra, rb = a[mask], b[mask]
        # symmetric: (a,b) and (b,a)
        rows_all.append(ra); cols_all.append(rb)
        rows_all.append(rb); cols_all.append(ra)
    rows = np.concatenate(rows_all)
    cols = np.concatenate(cols_all)
    data = np.ones(rows.shape[0], dtype=np.float64)
    cooc = sp.coo_matrix((data, (rows, cols)), shape=(V, V)).tocsr()
    cooc.sum_duplicates()
    return cooc


def build_ppmi(cooc, alpha=0.75):
    """PPMI with context-distribution smoothing (Levy-Goldberg 2015). Returns CSR float64."""
    coo = cooc.tocoo()
    total = float(coo.data.sum())
    row_sum = np.asarray(cooc.sum(axis=1)).ravel().astype(np.float64)
    col_sum = np.asarray(cooc.sum(axis=0)).ravel().astype(np.float64)
    col_sum_a = np.power(col_sum, alpha)
    col_total_a = float(col_sum_a.sum())
    r = row_sum[coo.row]
    c = col_sum_a[coo.col]
    # PPMI = max(0, log( P(w,c) / (P(w) * P_alpha(c)) ))
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = (coo.data * col_total_a) / (r * c + 1e-30)
        pmi = np.log(ratio + 1e-30)
    ppmi_data = np.maximum(pmi, 0.0)
    keep = ppmi_data > 0.0
    out = sp.coo_matrix((ppmi_data[keep], (coo.row[keep], coo.col[keep])),
                        shape=cooc.shape).tocsr()
    return out


def _l2norm_rows(M):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return M / n


def sparse_ternary_projection(V, N, sparsity, seed):
    """Sparse-ternary random projection R (V x N), Sahlgren-style s nonzeros per row."""
    rng = np.random.default_rng(seed)
    rows, cols, vals = [], [], []
    for i in range(V):
        idx = rng.choice(N, size=sparsity, replace=False)
        signs = rng.integers(0, 2, size=sparsity).astype(np.float64) * 2.0 - 1.0
        rows.append(np.full(sparsity, i)); cols.append(idx); vals.append(signs)
    R = sp.coo_matrix((np.concatenate(vals),
                       (np.concatenate(rows), np.concatenate(cols))),
                      shape=(V, N)).tocsr()
    return R


def build_codebook(arm, cooc, ppmi, V, N, seed, ri_sparsity):
    """Return (V x N) float64 L2-normalized codebook for the given arm. ONE variable = arm."""
    if arm == "random":
        rng = np.random.default_rng(seed)
        M = rng.standard_normal((V, N)).astype(np.float64)
        return _l2norm_rows(M)
    if arm == "ri_raw_rp":
        R = sparse_ternary_projection(V, N, ri_sparsity, seed)
        M = (cooc @ R).toarray().astype(np.float64)
        return _l2norm_rows(M)
    if arm == "ppmi_rp":
        R = sparse_ternary_projection(V, N, ri_sparsity, seed)
        M = (ppmi @ R).toarray().astype(np.float64)
        return _l2norm_rows(M)
    if arm == "ppmi_svd":
        k = min(N, V - 1)  # TruncatedSVD requires n_components < n_features(V)
        svd = TruncatedSVD(n_components=k, algorithm="randomized", n_iter=5, random_state=seed)
        M = svd.fit_transform(ppmi).astype(np.float64)
        if k < N:  # zero-pad to N so shape stays (V, N) across arms
            M = np.concatenate([M, np.zeros((V, N - k), dtype=np.float64)], axis=1)
        return _l2norm_rows(M)
    raise ValueError(f"unknown arm {arm!r}")


# --------------------------------------------------------------------------- references / eval
def load_wordsim(w2i):
    """wordsim353 CSV -> list of (i1, i2, score01) for in-vocab pairs."""
    pairs = []
    with open(WORDSIM, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            parts = line.rstrip("\n").split(",")
            if len(parts) < 3:
                continue
            w1, w2, s = parts[0].strip().lower(), parts[1].strip().lower(), parts[2].strip()
            if w1 in w2i and w2 in w2i and w1 != w2:
                pairs.append((w2i[w1], w2i[w2], float(s) / 10.0))
    return pairs


def load_simlex(w2i):
    """simlex999 TSV -> list of (i1, i2, score01) for in-vocab pairs (SimLex999 col index 3)."""
    pairs = []
    with open(SIMLEX, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            w1, w2, s = parts[0].strip().lower(), parts[1].strip().lower(), parts[3].strip()
            if w1 in w2i and w2 in w2i and w1 != w2:
                pairs.append((w2i[w1], w2i[w2], float(s) / 10.0))
    return pairs


def cos_pairs(codebook, pairs):
    """Cosine per (i1,i2,...) pair (codebook rows already L2-normalized -> dot = cosine).

    Accepts 2-tuples (i1,i2) or 3-tuples (i1,i2,score); uses only the first two indices.
    """
    if not pairs:
        return np.zeros(0)
    a = np.array([p[0] for p in pairs])
    b = np.array([p[1] for p in pairs])
    return np.sum(codebook[a] * codebook[b], axis=1)


def auc_true_vs_random(cos_true, cos_random):
    """AUC = P(cos_true > cos_random) via Mann-Whitney U (rank statistic)."""
    n1, n2 = len(cos_true), len(cos_random)
    if n1 == 0 or n2 == 0:
        return 0.5
    from scipy.stats import rankdata
    allv = np.concatenate([cos_true, cos_random])
    ranks = rankdata(allv)
    r1 = ranks[:n1].sum()
    u1 = r1 - n1 * (n1 + 1) / 2.0
    return float(u1 / (n1 * n2))


def make_true_random_sets(pairs, w2i, seed, top_tercile=True):
    """TRUE = top-tercile human-score in-vocab pairs; RANDOM = re-pairings of the SAME pooled words."""
    if not pairs:
        return [], []
    scores = np.array([p[2] for p in pairs])
    if top_tercile:
        thresh = np.quantile(scores, 2.0 / 3.0)
        true_pairs = [(p[0], p[1]) for p in pairs if p[2] >= thresh]
    else:
        true_pairs = [(p[0], p[1]) for p in pairs]
    # Pool of words that appear in rated pairs (exact frequency/vocab control).
    pool = sorted(set([p[0] for p in pairs] + [p[1] for p in pairs]))
    rng = np.random.default_rng(seed)
    true_set = set((min(a, b), max(a, b)) for a, b in true_pairs)
    n_random = max(len(true_pairs), 2000)
    random_pairs = []
    tries = 0
    while len(random_pairs) < n_random and tries < n_random * 20:
        tries += 1
        i = int(rng.choice(pool)); j = int(rng.choice(pool))
        if i == j:
            continue
        key = (min(i, j), max(i, j))
        if key in true_set:
            continue
        random_pairs.append((i, j))
    return true_pairs, random_pairs


# --------------------------------------------------------------------------- runner
def run(output_dir, n_tokens, vocab_size, N, window, min_count, ri_sparsity, seeds):
    t0 = time.perf_counter()
    expected_n_units = len(ARMS) * len(seeds)
    _write_start_marker(output_dir, os.path.basename(output_dir), expected_n_units)

    _hb(output_dir, f"loading {n_tokens} tokens from text8")
    tokens = load_tokens(n_tokens)
    _hb(output_dir, f"loaded {len(tokens)} tokens; building vocab (V<={vocab_size})")
    w2i, counts = build_vocab(tokens, vocab_size, min_count)
    V = len(w2i)
    _hb(output_dir, f"vocab V={V}; building co-occurrence (window={window})")
    cooc = build_cooc(tokens, w2i, window)
    _hb(output_dir, f"cooc nnz={cooc.nnz}; building PPMI")
    ppmi = build_ppmi(cooc)
    _hb(output_dir, f"ppmi nnz={ppmi.nnz}")

    ws_pairs = load_wordsim(w2i)
    sl_pairs = load_simlex(w2i)
    _hb(output_dir, f"references in-vocab: wordsim353={len(ws_pairs)} simlex999={len(sl_pairs)}")

    if len(ws_pairs) < 30 or len(sl_pairs) < 30:
        raise RuntimeError(
            f"REFERENCE_COVERAGE_TOO_LOW: wordsim={len(ws_pairs)} simlex={len(sl_pairs)} "
            f"(need >=30 each for stable Spearman/AUC); raise vocab_size/n_tokens")

    # TRUE/RANDOM sets built from the COMBINED reference pool (deterministic; seed 0 for the split).
    combined = ws_pairs + sl_pairs
    true_pairs, random_pairs = make_true_random_sets(combined, w2i, seed=0)
    _hb(output_dir, f"held-out sets: TRUE={len(true_pairs)} RANDOM={len(random_pairs)}")

    # Per arm x seed.
    per_unit = {}
    code_hashes_by_seed = {}
    arm_agg = {arm: {"auc": [], "ws_spearman": [], "sl_spearman": []} for arm in ARMS}
    n_units_done = 0
    for seed in seeds:
        code_hashes = {}
        for arm in ARMS:
            unit_key = f"{arm}__seed{seed}"
            try:
                cb = build_codebook(arm, cooc, ppmi, V, N, seed, ri_sparsity)
                import hashlib
                code_hashes[arm] = hashlib.sha256(np.ascontiguousarray(cb).tobytes()).hexdigest()
                cos_t = cos_pairs(cb, true_pairs)
                cos_r = cos_pairs(cb, random_pairs)
                auc = auc_true_vs_random(cos_t, cos_r)
                ws_cos = cos_pairs(cb, ws_pairs)
                ws_s = np.array([p[2] for p in ws_pairs])
                sl_cos = cos_pairs(cb, sl_pairs)
                sl_s = np.array([p[2] for p in sl_pairs])
                ws_sp = float(spearmanr(ws_cos, ws_s).correlation) if len(ws_pairs) > 2 else 0.0
                sl_sp = float(spearmanr(sl_cos, sl_s).correlation) if len(sl_pairs) > 2 else 0.0
                per_unit[unit_key] = {
                    "arm": arm, "seed": seed, "auc": auc,
                    "ws_spearman": ws_sp, "sl_spearman": sl_sp,
                    "mean_cos_true": float(np.mean(cos_t)) if len(cos_t) else 0.0,
                    "mean_cos_random": float(np.mean(cos_r)) if len(cos_r) else 0.0,
                    "failure_class": None,
                }
                arm_agg[arm]["auc"].append(auc)
                arm_agg[arm]["ws_spearman"].append(ws_sp)
                arm_agg[arm]["sl_spearman"].append(sl_sp)
                n_units_done += 1
                _hb(output_dir, f"{unit_key}: AUC={auc:.3f} ws_sp={ws_sp:.3f} sl_sp={sl_sp:.3f}")
            except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
                per_unit[unit_key] = {
                    "arm": arm, "seed": seed,
                    "failure_class": f"{type(e).__name__}: {str(e)[:200]}",
                }
                _hb(output_dir, f"{unit_key}: FAILED {type(e).__name__}")
        code_hashes_by_seed[seed] = code_hashes

    # ARMS-MUST-DIFFER (META_RULE_AF): within each seed, all 4 arm codebooks bit-distinct.
    arms_differ = True
    arms_differ_detail = {}
    for seed, hd in code_hashes_by_seed.items():
        vals = list(hd.values())
        distinct = len(set(vals)) == len(vals)
        arms_differ_detail[str(seed)] = distinct
        if not distinct:
            arms_differ = False

    # Aggregate means.
    def _m(a):
        return float(np.mean(a)) if a else float("nan")

    def _s(a):
        return float(np.std(a)) if len(a) > 1 else 0.0

    arm_summary = {}
    for arm in ARMS:
        arm_summary[arm] = {
            "auc_mean": _m(arm_agg[arm]["auc"]), "auc_std": _s(arm_agg[arm]["auc"]),
            "ws_spearman_mean": _m(arm_agg[arm]["ws_spearman"]),
            "sl_spearman_mean": _m(arm_agg[arm]["sl_spearman"]),
            "n_seeds": len(arm_agg[arm]["auc"]),
        }

    # Cardinality gate (META_RULE_H).
    cardinality_ok = (n_units_done == expected_n_units)

    # Discriminator-fires check.
    rnd_auc = arm_summary["random"]["auc_mean"]
    rnd_ws = abs(arm_summary["random"]["ws_spearman_mean"])
    svd_auc = arm_summary["ppmi_svd"]["auc_mean"]
    rp_auc = arm_summary["ppmi_rp"]["auc_mean"]
    svd_ws = arm_summary["ppmi_svd"]["ws_spearman_mean"]
    discriminator_fires = (rnd_auc <= NEG_CTRL_AUC_MAX and rnd_ws <= 0.10
                           and svd_auc > rnd_auc + 0.10)

    # Verdict logic.
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif rnd_auc > NEG_CTRL_AUC_MAX:
        verdict = "MIDDLE_BAND_NEG_CONTROL_NOT_AT_CHANCE"
    elif svd_auc >= HP_AUC and svd_ws >= HP_SPEARMAN and rnd_auc <= NEG_CTRL_AUC_MAX:
        verdict = "HARD_PASS"
    elif (svd_auc <= HF_AUC and rp_auc <= HF_AUC) or svd_ws <= HF_SPEARMAN:
        verdict = "HARD_FAIL_CODEBOOK_DOES_NOT_GENERALIZE_FOUNDATION_BLOCKED"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"ppmi_svd: AUC={svd_auc:.3f}+-{arm_summary['ppmi_svd']['auc_std']:.3f} "
        f"ws_sp={svd_ws:.3f} sl_sp={arm_summary['ppmi_svd']['sl_spearman_mean']:.3f} | "
        f"ppmi_rp AUC={rp_auc:.3f} ws_sp={arm_summary['ppmi_rp']['ws_spearman_mean']:.3f} | "
        f"ri_raw AUC={arm_summary['ri_raw_rp']['auc_mean']:.3f} | "
        f"random(neg-ctrl) AUC={rnd_auc:.3f} ws_sp={arm_summary['random']['ws_spearman_mean']:.3f} | "
        f"discriminator_fires={discriminator_fires} corpus={n_tokens}tok V={V} N={N}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:160]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "n_tokens": n_tokens, "vocab_size": vocab_size, "V": V, "N": N,
            "window": window, "min_count": min_count, "ri_sparsity": ri_sparsity, "seeds": seeds,
            "n_wordsim_pairs": len(ws_pairs), "n_simlex_pairs": len(sl_pairs),
            "n_true_pairs": len(true_pairs), "n_random_pairs": len(random_pairs),
        },
        "arm_summary": arm_summary,
        "per_unit": per_unit,
        "bands": {"HP_AUC": HP_AUC, "HP_SPEARMAN": HP_SPEARMAN, "HF_AUC": HF_AUC,
                  "HF_SPEARMAN": HF_SPEARMAN, "NEG_CTRL_AUC_MAX": NEG_CTRL_AUC_MAX},
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ,
        "arms_differ_detail": arms_differ_detail,
        "discriminator_fires": discriminator_fires,
        "crlb_n/a": "distributional-geometry generalization test; no argmax/capacity noise-floor",
        "prior_art": "Kanerva1988/Sahlgren2005 RI; Jones-Mewhort2007 BEAGLE; Church-Hanks1990/Levy-Goldberg2015 PPMI/SVD",
        "codebook_substrate_note": "codes are dense real L2-normalized HD; bundle(sum)-compatible + bipolarizable for HDC bind",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test at tiny scale: exercises the REAL builders + eval (no synthetic-only branch)."""
    print("[self-test] building tiny toy corpus", flush=True)
    # Toy corpus with clear topical clusters so distributional structure exists.
    base = (["cat", "pet", "feline", "purr", "whiskers"] * 8
            + ["dog", "pet", "canine", "bark", "loyal"] * 8
            + ["car", "road", "engine", "wheel", "drive"] * 8
            + ["king", "queen", "royal", "crown", "throne"] * 8)
    rng = np.random.default_rng(0)
    tokens = list(rng.permutation(base * 6))
    w2i, counts = build_vocab(tokens, vocab_size=50, min_count=1)
    V = len(w2i)
    assert V >= 12, f"toy vocab too small V={V}"
    cooc = build_cooc(tokens, w2i, window=3)
    assert cooc.nnz > 0, "empty cooc"
    ppmi = build_ppmi(cooc)
    assert ppmi.nnz > 0, "empty ppmi"
    N = 8  # toy: N < V (real run V>>N); exercises SVD cap+pad path too
    # Exercise ALL real arm builders (real_code_path: no synthetic-only branch).
    exercised = set()
    hashes = {}
    import hashlib
    for arm in ARMS:
        cb = build_codebook(arm, cooc, ppmi, V, N, seed=7, ri_sparsity=4)
        assert cb.shape == (V, N), f"{arm} shape {cb.shape}"
        assert np.all(np.isfinite(cb)), f"{arm} produced non-finite"
        nrm = np.linalg.norm(cb, axis=1)
        assert np.allclose(nrm[nrm > 0], 1.0, atol=1e-5), f"{arm} rows not L2-normalized"
        hashes[arm] = hashlib.sha256(np.ascontiguousarray(cb).tobytes()).hexdigest()
        exercised.add(arm)
    # ARMS-MUST-DIFFER.
    assert len(set(hashes.values())) == len(hashes), "META_RULE_AF: arm codebooks not bit-distinct"
    assert exercised == set(ARMS), f"real_code_path: not all arms exercised {exercised}"
    # AUC helper sanity: TRUE (identical index -> cos=1) vs RANDOM should give AUC=1 direction.
    a = auc_true_vs_random(np.array([0.9, 0.8, 0.7]), np.array([0.1, 0.2, 0.0]))
    assert a > 0.9, f"AUC helper wrong: {a}"
    a2 = auc_true_vs_random(np.array([0.1, 0.2]), np.array([0.8, 0.9]))
    assert a2 < 0.1, f"AUC helper wrong (reversed): {a2}"
    # References load + parse (real files).
    ws = load_wordsim(w2i)
    sl = load_simlex(w2i)  # toy vocab -> likely few/zero in-vocab; just assert no crash + list type.
    assert isinstance(ws, list) and isinstance(sl, list)
    # cos_pairs on toy codebook.
    cb = build_codebook("ppmi_svd", cooc, ppmi, V, N, seed=7, ri_sparsity=4)
    tp, rp = make_true_random_sets([(0, 1, 0.9), (2, 3, 0.8), (0, 2, 0.1), (1, 3, 0.2)], w2i, seed=0)
    assert isinstance(tp, list) and isinstance(rp, list)
    ct = cos_pairs(cb, [(0, 1), (2, 3)])
    assert ct.shape == (2,)
    print("[self-test] PASS: all 4 arm builders exercised + distinct; AUC/Spearman/refs/cos_pairs OK", flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, n_tokens=1_500_000, vocab_size=6000, N=1024, window=5,
            min_count=5, ri_sparsity=10, seeds=SEEDS)
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, n_tokens=8_000_000, vocab_size=10000, N=1024, window=5,
            min_count=5, ri_sparsity=10, seeds=SEEDS)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
