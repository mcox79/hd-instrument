"""clean_encoder_eval_harness_v1 -- methodology-corrected encoder evaluation.

USER 2026-06-23 caught that ALL encoder tests this session were contaminated by
char-trigram-shaped substrate state. This cell establishes a CLEAN harness:
external ground truth + fresh per-arm encoding + NO substrate W / atoms /
internal state in the loop.

DESIGN (4 arms x 2 external benchmarks x 3 seeds for projection variance):
  ARM_CHAR_TRIGRAM_HONEST  -- substrate's bag-of-char-trigrams at N_DIM=4096.
                              Honest baseline (real English words; no name-leak).
  ARM_WORD2VEC_300D        -- word2vec-google-news-300 -> 4096d via Gaussian.
  ARM_GLOVE_300D           -- glove-wiki-gigaword-300 -> 4096d via Gaussian.
  ARM_FASTTEXT_300D        -- fasttext-wiki-news-subwords-300 -> 4096d (OOV via
                              char-ngram backoff built into model).

BENCHMARKS (cached at data/encoder_eval_benchmarks/):
  WordSim353 (Finkelstein 2001): 353 pairs, 0-10 human similarity.
  SimLex-999 (Hill 2015): 999 pairs, pure similarity (not relatedness).

METRIC:
  Spearman rank correlation between per-arm cosine and human score across
  all in-vocab pairs. OOV pairs dropped per arm; coverage reported.

PRE-REG bands (preregs/2026-06-23_clean_encoder_eval_harness_v1.md):
  HARD_PASS:  ANY arm achieves rho >= 0.50 on WS353 AND rho >= 0.40 on SimLex
  HARD_FAIL:  ALL arms achieve rho < 0.25 on WS353 (setup broken or fully null)
  MIDDLE_BAND: otherwise

SANITY:
  Planted pair (("king","queen") vs ("king","potato")): all SEMANTIC arms must
  rank cosine(king,queen) > cosine(king,potato). char_trigram may fail.

SUBSTRATE-ONLY: no LLM at inference; pretrained encoders are open-weight
static lookups; NO substrate W / atoms / Store touched.

Cites:
  - preregs/2026-06-23_clean_encoder_eval_harness_v1.md
  - experiments/exp_encoder_word2vec_substrate_bind_v1.py (sibling; substrate-internal metric)
  - Mikolov 2013 / Pennington 2014 / Bojanowski 2017
  - Finkelstein 2001 WordSim353 / Hill 2015 SimLex-999
  - USER_2026-06-23_contamination_diagnosis
  - USER_2026-06-22_no_minilm_no_bge
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit, hashlib, csv, io, zipfile, ssl
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "clean_encoder_eval_harness_v1"
BENCH_DIR = REPO / "data" / "encoder_eval_benchmarks"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WS353_FILE = BENCH_DIR / "wordsim353_combined.csv"
SIMLEX_FILE = BENCH_DIR / "simlex999.txt"
WS353_URL = "http://www.gabrilovich.com/resources/data/wordsim353/wordsim353.zip"
SIMLEX_URL = "https://fh295.github.io/SimLex-999.zip"

_LLM_CALL_COUNTER = [0]

# Pre-reg bands
HP_WS353_RHO = 0.50
HP_SIMLEX_RHO = 0.40
HF_WS353_RHO = 0.25

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
PRETRAIN_DIM = 300

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    PAIRS_CAP = None  # use all pairs
else:
    SEEDS = [0]
    PAIRS_CAP = 50

ARMS = ["ARM_CHAR_TRIGRAM_HONEST", "ARM_WORD2VEC_300D", "ARM_GLOVE_300D", "ARM_FASTTEXT_300D"]
SEMANTIC_ARMS = {"ARM_WORD2VEC_300D", "ARM_GLOVE_300D", "ARM_FASTTEXT_300D"}
PRETRAINED_ARMS = SEMANTIC_ARMS
GENSIM_MODEL_FOR = {
    "ARM_WORD2VEC_300D":   "word2vec-google-news-300",
    "ARM_GLOVE_300D":      "glove-wiki-gigaword-300",
    "ARM_FASTTEXT_300D":   "fasttext-wiki-news-subwords-300",
}

CONFIG_VERSION = (
    "clean_encoder_eval_harness_v1; N_DIM=%d PRETRAIN_DIM=%d seeds=%s arms=%s "
    "pairs_cap=%s mode=%s; bands HP_ws353_rho>=%.2f HP_simlex_rho>=%.2f "
    "HF_ws353_rho<%.2f"
) % (
    N_DIM, PRETRAIN_DIM, SEEDS, ARMS, PAIRS_CAP, RUN_MODE,
    HP_WS353_RHO, HP_SIMLEX_RHO, HF_WS353_RHO,
)


# ============================================================================
# Benchmark loaders (cached locally; fallback to download)
# ============================================================================

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _download_zip(url: str, inner_path: str, out_path: Path) -> None:
    """Download zip from url; extract inner_path; write bytes to out_path."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        data = r.read()
    z = zipfile.ZipFile(io.BytesIO(data))
    with z.open(inner_path) as f:
        payload = f.read()
    _ensure_dir(out_path.parent)
    with open(out_path, "wb") as o:
        o.write(payload)


def load_wordsim353() -> List[Tuple[str, str, float]]:
    """Returns list of (word1, word2, human_score) from WordSim353 combined.csv."""
    if not WS353_FILE.exists():
        print("[bench] WS353 cache miss; downloading from %s" % WS353_URL, flush=True)
        _download_zip(WS353_URL, "combined.csv", WS353_FILE)
    pairs: List[Tuple[str, str, float]] = []
    with open(WS353_FILE, "r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        for row in rdr:
            if len(row) < 3:
                continue
            w1, w2, score = row[0].strip(), row[1].strip(), float(row[2])
            pairs.append((w1, w2, score))
    return pairs


def load_simlex999() -> List[Tuple[str, str, float]]:
    """Returns list of (word1, word2, human_score) from SimLex-999.txt (TSV).

    Columns: word1, word2, POS, SimLex999, conc(w1), conc(w2), concQ,
             Assoc(USF), SimAssoc333, SD(SimLex)
    We use SimLex999 (column 3).
    """
    if not SIMLEX_FILE.exists():
        print("[bench] SimLex cache miss; downloading from %s" % SIMLEX_URL, flush=True)
        _download_zip(SIMLEX_URL, "SimLex-999/SimLex-999.txt", SIMLEX_FILE)
    pairs: List[Tuple[str, str, float]] = []
    with open(SIMLEX_FILE, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue
            w1, w2, score = parts[0].strip(), parts[1].strip(), float(parts[3])
            pairs.append((w1, w2, score))
    return pairs


# ============================================================================
# Substrate primitives -- char-trigram baseline
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    """Bag-of-trigrams sign-bundled bipolar HD vector. Deterministic; substrate-native."""
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def _l2_normalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    """Random Gaussian projection [out_dim, in_dim] with 1/sqrt(in_dim) scale (JL)."""
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# ============================================================================
# Pretrained-model loader (gensim downloader; cached at data/gensim_cache)
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(model_name)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


# ============================================================================
# Per-arm pair-encoder + cosine scorer
# ============================================================================

def _pair_words(pairs: List[Tuple[str, str, float]]) -> List[str]:
    seen = []
    s = set()
    for w1, w2, _ in pairs:
        if w1 not in s:
            seen.append(w1); s.add(w1)
        if w2 not in s:
            seen.append(w2); s.add(w2)
    return seen


def encode_words_char_trigram(words: List[str], n_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Encode each word via char-trigram into [V, n_dim] L2-normalized; returns (E, in_vocab_mask).

    char_trigram has 100% in-vocab coverage by construction.
    """
    V = len(words)
    E = np.zeros((V, n_dim), dtype=np.float32)
    mask = np.ones(V, dtype=bool)
    for i, w in enumerate(words):
        E[i] = char_trigram_encode(w, n_dim, seed)
    E = _l2_normalize(E)
    return E, mask


def encode_words_pretrained(words: List[str], n_dim: int, seed: int,
                            model_name: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """Encode each word via pretrained KV; project 300d -> n_dim via fresh per-seed Gaussian.

    OOV handling: mask=False for OOV; vector stays zero so cosine becomes 0 / undefined
    (we filter OOV pairs out of correlation downstream).
    Returns (E [V, n_dim], in_vocab_mask [V], meta).
    """
    kv = _load_gensim_kv(model_name)
    dim_pre = int(kv.vector_size)
    V = len(words)
    E_pre = np.zeros((V, dim_pre), dtype=np.float32)
    mask = np.zeros(V, dtype=bool)
    n_hit = 0
    n_miss = 0
    for i, w in enumerate(words):
        v = None
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        else:
            try:
                v = kv.get_vector(w, norm=False)
            except Exception:
                v = None
        if v is None:
            n_miss += 1
            continue
        E_pre[i] = v.astype(np.float32)
        mask[i] = True
        n_hit += 1
    E_pre_n = _l2_normalize(E_pre)
    # Fresh Gaussian per seed -- isolates "encoder semantic content" from
    # "projection noise". Same matrix across all 3 pretrained arms within
    # a seed so projection-noise is controlled.
    P = _gaussian_projection(in_dim=dim_pre, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    # Re-normalize after projection (JL approximately preserves; renormalize for cosine)
    E_proj = _l2_normalize(E_proj)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss), "n_vocab": int(V),
            "pretrain_dim": dim_pre}
    return E_proj, mask, meta


def cosine_pair_scores(E: np.ndarray, mask: np.ndarray, pairs: List[Tuple[str, str, float]],
                        word_to_idx: Dict[str, int]) -> Tuple[np.ndarray, np.ndarray, int]:
    """For each pair, compute cosine(E[w1], E[w2]) and align with human score.

    Pairs where either word is OOV (mask=False) are dropped.
    Returns (cosines [n_used], humans [n_used], n_used).
    """
    cosines = []
    humans = []
    for w1, w2, h in pairs:
        i1 = word_to_idx.get(w1)
        i2 = word_to_idx.get(w2)
        if i1 is None or i2 is None:
            continue
        if not mask[i1] or not mask[i2]:
            continue
        c = float(np.dot(E[i1], E[i2]))
        cosines.append(c)
        humans.append(h)
    return np.array(cosines, dtype=np.float64), np.array(humans, dtype=np.float64), len(cosines)


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation via scipy."""
    from scipy.stats import spearmanr
    if len(x) < 3:
        return float("nan")
    r = spearmanr(x, y)
    rho = float(getattr(r, "statistic", r[0] if hasattr(r, "__len__") else r))
    if not np.isfinite(rho):
        return float("nan")
    return rho


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] loading benchmarks" % seed, flush=True)
    ws353_all = load_wordsim353()
    simlex_all = load_simlex999()
    if PAIRS_CAP is not None:
        ws353 = ws353_all[:PAIRS_CAP]
        simlex = simlex_all[:PAIRS_CAP]
    else:
        ws353 = ws353_all
        simlex = simlex_all
    print("[seed=%d] WS353 pairs=%d  SimLex pairs=%d" % (seed, len(ws353), len(simlex)),
          flush=True)

    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] encoding" % (seed, arm_label), flush=True)

        arm_result = {"by_benchmark": {}, "meta": {}}

        for bench_label, pairs in (("WordSim353", ws353), ("SimLex999", simlex)):
            words = _pair_words(pairs)
            word_to_idx = {w: i for i, w in enumerate(words)}
            t_enc = time.time()
            if arm_label == "ARM_CHAR_TRIGRAM_HONEST":
                E, mask = encode_words_char_trigram(words, N_DIM, seed)
                meta = {"n_hit": int(mask.sum()), "n_miss": int((~mask).sum()),
                        "n_vocab": int(len(words)), "pretrain_dim": 0}
            else:
                model_name = GENSIM_MODEL_FOR[arm_label]
                E, mask, meta = encode_words_pretrained(words, N_DIM, seed, model_name)
            t_enc_s = time.time() - t_enc

            cos, hum, n_used = cosine_pair_scores(E, mask, pairs, word_to_idx)
            rho = spearman_rho(cos, hum) if n_used >= 3 else float("nan")
            arm_result["by_benchmark"][bench_label] = {
                "rho": float(rho) if np.isfinite(rho) else None,
                "n_pairs_total": int(len(pairs)),
                "n_pairs_used": int(n_used),
                "coverage": round(float(n_used) / max(len(pairs), 1), 4),
                "wall_encode_s": round(t_enc_s, 2),
                "encoder_meta": meta,
            }
            arm_result["meta"][bench_label] = meta
            rho_str = "nan" if rho is None or not np.isfinite(rho) else ("%.4f" % rho)
            print("    [seed=%d arm=%s bench=%s] rho=%s n_used=%d/%d cov=%.2f "
                  "(hit/miss=%d/%d enc=%.1fs)" % (
                seed, arm_label, bench_label, rho_str, n_used, len(pairs),
                float(n_used) / max(len(pairs), 1),
                meta.get("n_hit", 0), meta.get("n_miss", 0), t_enc_s), flush=True)

        by_arm[arm_label] = arm_result
        print("  [seed=%d arm=%s] total wall=%.1fs" % (
            seed, arm_label, time.time() - t_arm), flush=True)

    # Sanity planted-pair: king/queen vs king/potato across SEMANTIC arms
    planted = sanity_planted_pair(seed)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "sanity_planted_pair": planted,
        "N_DIM": N_DIM,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "n_ws353_pairs": int(len(ws353)),
        "n_simlex_pairs": int(len(simlex)),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


def sanity_planted_pair(seed: int) -> Dict:
    """king/queen should be MORE similar than king/potato across SEMANTIC arms."""
    out = {}
    triplet = ["king", "queen", "potato"]
    idx = {w: i for i, w in enumerate(triplet)}
    for arm_label in ARMS:
        if arm_label == "ARM_CHAR_TRIGRAM_HONEST":
            E, mask = encode_words_char_trigram(triplet, N_DIM, seed)
        else:
            model_name = GENSIM_MODEL_FOR[arm_label]
            E, mask, _ = encode_words_pretrained(triplet, N_DIM, seed, model_name)
        if not (mask[idx["king"]] and mask[idx["queen"]] and mask[idx["potato"]]):
            out[arm_label] = {"semantic_order_correct": None, "reason": "OOV"}
            continue
        cos_kq = float(np.dot(E[idx["king"]], E[idx["queen"]]))
        cos_kp = float(np.dot(E[idx["king"]], E[idx["potato"]]))
        out[arm_label] = {
            "cos_king_queen": round(cos_kq, 4),
            "cos_king_potato": round(cos_kp, 4),
            "semantic_order_correct": bool(cos_kq > cos_kp),
        }
    return out


# ============================================================================
# Verdict
# ============================================================================

def _mean_finite(vals: List[float]) -> Optional[float]:
    vs = [v for v in vals if v is not None and np.isfinite(v)]
    if not vs:
        return None
    return float(np.mean(vs))


def _std_finite(vals: List[float]) -> Optional[float]:
    vs = [v for v in vals if v is not None and np.isfinite(v)]
    if len(vs) < 2:
        return 0.0
    return float(np.std(vs))


def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_labels = list(units[0]["by_arm"].keys())
    bench_labels = ["WordSim353", "SimLex999"]

    by_arm_agg: Dict[str, Dict] = {}
    for arm_label in arm_labels:
        agg: Dict = {}
        for bl in bench_labels:
            rhos = [u["by_arm"][arm_label]["by_benchmark"][bl]["rho"] for u in units]
            ns = [u["by_arm"][arm_label]["by_benchmark"][bl]["n_pairs_used"] for u in units]
            covs = [u["by_arm"][arm_label]["by_benchmark"][bl]["coverage"] for u in units]
            mean_rho = _mean_finite(rhos)
            std_rho = _std_finite(rhos)
            agg[bl] = {
                "rho_mean": round(mean_rho, 4) if mean_rho is not None else None,
                "rho_std": round(std_rho, 4) if std_rho is not None else None,
                "rho_per_seed": [round(r, 4) if r is not None and np.isfinite(r) else None for r in rhos],
                "n_pairs_used_mean": float(np.mean(ns)) if ns else 0.0,
                "coverage_mean": round(float(np.mean(covs)), 4) if covs else 0.0,
            }
        by_arm_agg[arm_label] = agg

    # Per-arm dual-pass classification
    pass_per_arm: Dict[str, Dict] = {}
    for arm_label in arm_labels:
        ws_rho = by_arm_agg[arm_label]["WordSim353"]["rho_mean"]
        sl_rho = by_arm_agg[arm_label]["SimLex999"]["rho_mean"]
        ws_pass = (ws_rho is not None) and (ws_rho >= HP_WS353_RHO)
        sl_pass = (sl_rho is not None) and (sl_rho >= HP_SIMLEX_RHO)
        ws_fail = (ws_rho is None) or (ws_rho < HF_WS353_RHO)
        pass_per_arm[arm_label] = {
            "ws353_rho_mean": ws_rho,
            "simlex_rho_mean": sl_rho,
            "ws353_hard_pass": bool(ws_pass),
            "simlex_hard_pass": bool(sl_pass),
            "dual_hard_pass": bool(ws_pass and sl_pass),
            "ws353_hard_fail": bool(ws_fail),
        }

    any_dual = [a for a in arm_labels if pass_per_arm[a]["dual_hard_pass"]]
    all_ws_fail = all(pass_per_arm[a]["ws353_hard_fail"] for a in arm_labels)

    # Sanity planted-pair: SEMANTIC arms must rank king-queen > king-potato
    planted_failures = []
    for u in units:
        sp = u.get("sanity_planted_pair", {})
        for arm in SEMANTIC_ARMS:
            r = sp.get(arm, {})
            if r.get("semantic_order_correct") is False:
                planted_failures.append("seed=%d %s cos_kq=%s cos_kp=%s" % (
                    u["seed"], arm, r.get("cos_king_queen"), r.get("cos_king_potato")))
    sanity_ok = len(planted_failures) == 0

    detail = {
        "by_arm_agg": by_arm_agg,
        "pass_per_arm": pass_per_arm,
        "any_dual_hard_pass_arms": list(any_dual),
        "all_ws353_hard_fail": bool(all_ws_fail),
        "sanity_planted_pair_ok": sanity_ok,
        "sanity_planted_pair_failures": planted_failures,
        "n_seeds": len(units),
        "HP_WS353_RHO": HP_WS353_RHO,
        "HP_SIMLEX_RHO": HP_SIMLEX_RHO,
        "HF_WS353_RHO": HF_WS353_RHO,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "External-ground-truth encoder eval; 4 arms x 2 canonical word-similarity "
            "benchmarks (WordSim353 + SimLex-999) x %d seeds. NO substrate W / atoms / "
            "internal state in loop. Metric: Spearman rho between per-arm cosine and "
            "human similarity score. HARD_PASS = ANY arm rho>=%.2f on WS353 AND rho>=%.2f "
            "on SimLex. HARD_FAIL = ALL arms rho<%.2f on WS353 (setup or fully null). "
            "Methodology fix for char-trigram-contaminated substrate state."
        ) % (len(units), HP_WS353_RHO, HP_SIMLEX_RHO, HF_WS353_RHO),
        "cites": [
            "preregs/2026-06-23_clean_encoder_eval_harness_v1.md",
            "experiments/exp_encoder_word2vec_substrate_bind_v1.py (sibling; substrate-internal metric)",
            "Mikolov_2013_word2vec",
            "Pennington_2014_GloVe",
            "Bojanowski_2017_fastText",
            "Finkelstein_2001_WordSim353",
            "Hill_2015_SimLex_999",
            "USER_2026-06-23_contamination_diagnosis",
            "USER_2026-06-22_no_minilm_no_bge",
        ],
    }

    # Build summary
    parts = []
    for a in arm_labels:
        ws = by_arm_agg[a]["WordSim353"]["rho_mean"]
        sl = by_arm_agg[a]["SimLex999"]["rho_mean"]
        ws_s = "nan" if ws is None else ("%.3f" % ws)
        sl_s = "nan" if sl is None else ("%.3f" % sl)
        flag = "/DUAL" if pass_per_arm[a]["dual_hard_pass"] else ""
        parts.append("%s=ws%s/sl%s%s" % (a, ws_s, sl_s, flag))
    summary = "CLEAN_ENCODER_EVAL: " + " | ".join(parts) + " | sanity_ok=" + str(sanity_ok)

    if not sanity_ok:
        return ("CONFOUND_FAIL",
                ("CONFOUND_FAIL: planted-pair sanity failed: SEMANTIC arm(s) ranked "
                 "cos(king,potato) > cos(king,queen) -- encoder loading bug suspected, "
                 "NOT mechanism rejection. Failures: %s. " % "; ".join(planted_failures[:5])) + summary,
                detail)

    if any_dual:
        any_dual_sorted = sorted(any_dual, key=lambda x: (
            -(by_arm_agg[x]["WordSim353"]["rho_mean"] or 0.0),
            -(by_arm_agg[x]["SimLex999"]["rho_mean"] or 0.0),
        ))
        top = any_dual_sorted[0]
        t_ws = by_arm_agg[top]["WordSim353"]["rho_mean"]
        t_sl = by_arm_agg[top]["SimLex999"]["rho_mean"]
        return ("HARD_PASS",
                ("CLEAN_ENCODER_EVAL HARD_PASS: arm %s clears BOTH bands (WS353 rho=%.3f >= "
                 "%.2f AND SimLex rho=%.3f >= %.2f); encoder candidate aligned with human "
                 "similarity judgement on canonical external benchmarks; chain-grade-eligible "
                 "for downstream substrate use. dual_arms_count=%d. " % (
                     top, t_ws, HP_WS353_RHO, t_sl, HP_SIMLEX_RHO, len(any_dual))) + summary,
                detail)

    if all_ws_fail:
        return ("HARD_FAIL",
                ("CLEAN_ENCODER_EVAL HARD_FAIL: ALL %d arms (incl. word2vec/GloVe/fastText) "
                 "achieved Spearman rho < %.2f on WordSim353; either test setup is broken "
                 "(gensim load failure / lookup miscoded) OR no encoder candidate produces "
                 "human-aligned semantic structure on canonical benchmark. Diagnose test "
                 "setup before re-interpreting; word2vec lit baseline is rho~0.65 on WS353. "
                 % (len(arm_labels), HF_WS353_RHO)) + summary,
                detail)

    return ("MIDDLE_BAND",
            ("CLEAN_ENCODER_EVAL MIDDLE_BAND: at least one arm clears HF threshold on WS353 "
             "but NO arm achieves dual-band HP (rho>=%.2f on WS353 AND rho>=%.2f on SimLex). "
             "Partial encoder quality; route to follow-up if best candidate is encoder lever. "
             % (HP_WS353_RHO, HP_SIMLEX_RHO)) + summary,
            detail)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF: List[Optional[Path]] = [None]
_T0_REF: List[Optional[float]] = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize: compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_clean_encoder_eval_harness_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram encoder produces bipolar sign vectors
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,), "T1 shape: %s" % (v.shape,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 not bipolar: %s" % uniq

    # T2: Gaussian projection determinism + JL scale
    P1 = _gaussian_projection(300, 64, seed=7)
    P2 = _gaussian_projection(300, 64, seed=7)
    assert np.allclose(P1, P2), "T2 not deterministic"
    P3 = _gaussian_projection(300, 64, seed=8)
    assert not np.allclose(P1, P3), "T2 different seeds collided"
    std_P = float(P1.std())
    assert 0.04 < std_P < 0.08, "T2 JL std out of range: %.4f" % std_P

    # T3: L2-normalize
    X = np.array([[3.0, 4.0], [0.0, 0.0], [1.0, 0.0]], dtype=np.float32)
    Xn = _l2_normalize(X)
    assert abs(np.linalg.norm(Xn[0]) - 1.0) < 1e-5, "T3 norm 1 wrong"
    assert abs(np.linalg.norm(Xn[2]) - 1.0) < 1e-5, "T3 norm 2 wrong"

    # T4: cosine_pair_scores drops OOV
    words = ["a", "b", "c"]
    w2i = {w: i for i, w in enumerate(words)}
    E = np.eye(3, 64, dtype=np.float32)
    mask = np.array([True, True, False])
    pairs = [("a", "b", 5.0), ("a", "c", 3.0), ("b", "c", 1.0)]
    cos, hum, n_used = cosine_pair_scores(E, mask, pairs, w2i)
    assert n_used == 1, "T4 OOV drop wrong: %d" % n_used
    assert hum[0] == 5.0, "T4 wrong pair survived: %s" % hum

    # T5: spearman_rho monotonic case
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.array([1.0, 2.0, 3.0, 4.0])
    rho = spearman_rho(x, y)
    assert abs(rho - 1.0) < 1e-6, "T5 monotonic rho not 1: %s" % rho

    # T6: spearman_rho anti-monotonic case
    rho2 = spearman_rho(x, y[::-1])
    assert abs(rho2 + 1.0) < 1e-6, "T6 anti-mono rho not -1: %s" % rho2

    # T7: benchmark loaders return sane shape (if cache exists or downloadable)
    try:
        ws = load_wordsim353()
        assert len(ws) >= 100, "T7 WS353 too small: %d" % len(ws)
        w1, w2, s = ws[0]
        assert isinstance(w1, str) and isinstance(w2, str) and isinstance(s, float), "T7 WS353 row shape"
    except Exception as e:
        print("[selftest] T7 WS353 load skipped: %s" % e, flush=True)
    try:
        sl = load_simlex999()
        assert len(sl) >= 500, "T7 SimLex too small: %d" % len(sl)
        w1, w2, s = sl[0]
        assert isinstance(w1, str) and isinstance(w2, str) and isinstance(s, float), "T7 SimLex row shape"
    except Exception as e:
        print("[selftest] T7 SimLex load skipped: %s" % e, flush=True)

    # T8: char-trigram encoder gives different vectors for different words
    a = char_trigram_encode("cat", 256, seed=0)
    b = char_trigram_encode("dog", 256, seed=0)
    cos_ab = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    assert cos_ab < 0.99, "T8 cat/dog trigram too similar: %s" % cos_ab

    # T9: verdict-shape harness synthesizing units
    def _mk_unit(rhos_by_arm_bench, planted_ok=True, seed=0):
        # rhos_by_arm_bench: dict[arm] -> {WS353: rho, SimLex999: rho}
        by_arm = {}
        for arm in ARMS:
            ws = rhos_by_arm_bench[arm]["WordSim353"]
            sl = rhos_by_arm_bench[arm]["SimLex999"]
            by_arm[arm] = {
                "by_benchmark": {
                    "WordSim353": {"rho": ws, "n_pairs_total": 300, "n_pairs_used": 300,
                                    "coverage": 1.0, "wall_encode_s": 0.0,
                                    "encoder_meta": {"n_hit": 300, "n_miss": 0,
                                                      "n_vocab": 300, "pretrain_dim": 300}},
                    "SimLex999": {"rho": sl, "n_pairs_total": 900, "n_pairs_used": 900,
                                   "coverage": 1.0, "wall_encode_s": 0.0,
                                   "encoder_meta": {"n_hit": 900, "n_miss": 0,
                                                     "n_vocab": 900, "pretrain_dim": 300}},
                },
                "meta": {},
            }
        # Planted pair: semantic arms get correct order if planted_ok=True
        sp = {}
        for arm in ARMS:
            if arm in SEMANTIC_ARMS:
                sp[arm] = {"cos_king_queen": 0.8, "cos_king_potato": 0.1,
                            "semantic_order_correct": planted_ok}
            else:
                sp[arm] = {"cos_king_queen": 0.5, "cos_king_potato": 0.5,
                            "semantic_order_correct": False}
        return {
            "seed": seed,
            "by_arm": by_arm,
            "sanity_planted_pair": sp,
            "N_DIM": 4096, "PRETRAIN_DIM": 300,
            "n_ws353_pairs": 300, "n_simlex_pairs": 900,
            "run_mode": "smoke", "config_version": "selftest", "elapsed_s_seed": 0.0,
        }

    # T9a: HARD_PASS when any pretrained arm clears both bands
    rhos_pass = {
        "ARM_CHAR_TRIGRAM_HONEST": {"WordSim353": 0.15, "SimLex999": 0.08},
        "ARM_WORD2VEC_300D":        {"WordSim353": 0.65, "SimLex999": 0.42},
        "ARM_GLOVE_300D":           {"WordSim353": 0.60, "SimLex999": 0.40},
        "ARM_FASTTEXT_300D":        {"WordSim353": 0.62, "SimLex999": 0.43},
    }
    units_pass = [_mk_unit(rhos_pass, planted_ok=True, seed=s) for s in (0, 1, 2)]
    v, m, d = compute_verdict(units_pass)
    assert v == "HARD_PASS", "T9a expected HARD_PASS got %s : %s" % (v, m[:180])
    assert "ARM_WORD2VEC_300D" in d["any_dual_hard_pass_arms"], "T9a dual missing word2vec"

    # T9b: HARD_FAIL when ALL arms rho < 0.25 on WS353
    rhos_fail = {a: {"WordSim353": 0.12, "SimLex999": 0.06} for a in ARMS}
    units_fail = [_mk_unit(rhos_fail, planted_ok=True, seed=s) for s in (0, 1, 2)]
    v, m, _ = compute_verdict(units_fail)
    assert v == "HARD_FAIL", "T9b expected HARD_FAIL got %s : %s" % (v, m[:180])

    # T9c: MIDDLE_BAND when partial (best arm clears WS but not SimLex)
    rhos_middle = {
        "ARM_CHAR_TRIGRAM_HONEST": {"WordSim353": 0.15, "SimLex999": 0.08},
        "ARM_WORD2VEC_300D":        {"WordSim353": 0.55, "SimLex999": 0.30},
        "ARM_GLOVE_300D":           {"WordSim353": 0.50, "SimLex999": 0.28},
        "ARM_FASTTEXT_300D":        {"WordSim353": 0.52, "SimLex999": 0.32},
    }
    units_middle = [_mk_unit(rhos_middle, planted_ok=True, seed=s) for s in (0, 1, 2)]
    v, m, _ = compute_verdict(units_middle)
    assert v == "MIDDLE_BAND", "T9c expected MIDDLE got %s : %s" % (v, m[:180])

    # T9d: CONFOUND_FAIL when planted-pair sanity fails
    units_confound = [_mk_unit(rhos_pass, planted_ok=False, seed=s) for s in (0, 1, 2)]
    v, m, _ = compute_verdict(units_confound)
    assert v == "CONFOUND_FAIL", "T9d expected CONFOUND got %s : %s" % (v, m[:180])

    print("[selftest] PASS: T1 trigram bipolar + T2 projection det/JL + T3 L2-norm + "
          "T4 OOV drop + T5/T6 spearman + T7 bench loaders + T8 trigram different "
          "+ T9 verdict HARD_PASS / HARD_FAIL / MIDDLE / CONFOUND OK",
          flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d seeds=%s arms=%s pairs_cap=%s | "
          "name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, SEEDS, ARMS, PAIRS_CAP,
              _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "clean-encoder-eval-harness-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_clean_encoder_eval_harness_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (pure encoder eval; no substrate W/atoms in loop; cosine on bipolar HD; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
